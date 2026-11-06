#!/usr/bin/env python3
"""TLDR: Experiment 66 condition R1 (retrospective, zero calls): across experiment 39's judge configurations, does the
label-free index predict agreement with experiment 42's fixed Lean reverse-implication procedure, and does selecting
a judge by it give low prover-outcome error?

Level 1 (artifact): per configuration theta, q_theta(z) on experiment 42's Lean-valid probes z, scored against
Y_P(z), the recorded outcome of the fixed procedure; G_P(theta) = 1 - mean (q - Y)^2 on evaluation-split tasks.
Level 2 (judge): association of the frozen index with G_P across configurations, and selection regret."""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
REPO = EXP.parents[1]
CFG_PATH = EXP / "config_r1.json"
CFG = json.loads(CFG_PATH.read_text())
sys.path[:0] = [str(REPO / CFG["e39_dir"] / "scripts")]
import analysis_lib as A  # noqa: E402  (experiment 39's frozen pure-Python library)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expit(x: float) -> float:
    return 1 / (1 + math.exp(-x)) if x >= 0 else math.exp(x) / (1 + math.exp(x))


def fit_logistic(xs, ys, ridge):
    """Logistic log loss with an L2 penalty on the slope; Newton steps (two parameters)."""
    b0, b1 = 0.0, 0.0
    n = len(xs)
    for _ in range(200):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in zip(xs, ys):
            p = expit(b0 + b1 * x)
            g0 += (p - y) / n
            g1 += (p - y) * x / n
            w = p * (1 - p) / n
            h00 += w
            h01 += w * x
            h11 += w * x * x
        g1 += ridge * b1
        h11 += ridge
        h00 += 1e-12
        det = h00 * h11 - h01 * h01
        if det <= 0:
            break
        d0 = (h11 * g0 - h01 * g1) / det
        d1 = (h00 * g1 - h01 * g0) / det
        b0, b1 = b0 - d0, b1 - d1
        if abs(d0) + abs(d1) < 1e-10:
            break
    return b0, b1


def auc(scores, ys):
    pos = [s for s, y in zip(scores, ys) if y == 1]
    neg = [s for s, y in zip(scores, ys) if y == 0]
    if not pos or not neg:
        return None
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def load_targets():
    manifest_path = REPO / CFG["e42_manifest"]
    assert sha(manifest_path) == CFG["e42_manifest_sha256"]
    assert sha(REPO / CFG["e42_procedure_script"]) == CFG["e42_procedure_script_sha256"]
    rows = [r for r in json.loads(manifest_path.read_text())["rows"] if r["valid"] is True]
    audit = {}
    for f in sorted((REPO / CFG["e42_audit_dir"]).glob("*.json")):
        audit.update(json.loads(f.read_text())["labels"])
    probes = []
    for r in rows:
        pid = f"{r['kind']}__{r['task']}__L{r['level']}"
        assert pid == r["probe_id"]
        if r["reverse"] == "unproved":
            y = 0
        elif r["reverse"] == "not_applicable" and r["family"] in ("identity", "formatting"):
            y = 1
        else:
            raise AssertionError(f"unexpected valid probe outcome {pid}: {r['reverse']}")
        if r["family"] in ("weakening", "overconstraint"):
            lab = audit.get(pid, {}).get("label")
            y_audit = {"strict": 0, "redundant": 1}.get(lab)
        else:
            y_audit = 0 if r["family"] == "vacuity" else 1
        probes.append({"pid": pid, "kind": r["kind"], "family": r["family"], "task": r["task"], "level": r["level"],
                       "sha256": r["sha256"], "y": y, "y_audit": y_audit})
    return probes


def load_split():
    path = REPO / CFG["items"]
    assert sha(path).startswith(CFG["items_sha256_prefix"])
    split = {}
    for line in path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            assert split.setdefault(row["task"], row["split"]) == row["split"]
    return split, sha(path)


def load_e39_units():
    units = {}
    for name in ("units_train_val.json", "units_test.json"):
        for u in json.loads((REPO / CFG["e39_dir"] / "results" / name).read_text())["units"]:
            assert u["config"] not in units
            units[u["config"]] = u
    return units


