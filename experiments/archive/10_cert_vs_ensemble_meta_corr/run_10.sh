#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXP="$ROOT/experiments/10_cert_vs_ensemble_meta_corr"

python "$EXP/run_analysis.py" \
  --exp06-summary "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/summary.json" \
  --exp09-summary "$ROOT/experiments/09_single_certified_judge_vs_ensemble/full_run/median/summary.json" \
  --out-dir "$EXP/full_run/median" \
  --label median

python "$EXP/run_analysis.py" \
  --exp06-summary "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/summary.json" \
  --exp09-summary "$ROOT/experiments/09_single_certified_judge_vs_ensemble/full_run/mean/summary.json" \
  --out-dir "$EXP/full_run/mean" \
  --label mean

python "$EXP/run_analysis.py" \
  --exp06-summary "$ROOT/experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/summary.json" \
  --exp09-summary "$ROOT/experiments/09_single_certified_judge_vs_ensemble/smoke/summary.json" \
  --out-dir "$EXP/smoke" \
  --label smoke

echo "Wrote:"
echo "  $EXP/full_run/median"
echo "  $EXP/full_run/mean"
echo "  $EXP/smoke"
