#!/usr/bin/env python3
"""TLDR: Experiment 42's analysis (no model calls). Per judge configuration: directional accuracy against the identity
score on vacuity, weakening and over-constraint probes, Kendall tau-b of score with weakening level, the formatting
invariance gap, and the locked pass/fail rule, each with task-clustered bootstrap intervals; then the association of
these components with experiment 39's expert criterion on its train and val units (and on its test units only if its
results/TEST_RECEIPT.json exists, labelled post hoc). Writes results/semantic_screen.json and
results/index_association.json.

Usage:  analyze.py screen                 # per-configuration metrics from results/harvest/*.json
        analyze.py index --e39-ref <git ref>   # association with experiment 39's criterion (reads its committed files)"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent),
                str(Path(__file__).resolve().parents[2] / "39_label_free_proxy_index_train_val_test_over_judge_families/scripts")]
import e42                                                    # noqa: E402
import analysis_lib as A                                      # noqa: E402  (experiment 39's statistics, read-only import)

SEMANTIC = ("vacuity", "weakening", "overconstraint")
SCORED = ("measured", "deterministic")
MIN_REPEATS = 2                   # a probe's score is the median of its scored repeats; at least 2 of 3 are required
MIN_COVERAGE = 0.8                # a metric needs >= 80% of its valid probes scored, else NOT_COMPUTABLE


def probe_scores(harvest: dict) -> dict[tuple[str, str, int], float]:
    """(kind, task, level) -> median over scored repeats (None when fewer than MIN_REPEATS repeats are scored)."""
    by = {}
    for c in harvest["cells"]:
        by.setdefault((c["kind"], c["task"], c["level"]), []).append(c.get("score") if c.get("status") in SCORED else None)
    out = {}
    for key, vals in by.items():
        vals = [v for v in vals if v is not None]
        out[key] = statistics.median(vals) if len(vals) >= MIN_REPEATS else None
    return out


def valid_rows(manifest: dict) -> list[dict]:
    return [r for r in manifest["rows"] if r["valid"] is True]


def comparisons(scores: dict, rows: list[dict]) -> dict[str, list[tuple[str, float | None]]]:
    """Per family: (task, outcome) for every valid probe. Semantic families: 1 if the probe scores strictly below the
    task's identity score, 0 otherwise (a tie counts as a miss). Formatting: |probe - identity|. None = unscored."""
    out: dict[str, list] = {f: [] for f in e42.FAMILIES}
    for r in rows:
        if r["kind"] == "ident":
            continue
        ident = scores.get(("ident", r["task"], 1))
        s = scores.get((r["kind"], r["task"], r["level"]))
        if ident is None or s is None:
            out[r["family"]].append((r["task"], None))
        elif r["family"] == "formatting":
            out[r["family"]].append((r["task"], abs(s - ident)))
        else:
            out[r["family"]].append((r["task"], 1.0 if s < ident else 0.0))
    return out


def ties_half(scores: dict, rows: list[dict]) -> dict[str, float | None]:
    """Secondary view: a tie counts 0.5."""
    out = {}
    for fam in SEMANTIC:
        vals = []
        for r in rows:
            if r["family"] != fam:
                continue
            ident, s = scores.get(("ident", r["task"], 1)), scores.get((r["kind"], r["task"], r["level"]))
            if ident is not None and s is not None:
                vals.append(1.0 if s < ident else 0.5 if s == ident else 0.0)
        out[fam] = sum(vals) / len(vals) if vals else None
    return out


def cluster_mean_ci(pairs: list[tuple[str, float]], draws: int, seed: int) -> dict:
    """Pooled mean with a task-clustered percentile bootstrap (tasks resampled with replacement)."""
    if not pairs:
        return {"value": None, "lo": None, "hi": None, "n": 0, "n_tasks": 0}
    groups: dict[str, list[float]] = {}
    for t, v in pairs:
        groups.setdefault(t, []).append(v)
    keys = sorted(groups)
    value = sum(v for _, v in pairs) / len(pairs)
    rng = random.Random(seed)
    stats = []
    for _ in range(draws):
        sample = [v for k in (rng.choice(keys) for _ in keys) for v in groups[k]]
        stats.append(sum(sample) / len(sample))
    stats.sort()
    return {"value": value, "lo": stats[int(0.025 * (draws - 1))], "hi": stats[int(0.975 * (draws - 1))],
            "n": len(pairs), "n_tasks": len(keys)}


