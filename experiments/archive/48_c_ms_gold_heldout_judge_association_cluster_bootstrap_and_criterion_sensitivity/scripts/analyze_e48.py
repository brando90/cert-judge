#!/usr/bin/env python3
"""TLDR: Experiment 48 — zero-inference sensitivity study of experiment 39's held-out C_ms_gold association
(Spearman over the 16 computable held-out judge configurations). Gate G0 reproduces the registered numbers through
experiment 39's own analysis_lib; A1 cluster bootstraps (judge models, prompts) and leave-one-out views; A2 stratified
permutation tests (within judge model, within prompt-rendering family); A3 task-level criterion resampling (task-only and
two-level); A4 rater views (single raters, all available raters, leave-one-rater-out); A5 reference-quality views of the
criterion items; A6 split-half attenuation bound. Seed 48 for every new resample, seed 39 only for the G0 reproduction.
No model calls, no credentials, no network. Run from the repository root:

    PYTHONPATH=py_src python3 experiments/48_.../scripts/analyze_e48.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
E48 = HERE.parent
REPO = next(q for q in E48.parents if (q / "py_src" / "cert_judge").is_dir())   # repo root, valid under experiments/ or experiments/archive/
RESULTS = E48 / "results"
REPORT = E48 / "RESULTS_heldout_association_sensitivity.md"
E39_REL = ("experiments/39_label_free_proxy_index_train_val_test_over_judge_families",
           "experiments/archive/39_label_free_proxy_index_train_val_test_over_judge_families")
ITEMS_REL = "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/items.jsonl"
ITEMS_SHA256 = "ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c"
SEED_NEW = 48                 # every new resample in this experiment
SEED_REGISTERED = 39          # only the G0 reproduction of experiment 39's receipt
DRAWS = 10000
GATE = 0.45                   # experiment 39 PROTOCOL.md: pre-registered test gate on Spearman
GATE_P = 0.05                 # experiment 39 PROTOCOL.md: one-sided permutation p gate
TOL = 1e-9
HELDOUT_SPLITS = ("val", "test")
FULLER = {"D0", "H0", "H1", "H2", "R4"}      # fuller-context prompts (experiment 39 PROTOCOL.md)
LEGACY = {"P1", "P4", "P8", "LEX"}           # legacy prompts: judge sees only the gold's last theorem block
RATERS = ("p1", "p2", "p3", "p4", "p5")
PLACEHOLDER_FLAG = "ref_placeholder_at_annotation"
AMBIGUOUS_FLAG = "ref_ambiguous_in_window"
MIN_CRITERION_COVERAGE = 0.90                # experiment 39 analysis_lib.MIN_CRITERION_COVERAGE


def e39_root() -> Path:
    for rel in E39_REL:
        p = REPO / rel
        if (p / "results" / "units_test.json").exists():
            return p
    raise FileNotFoundError("experiment 39 results not found under experiments/ or experiments/archive/")


try:
    E39 = e39_root()
    sys.path.insert(0, str(E39 / "scripts"))
    import analysis_lib as A                                      # noqa: E402  (experiment 39's frozen statistics)
except FileNotFoundError:                                          # pragma: no cover - tests skip without the receipts
    E39, A = None, None


# ------------------------------------------------------------------ small helpers
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1) + "\n")


def harvest_path(root: Path, config: str) -> Path:
    return root / "results" / "harvest" / (config.replace("|", "__") + ".json")


def model_of(config: str) -> str:
    return config.split("|")[0]


def prompt_of(config: str) -> str:
    return config.split("|")[1]


def family_of(config: str) -> str:
    return "fuller_context" if prompt_of(config) in FULLER else "legacy"


def close(a, b, tol: float = TOL) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def pct_interval(values: list[float], level: float = 0.95) -> dict:
    if not values:
        return {"lo": None, "hi": None, "valid_draws": 0}
    vals = sorted(values)
    a = (1 - level) / 2
    return {"lo": vals[int(a * (len(vals) - 1))], "hi": vals[int((1 - a) * (len(vals) - 1))], "valid_draws": len(vals)}


def reading(spearman, p) -> str:
    """Pre-declared reading (PROTOCOL.md): ROBUST if Spearman >= 0.45 and, where a test exists, p < 0.05;
    WEAKENED if 0 < Spearman < 0.45 or p >= 0.05; REVERSED if Spearman <= 0."""
    if spearman is None:
        return "unavailable"
    if spearman <= 0:
        return "REVERSED"
    if spearman >= GATE and (p is None or p < GATE_P):
        return "ROBUST"
    return "WEAKENED"


def git_head() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True, timeout=30)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------ inputs
def load_items() -> tuple[Path, str, list[dict]]:
    vb = Path(os.environ.get("CJ_VERIBENCH_REPO", "/Users/brandomiranda/veribench"))
    path = vb / ITEMS_REL
    if not path.exists():
        raise FileNotFoundError(f"VeriBench items file not found: {path} (set CJ_VERIBENCH_REPO)")
    digest = sha256(path)
    if digest != ITEMS_SHA256:
        raise SystemExit(f"refusing {path}: SHA-256 {digest} != pinned {ITEMS_SHA256}")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return path, digest, rows


# ------------------------------------------------------------------ statistics used by the views
def outer(pairs: list[tuple], seed: int = SEED_NEW, draws: int = DRAWS, with_uncertainty: bool = True) -> dict:
    """Association over judge configurations between the proxy (first) and a criterion (second), experiment 39's
    conventions: nothing below 8 units; configuration bootstrap interval; one-sided permutation p for a positive
    association."""
    x = [a for a, b in pairs]
    y = [b for a, b in pairs]
    out = {"n_units": len(pairs), "spearman": None, "kendall": None, "pearson": None, "ci": None, "permutation_p": None,
           "bootstrap_unit": "judge configuration", "draws": draws, "seed": seed}
    if len(pairs) < A.MIN_UNITS:
        return out
    out.update(spearman=A.spearman(x, y), kendall=A.kendall(x, y), pearson=A.pearson(x, y))
    if with_uncertainty:
        out["ci"] = A.bootstrap_ci(x, y, A.spearman, draws, seed)
        out["permutation_p"] = A.permutation_p(x, y, A.spearman, draws, seed)
    return out


def cluster_bootstrap(x, y, clusters, draws: int = DRAWS, seed: int = SEED_NEW, min_units: int = 8, level: float = 0.95) -> dict:
    """Percentile interval over resampled clusters (same random sequence as analysis_lib.bootstrap_ci with clusters),
    with the counts the protocol asks for: draws with fewer than `min_units` units and undefined draws."""
    rng = random.Random(seed)
    groups: dict = {}
    for i, c in enumerate(clusters):
        groups.setdefault(c, []).append(i)
    keys = sorted(groups)
    values, values_big, small, undefined = [], [], 0, 0
    for _ in range(draws):
        idx = [i for k in (rng.choice(keys) for _ in keys) for i in groups[k]]
        v = A.spearman([x[i] for i in idx], [y[i] for i in idx])
        if len(idx) < min_units:
            small += 1
        if v is None:
            undefined += 1
            continue
        values.append(v)
        if len(idx) >= min_units:
            values_big.append(v)
    return {"n_clusters": len(keys), "clusters": keys, "cluster_sizes": {k: len(groups[k]) for k in keys}, "draws": draws, "seed": seed,
            "all_defined_draws": pct_interval(values, level), "draws_with_at_least_8_units": pct_interval(values_big, level),
            "draws_fewer_than_8_units": small, "undefined_draws": undefined,
            "distinct_cluster_multisets": math.comb(2 * len(keys) - 1, len(keys))}


def stratified_permutation_p(x, y, strata, draws: int = DRAWS, seed: int = SEED_NEW) -> tuple:
    """One-sided p for a positive Spearman association when the criterion is permuted only within strata,
    (k + 1)/(n + 1). With a single stratum this is exactly analysis_lib.permutation_p."""
    observed = A.spearman(x, y)
    if observed is None:
        return None, None
    rng = random.Random(seed)
    groups: dict = {}
    for i, s in enumerate(strata):
        groups.setdefault(s, []).append(i)
    keys = sorted(groups)
    ys = list(y)
    k = 0
    for _ in range(draws):
        for key in keys:
            idx = groups[key]
            sub = [ys[i] for i in idx]
            rng.shuffle(sub)
            for i, v in zip(idx, sub):
                ys[i] = v
        v = A.spearman(x, ys)
        if v is not None and v >= observed - 1e-12:
            k += 1
    return (k + 1) / (draws + 1), observed


def criterion_over(medians: dict, items: list[dict], target: dict, min_cov: float = MIN_CRITERION_COVERAGE) -> tuple:
    """Tie-aware Spearman between a configuration's per-item median scores and a target over `items` (duplicates
    allowed, as in a task bootstrap). An item without a target under the view is not declared. None unless at least
    90% of the declared items have a score (experiment 39's rule). Returns (spearman, n_scored, n_declared)."""
    xs, ys, declared = [], [], 0
    for it in items:
        t = target.get(it["item"])
        if t is None:
            continue
        declared += 1
        m = medians.get(it["item"])
        if m is not None:
            xs.append(m)
            ys.append(t)
    if declared == 0 or len(xs) / declared + 1e-9 < min_cov:
        return None, len(xs), declared
    return A.spearman(xs, ys), len(xs), declared


def mean_target(vals: list) -> float | None:
    return (sum(vals) / len(vals)) / 5.0 if vals else None


def rater_targets(items: list[dict]) -> dict:
    """Per-item 0-1 targets under each rater view: single raters, the mean of all available current raters,
    leave-one-rater-out means, and the registered target_expert."""
    views = {}
    for r in RATERS:
        views[f"single_{r}"] = {it["item"]: (float(it[r]) / 5.0 if it.get(r) is not None else None) for it in items}
    views["all_available_raters_mean"] = {it["item"]: mean_target([float(it[r]) for r in RATERS if it.get(r) is not None]) for it in items}
    for r in RATERS:
        views[f"leave_out_{r}"] = {it["item"]: mean_target([float(it[q]) for q in RATERS if q != r and it.get(q) is not None]) for it in items}
    views["registered_target_expert"] = {it["item"]: float(it["target_expert"]) for it in items}
    return views


def reference_views(held: list[dict]) -> tuple:
    """Experiment 44's reference-quality views: tasks flagged placeholder-at-annotation removed, tasks flagged
    ambiguous-in-window removed, both removed; plus the original and the test-task-only items."""
    ph_tasks = sorted({it["task"] for it in held if it.get(PLACEHOLDER_FLAG)})
    am_tasks = sorted({it["task"] for it in held if it.get(AMBIGUOUS_FLAG)})
    views = {"original45": list(held),
             "no_placeholder_reference_tasks": [it for it in held if it["task"] not in ph_tasks],
             "no_ambiguous_reference_tasks": [it for it in held if it["task"] not in am_tasks],
             "neither_placeholder_nor_ambiguous": [it for it in held if it["task"] not in ph_tasks and it["task"] not in am_tasks],
             "test_tasks_only30": [it for it in held if it["split"] == "test"]}
    return views, ph_tasks, am_tasks


def ms_gold_over_keys(sc, probes: dict, keys: set) -> float | None:
    """C_ms_gold restricted to a subset of gold ladders (analysis_lib.components' ms_gold branch on that subset)."""
    by_key: dict = {}
    for r in probes.get("ms_gold", []):
        if r["key"] in keys:
            by_key.setdefault(r["key"], []).append(r["level"])
    qualities = []
    for key, levels in by_key.items():
        lv, meds = A.ladder_medians(sc, "ms_gold", key, "ident", levels)
        if lv is None:
            continue
        q = A.ladder_quality(lv, meds)
        if q is not None:
            qualities.append(q)
    declared = len(by_key)
    if declared == 0 or len(qualities) / declared + 1e-9 < A.MIN_COMPONENT_COVERAGE:
        return None
    return sum(qualities) / len(qualities)


def spearman_brown(r) -> float | None:
    return None if r is None or r <= -1 else 2 * r / (1 + r)


# ------------------------------------------------------------------ G0
def run_g0(root: Path, items: list[dict], test_units: list[dict], llm_units: list[dict], scores: dict, probes: dict,
           receipt: dict, units_tv: dict, ci_draws: int = DRAWS) -> dict:
    reg = receipt["reported"]["C_ms_gold"]["test"]
    rep = A.association(test_units, "C_ms_gold", draws=DRAWS, seed=SEED_REGISTERED)
    keys = ("n_units", "spearman", "kendall", "pearson", "permutation_p")
    assoc_pass = all(close(rep[k], reg[k]) for k in keys) and close(rep["ci"]["lo"], reg["ci"]["lo"]) and close(rep["ci"]["hi"], reg["ci"]["hi"])
    crit_rows, ms_rows = [], []
    for u in test_units:
        sc = scores[u["config"]]
        c = A.criterion(sc, items, HELDOUT_SPLITS, draws=ci_draws, seed=SEED_REGISTERED)
        stored = u["criteria"]["heldout"]
        crit_rows.append({"config": u["config"], "stored": stored["spearman"], "recomputed": c["spearman"], "n_items": c["n_items"],
                          "stored_ci": stored.get("ci"), "recomputed_ci": c["ci"], "pass": close(c["spearman"], stored["spearman"])})
        ms = A.components(sc, probes)["ms_gold"]
        ms_rows.append({"config": u["config"], "stored": u["indices"].get("C_ms_gold"), "recomputed": ms["value"], "n_ladders": ms["n"],
                        "declared": ms["declared"], "pass": close(ms["value"], u["indices"].get("C_ms_gold"))})
    xs = [(u["criteria"]["val_items"] or {}).get("spearman") for u in llm_units]
    ys = [(u["criteria"]["test_items"] or {}).get("spearman") for u in llm_units]
    pairs = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    rel = A.spearman([a for a, _ in pairs], [b for _, b in pairs])
    stored_rel = (units_tv.get("reliability_all_llm_units") or {}).get("spearman_val_items_vs_test_items")
    rel_pass = rel is not None and round(rel, 3) == 0.928 and stored_rel is not None and abs(rel - stored_rel) < 5e-4
    g0 = {"written_utc": stamp(), "seed": SEED_REGISTERED, "draws": DRAWS, "tolerance": TOL,
          "registered_association": {"receipt": {k: reg[k] for k in keys} | {"ci": reg["ci"]},
                                     "recomputed": {k: rep[k] for k in keys} | {"ci": rep["ci"]}, "pass": assoc_pass},
          "criterion_reproduction": {"rows": crit_rows, "pass": all(r["pass"] for r in crit_rows), "ci_draws": ci_draws},
          "c_ms_gold_reproduction": {"rows": ms_rows, "pass": all(r["pass"] for r in ms_rows)},
          "criterion_ranking_reproducibility": {"n_units": len(pairs), "recomputed": rel, "stored": stored_rel, "expected_3dp": 0.928, "pass": rel_pass}}
    g0["pass"] = bool(assoc_pass and g0["criterion_reproduction"]["pass"] and g0["c_ms_gold_reproduction"]["pass"] and rel_pass)
    return g0


# ------------------------------------------------------------------ analyses
def run_a1(pairs16: list[tuple], registered: dict) -> dict:
    x = [a for a, _, _ in pairs16]
    y = [b for _, b, _ in pairs16]
    cfgs = [c for _, _, c in pairs16]
    a1 = {"written_utc": stamp(), "seed": SEED_NEW, "draws": DRAWS, "units": cfgs,
          "a_registered_configuration_bootstrap_seed39": registered,
          "a_configuration_bootstrap_seed48": outer([(a, b) for a, b, _ in pairs16]),
          "b_model_cluster_bootstrap": cluster_bootstrap(x, y, [model_of(c) for c in cfgs]),
          "c_prompt_cluster_bootstrap": cluster_bootstrap(x, y, [prompt_of(c) for c in cfgs])}
    loo_model, loo_prompt = {}, {}
    for m in sorted({model_of(c) for c in cfgs}):
        sub = [(a, b) for a, b, c in pairs16 if model_of(c) != m]
        o = outer(sub)
        loo_model[m] = {"dropped_units": len(pairs16) - len(sub), **o, "reading": reading(o["spearman"], o["permutation_p"])}
    for p in sorted({prompt_of(c) for c in cfgs}):
        sub = [(a, b) for a, b, c in pairs16 if prompt_of(c) != p]
        o = outer(sub)
        loo_prompt[p] = {"dropped_units": len(pairs16) - len(sub), **o, "reading": reading(o["spearman"], o["permutation_p"])}

    def summ(d):
        vals = [v["spearman"] for v in d.values() if v["spearman"] is not None]
        return {"min": min(vals), "median": statistics.median(vals), "max": max(vals), "n_views": len(vals),
                "readings": {k: v["reading"] for k, v in d.items()}} if vals else {"min": None, "median": None, "max": None, "n_views": 0, "readings": {}}
    a1["d_leave_one_model_out"] = {"views": loo_model, "summary": summ(loo_model)}
    a1["d_leave_one_prompt_out"] = {"views": loo_prompt, "summary": summ(loo_prompt)}
    return a1


def run_a2(pairs16: list[tuple]) -> dict:
    x = [a for a, _, _ in pairs16]
    y = [b for _, b, _ in pairs16]
    cfgs = [c for _, _, c in pairs16]
    models = [model_of(c) for c in cfgs]
    families = [family_of(c) for c in cfgs]
    p_model, obs = stratified_permutation_p(x, y, models)
    p_family, _ = stratified_permutation_p(x, y, families)
    within = {}
    for m in sorted(set(models)):
        sub = [(a, b) for a, b, c in pairs16 if model_of(c) == m]
        row = {"n_units": len(sub), "spearman": None, "kendall": None, "pearson": None}
        if len(sub) >= 3:
            sx, sy = [a for a, _ in sub], [b for _, b in sub]
            row.update(spearman=A.spearman(sx, sy), kendall=A.kendall(sx, sy), pearson=A.pearson(sx, sy),
                       note="descriptive: fewer than 8 units, no interval and no test")
        else:
            row["note"] = "not computed: fewer than 3 units"
        within[m] = row
    sizes = lambda labels: {k: labels.count(k) for k in sorted(set(labels))}  # noqa: E731
    return {"written_utc": stamp(), "seed": SEED_NEW, "draws": DRAWS, "observed_spearman": obs, "n_units": len(pairs16),
            "within_model": {"strata_sizes": sizes(models), "permutation_p": p_model, "test": "one-sided permutation of the criterion within judge model",
                             "reading": "association present within judge models" if (p_model is not None and p_model < GATE_P) else "pooled association not shown to hold within models"},
            "within_prompt_family": {"strata_sizes": sizes(families), "permutation_p": p_family, "test": "one-sided permutation of the criterion within prompt-rendering family (legacy vs fuller-context)",
                                     "reading": "association present within prompt families" if (p_family is not None and p_family < GATE_P) else "pooled association not shown to hold within prompt families"},
            "within_model_descriptive": within}


def run_a3(pairs16: list[tuple], medians: dict, held: list[dict], target: dict) -> dict:
    rng = random.Random(SEED_NEW)
    tasks = sorted({it["task"] for it in held})
    by_task = {t: [it for it in held if it["task"] == t] for t in tasks}
    vals_task, vals_two = [], []
    undefined_task = undefined_two = draws_lt8 = 0
    per_unit: dict = {c: [] for _, _, c in pairs16}
    dropped = {c: 0 for _, _, c in pairs16}
    for _ in range(DRAWS):
        drawn = [rng.choice(tasks) for _ in tasks]
        items_d = [it for t in drawn for it in by_task[t]]
        pr = []
        for a, _, c in pairs16:
            crit, _, _ = criterion_over(medians[c], items_d, target)
            if crit is None:
                dropped[c] += 1
                continue
            per_unit[c].append(crit)
            pr.append((a, crit))
        if len(pr) < A.MIN_UNITS:
            draws_lt8 += 1
            undefined_task += 1
            undefined_two += 1
            continue
        v = A.spearman([a for a, _ in pr], [b for _, b in pr])
        if v is None:
            undefined_task += 1
        else:
            vals_task.append(v)
        idx = [rng.randrange(len(pr)) for _ in pr]
        v2 = A.spearman([pr[i][0] for i in idx], [pr[i][1] for i in idx])
        if v2 is None:
            undefined_two += 1
        else:
            vals_two.append(v2)
    unit_sd = {c: (statistics.pstdev(v) if len(v) >= 2 else None) for c, v in per_unit.items()}
    ti, tw = pct_interval(vals_task), pct_interval(vals_two)
    return {"written_utc": stamp(), "seed": SEED_NEW, "draws": DRAWS, "n_tasks": len(tasks), "n_items": len(held), "n_units": len(pairs16),
            "random_sequence": "per draw: 15 task choices, then (two-level only) 16 configuration choices",
            "a_task_bootstrap_only": {**ti, "undefined_draws": undefined_task, "p_val": "n/a", "resampled_unit": "held-out task (3 items move together)"},
            "b_two_level_task_then_configuration": {**tw, "undefined_draws": undefined_two, "p_val": "n/a",
                                                    "resampled_unit": "held-out task, then judge configuration within the draw",
                                                    "lower_bound_above_0": (tw["lo"] is not None and tw["lo"] > 0),
                                                    "lower_bound_above_gate": (tw["lo"] is not None and tw["lo"] > GATE)},
            "draws_with_fewer_than_8_computable_units": draws_lt8,
            "per_unit_criterion_sd_over_task_draws": unit_sd, "per_unit_draws_not_computable": dropped,
            "mean_task_only_spearman": (statistics.mean(vals_task) if vals_task else None)}


def view_association(pairs16: list[tuple], medians: dict, items: list[dict], target: dict) -> dict:
    rows, pr = {}, []
    for a, _, c in pairs16:
        crit, n_scored, declared = criterion_over(medians[c], items, target)
        rows[c] = {"criterion": crit, "n_scored": n_scored, "n_declared": declared}
        if crit is not None:
            pr.append((a, crit))
    o = outer(pr)
    return {**o, "units_computable": len(pr), "units_declared": len(pairs16), "per_unit": rows, "reading": reading(o["spearman"], o["permutation_p"])}


def run_a4(pairs16: list[tuple], medians: dict, held: list[dict]) -> dict:
    views = rater_targets(held)
    out = {"written_utc": stamp(), "seed": SEED_NEW, "draws": DRAWS, "views": {}}
    for name, target in views.items():
        declared = sum(1 for it in held if target.get(it["item"]) is not None)
        v = view_association(pairs16, medians, held, target)
        out["views"][name] = {"declared_items": declared, **v}
    original = {it["item"]: mean_target([float(it[r]) for r in ("p1", "p2", "p3") if it.get(r) is not None]) for it in held}
    out["registered_target_check"] = {"max_abs_diff_mean_of_available_p1_p2_p3_vs_target_expert":
                                      max(abs(original[it["item"]] - float(it["target_expert"])) for it in held),
                                      "items_without_p3": sum(1 for it in held if it.get("p3") is None)}
    sp = {k: v["spearman"] for k, v in out["views"].items() if v["spearman"] is not None}
    out["range_over_views"] = {"min": min(sp.values()), "min_view": min(sp, key=sp.get), "max": max(sp.values()), "max_view": max(sp, key=sp.get),
                               "readings": {k: v["reading"] for k, v in out["views"].items()}}
    return out


def run_a5(pairs16: list[tuple], medians: dict, held: list[dict]) -> dict:
    views, ph_tasks, am_tasks = reference_views(held)
    target = {it["item"]: float(it["target_expert"]) for it in held}
    out = {"written_utc": stamp(), "seed": SEED_NEW, "draws": DRAWS, "placeholder_tasks": ph_tasks, "ambiguous_tasks": am_tasks, "views": {}}
    for name, its in views.items():
        v = view_association(pairs16, medians, its, target)
        out["views"][name] = {"n_items": len(its), "n_tasks": len({it["task"] for it in its}), **v}
    pre = ("original45", "no_placeholder_reference_tasks", "no_ambiguous_reference_tasks", "neither_placeholder_nor_ambiguous")
    sp = {k: out["views"][k]["spearman"] for k in pre if out["views"][k]["spearman"] is not None}
    out["minimum_over_reference_quality_views"] = {"min": min(sp.values()), "min_view": min(sp, key=sp.get),
                                                   "readings": {k: out["views"][k]["reading"] for k in pre}}
    return out


def run_a6(llm_units: list[dict], scores: dict, probes: dict, observed_test_spearman: float, g0: dict) -> dict:
    rel = g0["criterion_ranking_reproducibility"]
    xs = [(u["criteria"]["val_items"] or {}).get("spearman") for u in llm_units]
    ys = [(u["criteria"]["test_items"] or {}).get("spearman") for u in llm_units]
    pairs = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    r_crit = rel["recomputed"]
    keys = sorted({r["key"] for r in probes.get("ms_gold", [])})
    odd, even = keys[0::2], keys[1::2]
    px, py, used = [], [], []
    for u in llm_units:
        sc = scores[u["config"]]
        a, b = ms_gold_over_keys(sc, probes, set(odd)), ms_gold_over_keys(sc, probes, set(even))
        if a is not None and b is not None:
            px.append(a)
            py.append(b)
            used.append(u["config"])
    r_proxy = A.spearman(px, py)
    sb_crit, sb_proxy = spearman_brown(r_crit), spearman_brown(r_proxy)

    def disatt(r1, r2):
        if r1 is None or r2 is None or r1 <= 0 or r2 <= 0:
            return None
        return observed_test_spearman / math.sqrt(r1 * r2)
    return {"written_utc": stamp(), "observed_test_spearman": observed_test_spearman,
            "criterion_split_half": {"n_units": len(pairs), "halves": "15 validation-task items vs 30 test-task items", "spearman": r_crit,
                                     "kendall": A.kendall([a for a, _ in pairs], [b for _, b in pairs]), "pearson": A.pearson([a for a, _ in pairs], [b for _, b in pairs]),
                                     "spearman_brown": sb_crit},
            "proxy_split_half": {"n_units": len(px), "units": used, "halves": f"odd ({len(odd)}) vs even ({len(even)}) gold ladders in sorted key order",
                                 "odd_keys": odd, "even_keys": even, "spearman": r_proxy, "kendall": A.kendall(px, py), "pearson": A.pearson(px, py),
                                 "spearman_brown": sb_proxy},
            "disattenuated_test_spearman": {"using_spearman_brown_reliabilities": disatt(sb_crit, sb_proxy), "using_raw_half_correlations": disatt(r_crit, r_proxy),
                                            "note": "a bound from unequal halves (15 vs 30 items; 12 vs 12 ladders), not a population estimate; values above 1 are reported as computed"}}


# ------------------------------------------------------------------ report
def fmt(v, nd: int = 3) -> str:
    return "unavailable" if v is None else f"{v:.{nd}f}"


def fmt_ci(o: dict) -> str:
    ci = o.get("ci") or {}
    p = o.get("permutation_p")
    return f"{fmt(o.get('spearman'))} [{fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}] p-val={fmt(p, 4) if p is not None else 'n/a'}"


def write_report(g0: dict, a1: dict, a2: dict, a3: dict, a4: dict, a5: dict, a6: dict, summary: dict, manifest: dict) -> None:
    L = ["# Experiment 48 results: cluster-aware intervals and criterion sensitivity of the held-out judge association of `C_ms_gold`", "",
         f"**Doc link:** <https://github.com/brando90/cert-judge/blob/main/{E48.relative_to(REPO)}/RESULTS_heldout_association_sensitivity.md>", "",
         f"Generated {summary['written_utc']} by `scripts/analyze_e48.py` (zero inference; inputs hashed in `results/input_manifest.json`, repository HEAD `{manifest.get('git_head')}`). "
         "Unless stated, every number is a tie-aware Spearman correlation between `C_ms_gold` and the judge–human criterion over the 16 computable held-out judge configurations; "
         "intervals are 95% percentile bootstraps (10,000 draws) with the resampled unit named; p-values are one-sided permutation tests for a positive association, (k + 1)/(n + 1) over 10,000 draws; "
         "seed 48 for every new resample, seed 39 only for the reproduction of experiment 39's receipt. Thresholds: 0.45 and p-val < 0.05 are experiment 39's pre-registered gate (its `PROTOCOL.md`); 0 is 'no positive association'. "
         "Readings follow `PROTOCOL.md` § Pre-declared readings (ROBUST / WEAKENED / REVERSED).", "",
         "## TLDR", "",
         f"- **Headline triple.** Within-judge-model permutation p-val={fmt(summary['headline']['within_model_permutation_p'], 4)} ({summary['headline']['within_model_reading']}); "
         f"minimum Spearman over the reference-quality views {fmt(summary['headline']['min_reference_quality_spearman'])} (view `{summary['headline']['min_reference_quality_view']}`, {summary['headline']['min_reference_quality_reading']}); "
         f"two-level (task, then configuration) interval lower bound {fmt(summary['headline']['two_level_lower_bound'])} (above 0: {summary['headline']['two_level_lower_bound_above_0']}; above 0.45: {summary['headline']['two_level_lower_bound_above_gate']}).",
         f"- **Readings.** Leave-one-model-out: {summary['readings']['leave_one_model_out']}; leave-one-prompt-out: {summary['readings']['leave_one_prompt_out']}; rater views: {summary['readings']['rater_views']}; reference-quality views: {summary['readings']['reference_quality_views']}.",
         f"- **Registered result reproduced (G0 PASS={g0['pass']}):** test Spearman {fmt(g0['registered_association']['recomputed']['spearman'])} "
         f"[{fmt(g0['registered_association']['recomputed']['ci']['lo'])}, {fmt(g0['registered_association']['recomputed']['ci']['hi'])}] p-val={fmt(g0['registered_association']['recomputed']['permutation_p'], 4)} "
         f"(configuration bootstrap and permutation, seed 39, 16 units); every test unit's criterion and `C_ms_gold` reproduced to 1e-9; criterion ranking reproducibility {fmt(g0['criterion_ranking_reproducibility']['recomputed'])} over {g0['criterion_ranking_reproducibility']['n_units']} configurations.",
         "- Experiment 39's registered PASS is unchanged; this report states its scope.", "",
         "## G0 — reproduction of experiment 39's receipt", "",
         "| Check | Stored | Recomputed | Pass |", "|---|---|---|---|"]
    ra = g0["registered_association"]
    L.append(f"| Test association `C_ms_gold` (16 units, seed 39) | {fmt(ra['receipt']['spearman'])} [{fmt(ra['receipt']['ci']['lo'])}, {fmt(ra['receipt']['ci']['hi'])}] p-val={fmt(ra['receipt']['permutation_p'], 4)} | "
             f"{fmt(ra['recomputed']['spearman'])} [{fmt(ra['recomputed']['ci']['lo'])}, {fmt(ra['recomputed']['ci']['hi'])}] p-val={fmt(ra['recomputed']['permutation_p'], 4)} | {ra['pass']} |")
    cr = g0["criterion_reproduction"]
    L.append(f"| Held-out criterion of every test unit (18 units, 45 items) | max abs diff {max(abs((r['stored'] or 0) - (r['recomputed'] or 0)) for r in cr['rows']):.1e} | from harvest `crit` cells, median of repeats | {cr['pass']} |")
    ms = g0["c_ms_gold_reproduction"]
    L.append(f"| `C_ms_gold` of every test unit (18 units; 2 None) | max abs diff {max(abs((r['stored'] or 0) - (r['recomputed'] or 0)) for r in ms['rows']):.1e} | `analysis_lib.components` on harvest + manifest | {ms['pass']} |")
    rr = g0["criterion_ranking_reproducibility"]
    L.append(f"| Criterion ranking reproducibility (validation items vs test items, {rr['n_units']} LLM configurations) | {fmt(rr['stored'])} | {fmt(rr['recomputed'])} | {rr['pass']} |")
    L += ["", "## A1 — cluster-aware uncertainty", "", "| View | Resampled unit | Spearman [95% interval] p-val | Kendall τ-b | Pearson | Draws defined / <8 units | Note |", "|---|---|---|---|---|---|---|"]
    a = a1["a_registered_configuration_bootstrap_seed39"]
    L.append(f"| (a) registered configuration bootstrap, seed 39 | judge configuration | {fmt_ci(a)} | {fmt(a['kendall'])} | {fmt(a['pearson'])} | {a['ci']['valid_draws']} / 0 | experiment 39's receipt |")
    a = a1["a_configuration_bootstrap_seed48"]
    L.append(f"| (a) configuration bootstrap, seed 48 | judge configuration | {fmt_ci(a)} | {fmt(a['kendall'])} | {fmt(a['pearson'])} | {a['ci']['valid_draws']} / 0 | same statistic, this experiment's seed |")
    for key, label in (("b_model_cluster_bootstrap", "(b) judge-model cluster bootstrap"), ("c_prompt_cluster_bootstrap", "(c) prompt cluster bootstrap")):
        b = a1[key]
        d = b["all_defined_draws"]
        e = b["draws_with_at_least_8_units"]
        L.append(f"| {label} ({b['n_clusters']} clusters: {', '.join(f'{k}×{v}' for k, v in b['cluster_sizes'].items())}) | cluster | {fmt(a1['a_configuration_bootstrap_seed48']['spearman'])} [{fmt(d['lo'])}, {fmt(d['hi'])}] p-val=n/a | — | — | {d['valid_draws']} / {b['draws_fewer_than_8_units']} | "
                 f"over draws with ≥ 8 units: [{fmt(e['lo'])}, {fmt(e['hi'])}] ({e['valid_draws']} draws); {b['distinct_cluster_multisets']} distinct cluster multisets; undefined draws {b['undefined_draws']} |")
    for key, label in (("d_leave_one_model_out", "Leave one judge model out"), ("d_leave_one_prompt_out", "Leave one prompt out")):
        L += ["", f"**(d) {label}.** Summary over deletions: min {fmt(a1[key]['summary']['min'])}, median {fmt(a1[key]['summary']['median'])}, max {fmt(a1[key]['summary']['max'])} ({a1[key]['summary']['n_views']} views).", "",
              "| Dropped | Units left | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |", "|---|---|---|---|---|---|"]
        for k, v in a1[key]["views"].items():
            L.append(f"| `{k}` | {v['n_units']} (−{v['dropped_units']}) | {fmt_ci(v)} | {fmt(v['kendall'])} | {fmt(v['pearson'])} | {v['reading']} |")
    L += ["", "## A2 — stratified permutation tests", "", f"Observed Spearman {fmt(a2['observed_spearman'])} over {a2['n_units']} units.", "",
          "| Strata | Sizes | One-sided permutation p-val (criterion permuted within strata) | Reading |", "|---|---|---|---|"]
    for key in ("within_model", "within_prompt_family"):
        w = a2[key]
        L.append(f"| {key.replace('_', ' ')} | {', '.join(f'{k}×{v}' for k, v in w['strata_sizes'].items())} | p-val={fmt(w['permutation_p'], 4)} | {w['reading']} |")
    L += ["", "Within-model association (descriptive; fewer than 8 units, so no interval and no test):", "", "| Judge model | Units | Spearman | Kendall τ-b | Pearson | Note |", "|---|---|---|---|---|---|"]
    for k, v in a2["within_model_descriptive"].items():
        L.append(f"| `{k}` | {v['n_units']} | {fmt(v['spearman'])} | {fmt(v['kendall'])} | {fmt(v['pearson'])} | {v['note']} |")
    L += ["", "## A3 — criterion-noise-aware intervals", "", f"{a3['n_tasks']} held-out tasks ({a3['n_items']} items), {a3['n_units']} units, {a3['draws']} draws, seed 48; the point estimate is the registered {fmt(a1['a_configuration_bootstrap_seed48']['spearman'])}.", "",
          "| Interval | Resampled unit | 95% interval | Defined draws | Undefined draws | Draws with < 8 computable units |", "|---|---|---|---|---|---|"]
    t = a3["a_task_bootstrap_only"]
    L.append(f"| (a) task bootstrap only | {t['resampled_unit']} | [{fmt(t['lo'])}, {fmt(t['hi'])}] p-val=n/a | {t['valid_draws']} | {t['undefined_draws']} | {a3['draws_with_fewer_than_8_computable_units']} |")
    t = a3["b_two_level_task_then_configuration"]
    L.append(f"| (b) two-level, task then configuration | {t['resampled_unit']} | [{fmt(t['lo'])}, {fmt(t['hi'])}] p-val=n/a | {t['valid_draws']} | {t['undefined_draws']} | {a3['draws_with_fewer_than_8_computable_units']} |")
    L += ["", f"Two-level lower bound above 0: {t['lower_bound_above_0']}; above 0.45: {t['lower_bound_above_gate']}. Mean task-only Spearman across draws {fmt(a3['mean_task_only_spearman'])}. "
          "Per-unit criterion SD over task draws (criterion estimation noise, 45 items): " + ", ".join(f"`{c}` {fmt(s, 3)}" for c, s in a3["per_unit_criterion_sd_over_task_draws"].items()) + ".",
          "Draws in which a unit's criterion was NOT_COMPUTABLE (coverage below 90% of the drawn items): " + ", ".join(f"`{c}` {n}" for c, n in a3["per_unit_draws_not_computable"].items() if n) + ("." if any(a3["per_unit_draws_not_computable"].values()) else "none."),
          "", "## A4 — rater views of the criterion", "",
          f"Registered target check: max |mean of available raters 1–3 ÷ 5 − `target_expert`| = {a4['registered_target_check']['max_abs_diff_mean_of_available_p1_p2_p3_vs_target_expert']:.1e} over 45 items ({a4['registered_target_check']['items_without_p3']} items without rater 3).", "",
          "| Target | Declared items | Computable units | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |", "|---|---|---|---|---|---|---|"]
    for k, v in a4["views"].items():
        L.append(f"| {k} | {v['declared_items']} | {v['units_computable']}/{v['units_declared']} | {fmt_ci(v)} | {fmt(v['kendall'])} | {fmt(v['pearson'])} | {v['reading']} |")
    r = a4["range_over_views"]
    L += ["", f"Range over rater views: min {fmt(r['min'])} (`{r['min_view']}`), max {fmt(r['max'])} (`{r['max_view']}`).", "",
          "## A5 — reference-quality views of the criterion items", "",
          f"Placeholder-reference tasks: {', '.join(f'`{t}`' for t in a5['placeholder_tasks'])}; ambiguous-reference tasks: {', '.join(f'`{t}`' for t in a5['ambiguous_tasks'])} (flags from VeriBench experiment 100's `items.jsonl`; views as in experiment 44).", "",
          "| View | Items / tasks | Computable units | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |", "|---|---|---|---|---|---|---|"]
    for k, v in a5["views"].items():
        L.append(f"| {k} | {v['n_items']} / {v['n_tasks']} | {v['units_computable']}/{v['units_declared']} | {fmt_ci(v)} | {fmt(v['kendall'])} | {fmt(v['pearson'])} | {v['reading']} |")
    m = a5["minimum_over_reference_quality_views"]
    L += ["", f"Minimum over the four pre-registered reference-quality views: {fmt(m['min'])} (`{m['min_view']}`).", "",
          "## A6 — attenuation bound (descriptive)", "", "| Quantity | Value | Units | Note |", "|---|---|---|---|"]
    c = a6["criterion_split_half"]
    p = a6["proxy_split_half"]
    L.append(f"| Criterion split-half (Spearman / Kendall / Pearson) | {fmt(c['spearman'])} / {fmt(c['kendall'])} / {fmt(c['pearson'])}; Spearman–Brown {fmt(c['spearman_brown'])} | {c['n_units']} LLM configurations | {c['halves']} |")
    L.append(f"| `C_ms_gold` split-half (Spearman / Kendall / Pearson) | {fmt(p['spearman'])} / {fmt(p['kendall'])} / {fmt(p['pearson'])}; Spearman–Brown {fmt(p['spearman_brown'])} | {p['n_units']} LLM configurations | {p['halves']} |")
    d = a6["disattenuated_test_spearman"]
    L.append(f"| Disattenuated test Spearman | {fmt(d['using_spearman_brown_reliabilities'])} (Spearman–Brown reliabilities); {fmt(d['using_raw_half_correlations'])} (raw half correlations) | 16 units | {d['note']} |")
    L += ["", "## Deviations", "", "Recorded in `results.md`; none affect the pre-registered views unless listed there.", ""]
    REPORT.write_text("\n".join(L))


# ------------------------------------------------------------------ main
def main() -> int:
    t0 = time.time()
    if A is None:
        raise SystemExit("experiment 39 receipts not found; nothing to analyse")
    root = E39
    items_path, items_digest, items = load_items()
    held = [it for it in items if it["split"] in HELDOUT_SPLITS]
    units_test = read_json(root / "results/units_test.json")
    units_tv = read_json(root / "results/units_train_val.json")
    receipt = read_json(root / "results/TEST_RECEIPT.json")
    manifest_probes = read_json(root / "results/probe_manifest.json")
    probes = A.valid_probes(manifest_probes)
    test_units = [u for u in units_test["units"] if u["kind"] == "llm"]
    llm_units = [u for u in units_tv["units"] if u["kind"] == "llm"] + test_units
    scores, hashes = {}, {}
    for u in llm_units:
        p = harvest_path(root, u["config"])
        scores[u["config"]] = A.Scores(read_json(p))
        hashes[str(p.relative_to(REPO))] = sha256(p)
    for name in ("units_test.json", "units_train_val.json", "TEST_RECEIPT.json", "probe_manifest.json"):
        hashes[str((root / "results" / name).relative_to(REPO))] = sha256(root / "results" / name)
    manifest = {"written_utc": stamp(), "git_head": git_head(), "experiment_39_root": str(root.relative_to(REPO)),
                "veribench_items": {"path": str(items_path), "sha256": items_digest, "pinned_sha256": ITEMS_SHA256},
                "inputs_sha256": hashes, "seeds": {"new": SEED_NEW, "registered_reproduction": SEED_REGISTERED}, "draws": DRAWS,
                "n_items": len(items), "n_heldout_items": len(held), "n_heldout_tasks": len({it["task"] for it in held}),
                "n_llm_units": len(llm_units), "n_test_units": len(test_units)}
    write_json(RESULTS / "input_manifest.json", manifest)

    g0 = run_g0(root, items, test_units, llm_units, scores, probes, receipt, units_tv)
    write_json(RESULTS / "g0_reproduction.json", g0)
    print(json.dumps({"G0": g0["pass"], "association": g0["registered_association"]["pass"], "criterion": g0["criterion_reproduction"]["pass"],
                      "c_ms_gold": g0["c_ms_gold_reproduction"]["pass"], "ranking": g0["criterion_ranking_reproducibility"]["pass"]}))
    if not g0["pass"]:
        print("G0 FAILED: stopping before any new number (PROTOCOL.md)")
        return 1

    pairs16 = [(u["indices"]["C_ms_gold"], u["criteria"]["heldout"]["spearman"], u["config"]) for u in test_units
               if u["indices"].get("C_ms_gold") is not None and (u["criteria"]["heldout"] or {}).get("spearman") is not None]
    medians = {c: {it["item"]: scores[c].median("crit", it["item"], 0) for it in held} for _, _, c in pairs16}
    target = {it["item"]: float(it["target_expert"]) for it in held}
    registered = g0["registered_association"]["recomputed"]
    registered = {**registered, "bootstrap_unit": "judge configuration", "draws": DRAWS, "seed": SEED_REGISTERED}

    a1 = run_a1(pairs16, registered)
    write_json(RESULTS / "a1_cluster.json", a1)
    a2 = run_a2(pairs16)
    write_json(RESULTS / "a2_stratified_permutation.json", a2)
    a3 = run_a3(pairs16, medians, held, target)
    write_json(RESULTS / "a3_criterion_noise.json", a3)
    a4 = run_a4(pairs16, medians, held)
    write_json(RESULTS / "a4_rater_views.json", a4)
    a5 = run_a5(pairs16, medians, held)
    write_json(RESULTS / "a5_reference_quality.json", a5)
    a6 = run_a6(llm_units, scores, probes, registered["spearman"], g0)
    write_json(RESULTS / "a6_attenuation.json", a6)

    two = a3["b_two_level_task_then_configuration"]
    m5 = a5["minimum_over_reference_quality_views"]
    summary = {"written_utc": stamp(), "seed": SEED_NEW, "draws": DRAWS, "n_units": len(pairs16), "g0_pass": g0["pass"],
               "registered_test_spearman": registered["spearman"],
               "headline": {"within_model_permutation_p": a2["within_model"]["permutation_p"], "within_model_reading": a2["within_model"]["reading"],
                            "within_prompt_family_permutation_p": a2["within_prompt_family"]["permutation_p"],
                            "min_reference_quality_spearman": m5["min"], "min_reference_quality_view": m5["min_view"],
                            "min_reference_quality_reading": a5["views"][m5["min_view"]]["reading"],
                            "two_level_lower_bound": two["lo"], "two_level_upper_bound": two["hi"],
                            "two_level_lower_bound_above_0": two["lower_bound_above_0"], "two_level_lower_bound_above_gate": two["lower_bound_above_gate"],
                            "task_only_interval": [a3["a_task_bootstrap_only"]["lo"], a3["a_task_bootstrap_only"]["hi"]]},
               "readings": {"leave_one_model_out": a1["d_leave_one_model_out"]["summary"]["readings"],
                            "leave_one_prompt_out": a1["d_leave_one_prompt_out"]["summary"]["readings"],
                            "rater_views": a4["range_over_views"]["readings"],
                            "reference_quality_views": m5["readings"]},
               "cluster_intervals": {"model_cluster_all_defined": [a1["b_model_cluster_bootstrap"]["all_defined_draws"]["lo"], a1["b_model_cluster_bootstrap"]["all_defined_draws"]["hi"]],
                                     "prompt_cluster_all_defined": [a1["c_prompt_cluster_bootstrap"]["all_defined_draws"]["lo"], a1["c_prompt_cluster_bootstrap"]["all_defined_draws"]["hi"]]},
               "attenuation": {"criterion_split_half_spearman_brown": a6["criterion_split_half"]["spearman_brown"], "proxy_split_half_spearman_brown": a6["proxy_split_half"]["spearman_brown"],
                               "disattenuated_test_spearman": a6["disattenuated_test_spearman"]["using_spearman_brown_reliabilities"]},
               "runtime_seconds": round(time.time() - t0, 1)}
    write_json(RESULTS / "summary.json", summary)
    write_report(g0, a1, a2, a3, a4, a5, a6, summary, manifest)
    print(json.dumps({"headline": summary["headline"], "readings": summary["readings"], "runtime_s": summary["runtime_seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
