#!/bin/bash
# AT-2184: Qwen3-14B human-mix SFT pilot, exp 63 recipe, 3 seeds, one A100-80GB each, val-only freeze, no test pack
R=/lfs/skampere1/0/brando9/at2184
cd $R
PY=/lfs/skampere1/0/brando9/at1445/venv/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True WANDB_MODE=offline
for spec in 0:0 5:1 6:2; do
  g=${spec%%:*}; s=${spec##*:}
  CUDA_VISIBLE_DEVICES=$g $PY sft_lora.py --model /dfs/scratch0/brando9/e62/models/Qwen3-14B --ngpu 1 --pack pack_trainval.jsonl \
    --out runs/sft_q3_14b_hm_s$s --seed $s --epochs 4 --human_mix 0.5 --name q3_14b_hm_s$s > runs/sft_q3_14b_hm_s$s.log 2>&1 &
done
wait
echo "all done $(date)" > runs/ALL.done
