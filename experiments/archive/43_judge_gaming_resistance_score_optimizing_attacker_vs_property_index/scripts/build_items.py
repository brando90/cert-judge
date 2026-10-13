#!/usr/bin/env python3
"""TLDR: Build a Lean-valid attack start for each of VeriBench experiment 100's 75 rated candidates with the fixed
repair ladder (lean_guard.build_start), then apply experiment 43's item rule (criterion tasks, expert-mean coverage
<= 0.6, Lean-eligible start, ascending coverage then item id, first 15) and the pilot rule (the first three items of
distinct tasks). Writes results/start_manifest.json and results/items.json; start texts go to private/starts/.
Labels are used only for this selection and in the final analysis; the attacker never sees them. Zero model calls."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e43                                                    # noqa: E402
import lean_guard as G                                        # noqa: E402

STARTS = e43.PRIVATE / "starts"


def select(rows: list[dict], manifest: dict[str, dict], n: int = e43.N_ITEMS) -> tuple[list[str], list[str], dict]:
    eligible = [r for r in rows if r["split"] in e43.CRITERION_SPLITS and r["target_expert"] <= e43.COVERAGE_MAX
                and manifest[r["item"]]["stage"] != "FAIL"]
    eligible.sort(key=lambda r: (r["target_expert"], r["item"]))
    chosen = [r["item"] for r in eligible[:n]]
    pilot, seen = [], set()
    for item in chosen:
        task = next(r["task"] for r in rows if r["item"] == item)
        if task not in seen:
            pilot.append(item)
            seen.add(task)
        if len(pilot) == e43.PILOT["items"]:
            break
    info = {"n_candidates": len(rows),
            "n_criterion_low_coverage": sum(1 for r in rows if r["split"] in e43.CRITERION_SPLITS and r["target_expert"] <= e43.COVERAGE_MAX),
            "n_eligible": len(eligible), "shortfall": max(0, n - len(eligible))}
    return chosen, pilot, info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=16)
    args = ap.parse_args()
    lean = G.Lean()
    rows = e43.load_items()

    def one(r: dict) -> tuple[str, dict]:
        original = Path(r["candidate_path_abs"]).read_text(encoding="utf-8", errors="replace")
        out = G.build_start(original, lean)
        rec = {"item": r["item"], "task": r["task"], "split": r["split"], "stage": out["stage"],
               "stages": out["stages"], "pruned": out["pruned"], "original_sha256": e43.sha(original.encode()),
               "error": out.get("error"), "error_class": out.get("error_class")}
        if out["code"] is not None:
            STARTS.mkdir(parents=True, exist_ok=True)
            (STARTS / f"{r['item']}.lean").write_text(out["code"], encoding="utf-8")
            rec.update(start_sha256=e43.sha(out["code"].encode()), start_bytes=len(out["code"].encode()),
                       n_theorems=len(G.statements(out["code"])), n_implementation=len(G.implementation(out["code"])))
        return r["item"], rec

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        manifest = dict(pool.map(one, rows))
    counts: dict[str, int] = {}
    for rec in manifest.values():
        counts[rec["stage"]] = counts.get(rec["stage"], 0) + 1
    e43.write_json(e43.RESULTS / "start_manifest.json", {
        "written_utc": e43.stamp(), "lean_project": str(lean.lake_dir), "items_sha256": e43.sha_file(e43.X100 / "inputs/items.jsonl"),
        "ladder": ["S0_original", "S1_syntax", "S2_imports", "S3_proofs_sorry", "S4_prune_failing_spec_and_tests"],
        "stage_counts": counts, "rows": [manifest[r["item"]] for r in rows]})
    chosen, pilot, info = select(rows, manifest)
    by_id = {r["item"]: r for r in rows}
    e43.write_json(e43.RESULTS / "items.json", {
        "written_utc": e43.stamp(), "rule": ("experiment 39's criterion tasks (experiment 75 val + test task split); expert-mean "
                                             "coverage <= 0.6; the repair ladder yields a Lean-valid start; ascending coverage, "
                                             "then item id; first 15"),
        "pilot_rule": "the first three selected items from distinct tasks", **info,
        "items": [{"item": i, "task": by_id[i]["task"], "split": by_id[i]["split"], "start_stage": manifest[i]["stage"],
                   "start_sha256": manifest[i]["start_sha256"], "n_start_theorems": manifest[i]["n_theorems"],
                   "n_gold_theorems": by_id[i]["n_ref_theorems_ann"]} for i in chosen],
        "pilot_items": pilot})
    print(json.dumps({"stage_counts": counts, **info, "items": chosen, "pilot": pilot}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
