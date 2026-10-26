#!/usr/bin/env python3
"""TLDR: Rebuild experiment 39's and experiment 42's probe texts and judge prompts off SNAP, from a VeriBench clone and
the two experiments' own (imported, unedited) builders and renderers, and verify every cell against the committed
hashes: candidate_sha256 per probe and prompt_sha256 per (prompt, cell) in results/cells/. Lean is replayed, not run:
a probe counts as valid exactly when the committed manifest says Lean accepted it. Only hash-matched cells are written
to private/prompts/<exp>/<prompt>.jsonl.gz for judging; every mismatch is listed in results/REBUILD_REPORT.json and its
cell is marked unmeasured_rebuild_mismatch, never judged. Zero model calls.

Usage: E58_VERIBENCH_REPO=<veribench clone> rebuild_prompts.py [--exps e39,e42] [--prompts D0,R4,...]"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402


# ------------------------------------------------------------------ experiment 39 probes
def e39_oracle(manifest: dict):
    """A `code -> bool` stand-in for Lean that answers exactly as the committed manifest records.

    Accepted: every artifact the manifest marks valid (except crit/blank rows, which are valid regardless of
    elaboration), each gold that elaborated (its ident row is valid) and each candidate whose own probes were attempted
    (no 'candidate does not elaborate' row). Anything else was rejected by Lean or never reached it."""
    ok = set()
    for r in manifest["rows"]:
        if r["valid"] is True and r["kind"] not in ("crit", "blank") and r["sha256"]:
            ok.add(r["sha256"])
        if r["kind"] in ("ms_cand", "alpha", "reorder", "sorry", "spam") and r["reason"] != "candidate does not elaborate":
            ok.add(r["source_sha256"])
    return lambda code: e58.sha(code.encode()) in ok


def rebuild_e39(manifest: dict) -> tuple[dict[str, dict], dict]:
    """probe_id -> {row fields + code} for every manifest-valid probe, rebuilt with experiment 39's build_task."""
    e39, probes, _ = e58.e39_modules()
    sys.path.insert(0, str(e58.E39_DIR / "scripts"))
    import build_probes                                       # noqa: E402  (experiment 39's builder, unedited)
    texts: dict[tuple, str] = {}
    original_write = build_probes.write_artifact

    def capture(kind, key, level, code):                      # keep the text in memory instead of e39/private/
        texts[(kind, key, level)] = code
        return Path(f"<rebuilt>/{kind}/{key}__L{level}.lean")

    build_probes.write_artifact = capture
    try:
        validate = e39_oracle(manifest)
        items = e39.load_items()
        by_task: dict[str, list[dict]] = {}
        for it in items:
            by_task.setdefault(it["task"], []).append(it)
        rows = []
        for task in sorted(by_task):
            rows += build_probes.build_task(task, by_task[task][0], sorted(by_task[task], key=lambda r: r["item"]), validate, None)
    finally:
        build_probes.write_artifact = original_write
    by_item = {it["item"]: it for it in items}
    first_of_task = {}
    for it in items:
        first_of_task.setdefault(it["task"], it)
    rebuilt = {}
    for r in rows:
        if r["valid"] is not True:
            continue
        base = by_item[r["item"]] if r["item"] else first_of_task[r["task"]]
        if r["kind"] == "crit":
            code = Path(base["candidate_path_abs"]).read_text(encoding="utf-8", errors="replace")
        elif r["kind"] == "ident":
            code = Path(base["ref_ann_path_abs"]).read_text(encoding="utf-8", errors="replace")
        elif r["kind"] == "blank":
            code = ""
        else:
            code = texts[(r["kind"], r["key"], r["level"])]
        rebuilt[r["probe_id"]] = dict(r, code=code, base_item=base,
                                      candidate_name=base["candidate_file"] if r["item"] else f"{r['task']}__agent3.lean")
    committed = {r["probe_id"]: r for r in manifest["rows"] if r["valid"] is True}
    report = probe_report(committed, rebuilt)
    return rebuilt, report


