#!/usr/bin/env bash
# Folder 07: P1/P2/P4 sanity checks on Folder 06 detail_rows.csv.
# Usage: bash run_07.sh [median|mean]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHICH="${1:-median}"

case "$WHICH" in
    median|mean) ;;
    *) echo "Usage: $0 [median|mean]"; exit 2 ;;
esac

DETAIL_CSV="$SCRIPT_DIR/../06_cert_index_vs_human_judge_corr_and_low_var/full_run/$WHICH/detail_rows.csv"
OUT_DIR="$SCRIPT_DIR/full_run/$WHICH"
mkdir -p "$OUT_DIR"

if [ ! -f "$DETAIL_CSV" ]; then
    echo "ERROR: $DETAIL_CSV does not exist; run folder 06 ($WHICH) first."
    exit 1
fi

cd "$SCRIPT_DIR"
python -u run_property_analysis.py \
    --detail-csv "$DETAIL_CSV" \
    --out-dir "$OUT_DIR" \
    --label "$WHICH" \
    --bootstrap-iters 10000 \
    --perm-iters 20000 \
    --seed 42

echo "Done. Outputs in $OUT_DIR"
