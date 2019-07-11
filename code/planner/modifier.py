from satispy import Variable, Cnf
import utils

# TODO: Per il momento sono banalmente delle funzioni, bisogna riorganizzare
class Modifier():

    def encodeLinearModifier(self, horizon, actions, action_variables):
        self.horizon = horizon
        self.actions = actions
        self.action_variables = action_variables
        mutexes = []

        for a1 in actions:
            for a2 in actions:
                if not a1.name == a2.name:
                    for step in range(self.horizon):
                        mutexes.append(-(self.action_variables[utils.makeName(a1.name, step)]) | -(
                            self.action_variables[str(a2.name) + "@" + str(step)]))

        for formula in mutexes:
            if formula is mutexes[0]:
                sem = formula
            else:
                sem = sem & formula
        print(sem)
        return sem

    ## Lo uso per fare il Linear Modifier ##
    def encodeParallelModifier(self, horizon, actions, boolean_variables, action_variables):
        """
        Compute mutually exclusive actions using the conditions
        we saw during lecture
        """
        self.horizon = horizon
        self.actions = actions
        self.boolean_variables = boolean_variables
        self.action_variables = action_variables
        mutexes = []
        for a1 in self.actions:
            for a2 in self.actions:
                if not a1.name == a2.name:
                    for step in range(self.horizon):

                        preaction_a1 = set()
                        for pre in a1.condition:
                            preaction_a1.add(
                                self.boolean_variables[str(pre) + "@" + str(step)])

                        preaction_a2 = set()
                        for pre in a2.condition:
                            preaction_a2.add(
                                self.boolean_variables[str(pre) + "@" + str(step)])

                        delection_a1 = set()
                        for de in a1.del_effects:
                            delection_a1.add(
                                self.boolean_variables[str(de[1]) + "@" + str(step)])

                        delection_a2 = set()
                        for de in a2.del_effects:
                            delection_a2.add(
                                self.boolean_variables[str(de[1]) + "@" + str(step)])

                        if preaction_a1.intersection(delection_a2) or preaction_a2.intersection(delection_a1):
                            mutexes.append(-(self.action_variables[str(a1.name) + "@" + str(step)]) | -(
                                self.action_variables[str(a2.name) + "@" + str(step)]))

        for formula in mutexes:
            if formula is mutexes[0]:
                sem = formula
            else:
                sem = sem & formula
        return sem
