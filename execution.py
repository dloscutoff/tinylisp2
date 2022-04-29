
import sys
import os
from itertools import zip_longest
from contextlib import contextmanager

from cfg import nil, Symbol, UNLIMITED
import cfg
from parsing import parse
# TODO:
#import help_text


# Built-in functions and macros
# Key = implementation name; value = tinylisp name

builtins = {
    # Functions:
    "tl_cons": "cons",
    "tl_head": "head",
    "tl_tail": "tail",
    "tl_add": "+",
    "tl_sub": "-",
    "tl_mul": "*",
    "tl_div": "/",
    "tl_mod": "mod",
    "tl_less": "<",
    "tl_equal": "=",
    "tl_same_type": "same-type?",
    "tl_unparse": "unparse",
#    "tl_parse": "parse",
    "tl_write": "write",
    "tl_locals": "locals",
    "tl_eval": "eval",
    # Macros:
    "tl_def": "def",
    "tl_if": "if",
    "tl_quote": "q",
    "tl_load": "load",
    "tl_comment": "comment",
    # For REPL use:
    "tl_help": "help",
    "tl_restart": "restart",
    "tl_quit": "quit",
    }

# These are functions and macros that should not output their return
# values when called at the top level (except in repl mode)

top_level_quiet_fns = ["tl_def", "tl_print", "tl_load", "tl_comment"]


# Decorators for member functions that implement builtins

def macro(pyfunc):
    """Mark this builtin as a macro."""
    pyfunc.is_macro = True
    pyfunc.name = pyfunc.__name__
    if not hasattr(pyfunc, "top_level_only"):
        pyfunc.top_level_only = False
    if not hasattr(pyfunc, "repl_only"):
        pyfunc.repl_only = False
    return pyfunc


def function(pyfunc):
    """Mark this builtin as a function."""
    pyfunc.is_macro = False
    pyfunc.name = pyfunc.__name__
    if not hasattr(pyfunc, "top_level_only"):
        pyfunc.top_level_only = False
    if not hasattr(pyfunc, "repl_only"):
        pyfunc.repl_only = False
    return pyfunc


def top_level_only(pyfunc):
    """This builtin cannot be called inside a function, only at top level."""
    pyfunc.top_level_only = True
    return pyfunc


def repl_only(pyfunc):
    """This builtin can only be called at top level in the REPL."""
    pyfunc.repl_only = True
    pyfunc.top_level_only = True
    return pyfunc


def params(min_param_count, max_param_count=None):
    """Specify the min and max number of params this builtin takes."""
    def params_decorator(pyfunc):
        if max_param_count is not None:
            pyfunc.min_param_count = min_param_count
            pyfunc.max_param_count = max_param_count
        elif min_param_count == UNLIMITED:
            # This indicates a variadic builtin, so the actual minimum
            # is zero, not infinity
            pyfunc.min_param_count = 0
            pyfunc.max_param_count = min_param_count
        else:
            pyfunc.min_param_count = min_param_count
            pyfunc.max_param_count = min_param_count
        return pyfunc
    return params_decorator


