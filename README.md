## Phase Field Crystal Simulations of Foams on a Spherical Surface

This repository contains python scripts for performing and analyzing phase field crystal simulations on a spherical surface. This file describes environment setup. For details of simulation or analyses, see the READMEs in the respective subdirectories.

### Dependencies

- [FiPy](https://pages.nist.gov/fipy/en/latest/index.html)
- [gmsh](https://gmsh.info/)

In a new venv/conda environment, run `$ pip install -r requirements.txt` to install requirements for simulation and analysis.

You can install `gmsh` via a package manager or download compiled binaries from their website. If the latter, you must specify the path to the binary, `export PATH="/path/to/gmsh/bin:$PATH"`, such that `PiFy` can make subprocess calls to it.

### GPU Support

To use GPUs to accelerate PFC simulations, the [AMGX](https://github.com/NVIDIA/AMGX) AND [pyamgx](https://github.com/shwina/pyamgx) packages are required. Compile `AMGX` with the following modules:

- CMake/3.24.3-GCCcore-12.2.0
- CUDA/12.8
- Specify CUDA architecture with CMake: `cmake ../ -DCMAKE_CUDA_ARCHITECTURES=86`

Once `AMGX` is compiled, follow `pyamgx` installation instructions. Extra steps are specified below:

- Install extra requirement `Cython`: `$ pip install Cython`
- If in virtual python environment (i.e. conda), install `pyamgx` with: `$ pip install --no-build-isolation .`

NOTE - Some issues experienced with `pyamgx`:
- [Memory leak for pyamgx solvers resulting in termination](https://github.com/usnistgov/fipy/issues/1204)
- [object has no attribute 'precon' in pyamgx solvers](https://github.com/usnistgov/fipy/issues/1199)

### Running on Different Platforms

See `simulation/README` and associated slurm scripts for instructions on running simulations with different hardware support.
