#!/usr/bin/env python3
"""TLDR: Stage A of the judge-selection experiment: does a label-free score pick the open-weight judge unit that matches humans?
Zero model calls, CPU only: reads results/units_90.json (90 open-weight judge units of experiments 59/60: config = model|prompt,
`criterion` = Spearman of the unit's median item score with the 3-expert mean over 45 val+test items, plus the label-free scores
C_ms_gold, F1_probe, F2_item) and compares selection rules (three label-free scores, random, oracle) by human rho and regret.
Usage: python3 stage_a_selection.py [--units results/units_90.json] [--retest results/units_seed1_replicates.json] [--out results] [--draws 10000]
Needs numpy and scipy (~/.venvs/e59/bin/python has them). Writes ANALYSIS.json and RESULTS_stage_a.md."""
import argparse, json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

SEED = 62
RULES = ("C_ms_gold", "F2_item", "F1_probe")
LABEL = {"C_ms_gold": "C_ms_gold (frozen label-free gold-probe index)", "F2_item": "F2_item (agreement with frontier-judge consensus, no human labels)",
         "F1_probe": "F1_probe (probe-cell agreement with frontier judge)"}


def rho(x, y):
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(spearmanr(x, y)[0])


def argmax_first(v):
    return int(np.argmax(v))          # ties: first unit in sorted config order


def load(path):
    U = sorted(json.loads(Path(path).read_text()), key=lambda u: u["config"])
    for u in U:
        u["prompt"] = u["config"].split("|")[1]
    return U


def pool_arrays(U, rule):
    sel = [u for u in U if u.get(rule) is not None and u["criterion"] is not None]
    return sel, np.array([u[rule] for u in sel]), np.array([u["criterion"] for u in sel]), np.array([u["family"] for u in sel])


def global_pick(U, rule):
    sel, s, y, f = pool_arrays(U, rule)
    i = argmax_first(s)
    return {"n_units": len(sel), "pick": sel[i]["config"], "pick_rho": float(y[i]), "pick_ci": sel[i].get("criterion_ci"), "oracle": sel[i]["config"] if y[i] == y.max() else sel[int(np.argmax(y))]["config"],
            "oracle_rho": float(y.max()), "regret": float(y.max() - y[i]), "random_mean_rho": float(y.mean()), "rank_of_pick_by_human": int((y > y[i]).sum() + 1),
            "top3_mean_rho": float(y[np.argsort(-s)[:3]].mean())}


