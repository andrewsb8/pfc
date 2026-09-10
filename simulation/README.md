## Phase Field Crystal Simulation

The directory contains scripts and configuration files for conducting Phase Field Crystal simulations on a periodic 2D Grid or the surface of a sphere.

### Getting Started

After installing dependencies and setting up your python environment (see top level README), run a simulation:

`$ python simulate.py config.yaml`

### Configuration Files

- config.yaml: Configuration variables 
  - Values of Coefficients for the PFC partial differential equation
  - Specify 2 or 3 dimensional simulations
  - Details for log and trajectory files

### Output Files

Simulations will output two files:
- Log File: Parameters, warnings, errors, and progress information.
- H5DF Trajectory File: Also contains parameters for redundancy and the time evolution of the field.
