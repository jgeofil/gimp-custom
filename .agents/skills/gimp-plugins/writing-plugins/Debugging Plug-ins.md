---
title: "Debugging Plug-ins"
source: "https://developer.gimp.org/resource/debug/"
author:
published: 2003-02-08
created: 2026-05-07
description: "Eeek! The filter or plug-in you’re working on has a bug in it! And the fix isn’t completely obvious, so you want to use a debugger to see what is going on.Debugging a filter is straight-foward like debugging GIMP (since the filter is a shared library loaded by GEGL which is loaded by GIMP, GIMP process will crash so the debugger can catch the threads information, including the one on which the filter crashed). So, see: Debugging Tips."
tags:
  - "gimp-plugin-debugging"
  - "libgimp-development"
  - "software-troubleshooting"
  - "environment-variables"
  - "gdb-integration"
  - "stack-trace-analysis"
category: "general"
---
Debugging Plug-ins

Eeek! The filter or plug-in you’re working on has a bug in it! And the fix isn’t completely obvious, so you want to use a debugger to see what is going on.

Debugging a filter is straight-foward like debugging GIMP (since the filter is a shared library loaded by GEGL which is loaded by GIMP, GIMP process will crash so the debugger can catch the threads information, including the one on which the filter crashed). So, see: [Debugging Tips](https://developer.gimp.org/core/debug/debugging-tips/).

But hmm, how does one start a plug-in under a debugger if GIMP is the one who is starting the plug-in… If you analyze both GIMP and a plugin, you might have interleaved output from:

- the GIMP app process
- the old ScriptFu extension
- a running plugin under test
- any plugin called by the plugin under test

To address this issue, libgimp has some hooks controlled by the `GIMP_PLUGIN_DEBUG` or `GIMP_PLUGIN_DEBUG_WRAP*` environment variables at runtime.

## Format of GIMP\_PLUGIN\_DEBUG

`GIMP_PLUGIN_DEBUG` lets you arrange that a plug-in suspends when it starts, and then you can start a debugger and attach the debugger to the pid of the plug-in.

```sh
GIMP_PLUGIN_DEBUG=<domain>,<options>
```

It have a similar format to [`GIMP_DEBUG`](https://developer.gimp.org/core/debug/debugging-tips/#debug-logs). The “domain” will be the plug-in name. `all` is a domain to debug every plug-in.

A plug-in name is usually the name of the executable file, including any suffix, not the procedure-name, e.g. “file-psd” not “file-psd-export”. Other valid examples: “foggify.py” or on some platforms “foo.exe”.

Since forever, GIMP does not understand Python packages. A directory that is a Python package (having an **init**.py file) will be read by GIMP at startup, but GIMP will only install one plugin from that directory, and only if the.py file is named like the directory.

“options” is zero or more of the following options, separated by:’s

- `query`: suspend the plug-in when its query func is called (only on plug-in first install).
- `init`: suspend the plug-in when its init func is called (on subsequent starts at splash screen).
- `run`: suspend the plug-in when its run func is called (on plug-in execution by the user, default).
- `quit`: suspend the plug-in when its quit func is called.
- `pid`: just print the pid of the plug-in on run\_proc.
- `fatal-warnings`: similar to [gimp –g-fatal-warnings](https://developer.gimp.org/core/debug/debugging-tips/#debugging-a-warning-or-critical) on the command line, but for the plugin process
- `fw`: shorthand for above (fatal-warnings).
- `fatal-criticals`: make CRITICAL level messages fatal (but not WARNING)

In the absence of an options string, only ERRORs are fatal and generate a backtrace according to [stack-trace-mode](#gimp_plugin_debug-and-stack-trace-mode).

## To use a debugger on a plug-in

0. Ensure GIMP was built with debugging information. A detailed backtrace partly depends on building GIMP (`-Dbuildtype=debug*`) and [dependencies](https://developer.gimp.org/core/debug/debugging-tips/#basics) with debug info enabled.
1. In a **first terminal**, start GIMP with the environment variable `GIMP_PLUGIN_DEBUG` set:
	```sh
	export GIMP_PLUGIN_DEBUG=blur,run #on Linux/macOS
	$env:GIMP_PLUGIN_DEBUG='blur,run' #on Windows
	path_to_gimp
	```
	Exceptions in an interpreted language may print on their own and **not** generate log events to be caught by `GIMP_PLUGIN_DEBUG`.
	To get frames at least from log events of the interpreter calling out to LibGimp and GLib, evaluate to `all,fatal-criticals`, or `all,fatal-warnings` if appropriate.
2. In another, **second terminal**, start a debugger (gdb, cdb, lldb, or other) and load the plug-in program into the debugger. Loading only loads the debug symbols.
	```sh
	gdb path_to_blur_plugin
	```
3. Invoke the plug-in procedure in GIMP. GIMP will start the plug-in process, then suspend it and print the pid of the plug-in process to the terminal where you started GIMP. On Windows: you should see something in the **first terminal** like: `(blur:8992): LibGimp-DEBUG: 16:44:50.894: Debugging (restart externally): 8992`. The number at the end is the `<pid>` of the plug-in.
4. In the debugger on the **second terminal**, attach to the pid of the plug-in process. Expect the debugger to say where the plug-in is suspended.
	```sh
	attach <pid> #on GDB/LLDB (e.g. Linux, macOS)
	.Attach 0n<pid> #on CDB (Windows)
	```
5. In the debugger, set breakpoints (or examine memory, or step, etc.)
6. Windows: in a **third terminal**, resume the plug-in process with `gimp-debug-resume.exe` available from your build directory.
	```sh
	path_to_build/tools/gimp-debug-resume.exe <pid>
	```
	Linux and Unix-like: the gdb `continue` or lldb `c` command might resume the attached process. Possibly you will have to send a SIGCONT signal:
	```sh
	kill -SIGCONT <pid>
	```
7. In the debugger on the **second terminal**, enter `continue` if GDB or `c` if LLDB. Expect the plug-in to resume under control of the debugger and pause at breakpoints.
	```sh
	c #on GDB/LLDB (e.g. Linux, macOS)
	g #on cDB (Windows)
	```
8. When it crashes, the debugger should catch a signal. Your response might be the following to obtain a backtrace:
	```sh
	bt #on GDB/LLDB (e.g. Linux, macOS)
	kp #on CDB (Windows)
	```

## Format of GIMP\_PLUGIN\_DEBUG\_WRAP\*

Hmm, but what about memory debuggers such as valgrind? For those you need to set the following two vars:

```sh
GIMP_PLUGIN_DEBUG_WRAP=<domain>,<options>
GIMP_PLUGIN_DEBUG_WRAPPER=<debugger>
```

`GIMP_PLUGIN_DEBUG_WRAP` is similar to [`GIMP_PLUGIN_DEBUG`](#format-of-gimp_plugin_debug). But `all` domain does not always work. And `query`, `init`, and `run` are the only valid options.

“debugger” on `GIMP_PLUGIN_DEBUG_WRAPPER` refers to the debugger executable name on PATH. You can put command line options here too, they will be parsed like they do in the shell.

## To use a debugger on a plug-in (alternative)

0. Similarly to when using GIMP\_PLUGIN\_DEBUG, ensure GIMP (`-Dbuildtype=debug*`) and [dependencies](https://developer.gimp.org/core/debug/debugging-tips/#basics) were built with debug info enabled.
	Even some debuggers, like valgrind, working differently (and slowly) to get more information, they still will be benefited from debug info in binaries.
1. In a terminal, start GIMP with:
	```sh
	export GIMP_PLUGIN_DEBUG_WRAP=script-fu #on Linux/macOS
	export GIMP_PLUGIN_DEBUG_WRAPPER="gdb --args" #on Linux/macOS
	$env:GIMP_PLUGIN_DEBUG_WRAP='script-fu' #on Windows
	$env:GIMP_PLUGIN_DEBUG_WRAPPER="gdb --args" #on Windows
	path_to_gimp
	```
	GIMP\_PLUGIN\_DEBUG\_WRAP is more limited than GIMP\_PLUGIN\_DEBUG for interpreted plugins, since, as said, it do **not** even have fatal-\* <options>.
	You can, then, set `G_DEBUG` env var evaluating it to `fatal-criticals` so that CRITICALS are fatal, or `fatal-warnings` for fatal WARNINGS and CRITICALS.
	You can change `gdb --args` to `cdb`, `lldb --` or another debugger (e.g. `valgrind`)
	We run the debugger in a way that everything after that will be passed as args to the program being debugged, since there may be many args that GIMP passes to a plug-in (e.g. for ScriptFu extension).
2. Launch the plugin from the GIMP app. The debugger will now be invoked and load the symbols.
3. The debugger is waiting on you. Set breakpoints, etc, then run:
	```sh
	r #on GDB/LLDB (e.g. Linux, macOS)
	g #on CDB (Windows)
	```
4. When it crashes, the debugger should catch a signal, write the details to the terminal, and prompt you. Your response might be the following to obtain a backtrace:
	```sh
	bt #on GDB/LLDB (e.g. Linux, macOS)
	kp #on CDB (Windows)
	```

## GIMP\_PLUGIN\_DEBUG and stack-trace-mode

The GIMP app on the command line can take this flag:

```sh
--stack-trace-mode [never, query, always]
```

That flag will make GIMP redirect the stack-trace printing from the usual GUI gimp-debug-tool to the CLI (the terminal where GIMP was called) instead.

When the GIMP app forks a plugin process, it passes that arg to the plugin, and the arg controls how a backtrace is printed:

- The default is `query`, which means libgimp will ask you: “\[E\]xit \[S\]tacktrace \[P\]roceed” (similar to the GLib default handler for ERROR log events.)
- `always` means libgimp prints a backtrace (and then the plugin terminates.)
- `never` means libgimp does not print a backtrace, only a message. But for GIMP\_PLUGIN\_DEBUG=all,fatal-warning, the plugin terminates on the first WARNING.

Last updated on