def fit_task_index(split):
    """C_ms_gold recomputed with experiment 39's code on ladders from fitting-split tasks only (versioned variant)."""
    manifest = json.loads((REPO / CFG["e39_dir"] / "results/probe_manifest.json").read_text())
    probes = A.valid_probes(manifest)
    keep = {k: [r for r in v if split.get(r["task"]) in CFG["fit_task_split"]] for k, v in probes.items()}
    out = {}
    for path in sorted((REPO / CFG["e39_dir"] / "results/harvest").glob("*.json")):
        sc = A.Scores(json.loads(path.read_text()))
        out[sc.config] = A.components(sc, keep)["ms_gold"]
    return out


def judge_rows(probes, split):
    fit_tasks = {t for t, s in split.items() if s in CFG["fit_task_split"]}
    eval_tasks = {t for t, s in split.items() if s in CFG["evaluation_task_splits"]}
    out = []
    for path in sorted((REPO / CFG["e42_harvest_dir"]).glob("*.json")):
        h = json.loads(path.read_text())
        sc = A.Scores(h)
        med = {p["pid"]: sc.median(p["kind"], p["task"], p["level"]) for p in probes}
        fit = [(med[p["pid"]], p["y"]) for p in probes if p["task"] in fit_tasks and med[p["pid"]] is not None]
        ev_decl = [p for p in probes if p["task"] in eval_tasks]
        ev = [p for p in ev_decl if med[p["pid"]] is not None]
        coverage = len(ev) / len(ev_decl)
        prev = sum(y for _, y in fit) / len(fit)
        xs = [x for x, _ in fit]
        if max(xs) - min(xs) > 0:
            b0, b1 = fit_logistic(xs, [y for _, y in fit], CFG["map_slope_ridge"])
        else:
            b0, b1 = math.log(prev / (1 - prev)), 0.0
        per_probe = []
        for p in ev:
            s = med[p["pid"]]
            q = expit(b0 + b1 * s)
            per_probe.append({"task": p["task"], "family": p["family"], "y": p["y"], "y_audit": p["y_audit"],
                              "s": s, "q": q, "e_fit": (q - p["y"]) ** 2, "e_raw": (s - p["y"]) ** 2,
                              "e_const": (prev - p["y"]) ** 2})
        computed = coverage + 1e-9 >= CFG["min_criterion_coverage"]
        ys = [r["y"] for r in per_probe]
        ss = [r["s"] for r in per_probe]
        audit_rows = [r for r in per_probe if r["y_audit"] is not None]
        crit = {
            "coverage": round(coverage, 4), "n_eval": len(ev), "n_declared": len(ev_decl), "n_fit": len(fit),
            "status": "COMPUTED" if computed else "NOT_COMPUTABLE", "map": [b0, b1], "fit_prevalence": prev,
            "G_P_fitted": 1 - statistics.mean(r["e_fit"] for r in per_probe) if computed else None,
            "G_P_raw": 1 - statistics.mean(r["e_raw"] for r in per_probe) if computed else None,
            "G_P_constant": 1 - statistics.mean(r["e_const"] for r in per_probe) if computed else None,
            "rank_spearman": A.spearman(ss, ys) if computed else None,
            "rank_auc": auc(ss, ys) if computed else None,
            "G_audit_fitted": (1 - statistics.mean((r["q"] - r["y_audit"]) ** 2 for r in audit_rows)) if computed else None,
            "by_family_mean_score": {f: statistics.mean(r["s"] for r in per_probe if r["family"] == f)
                                     for f in sorted({r["family"] for r in per_probe})} if per_probe else {},
        }
        out.append({"config": h["config"], "family": h["family"], "split": h["split"], "kind": h["kind"],
                    "prompt": h["config"].split("|")[-1], "criterion": crit, "per_probe": per_probe})
    return out


def corr_triplet(x, y):
    if len(x) < A.MIN_UNITS:
        return {"n": len(x), "spearman": None, "pearson": None, "kendall": None}
    return {"n": len(x), "spearman": A.spearman(x, y), "pearson": A.pearson(x, y), "kendall": A.kendall(x, y)}


