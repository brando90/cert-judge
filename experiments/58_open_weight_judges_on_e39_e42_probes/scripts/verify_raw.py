#!/usr/bin/env python3
"""Read-only E58 raw/metadata/harvest replay. No inference or source rewrites.

Requires rebuilt private prompts and a collected run with MANIFEST.sha256.
Writes only the explicitly named receipt; exits nonzero on any integrity error.
Recorded runtime deviations are reported separately from parser reproduction.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import analysis_inputs as I
import e58
import harvest_lib as H


def validate_raw(rows: list[dict], prompts: list[dict], model: str, prompt: str) -> None:
    """Reject rows the historical last-write-wins harvester could silently hide."""
    expected = {p["cell"]: p for p in prompts}
    seen = set()
    cfg = e58.config_id(model, prompt)
    m = e58.MODELS[model]
    max_tokens = e58.e39_modules()[0].PROMPTS[prompt]["max_tokens"]
    for r in rows:
        cell = r["cell"]
        if cell in seen or cell not in expected or expected[cell]["status"] != "render":
            raise ValueError(f"duplicate, unknown or non-rendered raw cell: {cell}")
        seen.add(cell)
        status = r.get("status")
        if status not in ("generated", *H.NOT_CALLED):
            raise ValueError(f"unknown raw status: {cell}: {status}")
        if status == "unmeasured_infra":
            continue
        n_prompt = r.get("n_prompt_tokens")
        if type(n_prompt) is not int or n_prompt < 0:
            raise ValueError(f"invalid prompt token count: {cell}")
        budget = min(max_tokens, m["max_model_len"] - n_prompt)
        if type(r.get("budget")) is not int or r["budget"] != budget:
            raise ValueError(f"wrong generation budget: {cell}")
        if status == "unmeasured_over_context":
            if budget >= e58.MIN_GENERATION_BUDGET:
                raise ValueError(f"incorrect over-context status: {cell}")
            continue
        if budget < e58.MIN_GENERATION_BUDGET:
            raise ValueError(f"generated below minimum budget: {cell}")
        if r.get("prompt_sha256") != expected[cell]["prompt_sha256"]:
            raise ValueError(f"raw prompt hash mismatch: {cell}")
        seed = int(e58.sha(f"58|{cfg}|{cell}".encode())[:8], 16)
        if type(r.get("seed")) is not int or r["seed"] != seed:
            raise ValueError(f"wrong per-cell seed: {cell}")
        n_output = r.get("n_output_tokens")
        if type(n_output) is not int or not 0 <= n_output <= budget:
            raise ValueError(f"invalid output token count: {cell}")
        if not isinstance(r.get("text"), str):
            raise ValueError(f"missing raw text: {cell}")


def checked_prompts(exp: str, prompt: str) -> list[dict]:
    rows = e58.read_jsonl(e58.prompts_path(exp, prompt))
    declared = {r["cell"]: r for r in I.declared_cells(exp, prompt)}
    if len(rows) != len(declared) or {r["cell"] for r in rows} != set(declared):
        raise ValueError(f"rebuilt prompt cell set mismatch: {exp}/{prompt}")
    for r in rows:
        d = declared[r["cell"]]
        if any(r.get(k) != d.get(k) for k in ("kind", "key", "task", "item", "level", "repeat", "prompt_sha256")):
            raise ValueError(f"rebuilt prompt identity mismatch: {exp}/{prompt}/{r['cell']}")
        if r["status"] == "render" and e58.prompt_sha(r["system"], r["user"]) != r["prompt_sha256"]:
            raise ValueError(f"rebuilt prompt text hash mismatch: {exp}/{prompt}/{r['cell']}")
    return rows


def comparable(harvest: dict) -> dict:
    return {k: v for k, v in harvest.items() if k != "written_utc"}


def verify(run: Path) -> dict:
    collection = I.verify_collection(run)
    listed = {(run / line[66:]).resolve() for line in (run / "MANIFEST.sha256").read_text().splitlines()}
    inputs = {p.resolve() for folder in ("raw", "harvest") for p in (run / folder).rglob("*") if p.is_file()}
    if not inputs <= listed:
        raise ValueError("raw/meta/harvest inputs are not all covered by MANIFEST.sha256")
    runtime = I.runtime_contract(run)  # Also checks declared harvest identities and score ranges.
    if not runtime["n_present_harvests"]:
        raise ValueError("no observed harvests: empty input is not raw verification")
    results, raw_only, expected_paths = [], [], set()
    prompt_hashes = {}
    status_counts = Counter()
    score_histogram = Counter()
    for exp in e58.EXPS:
        for prompt in e58.PROMPT_ORDER:
            prompts = checked_prompts(exp, prompt)
            prompt_hashes[f"{exp}/{prompt}"] = e58.sha_file(e58.prompts_path(exp, prompt))
            for model in e58.MODEL_ORDER:
                rp = H.raw_path(run, exp, model, prompt)
                mp = rp.with_suffix(".meta.json")
                hp = H.harvest_path(run, exp, model, prompt)
                expected_paths.update((rp.resolve(), mp.resolve()))
                if not rp.exists():
                    if hp.exists():
                        raise ValueError(f"harvest without raw source: {hp.relative_to(run)}")
                    if mp.exists():
                        raise ValueError(f"metadata without raw source: {mp.relative_to(run)}")
                    continue
                rows = e58.read_jsonl(rp)
                validate_raw(rows, prompts, model, prompt)
                if not hp.exists():
                    raw_only.append({"path": str(rp.relative_to(run)), "n_rows": len(rows), "sha256": e58.sha_file(rp)})
                    continue
                if not mp.is_file():
                    raise ValueError(f"harvest without raw metadata: {hp.relative_to(run)}")
                saved = e58.read_json(hp)
                replay = H.build_harvest(exp, model, prompt, prompts, rows, e58.read_json(mp))
                if comparable(saved) != comparable(replay):
                    changed = sorted(k for k in set(saved) | set(replay) if k != "written_utc" and saved.get(k) != replay.get(k))
                    raise ValueError(f"harvest replay mismatch: {hp.relative_to(run)}: {changed}")
                status_counts.update(saved["status_counts"])
                score_histogram.update(str(c["score"]) for c in saved["cells"] if c["status"] == "measured")
                results.append({"probe_set": exp, "config": saved["config"], "raw_rows": len(rows),
                                "n_cells": saved["n_cells"], "status_counts": saved["status_counts"],
                                "raw_sha256": e58.sha_file(rp), "meta_sha256": e58.sha_file(mp),
                                "harvest_sha256": e58.sha_file(hp), "replay": "EXACT_EXCEPT_WRITTEN_UTC"})
    unexpected = sorted(str(p.relative_to(run.resolve())) for p in inputs if p.is_relative_to((run / "raw").resolve()) and p not in expected_paths)
    if unexpected:
        raise ValueError(f"unexpected raw input paths: {unexpected}")
    code = {name: e58.sha_file(Path(path)) for name, path in {
        "verify_raw.py": __file__, "analysis_inputs.py": I.__file__, "e58.py": e58.__file__,
        "harvest_lib.py": H.__file__, "legacy_parser.py": e58.e39_modules()[2].__file__,
        "veribench_prompts.py": H._x100_prompts().__file__}.items()}
    return {"status": "VERIFIED_RAW_REPLAY", "written_utc": e58.stamp(), "collection": collection,
            "code_sha256": code, "rebuilt_prompt_file_sha256": prompt_hashes,
            "n_replayed_harvests": len(results), "n_raw_rows_replayed": sum(r["raw_rows"] for r in results),
            "n_cells_replayed": sum(r["n_cells"] for r in results), "status_counts": dict(status_counts),
            "measured_score_histogram": dict(sorted(score_histogram.items())), "runtime_contract": runtime,
            "raw_only_without_harvest": raw_only, "harvests": results,
            "limits": "Checks recorded data, not executed weight identity or a fresh generation. Raw-only rows are checked but not admitted as new harvests."}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--receipt", required=True, type=Path)
    args = ap.parse_args()
    if args.receipt.resolve().is_relative_to(args.run.resolve()):
        ap.error("receipt must be outside the immutable source run")
    try:
        result = verify(args.run)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        e58.write_json(args.receipt, {"status": "FAILED", "written_utc": e58.stamp(), "error": str(exc)})
        print(str(exc))
        return 1
    e58.write_json(args.receipt, result)
    print(json.dumps({k: result[k] for k in ("status", "n_replayed_harvests", "n_raw_rows_replayed", "n_cells_replayed")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
