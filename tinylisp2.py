#!/usr/bin/env python3

import sys
import argparse

import run


def parse_args(args=None):
    argparser = argparse.ArgumentParser()
    liboptions = argparser.add_mutually_exclusive_group()
    liboptions.add_argument("--no-library",
                            help="don't autoload the core library",
                            action="store_true")
    liboptions.add_argument("--no-short-names",
                            help="don't autoload any short aliases",
                            action="store_true")
    liboptions.add_argument("--builtins-only",
                            help="don't autoload library or aliases",
                            action="store_true")
    argparser.add_argument("filename",
                           help="code file to execute",
                           nargs="?")
    if args is not None:
        # Parse the argument list passed into the function
        options = argparser.parse_args(args)
    else:
        # Parse the actual command-line args
        options = argparser.parse_args()
    if options.builtins_only:
        options.no_library = True
        options.no_short_names = True
    return options


if __name__ == "__main__":
    options = parse_args()
    if options.filename:
        # User specified a filename--run it
        run.run_file(options.filename, options=options)
    elif sys.stdin.isatty():
        # No filename specified, and the input is coming from a terminal;
        # run in REPL mode
        run.repl(options=options)
    else:
        # No filename specified, but input is piped in from a file or
        # another process, so treat that as a program and run it
        code = sys.stdin.read()
        run.run_program(code, options=options)
