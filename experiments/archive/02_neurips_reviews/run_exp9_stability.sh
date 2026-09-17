#!/usr/bin/env bash
# Run Experiment 9 (P4 Stability) on VeriBench.
#
# Usage:
#   bash run_exp9_stability.sh pilot
#   bash run_exp9_stability.sh full
#
# Optional env overrides:
#   MODEL=gpt-5.3-codex
#   N_REPEATS=5
#   PROMPT_NAMES="P1_BASELINE,P2_FORMAL,P4_CHECKLIST,P8_STRICT_B"
#   VERIBENCH_ROOT=/abs/path/to/veribench
#   OUT_TAG=mytag

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${1:-pilot}" # pilot|full
MODEL="${MODEL:-gpt-5.3-codex}"
N_REPEATS="${N_REPEATS:-5}"
PROMPT_NAMES="${PROMPT_NAMES:-P1_BASELINE,P2_FORMAL,P4_CHECKLIST,P8_STRICT_B}"
VERIBENCH_ROOT="${VERIBENCH_ROOT:-$SCRIPT_DIR/../../../data/veribench_dataset/lean_src/veribench}"
APPEND_VERIBENCH_ROOT="${APPEND_VERIBENCH_ROOT:-$SCRIPT_DIR/../../../data/veribench_dataset_newest/lean_src/veribench}"
OUT_TAG="${OUT_TAG:-}"
JUDGE_MODE="${JUDGE_MODE:-api}" # api|local
APPEND_MAX_FILES="${APPEND_MAX_FILES:-}"

case "$MODE" in
  pilot)
    MAX_FILES="${MAX_FILES:-20}"
    APPEND_MAX_FILES="${APPEND_MAX_FILES:-0}"
    ;;
  full)
    MAX_FILES="${MAX_FILES:-0}" # 0 => all files
    APPEND_MAX_FILES="${APPEND_MAX_FILES:-34}"
    ;;
  *)
    echo "Unknown mode: $MODE (expected: pilot|full)"
    exit 1
    ;;
esac

if [ ! -d "$VERIBENCH_ROOT" ]; then
  echo "ERROR: VeriBench root not found: $VERIBENCH_ROOT"
  exit 1
fi

# Activate env if available.
if [ -f "$HOME/uv_envs/cert-judge/bin/activate" ]; then
  # shellcheck disable=SC1090
  source "$HOME/uv_envs/cert-judge/bin/activate"
fi

# Keep matplotlib/font cache writable in sandboxed environments.
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

if [ "$JUDGE_MODE" = "api" ]; then
  # Load OpenAI key if not already set.
  if [ -z "${OPENAI_API_KEY:-}" ] && [ -f "$HOME/keys/openai_api_brandos_personal_key.txt" ]; then
    export OPENAI_API_KEY
    OPENAI_API_KEY="$(cat "$HOME/keys/openai_api_brandos_personal_key.txt")"
  fi

  if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: OPENAI_API_KEY is not set."
    echo "Set it in your shell or place key at ~/keys/openai_api_brandos_personal_key.txt"
    exit 1
  fi
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
SAFE_MODEL="${MODEL//./}"
RUN_NAME="stability_${SAFE_MODEL}_${MODE}_${STAMP}"
if [ -n "$OUT_TAG" ]; then
  RUN_NAME="${RUN_NAME}_${OUT_TAG}"
fi

RESULTS_DIR="$SCRIPT_DIR/results/$RUN_NAME"
FIGURES_DIR="$SCRIPT_DIR/figures/$RUN_NAME"

echo "============================================================"
echo "EXP9 Stability Run"
echo " mode=$MODE"
echo " model=$MODEL"
echo " judge_mode=$JUDGE_MODE"
echo " repeats=$N_REPEATS"
echo " max_files=$MAX_FILES"
echo " prompts=$PROMPT_NAMES"
echo " veribench_root=$VERIBENCH_ROOT"
echo " append_veribench_root=$APPEND_VERIBENCH_ROOT"
echo " append_max_files=$APPEND_MAX_FILES"
echo " results_dir=$RESULTS_DIR"
echo " figures_dir=$FIGURES_DIR"
echo "============================================================"

python exp9_stability.py \
  --model "$MODEL" \
  --judge-mode "$JUDGE_MODE" \
  --n-repeats "$N_REPEATS" \
  --max-files "$MAX_FILES" \
  --prompt-names "$PROMPT_NAMES" \
  --veribench-root "$VERIBENCH_ROOT" \
  --append-veribench-root "$APPEND_VERIBENCH_ROOT" \
  --append-max-files "$APPEND_MAX_FILES" \
  --results-dir "$RESULTS_DIR" \
  --figures-dir "$FIGURES_DIR"

echo ""
echo "Done."
echo "Summary: $RESULTS_DIR/summary.json"
