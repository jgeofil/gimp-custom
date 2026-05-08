---
title: "Python Plug-Ins"
source: "https://developer.gimp.org/resource/writing-a-plug-in/tutorial-python/"
author:
published: 2025-02-13
created: 2026-05-07
description: "Write a Python plug-in for GIMP 3.0"
tags:
  - "gimp-3-0"
  - "python-plug-ins"
  - "gobject-introspection"
  - "api-bindings"
  - "tutorial"
  - "procedural-database"
  - "gimp-development"
  - "libgimp"
  - "libgimpui"
category: "general"
---
Python Plug-Ins

## \[Theory\] Introduction

Both our `libgimp` and `libgimpui` libraries are introspected thanks to the [`GObject-Introspection`](https://gi.readthedocs.io/en/latest/) project. It means that the Python API is actually nearly exactly the same as the C library, except it follows Python language idiosyncrasies.

For instance, the signature of [`gimp_layer_get_blend_space()`](https://developer.gimp.org/api/3.0/libgimp/method.Layer.get_blend_space.html) in C is:

```c
GimpLayerColorSpace gimp_layer_get_blend_space (GimpLayer* layer);
```

Here it is in Python:

```py3
In [2]: Gimp.Layer.get_blend_space.__doc__
Out[2]: 'get_blend_space(self) -> Gimp.LayerColorSpace'
```

Now where it gets interesting is when you have several return values. In C, this would be implemented as pointers to values. In Python, we can actually have several return values. Therefore while [`gimp_drawable_get_offsets()`](https://developer.gimp.org/api/3.0/libgimp/method.Drawable.get_offsets.html) ’s signature looks like this in C (with 3 return values: a boolean `success` and 2 integer offsets):

```c
gboolean gimp_drawable_get_offsets (GimpDrawable *drawable,
                                    gint         *offset_x,
                                    gint         *offset_y);
```

This is in Python:

```py3
In [3]: Gimp.Drawable.get_offsets.__doc__
Out[3]: 'get_offsets(self) -> bool, offset_x:int, offset_y:int'
```

It typically means that if you had a `GimpDrawable` variable named `drawable`, you’d call:

```py3
success, x_offset, y_offset = drawable.get_offsets()
```

Notice also how we don’t call `Gimp.Drawable.get_offsets(drawable)` but `drawable.get_offsets()`, i.e. that `get_offsets()` is really a method to the `drawable` object (of type `Gimp.Drawable`). This makes for a very Python-style interface!

Not only this, it is also full-featured. Only very few `libgimp` or `libgimpui` functions are not available in bindings, and only because this is not supported by `GObject-Introspection`. For instance the `varargs` functions (variable-length arguments à-la `printf`) don’t have a Python version. Instead though, non-varargs versions always exist so that bindings can still do absolutely everything which the C API can do.

This all makes the C API reference very usable even to develop Python plug-ins. Nevertheless if you would prefer a reference specifically dedicated to the Python binding, there exists some third-party documentation:

- [libgimp API in Python](https://lazka.github.io/pgi-docs/#Gimp-3.0)
- [libgimpui API in Python](https://lazka.github.io/pgi-docs/#GimpUi-3.0)

## \[Theory\] What about Other Bindings?

This tutorial will only propose a Python 3 version, but we theoretically support all languages bindable with `GObject-Introspection`.

Additionally to [Python 3](https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-py3.py), we also have demo code for:

- [Lua](https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-lua.lua)
- [Javascript](https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-gjs.js)
- [Vala](https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-vala.vala)

They all implement the same as this [C demo plug-in](https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-c.c).

Note however that we have memory issues with the **Lua** binding (which is why we disable it by default) and that the **Javascript** binding is not currently enabled on Windows because packaging an interpreter turned out to be quite a challenge. As for the **Vala** binding, as far as we know, it works well, except that the generated code outputs many annoying warnings. Moreover it is a compiled language and we believe that most people doing plug-ins are more interested into interpreted script languages for quicker development.

Python, on the other hand, along with C, is one of the few languages that is available on all platforms where GIMP runs, and, as said above, is nearly the same as the C API, having unmatched feature parity.

This is why we are mostly focusing on the Python 3 API only for now.

## \[Code\] Reimplementing Hello World in Python 3

I am going to assume you read at least the `[Theory]` sections of the previous tutorials and will reimplement the whole demo plug-in we made in C at once in Python 3. Here is what it would look like:

```py3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
import sys

plug_in_proc   = "plug-in-zemarmot-py3-demo-hello-world"
plug_in_binary = "py3-hello-world"

def hello_world_run(procedure, run_mode, image, drawables, config, data):
  if len(drawables) > 1:
    return procedure.new_return_values (Gimp.PDBStatusType.CALLING_ERROR,
                                        GLib.Error(f"Procedure '{plug_in_proc}' works with zero or one layer."))
  elif len(drawables) == 1:
    if not isinstance(drawables[0], Gimp.Layer):
      return procedure.new_return_values (Gimp.PDBStatusType.CALLING_ERROR,
                                          GLib.Error(f"Procedure '{plug_in_proc}' works with layers only."))

    parent   = drawables[0].get_parent ()
    position = image.get_item_position (drawables[0])

  if run_mode == Gimp.RunMode.INTERACTIVE:
    gi.require_version('GimpUi', '3.0')
    from gi.repository import GimpUi

    GimpUi.init(plug_in_binary)

    dialog = GimpUi.ProcedureDialog.new(procedure, config, "Hello World")
    box = dialog.fill_box("size-box", ["font-size", "font-unit"])
    box.set_orientation (Gtk.Orientation.HORIZONTAL)
    dialog.fill_frame("size-frame", "compute-size", True, "size-box")
    dialog.fill(["text", "font", "size-frame"])
    if not dialog.run():
      dialog.destroy()
      return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
    else:
      dialog.destroy()

  text         = config.get_property('text')
  font         = config.get_property('font')
  compute_size = config.get_property('compute-size')
  size         = config.get_property('font-size')
  unit         = config.get_property('font-unit')

  image.undo_group_start()
  text_layer = Gimp.TextLayer.new (image, text, font, size, unit)
  image.insert_layer (text_layer, parent, position)
  if compute_size:
    image_width = image.get_width()
    layer_width = text_layer.get_width()

    size = size * (image_width - 1) / layer_width
    text_layer.set_font_size(size, Gimp.Unit.pixel())

    while size > 1:
      layer_width = text_layer.get_width()

      if layer_width < image_width:
        break

      size -= 1
      text_layer.set_font_size(size, Gimp.Unit.pixel())

  image.undo_group_end()

  return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class HelloWorld (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]

  def do_create_procedure(self, name):
    procedure = None

    if name == plug_in_proc:
      procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          hello_world_run, None)
      procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                      Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
      procedure.set_menu_label("_Python 3 Hello World")
      procedure.set_attribution("Jehan", "Jehan, ZeMarmot project", "2025")
      procedure.add_menu_path ("<Image>/Hell_o Worlds")
      procedure.set_documentation ("Official Hello World Tutorial in Python 3",
                                   "Some longer text to explain about this procedure. " + \
                                   "This is mostly for other developers calling this procedure.",
                                   None)

      procedure.add_string_argument  ("text", "Text", None, "Hello World!",
                                      GObject.ParamFlags.READWRITE)
      procedure.add_font_argument    ("font", "Font", None, False, None, True,
                                      GObject.ParamFlags.READWRITE)
      procedure.add_boolean_argument ("compute-size", "Compute Ideal Size",
                                      "This option will compute a font size " + \
                                      "so that the text optimally fills the whole canvas",
                                      False, GObject.ParamFlags.READWRITE)
      procedure.add_int_argument     ("font-size", "Font Size", None,
                                      1, 1000, 20, GObject.ParamFlags.READWRITE)
      procedure.add_unit_argument    ("font-unit", "Font Unit", None,
                                      True, False, Gimp.Unit.pixel(),
                                      GObject.ParamFlags.READWRITE)

    return procedure

Gimp.main(HelloWorld.__gtype__, sys.argv)
```

## \[Theory\] Studying the Python Hello World

### Interpreter and Encoding

The first lines are very standard:

```py3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

We start our script with a `shebang` so that your OS kernel (or through [cross-platform rules](https://docs.python.org/3/using/windows.html#shebang-lines)) finds the interpreter. In fact GIMP has its own infrastructure and may also override the interpreter in some cases. As a general rule, just always set your standard shebang line.

The second line is quite a standard [encoding declaration](https://docs.python.org/3/reference/lexical_analysis.html#encoding-declarations). Though it is not mandatory, it is quite a good practice, especially as various `GLib` or `libgimp` functions expects input to be proper UTF-8.

### Modules

In place of including `libgimp` and `libgimpui`, you `import` the 2 modules, respectively named `Gimp` and, later on the run function, `GimpUi` from the `gi` module. Even though we only have a ‘3.0’ version right now, you should always set the version.

A few more modules are needed because we will use explicit API from these: `GObject`, `GLib`, `Gtk` also from `gi` and the `sys` module from standard library.

```py3
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('Gegl', '0.4')
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
import sys
```

### Subclassing in Python

Now [same as in C](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-c-basic#theory-plug-in-structure), we create the `HelloWorld` class as a subclass of `Gimp.PlugIn`, except it uses Python subclassing. You will note also that all the abstract methods which you are expected to implement are prefixed by `do_`. Apart from this, it works pretty much the same:

```py3
class HelloWorld (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]

  def do_create_procedure(self, name):
    procedure = None

    if name == plug_in_proc:
      procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          hello_world_run, None)
      procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                      Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
      procedure.set_menu_label("_Python 3 Hello World")
      procedure.set_attribution("Jehan", "Jehan, ZeMarmot project", "2025")
      procedure.add_menu_path ("<Image>/Hell_o Worlds")
      procedure.set_documentation ("Official Hello World Tutorial in Python 3",
                                   "Some longer text to explain about this procedure. " + \
                                   "This is mostly for other developers calling this procedure.",
                                   None)

      procedure.add_string_argument  ("text", "Text", None, "Hello World!",
                                      GObject.ParamFlags.READWRITE)
      procedure.add_font_argument    ("font", "Font", None, False, None, True,
                                      GObject.ParamFlags.READWRITE)
      procedure.add_boolean_argument ("compute-size", "Compute Ideal Size",
                                      "This option will compute a font size " + \
                                      "so that the text optimally fills the whole canvas",
                                      False, GObject.ParamFlags.READWRITE)
      procedure.add_int_argument     ("font-size", "Font Size", None,
                                      1, 1000, 20, GObject.ParamFlags.READWRITE)
      procedure.add_unit_argument    ("font-unit", "Font Unit", None,
                                      True, False, Gimp.Unit.pixel(),
                                      GObject.ParamFlags.READWRITE)

    return procedure
```

### Reimplementing the Core Processing

The `hello_world_run()` function is also quite similar, except that it uses Python idiosyncrasies:

- `drawables` is a standard Python list of [`Gimp.Drawable`](https://lazka.github.io/pgi-docs/#Gimp-3.0/classes/Drawable.html) objects.
- Its length can therefore be verified with the generic `len()` function.
- C `NULL` is replaced by Python `None`.
- Checking for real type of an object in python works well with [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) (all the `GIMP_IS_` macros from C don’t exist in Python).

You will also notice that the various `config` properties must be requested one by one with `config.get_property()`. This is because of what I was saying in the [introduction](#theory-introduction) about variable-length arguments functions which are among the few cases of non-bindable API.

### The Gimp.main() function

Finally the Python plug-in ends with a call to [`Gimp.main()`](https://lazka.github.io/pgi-docs/#Gimp-3.0/functions.html#Gimp.main). As explained in the [C basic tutorial](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-c-basic#theory-plug-in-structure), the `GIMP_MAIN` macro is C-only. You must pass the `GType` of your custom `Gimp.PlugIn` class as first parameter, which in Python is the `__gtype__` argument of the class name. The second argument is the list of arguments passed to this executable, which is why we also imported `sys`:

```py3
Gimp.main(HelloWorld.__gtype__, sys.argv)
```

Apart from this, the whole code is pretty similar in C and Python. It is also a lot shorter because most of the C boilerplate code doesn’t exist in the Python 3 version.

## \[Theory\] File Architecture

First of all, installing any plug-in is identical in GIMP, which means you must create a folder [in your `plug-ins/` directory](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-c-basic/#theory-file-architecture) and put your Python file in this folder with the same name (only adding the `.py` extension).

For instance, if you write your code in a file named `py3-hello-world.py`, install it in a directory named `py3-hello-world/`.

Then make sure your script file is executable, in the case where you are on a platform where this matters (which is probably any OS but Windows):

```sh
chmod u+x py3-hello-world.py
```

Now if you restart GIMP, it should pick up your plug-in.

## Calling a PDB Procedure in Python

Calling a PDB procedure from a Python (or other bindings) plug-ins is slightly longer than [in C](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-pdb#code-calling-your-hello-world-plug-in), again for the same reason of non-bindable functions with variable-length arguments. This makes [`gimp_procedure_run()`](https://developer.gimp.org/api/3.0/libgimp/method.Procedure.run.html) not bindable, and instead replaced by [`gimp_procedure_run_config()`](https://developer.gimp.org/api/3.0/libgimp/method.Procedure.run_config.html) which is renamed to [`Gimp.Procedure.run()`](https://testing.developer.gimp.org/api/3.0/libgimp/method.Procedure.run_config.html) in Python.

Furthermore, since we cannot use [`g_object_set()`](https://docs.gtk.org/gobject/method.Object.set.html) in Python (still for the same reason), we must set properties with multiple commands. Nevertheless it stays quite simple to call a PDB procedure. And the equivalent to the [C code](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-pdb#code-calling-your-hello-world-plug-in) is:

```py3
procedure = Gimp.get_pdb().lookup_procedure('plug-in-zemarmot-c-demo-hello-world')
config    = procedure.create_config()
config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
config.set_property('image', image)
config.set_property('text', 'Hello Universe!')
config.set_property('compute-size', True)
result = procedure.run(config)

if result.index(0) is Gimp.PDBStatusType.SUCCESS:
  # Do something in case of success!
```

If anyone has a very keen eye for details, you may have noted that I called “plug-in-zemarmot-c-demo-hello-world” which is the procedure name for the C Hello World. I did this on purpose to really make clear that PDB procedures are absolutely language-agnostic.

You may call a C plug-in procedure from a Python plug-in, a Python plug-in procedure from a C plug-in, and obviously a Python procedure from a Python plug-in or a C procedure from a C plug-in. You can further mix by calling Javascript plug-in procedures, Lua, Script-Fu… anything! It simply doesn’t matter. Once a procedure has been registered in the Procedural DataBase, it is a neutral interface with a name and various arguments. That’s all!

## Conclusion

And that’s about it. If you followed the C tutorial first, the Python tutorial should be pretty straightforward as all the concepts are the same. The `Gimp` and `GimpUi` modules are nearly a perfect mapping of the C libraries.

You will also notice how there is absolutely no styling difference with Python plug-ins in the graphical interface and how no features are missing. Basically from the point of view of people using your plug-ins, it makes not a single difference in which language the plug-in is made. They can’t even know (apart by checking the code, of course).

- Back to [“How to write a plug-in” tutorial index](https://developer.gimp.org/resource/writing-a-plug-in/)
- Previous tutorial: [C plug-ins - Procedure DataBase](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-pdb)
- Next tutorial: [Script-Fu plug-ins](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-script-fu)

Last updated on