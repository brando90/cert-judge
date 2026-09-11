#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

RESULTS_DIR="${RESULTS_DIR:-$SCRIPT_DIR/results}"
OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_multi_judge_trend}"
JUDGE_REPEATS="${JUDGE_REPEATS:-3}"
THRESHOLD="${THRESHOLD:-0.85}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-5000}"
PERM_ITERS="${PERM_ITERS:-10000}"
SEED="${SEED:-42}"
JUDGES="${JUDGES:-llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P1_BASELINE,llm:gpt-4o-mini:P8_STRICT_B,editdist:e1:na,random:r1:na}"

echo "============================================================"
echo "EXP14 Multi-Judge Trend"
echo "results_dir=$RESULTS_DIR"
echo "out_dir=$OUT_DIR"
echo "judge_repeats=$JUDGE_REPEATS threshold=$THRESHOLD"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS"
echo "judges=$JUDGES"
echo "============================================================"

python -u exp_multi_judge_trend.py \
  --results-dir "$RESULTS_DIR" \
  --out-dir "$OUT_DIR" \
  --judge-repeats "$JUDGE_REPEATS" \
  --threshold "$THRESHOLD" \
  --seed "$SEED" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --judges "$JUDGES"

echo "Done."
echo "  $OUT_DIR/judge_rows.csv"
echo "  $OUT_DIR/trend_summary.json"
echo "  $OUT_DIR/fig_cert_vs_human_scatter.png"
echo "  $OUT_DIR/fig_human_corr_bars.png"
