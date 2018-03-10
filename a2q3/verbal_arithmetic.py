import z3
## See https://en.wikipedia.org/wiki/Verbal_arithmetic
## cute: http://mathforum.org/library/drmath/view/60417.html

vars = dict()
def _mk_int_var (x):
    if x not in vars:
        vars[x] = z3.Int (str(x))
    return vars[x]

def mk_var (x):
    return _mk_int_var (x)

def get_vars ():
    return vars.values ()


def solve (s1, s2, s3):
    global vars
    vars = dict()
    for c in s1:
        mk_var(c)
    for c in s2:
        mk_var(c)
    for c in s3:
        mk_var(c)

    
    #now that we have vars, we need to use z3. Basic rules for digits
    s = z3.Solver()
    s.add(z3.Distinct(get_vars()))
    for v in get_vars():
        s.add(0<=v)
        s.add(v<=9)

    #The one rule that is different for no-carry
    case1 = vars[s1[len(s1)-1]]+vars[s2[len(s2)-1]] == vars[s3[len(s3)-1]]
    case2 = vars[s1[len(s1)-1]]+vars[s2[len(s2)-1]] == vars[s3[len(s3)-1]]+10
    s.add(z3.Or(case1, case2))
    
    #And now some rules for the strings themselves (with carry)
    for i in range(2, len(s3)+1):
        #add rule(s) for this constraint
        top = 0
        mid = 0
        bottom = 0
        if len(s1)-i>=0:
            top = vars[s1[len(s1)-i]]
        if len(s2)-i>=0:
            mid = vars[s2[len(s2)-i]]
        bottom = vars[s3[len(s3)-i]]
        #add rule for top+mid=bottom digit...need to consider carry
        carSum1 = 0
        carSum2 = 0
        if len(s1)-i+1>=0:
            carSum1 = vars[s1[len(s1)-i+1]]
        if len(s2)-i+1>=0:
            carSum2 = vars[s2[len(s2)-i+1]]
        #add rule for top+mid+(if carSum, 1, else 0)=bottom (or bottom +10)
        rule = z3.If(carSum1+carSum2>=10, z3.Or(top+mid+1==bottom, top+mid+1==bottom+10), z3.Or(top+mid==bottom, top+mid==bottom+10))
        s.add(rule)
        

    #Check if s1 or s2 are longer than s3. If so, assert all those digits are zero.
    for i in range(0, len(s1)-len(s3)):
        s.add(vars[s1[i]]==0)
    for i in range(0, len(s2)-len(s3)):
        s.add(vars[s2[i]]==0)
    #replace with output None or (val1,val2,val3)
    if s.check()==z3.sat:
        sol = s.model()
        s1sol = ""
        s2sol = ""
        s3sol = ""
        for c in s1:
            s1sol += str( (sol[vars[c]]) )
        for c in s2:
            s2sol += str((sol[vars[c]]))
        for c in s3:
            s3sol += str((sol[vars[c]]))
        print_sum(s1, s2, s3)
        print_sum(s1sol, s2sol, s3sol)
        return (s1sol, s2sol, s3sol)
    else:
        print_sum(s1,s2,s3)
        print "unsat"
        return None
    pass

def print_sum (s1, s2, s3):
    s1 = str(s1)
    s2 = str(s2)
    s3 = str(s3)
    rjust = max(len(s1)+1, len(s2)+1, len(s3)+1)
    print
    print s1.rjust (rjust)
    print '+'
    print s2.rjust (rjust)
    print ('-'*(rjust))
    print s3.rjust (rjust)
    
def puzzle (s1, s2, s3):
    print_sum (s1, s2, s3)
    res = solve (s1, s2, s3)
    if res is None:
        print 'No solution'
    else:
        print 'Solution:'
        print_sum (res[0], res[1], res[2])
        
if __name__ == '__main__':
    puzzle ('SEND', 'MORE', 'MONEY')
