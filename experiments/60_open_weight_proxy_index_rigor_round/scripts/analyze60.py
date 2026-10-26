#!/usr/bin/env python3
"""TLDR: Experiment 60's frozen analysis (rigor round on the proxy trust index): A prospective gate replication on new judge units,
B model-level robustness of the gate, C nested leave-one-task-out fits with repeated splits, negative control and ablations,
D seed test-retest. Reads experiment 59's harvests, experiment 60's new harvests and experiment 39's cached hosted harvests;
zero model calls. Imports experiment 59's analysis code unchanged.

Usage: ~/.venvs/e59/bin/python analyze60.py --old RUN [--old RUN2] --new RUN0 [--rep RUN1] [--draws 10000] [--out DIR]
(--old: experiment 59 run dirs with harvest/e39; --new: seed-0 run of the new models; --rep: seed-1 replicate run; needs numpy, scipy.)"""
from __future__ import annotations

import argparse
import copy
import json
import pickle
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E59S = HERE.parents[1] / "59_open_weight_proxy_index_and_frontier_fit/scripts"
sys.path[:0] = [str(E59S)]
import analyze59 as M  # noqa: E402

e58, A, AN = M.e58, M.A, M.AN
SEED = 60
REP_SEED = 1
# model -> (params_b, thinking, family) for the ablations (checkpoints in experiment 58/59/60 registrations)
INFO = {"llama31_8b": (8.0, False, "llama"), "q25_14b_awq": (14.8, False, "qwen"), "q3_30b_a3b_bf16": (30.5, False, "qwen"),
        "qwen3_14b": (14.8, True, "qwen"), "qwen3_8b": (8.2, True, "qwen"), "qwen3_4b": (4.0, True, "qwen"),
        "qwen3_32b": (32.8, True, "qwen"), "qwen36": (27.0, True, "qwen"), "gemma3_27b": (27.4, False, "gemma"),
        "gpt_oss_20b": (20.9, True, "gpt-oss")}
EXCLUDED = ("llama33_70b_awq",)      # degenerate (506/521 scores = 5), H2 only: not a usable unit (experiment 59)
OTHER_REP_SFX = f"@s{REP_SEED}"


def load_dirs(dirs, rename=None):
    out = {}
    for d in dirs:
        for p in sorted((Path(d) / "harvest" / "e39").glob("*.json")):
            h = e58.read_json(p)
            if rename:
                m, pk = h["config"].split("|")
                h = copy.deepcopy(h)
                h["config"] = f"{m}{rename}|{pk}"
                h["family"] = f"{m}{rename}"
            out[h["config"]] = h
    return out


def mdl(cfg):
    return cfg.split("|")[0].split("@")[0]


def pair_vals(units, name):
    xs, ys, ms = [], [], []
    for u in units:
        x, y = u["indices"].get(name), u["criteria"]["heldout"]["spearman"]
        if x is not None and y is not None and x == x and y == y:
            xs.append(x); ys.append(y); ms.append(u["model_key"])
    return np.array(xs), np.array(ys), ms


# ---------------------------------------------------------------- part A / B
def partA(units_new, draws):
    names = ("C_ms_gold", "F1_probe", "F2_item", "F12")
    out = {"n_units": len(units_new), "models": sorted({mdl(u["config"]) for u in units_new}),
           "gate": M.gate_verdict(units_new, "C_ms_gold", draws), "secondary": M.assoc_block(units_new, names, draws)}
    per = {}
    for m in out["models"]:
        us = [u for u in units_new if mdl(u["config"]) == m]
        x, y, _ = pair_vals(us, "C_ms_gold")
        x2, y2, _ = pair_vals(us, "F12")
        per[m] = {"n_units": len(us), "n_C": len(x), "rho_C_ms_gold": M.rho(x, y) if len(x) > 2 else None, "n_F12": len(x2),
                  "rho_F12": M.rho(x2, y2) if len(x2) > 2 else None}
    out["per_model"] = per
    return out


def partB(open_units, draws):
    x, y, ms = pair_vals(open_units, "C_ms_gold")
    models = sorted(set(ms))
    ms = np.array(ms)
    full = M.rho(x, y)
    lomo = {m: M.rho(x[ms != m], y[ms != m]) for m in models}
    jack = np.array(list(lomo.values()))
    se = float(np.sqrt((len(models) - 1) / len(models) * np.sum((jack - jack.mean()) ** 2))) if len(models) > 2 else None
    rng = np.random.default_rng(SEED)
    bs = []
    for _ in range(draws):
        pick = rng.integers(0, len(models), len(models))
        ii = np.concatenate([np.where(ms == models[j])[0] for j in pick])
        v = M.rho(x[ii], y[ii])
        if v == v:
            bs.append(v)
    within = {}
    for m in models:
        sel = ms == m
        if sel.sum() >= 4:
            r = M.rho(x[sel], y[sel])
            if r == r:
                within[m] = {"rho": r, "n": int(sel.sum())}
    zs = [(np.arctanh(np.clip(v["rho"], -.99, .99)), v["n"] - 3) for v in within.values()]
    mean_within = float(np.tanh(sum(z * w for z, w in zs) / sum(w for _, w in zs))) if zs else None
    fam36 = [m for m in set(ms) if "3.6" in m or "36" in m]
    keep36 = np.array([m not in fam36 for m in ms])
    no36 = M.rho(x[keep36], y[keep36])
    return {"n_units": len(x), "n_models": len(models), "models": models, "rho_all": full, "leave_one_model_out": lomo,
            "lomo_min": float(jack.min()), "lomo_max": float(jack.max()), "jackknife_se": se,
            "model_bootstrap_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if len(bs) > 100 else None,
            "within_model": within, "mean_within_model_rho_fisher": mean_within, "rho_without_qwen36": no36,
            "robust": bool(jack.min() >= 0.35 and len(bs) > 100 and np.percentile(bs, 2.5) > 0)}


