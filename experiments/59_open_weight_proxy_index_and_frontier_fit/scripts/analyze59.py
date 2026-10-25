#!/usr/bin/env python3
"""TLDR: Experiment 59's frozen analysis. Part 1: label-free indices (C_ms_gold, F1_probe, F2_item, F12) of open-weight judge
units against the human criterion. Part 2: learners L0-L4 that fit open-weight unit scores to the frontier consensus T and
are tested once on the 30 test items. Reads experiment 59's harvests (judge59.py output) and experiment 39's cached hosted
harvests; writes results/ANALYSIS.json and results/RESULTS_open_weight_proxy_fit.md. Zero model calls.

Usage: ~/.venvs/e59/bin/python analyze59.py --run RUN [--run RUN2 ...] [--draws 10000] [--out DIR]
(RUN = a directory with harvest/e39/*.json from judge59.py; needs numpy and scipy.)"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import nnls
from scipy.stats import kendalltau, rankdata

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
import register59  # noqa: E402

e58 = register59.e58
sys.path.append(str(register59.E58_SCRIPTS))
import analyze58 as AN  # noqa: E402

A = e58.analysis_lib()
E59 = HERE.parent
SEED = 59
FRONT_H2 = ("sol6h", "sonnet5m", "luna6h", "gem31h", "opus55x")          # frontier consensus T (protocol section 2)
OWN_MODEL = {"t2_luna": "luna6h", "t2_sonnet5": "sonnet5m"}               # agent judges: leave their model out of T too
HOSTED_OPEN = ("qwen36",)                                                 # cached open-weight units
# Reference arms (protocol section 2 and Addendum 3): arm -> (members whose H2 unit forms T, minimum members). A unit's own
# model is always left out of its T. "frontier" is the primary arm; the O_* arms use open-weight references only.
ARMS = {"frontier": (FRONT_H2, 4), "O_qwen36": (("qwen36",), 1), "O_llama70": (("llama33_70b_awq",), 1),
        "O_qwen32": (("qwen3_32b",), 1), "O_both": (("qwen36", "qwen3_32b"), 2)}
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0)
TOPK = 5
GATE_RHO, GATE_P, CLUSTER_P = 0.45, 0.05, 0.10


# ------------------------------------------------------------------ statistics
def rho(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def pear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def kend(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(kendalltau(x, y).statistic)


def icc(x, y, kind):
    """Two-rater ICC: 'C' = ICC(C,1) consistency, 'A' = ICC(A,1) absolute agreement (McGraw and Wong)."""
    d = np.column_stack([np.asarray(x, float), np.asarray(y, float)])
    n, k = d.shape
    if n < 3:
        return float("nan")
    gm = d.mean()
    msr = k * ((d.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((d.mean(0) - gm) ** 2).sum() / (k - 1)
    sse = ((d - d.mean(1, keepdims=True) - d.mean(0, keepdims=True) + gm) ** 2).sum()
    mse = sse / ((n - 1) * (k - 1))
    if kind == "C":
        den = msr + (k - 1) * mse
        return float((msr - mse) / den) if den > 0 else float("nan")
    den = msr + (k - 1) * mse + k * (msc - mse) / n
    return float((msr - mse) / den) if den > 0 else float("nan")


METRICS = {"spearman": rho, "pearson": pear, "kendall": kend, "icc_c1": lambda a, b: icc(a, b, "C"),
           "icc_a1": lambda a, b: icc(a, b, "A")}


def task_boot(preds: dict[str, np.ndarray], y, tasks, fn, draws, seed=SEED, pairs=()):
    """Task-clustered bootstrap percentile intervals of fn(pred, y) per predictor, plus paired differences for `pairs`."""
    y = np.asarray(y, float)
    tasks = np.asarray(tasks)
    uniq = sorted(set(tasks))
    idx = {t: np.where(tasks == t)[0] for t in uniq}
    rng = np.random.default_rng(seed)
    vals = {k: [] for k in preds}
    diffs = {p: [] for p in pairs}
    for _ in range(draws):
        pick = rng.integers(0, len(uniq), len(uniq))
        ii = np.concatenate([idx[uniq[j]] for j in pick])
        cur = {k: fn(np.asarray(v)[ii], y[ii]) for k, v in preds.items()}
        for k, v in cur.items():
            vals[k].append(v)
        for a, b in pairs:
            diffs[(a, b)].append(cur[a] - cur[b])

    def ci(v):
        v = np.array([t for t in v if t == t])
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 50 else None
    return {k: ci(v) for k, v in vals.items()}, {f"{a} - {b}": ci(v) for (a, b), v in diffs.items()}


# ------------------------------------------------------------------ data
def load_run_harvests(runs: list[Path]) -> dict[str, dict]:
    out = {}
    for run in runs:
        for p in sorted((run / "harvest" / "e39").glob("*.json")):
            h = e58.read_json(p)
            out[h["config"]] = h
    return out


def load_hosted() -> dict[str, dict]:
    out = {}
    for p in sorted((e58.E39_DIR / "results/harvest").glob("*.json")):
        h = e58.read_json(p)
        out[h["config"]] = h
    return out


def cell_table(h: dict) -> dict[str, dict]:
    return {c["cell"]: c for c in h["cells"] if c["status"] in ("measured", "deterministic") and c.get("score") is not None}


def consensus(tables: dict[str, dict], exclude_model: str | None = None, arm: str = "frontier") -> dict[str, float]:
    """T per cell: mean score of the arm's H2 reference units over cells every remaining member measured."""
    pool, min_members = ARMS[arm]
    members = [m for m in pool if m != exclude_model and f"{m}|H2" in tables]
    need = [tables[f"{m}|H2"] for m in members]
    if len(members) < min_members:
        return {}
    cells = set(need[0])
    for t in need[1:]:
        cells &= set(t)
    return {c: float(np.mean([t[c]["score"] for t in need])) for c in cells}


