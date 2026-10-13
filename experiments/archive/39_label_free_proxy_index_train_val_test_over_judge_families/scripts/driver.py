#!/usr/bin/env python3
"""TLDR: Experiment 39's durable stage driver — one idempotent pass over: smoke per configuration, main admission
in the pre-registered order (train models, then val, then test), polling, harvest, one labelled recovery pass,
merge, controls, unit analysis, selection, and (only after FINALISTS.json is committed) the sealed test unlock and
report. Never re-admits a cell that already has a verdict; stops on private/STOP; writes private/DONE at the end."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402
import judge_controller as J                                  # noqa: E402

PYTHON = sys.executable
ORDER = ("train", "val", "test")
DONE = e39.PRIVATE / "DONE"
STOP = e39.PRIVATE / "STOP"


def sh(args: list[str], timeout: int = 7200) -> subprocess.CompletedProcess:
    return subprocess.run([PYTHON, str(e39.E / "scripts" / args[0])] + args[1:], capture_output=True, text=True, timeout=timeout)


def llm_units() -> list[dict]:
    return [u for u in e39.read_json(e39.RESULTS / "panel.json")["units"] if u["kind"] == "llm"]


def run_entry(config: str, part: str, suffix: str = "") -> dict | None:
    return J.load_state()["runs"].get(f"{config}@{part}{suffix}")


def deployed(model_key: str) -> bool:
    return (e39.PRIVATE / f"deployment_{model_key}.json").exists()


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
        if not (e39.RESULTS / "harvest" / (J.fs(cfg) + ".json")).exists():
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
        print("DONE marker present")
        return 0
    units = llm_units()
    J.poll(publish=True)
    smoke_ok = stage_smoke(units, args.concurrency)
    main_ok = stage_main(units, args.concurrency) if smoke_ok or any(run_entry(u["config"], "smoke") for u in units) else False
    harvest_ok = stage_harvest(units, args.concurrency)
    status = {"smoke_ok": smoke_ok, "main_admitted": main_ok, "harvest_done": harvest_ok, "ts": e39.stamp()}
    if harvest_ok:
        sealed = (e39.RESULTS / "FINALISTS.json").exists()
        if not sealed:
            # The open rows are frozen at selection: controls and the unit analysis run only until the seal exists.
            for step in (["local_controls.py"], ["analyze.py", "units"]):
                done = sh(step)
                status[step[0] + ":" + ("".join(step[1:]) or "run")] = done.returncode
            done = sh(["analyze.py", "select"])
            status["select"] = done.returncode
            status["next"] = "commit results/FINALISTS.json and results/SELECTION.json, then the driver unlocks the test split"
        else:
            # A re-run of `analyze.py units` after the seal rewrites results/units_train_val.json (new timestamp, same numbers),
            # which the test unlock rightly refuses; the committed file is the sealed one, so restore it from git if it drifted.
            fin = e39.read_json(e39.RESULTS / "FINALISTS.json")
            units_open = e39.RESULTS / "units_train_val.json"
            if not units_open.exists() or e39.sha_file(units_open) != fin.get("units_open_sha256"):
                restored = subprocess.run(["git", "checkout", "--", "results/units_train_val.json"], cwd=str(e39.E), capture_output=True, text=True)
                status["units_restored_from_git"] = restored.returncode
            commit = subprocess.run(["git", "log", "-1", "--format=%H", "--", "results/FINALISTS.json"], cwd=str(e39.E), capture_output=True, text=True).stdout.strip()
            if commit and not (e39.RESULTS / "TEST_RECEIPT.json").exists():
                done = sh(["analyze.py", "test", "--finalists-commit", commit])
                status["test"] = done.returncode
                status["test_stderr"] = done.stderr[-400:]
            if (e39.RESULTS / "TEST_RECEIPT.json").exists():
                sh(["analyze.py", "report"])
                DONE.write_text(e39.stamp() + "\n")
                status["done"] = True
    e39.write_json(e39.PRIVATE / "driver_status.json", status)
    print(json.dumps(status, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
