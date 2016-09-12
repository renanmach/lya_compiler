#!/usr/bin/python
# -*- coding: utf-8 -*-

from lya_environment import *
from lya_errors import *
from lya_codeprinter import CodePrinter
from lya_codegen import CodeGen

environment = Environment()

# prints the code of a tree object
cp = CodePrinter()
cg = CodeGen()
#li = LabelInformation()


def reset():
    global environment
    environment = Environment()
    global cg
    cg = CodeGen()


class AST(object):
    _fields = ["program"]
    lineno = None

    def set_output(self, output_file):
        global cp
        cp = CodePrinter(output_file)

    def __init__(self, *args, **kwargs):
        assert len(args) == len(self._fields)
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        # Assign additional keyword arguments if supplied
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.type = self.__class__.__name__.lower()

        self.location = "(at line: " + str(self.lineno) + ")"

    # Returns the name of the class to printing
    def get_type_formated(self):
        return "".join([i.capitalize() for i in self.type.split('_')])

    def print_spacing(self, spacing, *args):
        type_formated =  self.get_type_formated()

        type_formated = type_formated.replace("Statement", "Stat")
        type_formated = type_formated.replace("Definition", "Def")
        type_formated = type_formated.replace("Parameter", "Param")
        type_formated = type_formated.replace("Procedure", "Proc")
        type_formated = type_formated.replace("Expression", "Expr")
        type_formated = type_formated.replace("Declaration", "Decl")
        
        if args is not None and len(args) > 0:
            print spacing * " " + type_formated + ":", " ".join(args)
        else:
            print spacing * " " + type_formated + ":"

    def print_node(self, spacing):
        raise InvalidASTNode("printNode not defined", "on class " + self)

    def visit_node(self):
        raise InvalidASTNode("visitNode not defined", "on class " + self)

    def check_assignment_type(self, mode, expression, identifier, elementMode=None):
        if expression.valueType == "empty_literal" or expression.valueType == "builtin_call":
            expression.valueType = None

        if mode == "int" and (expression.valueType is None or expression.valueType == "int"):
            environment.add_local(identifier.id, IntType(identifier.id, expression))
            return True
        elif mode == "char" and (expression.valueType is None or expression.valueType == "char"):
            environment.add_local(identifier.id, CharType(identifier.id, expression))
            return True
        elif mode == "bool" and (expression.valueType is None or expression.valueType == "bool"):
            environment.add_local(identifier.id, BoolType(identifier.id, expression))
            return True
        elif mode == "string" and (expression.valueType is None or expression.valueType == "string"):
            environment.add_local(identifier.id, StringType(identifier.id, expression))
            return True
        elif hasattr(mode, "type") and mode.type == "array":
            environment.add_local(identifier.id, ArrayType(identifier.id, mode.elementMode, expression)) 
            return True
        elif mode == "array":
            environment.add_local(identifier.id, ArrayType(identifier.id, elementMode, expression)) 
            return True  

        # Not added, the caller should raise an error   
        return False
    
    def get_array_type(self, arrayType):
        x = None
        
        if arrayType.valuesType == "int":
            x = IntType()
        elif arrayType.valuesType == "bool":
            x = BoolType()
        elif arrayType.valuesType == "string":
            x = StringType()
        elif arrayType.valuesType == "char":
            x = CharType()
            
        return x

    def generate_code1(self):
        raise InvalidASTNode("generateCode1 not defined", "on class " + str(self))

    def print_code(self):
        raise InvalidASTNode("printCode not defined", "on class " + str(self))

    def print_operator(self, operator):
        if operator == '+':
            cp.add()
        elif operator == '-':
            cp.subtract()
        elif operator == '*':
            cp.multiply()
        elif operator == '/':
            cp.subtract()
        elif operator == '%':
            cp.modulus()
        elif operator == '&&':
            cp.logicalAnd()
        elif operator == '||':
            cp.logicalOr()
        elif operator == '==':
            cp.equal()
        elif operator == '!=':
            cp.notEqual()
        elif operator == '>':
            cp.greater()
        elif operator == '>=':
            cp.greaterOrEqual()
        elif operator == '<':
            cp.less()
        elif operator == '<=':
            cp.lessOrEqual()


