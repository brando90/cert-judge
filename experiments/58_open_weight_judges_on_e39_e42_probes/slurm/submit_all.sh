#!/bin/bash
# TLDR: submit the experiment 58 judging jobs on FarmShare after the smoke passed: one array for the 1-GPU models (%4) and one
# for the 2-GPU models (%2), so at most 4 GPUs run at once (QOS gpu: 4 GPUs, 32 submitted). Prints and saves every job id.
# usage: bash submit_all.sh                    (all 13 models)
#        ONLY="0 1 2 3" bash submit_all.sh     (only these task indices of tasks.tsv, e.g. the cheap 1-GPU first)
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd $E58_HOME
D=$CODE/slurm
USED=$(squeue -r -h -u $USER -q gpu | wc -l)
echo "GPU tasks already queued/running for $USER on QOS gpu: $USED (limit 32 submitted, 4 running); this submits at most 13"
[ $(( USED + 13 )) -le 32 ] || { echo "not enough QOS gpu room: set ONLY to a part that fits"; exit 3; }
ONE=(); TWO=()
i=0
while read KEY NGPU; do
  if [ -z "${ONLY:-}" ] || [[ " $ONLY " == *" $i "* ]]; then
    if [ "$NGPU" = 1 ]; then ONE+=($i); else TWO+=($i); fi
  fi
  i=$((i+1))
done < $D/tasks.tsv
join() { local IFS=,; echo "$*"; }
if [ ${#ONE[@]} -gt 0 ]; then
  A=$(sbatch --parsable --gres=gpu:1 --array=$(join "${ONE[@]}")%4 $D/run_model.sbatch)
  echo "$(date -Is) 1-GPU models array=$A tasks=$(join "${ONE[@]}")" | tee -a $E58_HOME/job_ids.txt
fi
if [ ${#TWO[@]} -gt 0 ]; then
  B=$(sbatch --parsable --gres=gpu:2 --array=$(join "${TWO[@]}")%2 $D/run_model.sbatch)
  echo "$(date -Is) 2-GPU models array=$B tasks=$(join "${TWO[@]}")" | tee -a $E58_HOME/job_ids.txt
fi
echo "collect when both are COMPLETED: bash $D/collect.sh"
