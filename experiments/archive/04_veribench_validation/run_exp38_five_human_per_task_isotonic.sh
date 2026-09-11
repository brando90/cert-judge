#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_exp38_five_human_per_task_isotonic}"
PAPER_FIG_DIR="${PAPER_FIG_DIR:-$SCRIPT_DIR/../../paper_latex/TMLR_2026/figures/exp38_five_human_per_task_isotonic}"
PLOTS_ONLY="${PLOTS_ONLY:-0}"

echo "============================================================"
echo "EXP38 Five-Rater Mean + Per-Task Isotonic"
echo "out_dir=$OUT_DIR"
echo "paper_fig_dir=$PAPER_FIG_DIR"
echo "plots_only=$PLOTS_ONLY"
echo "============================================================"

ARGS=(
  --out-dir "$OUT_DIR"
  --paper-fig-dir "$PAPER_FIG_DIR"
)
if [[ "$PLOTS_ONLY" == "1" ]]; then
  ARGS+=(--plots-only)
fi

python -u exp38_five_human_per_task_isotonic.py "${ARGS[@]}"

echo "Done."
echo "  $OUT_DIR/summary.json"
echo "  $OUT_DIR/REPORT.md"
echo "  $OUT_DIR/plots/"