def split_of_tasks(items: list[dict]) -> dict[str, str]:
    return {it["task"]: it["split"] for it in items}


_ITEM_CACHE: dict = {}


def item_median(table: dict[str, dict], item: str) -> float | None:
    key = id(table)
    if key not in _ITEM_CACHE:
        by: dict = {}
        for c in table.values():
            if c["kind"] == "crit":
                by.setdefault(c["key"], []).append(c["score"])
        _ITEM_CACHE[key] = (table, {k: float(statistics.median(v)) for k, v in by.items()})   # holds the table: its id is not reused
    return _ITEM_CACHE[key][1].get(item)


# ------------------------------------------------------------------ part 1
def part1(units, items, hosted, newset, draws, arm="frontier"):
    """F1/F2/F12 against the arm's T; the frontier arm keeps the plain index names, the others carry an `@arm` suffix."""
    sfx = "" if arm == "frontier" else f"@{arm}"
    tables = {c: cell_table(h) for c, h in {**hosted, **newset}.items()}
    t_all = consensus(tables, None, arm)
    t_by_model = {m: consensus(tables, m, arm) for m in set(ARMS[arm][0])}
    ref = tables["sol6h|H2"]                                   # the cell layout (kinds, items) is the same for every unit
    crit_items = [it["item"] for it in items]
    crit_cells = {it: [c for c in ref if ref[c]["kind"] == "crit" and ref[c]["key"] == it] for it in crit_items}
    extra = {}
    for u in units:
        cfg = u["config"]
        if cfg not in tables or u["kind"] != "llm":
            continue
        model = cfg.split("|")[0]
        own = model if model in ARMS[arm][0] else (OWN_MODEL.get(model) if arm == "frontier" else None)
        T = t_by_model[own] if own in t_by_model else t_all
        if not T:
            continue
        tab = tables[cfg]
        declared = [c for c in T if c in ref and ref[c]["kind"] != "crit"]
        noncrit = [c for c in declared if c in tab]
        f1 = rho([tab[c]["score"] for c in noncrit], [T[c] for c in noncrit]) if declared and len(noncrit) / len(declared) >= 0.8 else None
        xs, ys = [], []
        for it in crit_items:
            m = item_median(tab, it)
            t = [T[c] for c in crit_cells[it] if c in T]
            if m is not None and t:
                xs.append(m)
                ys.append(float(statistics.median(t)))
        f2 = rho(xs, ys) if len(xs) / len(crit_items) >= 0.9 else None
        f1 = None if f1 is not None and math.isnan(f1) else f1
        f2 = None if f2 is not None and math.isnan(f2) else f2
        f12 = math.sqrt(max(f1, 0) * max(f2, 0)) if f1 is not None and f2 is not None else None
        u["indices"].update({f"F1_probe{sfx}": f1, f"F2_item{sfx}": f2, f"F12{sfx}": f12})
        extra[cfg] = {f"F1_probe{sfx}": f1, f"F2_item{sfx}": f2, f"F12{sfx}": f12, "n_probe_cells": len(noncrit), "n_items": len(xs)}
    return extra


def assoc_block(units, names, draws):
    out = {}
    for n in names:
        out[n] = A.association(units, n, "heldout", draws=draws, seed=39)
    return out


def clustered_p(units, name, draws):
    try:
        return AN.clustered_stats(A, units, name, draws)
    except Exception as e:  # models whose nine units are not all computable leave too few clusters
        return {"error": str(e)[:200]}


def gate_verdict(units, name, draws):
    plain = A.association(units, name, "heldout", draws=draws, seed=39)
    clus = clustered_p(units, name, draws)
    rho_, p = plain["spearman"], plain["permutation_p"]
    plain_pass = bool(rho_ is not None and p is not None and rho_ >= GATE_RHO and p < GATE_P)
    cp = clus.get("permutation_p") if isinstance(clus, dict) else None
    cl_pass = bool(cp is not None and cp < CLUSTER_P)
    verdict = ("PASS" if plain_pass and cl_pass else "INCONCLUSIVE (plain PASS, clustered not)" if plain_pass else "FAIL")
    return {"index": name, "plain": plain, "plain_PASS": plain_pass, "model_clustered": clus, "clustered_p_below_0.10": cl_pass,
            "verdict": verdict}


