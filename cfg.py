
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