class Program:
    def __init__(self, is_repl=False, debug_mode=False, options=None):
        self.is_repl = is_repl
        self.debug_mode = debug_mode
        self.modules = []
        self.module_paths = [os.path.abspath(os.path.dirname(__file__))]
        self.global_scope = {}
        self.local_scopes = [{}]
        self.builtins = []
        # Go through the tinylisp builtins and put the corresponding
        # member functions into the top-level symbol table
        for func_name, tl_func_name in builtins.items():
            builtin = getattr(self, func_name)
            self.builtins.append(builtin)
            self.global_scope[Symbol(tl_func_name)] = builtin
        if options is not None:
            # Load the core library and short names according to
            # the user-specified options
            if not options.no_library:
                self.tl_load("lib/core")
            if not options.no_short_names:
                self.tl_load("lib/short-builtins")
            if not options.no_library and not options.no_short_names:
                self.tl_load("lib/short-names")
        else:
            # By default, load the library and short names
            self.tl_load("lib/core")
            self.tl_load("lib/short-builtins")
            self.tl_load("lib/short-names")

    @property
    def current_scope(self):
        """The innermost local scope."""
        return self.local_scopes[-1]

    @property
    def is_quiet(self):
        """True (suppress output) while in process of loading modules."""
        return len(self.module_paths) > 1

    def execute(self, code):
        if isinstance(code, str):
            # Determine whether the code is in single-line or
            # multiline form:
            # In single-line form, the code is parsed one line at a time
            # with closing parentheses inferred at the end of each line
            # In multiline form, the code is parsed as a whole, with
            # closing parentheses inferred only at the end
            # If any line in the code contains more closing parens than
            # opening parens, the code is assumed to be in multiline
            # form; otherwise, it's single-line
            codelines = code.split("\n")
            multiline = any(line.count(")") > line.count("(")
                            for line in codelines)
            result = None
            if multiline:
                # Parse code as a whole
                for expr in parse(code):
                    result = self.execute_expression(expr)
            else:
                # Parse each line separately
                for codeline in codelines:
                    for expr in parse(codeline):
                        result = self.execute_expression(expr)
            # Return the result of the last expression
            return result
        else:
            raise NotImplementedError("Argument to execute() must be "
                                      f"str, not {type(code)}")
    
    def execute_expression(self, expr):
        """Evaluate an expression; display it if in repl mode."""
        result = self.evaluate(expr, top_level=True)
        if self.is_repl:
            # If running in repl mode, display the result
            self.display(result)
        else:
            # If running in full-program mode, display the result
            # TODO: unless the outer function is a top-level quiet function
            self.display(result)
        return result

    def evaluate(self, expr, top_level=False):
        # TODO: better error handling instead of just returning nil
        bindings = None
        # Loop while the expression represents a call to a user-defined
        # function (tail-call optimization)
        while True:
            with self.open_scope(bindings):
                # Eliminate any macros, ifs, and evals
                if isinstance(expr, list) and expr != []:
                    head = self.evaluate(expr[0])
                    tail = expr[1:]
                    try:
                        head, tail = self.resolve_macros(head, tail)
                    except TypeError:
                        # resolve_macros encountered an error condition
                        # (it already gave the error message)
                        return nil
                else:
                    head = None
                    tail = expr
                if head is not None:
                    # After macro elimination, expr is still some kind of
                    # function call
                    if head in self.builtins:
                        # Call to a builtin function or macro
                        builtin = head
                        if builtin.top_level_only and not top_level:
                            cfg.error(builtins[builtin.name],
                                      "can only be called at top level")
                            return nil
                        elif builtin.repl_only and not self.is_repl:
                            cfg.error(builtins[builtin.name],
                                      "can only be used in REPL mode")
                        if builtin.is_macro:
                            # Macros receive their args unevaluated
                            args = tail
                        else:
                            # Functions receive their args evaluated
                            args = [self.evaluate(arg) for arg in tail]
                        if len(args) < builtin.min_param_count:
                            cfg.error(builtins[builtin.name],
                                      "takes at least",
                                      builtin.min_param_count,
                                      "arguments, got",
                                      len(args))
                            return nil
                        elif len(args) > builtin.max_param_count:
                            cfg.error(builtins[builtin.name],
                                      "takes at most",
                                      builtin.max_param_count,
                                      "arguments, got",
                                      len(args))
                            return nil
                        else:
                            return builtin(*args)
                    elif isinstance(head, list) and head != []:
                        # User-defined function; do a tail call
                        try:
                            environment, param_names, body = head
                        except ValueError:
                            cfg.error("List callable as function must have "
                                      "3 elements, not",
                                      len(head))
                            return nil
                        args = [self.evaluate(arg) for arg in tail]
                        try:
                            bindings = self.bind_params(environment,
                                                        param_names,
                                                        args)
                        except TypeError:
                            # There was a problem with the structure of
                            # the parameter list (bind_params already gave
                            # the error message)
                            return nil
                        expr = body
                        top_level = False
                        # Loop with the new expression and bindings
                    else:
                        # Trying to call something other than a builtin or
                        # user-defined function
                        cfg.error(head, "is not a function or macro")
                        return nil
                else:
                    # If head is None, the expression (stored in tail)
                    # must be nil, a symbol, or a literal
                    expr = tail
                    if expr == nil:
                        # Nil evaluates to itself
                        return nil
                    elif isinstance(expr, Symbol):
                        # A symbol is looked up as a name
                        try:
                            return self.lookup_name(expr)
                        except NameError as err:
                            cfg.error(*err.args)
                            return nil
                    elif isinstance(expr, (int, str)):
                        # Integers and strings evaluate to themselves
                        return expr
                    elif expr in self.builtins:
                        # Builtins also evaluate to themselves
                        return expr
                    else:
                        # Code should never get here
                        raise TypeError("unexpected type in evaluate():",
                                        type(expr))

    @contextmanager
    def open_scope(self, bindings):
        """Open a new scope with the given bindings.

If bindings is None, do not open a new scope, just use the current one.
"""
        if bindings is not None:
            self.local_scopes.append(bindings)
        try:
            yield self.current_scope
        finally:
            if bindings is not None:
                self.local_scopes.pop()

    def lookup_name(self, name):
        """Look up a name in the local and global symbol tables.

Raises NameError if the name is not found.
"""
        if name in self.current_scope:
            return self.current_scope[name]
        elif name in self.global_scope:
            return self.global_scope[name]
        else:
            raise NameError(f"{name!r} is not defined")

    def bind_params(self, environment, param_names, arglist):
        """Return a dictionary of name:value pairs.

First, the (name value) pairs from environment are bound. Then, each
name from param_names is bound to the corresponding value from arglist.
If an element of param_names is a parameter with a default value,
the default value is used if there is no corresponding argument.
Otherwise, if the number of parameters doesn't match the number of
arguments, raise TypeError.
"""
        # Bind names from environment first (these are local names captured
        # from a lexically enclosing scope)
        new_scope = {}
        for pair in environment:
            if isinstance(pair, list) and len(pair) == 2:
                name, val = pair
                if isinstance(name, Symbol):
                    new_scope[name] = val
                else:
                    cfg.error("expected (name value) pair in function's "
                              "environment; got",
                              cfg.tl_type(name), "instead of name")
                    raise TypeError
            else:
                cfg.error("expected (name value) pair in function's "
                          "environment; got", pair, "instead")
                raise TypeError
        # Bind argument values to parameter names
        if isinstance(param_names, list):
            name_count = 0
            val_count = 0
            for name, val in zip_longest(param_names, arglist):
                if isinstance(name, list):
                    # Should be a name + default value pair
                    default_param = name
                    if len(default_param) == 2:
                        name, default_value = default_param
                    elif len(default_param) == 1:
                        # An unspecified default value == nil
                        name, = default_param
                        default_value = nil
                    else:
                        cfg.error("default parameter must be given as a "
                                  "List of either one or two elements")
                        raise TypeError
                else:
                    default_value = None
                if val is None and default_value is not None:
                    val = self.evaluate(default_value)
                if name is None:
                    # Ran out of parameter names
                    val_count += 1
                elif val is None:
                    # Ran out of argument values
                    name_count += 1
                elif isinstance(name, Symbol):
                    if name in self.global_scope:
                        cfg.warn("parameter name shadows global name",
                                 name)
                    new_scope[name] = val
                    name_count += 1
                    val_count += 1
                else:
                    cfg.error("parameter list must contain Symbols, not", name)
                    raise TypeError
            if name_count != val_count:
                # Wrong number of arguments
                cfg.error("expected", name_count, "arguments, got",
                          val_count)
                raise TypeError
        elif isinstance(param_names, Symbol):
            # Single name, bind entire arglist to it
            arglist_name = param_names
            if arglist_name in self.global_scope:
                cfg.warn("parameter name shadows global name", arglist_name)
            new_scope[arglist_name] = arglist
        else:
            cfg.error("parameters must either be Symbol or List of Symbols, "
                      "not", param_names)
            raise TypeError
        return new_scope

    def resolve_macros(self, head, tail):
        """Given head and tail of an expression, rewrite any macros.

This function eliminates the builtins <if> and <eval>, as well as any
user-defined macros.
- If the head of the expression is <if>, evaluate the condition and
  replace the expression with the true or false branch.
- If the head of the expression is <eval>, evaluate the argument and
  replace the expression with the result.
- If the head of the expression is a user-defined macro, call the
  macro with the arguments unevaluated; then evaluate its return
  value and replace the expression with that.
"""
        self.debug("Resolve macros:", head, tail)
        while (head == self.tl_if
               or head == self.tl_eval
               or self.is_macro(head)):
            if head == self.tl_if:
                # The head is (some name for) tl_if
                # If needs exactly three arguments
                if len(tail) == 3:
                    condition = self.evaluate(tail[0])
                    if cfg.tl_truthy(condition):
                        # Use the true branch
                        expression = tail[1]
                    else:
                        # Use the false branch
                        expression = tail[2]
                else:
                    cfg.error("if takes 3 arguments, not", len(tail))
                    raise TypeError
            elif head == self.tl_eval:
                # The head is (some name for) tl_eval
                # Eval needs exactly one argument
                if len(tail) == 1:
                    expression = self.evaluate(tail[0])
                else:
                    cfg.error("eval takes 1 argument, not", len(tail))
                    raise TypeError
            else:
                # The head is a list representing a user-defined macro
                macro_params, macro_body = head
                try:
                    macro_bindings = self.bind_params([], macro_params, tail)
                except TypeError:
                    self.debug("TypeError from bind_params")
                    raise
                # Substitute the arguments for the parameter names in
                # the macro body expression
                expression = self.replace(macro_bindings, macro_body)
            if expression and isinstance(expression, list):
                # The result was a nonempty s-expression which could be
                # another macro invocation, so set up for another trip
                # through the loop
                head, *tail = expression
                head = self.evaluate(head)
            else:
                # The result was nil or something other than an
                # s-expression; mark this case by setting head to None
                head = None
                tail = expression
        # We exit the loop when we have an expression that doesn't have
        # a head or whose head is no longer a macro--finish its evaluation
        # somewhere else
        self.debug("Return:", head, tail)
        return head, tail

    def is_macro(self, expression):
        """Does an expression represent a user-defined macro?"""
        # A macro must be a list with two elements (params and body)
        if isinstance(expression, list) and len(expression) == 2:
            return True
        else:
            return False

    def replace(self, bindings, expression):
        """Replaces names in expression with their values from bindings.

Bindings is a dictionary; expression is any expression.
Names that aren't in bindings are left untouched.
"""
        if isinstance(expression, list):
            # An s-expression
            return [self.replace(bindings, subexpr) for subexpr in expression]
        elif isinstance(expression, Symbol) and expression in bindings:
            # A name that needs to be replaced
            return bindings[expression]
        else:
            # A non-bound name or a literal
            return expression

    def display(self, value):
        """Output an unambiguous representation of a value."""
        if value is not None and not self.is_quiet:
            print(self.tl_unparse(value))

    def inform(self, *messages):
        """Output messages, but only in REPL mode."""
        if self.is_repl and not self.is_quiet:
            print(*messages)

    def debug(self, *messages):
        """Output debug messages, but only in debug mode."""
        if self.debug_mode and not self.is_quiet:
            print(*messages, file=sys.stderr)

    @function
    @params(2)
    def tl_cons(self, head, tail):
        if isinstance(tail, list):
            # Prepend an item to a list
            return [head] + tail
        elif isinstance(tail, str):
            # Prepend a character code to a string
            if isinstance(head, int):
                return chr(head) + tail
            else:
                cfg.error("cannot cons", cfg.tl_type(head), "to String")
                return nil
        else:
            cfg.error("second argument of cons must be List or String, not",
                      cfg.tl_type(tail))
            return nil

    @function
    @params(1)
    def tl_head(self, val):
        if isinstance(val, list):
            if val == nil:
                return nil
            else:
                return val[0]
        elif isinstance(val, str):
            if val == "":
                return nil
            else:
                return ord(val[0])
        else:
            cfg.error("cannot get head of", cfg.tl_type(val))
            return nil

    @function
    @params(1)
    def tl_tail(self, val):
        if isinstance(val, list):
            if val == nil:
                return nil
            else:
                return val[1:]
        elif isinstance(val, str):
            if val == "":
                return ""
            else:
                return val[1:]
        else:
            cfg.error("cannot get tail of", cfg.tl_type(val))
            return nil

    @function
    @params(UNLIMITED)
    def tl_add(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            # Given a single list argument, sum the list
            args = args[0]
        result = 0
        for arg in args:
            if isinstance(arg, int):
                result += arg
            else:
                cfg.error("cannot add", cfg.tl_type(arg))
                return nil
        return result

    @function
    @params(UNLIMITED)
    def tl_sub(self, *args):
        if len(args) == 0:
            return -1
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, int):
                return -arg
            else:
                cfg.error("cannot negate", cfg.tl_type(arg))
                return nil
        else:
            result = args[0]
            if not isinstance(result, int):
                cfg.error("cannot subtract from", cfg.tl_type(arg))
                return nil
            for arg in args[1:]:
                if isinstance(arg, int):
                    result -= arg
                else:
                    cfg.error("cannot subtract", cfg.tl_type(arg))
                    return nil
            return result

    @function
    @params(UNLIMITED)
    def tl_mul(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            # Given a single list argument, take the product of the list
            args = args[0]
        result = 1
        for arg in args:
            if isinstance(arg, int):
                result *= arg
            else:
                cfg.error("cannot multiply", cfg.tl_type(arg))
                return nil
        return result

    @function
    @params(2, UNLIMITED)
    def tl_div(self, *args):
        result = args[0]
        if not isinstance(result, int):
            cfg.error("cannot divide", cfg.tl_type(arg))
            return nil
        for arg in args[1:]:
            if isinstance(arg, int):
                if arg != 0:
                    result //= arg
                else:
                    cfg.error("division by zero")
                    return nil
            else:
                cfg.error("cannot divide by", cfg.tl_type(arg))
                return nil
        return result

    @function
    @params(2)
    def tl_mod(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            if arg2 != 0:
                return arg1 % arg2
            else:
                cfg.error("mod by zero")
                return nil
        else:
            cfg.error("cannot mod", cfg.tl_type(arg1), "and",
                      cfg.tl_type(arg2))
            return nil

    @function
    @params(1, UNLIMITED)
    def tl_less(self, *args):
        result = True
        for arg1, arg2 in zip(args, args[1:]):
            if isinstance(arg1, int) and isinstance(arg2, int):
                result = result and arg1 < arg2
            else:
                cfg.error("cannot compare", cfg.tl_type(arg1),
                          "and", cfg.tl_type(arg2))
                return nil
        return int(result)

    @function
    @params(1, UNLIMITED)
    def tl_equal(self, *args):
        result = True
        arg1 = args[0]
        for arg2 in args[1:]:
            result = result and arg1 == arg2
        return int(result)

    @function
    @params(1, UNLIMITED)
    def tl_same_type(self, *args):
        result = True
        arg1 = args[0]
        for arg2 in args[1:]:
            result = result and cfg.tl_type(arg1) == cfg.tl_type(arg2)
        return int(result)

    @function
    @params(1)
    def tl_unparse(self, value):
        if isinstance(value, list):
            # Join items of a list on space and wrap in parentheses
            first_item = True
            result = "("
            for item in value:
                if first_item:
                    first_item = False
                else:
                    result += " "
                result += self.tl_unparse(item)
            result += ")"
        elif value in self.builtins:
            # A builtin function or macro can't be unparsed because it
            # don't have a literal syntax, but at least return something
            # that looks okay when displayed
            builtin_type = "macro" if value.is_macro else "function"
            result = f"<builtin {builtin_type} {value.name}>"
        elif isinstance(value, str):
            # Wrap a string in double-quotes and escape special characters
            python_repr = repr('\'"' + value)
            result = python_repr[4:-1]
            result = result.replace(r"\'", "'").replace('"', r'\"')
            result = '"' + result + '"'
        else:
            # Convert an integer or symbol to a string
            result = str(value)
        return result

    @function
    @params(UNLIMITED)
    def tl_write(self, *vals):
        for val in vals:
            if isinstance(val, str):
                # Write strings without surrounding quotes
                cfg.write(val)
            else:
                # Write other values the same as their unparsed format
                cfg.write(self.tl_unparse(val))
        return nil

    @function
    @params(0)
    def tl_locals(self):
        return [[name, val] for name, val in self.current_scope.items()]

    @function
    @params(1)
    def tl_eval(self, expr):
        # This implementation should never actually be called
        raise NotImplementedError("tl_eval should not be called directly")

    @macro
    @top_level_only
    @params(2)
    def tl_def(self, name, value):
        if isinstance(name, Symbol):
            if name in self.global_scope:
                cfg.error("name", name, "already in use")
                return nil
            else:
                self.global_scope[name] = self.evaluate(value)
                return name
        else:
            cfg.error("def expected Symbol, not", cfg.tl_type(name))
            return nil

    @macro
    @params(3)
    def tl_if(self, cond, true_expr, false_expr):
        # This implementation should never actually be called
        raise NotImplementedError("tl_if should not be called directly")

    @macro
    @params(1)
    def tl_quote(self, expr):
        return expr

    @macro
    @top_level_only
    @params(1)
    def tl_load(self, module):
        if isinstance(module, Symbol):
            module = str(module)
        if not isinstance(module, str):
            cfg.error("load requires module name, not", cfg.tl_type(module))
            return nil
        if not module.endswith(".tl"):
            module += ".tl"
        abspath = os.path.abspath(os.path.join(self.module_paths[-1], module))
        module_directory, module_name = os.path.split(abspath)
        if abspath not in self.modules:
            # Module has not already been loaded
            try:
                with open(abspath) as f:
                    module_code = f.read()
            except (FileNotFoundError, IOError):
                cfg.error("could not load", module_name,
                          "from", module_directory)
                return nil
            else:
                # Add the module to the list of loaded modules
                self.modules.append(abspath)
                # Push the module's directory to the stack of module
                # directories--this allows relative paths in load calls
                # from within the module
                self.module_paths.append(module_directory)
                # Execute the module code
                self.execute(module_code)
                # Put everything back the way it was before loading
                self.module_paths.pop()
                self.inform("Loaded", module)
        else:
            self.inform("Already loaded", module)
        return nil

    @macro
    @top_level_only
    @params(UNLIMITED)
    def tl_comment(self, *args):
        return nil

    @macro
    @repl_only
    @params(0)
    def tl_help(self):
        self.inform("Help text TODO")
        return nil

    @macro
    @repl_only
    @params(0)
    def tl_restart(self):
        self.inform("Restarting...")
        self.__init__(is_repl=self.is_repl)
        return nil

    @macro
    @repl_only
    @params(0)
    def tl_quit(self):
        raise cfg.UserQuit
