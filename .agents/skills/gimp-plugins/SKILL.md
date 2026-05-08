---
name: gimp-api-docs
description: Navigate and search the local GIMP 3.0 API documentation files.
version: 1.1.0
---

# GIMP 3.0 API Documentation Skill

## Capability

This skill allows agents to efficiently locate and interpret GIMP 3.0 API reference files stored locally. It provides an index of the naming conventions and key entry points for the `libgimp-3.0` and `libgimpui-3.0` libraries.

## Triggers

- User asks for details on a GIMP class (e.g., "What properties does Gimp.Image have?").
- User needs to know how to call a specific PDB function or GIMP method.
- Implementation tasks requiring GIMP UI elements or procedure configurations.
- Any request for "how to" using GIMP 3.0 Python API.

## Instructions

The documentation is split into two main libraries within the skill directory:

1. `libgimp-3.0/`: Core GIMP logic, PDB, Images, Layers, Procedures.
2. `libgimpui-3.0/`: GIMP-specific UI widgets and dialogs.

### File Naming Convention

Files follow a strict pattern based on their GObject type or role:

- **Classes**: `libgimp-3.0/class.<ClassName>.md` (e.g., `class.Image.md`)
- **Methods**: `libgimp-3.0/method.<ClassName>.<MethodName>.md` (e.g., `method.Image.get_layers.md`)
- **Constructors**: `libgimp-3.0/ctor.<ClassName>.<ConstructorName>.md` (e.g., `ctor.Image.new.md`)
- **Static/Class Methods**: `libgimp-3.0/type_func.<ClassName>.<MethodName>.md` (e.g., `type_func.Image.get_by_id.md`)
- **Virtual Methods**: `libgimp-3.0/vfunc.<ClassName>.<VfuncName>.md` (e.g., `vfunc.PlugIn.create_procedure.md`)
- **Properties**: `libgimp-3.0/property.<ClassName>.<PropertyName>.md` (e.g., `property.Image.id.md`)
- **Signals**: `libgimp-3.0/signal.<ClassName>.<SignalName>.md` (e.g., `signal.ColorManaged.profile-changed.md`)
- **Structs**: `libgimp-3.0/struct.<StructName>.md` (e.g., `struct.Parasite.md`)
- **Constants/Enums**: `libgimp-3.0/const.<Name>.md` or `libgimp-3.0/enum.<Name>.md`

### Search Strategy

1. **Find Class**: Always start by reading the `class.<ClassName>.md` file. It contains a list of all available methods and properties.
2. **Locate Member**: Use `ls` with the appropriate prefix (`method.`, `ctor.`, `type_func.`, etc.) to verify the exact file.
3. **Grep for Keywords**: Use `grep_search` within the `libgimp-3.0/` or `libgimpui-3.0/` directories for specific PDB procedure names or keywords if the class is unknown.

## Key Classes Index

### Core GIMP (`libgimp-3.0`)

- `Gimp.PlugIn`: Base class for all plugins.
- `Gimp.Image`: Image handling, layer management, metadata.
- `Gimp.Layer`: Layer properties, masks, transparency.
- `Gimp.Drawable`: Base class for layers and channels (pixel data operations).
- `Gimp.Procedure`: Base class for PDB procedures.
- `Gimp.ImageProcedure`: Specific procedure for image-filtering plugins.
- `Gimp.PDB`: The Procedure Database for calling other GIMP functions.

### GIMP UI (`libgimpui-3.0`)

- `GimpUi.ProcedureDialog`: Automatic dialog generation for plugin settings.
- `GimpUi.Dialog`: Base class for GIMP-styled dialogs.
- `GimpUi.ProcBrowserDialog`: UI for browsing the PDB.

## Examples

**User:** "How do I create a new layer in GIMP 3.0?"
**Action:**

1. Check `libgimp-3.0/class.Layer.md` to see available constructors.
2. Verify `libgimp-3.0/ctor.Layer.new.md` for argument details.

**User:** "How do I show a message to the user?"
**Action:**

1. Search `libgimp-3.0/` for "message".
2. Locate `function.message.md` (if it exists) or search `PDB.md` for messaging procedures.
