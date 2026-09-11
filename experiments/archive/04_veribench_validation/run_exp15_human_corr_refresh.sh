#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

HUMAN_TSV="${HUMAN_TSV:-$SCRIPT_DIR/data/ethan_human_scores_20260425.tsv}"
JUDGE_CSV="${JUDGE_CSV:-$SCRIPT_DIR/../03_human_validation/results/ethan_human_vs_judge/scored_rows.csv}"
OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_exp15_human_corr_refresh}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-10000}"
PERM_ITERS="${PERM_ITERS:-20000}"
SEED="${SEED:-42}"

echo "============================================================"
echo "EXP15 Human Correlation Refresh"
echo "human_tsv=$HUMAN_TSV"
echo "judge_csv=$JUDGE_CSV"
echo "out_dir=$OUT_DIR"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS seed=$SEED"
echo "============================================================"

python -u exp15_human_corr_refresh.py \
  --human-tsv "$HUMAN_TSV" \
  --judge-csv "$JUDGE_CSV" \
  --out-dir "$OUT_DIR" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED"

echo "Done."
echo "  $OUT_DIR/summary.json"
echo "  $OUT_DIR/results_summary.md"
echo "  $OUT_DIR/merged_rows.csv"
echo "  $OUT_DIR/missing_pairs.csv"
echo "  $OUT_DIR/fig_human_vs_judge_scatter.png"
echo "  $OUT_DIR/fig_per_split_spearman.png"
