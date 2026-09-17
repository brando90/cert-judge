#!/usr/bin/env bash
# Run EFG baseline (Zhang et al., arXiv:2506.10903) vs human labels.
# Usage:
#   bash run.sh                        # default: oap_wa mode with gpt-4o-mini
#   bash run.sh --mode both            # run both direct and oap_wa
#   bash run.sh --model gpt-4.1-mini   # use a different model
#   bash run.sh --max-rows 5           # quick test with 5 rows

set -euo pipefail
cd "$(dirname "$0")"

REPO_ROOT="$(cd ../../.. && pwd)"

# Activate environment if available
if [ -f "$HOME/uv_envs/cert-judge/bin/activate" ]; then
    source "$HOME/uv_envs/cert-judge/bin/activate"
fi

python run_efg_vs_human.py "$@"
