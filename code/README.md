The final project consists in the implementation of a SAT based planner that
leverages the SAT solver you implemented during the first half of the course.

Your planner will have to:
1) parse problems modeled in PDDL, 
2) build a propositional formula encoding the planning problem and
3) feed it to the SAT solver. 

On top of this, you will have to implement a simple horizon-allocation
strategy that will allow you to compute encode formulas for increasing
horizons.

We will provide you with some code so you don't have to start implementing
from scratch.

Requirements:

There are some basic requirements your planner must meet to be evaluated.

Parsing is already taken care of by the code we will give you, so you don't 
need to worry about it.

Your code MUST run without throwing unhandled exceptions, seg faults etc. 
It's python code, so there's a good chance everything will work fine. 
But if it does not, you will lose points.

Code provided:
enhsp is the code for planning that is base on heuristic(?) and need to have java
	(lower bound for the exploration) oherwise we can go for a horizon with exponential growth 		(2-4-8-16-..) and sometimes we know the length of the plan (for some problems)

translate: translate the project at run time and (online temporal fast downward)

driver has the main file that run the code and have to convert pddl in a FOL structure

planner: here we have to modify majority of the code, we have to implement or conclude the algorithm of encoding and searching

convert problem into planning domain to the PL domain so before we have to translate their
