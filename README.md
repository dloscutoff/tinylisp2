# tinylisp 2

A minimalist Lisp dialect and successor to [tinylisp](https://github.com/dloscutoff/Esolangs/tree/master/tinylisp).

## Features

- Only 20-ish builtins and five data types
- [Tail-call optimization](https://en.wikipedia.org/wiki/Tail_call), allowing unlimited recursion depth for properly written functions
- Lexical scope and [closures](https://en.wikipedia.org/wiki/Closure_(computer_programming))
- A simple yet powerful macro system
- An automatically loaded core library, written in tinylisp 2
- Short aliases for commonly used functions, convenient for [code golf](https://en.wikipedia.org/wiki/Code_golf)

## Running tinylisp 2

You can run tinylisp 2 in interactive REPL mode at [Replit](https://replit.com/@dloscutoff/tinylisp2).

If you `git clone` tinylisp 2 to your computer (requires [Python](https://www.python.org/downloads/) 3.6 or higher), you have two options: run a file, or open the REPL.

- To run code from a file, pass the filename as a command-line argument to the interpreter: `python3 tinylisp2.py file.tl` (Linux) or `tinylisp2.py file.tl` (Windows).
- To start the REPL, run the interpreter without command-line arguments: `python3 tinylisp2.py` or `tinylisp2.py`.

Helpful commands when using the REPL:

- `(help)` displays a help document.
- `(restart)` clears all user-defined names, starting over from scratch.
- `(quit)` ends the session.
