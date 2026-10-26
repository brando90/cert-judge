#!/bin/bash
# TLDR: experiment 58 judging, FarmShare: one array task = one panel model (tasks.tsv line SLURM_ARRAY_TASK_ID), E39 probes then E42
# probes, all nine prompt configurations, resumable (raw output is appended after every 256 cells; a re-run skips finished cells).
# submit_all.sh passes --array and --gres (1 or 2 L40S) per group; do not run this file directly. Timed out? Resubmit the same index.
#SBATCH -J e58_judge
#SBATCH -p gpu
#SBATCH --qos=gpu
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 2-00:00:00
#SBATCH -o /home/users/%u/e58/logs/%x_%A_%a.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=brandojazz@gmail.com,brando.science@gmail.com
set -euo pipefail
source $HOME/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/env.sh
read KEY NGPU <<< "$(e58_task $SLURM_ARRAY_TASK_ID)"
echo "task $SLURM_ARRAY_TASK_ID: $KEY ($NGPU GPU) on $(hostname)"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
[ "$(nvidia-smi -L | wc -l)" -ge "$NGPU" ] || { echo "allocated fewer than $NGPU GPUs: submit with --gres=gpu:$NGPU"; exit 4; }
source $FS_HF/bin/activate
for EXP in e39 e42; do
  python $CODE/scripts/judge_vllm.py --model $KEY --exp $EXP --run $RUN --weights $MODELS_DIR/$KEY
done
echo "JUDGE TASK OK: $KEY"
