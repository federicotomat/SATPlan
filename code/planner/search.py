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
        self.found = False

# The linear planning work on one goal until completely solved before moving on to the next goal. STRIPS is an example of linear planner
# Noi non dobbiamo fare uno STRIPS ma dobbiamo solo risolvere la formula e ritorna un'assegnazione (uso un SAT solver), è corretto?

class LinearSearch(Search):

    def do_search(self): # Trovare percorso fra Initial e Goal

        ## Override initial horizon, non capisco l'assegnazione qua, se lo ho già da encode (?)
        self.horizon = 1

        print('Start linear search')
        ## Implement linear search here and return a plan

        solver = Minisat()
        solution = solver.solve(self.encoder)
        
        if solution.success:
            print("The expression can be satisfied...")
            self.found == True
        else:
            print("The expression cannot be satisfied, it's UNSAT...")
        
        '''
        ## Must return a plan object when plan is found 
        planning = plan.Plan(solution, self.encoder)
        return planning
        '''