#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

PASS1_TSV="${PASS1_TSV:-$SCRIPT_DIR/data/ethan_human_scores_20260425.tsv}"
PASS2_TSV="${PASS2_TSV:-$SCRIPT_DIR/data/ethan_human_scores_ORIGINAL.tsv}"
AVG_TSV="${AVG_TSV:-$SCRIPT_DIR/data/ethan_human_scores_avg_two_passes_20260425.tsv}"

# Separate test output root
OUT_ROOT="${OUT_ROOT:-$SCRIPT_DIR/results_exp22_expanded_judges_stable}"
EXP16_OUT="${EXP16_OUT:-$OUT_ROOT/exp16}"
EXP17_PREFIX="${EXP17_PREFIX:-$OUT_ROOT/exp17}"
EXP19_OUT="${EXP19_OUT:-$OUT_ROOT/exp19}"

# Stability-focused defaults
JUDGE_REPEATS="${JUDGE_REPEATS:-9}"
REPEAT_AGG="${REPEAT_AGG:-median}"
THRESHOLD="${THRESHOLD:-0.85}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-10000}"
PERM_ITERS="${PERM_ITERS:-20000}"
SEED="${SEED:-42}"
CACHE_TAG="${CACHE_TAG:-exp22_r${JUDGE_REPEATS}_${REPEAT_AGG}_$(date +%Y%m%d_%H%M%S)}"
PLOT_ERROR_BARS="${PLOT_ERROR_BARS:-off}"

# Expanded judge panel (same-family prompt diversity + cross-family baselines)
JUDGES="${JUDGES:-llm:gpt-5.3-codex:P1_BASELINE,llm:gpt-5.3-codex:P2_FORMAL,llm:gpt-5.3-codex:P3_CONCISE,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P7_STRICT_A,llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P11_JSON_FIRST,llm:gpt-4o-mini:P1_BASELINE,llm:gpt-4o-mini:P4_CHECKLIST,llm:gpt-4o-mini:P8_STRICT_B,llm_bad:gpt-5.3-codex:BAD_STRINGY,editdist:e1:na,random:r1:na}"

echo "============================================================"
echo "EXP22 Expanded Judges Stable Test"
echo "pass1_tsv=$PASS1_TSV"
echo "pass2_tsv=$PASS2_TSV"
echo "avg_tsv=$AVG_TSV"
echo "out_root=$OUT_ROOT"
echo "exp16_out=$EXP16_OUT"
echo "judge_repeats=$JUDGE_REPEATS repeat_agg=$REPEAT_AGG threshold=$THRESHOLD"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS seed=$SEED"
echo "cache_tag=$CACHE_TAG plot_error_bars=$PLOT_ERROR_BARS"
echo "judges=$JUDGES"
echo "============================================================"

mkdir -p "$OUT_ROOT"

echo
echo "[1/3] Running EXP16 with expanded judges"
python -u exp16_multi_judge_human_sets.py \
  --pass1-tsv "$PASS1_TSV" \
  --pass2-tsv "$PASS2_TSV" \
  --avg-tsv "$AVG_TSV" \
  --out-dir "$EXP16_OUT" \
  --judge-repeats "$JUDGE_REPEATS" \
  --repeat-agg "$REPEAT_AGG" \
  --threshold "$THRESHOLD" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED" \
  --cache-tag "$CACHE_TAG" \
  --plot-error-bars "$PLOT_ERROR_BARS" \
  --judges "$JUDGES"

echo
echo "[2/3] Running EXP17 on pass1/pass2/avg"
for LABEL in pass1 pass2 avg; do
  OUT_DIR="${EXP17_PREFIX}_${LABEL}"
  echo "  - LABEL_SET=$LABEL -> $OUT_DIR"
  python -u exp17_property_human_analysis.py \
    --exp16-summary "$EXP16_OUT/summary.json" \
    --out-dir "$OUT_DIR" \
    --label-set "$LABEL" \
    --perm-iters "$PERM_ITERS" \
    --seed "$SEED" \
    --bad-judge-pattern "BAD_STRINGY"
done

echo
echo "[3/3] Running EXP19 low-variance/failure-mode replot"
python -u exp19_replot_low_variance.py \
  --detail-rows "$EXP16_OUT/detail_rows.csv" \
  --judge-rows "$EXP16_OUT/judge_rows.csv" \
  --out-dir "$EXP19_OUT" \
  --repeat-agg "$REPEAT_AGG"

echo "Done."
echo "  EXP16: $EXP16_OUT/summary.json"
echo "  EXP17 pass1: ${EXP17_PREFIX}_pass1/summary.json"
echo "  EXP17 pass2: ${EXP17_PREFIX}_pass2/summary.json"
echo "  EXP17 avg:   ${EXP17_PREFIX}_avg/summary.json"
echo "  EXP19: $EXP19_OUT/summary.json"

