#!/bin/bash -l 

#SBATCH --job-name=recipe_cvdp.%J
#SBATCH --output=/work/bd1083/b380971/output/daily_ozone/recipe_cvdp.%J.out
#SBATCH --error=/work/bd1083/b380971/output/daily_ozone/recipe_cvdp.%J.err
#SBATCH --account=bd1083
#SBATCH --partition=interactive
#SBATCH --time=04:00:00
#SBATCH --mem=64G

set -eo pipefail 
unset PYTHONPATH 

. /work/bd0854/b380971/python/mambaforge/etc/profile.d/conda.sh
conda activate esmvaltool_january

esmvaltool run recipe_cvdp.yml --max_parallel_tasks=8
