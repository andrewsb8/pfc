#!/bin/bash
#
#SBATCH --job-name=pfc
#SBATCH --output=slurm.sh.o%j
#SBATCH --account=
#SBATCH --partition=
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem-per-gpu=44G

module load cuda/12.6

export PATH="/path/to/gmsh/bin:$PATH"

. /path/to/miniconda3/etc/profile.d/conda.sh
conda activate pfc

PIFY_SOLVERS=amgxpy python3 simulate.py
