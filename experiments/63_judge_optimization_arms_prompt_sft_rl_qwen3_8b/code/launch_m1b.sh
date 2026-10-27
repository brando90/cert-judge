#!/bin/bash
# mercury1: RL pilot (GPUs 0-2) and human-mix SFT (GPUs 6-8)
cd /dfs/scratch0/brando9/e62
rm -rf runs/rl_q3_8b_s0 runs/sft_q3_8b_hm_s0
PY=/lfs/mercury1/0/brando9/at979/venv128/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True E62_EXTRA_LIBS=/lfs/mercury1/0/brando9/e62_pylibs_m WANDB_MODE=offline
COMMON="--model /dfs/scratch0/brando9/e62/models/Qwen3-8B --ngpu 3 --pack pack_trainval.jsonl"
CUDA_VISIBLE_DEVICES=0,1,2 nohup setsid $PY sft_lora.py $COMMON --out runs/rl_q3_8b_s0 --seed 0 --loss grpo --lr 5e-5 --epochs 3 --name rl_s0 > runs/rl_q3_8b_s0.log 2>&1 < /dev/null &
CUDA_VISIBLE_DEVICES=6,7,8 nohup setsid $PY sft_lora.py $COMMON --out runs/sft_q3_8b_hm_s0 --seed 0 --epochs 4 --human_mix 0.5 --name sft_hm_s0 > runs/sft_q3_8b_hm_s0.log 2>&1 < /dev/null &
sleep 1; echo launched m1b
