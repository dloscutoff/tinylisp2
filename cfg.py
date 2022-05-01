
import sys
import string


# Scanning/parsing related constants
WHITESPACE = string.whitespace
PARENS = "()"
LINE_COMMENT_CHAR = ";"
STRING_DELIMITER = '"'
STRING_ESCAPE_CHAR = "\\"
SPECIAL_CHARS = WHITESPACE + PARENS + LINE_COMMENT_CHAR + STRING_DELIMITER

# Repl prompt string
PROMPT = "tl2> "

HELP_TEXT = """
Enter expressions at the prompt.

- Anything starting with ; is a comment and will be ignored.
- Any run of digits (with optional minus sign) is an integer literal.
- () is the empty list, nil.
- Anything in "double quotes" is a string literal. Special characters
  can be escaped with backslashes.
- A series of expressions enclosed in parentheses is a function or
  macro call.
- Anything else is a symbol, which returns the value bound to it or
  errors if it is unbound; if quoted with q, it is kept unevaluated.

The builtin functions and macros are: cons, head, tail, +, -, *, /,
mod, <, =, same-type?, unparse, write, locals, eval, def, if, q,
and load. Most of these also have abbreviated names, unless you have
invoked the interpreter with --no-short-names or --builtins-only:
cons -> c, head -> h, tail -> t, mod -> %, same-type? -> y,
unparse -> u, write -> w, eval -> v, def -> d, if -> ?.

The core library defines many more functions and macros. It is loaded
by default, unless you have invoked the interpreter with --no-library
or --builtins-only. Some library functions also have abbreviated names.

You can create your own functions. The easiest way is to use the lambda
macro from the library: (lambda (x) (+ x 2)) is a function that adds 2
to its argument. To create a named function, bind it to a name using def.

Special features in the interactive prompt:

- The name _ is bound to the value of the last evaluated expression.
- (restart) clears all user-defined names, starting over from scratch.
- (help) displays this help text.
- (quit) ends the session.
"""

# Max param count of variadic builtins
UNLIMITED = float("inf")

# The empty list, nil
nil = []


# Shortcut functions for print without newline and print to stderr
def write(*args):
    print(*args, end="")


def error(*args):
    print("Error:", *args, file=sys.stderr)


def warn(*args):
    print("Warning:", *args, file=sys.stderr)


def interrupted_error():
    error("calculation interrupted by user.")


def recursion_error():
    error("recursion depth exceeded. How could you forget to use tail calls?!")


def tl_truthy(value):
    """Is the value truthy in tinylisp?"""
    if value == nil or value == "" or value == 0:
        return False
    else:
        return True


def tl_type(value):
    if isinstance(value, list):
        return "List"
    elif isinstance(value, int):
        return "Integer"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, Symbol):
        return "Symbol"
    else:
        return "Builtin"


# Exception that is raised by the (quit) macro

class UserQuit(BaseException):
    pass


# Class for symbols to distinguish them from strings

class Symbol:
    def __init__(self, name):
        self.name = str(name)

    def __eq__(self, rhs):
        if isinstance(rhs, Symbol):
            return self.name == rhs.name
        else:
            return self.name == rhs

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Symbol({self.name!r})"

    def __hash__(self):
        return hash(repr(self))
