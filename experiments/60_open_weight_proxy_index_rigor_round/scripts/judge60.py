#!/usr/bin/env python3
"""TLDR: Run experiment 58's vLLM judge driver on experiment 60's panel (E39 cells, nine prompts); E60_SEED=<n> makes a seed replicate.
Use after fetch60.py; arguments as judge_vllm.py: judge60.py --model gemma3_27b --exp e39 --run RUN --weights DIR [--prompts H2,D0].
Needs the E58 package tree, vLLM and a free GPU."""
import runpy
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import register60  # noqa: E402,F401

runpy.run_path(str(register60.e58.__file__).rsplit("/", 1)[0] + "/judge_vllm.py", run_name="__main__")
