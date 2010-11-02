#! /usr/bin/env python 
# -*- coding: utf-8 -*- 

"""
a simple expression calculator
which supports +, -, *, /, ^, brackets, and variables.
requires Python 2.6 or later (for math.isnan).
author: Ji Han
date: July 28, 2009
"""

import sys, re, math


class SimpleCalculator:
    def __init__(self):
        self.clear()

    def clear(self):
        self.variables = dict()

    class Stack(list):
        def empty(self): return not self
        def size(self): return len(self)
        def top(self): return self[len(self)-1]
        def push(self, elem): return list.append(self, elem)
        def pop(self): return list.pop(self)

    ops = { '+': lambda x, y: x + y, '-': lambda x, y: x - y, 
        '*': lambda x, y: x * y, '/': lambda x, y: x / y, 
        '^': lambda x, y: x ** y }

    precedence = { 
        # left bracket has highest pushing precedence
        # and lowest poping precedence
        '(': 0, ')': 0, 
        '=': 1, 
        '+': 2, '-': 2, 
        '*': 3, '/': 3, 
        '^': 4 }

    associativity = { 
        '=': 'right', 
        '+': 'left', '-': 'left', 
        '*': 'left', '/': 'left', 
        '^': 'right' }

    def deref(self, x):
        ret = None
        if x[0]=='numeral':
            ret = x[1]
        elif x[0]=='variable' and x[1] in self.variables:
            ret = self.variables[x[1]]
        else:
            # raise SyntaxError('Invalid reference to ' + str(x[1]))
            ret = float('nan')
        return ret

    def assign(self, var, val):
        if var[0]!='variable':
            raise SyntaxError(str(x[1]) + ' is not an lvalue.')
        self.variables[var[1]] = self.deref(val)
        return var

    def apply(self, op, x, y):
        if op[1] == '=':
            return self.assign(x, y)
        else:
            return ('numeral',
                self.ops[op[1]](self.deref(x),self.deref(y)))

    def float(self, x):
        ret = float('nan')
        try: ret = float(x)
        except ValueError: pass
        finally: return ret

    def lexer(self, string):
        string = re.sub('[ \t\v\f\r\n]+', '', string)
        string = re.sub('([\,\;\=\(\)\+\-\*\/\^])', ' \\1 ', string)
        tokens = string.split()
        tokens.append(';')
        left_bracket_counter = right_bracket_counter = 0
        ret = []
        for token in tokens:
            if len(token)==0:
                pass
            elif token=='(':
                left_bracket_counter += 1
                ret.append(('left-bracket', token))
            elif token==')':
                right_bracket_counter += 1
                if right_bracket_counter > left_bracket_counter:
                    raise SyntaxError("No matching '(' for ')'. ")
                ret.append(('right-bracket', token))
            elif len(token)==1 and token in '+-*/^':
                if token=='-':
                    if not ret or ( 
                        ret[len(ret)-1][0]!='numeral' and 
                        ret[len(ret)-1][0]!='variable'):
                        ret.append(('numeral', 0))
                ret.append(('operator', token))
            elif token=='=':
                ret.append(('assignment', token))
            elif token==';' or token==',':
                if left_bracket_counter != right_bracket_counter:
                    raise SyntaxError('Unbalanced Brackets.')
                left_bracket_counter = right_bracket_counter = 0
                ret.append(('seperator', token))
            elif not math.isnan(self.float(token)):
                ret.append(('numeral', self.float(token)))
            elif token.isalnum() and token[0].isalpha():
                ret.append(('variable', token))
            else:
                raise SyntaxError('Invalid token: ' + token)
        return ret

    def calc(self, string):
        self.tokens = self.lexer(string)
        self.operands = self.Stack()
        self.operators = self.Stack()
        for token in self.tokens:
            if token[0]=='numeral' or token[0]=='variable':
                self.operands.push(token)
            elif token[0]=='left-bracket':
                self.operators.push(token)
            elif token[0]=='right-bracket':
                while self.operators.top()[0]!='left-bracket':
                    op = self.operators.pop()
                    r = self.operands.pop()
                    l = self.operands.pop()
                    self.operands.push(self.apply(op, l, r))
                self.operators.pop()
            elif token[0]=='operator' or token[0]=='assignment':
                while self.operators and \
                      (self.precedence[token[1]] < 
                      self.precedence[self.operators.top()[1]] or 
                      self.precedence[token[1]] == 
                      self.precedence[self.operators.top()[1]] and 
                      self.associativity[token[1]] == 'left'):
                    op = self.operators.pop()
                    r = self.operands.pop()
                    l = self.operands.pop()
                    self.operands.push(self.apply(op, l, r))
                self.operators.push(token)
            elif token[0]=='seperator':
                while self.operators:
                    op = self.operators.pop()
                    r = self.operands.pop()
                    l = self.operands.pop()
                    self.operands.push(self.apply(op, l, r))
                ans = []
                while self.operands:
                    ans.insert(0, self.deref(self.operands.pop()))
                if token[1]==';':
                    for i in ans:
                        print(i),
                    print('\n')


if __name__=='__main__':
    myCalculator = SimpleCalculator()
    for line in sys.stdin:
        myCalculator.calc(line)

