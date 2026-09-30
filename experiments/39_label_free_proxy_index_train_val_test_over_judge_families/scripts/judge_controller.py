#!/usr/bin/env python3
"""TLDR: Admit, poll and harvest experiment 39's judge runs through Valkyrie with experiment 103's validated
`vb103_judge` agent — one run per (configuration, part) over that model's served pack — parse every verdict on
the host with the rubric's own parser (experiment 100's `prompts.parse` or `legacy.parse`), merge the
deterministic no-call cells, and write results/harvest/<config>.json. Adapted from experiment 105's controller.

Usage:  judge_controller.py admit   --config <model|prompt> --part smoke|main [--concurrency 20]
        judge_controller.py poll
        judge_controller.py harvest --config <model|prompt> --part smoke|main
        judge_controller.py recover --config <model|prompt> [--dry-run]     # one labelled pass over unmeasured cells
        judge_controller.py merge   --config <model|prompt>                  # main + recovery + deterministic -> results/harvest
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402
import legacy                                                 # noqa: E402

JUDGE = e39.PRIVATE / "judge"
STATE = JUDGE / "state.json"
RAW = JUDGE / "raw"
UUID_RE = re.compile(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}")
TERMINAL_RUN = {"finished", "completed", "error", "failed", "stopped", "cancelled", "canceled", "success", "succeeded"}
PARTS = {"main": "cells", "smoke": "smoke_cells"}


def fs(config: str) -> str:
    return config.replace("|", "__")


def env() -> dict[str, str]:
    out = dict(os.environ)
    for key in ("VALKYRIE_API_KEY", "TRACKER_SERVICE_URL", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN", "PYTHONPATH", "PYTHONHOME"):
        out.pop(key, None)
    out.update(VALKYRIE_ENV="bench", VALKYRIE_CONFIG_PATH=str(e39.PRIVATE / "valkyrie.yaml"))
    return out


def cli(args: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run([str(e39.VALK)] + args, env=env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"runs": {}, "created": e39.stamp()}


def save_state(state: dict) -> None:
    state["updated"] = e39.stamp()
    JUDGE.mkdir(parents=True, exist_ok=True)
    disk = load_state()
    for key, entry in disk.get("runs", {}).items():
        state.setdefault("runs", {}).setdefault(key, entry)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n")
    tmp.replace(STATE)


def unit_of(config: str) -> dict:
    for unit in e39.read_json(e39.RESULTS / "panel.json")["units"]:
        if unit["config"] == config:
            return unit
    raise KeyError(config)


def pack_rows(config: str, part: str) -> list[dict]:
    model_key = config.split("|")[0]
    return e39.read_json(e39.RESULTS / "packs.json")["packs"][model_key]["per_config"][config][PARTS[part]]


def selector_for(unit: dict) -> tuple[str, str]:
    """The selector this run uses: the first pre-registered one unless results/selectors.json overrides it
    (a substitute recorded by the worker, with its reason, BEFORE any score of that model was seen)."""
    override = e39.RESULTS / "selectors.json"
    if override.exists():
        chosen = e39.read_json(override).get(unit["model_key"])
        if chosen:
            allowed = unit["selectors"] + unit["substitutes"]
            assert chosen["selector"] in allowed, f"{unit['model_key']}: {chosen['selector']} is not pre-registered"
            return chosen["selector"], chosen.get("source", "override")
    return unit["selectors"][0], "pre-registered"


def admit(config: str, part: str, concurrency: int, only: list[str] | None = None, suffix: str = "") -> int:
    hold = e39.PRIVATE / "HOLD_JUDGE_ADMISSIONS"
    if hold.exists():
        raise SystemExit(f"judge admissions on hold ({hold}): {hold.read_text().strip()}")
    bundle = e39.read_json(e39.RESULTS / "agent_bundle_check.json")
    assert bundle["verdict"] == "PASS", "the judge bundle on the server is not the validated bytes"
    packs = e39.read_json(e39.RESULTS / "packs.json")
    assert packs["verdict"] == "PASS", "the packs failed their round-trip check"
    unit = unit_of(config)
    model_key = unit["model_key"]
    deployment = e39.read_json(e39.PRIVATE / f"deployment_{model_key}.json")
    benchmark = deployment["benchmark"]
    key = f"{config}@{part}{suffix}"
    state = load_state()
    if key in state["runs"]:
        print(f"{key}: already admitted as {state['runs'][key].get('run_id')}; a second admission would re-spend judge calls, refusing")
        return 0
    ids = [row["task_id"] for row in pack_rows(config, part)]
    if only is not None:
        keep = set(only)
        ids = [i for i in ids if i in keep]
    assert ids, f"{key}: no task ids to admit"
    ids_file = JUDGE / f"task_ids_{fs(key).replace('@', '_')}.txt"
    ids_file.parent.mkdir(parents=True, exist_ok=True)
    ids_file.write_text("".join(i + "\n" for i in ids))
    selector, source = selector_for(unit)
    if unit["pack_flavor"] == "agent":
        # Agent judge: the Terminus2 bundle recorded by the harness check (results/agent_harness.json), its own kwargs,
        # and the gateway secret NAME mapped by Valkyrie server-side (never read on the host).
        harness = e39.read_json(e39.RESULTS / "agent_harness.json")
        assert harness["verdict"] == "PASS", "agent harness check has not passed"
        agent = harness["agent"]
        kwargs = {k: str(v) for k, v in harness.get("kwargs", {}).items()}
        kwargs.update({k: str(v) for k, v in unit["kwargs"].items() if k in harness.get("supported_kwargs", [])})
        secret_args = ["-s", harness["secret_env"], e39.GATEWAY_SECRET] if harness.get("secret_env") else []
        agent_sha = harness.get("contract_sha256")
    else:
        agent = e39.AGENT
        kwargs = {"judge_config": config, "max_tokens": str(unit["max_tokens"]), "benchmark": benchmark}
        kwargs.update({k: str(v) for k, v in unit["kwargs"].items()})
        secret_args = []                            # vb103_judge's contract declares its own secret mapping
        agent_sha = bundle["downloaded_now_sha256"].get("judge_call.py")
    args = ["run", "start", "--agent", agent, "--benchmark", benchmark, "--dataset", "default", "--model", selector,
            "--concurrency", str(concurrency), "--task-ids-file", str(ids_file), "--label", f"cj39-{part}{suffix}-{fs(config)}"[:96]]
    args += secret_args
    for kwarg, value in kwargs.items():
        args += ["-k", kwarg, value]
    entry = {"config": config, "agent": agent, "harness": unit["harness"], "selector": selector, "selector_source": source,
             "kwargs": kwargs, "concurrency": concurrency, "expected_cells": len(ids), "part": part, "suffix": suffix,
             "benchmark": benchmark, "judge_agent_sha256": agent_sha, "service_pid": deployment["service_pid"],
             "admitted_at": e39.stamp(), "task_ids_file": str(ids_file), "task_ids": ids if only is not None else None,
             "phase": "admitting", "command": args}
    state["runs"][key] = entry
    save_state(state)                                          # recorded BEFORE the call: never replay an admission
    result = cli(args)
    log = JUDGE / "admissions" / f"{fs(key).replace('@', '_')}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr)
    found = UUID_RE.findall(result.stdout)
    if result.returncode or not found:
        entry.update(phase="admission_failed", returncode=result.returncode, stderr_tail=(result.stderr or "")[-800:])
        print(f"{key}: ADMISSION FAILED rc={result.returncode} (see {log})")
        print((result.stderr or result.stdout or "")[-600:])
    else:
        entry.update(phase="running", run_id=found[0])
        print(f"{key}: run_id={found[0]} over {len(ids)} cells at concurrency {concurrency} ({selector}, {source})")
    save_state(state)
    return 0


def poll(publish: bool = True) -> int:
    state = load_state()
    summary = {}
    for key, entry in state["runs"].items():
        run_id = entry.get("run_id")
        if not run_id:
            summary[key] = {"phase": entry.get("phase")}
            continue
        if entry.get("phase") == "terminal":
            summary[key] = {"phase": "terminal", "cells_terminal": entry.get("cells_terminal"), "expected": entry["expected_cells"]}
            continue
        result = cli(["run", "status", "--ids", run_id, "--format", "json"], timeout=600)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            entry["poll_error"] = (result.stderr or result.stdout or "")[-300:]
            summary[key] = {"phase": entry.get("phase"), "poll_error": True}
            continue
        runs = payload.get("runs") if isinstance(payload, dict) else payload
        row = runs[0] if isinstance(runs, list) and runs else (runs if isinstance(runs, dict) else (payload if isinstance(payload, dict) else {}))
        counts = row.get("task_state_counts") or row.get("task_states") or {}
        status = str(row.get("status") or row.get("state") or "").lower()
        terminal = sum(int(counts.get(k, 0)) for k in ("FINISHED", "ERROR", "STOPPED"))
        entry.update(run_status=status, task_state_counts=counts, cells_terminal=terminal, polled_at=e39.stamp())
        if status in TERMINAL_RUN and terminal >= entry["expected_cells"]:
            entry["phase"] = "terminal"
        summary[key] = {"phase": entry["phase"], "run_status": status, "cells_terminal": terminal, "expected": entry["expected_cells"]}
    save_state(state)
    progress = {"written_utc": e39.stamp(), "experiment": e39.EXPERIMENT, "per_run": summary}
    e39.write_json(JUDGE / "progress.json", progress)
    if publish:
        e39.write_json(e39.RESULTS / "judge_progress.json", progress)
    print(json.dumps(summary, indent=1))
    return 0


def download(key: str, run_id: str) -> tuple[Path, Path]:
    RAW.mkdir(parents=True, exist_ok=True)
    name = fs(key).replace("@", "_")
    results, artifacts = RAW / f"{name}_results.json", RAW / f"{name}_artifacts"
    if results.exists():
        results.unlink()
    if artifacts.exists():
        shutil.rmtree(artifacts)
    with (RAW / f"{name}_download.log").open("w") as log:
        for args in (["run", "results", run_id, "--path", str(results)], ["run", "output", run_id, "-o", str(artifacts)]):
            done = cli(args, timeout=5400)
            log.write(f"{e39.stamp()} {' '.join(args[:3])} rc={done.returncode}\n")
            if done.returncode:
                log.write((done.stdout or "")[-2000:] + (done.stderr or "")[-2000:] + "\n")
    return results, artifacts


def rows_of(results_path: Path) -> dict[str, dict]:
    payload = json.loads(results_path.read_text())
    blob = payload[0] if isinstance(payload, list) and payload else payload
    raw = (blob.get("evaluation_results") or blob.get("results") or blob.get("task_results") or {})
    out = {}
    for task_id, value in raw.items():
        row = value.get("result", value) if isinstance(value, dict) else value
        out[task_id] = row if isinstance(row, dict) else {}
    return out


def parse_verdict(unit: dict, text: str, prompts_mod):
    if unit["prompt_family"] == "legacy":
        return legacy.parse(text)
    return prompts_mod.parse(unit["rubric"], text)


def harvest(config: str, part: str, suffix: str = "") -> int:
    _, prompts_mod, _ = e39.x100_modules()
    unit = unit_of(config)
    all_meta = {row["task_id"]: row for row in pack_rows(config, part)}
    state = load_state()
    key = f"{config}@{part}{suffix}"
    entry = state["runs"].get(key)
    if not entry or not entry.get("run_id"):
        print(f"{key}: not admitted, nothing to harvest")
        return 2
    wanted = entry.get("task_ids") or list(all_meta)
    rows_meta = {k: v for k, v in all_meta.items() if k in set(wanted)}
    results_path, artifacts = download(key, entry["run_id"])
    if not results_path.exists():
        print(f"{key}: no results file downloaded; see private/judge/raw/")
        return 2
    served = rows_of(results_path)
    receipts = {}
    for path in sorted(artifacts.rglob("receipt.json")):
        try:
            receipt = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        receipts[receipt.get("task_id") or path.parent.name] = receipt
    cells, charges = [], 0.0
    for task_id, meta in sorted(rows_meta.items()):
        row, receipt = served.get(task_id, {}), receipts.get(task_id, {})
        cell = {k: meta[k] for k in ("task_id", "cell", "kind", "key", "task", "item", "level", "repeat", "prompt_sha256")}
        cell.update(config=config, agent_status=receipt.get("status"), prompt_sha256_delivered=receipt.get("prompt_sha256"),
                    finish_reason=receipt.get("finish_reason"), cost_usd=receipt.get("cost_usd"),
                    submission_status=row.get("submission_status"))
        charges += cell["cost_usd"] or 0.0
        blob = row.get("solution_b64")
        if blob:
            text = base64.b64decode(blob).decode("utf-8", errors="replace")
            cell["verdict_sha256"] = e39.sha(text.encode())
            try:
                raw_score, norm, verdict = parse_verdict(unit, text, prompts_mod)
                cell.update(status="measured", score_raw=raw_score, score=norm,
                            rationale=str(verdict.get("rationale") or verdict.get("reasoning") or verdict.get("reason") or "")[:300])
            except ValueError as exc:
                cell.update(status="parse_error", error=str(exc)[:200])
        elif receipt.get("status") == "model_error":
            cell.update(status="model_error", error_type=receipt.get("error_type"))
        elif receipt.get("status") == "incomplete":
            cell.update(status="incomplete", reason=receipt.get("reason"))
        else:
            cell.update(status="unmeasured_infra", reason=receipt.get("reason") or receipt.get("error_kind")
                        or f"no collected verdict (submission_status={row.get('submission_status')})")
        if cell.get("prompt_sha256_delivered") and cell["prompt_sha256_delivered"] != meta["prompt_sha256"]:
            cell.update(status="unmeasured_infra", reason="delivered prompt hash != frozen prompt hash")
        cells.append(cell)
    counts: dict[str, int] = {}
    for cell in cells:
        counts[cell["status"]] = counts.get(cell["status"], 0) + 1
    out = {"written_utc": e39.stamp(), "config": config, "part": part, "suffix": suffix, "run_id": entry["run_id"],
           "selector": entry["selector"], "selector_source": entry.get("selector_source"), "kwargs": entry["kwargs"],
           "n_cells": len(cells), "status_counts": counts, "charges_usd": round(charges, 6), "cells": cells}
    e39.write_json(JUDGE / "harvests" / f"{fs(key).replace('@', '_')}.json", out)
    print(json.dumps({key: {"status_counts": counts, "charges_usd": round(charges, 6)}}))
    return 0


def harvested(config: str, part: str, suffix: str = "") -> dict | None:
    path = JUDGE / "harvests" / f"{fs(config + '@' + part + suffix).replace('@', '_')}.json"
    return e39.read_json(path) if path.exists() else None


def recover(config: str, concurrency: int, dry_run: bool) -> int:
    """One labelled, score-independent pass over the cells of `main` that have no verdict (PROTOCOL.md section 6)."""
    blob = harvested(config, "main")
    if not blob:
        print(f"{config}: harvest --part main first")
        return 2
    missing = [c["task_id"] for c in blob["cells"] if c["status"] in ("unmeasured_infra", "model_error", "incomplete")]
    print(json.dumps({"config": config, "recovery_candidates": len(missing)}))
    if not missing or dry_run:
        return 0
    return admit(config, "main", concurrency, only=missing, suffix="@recovery_1")


def merge(config: str) -> int:
    """Main + recovery_1 (recovery fills only cells that had no verdict) + deterministic cells -> results/harvest."""
    unit = unit_of(config)
    main = harvested(config, "main")
    if not main:
        print(f"{config}: no main harvest")
        return 2
    by_cell = {c["cell"]: c for c in main["cells"]}
    recovery = harvested(config, "main", "@recovery_1")
    recovered = 0
    if recovery:
        for c in recovery["cells"]:
            if by_cell.get(c["cell"], {}).get("status") != "measured" and c["status"] == "measured":
                by_cell[c["cell"]] = dict(c, recovered=True)
                recovered += 1
    cells_blob = e39.read_json(e39.RESULTS / "cells" / (fs(config) + ".json"))
    for c in cells_blob["cells"]:
        if c["status"] == "deterministic":
            by_cell[c["cell"]] = {"cell": c["cell"], "kind": c["kind"], "key": c["key"], "task": c["task"], "item": c["item"],
                                  "level": c["level"], "repeat": c["repeat"], "config": config, "status": "deterministic",
                                  "score": c["score"], "score_raw": c["score"] * unit["scale"], "reason": c["reason"]}
        elif c["status"] != "render" and c["cell"] not in by_cell:
            by_cell[c["cell"]] = {"cell": c["cell"], "kind": c["kind"], "key": c["key"], "task": c["task"], "item": c["item"],
                                  "level": c["level"], "repeat": c["repeat"], "config": config, "status": c["status"], "reason": c.get("reason")}
    cells = [by_cell[k] for k in sorted(by_cell)]
    counts: dict[str, int] = {}
    for cell in cells:
        counts[cell["status"]] = counts.get(cell["status"], 0) + 1
    charges = round((main["charges_usd"] or 0.0) + ((recovery or {}).get("charges_usd") or 0.0), 6)
    out = {"written_utc": e39.stamp(), "config": config, "family": unit["family"], "split": unit["split"], "kind": unit["kind"],
           "harness": unit["harness"], "rubric": unit["rubric"], "scale": unit["scale"], "selector": main["selector"],
           "selector_source": main.get("selector_source"),
           "kwargs": main["kwargs"], "run_ids": {"main": main["run_id"], "recovery_1": (recovery or {}).get("run_id")},
           "n_cells": len(cells), "status_counts": counts, "recovered_cells": recovered, "charges_usd": charges, "cells": cells}
    e39.write_json(e39.RESULTS / "harvest" / (fs(config) + ".json"), out)
    print(json.dumps({config: {"status_counts": counts, "recovered": recovered, "charges_usd": charges}}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("admit"); a.add_argument("--config", required=True); a.add_argument("--part", choices=sorted(PARTS), required=True); a.add_argument("--concurrency", type=int, default=20)
    sub.add_parser("poll")
    h = sub.add_parser("harvest"); h.add_argument("--config", required=True); h.add_argument("--part", choices=sorted(PARTS), required=True); h.add_argument("--suffix", default="")
    r = sub.add_parser("recover"); r.add_argument("--config", required=True); r.add_argument("--concurrency", type=int, default=20); r.add_argument("--dry-run", action="store_true")
    m = sub.add_parser("merge"); m.add_argument("--config", required=True)
    args = ap.parse_args()
    if args.cmd == "admit":
        return admit(args.config, args.part, args.concurrency)
    if args.cmd == "poll":
        return poll()
    if args.cmd == "harvest":
        return harvest(args.config, args.part, args.suffix)
    if args.cmd == "recover":
        return recover(args.config, args.concurrency, args.dry_run)
    if args.cmd == "merge":
        return merge(args.config)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
