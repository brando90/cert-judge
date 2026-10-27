#!/bin/bash
# mercury2: shuffled-label control (GPUs 4-6) and SFT seed 1 (GPUs 7-9)
cd /dfs/scratch0/brando9/e62
rm -rf runs/sft_q3_8b_s1 runs/sft_q3_8b_shuf_s0
PY=/lfs/mercury2/0/brando9/at979/venv128/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True E62_EXTRA_LIBS=/tmp/e62/e62_pylibs_m WANDB_MODE=offline
COMMON="--model /dfs/scratch0/brando9/e62/models/Qwen3-8B --ngpu 3 --pack pack_trainval.jsonl"
CUDA_VISIBLE_DEVICES=4,5,6 nohup setsid $PY sft_lora.py $COMMON --out runs/sft_q3_8b_shuf_s0 --seed 0 --epochs 2 --shuffle_labels --name sft_shuffled_control > runs/sft_q3_8b_shuf_s0.log 2>&1 < /dev/null &
CUDA_VISIBLE_DEVICES=7,8,9 nohup setsid $PY sft_lora.py $COMMON --out runs/sft_q3_8b_s1 --seed 1 --epochs 4 --name sft_s1 > runs/sft_q3_8b_s1.log 2>&1 < /dev/null &
sleep 1; echo launched m2
