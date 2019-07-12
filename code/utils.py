import itertools
from z3 import *
# from translate.pddl import *
import translate.pddl as pddl
from collections import Iterable
import os
import re

def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

def getDomainName(task_filename):
    dirname, basename = os.path.split(task_filename)
    ## look for domain in folder or  folder up
    domain_filename = os.path.join(dirname, "domain.pddl")
    os.path.exists(domain_filename) 
    if not os.path.exists(domain_filename):
      domain_filename = os.path.join(dirname, "../domain.pddl")    
    if not os.path.exists(domain_filename) and re.match(r"p[0-9][0-9]\b", basename):
      domain_filename = os.path.join(dirname, basename[:4] + "domain.pddl")
    if not os.path.exists(domain_filename) and re.match(r"p[0-9][0-9]\b", basename):
      domain_filename = os.path.join(dirname, basename[:3] + "-domain.pddl")
    if not os.path.exists(domain_filename):
      raise SystemExit("Error: Could not find domain file using "
                       "automatic naming rules.")
    return domain_filename

def getValFromModel(assignment):
    """
        Extracts values from Z3 model
        making sure types are properly
        converted
    """
    
    if is_true(assignment) or is_false(assignment):
        return assignment
    if is_int_value(assignment):
        return assignment.as_long()       
    elif is_algebraic_value(assignment):
        proxy = assignment.approx(20)
        return float(proxy.numerator_as_long())/float(proxy.denominator_as_long())
    elif is_rational_value(assignment):
        return float(assignment.numerator_as_long())/float(assignment.denominator_as_long())
    else:
        raise Exception('Unknown type for assignment')


def varNameFromNFluent(fluent):
    """
        Returns variable name used for encoding
        numeric fluents in SMT
    """
    
    args = [arg.name for arg in fluent.args]
    if len(args) == 0:
        return fluent.symbol
    return '{}_{}'.format(fluent.symbol,'_'.join(args))

def varNameFromBFluent(fluent):
    """
        Returns variable name used for encoding
        boolean fluents in SMT
    """
    
    args = [arg.name for arg in fluent.args]
    if len(args) == 0:
        return fluent.predicate
    return '{}_{}'.format(fluent.predicate,  '_'.join(args))


def isBoolFluent(fluent):
    if isinstance(fluent, (pddl.conditions.Atom, pddl.conditions.NegatedAtom)):
        return True
    else:
        return False
    
def isNumFluent(fluent):
    if isinstance(fluent, (pddl.f_expression.FunctionalExpression, pddl.f_expression.FunctionAssignment)):
        return True
    else:
        return False


