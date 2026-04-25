#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

PASS1_TSV="${PASS1_TSV:-$SCRIPT_DIR/data/ethan_human_scores_20260425.tsv}"
PASS2_TSV="${PASS2_TSV:-$SCRIPT_DIR/data/ethan_human_scores_second_pass_20260425.tsv}"
AVG_TSV="${AVG_TSV:-$SCRIPT_DIR/data/ethan_human_scores_avg_two_passes_20260425.tsv}"
OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_exp16_multi_judge_human_sets}"
VERIBENCH_ROOT="${VERIBENCH_ROOT:-$SCRIPT_DIR/../../data/veribench_dataset/lean_src/veribench}"
GENERATED_AGENTS_DIR="${GENERATED_AGENTS_DIR:-$SCRIPT_DIR/../../data/generated_agents}"
JUDGE_REPEATS="${JUDGE_REPEATS:-3}"
THRESHOLD="${THRESHOLD:-0.85}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-5000}"
PERM_ITERS="${PERM_ITERS:-10000}"
SEED="${SEED:-42}"
JUDGES="${JUDGES:-llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P1_BASELINE,llm_bad:gpt-5.3-codex:na,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na}"

echo "============================================================"
echo "EXP16 Multi-Judge Human Sets"
echo "pass1_tsv=$PASS1_TSV"
echo "pass2_tsv=$PASS2_TSV"
echo "avg_tsv=$AVG_TSV"
echo "out_dir=$OUT_DIR"
echo "judge_repeats=$JUDGE_REPEATS threshold=$THRESHOLD"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS seed=$SEED"
echo "judges=$JUDGES"
echo "============================================================"

python -u exp16_multi_judge_human_sets.py \
  --pass1-tsv "$PASS1_TSV" \
  --pass2-tsv "$PASS2_TSV" \
  --avg-tsv "$AVG_TSV" \
  --out-dir "$OUT_DIR" \
  --veribench-root "$VERIBENCH_ROOT" \
  --generated-agents-dir "$GENERATED_AGENTS_DIR" \
  --judge-repeats "$JUDGE_REPEATS" \
  --threshold "$THRESHOLD" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED" \
  --judges "$JUDGES"

echo "Done."
echo "  $OUT_DIR/summary.json"
echo "  $OUT_DIR/judge_rows.csv"
echo "  $OUT_DIR/detail_rows.csv"
echo "  $OUT_DIR/fig_cert_vs_human_scatter_pass1.png"
echo "  $OUT_DIR/fig_cert_vs_human_scatter_pass2.png"
echo "  $OUT_DIR/fig_cert_vs_human_scatter_avg.png"
