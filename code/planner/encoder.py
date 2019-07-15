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

class EncoderSAT():
    
    def __init__(self, task, modifier, horizon):
        """
        From the translate you have:
        - Boolean fluents
        - Actions
        - Numeric fluents
        - Axioms
        - Numeric axioms --> - Axioms by name
                             - Depends on
                             - Axioms by layer
        """

        self.task = task
        self.modifier = modifier
        self.horizon = horizon

        (self.boolean_fluents,
         self.actions,
         self.numeric_fluents,
         self.axioms,
         self.numeric_axioms) = self.ground()

        (self.axioms_by_name,
         self.depends_on,
         self.axioms_by_layer) = self.sort_axioms()

    ## A term is ground iff it does not contain variables in it.
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

    ## A fluent is a condition that can change over time.
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


    ## Create boolean variables for boolean fluents and propositional variables for actions ids.
    def createVariables(self):
        """
        Allocate 2 dictionaries:
        - boolean variables
        - action variable
        """

        self.boolean_variables = defaultdict(dict)
        for step in range(self.horizon + 1):
            for fluent in self.boolean_fluents:
                var_name = utils.makeName(fluent, step)
                self.boolean_variables.update({var_name: Variable(var_name)})

        self.action_variables = defaultdict(dict)
        for step in range(self.horizon):
            for a in self.actions:
                action_name = utils.makeName(a.name, step)
                self.action_variables.update(
                    {action_name: Variable(action_name)})

    ##  Encode formula defining initial state
    def encodeInitialState(self):
        """
        Returns the formula that encode the initial state (Inital State Axioms).
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

        for var_name in self.boolean_variables:
            step = utils.getStep(var_name)
            if step == 0:
                var = self.boolean_variables[var_name]
                if not var in initial:
                    initial.append(-var)

        return utils.make_formula_and(initial)

    ## Encode formula defining goal state
    def encodeGoalState(self):
        """
        Returns the formula that encode the goal state (Goal State Axioms).
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

        return utils.make_formula_and(encodePropositionalGoals())

    ## Encode action constraints: each action variable implies its preconditions and effects
    def encodeActions(self):
        """
        Returns the encoded formula for actions (Universal Frame Axioms).
        """

        actions = []

        for step in range(self.horizon):
            for action in self.actions:

                action_variable = self.action_variables[utils.makeName(action.name, step)]
                condition_list = list()

                # Encode preconditions
                for pre in action.condition:
                    pre_name = utils.makeName(pre, step)
                    if pre_name in self.boolean_variables:
                        if isinstance(pre, pddl.conditions.NegatedAtom):
                            condition_list.append(
                                -(self.boolean_variables[pre_name]))
                        else:
                            condition_list.append(
                                self.boolean_variables[pre_name])

                # Encode add effects
                for add in action.add_effects:
                    add_name = utils.makeName(add[1], step + 1)
                    if add_name in self.boolean_variables:
                        condition_list.append(self.boolean_variables[add_name])

                # Encode delete effects
                for de in action.del_effects:
                    del_name = utils.makeName(de[1], step + 1)
                    if del_name in self.boolean_variables:
                        condition_list.append(
                            -(self.boolean_variables[del_name]))

                # Universal Frame Axiom: (a_i -> (pre_a_i ^ add_a_i ^ -del_a_i))
                implicated_by_action = utils.make_formula_and(condition_list)

                universal_axiom = (action_variable >> implicated_by_action)
                actions.append(universal_axiom)

        return utils.make_formula_and(actions)

    ## Encode explanatory frame axioms
    def encodeFrame(self):
        """
        Returns the formula that encode the Explanatory Frame Axioms
        """

        frame = []
        for step in range(self.horizon):
            # Encode frame axioms for boolean fluents
            for fluent in self.boolean_fluents:

                fluent_name = utils.makeName(fluent, step)
                fluent_i = self.boolean_variables[fluent_name]

                fluent_name_suc = utils.makeName(fluent, step + 1)
                fluent_i_plus_one = self.boolean_variables[fluent_name_suc]

                action_delete_fluent = list()
                action_add_fluent = list()

                for action in self.actions:
                    # Check if f is in del of some act_i
                    for de in action.del_effects:
                        del_name = utils.makeName(de[1], step)
                        if del_name in self.boolean_variables:
                            if fluent_i == self.boolean_variables[del_name]:
                                action_delete_fluent.append(
                                    self.action_variables[utils.makeName(action.name, step)])

                    # Check if f is in add of some act_i
                    for add in action.add_effects:
                        add_name = utils.makeName(add[1], step)
                        if add_name in self.boolean_variables:
                            if fluent_i == self.boolean_variables[add_name]:
                                action_add_fluent.append(
                                    self.action_variables[utils.makeName(action.name, step)])

                # Explantory Frame Axiom: 
                # If action_delete_fluent (by actions) is not zero: ((f_i & -f_i+1) -> Or(a_i))
                if len(action_delete_fluent) is not 0: 
                    del_action = utils.make_formula_or(action_delete_fluent)
                    frame.append((fluent_i & -(fluent_i_plus_one)) >> del_action)
                else:
                    frame.append((-(fluent_i) | fluent_i_plus_one))
                    
                # If ction_add_fluent (by actions) is not zero: ((-f_i & f_i+1) -> Or(a_i))
                if len(action_add_fluent) is not 0:
                    add_action = utils.make_formula_or(action_add_fluent)
                    frame.append((-(fluent_i) & fluent_i_plus_one) >> add_action)
                else:
                    frame.append((fluent_i | -(fluent_i_plus_one)))

        return utils.make_formula_and(frame)

    ## Encode At Least One frame axioms
    def encodeAtLeastOne(self):
        """
        Returns the encoding formula of at least one
        """

        at_least_one = []
        action_set = set()

        for act in self.action_variables:
            action_name = act.split('@', 1)
            action_set.add(action_name[0])

        action_list = list(set(action_set))

        # Disjunctions of all action at step i
        for step in range(self.horizon):
            for act in action_list:
                action_name = utils.makeName(act, step)
                if action_name in self.action_variables:
                    if act is action_list[0]:
                        at_least_component = self.action_variables[action_name]
                    else:
                        at_least_component = at_least_component | self.action_variables[action_name]
            at_least_one.append(at_least_component)

        return utils.make_formula_and(at_least_one)

    ## Encode The Execution Semantics
    def encodeExecutionSemantics(self):
        """
        Returns in base on modifier, the paraller or the linear execution.
        """

        modicator = modifier.EncodeModifier(self.horizon, self.actions, self.boolean_variables, self.action_variables)
        if self.modifier is True:
            return modicator.encode_parallel_modifier()
        else:
            return modicator.encode_linear_modifier()

    ## Encode The Propositional Formula
    def do_encode(self):
        """
        Returns the formula to be solved.
        """

        # Create variables
        self.createVariables()

        # Start encoding formula
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

        return utils.make_formula_and(formula.values())

    def dump(self):
        print('Dumping encoding')
        raise Exception('Not implemented yet')
