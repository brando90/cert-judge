#!/bin/bash
# TLDR: Sherlock one-time setup (needs internet: a dev node): weights at the pinned revisions (huggingface_hub from the image's python,
# installed to a user dir if missing), tasks.tsv, prompt-hash check. The vLLM image from AT-476 must exist at $SIF.
# usage: srun -p dev -c 4 --mem=16G -t 02:00:00 bash $SCRATCH/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/sherlock/prepare.sh [model,model|all]
set -euo pipefail
source "$(dirname "$0")/env.sh"
[ -f $SIF ] || { echo "missing $SIF (AT-476 image)"; exit 2; }
MODELS=${1:-all}
export HF_HUB_OFFLINE=0
apptainer exec -B /scratch --env "HF_HOME=$B/cache/hf" $SIF python3 $CODE/scripts/fetch_models.py --dir $MODELS_DIR --models $MODELS
apptainer exec -B /scratch $SIF python3 $CODE/scripts/fetch_models.py --dir $MODELS_DIR --list > $CODE/slurm/tasks.tsv
e58_py $CODE/scripts/verify_prompts.py
echo "PREPARE OK"
