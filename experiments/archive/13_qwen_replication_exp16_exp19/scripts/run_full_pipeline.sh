#!/usr/bin/env bash
# Full Qwen replication of Exp16 -> Exp19 -> Exp25 (geometric trust index).
# Mirrors experiments/13_qwen_replication_exp16_exp19/cc.md but uses
# Qwen3-Coder-30B-A3B-Instruct (open-weights, served via local vLLM
# on http://127.0.0.1:8765/v1).
set -euo pipefail

unset PYTHONPATH
unset PYTHONHOME

VENV=/lfs/skampere3/0/brando9/uv_envs/cert-judge
PY="$VENV/bin/python"
REPO=/dfs/scratch0/brando9/cert-judge
EXP_DIR="$REPO/experiments/13_qwen_replication_exp16_exp19"
VB_DIR="$REPO/experiments/04_veribench_validation"

export HF_HOME=/lfs/skampere3/0/brando9/hf_cache
export MPLBACKEND=Agg
export MPLCONFIGDIR="$EXP_DIR/.mplconfig"
mkdir -p "$MPLCONFIGDIR"

# Isolate this experiment's judge cache so it doesn't clobber / get clobbered by
# concurrent runs (exp12 Leanstral, etc.). Honored by judge_caller.py since the
# CERT_JUDGE_CACHE_PATH patch.
export CERT_JUDGE_CACHE_PATH="${CERT_JUDGE_CACHE_PATH:-$EXP_DIR/results/judge_cache_qwen.json}"
mkdir -p "$(dirname "$CERT_JUDGE_CACHE_PATH")"

# vLLM endpoint (judge_caller.py routes qwen* models here).
export QWEN_BASE_URL="${QWEN_BASE_URL:-http://127.0.0.1:8765/v1}"
export QWEN_API_KEY="${QWEN_API_KEY:-EMPTY}"

# Model identifier exactly as served by vLLM (--served-model-name).
QWEN_MODEL="${QWEN_MODEL:-Qwen/Qwen3-Coder-30B-A3B-Instruct}"

# Output directories — keep all artifacts inside cert-judge repo.
EXP16_OUT="$EXP_DIR/results/exp16_qwen_r3_median"
EXP19_OUT="$EXP_DIR/results/exp19_low_variance_replot_qwen"
EXP25_OUT_BASE="$EXP_DIR/results/exp25_geometric_qwen_r3_median_mono_stab_40_60"

JUDGES="${JUDGES:-llm:${QWEN_MODEL}:P8_STRICT_B,llm:${QWEN_MODEL}:P4_CHECKLIST,llm:${QWEN_MODEL}:P1_BASELINE,llm_bad:${QWEN_MODEL}:BAD_STRINGY,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na}"

echo "============================================================"
echo "EXP13 Qwen replication: Exp16 -> Exp19 -> Exp25"
echo "QWEN_MODEL  = $QWEN_MODEL"
echo "QWEN_URL    = $QWEN_BASE_URL"
echo "EXP16_OUT   = $EXP16_OUT"
echo "EXP19_OUT   = $EXP19_OUT"
echo "EXP25_BASE  = $EXP25_OUT_BASE"
echo "JUDGES      = $JUDGES"
echo "============================================================"

mkdir -p "$EXP16_OUT" "$EXP19_OUT"

# Save MODEL_USED tag for provenance.
echo "MODEL_USED=$QWEN_MODEL" > "$EXP16_OUT/MODEL_USED.txt"
echo "EXP_ROOT=$EXP_DIR"      >> "$EXP16_OUT/MODEL_USED.txt"
echo "QWEN_URL=$QWEN_BASE_URL" >> "$EXP16_OUT/MODEL_USED.txt"
echo "DATE=$(date -Iseconds)" >> "$EXP16_OUT/MODEL_USED.txt"

# 1) EXP16
echo
echo "[1/3] EXP16: multi-judge cert-vs-human trend"
"$PY" -u "$VB_DIR/exp16_multi_judge_human_sets.py" \
  --judge-repeats 3 \
  --repeat-agg median \
  --threshold 0.85 \
  --plot-error-bars on \
  --cache-tag qwen_full_r3_median \
  --judges "$JUDGES" \
  --out-dir "$EXP16_OUT"

# 2) EXP19
echo
echo "[2/3] EXP19: low-variance replot"
"$PY" -u "$VB_DIR/exp19_replot_low_variance.py" \
  --detail-rows "$EXP16_OUT/detail_rows.csv" \
  --judge-rows  "$EXP16_OUT/judge_rows.csv" \
  --repeat-agg  median \
  --bootstrap-iters 4000 \
  --out-dir "$EXP19_OUT"

# 3) EXP25 geometric reanalysis (avg/pass1/pass2)
echo
echo "[3/3] EXP25: geometric trust-index reanalysis"
for LS in avg pass1 pass2; do
  OUT="${EXP25_OUT_BASE}_${LS}"
  mkdir -p "$OUT"
  "$PY" -u "$VB_DIR/exp25_plot_baseline_vs_geometric.py" \
    --summary-json "$EXP16_OUT/summary.json" \
    --label-set "$LS" \
    --mono-weight 0.4 \
    --stab-weight 0.6 \
    --out-dir "$OUT"
done

echo
echo "============================================================"
echo "DONE. Artifacts:"
echo "  $EXP16_OUT/summary.json"
echo "  $EXP16_OUT/judge_rows.csv"
echo "  $EXP16_OUT/detail_rows.csv"
echo "  $EXP16_OUT/fig_cert_vs_human_scatter_{pass1,pass2,avg}.png"
echo "  $EXP19_OUT/fig_main_monotonicity_lowvar.png"
echo "  $EXP19_OUT/fig_failure_alpha_variant_breakdown.png"
echo "  $EXP19_OUT/fig_failure_bug_reversal_rates.png"
for LS in avg pass1 pass2; do
  echo "  ${EXP25_OUT_BASE}_${LS}/summary.json"
done
echo "============================================================"