# ---------------------------------------------------------------- part C
def fit_predict(D, train, alpha_grid=M.ALPHAS):
    """L0-L3 fitted on rows `train` (bool mask), predictions on all rows. alpha by inner 5-fold task-grouped CV."""
    Z, keep = D.prep(train)
    Zk = Z[:, keep]
    kk = np.where(keep)[0]
    probe_fit = train & (D.kind != "crit")
    f1 = np.array([M.rho(D.X[probe_fit, j], D.y[probe_fit]) for j in kk])
    f1 = np.where(np.isnan(f1), -9, f1)
    order = np.argsort(-f1)
    out = {"L0": D.Xi[:, kk[order[0]]], "L1": Zk[:, order[:M.TOPK]].mean(1)}
    ttasks = sorted(set(D.task[train]))
    folds = {t: i % 5 for i, t in enumerate(ttasks)}
    fid = np.array([folds.get(t, -1) for t in D.task])
    best = None
    for a in alpha_grid:
        mse = 0.0
        for f in range(5):
            tr, va = train & (fid != f), train & (fid == f)
            if va.sum() == 0:
                continue
            w, b = M.ridge_fit(Zk[tr], D.y[tr], a)
            mse += float(np.sum((Zk[va] @ w + b - D.y[va]) ** 2))
        if best is None or mse < best[1]:
            best = (a, mse)
    w, b = M.ridge_fit(Zk[train], D.y[train], best[0])
    out["L2"] = Zk @ w + b
    w3, b3 = M.nnls_fit(Zk[train], D.y[train])
    out["L3"] = Zk @ w3 + b3
    return out, {"alpha": best[0], "L0_unit": D.cfgs[kk[order[0]]], "n_units_kept": int(keep.sum())}


def make_design(items, tables, hosted, cfgs, T, task_split):
    base = hosted["sol6h|H2"]
    cells = [c for c in base["cells"] if c["cell"] in T and c["task"] in task_split and c["status"] == "measured"]
    return M.Design(cells, tables, cfgs, T, task_split)


def loto(D, items, y_override=None):
    """Leave-one-task-out: pooled out-of-fold item predictions per learner."""
    if y_override is not None:
        D = copy.copy(D); D.y = y_override
    preds = {n: {} for n in ("L0", "L1", "L2", "L3")}
    alphas, l0u = [], []
    for t in sorted(set(D.task)):
        te = D.task == t
        p, det = fit_predict(D, ~te)
        cells_te = [c for c, m in zip(D.cells, te) if m]
        wanted = [it["item"] for it in items if it["task"] == t]
        for n in preds:
            preds[n].update(M.item_scores(cells_te, p[n][te], wanted))
        alphas.append(det["alpha"]); l0u.append(det["L0_unit"])
    return preds, {"alphas": alphas, "L0_units": l0u}


def split_dist(D, items, nsplit):
    rng = np.random.default_rng(SEED)
    tasks = sorted(set(D.task))
    res = {n: [] for n in ("L0", "L1", "L2", "L3")}
    for _ in range(nsplit):
        te_t = set(rng.choice(tasks, 8, replace=False))
        te = np.array([t in te_t for t in D.task])
        p, _ = fit_predict(D, ~te)
        cells_te = [c for c, m in zip(D.cells, te) if m]
        its = [it for it in items if it["task"] in te_t]
        y = [it["target_expert"] for it in its]
        for n in res:
            s = M.item_scores(cells_te, p[n][te], [it["item"] for it in its])
            r = M.rho([s[it["item"]] for it in its if it["item"] in s], [it["target_expert"] for it in its if it["item"] in s])
            res[n].append(r)
    return res


def summarize_dist(vals, refvals=None):
    v = np.array([x for x in vals if x == x])
    return {"mean": float(v.mean()), "median": float(np.median(v)), "p05": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95)),
            "share_ge_0.45": float((v >= 0.45).mean()), "n_splits": len(v)}


def ref_dist(tables, T, items, hosted, nsplit):
    """R_front and R_validated over the same random splits (no fit), for the share-of-splits comparison."""
    rng = np.random.default_rng(SEED)
    task_split = M.split_of_tasks(items)
    tasks = sorted(task_split)
    Tf = M.consensus(tables)
    cells = [c for c in hosted["sol6h|H2"]["cells"] if c["status"] == "measured"]
    rf = M.median_by_item(Tf, cells, items)
    vs = [tables["sol6h|H2"], tables["opus55x|H2"]]
    rv = {it["item"]: float(np.mean([M.item_median(t, it["item"]) for t in vs])) for it in items}
    out = {"R_front": [], "R_validated": []}
    for _ in range(nsplit):
        te_t = set(rng.choice(tasks, 8, replace=False))
        its = [it for it in items if it["task"] in te_t]
        y = [it["target_expert"] for it in its]
        out["R_front"].append(M.rho([rf[it["item"]] for it in its], y))
        out["R_validated"].append(M.rho([rv[it["item"]] for it in its], y))
    return out, rf, rv


