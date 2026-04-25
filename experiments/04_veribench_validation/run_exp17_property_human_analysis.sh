#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

EXP16_SUMMARY="${EXP16_SUMMARY:-$SCRIPT_DIR/results_exp16_multi_judge_human_sets/summary.json}"
OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_exp17_property_human_analysis}"
LABEL_SET="${LABEL_SET:-avg}"
PERM_ITERS="${PERM_ITERS:-20000}"
SEED="${SEED:-42}"
BAD_JUDGE_PATTERN="${BAD_JUDGE_PATTERN:-BAD_STRINGY}"

echo "============================================================"
echo "EXP17 Property-Human Analysis"
echo "exp16_summary=$EXP16_SUMMARY"
echo "out_dir=$OUT_DIR"
echo "label_set=$LABEL_SET perm_iters=$PERM_ITERS seed=$SEED"
echo "bad_judge_pattern=$BAD_JUDGE_PATTERN"
echo "============================================================"

python -u exp17_property_human_analysis.py \
  --exp16-summary "$EXP16_SUMMARY" \
  --out-dir "$OUT_DIR" \
  --label-set "$LABEL_SET" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED" \
  --bad-judge-pattern "$BAD_JUDGE_PATTERN"

echo "Done."
echo "  $OUT_DIR/summary.json"
echo "  $OUT_DIR/per_property_correlations.csv"
echo "  $OUT_DIR/partial_correlations.csv"
echo "  $OUT_DIR/regression_summary.json"
echo "  $OUT_DIR/fig_property_vs_human_bars.png"
