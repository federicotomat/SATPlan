# coding=utf-8
from planner import plan
from planner import encoder
import utils
from satispy import Variable, Cnf
from satispy.solver import Minisat

class Search():
    def __init__(self, encoder, initial_horizon):
        self.encoder = encoder 
        self.horizon = initial_horizon
        self.found = False

class LinearSearch(Search):

    ## Find the path that joins start and goal, returns the list of actions ##
    def do_search(self):

        print('Start linear search...')
        solver = Minisat()
        solution = solver.solve(self.encoder.do_encode())
        solution_list = list()

        if solution.error != False:
            print("Error:")
            print(solution.error)
        elif solution.success:
            print("The expression can be satisfied...")
            for action in self.encoder.action_variables.values():
                if solution.varmap[action]:
                    [action, step] = str(action).split("@")
                    solution_list.append([int(step), action])
            self.found = True
            planning = plan.Plan(sorted(solution_list), self.horizon)
            return planning
        else:
            print("The expression cannot be satisfied, it's UNSAT...")
            return False
