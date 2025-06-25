import re

TOKEN_SPEC = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('STRING',   r'"[^"]*"'),
    ('OP',       r'==|!=|<=|>=|[+\-*/=<>]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('SEMICOLON',r';'),
    ('COMMA',    r','),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.'),
]

TOKEN_REGEX = '|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC)

def tokenize(code):
    tokens = []
    for mo in re.finditer(TOKEN_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        elif kind == 'STRING':
            value = value[1:-1]
        elif kind == 'SKIP' or kind == 'NEWLINE':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character {value}")
        tokens.append((kind, value))
    return tokens
