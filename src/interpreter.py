# ============================================
# Alpha J Language - Interpreter
# Language: Alpha J
# Course: CIT4004 - Analysis of Programming Languages
# University of Technology, Jamaica
# ============================================

# Exception class used to trap runtime interpreter errors (e.g., division by zero, undefined variables)
class InterpreterError(Exception):
    pass

# ============================================
# Environment Handler (Scope and Memory Map)
# ============================================
class Environment:
    def __init__(self, enclosing=None):
        # Dictionary linking variable identifiers to their assigned values
        self.values = {}
        
        # Reference to the enclosing (parent) scope, if one exists (e.g., global scope outside a cycle block)
        self.enclosing = enclosing

    # Declares a new variable exclusively in the current local scope
    # Alpha J mapping: `youare x = 5`
    def define(self, name, value):
        self.values[name] = value

    # Updates an existing variable
    # Alpha J mapping: `x = x + 1`
    def assign(self, name, value):
        # If the variable exists in the current scope, update it
        if name in self.values:
            self.values[name] = value
            return
        
        # If the variable exists in an outer scope, traverse upwards and update it there
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        # Fails if the variable was never declared in any accessible scope
        raise InterpreterError(f"Interpreter Error: Undefined variable '{name}'.")

    # Retrieves a variable's stored value
    def get(self, name):
        if name in self.values:
            return self.values[name]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
            
        raise InterpreterError(f"Interpreter Error: Undefined variable '{name}'.")

