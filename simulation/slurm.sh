#!/bin/bash
#
#SBATCH --job-name=pfc
#SBATCH --output=pfc.sh.o%j
#SBATCH --account=
#SBATCH --partition=
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem-per-gpu=44G

# module load /path/to/cuda # if gpu enabled

export PATH="/path/to/gmsh/bin:$PATH"
# If needed:
# export LD_LIBRARY_PATH="/shared/apps/mytool/lib:$LD_LIBRARY_PATH"

. /path/to/conda/setup
conda activate pfc

python3 simulate.py
