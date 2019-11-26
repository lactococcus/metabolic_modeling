# Bac-CoMed (Bacterial Community Medium Designer)

Bac-CoMed combines Genome-Scale Metabolic Models, Flux Balance Analysis (FBA) and Genetic Algorithms (GA) to design novel growth media for bacterial communities, in which the bacteria show a certain growth behavior.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Dependencies

The following python packages are required to run Bac-CoMed:

[cobrapy](https://github.com/opencobra/cobrapy)

### Solvers

A solver is needed to run the Flux Balance Analysis. At this time you have the following options:

-  ILOG/CPLEX (available with
   [Academic](https://www.ibm.com/developerworks/university/academicinitiative/)
   and
   [Commercial](http://www.ibm.com/software/integration/optimization/cplex-optimizer/)
   licenses).
-  [gurobi](http://gurobi.com)
-  [glpk](http://www.gnu.org/software/glpk/)

### Installing

- Download and install the dependencies listed above
- Download Bac-CoMed from github
```
TODO
```
- Run Bac-CoMed using the console
```
python your/install/directory/BacCoMed.py
```
Running the BacCoMed.py script without arguments will open the Bac-CoMed GUI.

