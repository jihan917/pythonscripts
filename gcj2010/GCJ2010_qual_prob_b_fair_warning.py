#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
solution to Google Code Jam 2010, Qualification Round, Problem B.
author: Ji Han
date: May 8, 2010
"""

import sys, operator

def gcd(a, b):
    if a == 0: return b
    return gcd(b % a, a)

def diff(L):
    return map(operator.sub, L[1:], L[:-1])

def start():
    for i in map(lambda x:x+1, range(long(sys.stdin.readline()))):
        L = map(long, sys.stdin.readline().split())
        N, TS = L[0], sorted(L[1:])
        T = reduce(gcd, diff(TS), 0)
        print "Case #%d: %d" % (i, 0 if TS[0] % T == 0 else T - TS[0] % T)

if __name__=='__main__': 
        start()

