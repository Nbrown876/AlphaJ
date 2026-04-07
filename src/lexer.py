# Alpha J Language - Lexer (Tokenizer)
# Built with PLY (Python Lex-Yacc)
# Language: Alpha J
# Course: CIT4004 - Anaylsis of Programming Languages
# University of Technology, Jamaica
# Jonique Hosang Shaw, Neechelo Brown, Leigh-Ann Cammock, Damani Poyser

import ply.lex as lex

# Reserved Keywords
reserved = {
    'youare'     : 'YOUARE',
    'broadcast'  : 'BROADCAST',
    'try'        : 'TRY',
    'catch'      : 'CATCH',
    'if'         : 'IF',
    'fallback'   : 'FALLBACK',
    'cycle'      : 'CYCLE',
    'end'        : 'END',
}

#Full Token List
tokens = [
    'ID',
    'NUMBER',
    'STRING',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'POWER',
    'ASSIGNTO',
    'EQT',
    'NEQT',
    'LTE',
    'GTE',
    'LT',
    'GT',
    'LT_PARENT',
    'RT_PARENT',
    'NOTES',
    'NEWLINE',
] + list(reserved.values())

#Token rules
t_EQT        = r'=='
t_NEQT       = r'!='
t_LTE        = r'<='
t_GTE        = r'>='
t_LT         = r'<'
t_GT         = r'>'
t_PLUS       = r'\+'
t_MINUS      = r'-'
t_TIMES      = r'\*'
t_DIVIDE     = r'/'
t_POWER      = r'\^'
t_ASSIGNTO   = r'='
t_LT_PARENT  = r'[(]'
t_RT_PARENT  = r'[)]'


#Our Complex Token Rules
def t_NOTES(t):
    r'@@[^\n]*'
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in str(t.value) else int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID') #Checks the reserved words first
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value) #Tracks the number of lines
    return t

#THis is used for Ignoring spaces and tabs
t_ignore = ' \t'

def t_error(t):
    print(f"[Alpha J Lexer Error] Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

#Build the lexer
lexer = lex.lex()

#Quick Test
if __name__ == "__main__":
    test = "youare A = 20 + 30"
    lexer.input(test)
    for tok in lexer:
        print(tok)

