#!/usr/bin/env python3
"""Zero-call, source-hash-bound v5 target reconstruction and cache inventory."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "inputs" / "veribench_v5"
RAW = ROOT / "private" / "raw_v5_cells"
OUT = ROOT / "results"
RUN_ID = "cj-e47-v5-10-08-2026-a1"
PRIMARY_FAMILIES = {"Anthropic", "Alibaba"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text())


def complete_first(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    """Frozen v5 S2 rule: repeat 1, COMPLETE, parser-v2, one entry per slot."""
    out = {}
    for r in rows:
        if r.get("repeat") != 1 or r.get("category") != "COMPLETE":
            continue
        if r.get("score_0_5_parser_v2") is None:
            continue
        k = (r["item"], r["frame"], r["run_key"].replace("LATE_", "").replace("S2_", ""))
        if k in out:
            raise ValueError(f"duplicate first COMPLETE slot: {k}")
        out[k] = r
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = load_json(INPUT / "manifest.json")
    raw = gzip.decompress((INPUT / "manifest_cells.json.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != manifest["cells"]["json_sha256"]:
        raise ValueError("manifest_cells gzip content hash mismatch")
    late = load_json(INPUT / "late" / "manifest_G16_G17.json")
    panel = load_json(INPUT / "panel.json")
    families = {x["key"]: x["family"] for x in panel["members"]}
    # G00 is the historical 75-item anchor, expressly outside the 50-task fresh pool.
    items = {x["item"]: x for x in manifest["items"] if x["group"] != "G00"}
    items.update({x["item"]: x for x in late["items"]})
    files = sorted(RAW.glob("*/*cells.jsonl"))
    required = {"S2_" + k for k in families} | {"LATE_S2_" + k for k in families}
    actual = {p.parent.name for p in files}
    missing_runs = sorted(required - actual)
    rows, hashes = [], {}
    for p in files:
        hashes[str(p.relative_to(ROOT))] = sha(p)
        rows.extend(json.loads(line) for line in p.read_text().splitlines() if line.strip())
    slots = complete_first(rows)
    audit = Counter((r.get("run_key"), r.get("category")) for r in rows)
    targets, coverage = [], Counter()
    for iid, item in sorted(items.items()):
        fv, c0 = {}, {}
        for model, family in families.items():
            vals = [slots.get((iid, frame, model), {}).get("score_0_5_parser_v2") for frame in ("P1", "P2", "P3")]
            vals = [v / 5 for v in vals if v is not None]
            fv[family] = sum(vals) / len(vals) if len(vals) >= 2 else None
            v = slots.get((iid, "C0", model), {}).get("score_0_5_parser_v2")
            c0[family] = None if v is None else v / 5
        def mean_available(values, need):
            present = [v for v in values if v is not None]
            return (sum(present) / len(present)) if len(present) >= need else None
        fvals, cvals = list(fv.values()), list(c0.values())
        t_all = mean_available(fvals, math.ceil(2 * len(families) / 3))
        t_c0 = mean_available(cvals, math.ceil(2 * len(families) / 3))
        common = [v for family, v in fv.items() if family not in PRIMARY_FAMILIES]
        t_common = mean_available(common, max(3, math.ceil(2 * len(common) / 3)))
        coverage.update({"items": 1, "nonblank": int(not item["blank"]), "T_all": int(t_all is not None), "T_C0": int(t_c0 is not None), "T_common": int(t_common is not None)})
        targets.append({"item": iid, "group": item["group"], "task": item["task"], "family": item["family"], "blank": item["blank"], "family_values": fv, "c0_values": c0, "T_all": t_all, "T_C0": t_c0, "T_common_excluding_Anthropic_Alibaba": t_common})
    report = {"run_id": RUN_ID, "source_commit": "ccd86d467fd7577826c4b549df2c532bf43b1892", "input_hashes": {str(p.relative_to(INPUT)): sha(p) for p in (INPUT / "manifest.json", INPUT / "manifest_cells.json.gz", INPUT / "panel.json", INPUT / "late" / "manifest_G16_G17.json")}, "raw_cell_hashes": hashes, "panel_families": families, "expected_raw_runs": sorted(required), "missing_raw_runs": missing_runs, "raw_category_counts": {f"{k[0]}::{k[1]}": v for k, v in sorted(audit.items())}, "first_complete_slots": len(slots), "items": coverage, "note": "No criterion association or new judge score is computed here; first COMPLETE S2 parser-v2 calls reconstruct simulated-panel targets."}
    if args.check:
        assert not missing_runs
        assert len(targets) == 750
        assert len({x["item"] for x in targets}) == 750
    OUT.mkdir(exist_ok=True)
    (OUT / "zero_call_inventory.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (OUT / "targets_reconstructed.json").write_text(json.dumps(targets, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"items": len(targets), "slots": len(slots), "missing_runs": missing_runs, "coverage": coverage}, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
