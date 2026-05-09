#!/home/jgf2/git/gimp-custom/app_build/.venv/bin/python3
"""Nanobanana — GIMP 3.2 GenAI plugin suite: Inpaint & Background Removal."""

import os
import sys
import tempfile
import threading
import time

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp  # noqa: E402

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi  # noqa: E402

gi.require_version("GLib", "2.0")
from gi.repository import GLib  # noqa: E402

gi.require_version("GObject", "2.0")
from gi.repository import GObject  # noqa: E402

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa: E402

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

DEFAULT_MODEL = "gemini-2.0-flash-preview-image-generation"
MAX_RETRIES = 3
# Use JPEG for images above 3000×3000 (9 million pixels)
JPEG_THRESHOLD_PIXELS = 9_000_000

# Known image-capable models (fallback if API list unavailable)
KNOWN_MODELS = [
    ("gemini-2.0-flash-preview-image-generation", "Gemini 2.0 Flash (Image Gen Preview)"),
    ("gemini-3-pro-image-preview", "Gemini 3 Pro (Image Preview)"),
    ("gemini-2.0-flash", "Gemini 2.0 Flash"),
]

# Cache for dynamically fetched models
_cached_models = None


def _fetch_image_models(api_key):
    """Fetch models that support generateContent from the Gemini API."""
    global _cached_models
    if _cached_models is not None:
        return _cached_models
    if not api_key or genai is None:
        return None
    try:
        client = genai.Client(api_key=api_key)
        models = []
        for m in client.models.list():
            # Only include models that support content generation
            actions = getattr(m, "supported_actions", []) or []
            methods = getattr(m, "supported_generation_methods", []) or []
            if "generateContent" in actions or "generateContent" in methods:
                name = m.name
                # Strip 'models/' prefix if present
                if name is not None and name.startswith("models/"):
                    name = name[7:]
                display = getattr(m, "display_name", name) or name
                models.append((name, display))
        if models:
            _cached_models = models
            return models
    except Exception:
        pass
    return None


def _build_model_choice(api_key):
    """Build a Gimp.Choice populated with available models."""
    choice = Gimp.Choice.new()

    # Try dynamic list first
    dynamic = _fetch_image_models(api_key)
    model_list = dynamic if dynamic else KNOWN_MODELS

    for i, (nick, label) in enumerate(model_list):
        choice.add(nick, i, label, "")

    return choice


def _get_api_key():
    """Try to load API key from environment."""
    if load_dotenv:
        load_dotenv()
    return os.environ.get("GEMINI_API_KEY", "")


# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------


def compute_crop_bounds(image, sx, sy, sw, sh):
    """Return padded crop bounds (x, y, w, h) clamped to image size."""
    img_w, img_h = image.get_width(), image.get_height()
    pad_x = max(50, int(sw * 0.15))
    pad_y = max(50, int(sh * 0.15))
    x0 = max(0, sx - pad_x)
    y0 = max(0, sy - pad_y)
    x1 = min(img_w, sx + sw + pad_x)
    y1 = min(img_h, sy + sh + pad_y)
    return x0, y0, x1 - x0, y1 - y0


def export_image(image, crop_bounds=None):
    """Flatten, optionally crop, and export. Returns (bytes, mime)."""
    dup = image.duplicate()
    dup.flatten()
    if crop_bounds:
        bx, by, bw, bh = crop_bounds
        dup.crop(bw, bh, bx, by)

    w, h = dup.get_width(), dup.get_height()
    if w * h > JPEG_THRESHOLD_PIXELS:
        ext, mime = "jpg", "image/jpeg"
    else:
        ext, mime = "png", "image/png"

    path = os.path.join(tempfile.gettempdir(), f"nb_src_{os.getpid()}.{ext}")
    Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, dup, Gio.File.new_for_path(path), None)
    dup.delete()

    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    return data, mime