def weakening_tau(scores: dict, rows: list[dict]) -> dict[str, float | None]:
    """Per task with the identity and >= 1 scored weakening level: Kendall tau-b between level (0 = identity) and
    score. All-tied scores give no ordering and count as tau = 0; the required direction is tau < 0."""
    out = {}
    tasks = sorted({r["task"] for r in rows if r["family"] == "weakening"})
    for t in tasks:
        levels = [0] + sorted(r["level"] for r in rows if r["family"] == "weakening" and r["task"] == t)
        vals = [scores.get(("ident", t, 1))] + [scores.get(("weak", t, lv)) for lv in levels[1:]]
        pts = [(lv, v) for lv, v in zip(levels, vals) if v is not None]
        if len(pts) < 2 or vals[0] is None:
            out[t] = None
            continue
        if len({v for _, v in pts}) < 2:
            out[t] = 0.0
            continue
        out[t] = A.PV.kendall_tau_b([lv for lv, _ in pts], [v for _, v in pts]) if len(pts) >= 3 else (-1.0 if pts[1][1] < pts[0][1] else 1.0)
    return out


def screen_one(harvest: dict, rows: list[dict], draws: int) -> dict:
    scores = probe_scores(harvest)
    comps = comparisons(scores, rows)
    metrics, computable = {}, True
    for fam in e42.FAMILIES:
        all_pairs = comps[fam]
        scored = [(t, v) for t, v in all_pairs if v is not None]
        coverage = len(scored) / len(all_pairs) if all_pairs else None
        ci = cluster_mean_ci(scored, draws, e42.SEED)
        ok = coverage is not None and coverage >= MIN_COVERAGE
        computable &= ok
        metrics[fam] = dict(ci, coverage=coverage, n_declared_valid=len(all_pairs), computable=ok,
                            metric="formatting_gap" if fam == "formatting" else "directional_accuracy")
    taus = weakening_tau(scores, rows)
    tau_pairs = [(t, v) for t, v in taus.items() if v is not None]
    metrics["weakening_kendall_tau"] = cluster_mean_ci(tau_pairs, draws, e42.SEED)
    metrics["directional_accuracy_ties_half"] = ties_half(scores, rows)
    ident_vals = [v for (k, _, _), v in scores.items() if k == "ident" and v is not None]
    metrics["identity_mean_score"] = sum(ident_vals) / len(ident_vals) if ident_vals else None
    if not computable:
        verdict = "NOT_COMPUTABLE"
    else:
        passed = (all(metrics[f]["value"] >= e42.PASS_DIRECTIONAL for f in SEMANTIC)
                  and metrics["formatting"]["value"] <= e42.PASS_FORMATTING_GAP)
        verdict = "PASS" if passed else "FAIL"
    s_comp = None
    if computable:
        s_comp = A.geometric_mean([metrics[f]["value"] for f in SEMANTIC] + [max(0.0, 1.0 - metrics["formatting"]["value"])])
    return {"config": harvest["config"], "family": harvest.get("family"), "split": harvest.get("split"),
            "kind": harvest.get("kind"), "selector": harvest.get("selector"), "status_counts": harvest.get("status_counts"),
            "charges_usd": harvest.get("charges_usd"), "metrics": metrics, "semantic_component_S": s_comp, "verdict": verdict}


def cmd_screen(args) -> int:
    manifest = e42.read_json(e42.RESULTS / "semantic_probe_manifest.json")
    rows = valid_rows(manifest)
    units = []
    for path in sorted((e42.RESULTS / "harvest").glob("*.json")):
        units.append(screen_one(e42.read_json(path), rows, args.draws))
    summary = {v: sum(u["verdict"] == v for u in units) for v in ("PASS", "FAIL", "NOT_COMPUTABLE")}
    e42.write_json(e42.RESULTS / "semantic_screen.json", {
        "written_utc": e42.stamp(), "rule": f"PASS iff directional accuracy >= {e42.PASS_DIRECTIONAL} on each of vacuity, weakening "
        f"and over-constraint AND formatting gap <= {e42.PASS_FORMATTING_GAP} (point estimates; ties count as misses; "
        f"probe score = median of >= {MIN_REPEATS} scored repeats; each metric needs >= {MIN_COVERAGE:.0%} of valid probes scored)",
        "bootstrap": {"draws": args.draws, "seed": e42.SEED, "cluster": "task"}, "n_units": len(units), "verdicts": summary,
        "total_charges_usd": round(sum(u["charges_usd"] or 0.0 for u in units), 4), "units": units})
    print(json.dumps({"n_units": len(units), "verdicts": summary}, indent=1))
    return 0


# ------------------------------------------------------------------------------------------------------------------
# Index association with experiment 39's criterion
# ------------------------------------------------------------------------------------------------------------------

E39_REL = "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results"


def git_json(ref: str, rel: str):
    out = subprocess.run(["git", "show", f"{ref}:{E39_REL}/{rel}"], cwd=str(e42.REPO), capture_output=True, text=True)
    return json.loads(out.stdout) if out.returncode == 0 else None


def assoc(xs, ys, draws: int) -> dict:
    rho = A.spearman(xs, ys)
    return {"spearman": rho, "kendall": A.kendall(xs, ys), "n": sum(1 for a, b in zip(xs, ys) if a is not None and b is not None),
            "ci95": A.bootstrap_ci(xs, ys, A.spearman, draws, e42.SEED), "perm_p_one_sided": A.permutation_p(xs, ys, A.spearman, draws, e42.SEED)}


