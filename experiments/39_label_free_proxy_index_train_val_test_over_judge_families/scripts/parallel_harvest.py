#!/usr/bin/env python3
"""TLDR: Harvest experiment 39's terminal `main` runs in parallel (N worker processes calling
`judge_controller.py harvest`), walking the panel order BACKWARDS so it never meets the serial stage driver, which
walks forwards; a run is skipped once its harvest file exists and the last `--leave` unharvested runs are left to the
driver. Downloads only (`valk run results` / `valk run output`); zero model calls; no state.json writes."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402

HARVESTS = e39.PRIVATE / "judge" / "harvests"


def harvested(config: str) -> bool:
    return (HARVESTS / f"{config.replace('|', '__')}_main.json").exists()


def todo(panel: list[str], part: str) -> list[str]:
    state = json.loads((e39.PRIVATE / "judge" / "state.json").read_text())["runs"]
    return [c for c in panel if state.get(f"{c}@{part}", {}).get("phase") == "terminal" and not harvested(c)]


def harvest(config: str, part: str) -> tuple[str, int, str]:
    if harvested(config):
        return config, 0, "already harvested"
    done = subprocess.run([sys.executable, str(e39.E / "scripts/judge_controller.py"), "harvest", "--config", config, "--part", part],
                          capture_output=True, text=True, timeout=7200)
    return config, done.returncode, (done.stdout.strip().splitlines() or [done.stderr.strip()[-200:]])[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--leave", type=int, default=3, help="leave this many of the earliest unharvested runs to the driver")
    ap.add_argument("--part", default="main")
    args = ap.parse_args()
    panel = [u["config"] for u in e39.read_json(e39.RESULTS / "panel.json")["units"] if u["kind"] == "llm"]
    taken: set[str] = set()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        while True:
            pending = [c for c in todo(panel, args.part) if c not in taken]
            while len(pending) > args.leave and len(futures) < args.workers:
                config = pending.pop()                         # from the END of the driver's order
                taken.add(config)
                futures[pool.submit(harvest, config, args.part)] = config
            if not futures:
                if len(pending) <= args.leave:
                    print(f"{e39.stamp()} nothing left beyond the {args.leave} runs left to the driver; exiting", flush=True)
                    return 0
                time.sleep(60)
                continue
            done = next(f for f in list(futures) if f.done()) if any(f.done() for f in futures) else None
            if done is None:
                time.sleep(10)
                continue
            config = futures.pop(done)
            name, rc, line = done.result()
            print(f"{e39.stamp()} {name}: rc={rc} {line}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
