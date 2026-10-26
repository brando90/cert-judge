#!/usr/bin/env python3
"""TLDR: Experiment 60's open-weight judge panel: experiment 59's registrations plus two new families on one free A100 80 GB.
Imported by judge60.py and fetch60.py; zero model calls. Seed replicates use E60_SEED (default: experiment 58's seed)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

E59_SCRIPTS = Path(__file__).resolve().parents[2] / "59_open_weight_proxy_index_and_frontier_fit/scripts"
sys.path[:0] = [str(E59_SCRIPTS)]
import register59  # noqa: E402
e58 = register59.e58

# Gemma 3 27B bf16 (54.9 GB) on one A100 80 GB at 32,768 context (experiment 58 planned 2 x L40S at 65,536).
e58.MODELS["gemma3_27b"] = dict(e58.MODELS["gemma3_27b"], gpus=1, max_model_len=32768)
e58.MODEL_ORDER = tuple(e58.MODELS)

# Seed replicate: the per-cell sampling seed is int(sha256('<SEED>|<config>|<cell>')[:8], 16); a replicate changes SEED only.
if os.environ.get("E60_SEED"):
    e58.SEED = int(os.environ["E60_SEED"])
