#!/usr/bin/env bash
# Stand up vLLM OpenAI-compatible server for Qwen3-Coder-30B-A3B-Instruct on snap.
# Server URL once running: http://127.0.0.1:8765/v1
set -euo pipefail

unset PYTHONPATH
unset PYTHONHOME

VENV=/lfs/skampere3/0/brando9/uv_envs/cert-judge
export HF_HOME=/lfs/skampere3/0/brando9/hf_cache
export PATH="$VENV/bin:$PATH"
export VLLM_USE_V1=1

# Disable DeepGEMM (not installed in this env)
export VLLM_USE_DEEP_GEMM=0
export VLLM_MOE_USE_DEEP_GEMM=0
export VLLM_DEEP_GEMM_WARMUP=skip

# Pick GPUs with most free memory (skip 0/1/7 which are partially busy).
# Force override (any pre-existing CUDA_VISIBLE_DEVICES gets replaced).
export CUDA_VISIBLE_DEVICES="${VLLM_CUDA_DEVICES:-4}"

MODEL="${MODEL:-Qwen/Qwen3-Coder-30B-A3B-Instruct}"
PORT="${PORT:-8765}"
TP="${TP:-1}"
MAX_LEN="${MAX_LEN:-32768}"
GPU_UTIL="${GPU_UTIL:-0.6}"

LOG_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/vllm_$(date +%Y%m%d_%H%M%S).log"

echo "[start_vllm] model=$MODEL  port=$PORT  TP=$TP  max_len=$MAX_LEN"
echo "[start_vllm] CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "[start_vllm] log=$LOG"

exec "$VENV/bin/vllm" serve "$MODEL" \
    --port "$PORT" \
    --host 127.0.0.1 \
    --tensor-parallel-size "$TP" \
    --max-model-len "$MAX_LEN" \
    --gpu-memory-utilization "$GPU_UTIL" \
    --served-model-name Qwen/Qwen3-Coder-30B-A3B-Instruct Qwen3-Coder-30B-A3B-Instruct qwen3-coder-30b \
    --trust-remote-code \
    --dtype bfloat16 \
    --enforce-eager \
    --moe-backend triton \
    --attention-backend FLASH_ATTN \
    > "$LOG" 2>&1