# ============================================
# AST Walker Engine
# ============================================
class Interpreter:
    def __init__(self):
        # Initialize the baseline global environment
        self.globals = Environment()
        
        # Set the active execution environment pointers
        self.environment = self.globals
        
        # Maintain an execution log specifically for verifying outputs against LLM testing loops later
        self.output_log = []

    # Utility method to handle standard out while pushing to the trace log
    def log_output(self, message):
        msg_str = str(message)
        print(msg_str)
        self.output_log.append(msg_str)

    # Master execution interface. Traps InterpreterErrors gracefully without crashing the core thread.
    def interpret(self, ast):
        try:
            self.evaluate(ast)
        except InterpreterError as err:
            self.log_output(str(err))

    # Core AST evaluation cycle recursively processing incoming node tuples.
    def evaluate(self, node):
        if node is None:
            return None
        
        # Base case: Node is directly a constant numerical value
        if isinstance(node, (int, float)):
            return node
            
        # Base case: Node is a raw string identifier; retrieve its resolved value from the environment
        if isinstance(node, str):
            return self.environment.get(node)

        # Standard statement blocks represent consecutive AST structures via lists
        if isinstance(node, list):
            result = None
            for item in node:
                result = self.evaluate(item) 
            return result

        # Alpha J's parser emits parsed AST elements as tuples mapping to structural logic trees
        if isinstance(node, tuple):
            
            node_type = node[0]

            # ---------------------------
            # Statement Handlers
            # ---------------------------

            # Program Root Node
            if node_type == "program":
                _, stmt_list = node
                return self.evaluate(stmt_list)

            # Declaration Node Handler
            # Alpha J mapping: `youare name = expr`
            # AST Structure: ('declare', 'name', <expression tuple>)
            elif node_type == "declare":
                _, name, expr = node
                val = self.evaluate(expr)     
                self.environment.define(name, val) 
                return None
                
            # Assignment Node Handler
            # Alpha J mapping: `name = expr`
            # AST Structure: ('assign', 'name', <expression tuple>)
            elif node_type == "assign":
                _, name, expr = node
                val = self.evaluate(expr)
                self.environment.assign(name, val)
                return None

            # Standard Output Protocol
            # Alpha J mapping: `broadcast "Result: " x`
            # AST Structure: ('broadcast', [('string', '"Result: "'), ('expr', 'x')])
            elif node_type == "broadcast":
                _, args = node
                out_parts = []
                for arg in args:
                    if arg[0] == 'string':
                        # Stripping boundary quote tags prior to rendering out
                        s = arg[1]
                        if s.startswith('"') and s.endswith('"'):
                            s = s[1:-1]
                        out_parts.append(s)
                    elif arg[0] == 'expr':
                        # Evaluating numeric/variable logic and casting to string representation
                        out_parts.append(str(self.evaluate(arg[1]))) 
                
                self.log_output("".join(out_parts))
                return None

            # Exception Catch Logic
            # Alpha J mapping: `try <stmt block> catch <stmt block> end`
            elif node_type == "try_catch":
                _, try_block, catch_block = node
                previous_env = self.environment 
                
                try:
                    # Isolate standard try execution within an temporary sub-scope 
                    self.environment = Environment(previous_env) 
                    self.evaluate(try_block)                     
                except Exception as e:
                    # Switch to fallback catch block over a fresh temporary execution environment
                    self.environment = Environment(previous_env) 
                    self.evaluate(catch_block)                   
                finally:
                    # Rollback memory to the original encapsulating scope guaranteeing memory safety
                    self.environment = previous_env
                return None

            # Conditional IF Statement Handler
            # Alpha J mapping: `if condition <stmt block> fallback <stmt block> end`
            elif node_type == "if":
                _, condition, then_block, else_block = node
                
                if self.evaluate(condition):
                    previous_env = self.environment
                    self.environment = Environment(previous_env) 
                    self.evaluate(then_block)
                    self.environment = previous_env
                elif else_block is not None:
                    previous_env = self.environment
                    self.environment = Environment(previous_env)
                    self.evaluate(else_block)
                    self.environment = previous_env
                return None

            # Looping Block Handler
            # Alpha J mapping: `cycle condition <stmt block> end`
            elif node_type == "cycle":
                _, condition, body = node
                
                # Resolving boolean parameters each execution loop 
                while self.evaluate(condition):
                    previous_env = self.environment
                    self.environment = Environment(previous_env)
                    self.evaluate(body)
                    self.environment = previous_env
                return None

            # ---------------------------
            # Expression/Binary Operation Logic
            # ---------------------------

            # Relational Operators handling comparisons
            # Handled Operators: ==, !=, >, <, >=, <=
            elif node_type == "relop":
                _, op, left, right = node
                l = self.evaluate(left)   
                r = self.evaluate(right)  
                
                if op == '==': return l == r
                if op == '!=': return l != r
                if op == '<':  return l < r
                if op == '<=': return l <= r
                if op == '>':  return l > r
                if op == '>=': return l >= r
                
            # Binary Math Operators (+, -, *, /)
            # The compound OR logic merges inconsistency generated by Alpha J's parser mapping 
            # ("binop", "+", left, right) vs directly indexing ("*", left, right).
            elif node_type == "binop" or node_type in {"+", "-", "*", "/", "^"}:
                
                if node_type == "binop":
                    _, op, left, right = node # Discards leading identifier via '_' discard binding.
                else: 
                    op = node_type
                    left = node[1]
                    right = node[2]

                # Process sides recursively for nested math calculations (e.g., 5 + 3 * 2) 
                l = self.evaluate(left)
                r = self.evaluate(right)
                
                if op == '+': return l + r
                if op == '-': return l - r
                if op == '*': return l * r
                if op == '/':
                    if r == 0:
                        raise InterpreterError("Interpreter Error: Division by zero attempted.")
                    return l / r
                if op == '^': return l ** r


            #String Node Handler
            elif node_type == "string":
                s = node[1]
                if s.startswith('"') and s.endswith('"'):
                    s = s[1:-1]
                return s    

            # Comments - do nothing
            elif node_type == "notes":
                return None

            # Numeric Negation
            # Alpha J mapping: `-5`
            elif node_type == "unary_minus":
                _, expr = node
                return -self.evaluate(expr)

        
        # Hard system fault if an unexpected structural identifier attempts parsing
        raise InterpreterError(f"Interpreter Error: Unrecognized AST node {node}")

# ==========================================
# Development Environment Test Runtime
# ==========================================
if __name__ == "__main__":
    import sys, os
    
    # Establish dynamic project rooting for relative execution testing
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.parser.parser_1 import parser
    from src.lexer import lexer

    # Alpha J Verification Application Script
    code = '''
youare x = -10
youare y = -50

youare s = 100
youare t = 200
broadcast "Initial Variables: x = " x " y = " y

if x > y
    broadcast "x is bigger than y"

    if s > t
        broadcast "s is bigger than t"
    fallback
        broadcast "t is bigger than s"
    end

fallback
    broadcast "y is bigger than x"
end

@@ this is a cycle loop properly using assignment without redeclaring!
youare c = 0
cycle c < 11
    broadcast "Cycle Iteration: " c
    x = x + 1
    c = c + 1
end

broadcast "x is now: " x

try
    broadcast "Attempting division by zero..."
    youare z = x / 0
catch
    broadcast "Caught exception! Resuming safely."
end

broadcast "Program execution successful!"
'''
    print("========================================")
    print("Executing Sample Code:")
    print("========================================")
    
    # 1. Trigger Tokenizer/Parser phase yielding active AST mapping  
    ast = parser.parse(code, lexer=lexer)
    
    # 2. Assign root interpreter execution context pointer
    interpreter = Interpreter()
    
    # 3. Fire deterministic evaluation phase 
    interpreter.interpret(ast)
    
    print("========================================")