def inorderTraversal(encoder,nax, numeric_variables):
        """
        'Sort of' in order traversal.
        """
                
        for layer, lst in encoder.axioms_by_layer.items():
            if nax in lst:
                break       
                 
        if layer < 0:
            # it's a const, we're good
            assert len(nax.parts) == 1       
            return nax.parts[0].value
        
        elif layer == 0:
            # variable assignment

            assert len(nax.parts) == 2
            # one part contains PDDL function, i.e, SMT  variable
            # the other contains either a PDDL function or a const

            if nax.parts[0] in encoder.numeric_fluents and not nax.parts[1] in encoder.numeric_fluents:
                fluent = nax.parts[0]
                var_name = varNameFromNFluent(fluent)
                l_expr = numeric_variables[var_name]
                const_ax = nax.parts[1]
                r_expr = inorderTraversal(encoder,encoder.axioms_by_name[const_ax],numeric_variables)

            elif nax.parts[1] in encoder.numeric_fluents and not nax.parts[0] in encoder.numeric_fluents:
                fluent = nax.parts[1]
                var_name = varNameFromNFluent(fluent)
                r_expr = numeric_variables[var_name]
                const_ax = nax.parts[0]
                l_expr = inorderTraversal(encoder,encoder.axioms_by_name[const_ax],numeric_variables)
                
            elif nax.parts[0] in encoder.numeric_fluents and nax.parts[1] in encoder.numeric_fluents:
                ## fluent 1
                l_fluent = nax.parts[0]
                var_name = varNameFromNFluent(l_fluent)
                l_expr = numeric_variables[var_name]

                ## fluent 2
                r_fluent = nax.parts[1]
                
                var_name = varNameFromNFluent(r_fluent)
                r_expr = numeric_variables[var_name]
            else:
                raise Exception('Axiom {} not recognized.'.format(nax))
                

            if nax.op == '+':
                return l_expr + r_expr
            elif nax.op == '-':
                return l_expr - r_expr
            elif nax.op == '*':
                return l_expr * r_expr
            elif nax.op == '/':
                return l_expr / r_expr
            else:
                raise Exception('Operator not recognized')

                
        else:
            # complex expression
            # if part is just a fluent, retrieve the corresponding SMT variable
            # otherwise go down the graph
            
            if nax.parts[0] in encoder.numeric_fluents and not nax.parts[0].symbol.startswith('derived!'):
                var_name = varNameFromNFluent(nax.parts[0])
                l_expr = numeric_variables[var_name]
            else:
                l_expr = inorderTraversal(encoder,encoder.axioms_by_name[nax.parts[0]],numeric_variables)


            if nax.parts[1] in encoder.numeric_fluents and not nax.parts[1].symbol.startswith('derived!'):
                var_name = varNameFromNFluent(nax.parts[1])
                r_expr = numeric_variables[var_name]
            else:
                r_expr = inorderTraversal(encoder,encoder.axioms_by_name[nax.parts[1]],numeric_variables)


            if nax.op == '+':
                return l_expr + r_expr
            elif nax.op == '-':
                return l_expr - r_expr
            elif nax.op == '*':
                return l_expr * r_expr
            elif nax.op == '/':
                return l_expr / r_expr
            else:
                raise Exception('Operator not recognized')

def inorderTraversalFC(encoder,condition, numeric_variables):
        """
            Inorder traversal for Comparison axioms
            internally relies on inorderTraversal() above.
            Returns an SMT formula for comparison axioms
        """
        
        assert len(condition.parts) == 2

        # if part is just a fluent, retrieve the corresponding SMT variable
        # otherwise go down the graph

        ## HACKISH check to discard derived axioms

        
        if condition.parts[0] in encoder.numeric_fluents and not condition.parts[0].symbol.startswith('derived!'):
            var_name = varNameFromNFluent(condition.parts[0])
            l_expr = numeric_variables[var_name]
        else:
            l_expr = inorderTraversal(encoder,encoder.axioms_by_name[condition.parts[0]],numeric_variables)


        if condition.parts[1] in encoder.numeric_fluents and not condition.parts[1].symbol.startswith('derived!'):
            var_name = utils.varNameFromNFluent(condition.parts[1])
            r_expr = numeric_variables[var_name]
        else:
            r_expr = inorderTraversal(encoder,encoder.axioms_by_name[condition.parts[1]],numeric_variables)

       
        if condition.comparator == '=':
            return l_expr == r_expr
        elif condition.comparator == '<':
            return l_expr < r_expr
        elif condition.comparator == '<=':
            return l_expr <= r_expr
        elif condition.comparator == '>':
            return l_expr > r_expr
        elif condition.comparator == '>=':
            return l_expr >= r_expr
        else:
            raise Exception('Comparator not recognized')

