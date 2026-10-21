# TLDR: paths for the Sherlock fallback of experiment 58 (Apptainer vLLM image route of AT-476); source it, nothing runs.
export B=$SCRATCH/e58
export CODE=$B/code/experiments/58_open_weight_judges_on_e39_e42_probes
export RUN=${RUN:-$B/runs/main} MODELS_DIR=$B/models
export E58_VERIBENCH_REPO=$CODE/private/veribench_min
export SIF=$SCRATCH/rl4cv_sherlock/containers/vllm-openai_v0.30.0.sif   # vllm 0.30.0, torch 2.13.0+cu130
mkdir -p $B/logs $B/cache $RUN
CL=/usr/local/cuda/compat:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/.singularity.d/libs
APPENV="HF_HUB_OFFLINE=1,TOKENIZERS_PARALLELISM=false,OMP_NUM_THREADS=4,VLLM_WORKER_MULTIPROC_METHOD=spawn,XDG_CACHE_HOME=$B/cache,VLLM_CACHE_ROOT=$B/cache/vllm,TRITON_CACHE_DIR=$B/cache/triton,FLASHINFER_WORKSPACE_BASE=$B/cache/flashinfer,HF_HOME=$B/cache/hf,E58_VERIBENCH_REPO=$E58_VERIBENCH_REPO"
# Driver 550 (CUDA 12.4) vs image CUDA 13.0: use the image's forward-compat libcuda when it initialises.
e58_ldenv() {
  local P="import torch; x=torch.ones(4, device='cuda'); print(torch.cuda.get_device_name(0), (x*2).sum().item())"
  if apptainer exec --nv $SIF env LD_LIBRARY_PATH=$CL python3 -c "$P" >&2; then echo ",LD_LIBRARY_PATH=$CL"
  elif apptainer exec --nv $SIF python3 -c "$P" >&2; then echo ""
  else echo "CUDA init failed with and without forward compat" >&2; return 3; fi
}
e58_py() { apptainer exec -B /scratch --env "$APPENV" $SIF python3 "$@"; }   # CPU steps
e58_task() { sed -n "$(( $1 + 1 ))p" $CODE/slurm/tasks.tsv; }
