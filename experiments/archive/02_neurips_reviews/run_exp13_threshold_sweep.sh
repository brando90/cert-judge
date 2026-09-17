#!/usr/bin/env bash
# Run Experiment 13: threshold calibration sweep

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

MODEL="${MODEL:-gpt-5.3-codex}"
JUDGE_MODE="${JUDGE_MODE:-api}"
PROMPT_NAME="${PROMPT_NAME:-P8_STRICT_B}"
MAX_FILES="${MAX_FILES:-30}"
REPEATS="${REPEATS:-3}"
SEED="${SEED:-42}"
THRESHOLDS="${THRESHOLDS:-0.6,0.65,0.7,0.75,0.8,0.85}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-1000}"
RESULTS_DIR="${RESULTS_DIR:-$SCRIPT_DIR/results/threshold_calibration_sweep}"
FIGURES_DIR="${FIGURES_DIR:-$SCRIPT_DIR/figures/threshold_calibration_sweep}"
VERIBENCH_ROOT="${VERIBENCH_ROOT:-$SCRIPT_DIR/../../../data/veribench_dataset/lean_src/veribench}"

echo "============================================================"
echo "EXP13 Threshold Calibration Sweep"
echo "model=${MODEL} mode=${JUDGE_MODE} prompt=${PROMPT_NAME}"
echo "max_files=${MAX_FILES} repeats=${REPEATS} thresholds=${THRESHOLDS}"
echo "bootstrap_iters=${BOOTSTRAP_ITERS}"
echo "veribench_root=${VERIBENCH_ROOT}"
echo "============================================================"

python exp13_threshold_calibration_sweep.py \
  --model "$MODEL" \
  --judge-mode "$JUDGE_MODE" \
  --prompt-name "$PROMPT_NAME" \
  --max-files "$MAX_FILES" \
  --n-repeats "$REPEATS" \
  --seed "$SEED" \
  --thresholds "$THRESHOLDS" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --veribench-root "$VERIBENCH_ROOT" \
  --results-dir "$RESULTS_DIR" \
  --figures-dir "$FIGURES_DIR"

echo "Done."
echo "  Summary: $RESULTS_DIR/summary.json"
echo "  Table:   $RESULTS_DIR/threshold_metrics.csv"
echo "  Figure:  $FIGURES_DIR/threshold_stability_curve.png"
