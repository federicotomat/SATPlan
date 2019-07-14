# SATPlan

Satplan (better known as Planning as Satisfiability) is a method for automated planning. It converts the planning problem instance into an instance of the Boolean satisfiability problem, which is then solved using a the [Minisat](http://minisat.se/) in order to establishing satisfiability.

Given a problem instance in planning, with a given initial state, a given set of actions, a goal, and a horizon length, a formula is generated so that the formula is satisfiable if and only if there is a plan with the given horizon length. A plan can be found by testing the satisfiability of the formulas for different horizon lengths. The simplest way of doing this is to the [ENHSP](https://bitbucket.org/enricode/the-enhsp-planner/src/master/) in order to compute the better initial horizon.