# ------------------------------------------------------------------ experiment 42 probes
def rebuild_e42(manifest: dict) -> tuple[dict[str, dict], dict]:
    """probe_id -> row + code for every valid experiment 42 probe, from its own constructors (Lean replayed by the
    manifest: over-constraint level 2 re-applies the manifest's dropped_targets, which Lean errors chose)."""
    e42, S, _ = e58.e42_modules()
    refs = e42.references()
    first_of_task = {}
    for it in e42.load_items():
        first_of_task.setdefault(it["task"], it)
    specs = {}
    rebuilt = {}
    for r in manifest["rows"]:
        if r["valid"] is not True:
            continue
        task, kind, level = r["task"], r["kind"], r["level"]
        ref = refs[task]["text"]
        code, err = None, ""
        try:
            if kind == "ident":
                code = ref
            elif kind == "vac_true":
                code = S.vac_true(ref)
            elif kind == "vac_hyp":
                code = S.vac_hyp(ref)
            elif kind == "weak":
                if task not in specs:
                    path = e42.E / "probe_edits" / f"{task}.json"
                    specs[task] = {p.level: p for p, _ in S.weak_levels(ref, e42.read_json(path))} if path.exists() else {}
                p = specs[task].get(level)
                code = p.code if p is not None else None
            elif kind == "overc":
                made = S.overc(ref, level, frozenset(r.get("extra", {}).get("dropped_targets", [])))
                code = made[0] if made else None
            elif kind == "fmt_comments":
                code = S.fmt_comments(ref)
            elif kind == "fmt_layout":
                code = S.fmt_layout(ref)
        except Exception as exc:                              # a constructor that raises is a documented mismatch
            err = f"{type(exc).__name__}: {exc}"[:200]
        if code is None:
            rebuilt[r["probe_id"]] = dict(r, code=None, rebuild_error=err or "constructor returned nothing")
            continue
        rebuilt[r["probe_id"]] = dict(r, key=task, item=None, code=code, base_item=first_of_task[task],
                                      candidate_name=f"{task}__agent3.lean")
    committed = {r["probe_id"]: r for r in manifest["rows"] if r["valid"] is True}
    return rebuilt, probe_report(committed, rebuilt)


def probe_report(committed: dict[str, dict], rebuilt: dict[str, dict]) -> dict:
    by_kind: dict[str, Counter] = {}
    mismatches = []
    for pid, r in committed.items():
        c = by_kind.setdefault(r["kind"], Counter())
        c["committed"] += 1
        got = rebuilt.get(pid)
        if got is None or got.get("code") is None:
            c["missing"] += 1
            mismatches.append({"probe_id": pid, "why": "not rebuilt" if got is None else got.get("rebuild_error")})
            continue
        got_sha = e58.sha(got["code"].encode())
        if got_sha == r["sha256"]:
            c["match"] += 1
            got["sha_match"] = True
        else:
            c["mismatch"] += 1
            got["sha_match"] = False
            mismatches.append({"probe_id": pid, "why": "candidate_sha256 differs", "committed": r["sha256"], "rebuilt": got_sha})
    extra = sorted(set(p for p, r in rebuilt.items() if r.get("code") is not None) - set(committed))
    n = sum(c["committed"] for c in by_kind.values())
    m = sum(c["match"] for c in by_kind.values())
    return {"n_committed_valid": n, "n_match": m, "match_rate": round(m / n, 6) if n else None,
            "by_kind": {k: dict(v) for k, v in sorted(by_kind.items())}, "mismatches": mismatches,
            "rebuilt_not_in_manifest": extra}


# ------------------------------------------------------------------ rendering (experiment 39's render_unit logic)
def render_cells(exp: str, prompt_key: str, rebuilt: dict[str, dict], repeats_of) -> list[dict]:
    e39, _, legacy = e58.e39_modules()
    _, prompts_mod, _ = e39.x100_modules()
    unit = e39.PROMPTS[prompt_key]
    out = []
    for pid in sorted(rebuilt):
        r = rebuilt[pid]
        if r.get("code") is None or not r.get("sha_match"):
            continue
        base, text = r["base_item"], r["code"]
        status, value, reason, system, user = "render", None, "", None, None
        if unit["family"] == "legacy":
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
        for repeat in range(1, repeats_of(r["kind"]) + 1):
            cell = {"cell": f"{r['kind']}__{r['key']}__L{r['level']}__r{repeat}", "kind": r["kind"], "key": r["key"],
                    "task": r["task"], "item": r["item"], "level": r["level"], "repeat": repeat, "probe_id": pid,
                    "candidate_sha256": r["sha256"], "status": status}
            if status == "render":
                cell.update(prompt_sha256=e58.prompt_sha(system, user), system=system, user=user)
            elif status == "deterministic":
                cell.update(score=value, reason=reason)
            else:
                cell.update(reason=reason)
            out.append(cell)
    return out


def committed_cells(exp: str, prompt_key: str) -> tuple[str | None, dict[str, dict]]:
    """The committed cells file of any experiment-39/42 model for this prompt (prompt bytes do not depend on the model;
    every committed model file of a prompt carries identical hashes, checked in the report)."""
    d = (e58.E39_DIR if exp == "e39" else e58.E42_DIR) / "results/cells"
    files = sorted(d.glob(f"*__{prompt_key}.json"))
    if not files:
        return None, {}
    blobs = [e58.read_json(f) for f in files]
    ref = {c["cell"]: c for c in blobs[0]["cells"]}
    for b in blobs[1:]:
        other = {c["cell"]: (c.get("prompt_sha256"), c["status"]) for c in b["cells"]}
        if other != {k: (v.get("prompt_sha256"), v["status"]) for k, v in ref.items()}:
            raise SystemExit(f"committed {exp} cells for {prompt_key} differ across models ({files[0].name} vs {b['config']})")
    return files[0].name, ref


