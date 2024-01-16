#!/bin/bash -l 

#SBATCH --job-name=recipe_lauer22jclim_fig7_seas.%J
#SBATCH --output=/home/b/b380971//work/bd1083/b380971/output/daily_ozone//recipe_lauer22jclim_fig7_seas.%J.out
#SBATCH --error=/home/b/b380971//work/bd1083/b380971/output/daily_ozone//recipe_lauer22jclim_fig7_seas.%J.err
#SBATCH --account=bd1083
#SBATCH --partition=interactive
#SBATCH --time=04:00:00
#SBATCH --mem=64G

set -eo pipefail 
unset PYTHONPATH 

. /work/bd0854/b380971/python/mambaforge/etc/profile.d/conda.sh
conda activate esmvaltool_sweden

esmvaltool run clouds/recipe_lauer22jclim_fig7_seas.yml --max_parallel_tasks=8
