#!/bin/bash
# E62 test scoring on mercury2 (free GPUs 4-9): prompt arm (frozen addenda) and zero-shot baseline via vLLM
cd /dfs/scratch0/brando9/e62
PY=/lfs/mercury2/0/brando9/at979/venv128/bin/python
export E62_EXTRA_LIBS=/tmp/e62/e62_pylibs_m
$PY - <<'PYEOF'
import json
for s in (0,1):
    open(f"runs/arm1_q3_8b_s{s}/frozen_addendum.txt","w").write(json.load(open(f"runs/arm1_q3_8b_s{s}/FROZEN.json"))["frozen"]["addendum"])
open("runs/empty_addendum.txt","w").write("")
PYEOF
M=/dfs/scratch0/brando9/e62/models/Qwen3-8B
CUDA_VISIBLE_DEVICES=4,5 $PY vllm_eval.py --model $M --tp 2 --pack pack_test.jsonl --out runs/arm1_q3_8b_s0/eval_test.json --addendum runs/arm1_q3_8b_s0/frozen_addendum.txt > runs/eval_test_arm1_s0.log 2>&1 &
CUDA_VISIBLE_DEVICES=6,7 $PY vllm_eval.py --model $M --tp 2 --pack pack_test.jsonl --out runs/arm1_q3_8b_s1/eval_test.json --addendum runs/arm1_q3_8b_s1/frozen_addendum.txt > runs/eval_test_arm1_s1.log 2>&1 &
CUDA_VISIBLE_DEVICES=8,9 $PY vllm_eval.py --model $M --tp 2 --pack pack_test.jsonl --out runs/base_q3_8b_test.json > runs/eval_test_base.log 2>&1 &
wait
echo done > runs/eval_m2.done
