#!/usr/bin/python

from interpreter import Interpreter
from compiler import LyaCompiler
from lya_errors import *
import unittest
import os
import sys


def fit(text, size=80, filler='#'):
    be_used = size - len(text)
    ret = filler * int(be_used/2) + text + filler * int(be_used/2)
    if len(text) % 2 == 1:
        ret += "#"
    return ret


class Examples(unittest.TestCase):
    def test_all(self):
        folder = "./examples/"
        files = os.listdir(folder)
        for i in files:
            if "example" in i and ".lya" in i and not '.o' in i:
                sys.argv = ['./compiler.py', '-ast-walker', folder + i]
                print fit(i)
                m = LyaCompiler()
                m.run()
                print fit("")


class ErrorTests(unittest.TestCase):
    def test_errors(self):
        folder = "./examples/errors/"
        files = os.listdir(folder)
        for i in files:
            print fit(i)
            sys.argv = ['./compiler.py', '-ast-walker', folder + i]
            m = LyaCompiler()

            if "invalid" in i:
                self.assertRaises(CompilerException, lambda: m.run())
            else:
                m.run()
            print fit("")

"""
class InterpreterTests(unittest.TestCase):
    def test_H(self):
        sys.argv = ['./interpreter.py', './examples/test_interpreter_H.lya.i']
        i = Interpreter()
        i.load_program()

    def test_no_H(self):
        sys.argv = ['./interpreter.py', './examples/test_interpreter.lya.i']
        i = Interpreter()
        i.load_program()
"""

class CodeGeneration(unittest.TestCase):
    def test_all(self):
        diff_set = set()

        folder = "./examples/"
        resps_folder = "./examples/resps/"
        files = os.listdir(folder)
        for i in files:
            if "email" in i and ".lya" in i and not ".o" in i:
                sys.argv = ['./compiler.py', folder + i, '-o', folder + i + ".o"]
                print fit("running: " + i)
                m = LyaCompiler()
                m.run()
                print fit("")

        from lya_ast import cp
        from lya_codeprinter import CodePrinter
        global cp
        cp = CodePrinter()


        for i in files:
            if "email" in i and ".lya" in i and not ".o" in i:
                import ast
                import re
                output_file = folder + i + ".o"
                resp_file = resps_folder + i.replace(".lya", ".out")

                print fit("comparing: " + i)
                f_o = open(output_file, 'r')
                data_o = f_o.read()
                data_o = data_o.replace("true", "True")
                data_o = data_o.replace("false", "False")
                try:
                    data_o = ast.literal_eval(data_o)
                except Exception as e:
                    diff_set.add(i)
                    print i, "has invalid output from code"
                    print data_o
                    print e
                    print fit("")
                    continue

                r_o = open(resp_file, 'r')
                data_r = r_o.read()
                data_r = data_r.replace("true", "True")
                data_r = data_r.replace("false", "False")
                if data_r == '':
                    diff_set.add(i)
                    print i, "has no answer"
                    print fit("")
                    continue
                data_r = re.sub("//.*\n", "\n", data_r)
                data_r = ast.literal_eval(data_r)

                if data_o != data_r:
                    if len(data_o) > len(data_r):
                        _max = len(data_o)
                    else:
                        _max = len(data_r)
                    for l in range(_max):
                        if data_o[l] != data_r[l]:
                            diff_set.add(i)
                            print "line:", l+1
                            print "output >", data_o[l]
                            print "answer <", data_r[l]
                print fit("")
        print fit("")
        print "the files with problems are:", ", ".join(list(diff_set))
        print fit("")

if __name__ == "__main__":
    unittest.main()