# ------------------------------------------------------------------ part 2
def ridge_fit(X, y, alpha):
    xm, ym = X.mean(0), y.mean()
    Xc, yc = X - xm, y - ym
    w = np.linalg.solve(Xc.T @ Xc + alpha * np.eye(X.shape[1]), Xc.T @ yc)
    return w, ym - xm @ w


def nnls_fit(X, y):
    xm, ym = X.mean(0), y.mean()
    w, _ = nnls(X - xm, y - ym, maxiter=50 * X.shape[1])
    return w, ym - xm @ w


class Design:
    """Rows = cells with a consensus T; columns = open-weight units; fixed standardization from the given rows."""

    def __init__(self, cells, tables, open_cfgs, T, task_split):
        self.cells = cells
        self.cfgs = open_cfgs
        self.y = np.array([T[c["cell"]] for c in cells])
        self.X = np.full((len(cells), len(open_cfgs)), np.nan)
        for j, cfg in enumerate(open_cfgs):
            tab = tables[cfg]
            for i, c in enumerate(cells):
                t = tab.get(c["cell"])
                if t is not None:
                    self.X[i, j] = t["score"]
        self.split = np.array([task_split[c["task"]] for c in cells])
        self.kind = np.array([c["kind"] for c in cells])
        self.task = np.array([c["task"] for c in cells])

    def prep(self, fit_mask):
        med = np.nanmedian(self.X[fit_mask], axis=0)
        keep = (np.isfinite(self.X[fit_mask]).mean(0) >= 0.5) & np.isfinite(med)
        Xi = np.where(np.isfinite(self.X), self.X, med)
        mu, sd = Xi[fit_mask].mean(0), Xi[fit_mask].std(0)
        keep &= sd > 0
        Z = (Xi - mu) / np.where(sd > 0, sd, 1)
        self.Xi = Xi
        return Z, keep


def item_scores(rows_cells, pred, items_wanted):
    """Median over repeats of a per-cell prediction, per criterion item."""
    by = {}
    for c, p in zip(rows_cells, pred):
        if c["kind"] == "crit":
            by.setdefault(c["key"], []).append(p)
    return {it: float(np.median(by[it])) for it in items_wanted if it in by}


def run_learners(D: Design, fit_splits, eval_mask, alpha_fixed=None):
    """Fit L0-L3 on rows of `fit_splits`; return per-cell predictions on eval rows (a dict learner -> array) and details."""
    fit = np.isin(D.split, fit_splits)
    Z, keep = D.prep(fit)
    Zk = Z[:, keep]
    cfgs = [c for c, k in zip(D.cfgs, keep) if k]
    probe_fit = fit & (D.kind != "crit")
    f1 = np.array([rho(D.X[probe_fit, j], D.y[probe_fit]) for j in np.where(keep)[0]])
    f1 = np.where(np.isnan(f1), -9, f1)
    order = np.argsort(-f1)
    out, det = {}, {"kept_units": len(cfgs), "dropped_units": [c for c, k in zip(D.cfgs, keep) if not k]}
    j0 = order[0]
    out["L0"] = D.Xi[:, np.where(keep)[0][j0]]
    det["L0_unit"] = cfgs[j0]
    det["L0_F1_train_val" if len(fit_splits) > 1 else "L0_F1_train"] = float(f1[j0])
    top = order[:TOPK]
    out["L1"] = Zk[:, top].mean(1)
    det["L1_units"] = [cfgs[j] for j in top]
    Xf, yf = Zk[fit], D.y[fit]
    if alpha_fixed is None:
        tr = D.split == "train"
        va = D.split == "val"
        best = None
        for a in ALPHAS:
            w, b = ridge_fit(Zk[tr], D.y[tr], a)
            mse = float(np.mean((Zk[va] @ w + b - D.y[va]) ** 2))
            if best is None or mse < best[1]:
                best = (a, mse)
        alpha = best[0]
    else:
        alpha = alpha_fixed
    w, b = ridge_fit(Xf, yf, alpha)
    out["L2"] = Zk @ w + b
    det["L2_alpha"] = alpha
    det["L2_top_weights"] = sorted(((cfgs[j], round(float(w[j]), 4)) for j in range(len(cfgs))), key=lambda t: -abs(t[1]))[:8]
    w3, b3 = nnls_fit(Xf, yf)
    out["L3"] = Zk @ w3 + b3
    det["L3_weights"] = sorted(((cfgs[j], round(float(w3[j]), 4)) for j in range(len(cfgs)) if w3[j] > 0), key=lambda t: -t[1])
    return out, det


