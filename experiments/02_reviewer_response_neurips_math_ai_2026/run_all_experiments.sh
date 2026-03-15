#!/usr/bin/env bash
# Run all certification judge experiments in order.
# Usage: bash run_all_experiments.sh
# Run from: experiments/02_reviewer_response_neurips_math_ai_2026/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  Certification Judge Experiments -- Run All"
echo "  Dir: $SCRIPT_DIR"
echo "============================================================"

# Activate environment
source "$HOME/uv_envs/cert-judge/bin/activate"

# Load API keys
export WANDB_API_KEY=$(cat ~/keys/brandos_wandb_key.txt)
export ANTHROPIC_API_KEY=$(cat ~/keys/anthropic_bm_key_koyejolab.txt)
export WANDB_PROJECT="trusting-formal-judge"
export WANDB_GROUP="certification-experiments"

# Load OpenAI key if available
if [ -f ~/keys/openai_api_brandos_personal_key.txt ]; then
    export OPENAI_API_KEY=$(cat ~/keys/openai_api_brandos_personal_key.txt)
    echo "OpenAI key loaded."
else
    echo "NOTE: OpenAI key not found. OpenAI models will be skipped."
fi

echo ""
echo "Step 1: Install dependencies"
uv pip install anthropic wandb openai Levenshtein nltk matplotlib scipy scikit-learn seaborn --quiet

echo ""
echo "Step 2: Create result directories"
mkdir -p results figures utils
mkdir -p results/edit_distance_control
mkdir -p results/hard_identity
mkdir -p results/hard_monotonicity
mkdir -p results/multi_model
mkdir -p results/out_of_domain

echo ""
echo "======================================================="
echo "EXP 5: Edit Distance Control (SMOKE TEST)"
echo "======================================================="
python exp5_edit_distance_control.py
echo "EXP 5 done."

echo ""
echo "======================================================="
echo "EXP 1: Hard Identity"
echo "======================================================="
python exp1_hard_identity.py
echo "EXP 1 done."

echo ""
echo "======================================================="
echo "EXP 2: Hard Monotonicity"
echo "======================================================="
python exp2_hard_monotonicity.py
echo "EXP 2 done."

echo ""
echo "======================================================="
echo "EXP 4: Out-of-Domain Generalization"
echo "======================================================="
python exp4_out_of_domain.py
echo "EXP 4 done."

echo ""
echo "======================================================="
echo "EXP 3: Multi-Model Ablation"
echo "======================================================="
python exp3_multi_model.py
echo "EXP 3 done."

echo ""
echo "======================================================="
echo "FINAL REPORT"
echo "======================================================="
python utils/final_report.py
echo "Final report done."

echo ""
echo "======================================================="
echo "ALL EXPERIMENTS COMPLETE"
echo "Results in: $SCRIPT_DIR/results/"
echo "Figures in: $SCRIPT_DIR/figures/"
echo "======================================================="
