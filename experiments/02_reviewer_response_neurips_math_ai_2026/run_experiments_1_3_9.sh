#!/usr/bin/env bash
# Run variance-reduction experiments selected from proposal list:
# 1) Prompt Template Ablation
# 3) Self-Consistency Aggregation
# 9) Cross-Judge Ensemble

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODEL_DEFAULT="${MODEL_DEFAULT:-gpt-5.3-codex}"
MAX_FILES="${MAX_FILES:-0}"
SEED="${SEED:-42}"
REPEATS="${REPEATS:-3}"
JUDGE_MODE="${JUDGE_MODE:-api}"
JUDGES="${JUDGES:-gpt-5.3-codex:P1_BASELINE,gpt-5.3-codex:P4_CHECKLIST,claude-sonnet-4-20250514:P8_STRICT_B}"

mkdir -p results

echo "============================================================"
echo "Running selected variance experiments (1,3,9)"
echo "model=${MODEL_DEFAULT} mode=${JUDGE_MODE} max_files=${MAX_FILES} repeats=${REPEATS} seed=${SEED}"
echo "============================================================"

python exp10_prompt_template_ablation.py \
  --model "$MODEL_DEFAULT" \
  --judge-mode "$JUDGE_MODE" \
  --n-repeats "$REPEATS" \
  --max-files "$MAX_FILES" \
  --seed "$SEED" \
  --results-dir "$SCRIPT_DIR/results/prompt_template_ablation"

python exp11_self_consistency_sweep.py \
  --model "$MODEL_DEFAULT" \
  --judge-mode "$JUDGE_MODE" \
  --max-files "$MAX_FILES" \
  --seed "$SEED" \
  --k-values "1,3,5,7" \
  --results-dir "$SCRIPT_DIR/results/self_consistency_sweep"

python exp12_cross_judge_ensemble.py \
  --judge-mode "$JUDGE_MODE" \
  --n-repeats "$REPEATS" \
  --max-files "$MAX_FILES" \
  --seed "$SEED" \
  --judges "$JUDGES" \
  --results-dir "$SCRIPT_DIR/results/cross_judge_ensemble"

echo "Done. Results:"
echo "  $SCRIPT_DIR/results/prompt_template_ablation"
echo "  $SCRIPT_DIR/results/self_consistency_sweep"
echo "  $SCRIPT_DIR/results/cross_judge_ensemble"
