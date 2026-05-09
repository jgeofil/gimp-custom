import os
import subprocess
import tempfile
import shutil
import pytest

@pytest.mark.skipif(shutil.which("gimp") is None and shutil.which("gimp-console-3.0") is None,
                    reason="GIMP 3.0+ is required for integration tests")
def test_plugin_registration_and_execution_in_gimp():
    # Find gimp executable
    gimp_exe = shutil.which("gimp-console-3.0") or shutil.which("gimp")
    
    # We will create a temporary directory to act as the GIMP profile
    # so we can safely inject our plugin without messing with the user's setup.
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as tmpdir:
        plugin_dir = os.path.join(tmpdir, "plug-ins", "nanobanana_inpaint")
        os.makedirs(plugin_dir)
        
        # Get absolute path to the plugin script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nanobanana_inpaint.py"))
        
        # Symlink or copy the script into the plugin directory
        target_script = os.path.join(plugin_dir, "nanobanana_inpaint.py")
        with open(script_path, "r") as f:
            script_content = f.read()
        
        # Replace custom venv shebang with standard env python3 for GIMP to execute properly
        if script_content.startswith("#!"):
            script_content = "#!/usr/bin/env python3\n" + script_content.split("\n", 1)[1]
            
        with open(target_script, "w") as f:
            f.write(script_content)
        os.chmod(target_script, 0o755)

        # Create a custom gimprc that adds this directory to the plug-in path
        gimprc_path = os.path.join(tmpdir, "gimprc")
        with open(gimprc_path, "w") as f:
            f.write(f"(plug-in-path \"${{gimp_plug_in_dir}}/plug-ins:{os.path.join(tmpdir, 'plug-ins')}\")\n")

        # The python script to run inside GIMP's batch interpreter
        batch_script = """
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, GObject
import sys

def run_test():
    pdb = Gimp.get_pdb()
    # 1. Verify the procedure is registered
    proc = pdb.lookup_procedure('nanobanana-inpaint')
    if not proc:
        print("TEST_FAILED: Procedure not found in PDB")
        return

    # 2. Test execution (we expect an error because there's no active drawable/image by default)
    # The arguments are: run_mode, image, drawables, prompt, model, crop-context, position-layer, creativity, api-key
    
    config = proc.create_config()
    config.set_property("prompt", "test prompt")
    config.set_property("model", "gemini-3-pro-image-preview")
    config.set_property("api-key", "dummy-key")
    
    # We will just run it without setting an image or drawables, so it should fail gracefully
    # and return an execution error instead of crashing.
    result = proc.run(config)
    status = result.index(0) if result.length() > 0 else None
    
    # Check if the plugin failed gracefully
    import os
    out_path = os.path.join(sys.path[-1], "result.txt")
    with open(out_path, "w") as f:
        if status in (Gimp.PDBStatusType.EXECUTION_ERROR, Gimp.PDBStatusType.CALLING_ERROR):
            f.write("TEST_PASSED")
        else:
            f.write(f"TEST_FAILED: Expected EXECUTION_ERROR or CALLING_ERROR, got {status}")

run_test()

"""
        
        # Save the batch script
        batch_path = os.path.join(tmpdir, "batch.py")
        with open(batch_path, "w") as f:
            f.write(batch_script)

        # Run GIMP headlessly
        cmd = [
            gimp_exe,
            "-i", # headless
            "--quit", # quit after batch
            "-c", # console messages
            "-g", gimprc_path, # custom gimprc
            "--batch-interpreter", "python-fu-eval",
            "-b", f"import sys; sys.path.append('{tmpdir}'); import batch"
        ]

        # Use environment variables to set the config path to our tmpdir if possible
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = tmpdir
        # Ensure we don't accidentally load UI plugins that might hang
        env["GEGL_USE_OPENCL"] = "no"

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        result_path = os.path.join(tmpdir, "result.txt")
        test_passed = False
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                if "TEST_PASSED" in f.read():
                    test_passed = True
        
        if not test_passed:
            output = result.stdout + result.stderr
            print("GIMP Output:\n", output)
            if os.path.exists(result_path):
                print("Result file content:\n", open(result_path).read())
            pytest.fail("Integration test failed to register and execute the plugin gracefully in a real GIMP environment.")
