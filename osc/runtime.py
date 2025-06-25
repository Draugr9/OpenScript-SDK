from osc.lexer import tokenize
from osc.parser import Parser
from osc.interpreter import exec_class, Env

def run(code):
    tokens = tokenize(code)
    parser = Parser(tokens)
    program = parser.parse()
    env = Env()
    for cls in program.classes:
        exec_class(cls, env)
