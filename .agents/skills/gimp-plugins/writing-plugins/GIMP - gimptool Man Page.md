---
title: "GIMP - gimptool Man Page"
source: "https://www.gimp.org/man/gimptool.html"
author:
published:
created: 2026-05-07
description: "NAME¶ gimptool - script to perform various GIMPy functions SYNOPSIS¶ gimptool [—prefix[=DIR]] [—exec-prefix[=DIR]] [—version] [—help] [—quiet] [—silent] [-n] [—just-print] [—dry-run] [—recon] [—msvc-syntax] [—bindir] [—sbindir] [—libexecdir] [—datadir] [—sysconfdir] [—sharedstatedir] [—localstatedir] [—libdir] [—infodir] [—mandir] [—includedir] [—gimpplugindir] [—gimpdatadir] [—libs] [—libs-noui] [—cflags] [—cflags-noi] [—build plug-in.c] [—build-strip plug-in.c] [—install plug-in.c] [—install-strip …"
tags:
    - "gimptool"
    - "gimp-plugin-development"
    - "cli-tool"
    - "software-compilation"
    - "linux-man-page"
    - "build-automation"
    - "plugin-installation"
    - "gimp-scripts"
category: "general"
---

## gimptool Man Page

## NAME

gimptool - script to perform various GIMPy functions

## SYNOPSIS

**gimptool** \[—prefix _\[=DIR\]_\] \[—exec-prefix _\[=DIR\]_\] \[—version\] \[—help\] \[—quiet\] \[—silent\] \[-n\] \[—just-print\] \[—dry-run\] \[—recon\] \[—msvc-syntax\] \[—bindir\] \[—sbindir\] \[—libexecdir\] \[—datadir\] \[—sysconfdir\] \[—sharedstatedir\] \[—localstatedir\] \[—libdir\] \[—infodir\] \[—mandir\] \[—includedir\] \[—gimpplugindir\] \[—gimpdatadir\] \[—libs\] \[—libs-noui\] \[—cflags\] \[—cflags-noi\] \[—build _plug-in.c_\] \[—build-strip _plug-in.c_\] \[—install _plug-in.c_\] \[—install-strip _plug-in.c_\] \[—install-admin _plug-in.c_\] \[—install-bin _plug-in_\] \[—install-admin-strip _plug-in.c_\] \[—install-bin-strip _plug-in_\] \[—install-admin-bin _plug-in_\] \[—install-script _script.scm_\] \[—install-admin-script _script.scm_\] \[—uninstall-bin _plug-in_\] \[—uninstall-admin-bin _plug-in_\] \[—uninstall-script _script.scm_\] \[—uninstall-admin-script _script.scm_\]

## DESCRIPTION

_gimptool_ is a tool that can, among other things, build plug-ins or scripts and install them if they are distributed in one source file.

_gimptool_ can also be used by programs that need to know what libraries and include-paths _GIMP_ was compiled with. _gimptool_ uses _pkg-config_ for this task. For use in Makefiles, it is recommended that you use _pkg-config_ directly instead of calling _gimptool_.

## OPTIONS

_gimptool_ accepts the following options:

**version**

Print the currently installed version of _GIMP_ on the standard output.

**help**

Print out the help blurb, showing commonly used commandline options.

**quiet**

Run quietly without echoing any of the build commands.

**silent**

Run silently without echoing any of the build commands. Same as —quiet.

**\-n**

Test mode. Print the commands but don't actually execute them. Useful for making dry runs for testing.

**just-print**

Test mode. Print the commands but don't actually execute them. Same as -n.

**dry-run**

Test mode. Print the commands but don't actually execute them. Same as -n.

**recon**

Test mode. Print the commands but don't actually execute them. Same as -n.

**msvc-syntax**

Useful on Windows. Outputs the compiler and linker flags in the syntax used by Microsoft's toolchain. Passed to the pkg-config command that does most of _gimptool_ 's work.

**bindir**

Outputs the bindir used to install the _GIMP_.

**sbindir**

Outputs the sbindir used to install the _GIMP_.

**libexecdir**

Outputs the libexecdir used to install the _GIMP_.

**datadir**

Outputs the datadir used to install the _GIMP_.

**sysconfdir**

Outputs the sysconfdir used to install the _GIMP_.

**sharedstatedir**

Outputs the sharedstatedir used to install the _GIMP_.

**localstatedir**

Outputs the localstatedir used to install the _GIMP_.

**libdir**

Outputs the libdir used to install the _GIMP_.

**infodir**

Outputs the infodir used to install the _GIMP_.

