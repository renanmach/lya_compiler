#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import sys

from lya_ast import AST, reset
from lya_lex import LyaLexer
from lya_parser import LyaParser
from lya_errors import FileNotFoundError


class LyaCompiler:
    lexer = LyaLexer()
    parser = LyaParser()

    def __init__(self):
        self.args = None
        self._parse_args()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description='Compile a lya source code.')
        parser.add_argument('files', metavar='files', type=str, nargs=1,
                            help='the source code')
        parser.add_argument('-lexer', dest='lexer', action='store_const',
                            const=True, default=False,
                            help='select to run the lexer')
        parser.add_argument('-ast', dest='ast', action='store_const',
                            const=True, default=False,
                            help='select to run the ast')
        parser.add_argument('-ast-gencode', dest='ast_gencode', action='store_const',
                            const=True, default=False,
                            help='')
        parser.add_argument('-ast-walker', dest='ast_walker', action='store_const',
                            const=True, default=False,
                            help='')
        parser.add_argument('-run', dest='run', action='store_const',
                            const=True, default=False,
                            help='')
        parser.add_argument('-o', dest='output', type=str, default="", nargs=1, help='output file')
        self.args = parser.parse_args()
        if type(self.args.output) == list:
            self.args.output = self.args.output[0]

    def run(self):
        if self.args.lexer:
            self._lexer()
        if self.args.ast:
            self._ast()
        if self.args.ast_walker:
            self._ast_walker()
        if not (self.args.lexer or self.args.ast or self.args.ast_walker):
            if self.args.run:
                self.args.output = ".temporary_interpreter.tmp"
                self._ast_gencode()
                ast = AST([])
                ast.set_output(None)
                sys.argv = ['./interpreter.py', self.args.output]
                from interpreter import Interpreter
                i = Interpreter(False)
                i.load_program()
            else:
                self._ast_gencode()

    def _lexer(self):
        for f in self.args.files:
            LyaCompiler.lexer.lineno = 0
            reset()
            if len(self.args.files) > 1:
                print("Output for file: ", f, file=sys.stderr)
            values = self.readfile(f)
            result = LyaCompiler.lexer.to_token(values)
            print(result)

    def _ast(self):
        for f in self.args.files:
            LyaCompiler.lexer.lineno = 0
            reset()
            if len(self.args.files) > 1:
                print("Output for file: ", f, file=sys.stderr)
            values = self.readfile(f)
            result = LyaCompiler.parser.parseInput(values)
            ast = AST(result)
            ast.program.print_node(0)

    def _ast_walker(self):
        for f in self.args.files:
            LyaCompiler.lexer.lineno = 0
            reset()
            if len(self.args.files) > 1:
                print("Output for file: ", f, file=sys.stderr)
            values = self.readfile(f)
            result = LyaCompiler.parser.parseInput(values)
            ast = AST(result)
            ast.program.visit_node()

    def _ast_gencode(self):
        for f in self.args.files:
            LyaCompiler.lexer.lineno = 0
            reset()
            if len(self.args.files) > 1:
                print("Output for file: ", f, file=sys.stderr)
            values = self.readfile(f)
            result = LyaCompiler.parser.parseInput(values)
            ast = AST(result)
            if self.args.output != '':
                ast.set_output(self.args.output)
            # check semantic errors
            ast.program.visit_node()
            # generate code
            ast.program.generate_code1()

    def readfile(self, name):
        try:
            curr = open(name, "r")
        except:
            raise FileNotFoundError("Could not open file.", name)
        values = curr.read()
        curr.close()
        return values

if __name__ == "__main__":
    m = LyaCompiler()
    m.run()
