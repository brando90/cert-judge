#!/usr/bin/env python3
"""TLDR: Experiment 59's open-weight judge panel. Adds two models to experiment 58's frozen panel at runtime (without
editing e58.py) and fixes the six models run in stage 1. Imported by judge59.py and fetch59.py; zero model calls."""
from __future__ import annotations

import sys
from pathlib import Path

E58_SCRIPTS = Path(__file__).resolve().parents[2] / "58_open_weight_judges_on_e39_e42_probes/scripts"
sys.path[:0] = [str(E58_SCRIPTS)]
import e58  # noqa: E402

# Added to experiment 58's MODELS (revisions read from the Hugging Face API on 10-24-2026).
EXTRA = {
    # Brando's default local judge (Oct 24 decision): single call, AWQ int4, no thinking mode.
    "q25_14b_awq": {"repo": "Qwen/Qwen2.5-14B-Instruct-AWQ", "revision": "539535859b135b0244c91f3e59816150c8056698",
                    "source": "official", "family": "qwen2.5", "params_b": 14.8, "gpus": 1, "max_model_len": 32768,
                    "weights_gb": 10.0, "thinking": False, "quantization": "awq"},
    # MoE, 3B active, FP8; non-thinking instruct, fast.
    "q3_30b_a3b_fp8": {"repo": "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8", "revision": "5a5a776300a41aaa681dd7ff0106608ef2bc90db",
                       "source": "official", "family": "qwen3", "params_b": 30.5, "gpus": 1, "max_model_len": 65536,
                       "weights_gb": 31.2, "thinking": False, "quantization": "fp8"},
}
e58.MODELS.update(EXTRA)
# Lane B runs on a 16 GB card: vLLM refused qwen3_4b at E58's 40,960-token context (5.62 GiB KV needed, 5.03 free), so the
# context is cut to 28,672 (longest E39 prompt ~15k tokens; output budget = context - prompt, so thinking is capped at
# ~13k tokens on the longest prompts). Recorded in PROTOCOL.md Addendum 2.
e58.MODELS["qwen3_4b"] = dict(e58.MODELS["qwen3_4b"], max_model_len=28672)
# Open-weight reference arm (PROTOCOL.md Addendum 3): the largest open judge that fits one free A100 80 GB, run on the H2
# prompt only. E58 planned it on 2 x L40S (65,536 context); here 1 GPU and 32,768 context (longest prompt ~15k tokens).
e58.MODELS["llama33_70b_awq"] = dict(e58.MODELS["llama33_70b_awq"], gpus=1, max_model_len=32768)
e58.MODEL_ORDER = tuple(e58.MODELS)

# Stage 1 panel, in run order. Lane A: skampere1 GPU 5 (A100 80 GB), fastest first. Lane B: mercury2 GPU 9 (16 GB).
LANE_A = ("llama31_8b", "llama33_70b_awq:H2", "q25_14b_awq", "q3_30b_a3b_fp8", "qwen3_8b", "qwen3_14b")   # "model:prompts"
LANE_B = ("qwen3_4b",)
STAGE1 = tuple(m.split(":")[0] for m in LANE_A) + LANE_B
EXP = "e39"                      # experiment 42's semantic probes are not re-scored here
