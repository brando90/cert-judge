#!/bin/bash
# TLDR: experiment 59 stage-1 lane: for each model, wait for the GPU to be empty, fetch weights, run judge59.py on E39 cells, delete weights.
# Usage: e59_lane.sh <gpu index> <venv dir> <run dir> <models comma list, each "model" or "model:prompts">   (nohup setsid, resumable: finished prompts are skipped by the driver)
GPU=$1; VENV=$2; RUN=$3; MODELS=$4
W=/lfs/skampere1/0/brando9/at1209
[ -d "$W" ] || W=/lfs/mercury2/0/brando9/at1209
C58=$W/code/experiments/58_open_weight_judges_on_e39_e42_probes
C59=$W/code/experiments/59_open_weight_proxy_index_and_frontier_fit
WT=/dfs/scratch0/brando9/at1209_hf
mkdir -p $WT $RUN $W/logs
export E58_VERIBENCH_REPO=$C58/private/veribench_min HF_HOME=/dfs/scratch0/brando9/at1209_hf_cache TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4
export CUDA_VISIBLE_DEVICES=$GPU
export PYTHONPATH=$C59/scripts
for spec in ${MODELS//,/ }; do
  m=${spec%%:*}; P=all; [[ "$spec" == *:* ]] && P=${spec#*:}   # "model" or "model:prompt list" (e.g. llama33_70b_awq:H2)
  for i in $(seq 1 72); do   # up to 6 h of waiting for an empty GPU
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU | head -1)
    [ "${used:-99999}" -lt 500 ] && break
    echo "$(date -Is) GPU $GPU busy ($used MiB), waiting before $m"; sleep 300
  done
  echo "$(date -Is) START $m"
  $VENV/bin/python $C59/scripts/fetch59.py --dir $WT --models $m || { echo "FETCH FAILED $m"; continue; }
  $VENV/bin/python $C59/scripts/judge59.py --model $m --exp e39 --run $RUN --weights $WT/$m --prompts $P > $W/logs/judge_$m.log 2>&1
  echo "$(date -Is) END $m exit $?"
  rm -rf $WT/$m
done
echo "$(date -Is) LANE DONE"
