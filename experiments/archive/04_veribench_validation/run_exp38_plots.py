#!/usr/bin/env python3
"""Regenerate EXP38 scatter plots from existing CSV outputs."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "experiments/04_veribench_validation/exp38_five_human_per_task_isotonic.py"


def main() -> int:
    cmd = [sys.executable, str(SCRIPT), "--plots-only"]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=REPO)


if __name__ == "__main__":
    raise SystemExit(main())
