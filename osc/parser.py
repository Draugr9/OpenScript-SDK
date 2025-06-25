from collections import namedtuple

# AST nodes
VarDecl = namedtuple('VarDecl', ['type', 'name', 'value'])
Assign = namedtuple('Assign', ['name', 'value'])
BinOp = namedtuple('BinOp', ['left', 'op', 'right'])
Number = namedtuple('Number', ['value'])
String = namedtuple('String', ['value'])
Var = namedtuple('Var', ['name'])
MethodCall = namedtuple('MethodCall', ['class_name', 'method_name', 'args'])
Print = namedtuple('Print', ['expr'])
WhileLoop = namedtuple('WhileLoop', ['condition', 'body'])
ForLoop = namedtuple('ForLoop', ['init', 'condition', 'step', 'body'])
Block = namedtuple('Block', ['statements'])
MethodDef = namedtuple('MethodDef', ['name', 'params', 'body', 'is_static'])
ClassDef = namedtuple('ClassDef', ['name', 'methods'])
Program = namedtuple('Program', ['classes'])

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def expect(self, kind, value=None):
        tok = self.current()
        if tok[0] != kind or (value is not None and tok[1] != value):
            raise SyntaxError(f"Expected {kind} {value} but got {tok}")
        self.pos += 1
        return tok[1]

    def match(self, kind, value=None):
        if self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            if tok[0] == kind and (value is None or tok[1] == value):
                self.pos += 1
                return tok[1]
        return None

    def parse(self):
        classes = []
        while self.pos < len(self.tokens):
            classes.append(self.parse_class())
        return Program(classes)

    def parse_class(self):
        self.expect('ID', 'class')
        name = self.expect('ID')
        self.expect('LBRACE')
        methods = []
        while self.current()[0] != 'RBRACE':
            methods.append(self.parse_method())
        self.expect('RBRACE')
        return ClassDef(name, methods)

    def parse_method(self):
        is_static = False
        if self.match('ID', 'static'):
            is_static = True
        # void return type assumed for now
        self.expect('ID', 'void')
        name = self.expect('ID')
        self.expect('LPAREN')
        params = self.parse_params()
        self.expect('RPAREN')
        body = self.parse_block()
        return MethodDef(name, params, body, is_static)

    def parse_params(self):
        params = []
        if self.current()[0] != 'RPAREN':
            while True:
                ptype = self.expect('ID')
                pname = self.expect('ID')
                params.append((ptype, pname))
                if not self.match('COMMA'):
                    break
        return params

    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while self.current()[0] != 'RBRACE':
            stmts.append(self.parse_statement())
        self.expect('RBRACE')
        return Block(stmts)

    def parse_statement(self):
        tok = self.current()
        if tok[0] == 'ID' and tok[1] in ('int', 'float', 'string'):
            return self.parse_var_decl()
        elif tok[0] == 'ID' and tok[1] == 'while':
            return self.parse_while()
        elif tok[0] == 'ID' and tok[1] == 'for':
            return self.parse_for()
        elif tok[0] == 'ID' and tok[1] == 'print':
            return self.parse_print()
        elif tok[0] == 'ID':
            # Could be assign or method call
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] == 'OP' and self.tokens[self.pos + 1][1] == '=':
                return self.parse_assign()
            else:
                return self.parse_method_call()
        else:
            raise SyntaxError(f"Unexpected token {tok}")

    def parse_var_decl(self):
        vtype = self.expect('ID')
        name = self.expect('ID')
        self.expect('OP', '=')
        value = self.parse_expr()
        self.expect('SEMICOLON')
        return VarDecl(vtype, name, value)

    def parse_assign(self):
        name = self.expect('ID')
        self.expect('OP', '=')
        value = self.parse_expr()
        self.expect('SEMICOLON')
        return Assign(name, value)

    def parse_print(self):
        self.expect('ID', 'print')
        self.expect('LPAREN')
        expr = self.parse_expr()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return Print(expr)

    def parse_while(self):
        self.expect('ID', 'while')
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileLoop(cond, body)

    def parse_for(self):
        self.expect('ID', 'for')
        self.expect('LPAREN')
        init = self.parse_statement()  # Expect var decl or assign with semicolon
        cond = self.parse_expr()
        self.expect('SEMICOLON')
        step = self.parse_assign()
        self.expect('RPAREN')
        body = self.parse_block()
        return ForLoop(init, cond, step, body)

    def parse_method_call(self):
        # e.g. System.print("hi");
        class_name = self.expect('ID')
        self.expect('OP', '.')
        method_name = self.expect('ID')
        self.expect('LPAREN')
        args = []
        if self.current()[0] != 'RPAREN':
            while True:
                args.append(self.parse_expr())
                if not self.match('COMMA'):
                    break
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return MethodCall(class_name, method_name, args)

    def parse_expr(self):
        # Simple expr for demo (only support numbers, vars, string literals, + operation)
        left = self.parse_term()
        while self.current()[0] == 'OP' and self.current()[1] == '+':
            op = self.expect('OP')
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    def parse_term(self):
        tok = self.current()
        if tok[0] == 'NUMBER':
            self.pos += 1
            return Number(tok[1])
        elif tok[0] == 'STRING':
            self.pos += 1
            return String(tok[1])
        elif tok[0] == 'ID':
            self.pos += 1
            return Var(tok[1])
        elif tok[0] == 'LPAREN':
            self.pos += 1
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token in expression {tok}")
