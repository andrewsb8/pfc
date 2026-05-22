#!/bin/bash
#
#SBATCH --job-name=pfc
#SBATCH --output=slurm.sh.o%j
#SBATCH --account=
#SBATCH --partition=
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00

export PATH="/path/to/gmsh/bin:$PATH"

source /path/to/miniconda3/etc/profile.d/conda.sh
conda activate pfc

python3 simulate.py