def pooled_rho(U, rule, draws, rng):
    sel, s, y, f = pool_arrays(U, rule)
    fams = sorted(set(f)); idx = {m: np.where(f == m)[0] for m in fams}
    bs = []
    for _ in range(draws):
        pick = rng.integers(0, len(fams), len(fams))
        ii = np.concatenate([idx[fams[j]] for j in pick])
        v = rho(s[ii], y[ii])
        if v == v:
            bs.append(v)
    return {"n_units": len(sel), "n_families": len(fams), "spearman": rho(s, y), "family_bootstrap_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def lofo_global(U, rule):
    sel, s, y, f = pool_arrays(U, rule)
    out = {}
    for m in sorted(set(f)):
        k = f != m
        i = np.where(k)[0][argmax_first(s[k])]
        out[m] = {"pick": sel[i]["config"], "pick_rho": float(y[i]), "oracle_rho_remaining": float(y[k].max())}
    v = np.array([o["pick_rho"] for o in out.values()])
    return {"per_family_dropped": out, "min": float(v.min()), "max": float(v.max()), "mean": float(v.mean()), "distinct_picks": sorted({o["pick"] for o in out.values()})}


def prompt_transfer(U, rule):
    """Leave-one-family-out prompt selection: choose the prompt with the best mean label-free score over the OTHER families,
    apply it to the held-out family, compare with that family's best and its average prompt."""
    sel, s, y, f = pool_arrays(U, rule)
    p = np.array([u["prompt"] for u in sel])
    rows = {}
    for m in sorted(set(f)):
        k = f != m
        prompts = sorted(set(p[k]))
        mean_s = {q: float(s[k & (p == q)].mean()) for q in prompts}
        mine = {u["prompt"]: u["criterion"] for u in sel if u["family"] == m}
        cand = [q for q in prompts if q in mine]
        if not cand:
            continue
        q = max(cand, key=lambda z: (mean_s[z], z))     # best-scoring prompt that the held-out family also has
        rows[m] = {"prompt": q, "pick_rho": float(mine[q]), "oracle_rho": float(max(mine.values())), "random_rho": float(np.mean(list(mine.values())))}
    return rows


def within_family(U, rule, draws, rng):
    sel, s, y, f = pool_arrays(U, rule)
    fams = [m for m in sorted(set(f)) if (f == m).sum() >= 3]
    rows = {}
    for m in fams:
        k = f == m
        sm, ym = s[k], y[k]
        rows[m] = {"n": int(k.sum()), "pick_rho": float(ym[argmax_first(sm)]), "oracle_rho": float(ym.max()), "random_rho": float(ym.mean()),
                   "rho_score_vs_human": rho(sm, ym)}
    P = np.array([r["pick_rho"] for r in rows.values()]); O = np.array([r["oracle_rho"] for r in rows.values()]); R = np.array([r["random_rho"] for r in rows.values()])
    # permutation null: shuffle the scores inside each family
    null = []
    for _ in range(draws):
        t = [ym[argmax_first(rng.permutation(sm))] for sm, ym in ((s[f == m], y[f == m]) for m in fams)]
        null.append(np.mean(t))
    null = np.array(null)
    bs_gain, bs_regret = [], []
    for _ in range(draws):
        j = rng.integers(0, len(fams), len(fams))
        bs_gain.append(float(np.mean(P[j] - R[j]))); bs_regret.append(float(np.mean(O[j] - P[j])))
    return {"families": rows, "n_families": len(fams), "mean_pick_rho": float(P.mean()), "mean_oracle_rho": float(O.mean()), "mean_random_rho": float(R.mean()),
            "mean_regret": float((O - P).mean()), "regret_ci95": [float(np.percentile(bs_regret, 2.5)), float(np.percentile(bs_regret, 97.5))],
            "gain_over_random": float((P - R).mean()), "gain_ci95": [float(np.percentile(bs_gain, 2.5)), float(np.percentile(bs_gain, 97.5))],
            "perm_null_mean": float(null.mean()), "perm_p_pick_ge_obs": float((1 + (null >= P.mean() - 1e-12).sum()) / (1 + draws)),
            "families_where_pick_is_oracle": int(sum(r["pick_rho"] == r["oracle_rho"] for r in rows.values()))}


def paired_rule_diff(U, a, b, draws, rng):
    """Family-clustered paired difference of mean within-family pick rho between two rules, on the units that have both scores."""
    V = [u for u in U if all(u.get(r) is not None for r in (a, b)) and u["criterion"] is not None]
    fams = sorted({u["family"] for u in V}); d = []
    for m in fams:
        vm = [u for u in V if u["family"] == m]
        if len(vm) < 3:
            continue
        ya = vm[argmax_first([u[a] for u in vm])]["criterion"]; yb = vm[argmax_first([u[b] for u in vm])]["criterion"]
        d.append(ya - yb)
    d = np.array(d)
    bs = [float(np.mean(d[rng.integers(0, len(d), len(d))])) for _ in range(draws)]
    return {"a": a, "b": b, "n_families": len(d), "mean_diff_a_minus_b": float(d.mean()), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def retest(U, R, rule="C_ms_gold"):
    """Seed retest: pick inside a family with the seed-0 score, evaluate on the seed-1 replicate's human rho."""
    s0 = {u["config"]: u for u in U}
    rows = {}
    for m in sorted({r["family"].split("@")[0] for r in R}):
        reps = {r["config"].split("@")[0] + "|" + r["config"].split("|")[1]: r for r in R if r["family"].split("@")[0] == m}
        cfgs = [c for c in reps if c in s0 and s0[c].get(rule) is not None]
        if len(cfgs) < 3:
            continue
        i = max(cfgs, key=lambda c: (s0[c][rule], c))
        rows[m] = {"pick": i, "pick_rho_seed0": s0[i]["criterion"], "pick_rho_seed1": reps[i]["criterion"], "best_seed1_rho": max(reps[c]["criterion"] for c in cfgs),
                   "mean_seed1_rho": float(np.mean([reps[c]["criterion"] for c in cfgs]))}
    return rows


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=Path, default=here.parent / "results/units_90.json")
    ap.add_argument("--retest", type=Path, default=here.parent / "results/units_seed1_replicates.json")
    ap.add_argument("--out", type=Path, default=here.parent / "results")
    ap.add_argument("--draws", type=int, default=10000)
    a = ap.parse_args()
    U = load(a.units); Rp = json.loads(a.retest.read_text())
    common = [u for u in U if all(u.get(r) is not None for r in RULES) and u["criterion"] is not None]
    rng = np.random.default_rng(SEED)
    R = {"experiment": 62, "n_units_with_criterion": len(U), "n_common_units": len(common), "draws": a.draws, "rules": {}}
    for r in RULES:
        R["rules"][r] = {"pooled": pooled_rho(U, r, a.draws, rng), "global_pick": global_pick(U, r), "global_pick_common_pool": global_pick(common, r),
                         "lofo_global": lofo_global(U, r), "lofo_prompt_transfer": prompt_transfer(U, r), "within_family": within_family(U, r, a.draws, rng)}
        pt = R["rules"][r]["lofo_prompt_transfer"]
        P = np.array([v["pick_rho"] for v in pt.values()]); O = np.array([v["oracle_rho"] for v in pt.values()]); Rr = np.array([v["random_rho"] for v in pt.values()])
        bs = [float(np.mean((P - Rr)[j])) for j in (rng.integers(0, len(P), len(P)) for _ in range(a.draws))]
        R["rules"][r]["prompt_transfer_summary"] = {"n_families": len(P), "mean_pick_rho": float(P.mean()), "mean_oracle_rho": float(O.mean()), "mean_random_rho": float(Rr.mean()),
                                                    "mean_regret": float((O - P).mean()), "gain_over_random": float((P - Rr).mean()), "gain_ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    y = np.array([u["criterion"] for u in U])
    R["oracle_global"] = {"pick": U[int(np.argmax(y))]["config"], "rho": float(y.max())}
    R["random_global_mean"] = float(y.mean())
    R["paired_rule_differences"] = [paired_rule_diff(U, "C_ms_gold", "F2_item", a.draws, rng), paired_rule_diff(U, "C_ms_gold", "F1_probe", a.draws, rng), paired_rule_diff(U, "F2_item", "F1_probe", a.draws, rng)]
    R["retest_seed1"] = {r: retest(U, Rp, r) for r in RULES}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "ANALYSIS.json").write_text(json.dumps(R, indent=1))
    write_report(a.out / "RESULTS_stage_a.md", R)
    print("ok")


def f3(v):
    return "n/a" if v is None or v != v else f"{v:.3f}"


def ci(c):
    return "n/a" if not c else f"[{c[0]:.2f}, {c[1]:.2f}]"


def write_report(path, R):
    L = ["# Experiment 62 Stage A: does a label-free score pick the judge that matches humans? (zero model calls)", "",
         "Caveat first: human ratings are 75 Claude 3.7 Sonnet items only; each unit's human rho is on the 45 val+test items (CI about +/-0.3 per unit); there are no human ratings of frontier-judge outputs until 2026-11-06.", "",
         "Harness for every row: single-call LLM, no tools (open-weight judge units of experiments 59/60: 10 model families x up to 9 prompts, seed 58, median of 3 samples). N = judge units; 'family' = model. Human rho = Spearman of the unit's item scores with the 3-expert mean on 45 items. Regret = best unit's human rho minus the picked unit's. CIs resample model families (the unit of independence).", "",
         f"Units: {R['n_units_with_criterion']} with a human rho; {R['n_common_units']} with all three label-free scores (the 'common pool', used for the headline table). Scores: C_ms_gold = frozen label-free gold-probe index; F2_item = agreement with the frontier-judge consensus on the 75 items (no human labels); F1_probe = probe-cell agreement with the frontier judge.", ""]
    L += ["## Bar (pre-registered in the design Doc)", "", "Success = the picked judge reaches human rho >= 0.75, CI above 0, and clearly beats 0.60 (best label-free single unit of experiment 60). Null = no better than 0.60: keep stacking open-weight judges.", ""]
    L += ["## Table 1. Global pick: one unit chosen from the whole pool (common pool)", "", "| rule | N units | picked unit | picked human rho [95% CI] | regret | oracle rho | random-pick mean rho | rank of pick by human rho | meets 0.75 | beats 0.60 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in RULES:
        g = R["rules"][r]["global_pick_common_pool"]
        L.append(f"| {r} | {g['n_units']} | {g['pick']} | {f3(g['pick_rho'])} {ci([g['pick_ci']['lo'], g['pick_ci']['hi']]) if g['pick_ci'] else '(CI not stored)'} | {f3(g['regret'])} | {f3(g['oracle_rho'])} ({g['oracle']}) | {f3(g['random_mean_rho'])} | {g['rank_of_pick_by_human']} | {'yes' if g['pick_rho'] >= .75 else 'no'} | {'yes' if g['pick_rho'] > .60 else 'no'} |")
    L += ["", f"Oracle over all {R['n_units_with_criterion']} units: {R['oracle_global']['pick']} {f3(R['oracle_global']['rho'])}; random pick expectation {f3(R['random_global_mean'])}.", ""]
    L += ["## Table 2. Does the score rank units like humans? (pooled over units, family-bootstrap CI)", "", "| rule | N units | N families | Spearman(score, human rho) | 95% CI |", "|---|---|---|---|---|"]
    for r in RULES:
        p = R["rules"][r]["pooled"]
        L.append(f"| {r} | {p['n_units']} | {p['n_families']} | {f3(p['spearman'])} | {ci(p['family_bootstrap_ci95'])} |")
    L += ["", "## Table 3. Leave-one-family-out, global pick (drop a model family, pick among the rest)", "", "| rule | mean human rho of pick | min | max | distinct picks |", "|---|---|---|---|---|"]
    for r in RULES:
        g = R["rules"][r]["lofo_global"]
        L.append(f"| {r} | {f3(g['mean'])} | {f3(g['min'])} | {f3(g['max'])} | {', '.join(g['distinct_picks'])} |")
    L += ["", "## Table 4. Leave-one-family-out prompt transfer (best prompt by mean score over the OTHER families, applied to the held-out family)", "", "| rule | N families | pick human rho (mean) | oracle prompt | random prompt | regret | gain over random [95% CI] |", "|---|---|---|---|---|---|---|"]
    for r in RULES:
        g = R["rules"][r]["prompt_transfer_summary"]
        L.append(f"| {r} | {g['n_families']} | {f3(g['mean_pick_rho'])} | {f3(g['mean_oracle_rho'])} | {f3(g['mean_random_rho'])} | {f3(g['mean_regret'])} | {f3(g['gain_over_random'])} {ci(g['gain_ci95'])} |")
    L += ["", "## Table 5. Within-family pick (the practical case: which prompt for this model), versus random and oracle", "", "| rule | N families | mean pick rho | mean oracle rho | mean random rho | mean regret [95% CI] | gain over random [95% CI] | permutation p (scores shuffled in family) | families where pick = oracle |", "|---|---|---|---|---|---|---|---|---|"]
    for r in RULES:
        w = R["rules"][r]["within_family"]
        L.append(f"| {r} | {w['n_families']} | {f3(w['mean_pick_rho'])} | {f3(w['mean_oracle_rho'])} | {f3(w['mean_random_rho'])} | {f3(w['mean_regret'])} {ci(w['regret_ci95'])} | {f3(w['gain_over_random'])} {ci(w['gain_ci95'])} | {w['perm_p_pick_ge_obs']:.4f} | {w['families_where_pick_is_oracle']}/{w['n_families']} |")
    L += ["", "Per family (C_ms_gold): " + "; ".join(f"{m} pick {f3(v['pick_rho'])} / oracle {f3(v['oracle_rho'])} / random {f3(v['random_rho'])}" for m, v in R["rules"]["C_ms_gold"]["within_family"]["families"].items()), ""]
    L += ["## Table 6. Rule vs rule (within-family pick, family-clustered paired difference)", "", "| a | b | N families | mean (a - b) human rho | 95% CI |", "|---|---|---|---|---|"]
    for d in R["paired_rule_differences"]:
        L.append(f"| {d['a']} | {d['b']} | {d['n_families']} | {f3(d['mean_diff_a_minus_b'])} | {ci(d['ci95'])} |")
    L += ["", "## Table 7. Seed retest: pick with the seed-58 score, evaluate on the seed-1058 replicate (families with replicates only)", "", "| rule | family | picked unit | rho seed 58 | rho seed 1058 | best unit rho (seed 1058) | mean unit rho (seed 1058) |", "|---|---|---|---|---|---|---|"]
    for r in RULES:
        for m, v in R["retest_seed1"][r].items():
            L.append(f"| {r} | {m} | {v['pick']} | {f3(v['pick_rho_seed0'])} | {f3(v['pick_rho_seed1'])} | {f3(v['best_seed1_rho'])} | {f3(v['mean_seed1_rho'])} |")
    path.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
