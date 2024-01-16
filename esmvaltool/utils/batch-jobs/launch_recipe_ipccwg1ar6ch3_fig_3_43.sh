#!/bin/bash -l 

#SBATCH --job-name=recipe_ipccwg1ar6ch3_fig_3_43.%J
#SBATCH --output=/home/b/b380971//work/bd1083/b380971/output/daily_ozone//recipe_ipccwg1ar6ch3_fig_3_43.%J.out
#SBATCH --error=/home/b/b380971//work/bd1083/b380971/output/daily_ozone//recipe_ipccwg1ar6ch3_fig_3_43.%J.err
#SBATCH --account=bd1083
#SBATCH --partition=compute 
#SBATCH --time=08:00:00 
#SBATCH --mem=0

set -eo pipefail 
unset PYTHONPATH 

. /work/bd0854/b380971/python/mambaforge/etc/profile.d/conda.sh
conda activate esmvaltool_sweden

esmvaltool run ipccwg1ar6ch3/recipe_ipccwg1ar6ch3_fig_3_43.yml --max_parallel_tasks=1
