#!/usr/bin/env python3

import sys

import run


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User specified a filename--run it
        run.run_file(sys.argv[1])
    elif sys.stdin.isatty():
        # No filename specified, and the input is coming from a terminal;
        # run in REPL mode
        run.repl()
    else:
        # No filename specified, but input is piped in from a file or
        # another process, so treat that as a program and run it
        code = sys.stdin.read()
        run.run_program(code)
