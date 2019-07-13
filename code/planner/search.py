# coding=utf-8
from planner import plan
from planner import encoder
import utils
from satispy import Variable, Cnf 
from satispy.solver import Minisat

class Search():
    def __init__(self, encoder, initial_horizon):
        self.encoder = encoder # Contiene il dizionario di formule
        self.horizon = initial_horizon
        # self.found = False

# The linear planning work on one goal until completely solved before moving on to the next goal. STRIPS is an example of linear planner
# Noi non dobbiamo fare uno STRIPS ma dobbiamo solo risolvere la formula e ritorna un'assegnazione (uso un SAT solver), è corretto?

class LinearSearch(Search):

    def do_search(self): # Trovare percorso fra Initial e Goal

        print('Start linear search')
        ## Implement linear search here and return a plan

        solver = Minisat()
        solution = solver.solve(self.encoder)
        solution_list = list()

        if solution.error != False:
            print("Error:")
            print(solution.error)
        elif solution.success:
            print("The expression can be satisfied...")
            ## Must return a plan object when plan is found
            for action in self.encoder.action_variables.keys():
                if solution.varmap[action] is True:
                    solution_list.append(utils.getStep(action), utils.getAct(action))
                else:
                    continue
                
            print(solution_list)
            planning = plan.Plan(solution, self.horizon)
            return planning
        else:
            print("The expression cannot be satisfied, it's UNSAT...")
            return False
