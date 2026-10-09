#!/usr/bin/env python3
"""Verify reusable v5 H0/H2 cached cells without treating them as the full 12-judge pool."""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median, stdev
from receipt_validation import accepted, unique_repeats


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "inputs" / "veribench_v5"
RAW = ROOT / "private" / "raw_v5_cells"
OUT = ROOT / "results"
RUN_ID = "cj-e47-v5-10-08-2026-a1"
CONFIGS = {
    "F_H2_opus55_max": ("F", "H2_opus55_max", "opus55x|H2"),
    "Z_H0_opus55_max": ("Z", "H0_opus55_max", "opus55x|H0"),
    "LATE_F_H2_opus55_max": ("F", "H2_opus55_max", "opus55x|H2"),
    "LATE_Z_H0_opus55_max": ("Z", "H0_opus55_max", "opus55x|H0"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def declared_cells() -> tuple[dict[str, dict], dict[str, dict]]:
    main = json.loads(gzip.decompress((INPUT / "manifest_cells.json.gz").read_bytes()))
    late = json.loads((INPUT / "late" / "manifest_G16_G17.json").read_text())
    items = json.loads((INPUT / "manifest.json").read_text())["items"] + late["items"]
    fresh = {x["item"]: x for x in items if x["group"] != "G00"}
    cells = {}
    for arm in ("F", "Z"):
        for row in main[arm] + late["cells"][arm]:
            if row["item"] in fresh and row["member"] in {"H2_opus55_max", "H0_opus55_max"}:
                cells[row["cell"]] = row
    return fresh, cells


def verify_and_aggregate(fresh: dict[str, dict], expected: dict[str, dict]) -> tuple[dict, dict]:
    rows, hashes, seen = defaultdict(list), {}, set()
    problems = []
    proof_path=OUT/'fresh_prompt_proof.json'
    proof={(r['prompt'],r['item']):r for r in json.loads(proof_path.read_text())['rows']} if proof_path.exists() else {}
    for run, (_, member, config) in CONFIGS.items():
        path = RAW / run / "cells.jsonl"
        if not path.exists():
            problems.append({"run": run, "problem": "MISSING_RAW_FILE"})
            continue
        hashes[str(path.relative_to(ROOT))] = sha(path)
        for line in path.read_text().splitlines():
            r = json.loads(line)
            cell = r.get("cell")
            if cell not in expected:
                continue
            e = expected[cell]
            if e["member"] != member:
                problems.append({"cell": cell, "problem": "MEMBER_MISMATCH"})
                continue
            for key in ("item", "group", "repeat", "prompt_sha256"):
                if r.get(key) != e.get(key):
                    problems.append({"cell": cell, "problem": f"IDENTITY_{key}"})
            if r.get("prompt_sha256_delivered") not in (None, e["prompt_sha256"]):
                problems.append({"cell": cell, "problem": "DELIVERED_PROMPT_HASH"})
            if cell in seen:
                problems.append({"cell": cell, "problem": "DUPLICATE_RECEIPT"})
            seen.add(cell)
            ok,reason=accepted(r,e['prompt_sha256'])
            match=proof.get((config.split('|')[1],e['item']),{})
            if match.get('status')!='EXACT' or match.get('rendered')!=e['prompt_sha256']:
                ok,reason=False,'FRESH_RENDER_NOT_PROVED'
            rows[(config, e["item"])].append({**r,'accepted':ok,'acceptance_reason':reason,'source_run':run})
    out, coverage = {}, {}
    for config in sorted({x[2] for x in CONFIGS.values()}):
        by_item, statuses = {}, Counter()
        for iid, item in sorted(fresh.items()):
            if item["blank"]:
                by_item[iid] = {"value": 0.0, "complete_repeats": 0, "structural_blank": True, "repeats": []}
                continue
            rs = rows[(config, iid)]
            statuses.update(r.get("category", "MISSING") for r in rs)
            unique_repeats(rs)
            vals = [r['score'] for r in rs if r['accepted']]
            if any(not 0 <= x <= 1 for x in vals):
                problems.append({"config": config, "item": iid, "problem": "SCORE_OUT_OF_RANGE"})
            by_item[iid] = {"value": median(vals) if len(vals) >= 2 else None, "complete_repeats": len(vals), "structural_blank": False,
                           "repeats": [{k:r.get(k) for k in ('repeat','cell','task_id','run_id','source_run','score','score_0_5','category','accepted','acceptance_reason','prompt_sha256','prompt_sha256_delivered','verdict_sha256')} for r in rs]}
        retained = [x for x in by_item.values() if not x["structural_blank"]]
        coverage[config] = {"fresh_items": len(fresh), "nonblank_items": len(retained),
                            "scorable_nonblank_items": sum(x["value"] is not None for x in retained),
                            "status_counts": dict(sorted(statuses.items()))}
        out[config] = by_item
    nonblank_expected = {cell for cell, row in expected.items() if not row["blank"]}
    missing = sorted(nonblank_expected - seen)
    return {"run_id": RUN_ID, "configs_reused": sorted(out), "declared_cached_cells": len(expected),
            "declared_nonblank_cached_cells": len(nonblank_expected), "seen_cached_cells": len(seen),
            "missing_declared_nonblank_cells": missing, "structural_blank_cells_without_receipts": len(expected) - len(nonblank_expected), "problems": problems,
            "raw_hashes": hashes, "coverage": coverage,
            "note": "Only cached opus55x H0/H2 cells are reusable. The other ten declared primary configurations remain missing declared conditions."}, out


def main() -> int:
    fresh, expected = declared_cells()
    report, scores = verify_and_aggregate(fresh, expected)
    OUT.mkdir(exist_ok=True)
    (OUT / "cached_primary_pool_inventory.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (ROOT/'private/accepted_cached_primary_scores.json').write_text(json.dumps(scores,indent=2,sort_keys=True)+'\n')
    public={cfg:{iid:{**{k:v for k,v in row.items() if k!='repeats'},'raw_repeats_sha256':hashlib.sha256(json.dumps(row['repeats'],sort_keys=True).encode()).hexdigest(),
                      'raw_repeat_sample_sd':stdev([r['score'] for r in row['repeats'] if r['accepted']]) if row['complete_repeats']>=2 else None} for iid,row in items.items()} for cfg,items in scores.items()}
    (OUT / "cached_primary_scores.json").write_text(json.dumps(public, indent=2, sort_keys=True) + "\n")
    if report["problems"] or report["missing_declared_nonblank_cells"]:
        raise SystemExit("cached primary verification failed")
    print(json.dumps(report["coverage"], sort_keys=True))
    return 0


if __name__ == "__main__":
    main()
