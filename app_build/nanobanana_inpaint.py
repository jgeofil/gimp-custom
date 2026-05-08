#!/usr/bin/env python3
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

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        if genai is None:
            Gimp.message("Error: google-genai library is not installed.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init("nanobanana-inpaint")
            dialog = GimpUi.ProcedureDialog.new(procedure, config, "Nanobanana Inpaint")
            dialog.fill(["prompt"])
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
            dialog.destroy()

        prompt = config.get_property("prompt")
        
        # We need an active API key
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            Gimp.message("Error: GEMINI_API_KEY environment variable not found.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        # Get active drawable
        if not drawables:
            Gimp.message("Error: No active drawable.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        
        drawable = drawables[0]

        # Check if there is a selection
        is_sel, x, y, w, h = image.mask_intersect(drawable)
        if not is_sel:
            Gimp.message("Error: Please make a selection to indicate the inpainting area.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        # We need to save the image and the mask to temporary files
        temp_dir = tempfile.mkdtemp()
        img_path = os.path.join(temp_dir, "image.png")
        mask_path = os.path.join(temp_dir, "mask.png")
        res_path = os.path.join(temp_dir, "result.png")

        try:
            # Save the active drawable as PNG
            img_file = Gio.File.new_for_path(img_path)
            # Since GIMP 3.0, we use file_png_save. 
            # Actually, using Gimp.get_pdb().run_procedure is safer if we don't know the exact signature
            # But wait, we can just use Gegl to save the buffer or Gimp.file_save
            Gimp.get_pdb().run_procedure("file-png-save", [
                GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
                GObject.Value(Gimp.Image, image),
                GObject.Value(Gimp.Drawable, drawable),
                GObject.Value(Gio.File, img_file),
                GObject.Value(GObject.TYPE_BOOLEAN, False), # interlace
                GObject.Value(GObject.TYPE_INT, 9),         # compression
                GObject.Value(GObject.TYPE_BOOLEAN, True),  # bkgd
                GObject.Value(GObject.TYPE_BOOLEAN, True),  # gamma
                GObject.Value(GObject.TYPE_BOOLEAN, True),  # offs
                GObject.Value(GObject.TYPE_BOOLEAN, True),  # phys
                GObject.Value(GObject.TYPE_BOOLEAN, True),  # time
            ])
            
            # Save the selection mask as PNG
            mask = image.get_selection()
            mask_file = Gio.File.new_for_path(mask_path)
            Gimp.get_pdb().run_procedure("file-png-save", [
                GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
                GObject.Value(Gimp.Image, image),
                GObject.Value(Gimp.Drawable, mask),
                GObject.Value(Gio.File, mask_file),
                GObject.Value(GObject.TYPE_BOOLEAN, False),
                GObject.Value(GObject.TYPE_INT, 9),
                GObject.Value(GObject.TYPE_BOOLEAN, True),
                GObject.Value(GObject.TYPE_BOOLEAN, True),
                GObject.Value(GObject.TYPE_BOOLEAN, True),
                GObject.Value(GObject.TYPE_BOOLEAN, True),
                GObject.Value(GObject.TYPE_BOOLEAN, True),
            ])

            # Initialize GenAI Client
            client = genai.Client(api_key=api_key)

            Gimp.message("Sending request to Gemini (nanobanana)...")
            
            # We assume nanobanana works via edit_image or generate_content
            # We will use edit_image and pass the reference images
            raw_ref_image = types.RawReferenceImage(
                reference_id=1,
                reference_image=types.Image.from_file(img_path),
            )
            mask_ref_image = types.MaskReferenceImage(
                reference_id=2,
                config=types.MaskReferenceConfig(
                    mask_mode='MASK_MODE_PROVIDED_IMAGE',
                    mask_dilation=0,
                ),
            )
            
            # Note: We are using gemini-3-pro-image-preview here based on user context
            response = client.models.edit_image(
                model='gemini-3-pro-image-preview',
                prompt=prompt,
                reference_images=[raw_ref_image, mask_ref_image],
                config=types.EditImageConfig(
                    edit_mode='EDIT_MODE_INPAINT_INSERTION',
                    number_of_images=1,
                    include_rai_reason=True,
                    output_mime_type='image/png',
                ),
            )

            if not response.generated_images:
                Gimp.message("Error: No images returned from the GenAI API.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
                
            res_path = os.path.join(temp_dir, "result.png")
            response.generated_images[0].image.save(res_path)

            # Load the result into GIMP
            res_file = Gio.File.new_for_path(res_path)
            res_image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, res_file)
            if not res_image:
                Gimp.message("Error: Failed to load the result image into GIMP.")
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

            res_drawable = res_image.get_active_layer()

            # Create a new layer in the original image
            new_layer = Gimp.Layer.new(image, "Inpainting Result", 
                                       drawable.get_width(), drawable.get_height(), 
                                       drawable.type(), 100, Gimp.LayerMode.NORMAL)
            image.insert_layer(new_layer, None, -1)

            # Copy buffer from result to new layer
            src_buffer = res_drawable.get_buffer()
            dest_buffer = new_layer.get_buffer()
            dest_buffer.copy(src_buffer, None)
            dest_buffer.flush()

            image.undo_group_end()
            Gimp.displays_flush()

        except Exception as e:
            Gimp.message(f"Exception occurred: {str(e)}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())
        finally:
            # Clean up temp files
            for f in [img_path, mask_path, res_path]:
                if os.path.exists(f):
                    os.remove(f)
            os.rmdir(temp_dir)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(NanobananaInpaint.__gtype__, sys.argv)
