# GIMP Custom Plugins Project

This project is a collection of GIMP plugins written in Python, targeting the **GIMP 3.0 API**. It leverages `pygobject` for introspection and includes tools for generative AI, image editing, and more.

## Project Overview

- **Core Technologies:** Python 3.12+, GIMP 3.0 (via PyGObject), GEGL 0.4, GTK 3.0.
- **Dependency Management:** Managed by `uv`.
- **Documentation:** A local copy of the GIMP 3.0 API reference is available in the `reference/` directory. For help navigating it, see `reference/SKILL.md`.

## Directory Structure

- `plug-ins/`: Active plugins. Each plugin typically resides in its own subdirectory.
- `dev-plugins/`: Example plugins and experimental scripts for development reference.
- `reference/`: Markdown-formatted API documentation for `libgimp-3.0` and `libgimpui-3.0`.
- `pyproject.toml`: Project configuration and dependencies.

## Development Guidelines

### Creating a New Plugin

Follow the standard GIMP 3.0 Python plugin structure:

1.  **Subclass `Gimp.PlugIn`**:
    ```python
    class MyPlugin(Gimp.PlugIn):
        def do_query_procedures(self):
            return ["my-procedure-name"]

        def do_create_procedure(self, name):
            # Create and configure Gimp.Procedure or Gimp.ImageProcedure
            procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run, None)
            # ... set menu, documentation, arguments ...
            return procedure

        def run(self, procedure, run_mode, image, drawables, config, run_data):
            # Implementation logic here
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    ```

2.  **Entry Point**:
    ```python
    if __name__ == "__main__":
        Gimp.main(MyPlugin.__gtype__, sys.argv)
    ```

### API Reference

When looking for GIMP-specific functions, classes, or constants, prioritize checking the files in `reference/libgimp-3.0/`. 

**Navigation Tips:**
- Refer to `reference/SKILL.md` for a complete index of naming conventions and search strategies.
- Common entry points include:
    - `class.PlugIn.md`: Base class information.
    - `class.Image.md`: Image manipulation.
    - `class.Layer.md`: Layer operations.
    - `class.Procedure.md`: Procedure registration and configuration.

### Coding Style & Conventions

- **Initialization**: Use `gi.require_version('Gimp', '3.0')` before importing from `gi.repository`.
- **UI**: For interactive plugins, use `GimpUi.ProcedureDialog` to automatically generate dialogs from procedure arguments.
- **Internationalization**: Most plugins use `gettext` or `GLib.dgettext` for translation support.

## Building and Running

### Environment Setup

Use `uv` to manage the local virtual environment:

```bash
uv sync
source .venv/bin/activate
```

### Installation

To test plugins in GIMP, they generally need to be symlinked or copied into your GIMP 3.0 preferences folder (e.g., `~/.config/GIMP/3.0/plug-ins/`).

### Testing

The project is configured for `pytest`.
```bash
uv run pytest
```
*(Note: Many GIMP plugins require a running GIMP environment or mocked GIMP objects for full testing.)*
