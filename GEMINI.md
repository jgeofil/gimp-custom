# gimp-custom

The `gimp-custom` project is a collection of custom GIMP plug-ins written in Python 3, designed for GIMP 3.0. It leverages GObject Introspection (`gi`) to provide deep integration with GIMP's core and UI.

## Project Overview

- **Purpose:** Developing and managing custom Python plug-ins for GIMP 3.0.
- **Tech Stack:**
    - **Language:** Python (>= 3.12)
    - **Core Libraries:** `pygobject` (GObject Introspection), `Gimp 3.0`, `Gegl 0.4`, `Gtk 3.0`.
    - **Environment:** Managed with `uv`.

## Directory Structure

- `plug-ins/`: Root directory for all custom GIMP plug-ins.
    - `colorxhtml/`: Plug-in for exporting as colorized XHTML.
    - `foggify/`: Adds a fog layer to an image.
    - `python-console/`: Provides an interactive Python console within GIMP.
    - `spyro-plus/`: Advanced spirograph-like drawing tool.
- `goat-exercise-py3.py`: A reference implementation of a GIMP 3 Python plug-in.
- `pyproject.toml`: Defines project metadata and dependencies (`pygobject`).

## Development Guide

### GIMP 3.0 Plug-in Architecture

Plug-ins in this repository follow the GIMP 3.0 architecture:

1.  **Inheritance:** Classes inherit from `Gimp.PlugIn`.
2.  **Registration:** Implement `do_query_procedures` to return procedure names and `do_create_procedure` to define the procedure's metadata (menu path, arguments, documentation).
3.  **Execution:** The `run` method handles the plug-in logic, often using GEGL for image processing.

### Key Snippet: Plug-in Initialization

```python
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

class MyPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["my-plugin-name"]
    # ...
```

## Setup and Installation

### Prerequisites

- GIMP 3.0 (Development version or nightly as required for API compatibility).
- Python 3.12+.
- `uv` package manager.

### Installation

1.  Clone the repository.
2.  Sync dependencies:

    ```bash
    uv sync
    ```

3.  To use the plug-ins in GIMP, link or copy the desired plug-in folders into your GIMP plug-ins directory:
    - Linux: `~/.config/GIMP/3.0/plug-ins/`

## Testing and Validation

- **Linting:** Use `ruff` or `flake8` to ensure Python code quality.
- **Manual Verification:** Load the plug-in into GIMP and verify its appearance in the specified menu path (e.g., `<Image>/Filters/Development/`).
