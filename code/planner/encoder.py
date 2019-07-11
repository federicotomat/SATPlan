# coding=utf-8
import translate.pddl as pddl
import utils
from translate import instantiate
from translate import numeric_axiom_rules
from collections import defaultdict
import numpy as np
import os
from satispy import Variable, Cnf
import modifier

# TODO: Scrivere commenti e togliere quelli inutili

class EncoderSAT():

    def __init__(self, task, modifier, horizon):
        self.task = task
        self.modifier = modifier
        self.horizon = horizon

        (self.boolean_fluents,
         self.actions,
         self.numeric_fluents,
         self.axioms,
         self.numeric_axioms) = self.ground()

        # Dai costruttori ho:
        # 1. Boolean fluents
        # 2. Actions
        # 3. Numeric fluents
        # 4. Axioms
        # 5. Numeric axioms --> 1. Axioms by name
        #                       2. Depends on
        #                       3. Axioms by layer

        (self.axioms_by_name,
         self.depends_on,
         self.axioms_by_layer) = self.sort_axioms()

    # A term is ground iff it does not contain variables in it.
    def ground(self):
        """
        Ground action schemas:
        This operation leverages optimizations
        implemented in the parser of the
        Temporal Fast-Downward planner
        """

        (relaxed_reachable, boolean_fluents, numeric_fluents, actions,
         durative_actions, axioms, numeric_axioms,
         reachable_action_params) = instantiate.explore(self.task)

        return boolean_fluents, actions, numeric_fluents, axioms, numeric_axioms

    # A fluent is a condition that can change over time, in FOL, the fluents are represented by predicates having an argument that depend on time.
    # An atom is an expression of the form P(t1...) where P is an n-ary predicate applied to n terms. A literal is an atom ort its negation.
    # A state is a conjuction of ground atoms.

    def sort_axioms(self):
        """
        Returns 3 dictionaries:
        - axioms sorted by name
        - dependencies between axioms
        - axioms sorted by layer
        """

        axioms_by_name = {}
        for nax in self.numeric_axioms:
            axioms_by_name[nax.effect] = nax

        depends_on = defaultdict(list)
        for nax in self.numeric_axioms:
            for part in nax.parts:
                depends_on[nax].append(part)

        axioms_by_layer, _, _, _ = numeric_axiom_rules.handle_axioms(
            self.numeric_axioms)

        return axioms_by_name, depends_on, axioms_by_layer

    def createVariables(self):

        ### Create boolean variables for boolean fluents ###
        self.boolean_variables = defaultdict(dict)
        for step in range(self.horizon + 1):
            for fluent in self.boolean_fluents:
                var_name = utils.makeName(fluent, step)
                self.boolean_variables.update({var_name: Variable(var_name)})

        ### Create propositional variables for actions ids ###
        self.action_variables = defaultdict(dict)
        for step in range(self.horizon):
            for a in self.actions:
                action_name = utils.makeName(a.name, step)
                self.action_variables.update(
                    {action_name: Variable(action_name)})

    def encodeInitialState(self):
        """
        Encode formula defining initial state
        """

        initial = []

        for fact in self.task.init:

            if utils.isBoolFluent(fact):
                if not fact.predicate == '=':
                    if fact in self.boolean_fluents:
                        init = utils.makeName(fact, 0)
                        initial.append((self.boolean_variables[init]))

            else:
                raise Exception(
                    'Initial condition \'{}\': type \'{}\' not recognized'.format(fact, type(fact)))

        # Close-world assumption: if fluent is not asserted
        # in init formula then it must be set to false.

        for var_name in self.boolean_variables:
            var = self.boolean_variables[var_name]
            if not var in initial:
                initial.append(-var)

        for variable in initial:
            if variable is initial[0]:
                encodeInitialState = variable
            else:
                encodeInitialState = encodeInitialState & variable

        return encodeInitialState

    def encodeGoalState(self):
        """
        Encode formula defining goal state
        """

        def encodePropositionalGoals(goal=None):

            propositional_subgoal = []

            # UGLY HACK: we skip atomic propositions that are added
            # to handle numeric axioms by checking names.
            axiom_names = [axiom.name for axiom in self.task.axioms]

            if goal is None:
                goal = self.task.goal

            # Check if goal is just a single atom
            if isinstance(goal, pddl.conditions.Atom):
                if not goal.predicate in axiom_names:

                    goal_var = utils.makeName(goal, self.horizon)
                    propositional_subgoal.append(
                        self.boolean_variables[goal_var])

            # Check if goal is a conjunction
            elif isinstance(goal, pddl.conditions.Conjunction):
                for fact in goal.parts:

                    goal_var = utils.makeName(fact, self.horizon)
                    propositional_subgoal.append(
                        self.boolean_variables[goal_var])

            else:
                raise Exception(
                    'Propositional goal condition \'{}\': type \'{}\' not recognized'.format(goal, type(goal)))

            return propositional_subgoal

        propositional_subgoal = encodePropositionalGoals()

        for variable in propositional_subgoal:
            if variable is propositional_subgoal[0]:
                encodeGoalState = variable
            else:
                encodeGoalState = encodeGoalState & variable
        return encodeGoalState

    # Qua ritorno un'unica formula oppure una formula per azione?

    def encodeActions(self):
        """
        Encode action constraints:
        each action variable implies its preconditions
        and effects
        """

        actions = []

        for step in range(self.horizon):
            for action in self.actions:
                # Ho bisogno di due liste, rispettivamente per ADD e per DEL, ovvero per tenere i fluent che vengono aggiunti
                # da una determinata azione e quelli che vengono rimossi, per ogni azione

                # Devo farlo per ogni action, ho il nome:
                action_variable = self.action_variables[utils.makeName(
                    action.name, step)]

                precondition_list = list()
                # Encode preconditions
                for pre in action.condition:
                    pre_name = utils.makeName(pre, step)
                    if pre_name in self.boolean_variables:
                        # Ho una lista di "formule" di precondition
                        if isinstance(pre, pddl.conditions.NegatedAtom):
                            precondition_list.append(
                                -(self.boolean_variables[pre_name]))
                        else:
                            precondition_list.append(
                                self.boolean_variables[pre_name])

                add_list = list()
                # Encode add effects (conditional supported)
                for add in action.add_effects:
                    # Aggiunto la successiva
                    add_name = utils.makeName(add[1], step + 1)
                    if add_name in self.boolean_variables:
                        # Ho una lista di "formule" di add
                        add_list.append(self.boolean_variables[add_name])

                del_list = list()
                # Encode delete effects (conditional supported)
                for de in action.del_effects:
                    del_name = utils.makeName(de[1], step + 1)
                    if del_name in self.boolean_variables:
                        del_list.append(-(self.boolean_variables[del_name]))

                # TODO: ridurre questi step
                for variable in precondition_list:
                    if variable is precondition_list[0]:
                        precondition_formula = variable
                    else:
                        precondition_formula = precondition_formula & variable

                for variable in add_list:
                    if variable is add_list[0]:
                        add_formula = variable
                    else:
                        add_formula = add_formula & variable

                for variable in del_list:
                    if variable is del_list[0]:
                        del_formula = variable
                    else:
                        del_formula = del_formula & variable

                exp = (action_variable >> (
                    precondition_formula & add_formula & del_formula))
                actions.append(exp)

        for subformula in actions:
            if subformula is actions[0]:
                encodeActions = subformula
            else:
                encodeActions = encodeActions & subformula
        return encodeActions

    def encodeFrame(self):
        """
        Encode explanatory frame axioms
        """

        frame = []
        for step in range(self.horizon):
            # Encode frame axioms for boolean fluents
            for fluent in self.boolean_fluents:

                fluent_name = utils.makeName(fluent, step)
                fluent_i = self.boolean_variables[fluent_name]

                fluent_name_suc = utils.makeName(fluent, step + 1)
                fluent_i_plus_one = self.boolean_variables[fluent_name_suc]

                for action in self.actions:
                    control = False
                    for add in action.add_effects:
                        add_name = utils.makeName(add[1], step)
                        if add_name in self.boolean_variables:
                            if fluent_i == self.boolean_variables[add_name]:
                                if control is False:
                                    subformula1 = self.action_variables[utils.makeName(
                                        action.name, step)]
                                    control = True
                                else:
                                    subformula1 = subformula1 | self.action_variables[utils.makeName(
                                        action.name, step)]

                    control = False
                    for de in action.del_effects:
                        del_name = utils.makeName(de[1], step)
                        if add_name in self.boolean_variables:
                            if fluent_i == self.boolean_variables[del_name]:
                                if control is False:
                                    subformula2 = self.action_variables[utils.makeName(
                                        action.name, step)]
                                    control = True
                                else:
                                    subformula2 = subformula2 | self.action_variables[utils.makeName(
                                        action.name, step)]

                exp = (((fluent_i & -(fluent_i_plus_one)) >> subformula1)
                       & ((-(fluent_i) & fluent_i_plus_one) >> subformula2))
                frame.append(exp)

        for subformula in frame:
            if subformula is frame[0]:
                encodeFrame = subformula
            else:
                encodeFrame = encodeFrame & subformula

        return encodeFrame

    def encodeAtLeastOne(self):

        atleastone = []
        # TODO: Controllare questo passagio, ha senso spezzarli? Non cambia nulla, posso droppare
        action_set = set()

        for act in self.action_variables:
            action_name = act.split('@', 1)
            action_set.add(action_name[0])

        # Rimuovo i duplicati dal set di actions, qua ho delle stringhe, devo farci un dizionario di formule
        action_list = list(set(action_set))

        for step in range(self.horizon):
            for act in action_list:
                action_name = utils.makeName(act, step)
                if action_name in self.action_variables:
                    if act is action_list[0]:
                        variable = self.action_variables[action_name]
                    else:
                        variable = variable | self.action_variables[action_name]
            atleastone.append(variable)

        for subformula in atleastone:
            if subformula is atleastone[0]:
                encodeAtLeastOne = subformula
            else:
                encodeAtLeastOne = encodeAtLeastOne & subformula

        return encodeAtLeastOne

    def encodeExecutionSemantics(self):
        if self.modifier is True:
            return modifier.Modifier().encodeParallelModifier(self.horizon, self.actions, self.boolean_variables, self.action_variables)
        else:
            return modifier.Modifier().encodeLinearModifier(self.horizon, self.actions, self.action_variables)

    def encode(self):

        # Create variables
        self.createVariables()

        ### Start encoding formula ###

        formula = defaultdict(list)

        # Encode initial state axioms

        formula['initial'] = self.encodeInitialState()

        # Encode goal state axioms

        formula['goal'] = self.encodeGoalState()

        # Encode universal axioms

        formula['actions'] = self.encodeActions()

        # Encode explanatory frame axioms

        formula['frame'] = self.encodeFrame()

        # Encode execution semantics (lin/par)

        formula['sem'] = self.encodeExecutionSemantics()

        # Encode at least one axioms

        formula['alo'] = self.encodeAtLeastOne()

        formulaToSolve = formula['initial'] & formula['actions'] & formula[
            'frame'] & formula['alo'] & formula['goal'] & formula['sem']
        return formulaToSolve

    def dump(self):
        print('Dumping encoding')
        raise Exception('Not implemented yet')