def human_fit(D, items, fit_splits, eval_split_items):
    """L4: ridge on item medians of the unit scores against the expert mean (labels used; diagnostic)."""
    fit_items = [it for it in items if it["split"] in fit_splits]
    cfgs = D.cfgs
    tab_rows = {}
    for j, cfg in enumerate(cfgs):
        for i, c in enumerate(D.cells):
            if c["kind"] == "crit" and np.isfinite(D.X[i, j]):
                tab_rows.setdefault((c["key"], j), []).append(D.X[i, j])

    def feat(it):
        return np.array([np.median(tab_rows[(it["item"], j)]) if (it["item"], j) in tab_rows else np.nan for j in range(len(cfgs))])
    F = np.vstack([feat(it) for it in items])
    split = np.array([it["split"] for it in items])
    y = np.array([it["target_expert"] for it in items], float)
    fit = np.isin(split, fit_splits)
    med = np.nanmedian(F[fit], axis=0)
    keep = np.isfinite(med)
    F = np.where(np.isfinite(F), F, med)[:, keep]
    mu, sd = F[fit].mean(0), F[fit].std(0)
    ok = sd > 0
    F = ((F - mu) / np.where(sd > 0, sd, 1))[:, ok]
    if len(fit_splits) == 1:
        va = split == "val"
        best = min(ALPHAS, key=lambda a: float(np.mean((F[va] @ ridge_fit(F[fit], y[fit], a)[0] + ridge_fit(F[fit], y[fit], a)[1] - y[va]) ** 2)))
    else:
        best = human_fit.alpha
    w, b = ridge_fit(F[fit], y[fit], best)
    human_fit.alpha = best
    return {it["item"]: float(F[i] @ w + b) for i, it in enumerate(items)}, best


human_fit.alpha = 10.0


def evaluate(preds: dict[str, dict], items_eval, draws, pairs):
    """preds: name -> {item: score}. Common items only. Metrics with task-clustered CIs and paired differences."""
    names = list(preds)
    common = [it for it in items_eval if all(it["item"] in preds[n] for n in names)]
    y = np.array([it["target_expert"] for it in common], float)
    tasks = [it["task"] for it in common]
    arr = {n: np.array([preds[n][it["item"]] for it in common]) for n in names}
    out = {"n_items": len(common), "n_tasks": len(set(tasks)), "rows": {}}
    cis = {m: task_boot(arr, y, tasks, fn, draws, pairs=pairs) for m, fn in METRICS.items() if m in ("spearman",)}
    for n in names:
        row = {m: fn(arr[n], y) for m, fn in METRICS.items()}
        row["spearman_ci95"] = cis["spearman"][0][n]
        out["rows"][n] = row
    out["paired_spearman_diff_ci95"] = cis["spearman"][1]
    for m in ("pearson", "kendall", "icc_c1", "icc_a1"):
        c, _ = task_boot(arr, y, tasks, METRICS[m], min(draws, 2000))
        for n in names:
            out["rows"][n][f"{m}_ci95"] = c[n]
    return out


def median_by_item(T, cells, items):
    out = {}
    for it in items:
        v = [T[c["cell"]] for c in cells if c["kind"] == "crit" and c["key"] == it["item"] and c["cell"] in T]
        if v:
            out[it["item"]] = float(statistics.median(v))
    return out


def reference_check(tables, items, arm):
    """How good a stand-in the open reference is: its T against the frontier consensus (probe cells and the 75 items), plus
    the reference used directly as a judge against the experts on the 45 val+test items."""
    T, Tf = consensus(tables, None, arm), consensus(tables)
    base = tables["sol6h|H2"]
    cells = [{"cell": k, "kind": v["kind"], "key": v["key"]} for k, v in base.items() if k in T and k in Tf]
    pc = [c for c in cells if c["kind"] != "crit"]
    mt, mf = median_by_item(T, cells, items), median_by_item(Tf, cells, items)
    common = [k for k in mt if k in mf]
    ev = [it for it in items if it["split"] in ("val", "test") and it["item"] in mt]
    return {"probe_cells_spearman": rho([T[c["cell"]] for c in pc], [Tf[c["cell"]] for c in pc]), "n_probe_cells": len(pc),
            "items_spearman": rho([mt[k] for k in common], [mf[k] for k in common]), "n_items": len(common),
            "reference_vs_experts_45_items": rho([mt[it["item"]] for it in ev], [it["target_expert"] for it in ev]), "n_items_vs_experts": len(ev),
            "frontier_vs_experts_45_items": rho([mf[it["item"]] for it in ev if it["item"] in mf], [it["target_expert"] for it in ev if it["item"] in mf])}


