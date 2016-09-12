# -*- coding: utf-8 -*-


class CompilerException(Exception):
    def __init__(self, what, explanation):
        super(CompilerException, self).__init__("Error: " + str(what) + "\n" + str(explanation))


class InvalidASTNode(CompilerException):
    pass


class InitializationError(CompilerException):
    pass


class DefinitionError(CompilerException):
    pass


class VariableTypeError(CompilerException):
    pass


class UnexpectedError(CompilerException):
    pass


class InvalidOperatorError(CompilerException):
    pass


class NewModeStatementError(CompilerException):
    pass


class SynonymAssignmentError(CompilerException):
    pass


class FileNotFoundError(CompilerException):
    pass


class InterpreterError(CompilerException):
    pass
