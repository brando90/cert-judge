#!/bin/bash
# TLDR: experiment 58 judging, Sherlock fallback: one array task = one panel model, vLLM 0.30.0 in the AT-476 image on L40S or H100;
# resumable. Submit through sherlock/submit_all.sh (it sets --gres per group). Smoke: sbatch --array=0 run_model.sbatch smoke
#SBATCH -J e58_judge
#SBATCH -p gpu
#SBATCH -C GPU_SKU:L40S|GPU_SKU:H100_SXM5
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 2-00:00:00
#SBATCH -o logs/%x_%A_%a.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=brandojazz@gmail.com,brando.science@gmail.com
set -euo pipefail
source $SCRATCH/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/sherlock/env.sh
LDENV=$(e58_ldenv)
read KEY NGPU <<< "$(e58_task $SLURM_ARRAY_TASK_ID)"
echo "task $SLURM_ARRAY_TASK_ID: $KEY ($NGPU GPU) on $(hostname)"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
[ "$(nvidia-smi -L | wc -l)" -ge "$NGPU" ] || { echo "allocated fewer than $NGPU GPUs"; exit 4; }
gpy() { apptainer exec --nv -B /scratch --env "$APPENV$LDENV" $SIF python3 "$@"; }
if [ "${1:-}" = smoke ]; then
  gpy $CODE/scripts/judge_vllm.py --model $KEY --exp e39 --run $B/runs/smoke --weights $MODELS_DIR/$KEY --prompts R4,P1 --limit-cells 10
  echo "SMOKE OK"; exit 0
fi
for EXP in e39 e42; do
  gpy $CODE/scripts/judge_vllm.py --model $KEY --exp $EXP --run $RUN --weights $MODELS_DIR/$KEY
done
echo "JUDGE TASK OK: $KEY"
