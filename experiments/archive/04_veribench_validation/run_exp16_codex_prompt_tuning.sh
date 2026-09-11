#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_exp16_codex_prompt_tuning_r9_median}"
JUDGE_REPEATS="${JUDGE_REPEATS:-9}"
REPEAT_AGG="${REPEAT_AGG:-median}"
SEED="${SEED:-42}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-5000}"
PERM_ITERS="${PERM_ITERS:-10000}"
CACHE_TAG="${CACHE_TAG:-codex_prompt_tuning_r9_med}"

# Codex-only prompt sweep (no bad baselines)
JUDGES="${JUDGES:-llm:gpt-5.3-codex:P1_BASELINE,llm:gpt-5.3-codex:P2_FORMAL,llm:gpt-5.3-codex:P3_CONCISE,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P14_HUMAN_ALIGN_V2,llm:gpt-5.3-codex:P15_COMPARATIVE_HOLISTIC,llm:gpt-5.3-codex:P16_ERIC_COMPARATIVE_TRACKED,llm:gpt-5.3-codex:P17_COMPARATIVE_RANKFIRST,llm:gpt-5.3-codex:P18_COMPARATIVE_EDGEAWARE,llm:gpt-5.3-codex:P19_COMPARATIVE_CONSERVATIVE_HUMANLIKE,random:r1:na}"

echo "============================================================"
echo "EXP16 Codex Prompt Tuning Sweep"
echo "out_dir=$OUT_DIR"
echo "judge_repeats=$JUDGE_REPEATS repeat_agg=$REPEAT_AGG"
echo "seed=$SEED bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS"
echo "cache_tag=$CACHE_TAG"
echo "judges=$JUDGES"
echo "============================================================"

python -u exp16_multi_judge_human_sets.py \
  --out-dir "$OUT_DIR" \
  --judge-repeats "$JUDGE_REPEATS" \
  --repeat-agg "$REPEAT_AGG" \
  --seed "$SEED" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --cache-tag "$CACHE_TAG" \
  --judges "$JUDGES"

python -u summarize_codex_prompt_tuning.py \
  --judge-rows "$OUT_DIR/judge_rows.csv" \
  --out-md "$OUT_DIR/prompt_tuning_summary.md"

echo "Done."
echo "  $OUT_DIR/judge_rows.csv"
echo "  $OUT_DIR/prompt_tuning_summary.md"