def export_mask(image, crop_bounds=None):
    """Export the selection channel as a grayscale PNG (white=edit)."""
    sel_channel = image.get_selection()
    w, h = image.get_width(), image.get_height()

    mask_img = Gimp.Image.new(w, h, Gimp.ImageBaseType.GRAY)
    mask_layer = Gimp.Layer.new_from_drawable(sel_channel, mask_img)
    mask_img.insert_layer(mask_layer, None, 0)

    if crop_bounds:
        bx, by, bw, bh = crop_bounds
        mask_img.crop(bw, bh, bx, by)

    path = os.path.join(tempfile.gettempdir(), f"nb_mask_{os.getpid()}.png")
    Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, mask_img, Gio.File.new_for_path(path), None)
    mask_img.delete()

    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    return data


def api_call_with_retry(client, model, contents, gen_config):
    """Call generate_content with retry on transient errors (429/500/503)."""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=gen_config,
            )
        except Exception as e:
            last_err = e
            code = str(e)
            if any(c in code for c in ("429", "500", "503")) and attempt < MAX_RETRIES:
                wait = 2**attempt
                Gimp.progress_set_text(f"Retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})…")
                Gimp.message(f"Transient API error — retrying in {wait}s (attempt {attempt}/{MAX_RETRIES}): {e}")
                time.sleep(wait)
                continue
            raise
    if last_err is not None:
        raise last_err


def extract_image_data(response):
    """Pull the first inline_data image from a Gemini response."""
    sources = []
    if response.candidates and response.candidates[0].content:
        sources.append(response.candidates[0].content.parts or [])
    if response.parts:
        sources.append(response.parts)
    for parts in sources:
        for part in parts:
            if part.inline_data is not None:
                return part.inline_data.data
    return None


def threaded_api_call(api_func):
    """Run api_func in a thread while pulsing the GIMP progress bar."""
    value = None
    error = None

    def target():
        nonlocal value, error
        try:
            value = api_func()
        except Exception as e:
            error = e

    t = threading.Thread(target=target)
    t.start()
    while t.is_alive():
        Gimp.progress_pulse()
        t.join(timeout=0.3)

    if error is not None:
        raise error
    return value


def load_result_as_layer(image, result_data, layer_name, target_w, target_h, offset_x, offset_y, apply_offset):
    """Save API result bytes, load into GIMP, insert as a new layer."""
    res_path = os.path.join(tempfile.gettempdir(), f"nb_res_{os.getpid()}.png")
    with open(res_path, "wb") as f:
        f.write(result_data)

    res_image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(res_path))
    os.remove(res_path)

    if not res_image:
        raise RuntimeError("Failed to load result image into GIMP.")

    rw, rh = res_image.get_width(), res_image.get_height()
    if rw != target_w or rh != target_h:
        res_image.scale(target_w, target_h)

    res_layers = res_image.get_selected_layers()
    res_layer = res_layers[0] if res_layers else res_image.list_layers()[0]

    image.undo_group_start()
    new_layer = Gimp.Layer.new_from_drawable(res_layer, image)
    new_layer.set_name(layer_name)
    image.insert_layer(new_layer, None, -1)

    if apply_offset:
        new_layer.set_offsets(offset_x, offset_y)

    res_image.delete()
    image.undo_group_end()
    Gimp.displays_flush()


# ==================================================================
# Plugin class — registers both procedures
# ==================================================================


