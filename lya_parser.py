#!/usr/bin/python
# -*- coding: utf-8 -*-

import ply.yacc as yacc
from lya_lex import LyaLexer
from lya_ast import *


class LyaParser:
    def __init__(self):
        self.tokens = LyaLexer.tokens
        self.parser = yacc.yacc(optimize=1, debug=0, write_tables=True, module=self)
        self.lexer = LyaLexer().lexer
    
    precedence = (
            ('left', 'AND', 'OR', 'NOT'),
            ('left', 'EQUAL', 'NOTEQUAL'),
            ('left', 'GREATER', 'GREATEREQUAL', 'LESS', 'LESSEQUAL'),
            ('left', 'IN'),
            ('left', 'PLUS', 'MINUS'),
            ('left', 'SCONC'),
            ('left', 'TIMES', 'DIVIDE', 'MODUS')
    )

    def p_program(self, p):
        '''program : statement_list'''
        p[0] = Program(p[1], lineno=p.lineno(1))

    def p_statement_list(self, p):
        '''statement_list : statement 
                | statement statement_list'''
        if len(p) == 2:
            p[0] = Statement_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Statement_list(self.flat([p[1], p[2].statements]), lineno=p.lineno(1))

    def p_statement(self, p):
        '''statement : declaration_statement 
                | synonym_statement 
                | newmode_statement 
                | procedure_statement 
                | action_statement'''
        p[0] = p[1]

    def p_declaration_statement(self, p):
        '''declaration_statement : DCL declaration_list SEMI'''
        p[0] = Declaration_statement(p[2], lineno=p.lineno(1))

    def p_declaration_list(self, p):
        '''declaration_list : declaration 
                | declaration COMMA declaration_list'''
        if len(p) == 2:
            p[0] = Declaration_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Declaration_list(self.flat([p[1], p[3].declarations]), lineno=p.lineno(1))

    def p_declaration(self, p):
        '''declaration : identifier_list mode 
                | identifier_list mode initialization'''
        if len(p) == 3:
            p[0] = Declaration(p[1], p[2], None, lineno=p.lineno(1))
        else:
            p[0] = Declaration(p[1], p[2], p[3], lineno=p.lineno(1))

    def p_initialization(self, p):
        '''initialization : ASSIGN expression'''
        p[0] = p[2]

    def p_identifier_list(self, p):
        '''identifier_list : identifier 
                | identifier COMMA identifier_list'''
        if len(p) == 2:
            p[0] = Identifier_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Identifier_list(self.flat([p[1], p[3].identifiers]), lineno=p.lineno(1))

    def p_identifier(self, p):
        '''identifier : ID'''
        p[0] = Identifier(p[1], lineno=p.lineno(1))

    def p_synonym_statement(self, p):
        '''synonym_statement : SYN synonym_list SEMI'''
        p[0] = p[2]

    def p_synonym_list(self, p):
        '''synonym_list : synonym_definition 
                | synonym_definition COMMA synonym_list'''
        if len(p) == 2:
            p[0] = Synonym_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Synonym_list(self.flat([p[1], p[3].synonym_definitions]), lineno=p.lineno(1))

    def p_synonym_definition(self, p):
        '''synonym_definition : identifier_list ASSIGN constant_expression
                | identifier_list mode ASSIGN constant_expression'''
        if len(p) == 4:
            p[0] = Synonym_definition(p[1], None, p[3], lineno=p.lineno(1))
        else:
            p[0] = Synonym_definition(p[1], p[2], p[4], lineno=p.lineno(1))

    def p_constant_expression(self, p):
        '''constant_expression : expression'''
        p[0] = p[1]

    def p_newmode_statement(self, p):
        '''newmode_statement : TYPE newmode_list SEMI'''
        p[0] = Newmode_statement(p[2], lineno=p.lineno(1))

    def p_newmode_list(self, p):
        '''newmode_list : mode_definition 
                | mode_definition COMMA newmode_list'''
        if len(p) == 2:
            p[0] = Newmode_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Newmode_list(self.flat([p[1], p[3].mode_definitions]), lineno=p.lineno(1))

    def p_mode_definition(self, p):
        '''mode_definition : identifier_list ASSIGN mode'''
        p[0] = Mode_definition(p[1], p[3], lineno=p.lineno(1))

    # mode_name = id
    # discrete_mode = int,bool,char,tipo discreto
    # reference_mode = REF mode
    # array_mode
    # string_mode
    def p_mode(self, p):
        '''mode : mode_name 
                | discrete_mode 
                | reference_mode
                | string_mode
                | array_mode
                | '''
        p[0] = Mode(p[1], lineno=p.lineno(1))

    def p_discrete_mode(self, p):
        '''discrete_mode : integer_mode 
                | boolean_mode 
                | character_mode
                | discrete_range_mode'''
        p[0] = Discrete_mode(p[1], lineno=p.lineno(1))

    def p_integer_mode(self, p):
        '''integer_mode : INT'''
        p[0] = p[1]

    def p_boolean_mode(self, p):
        '''boolean_mode : BOOL'''
        p[0] = p[1]

    def p_character_mode(self, p):
        '''character_mode : CHAR'''
        p[0] = p[1]

    def p_discrete_range_mode(self, p):
        '''discrete_range_mode : discrete_mode_name LPAREN literal_range RPAREN
                | discrete_mode LPAREN literal_range RPAREN'''
        p[0] = Discrete_range_mode(p[1], p[3], lineno=p.lineno(1))

    def p_mode_name(self, p):
        '''mode_name : identifier'''
        p[0] = Mode_name(p[1], lineno=p.lineno(1))

    def p_discrete_mode_name(self, p):
        '''discrete_mode_name : identifier'''
        p[0] = p[1]

    def p_literal_range(self, p):
        '''literal_range : expression COLON expression'''
        p[0] = Literal_range(p[1], p[3], lineno=p.lineno(1))

    def p_reference_mode(self, p):
        '''reference_mode : REF mode'''
        p[0] = Reference_mode(p[2], lineno=p.lineno(1))

    def p_string_mode(self, p):
        '''string_mode : CHARS LBRACKET string_length RBRACKET'''
        p[0] = String_mode(p[3], lineno=p.lineno(1))

    def p_string_length(self, p):
        '''string_length : integer_literal'''
        p[0] = String_length(p[1], lineno=p.lineno(1))

    def p_array_mode(self, p):
        '''array_mode : ARRAY LBRACKET index_list RBRACKET mode'''
        p[0] = Array_mode(p[3], p[5], lineno=p.lineno(1))

    def p_index_list(self, p):
        '''index_list : index_mode 
                | index_mode COMMA index_list'''
        if len(p) == 2:
            p[0] = Index_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Index_list(self.flat([p[1], p[3].index_modes]), lineno=p.lineno(1))

    def p_index_mode(self, p):
        '''index_mode : discrete_mode 
                | literal_range'''
        p[0] = p[1]

    def p_location(self, p):
        '''location : identifier 
                | dereferenced_reference
                | string_element
                | slice
                | procedure_call
                | builtin_call'''
        p[0] = Location(p[1], lineno=p.lineno(1))

    def p_dereferenced_reference(self, p):
        '''dereferenced_reference : location ARROW'''
        p[0] = Dereferenced_reference(p[1], lineno=p.lineno(1))

    def p_string_element(self, p):
        '''string_element : location LBRACKET expression_list RBRACKET'''
        p[0] = StringArray_element(p[1], p[3], lineno=p.lineno(1))

    def p_slice(self, p):
        '''slice : location LBRACKET expression COLON expression RBRACKET'''
        p[0] = Slice(p[1], p[3], p[5], lineno=p.lineno(1))

    def p_expression_list(self, p):
        '''expression_list : expression 
                | expression COMMA expression_list'''
        if len(p) == 2:
            p[0] = Expression_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Expression_list(self.flat([p[1], p[3].expressions]), lineno=p.lineno(1))

    def p_primitive_value(self, p):
        '''primitive_value : literal 
                | value_array_element 
                | value_array_slice 
                | parenthesized_expression'''
        p[0] = p[1]

    def p_literal(self, p):
        '''literal : integer_literal 
                | boolean_literal 
                | character_literal 
                | empty_literal 
                | character_string_literal'''
        p[0] = p[1]

    def p_integer_literal(self, p):
        '''integer_literal : ICONST'''
        p[0] = Int(p[1], lineno=p.lineno(1))

    def p_boolean_literal(self, p):
        '''boolean_literal : FALSE 
                | TRUE'''
        p[0] = Bool(p[1], lineno=p.lineno(1))

    def p_character_literal(self, p):
        '''character_literal : CCONST
                | SQUOTE CARET LPAREN ICONST RPAREN SQUOTE'''
        if len(p) == 2:
            p[0] = Char(p[1], "1", lineno=p.lineno(1))
        else:
            p[0] = Char(p[4], "2", lineno=p.lineno(1))

    def p_empty_literal(self, p):
        '''empty_literal : NULL'''
        p[0] = Empty_literal(p[1], lineno=p.lineno(1))

    def p_character_string_literal(self, p):
        '''character_string_literal : SCONST'''
        p[0] = String(p[1], lineno=p.lineno(1))

    def p_value_array_element(self, p):
        '''value_array_element : array_primitive_value LBRACKET expression_list RBRACKET'''
        p[0] = [p[1], [3]]

    def p_value_array_slice(self, p):
        '''value_array_slice : array_primitive_value LBRACKET expression COLON expression RBRACKET'''
        p[0] = [p[1], p[3]]

    def p_array_primitive_value(self, p):
        '''array_primitive_value : primitive_value'''
        p[0] = p[1]

    def p_parenthesized_expression(self, p):
        '''parenthesized_expression : LPAREN expression RPAREN'''
        p[0] = p[2]

    def p_expression(self, p):
        '''expression : operand0 
                | conditional_expression'''
        if isinstance(p[1], Expression):  # avoid creating class inside class of expression in the likeness of (((a+b)))
            p[0] = p[1]
        else:
            p[0] = Expression(p[1], lineno=p.lineno(1))

    def p_conditional_expression(self, p):
        '''conditional_expression : IF boolean_expression then_expression else_expression FI 
                | IF boolean_expression then_expression elsif_expression else_expression FI'''
        if len(p) == 6:
            p[0] = Conditional_expression(p[2], p[3], None, p[4], lineno=p.lineno(1))
        else:
            p[0] = Conditional_expression(p[2], p[3], p[4], p[5], lineno=p.lineno(1))

    def p_boolean_expression(self, p):
        '''boolean_expression : expression'''
        p[0] = p[1]

    def p_then_expression(self, p):
        '''then_expression : THEN expression'''
        p[0] = p[2]

    def p_else_expression(self, p):
        '''else_expression : ELSE expression'''
        p[0] = p[2]

    def p_elsif_expression(self, p):
        '''elsif_expression : ELSIF boolean_expression then_expression 
                | elsif_expression ELSIF boolean_expression then_expression'''
        if len(p) == 4:
            p[0] = Elsif_expression(None, p[2], p[3], lineno=p.lineno(1))
        else:
            p[0] = Elsif_expression(p[1], p[3], p[4], lineno=p.lineno(1))

    def p_operand0(self, p):
        '''operand0 : operand1
                | operand0 operator1 operand1'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Binary_Operator(p[2], p[1], p[3], lineno=p.lineno(1))

    def p_operator1(self, p):
        '''operator1 : relational_operator
                | membership_operator'''
        p[0] = p[1]

    def p_relational_operator(self, p):
        '''relational_operator : AND
                | OR
                | EQUAL
                | NOTEQUAL
                | GREATER
                | GREATEREQUAL
                | LESS
                | LESSEQUAL'''
        p[0] = p[1]

    def p_membership_operator(self, p):
        '''membership_operator : IN'''        
        p[0] = p[1]

    def p_operand1(self, p):
        '''operand1 : operand2
                | operand1 operator2 operand2'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Binary_Operator(p[2], p[1], p[3], lineno=p.lineno(1))

    def p_operator2(self, p):
        '''operator2 : arithmetic_additive_operator
                | string_concatenation_operator'''
        p[0] = p[1]

    def p_arithmetic_additive_operator(self, p):
        '''arithmetic_additive_operator : PLUS
                | MINUS'''
        p[0] = p[1]

    def p_string_concatenation_operator(self, p):
        '''string_concatenation_operator : SCONC'''
        p[0] = p[1]

    def p_operand2(self, p):
        '''operand2 : operand3
                | operand2 arithmetic_multiplicative_operator operand3'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Binary_Operator(p[2], p[1], p[3], lineno=p.lineno(1))

    def p_arithmetic_multiplicative_operator(self, p):
        '''arithmetic_multiplicative_operator : TIMES
                | DIVIDE
                | MODUS'''
        p[0] = p[1]

    def p_operand3(self, p):
        '''operand3 : operand4
                | monadic_operator operand4'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Unary_Operator(p[1], p[2], lineno=p.lineno(1))

    def p_monadic_operator(self, p):
        '''monadic_operator : MINUS
                | NOT'''
        p[0] = p[1]

    def p_operand4(self, p):
        '''operand4 : location
                | referenced_location
                | primitive_value'''
        p[0] = p[1]

    def p_referenced_location(self, p):
        '''referenced_location : ARROW location'''
        p[0] = Referenced_location(p[2], lineno=p.lineno(1))

    def p_action_statement(self, p):
        '''action_statement : identifier COLON action SEMI 
                | action SEMI'''
        if len(p) == 5:
            p[0] = Action_statement(p[3], p[1], lineno=p.lineno(1))
        else:
            p[0] = Action_statement(p[1], None, lineno=p.lineno(1))

    def p_action(self, p):
        '''action : bracketed_action
                | assignment_action 
                | procedure_call
                | builtin_call
                | exit_action 
                | return_action 
                | result_action'''
        p[0] = p[1]

    def p_bracketed_action(self, p):
        '''bracketed_action : if_action 
                | do_action'''
        p[0] = p[1]

    def p_assignment_action(self, p):
        '''assignment_action : location assigning_operator expression'''
        p[0] = Assignment_action(p[1], p[2], p[3], lineno=p.lineno(1))

    def p_assigning_operator(self, p):
        '''assigning_operator : ASSIGN
                | closed_dyadic_operator ASSIGN'''
        if len(p) == 2:
            p[0] = Assigning_operator(None, lineno=p.lineno(1))
        else:
            p[0] = Assigning_operator(p[1], lineno=p.lineno(1))

    def p_closed_dyadic_operator(self, p):
        '''closed_dyadic_operator : arithmetic_additive_operator
                | arithmetic_multiplicative_operator
                | string_concatenation_operator'''
        p[0] = p[1]

    def p_if_action(self, p):
        '''if_action : IF boolean_expression then_clause FI 
                | IF boolean_expression then_clause else_clause FI'''
        if len(p) == 5:
            p[0] = If_action(p[2], p[3], None, lineno=p.lineno(1))
        else:
            p[0] = If_action(p[2], p[3], p[4], lineno=p.lineno(1))

    def p_then_clause(self, p):
        '''then_clause : THEN 
                | THEN action_statement_list'''
        if len(p) == 2:
            p[0] = Then_clause(None, lineno=p.lineno(1))
        else:
            p[0] = Then_clause(p[2], lineno=p.lineno(1))

    def p_else_clause(self, p):
        '''else_clause : ELSE 
                | ELSE action_statement_list
                | ELSIF boolean_expression then_clause 
                | ELSIF boolean_expression then_clause else_clause'''
        if len(p) == 2:
            p[0] = Else_clause(None, None, None, None, lineno=p.lineno(1))
        elif len(p) == 3:
            p[0] = Else_clause(p[2], None, None, None, lineno=p.lineno(1))
        elif len(p) == 4:
            p[0] = Else_clause(None, p[2], p[3], None, lineno=p.lineno(1))
        else:
            p[0] = Else_clause(None, p[2], p[3], p[4], lineno=p.lineno(1))

    def p_do_action(self, p):
        '''do_action : DO OD 
                | DO action_statement_list OD 
                | DO control_part SEMI OD
                | DO control_part SEMI action_statement_list OD'''
        if len(p) == 3:
            p[0] = Do_action(None, None, lineno=p.lineno(1))
        elif len(p) == 4:
            p[0] = Do_action(p[2], None, lineno=p.lineno(1))
        elif len(p) == 5:
            p[0] = Do_action(None, p[2], lineno=p.lineno(1))
        else:
            p[0] = Do_action(p[4], p[2], lineno=p.lineno(1))

    def p_control_part(self, p):
        '''control_part : for_control 
                | for_control while_control 
                | while_control'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1], p[2]]

    def p_for_control(self, p):
        '''for_control : FOR iteration'''
        p[0] = For_control(p[2], lineno=p.lineno(1))

    def p_iteration(self, p):
        '''iteration : step_enumeration 
                | range_enumeration'''
        p[0] = p[1]

    def p_step_enumeration(self, p):
        '''step_enumeration : identifier ASSIGN expression end_value
                            | identifier ASSIGN expression step_value end_value
                            | identifier ASSIGN expression DOWN end_value
                            | identifier ASSIGN expression step_value DOWN end_value'''

        if len(p) == 6 and p[4] == 'down':
            p[0] = Step_enumeration(p[1], p[3], None, p[5], True, lineno=p.lineno(1))
        elif len(p) == 5:
            p[0] = Step_enumeration(p[1], p[3], None, p[4], False, lineno=p.lineno(1))
        elif len(p) == 6:
            p[0] = Step_enumeration(p[1], p[3], p[4], p[5], False, lineno=p.lineno(1))
        else:
            p[0] = Step_enumeration(p[1], p[3], p[4], p[6], True, lineno=p.lineno(1))

    def p_step_value(self, p):
        '''step_value : BY expression'''
        p[0] = p[2]

    def p_end_value(self, p):
        '''end_value : TO expression'''
        p[0] = p[2]

    def p_range_enumeration(self, p):
        '''range_enumeration : identifier IN discrete_range_mode 
                | identifier DOWN IN discrete_range_mode'''
        if len(p) == 4:
            p[0] = Range_enumeration(p[1], p[3], False, lineno=p.lineno(1))
        else:
            p[0] = Range_enumeration(p[1], p[4], True, lineno=p.lineno(1))

    def p_while_control(self, p):
        '''while_control : WHILE boolean_expression'''
        p[0] = While_control(p[2], lineno=p.lineno(1))

    def p_procedure_call(self, p):
        '''procedure_call : identifier LPAREN RPAREN 
                | identifier LPAREN parameter_list RPAREN'''
        if len(p) == 4:
            p[0] = Procedure_call(p[1], None, lineno=p.lineno(1))
        else:
            p[0] = Procedure_call(p[1], p[3], lineno=p.lineno(1))

    def p_parameter_list(self, p):
        '''parameter_list : expression 
                | expression COMMA parameter_list'''
        if len(p) == 2:
            p[0] = Parameter_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Parameter_list(self.flat([p[1], p[3].expressions]), lineno=p.lineno(1))

    def p_exit_action(self, p):
        '''exit_action : EXIT identifier'''
        p[0] = Exit_action(p[2], lineno=p.lineno(1))

    def p_return_action(self, p):
        '''return_action : RETURN 
                | RETURN expression'''
        if len(p) == 2:
            p[0] = Return_action(None, lineno=p.lineno(1))
        else:
            p[0] = Return_action(p[2], lineno=p.lineno(1))

    def p_result_action(self, p):
        '''result_action : RESULT expression'''
        p[0] = Result_action(p[2], lineno=p.lineno(1))

    def p_builtin_call(self, p):
        '''builtin_call : builtin_name LPAREN RPAREN 
                | builtin_name LPAREN parameter_list RPAREN'''
        if len(p) == 4:
            p[0] = Builtin_call(p[1], None, lineno=p.lineno(1))
        else:
            p[0] = Builtin_call(p[1], p[3], lineno=p.lineno(1))

    def p_builtin_name(self, p):
        '''builtin_name : NUM 
                | PRED 
                | SUCC 
                | UPPER 
                | LOWER 
                | LENGTH 
                | READ 
                | PRINT'''
        p[0] = p[1]

    def p_procedure_statement(self, p):
        '''procedure_statement : identifier COLON procedure_definition SEMI'''
        p[0] = Procedure_statement(p[1], p[3], lineno=p.lineno(1))

    def p_procedure_definition(self, p):
        '''procedure_definition : PROC LPAREN RPAREN SEMI END
                | PROC LPAREN formal_parameter_list RPAREN SEMI END
                | PROC LPAREN RPAREN result_spec SEMI END
                | PROC LPAREN RPAREN SEMI statement_list END
                | PROC LPAREN formal_parameter_list RPAREN result_spec SEMI END
                | PROC LPAREN formal_parameter_list RPAREN SEMI statement_list END
                | PROC LPAREN RPAREN result_spec SEMI statement_list END
                | PROC LPAREN formal_parameter_list RPAREN result_spec SEMI statement_list END'''
        if len(p) == 6:
            p[0] = Procedure_definition(None, None, None, lineno=p.lineno(1)) 
        elif len(p) == 7 and p[3] != ')':
            p[0] = Procedure_definition(p[3], None, None, lineno=p.lineno(1))
        elif len(p) == 7 and p[4] != ';':
            p[0] = Procedure_definition(None, p[4], None, lineno=p.lineno(1))     
        elif len(p) == 7:
            p[0] = Procedure_definition(None, None, p[5], lineno=p.lineno(1))     
        elif len(p) == 8 and p[3] != ')' and p[5] != ';':
            p[0] = Procedure_definition(p[3], p[5], None,lineno=p.lineno(1))
        elif len(p) == 8 and p[3] != ')':
            p[0] = Procedure_definition(p[3], None, p[6], lineno=p.lineno(1))
        elif len(p) == 8:
            p[0] = Procedure_definition(None, p[4], p[6], lineno=p.lineno(1))     
        else:
            p[0] = Procedure_definition(p[3], p[5],p[7], lineno=p.lineno(1))

    def p_action_statement_list(self, p):
        '''action_statement_list : action_statement 
                | action_statement action_statement_list'''
        if len(p) == 2:
            p[0] = Action_statement_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Action_statement_list(self.flat([p[1], p[2].action_statements]), lineno=p.lineno(1))

    def p_formal_parameter_list(self, p):
        '''formal_parameter_list : formal_parameter 
                | formal_parameter COMMA formal_parameter_list'''
        if len(p) == 2:
            p[0] = Formal_parameter_list([p[1]], lineno=p.lineno(1))
        else:
            p[0] = Formal_parameter_list(self.flat([p[1], p[3].formal_parameters]), lineno=p.lineno(1))

    def p_formal_parameter(self, p):
        '''formal_parameter : identifier_list parameter_spec'''
        p[0] = Formal_parameter(p[1], p[2], lineno=p.lineno(1))

    def p_parameter_spec(self, p):
        '''parameter_spec : mode 
                | mode LOC'''
        if len(p) == 2:
            p[0] = Parameter_spec(p[1], False, lineno=p.lineno(1))
        else:
            p[0] = Parameter_spec(p[1], True, lineno=p.lineno(1))

    def p_result_spec(self, p):
        '''result_spec : RETURNS LPAREN mode RPAREN 
                       | RETURN LPAREN mode LOC RPAREN'''
        
        if len(p) == 5:
            p[0] = Result_spec(p[3], False, lineno=p.lineno(1))
        else:
            p[0] = Result_spec(p[3], True, lineno=p.lineno(1))

    def p_error(self, p):
        print "Syntax error in input!", p

    def parseInput(self, s):
        return self.parser.parse(s, tracking=True, debug=False)

    def flat(self, l):
        if type(l) != list:
            return l
        else:
            acc = []
            for i in l:
                r = self.flat(i)
                if type(r) == list:
                    for x in r:
                        acc.append(x)
                else:
                    acc.append(r)
        return acc