def part2(items, hosted, newset, open_cfgs, draws, arm="frontier"):
    tables = {c: cell_table(h) for c, h in {**hosted, **newset}.items()}
    T = consensus(tables, None, arm)
    Tf = consensus(tables)                                                  # frontier consensus, reference R_front in every arm
    open_cfgs = [c for c in open_cfgs if c.split("|")[0] not in (ARMS[arm][0] if arm != "frontier" else ())]
    task_split = split_of_tasks(items)
    base = hosted["sol6h|H2"]
    cells = [c for c in base["cells"] if c["cell"] in T and c["task"] in task_split and c["status"] == "measured"]
    D = Design(cells, tables, open_cfgs, T, task_split)
    res = {"n_rows": len(cells), "rows_by_split": {s: int((D.split == s).sum()) for s in ("train", "val", "test")},
           "n_open_units": len(open_cfgs)}
    # validation-time versions (fit on train only) -> chosen learner; test-time versions (fit on train+val)
    pv, dv = run_learners(D, ["train"], None)
    val_items = [it for it in items if it["split"] == "val"]
    test_items = [it for it in items if it["split"] == "test"]
    vm = D.split == "val"
    val_pred = {n: item_scores([c for c, m in zip(D.cells, vm) if m], p[vm], [it["item"] for it in val_items]) for n, p in pv.items()}
    val_eval = {n: rho([val_pred[n][it["item"]] for it in val_items if it["item"] in val_pred[n]],
                       [it["target_expert"] for it in val_items if it["item"] in val_pred[n]]) for n in val_pred}
    cand = [n for n in ("L1", "L2", "L3") if val_eval.get(n) == val_eval.get(n)]
    chosen = max(cand, key=lambda n: val_eval[n]) if cand else None
    res["validation"] = {"fit_on": "train", "spearman_vs_expert_val_items": val_eval, "chosen_among_L1_L2_L3": chosen,
                         "L2_alpha": dv["L2_alpha"], "details": {k: v for k, v in dv.items() if k.startswith("L0")}}
    # final: fit train+val, evaluate test once
    pf, df = run_learners(D, ["train", "val"], None, alpha_fixed=dv["L2_alpha"])
    tm = D.split == "test"
    test_cells = [c for c, m in zip(D.cells, tm) if m]
    preds = {n: item_scores(test_cells, p[tm], [it["item"] for it in test_items]) for n, p in pf.items()}
    l4, a4 = human_fit(D, items, ["train"], None)
    l4f, _ = human_fit(D, items, ["train", "val"], None)
    preds["L4_human_fit"] = {it["item"]: l4f[it["item"]] for it in test_items}
    # references
    preds["R_front"] = median_by_item(Tf, D.cells, test_items)
    if arm != "frontier":
        preds["R_ref"] = median_by_item(T, D.cells, test_items)             # the arm's own open reference as a judge
    vsel = [tables["sol6h|H2"], tables["opus55x|H2"]]
    preds["R_validated"] = {it["item"]: float(np.mean([item_median(t, it["item"]) for t in vsel])) for it in test_items}
    if "q25_14b_awq|H2" in tables:
        preds["R_local_default"] = {it["item"]: item_median(tables["q25_14b_awq|H2"], it["item"]) for it in test_items
                                    if item_median(tables["q25_14b_awq|H2"], it["item"]) is not None}
    # oracle: best open unit by test criterion
    best_o = None
    for cfg in open_cfgs:
        s = {it["item"]: item_median(tables[cfg], it["item"]) for it in test_items}
        if any(v is None for v in s.values()):
            continue
        r = rho([s[it["item"]] for it in test_items], [it["target_expert"] for it in test_items])
        if r == r and (best_o is None or r > best_o[1]):
            best_o = (cfg, r, s)
    if best_o:
        preds["ORACLE_best_open_unit"] = best_o[2]
    rname = "R_front" if arm == "frontier" else "R_ref"
    pairs = [(a, b) for a in ("L1", "L2", "L3") for b in ("L0", rname)] + [("L4_human_fit", "L2")]
    pairs = [(a, b) for a, b in pairs if a in preds and b in preds]
    ev = evaluate(preds, test_items, draws, pairs)
    res["test"] = {"fit_on": "train+val", "details": df, "oracle_unit": best_o[0] if best_o else None, **ev}
    # verdict
    row = ev["rows"].get(chosen, {}) if chosen else {}
    ci = row.get("spearman_ci95")
    l0 = ev["rows"]["L0"]["spearman"]
    fit_pass = bool(chosen and row.get("spearman") is not None and row["spearman"] >= GATE_RHO and ci and ci[0] > 0 and row["spearman"] > l0)
    no_gain = bool(chosen and not fit_pass and any(ev["rows"][n]["spearman"] >= GATE_RHO for n in ("L1", "L2", "L3")))
    res["verdict"] = {"chosen_by_validation": chosen, "FIT_PASS": fit_pass,
                      "label": "FIT-PASS" if fit_pass else "FIT-NO-GAIN" if no_gain else "FIT-FAIL",
                      "interval_contains_0_and_reference": bool(ci and ci[0] <= 0 and ev["rows"][rname]["spearman"] <= ci[1])}
    # descriptive 5-fold task-grouped CV over all 25 tasks (alpha fixed to the validation choice)
    tasks = sorted(task_split)
    rng = np.random.default_rng(SEED)
    perm = list(rng.permutation(len(tasks)))
    fold_of = {tasks[i]: k % 5 for k, i in enumerate(perm)}
    cv = {n: {} for n in ("L0", "L1", "L2", "L3")}
    for f in range(5):
        te = np.array([fold_of[t] == f for t in D.task])
        sub_split = np.where(te, "test", "train")
        D2 = Design.__new__(Design)
        D2.__dict__.update(D.__dict__)
        D2.split = sub_split
        p, _ = run_learners(D2, ["train"], None, alpha_fixed=dv["L2_alpha"])
        te_cells = [c for c, m in zip(D.cells, te) if m]
        eit = [it["item"] for it in items if fold_of[it["task"]] == f]
        for n in cv:
            cv[n].update(item_scores(te_cells, p[n][te], eit))
    cvp = dict(cv)
    cvp["R_front"] = median_by_item(Tf, D.cells, items)
    if arm != "frontier":
        cvp["R_ref"] = median_by_item(T, D.cells, items)
    cvp["R_validated"] = {it["item"]: float(np.mean([item_median(t, it["item"]) for t in vsel])) for it in items}
    res["cv5_all_tasks"] = evaluate(cvp, items, draws, [])
    if arm != "frontier":                                                   # how good a stand-in is the open reference?
        both = [c for c in D.cells if c["cell"] in Tf]
        pc = [c for c in both if c["kind"] != "crit"]
        mt, mf = median_by_item(T, D.cells, items), median_by_item(Tf, D.cells, items)
        res["reference_vs_frontier"] = {
            "probe_cells_spearman": rho([T[c["cell"]] for c in pc], [Tf[c["cell"]] for c in pc]), "n_probe_cells": len(pc),
            "items_spearman": rho([mt[k] for k in mt if k in mf], [mf[k] for k in mt if k in mf]), "n_items": len([k for k in mt if k in mf])}
    return res