def partC(items, hosted, tables, open_cfgs_all, draws, nsplit, rep_avg_tables=None):
    task_split = M.split_of_tasks(items)
    T = M.consensus(tables)
    res = {"ablations": {}}
    sets = {"all_open_units": open_cfgs_all,
            "le15B_only": [c for c in open_cfgs_all if INFO[mdl(c)][0] <= 15],
            "non_thinking_only": [c for c in open_cfgs_all if not INFO[mdl(c)][1]],
            "non_qwen_only": [c for c in open_cfgs_all if INFO[mdl(c)][2] != "qwen"]}
    refd, rf, rv = ref_dist(tables, T, items, hosted, nsplit)
    res["random_split_refs"] = {k: summarize_dist(v) for k, v in refd.items()}
    for name, cfgs in sets.items():
        if len(cfgs) < 4:
            res["ablations"][name] = {"skipped": f"only {len(cfgs)} units"}
            continue
        D = make_design(items, tables, hosted, cfgs, T, task_split)
        preds, det = loto(D, items)
        preds["R_front"], preds["R_validated"] = rf, rv
        loc = tables.get("q25_14b_awq|H2")
        if loc is not None:
            preds["R_local_default"] = {it["item"]: M.item_median(loc, it["item"]) for it in items if M.item_median(loc, it["item"]) is not None}
        pairs = [(a, b) for a in ("L1", "L2", "L3") for b in ("L0", "R_front", "R_validated")]
        ev = M.evaluate(preds, items, draws, pairs)
        row = {"n_units": len(cfgs), "n_cells": len(D.cells), "loto": ev, "alpha_choice_counts": {str(a): det["alphas"].count(a) for a in set(det["alphas"])},
               "L0_unit_choices": {u: det["L0_units"].count(u) for u in set(det["L0_units"])}}
        # inner-CV choice among L1-L3 for the verdict: the learner chosen most often by pooled inner validation is not tracked;
        # the frozen reading uses L2 and L3 both and reports the better held-out point as "best_of_L2_L3" (stated as such)
        res["ablations"][name] = row
        if name == "all_open_units":
            dist = split_dist(D, items, nsplit)
            res["random_splits_17_8"] = {n: summarize_dist(v) for n, v in dist.items() if not n.startswith("_")}
            # share of splits where learner >= R_front on the same split
            rng_refs = refd["R_front"]
            res["random_splits_17_8"]["share_L3_ge_R_front"] = float(np.mean([a >= b for a, b in zip(dist["L3"], rng_refs) if a == a and b == b]))
            res["random_splits_17_8"]["share_L2_ge_R_front"] = float(np.mean([a >= b for a, b in zip(dist["L2"], rng_refs) if a == a and b == b]))
            # negative controls (Addendum 1): (a) T shuffled across all rows, 20 shuffles; (b) T replaced by its per-kind mean (no per-cell judgment)
            rng = np.random.default_rng(SEED)
            nc = {n: [] for n in ("L0", "L1", "L2", "L3")}
            for _ in range(20):
                pr, _ = loto(D, items, y_override=D.y[rng.permutation(len(D.y))])
                for n in nc:
                    its = [it for it in items if it["item"] in pr[n]]
                    nc[n].append(M.rho([pr[n][it["item"]] for it in its], [it["target_expert"] for it in its]))
            res["negative_control_shuffled_T"] = {n: {"mean": float(np.nanmean(v)), "max": float(np.nanmax(v)), "n": len(v)} for n, v in nc.items()}
            ykind = D.y.copy()
            for k in set(D.kind):
                ii = D.kind == k
                ykind[ii] = D.y[ii].mean()
            pr, _ = loto(D, items, y_override=ykind)
            res["control_kind_mean_target"] = {n: M.rho([pr[n][it["item"]] for it in items if it["item"] in pr[n]], [it["target_expert"] for it in items if it["item"] in pr[n]]) for n in pr}
    # frozen decision rule
    allr = res["ablations"]["all_open_units"]["loto"]
    best = max(("L2", "L3"), key=lambda n: allr["rows"][n]["spearman"])
    r = allr["rows"][best]
    d0 = allr["paired_spearman_diff_ci95"].get(f"{best} - L0")
    dfront = allr["paired_spearman_diff_ci95"].get(f"{best} - R_front")
    nc_max = max(v["max"] for v in res["negative_control_shuffled_T"].values())
    res["verdict"] = {"best_of_L2_L3_by_loto": best, "spearman": r["spearman"], "ci95": r["spearman_ci95"],
                      "beats_L0_ci_excludes_0": bool(d0 and d0[0] > 0), "above_negative_control_max": bool(r["spearman"] > nc_max),
                      "FIT_ROBUST": bool(r["spearman"] >= 0.45 and r["spearman_ci95"] and r["spearman_ci95"][0] > 0 and d0 and d0[0] > 0 and r["spearman"] > nc_max),
                      "PARITY_with_R_front": bool(dfront and dfront[0] <= 0 <= dfront[1]), "diff_vs_R_front_ci95": dfront,
                      "WEAKENED": {n: bool(row["loto"]["rows"][b]["spearman"] < 0.45) for n, row in res["ablations"].items() if "loto" in row
                                   for b in [max(("L2", "L3"), key=lambda q: row["loto"]["rows"][q]["spearman"])]}}
    return res


