#!/usr/bin/python
# -*- coding: utf-8 -*-

class SymbolTable(dict):
    def __init__(self, decl=None):
        super(SymbolTable, self).__init__()
        self.decl = decl

    def add(self, name, value):
        self[name] = value

    def lookup(self, name):
        return self.get(name, None)


class Parameters(object):
    def __init__(self):
        self.id = None
        self.value = None
        self.mode = None
        self.idStart = None
        self.idEnd = None
        self.idSize = None
        self.type = None
        self.actionStatementLabel = None
        self.scope = None
        self.isLocation = False
        self.hasReturn = False
        self.returnSize = Non
        self.indexList = None
        self.param_list = None


class ProgramTree(object):
    def __init__(self):
        self.root = Node(None, 0)


class Node(object):
    def __init__(self, parent, scope):
        self.children = []

        self.st = SymbolTable()
        self.ids_start = 0
        self.parent = parent
        self.ids_parameter = -3
        self.scope = scope
        self.nodeId = None

    def get_id_start(self):
        return self.ids_start

    def update_id_start(self, size):
        self.ids_start += size

    def get_id_start_parameter(self, resultSpec):
        if resultSpec is None and False:
            return self.ids_parameter+1
        else:
            return self.ids_parameter

    def update_id_start_parameter(self, size):
        self.ids_parameter -= size

    def add_child(self, nodeId=None):
        node = Node(self, self.scope+1)
        self.children.append(node)
        node.nodeId = nodeId
        return node

    def remove_child_front(self):
        self.children.pop(0)

    def remove_child_back(self):
        self.children.pop()

    def peek(self):
        return self.children[-1]

    def call_procedure(self):
        return self.children[0]

    def leave_procedure(self):
        node = self.parent
        node.remove_child_front()
        return node

    def add_local_declaration(self, name, params):
        params.type = "declaration"
        params.scope = self.scope
        self.st.add(name, params)

    def add_local_procedure(self, name, params):
        params.type = "procedure"
        params.scope = self.scope
        self.st.add(name, params)

    def add_local_synonym(self, name, params):
        params.type = "synonym"
        params.scope = self.scope
        self.st.add(name, params)

    def add_local_mode_definition(self, name, params):
        params.type = "mode_definition"
        params.scope = self.scope
        self.st.add(name, params)

    def add_local_parameter(self, name, params):
        params.type = "parameter"
        params.scope = self.scope
        self.st.add(name, params)

    def add_local_action_statement(self, name, params):
        params.type = "action_statement"
        params.scope = self.scope
        self.st.add(name, params)

    def find(self, name):
        if name in self.st:
            return True
        else:
            return False

    def lookup(self, name):
        node = self

        while node is not None:
            hit = node.st.lookup(name)
            if hit is not None:
                return hit

            node = node.parent

        return None

class Environment(object):
    def __init__(self):
        self.stack = []
        self.root = SymbolTable()
        self.stack.append(self.root)
        self.root.update({
            "int": IntType("int"),
            "char": CharType("char"),
            "string": StringType("string"),
            "bool": BoolType("bool")
        })

    def push(self, enclosure):
        self.stack.append(SymbolTable(decl=enclosure))

    def pop(self):
        self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def scope_level(self):
        return len(self.stack)

    def add_local(self, name, value):
        self.peek().add(name, value)

    def add_root(self, name, value):
        self.root.add(name, value)

    def lookup(self, name):
        for scope in reversed(self.stack):
            hit = scope.lookup(name)
            if hit is not None:
                return hit
        return None

    def find(self, name):
        if name in self.stack[-1]:
            return True
        else:
            return False


class ExprType(object):
    def __init__(self, name=None):
        self.name = name


class IntType(ExprType):
    def __init__(self, name=None, value=0, synonym=False):
        super(IntType, self).__init__(name)
        self._accepted_operations_binary = ['+', '-', '*', '/', '%', '==', '!=', '>', '>=', '<', '<=']
        self._accepted_operations_unary = ['+', '-']
        self._value = value
        self.type = "int"
        self.synonym = synonym


class CharType(ExprType):
    def __init__(self, name=None, value='', synonym=False):
        super(CharType, self).__init__(name)
        self._accepted_operations_binary = ['==', '!=', '>', '>=', '<', '<=']
        self._accepted_operations_unary = []
        self._value = value
        self.type = "char"
        self.synonym = synonym


class StringType(ExprType):
    def __init__(self, name=None, value="", synonym=False):
        super(StringType, self).__init__(name)
        self._accepted_operations_binary = ['+', '==', '!=']
        self._accepted_operations_unary = []
        self._value = value
        self.type = "string"
        self.synonym = synonym


class ArrayType(ExprType):
    def __init__(self, name=None,valuesType=None, value=None):
        super(ArrayType, self).__init__(name)
        self._accepted_operations_binary = []
        self._accepted_operations_unary = []
        self._value = value
        self.type = "array"
        self.valuesType = valuesType


class BoolType(ExprType):
    def __init__(self, name=None, value=False, synonym=False):
        super(BoolType, self).__init__(name)
        self._accepted_operations_binary = ['==', '!=']
        self._accepted_operations_unary = ['!']
        self._value = value
        self.type = "bool"
        self.synonym = synonym


class VoidType(ExprType):
    def __init__(self, name=None, value=False):
        super(VoidType, self).__init__(name)
        self._accepted_operations_binary = []
        self._accepted_operations_unary = []
        self._value = value
        self.type = "void"


class LabelType(ExprType):
    def __init__(self, name=None, value=None):
        super(LabelType, self).__init__(name)
        self._accepted_operations_binary = []
        self._accepted_operations_unary = []
        self._value = value
        self.type = "label"

