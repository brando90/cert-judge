#!/bin/bash
# usage: lane.sh <node m1|m2> <gpus> <name:seed:hm> [<name:seed:hm> ...]   train (freezes on val automatically) then one test pass, same script as E63
cd /dfs/scratch0/brando9/e62
node=$1; gpus=$2; shift 2
if [ $node = m1 ]; then PY=/lfs/mercury1/0/brando9/at979/venv128/bin/python; LIBS=/lfs/mercury1/0/brando9/e62_pylibs_m; else PY=/lfs/mercury2/0/brando9/at979/venv128/bin/python; LIBS=/tmp/e62/e62_pylibs_m; fi
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True E62_EXTRA_LIBS=$LIBS WANDB_MODE=offline
M="--model /dfs/scratch0/brando9/e62/models/Qwen3-8B --ngpu 3"
for spec in "$@"; do
  IFS=: read name seed hm <<< "$spec"
  out=runs/$name
  if [ ! -f $out/FROZEN.json ]; then
    rm -rf $out
    hmarg=""; [ "$hm" = "1" ] && hmarg="--human_mix 0.5"
    CUDA_VISIBLE_DEVICES=$gpus $PY sft_lora.py $M --pack pack_trainval.jsonl --out $out --seed $seed --epochs 4 $hmarg --name ${name#sft_q3_8b_} > runs/$name.log 2>&1
  fi
  if [ -f $out/FROZEN.json ]; then
    ep=$($PY -c "import json;print(json.load(open('$out/FROZEN.json'))['frozen_epoch'])")
    CUDA_VISIBLE_DEVICES=$gpus $PY sft_lora.py $M --eval_pack pack_test.jsonl --name test --adapter $out/ep$ep --out $out >> runs/eval_test_$name.log 2>&1
  fi
  echo "$name done $(date)" >> runs/e64_lanes.done
done
