# How to run the simulator
Clone the repository:
```
git clone https://github.com/federicotomat/SATPlan.git
```
Install the required libraries and the Minisat solver:
```
pip -r requirements.txt
sudo apt-get update
sudo apt-get install minisat
```
Enter in the workspace folder and install the ENHSP module:
```
cd ~/SATPlan/code/enhsp
./install
```
Go back to previous folder, export your python path to the folder of the code and run the code on a PDDL domain:
```
export PYTHONPATH="<(your_path)>"
python2 plan.py -domain <(pddl-domain) <(pddl-problem)>
```


