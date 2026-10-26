#!/usr/bin/env python3
"""TLDR: Experiment 61's open-weight panel on mercury2 RTX A4000 16 GB cards: experiment 60's registrations (hence 58/59) with 16 GB context settings. Zero model calls.
Imported by run61.py and fetch61.py. Contexts are cut for the 16 GB cards (PROTOCOL.md section 2)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

E60_SCRIPTS = Path(__file__).resolve().parents[2] / "60_open_weight_proxy_index_rigor_round/scripts"
sys.path[:0] = [str(E60_SCRIPTS)]
import register60  # noqa: E402
e58 = register60.e58

SEED61 = 61
PANEL = ("qwen3_4b", "q25_14b_awq", "qwen3_8b", "llama31_8b", "gemma3_12b")
e58.MODELS["qwen3_4b"] = dict(e58.MODELS["qwen3_4b"], max_model_len=28672)                 # as experiment 59 (1 x A4000)
e58.MODELS["q25_14b_awq"] = dict(e58.MODELS["q25_14b_awq"], gpus=2, max_model_len=20480)   # Addendum 3: 1 x A4000 failed twice (KV at 20,480; then sampler warm-up OOM at 14,336); AWQ int4 over 2 x A4000
e58.MODELS["qwen3_8b"] = dict(e58.MODELS["qwen3_8b"], gpus=2, max_model_len=28672)         # bf16 16.4 GB over 2 x A4000 (tensor parallel 2)
e58.MODELS["llama31_8b"] = dict(e58.MODELS["llama31_8b"], gpus=2, max_model_len=28672)       # Addendum 2: non-Qwen family, bf16 16.1 GB over 2 x A4000
e58.MODELS["gemma3_12b"] = dict(e58.MODELS["gemma3_12b"], gpus=2, max_model_len=16384)        # Addendum 2: bf16 24.4 GB over 2 x A4000, short context for KV
if os.environ.get("E61_GPU_UTIL"):                                                          # Addendum 4: vLLM gpu_memory_utilization override (default 0.90)
    e58.GPU_MEMORY_UTILIZATION = float(os.environ["E61_GPU_UTIL"])
e58.MODEL_ORDER = tuple(e58.MODELS)
