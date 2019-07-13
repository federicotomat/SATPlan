# coding=utf-8
from satispy import Variable, Cnf
from satispy.solver import Minisat
import sys

if __name__ == '__main__':

    stringa = "ciao@1"
    [x, y] = stringa.split("@")
    print(x)
    print(y)
    v1 = Variable("ciao@1")
    v2 = Variable("ciao@2")
    v3 = Variable("ciao@3")

    a1 = Variable("a@1")
    a2 = Variable("a@2")
    a3 = Variable("a@3")

    exp = v1 >> v2 >> v3 & a1 >> a2 >> a3
    exp2 = exp & v1

    solver = Minisat()
    solution = solver.solve(exp2)

    if solution.success:
        print("The expression can be satisfied...")
        if solution.varmap[v1] is True:
            print(solution.varmap[v1])
        if solution.varmap[v2] is True:
            print(solution.varmap[v2])
        if solution.varmap[v3] is True:
            print(solution.varmap[v3])
    else:
        print("The expression cannot be satisfied, it's UNSAT...")
