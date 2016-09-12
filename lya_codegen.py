#!/usr/bin/python
# -*- coding: utf-8 -*

from lya_environment import ProgramTree
from lya_environment import Parameters
from lya_errors import *


class CodeGen(object):
    def __init__(self):
        self.pt = ProgramTree()
        self.curr_node = self.pt.root
        self.label_counter = 1
        self.string_dict = dict()
        self.string_dict_count = 0

    def add_str(self, txt):
        self.string_dict[txt] = self.string_dict_count
        self.string_dict_count += 1

    def get_str(self, txt):
        return self.string_dict.get(txt, None)

    def get_all_str(self):
        return self.string_dict

    def declaration(self, identifierList, mode):
        size = self.calculateModeSize(mode)

        for identifier in identifierList:
            params = Parameters()
            params.id = identifier
            params.idSize = size
            params.mode = mode
            params.idStart = self.curr_node.get_id_start()
            params.idEnd = params.idStart+size

            ret = self.curr_node.lookup(mode.modeNameModeId)

            # se for um mode definido, ve o mode que ele representa
            if ret is not None:
                mode = ret.mode

            if mode.type2 == "array":
                params.indexList = mode.arrayIndexModeList

            self.curr_node.update_id_start(size)
            self.curr_node.add_local_declaration(identifier, params)


    def synonymDefinition(self, identifierList, mode, initialization):
        if mode.type2 == "discrete_mode":
            for identifier in identifierList:
                params = Parameters()
                params.id = identifier
                params.mode = mode.discreteModeType
                params.idSize = 1
                params.value = initialization.value
                self.curr_node.add_local_synonym(identifier, params)
        elif mode.type2 ==   "string":
            for identifier in identifierList:
                params = Parameters()
                params.id = identifier
                params.mode = "string"
                params.idSize = self.calculateModeSize(mode)
                params.value = initialization.value
                self.curr_node.add_local_synonym(identifier, params)
        else:
            raise UnexpectedError("synonymDefinition mode devia ser discrete_mode ou string.Line={0}".format(mode.lineno),"")


    def modeDefinition(self, identifierList, mode):
        size = self.calculateModeSize(mode)

        for identifier in identifierList:
            params = Parameters()
            params.idSize = size
            params.mode = mode
            params.id=identifier

            if mode.type2 == "array":
                params.indexList = mode.arrayIndexModeList

            self.curr_node.add_local_mode_definition(identifier, params)


    def procedureDefinitionStart(self, procDefObject):
        procDefObject.start = self.label_counter
        self.label_counter += 1

        self.curr_node = self.curr_node.add_child(nodeId=procDefObject.identifier)

        if procDefObject.formalParameterList is not None:
            procDefObject.param_list = []

            for formalParameter in procDefObject.formalParameterList:
                indexList = None
                if formalParameter.parameterSpecMode.type2 == "mode_name":
                    # procura o mode na tabela
                    ret = self.curr_node.lookup(formalParameter.parameterSpecMode.modeNameModeId)
                    if ret:
                        indexList=ret.indexList

                for identifier in formalParameter.identifierList:
                    params = Parameters()
                    procDefObject.param_list.append(formalParameter.isLocation)

                    if formalParameter.isLocation:
                        params.isLocation = True

                    # se for array, o tamanho eh 1 pq o array eh carregado por referencia
                    if indexList:
                        params.indexList = indexList
                        size = 1
                    else:
                        size = self.calculateModeSize(formalParameter.parameterSpecMode)

                    params.idSize = size
                    params.id = identifier
                    params.idStart = self.curr_node.get_id_start_parameter(procDefObject.resultSpec)
                    params.idEnd = params.idStart - size

                    self.curr_node.update_id_start_parameter(size)

                    self.curr_node.add_local_parameter(identifier, params)
                    procDefObject.nParameters+=1


    def procedureCall(self):
        self.curr_node = self.curr_node.call_procedure()


    def procedureLeave(self):
        self.curr_node = self.curr_node.leave_procedure()

    def procedureDefinitionEnd(self, procDefObject):
        procDefObject.end = self.label_counter
        self.label_counter += 1

        # ao sair do procedimento, volta pro pai do procedimento
        self.curr_node = self.curr_node.parent

        params = Parameters()
        params.idStart = procDefObject.start
        params.idEnd = procDefObject.end
        params.id = procDefObject.identifier
        params.param_list = procDefObject.param_list

        if procDefObject.resultSpec is not None:
            if procDefObject.resultSpec.isReference is True:
                params.isLocation = True
            params.hasReturn = True
            params.returnSize = self.calculateModeSize(procDefObject.resultSpec.resultSpecMode)

        self.curr_node.add_local_procedure(params.id, params)


    def actionStatement(self, identifier):
        params = Parameters()
        params.actionStatementLabel = self.label_counter
        params.id = identifier

        self.curr_node.add_local_action_statement(identifier, params)
        self.label_counter += 1

    # label para pular para o proximo elsif ou else
    def ifActionEnd(self, ifObject):
        ifObject.end = self.label_counter
        self.label_counter += 1

    # pula pro fim do bloco de if (entrou no if agr n passa pelos elsif, else...)
    def ifActionEnd2(self, ifObject):
        ifObject.end2 = self.label_counter
        self.label_counter += 1

    def elseActionEnd(self, elseObject):
        elseObject.end = self.label_counter
        self.label_counter += 1

    def doActionStart(self, doObject):
        doObject.start = self.label_counter
        self.label_counter += 1

    def doActionEnd(self, doObject):
        doObject.end = self.label_counter
        self.label_counter += 1

    """
        self.isReference = False
        self.type2 = modeType.type
        self.modeNameModeId = None
        self.stringLength = None
        self.arrayIndexModeList = None
        self.arrayElementMode = None
        self.discreteModeType = None
        self.referenceModeMode = None
    """
    def calculateModeSize(self, mode):
        if mode.type2 == "mode_name":
            ret = self.curr_node.lookup(mode.modeNameModeId)
            mode = ret.mode

        if mode.type2 == "reference_mode":
           mode = mode.referenceModeMode

        if mode.type2 == "string":
            return mode.stringLength
        elif mode.type2 == "array":
            sum = 0
            for indexMode in mode.arrayIndexModeList:
                try:
                    if indexMode.type == "literal_range":
                        sum = indexMode.expr2.value - indexMode.expr1.value + 1
                except:
                    return 1

            return sum

        elif mode.type2 == "discrete_mode":
            if mode.discreteModeType != "discrete_range_mode":
                return 1
            else:
                return 1
        return 1

