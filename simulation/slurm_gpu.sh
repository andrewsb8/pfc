#!/bin/bash
#
#SBATCH --job-name=pfc-gpu
#SBATCH --output=slurm.sh.o%j
#SBATCH --partition=
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH --mem-per-gpu=32G

module load CUDA

export PATH="/path/to/gmsh/bin:$PATH"

source /gpfs/gibbs/project/sweeney_alison/ba557/miniconda3/etc/profile.d/conda.sh
conda activate pfc

python3 simulate.py
