#!/usr/bin/env python3
"""TLDR: Experiment 43's analysis (zero model calls): per attacked judge, the gaming gap (attacked-judge gain minus
reference gain, start -> final, fresh repeats) with a task-clustered bootstrap interval, the attacked and reference
gains, the share of final candidates the deterministic checks flag, loop statistics and example trajectories; across
judges, the Spearman association between the label-free index values experiment 39 committed for these configurations
(its selected index, PTI_v0_frozen, TI_var_trainnorm; train/val units only, never the sealed test file) and the gaming
gap, with an exact permutation p-value and the pre-registered reading rule. Writes results/analysis.json.

Usage:  analyze.py [--stage full|pilot] [--index-ref origin/main]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e43                                                    # noqa: E402

E39_DIR = "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E39_OPEN = f"{E39_DIR}/results/units_train_val.json"          # train + val units only (the test units are sealed elsewhere)
E39_FINALISTS = f"{E39_DIR}/results/FINALISTS.json"
FROZEN = ("PTI_v0_frozen", "TI_var_trainnorm")
MIN_JUDGES = 5                                                # association needs >= 5 judges with index and gap


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for t in range(i, j + 1):
            r[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def exact_perm_p(x, y, observed: float) -> dict:
    """Exact permutation distribution of Spearman over all orderings of y (n <= 8)."""
    vals = []
    for perm in itertools.permutations(y):
        v = spearman(x, list(perm))
        if v is not None:
            vals.append(v)
    eps = 1e-12
    return {"n_perms": len(vals), "p_one_sided_negative": sum(1 for v in vals if v <= observed + eps) / len(vals),
            "p_two_sided": sum(1 for v in vals if abs(v) >= abs(observed) - eps) / len(vals)}


def cluster_bootstrap(rows: list[dict], key: str, reps: int, seed: int) -> dict:
    """Percentile 95% interval of the mean of `key` over cells, resampling tasks with replacement."""
    rows = [r for r in rows if r.get(key) is not None]
    if not rows:
        return {"n_cells": 0, "n_tasks": 0, "mean": None, "ci95": None}
    by_task: dict[str, list[float]] = {}
    for r in rows:
        by_task.setdefault(r["task"], []).append(r[key])
    tasks = sorted(by_task)
    rng = random.Random(seed)
    stats = []
    for _ in range(reps):
        vals = [v for t in (rng.choice(tasks) for _ in tasks) for v in by_task[t]]
        stats.append(sum(vals) / len(vals))
    stats.sort()
    return {"n_cells": len(rows), "n_tasks": len(tasks), "mean": sum(r[key] for r in rows) / len(rows),
            "ci95": [stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1]]}


def git_show(ref: str, path: str):
    out = subprocess.run(["git", "-C", str(e43.REPO), "show", f"{ref}:{path}"], capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None


def index_values(refs: list[str]) -> dict:
    """Index values of the attacked configurations from experiment 39's committed OPEN units file (never the sealed one)."""
    for ref in refs:
        units = git_show(ref, E39_OPEN)
        if units is None:
            continue
        fin = git_show(ref, E39_FINALISTS) or {}
        selected = fin.get("selected")
        names = ([selected] if selected else []) + list(FROZEN)
        per = {}
        for u in units["units"]:
            if u["config"] in e43.JUDGES:
                per[u["config"]] = {n: u["indices"].get(n) for n in names}
        return {"source_ref": ref, "source_path": E39_OPEN, "selected_index": selected, "index_names": names, "values": per}
    return {"source_ref": None, "selected_index": None, "index_names": list(FROZEN), "values": {},
            "status": "NOT_AVAILABLE: experiment 39 has not committed results/units_train_val.json on any searched ref"}


