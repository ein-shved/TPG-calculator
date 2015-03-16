#!/usr/bin/python
# coding: utf

from sys import stdin
import sys
import tpg
import itertools

if stdin.isatty():
    import readline

def make_op(s):
    return {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x/y,
        '&': lambda x,y: x&y,
        '|': lambda x,y: x|y,
    }[s]

class Vector(list):
    def __init__(self, *argp, **argn):
        list.__init__(self, *argp, **argn)
    def __init__(self, vector):
        list.__init__(self, vector)

    def __str__(self):
        return "[" + " ".join(str(c) for c in self) + "]"

    def __op(self, a, op):
        try:
            return self.__class__(op(s,e) for s,e in zip(self, a))
        except TypeError:
            return self.__class__(op(c,a) for c in self)

    def __add__(self, a): return self.__op(a, lambda c,d: c+d)
    def __sub__(self, a): return self.__op(a, lambda c,d: c-d)
    def __div__(self, a): return self.__op(a, lambda c,d: c/d)
    def __mul__(self, a):
        m_a = None;
        m_s = self.to_matrix();
        if m_s != None:
            m_a = a.to_matrix();
        if m_a != None:
            return m_s.__mul__(m_a);
        return self.__op(a, lambda c,d: c*d)

    def __and__(self, a):
        try:
            return reduce(lambda s, (c,d): s+c*d, zip(self, a), 0)
        except TypeError:
            return self.__class__(c and a for c in self)

    def __or__(self, a):
        try:
            return self.__class__(itertools.chain(self, a))
        except TypeError:
            return self.__class__(c or a for c in self)
    def to_matrix(self):
        try:
            m = Matrix(self);
            return m;
        except TypeError:
            return None

class Matrix(Vector):
    def __init__(self, vector):
        Vector.__init__(self, vector)
        self.n = len(self)
        self.m = len(self[0])
        for l in self:
            self.m = min(self.m, len(l))
            for v in l:
                if not isinstance(v, int):
                    raise TypeError

    def __mul__(self, other):
        if self.m != other.n:
            return Vector.__mul__(self, other)
        l= [[sum(a*b for a,b in zip(self_row,other_col)) for other_col in zip(*other)] for self_row in self]
        return Vector(Vector(v) for v in l)


class Calc(tpg.Parser):
    r"""

    separator spaces: '\s+' ;
    separator comment: '#.*' ;

    token fnumber: '\d+[.]\d*' float ;
    token number: '\d+' int ;
    token op1: '[|&+-]' make_op ;
    token op2: '[*/]' make_op ;
    token id: '\w+' ;

    START/e -> Operator $e=None$ | Expr/e | $e=None$ ;
    Operator -> Assign ;
    Assign -> id/i '=' Expr/e $Vars[i]=e$ ;
    Expr/t -> Fact/t ( op1/op Fact/f $t=op(t,f)$ )* ;
    Fact/f -> Atom/f ( op2/op Atom/a $f=op(f,a)$ )* ;
    Atom/a ->   Vector/a
              | id/i ( check $i in Vars$ | error $"Undefined variable '{}'".format(i)$ ) $a=Vars[i]$
              | fnumber/a
              | number/a
              | '\(' Expr/a '\)' ;
    Vector/$Vector(a)$ -> '\[' '\]' $a=[]$ | '\[' Atoms/a '\]' ;
    Atoms/v -> Expr/a Atoms/t $v=[a]+t$ | Expr/a $v=[a]$ ;

    """

calc = Calc()
Vars={}
if stdin.isatty():
    PS1='--> '
else:
    PS1=''

Stop=False
while not Stop:
    try:
        line = raw_input(PS1)
    except EOFError:
        break
    try:
        res = calc(line)
    except tpg.Error as exc:
        print >> sys.stderr, exc
        res = None
    if res != None:
        if stdin.isatty():
            print res
        else:
            print line + ' >> ' + str(res)
if stdin.isatty():
    print
