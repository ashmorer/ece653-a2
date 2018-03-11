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

from __future__ import print_function

import wlang.ast
import cStringIO
import sys
import copy

import z3

class SymState(object):
    def __init__(self, solver = None):
        # environment mapping variables to symbolic constants
        self.env = dict()
        # path condition
        self.path = list ()
        self._solver = solver
        if self._solver is None:
            self._solver = z3.Solver ()

        # true if this is an error state
        self._is_error = False

    def add_pc (self, *exp):
        """Add constraints to the path condition"""
        self.path.extend (exp)
        self._solver.append (exp)
        
    def is_error (self):
        return self._is_error
    def mk_error (self):
        self._is_error = True
        
    def is_empty (self):
        """Check whether the current symbolic state has any concrete states"""
        res = self._solver.check ()
        return res == z3.unsat

    def pick_concerete (self):
        """Pick a concrete state consistent with the symbolic state.
           Return None if no such state exists"""
        res = self._solver.check ()
        if res <> z3.sat:
            return None
        model = self._solver.model ()
        import wlang.int
        st = wlang.int.State ()
        for (k, v) in self.env.items():
            st.env [k] = model.eval (v)
        return st
        
    def fork(self):
        """Fork the current state into two identical states that can evolve separately"""
        child = SymState ()
        child.env = dict(self.env)
        child.add_pc (*self.path)
        
        return (self, child)
    
    def __repr__ (self):
        return str(self)
        
    def to_smt2 (self):
        """Returns the current state as an SMT-LIB2 benchmark"""
        return self._solver.to_smt2 ()
    
        
    def __str__ (self):
        buf = cStringIO.StringIO ()
        for k, v in self.env.iteritems():
            #print(str(k), ": ", str(v), "\n")
            buf.write (str (k))
            buf.write (': ')
            buf.write (str (v))
            buf.write ('\n')
        buf.write ('pc: ')
        buf.write (str (self.path))
        if(self._is_error):
            buf.write('\nUNSAT or divergent\n')
        buf.write ('\n')
            
        return buf.getvalue ()
                   