def cmd_index(args) -> int:
    screen = {u["config"]: u for u in e42.read_json(e42.RESULTS / "semantic_screen.json")["units"]}
    opened = git_json(args.e39_ref, "units_train_val.json")
    if opened is None:
        raise SystemExit(f"experiment 39's results/units_train_val.json is not committed at {args.e39_ref}; the index analysis waits")
    selection = git_json(args.e39_ref, "SELECTION.json") or {}
    selected = selection.get("selected") or (git_json(args.e39_ref, "FINALISTS.json") or {}).get("selected")
    test_receipt = git_json(args.e39_ref, "TEST_RECEIPT.json")
    units = [u for u in opened["units"] if u.get("kind") == "llm"]
    views = {"train_val": units}
    if test_receipt is not None:
        test_units = git_json(args.e39_ref, "units_test.json")
        if test_units:
            views["test_post_hoc"] = [u for u in test_units.get("units", []) if u.get("kind") == "llm"]
    comps = {"DA_vacuity": lambda s: s["metrics"]["vacuity"]["value"], "DA_weakening": lambda s: s["metrics"]["weakening"]["value"],
             "DA_overconstraint": lambda s: s["metrics"]["overconstraint"]["value"],
             "one_minus_formatting_gap": lambda s: None if s["metrics"]["formatting"]["value"] is None else 1 - s["metrics"]["formatting"]["value"],
             "neg_weakening_tau": lambda s: None if s["metrics"]["weakening_kendall_tau"]["value"] is None else -s["metrics"]["weakening_kendall_tau"]["value"],
             "S_semantic": lambda s: s["semantic_component_S"]}
    result = {"written_utc": e42.stamp(), "e39_ref": args.e39_ref,
              "e39_ref_commit": subprocess.run(["git", "rev-parse", args.e39_ref], cwd=str(e42.REPO), capture_output=True, text=True).stdout.strip(),
              "criterion": "experiment 39 criteria.heldout.spearman (agreement with the expert coverage ratings on 45 held-out items)",
              "e39_selected_index": selected, "test_view": "post hoc (TEST_RECEIPT.json present)" if test_receipt else "sealed, not read",
              "views": {}}
    for view, us in views.items():
        crit = [((u.get("criteria") or {}).get("heldout") or {}).get("spearman") for u in us]
        block = {"n_units": len(us), "components": {}}
        for name, fn in comps.items():
            xs = [fn(screen[u["config"]]) if u["config"] in screen else None for u in us]
            block["components"][name] = assoc(xs, crit, args.draws)
        for base in [b for b in (selected, "PTI_v0_frozen", "TI_var_trainnorm") if b]:
            bx = [(u.get("indices") or {}).get(base) for u in us]
            sx = [screen[u["config"]]["semantic_component_S"] if u["config"] in screen else None for u in us]
            aug = [A.geometric_mean([b, s]) if b is not None and s is not None else None for b, s in zip(bx, sx)]
            base_a, aug_a = assoc(bx, crit, args.draws), assoc(aug, crit, args.draws)
            rng, diffs = random.Random(e42.SEED), []
            idx = [i for i in range(len(us)) if bx[i] is not None and aug[i] is not None and crit[i] is not None]
            for _ in range(args.draws if len(idx) >= 3 else 0):
                pick = [rng.choice(idx) for _ in idx]
                a1 = A.spearman([aug[i] for i in pick], [crit[i] for i in pick])
                b1 = A.spearman([bx[i] for i in pick], [crit[i] for i in pick])
                if a1 is not None and b1 is not None:
                    diffs.append(a1 - b1)
            diffs.sort()
            block[f"augmented_{base}"] = {"base": base_a, "augmented_GM_with_S": aug_a,
                                          "delta_spearman": None if base_a["spearman"] is None or aug_a["spearman"] is None else aug_a["spearman"] - base_a["spearman"],
                                          "delta_ci95": [diffs[int(0.025 * (len(diffs) - 1))], diffs[int(0.975 * (len(diffs) - 1))]] if diffs else None}
        result["views"][view] = block
    e42.write_json(e42.RESULTS / "index_association.json", result)
    print(json.dumps({v: {k: b["components"][k]["spearman"] for k in b["components"]} for v, b in result["views"].items()}, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("screen"); s.add_argument("--draws", type=int, default=e42.BOOTSTRAP_DRAWS)
    i = sub.add_parser("index"); i.add_argument("--e39-ref", required=True); i.add_argument("--draws", type=int, default=e42.BOOTSTRAP_DRAWS)
    args = ap.parse_args()
    return cmd_screen(args) if args.cmd == "screen" else cmd_index(args)


if __name__ == "__main__":
    raise SystemExit(main())
