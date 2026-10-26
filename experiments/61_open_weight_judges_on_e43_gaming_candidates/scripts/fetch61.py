#!/usr/bin/env python3
"""TLDR: Download experiment 61's models at their pinned revisions (experiment 58's fetch_models.py). Usage: fetch61.py --dir DIR --models qwen3_4b"""
import runpy
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import register61  # noqa: E402,F401

runpy.run_path(str(register61.e58.__file__).rsplit("/", 1)[0] + "/fetch_models.py", run_name="__main__")
