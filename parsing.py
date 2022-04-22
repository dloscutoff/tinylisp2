
import cfg


def scan(code):
    """Take a string and yield a series of tokens."""
    # Add a newline to the end to allow peeking at the next character
    # without requiring a check for end-of-string
    code += "\n"
    i = 0
    while i < len(code):
        char = code[i]
        if char in cfg.WHITESPACE:
            # Whitespace--ignore
            pass
        elif char == cfg.LINE_COMMENT_CHAR:
            # Start of a comment--scan till newline
            while code[i+1] != "\n":
                i += 1
        elif char in cfg.PARENS:
            # Parentheses are their own tokens
            yield char
        elif char == cfg.STRING_DELIMITER:
            # Start of a string literal--scan till the end of it
            # A string literal looks like:
            #  "chars \"and\" \\escapes"
            # which represents this string:
            #  chars "and" \escapes
            start = i
            i += 1
            while code[i] != cfg.STRING_DELIMITER:
                if code[i] == "\n":
                    # String literals that are unterminated by the end
                    # of a line get autoclosed
                    yield code[start:i] + cfg.STRING_DELIMITER
                    # Back the index up a notch so the newline gets
                    # scanned in its own right on the next iteration
                    i -= 1
                    break
                elif code[i] == cfg.STRING_ESCAPE_CHAR:
                    # Include the whole escape sequence together
                    i += 2
                    # But make sure we didn't just walk off the end of
                    # the code
                    if i >= len(code):
                        cfg.warn("unterminated escape sequence in string")
                        yield code[start:i] + cfg.STRING_DELIMITER
                        i -= 1
                        break
                else:
                    # Include a single character
                    i += 1
            else:
                yield code[start:i+1]
        else:
            # Start of a regular, non-extended token (symbol or
            # numeric literal)--scan till the end of it
            start = i
            while code[i+1] not in cfg.SPECIAL_CHARS:
                i += 1
            yield code[start:i+1]
        i += 1


def parse(code):
    """Take a series of expressions, yield a series of parse trees.

The code can be a string or an iterator that yields tokens.
Each resulting parse tree is a nested list.
"""
    if isinstance(code, str):
        # If we're given a raw codestring, scan it before parsing
        code = scan(code)
    try:
        while True:
            token = next(code)
            if token == "(":
                # After an opening parenthesis, parse expressions until
                # the matching closing parenthesis and yield the
                # resulting nested list
                yield parse_expressions(code)
            elif token == ")":
                # Ignore unmatched closing parentheses with a warning
                cfg.warn("unmatched closing parenthesis")
            else:
                # If the code doesn't start with a parenthesis, it must
                # be a symbol, a string literal, or a numeric literal
                yield parse_symbol_or_literal(token)
    except StopIteration:
        # Everything has been parsed
        pass


def parse_expressions(code):
    """Take a token iterator and parse expressions from it until ).

This function assumes we're parsing an s-expression and that the
opening parenthesis has already been processed. So we parse the items
or (sub)expressions in the s-expr one after the other, turning them
into a list. When we go to parse another item and we find a closing
parenthesis, we've hit the end of the s-expr, so we return nil.
"""
    parsed = []
    while True:
        try:
            token = next(code)
        except StopIteration:
            # If the s-expression is unfinished and we've run out of tokens,
            # supply the missing close-paren
            token = ")"
        if token == ")":
            break
        elif token == "(":
            # The subexpression is itself a list
            expr = parse_expressions(code)
        else:
            expr = parse_symbol_or_literal(token)
        parsed.append(expr)
    return parsed


def parse_symbol_or_literal(token):
    "Take a string and parse it as a literal or a symbol."""
    if token.startswith(cfg.STRING_DELIMITER):
        # String literal--should be the same syntax as a Python string
        # literal, so try just eval'ing it
        # TODO: error handling
        return eval(token)
    if token.isdigit() or token.startswith("-") and token[1:].isdigit():
        # Integer literal
        return int(token)
    else:
        # If it's not any kind of recognized literal, it's a symbol
        return cfg.Symbol(token)
