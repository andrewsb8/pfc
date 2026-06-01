## Phase Field Crystal Simulation

The directory contains scripts and configuration files for conducting Phase Field Crystal simulations on the surface of a sphere.

### Getting Started

After installing dependencies and setting up your python environment (see top level README), run a simulation:

`$ python simulate.py`

To specify specific solvers (like `pyamgx` for gpu acceleration), run the command like

`$ FIPY_SOLVERS=pyamgx python simulate.py`

### Configuration Files

- mesh.geo: Contains information for constructing the surface, a sphere in this case
- config.yaml: Configuration variables with (TODO) descriptive comments
  - Values of Coefficients for the PFC partial differential equation
  - Details for log and trajectory files

### Output Files

Simulations will output two files:
- Log File: Parameters, warnings, errors, and progress information.
- H5DF Trajectory File: Also contains parameters for redundancy and the time evolution of the field.

### Running on HPC

This directory contains `slurm_[platform].sh` which shows example execution and required modules for running simulations in an HPC environment. If executing locally, you can copy the final line of each file to run with desired hardware support.