class SymExec (wlang.ast.AstVisitor):
    def __init__(self):
        self.i = 0
        pass

    def run (self, ast, state):
        #print ("running SymExec.run()")
        ## set things up and 
        ## call self.visit (ast, state=state)
        #state = True
        #print ("state=", state)
        return self.visit(ast, state=state)

    def visit_IntVar (self, node, *args, **kwargs):
        #print ("visiting IntVar")
        #print ("node=", node)
        #print ("args=", args)
        #print ("kwargs=", kwargs)
        #print ("kwargs['state'].env=", kwargs['state'].env)
        #print ("node.name=" ,node.name)
        if node.name in kwargs['state'].env:
            return kwargs['state'].env [node.name]
        else:   
            kwargs['state'].env[node.name] = z3.Int(node.name+str(self.i))
            self.i = self.i+1
            #print ("created var: ", kwargs['state'])
            return kwargs['state'].env[node.name]
            
    def visit_BoolConst(self, node, *args, **kwargs):
        return z3.BoolVal (node.val)

    def visit_IntConst (self, node, *args, **kwargs):
        #print ("visiting int_const")
        #print ("node.val=", node.val, "type(node.val)=", type(node.val))
        #if type(node.val)!=int:
        #    print ("wtf...")
        #    return node.val
        #else:
        #    print ("a classic int")
        return z3.IntVal (node.val)
    
    def visit_RelExp (self, node, *args, **kwargs):
        #print ("visiting relExp")
        #print ("node=", node)
        #print ("args=", args)
        #print ("kwargs=", kwargs)
        lhs = self.visit(node.arg(0), *args, **kwargs)
        rhs = self.visit(node.arg(1), *args, **kwargs)
        if node.op == '<=': return lhs <= rhs
        if node.op == '<':  return lhs <  rhs
        if node.op == '=':  return lhs == rhs
        if node.op == '>':  return lhs >  rhs
        if node.op == '>=': return lhs >= rhs
        assert False 

    def visit_BExp (self, node, *args, **kwargs):
        #print ("visiting BExp")
        kids = [self.visit (a, *args, **kwargs) for a in node.args]
        
        if node.op == 'not':
            assert node.is_unary ()
            assert len (kids) == 1
            return z3.Not( kids[0])
        
        result = None
        if node.op == 'and':
            result = z3.And(kids)
        elif node.op == 'or':
            result = z3.Or(kids)

        assert result is not None
        #Need to return an abstract z3 expression
        return result
        
    def visit_AExp (self, node, *args, **kwargs):
        kids = [self.visit (a, *args, **kwargs) for a in node.args]

        fn = None
        base = None

        if node.op == '+':
            fn = lambda x, y: x + y
            
        elif node.op == '-':
            fn = lambda x, y: x - y

        elif node.op == '*':
            fn = lambda x, y: x * y

        elif node.op == '/':
            fn = lambda x, y : x / y
            
        
        assert fn is not None
        return reduce (fn, kids)
        
    def visit_SkipStmt (self, node, *args, **kwargs):
        #print ("visiting a skip statement")
        return [kwargs['state']]
    
    def visit_PrintStateStmt (self, node, *args, **kwargs):
        #print ("visiting print_stmt")
        #print (kwargs['state'])
        return [kwargs['state']]

    def visit_AsgnStmt (self, node, *args, **kwargs):
        #print ("visiting assign_stmt")
        st = kwargs['state']
        st.env [node.lhs.name] = self.visit (node.rhs, *args, **kwargs)
        return [st]

    def visit_IfStmt (self, node, *args, **kwargs):
        #print("visiting if stmt")
        #print ("node=", node)
        #print ("args=", args)
        #print ("kwargs=", kwargs)
        cond = self.visit (node.cond, *args, **kwargs)
        (then, els) = kwargs['state'].fork()
        #print(type(then))
        then.add_pc(cond)
        els.add_pc(z3.Not(cond))
        if not then.is_empty():
            #print ("then branch possible")
            then =  self.visit (node.then_stmt, *args, state=then)
        else:
            #print ("then branch impossible")
            then.mk_error()
            then = [then]
            #the then path is infeasible, mark as such and ignore contents
        if not els.is_empty():
            #print ("else branch possible")
            if node.has_else ():
                els =  self.visit (node.else_stmt, *args, state=els)
            else:
                els = [els]
        else:
            #print ("else branch impossible")
            els.mk_error()
            els = [els]
            #as before, skipping then branch infeasible, mark as such and igonore this branch.
        #print ("returning then,els=\n", then,"\n\n",   els)
        #print(type(then), type(els))
        result = []
        result.extend(then)
        result.extend(els)
        #print("\n\n\nENDING IF STATEMENT. Returning result=", result)
        return result
    
    def visit_WhileStmt (self, node, *args, **kwargs):
        #print("visiting while stmt")
        #print("node=", node)
        #print("args=", args)
        #print("While kwargs=", kwargs)
        cond = self.visit (node.cond, *args, **kwargs)
        (run, noRun) = kwargs['state'].fork()
        run.add_pc(cond)
        noRun.add_pc(z3.Not(cond))
        if not run.is_empty():
            # count how many executions we're at
            if('level'+str(node) in kwargs):
                if(kwargs['level'+str(node)]==10):
                    run.mk_error()
                    return [run]
                else:
                    kwargs['level'+str(node)] = kwargs['level'+str(node)]+1
            else:
                kwargs['level'+str(node)] = 1

            #Now that we've done bookkeeping, execute body:
            states = self.visit (node.body, *args, **kwargs)
            #states is now array of symbolic states
            
            # execute the loop again
            result = []
            for st in states:
                kwargs['state'] = st
                result.extend(self.visit (node, *args, **kwargs))
            run = result
        else:
            # loop condition is infeasible, mark as such and ignore contents
            run.mk_error()
            run = [run]
        if not noRun.is_empty():
            #possible to skip running
            noRun = [noRun]
        else:
            #not possible to skip running
            noRun.mk_error()
            noRun = [noRun]
        result = []
        result.extend(run)
        result.extend(noRun)
        return result

    def visit_AssertStmt (self, node, *args, **kwargs):
        ## Don't forget to print an error message if an assertion might be violated
        #print("visiting assert stmt")
        #print ("node=", node)
        #print ("args=", args)
        #print ("kwargs=", kwargs)
        #cond = self.visit (node.cond, *args, **kwargs)
        #if not cond:
        #    assert False, 'Assertion error: ' + str (node)
        #return kwargs['state']
        #^^^Old code^^^

        #Now we need to check if the symbolic state is compatible with not the assertion
        
        cond = self.visit(node.cond, *args, **kwargs)
        solver = kwargs['state']._solver
        solver.push()
        solver.add(z3.Not(cond))
        print (solver)
        if solver.check()==z3.unsat:
            #assert succeeds
            print ("assert verified")
            solver.pop()
        else:
            #assert fails
            print ("assert failed")
            mdl = solver.model()
            print ("mdl: ", mdl)
            assert False, 'Assertion error: ' + str(node)
        return [kwargs['state']]
        
    def visit_AssumeStmt (self, node, *args, **kwargs):
        #print ("visiting assume statement")
        cond = self.visit(node.cond, *args, **kwargs)
        #print("Resolved the condition: cond=", cond)
        kwargs['state'].add_pc(cond)
        #print("successfully added cond to state's pc")
        #print (kwargs['state'])
        return [kwargs['state']]

    def visit_HavocStmt (self, node, *args, **kwargs):
        #print("visiting havoc stmt")
        #print ("node=", node)
        #print ("args=", args)
        #print ("kwargs=", kwargs)
        st = kwargs['state']
        for v in node.vars:
            st.env[v.name] = z3.Int(v.name+str(self.i))
            #print (v.name, " = ", st.env[v.name])
            self.i= self.i+1
        return [st]

    def visit_StmtList (self, node, *args, **kwargs):
        #print ("visiting a statement list")
        #print ("node=", node)
        #print ("args=", args)
        #print ("**kwargs=", kwargs)
        stateList = [kwargs['state']]
        stateListNext = []
        nkwargs = dict (kwargs)
        for stmt in node.stmts:
            for st in stateList:
                nkwargs ['state'] = st
                #print("Examining st=", st, " on stmt=", stmt)
                visit = self.visit(stmt, *args, **nkwargs)
                stateListNext.extend(visit)
                #Be careful, st may be a list of statements now
            stateList = stateListNext
            print ("stateList length is ", len(stateList), " after stmt=", stmt)
            stateListNext = []
        return stateList
        
def _parse_args ():
    import argparse
    ap = argparse.ArgumentParser (prog='sym',
                                  description='WLang Interpreter')
    ap.add_argument ('in_file', metavar='FILE', help='WLang program to interpret')
    args = ap.parse_args ()
    return args
    
def main ():
    args = _parse_args ()
    print ('args=')
    print (args)
    ast = wlang.ast.parse_file (args.in_file)
    print ('ast=')
    print (ast)
    st = SymState ()
    sym = SymExec ()

    states = sym.run (ast, st)
    if states is None:
        print ('[symexec]: no output states')
    else:
        count = 0
        for out in states:
            count = count + 1
            print ('[symexec]: symbolic state reached')
            print (out)
        print ('[symexec]: found', count, 'symbolic states')
    return 0

if __name__ == '__main__':
    sys.exit (main ())
                    
