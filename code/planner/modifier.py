from satispy import Variable, Cnf
import utils

class EncodeModifier():

    def __init__(self, horizon, actions, boolean_variables, action_variables):
        self.horizon = horizon
        self.actions = actions
        self.boolean_variables = boolean_variables
        self.action_variables = action_variables

    ## Encode Linear Modifier ##
    def encode_linear_modifier(self):

        mutexes = []

        for step in range(self.horizon):
            for a1 in self.actions:
                for a2 in self.actions:
                    if not a1.name == a2.name:
                        mutexes.append(-(self.action_variables[utils.makeName(a1.name, step)]) | -(self.action_variables[utils.makeName(a2.name, step)]))

        return utils.make_formula_and(mutexes)

    ## Encode Parallel Modifier ##
    def encode_parallel_modifier(self):

        mutexes = []
        for step in range(self.horizon):
            for a1 in self.actions:
                for a2 in self.actions:
                    if not a1.name == a2.name:

                        preaction_a1 = set()
                        for pre in a1.condition:
                            preaction_a1.add(
                                self.boolean_variables[utils.makeName(pre, step)])

                        preaction_a2 = set()
                        for pre in a2.condition:
                            preaction_a2.add(
                                self.boolean_variables[utils.makeName(pre, step)])

                        delection_a1 = set()
                        for de in a1.del_effects:
                            delection_a1.add(
                                self.boolean_variables[utils.makeName(de[1], step)])

                        delection_a2 = set()
                        for de in a2.del_effects:
                            delection_a2.add(
                                self.boolean_variables[utils.makeName(de[1], step)])

                        if preaction_a1.intersection(delection_a2) or preaction_a2.intersection(delection_a1):
                            mutexes.append(-(self.action_variables[utils.makeName(a1.name, step)]) | -(
                                self.action_variables[utils.makeName(a2.name, step)]))

        return utils.make_formula_and(mutexes)
