#!/bin/bash
# TLDR: one-time setup in the OnDemand JupyterLab terminal (a node with internet): check the shared vLLM venv, download the
# panel's weights at their pinned revisions, tokenize every prompt through each model's chat template (token_budget.py: the
# over-context cells per model, no GPU), run the CPU tests, and verify the prompt hashes. Resumable: finished steps are skipped.
# usage: bash $HOME/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/prepare.sh [model,model|all]
set -euo pipefail
source "$(dirname "$0")/env.sh"
unset HF_HUB_OFFLINE   # downloads happen here, jobs stay offline
MODELS=${1:-all}
[ -x $FS_HF/bin/python ] || { echo "missing $FS_HF: build it first (SUBMIT.md, step 0)"; exit 2; }
source $FS_HF/bin/activate
python -c "import vllm, transformers, huggingface_hub; print('vllm', vllm.__version__, 'transformers', transformers.__version__)"
python $CODE/scripts/fetch_models.py --dir $MODELS_DIR --models $MODELS
python $CODE/scripts/fetch_models.py --dir $MODELS_DIR --list > $CODE/slurm/tasks.tsv
# Every shipped prompt must hash to the frozen prompt_sha256 (the driver re-checks each row before generating).
python $CODE/scripts/verify_prompts.py
export HF_HUB_OFFLINE=1
python $CODE/scripts/token_budget.py --tokenizers $MODELS_DIR --models $MODELS
pip install -q pytest 2>&1 | tail -1 || true
cd $CODE/../.. && python -m pytest -q -p no:cacheprovider $CODE/tests
echo "PREPARE OK"
