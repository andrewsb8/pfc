## Phase Field Crystal Simulations of Foams

This repository contains python scripts for performing and analyzing phase field crystal simulations in a 2D Grid or the 2D surface of a sphere. 

- The free energy is taken from [Guttenberg, Goldenfeld, and Danzig](https://doi.org/10.1103/PhysRevE.81.065301) and designed to produce foams in 2D. The free energy form can be changed by modifying `_generate_eq_motion`. 
- In the main branch, The field is evolved through time with first-order exponential time differentiation ([Cox and Matthews. JCP. 2002](https://www.sciencedirect.com/science/article/abs/pii/S0021999102969950)) and a pseudospectral method to calculate the nonlinear terms which is common for phase field methods ([Moats et al. PRE. 2019](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.99.012803)). 
- Parameters are set in a `.yaml` file for convenient experiment setup and logging and read using [PyYAML](https://pyyaml.org/).
- Trajectories are stored in the [HDF5](https://support.hdfgroup.org/documentation/hdf5/latest/_intro_h_d_f5.html) file format with the associated metadata for large scale simulation and convenient analysis. For details of simulation or analyses, see the READMEs in the respective subdirectories.
- Simulations in different geometries (2D vs 3D) are managed by changing a single parameter in the `.yaml` config file. The [Strategy](https://en.wikipedia.org/wiki/Strategy_pattern) pattern is employed so the unique aspects of simulations in each dimension are managed in the same workflow (logging, trajectory, etc).

### Dependencies

In a new venv/conda environment, run `$ pip install -r requirements.txt` to install requirements for simulation and analysis.

### Contents

- `simulation`: contains scripts and configuration files for running the simulations.
- `analyses`: contains scripts for analyzing the simulations.

### Known Issues

- The free energy form from Guttenberg with pseudospectral simulations is not suitable in 3D geometries because the eigenvalues of the Laplacian go from a continuous wavevector magnitude, k, to integers, l. Therefore, only low l modes are accessible in reasonable parameter ranges and the field will always coarsen to the l=1 mode or l=0 mode depending on the parameters. Adding a unique free energy for each dimension would require modifying the `DimensionTemplate` base class and defining the equation of motion in the `PFCxD` classes instead of the `PFC_Sim` class.

### Branches

Other branches include alternate implementations or higher order solvers.

- `real-space`: Implements PFC simulations using `FiPy` where the free energy is evaluated in real space as opposed to Fourier space. Includes instructions for running in HPC environment with slurm. Though it could utilize GPU-acceleration or massive parallelization, evaluating a real-space free energy with $\nabla^{8}$ was too computationally expensive.
- `etd2rk`: Implements the same as the main branch but uses second order exponential time differentiation with Runge Kutta time stepping.
