#!/usr/bin/python
# -*- coding: utf-8 -*


from __future__ import print_function

import sys


class CodePrinter(object):
    def __init__(self, output=sys.stdout):
        self.M = []
        self.D = []
        if type(output) == str:
            self.output = open(output, 'w')
        else:
            self.output = output

    def __exit__(self, exc_type, exc_val, exc_tb):
        if type(self.output) == file:
            self.output.close()

    def printStrs(self, strs):
        print("H = {}".format(strs), file=self.output)

    # 'stp') Start Program
    # sp=-1; D[0]=0
    def startProgram(self):
        print("[", file=self.output)
        print(" ('stp'),", file=self.output)

    # ('end') Stop execution
    def endProgram(self):
        print(" ('end'),", file=self.output)
        print("]", file=self.output)


    # ('alc', n)  # Allocate memory
    # sp = sp + n
    def alocateMemory(self, n):
        print(" ('alc', {0}),".format(n), file=self.output)


    # Load constant
    # ('ldc', k)
    # sp=sp+1;
    # M[sp]=k
    def loadConstant(self, k):
        print(" ('ldc', {0}),".format(k), file=self.output)


    # Load value
    # ('ldv', i, j)
    # sp = sp + 1;
    # M[sp] = M[D[i] + j]
    def loadValue(self, i, j):
        print(" ('ldv', {0}, {1}),".format(i, j), file=self.output)


    # Load reference
    # ('ldr', i, j)
    # sp = sp + 1;
    # M[sp] = D[i] + j
    def loadReference(self, i, j):
        print(" ('ldr', {0}, {1}),".format(i, j), file=self.output)


    # ('stv', i, j)  # Store value
    # M[D[i] + j] = M[sp];
    # sp = sp
    def storeValue(self, i, j):
        print(" ('stv', {0}, {1}),".format(i, j), file=self.output)


    # ('lrv', i, j)  # Load reference value
    # sp = sp + 1;
    # M[sp] = M[M[D[i] + j]]
    def loadReferenceValue(self, i, j):
        print(" ('lrv', {0}, {1}),".format(i, j), file=self.output)


    # ('srv', i, j)  # Store reference value
    # M[M[D[i] + j]] = M[sp];
    # sp = sp - 1
    def storeReferenceValue(self, i, j):
        print(" ('srv', {0}, {1}),".format(i, j), file=self.output)


    # ('add')  # Add
    # M[sp - 1] = M[sp - 1] + M[sp];
    # sp = sp - 1
    def add(self):
        print(" ('add'),", file=self.output)


    # ('sub')  # Subtract
    # M[sp - 1] = M[sp - 1] - M[sp];
    # sp = sp - 1
    def subtract(self):
        print(" ('sub'),", file=self.output)


    # ('mul')  # Multiply
    # M[sp - 1] = M[sp - 1] * M[sp];
    # sp = sp - 1
    def multiply(self):
        print(" ('mul'),", file=self.output)


    # ('div')  # Division
    # M[sp - 1] = M[sp - 1] / M[sp];
    # sp = sp - 1
    def division(self):
        print(" ('div'),", file=self.output)


    # ('mod')  # Modulus
    # M[sp - 1] = M[sp - 1] % M[sp];
    # sp = sp - 1
    def modulus(self):
        print(" ('mod'),", file=self.output)


    # ('neg')  # Negate
    # M[sp] = -M[sp]
    def negate(self):
        print(" ('neg'),", file=self.output)


    # (' and ')  # Logical And
    # M[sp - 1] = M[sp - 1] and M[sp];
    # sp = sp - 1
    def logicalAnd(self):
        print(" ('and'),", file=self.output)


    # ('lor')  # Logical Or
    # M[sp - 1] = M[sp - 1] or M[sp];
    # sp = sp - 1
    def logicalOr(self):
        print(" ('lor'),", file=self.output)


    # ('not')  # Logical Not
    # M[sp] = not M[sp]
    def logicalNot(self):
        print(" ('not'),", file=self.output)


    # ('les')  # Less
    # M[sp - 1] = M[sp - 1] < M[sp];
    # sp = sp - 1
    def less(self):
        print(" ('les'),", file=self.output)


    # ('leq')  # Less or Equal
    # M[sp - 1] = M[sp - 1] <= M[sp];
    # sp = sp - 1
    def lessOrEqual(self):
        print(" ('leq'),", file=self.output)


    # ('grt')  # Greater
    # M[sp - 1] = M[sp - 1] > M[sp];
    # sp = sp - 1
    def greater(self):
        print(" ('grt'),", file=self.output)


    # ('gre')  # Greater or Equal
    # M[sp - 1] = M[sp - 1] >= M[sp];
    # sp = sp - 1
    def greaterOrEqual(self):
        print(" ('gre'),", file=self.output)


    # ('equ')  # Equal
    # M[sp - 1] = M[sp - 1] == M[sp];
    # sp = sp - 1
    def equal(self):
        print(" ('equ'),", file=self.output)


    # ('neq')  # Not Equal
    # M[sp - 1] = M[sp - 1] != M[sp];
    # sp = sp - 1
    def notEqual(self):
        print(" ('neq'),", file=self.output)


    # ('jmp', p)  # Jump
    # pc = p
    def jump(self, p):
        print(" ('jmp', {0}),".format(p), file=self.output)


    # ('jof', p)  # Jump on False
    #if not M[sp]:
    #    pc = p
    #else:
    #    pc = pc + 1
    # sp = sp - 1
    def jumpOnFalse(self, p):
        print(" ('jof', {0}),".format(p), file=self.output)


    # ('dlc', n)  # Deallocate memory
    # sp = sp - n
    def deallocateMemory(self, n):
        print(" ('dlc', {0}),".format(n), file=self.output)


    # ('cfu', p)  # Call Function
    # sp = sp + 1;
    # M[sp] = pc + 1;
    # pc = p
    def callFunction(self, p):
        print(" ('cfu', {0}),".format(p), file=self.output)


    # ('enf', k)  # Enter Function
    # sp = sp + 1;
    # M[sp] = D[k];
    # D[k] = sp + 1
    def enterFunction(self, k):
        print(" ('enf', {0}),".format(k), file=self.output)


    # ('ret', k, n)  # Return from Function
    # D[k] = M[sp];
    # pc = M[sp - 1];
    #  sp = sp - (n + 2)
    def returnFromFunction(self, k, n):
        print(" ('ret', {0}, {1}),".format(k, n), file=self.output)


    # ('idx', k)  # Index
    # M[sp - 1] = M[sp - 1] + M[sp] * k
    # sp = sp - 1
    def index(self, k):
        print(" ('idx', {0}),".format(k), file=self.output)


    # ('grc')  # Get(Load) Reference Contents
    # M[sp] = M[M[sp]]
    def getReferenceContents(self):
        print(" ('grc'),", file=self.output)


    # ('lmv', k)  # Load multiple values
    # t = M[sp]
    # M[sp:sp + k] = M[t:t + k]
    # sp += (k - 1)
    def loadMultipleValues(self, k):
        print(" ('lmv', {0}),".format(k), file=self.output)


    # ('smv', k)  # Store multiple Values
    # t = M[sp - k]
    # M[t:t + k] = M[sp - k + 1:sp + 1]
    # sp -= (k + 1)
    def storeMultipleValues(self, k):
        print(" ('smv', {0}),".format(k), file=self.output)


    # ('smr', k)  # Store multiple References
    # t1 = M[sp - 1]
    # t2 = M[sp]
    # M[t1:t1 + k] = M[t2:t2 + k]
    # sp -= 1
    def storeMultipleReferences(self, k):
        print(" ('smr', {0}),".format(k), file=self.output)


    # ('sts', k)  # Store string constant on reference
    # adr = M[sp]
    # M[adr] = len(H[k])
    # for c in H[k]:
    #    adr = adr + 1
    #    M[adr] = c;
    # sp = sp - 1
    def storeStringReference(self, k):
        print(" ('sts', {0}),".format(k), file=self.output)


    # ('rdv')  # Read single Value
    # sp = sp + 1;
    # M[sp] = input()
    def readSingleValue(self):
        print(" ('rdv'),", file=self.output)


    # ('rds')  # Read String and store it on stack reference
    # str = input()
    # adr = M[sp]
    # M[adr] = len(str)
    # for k in str:
    #    adr = adr + 1
    #    M[adr] = k
    # sp = sp - 1
    def readString(self):
        print(" ('rds'),", file=self.output)


    # ('prv')  # Print Value
    # print(M[sp]);
    # sp = sp - 1
    def printValue(self):
        print(" ('prv'),", file=self.output)


    # ('prt', k)  # Print Multiple Values
    # print(M[sp - k + 1:sp + 1]);
    # sp -= (k - 1)
    def printMultipleValues(self, k):
        print(" ('prt', {0}),".format(k), file=self.output)


    # ('prc', i)  # Print String constant
    # print(H(i), end="")
    def printStringContents(self, i):
        print(" ('prc', {0}),".format(i), file=self.output)


        # ('prs')  # Print contents of a string location
        # adr = M[sp]
        # len = M[adr]
        # for i in range(0, len):
        #    adr = adr + 1
        #    print(M(adr), end="")
        # sp = sp - 1
    def printStringContentsLocation(self):
        print(" ('prs'),", file=self.output)


    # ('lbl', i)  # No operation
    # (define the label index i)
    def addLabel(self, i):
        print(" ('lbl', {0}),".format(i), file=self.output)
    
    