
import cfg
from execution import Program


def repl(environment=None, options=None):
    print("(tinylisp 2)")
    print("Type (help) for information")
    if environment is None:
        environment = Program(is_repl=True, options=options)
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
