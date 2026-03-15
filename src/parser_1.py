# Alpha J Language - Parser (Syntax Analysis)
# Built with PLY (Python Lex-Yacc)
# Language: Alpha J/MiniCalc++
# Course: CIT4004 - Anaylsis of Programming Languages
# University of Technology, Jamaica

import ply.yacc as yacc
from lexer import tokens, lexer

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'POWER')
)

#starting rule
def program(p):
    '''
    program : statements '''
    p[0]= ("program", p[1])

#statement list 
def p_statement_list(p):
    '''
    statement_list : statement '''
    p[0]= [p[1]]
    

def multi_statements(p):
    '''
    statement_list : statement_list statement '''
    p[0]= p[1] + [[p2]]

#types of statements 
 def p_statement(p):
    '''
    statement : declaration
                |broadcast_stmt
                |try_catch
                |if_stmt
                |cycle_stmt
                |notes '''   
    p[0]= p[1]

def p_declaration(p):
    '''
    declaration: YOUARE ID ASSIGNTO expression '''
    p[0]= ("declare", p[2], p[4])

def p_broadcast_stmt(p):
    '''
    broadcast_stmt: BROADCAST broadcast_args '''
    p[0]= ("broadcast", p[2])

def p_single_broadcast_args(p):
    '''
    broadcast_args: broadcast_arg '''
    p[0]= [p[1]]

def p_multi_broadcast_args(p):
    '''
    broadcast_args: broadcast_args broardcast_arg '''
    p[0]= p[1] + [[p2]]

def p_broadcast_arg_string(p):
    '''
    broargcast_arg: STRING '''
    p[0]= [p[1]]

def p_broadcast_arg_expression(p):
    '''
    broargcast_arg: expression '''
    p[0]= [p[1]]

def try_catch(p):
    '''
    try_catch: TRY statement_list CATCH statement_list END '''
    p[0]= ("trycatch", p[2], p[4])

    