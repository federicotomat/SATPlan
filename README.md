# SATPlan

Implementation of SATPlan (Planning as Satisfiability), which is a method for automated planning. It convert the instance of the Planning problem to one of Boolean satisfiability, which is then solved using the [Minisat](http://minisat.se/).

Given the instance of a planning problem, with a given initial state and actions, a goal and a horizon length, a formula is generated which turns out to be satisfiable if and only if there was a plan with the given horizon length . A plan can be found by testing the satisfiability of the formulas for different horizon lengths. The simplest way to do this is to use the [ENHSP](https://bitbucket.org/enricode/the-enhsp-planner/src/master/) to calculate the best starting horizon.

# Usage
Clone the repository:
```bash
git clone https://github.com/federicotomat/SATPlan.git
```
Install the required libraries and the Minisat solver:
```bash
cd ~/SATPlan
pip install -r requirements.txt
sudo apt-get update
sudo apt-get install minisat
```
Enter in the workspace folder and install the ENHSP module:
```bash
cd code/enhsp
./install
```
Turn in the main folder, export python path and run the code on a PDDL problem:
```bash
cd ..
export PYTHONPATH="<(folder-path)>"
python2 plan.py -domain <(path-pddl-domain)> <(path-pddl-problem)>
```
# References

[F. Leofante, E. Giunchiglia, E. Ábráham, A. Tacchella - Optimal Planning Modulo Theories](https://doi.org/10.24963/ijcai.2020/571)
