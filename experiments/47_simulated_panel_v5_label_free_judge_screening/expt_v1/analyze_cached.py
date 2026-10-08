#!/usr/bin/env python3
"""Zero-call, source-hash-bound v5 target reconstruction and cache inventory."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from receipt_validation import transport_evidence
from statistics_v5 import target_excluding


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "inputs" / "veribench_v5"
RAW = ROOT / "private" / "raw_v5_cells"
OUT = ROOT / "results"
RUN_ID = "cj-e47-v5-10-08-2026-a1"
PRIMARY_FAMILIES = {"Anthropic", "Alibaba"}
RECOVERY_RUNS = {
    "S2_grok47_rec1a": "grok47",
    "S2_grok47_rec1b": "grok47",
    "S2_grok47_rec1c": "grok47",
    "S2_qwen38max_rec1a": "qwen38max",
    "S2_qwen38max_rec1b": "qwen38max",
    "S2_qwen38max_rec1c": "qwen38max",
}
RECOVERABLE = {"MISSING", "INFRA_ERROR", "PROVIDER_ERROR", "NONCLEAN_FINISH", "MODEL_ERROR"}
TARGET_CSV_SOURCE_BLOB = "113fdd5635bef101cde0fd02575b824236de8d3a"
TARGET_CSV_SOURCE_CONTENT_SHA256 = "251da962838762eefc148d998beafbb637e7f8afaa7d83952bf78a52f209e583"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text())


def resolve_receipts(rows: list[tuple[str, dict]], declared: dict[str, dict]) -> tuple[dict[str, dict], dict]:
    """Apply v5 recovery precedence without allowing a recovery to replace measured data."""
    chosen, audit = {}, {"accepted_recoveries": [], "ignored_recoveries": [], "initial_cells": 0}
    for source, r in rows:
        cell = r.get("cell")
        expected = declared.get(cell)
        if expected is None:
            raise ValueError(f"undeclared cell in {source}: {cell}")
        for key in ("item", "frame", "repeat", "prompt_sha256"):
            if r.get(key) != expected.get(key):
                raise ValueError(f"identity mismatch {source} {cell} {key}: {r.get(key)!r} != {expected.get(key)!r}")
        expected_model = expected["model"]
        if source in RECOVERY_RUNS and RECOVERY_RUNS[source] != expected_model:
            raise ValueError(f"recovery model mismatch {source} {cell}")
        if r.get("prompt_sha256_delivered") not in (None, r["prompt_sha256"]):
            raise ValueError(f"delivered prompt mismatch {source} {cell}")
        old = chosen.get(cell)
        if old is None:
            chosen[cell] = {**r, "_source_run": source, "_declared_model": expected_model}
            audit["initial_cells"] += 1
        elif source not in RECOVERY_RUNS:
            raise ValueError(f"duplicate non-recovery receipt {source} {cell}")
        elif (old["_source_run"] in RECOVERY_RUNS or old["category"] in RECOVERABLE) and r["category"] != "MISSING":
            chosen[cell] = {**r, "_source_run": source, "_declared_model": expected_model}
            audit["accepted_recoveries"].append({"cell": cell, "from": old["_source_run"], "to": source,
                                                  "from_category": old["category"], "to_category": r["category"]})
        else:
            audit["ignored_recoveries"].append({"cell": cell, "from": old["_source_run"], "to": source,
                                                 "from_category": old["category"], "to_category": r["category"]})
    return chosen, audit


def complete_first(rows: dict[str, dict]) -> dict[tuple[str, str, str], dict]:
    """Frozen v5 S2 rule: declared repeat 1, COMPLETE parser-v2 receipt per rater slot."""
    out = {}
    for r in rows.values():
        if r.get("repeat") != 1 or r.get("category") != "COMPLETE":
            continue
        if not transport_evidence(r,r['prompt_sha256'])[0]:
            continue
        if r.get("score_0_5_parser_v2") is None:
            continue
        k = (r["item"], r["frame"], r["_declared_model"])
        if k in out:
            raise ValueError(f"duplicate first COMPLETE slot after recovery precedence: {k}")
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
    declared_main = json.loads(raw)["S2"]
    late = load_json(INPUT / "late" / "manifest_G16_G17.json")
    panel = load_json(INPUT / "panel.json")
    families = {x["key"]: x["family"] for x in panel["members"]}
    # G00 is the historical 75-item anchor, expressly outside the 50-task fresh pool.
    items = {x["item"]: x for x in manifest["items"] if x["group"] != "G00"}
    items.update({x["item"]: x for x in late["items"]})
    declared_late = late["cells"]["S2"]
    declared = {c["cell"]: c for c in declared_main + declared_late}
    if len(declared) != len(declared_main) + len(declared_late):
        raise ValueError("duplicate declared S2 cell id")
    files = sorted(RAW.glob("*/*cells.jsonl"))
    required = {"S2_" + k for k in families} | {"LATE_S2_" + k for k in families}
    actual = {p.parent.name for p in files}
    missing_runs = sorted(required - actual)
    rows, hashes = [], {}
    raw_audit = Counter()
    for p in files:
        hashes[str(p.relative_to(ROOT))] = sha(p)
        source = p.parent.name
        file_rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
        raw_audit.update((r.get("run_key"), r.get("category")) for r in file_rows)
        rows.extend((source, r) for r in file_rows if r.get("cell") in declared)
    resolved, recovery_audit = resolve_receipts(rows, declared)
    slots = complete_first(resolved)
    audit = Counter((r.get("run_key"), r.get("category")) for r in resolved.values())
    targets, coverage = [], Counter()
    for iid, item in sorted(items.items()):
        fv, c0 = {}, {}
        for model, family in families.items():
            if item["blank"]:
                # Frozen v5 aggregation assigns blank items zero without a model call.
                fv[family] = 0.0
                c0[family] = 0.0
                continue
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
    saved_path = INPUT / "targets_main_saved.csv"
    saved = {r["item"]: r for r in csv.DictReader(saved_path.open())} if saved_path.exists() else {}
    compared, mismatches = 0, []
    for row in targets:
        old = saved.get(row["item"])
        if old is None:
            continue
        compared += 1
        for key in ("T_all", "T_C0"):
            got = row[key]
            want = None if old[key] == "" else float(old[key])
            if (got is None) != (want is None) or (got is not None and round(got, 6) != want):
                mismatches.append({"item": row["item"], "field": key, "got_rounded": None if got is None else round(got, 6), "saved": want})
    recovery_summary = {"initial_cells": recovery_audit["initial_cells"],
                        "accepted_count": len(recovery_audit["accepted_recoveries"]),
                        "ignored_count": len(recovery_audit["ignored_recoveries"]),
                        "accepted_sha256": hashlib.sha256(json.dumps(recovery_audit["accepted_recoveries"], sort_keys=True).encode()).hexdigest(),
                        "ignored_sha256": hashlib.sha256(json.dumps(recovery_audit["ignored_recoveries"], sort_keys=True).encode()).hexdigest()}
    report = {"run_id": RUN_ID, "source_commit": "ccd86d467fd7577826c4b549df2c532bf43b1892", "input_hashes": {str(p.relative_to(INPUT)): sha(p) for p in (INPUT / "manifest.json", INPUT / "manifest_cells.json.gz", INPUT / "panel.json", INPUT / "late" / "manifest_G16_G17.json", saved_path) if p.exists()}, "raw_cell_hashes": hashes, "panel_families": families, "expected_raw_runs": sorted(required), "missing_raw_runs": missing_runs, "raw_category_counts_before_recovery_precedence": {f"{k[0]}::{k[1]}": v for k, v in sorted(raw_audit.items())}, "resolved_s2_category_counts": {f"{k[0]}::{k[1]}": v for k, v in sorted(audit.items())}, "first_complete_slots": len(slots), "items": coverage, "recovery_precedence": recovery_summary, "saved_target_comparison": {"source": str(saved_path.relative_to(ROOT)) if saved_path.exists() else None, "source_git_blob": TARGET_CSV_SOURCE_BLOB, "source_content_sha256_before_lf_normalization": TARGET_CSV_SOURCE_CONTENT_SHA256, "items_compared": compared, "six_decimal_mismatches": mismatches, "late_items_without_saved_target_file": sum(1 for row in targets if row["group"] in {"G16", "G17"})}, "note": "No criterion association or new judge score is computed here; first COMPLETE S2 parser-v2 calls reconstruct simulated-panel targets after frozen recovery precedence."}
    if args.check:
        assert not missing_runs
        assert len(targets) == 750
        assert len({x["item"] for x in targets}) == 750
        assert compared == 650
        assert not mismatches
    OUT.mkdir(exist_ok=True)
    (OUT / "zero_call_inventory.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (ROOT/'private/targets_with_family_values.json').write_text(json.dumps(targets,indent=2,sort_keys=True)+'\n')
    public=[{**{k:v for k,v in r.items() if k not in ('family_values','c0_values')},
             'T_excluding_Anthropic':target_excluding(r['family_values'],{'Anthropic'}),
             'T_excluding_Alibaba':target_excluding(r['family_values'],{'Alibaba'}),
             'T_excluding_OpenAI':target_excluding(r['family_values'],{'OpenAI'}),
             'T_excluding_Anthropic_OpenAI':target_excluding(r['family_values'],{'Anthropic','OpenAI'})} for r in targets]
    (OUT / "targets_reconstructed.json").write_text(json.dumps(public, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"items": len(targets), "slots": len(slots), "missing_runs": missing_runs, "coverage": coverage}, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
