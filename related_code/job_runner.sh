#!/bin/bash
#SBATCH --account=astuart
#SBATCH --job-name=jobbie.job
#SBATCH --output=jobbie.out
#SBATCH --error=jobbie.err
#SBATCH --time=2:00:00
#SBATCH --exclusive
#SBATCH --gres=gpu:1
load python3/3.7.0
python3 train.py
