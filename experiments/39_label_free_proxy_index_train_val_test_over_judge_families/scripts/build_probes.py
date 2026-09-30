#!/usr/bin/env python3
"""TLDR: Build every label-free probe of experiment 39 from experiment 100's annotation-era golds and the 75
rated candidates (identity, blank, theorem-deletion ladders on gold and candidates, bug ladders, alpha /
reorder / proof-to-sorry rewrites, spam), validate each transformed artifact with the pinned Lean project
(fail-closed), and write the structural manifest results/probe_manifest.json. Zero model calls."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402
import probes as P                                            # noqa: E402

PROBE_DIR = e39.PRIVATE / "probes"


def write_artifact(kind: str, key: str, level: int, code: str) -> Path:
    path = PROBE_DIR / kind / f"{key}__L{level}.lean"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return path


def row(kind: str, key: str, task: str, item: str | None, level: int, path: Path | None, artifact, source_sha: str,
        valid, reason: str = "") -> dict:
    return {"probe_id": f"{kind}__{key}__L{level}", "kind": kind, "key": key, "task": task, "item": item, "level": level,
            "path": str(path) if path else None, "sha256": artifact.sha256 if artifact else None,
            "source_sha256": source_sha, "valid": valid, "reason": reason, "note": artifact.note if artifact else ""}


def build_task(task: str, first: dict, cands: list[dict], validate, unvalidated) -> list[dict]:
    rows = []
    gold = Path(first["ref_ann_path_abs"]).read_text(encoding="utf-8", errors="replace")
    gold_sha = e39.sha(gold.encode())
    gold_ok = True if validate is None else validate(gold)
    rows.append(row("ident", task, task, None, 0, None, P.Artifact(0, gold, gold_sha, "gold as candidate"), gold_sha,
                    unvalidated if validate is None else gold_ok, "" if gold_ok else "gold does not elaborate"))
    rows.append(row("blank", task, task, None, 0, None, P.Artifact(0, "", e39.sha(b""), "empty candidate"), gold_sha, True))
    if gold_ok:
        ladder = P.delete_theorems_ladder(gold, e39.KINDS["ms_gold"]["levels"], validate)
        for art in ladder[1:]:
            rows.append(row("ms_gold", task, task, None, art.level, write_artifact("ms_gold", task, art.level, art.code), art,
                            gold_sha, unvalidated if validate is None else True))
        declared = len(P.cut_points(len(P.theorem_decls(gold)), e39.KINDS["ms_gold"]["levels"]))
        for level in range(len(ladder), declared + 1):
            rows.append(row("ms_gold", task, task, None, level, None, None, gold_sha, False, "level did not elaborate or was a no-op"))
        bugs = P.bug_ladder(gold, validate, e39.KINDS["bm_gold"]["levels"])
        for art in bugs[1:]:
            rows.append(row("bm_gold", task, task, None, art.level, write_artifact("bm_gold", task, art.level, art.code), art,
                            gold_sha, unvalidated if validate is None else True))
        for level in range(len(bugs), e39.KINDS["bm_gold"]["levels"] + 1):
            rows.append(row("bm_gold", task, task, None, level, None, None, gold_sha, False, "no compile-valid cumulative mutation"))
    else:
        for kind in ("ms_gold", "bm_gold"):
            rows.append(row(kind, task, task, None, 1, None, None, gold_sha, False, "gold does not elaborate"))
    for it in cands:
        item = it["item"]
        cand = Path(it["candidate_path_abs"]).read_text(encoding="utf-8", errors="replace")
        cand_sha = e39.sha(cand.encode())
        rows.append(row("crit", item, task, item, 0, None, P.Artifact(0, cand, cand_sha, "rated candidate"), cand_sha, True))
        cand_ok = True if validate is None else validate(cand)
        if not cand_ok:
            for kind in ("ms_cand", "alpha", "reorder", "sorry", "spam"):
                rows.append(row(kind, item, task, item, 1, None, None, cand_sha, False, "candidate does not elaborate"))
            continue
        ladder = P.delete_theorems_ladder(cand, e39.KINDS["ms_cand"]["levels"], validate)
        for art in ladder[1:]:
            rows.append(row("ms_cand", item, task, item, art.level, write_artifact("ms_cand", item, art.level, art.code), art,
                            cand_sha, unvalidated if validate is None else True))
        declared = len(P.cut_points(len(P.theorem_decls(cand)), e39.KINDS["ms_cand"]["levels"]))
        for level in range(len(ladder), declared + 1):
            rows.append(row("ms_cand", item, task, item, level, None, None, cand_sha, False, "level did not elaborate or was a no-op"))
        for kind, fn in (("alpha", P.alpha), ("reorder", P.reorder), ("sorry", P.strip_proofs), ("spam", P.spam)):
            art = fn(cand, validate)
            if art is None:
                rows.append(row(kind, item, task, item, 1, None, None, cand_sha, False, "no conservative transform or it did not elaborate"))
            else:
                rows.append(row(kind, item, task, item, 1, write_artifact(kind, item, 1, art.code), art, cand_sha,
                                unvalidated if validate is None else True))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lake-dir", type=Path, default=e39.LAKE_DIR)
    ap.add_argument("--lake-bin", type=Path, default=e39.LAKE_BIN)
    ap.add_argument("--no-lean", action="store_true", help="construct without elaboration; probes are UNVALIDATED (dry runs only)")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", type=Path, default=e39.RESULTS / "probe_manifest.json")
    args = ap.parse_args()
    validate = None if args.no_lean else P.make_validator(args.lake_dir, args.lake_bin, args.timeout)
    unvalidated = None                       # `valid: null` marks an unvalidated (dry-run) artifact
    items = e39.load_items()
    by_task: dict[str, list[dict]] = {}
    for it in items:
        by_task.setdefault(it["task"], []).append(it)
    tasks = sorted(by_task)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        per_task = list(pool.map(lambda t: build_task(t, by_task[t][0], sorted(by_task[t], key=lambda r: r["item"]), validate, unvalidated), tasks))
    rows = [r for group in per_task for r in group]
    counts: dict[str, dict[str, int]] = {}
    for r in rows:
        bucket = counts.setdefault(r["kind"], {"valid": 0, "invalid": 0, "unvalidated": 0})
        bucket["valid" if r["valid"] is True else "invalid" if r["valid"] is False else "unvalidated"] += 1
    manifest = {"written_utc": e39.stamp(), "experiment": e39.EXPERIMENT, "lean": None if validate is None else
                {"lake_dir": str(args.lake_dir), "lake_bin": str(args.lake_bin), "timeout_seconds": args.timeout},
                "items_sha256": e39.sha_file(e39.X100 / "inputs/items.jsonl"), "n_tasks": len(tasks), "n_items": len(items),
                "kinds": e39.KINDS, "counts": counts, "rows": rows}
    e39.write_json(args.out, manifest)
    print(json.dumps({"n_rows": len(rows), "counts": counts, "validated": validate is not None}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
