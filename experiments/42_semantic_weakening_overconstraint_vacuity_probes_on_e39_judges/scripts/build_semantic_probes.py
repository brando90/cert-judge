#!/usr/bin/env python3
"""TLDR: Build and Lean-validate every experiment 42 probe from the 25 annotation-era VeriBench references: identity,
vacuity (2 variants), weakening (up to 3 cumulative levels from probe_edits/<task>.json), over-constraint (2 levels)
and formatting (2 variants). Writes results/semantic_probe_manifest.json (one row per declared probe with its hash,
level, the Lean checks run and valid true/false with the reason), probe files under private/probes/ and check files
under private/checks/. Zero model calls.

Usage: build_semantic_probes.py [--tasks a,b] [--jobs 8] [--out results/semantic_probe_manifest.json]"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e42                                                    # noqa: E402
import semantic_probes as S                                   # noqa: E402

PROBE_DIR = e42.PRIVATE / "probes"
CHECK_DIR = e42.PRIVATE / "checks"
EDIT_DIR = e42.E / "probe_edits"
DECLARED = [("vac_true", 1), ("vac_hyp", 1), ("weak", 1), ("weak", 2), ("weak", 3), ("overc", 1), ("overc", 2),
            ("fmt_comments", 1), ("fmt_layout", 1)]


def save(kind: str, task: str, level: int, code: str) -> Path:
    path = PROBE_DIR / kind / f"{task}__L{level}.lean"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return path


def row(task: str, p: S.Probe, ref_sha: str, path: Path | None, proposer: str | None = None) -> dict:
    return {"probe_id": f"{p.kind}__{task}__L{p.level}", "kind": p.kind, "family": e42.KINDS[p.kind]["family"], "task": task,
            "level": p.level, "path": str(path) if path else None, "sha256": p.sha256 if p.valid else None,
            "source_sha256": ref_sha, "valid": p.valid, "reason": p.reason, "note": p.note, "reverse": p.reverse,
            "checks": p.checks, "extra": {k: v for k, v in p.extra.items() if not k.startswith("_")},
            "proposer": proposer}


def dump_check(task: str, p: S.Probe) -> None:
    if "_check_text" in p.extra:
        d = CHECK_DIR / task
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{p.kind}_L{p.level}.lean").write_text(p.extra["_check_text"])
        (d / f"{p.kind}_L{p.level}.out").write_text(p.extra["_check_output"])


def build_task(task: str, ref_info: dict, validator: S.Validator, only: set[str] | None = None) -> list[dict]:
    ref = ref_info["text"]
    ref_sha = e42.sha(ref.encode())
    rows = []
    ref_ok = validator.compile(ref)
    ident = S.Probe("ident", 1, ref, "reference as its own candidate")
    ident.valid, ident.reason = (True, "") if ref_ok.ok else (False, "reference does not elaborate: " + S._first_error(ref_ok.output))
    ident.reverse = "not_applicable"
    rows.append(row(task, ident, ref_sha, Path(ref_info["path"])))
    if not ref_ok.ok:
        for kind, level in DECLARED:
            p = S.Probe(kind, level, None, e42.KINDS[kind]["doc"], False, "reference does not elaborate (no anchor)")
            rows.append(row(task, p, ref_sha, None))
        return rows

    def finish(p: S.Probe, proposer: str | None = None) -> None:
        dump_check(task, p)
        path = save(p.kind, task, p.level, p.code) if p.valid else None
        rows.append(row(task, p, ref_sha, path, proposer))

    if only is not None:                       # proposer iteration: build only the requested families
        rows[:] = rows[:1]
    # Vacuity.
    for kind, fn in (("vac_true", S.vac_true), ("vac_hyp", S.vac_hyp)) if only is None or "vacuity" in only else ():
        p = S.Probe(kind, 1, fn(ref), e42.KINDS[kind]["doc"])
        if p.code is None:
            p.reason = "no change applies (no theorem, or no theorem keeps a binder or premise)" if kind == "vac_hyp" else "no theorem"
        finish(S.judge_semantic(p, validator, ref))

    # Weakening (proposed edits, validated here).
    if only is not None and "weakening" not in only:
        return rows
    spec_path = EDIT_DIR / f"{task}.json"
    spec = e42.read_json(spec_path) if spec_path.exists() else {"levels": []}
    proposer = spec.get("proposer")
    built = {}
    for p, info in S.weak_levels(ref, spec):
        if p.valid is None:
            S.judge_semantic(p, validator, ref, proofs=info["proofs"], closure=info["closure"], edited_defs=info["edited_defs"])
        p.extra["closure"] = sorted(info["closure"])
        built[p.level] = p
    for level in (1, 2, 3):
        if level in built:
            finish(built[level], proposer)
        else:
            reason = spec.get("no_more_levels_reason") or "no weakening edit proposed at this level"
            finish(S.Probe("weak", level, None, e42.KINDS["weak"]["doc"], False,
                           f"not constructed: {reason}" if spec_path.exists() else "not constructed: no probe_edits file"), proposer)

    if only is not None:
        return rows
    # Over-constraint.
    for level in (1, 2):
        made, dropped = S.overc(ref, level), set()
        for _ in range(4):                     # L2: drop targets whose own proof breaks under the hypothesis, retry
            if made is None or level == 1:
                break
            compiled = validator.compile(made[0])
            if compiled.ok:
                break
            broken = S.theorems_with_errors(made[0], compiled.output) & {a["theorem"] for a in made[1]}
            if not broken:
                break
            dropped |= broken
            made = S.overc(ref, level, frozenset(dropped))
        if made is None:
            p = S.Probe("overc", level, None, e42.KINDS["overc"]["doc"], False,
                        "no eligible theorem (needs an explicit Nat/List/Array/String/Int binder)" if level == 1
                        else "fewer than two eligible theorems (level 2 would equal level 1)")
            finish(p)
            continue
        code, added = made
        p = S.Probe("overc", level, code, "; ".join(f"{a['theorem']} += {a['hypothesis']}" for a in added))
        p.extra["added"] = added
        p.extra["dropped_targets"] = sorted(dropped)
        finish(S.judge_semantic(p, validator, ref, unsat=added))

    # Formatting only.
    ref_msgs = S.normalized_messages(validator.compile(ref + S.print_block(ref)).output)
    for kind, fn in (("fmt_comments", S.fmt_comments), ("fmt_layout", S.fmt_layout)):
        finish(S.judge_formatting(S.Probe(kind, 1, fn(ref), e42.KINDS[kind]["doc"]), validator, ref, ref_msgs))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", type=Path, default=e42.RESULTS / "semantic_probe_manifest.json")
    ap.add_argument("--lake-dir", type=Path, default=e42.LAKE_DIR)
    ap.add_argument("--lake-bin", type=Path, default=e42.LAKE_BIN)
    ap.add_argument("--only", default="", help="comma list of families to build (vacuity,weakening); proposer iteration only")
    args = ap.parse_args()
    refs = e42.references()
    tasks = sorted(refs) if not args.tasks else [t for t in args.tasks.split(",") if t]
    validator = S.Validator(args.lake_dir, args.lake_bin, args.timeout)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        only = set(args.only.split(",")) if args.only else None
        per_task = list(pool.map(lambda t: build_task(t, refs[t], validator, only), tasks))
    rows = [r for group in per_task for r in group]
    counts: dict[str, dict[str, int]] = {}
    reasons: dict[str, dict[str, int]] = {}
    for r in rows:
        bucket = counts.setdefault(r["kind"], {"valid": 0, "invalid": 0})
        bucket["valid" if r["valid"] else "invalid"] += 1
        if not r["valid"]:
            key = r["reason"].split(":")[0][:80]
            reasons.setdefault(r["kind"], {}).setdefault(key, 0)
            reasons[r["kind"]][key] += 1
    manifest = {"written_utc": e42.stamp(), "experiment": e42.EXPERIMENT,
                "lean": {"lake_dir": str(args.lake_dir), "lake_bin": str(args.lake_bin), "timeout_seconds": args.timeout},
                "items_sha256": e42.sha_file(e42.X100 / "inputs/items.jsonl"), "n_tasks": len(tasks),
                "declared_per_task": [["ident", 1]] + [list(x) for x in DECLARED], "kinds": e42.KINDS,
                "counts": counts, "invalid_reasons": reasons, "rows": rows}
    if args.tasks:
        args.out = args.out.with_name(args.out.stem + "_partial.json") if args.out.name == "semantic_probe_manifest.json" else args.out
    e42.write_json(args.out, manifest)
    print(json.dumps({"out": str(args.out), "n_rows": len(rows), "counts": counts, "invalid_reasons": reasons}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
