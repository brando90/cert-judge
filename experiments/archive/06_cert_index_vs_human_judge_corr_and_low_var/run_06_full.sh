#!/usr/bin/env bash
# Folder 06 full run — wrapper that drives PROTOCOL.md parameters.
# DEVIATION from PROTOCOL.md: JUDGE_REPEATS=3 (was 9). Reason: n_repeats=9
# would take ~8 hours of fresh LLM calls; the smoke cache is n_repeats=3 and
# reusing it (no --cache-tag) lets us expand to the full 9-judge panel via
# cache hits in minutes. The n_repeats=9 follow-up is filed as Folder 06b.
# Documented in REPORT.md → Open questions.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP04_DIR="$SCRIPT_DIR/../04_veribench_validation"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$EXP04_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

# Empty CACHE_TAG -> upstream default cache_namespace (hits smoke cache).
CACHE_TAG="${CACHE_TAG:-}"

PASS1_TSV="$EXP04_DIR/data/ethan_human_scores_20260425.tsv"
PASS2_TSV="$EXP04_DIR/data/ethan_human_scores_ORIGINAL.tsv"
AVG_TSV="$EXP04_DIR/data/ethan_human_scores_avg_two_passes_20260425.tsv"
VERIBENCH_ROOT="$SCRIPT_DIR/../../data/veribench_dataset/lean_src/veribench"
GENERATED_AGENTS_DIR="$SCRIPT_DIR/../../data/generated_agents"

# From PROTOCOL.md (JUDGE_REPEATS=3 is a documented deviation; see header).
JUDGE_REPEATS=3
THRESHOLD=0.85
BOOTSTRAP_ITERS=10000
PERM_ITERS=20000
SEED=42
JUDGES="llm:claude-sonnet-4-20250514:P8_STRICT_B,llm:claude-sonnet-4-20250514:P4_CHECKLIST,llm:claude-sonnet-4-20250514:P1_BASELINE,llm_bad:claude-sonnet-4-20250514:BAD_STRINGY,llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P1_BASELINE,editdist:e1:na,random:r1:na"

WHICH="${1:-median}"
case "$WHICH" in
    median) REPEAT_AGG=median ;;
    mean) REPEAT_AGG=mean ;;
    *) echo "Usage: $0 [median|mean]"; exit 2 ;;
esac

OUT_DIR="$SCRIPT_DIR/full_run/$WHICH"
mkdir -p "$OUT_DIR"

echo "============================================================"
echo "Folder 06 FULL RUN ($WHICH)"
echo "judge_repeats=$JUDGE_REPEATS repeat_agg=$REPEAT_AGG"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS"
echo "cache_tag=${CACHE_TAG:-(empty -> default exp16: namespace)}"
echo "out_dir=$OUT_DIR"
echo "judges=$JUDGES"
echo "============================================================"

cd "$EXP04_DIR"
python -u exp16_multi_judge_human_sets.py \
    --pass1-tsv "$PASS1_TSV" \
    --pass2-tsv "$PASS2_TSV" \
    --avg-tsv "$AVG_TSV" \
    --out-dir "$OUT_DIR" \
    --veribench-root "$VERIBENCH_ROOT" \
    --generated-agents-dir "$GENERATED_AGENTS_DIR" \
    --judge-repeats "$JUDGE_REPEATS" \
    --repeat-agg "$REPEAT_AGG" \
    --threshold "$THRESHOLD" \
    --bootstrap-iters "$BOOTSTRAP_ITERS" \
    --perm-iters "$PERM_ITERS" \
    --seed "$SEED" \
    --judges "$JUDGES" \
    --cache-tag "$CACHE_TAG"

echo "Done. Outputs in $OUT_DIR"
