#!/bin/bash
# E62 test scoring on mercury1: frozen adapters on pack_test (one pass each, no refit)
cd /dfs/scratch0/brando9/e62
PY=/lfs/mercury1/0/brando9/at979/venv128/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True E62_EXTRA_LIBS=/lfs/mercury1/0/brando9/e62_pylibs_m WANDB_MODE=offline
M="--model /dfs/scratch0/brando9/e62/models/Qwen3-8B --ngpu 3 --eval_pack pack_test.jsonl --name test"
ev() { # gpus run epoch
  CUDA_VISIBLE_DEVICES=$1 $PY sft_lora.py $M --adapter runs/$2/ep$3 --out runs/$2 >> runs/eval_test_$2.log 2>&1
}
(ev 0,1,2 sft_q3_8b_s0 4; ev 0,1,2 sft_q3_8b_hm_s0 3; ev 0,1,2 rl_q3_8b_s0 3) > /dev/null 2>&1 &
(ev 3,4,5 sft_q3_8b_s1 2; ev 3,4,5 sft_q3_8b_hm_s1 4; ev 3,4,5 rl_q3_8b_s1 3) > /dev/null 2>&1 &
(ev 6,7,8 sft_q3_8b_s2 3; ev 6,7,8 rl_q3_8b_s2 3; ev 6,7,8 sft_q3_8b_shuf_s0 2) > /dev/null 2>&1 &
wait
echo done > runs/eval_m1.done
