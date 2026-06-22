## Phase Field Crystal Simulation

The directory contains scripts and configuration files for conducting Phase Field Crystal simulations on a periodic 2D Grid or the surface of a sphere.

This repository focuses on the evolution of phase fields describing foams as detailed by [Guttenberg et al. PRE. 2010](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.81.065301). The field is evolved through time with second order exponential time differentiation with Runge Kutta time stepping (EDT2RK, [Cox and Matthews. JCP. 2002](https://www.sciencedirect.com/science/article/abs/pii/S0021999102969950)) and a pseudospectral method to calculate the nonlinear terms which is common for phase field methods ([Moats et al. PRE. 2019](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.99.012803)).

### Getting Started

After installing dependencies and setting up your python environment (see top level README), run a simulation:

`$ python simulate.py`

### Configuration Files

- mesh.geo: Contains information for constructing the surface, a sphere in this case, for use in 3D PFC simulations
- config.yaml: Configuration variables with (TODO) descriptive comments
  - Values of Coefficients for the PFC partial differential equation
  - Details for log and trajectory files

### Output Files

Simulations will output two files:
- Log File: Parameters, warnings, errors, and progress information.
- H5DF Trajectory File: Also contains parameters for redundancy and the time evolution of the field.
