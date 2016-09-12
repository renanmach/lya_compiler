#!/usr/bin/python
# -*- coding: utf-8 -*-

import ply.lex as lex

class LyaLexer:
    def __init__(self):
        self.lexer = lex.lex(optimize=1, module=self)
        self.error = False

    reserved = {
        'array': 'ARRAY',
        'by': 'BY',
        'chars': 'CHARS',
        'dcl': 'DCL',
        'do': 'DO',
        'down': 'DOWN',
        'else': 'ELSE',
        'elsif' : 'ELSIF',
        'end': 'END',
        'exit': 'EXIT',
        'fi': 'FI',
        'for': 'FOR',
        'if': 'IF',
        'in': 'IN',
        'loc': 'LOC',
        'type': 'TYPE',
        'od': 'OD',
        'proc': 'PROC',
        'ref': 'REF',
        'result': 'RESULT',
        'return': 'RETURN',
        'returns': 'RETURNS',
        'syn': 'SYN',
        'then': 'THEN',
        'to': 'TO',
        'while': 'WHILE'
    }

    predefined = {
        'bool': 'BOOL',
        'char': 'CHAR',
        'false': 'FALSE',
        'int': 'INT',
        'length': 'LENGTH',
        'lower': 'LOWER',
        'null': 'NULL',
        'num': 'NUM',
        'pred': 'PRED',
        'print': 'PRINT',
        'read': 'READ',
        'succ': 'SUCC',
        'true': 'TRUE',
        'upper': 'UPPER'
    }

    tokens = [
        ### nós colocamos
        'AND',
        'OR',
        'NOT',
        'EQUAL',
        'NOTEQUAL',
        'GREATER',
        'GREATEREQUAL',
        'LESS',
        'LESSEQUAL',
        'COMMA',
        'COLON',
        'ARROW',
        'SCONC',
        'MODUS',
        'CARET',
        ### da página projeto 1
        'ID',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'ASSIGN',
        'SEMI',
        'LPAREN',
        'RPAREN',
        'LBRACKET',
        'RBRACKET',
        'ICONST',
        'CCONST',
        'SCONST',
        'SQUOTE'
        ] + list(reserved.values()) + list(predefined.values())

    t_IF = r'if'
    t_FI = r'fi'
    t_DO = r'do'
    t_OD = r'od'

    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_EQUAL = r'=='
    t_NOTEQUAL = r'!='
    t_GREATER = r'>'
    t_GREATEREQUAL = r'>='
    t_LESS = r'<'
    t_LESSEQUAL = r'<='
    t_COMMA = r','
    t_COLON = r':'
    t_ARROW = r'->'
    t_SCONC = r'&'
    t_MODUS = r'%'
    t_CARET = r'^'

    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_ASSIGN = r'='
    t_SEMI = r';'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'

    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'

    t_SQUOTE = r'\''

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*' 
        t.type = self.reserved.get(t.value, 'ID')
        if(t.type == 'ID'):
            t.type = self.predefined.get(t.value, 'ID')
        return t

    def t_ICONST(self, t):
        r'\d+'
        t.value = int(t.value)    
        return t

    def t_CCONST(self, t):
        r"'.'"
        t.value = str(t.value[1])
        return t
        
    def t_SCONST(self, t):
        r'"(.*?)"'
#        if "\\n" in t.value: #tem um \n de erro no meio
#            self.t_error(t)
        value = t.value
        value = value[1:-1]
        
        strpieces = []
        while value != "":
            loc = value.find("\\")
            if loc != -1:
                strpieces.append(value[:loc])
                try:
                    follower = value[loc+1]
                    if follower == "t":
                        strpieces.append("\\t")
                    elif follower == "n":
                        strpieces.append("\\n")
                    elif follower == '"':
                        strpieces.append("\\\"")
                    elif follower == "\\":
                        strpieces.append("\\\\")
                    else: #value different
                        print "%d: Bad string escape code '\%s'" % t.lexer.lineno, value[loc+1]
                except: #no character after
                    print "%d: String ends with '\\' - ignored" % t.lexer.lineno

                value = value[loc+2:] #continue on the remaining of string
            else: #if nothing left join the rest
                strpieces.append(value)
                value = ""
        value = "".join(strpieces)
        t.value = value
        return t

    def t_ignore_comment(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)'
        t.lexer.lineno += t.value.count('\n')
        pass
        
    def t_unfinished_comment(self, t):
        r'(/\*(.|\n)*?\Z)'
        print ">>>> " + str(t.lexer.lineno) + " Unterminated comment"
        pass

    def t_str_err_test(self, t):
        pass

    def t_str_escape_error(self, t):
        pass

    def t_error(self, t):
        self.error = True
        if t.value[0] == '"':
            self.error_message = str(t.lexer.lineno) + ": Unterminated string"
        else:
            self.error_message = "Illegal character '" + t.value[0] + "'"
        t.lexer.skip(1)
     
    def to_token(self, data):
        self.error = False
        self.error_message = ""
        # Build the lexer
        self.lexer = lex.lex(optimize=1, module=self)
        toks = []
        # Give the lexer some input
        self.lexer.input(data)
        # Tokenize
        while True:
            tok = self.lexer.token()
            if not tok: 
                break
            elif self.error:
                return self.error_message
            toks.append(tok)
        return toks