def verify(exp: str, prompt_key: str, cells: list[dict]) -> tuple[list[dict], dict]:
    """Mark each rebuilt cell matched or not against the committed cell; add committed cells that were not rebuilt."""
    source, ref = committed_cells(exp, prompt_key)
    got = {c["cell"]: c for c in cells}
    counts, mismatches, final = Counter(), [], []
    for cid in sorted(set(ref) | set(got)):
        c, r = got.get(cid), ref.get(cid)
        if r is None:
            counts["rebuilt_not_committed"] += 1
            mismatches.append({"cell": cid, "why": "rebuilt cell absent from the committed cells"})
            continue
        if c is None:
            counts["committed_not_rebuilt"] += 1
            mismatches.append({"cell": cid, "why": "committed cell not rebuilt (its probe did not match or was not rebuilt)"})
            final.append({k: r[k] for k in ("cell", "kind", "key", "task", "item", "level", "repeat", "probe_id", "candidate_sha256")}
                         | {"status": "unmeasured_rebuild_mismatch", "reason": "probe not rebuilt byte-identically", "e39_status": r["status"]})
            continue
        ok = c["status"] == r["status"] and c["candidate_sha256"] == r["candidate_sha256"]
        if ok and c["status"] == "render":
            ok = c["prompt_sha256"] == r["prompt_sha256"]
        if ok and c["status"] == "deterministic":
            ok = c["score"] == r.get("score")
        if ok:
            counts["match_" + c["status"]] += 1
            final.append(c)
        else:
            counts["mismatch"] += 1
            mismatches.append({"cell": cid, "why": "status/candidate/prompt hash differs", "committed_status": r["status"],
                               "rebuilt_status": c["status"], "committed_prompt_sha256": r.get("prompt_sha256"),
                               "rebuilt_prompt_sha256": c.get("prompt_sha256")})
            final.append({k: c[k] for k in ("cell", "kind", "key", "task", "item", "level", "repeat", "probe_id", "candidate_sha256")}
                         | {"status": "unmeasured_rebuild_mismatch", "reason": "rebuilt prompt hash != committed prompt hash"})
    n = len(ref)
    matched = sum(v for k, v in counts.items() if k.startswith("match_"))
    return final, {"committed_file": source, "n_committed": n, "n_rebuilt": len(got), "n_match": matched,
                   "match_rate": round(matched / n, 6) if n else None, "counts": dict(counts), "mismatches": mismatches}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exps", default="e39,e42")
    ap.add_argument("--prompts", default=",".join(e58.PROMPT_ORDER))
    ap.add_argument("--report", type=Path, default=e58.RESULTS / "REBUILD_REPORT.json")
    args = ap.parse_args()
    e39, _, _ = e58.e39_modules()
    report = {"written_utc": e58.stamp(), "experiment": e58.EXPERIMENT, "veribench_repo": str(e58.VB_REPO),
              "items_sha256": e58.sha_file(e39.X100 / "inputs/items.jsonl"), "exps": {}}
    for exp in args.exps.split(","):
        if exp == "e39":
            manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
            rebuilt, probe_rep = rebuild_e39(manifest)
            repeats_of = lambda kind: e39.KINDS[kind]["repeats"]  # noqa: E731
        else:
            manifest = e58.read_json(e58.E42_DIR / "results/semantic_probe_manifest.json")
            rebuilt, probe_rep = rebuild_e42(manifest)
            repeats_of = lambda kind: 3  # noqa: E731  (experiment 42: every kind has 3 repeats)
        if manifest["items_sha256"] != report["items_sha256"]:
            raise SystemExit(f"{exp}: VeriBench items.jsonl differs from the one the manifest was built on")
        exp_rep = {"probes": probe_rep, "prompts": {}}
        for prompt_key in args.prompts.split(","):
            cells, rep = verify(exp, prompt_key, render_cells(exp, prompt_key, rebuilt, repeats_of))
            e58.write_jsonl_gz(e58.prompts_path(exp, prompt_key), cells)
            rep["prompts_file_sha256"] = e58.sha_file(e58.prompts_path(exp, prompt_key))
            rep["n_to_judge"] = sum(1 for c in cells if c["status"] == "render")
            exp_rep["prompts"][prompt_key] = rep
            print(json.dumps({exp: prompt_key, "match_rate": rep["match_rate"], "n_committed": rep["n_committed"],
                              "counts": rep["counts"]}))
        tot_n = sum(p["n_committed"] for p in exp_rep["prompts"].values())
        tot_m = sum(p["n_match"] for p in exp_rep["prompts"].values())
        exp_rep["cells_match_rate"] = round(tot_m / tot_n, 6) if tot_n else None
        exp_rep["cells_committed"], exp_rep["cells_matched"] = tot_n, tot_m
        report["exps"][exp] = exp_rep
        print(json.dumps({exp: {"probe_match_rate": probe_rep["match_rate"], "cells_match_rate": exp_rep["cells_match_rate"],
                                "cells": f"{tot_m}/{tot_n}"}}))
    e58.write_json(args.report, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
