## Phase Field Crystal Simulations of Foams on a Spherical Surface

This repository contains python scripts for performing and analyzing phase field crystal simulations on a spherical surface. 

### Dependencies

- [FiPy](https://pages.nist.gov/fipy/en/latest/index.html)
- [gmsh](https://gmsh.info/)

In a new venv/conda environment, run `$ pip install -r requirements.txt` to install requirements for simulation and analysis.

You can install `gmsh` via a package manager or download compiled binaries from their website. If the latter, you must specify the path to the binary, `export PATH="/path/to/gmsh/bin:$PATH"`, such that `PiFy` can make subprocess calls to it.

### GPU Support

To use GPUs to accelerate PFC simulations, the [AMGX](https://github.com/NVIDIA/AMGX) AND [pyamgx](https://github.com/shwina/pyamgx) packages are required. Once `AMGX` is compiled, follow `pyamgx` installation instructions. Potential extra steps are specified below:

- Install extra requirement `Cython`: `$ pip install Cython`
- If in virtual python environment (i.e. on cluster), install `pyamgx` with: `$ pip install --no-build-isolation .`
