#!/usr/bin/env python3
"""TLDR: Download experiment 59's models at their pinned revisions (experiment 58's fetch_models.py on the extended panel).
Usage: fetch59.py --dir DIR --models llama31_8b,q25_14b_awq ; needs internet and huggingface_hub."""
import runpy
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import register59  # noqa: E402,F401

runpy.run_path(str(register59.E58_SCRIPTS / "fetch_models.py"), run_name="__main__")