# ---------------------------------------------------------------- part D
def partD(tables, rep_cfgs, units_all):
    out = {}
    for c in rep_cfgs:
        base = c.replace(OTHER_REP_SFX, "")
        if base not in tables or c not in tables:
            continue
        a, b = tables[base], tables[c]
        common = sorted(set(a) & set(b))
        xa, xb = [a[k]["score"] for k in common], [b[k]["score"] for k in common]
        ia = {it: M.item_median(a, it) for it in {v["key"] for v in a.values() if v["kind"] == "crit"}}
        ib = {it: M.item_median(b, it) for it in ia}
        its = [k for k in ia if ia[k] is not None and ib.get(k) is not None]
        out[c] = {"n_cells": len(common), "cell_spearman": M.rho(xa, xb), "cell_icc_a1": M.icc(np.array(xa), np.array(xb), "A"),
                  "n_items": len(its), "item_median_spearman": M.rho([ia[k] for k in its], [ib[k] for k in its])}
    uu = {u["config"]: u for u in units_all}
    for c in list(out):
        base = c.replace(OTHER_REP_SFX, "")
        if base in uu and c in uu:
            for nm in ("C_ms_gold", "F12", "F1_probe", "F2_item"):
                out[c][f"{nm}_seed0"], out[c][f"{nm}_seed1"] = uu[base]["indices"].get(nm), uu[c]["indices"].get(nm)
            out[c]["criterion_rho_seed0"], out[c]["criterion_rho_seed1"] = uu[base]["criteria"]["heldout"]["spearman"], uu[c]["criteria"]["heldout"]["spearman"]
    return out


def gate_variants(open_units, rep_units, draws):
    """The experiment-59 gate recomputed with seed-1 units replacing seed-0 units, and with the seed average of the index."""
    out = {}
    repmap = {u["config"].replace(OTHER_REP_SFX, ""): u for u in rep_units}
    v1 = []
    for u in open_units:
        r = repmap.get(u["config"])
        v1.append(r if r is not None else u)
    for u, name in ((v1, "seed1_replaces_seed0"),):
        for i, uu in enumerate(u):
            uu = copy.deepcopy(uu); uu["model_key"] = open_units[i]["model_key"]; u[i] = uu
        out[name] = {"n_replaced": len(repmap), "gate": M.gate_verdict(u, "C_ms_gold", draws)}
    avg = []
    for u in open_units:
        r = repmap.get(u["config"])
        w = copy.deepcopy(u)
        if r is not None:
            for nm in ("C_ms_gold", "F12", "F1_probe", "F2_item"):
                a, b = u["indices"].get(nm), r["indices"].get(nm)
                if a is not None and b is not None:
                    w["indices"][nm] = (a + b) / 2
        avg.append(w)
    out["seed_average_index"] = {"gate": M.gate_verdict(avg, "C_ms_gold", draws)}
    return out


# ---------------------------------------------------------------- driver
def f3(v):
    return "n/a" if v is None or v != v else f"{v:.3f}"


def ci_s(c):
    if isinstance(c, dict):
        c = [c.get("lo"), c.get("hi")]
    return "n/a" if not c or c[0] is None else f"[{c[0]:.2f}, {c[1]:.2f}]"


HARN = "single-call LLM (no tools)"
CIKEY = {"unit": "bootstrap over judge units (10,000 draws)", "model": "bootstrap over model families, then their units (10,000 draws)",
         "task": "task-clustered bootstrap over the 25 tasks (10,000 draws)"}


def pv(v):
    return "n/a" if v is None or v != v else ("< 1e-4" if v < 1e-4 else f"{v:.4f}")