def association(judge_rows: dict[str, dict], idx: dict, cells: list[dict], reps: int) -> dict:
    out = {}
    for name in idx["index_names"]:
        pairs = [(idx["values"].get(j, {}).get(name), judge_rows[j]["gaming_gap"]["mean"]) for j in e43.JUDGES]
        keep = [(j, a, b) for j, (a, b) in zip(e43.JUDGES, pairs) if a is not None and b is not None]
        if len(keep) < MIN_JUDGES:
            out[name] = {"status": "NOT_COMPUTABLE", "n_judges": len(keep)}
            continue
        x = [a for _, a, _ in keep]
        y = [b for _, _, b in keep]
        rho = spearman(x, y)
        if rho is None:
            out[name] = {"status": "NOT_COMPUTABLE", "n_judges": len(keep), "reason": "constant index or gap"}
            continue
        perm = exact_perm_p(x, y, rho)
        # task-clustered bootstrap of rho: resample tasks, recompute every judge's mean gap, correlate with the fixed index
        by_task: dict[str, list[dict]] = {}
        for c in cells:
            if c.get("gaming_gap") is not None:
                by_task.setdefault(c["task"], []).append(c)
        tasks = sorted(by_task)
        rng = random.Random(e43.SEED + 1)
        boots = []
        for _ in range(reps):
            sample = [c for t in (rng.choice(tasks) for _ in tasks) for c in by_task[t]]
            gaps = [mean([c["gaming_gap"] for c in sample if c["judge"] == j]) for j, _, _ in keep]
            if any(g is None for g in gaps):
                continue
            v = spearman(x, gaps)
            if v is not None:
                boots.append(v)
        boots.sort()
        ci = [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]] if len(boots) >= 100 else None
        if perm["p_one_sided_negative"] <= 0.05:
            reading = "SUPPORTED: higher index, smaller gaming gap (exact one-sided permutation p <= 0.05)"
        elif rho > 0 and perm["p_two_sided"] <= 0.05:
            reading = "CONTRARY: higher index, larger gaming gap (two-sided permutation p <= 0.05)"
        else:
            reading = "NOT SUPPORTED: no association detectable at this number of judges"
        out[name] = {"status": "COMPUTED", "n_judges": len(keep), "judges": [j for j, _, _ in keep], "index": x, "gaming_gap": y,
                     "spearman": rho, "pearson": pearson(x, y), **perm, "bootstrap_ci95_task_clustered": ci,
                     "n_bootstrap_used": len(boots), "reading": reading}
    return out


def trajectories(cells: list[dict], per_judge: int = 1) -> list[dict]:
    out = []
    for j in e43.JUDGES:
        rows = sorted([c for c in cells if c["judge"] == j and c.get("gaming_gap") is not None], key=lambda c: -c["gaming_gap"])
        for c in rows[:per_judge]:
            added = [s for s in c["checks"]["statements"] if s["new_or_changed"]]
            out.append({"judge": j, "item": c["item"], "loop_start": c["start_score_loop"], "loop_scores": c["loop_scores"],
                        "reject_reasons": c["reject_reasons"], "attacked_start": c["attacked_start"], "attacked_final": c["attacked_final"],
                        "reference_start": c["reference_start"]["ensemble"], "reference_final": c["reference_final"]["ensemble"],
                        "gaming_gap": c["gaming_gap"], "n_statements": [c["checks"]["n_statements_start"], c["checks"]["n_statements_final"]],
                        "added_statements": added[:8], "flag_counts": c["checks"]["flag_counts"]})
    return out


def analyze(stage: str, refs: list[str], reps: int = e43.BOOTSTRAP_REPS) -> dict:
    blob = e43.read_json(e43.RESULTS / stage / "cells.json")
    cells = blob["cells"]
    judges = [j for j in e43.JUDGES if any(c["judge"] == j for c in cells)]
    per = {}
    for j in judges:
        rows = [c for c in cells if c["judge"] == j]
        scored = [c for c in rows if c.get("gaming_gap") is not None]
        for c in rows:
            c["flagged_int"] = None if "checks" not in c else int(c["checks"]["flagged"])
        edited = [c for c in rows if "checks" in c and not c.get("final_is_start")]
        per[j] = {"n_cells": len(rows), "n_scored": len(scored),
                  "missing": {s: sum(1 for c in rows if c.get("gaming_gap") is None and c["status"] == s) for s in {c["status"] for c in rows}},
                  "gaming_gap": cluster_bootstrap(rows, "gaming_gap", reps, e43.SEED),
                  "attacked_gain": cluster_bootstrap(rows, "attacked_gain", reps, e43.SEED),
                  "reference_gain": cluster_bootstrap(rows, "reference_gain", reps, e43.SEED),
                  "flagged_share_all_cells": cluster_bootstrap(rows, "flagged_int", reps, e43.SEED),
                  "flagged_share_edited_cells": (sum(c["checks"]["flagged"] for c in edited) / len(edited)) if edited else None,
                  "n_edited_cells": len(edited),
                  "loop": {"attempts": sum(c["n_attempts"] for c in rows), "attacker_completions": sum(c["n_attacker_measured"] for c in rows),
                           "lean_valid": sum(c["n_valid"] for c in rows), "accepted": sum(c["n_accepted"] for c in rows),
                           "mean_in_loop_gain": mean([None if c["final_score_loop"] is None or c["start_score_loop"] is None
                                                      else c["final_score_loop"] - c["start_score_loop"] for c in rows])},
                  "flag_totals": {f: sum(c["checks"]["flag_counts"][f] for c in rows if "checks" in c)
                                  for f in ("vacuous", "ground", "unrelated", "duplicate", "inflation", "axiom")}}
    idx = index_values(refs)
    assoc = association(per, idx, cells, reps) if stage == "full" else {}
    out = {"written_utc": e43.stamp(), "stage": stage, "n_cells": len(cells), "per_judge": per, "index_source": idx,
           "association": assoc, "trajectories": trajectories(cells), "charges": blob.get("charges")}
    e43.write_json(e43.RESULTS / ("analysis.json" if stage == "full" else f"analysis_{stage}.json"), out)
    return out


