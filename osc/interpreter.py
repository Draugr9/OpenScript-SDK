from osc.parser import *

class BuiltinSystem:
    @staticmethod
    def print(*args):
        print(*args)

class BuiltinMath:
    @staticmethod
    def add(a, b): return a + b
    @staticmethod
    def sub(a, b): return a - b
    @staticmethod
    def mul(a, b): return a * b
    @staticmethod
    def div(a, b): return a / b

class Env:
    def __init__(self):
        self.vars = {}
        self.types = {}
        self.classes = {
            "System": BuiltinSystem,
            "Math": BuiltinMath,
        }

    def declare_var(self, name, value, declared_type):
        if declared_type == "int" and not isinstance(value, int):
            raise TypeError(f"Variable {name} must be int")
        if declared_type == "float" and not isinstance(value, float):
            raise TypeError(f"Variable {name} must be float")
        if declared_type == "string" and not isinstance(value, str):
            raise TypeError(f"Variable {name} must be string")
        self.vars[name] = value
        self.types[name] = declared_type

    def assign_var(self, name, value):
        if name not in self.vars:
            raise NameError(f"Variable {name} not declared")
        declared_type = self.types[name]
        if declared_type == "int" and not isinstance(value, int):
            raise TypeError(f"{name} is int, got {type(value)}")
        if declared_type == "float" and not isinstance(value, float):
            raise TypeError(f"{name} is float, got {type(value)}")
        if declared_type == "string" and not isinstance(value, str):
            raise TypeError(f"{name} is string, got {type(value)}")
        self.vars[name] = value

    def get_var(self, name):
        if name not in self.vars:
            raise NameError(f"Variable {name} not declared")
        return self.vars[name]

    def call_static_method(self, class_name, method_name, args):
        cls = self.classes.get(class_name)
        if not cls:
            raise Exception(f"Class {class_name} not found")
        method = getattr(cls, method_name, None)
        if not method:
            raise Exception(f"Method {method_name} not found in {class_name}")
        return method(*args)

def eval_expr(node, env):
    if isinstance(node, Number):
        return node.value
    if isinstance(node, String):
        return node.value
    if isinstance(node, Var):
        return env.get_var(node.name)
    if isinstance(node, BinOp):
        left = eval_expr(node.left, env)
        right = eval_expr(node.right, env)
        if node.op == '+':
            return left + right
        raise Exception(f"Unsupported operator {node.op}")
    raise Exception(f"Unknown expression node {node}")

def exec_stmt(stmt, env):
    if isinstance(stmt, VarDecl):
        val = eval_expr(stmt.value, env)
        env.declare_var(stmt.name, val, stmt.type)
    elif isinstance(stmt, Assign):
        val = eval_expr(stmt.value, env)
        env.assign_var(stmt.name, val)
    elif isinstance(stmt, Print):
        val = eval_expr(stmt.expr, env)
        print(val)
    elif isinstance(stmt, WhileLoop):
        while eval_expr(stmt.condition, env):
            for s in stmt.body.statements:
                exec_stmt(s, env)
    elif isinstance(stmt, ForLoop):
        exec_stmt(stmt.init, env)
        while eval_expr(stmt.condition, env):
            for s in stmt.body.statements:
                exec_stmt(s, env)
            exec_stmt(stmt.step, env)
    elif isinstance(stmt, MethodCall):
        args = [eval_expr(arg, env) for arg in stmt.args]
        env.call_static_method(stmt.class_name, stmt.method_name, args)
    else:
        raise Exception(f"Unknown statement {stmt}")

def exec_method(method, env):
    for stmt in method.body.statements:
        exec_stmt(stmt, env)

def exec_class(cls, env):
    # Find static main and run it
    for method in cls.methods:
        if method.is_static and method.name == 'main':
            exec_method(method, env)
