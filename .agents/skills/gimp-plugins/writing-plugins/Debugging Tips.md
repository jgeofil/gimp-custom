---
title: "Debugging Tips"
source: "https://developer.gimp.org/core/debug/debugging-tips/"
author:
published: 2017-12-22
created: 2026-05-08
description: "There are a few environment variables, options or other more-or-less known tricks to debug GIMP. Let’s try to add them here for reminder and newcomers.Basics The following tips will help everyone, specially bug reporters, on how to debug GIMP at a basic level.Debugging on AppImage On AppImage, to get more detailed info on stacktraces first ensure you have debuginfod package installed."
tags:
  - "gimp-debugging"
  - "software-development"
  - "troubleshooting"
  - "cross-platform-development"
  - "linux-packages"
  - "stack-traces"
  - "environment-variables"
  - "gegl-debugging"
  - "gtk-tools"
  - "gdb-tutorial"
category: "general"
---
Debugging Tips

There are a few environment variables, options or other more-or-less known tricks to debug GIMP. Let’s try to add them here for reminder and newcomers.

## Basics

The following tips will help everyone, specially bug reporters, on how to debug GIMP at a basic level.

### Debugging on AppImage

On AppImage, to get more detailed info on stacktraces first ensure you have `debuginfod` package installed.

Then, set `DEBUGINFOD_URLS` variable before calling GIMP:

```sh
export DEBUGINFOD_URLS="https://debuginfod.debian.net"
```

Run GIMP as customary. If your debugger supports debuginfod, it will auto download the needed.debug symbols on demand.

```sh
./GIMP*.AppImage --verbose --console-messages
```

### Debugging on Flatpak

In all flatpak commands, replace `--system` with `--user` if GIMP was installed as “user” installation. Also replace `stable` with `beta` or `master` depending from the repository you installed GIMP (the repos are `flathub`, `flathub-beta` and `gnome-nightly` respectively).

On Flatpak, you need to use the sandbox environment, which should be identical on all machines (GNOME.Platform). But we recommend using the.Sdk as environ (instead of the.Platform), since it gives you access to a few additional debug tools, such as `gdb` debugger. So, if you want better stacktraces, first type (outside the sandbox):

```sh
GNOME_SDK_VERSION=\`flatpak remote-info --system flathub org.gimp.GIMP//stable | grep Sdk: | sed 's#.*/##'\`
flatpak install --system org.gnome.Sdk//$GNOME_SDK_VERSION
```

Additionally to install debug symbols useful for the sandbox, run:

```sh
flatpak install --system org.gimp.GIMP.Debug//stable
flatpak install --system org.gnome.Sdk.Debug//$GNOME_SDK_VERSION
```

Then, finally enter the sandbox with “flatpak run” and run GIMP. You can do so by specifying a custom shell instead of the GIMP binary with:

```sh
flatpak run --system --devel --command=bash org.gimp.GIMP//stable
gimp --verbose --console-messages
```

### Debugging on Snap

To debug GIMP Snap, since the sandbox is privileged, you need to debug “remotely” with the sandbox serving an unprivileged client/debugger:

```sh
snap run --gdbserver gimp --verbose --console-messages
```