def g_from(per_probe_by_task, tasks, key):
    """Criterion recomputed on resampled tasks: 1 - mean error for Brier keys; AUC of raw scores for 'auc'.
    Deviation 1 (post-run code fix): the first run recomputed the Brier criterion for the rank analysis."""
    if key == "auc":
        rows = [r for t in tasks for r in per_probe_by_task.get(t, [])]
        return auc([r["s"] for r in rows], [r["y"] for r in rows])
    num = den = 0.0
    for t in tasks:
        rows = per_probe_by_task.get(t, [])
        num += sum(r[key] for r in rows)
        den += len(rows)
    return 1 - num / den if den else None


def pick(units, index):
    best = max(units, key=lambda u: (u["index"][index], [-ord(c) for c in u["config"]]))
    return best


def analyse_pool(units, index, rng_seed, draws, crit_key="G_P_fitted", err_key="e_fit"):
    us = [u for u in units if u["index"].get(index) is not None and u["criterion"][crit_key] is not None]
    x = [u["index"][index] for u in us]
    y = [u["criterion"][crit_key] for u in us]
    res = {"index": index, "criterion": crit_key, "units": len(us), "families": len({u["family"] for u in us}),
           "association": corr_triplet(x, y)}
    if len(us) < A.MIN_UNITS:
        return res
    rng = random.Random(rng_seed)
    k = sum(1 for _ in range(draws) if A.spearman(rng.sample(x, len(x)), y) >= res["association"]["spearman"] - 1e-12)
    res["permutation_p_one_sided"] = (k + 1) / (draws + 1)
    fams = sorted({u["family"] for u in us})
    k2 = 0
    for _ in range(draws):
        xs = {}
        for f in fams:
            vals = [u["index"][index] for u in us if u["family"] == f]
            rng.shuffle(vals)
            xs[f] = iter(vals)
        k2 += A.spearman([next(xs[u["family"]]) for u in us], y) >= res["association"]["spearman"] - 1e-12
    res["within_family_permutation_p_one_sided"] = (k2 + 1) / (draws + 1)
    # selection on the full pool
    chosen = pick(us, index)
    g = {u["config"]: u["criterion"][crit_key] for u in us}
    oracle = max(us, key=lambda u: g[u["config"]])
    h2 = [g[u["config"]] for u in us if u["prompt"] == CFG["fixed_rubric_prompt"]]
    res["selection"] = {"picked": chosen["config"], "G_picked": g[chosen["config"]], "oracle": oracle["config"],
                        "G_oracle": g[oracle["config"]], "regret": g[oracle["config"]] - g[chosen["config"]],
                        "G_random_mean": statistics.mean(g.values()),
                        "G_fixed_rubric_mean": statistics.mean(h2) if h2 else None, "n_fixed_rubric": len(h2),
                        "G_constant_judge": statistics.mean(u["criterion"]["G_P_constant"] for u in us)}
    within = []
    for f in fams:
        fu = [u for u in us if u["family"] == f]
        if len(fu) >= 2:
            within.append(max(g[u["config"]] for u in fu) - g[pick(fu, index)["config"]])
    res["selection"]["within_family_regret_mean"] = statistics.mean(within) if within else None
    res["selection"]["within_family_n"] = len(within)
    # two-level bootstrap: judge families, then evaluation tasks; G recomputed per draw from per-probe errors
    tasks = sorted({r["task"] for u in us for r in u["per_probe"]})
    by_task = {u["config"]: {} for u in us}
    for u in us:
        for r in u["per_probe"]:
            by_task[u["config"]].setdefault(r["task"], []).append(r)
    rho_d, reg_d, pickg_d = [], [], []
    for _ in range(draws):
        fs = [rng.choice(fams) for _ in fams]
        ts = [rng.choice(tasks) for _ in tasks]
        bu = [u for f in fs for u in us if u["family"] == f]
        gx = [u["index"][index] for u in bu]
        gy = [g_from(by_task[u["config"]], ts, err_key) for u in bu]
        if any(v is None for v in gy):
            continue
        if len(set(gx)) > 1 and len(set(gy)) > 1:
            rho_d.append(A.spearman(gx, gy))
        gg = {id(u): v for u, v in zip(bu, gy)}
        ch = max(bu, key=lambda u: (u["index"][index], [-ord(c) for c in u["config"]]))
        reg_d.append(max(gg.values()) - gg[id(ch)])
        pickg_d.append(gg[id(ch)])
    q = lambda v: [statistics.quantiles(v, n=40)[0], statistics.quantiles(v, n=40)[-1]] if len(v) > 40 else None
    res["association"]["spearman_ci95_family_task"] = q(rho_d)
    res["association"]["valid_draws"] = len(rho_d)
    res["selection"]["regret_ci95_family_task"] = q(reg_d)
    res["selection"]["G_picked_ci95_family_task"] = q(pickg_d)
    return res