class NanobananaInpaint(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["nanobanana-inpaint", "nanobanana-remove-bg"]

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        # Try to fetch an API key for dynamic model listing
        env_key = _get_api_key()

        if name == "nanobanana-inpaint":
            return self._create_inpaint_procedure(name, env_key)
        elif name == "nanobanana-remove-bg":
            return self._create_remove_bg_procedure(name, env_key)
        return None

    # ------------------------------------------------------------------
    # Inpaint procedure
    # ------------------------------------------------------------------

    def _create_inpaint_procedure(self, name, env_key):
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run_inpaint, None)
        procedure.set_image_types("*")
        procedure.set_menu_label("Nanobanana Inpaint…")
        procedure.add_menu_path("<Image>/Filters/GenAI/")
        procedure.set_documentation(
            "Inpaint selection using GenAI",
            "Uses the Gemini API with a mask generated from the current selection to inpaint the image.",
            name,
        )
        procedure.set_attribution("Autonomous Developer", "Autonomous Developer", "2026")

        procedure.add_string_argument(
            "prompt",
            "Prompt",
            "Describe what to generate in the selected area",
            "",
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_choice_argument(
            "model",
            "Model",
            "Gemini model to use",
            _build_model_choice(env_key),
            DEFAULT_MODEL,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_boolean_argument(
            "crop-context",
            "Crop to Selection",
            "Send only the selection area (+ padding) for faster processing",
            False,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_boolean_argument(
            "position-layer",
            "Position Result at Selection",
            "Place the result at the selection offset",
            True,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_int_argument(
            "creativity",
            "Creativity",
            "0 = conservative, 100 = very creative",
            0,
            100,
            40,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_string_argument(
            "api-key",
            "API Key",
            "Gemini API Key (persists in GIMP settings)",
            "",
            GObject.ParamFlags.READWRITE,
        )
        return procedure

    def run_inpaint(self, procedure, run_mode, image, drawables, config, data):
        if genai is None:
            Gimp.message("Error: google-genai library is not installed.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("nanobanana-inpaint")
            dialog = GimpUi.ProcedureDialog.new(procedure, config, "Nanobanana Inpaint")
            dialog.fill([
                "prompt",
                "model",
                "crop-context",
                "position-layer",
                "creativity",
                "api-key",
            ])
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
            dialog.destroy()

        prompt = config.get_property("prompt")
        api_key = config.get_property("api-key")
        model = config.get_property("model") or DEFAULT_MODEL
        crop_context = config.get_property("crop-context")
        position_layer = config.get_property("position-layer")
        temperature = config.get_property("creativity") / 50.0

        if not api_key:
            api_key = _get_api_key()
        if not api_key:
            Gimp.message("Error: API Key is required.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        if not drawables:
            Gimp.message("Error: No active drawable.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        is_sel, sel_x, sel_y, sel_w, sel_h = drawables[0].mask_intersect()
        if not is_sel:
            Gimp.message("Error: Please make a selection first.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        Gimp.progress_init("Nanobanana Inpaint")
        try:
            Gimp.progress_set_text("Exporting image and mask…")
            Gimp.progress_update(0.05)

            crop_bounds = None
            if crop_context:
                crop_bounds = compute_crop_bounds(image, sel_x, sel_y, sel_w, sel_h)

            img_bytes, mime = export_image(image, crop_bounds)
            Gimp.progress_update(0.15)

            mask_bytes = export_mask(image, crop_bounds)
            Gimp.progress_update(0.25)

            Gimp.progress_set_text("Preparing request…")
            img_part = types.Part.from_bytes(data=img_bytes, mime_type=mime)
            mask_part = types.Part.from_bytes(data=mask_bytes, mime_type="image/png")

            text_prompt = (
                f"Edit this image using the provided mask. "
                f"The mask shows the area to modify (white = edit, black = preserve). "
                f"In the masked area, please: {prompt}. "
                f"Keep all unmasked areas exactly the same. "
                f"Return only the edited image."
            )
            gen_config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=temperature,
            )
            Gimp.progress_update(0.3)

            Gimp.progress_set_text(f"Waiting for {model}…")
            client = genai.Client(api_key=api_key)

            response = threaded_api_call(
                lambda: api_call_with_retry(
                    client,
                    model,
                    [text_prompt, img_part, mask_part],
                    gen_config,
                )
            )

            Gimp.progress_set_text("Processing result…")
            Gimp.progress_update(0.7)

            result_data = extract_image_data(response)
            if result_data is None:
                Gimp.message("Error: No image returned from the API.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

            Gimp.progress_update(0.8)
            Gimp.progress_set_text("Loading result into GIMP…")

            if crop_context and crop_bounds:
                tw, th = crop_bounds[2], crop_bounds[3]
                ox, oy = crop_bounds[0], crop_bounds[1]
            else:
                tw, th = image.get_width(), image.get_height()
                ox, oy = 0, 0

            load_result_as_layer(
                image,
                result_data,
                "Inpainting Result",
                tw,
                th,
                ox,
                oy,
                apply_offset=(crop_context or position_layer),
            )
            Gimp.progress_update(1.0)

        except Exception as e:
            import traceback

            Gimp.message(f"Exception: {e}\n{traceback.format_exc()}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        finally:
            Gimp.progress_end()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    # ------------------------------------------------------------------
    # Background Removal procedure
    # ------------------------------------------------------------------

    def _create_remove_bg_procedure(self, name, env_key):
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run_remove_bg, None)
        procedure.set_image_types("*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE | Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
        procedure.set_menu_label("Nanobanana Remove Background…")
        procedure.add_menu_path("<Image>/Filters/GenAI/")
        procedure.set_documentation(
            "Remove background using GenAI",
            "Uses the Gemini API to remove the background from the image and return a transparent result as a new layer.",
            name,
        )
        procedure.set_attribution("Autonomous Developer", "Autonomous Developer", "2026")

        procedure.add_choice_argument(
            "model",
            "Model",
            "Gemini model to use",
            _build_model_choice(env_key),
            DEFAULT_MODEL,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_string_argument(
            "subject",
            "Subject Hint (optional)",
            "Optionally describe the subject to keep (e.g. 'the person', 'the cat')",
            "",
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_string_argument(
            "api-key",
            "API Key",
            "Gemini API Key (persists in GIMP settings)",
            "",
            GObject.ParamFlags.READWRITE,
        )
        return procedure

    def run_remove_bg(self, procedure, run_mode, image, drawables, config, data):
        if genai is None:
            Gimp.message("Error: google-genai library is not installed.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("nanobanana-remove-bg")
            dialog = GimpUi.ProcedureDialog.new(procedure, config, "Remove Background")
            dialog.fill(["model", "subject", "api-key"])
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
            dialog.destroy()

        api_key = config.get_property("api-key")
        model = config.get_property("model") or DEFAULT_MODEL
        subject = config.get_property("subject")

        if not api_key:
            api_key = _get_api_key()
        if not api_key:
            Gimp.message("Error: API Key is required.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        Gimp.progress_init("Remove Background")
        try:
            Gimp.progress_set_text("Exporting image…")
            Gimp.progress_update(0.1)

            img_bytes, mime = export_image(image)
            Gimp.progress_update(0.2)

            Gimp.progress_set_text("Preparing request…")
            img_part = types.Part.from_bytes(data=img_bytes, mime_type=mime)

            if subject:
                text_prompt = (
                    f"Remove the background from this image, keeping only {subject}. "
                    f"Make the background fully transparent. "
                    f"Return only the image with a transparent background."
                )
            else:
                text_prompt = (
                    "Remove the background from this image. "
                    "Keep only the main subject(s) and make the background "
                    "fully transparent. Return only the image with a "
                    "transparent background."
                )

            gen_config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
            Gimp.progress_update(0.3)

            Gimp.progress_set_text(f"Waiting for {model}…")
            client = genai.Client(api_key=api_key)

            response = threaded_api_call(
                lambda: api_call_with_retry(
                    client,
                    model,
                    [text_prompt, img_part],
                    gen_config,
                )
            )

            Gimp.progress_set_text("Processing result…")
            Gimp.progress_update(0.7)

            result_data = extract_image_data(response)
            if result_data is None:
                Gimp.message("Error: No image returned from the API.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

            Gimp.progress_update(0.8)
            Gimp.progress_set_text("Loading result into GIMP…")

            load_result_as_layer(
                image,
                result_data,
                "Background Removed",
                image.get_width(),
                image.get_height(),
                0,
                0,
                apply_offset=False,
            )
            Gimp.progress_update(1.0)

        except Exception as e:
            import traceback

            Gimp.message(f"Exception: {e}\n{traceback.format_exc()}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        finally:
            Gimp.progress_end()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


if __name__ == "__main__":
    Gimp.main(NanobananaInpaint.__gtype__, sys.argv)
