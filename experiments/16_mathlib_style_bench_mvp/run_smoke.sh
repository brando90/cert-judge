#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python run_mathlib_style_bench.py \
  --pairs-file data/sample_pairs.jsonl \
  --out-dir results/smoke