def extractVariables(encoder,nax,variables):
        """
        'Sort of' in order traversal.
        Chiedere Tac, fa schifo...
        """
        
        for layer, lst in encoder.axioms_by_layer.items():
            if nax in lst:
                break
            
        if layer < 0:
            return
        elif layer == 0:
            # variable assignment

            assert len(nax.parts) == 2
            # one part contains PDDL function, i.e, SMT  variable
            # the other contains either a PDDL function or a const

            if nax.parts[0] in encoder.numeric_fluents and not nax.parts[1] in encoder.numeric_fluents:
                fluent = nax.parts[0]
                variables.append(varNameFromNFluent(fluent))
                return
                
            elif nax.parts[1] in encoder.numeric_fluents and not nax.parts[0] in encoder.numeric_fluents:
                fluent = nax.parts[1]
                variables.append(varNameFromNFluent(fluent)) 
                return
                
            elif nax.parts[0] in encoder.numeric_fluents and nax.parts[1] in encoder.numeric_fluents:
                ## fluent 1
                l_fluent = nax.parts[0]
                variables.append(varNameFromNFluent(l_fluent))
               
                ## fluent 2
                r_fluent = nax.parts[1]
                variables.append(varNameFromNFluent(r_fluent))
                return
                
            else:
                raise Exception('Axiom {} not recognized.'.format(nax))
             
        else:
            # complex expression
            # if part is just a fluent, retrieve the corresponding SMT variable
            # otherwise go down the graph
            
            if nax.parts[0] in encoder.numeric_fluents and not nax.parts[0].symbol.startswith('derived!'):
                variables.append(varNameFromNFluent(nax.parts[0]))
                
            else:
                extractVariables(encoder,encoder.axioms_by_name[nax.parts[0]],variables)

            if nax.parts[1] in encoder.numeric_fluents and not nax.parts[1].symbol.startswith('derived!'):
                variables.append(varNameFromNFluent(nax.parts[1]))
                
            else:
                extractVariables(encoder,encoder.axioms_by_name[nax.parts[1]],variables)

           

def extractVariablesFC(encoder,condition):
    """
        Inorder traversal for Comparison axioms
        internally relies on inorderTraversal() above.
        Returns an SMT formula for comparison axioms
    """
    c = condition

    variables = []

    
    assert len(c.parts) == 2

    # if part is just a fluent, retrieve the corresponding SMT variable
    # otherwise go down the graph
    if c.parts[0] in encoder.numeric_fluents and not c.parts[0].symbol.startswith('derived!'):
        variables.append(varNameFromNFluent(c.parts[0]))
    else:
        extractVariables(encoder,encoder.axioms_by_name[c.parts[0]],variables)


    if c.parts[1] in encoder.numeric_fluents and not c.parts[1].symbol.startswith('derived!'):
        variables.append(varNameFromNFluent(c.parts[1]))
    else:
        extractVariables(encoder,encoder.axioms_by_name[c.parts[1]],variables)
        
    return variables


def maximalIndepSet(encoder):
    import networkx as nx

    g = nx.Graph()

    edges = [(a1.name,a2.name)for a1, a2 in encoder.mutexes]

    g.add_edges_from(edges)

    m = nx.maximal_independent_set(g)
    
    return len(m)

def computeCC(encoder):
    import networkx as nx

    g = nx.Graph()

    edges = [(a1.name,a2.name)for a1, a2 in encoder.action_mutexes]

    g.add_edges_from(edges)

    ccs = sorted(nx.connected_components(g), key=len)

    return ccs

def parseMetric(encoder):
    metric = encoder.task.metric[1]
    fluents = encoder.numeric_variables[encoder.horizon]
   
    def inorderTraversal(metric):
        op = metric[0]

        if op in ['+','-','*','/']:
            l_expr = inorderTraversal(metric[1])

            r_expr = inorderTraversal(metric[2])

            if op == '+':
                return l_expr + r_expr
            elif op == '-':
                return l_expr - r_expr
            elif op == '*':
                return l_expr * r_expr
            elif op == '/':
                return l_expr / r_expr
            else:
                raise Exception('Operator not recognized')
        else:
            if isinstance(metric,basestring):
                return float(metric)
                
            else:
                return fluents['_'.join(metric)]
            
        
    if len(metric) == 1:
        metricExpr =  fluents[metric[0]]
    else:
        metricExpr = inorderTraversal(metric)
    
    return metricExpr


##
# https://github.com/Z3Prover/z3/blob/master/examples/python/visitor.py
def visitor(e, seen):
    if e in seen:
        return
    seen[e] = True
    yield e
    if is_app(e):
        for ch in e.children():
            for e in visitor(ch, seen):
                yield e
        return
    if is_quantifier(e):
        for e in visitor(e.body(), seen):
            yield e
    return

def makeName(name, step):
    return str(name) + "@" + str(step)

def getStep(var_name):
    [name, step] = var_name.split("@")
    return int(step)