#!/bin/bash -l
#SBATCH -D /u/ggitanjali/JWST/scripts/
#SBATCH --ntasks=1         # launch job on
#SBATCH --cpus-per-task=10  #   8 cores on a shared node
#SBATCH --time=23:30:00
#SBATCH --mail-user gitanjali.gitanjali@uni-potsdam.de
#SBATCH --mail-type=ALL

set -e
SECONDS=0

module purge
module load gcc/10
module load anaconda/3/2023.03


TARGET=$1
FILTER=$2
MODEL=$3
SKY=$4

DATA="../data/${TARGET}/${FILTER}.fits[91:110, 91:110]"
#DATA="../data/${TARGET}/${FILTER}.fits[86:115,86:115]"  ## this one is for GS-13971
PSF="../PSF_files/${TARGET}/${FILTER}.fits"

CONFIG="../configs/${TARGET}/${FILTER}_${MODEL}.dat"

OUTMODEL="../imfit_models/${TARGET}/${FILTER}_${MODEL}.fits"
OUTRESID="../imfit_resid/${TARGET}/${FILTER}_${MODEL}.fits"
OUTPARAM="../imfit_params/${TARGET}/${FILTER}_${MODEL}.dat"

mkdir -p \
    ../imfit_models/${TARGET} \
    ../imfit_resid/${TARGET} \
    ../imfit_params/${TARGET}

echo "=============================================="
echo "Target : ${TARGET}"
echo "Filter : ${FILTER}"
echo "Model  : ${MODEL}"
echo "=============================================="

imfit "$DATA" \
    -c "$CONFIG" \
    --psf "$PSF" \
    --sky="$SKY" \
    --save-model "$OUTMODEL" \
    --save-residual "$OUTRESID" \
    --save-params "$OUTPARAM"








