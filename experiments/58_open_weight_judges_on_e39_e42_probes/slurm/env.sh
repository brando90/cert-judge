# TLDR: paths and the vLLM venv shared by every experiment 58 FarmShare script (source it; nothing runs).
export E58_HOME=${E58_HOME:-$HOME/e58}
export CODE=$E58_HOME/code/experiments/58_open_weight_judges_on_e39_e42_probes
export RUN=${RUN:-$E58_HOME/runs/main}
export MODELS_DIR=${MODELS_DIR:-$E58_HOME/models}
export E58_VERIBENCH_REPO=$CODE/private/veribench_min     # the minimal VeriBench subset shipped in the package (parsers, renderers)
export HF_HOME=$HOME/hf_cache
export HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4
export FS_HF=$HOME/venvs/fs_hf      # shared vLLM 0.32.0 + transformers 5.19.0 (see notes: build_fs_hf.sbatch)
# The same two lines fs_hf's activate sets: without them vLLM dies at warmup (no nvcc; flashinfer JIT vs nvcc 13.4).
export CUDA_HOME=$FS_HF/lib/python3.12/site-packages/nvidia/cu13
export VLLM_USE_FLASHINFER_SAMPLER=0
mkdir -p $E58_HOME/logs $RUN
# model key and GPU count for task index i (0-based): tasks.tsv has a header-less "key gpus" line per model
e58_task() { sed -n "$(( $1 + 1 ))p" $CODE/slurm/tasks.tsv; }
