#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:37:49 2019

@author: tac
"""

from enum import Enum

class Operator(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IMP = "IMP"
    IFF = "IFF"

class Node:
    
    def __init__(self, nodeid, op = None, left = None, right = None, label = None):
        self.id = nodeid      # Unique node id
        self.op = op          # None if it is a variable 
        self.left = left      # left operand
        self.right = right    # right operand
        self.label = label    # an optional label (could be handy for encodings)
        self.refcount = 0     # reference count for garbage collection

    # Variables (op == None) are hashed according to their id
    # Expressions (op != None) are hashed according to children and operator
    # This enables subformula sharing
    def __hash__(self):
        base = 17
        if (self.op == None):
            base = 31 * base + hash(self.id)
        else:
            base = 31 * base + hash(self.op)            
        if (self.left != None):
            base = 31 * base + hash(self.left.id)
        if (self.right != None):
            base = 31 * base + hash(self.right.id)
        return base
    
    # Variables (op == None) are equal when they have the same id
    # Epressions (op != None) are equal according to children and operator
    def __eq__(self, other):
        result = self.__class__ == other.__class__ 
        if (self.op == None):
            return result and self.id == other.id
        else:
            return result and\
            self.op == other.op and\
            self.left.id == other.left.id and\
            (self.right == None or self.right.id == other.right.id)
            
    def do_print(self, print_id = False):
        # Internal function to prinr IDs
        def get_id(i, flag):
            if (flag):
                return ":" + str(i) 
            else:
                return ""
                
        if (self.op == None):
            print ("v"+str(self.id),)
        else:
            print("(",self.op.name + get_id(self.id, print_id)," ",)
            if (self.left != None):
                self.left.do_print(print_id)
            print(" ",)
            if (self.right != None):
                self.right.do_print(print_id)
            print(" )",)

class FormulaMgr:
    
    def __init__(self):
        self.lastId = -1
        self.recycleIds = list() # When deleting a node, recycle the unique id
        self.node2id = dict()    # Get node id from node
        self.id2node = list()    # Get node from node id
        self.name2id = dict()    # Get node id from label (labels must be unique)
    
    # Get a new id or recycle one
    def getId(self):
        if (len(self.recycleIds) == 0):
            self.id2node.append(None)
            self.lastId += 1
            return self.lastId
        else:
            return self.recycleIds.pop()
    
    # Dispose of a node when its reference count reaches 1
    # or reduce its reference count
    def dispose(self, node):
        if (node.refcount > 1): # TODO: DOVREBBE ESSERE == 1
            # Reduce the reference count of the children (if any)
            if (node.left != None):
                node.left.refcount -= 1
            if (node.right != None):
                node.right.refcount -= 1
            # If the node has a label, remove it from the index
            if (node.label != None):
                self.name2id.pop(node.label)
            # Remove the node from all other indexes
            self.node2id.pop(node)
            self.id2node[node.id] = None
            # The id can be recycled 
            self.recycleIds.append(node.id)
        else:
            node.refcount -= 1
    
    # Make a variable. The id is assigned by the manager, the
    # label can be chosen by the user. The label must be unique
    def mkVar(self, name = None):
        if (name != None):
            nodeid = self.name2id.get(name)
            if (nodeid != None):
                return self.id2node[nodeid]
        nodeid = self.getId()
        node = Node(nodeid, label = name)
        self.node2id[node] = nodeid
        self.id2node[nodeid] = node
        if (name != None):
            self.name2id[name] = nodeid
        return node
    
    # Get the variable node using the label as a reference
    def getVarByName(self, name):
        if (name != None):
            return self.id2node[self.name2id.get(name)]
        else:
            return None
    
    # Get the variable node using the unique id as a reference
    def getVarById(self, varid):
        if (varid <= self.lastId):
            return self.id2node[varid]
        else:
            return None
    
    # Proc
    def mkOp(self, temp):
        nodeid = self.node2id.get(temp)
        if (nodeid != None):
            # If the subformula was already created, share it
            node = self.id2node[nodeid]
            node.refcount += 1
            return node
        else:
            # Create a new subformula node
            nodeid = self.getId()
            temp.id = nodeid
            self.id2node[nodeid] = temp
            self.node2id[temp] = nodeid
        return temp
    
    def mkAnd(self, f, g):
        temp = Node(0, op = Operator.AND, left = f, right = g)
        return self.mkOp(temp)    
    
    def mkOr(self, f, g):
        temp = Node(0, op = Operator.OR, left = f, right = g)
        return self.mkOp(temp)
    
    def mkNot(self, f):
        temp = Node(0, op = Operator.NOT, left = f)
        return self.mkOp(temp)
    
    def mkImply(self, f, g):
        temp = Node(0, op = Operator.IMP, left = f, right = g)
        return self.mkOp(temp)

class NnfConversion:
    
    def __init__(self, mgr):
        self.manager = mgr
    
    def do_conversion(self, node):
        if (node.op != None):        
            if (node.op == Operator.NOT):
                temp = self.convert(node.left, -1)
                self.manager.dispose(node)
                node = temp
            else:
                node = self.convert(node, 1)
        return node
    
    def convert(self, node, polarity):
        if (node.op == None):
            if (polarity > 0):
                return node
            else:
                return self.manager.mkNot(node)
        if (node.op == Operator.NOT):
            temp = self.convert(node.left, -1 * polarity)
            self.manager.dispose(node)
            return temp
        elif (node.op == Operator.AND):
            if (polarity < 0):
                left = self.convert(node.left, -1)
                right = self.convert(node.right, -1)
                return self.manager.mkOr(left, right)
            else:
                left = self.convert(node.left, 1)
                right = self.convert(node.right, 1)
                return self.manager.mkAnd(left, right)
        elif (node.op == Operator.OR):
            if (polarity < 0):
                left = self.convert(node.left, -1)
                right = self.convert(node.right, -1)
                return self.manager.mkAnd(left, right)
            else:
                left = self.convert(node.left, 1)
                right = self.convert(node.right, 1)         
                return self.manager.mkOr(left, right)
        elif (node.op == Operator.IMP):
            if (polarity < 0):
                left = self.convert(node.left, 1)
                right = self.convert(node.right, -1)
                return self.manager.mkAnd(left, right)
            else:
                left = self.convert(node.left, 1)
                right = self.convert(node.right, 1)
                return self.manager.mkImply(left, right)
        else:
            # This cannot happen
            assert True
        
        
class CnfConversion:
    
    def __init__(self, mgr):
        self.clauses = list()
        self.definitions = dict()
        self.manager = mgr
        
    # Assumes that the formula is in negative normal form
    def do_conversion(self, node):
        # Fail if the formula is not in NNF
        assert (node.op != Operator.NOT) or (node.left.op == None)
    
        # Add the unit clause representing the formula itself
        self.clauses.append([node.id])
        if (node.op != None):
            self.convert(node)
        return
    
    def get_clauses(self):
        return self.clauses
    
    def convert(self, node):
        # Fail if the formula is not in NNF
        assert (node.op != Operator.NOT) or (node.left.op == None)
        # Nothing to do if a literal is reached (variable or negation thereof) 
        if (node.op == None) or (node.op == Operator.NOT):
            return
        # An operator: AND, OR, IMP: add the definitions and propagate 
        # If the subformula was already visited, no need to visit again
        self.add_definitions(node)
        if (self.definitions.get(node.left.id) == None):
            self.convert(node.left)
        if (self.definitions.get(node.right.id) == None):
            self.convert(node.right)
        
        
    def add_definitions(self, node):
        def_clauses = list()
        # Local alias for negation function
        neg = self.neg
        # The literal corresponding to the formula
        l = node.id
        # The literal corresponding to the left operand
        # Negations must be applied to variables only
        if (node.left.op == Operator.NOT):
            assert(node.left.left.op == None)
            l1 = neg(node.left.left.id)
        else:
            l1 = node.left.id
        # The literal corresponding to the right operand
        # Negations must be applied to variables only
        if (node.right.op == Operator.NOT):
            assert(node.right.left.op == None)
            l2 = neg(node.right.left.id)
        else:
            l2 = node.right.id
        if (node.op == Operator.AND):
            def_clauses.append([l, neg(l1), neg(l2)])
            def_clauses.append([neg(l), l1])
            def_clauses.append([neg(l), l2])
        elif (node.op == Operator.OR):
            def_clauses.append([neg(l), l1, l2])
            def_clauses.append([l, neg(l1)])
            def_clauses.append([l, neg(l2)])
        elif (node.op == Operator.IMP):
            def_clauses.append([neg(l), neg(l1), l2])
            def_clauses.append([l, l1])
            def_clauses.append([l, neg(l2)])
            pass
        else:
            # This cannot happen
            assert True
        self.definitions[node.id] = def_clauses
        self.clauses.extend(def_clauses)
        
    def neg(self, id):
        return int(id * -1)
        
if __name__ == "__main__":
    mgr = FormulaMgr()
    # Test creation of variables
    v1 = mgr.mkVar()
    v2 = mgr.mkVar()
    v3 = mgr.mkVar()
    
    # Test creation of formulas
    print(" f:")
    f = mgr.mkAnd(v1,v2)
    f.do_print()
    f_not = mgr.mkNot(f)

    print("\n g:")
    g = mgr.mkOr(v1,v2)
    g.do_print()   
    g_not = mgr.mkNot(g)

    print("\n h:")
    h = mgr.mkImply(v1,v2)
    h.do_print()
    h_not = mgr.mkNot(h)

    s = mgr.mkOr(g,h)
    s = mgr.mkOr(f,s)
    s_not = mgr.mkNot(s)    
    print("\n s:")
    s.do_print()
    print("\n s (neg):")
    s_not.do_print()
    s_not_not = mgr.mkNot(s_not)    
    print("\n s (neg, neg):")
    s_not_not.do_print()
    print("\n")
    
    # Test negation normal form
    nnfize = NnfConversion(mgr)
    f_nnf = nnfize.do_conversion(f)
    print("\n f_nnf:")
    f_nnf.do_print()
    f_nnf = nnfize.do_conversion(f_not)
    print("\n f_nnf (neg):")
    f_nnf.do_print()
    g_nnf = nnfize.do_conversion(g)
    print("\n g_nnf:")
    g_nnf.do_print()
    g_nnf = nnfize.do_conversion(g_not)
    print("\n g_nnf (neg):")
    g_nnf.do_print()
    print("\n h_nnf:")
    h_nnf = nnfize.do_conversion(h)
    h_nnf.do_print()
    h_nnf = nnfize.do_conversion(h_not)
    print("\n h_nnf (neg):")
    h_nnf.do_print()
    s_nnf = nnfize.do_conversion(s)
    print("\n s_nnf:")
    s_nnf.do_print()
    s_nnf = nnfize.do_conversion(s_not)
    print("\n s_nnf (neg):")
    s_nnf.do_print()
    s_nnf = nnfize.do_conversion(s_not_not)
    print("\n s_nnf (neg,neg):")
    s_nnf.do_print()
    print("\n")    
    
    # Test CNF conversion
    cnfize_s = CnfConversion(mgr)
    cnfize_s.do_conversion(s)
    print("\n s (with ids)")
    s.do_print(True)
    print("\n s in CNF:")
    print(cnfize_s.get_clauses())
    
    # Test CNF conversion with repeated subformulas
    r = mgr.mkAnd(s,s)
    cnfize_r = CnfConversion(mgr)
    cnfize_r.do_conversion(r)
    print("\n r (with ids)")
    r.do_print(True)
    print("\n r in CNF:")
    print(cnfize_r.get_clauses())
