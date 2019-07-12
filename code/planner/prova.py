# coding=utf-8
from satispy import Variable, Cnf
from satispy.solver import Minisat
import sys

if __name__ == '__main__':

    stringa = "ciao@1"
    [x, y] = stringa.split("@")
    print(x)
    print(y)
    v1 = Variable("v1")
    v2 = Variable("v2")
    v3 = Variable("v3")

    exp = v1 >> v2 >> v3
    exp2 = exp & v1

    solver = Minisat()
    solution = solver.solve(exp2)

    if solution.success:
        print("The expression can be satisfied...")
    else:
        print("The expression cannot be satisfied, it's UNSAT...")

    print(exp2)
