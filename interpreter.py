#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function


from lya_errors import FileNotFoundError, InterpreterError
import sys

from ast import literal_eval
import re


class Interpreter(object):
    def __init__(self, debug=False):
        self._debug = debug
        self._file = sys.argv[1:]
        # from file
        self._H = None
        self._text = ""
        # from execution
        self._pc = None
        self._sp = None
        self._M = None
        self._D = None
        self._running = None
        # labels
        self._labels_ref = dict()
        #input buffer
        self._input_buffer = list()

    def load_program(self, file_name=None):
        if file_name is None:
            if len(self._file) == 0:
                print("No input given.")
            for curr_src in self._file:
                self.load_file(curr_src)
                self.run()
        else:
            self.load_file(file_name)
            self.run()

    def load_file(self, file_name):
        try:
            curr_file = open(file_name, "r")
        except:
            raise FileNotFoundError("Could not open file.", file_name)
        for l in curr_file:
            if 'H' in l:
                self._H = re.sub("^\s+(.*)", '\\1', l.replace('’', "'"))
                self._H = self._H[self._H.find('['):]
            else:
                self._text += l
        if self._H is not None:
            self._H = literal_eval(self._H)

        self._text = self._text.replace('’', "'")
        self._text = self._text.replace("true", "True")
        self._text = self._text.replace("false", "False")
        # remove spacing
        self._text = re.sub("^\s+(.*)", '\\1', self._text, re.DOTALL)
        
        self._text = literal_eval(self._text)
        
        for i in range(len(self._text)):
            if type(self._text[i]) == str:
                self._text[i] = tuple((self._text[i], None))

        curr_file.close()

    def reset(self):
        self._pc = 0
        self._sp = 0
        self._M = [0] * 10000
        self._D = [0] * 6
        self._running = True

    def run(self):
        self.reset()
        """
        print "H", type(self._H)
        print self._H
        print "text", type(self._text)
        print self._text
        """
        self.process_labels()
        if self._debug:
            for i in range(len(self._text)):
                print(i, self._text[i])
        while self._running:
            if self._debug:
                print("pc:", self._pc, ", sp:", self._sp)
                print("M:", self._M)
                print("D:", self._D)
                print(self._text[self._pc])
            self.exec_op(self._text[self._pc])

    def process_labels(self):
        for i in range(len(self._text)):
            row = self._text[i]
            if row[0] == 'lbl':
                if self._labels_ref.get(row[1], None) == None:
                    self._labels_ref[row[1]] = i

    def exec_op(self, row):
        if row[0] == 'ldc':
            self._sp += 1
            self._M[self._sp] = row[1]
        elif row[0] == 'ldv':
            self._sp += 1
            self._M[self._sp] = self._M[self._D[row[1]] + row[2]]
        elif row[0] == 'ldr':
            self._sp += 1
            self._M[self._sp] = self._D[row[1]] + row[2]
        elif row[0] == 'stv':
            self._M[self._D[row[1]]+row[2]] = self._M[self._sp]
            self._sp -= 1
        elif row[0] == 'lrv':
            self._sp += 1
            self._M[self._sp] = self._M[self._M[self._D[row[1]] + row[2]]]
        elif row[0] == 'srv':
            self._M[self._M[self._D[row[1]] + row[2]]] = self._M[self._sp]
            self._sp -= 1
        elif row[0] == 'add':
            self._M[self._sp - 1] = eval("{} + {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'sub':
            self._M[self._sp - 1] = eval("{} - {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'mul':
            self._M[self._sp - 1] = eval("{} * {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'div':
            self._M[self._sp - 1] = eval("{} / {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'mod':
            self._M[self._sp - 1] = eval("{} % {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'neg':
            self._M[self._sp] = eval("-{}".format(self._M[self._sp]))
        elif row[0] == 'and':
            self._M[self._sp - 1] = eval("{} and {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'or':
            self._M[self._sp - 1] = eval("{} or {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'not':
            self._M[self._sp] = eval("not({})".format(self._M[self._sp]))
        elif row[0] == 'les':
            self._M[self._sp - 1] = eval("{} < {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'leq':
            self._M[self._sp - 1] = eval("{} <= {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'grt':
            self._M[self._sp - 1] = eval("{} > {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'gre':
            self._M[self._sp - 1] = eval("{} >= {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'equ':
            self._M[self._sp - 1] = eval("{} == {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'neq':
            self._M[self._sp - 1] = eval("{} != {}".format(self._M[self._sp - 1], self._M[self._sp]))
            self._sp -= 1
        elif row[0] == 'jmp':
            pos_dest = self._labels_ref.get(row[1], None)
            if pos_dest is None:
                raise InterpreterError("Jump to a place not identified.", row[1])
            self._pc = pos_dest - 1
        elif row[0] == 'jof':
            if not self._M[self._sp]:
                pos_dest = self._labels_ref.get(row[1], None)
                if pos_dest is None:
                    raise InterpreterError("Jump to a place not identified.", row[1])
                self._pc = pos_dest - 1
            self._sp -= 1
        elif row[0] == 'alc':
            self._sp += row[1]
        elif row[0] == 'dlc':
            self._sp -= row[1]
        elif row[0] == 'cfu':
            self._sp += 1
            self._M[self._sp] = self._pc + 1
            pos_dest = self._labels_ref.get(row[1], None)
            if pos_dest is None:
                raise InterpreterError("Jump to a place not identified.", row[1])
            self._pc = pos_dest - 1
        elif row[0] == 'enf':
            self._sp += 1
            self._M[self._sp] = self._D[row[1]]
            self._D[row[1]] = self._sp + 1
        elif row[0] == 'ret':
            self._D[row[1]] = self._M[self._sp]
            self._pc = self._M[self._sp - 1] - 1
            self._sp -= (row[2]+2)
        elif row[0] == 'idx':
            self._M[self._sp - 1] = self._M[self._sp - 1] + self._M[self._sp] * row[1]
            self._sp -= 1
        elif row[0] == 'grc':
            self._M[self._sp] = self._M[self._M[self._sp]]
        elif row[0] == 'lmv':
            t = self._M[self._sp]
            self._M[self._sp: self._sp + row[1]] = self._M[t: t + row[1]]
            self._sp += row[1] - 1
        elif row[0] == 'smv':
            t = self._M[self._sp - row[1]]
            self._M[t: t + row[1]] = self._M[self._sp - row[1] + 1: self._sp + 1]
            self._sp -= row[1] + 1
        elif row[0] == 'smr':
            t1 = self._M[self._sp - 1]
            t2 = self._M[self._sp]
            self._M[t1: t1 + row[1]] = self._M[t2: t2 + row[1]]
            self._sp -= 1
        elif row[0] == 'sts':
            adr = self._M[self._sp]
            self._M[adr] = len(self._H[row[1]])
            for c in self._H[row[1]]:
                adr += 1
                self._M[adr] = c
            self._sp -= 1
        elif row[0] == 'rdv':
            self._sp += 1
            if len(self._input_buffer) == 0:
                self._input_buffer = raw_input().split(' ')
            self._M[self._sp] = self._input_buffer[0]
            self._input_buffer = self._input_buffer[1:]
            if self._M[self._sp].isdigit():
                self._M[self._sp] = int(self._M[self._sp])
            elif self._M[self._sp] == 'true':
                self._M[self._sp] = "True"
            elif self._M[self._sp] == 'false':
                self._M[self._sp] = "False"
            else:
                raise InterpreterError("Invalid input, text when boolean or integer required.", self._M[self._sp])
        elif row[0] == 'rds':
            _str = raw_input()
            adr = self._M[self._sp]
            self._M[adr] = len(_str)
            for k in _str:
                adr += 1
                self._M[adr] = k
            self._sp -= 1
        elif row[0] == 'prv':
            print(self._M[self._sp])
            self._sp -= 1
        elif row[0] == 'prt':
            print(self._M[self._sp - row[1] + 1: self._sp + 1])
            self._sp -= row[1]-1
        elif row[0] == 'prc':
            print(self._H[row[1]], end="")
        elif row[0] == 'prs':
            adr = self._M[self._sp]
            _len = self._M[adr]
            for i in range(_len):
                adr += 1
                print(self._M[adr], end="")
            self._sp -= 1
        elif row[0] == 'stp':
            self._sp = -1
            self._D[0] = 0
        elif row[0] == 'lbl':
            pass
        elif row[0] == 'end':
            self._running = False
        self._pc += 1


if __name__ == "__main__":
    i = Interpreter(False)
    i.load_program()
