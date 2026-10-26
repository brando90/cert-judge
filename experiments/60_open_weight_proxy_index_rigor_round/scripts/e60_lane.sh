#!/bin/bash
# TLDR: experiment 60 lane: for each spec, wait for the GPU to be empty, fetch weights, run judge60.py on E39 cells, delete weights.
# Usage: e60_lane.sh <gpu index> <venv dir> <specs comma list>   spec = model[:prompts][@seed]  (e.g. qwen3_32b:D0+R4@0, q25_14b_awq@2; seed 0 = experiment 58's seed)
# Runs go to $W/runs60/seed<S>; resumable (the driver skips finished cells). Always release the GPU: nothing stays loaded after a spec.
GPU=$1; VENV=$2; SPECS=$3
W=/lfs/skampere1/0/brando9/at1209
C58=$W/code/experiments/58_open_weight_judges_on_e39_e42_probes
C60=$W/code/experiments/60_open_weight_proxy_index_rigor_round
WT=/dfs/scratch0/brando9/at1209_hf
mkdir -p $WT $W/logs60
export E58_VERIBENCH_REPO=$C58/private/veribench_min HF_HOME=/dfs/scratch0/brando9/at1209_hf_cache TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4
export CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=$C60/scripts
for spec in ${SPECS//,/ }; do
  S=0; [[ "$spec" == *@* ]] && { S=${spec##*@}; spec=${spec%@*}; }
  m=${spec%%:*}; P=all; [[ "$spec" == *:* ]] && P=${spec#*:}; P=${P//+/,}
  RUN=$W/runs60/seed$S; mkdir -p $RUN
  if [ "$S" != 0 ]; then export E60_SEED=$((58 + S * 1000)); else unset E60_SEED; fi
  for i in $(seq 1 72); do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU | head -1)
    [ "${used:-99999}" -lt 500 ] && break
    echo "$(date -Is) GPU $GPU busy ($used MiB), waiting before $m"; sleep 300
  done
  echo "$(date -Is) START $m prompts=$P seed=$S"
  $VENV/bin/python $C60/scripts/fetch60.py --dir $WT --models $m || { echo "FETCH FAILED $m"; continue; }
  $VENV/bin/python $C60/scripts/judge60.py --model $m --exp e39 --run $RUN --weights $WT/$m --prompts $P > $W/logs60/judge_${m}_s$S.log 2>&1
  echo "$(date -Is) END $m seed=$S exit $?"
  rm -rf $WT/$m
done
echo "$(date -Is) LANE DONE"
