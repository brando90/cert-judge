#!/usr/bin/env bash
# Experiment 05: Scaled Bug Ladder
# Generates semantic bug ladders for all VeriBench files using Claude,
# then scores each level with Claude as judge.
#
# Usage:
#   bash run.sh              # full run (all 150 files)
#   bash run.sh --n_files 5  # quick test with 5 files
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# --- Load API key ---
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    KEY_FILE="$HOME/keys/anthropic_bm_key_koyejolab.txt"
    if [ -f "$KEY_FILE" ]; then
        export ANTHROPIC_API_KEY
        ANTHROPIC_API_KEY="$(cat "$KEY_FILE")"
        echo "Loaded Anthropic key from $KEY_FILE"
    else
        echo "ERROR: Set ANTHROPIC_API_KEY or place key in $KEY_FILE"
        exit 1
    fi
fi

# --- Activate environment ---
VENV="$HOME/uv_envs/cert-judge"
if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
    echo "Activated venv: $VENV"
fi

# --- Ensure cert_judge is importable ---
cd "$REPO_ROOT"
pip install -e . --quiet 2>/dev/null || true

# --- Run ---
cd "$SCRIPT_DIR"
echo ""
echo "Starting Experiment 05: Scaled Bug Ladder"
echo "Model: claude-sonnet-4-20250514"
echo "=========================================="

python run_bug_ladder.py \
    --model claude-sonnet-4-20250514 \
    --n_repeats 3 \
    "$@"

echo ""
echo "Done. Results in: $SCRIPT_DIR/results/"
