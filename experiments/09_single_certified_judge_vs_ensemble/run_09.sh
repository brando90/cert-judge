#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP="$ROOT/experiments/09_single_certified_judge_vs_ensemble"

python "$EXP/run_analysis.py" \
  --detail-csv "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv" \
  --exp06-summary "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/summary.json" \
  --exp07-summary "$ROOT/experiments/07_property_vs_expected_behavior_corr/full_run/median/summary.json" \
  --out-dir "$EXP/full_run/median" \
  --label median \
  --bootstrap-iters 10000 \
  --perm-iters 20000 \
  --seed 42

python "$EXP/run_analysis.py" \
  --detail-csv "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/detail_rows.csv" \
  --exp06-summary "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/summary.json" \
  --exp07-summary "$ROOT/experiments/07_property_vs_expected_behavior_corr/full_run/mean/summary.json" \
  --out-dir "$EXP/full_run/mean" \
  --label mean \
  --bootstrap-iters 10000 \
  --perm-iters 20000 \
  --seed 42

python "$EXP/run_analysis.py" \
  --detail-csv "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv" \
  --exp06-summary "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/summary.json" \
  --exp07-summary "$ROOT/experiments/07_property_vs_expected_behavior_corr/full_run/median/summary.json" \
  --out-dir "$EXP/smoke" \
  --label smoke \
  --bootstrap-iters 500 \
  --perm-iters 0 \
  --seed 42

echo "Wrote:"
echo "  $EXP/full_run/median"
echo "  $EXP/full_run/mean"
echo "  $EXP/smoke"
