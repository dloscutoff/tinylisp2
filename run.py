
import cfg
from execution import Program


def run_file(filename, environment=None, options=None):
    if environment is None:
        environment = Program(is_repl=False, options=options)
    try:
        with open(filename) as f:
            code = f.read()
    except FileNotFoundError:
        cfg.error("could not find", filename)
        return
    except PermissionError:
        cfg.error("insufficient permissions to read", filename)
        return
    except IOError:
        cfg.error("could not read", filename)
        return
    # If file read was successful, execute the code
    run_program(code, environment)


def run_program(code, environment=None, options=None):
    if environment is None:
        environment = Program(is_repl=False, options=options)
    try:
        environment.execute(code)
    except KeyboardInterrupt:
        cfg.interrupted_error()
        return
    except RecursionError:
        cfg.recursion_error()
        return
    except Exception as err:
        # Miscellaneous exception, probably indicates a bug in
        # the interpreter
        cfg.error(err)
        return


def repl(environment=None, options=None):
    print("(tinylisp 2)")
    if environment is None:
        environment = Program(is_repl=True, options=options)
    print("Type (help) for information")
    instruction = input_instruction()
    while True:
        try:
            last_value = environment.execute(instruction)
        except KeyboardInterrupt:
            cfg.interrupted_error()
        except RecursionError:
            cfg.recursion_error()
        except cfg.UserQuit:
            break
        except Exception as err:
            # Miscellaneous exception, probably indicates a bug in
            # the interpreter
            cfg.error(err)
            break
        else:
            if last_value is not None:
                environment.global_scope[cfg.Symbol("_")] = last_value
        instruction = input_instruction()
    print("Bye!")


def input_instruction():
    try:
        instruction = input(cfg.PROMPT)
    except (EOFError, KeyboardInterrupt):
        instruction = "(quit)"
    return instruction