class Program(AST):
    _fields = ["statement_list"]

    def __init__(self, *args, **kwargs):
        self.statement_list = None

        super(Program, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.statement_list.print_node(spacing + 2)

    def visit_node(self):
        self.statement_list.visit_node()

    def generate_code1(self):
        self.statement_list.generate_code1()
        self.print_code()

    def print_code(self):
        strs = cg.get_all_str()
        other_ref_strs = [0]*len(strs)
        for i, j in strs.items():
            other_ref_strs[j] = i
        if len(other_ref_strs) > 0:
            cp.printStrs(other_ref_strs)
        cp.startProgram()
        _min = 99999999
        _max = 0
        for j in cg.curr_node.st:
            i = cg.curr_node.st[j]
            if i.type != "declaration":
                continue
            if i.idStart < _min:
                _min = i.idStart
            if i.idEnd > _max:
                _max = i.idEnd
        if _min <= _max:
            cp.alocateMemory(_max-_min)
        self.statement_list.print_code()
        if _min <= _max:
            cp.deallocateMemory(_max-_min)
        cp.endProgram()


class Statement_list(AST):
    _fields = ["statements"]

    def __init__(self, *args, **kwargs):
        self.statements = None

        super(Statement_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        for statements in self.statements:
            statements.print_node(spacing + 2)

    def visit_node(self):
        for statements in self.statements:
            statements.visit_node()

    def generate_code1(self):
        for statements in self.statements:
            statements.generate_code1()

    def print_code(self):
        for statements in self.statements:
            statements.print_code()


class Declaration_statement(AST):
    _fields = ["declaration_list"]

    def __init__(self, *args, **kwargs):
        self.declaration_list = None

        super(Declaration_statement, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.declaration_list.print_node(spacing + 2)

    def visit_node(self):
        self.declaration_list.visit_node()

    def generate_code1(self):
        self.declaration_list.generate_code1()

    def print_code(self):
        self.declaration_list.print_code()


class Declaration_list(AST):
    _fields = ["declarations"]

    def __init__(self, *args, **kwargs):
        self.declarations = None

        super(Declaration_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        for declaration in self.declarations:
            declaration.print_node(spacing + 2)

    def visit_node(self):
        for declaration in self.declarations:
            declaration.visit_node()

    def generate_code1(self):
        for declaration in self.declarations:
            declaration.generate_code1()

    def print_code(self):
        for declaration in self.declarations:
            declaration.print_code()


class Declaration(AST):
    _fields = ["identifier_list", "mode", "initialization"]

    def __init__(self, *args, **kwargs):
        self.identifier_list = None
        self.mode = None
        self.initialization = None
        super(Declaration, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.identifier_list.print_node(spacing)
        self.mode.print_node(spacing)
        if self.initialization is not None:
            self.initialization.print_node(spacing)

    def visit_node(self):
        identifierList = self.identifier_list.visit_node(declaring=True)
        mode = self.mode.visit_node()

        # Initialization is an expression
        initialization = None

        if self.initialization is not None:
            initialization = self.initialization.visit_node()

        # if there is no initialization   
        if initialization is None:
            initialization = Expression(None)
            initialization.value = None
            initialization.valueType = None

        isDiscreteRangeMode = False
        if hasattr(mode, "type") and mode.type == "discrete_range_mode":
            isDiscreteRangeMode = True

        if isDiscreteRangeMode is False:
            for identifier in identifierList:
                if self.check_assignment_type(mode, initialization, identifier) is False:
                    raise InitializationError(str(initialization.value) + " is not a {0}, it is a {2}. Line={1}".format(mode, self.lineno, initialization.valueType), "Be sure to check variables types.")

    def generate_code1(self):
        identifierList = self.identifier_list.generate_code1()
        mode = self.mode.generate_code1()

        # Initialization is an expression
        initialization = None

        if self.initialization is not None:
            initialization = self.initialization.generate_code1()

        cg.declaration(identifierList, mode)

    def print_code(self):
        identifierList = self.identifier_list.print_code()
        mode = self.mode.print_code()

        initialization = None

        if self.initialization is not None:
            for i in identifierList:
                initialization = self.initialization.print_code()

                ret = cg.curr_node.lookup(i)
                cp.storeValue(ret.scope, ret.idStart)


class Identifier_list(AST):
    _fields = ["identifiers"]

    def __init__(self, *args, **kwargs):
        self.identifiers = None

        super(Identifier_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        for identifier in self.identifiers:
            identifier.print_node(spacing)

    def visit_node(self, declaring=None):
        identifierList = list()
        for identifier in self.identifiers:
            identifierList.append(identifier.visit_node(declaring))
            
        return identifierList

    def generate_code1(self):
        self.identifierList = list()
        for identifier in self.identifiers:
            self.identifierList.append(identifier.generate_code1().id)
        return self.identifierList

    def print_code(self,type="load"):
        return self.identifierList


class Identifier(AST):
    _fields = ["id"]

    def __init__(self, *args, **kwargs):
        self.id = None

        super(Identifier, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        print spacing * " " +  "ID: " + self.id + " " + self.location

    def visit_node(self, declaring=None):
        if declaring is None and environment.lookup(self.id) is None:
            raise DefinitionError("'{0}' is not defined. Line = {1}.".format(self.id, self.lineno), "Be sure to declare variable before usage.")
        elif declaring is True and environment.find(self.id) is True:
            raise DefinitionError("'{0}' is already declared in this scope. Line = {1}.".format(self.id, self.lineno), "Do not declare the same variable twice in the same scope.")
        return self

    def generate_code1(self):
        return self


    def print_code(self, type="load"):
        ret = cg.curr_node.lookup(self.id)

        if ret.type == "synonym":
            cp.loadConstant(ret.value)

        try:
            if ret.indexList is not None:
                cp.loadReference(ret.scope, ret.idStart)
                if type == "store":
                    cp.loadMultipleValues(ret.idSize)
                    cp.storeMultipleValues(ret.idSize)
                elif type == "slice":
                    ret.indexList[0].print_code()
                return
        except:
            pass

        else:
            if type == "store":
                if ret.isLocation:
                    cp.storeReferenceValue(ret.scope, ret.idStart)
                else:
                    cp.storeValue(ret.scope, ret.idStart)
            elif type == "load":
                if ret is not None and ret.mode is not None and hasattr(ret.mode, "type") and ret.mode.type == "array":
                    cp.loadReference(ret.scope,ret.idStart)
                elif ret.isLocation:
                    cp.loadReferenceValue(ret.scope, ret.idStart)
                else:
                    cp.loadValue(ret.scope, ret.idStart)
            elif type == "load_reference_value":
                cp.loadReferenceValue(ret.scope, ret.idStart)
            elif type == "load_reference":
                cp.loadReference(ret.scope, ret.idStart)
            elif type == "referenced_location":
                cp.loadReference(ret.scope, ret.idStart)
            elif type == "store_reference_value":
                cp.storeReferenceValue(ret.scope, ret.idStart)


class Synonym_list(AST):
    _fields = ["synonym_definitions"]

    def __init__(self, *args, **kwargs):
        self.synonym_definitions = None

        super(Synonym_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        for synonym in self.synonym_definitions:
            synonym.print_node(spacing)

    def visit_node(self):
        for synonym in self.synonym_definitions:
            synonym.visit_node()

    def generate_code1(self):
        for synonym in self.synonym_definitions:
            synonym.generate_code1()

    def print_code(self):
        pass


class Synonym_definition(AST):
    _fields = ["identifier_list", "mode", "constant_expression"]

    def __init__(self, *args, **kwargs):
        self.identifier_list = None
        self.mode = None
        self.constant_expression = None
        super(Synonym_definition, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.identifier_list.print_node(spacing + 2)
        if self.mode is not None:
            self.mode.print_node(spacing + 2)
        self.constant_expression.print_node(spacing + 2)

    def visit_node(self):
        identifierList = self.identifier_list.visit_node(declaring=True)

        mode = None
        if self.mode:
            mode = self.mode.visit_node()

        initialization = None
        if self.constant_expression is not None:
            initialization = self.constant_expression.visit_node()

        if initialization is None:
            raise UnexpectedError(initialization, "SYN initialization must have a value.")

        if mode is None:
            mode = initialization.valueType

        for identifier in identifierList:
            if mode == "int" and (initialization.valueType is None or initialization.valueType == "int"):
                environment.add_local(identifier.id, IntType(identifier, initialization, synonym=True))
            elif mode == "char" and (initialization.valueType is None or initialization.valueType == "char"):
                environment.add_local(identifier.id, CharType(identifier, initialization, synonym=True))
            elif mode == "bool" and (initialization.valueType is None or initialization.valueType == "bool"):
                environment.add_local(identifier.id, BoolType(identifier, initialization, synonym=True))
            elif mode == "string" and (initialization.valueType is None or initialization.valueType == "string"):
                environment.add_local(identifier.id, StringType(identifier, initialization, synonym=True))
            else:
                raise InitializationError(initialization.value + "is not a {0}. Line={1}".format(mode, self.lineno), "")

    def generate_code1(self):
        identifierList = self.identifier_list.generate_code1()
        initialization = self.constant_expression.generate_code1()

        mode = None
        if self.mode:
            mode = self.mode.generate_code1()

        # mode must be the same of the initialization
        if mode is None:
            mode = initialization.valueType

        cg.synonymDefinition(identifierList, mode, initialization)

    def print_code(self):
        pass


class Newmode_statement(AST):
    _fields = ["newmode_list"]

    def __init__(self, *args, **kwargs):
        self.newmode_list = None

        super(Newmode_statement, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.newmode_list.print_node(spacing + 2)

    def visit_node(self):
        self.newmode_list.visit_node()

    def generate_code1(self):
        self.newmode_list.generate_code1()

    def print_code(self):
        pass


class Newmode_list(AST):
    _fields = ["mode_definitions"]

    def __init__(self, *args, **kwargs):
        self.mode_definitions = None

        super(Newmode_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        for modeDefinition in self.mode_definitions:
            modeDefinition.print_node(spacing)

    def visit_node(self):
        for modeDefinition in self.mode_definitions:
            modeDefinition.visit_node()

    def generate_code1(self):
        for modeDefinition in self.mode_definitions:
            modeDefinition.generate_code1()

    def print_code(self):
        pass


class Mode_definition(AST):
    _fields = ["identifier_list", "mode"]

    def __init__(self, *args, **kwargs):
        self.identifier_list = None
        self.mode = None
        super(Mode_definition, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.identifier_list.print_node(spacing + 2)
        self.mode.print_node(spacing + 2)

    def visit_node(self):
        identifierList = self.identifier_list.visit_node(declaring=True)
        mode = self.mode.visit_node()
        
        for identifier in identifierList:
            if mode == "int":
                environment.add_local(identifier.id, IntType(identifier, None))
            elif mode == "char":
                environment.add_local(identifier.id, CharType(identifier, None))
            elif mode == "bool" :
                environment.add_local(identifier.id, BoolType(identifier, None))
            elif mode == "string":
                environment.add_local(identifier.id, StringType(identifier, None))
            elif hasattr(mode, "type") and mode.type == "array":
                environment.add_local(identifier.id, ArrayType(identifier, mode.elementMode, None)) 
            else:
                raise NewModeStatementError("Mode {0} unknown. Line={1}".format(mode, self.lineno), "")

    def generate_code1(self):
        identifierList = self.identifier_list.generate_code1()
        mode = self.mode.generate_code1()
        cg.modeDefinition(identifierList, mode)

    def print_code(self):
        pass


class Mode(AST):
    _fields = ["mode_type"]

    def __init__(self, *args, **kwargs):
        self.mode_type = None

        super(Mode, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.mode_type.print_node(spacing + 2)

    def visit_node(self):
        mode = self.mode_type.visit_node()
        self.modeId = None
        self.modeIdType = None
        
        # if a mode is already defined
        if hasattr(mode, "type") and mode.type == "identifier":
            self.modeId = mode.id
            self.modeIdType = environment.lookup(mode.id)
            self.type = self.modeIdType.type
            
            if self.modeIdType.type == "array":
                self.elementMode = self.modeIdType.valuesType
            return self
            
        return mode

    def generate_code1(self):
        modeType = self.mode_type.generate_code1()
        self.isReference = False
        self.type2 = modeType.type
        self.modeNameModeId = None
        self.stringLength = None
        self.arrayIndexModeList = None
        self.arrayElementMode = None
        self.discreteModeType = None
        self.referenceModeMode = None

        if modeType.type == "reference_mode":
            self.isReference = True
            self.referenceModeMode = modeType.mode
        elif modeType.type == "string":
            self.stringLength = modeType.stringLength
        elif modeType.type == "array":
            self.arrayElementMode = modeType.elementMode
            self.arrayIndexModeList = modeType.indexModeList
        elif modeType.type == "mode_name":
            self.modeNameModeId = modeType.modeId
        elif modeType.type == "discrete_mode":
            self.discreteModeType =  modeType.mode
        else:
            print "Unknown error in class Mode. Type: ", modeType.type

        return self


    def print_code(self):
        pass


class Discrete_mode(AST):
    _fields = ["discrete_mode_type"]

    def __init__(self, *args, **kwargs):
        self.discrete_mode_type = None

        super(Discrete_mode, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.discrete_mode_type, self.location)

    def visit_node(self, declaring=None):
        return self.discrete_mode_type

    def generate_code1(self):
        self.mode = None
        self.discreteRangeModeName = None
        self.discreteRangeModeLiteralRange = None

        try:
            # if it is discrete_range_mode
            discreteModeType = self.discrete_mode_type.generate_code1()
            self.mode = discreteModeType.type
            self.discreteRangeModeName = discreteModeType.discreteModeName
            self.discreteRangeModeLiteralRange = discreteModeType.literalRange
        except:
            # if type is int,bool ou char
            self.mode = self.discrete_mode_type

        return self

    def print_code(self):
        if hasattr(self.discrete_mode_type, "type"):
            self.discrete_mode_type.print_code()


class Discrete_range_mode(AST):
    _fields = ["discrete_mode_name","literal_range"]

    def __init__(self, *args, **kwargs):
        self.discrete_mode_name = None
        self.literal_range = None
        super(Discrete_range_mode, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.discrete_mode_name.print_node(spacing + 2)
        self.literal_range.print_node(spacing + 2)

    def visit_node(self):
        self.id = self.discrete_mode_name.visit_node(declaring=True)
        self.literalRange = self.literal_range.visit_node()
        return self

    def generate_code1(self):
        self.discreteModeName = self.discrete_mode_name.generate_code1()
        self.literalRange = self.literal_range.generate_code1()
        return self

    def print_code(self):
        self.literal_range.print_code()
        self.discrete_mode_name.print_code()

    def print_code1(self):
        self.literal_range.print_code()

    def print_code2(self):
        self.literal_range.print_code2()


class Mode_name(AST):
    _fields = ["identifier"]

    def __init__(self, *args, **kwargs):
        self.identifier = None

        super(Mode_name, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        return self.identifier.print_node(spacing)

    def visit_node(self):
        return self.identifier.visit_node()

    def generate_code1(self):
        self.modeId = self.identifier.generate_code1().id
        return self

    def print_code(self):
        pass


class Literal_range(AST):
    _fields = ["expression1","expression2"]

    def __init__(self, *args, **kwargs):
        self.expression1 = None
        self.expression2 = None
        super(Literal_range, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.expression1.print_node(spacing)
        self.expression2.print_node(spacing)

    def visit_node(self):
        self.expr1 = self.expression1.visit_node()
        self.expr2 = self.expression2.visit_node()
        return self

    def generate_code1(self):
        self.expr1 = self.expression1.generate_code1()
        self.expr2 = self.expression2.generate_code1()
        return self

    def print_code(self):
       self.expr1.print_code(type="load")

    def print_code2(self):
        self.expr2.print_code(type="load")


class Reference_mode(AST):
    _fields = ["mode2"]

    def __init__(self, *args, **kwargs):
        self.mode2 = None
        super(Reference_mode, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.mode2.print_node(spacing + 2)

    def visit_node(self):
        return self.mode2.visit_node()

    def generate_code1(self):
        self.mode = self.mode2.generate_code1()
        return self

    def print_code(self):
        pass


class String_mode(AST):
    _fields = ["string_length"]

    def __init__(self, *args, **kwargs):
        self.string_length = None

        super(String_mode, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.string_length.print_node(spacing + 2)

    def visit_node(self):
        return "string"

    def generate_code1(self):
        self.stringLength = self.string_length.generate_code1()
        self.type = "string"
        return self

    def print_code(self):
        pass


class String_length(AST):
    _fields = ["length"]

    def __init__(self, *args, **kwargs):
        self.length = None

        super(String_length, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, str(self.length.value))

    def visitNode(self):
        pass

    def generate_code1(self):
        return self.length.value

    def print_code(self):
        pass


class Array_mode(AST):
    _fields = ["index_list", "element_mode"]

    def __init__(self, *args, **kwargs):
        self.index_list = None
        self.element_mode = None
        super(Array_mode, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.index_list.print_node(spacing + 2)
        self.element_mode.print_node(spacing + 2)

    def visit_node(self):
        self.indexList = self.index_list.visit_node()
        self.elementMode = self.element_mode.visit_node()
        self.type = "array"
        return self

    def generate_code1(self):
        self.indexModeList = self.index_list.generate_code1()
        self.elementMode = self.element_mode.generate_code1()
        self.type = "array"
        return self

    def print_code(self):
        pass 


class Index_list(AST):
    _fields = ["index_modes"]

    def __init__(self, *args, **kwargs):
        self.index_modes = None

        super(Index_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        for index in self.index_modes:
            index.print_node(spacing)

    def visit_node(self):
        self.indexModeList = []
        for index in self.index_modes:
            self.indexModeList.append(index.visit_node())
        return self

    def generate_code1(self):
        self.indexModeList = []
        for index in self.index_modes:
            self.indexModeList.append(index.generate_code1())
        return self.indexModeList

    def print_code(self):
        pass


'''location : identifier
    | dereferenced_reference
    | string_element
    | slice
    | procedure_call
    | builtin_call'''
class Location(AST):
    _fields = ["location_type"]

    def __init__(self, *args, **kwargs):
        self.location_type = None

        super(Location, self).__init__(*args, **kwargs)
    
    def print_node(self, spacing):
        self.location_type.print_node(spacing)
         
    def visit_node(self):
        loc = self.location_type.visit_node()
        return loc

    def generate_code1(self):
        loc = self.location_type.generate_code1()

        self.id = None
        self.locationType = loc.type
        self.stringArrayElementLoc = None
        self.stringArrayElementExpression = None
        self.sliceLeft = None
        self.sliceRight = None
        self.sliceLoc = None
        self.builtinName = None
        self.builtinParameterList = None
        self.procedureId = None
        self.procedureParameterList = None
        self.derefRefLocation = None

        if loc.type == "identifier":
            self.id = loc.id
        elif loc.type == "stringarray_element":
            self.stringArrayElementLoc = loc.loc2
            self.stringArrayElementExpressionList = loc.expressionList
            self.id = loc.id
        elif loc.type == "slice":
            self.id = loc.id
            self.sliceLeft = loc.left
            self.sliceRight = loc.right
            self.sliceLoc = loc.loc2
        elif loc.type == "procedure_call":
            self.procedureParameterList = loc.parameterList
            self.procedureId = loc.id
        elif loc.type == "builtin_call":
            self.builtinName = loc.builtinName
            self.builtinParameterList = loc.parameterList
        elif loc.type == "dereferenced_reference":
            self.derefRefLocation = loc.loc
        else:
            print "Unknown error in class Location. Type: ", loc.type

        return self

    def print_code(self, type="load"):
        if self.location_type.type == "stringarray_element":
            self.print_stringarray()
            if type == "load":
                cp.getReferenceContents()
        else:
            return self.location_type.print_code(type=type)

    def print_stringarray(self):
        self.location_type.print_stringarray()


class Dereferenced_reference(AST):
    _fields = ["loc"]

    def __init__(self, *args, **kwargs):
        self.loc = None

        super(Dereferenced_reference, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.loc.print_node(spacing + 2)

    def visit_node(self):
        return self.loc.visit_node()

    def generate_code1(self):
        return self

    def print_code(self, type="load"):
        self.loc.print_code(type="load_reference_value")

# string_element
# array_element
class StringArray_element(AST):
    _fields = ["loc", "expression_list"]

    def __init__(self, *args, **kwargs):
        self.loc = None
        self.expression_list = None
        super(StringArray_element, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.loc.print_node(spacing + 2)
        self.expression_list.print_node(spacing + 2)

    def visit_node(self):
        loc = self.loc.visit_node()
        self.expressionList = self.expression_list.visit_node()

        self.id = "_INVALID_STRINGARRAY_ELEMENT_"
        if(hasattr(loc, "id")):
            self.id = loc.id
        return self

    def generate_code1(self):
        self.loc2 = self.loc.generate_code1()
        self.expressionList = self.expression_list.generate_code1()
        self.id = self.loc2.id

        return self

    def print_code(self, type="load_reference"):
        self.expression_list.print_code(type)
        self.loc.print_code(type)
        return self

    def print_stringarray(self):
        ret = None
        if self.loc.location_type.type == "identifier":
            ret = cg.curr_node.lookup(self.loc.location_type.id)
            cp.loadReference(ret.scope, ret.idStart)

        self.expression_list.print_code()

        if ret is not None:
            if ret.indexList is not None:
                for index_mode in ret.indexList:
                    index_mode.print_code()

        cp.subtract()
        cp.index(1)


class Slice(AST):
    _fields = ["loc", "expression1", "expression2"]

    def __init__(self, *args, **kwargs):
        self.loc = None
        self.expression1 = None
        self.expression2 = None
        super(Slice, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.loc.print_node(spacing + 2)
        self.expression1.print_node(spacing + 2)
        self.expression2.print_node(spacing + 2)

    def visit_node(self):
        self.loc2 = self.loc.visit_node()
        self.left = self.expression1.visit_node()
        self.right = self.expression2.visit_node()
        self.id = self.loc2.id
        return self

    def generate_code1(self):
        self.loc2 = self.loc.generate_code1()
        self.left = self.expression1.generate_code1()
        self.right = self.expression2.generate_code1()
        self.id = self.loc2.id
        return self

    def print_code(self, type="load"):
        self.loc.print_code(type="slice")
        self.expression1.print_code()
        cp.subtract()
        cp.index(1)

        if type == "store":
            cp.loadMultipleValues(1)
            cp.storeMultipleValues(1)



class Expression_list(AST):
    _fields = ["expressions"]

    def __init__(self, *args, **kwargs):
        self.expressions = None

        super(Expression_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        for expression in self.expressions:
            expression.print_node(spacing)

    def visit_node(self):
        expressionList = []
        for expression in self.expressions:
            expressionList.append(expression.visit_node())
        return expressionList

    def generate_code1(self):
        self.expressionList = []
        for expression in self.expressions:
            self.expressionList.append(expression.generate_code1())
        return self.expressionList

    def print_code(self, type="load"):
        self.expressionList = []
        for expression in self.expressions:
            self.expressionList.append(expression.print_code(type=type))
        return self.expressionList


class Int(AST):
    _fields = ["value"]

    def __init__(self, *args, **kwargs):
        self.value = None

        super(Int, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, str(self.value), self.location)

    def visit_node(self):
        return self

    def generate_code1(self):
        return self

    def print_code(self, type=None):
        cp.loadConstant(self.value)


class Bool(AST):
    _fields = ["value"]

    def __init__(self, *args, **kwargs):
        self.value = None

        super(Bool, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, str(self.value), self.location)

    def visit_node(self):
        return self

    def generate_code1(self):
        return self

    def print_code(self, type=None):
        cp.loadConstant(self.value)


class Char(AST):
    _fields = ["value", "type"]

    def __init__(self, *args, **kwargs):
        self.value = None
        self.type = None
        super(Char, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, "'" + str(self.value) + "'", self.location)

    def visit_node(self):
        return self

    def generate_code1(self):
        return self

    def print_code(self, type=None):
        cp.loadConstant(self.value)


class Empty_literal(AST):
    _fields = ["value"]

    def __init__(self, *args, **kwargs):
        self.value = None

        super(Empty_literal, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, str(self.value), self.location)

    def visit_node(self):
        return self

    def generate_code1(self):
        return self

    def print_code(self, type=None):
        cp.loadConstant(self.value)


class String(AST):
    _fields = ["value"]

    def __init__(self, *args, **kwargs):
        self.value = None

        super(String, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, '"' + self.value + '"', self.location)

    def visit_node(self):
        return self

    def generate_code1(self):
        if cg.get_str(self.value) is None:
            cg.add_str(self.value)
        return self

    def print_code(self, type=None):
        #raise Exception("aqui")
        return str, cg.get_str(self.value)
        #cp.loadConstant(self.value)


class Expression(AST):
    _fields = ["expr"]

    def __init__(self, *args, **kwargs):
        self.expr = None

        super(Expression, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.expr.print_node(spacing + 2)

    def visit_node(self):
        child = self.expr.visit_node()
        self.valueType = "_INVALID_"
        self.value = "_INVALID_"

        # se tivermos um assigment do tipo
        # m += 2 por exemplo, expression2 vai receber o valor
        # antigo de m e operator2 recebe o +
        # isso serve para calcular o valor de m posteriormente
        # sao usadas na classe assignment_action
        self.expression2 = None
        self.operator2 = None
        
        if hasattr(child, "type"):
            if child.type == "int" or child.type == "char" or child.type == "bool" or child.type == "empty_literal" or child.type == "string":
                self.valueType = child.type
                self.value = child.value

            elif child.type == "identifier" or child.type == "procedure_call" or child.type == "slice":
                ret = environment.lookup(child.id)
                self.valueType = ret.type
                self.value = ret._value
                self.arrayId = child.id
                
            elif child.type == "stringarray_element":
                ret = environment.lookup(child.id)
                self.valueType = ret.valuesType
                self.value = ret._value
                self.arrayId = child.id
    
            elif child.type == "builtin_call":
                self.valueType = child.type

            else:
                pass

        else:
            raise UnexpectedError(child,"Expression line={0}".format(self.lineno))

        return self

    # soh eh usada na classe sinonimos
    def generate_code1(self):
        child = self.expr.generate_code1()
        return self

    def print_code(self, type="load"):
        child = self.expr.print_code(type=type)
        return child


class Conditional_expression(AST):
    _fields = ["boolean_expression", "then_expression", "elsif_expression", "else_expression"]

    def __init__(self, *args, **kwargs):
        self.boolean_expression = None
        self.then_expression = None
        self.elsif_expression = None
        self.else_expression = None
        super(Conditional_expression, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.boolean_expression.print_node(spacing + 2)
        self.then_expression.print_node(spacing + 2)
        if self.elsif_expression is not None:
            self.elsif_expression.print_node(spacing + 2)
        self.else_expression.print_node(spacing + 2)

    def visit_node(self):
        self.boolean_expression.visit_node()
        self.then_expression.visit_node()
        if self.elsif_expression is not None:
            self.elsif_expression.visit_node()
        self.else_expression.visit_node()

    def generate_code1(self):
        self.boolean_expression.generate_code1()
        self.then_expression.generate_code1()
        if self.elsif_expression is not None:
            self.elsif_expression.generate_code1()
        self.else_expression.generate_code1()

    def print_code(self, type="load"):
        self.boolean_expression.print_code()
        self.then_expression.print_code()
        if self.elsif_expression is not None:
            self.elsif_expression.print_code()
        self.else_expression.print_code()


class Elsif_expression(AST):
    _fields = ["elsif_expr", "boolean_expression", "then_expression"]

    def __init__(self, *args, **kwargs):
        self.elsif_expr = None
        self.boolean_expression = None
        self.then_expression = None
        super(Elsif_expression, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        if self.elsif_expr is not None:
            self.elsif_expr.print_node(spacing + 2)
        self.boolean_expression.print_node(spacing + 2)
        self.then_expression.print_node(spacing + 2)

    def visit_node(self):
        if self.elsif_expr is not None:
            self.elsif_expr.visit_node()
        self.boolean_expression.visit_node()
        self.then_expression.visit_node()

    def generate_code1(self):
        if self.elsif_expr is not None:
            self.elsif_expr.generate_code1()
        self.boolean_expression.generate_code1()
        self.then_expression.generate_code1()

    def print_code(self):
        if self.elsif_expr is not None:
            self.elsif_expr.print_code()
        self.boolean_expression.print_code()
        self.then_expression.print_code()


class Binary_Operator(AST):
    _fields = ["operator", "left_operand", "right_operand"]

    def __init__(self, *args, **kwargs):
        self.operator = None
        self.left_operand = None
        self.right_operand = None
        super(Binary_Operator, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.operator)
        self.left_operand.print_node(spacing + 2)
        self.right_operand.print_node(spacing + 2)

    def visit_node(self):
        try:
            id0 = self.left_operand.visit_node().id
            use = environment.lookup(id0)
        except AttributeError:
            type0 = self.left_operand.type
            type2 = "_INVALID_"
            
            # se for array, pega o tipo dos elementos
            if hasattr(self.left_operand,"valueType"):
                type2 = self.left_operand.valueType
                
            if type0 == 'int' or type2 == "int":
                use = IntType()
            elif type0 == 'bool' or type2 == "bool":
                use = BoolType()
            elif type0 == 'char' or type2 == "char":
                use = CharType()
            elif type0 == 'string' or type2 == "string":
                use = StringType()
            else:
                raise VariableTypeError("Invalid type: \"" + type0 +"\" at binary operation.",
                                        "Check variable types for left operand. line="+str(self.lineno))
        try:
            id1 = self.right_operand.visit_node().id
            use1 = environment.lookup(id1)
        except AttributeError:
            type1 = self.right_operand.type
            type2 = "_INVALID_"
            
            # se for array, pega o tipo dos elementos
            if hasattr(self.right_operand,"valueType"):
                type2 = self.right_operand.valueType
                
            if type1 == 'int' or type2 == "int":
                use1 = IntType()
            elif type1 == 'bool' or type2 == "bool":
                use1 = BoolType()
            elif type1 == 'char' or type2 == "char":
                use1 = CharType()
            elif type1 == 'string' or type2 == "string":
                use1 = StringType()
            else:
                raise VariableTypeError("Invalid type: \"" + type1 +"\" at binary operation.",
                                        "Check variable types for left operand. line="+str(self.lineno))
        
        # pega o tipo dos elementos do array
        if use.type == "array":
            use = self.get_array_type(use)
               
        if self.operator not in use._accepted_operations_binary:
            raise InvalidOperatorError("Invalid operator " + self.operator + " for operand: " + str(use.type), "Change operator.")
         
        # right operand
        if use1.type == "array":
            use1 = self.get_array_type(use1)
               
        if self.operator not in use1._accepted_operations_binary:
            raise InvalidOperatorError("Invalid operator " + self.operator + " for operands: " + str(use1.type), "Change operator.")
        
        # verifica se sao do mesmo tipo
        if type(use) is not type(use1):
            raise VariableTypeError("Invalid operation at binary operation with types: " + use.type + " and " + use1.type,
                                    "Check variable types for both operand. line=" + str(self.lineno))

        self.type = use.type
        self.value = use._value
        return self

    def generate_code1(self):
        left = self.left_operand.generate_code1()
        right = self.right_operand.generate_code1()

        return self

    def print_code(self, type="load"):
        self.left_operand.print_code(type)
        self.right_operand.print_code(type)
        self.print_operator(self.operator)


class Unary_Operator(AST):
    _fields = ["operator", "operand"]

    def __init__(self, *args, **kwargs):
        self.operator = None
        self.operand = None
        super(Unary_Operator, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.operator)
        self.operand.print_node(spacing + 2)

    def visit_node(self):
        try:
            id0 = self.operand.visit_node().id
            use = environment.lookup(id0)
        except AttributeError:
            use = self.operand.type
            if use == 'int':
                use = IntType()
            elif use == 'bool':
                use = BoolType()
            elif use == 'char':
                use = CharType()
            elif use == 'string':
                use = StringType()
            else:
                raise VariableTypeError("Invalid type at unary operation.",
                                        "Check variable types for operand. line=" + str(self.lineno))
        if self.operator not in use._accepted_operations_unary:
            raise VariableTypeError(
                "Invalid operation at unary operation with type: " + use.type + " and operator " + self.operator,
                "Check variable types for both operand. line=" + str(self.lineno))

        self.type = use.type
        self.value = use._value

        return self

    def generate_code1(self):
        operand = self.operand.generate_code1()

        return self

    def print_code(self, type="load"):
        self.operand.print_code()
        if self.operator == '-':
            cp.negate()
        elif self.operator == '!':
            cp.logicalNot()


class Referenced_location(AST):
    _fields = ["loc"]

    def __init__(self, *args, **kwargs):
        self.loc = None
        super(Referenced_location, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.loc.print_node(spacing)

    def visit_node(self):
        return self.loc.visit_node()

    def generate_code1(self):
        return self.loc.generate_code1()

    def print_code(self, type=None):
        self.loc.print_code(type="referenced_location")

class Action_statement(AST):
    _fields = ["action", "identifier"]

    def __init__(self, *args, **kwargs):
        self.action = None
        self.identifier = None
        super(Action_statement, self).__init__(*args, **kwargs)

    def print_node(self, spacing):

        if self.identifier is not None:
            self.print_spacing(spacing, "ID:", self.identifier.id, self.location)
            self.action.print_node(spacing + 2)
        else:
            self.action.print_node(spacing)

    def visit_node(self):
        # se a action possui um label, adiciona esse label
        # no environment
        self.labelId = None
        if self.identifier is not None:
            self.labelId = self.identifier.visit_node(declaring=True).id
            environment.add_local(self.labelId, LabelType(self.labelId, None))
                
        self.action.visit_node()

    def generate_code1(self):
        labelId = None
        if self.identifier is not None:
            labelId = self.identifier.generate_code1().id
            cg.actionStatement(labelId)

        self.action.generate_code1()

    def print_code(self):
        if self.labelId is not None:
            ret = cg.curr_node.lookup(self.labelId)
            self.action.print_code()
            cp.addLabel(ret.actionStatementLabel)
        else:
            self.action.print_code()


class Assignment_action(AST):
    _fields = ["loc", "assigning_operator", "expression"]

    def __init__(self, *args, **kwargs):
        self.loc = None
        self.assigning_operator = None
        self.expression = None
        super(Assignment_action, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.assigning_operator.print_node(spacing)
        self.loc.print_node(spacing + 2)
        self.expression.print_node(spacing + 2)

    def visit_node(self):
        operator = self.assigning_operator.visit_node()

        location = self.loc.visit_node()
        expression = self.expression.visit_node()

        ret = environment.lookup(location.id)

        if ret is None:
            raise UnexpectedError("unknown error.", ":-(")

        # se usa um closed_dyadic_operator, testa se eh valido
        # se for, coloca ele e o valor antigo da location na expressao
        if operator is not None:
            binOp = Binary_Operator(operator, location, expression)
            binOp.visit_node()

            expression.expression2 = ret._value
            expression.operator2 = operator

        # se for array, pega o tipo dos elementos do array
        arrayValuesType = None
        
        if ret.type == "array":
            arrayValuesType = ret.valuesType
            # se a for assign a um array, ve se eh do mesmo tipo os valores
            if expression.valueType == "array":
                expressionId = environment.lookup(expression.arrayId)
                expression.valueType = expressionId.valuesType

            if arrayValuesType != expression.valueType:
                raise VariableTypeError("The array was not declared as " + expression.valueType + " array it was declared as an {0} array. line={1}".format(arrayValuesType, self.lineno), "Be sure to only set a valid value to type.")

        # verifica se eh uma constante
        ret = environment.lookup(location.id)
        if hasattr(ret, "synonym") and ret.synonym is True:
            raise SynonymAssignmentError("You cannot assign to the synonym {0}. Line={1}".format(location.id, self.lineno),"Synonyms are constant values")

        if self.check_assignment_type(ret.type, expression, location, arrayValuesType) is False:
            raise VariableTypeError(expression.valueType + " is not a {0}. line={1}".format(ret.type, self.lineno), "Be sure to only set a valid value to type.")

    def generate_code1(self):
        self.assigning_operator.generate_code1()
        self.loc.generate_code1()
        self.expression.generate_code1()

    def print_code(self, type="load"):
        # se for array, carrega primeiro o indice
        if self.loc.location_type.type == "stringarray_element":
            self.loc.print_stringarray()

        # testa sea location eh um identifier de um vetor
        # b = a (ambos b e a sao vetores)
        elif self.loc.location_type.type == "identifier":
            ret = cg.curr_node.lookup(self.loc.location_type.id)
            if ret is not None and ret.indexList is not None:
                self.loc.print_code(type=type)
                self.expression.print_code(type="store")
                return

        if self.assigning_operator.closed_dyadic_operator is not None:
            self.loc.print_code(type="load")
        isLocation = self.expression.print_code(type=type)
        self.assigning_operator.print_code()

        type = "store"

        if isLocation:
            type = "store_reference_value"

        # se for array, guarda os multiplos valores
        if self.loc.location_type.type == "stringarray_element":
            cp.storeMultipleValues(1)
        else:
            self.loc.print_code(type=type)


class Assigning_operator(AST):
    _fields = ["closed_dyadic_operator"]

    def __init__(self, *args, **kwargs):
        self.closed_dyadic_operator = None

        super(Assigning_operator, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        print spacing * " " + "AssignOperator:",
        if self.closed_dyadic_operator is not None:
            print self.closed_dyadic_operator + "="
        else:
            print "="

    def visit_node(self):
        return self.closed_dyadic_operator

    def generate_code1(self):
        return self.closed_dyadic_operator

    def print_code(self):
        if self.closed_dyadic_operator is not None:
            self.print_operator(self.closed_dyadic_operator)


class If_action(AST):
    _fields = ["boolean_expression", "then_clause", "else_clause"]

    def __init__(self, *args, **kwargs):
        self.boolean_expression = None
        self.then_clause = None
        self.else_clause = None
        super(If_action, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.boolean_expression.print_node(spacing + 2)
        self.then_clause.print_node(spacing + 2)
        if self.else_clause is not None:
            self.else_clause.print_node(spacing + 2)

    def visit_node(self):
        self.boolean_expression.visit_node()
        self.then_clause.visit_node()
        if self.else_clause is not None:
            self.else_clause.visit_node()

    def generate_code1(self):
        self.end = None # pula pro else (ou pro fim do if)
        self.end2 = None # pula pro fim do if qdo ele eh verdadeiro

        self.boolean_expression.generate_code1()
        self.then_clause.generate_code1()

        cg.ifActionEnd(self)

        if self.else_clause is not None:
            self.else_clause.generate_code1()
            cg.ifActionEnd2(self)
        else:
            self.end2 = self.end

    def print_code(self):
        self.boolean_expression.print_code()

        cp.jumpOnFalse(self.end)

        self.then_clause.print_code()

        if self.else_clause is not None:
            cp.jump(self.end2)
            self.else_clause.print_code(prevObject=self, ifObject=self)

        cp.addLabel(self.end2)


class Then_clause(AST):
    _fields = ["action_statement_list"]

    def __init__(self, *args, **kwargs):
        self.action_statement_list = None

        super(Then_clause, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        if self.action_statement_list is not None:
            self.action_statement_list.print_node(spacing + 2)

    def visit_node(self):
        if self.action_statement_list is not None:
            self.action_statement_list.visit_node()

    def generate_code1(self):
        if self.action_statement_list is not None:
            self.action_statement_list.generate_code1()


    def print_code(self):
        if self.action_statement_list is not None:
            self.action_statement_list.print_code()


class Else_clause(AST):
    _fields = ["action_statement_list", "boolean_expression", "then_clause", "else_clause"]

    def __init__(self, *args, **kwargs):
        self.action_statement_list = None
        self.boolean_expression = None
        self.then_clause = None
        self.else_clause = None
        super(Else_clause, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.action_statement_list.print_node(spacing + 2)
        if self.boolean_expression is not None:
            self.boolean_expression.print_node(spacing + 2)
        if self.then_clause is not None:
            self.then_clause.print_node(spacing + 2)
        if self.else_clause is not None:
            self.else_clause.print_node(spacing + 2)

    def visit_node(self):
        if self.action_statement_list is not None:
            self.action_statement_list.visit_node()
        if self.boolean_expression is not None:
            self.boolean_expression.visit_node()
        if self.then_clause is not None:
            self.then_clause.visit_node()
        if self.else_clause is not None:
            self.else_clause.visit_node()

    def generate_code1(self):
        self.end = None # pula pro proximo else if

        # eh else
        if self.action_statement_list is not None:
            self.action_statement_list.generate_code1()

        # daqui pra baixo eh else if
        if self.boolean_expression is not None:
            self.boolean_expression.generate_code1()

        if self.then_clause is not None:
            self.then_clause.generate_code1()


        if self.else_clause is not None:
            cg.elseActionEnd(self)
            self.else_clause.generate_code1()

    def print_code(self,prevObject=None, ifObject=None):
        if prevObject.end is not None:
            cp.addLabel(prevObject.end)

        if self.action_statement_list is not None:
            self.action_statement_list.print_code()

        if self.boolean_expression is not None:
            self.boolean_expression.print_code()
            if self.end is not None:
                cp.jumpOnFalse(self.end)
            else:
                cp.jumpOnFalse(ifObject.end2)

        if self.then_clause is not None:
            self.then_clause.print_code()
            cp.jump(ifObject.end2)

        if self.else_clause is not None:
            self.else_clause.print_code(prevObject=self, ifObject=ifObject)


class Do_action(AST):
    _fields = ["action_statement_list", "control_part"]

    def __init__(self, *args, **kwargs):
        self.action_statement_list = None
        self.control_part = None
        super(Do_action, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.control_part[0].print_node(spacing + 2)
        if len(self.control_part) > 1:
            self.control_part[1].print_node(spacing + 2)

        self.action_statement_list.print_node(spacing + 2)

    def visit_node(self):
        if self.control_part is not None:
            self.control = None
            if(len(self.control_part)) == 2:
                self.forControl = self.control_part[0].visit_node()
                self.whileControl = self.control_part[1].visit_node()
            else:
                self.control = self.forControl = self.control_part[0].visit_node()

        if self.action_statement_list is not None:
            self.action_statement_list.visit_node()

    def generate_code1(self):
        self.start = None
        self.end = None

        if self.control_part is not None:
            cg.doActionStart(self)
            self.control = None
            if (len(self.control_part)) == 2:
                self.forControl = self.control_part[0].generate_code1()
                self.whileControl = self.control_part[1].generate_code1()
            else:
                self.control = self.forControl = self.control_part[0].generate_code1()

        if self.action_statement_list is not None:
            self.action_statement_list.generate_code1()

        if self.control_part is not None:
            cg.doActionEnd(self)

    def print_code(self):
        if self.control_part is not None:
            if (len(self.control_part)) == 2:
                self.control_part[0].print_code()
                cp.addLabel(self.start)
                self.control_part[1].print_code(jumpTo=self.end)

            # eh for ou while, se for for, declara o label dps de carregar o valor
            # do inicio do contador, se for while ja reclara antes
            else:
                if self.control_part[0].type == "while_control":
                    cp.addLabel(self.start)
                    self.control_part[0].print_code(jumpTo=self.end)
                else:
                    self.control_part[0].print_code()
                    cp.addLabel(self.start)

        if self.action_statement_list is not None:
            self.action_statement_list.print_code()

        # testa a condicao de parada do for
        if  self.control_part is not None and self.control_part[0].type == "for_control":
            self.control_part[0].print_code2(jumpTo=self.end)

        cp.jump(self.start)

        if self.control_part is not None:
            cp.addLabel(self.end)


class For_control(AST):
    _fields = ["iteration"]

    def __init__(self, *args, **kwargs):
        self.iteration = None

        super(For_control, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.iteration.print_node(spacing + 2)

    def visit_node(self):
        self.iteration.visit_node()

    def generate_code1(self):
        self.iteration.generate_code1()

    def print_code(self):
        self.iteration.print_code()

    def print_code2(self, jumpTo=None):
        self.iteration.print_code2()
        cp.jumpOnFalse(jumpTo)


class Step_enumeration(AST):
    _fields = ["identifier", "expression", "step_value", "end_value", "isDown"]

    def __init__(self, *args, **kwargs):
        self.identifier = None
        self.expression = None
        self.step_value = None
        self.end_value = None
        self.isDown = None
        super(Step_enumeration, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        if self.isDown:
            self.print_spacing(spacing, "DOWN")
        else:
            self.print_spacing(spacing)

        self.identifier.print_node(spacing + 2)
        self.expression.print_node(spacing + 2)
        if self.step_value is not None:
            self.step_value.print_node(spacing + 2)
        self.end_value.print_node(spacing + 2)

    def visit_node(self):
        self.identifier.visit_node()
        self.expression.visit_node()
        if self.step_value is not None:
            self.step_value.visit_node()
        self.end_value.visit_node()

    def generate_code1(self):
        self.identifier.generate_code1()
        self.expression.generate_code1()
        if self.step_value is not None:
            self.step_value.generate_code1()
        self.end_value.generate_code1()

    def print_code(self):
        self.expression.print_code()
        self.identifier.print_code(type="store")

    def print_code2(self):
        self.identifier.print_code(type="load")

        if self.step_value is not None:
            self.step_value.print_code()
        else:
            cp.loadConstant(1)

        if self.isDown:
            cp.subtract()
        else:
            cp.add()

        self.identifier.print_code(type="store")
        self.identifier.print_code(type="load")
        self.end_value.print_code()

        if self.isDown:
            cp.greaterOrEqual()
        else:
            cp.lessOrEqual()


class Range_enumeration(AST):
    _fields = ["identifier", "discrete_mode_name", "isDown"]

    def __init__(self, *args, **kwargs):
        self.identifier = None
        self.discrete_mode_name = None
        self.isDown = None
        super(Range_enumeration, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        if self.isDown:
            self.print_spacing(spacing, "DOWN")
        else:
            self.print_spacing(spacing)
        self.identifier.print_node(spacing + 2)
        self.discrete_mode_name.print_node(spacing + 2)

    def visit_node(self):
        self.identifier.visit_node()
        self.discrete_mode_name.visit_node()

    def generate_code1(self):
        identifier = self.identifier.generate_code1()
        discreteModeName = self.discrete_mode_name.generate_code1()

    def print_code(self):
        self.discrete_mode_name.print_code1()
        self.identifier.print_code(type="store")

    def print_code2(self):
        self.identifier.print_code(type="load")
        cp.loadConstant(1)
        cp.add()
        self.identifier.print_code(type="store")
        self.identifier.print_code(type="load")
        self.discrete_mode_name.print_code2()
        cp.lessOrEqual()


class While_control(AST):
    _fields = ["boolean_expression"]

    def __init__(self, *args, **kwargs):
        self.boolean_expression = None

        super(While_control, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.boolean_expression.print_node(spacing + 2)

    def visit_node(self):
        self.boolean_expression.visit_node()

    def generate_code1(self):
        self.boolean_expression.generate_code1()

    def print_code(self, jumpTo=None):
        self.boolean_expression.print_code()
        cp.jumpOnFalse(jumpTo)


class Procedure_call(AST):
    _fields = ["identifier", "parameter_list"]

    def __init__(self, *args, **kwargs):
        self.identifier = None
        self.parameter_list = None
        super(Procedure_call, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.identifier.print_node(spacing + 2)
        if self.parameter_list is not None:
            self.parameter_list.print_node(spacing + 2)

    def visit_node(self):
        self.identifier.visit_node()
        if self.parameter_list is not None:
            self.parameter_list.visit_node()
            
        self.id = None 
        if self.identifier.id is not None:
            self.id = self.identifier.id
        return self

    def generate_code1(self):
        identifier = self.identifier.generate_code1()
        self.parameterList = None
        self.id = None

        if self.parameter_list is not None:
            self.parameterList = self.parameter_list.generate_code1()

        if identifier is not None:
            self.id = identifier.id

        return self

    def print_code(self, type="load"):
        ret = cg.curr_node.lookup(self.id)

        # se tem retorno, aloca espaco na pilha para o resultado
        if ret.hasReturn:
            cp.alocateMemory(ret.returnSize)

        self.parameter_list.print_code(param_list=ret.param_list)

        cp.callFunction(ret.idStart)

        return ret.isLocation


class Parameter_list(AST):
    _fields = ["expressions"]

    def __init__(self, *args, **kwargs):
        self.expressions = None

        super(Parameter_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        for expression in self.expressions:
            expression.print_node(spacing + 2)

    def visit_node(self):
        for expression in self.expressions:
            expression.visit_node()

    def generate_code1(self):
        parameterList = []
        for expression in self.expressions:
            parameterList.append(expression.generate_code1())
        return parameterList

    def print_code(self, param_list=None):
        #param_list.reverse()
        for index in reversed(range(len(self.expressions))):
            expression = self.expressions[index]
            param = param_list[index]
            type="load"
            if param:
                type="load_reference"

            expression.print_code(type=type)


    def getParameterList(self):
        parameterList = []
        for expression in self.expressions:
            parameterList.append(expression)
        return parameterList


class Exit_action(AST):
    _fields = ["identifier"]

    def __init__(self, *args, **kwargs):
        self.identifier = None

        super(Exit_action, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.identifier.print_node(spacing + 2)

    def visit_node(self):
        self.identifier.visit_node()

    def generate_code1(self):
        identifier = self.identifier.generate_code1()

    def print_code(self):
        ret = cg.curr_node.lookup(self.identifier.id)
        cp.jump(ret.actionStatementLabel)


class Return_action(AST):
    _fields = ["expression"]

    def __init__(self, *args, **kwargs):
        self.expression = None

        super(Return_action, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        if self.expression is not None:
            self.expression.print_node(spacing + 2)

    def visit_node(self):
        if self.expression is not None:
            self.expression.visit_node()

    def generate_code1(self):
        if self.expression is not None:
            self.expression.generate_code1()

    def print_code(self):
        if self.expression is not None:
            ret = cg.curr_node.lookup(cg.curr_node.nodeId)
            type = "load"

            if ret.isLocation:
                type = "load_reference"

            self.expression.print_code(type=type)

            cp.storeValue(cg.curr_node.scope, cg.curr_node.ids_parameter)


class Result_action(AST):
    _fields = ["expression"]

    def __init__(self, *args, **kwargs):
        self.expression = None

        super(Result_action, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.expression.print_node(spacing + 2)

    def visit_node(self):
        self.expression.visit_node()

    def generate_code1(self):
        self.expression.generate_code1()

    def print_code(self):
        ret = cg.curr_node.lookup(cg.curr_node.nodeId)
        type="load"

        if ret.isLocation:
            type="load_reference"

        self.expression.print_code(type=type)

        cp.storeValue(cg.curr_node.scope, cg.curr_node.ids_parameter)


class Builtin_call(AST):
    _fields = ["builtin_name", "parameter_list"]

    def __init__(self, *args, **kwargs):
        self.builtin_name = None
        self.parameter_list = None
        super(Builtin_call, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.builtin_name, self.location)
        if self.parameter_list is not None:
            self.parameter_list.print_node(spacing + 2)

    def visit_node(self):
        if self.parameter_list is not None:
            self.parameterList = self.parameter_list.visit_node()
        self.builtinName = self.builtin_name
        return self

    def generate_code1(self):
        if self.parameter_list is not None:
            self.parameterList = self.parameter_list.generate_code1()
        self.builtinName = self.builtin_name
        return self


    def print_code(self, type="load"):
        if self.parameter_list is not None:
            parameterList = self.parameter_list.getParameterList()
            if self.builtin_name == "print":
                for expression in parameterList:
                    ret = expression.print_code()
                    if ret and ret[0] == str:
                        cp.printStringContents(ret[1])
                    else:
                        cp.printValue()
            elif self.builtin_name == "num":
                return 97
            elif self.builtin_name == "pred":
                return 97
            elif self.builtin_name == "succ":
                return 97
            elif self.builtin_name == "upper":
                try:
                    for expression in parameterList:
                        if expression.expr.location_type.type == "identifier":
                            ret = cg.curr_node.lookup(expression.expr.location_type.id)
                            value = ret.indexList[0].expr2.expr.value
                            cp.loadConstant(value)
                except:
                    pass
            elif self.builtin_name == "lower":
                try:
                    for expression in parameterList:
                        if expression.expr.location_type.type == "identifier":
                            ret = cg.curr_node.lookup(expression.expr.location_type.id)
                            value = ret.indexList[0].expr1.expr.value
                            cp.loadConstant(value)
                except:
                    pass
            elif self.builtin_name == "length":
                try:
                    for expression in parameterList:
                        if expression.expr.location_type.type == "identifier":
                            ret = cg.curr_node.lookup(expression.expr.location_type.id)
                            cp.loadConstant(ret.idSize)
                except:
                    pass
            elif self.builtin_name == "read":
                for expression in parameterList:
                    if expression.expr.type=="location":
                        l = expression.expr
                        if l.location_type.type == "stringarray_element":
                            l = l.location_type
                            expression.print_code(type="")
                            cp.readSingleValue()
                            cp.storeMultipleValues(1)
                        else:
                            cp.readSingleValue()
                            expression.print_code(type="store")
                    else:
                        cp.readSingleValue()
                        expression.print_code(type="store")


class Procedure_statement(AST):
    _fields = ["identifier", "procedure_definition"]

    def __init__(self, *args, **kwargs):
        self.identifier = None
        self.procedure_definition = None
        super(Procedure_statement, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing, self.location)
        self.identifier.print_node(spacing + 2)
        self.procedure_definition.print_node(spacing + 2)

    def visit_node(self):
        identifier = self.identifier.visit_node(declaring=True)
        procedureDefinition = self.procedure_definition.visit_node(procName=identifier.id)
        procedureDefinition.id = identifier.id
        return procedureDefinition

    def generate_code1(self):
        self.start = None
        self.end = None
        self.scope = None

        self.identifier = self.identifier.generate_code1().id
        self.procedure_definition.generate_code1(identifier=self.identifier)

    def print_code(self):
        ret = cg.curr_node.lookup(self.identifier)

        cp.jump(ret.idEnd)
        cp.addLabel(ret.idStart)
        cp.enterFunction(ret.scope+1)

        self.procedure_definition.print_code()

        cp.addLabel(ret.idEnd)


class Procedure_definition(AST):
    _fields = ["formal_parameter_list", "result_spec", "statement_list"]

    def __init__(self, *args, **kwargs):
        self.formal_parameter_list = None
        self.result_spec = None
        self.statement_list = None
        super(Procedure_definition, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        if self.formal_parameter_list is not None:
            self.formal_parameter_list.print_node(spacing)
        if self.result_spec is not None:
            self.result_spec.print_node(spacing)
        if self.statement_list is not None:
            self.statement_list.print_node(spacing)
            
    def visit_node(self, procName=None):
        self.parameterList = []
        self.resultSpec = None
        self.statementList = None
        
        if self.result_spec is not None:
            self.resultSpec = self.result_spec.visit_node()
         
        if self.resultSpec is not None: 
            # adiciona o procedimento no environment com o tipo adequado
            specMode = self.resultSpec.specMode
            if specMode == "int":
                environment.add_local(procName, IntType(procName, None))
            elif specMode == "char":
                environment.add_local(procName, CharType(procName, None)) 
            elif specMode == "bool":
                environment.add_local(procName, BoolType(procName, None)) 
            elif specMode == "string":
                environment.add_local(procName, StringType(procName, None)) 
            elif hasattr(self.resultSpec, "type") and specMode.type == "array":
                environment.add_local(procName, ArrayType(procName,specMode.elementMode, None))   
        else:
            environment.add_local(procName, VoidType(procName, None))

        environment.push(None)
                
        if self.formal_parameter_list is not None:
            self.parameterList = self.formal_parameter_list.visit_node(declaring=True)

        # adiciona os parametros
        for parameter in self.parameterList:
            for identifier in parameter.identifierList:
                mode = parameter.parameterSpec.specMode

                # used for arrays only
                try:
                    elementMode = mode.elementMode
                except:
                    elementMode = None
                   
                # if the mode was defined by the user
                if hasattr(mode, "type") and mode.type == "mode":
                    elementMode = mode.elementMode
                    mode = mode.modeIdType
                        
                if mode == "int":
                    environment.add_local(identifier.id, IntType(identifier.id, None))
                elif mode == "char":
                    environment.add_local(identifier.id, CharType(identifier.id, None)) 
                elif mode == "bool":
                    environment.add_local(identifier.id, BoolType(identifier.id, None)) 
                elif mode == "string":
                    environment.add_local(identifier.id, StringType(identifier.id, None)) 
                elif hasattr(mode, "type") and mode.type == "array":
                    environment.add_local(identifier.id, ArrayType(identifier.id,elementMode, None)) 

                else:
                    raise DefinitionError("Error: parameter mode {0} unknown. Line={1}".format(parameter.parameterSpec, self.lineno),"")
        
        if self.statement_list is not None:
            self.statement_list.visit_node()
        
        environment.pop()
        return self

    def generate_code1(self, identifier=None):
        self.identifier = identifier
        self.formalParameterList = None
        self.resultSpec = None
        self.statementList = None
        self.start = None
        self.end = None
        self.param_list = None
        self.nParameters = 0

        if self.formal_parameter_list is not None:
            self.formalParameterList = self.formal_parameter_list.generate_code1()
        if self.result_spec is not None:
            self.resultSpec = self.result_spec.generate_code1()

        cg.procedureDefinitionStart(self)

        if self.statement_list is not None:
            self.statementList = self.statement_list.generate_code1()

        cg.procedureDefinitionEnd(self)

        return self

    def print_code(self):
        cg.procedureCall()

        _min = 99999999
        _max = 0
        for j in cg.curr_node.st:
            i = cg.curr_node.st[j]
            if i.type != "declaration":
                continue
            if i.idStart < _min:
                _min = i.idStart
            if i.idEnd > _max:
                _max = i.idEnd
        if _min <= _max:
            cp.alocateMemory(_max-_min)

        self.statement_list.print_code()

        if _min <= _max:
            cp.deallocateMemory(_max - _min)

        cp.returnFromFunction(cg.curr_node.scope,self.nParameters)
        cg.procedureLeave()


class Action_statement_list(AST):
    _fields = ["action_statements"]

    def __init__(self, *args, **kwargs):
        self.action_statements = None

        super(Action_statement_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        #self.print_spacing(spacing, self.location)
        for i in self.action_statements:
            i.print_node(spacing)

    def visit_node(self):
        for actionStatement in self.action_statements:
            actionStatement.visit_node()

    def generate_code1(self):
        for actionStatement in self.action_statements:
            actionStatement.generate_code1()

    def print_code(self):
        for actionStatement in self.action_statements:
            actionStatement.print_code()


class Formal_parameter_list(AST):
    _fields = ["formal_parameters"]

    def __init__(self, *args, **kwargs):
        self.formal_parameters = None

        super(Formal_parameter_list, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        for i in self.formal_parameters:
            i.print_node(spacing)

    def visit_node(self, declaring=None):
        parameterList = []
        for i in self.formal_parameters:
            parameterList.append(i.visit_node(declaring))
        return parameterList

    def generate_code1(self):
        parameterList = []
        for parameter in self.formal_parameters:
            parameterList.append(parameter.generate_code1())
        return parameterList

    def print_code(self):
        pass


class Formal_parameter(AST):
    _fields = ["identifier_list", "parameter_spec"]

    def __init__(self, *args, **kwargs):
        self.identifier_list = None
        self.parameter_spec = None
        super(Formal_parameter, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        self.print_spacing(spacing)
        self.identifier_list.print_node(spacing + 2)
        self.parameter_spec.print_node(spacing + 2)

    def visit_node(self, declaring=None):
        self.parameterSpec = self.parameter_spec.visit_node()
        self.identifierList = self.identifier_list.visit_node(declaring)
        return self

    def generate_code1(self):
        self.identifierList = self.identifier_list.generate_code1()
        parameterSpec = self.parameter_spec.generate_code1()
        self.parameterSpecMode = parameterSpec.mode
        self.isLocation = parameterSpec.isReference
        return self

    def print_code(self):
        pass


class Parameter_spec(AST):
    _fields = ["mode", "isReference"]

    def __init__(self, *args, **kwargs):
        self.mode = None
        self.isReference = None
        super(Parameter_spec, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        if self.isReference:
            print " " * (spacing+2) + "LOC Param"
        self.mode.print_node(spacing)

    def visit_node(self):
        self.specMode = self.mode.visit_node()
        return self

    def generate_code1(self):
        self.parameterSpecMode = self.mode.generate_code1()
        return self

    def print_code(self):
        pass


class Result_spec(AST):
    _fields = ["mode", "isReference"]

    def __init__(self, *args, **kwargs):
        self.mode = None
        self.isReference = None
        super(Result_spec, self).__init__(*args, **kwargs)

    def print_node(self, spacing):
        if self.isReference:
            print " " * (spacing+2) + "LOC Result"
        self.mode.print_node(spacing)

    def visit_node(self):
        self.specMode = self.mode.visit_node()
        return self

    def generate_code1(self):
        self.resultSpecMode = self.mode.generate_code1()
        return self

    def print_code(self):
        pass
