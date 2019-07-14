# SATPlan

Satplan (better known as Planning as Satisfiability) is a method for automated planning. It converts the planning problem instance into an instance of the Boolean satisfiability problem, which is then solved using a the [Minisat](http://minisat.se/) in order to establishing satisfiability.

Given a problem instance in planning, with a given initial state, a given set of actions, a goal, and a horizon length, a formula is generated so that the formula is satisfiable if and only if there is a plan with the given horizon length. A plan can be found by testing the satisfiability of the formulas for different horizon lengths. The simplest way of doing this is to the [ENHSP](https://bitbucket.org/enricode/the-enhsp-planner/src/master/) in order to compute the better initial horizon.

# How to run the simulator
Clone the repository:
```
git clone https://github.com/federicotomat/SATPlan.git
```
Install the required libraries and the Minisat solver:
```
cd ~/SATPlan/
pip -r requirements.txt
sudo apt-get update
sudo apt-get install minisat
```
Enter in the workspace folder and install the ENHSP module:
```
cd code/enhsp
./install
```
Turn in the main folder, export python path and run the code on a PDDL problem:
```
cd ..
export PYTHONPATH="<(your_path)>"
python2 plan.py -domain <(pddl-domain) <(pddl-problem)>
```

