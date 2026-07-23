#!/bin/bash
# run_config.sh MODEL PROMPT TAG
# Scores ONE judge config via exp16 with an isolated cache + out-dir so many can
# run in parallel without colliding. Resumable (exp16 judge cache). Writes
# detail_rows.csv that pass2_analysis.py consumes.
set -u
MODEL="$1"; PROMPT="$2"; TAG="$3"
D="$HOME/cert-judge/experiments/24_expanded_panel_cli/results"
mkdir -p "$D/cfg_$TAG"
export CERT_JUDGE_CACHE_PATH="$D/cache_$TAG.json"
export CERT_JUDGE_CLI_FAILLOG="$D/cli_failures_$TAG.log"
cd "$HOME/cert-judge/experiments/04_veribench_validation" || exit 3
python3 exp16_multi_judge_human_sets.py \
  --judges "llm:$MODEL:$PROMPT" \
  --judge-repeats 3 --repeat-agg mean --seed 42 \
  --out-dir "$D/cfg_$TAG" \
  --bootstrap-iters 200 --perm-iters 200 --plot-error-bars off \
  > "$D/cfg_$TAG/run.log" 2>&1
echo "DONE $TAG rc=$? $(date +%H:%M:%S)"
