#!/bin/bash
# TLDR: experiment 61 lane: wait for the GPUs to be empty, fetch one model, run run61.py over the rendered E43 prompts, delete the weights.
# Usage: e61_lane.sh <gpu list, e.g. 0 or 2,3> <model> ; resumable. Run on mercury2 (W below).
GPUS=$1; M=$2
W=/lfs/mercury2/0/brando9/at1209
C61=$W/code/experiments/61_open_weight_judges_on_e43_gaming_candidates
VENV=/lfs/mercury2/0/brando9/at979/venv128
WT=/dfs/scratch0/brando9/at1209_hf
RUN=$W/runs61
mkdir -p $WT $RUN $W/logs61
export HF_HOME=/dfs/scratch0/brando9/at1209_hf_cache TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4 PYTHONPATH=$C61/scripts
export E58_VERIBENCH_REPO=$W/code/experiments/58_open_weight_judges_on_e39_e42_probes/private/veribench_min
export CUDA_VISIBLE_DEVICES=$GPUS E61_GPU_UTIL=${E61_GPU_UTIL:-}
for i in $(seq 1 72); do
  busy=0
  for g in ${GPUS//,/ }; do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g | head -1); [ "${u:-99999}" -ge 500 ] && busy=1; done
  [ $busy = 0 ] && break
  echo "$(date -Is) GPUs $GPUS busy, waiting before $M"; sleep 300
done
echo "$(date -Is) START $M gpus=$GPUS"
$VENV/bin/python $C61/scripts/fetch61.py --dir $WT --models $M || { echo "FETCH FAILED $M"; exit 1; }
$VENV/bin/python $C61/scripts/run61.py --model $M --prompts $C61/results/prompts61.jsonl --run $RUN --weights $WT/$M > $W/logs61/run_$M.log 2>&1
echo "$(date -Is) END $M exit $?"
rm -rf $WT/$M
echo "$(date -Is) LANE DONE $M"
