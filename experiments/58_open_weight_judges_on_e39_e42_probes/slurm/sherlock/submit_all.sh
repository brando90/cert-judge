#!/bin/bash
# TLDR: Sherlock fallback submit: 1-GPU models array (%4) and 2-GPU models array (%2) with -G set per group; ids saved to $B/jobs.txt.
# usage: bash submit_all.sh            (ONLY="0 1 2" bash submit_all.sh for a subset of tasks.tsv indices)
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd $B
D=$CODE/slurm/sherlock
ONE=(); TWO=(); i=0
while read KEY NGPU; do
  if [ -z "${ONLY:-}" ] || [[ " $ONLY " == *" $i "* ]]; then if [ "$NGPU" = 1 ]; then ONE+=($i); else TWO+=($i); fi; fi
  i=$((i+1))
done < $CODE/slurm/tasks.tsv
join() { local IFS=,; echo "$*"; }
[ ${#ONE[@]} -gt 0 ] && echo "$(date -Is) 1-GPU $(sbatch --parsable -G 1 --array=$(join "${ONE[@]}")%4 $D/run_model.sbatch)" | tee -a $B/jobs.txt
[ ${#TWO[@]} -gt 0 ] && echo "$(date -Is) 2-GPU $(sbatch --parsable -G 2 --array=$(join "${TWO[@]}")%2 $D/run_model.sbatch)" | tee -a $B/jobs.txt
echo "collect: bash $D/collect.sh"
