#!/usr/bin/env python3
"""TLDR: (Vendored from experiment 39's scripts/driver.py at origin/e39-proxy-index-search 9823689, adapted to experiment
42.) Experiment 42's durable stage driver — one idempotent pass over: smoke per configuration, main admission in
experiment 39's split order (train models, then val, then test; the order only schedules admissions here), polling,
harvest, one labelled recovery pass, merge and the deterministic controls. Never re-admits a cell that already has a
verdict; admits nothing unless private/GATE_OPEN exists (written by the worker once PROTOCOL.md is committed and
experiment 39's transport smoke has passed); stops on private/STOP; writes private/JUDGING_DONE when every run is
merged (private/DONE is reserved for the landed experiment and is never written here)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e42                                                    # noqa: E402
import judge_controller as J                                  # noqa: E402

PYTHON = sys.executable
ORDER = ("train", "val", "test")
DONE = e42.PRIVATE / "JUDGING_DONE"
GATE = e42.PRIVATE / "GATE_OPEN"
STOP = e42.PRIVATE / "STOP"


def sh(args: list[str], timeout: int = 7200) -> subprocess.CompletedProcess:
    return subprocess.run([PYTHON, str(e42.E / "scripts" / args[0])] + args[1:], capture_output=True, text=True, timeout=timeout)


def llm_units() -> list[dict]:
    return [u for u in e42.read_json(e42.RESULTS / "panel.json")["units"] if u["kind"] == "llm"]


def run_entry(config: str, part: str, suffix: str = "") -> dict | None:
    return J.load_state()["runs"].get(f"{config}@{part}{suffix}")


def deployed(model_key: str) -> bool:
    return (e42.PRIVATE / f"deployment_{model_key}.json").exists()


def stage_smoke(units: list[dict], concurrency: int) -> bool:
    """Every configuration gets its one spare smoke cell admitted and measured before its main pack."""
    all_ok = True
    for u in units:
        if not deployed(u["model_key"]):
            all_ok = False
            continue
        entry = run_entry(u["config"], "smoke")
        if entry is None:
            J.admit(u["config"], "smoke", 1)
            all_ok = False
        elif entry.get("phase") == "terminal" and not J.harvested(u["config"], "smoke"):
            J.harvest(u["config"], "smoke")
        blob = J.harvested(u["config"], "smoke")
        if not blob or not any(c["status"] == "measured" for c in blob["cells"]):
            all_ok = False
    return all_ok


def stage_main(units: list[dict], concurrency: int) -> bool:
    """Admit main packs split by split, in the pre-registered order; a later split waits for the earlier one's admission."""
    for split in ORDER:
        group = [u for u in units if u["split"] == split]
        pending = False
        for u in group:
            smoke = J.harvested(u["config"], "smoke")
            if not smoke or not any(c["status"] == "measured" for c in smoke["cells"]):
                pending = True
                continue
            if run_entry(u["config"], "main") is None:
                J.admit(u["config"], "main", concurrency)
                pending = True
        if pending:
            return False
    return True


def stage_harvest(units: list[dict], concurrency: int) -> bool:
    """Harvest terminal main runs, run the single recovery pass, harvest it, merge into results/harvest."""
    done = True
    for u in units:
        cfg = u["config"]
        entry = run_entry(cfg, "main")
        if not entry or entry.get("phase") != "terminal":
            done = False
            continue
        if not J.harvested(cfg, "main"):
            J.harvest(cfg, "main")
        rec = run_entry(cfg, "main", "@recovery_1")
        if rec is None:
            blob = J.harvested(cfg, "main")
            missing = [c for c in blob["cells"] if c["status"] in ("unmeasured_infra", "model_error", "incomplete")]
            if missing:
                J.recover(cfg, concurrency, dry_run=False)
                done = False
                continue
        elif rec.get("phase") != "terminal":
            done = False
            continue
        elif not J.harvested(cfg, "main", "@recovery_1"):
            J.harvest(cfg, "main", "@recovery_1")
        if not (e42.RESULTS / "harvest" / (J.fs(cfg) + ".json")).exists():
            J.merge(cfg)
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--concurrency", type=int, default=20)
    args = ap.parse_args()
    if STOP.exists():
        print("STOP marker present")
        return 0
    if DONE.exists():
        print("JUDGING_DONE marker present")
        return 0
    if not GATE.exists():
        print("wait gate closed (private/GATE_OPEN missing): no admission")
        return 0
    units = llm_units()
    J.poll(publish=True)
    smoke_ok = stage_smoke(units, args.concurrency)
    main_ok = stage_main(units, args.concurrency) if smoke_ok or any(run_entry(u["config"], "smoke") for u in units) else False
    harvest_ok = stage_harvest(units, args.concurrency)
    status = {"smoke_ok": smoke_ok, "main_admitted": main_ok, "harvest_done": harvest_ok, "ts": e42.stamp()}
    if harvest_ok:
        done = sh(["local_controls.py"])
        status["local_controls"] = done.returncode
        if done.returncode == 0:
            DONE.write_text(e42.stamp() + "\n")
            status["judging_done"] = True
    e42.write_json(e42.PRIVATE / "driver_status.json", status)
    print(json.dumps(status, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
