# Alpha J Language - Parser (Syntax Analysis)
# Built with PLY (Python Lex-Yacc)
# Language: Alpha J/MiniCalc++
# Course: CIT4004 - Anaylsis of Programming Languages
# University of Technology, Jamaica

import ply.yacc as yacc
from src.lexer import tokens, lexer

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'POWER'),
    ('right', 'UMINUS'),
)
                #GRAMMER RULES

#<program> ::= <statement_list>
def p_program(p):
    '''program : statement_list'''
    p[0] = ('program', p[1])

#statement list
def p_statement_list_single(p):
    '''statement_list : statement'''
    p[0] = [p[1]]

#This accounts for multiple statements
def p_statement_list_multi(p):
    '''statement_list : statement_list statement'''
    p[0] = p[1] + [p[2]]

#types of statements
def p_statement(p):
    '''statement : declaration
            | assignment
            | broadcast_stmt
            | try_catch
            | if_stmt
            | cycle_stmt'''
    p[0] = p[1]

# ignore empty lines
def p_newline(p):
    '''statement : NEWLINE'''
    p[0] = None

def p_assignment(p):
    '''assignment : ID ASSIGNTO expression'''
    p[0] = ("assign", p[1], p[3])


def p_declaration(p):
    '''declaration : YOUARE ID ASSIGNTO expression'''
    p[0] = ("declare", p[2], p[4])

def p_broadcast_stmt(p):
    '''broadcast_stmt : BROADCAST broadcast_args'''
    p[0] = ("broadcast", p[2])

def p_single_broadcast_args(p):
    '''broadcast_args : broadcast_arg '''
    p[0] = [p[1]]

def p_multi_broadcast_args(p):
    '''broadcast_args : broadcast_args broadcast_arg '''
    p[0] = p[1] + [p[2]]

def p_broadcast_arg_string(p):
    '''broadcast_arg : STRING '''
    p[0] = ('string', p[1])

def p_broadcast_arg_expression(p):
    '''broadcast_arg : expression '''
    p[0] = ('expr', p[1])

def p_try_catch(p):
    '''try_catch : TRY statement_list CATCH statement_list END '''
    p[0] = ('try_catch', p[2], p[4])

def p_if_stmt(p):
    '''if_stmt : IF condition statement_list END
         | IF condition statement_list FALLBACK statement_list END '''
    if len(p)==5:
        p[0] = ("if", p[2], p[3], None)

    #Fallback statement
    else:
        p[0] = ("if", p[2], p[3], p[5])

def p_cycle_stmt(p):
    '''cycle_stmt : CYCLE condition statement_list END '''
    p[0]= ("cycle", p[2], p[3])

def p_condition(p):
    '''condition : expression EQT expression
             | expression NEQT expression
             | expression LT expression
             | expression GT expression
             | expression LTE expression
             | expression GTE expression '''
    p[0]= ('relop', p[2], p[1], p[3])

def p_expression_add(p):
    '''expression : expression PLUS term
            | expression MINUS term '''
    p[0] = ('binop', p[2], p[1], p[3])


def p_expression_term(p):
    '''expression : term '''
    p[0] = p[1]

def p_multi_term(p):
    '''term : term TIMES factor
         | term DIVIDE factor '''
    p[0] = (p[2], p[1], p[3])


def p_term_factor(p):
    '''term : factor '''
    p[0] = p[1]

def p_factor_power(p):
    '''factor : base POWER factor '''
    p[0] = ("^", p[1], p[3])


def p_factor_base(p):
    '''factor : base '''
    p[0] = p[1]

#breaks infinite recursion loop
def p_base(p):
    '''
    base : NUMBER
         | ID
         | LT_PARENT expression RT_PARENT
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

# Unary minus e.g. -5 or -x
def p_base_uminus(p):
    '''base : MINUS base %prec UMINUS'''
    p[0] = ('unary_minus', p[2])


def p_error(p):
    if p:
        print(f"[Alpha J Parser Error] Unexpected token '{p.value}'")
    else:
        print("[Alpha J Parser Error] Unexpected end of input")

parser = yacc.yacc()


#TESTMAIN
if __name__ == "__main__":

    data = '''
    youare x = 10
    youare y = 5

    broadcast "x = " x

    if x > y
        broadcast "x bigger"
    fallback
        broadcast "y bigger"
    end

    cycle x < 15
        broadcast x
        x = x + 1
    end

    try
        broadcast "Running"
    catch
        broadcast "Error"
    end
    '''

    result = parser.parse(data)

    print(result)