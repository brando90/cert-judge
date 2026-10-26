#!/usr/bin/env python3
"""TLDR: Run experiment 58's vLLM judge driver on experiment 59's panel (E39 cells, nine prompts, one model per call).
Use after fetch59.py; same arguments as experiment 58's judge_vllm.py: judge59.py --model qwen3_8b --exp e39 --run RUN
--weights DIR. Needs the E58 package tree, vLLM and a free GPU."""
import runpy
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import register59  # noqa: E402,F401  (adds the extra models before judge_vllm builds its argparse choices)

runpy.run_path(str(register59.E58_SCRIPTS / "judge_vllm.py"), run_name="__main__")