This assumes you know how to use gdbserver. If not, see [Debugging though gdbserver](#debugging-though-gdbserver) section.

### Debugging on Windows

Go to Start Menu, type “PowerShell” (not PowerShell ISE), then open it.

For a installation from the.exe installer, run the following:

```pwsh
& "$(Get-ItemProperty Registry::'HKEY_*\Software\Microsoft\Windows\CurrentVersion\Uninstall\GIMP-3*' | Select-Object -ExpandProperty InstallLocation)bin\gimp" --verbose --console-messages
```

For the Store/MSIX package, enter:

```pwsh
gimp-3 --verbose --console-messages
```

### Debugging on macOS

Go to Applications/Utilities, then Terminal.

Enter:

```sh
/Applications/GIMP.app/Contents/MacOS/gimp --verbose --console-messages
```

### Debug logs

There are various `GIMP_LOG()` calls in the code. These will only be outputted when you set `GIMP_DEBUG` environment variable to a comma-separated list of domain. For instance, for `GIMP_LOG (XCF, "some string")` to be outputted, before running GIMP, set something like this (on Linux and macOS):

```sh
export GIMP_DEBUG=xcf
```

On Windows PowerShell, it would be:

```pwsh
$env:GIMP_DEBUG='xcf'
```

Special flags are:

- “all” to output all domain logs;
- “list-all” to get a list of available domains.

### Debugging a warning or critical

Logging levels helps to developers to understand the bug severity. Its use is by convention, and libraries that GIMP uses may not follow conventions. Generally speaking:

- WARNINGs (engendered by `g_warning()`) are common but don’t signify much. They might mean there is something wrong regarding API usage.
- CRITICALs (engendered by `g_return_value_if_fail()` or `g_return_if_fail()`) are rare but more significant. They usually mean that GIMP will attempt to continue past an errant condition.
- ERRORs (engendered by `g_assert()` or `g_error()`) are usually dire. They always terminate a process.

If you encounter a CRITICAL or WARNING message on console, GIMP will not generate a stacktrace by default. To get that, go to **Preferences > Debugging**, and make sure that all type of errors are debugged. Then a graphical dialog will automatically appear upon encountering any WARNING or CRITICAL (except on Windows due to DrMingw limitations).

Alternatively, to catch them while running a debugger, you can make so that GIMP crashes on it, which will make it easy to be tracked down, by running GIMP with **`--g-fatal-warnings`**. For example:

```sh
gdb --args gimp --g-fatal-warnings #on Linux
cdb gimp --g-fatal-warnings #on Windows
lldb -- gimp --g-fatal-warnings #on macOS
```

Note that running GIMP with the CLI option `--stack-trace-mode` to values “query” or “always” will output a stacktrace on terminal, [even for plug-ins](https://developer.gimp.org/resource/debug/#gimp_plugin_debug-and-stack-trace-mode), but it does not work for `WARNING` s and `CRITICAL` s here.

## Debugging specific cases

The following tips are more advanced and can be useful on special cases.

### Debugging GTK

You can use GtkInspector to check the CSS theme among other things by setting, before running GIMP, `GTK_DEBUG` to “interactive”.

On Linux, you may also start it at anytime with `ctrl-shift-d` shortcut (or `ctrl-shift-i` to inspect the focused widget), if you first enable with:

```sh
gsettings set org.gtk.Settings.Debug enable-inspector-keybinding true
```

Note also that running GIMP with `GDK_SCALE=2` (or other values) allow to test the interface in another scaling than your native one. This settings is also available in the GtkInspector.

### Debugging babl

Profile conversion is done with babl by default when possible, which is much faster. Setting `GIMP_COLOR_TRANSFORM_DISABLE_BABL` environment variable switch back to the old lcms implementation, which can be useful for comparison.

### Debugging GEGL code

You may encounter this kind of warning upon exiting GIMP:

> EEEEeEeek! 2 GeglBuffers leaked

To debug GeglBuffer leaks, make sure you built GEGL with `-Dbuildtype=debug` or `-Dbuildtype=debugoptimized` (your system also needs to have the header `execinfo.h`), and set the environment variable `GEGL_DEBUG` to “buffer-alloc”.

### Debugging the menu-bar

Our implementation of the menubar if customized by the `GimpMenuBar` class (macOS is the exception since we use proper macOS API there).

If you want to test the old GTK code path (`GimpMenuModel` class), you can run GIMP with the environment variable `GIMP_GTK_MENUBAR` set to “1”.

### Debugging fonts

The environment variable `GIMP_DEBUG_FONTS` will have GIMP list all ignored fonts on startup, with some basic information on why they were ignored.

### Testing older GIMP versions

A useful trick when you want to quickly test a specific GIMP older version (e.g. to confirm a behavior change) is to install it with our official flatpak. The flathub repository stores past builds (up to 20 at the time of writing). You can list them with the following command:

```sh
flatpak remote-info --system --log flathub org.gimp.GIMP//stable
```

Each build will have a “Subject” line (a comment to indicate the build reason, it may be just dependency updates or build fixes, or sometimes a bump in GIMP version) and a commit hash. When you have identified the build you want to test, update it like this:

```sh
flatpak update --system --commit=<hash-of-build> org.gimp.GIMP//stable
```

Then just run your older GIMP!

### Getting accurate traces from reported inaccurate traces

Even with reporter trace without debug symbols (yet debug symbols installed on your side), if you make sure you use exactly the same flatpak commit as the reporter (see [Testing older GIMP versions](#testing-older-gimp-versions) section) or the exact same.appimage,.snap,.exe installer,.msix or.dmg, you are ensured to use the same binaries. Hence you can trace back the code line from an offset.

For instance, say that your trace has this output:

```sh
gimp(file_open_image+0x4e8)[0x5637e0574738]
```

Here is how you can find the proper code line:

```sh
gdb gimp
(gdb) info line *(file_open_image+0x4e8)
Line 216 of "file-open.c" starts at address 0x4d5738 <file_open_image+1256> and ends at 0x4d5747 <file_open_image+1271>.
```

### Debugging though gdbserver

In some cases, when GIMP grabs the pointer and/or keyboard, i.e. when you debug something happening on canvas in particular, it might be very hard to get back to your debugger, since your system won’t be responding to your keyboard or click events.

To work around this, you can debug remotely, or simply from a TTY (while the desktop doesn’t answer properly):

In your desktop, run GIMP through a debugger server:

```sh
gdbserver gimp
```

Go to a TTY and run

```sh
gdb gimp
(gdb) target remote localhost:9999
(gdb) continue
```

Of course, before the `continue`, you may add whatever break points or other commands necessary for your specific issue. GIMP will start in the desktop when you hit `continue` (it will likely be a slower start).

Then do your issue reproduction steps on GIMP. When you need to debug, you can go to the TTY whenever you want, not bothering about any keyboard/pointer grabs.

Note that since copy-pasting is harder in a TTY, you might want to redirect your output to a file, especially if you need to upload it or read it slowly next to GIMP code. For instance here are commands to output a full backtrace into a file from the gdb prompt and exit (to force the device ungrab by killing GIMP and go work on desktop again):

```sh
(gdb) set logging file gimp-issue-1234.txt
(gdb) set logging on
(gdb) thread apply all backtrace full
(gdb) quit
```

### Debugging plug-ins

The process of debugging plug-ins is the most complex. So, you should look at [Debugging Plug-ins](https://developer.gimp.org/resource/debug/debug-plug-ins/) dedicated page.

Last updated on