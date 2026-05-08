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

**gimptool** \[—prefix *\[=DIR\]*\] \[—exec-prefix *\[=DIR\]*\] \[—version\] \[—help\] \[—quiet\] \[—silent\] \[-n\] \[—just-print\] \[—dry-run\] \[—recon\] \[—msvc-syntax\] \[—bindir\] \[—sbindir\] \[—libexecdir\] \[—datadir\] \[—sysconfdir\] \[—sharedstatedir\] \[—localstatedir\] \[—libdir\] \[—infodir\] \[—mandir\] \[—includedir\] \[—gimpplugindir\] \[—gimpdatadir\] \[—libs\] \[—libs-noui\] \[—cflags\] \[—cflags-noi\] \[—build *plug-in.c*\] \[—build-strip *plug-in.c*\] \[—install *plug-in.c*\] \[—install-strip *plug-in.c*\] \[—install-admin *plug-in.c*\] \[—install-bin *plug-in*\] \[—install-admin-strip *plug-in.c*\] \[—install-bin-strip *plug-in*\] \[—install-admin-bin *plug-in*\] \[—install-script *script.scm*\] \[—install-admin-script *script.scm*\] \[—uninstall-bin *plug-in*\] \[—uninstall-admin-bin *plug-in*\] \[—uninstall-script *script.scm*\] \[—uninstall-admin-script *script.scm*\]

## DESCRIPTION

*gimptool* is a tool that can, among other things, build plug-ins or scripts and install them if they are distributed in one source file.

*gimptool* can also be used by programs that need to know what libraries and include-paths *GIMP* was compiled with. *gimptool* uses *pkg-config* for this task. For use in Makefiles, it is recommended that you use *pkg-config* directly instead of calling *gimptool*.

## OPTIONS

*gimptool* accepts the following options:

**—version**

Print the currently installed version of *GIMP* on the standard output.

**—help**

Print out the help blurb, showing commonly used commandline options.

**—quiet**

Run quietly without echoing any of the build commands.

**—silent**

Run silently without echoing any of the build commands. Same as —quiet.

**\-n**

Test mode. Print the commands but don't actually execute them. Useful for making dry runs for testing.

**—just-print**

Test mode. Print the commands but don't actually execute them. Same as -n.

**—dry-run**

Test mode. Print the commands but don't actually execute them. Same as -n.

**—recon**

Test mode. Print the commands but don't actually execute them. Same as -n.

**—msvc-syntax**

Useful on Windows. Outputs the compiler and linker flags in the syntax used by Microsoft's toolchain. Passed to the pkg-config command that does most of *gimptool* 's work.

**—bindir**

Outputs the bindir used to install the *GIMP*.

**—sbindir**

Outputs the sbindir used to install the *GIMP*.

**—libexecdir**

Outputs the libexecdir used to install the *GIMP*.

**—datadir**

Outputs the datadir used to install the *GIMP*.

**—sysconfdir**

Outputs the sysconfdir used to install the *GIMP*.

**—sharedstatedir**

Outputs the sharedstatedir used to install the *GIMP*.

**—localstatedir**

Outputs the localstatedir used to install the *GIMP*.

**—libdir**

Outputs the libdir used to install the *GIMP*.

**—infodir**

Outputs the infodir used to install the *GIMP*.

**—mandir**

Outputs the mandir used to install the *GIMP*.

**—includedir**

Outputs the includedir used to install the *GIMP*.

**—gimpdatadir**

Outputs the actual directory where the *GIMP* data files were installed.

**—gimpplugindir**

Outputs the actual directory where the *GIMP* plug-ins were installed.

**—build *plug-in.c***

Compile and link *plug-in.c* into a *GIMP* plug-in.

**—build-strip *plug-in.c***

Compile,link, and strip *plug-in.c* into a *GIMP* plug-in.

**—install *plug-in.c***

Compile, link, and install *plug-in.c* into the user's personal *GIMP* plug-in directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/plug-ins)

**—install-strip *plug-in.c***

Compile, link,strip, and install *plug-in.c* into the user's personal *GIMP* plug-in directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/plug-ins)

**—install-admin *plug-in.c***

Compile, link, and install *plug-in.c* into the system-wide *GIMP* plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**—install-bin *plug-in***

Install *plug-in* into the user's personal *GIMP* plug-in directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/plug-ins)

**—install-admin-bin *plug-in***

Install *plug-in* into the system-wide *GIMP* plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**—install-bin-strip *plug-in***

Install stripped *plug-in* into the user's personal *GIMP* plug-in directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/plug-ins)

**—install-admin-bin-strip *plug-in***

Install stripped *plug-in* into the system-wide *GIMP* plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**—install-script *script.scm***

Install *script.scm* into the user's personal *GIMP* script directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/scripts)

**—install-admin-script *script.scm***

Install *script.scm* into the system-wide *GIMP* script directory (/usr/share/gimp/3.0/scripts)

**—uninstall-bin *plug-in***

Uninstall *plug-in* from the user's personal *GIMP* plug-in directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/plug-ins)

**—uninstall-admin-bin *plug-in***

Uninstall *plug-in* from the system-wide *GIMP* plug-in directory (/usr/lib64/gimp/3.0/plug-ins)

**—uninstall-script *script.scm***

Uninstall *script.scm* from the user's personal *GIMP* script directory (\\$XDG\_CONFIG\_HOME/GIMP/3.2/scripts)

**—uninstall-admin-script *script.scm***

Uninstall *script.scm* from the system-wide *GIMP* script directory (/usr/share/gimp/3.0/scripts)

**—libs**

Print the linker flags that are necessary to link a *GIMP* plug-in.

**—libs-noui**

Print the linker flags that are necessary to link a *GIMP* plug-in, for plug-ins that do not require the GTK libraries.

**—cflags**

Print the compiler flags that are necessary to compile a *GIMP* plug-in.

**—clags-noui**

Print the compiler flags that are necessary to compile a *GIMP* plug-in for plug-ins that do not require the GTK libraries.

**—prefix=PREFIX**

If specified, use PREFIX instead of the installation prefix that *GIMP* was built with when computing the output for the —cflags and —libs options. This option is also used for the exec prefix if —exec-prefix was not specified. This option must be specified before any —libs or —cflags options.

**—exec-prefix=PREFIX**

If specified, use PREFIX instead of the installation exec prefix that *GIMP* was built with when computing the output for the —cflags and —libs options. This option must be specified before any —libs or —cflags options.

## ENVIRONMENT

**CC**

to get the name of the desired C compiler.

**CFLAGS**

to get the preferred flags to pass to the C compiler for plug-in building.

**LDFLAGS**

to get the preferred flags for passing to the linker.

**LIBS**

for passing extra libs that may be needed in the build process. For example, LIBS=-lintl.

**PKG\_CONFIG**

to get the location of the *pkg-config* program that is used to determine details about your glib, pango, gtk and gimp installation.

## SEE ALSO

**gimp** (1), **gimprc** (5), **pkg-config** (1)

gimptool was written by Manish Singh (yosh@gimp.org) and is based on gtk-config by Owen Taylor (owen@gtk.org).

This man page was written by Ben Gertzfield (che@debian.org), and tweaked by Manish Singh (yosh@gimp.org), Adrian Likins (adrian@gimp.org) and Marc Lehmann (pcg@goof.com>).