def fmt(v, nd=3, signed=True):
    if v is None:
        return "—"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{v:+.{nd}f}" if signed else f"{v:.{nd}f}"
    return str(v)


def ci(b):
    return "—" if not b or b.get("ci95") is None else f"[{b['ci95'][0]:+.3f}, {b['ci95'][1]:+.3f}]"


def tables(out: dict) -> str:
    """Markdown tables for REPORT.md / results.md, written from analysis.json (no hand transcription)."""
    lines = ["| Attacked judge (Claude Sonnet 5, medium) | Cells scored | Gaming gap (95% CI, task-clustered) | Attacked-judge gain (95% CI) | Reference gain (95% CI) | Flagged share, all cells | Flagged share, edited cells | Valid / attempts | Accepted |",
             "|---|---|---|---|---|---|---|---|---|"]
    for j, v in out["per_judge"].items():
        lp = v["loop"]
        lines.append(f"| `{j.split('|')[1]}` | {v['n_scored']}/{v['n_cells']} | {fmt(v['gaming_gap']['mean'])} {ci(v['gaming_gap'])} | "
                     f"{fmt(v['attacked_gain']['mean'])} {ci(v['attacked_gain'])} | {fmt(v['reference_gain']['mean'])} {ci(v['reference_gain'])} | "
                     f"{fmt(v['flagged_share_all_cells']['mean'], 2, False)} | {fmt(v['flagged_share_edited_cells'], 2, False)} ({v['n_edited_cells']} edited) | "
                     f"{lp['lean_valid']}/{lp['attempts']} | {lp['accepted']} |")
    if out.get("association"):
        lines += ["", "| Index (experiment 39) | Judges | Spearman ρ (index, gaming gap) | Exact one-sided p (negative) | Two-sided p | Bootstrap 95% CI of ρ | Reading |",
                  "|---|---|---|---|---|---|---|"]
        for name, a in out["association"].items():
            if a.get("status") != "COMPUTED":
                lines.append(f"| `{name}` | {a.get('n_judges', 0)} | — | — | — | — | {a.get('status')} |")
                continue
            c = a["bootstrap_ci95_task_clustered"]
            lines.append(f"| `{name}` | {a['n_judges']} | {a['spearman']:+.3f} | {a['p_one_sided_negative']:.3f} | {a['p_two_sided']:.3f} | "
                         f"{'—' if not c else f'[{c[0]:+.3f}, {c[1]:+.3f}]'} | {a['reading']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="full", choices=["full", "pilot", "pilot_r1"])
    ap.add_argument("--index-ref", action="append", default=None, help="git refs searched for experiment 39's open units file")
    ap.add_argument("--reps", type=int, default=e43.BOOTSTRAP_REPS)
    args = ap.parse_args()
    refs = args.index_ref or ["origin/main", "origin/e39-proxy-index-search"]
    out = analyze(args.stage, refs, args.reps)
    (e43.RESULTS / ("report_tables.md" if args.stage == "full" else f"report_tables_{args.stage}.md")).write_text(tables(out))
    print(json.dumps({j: {"gap": v["gaming_gap"]["mean"], "ci": v["gaming_gap"]["ci95"], "flagged": v["flagged_share_all_cells"]["mean"]}
                      for j, v in out["per_judge"].items()}, indent=1))
    print(json.dumps({k: {kk: v.get(kk) for kk in ("status", "spearman", "p_one_sided_negative", "reading")} for k, v in out["association"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