**mandir**

Outputs the mandir used to install the _GIMP_.

**includedir**

Outputs the includedir used to install the _GIMP_.

**gimpdatadir**

Outputs the actual directory where the _GIMP_ data files were installed.

**gimpplugindir**

Outputs the actual directory where the _GIMP_ plug-ins were installed.

**build _plug-in.c_**

Compile and link _plug-in.c_ into a _GIMP_ plug-in.

**build-strip _plug-in.c_**

Compile,link, and strip _plug-in.c_ into a _GIMP_ plug-in.

**install _plug-in.c_**

Compile, link, and install _plug-in.c_ into the user's personal _GIMP_ plug-in directory (\\$XDG_CONFIG_HOME/GIMP/3.2/plug-ins)

**install-strip _plug-in.c_**

Compile, link,strip, and install _plug-in.c_ into the user's personal _GIMP_ plug-in directory (\\$XDG_CONFIG_HOME/GIMP/3.2/plug-ins)

**install-admin _plug-in.c_**

Compile, link, and install _plug-in.c_ into the system-wide _GIMP_ plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**install-bin _plug-in_**

Install _plug-in_ into the user's personal _GIMP_ plug-in directory (\\$XDG_CONFIG_HOME/GIMP/3.2/plug-ins)

**install-admin-bin _plug-in_**

Install _plug-in_ into the system-wide _GIMP_ plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**install-bin-strip _plug-in_**

Install stripped _plug-in_ into the user's personal _GIMP_ plug-in directory (\\$XDG_CONFIG_HOME/GIMP/3.2/plug-ins)

**install-admin-bin-strip _plug-in_**

Install stripped _plug-in_ into the system-wide _GIMP_ plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**install-script _script.scm_**

Install _script.scm_ into the user's personal _GIMP_ script directory (\\$XDG_CONFIG_HOME/GIMP/3.2/scripts)

**install-admin-script _script.scm_**

Install _script.scm_ into the system-wide _GIMP_ script directory (/usr/share/gimp/3.0/scripts)

**uninstall-bin _plug-in_**

Uninstall _plug-in_ from the user's personal _GIMP_ plug-in directory (\\$XDG_CONFIG_HOME/GIMP/3.2/plug-ins)

**uninstall-admin-bin _plug-in_**

Uninstall _plug-in_ from the system-wide _GIMP_ plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**uninstall-script _script.scm_**

Uninstall _script.scm_ from the user's personal _GIMP_ script directory (\\$XDG_CONFIG_HOME/GIMP/3.2/scripts)

**uninstall-admin-script _script.scm_**

Uninstall _script.scm_ from the system-wide _GIMP_ script directory (/usr/share/gimp/3.0/scripts)

**libs**

Print the linker flags that are necessary to link a _GIMP_ plug-in.

**libs-noui**

Print the linker flags that are necessary to link a _GIMP_ plug-in, for plug-ins that do not require the GTK libraries.

**cflags**

Print the compiler flags that are necessary to compile a _GIMP_ plug-in.

**clags-noui**

Print the compiler flags that are necessary to compile a _GIMP_ plug-in for plug-ins that do not require the GTK libraries.

**prefix=PREFIX**

If specified, use PREFIX instead of the installation prefix that _GIMP_ was built with when computing the output for the —cflags and —libs options. This option is also used for the exec prefix if —exec-prefix was not specified. This option must be specified before any —libs or —cflags options.

**exec-prefix=PREFIX**

If specified, use PREFIX instead of the installation exec prefix that _GIMP_ was built with when computing the output for the —cflags and —libs options. This option must be specified before any —libs or —cflags options.

## ENVIRONMENT

**CC**

to get the name of the desired C compiler.

**CFLAGS**

to get the preferred flags to pass to the C compiler for plug-in building.

**LDFLAGS**

to get the preferred flags for passing to the linker.

**LIBS**

for passing extra libs that may be needed in the build process. For example, LIBS=-lintl.

**PKG_CONFIG**

to get the location of the _pkg-config_ program that is used to determine details about your glib, pango, gtk and gimp installation.

## SEE ALSO

**gimp** (1), **gimprc** (5), **pkg-config** (1)

gimptool was written by Manish Singh (yosh@gimp.org) and is based on gtk-config by Owen Taylor (owen@gtk.org).

This man page was written by Ben Gertzfield (che@debian.org), and tweaked by Manish Singh (yosh@gimp.org), Adrian Likins (adrian@gimp.org) and Marc Lehmann (pcg@goof.com>).
