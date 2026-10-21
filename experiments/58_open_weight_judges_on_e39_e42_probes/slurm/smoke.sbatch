#!/bin/bash
# TLDR: experiment 58 smoke on FarmShare: Qwen3-4B (1 L40S), 10 cells of each of two prompt configurations (R4, P1) = 20 cells, E39 probes;
# loads vLLM, generates, parses with E39's parsers, writes harvests, prints measured/parse counts and tokens/s (the number that
# replaces the assumptions in GPU_HOURS.md). Run it before the array: sbatch smoke.sbatch
#SBATCH -J e58_smoke
#SBATCH -p gpu
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -o /home/users/%u/e58/logs/%x_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=brandojazz@gmail.com,brando.science@gmail.com
set -euo pipefail
source $HOME/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/env.sh
SMOKE=$E58_HOME/runs/smoke
echo "smoke on $(hostname)"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
source $FS_HF/bin/activate
python $CODE/scripts/judge_vllm.py --model qwen3_4b --exp e39 --run $SMOKE --weights $MODELS_DIR/qwen3_4b --prompts R4,P1 --limit-cells 10
python - <<PY
import json, glob
for f in sorted(glob.glob("$SMOKE/harvest/e39/*.json")):
    h = json.load(open(f)); print(h["config"], h["status_counts"])
for f in sorted(glob.glob("$SMOKE/raw/e39/qwen3_4b/*.meta.json")):
    m = json.load(open(f)); t = m["timing"][-1]
    print(f.split("/")[-1], "output tokens", t["output_tokens"], "seconds", t["seconds"], "tok/s", round(t["output_tokens"] / max(t["seconds"], 1), 1), "engine", m["engine"]["vllm"], m["engine"]["gpu"])
PY
echo "SMOKE OK"
