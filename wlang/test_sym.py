# The MIT License (MIT)
# Copyright (c) 2016 Arie Gurfinkel

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unittest
import wlang.ast as ast
import wlang.sym

class TestSym (unittest.TestCase):
    def test_one (self):
        prg1 = "havoc x; assume x > 10; assert x > 15"
        ast1 = ast.parse_string (prg1)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast1, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 1)
    def test_two (self):
        prg2 = "assume x > 100; assert x > 15"
        ast2 = ast.parse_string (prg2)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast2, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 1)
    def test_three (self):
        prg1 = "assert true; if ((7>=3 and 4>=4) or not true) then x:=10 else print_state"
        ast1 = ast.parse_string (prg1)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast1, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 2)
    def test_four(self):
        prg1 = "x:= (1+2)-(2*(6/3)); skip; print_state"
        ast1 = ast.parse_string (prg1)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast1, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 1)
    def test_five(self):
        prg1 = "assume x=2; if x>2 then skip; if x=2 then skip else skip; if not (x = 2) then skip else skip"
        ast1 = ast.parse_string (prg1)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast1, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 2*2*2)
    def test_six (self):
        prg1 = "assume x<20; while x>0 do x := x-1; print_state; while false do skip"
        ast1 = ast.parse_string (prg1)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast1, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 11*2)
    def test_seven (self):
        prg1 = "x:=10; while x=10 do x:=11"
        ast1 = ast.parse_string (prg1)
        sym = wlang.sym.SymExec ()
        st = wlang.sym.SymState ()
        out = [s for s in sym.run (ast1, st)]
        print("len(out)=", len(out))
        self.assertEquals (len(out), 3)
        
                
        
