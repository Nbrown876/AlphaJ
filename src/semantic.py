from dataclasses import dataclass
from typing import Dict, List, Optional


class SemanticError(Exception):
    """Semantic Analysis Failure indicator."""
    pass


@dataclass
class Symbol:
    name: str
    var_type: str
    scope_level: int


class SemanticAnalyzer:
    def __init__(self):
        # stack of scopes; scope[0] is a global scope
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.errors: List[str] = []

    # Management of the scope
    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def current_scope_level(self) -> int:
        return len(self.scopes) - 1

    # Operations of the Symbol Table
    def declare(self, name: str, var_type: str):
        current_scope = self.scopes[-1]
        if name in current_scope:
            self.errors.append(
                f"Semantic Error: Variable '{name}' already declared in current scope."
            )
        else:
            current_scope[name] = Symbol(name, var_type, self.current_scope_level())

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_in_current_scope(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    # Public Point of Entry
    def analyze(self, ast):
        self.visit(ast)
        if self.errors:
            raise SemanticError("\n".join(self.errors))

        return True

    # AST Visitor Dispatcher
    def visit(self, node):
        if node is None:
            return None

        # literals
        if isinstance(node, int):
            return "number"

        if isinstance(node, float):
            return "number"

        if isinstance(node, str):
            symbol = self.lookup(node)
            if symbol is None:
                self.errors.append(
                    f"Semantic Error: Variable '{node}' used before declaration."
                )
                return "error"
            return symbol.var_type

        if isinstance(node, list):
            result = None
            for item in node:
                result = self.visit(item)
            return result

        if isinstance(node, tuple):
            node_type = node[0]

            # AST roots and statements
            if node_type == "program":
                return self.visit_program(node)
            if node_type == "declare":
                return self.visit_declare(node)
            if node_type == "assign":
                return self.visit_assign(node)
            if node_type == "broadcast":
                return self.visit_broadcast(node)
            if node_type == "try_catch":
                return self.visit_try_catch(node)
            if node_type == "if":
                return self.visit_if(node)
            if node_type == "cycle":
                return self.visit_cycle(node)
            if node_type == "notes":
                return self.visit_notes(node)

            # expressions and conditions
            if node_type == "relop":
                return self.visit_relop(node)
            if node_type == "binop":
                return self.visit_binop(node)
            if node_type == "unary_minus":
                return self.visit_unary_minus(node)
            if node_type == "string":
                return "string"
            if node_type == "expr":
                return self.visit(node[1])

            # raw operator tuples
            if node_type in {"+", "-", "*", "/", "^"}:
                return self.visit_raw_binop(node)

        self.errors.append(f"Semantic Error: Unknown AST node {node}")
        return "error"

    # Statement Visitors
    def visit_program(self, node):
        _, statement_list = node
        for stmt in statement_list:
            if stmt is not None:
                self.visit(stmt)
        return None

    def visit_declare(self, node):
        _, name, expr = node
        expr_type = self.visit(expr)

        if expr_type == "error":
            return "error"

        # declare only once per current scope
        if self.lookup_in_current_scope(name):
            self.errors.append(
                f"Semantic Error: Variable '{name}' is already declared in this scope."
            )
            return "error"

        self.declare(name, expr_type)
        return None

    def visit_assign(self, node):
        _, name, expr = node

        symbol = self.lookup(name)
        if symbol is None:
            self.errors.append(
                f"Semantic Error: Variable '{name}' must be declared before assignment."
            )
            return "error"

        expr_type = self.visit(expr)
        if expr_type == "error":
            return "error"

        if symbol.var_type != expr_type:
            self.errors.append(
                f"Semantic Error: Type mismatch in assignment to variable '{name}'."
            )
            return "error"

        return None

    def visit_broadcast(self, node):
        _, args = node
        for arg in args:
            arg_type = self.visit(arg)
            if arg_type == "error":
                return "error"
        return None

    def visit_try_catch(self, node):
        _, try_block, catch_block = node

        # scope for try and catch block
        self.enter_scope()
        for stmt in try_block:
            if stmt is not None:
                self.visit(stmt)
        self.exit_scope()

        self.enter_scope()
        for stmt in catch_block:
            if stmt is not None:
                self.visit(stmt)
        self.exit_scope()

        return None

    def visit_if(self, node):
        _, condition, then_block, else_block = node

        cond_type = self.visit(condition)
        if cond_type != "boolean" and cond_type != "error":
            self.errors.append(
                "Semantic Error: IF condition must be evaluated to boolean."
            )

        self.enter_scope()
        for stmt in then_block:
            if stmt is not None:
                self.visit(stmt)
        self.exit_scope()

        if else_block is not None:
            self.enter_scope()
            for stmt in else_block:
                if stmt is not None:
                    self.visit(stmt)
            self.exit_scope()

        return None

    def visit_cycle(self, node):
        _, condition, body = node

        cond_type = self.visit(condition)
        if cond_type != "boolean" and cond_type != "error":
            self.errors.append(
                "Semantic Error: CYCLE condition must be evaluated to boolean."
            )

        self.enter_scope()
        for stmt in body:
            if stmt is not None:
                self.visit(stmt)
        self.exit_scope()

        return None

    def visit_notes(self, node):
        # notes are ignored during analysis
        return None
