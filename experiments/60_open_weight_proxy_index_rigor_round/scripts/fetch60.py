#!/usr/bin/env python3
"""TLDR: Download experiment 60's models at their pinned revisions (experiment 58's fetch_models.py).
Usage: fetch60.py --dir DIR --models gemma3_27b ; needs internet and huggingface_hub."""
import runpy
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import register60  # noqa: E402,F401

runpy.run_path(str(register60.e58.__file__).rsplit("/", 1)[0] + "/fetch_models.py", run_name="__main__")