def main():
    probes = load_targets()
    split, items_sha = load_split()
    e39 = load_e39_units()
    fit_index = fit_task_index(split)
    judges = judge_rows(probes, split)
    for j in judges:
        u = e39.get(j["config"])
        assert u is not None and u["split"] == j["split"] and u["family"] == j["family"], j["config"]
        j["index"] = {k: u["indices"].get(k) for k in ("C_ms_gold", "TI_var_trainnorm", "PTI_v0_frozen")}
        j["index"]["C_ms_gold_fit_tasks_only"] = fit_index[j["config"]]["value"]
        j["human_heldout_spearman"] = u["criteria"]["heldout"]["spearman"]
    llm = [j for j in judges if j["kind"] != "control"]
    rubric = ("D0", "H0", "H1", "H2", "R4")
    pools = {"test_llm": [j for j in llm if j["split"] == "test"],
             "train_val_llm": [j for j in llm if j["split"] in ("train", "val")], "all_llm": llm,
             "posthoc_test_rubric_prompts_only": [j for j in llm if j["split"] == "test" and j["prompt"] in rubric],
             "posthoc_all_rubric_prompts_only": [j for j in llm if j["prompt"] in rubric],
             "posthoc_all_with_controls": judges}
    analyses = {}
    for pname, pool in pools.items():
        for index in [CFG["primary_index"]] + CFG["secondary_indices"]:
            analyses[f"{pname}|{index}|G_P_fitted"] = analyse_pool(pool, index, CFG["seed"], CFG["bootstrap_draws"])
        analyses[f"{pname}|{CFG['primary_index']}|rank_auc"] = analyse_pool(
            pool, CFG["primary_index"], CFG["seed"], 2000, crit_key="rank_auc", err_key="auc")
        analyses[f"{pname}|{CFG['primary_index']}|G_P_raw"] = analyse_pool(
            pool, CFG["primary_index"], CFG["seed"], 2000, crit_key="G_P_raw", err_key="e_raw")
    hum = [(j["criterion"]["G_P_fitted"], j["human_heldout_spearman"]) for j in llm
           if j["criterion"]["G_P_fitted"] is not None and j["human_heldout_spearman"] is not None]
    counts = {f: {"probes": sum(p["family"] == f for p in probes), "y1": sum(p["y"] for p in probes if p["family"] == f)}
              for f in sorted({p["family"] for p in probes})}
    out = {
        "status": "R1_complete", "retrospective": True, "fresh_test": False,
        "config_sha256": sha(CFG_PATH), "script_sha256": sha(Path(__file__)), "items_sha256": items_sha,
        "probes": len(probes), "probe_counts_by_family": counts,
        "eval_tasks": sorted({t for t, s in split.items() if s in CFG["evaluation_task_splits"]}),
        "judges": [{k: j[k] for k in ("config", "family", "split", "kind", "prompt", "criterion", "index",
                                      "human_heldout_spearman")} for j in judges],
        "analyses": analyses,
        "prover_vs_human_criterion_all_llm": corr_triplet([a for a, _ in hum], [b for _, b in hum]),
        "new_model_calls": 0, "cost_usd": 0,
    }
    (EXP / "results").mkdir(exist_ok=True)
    (EXP / "results/r1_e42_target.json").write_text(json.dumps(out, indent=1) + "\n")
    prim = analyses[f"{CFG['primary_pool']}|{CFG['primary_index']}|{CFG['primary_criterion']}"]
    print(json.dumps({"probes": len(probes), "counts": counts, "primary": {k: prim[k] for k in prim if k != "units_detail"}},
                     indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
