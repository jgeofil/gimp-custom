# GIMP Custom Plugins Project

## Project Overview

This project is a collection of GIMP 3.0 plugins written in Python, leveraging generative AI and advanced image editing capabilities. It uses `pygobject` to interface with the GIMP 3.0 API and `uv` for dependency management.

### Key Technologies

- **Python 3.12+**
- **GIMP 3.0 API** (via `pygobject`)
- **uv** (Package & environment management)
- **Markitdown** (Used by conversion scripts)

## Building and Running

### Environment Setup

The project uses `uv`. To set up the development environment:

```bash
# Sync dependencies
uv sync
```

### Running the App

The core logic for building/testing the environment is in `app_build/`:

```bash
# Run the placeholder main script
uv run app_build/main.py
```

### GIMP Plugin Installation (Inferred)

To use these plugins in GIMP 3.0, you typically need to copy the plugin scripts to your GIMP 3.0 plug-ins directory (e.g., `~/.config/GIMP/3.0/plug-ins/`).

## Development Conventions

### GIMP 3.0 API Documentation

A comprehensive local copy of the GIMP 3.0 API documentation is available in:

- `.agents/skills/gimp-plugins/libgimp-3.0/`
- `.agents/skills/gimp-plugins/libgimpui-3.0/`

**Mandatory Workflow for GIMP Development:**

1.  **Activate the Skill:** Use `activate_skill(name="gimp-api-docs")` to receive specialized guidance.
2.  **Consult Docs:** Always check the `.md` files in the paths above before implementing GIMP-specific logic.
3.  **Follow Naming Conventions:**
    - `class.<ClassName>.md` for type overviews.
    - `method.<ClassName>.<MethodName>.md` for specific functionality.

### Plugin Structure

Plugins should follow the GIMP 3.0 `Gimp.PlugIn` and `Gimp.Procedure` patterns. Refer to the examples in `.agents/skills/gimp-plugins/examples/` for reference:

- `simple-plugin.py`: Basic structure.
- `goat-exercise-py3.py`: Comprehensive example of a GIMP 3.0 Python plugin.

## Project Structure

- `.agents/skills/gimp-plugins/`: Core GIMP development resources and API docs.
- `app_build/`: Build configuration and environment setup.
- `productions_artefacts/`: Directory for generated outputs and artifacts.
