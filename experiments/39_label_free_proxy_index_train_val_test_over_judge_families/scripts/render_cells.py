#!/usr/bin/env python3
"""TLDR: Render every judge cell (configuration x probe x repeat) of experiment 39 to frozen prompt bytes:
VeriBench prompts through experiment 100's `prompts.render` (imported, never edited), the paper's legacy prompts
through `legacy.render`; deterministic cells (the deployed judge's no-call rules) get their value without a
call. Prompt text stays under private/; results/cells/<config>.json carries only ids, hashes and sizes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402
import legacy                                                 # noqa: E402

CELL_DIR = e39.PRIVATE / "cells"


def cell_id(kind: str, key: str, level: int, repeat: int) -> str:
    return f"{kind}__{key}__L{level}__r{repeat}"


def probe_text(probe: dict) -> str:
    if probe["kind"] == "blank":
        return ""
    if probe["path"]:
        return Path(probe["path"]).read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"probe without text: {probe['probe_id']}")


def load_probe_rows(manifest: dict, items: list[dict], allow_unvalidated: bool) -> list[dict]:
    by_item = {it["item"]: it for it in items}
    first_of_task = {}
    for it in items:
        first_of_task.setdefault(it["task"], it)
    rows = []
    for r in manifest["rows"]:
        if r["valid"] is False or (r["valid"] is None and not allow_unvalidated):
            continue
        base = by_item[r["item"]] if r["item"] else first_of_task[r["task"]]
        if r["kind"] == "crit":
            r = dict(r, path=base["candidate_path_abs"])
        elif r["kind"] == "ident":
            r = dict(r, path=base["ref_ann_path_abs"])
        r["base_item"] = base
        # Neutral candidate names: a probe never reveals its manipulation in the prompt.
        r["candidate_name"] = base["candidate_file"] if r["item"] else f"{r['task']}__agent3.lean"
        rows.append(r)
    return rows


def render_unit(unit: dict, probe_rows: list[dict], prompts_mod, force: bool) -> dict:
    out_dir = CELL_DIR / unit["config"].replace("|", "__")
    out_dir.mkdir(parents=True, exist_ok=True)
    cells, deterministic, unmeasured = [], 0, 0
    for r in probe_rows:
        repeats = e39.KINDS[r["kind"]]["repeats"]
        text = probe_text(r)
        base = r["base_item"]
        status, value, reason, system, user = "render", None, "", None, None
        if unit["prompt_family"] == "legacy":
            gold = Path(base["ref_ann_path_abs"]).read_text(encoding="utf-8", errors="replace")
            system, user = legacy.render(unit["rubric"], gold, text)
        else:
            try:
                system, user = prompts_mod.render(unit["rubric"], base, text, r["candidate_name"])
            except prompts_mod.Unmeasured as exc:
                msg = str(exc)
                if msg.startswith("no_candidate_obligations"):
                    status, value, reason = "deterministic", 0.0, "deployed scorer assigns 0.0 without a call: no candidate obligations"
                elif msg.startswith("no_reference_obligations"):
                    status, value, reason = "deterministic", 1.0, "deployed scorer assigns 1.0 without a call: no reference obligations"
                else:
                    status, reason = "unmeasured_extraction", msg[:200]
        for repeat in range(1, repeats + 1):
            cid = cell_id(r["kind"], r["key"], r["level"], repeat)
            cell = {"cell": cid, "kind": r["kind"], "key": r["key"], "task": r["task"], "item": r["item"], "level": r["level"],
                    "repeat": repeat, "probe_id": r["probe_id"], "candidate_sha256": r["sha256"], "status": status}
            if status == "render":
                blob = {"system": system, "user": user}
                path = out_dir / f"{cid}.json"
                if force or not path.exists():
                    e39.write_json(path, blob)
                cell["prompt_sha256"] = e39.sha((system + "\n\n" + user).encode())
                cell["prompt_bytes"] = len((system + "\n\n" + user).encode())
            elif status == "deterministic":
                cell.update(score=value, reason=reason)
                deterministic += 1
            else:
                cell.update(reason=reason)
                unmeasured += 1
            cells.append(cell)
    n_calls = sum(1 for c in cells if c["status"] == "render")
    return {"written_utc": e39.stamp(), "config": unit["config"], "rubric": unit["rubric"], "prompt_family": unit["prompt_family"],
            "scale": unit["scale"], "max_tokens": unit["max_tokens"], "n_cells": len(cells), "n_calls": n_calls,
            "n_deterministic": deterministic, "n_unmeasured": unmeasured,
            "prompt_bytes_total": sum(c.get("prompt_bytes", 0) for c in cells), "cells": cells}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=e39.RESULTS / "probe_manifest.json")
    ap.add_argument("--panel", type=Path, default=e39.RESULTS / "panel.json")
    ap.add_argument("--configs", default="", help="comma list of configs to render (default: every LLM unit)")
    ap.add_argument("--allow-unvalidated", action="store_true", help="dry runs only: render probes that were not elaborated")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    _, prompts_mod, _ = e39.x100_modules()
    items = e39.load_items()
    probe_rows = load_probe_rows(e39.read_json(args.manifest), items, args.allow_unvalidated)
    units = [u for u in e39.read_json(args.panel)["units"] if u["kind"] == "llm"]
    if args.configs:
        wanted = set(args.configs.split(","))
        units = [u for u in units if u["config"] in wanted]
    summary = {}
    for unit in units:
        blob = render_unit(unit, probe_rows, prompts_mod, args.force)
        e39.write_json(e39.RESULTS / "cells" / (unit["config"].replace("|", "__") + ".json"), blob)
        summary[unit["config"]] = {k: blob[k] for k in ("n_cells", "n_calls", "n_deterministic", "n_unmeasured", "prompt_bytes_total")}
    e39.write_json(e39.RESULTS / "cells_summary.json", {"written_utc": e39.stamp(), "n_probe_rows": len(probe_rows),
                                                          "allow_unvalidated": args.allow_unvalidated, "per_config": summary})
    print(json.dumps({"configs": len(summary), "calls_total": sum(v["n_calls"] for v in summary.values()),
                      "deterministic_total": sum(v["n_deterministic"] for v in summary.values()),
                      "unmeasured_total": sum(v["n_unmeasured"] for v in summary.values())}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