# ------------------------------------------------------------------ driver
def build_units_from(harvests: dict[str, dict], items, manifest, draws):
    probes = A.valid_probes(manifest)
    norm = e58.read_json(e58.E39_DIR / "results/SELECTION.json")["ti_var_norm"]
    units = []
    for cfg, h in harvests.items():
        sc = A.Scores(h)
        crit = {"heldout": A.criterion(sc, items, ("val", "test"), draws=min(draws, 2000), seed=39)}
        comps = A.components(sc, probes)
        pti = A.pti_v0_frozen(sc, probes)
        raw = A.ti_var_raw(sc, probes)
        indices = {"PTI_v0_frozen": pti["value"],
                   "TI_var_trainnorm": A.ti_var(raw, {k: tuple(v) if isinstance(v, list) else v for k, v in norm.items()}) if raw else None}
        for name in A.CANDIDATES:
            if A.CANDIDATES[name][0] != "frozen":
                indices[name] = A.candidate_value(name, comps, indices)
        units.append({"config": cfg, "model_key": h["family"], "prompt_key": cfg.split("|")[1], "kind": h["kind"], "split": h["split"],
                      "status_counts": h["status_counts"], "criteria": crit, "indices": indices})
    return units


def fmt(v, nd=3):
    return "n/a" if v is None or (isinstance(v, float) and v != v) else f"{v:.{nd}f}"


def ci_s(ci):
    if isinstance(ci, dict):
        ci = [ci.get("lo"), ci.get("hi")]
    return "n/a" if not ci or ci[0] is None else f"[{ci[0]:.2f}, {ci[1]:.2f}]"


