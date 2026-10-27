#!/bin/bash
# mercury1: overfit test (GPUs 0-2) and SFT seed 0 (GPUs 3-5)
cd /dfs/scratch0/brando9/e62
rm -rf runs/sft_overfit runs/sft_q3_8b_s0
PY=/lfs/mercury1/0/brando9/at979/venv128/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True E62_EXTRA_LIBS=/lfs/mercury1/0/brando9/e62_pylibs_m WANDB_MODE=offline
COMMON="--model /dfs/scratch0/brando9/e62/models/Qwen3-8B --ngpu 3 --pack pack_trainval.jsonl"
CUDA_VISIBLE_DEVICES=0,1,2 nohup setsid $PY sft_lora.py $COMMON --out runs/sft_overfit --overfit_n 4 --overfit_steps 15 --name overfit_test > runs/sft_overfit.log 2>&1 < /dev/null &
CUDA_VISIBLE_DEVICES=3,4,5 nohup setsid $PY sft_lora.py $COMMON --out runs/sft_q3_8b_s0 --seed 0 --epochs 4 --name sft_s0 > runs/sft_q3_8b_s0.log 2>&1 < /dev/null &
sleep 1; echo launched m1