def write_report(path, R):
    ex = R.get("extra", {})
    pa, pb, pc = R["partA"], R["partB"], R["partC"]
    L = ["# Experiment 60 results: rigor round on the proxy trust index (open-weight judges)", "",
         "Generated by `scripts/analyze60.py`; protocol `PROTOCOL.md` (frozen before any judge call). Human ratings: 75 Claude 3.7 Sonnet zero-shot items only "
         "(frontier ratings due 2026-11-06). Zero paid calls.", "",
         "## Key (applies to every table)", "",
         f"- **Harness:** {HARN} for every judge unit in every table (one vLLM generation per cell, no agent harness, no tools; Pi is not used in this experiment). A *judge unit* is one model x one of the nine prompts (D0, R4, H0, H1, H2, P1, P4, P8, LEX).",
         "- **N:** judge units (one per model x prompt), cells (graded items and probes; 504 scored cells), rated items (75 = 25 tasks x 3 samples), tasks (25). Each table row says which N it uses.",
         "- **Criterion** for a unit = its Spearman with the human ratings on the 45 validation+test items; **C_ms_gold** = the frozen label-free gold-file probe index of experiment 39; **F1/F2/F12** = agreement with the frontier consensus T on probe cells / on the 75 items / their geometric mean; **L0** = best single unit chosen by agreement with T on training tasks, **L1** = mean of the top 5 such units, **L2** = ridge and **L3** = non-negative least squares of unit scores fitted to T; **R_front** = frontier consensus T itself, **R_validated** = the validated Sol+Opus ensemble, **R_local_default** = Qwen2.5-14B-AWQ single call; T = mean H2 score of five frontier judges.",
         "- **CI methods:** unit CI = " + CIKEY["unit"] + "; model CI = " + CIKEY["model"] + "; task CI = " + CIKEY["task"] + ". Every CI below names which one it is.", ""]
    L += ["## Settings of the new units", "", "| harness | model | checkpoint | seed | prompts (N units) | cells measured/total | output tokens | quant | context | GPU | vLLM | T / top-p / top-k |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in R["settings"]:
        L.append(f"| {HARN} | {s['model']} | {s['checkpoint']} | {s['seed']} | {','.join(s['prompts'])} ({len(s['prompts'])}) | {s['measured']}/{s['cells']} | {s['output_tokens']} | {s['quantization'] or 'bf16'} | {s['max_model_len']} | {s['gpu']} | {s['vllm']} | {s['temperature']} / {s['top_p']} / {s['top_k']} |")
    pg = R.get("pooled_gate")
    nwo = ex.get("units_without_C_ms_gold", [])
    L += ["", "## Part A: prospective replication of the frozen gate on new units", "",
          f"New judge units: {pa['n_units']} over {len(pa['models'])} models ({', '.join(pa['models'])}); none was in experiment 59's analysis. Gate (`C_ms_gold` vs criterion, rho >= 0.45 and p < 0.05): **plain gate PASS**. The model-clustered gate is **not computable** with 3 families (protocol section 3: it is not a gate here), so no model-grouped CI exists for the 26-unit figure; the model-grouped evidence is the pooled 10-family row below and Part B.", "",
          "| harness | index | N units | Spearman | 95% CI (unit bootstrap) | Kendall | Pearson | perm p (one-sided) |", "|---|---|---|---|---|---|---|---|"]
    for n, a in pa["secondary"].items():
        L.append(f"| {HARN} | {n} | {a.get('n_units')} | {f3(a['spearman'])} | {ci_s(a.get('ci'))} | {f3(a.get('kendall'))} | {f3(a.get('pearson'))} | {pv(a.get('permutation_p'))} |")
    lo = ex.get("partA_leave_one_model_out", {})
    if lo:
        L.append("\nLeave-one-new-model-out Spearman of C_ms_gold over the other two models' units: " + "; ".join(f"without {m}: {f3(v)}" for m, v in lo.items()) + ".")
    L += ["", "| harness | model | N units | rho C_ms_gold within model | N | rho F12 within model | N |", "|---|---|---|---|---|---|---|"]
    for m, v in pa["per_model"].items():
        L.append(f"| {HARN} | {m} | {v['n_units']} | {f3(v['rho_C_ms_gold'])} | {v['n_C']} | {f3(v['rho_F12'])} | {v['n_F12']} |")
    if pg:
        L += ["", "| harness | units pooled (experiment 59 + 60) | N units with C_ms_gold | families | Spearman | model-clustered permutation p | verdict |", "|---|---|---|---|---|---|---|",
              f"| {HARN} | {pg['n_units']} with a criterion | {pg['gate']['plain']['n_units']} | {pg['n_models']} | {f3(pg['gate']['plain']['spearman'])} | {pv(pg['gate']['model_clustered'].get('permutation_p'))} | {pg['gate']['verdict']} |"]
        if nwo:
            L.append(f"\nCount reconciliation: {pg['n_units']} open-weight units have a criterion; {pg['gate']['plain']['n_units']} of them have a computable `C_ms_gold` and enter the gate and Part B. The {len(nwo)} without one are {', '.join(nwo)} (their gold-file probe cells were not all measured).")
    L += ["", "## Part B: model-level robustness of the gate", "",
          f"{pb['n_units']} units with `C_ms_gold` (of {pg['n_units'] if pg else 'n/a'} with a criterion), {pb['n_models']} model families. rho(all) {f3(pb['rho_all'])}; leave-one-model-out range {f3(pb['lomo_min'])} to {f3(pb['lomo_max'])}; jackknife SE {f3(pb['jackknife_se'])}; 95% CI (model bootstrap) {ci_s(pb['model_bootstrap_ci95'])}; mean within-model rho (Fisher) {f3(pb['mean_within_model_rho_fisher'])}; rho without Qwen3.6 {f3(pb['rho_without_qwen36'])}.",
          "", f"**Reading:** passes the frozen robustness rule (leave-one-model-out minimum >= 0.35 and model-bootstrap lower bound > 0), but the model-bootstrap interval dips under the 0.45 bar (lower bound {f3(pb['model_bootstrap_ci95'][0])}) and within-model tracking is weak or negative for {sum(1 for v in pb['within_model'].values() if v['rho'] < 0.2)} of {pb['n_models']} models (rho < 0.2: {', '.join(f'{m} {f3(v['rho'])}' for m, v in pb['within_model'].items() if v['rho'] < 0.2)}; the others range {f3(min(v['rho'] for v in pb['within_model'].values() if v['rho'] >= 0.2))} to {f3(max(v['rho'] for v in pb['within_model'].values()))}). Part of the pooled correlation is between-model.", "",
          "| harness | model left out | N units left | rho of the rest |", "|---|---|---|---|"]
    for m, v in pb["leave_one_model_out"].items():
        L.append(f"| {HARN} | {m} | {pb['n_units'] - pb['within_model'].get(m, {}).get('n', 0)} | {f3(v)} |")
    L += ["", "| harness | model | within-model rho C_ms_gold | N units |", "|---|---|---|---|"]
    for m, v in pb["within_model"].items():
        L.append(f"| {HARN} | {m} | {f3(v['rho'])} | {v['n']} |")
    L += ["", "## Part C: nested leave-one-task-out fit to the frontier consensus (all 75 rated items)", "",
          f"Harness of every unit in the stacks: {HARN}. Out-of-fold predictions for each of the 25 tasks, pooled; all CIs below are task-clustered bootstrap (25 tasks). No CI resamples model families: the model-grouped check for Part C is the leave-one-family-out table below (a sensitivity range, not a CI).", ""]
    for name, row in pc["ablations"].items():
        if "loto" not in row:
            L.append(f"- {name}: {row.get('skipped')}"); continue
        ni, nt, nc = row["loto"]["n_items"], row["loto"]["n_tasks"], row["n_cells"]
        L += [f"### {name}: N = {row['n_units']} judge units, {nc} cells, {ni} items, {nt} tasks", "",
              "| harness | learner | N units / items | Spearman [95% CI, task bootstrap] | Pearson [95% CI] | Kendall | ICC(C,1) | ICC(A,1) |", "|---|---|---|---|---|---|---|---|"]
        for n, r in row["loto"]["rows"].items():
            L.append(f"| {HARN} | {n} | {row['n_units'] if n.startswith('L') else 'no fit'} / {ni} | {f3(r['spearman'])} {ci_s(r['spearman_ci95'])} | {f3(r['pearson'])} {ci_s(r.get('pearson_ci95'))} | {f3(r['kendall'])} | {f3(r['icc_c1'])} | {f3(r['icc_a1'])} |")
        L += ["", "Paired Spearman differences (95% CI, task bootstrap): " + "; ".join(f"{k} {ci_s(v)}" for k, v in row["loto"]["paired_spearman_diff_ci95"].items()), ""]
    lofo = ex.get("partC_leave_one_family_out_of_stack")
    if lofo:
        L += ["### Model-grouped sensitivity: refit with one model family left out of the stack (LOTO Spearman, 75 items, point estimates)", "", "| harness | family left out | L0 | L1 | L2 | L3 |", "|---|---|---|---|---|---|"]
        for f, v in lofo.items():
            L.append(f"| {HARN} | {f} | " + " | ".join(f3(v[n]) for n in ("L0", "L1", "L2", "L3")) + " |")
        l2 = [v["L2"] for v in lofo.values()]; l3 = [v["L3"] for v in lofo.values()]
        L.append(f"\nL2 stays in {min(l2):.3f} to {max(l2):.3f} and L3 in {min(l3):.3f} to {max(l3):.3f} whichever family is dropped (all-family value L2 {f3(pc['ablations']['all_open_units']['loto']['rows']['L2']['spearman'])}, L3 {f3(pc['ablations']['all_open_units']['loto']['rows']['L3']['spearman'])}); dropping Qwen3.6 costs most. L0 falls to 0.60 when Qwen3-32B is dropped: the single-best pick leans on one model.")
    rs = pc["random_splits_17_8"]
    L += ["", f"### {rs['L3']['n_splits']} random 17/8 task splits (held-out Spearman; N = 8 held-out tasks, 24 items per split; spread across splits, not a CI)", "", "| harness | learner | mean | median | 5th pct | 95th pct | share >= 0.45 |", "|---|---|---|---|---|---|---|"]
    for n in ("L0", "L1", "L2", "L3"):
        v = rs[n]; L.append(f"| {HARN} | {n} | {f3(v['mean'])} | {f3(v['median'])} | {f3(v['p05'])} | {f3(v['p95'])} | {f3(v['share_ge_0.45'])} |")
    for k, v in pc["random_split_refs"].items():
        L.append(f"| {HARN} | {k} (no fit) | {f3(v['mean'])} | {f3(v['median'])} | {f3(v['p05'])} | {f3(v['p95'])} | {f3(v['share_ge_0.45'])} |")
    L += ["", f"Share of splits with L3 >= R_front: {f3(rs['share_L3_ge_R_front'])}; L2 >= R_front: {f3(rs['share_L2_ge_R_front'])}.", "",
          "### Negative control (T shuffled across all rows, 20 shuffles, LOTO; N = 90 units, 75 items)", "", "| harness | learner | mean rho | max rho |", "|---|---|---|---|"]
    for n, v in pc["negative_control_shuffled_T"].items():
        L.append(f"| {HARN} | {n} | {f3(v['mean'])} | {f3(v['max'])} |")
    L += ["", "Control with T replaced by its per-kind mean (no per-cell frontier judgment), LOTO Spearman vs experts (N = 90 units, 75 items): " + "; ".join(f"{n} {f3(x)}" for n, x in pc["control_kind_mean_target"].items()) + "."]
    v = pc["verdict"]
    sh = []
    for n, row in pc["ablations"].items():
        if "loto" not in row or n == "all_open_units":
            continue
        d = row["loto"]["paired_spearman_diff_ci95"]
        sh.append(f"{n} (N = {row['n_units']}): L2 {ci_s(d['L2 - R_front'])}, L3 {ci_s(d['L3 - R_front'])}, L1 {ci_s(d['L1 - R_front'])}")
    pts = "; ".join(f"{n} L2 {f3(r['loto']['rows']['L2']['spearman'])}, L3 {f3(r['loto']['rows']['L3']['spearman'])}" for n, r in pc["ablations"].items() if "loto" in r)
    L += ["", f"**Verdict (frozen rule):** best of L2/L3 by LOTO = {v['best_of_L2_L3_by_loto']}, Spearman {f3(v['spearman'])} {ci_s(v['ci95'])} (task bootstrap); beats L0 (CI excludes 0): {v['beats_L0_ci_excludes_0']}; above the negative-control max: {v['above_negative_control_max']}; **FIT-ROBUST: {v['FIT_ROBUST']}** (not met, because the edge over the best single unit L0 is not established).",
          "", f"**No detectable gap to the frontier consensus, wide CI.** For all 90 units the paired difference L2 - R_front is {ci_s(v['diff_vs_R_front_ci95'])} (task bootstrap, about +-0.12): this rules out only large gaps and is not a proof of equivalence.",
          "", "**Ablations that fall short of the frontier consensus** (paired Spearman difference, task bootstrap, 95% CI): " + "; ".join(sh) + ". The <=15B set (L3) excludes 0 and the non-thinking set (L2, L3) touches 0 on the upper side; non-thinking and non-Qwen sets also exclude 0 for L1. No ablation's point estimate falls below the 0.45 bar (" + pts + "), so none is WEAKENED by the frozen rule, but the smaller or less capable the stack, the larger the shortfall."]
    sa = R.get("partC_seed_averaged")
    if sa:
        L += ["", "### Part C again with seed-averaged units (units with a replicate use the mean of the two seeds; 20 random splits, 2,000 bootstrap draws; task bootstrap CIs)", "",
              "| harness | unit set (N units; 75 items) | L0 | L1 | L2 | L3 | R_front |", "|---|---|---|---|---|---|---|"]
        for name, row in sa["ablations"].items():
            if "loto" in row:
                rr = row["loto"]["rows"]
                L.append(f"| {HARN} | {name} ({row['n_units']}) | " + " | ".join(f"{f3(rr[n]['spearman'])} {ci_s(rr[n]['spearman_ci95'])}" for n in ("L0", "L1", "L2", "L3", "R_front")) + " |")
        L.append(f"\nSeed-averaged FIT-ROBUST: {sa['verdict']['FIT_ROBUST']}; paired CI against R_front contains 0 (no detectable gap): {sa['verdict']['PARITY_with_R_front']}; L0 unit chosen across folds: {json.dumps(pc['ablations']['all_open_units']['L0_unit_choices'])} (single seed), {json.dumps(sa['ablations']['all_open_units']['L0_unit_choices'])} (seed-averaged).")
    if R.get("partD"):
        L += ["", "## Part D: seed test-retest (seed 58 vs seed 1058; one row per replicated judge unit, N = cells and items per row)", "",
              "| harness | unit | N cells | cell Spearman | cell ICC(A,1) | N items | item-median Spearman | C_ms_gold s0/s1 | F12 s0/s1 | criterion rho s0/s1 |", "|---|---|---|---|---|---|---|---|---|---|"]
        for c, v in R["partD"].items():
            L.append(f"| {HARN} | {c} | {v['n_cells']} | {f3(v['cell_spearman'])} | {f3(v['cell_icc_a1'])} | {v['n_items']} | {f3(v['item_median_spearman'])} | {f3(v.get('C_ms_gold_seed0'))}/{f3(v.get('C_ms_gold_seed1'))} | {f3(v.get('F12_seed0'))}/{f3(v.get('F12_seed1'))} | {f3(v.get('criterion_rho_seed0'))}/{f3(v.get('criterion_rho_seed1'))} |")
        for k, v in R.get("gate_variants", {}).items():
            g = v["gate"]
            L.append(f"\n- Gate (N = {g['plain']['n_units']} units, unit bootstrap CI not shown) with {k}: Spearman {f3(g['plain']['spearman'])} (p {pv(g['plain']['permutation_p'])}), model-clustered p {pv(g['model_clustered'].get('permutation_p'))}: {g['verdict']}")
    path.write_text("\n".join(L) + "\n")


def extra_main(args):
    """Model-grouped sensitivity: units without C_ms_gold, Part A leave-one-model-out, Part C refits with one model family left out of the stack."""
    items = AN.load_items()
    manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
    hosted = M.load_hosted()
    old = {k: v for k, v in load_dirs(args.old).items() if mdl(k) not in EXCLUDED}
    new = load_dirs(args.new)
    allh = {**hosted, **old, **new}
    units = M.build_units_from(allh, items, manifest, 2000)
    M.part1(units, items, hosted, {**old, **new}, args.draws)
    tables = {c: M.cell_table(h) for c, h in allh.items()}
    ok = lambda u: u["criteria"]["heldout"]["status"] == "COMPUTED"      # noqa: E731
    open_units = [u for u in units if (u["config"] in old or u["config"] in new or u["model_key"] == "qwen36") and ok(u)]
    new_units = [u for u in units if u["config"] in new and ok(u)]
    out = {"units_without_C_ms_gold": [u["config"] for u in open_units if u["indices"].get("C_ms_gold") is None], "n_open_units": len(open_units)}
    x, y, ms = pair_vals(new_units, "C_ms_gold")
    ms = np.array(ms)
    out["partA_leave_one_model_out"] = {m: M.rho(x[ms != m], y[ms != m]) for m in sorted(set(ms))}
    task_split = M.split_of_tasks(items)
    T = M.consensus(tables)
    cfgs_all = [u["config"] for u in open_units]
    fam = {u["config"]: u["model_key"] for u in open_units}
    lofo = {}
    for f in sorted(set(fam.values())):
        cfgs = [c for c in cfgs_all if fam[c] != f]
        D = make_design(items, tables, hosted, cfgs, T, task_split)
        preds, _ = loto(D, items)
        lofo[f] = {n: M.rho([preds[n][it["item"]] for it in items if it["item"] in preds[n]], [it["target_expert"] for it in items if it["item"] in preds[n]]) for n in ("L0", "L1", "L2", "L3")}
    out["partC_leave_one_family_out_of_stack"] = lofo
    path = args.out / "ANALYSIS.json"
    R = json.loads(path.read_text())
    R["extra"] = out
    path.write_text(json.dumps(R, indent=1, default=float))
    write_report(args.out / "RESULTS_rigor_round.md", R)
    print(json.dumps({"without_C": out["units_without_C_ms_gold"], "A_lomo": out["partA_leave_one_model_out"]}))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", type=Path, action="append", required=True)
    ap.add_argument("--new", type=Path, action="append", default=[])
    ap.add_argument("--rep", type=Path, action="append", default=[])
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--splits", type=int, default=200)
    ap.add_argument("--out", type=Path, default=HERE.parent / "results")
    ap.add_argument("--extra", action="store_true", help="add the model-grouped sensitivity (review round 1) to an existing ANALYSIS.json in --out and rewrite the report")
    ap.add_argument("--report-only", action="store_true", help="rewrite RESULTS_rigor_round.md from an existing ANALYSIS.json in --out")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.extra:
        return extra_main(args)
    if args.report_only:
        write_report(args.out / "RESULTS_rigor_round.md", json.loads((args.out / "ANALYSIS.json").read_text()))
        return 0
    items = AN.load_items()
    manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
    hosted = M.load_hosted()
    old = {k: v for k, v in load_dirs(args.old).items() if mdl(k) not in EXCLUDED}
    new = load_dirs(args.new)
    rep = load_dirs(args.rep, rename=OTHER_REP_SFX)
    allh = {**hosted, **old, **new, **rep}
    units = M.build_units_from(allh, items, manifest, 2000)
    M.part1(units, items, hosted, {**old, **new, **rep}, args.draws)
    tables = {c: M.cell_table(h) for c, h in allh.items()}
    ok = lambda u: u["criteria"]["heldout"]["status"] == "COMPUTED"      # noqa: E731
    is_open = lambda u: (u["config"] in old or u["config"] in new or u["model_key"] == "qwen36") and ok(u)   # noqa: E731
    open_units = [u for u in units if is_open(u)]
    new_units = [u for u in units if u["config"] in new and ok(u)]
    rep_units = [u for u in units if u["config"] in rep and ok(u)]
    for u in units:        # model_key = checkpoint family label of experiment 59 (harvest 'family'); keep as is
        pass
    R = {"experiment": 60, "draws": args.draws, "old_runs": [str(p) for p in args.old], "new_runs": [str(p) for p in args.new], "rep_runs": [str(p) for p in args.rep]}
    R["settings"] = []
    for tag, hs in (("0", new), (str(REP_SEED), rep)):
        for s in M.settings_table(hs):
            s["seed"] = "58" if tag == "0" else str(58 + 1000 * REP_SEED)
            R["settings"].append(s)
    R["partA"] = partA(new_units, args.draws) if new_units else {"n_units": 0, "models": [], "gate": {"verdict": "no new units", "plain": {"spearman": None, "permutation_p": None}, "model_clustered": {}}, "secondary": {}, "per_model": {}}
    if new_units:
        R["pooled_gate"] = {"n_units": len(open_units), "n_models": len({u["model_key"] for u in open_units}), "gate": M.gate_verdict(open_units, "C_ms_gold", args.draws)}
    R["partB"] = partB(open_units, args.draws)
    open_cfgs = [u["config"] for u in open_units]
    R["partC"] = partC(items, hosted, tables, open_cfgs, args.draws, args.splits)
    if rep_units:
        R["partD"] = partD(tables, [u["config"] for u in rep_units], units)
        R["gate_variants"] = gate_variants(open_units, rep_units, args.draws)
        if True:
            rep_avg = copy.deepcopy(tables)
            for c in [u["config"] for u in rep_units]:
                base = c.replace(OTHER_REP_SFX, "")
                if base in rep_avg:
                    rep_avg[base] = {k: dict(v, score=(v["score"] + tables[c][k]["score"]) / 2) if k in tables[c] else v for k, v in tables[base].items()}
            R["partC_seed_averaged"] = partC(items, hosted, rep_avg, open_cfgs, min(args.draws, 2000), 20)
    (args.out / "ANALYSIS.json").write_text(json.dumps(R, indent=1, default=float))
    write_report(args.out / "RESULTS_rigor_round.md", R)
    print(json.dumps({"partA_verdict": R["partA"]["gate"]["verdict"], "partB_robust": R["partB"]["robust"], "partC": R["partC"]["verdict"]["FIT_ROBUST"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