def write_report(path: Path, res: dict):
    L = ["# Experiment 59 results: open-weight proxy indices and frontier fit", "",
         f"Generated by `scripts/analyze59.py`; protocol `PROTOCOL.md` (frozen before any judge call). Human ratings: 75 Claude 3.7 Sonnet "
         f"zero-shot items only (no frontier outputs rated until 2026-11-06).", ""]
    p1 = res["part1"]
    L += ["## Part 1: label-free indices vs agreement with the expert ratings (open-weight units)", "",
          f"Open-weight units with a computable criterion: {p1['n_open_units']} ({p1['n_open_models']} models).", "",
          f"**Primary (gate, `C_ms_gold`):** {p1['primary']['verdict']}. Plain Spearman {fmt(p1['primary']['plain']['spearman'])} "
          f"{ci_s(p1['primary']['plain']['ci'])}, permutation p {fmt(p1['primary']['plain']['permutation_p'], 4)}, n units {p1['primary']['plain']['n_units']}; "
          f"model-clustered: {json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in p1['primary']['model_clustered'].items() if k in ('spearman', 'permutation_p', 'n_models', 'ci')})}.", "",
          "| index | n units | Spearman | 95% CI | Kendall | Pearson | perm p (one-sided) |", "|---|---|---|---|---|---|---|"]
    for n, a in p1["secondary"].items():
        L.append(f"| {n} | {a['n_units']} | {fmt(a['spearman'])} | {ci_s(a['ci'])} | {fmt(a['kendall'])} | {fmt(a['pearson'])} | {fmt(a['permutation_p'], 4)} |")
    L += ["", "Associations over other unit sets (Spearman, n):", ""]
    for k, blk in p1["other_sets"].items():
        L.append(f"- {k}: " + "; ".join(f"{n} {fmt(a['spearman'])} (n={a['n_units']})" for n, a in blk.items()))
    L += ["", "### Units", "", "| unit | criterion rho (45 items) | C_ms_gold | F1_probe | F2_item | status |", "|---|---|---|---|---|---|"]
    for r in p1["unit_table"]:
        L.append(f"| `{r['config']}` | {fmt(r['criterion'])} | {fmt(r['C_ms_gold'])} | {fmt(r['F1_probe'])} | {fmt(r['F2_item'])} | {r['status']} |")
    if res["part2"]:
        L += _part2_lines(res["part2"], "## Part 2: fitting open-weight units to the frontier consensus T")
    else:
        L += ["", "## Part 2", "", "Not run in this interim look (`--part1-only`): no learner was fitted and the test split was not read."]
    for arm, blk in res.get("arms", {}).items():
        L += ["", f"## Open-weight reference arm `{arm}` (members {', '.join(ARMS[arm][0])}; protocol Addendum 3)", "",
              f"Reference vs the frontier consensus: {json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in blk['reference_vs_frontier'].items()})}.", "",
              "Part 1 (label-free indices of this arm vs agreement with the expert ratings, over the open-weight units):", "",
              "| index | n units | Spearman | 95% CI | Kendall | Pearson | perm p (one-sided) |", "|---|---|---|---|---|---|---|"]
        for n, a in blk["part1"]["secondary"].items():
            L.append(f"| {n} | {a['n_units']} | {fmt(a['spearman'])} | {ci_s(a['ci'])} | {fmt(a['kendall'])} | {fmt(a['pearson'])} | {fmt(a['permutation_p'], 4)} |")
        sr = blk.get("substitute_reading")
        if sr:
            L.append(f"\nSubstitute reading (Addendum 3): **{'SUBSTITUTE-OK' if sr['SUBSTITUTE_OK'] else 'NOT SUBSTITUTE-OK'}** (arm chosen-learner test rho {fmt(sr['arm_chosen_test_rho'])}, frontier arm {fmt(sr['frontier_arm_chosen_test_rho'])}, arm FIT-PASS {sr['arm_FIT_PASS']}).")
        g = blk["part1"]["gate"]
        L.append(f"\nGate on `{g['index']}` (descriptive, same thresholds as the primary): {g['verdict']}; model-clustered p {fmt((g['model_clustered'] or {}).get('permutation_p'), 4)}.")
        if blk["part2"]:
            L += _part2_lines(blk["part2"], f"### Part 2, arm `{arm}`: fit to this reference")
    path.write_text("\n".join(L) + "\n")


