#!/home/jgf2/git/gimp-custom/app_build/.venv/bin/python3
import sys
import os
import tempfile
from dotenv import load_dotenv

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

gi.require_version("GimpUi", "3.0")
from gi.repository import GimpUi

gi.require_version("Gegl", "0.4")
from gi.repository import Gegl

gi.require_version("GLib", "2.0")
from gi.repository import GLib

gi.require_version("GObject", "2.0")
from gi.repository import GObject

gi.require_version("Gio", "2.0")
from gi.repository import Gio

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class NanobananaInpaint(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["nanobanana-inpaint"]

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run, None)
        
        procedure.set_image_types("*")
        procedure.set_menu_label("Nanobanana Inpaint...")
        procedure.add_menu_path("<Image>/Filters/GenAI/")
        
        procedure.set_documentation(
            "Inpaint an image selection using GenAI (nanobanana)",
            "Uses the Gemini GenAI API to inpaint the current selection with a user prompt.",
            name
        )
        procedure.set_attribution("Autonomous Developer", "Autonomous Developer", "2026")

        # Add string argument for the prompt
        procedure.add_string_argument(
            "prompt",
            "Prompt",
            "Describe what you want to inpaint in the selection",
            "",
            GObject.ParamFlags.READWRITE
        )

        procedure.add_string_argument(
            "api-key",
            "API Key",
            "Your Gemini API Key. Will persist in GIMP's settings.",
            "",
            GObject.ParamFlags.READWRITE
        )

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        if genai is None:
            Gimp.message("Error: google-genai library is not installed.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("nanobanana-inpaint")
            dialog = GimpUi.ProcedureDialog.new(procedure, config, "Nanobanana Inpaint")
            dialog.fill(["prompt", "api-key"])
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
            dialog.destroy()

        prompt = config.get_property("prompt")
        api_key = config.get_property("api-key")

        # Fallback to environment variable if empty
        if not api_key:
            load_dotenv()
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            Gimp.message("Error: API Key is required. Please enter it in the plugin dialog or set the GEMINI_API_KEY environment variable.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        # Get active drawable
        if not drawables:
            Gimp.message("Error: No active drawable.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        drawable = drawables[0]

        # Check if there is a selection — mask_intersect is on Drawable, not Image
        is_sel, x, y, w, h = drawable.mask_intersect()
        if not is_sel:
            Gimp.message("Error: Please make a selection to indicate the inpainting area.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        Gimp.progress_init("Nanobanana Inpaint: Preparing...")

        temp_dir = tempfile.mkdtemp()
        img_path = os.path.join(temp_dir, "image.png")
        res_path = os.path.join(temp_dir, "result.png")

        try:
            # --- Step 1: Export the flattened image to a temp PNG ---
            Gimp.progress_set_text("Exporting image...")
            Gimp.progress_update(0.1)

            dup_image = image.duplicate()
            dup_layer = dup_image.flatten()

            img_file = Gio.File.new_for_path(img_path)
            Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, dup_image, img_file, None)
            dup_image.delete()

            if not os.path.exists(img_path):
                Gimp.message("Error: Failed to export the image to a temporary file.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

            Gimp.progress_update(0.2)

            # --- Step 2: Read image bytes for the API ---
            Gimp.progress_set_text("Preparing API request...")
            with open(img_path, "rb") as f:
                image_bytes = f.read()

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/png",
            )

            full_prompt = (
                f"Edit this image. In the rectangular region from pixel ({x},{y}) "
                f"to ({x+w},{y+h}), please apply the following change: {prompt}. "
                f"Keep everything outside that region exactly the same. "
                f"Return only the edited image."
            )

            Gimp.progress_update(0.25)

            # --- Step 3: Call Gemini generate_content ---
            Gimp.progress_set_text("Waiting for Gemini AI response...")
            client = genai.Client(api_key=api_key)

            # Run the API call in a thread so we can pulse the progress bar
            import threading
            api_result = {"response": None, "error": None}

            def call_api():
                try:
                    api_result["response"] = client.models.generate_content(
                        model="gemini-3-pro-image-preview",
                        contents=[full_prompt, image_part],
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"],
                        ),
                    )
                except Exception as e:
                    api_result["error"] = e

            api_thread = threading.Thread(target=call_api)
            api_thread.start()

            # Pulse the progress bar while waiting for the API
            while api_thread.is_alive():
                Gimp.progress_pulse()
                api_thread.join(timeout=0.3)

            if api_result["error"]:
                raise api_result["error"]

            response = api_result["response"]

            # --- Step 4: Extract and apply the result ---
            Gimp.progress_set_text("Processing result...")
            Gimp.progress_update(0.7)

            # Find the image part in the response
            result_image_data = None
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        result_image_data = part.inline_data.data
                        break

            if result_image_data is None:
                if response.parts:
                    for part in response.parts:
                        if part.inline_data is not None:
                            result_image_data = part.inline_data.data
                            break

            if result_image_data is None:
                Gimp.message("Error: No image was returned from the GenAI API. The model may have refused the request.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

            # Save result to temp file
            with open(res_path, "wb") as f:
                f.write(result_image_data)

            Gimp.progress_update(0.8)
            Gimp.progress_set_text("Loading result into GIMP...")

            # Load result image into GIMP
            res_file = Gio.File.new_for_path(res_path)
            res_image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, res_file)
            if not res_image:
                Gimp.message("Error: Failed to load the result image into GIMP.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

            # Scale result to match original if needed
            res_w = res_image.get_width()
            res_h = res_image.get_height()
            orig_w = image.get_width()
            orig_h = image.get_height()
            if res_w != orig_w or res_h != orig_h:
                res_image.scale(orig_w, orig_h)

            Gimp.progress_update(0.9)

            res_layers = res_image.get_selected_layers()
            res_layer = res_layers[0] if res_layers else res_image.list_layers()[0]

            # Create a new layer in the original image
            image.undo_group_start()

            new_layer = Gimp.Layer.new_from_drawable(res_layer, image)
            new_layer.set_name("Inpainting Result")
            image.insert_layer(new_layer, None, -1)

            # Clean up the temporary result image
            res_image.delete()

            image.undo_group_end()
            Gimp.displays_flush()

            Gimp.progress_update(1.0)
            Gimp.progress_end()

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            Gimp.message(f"Exception occurred: {str(e)}\n{tb}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        finally:
            # Clean up temp files
            for f in [img_path, res_path]:
                if os.path.exists(f):
                    os.remove(f)
            if os.path.exists(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(NanobananaInpaint.__gtype__, sys.argv)