def _part2_lines(p2, title):
    L = ["", title, "",
          f"Rows {p2['n_rows']} ({json.dumps(p2['rows_by_split'])}); open-weight units {p2['n_open_units']}. Verdict: **{p2['verdict']['label']}** "
          f"(chosen by validation: {p2['verdict']['chosen_by_validation']}; validation Spearman {json.dumps({k: round(v, 3) for k, v in p2['validation']['spearman_vs_expert_val_items'].items() if v == v})}).", "",
          f"Test split: {p2['test']['n_items']} items, {p2['test']['n_tasks']} tasks, fit on train+val, tested once.", "",
          "| learner | Spearman [95% CI] | Pearson | Kendall | ICC(C,1) | ICC(A,1) |", "|---|---|---|---|---|---|"]
    for n, r in p2["test"]["rows"].items():
        L.append(f"| {n} | {fmt(r['spearman'])} {ci_s(r['spearman_ci95'])} | {fmt(r['pearson'])} {ci_s(r.get('pearson_ci95'))} | "
                 f"{fmt(r['kendall'])} {ci_s(r.get('kendall_ci95'))} | {fmt(r['icc_c1'])} {ci_s(r.get('icc_c1_ci95'))} | {fmt(r['icc_a1'])} {ci_s(r.get('icc_a1_ci95'))} |")
    L += ["", "Paired Spearman differences (task-cluster bootstrap 95%): " + "; ".join(f"{k} {ci_s(v)}" for k, v in p2["test"]["paired_spearman_diff_ci95"].items()), "",
          f"L0 unit: {p2['test']['details'].get('L0_unit')}; L1 units: {', '.join(p2['test']['details'].get('L1_units', []))}; L2 alpha {p2['test']['details'].get('L2_alpha')}; "
          f"L3 weights {json.dumps(p2['test']['details'].get('L3_weights'))}; oracle unit {p2['test']['oracle_unit']}.", "",
          "### Descriptive 5-fold task-grouped CV over all 25 tasks (75 items)", "", "| learner | Spearman [95% CI] |", "|---|---|"]
    for n, r in p2["cv5_all_tasks"]["rows"].items():
        L.append(f"| {n} | {fmt(r['spearman'])} {ci_s(r['spearman_ci95'])} |")
    return L


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, action="append", required=True)
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--out", type=Path, default=E59 / "results")
    ap.add_argument("--part1-only", action="store_true", help="interim look: label-free indices vs the criterion only; no learners, no test split read")
    ap.add_argument("--hosted-open", default=",".join(HOSTED_OPEN), help="hosted open-weight models counted in the open set")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    items = AN.load_items()
    manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
    hosted = load_hosted()
    new = load_run_harvests(args.run)
    allh = {**hosted, **new}
    units = build_units_from(allh, items, manifest, args.draws)
    extra = part1(units, items, hosted, new, args.draws)
    hosted_open = tuple(m for m in args.hosted_open.split(",") if m)
    is_open = lambda u: u["config"] in new or u["model_key"] in hosted_open    # noqa: E731
    open_units = [u for u in units if is_open(u) and u["criteria"]["heldout"]["status"] == "COMPUTED"]
    hosted_llm = [u for u in units if u["config"] in hosted and u["kind"] == "llm" and u["criteria"]["heldout"]["status"] == "COMPUTED"]
    names = ("C_ms_gold", "F1_probe", "F2_item", "F12", "PTI_v0_frozen", "TI_var_trainnorm")
    p1 = {"n_open_units": len(open_units), "n_open_models": len({u["model_key"] for u in open_units}),
          "primary": gate_verdict(open_units, "C_ms_gold", args.draws),
          "secondary": assoc_block(open_units, names, args.draws),
          "other_sets": {"hosted_llm_units": {n: A.association(hosted_llm, n, "heldout", with_uncertainty=False) for n in names[:4]},
                         "hosted_plus_new_llm_units": {n: A.association([u for u in units if u["kind"] == "llm" and u["criteria"]["heldout"]["status"] == "COMPUTED"], n, "heldout", with_uncertainty=False) for n in names[:4]},
                         "new_units_only": {n: A.association([u for u in open_units if u["config"] in new], n, "heldout", with_uncertainty=False) for n in names[:4]}},
          "unit_table": [{"config": u["config"], "criterion": u["criteria"]["heldout"]["spearman"], "C_ms_gold": u["indices"].get("C_ms_gold"),
                          "F1_probe": u["indices"].get("F1_probe"), "F2_item": u["indices"].get("F2_item"), "status": u["criteria"]["heldout"]["status"]}
                         for u in sorted(open_units, key=lambda u: u["config"])]}
    open_cfgs = [u["config"] for u in units if is_open(u)]
    p2 = None if args.part1_only else part2(items, hosted, new, open_cfgs, args.draws)
    arms = {}
    for arm in ("O_qwen36", "O_llama70", "O_qwen32", "O_both"):
        if not consensus({c: cell_table(h) for c, h in allh.items()}, None, arm):
            continue                                                         # reference not harvested (yet)
        extra_o = part1(units, items, hosted, new, args.draws, arm)
        subj = [u for u in open_units if u["config"].split("|")[0] not in ARMS[arm][0] and f"F12@{arm}" in u["indices"]]
        nm = tuple(f"{n}@{arm}" for n in ("F1_probe", "F2_item", "F12"))
        arms[arm] = {"part1": {"n_units": len(subj), "secondary": assoc_block(subj, nm, args.draws),
                               "gate": gate_verdict(subj, f"F12@{arm}", args.draws)},
                     "reference_vs_frontier": reference_check({c: cell_table(h) for c, h in allh.items()}, items, arm),
                     "part2": None if args.part1_only else part2(items, hosted, new, open_cfgs, args.draws, arm)}
    for arm, blk in ([] if args.part1_only else arms.items()):     # Addendum 3 reading: the open reference is a usable stand-in iff FIT-PASS and within 0.10 of the frontier arm
        fr, ar = p2["verdict"]["chosen_by_validation"], blk["part2"]["verdict"]["chosen_by_validation"]
        rf = p2["test"]["rows"].get(fr, {}).get("spearman") if fr else None
        ra = blk["part2"]["test"]["rows"].get(ar, {}).get("spearman") if ar else None
        blk["substitute_reading"] = {"frontier_arm_chosen_test_rho": rf, "arm_chosen_test_rho": ra, "arm_FIT_PASS": blk["part2"]["verdict"]["FIT_PASS"],
                                     "SUBSTITUTE_OK": bool(blk["part2"]["verdict"]["FIT_PASS"] and rf is not None and ra is not None and ra >= rf - 0.10)}
    res = {"experiment": 59, "draws": args.draws, "runs": [str(r) for r in args.run], "part1": p1, "part2": p2, "arms": arms,
           "status_counts": {u["config"]: u["status_counts"] for u in units if u["config"] in new}}
    (args.out / "ANALYSIS.json").write_text(json.dumps(res, indent=1, default=float))
    write_report(args.out / "RESULTS_open_weight_proxy_fit.md", res)
    print(json.dumps({"part1_verdict": p1["primary"]["verdict"], "part2_verdict": p2["verdict"]["label"] if p2 else "not run (--part1-only)",
                      "n_open_units": p1["n_open_units"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
