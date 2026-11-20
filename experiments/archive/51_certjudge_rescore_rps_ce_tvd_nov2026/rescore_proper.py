#!/usr/bin/env python3
"""CPU-only, zero model calls. Re-score CertJudge validation judges with RPS/CE/TVD against human rating
distributions, from saved cert-judge files. Metric definitions copied from
trustworthy-theorem-judges experiments/22_*/scripts/evaluate_5metrics.py (rps_components, ce_per_artifact,
tvd_per_artifact, laplace_smooth alpha=0.5, 6 categories 0..5)."""
import csv, json, itertools, sys, platform, math
from pathlib import Path
import numpy as np, scipy
from scipy import stats

CJ = Path(__file__).resolve().parents[2]
VB04 = CJ / "archive/04_veribench_validation"
VB13 = CJ / "archive/13_qwen_replication_exp16_exp19"
HL = CJ / "human_labels"
OUT = Path(__file__).resolve().parent
ALIAS = {"1_unsafeMultiply_safe.lean": "0_unsafeMultiply_safe.lean"}

FAM = {
 "Codex": (VB04/"results_exp16_final_robust_r9_median/detail_rows.csv", VB04/"results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv"),
 "Claude Opus": (VB04/"results_exp16_opus47_r3_median/detail_rows.csv", VB04/"results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv"),
 "Qwen3-Coder": (VB13/"results/exp16_qwen_r3_median/detail_rows.csv", VB04/"results_exp28_varaware_qwen_avg/judge_trust_vector.csv"),
}

def read_labels(p, rename=False):
    out = {}
    for r in csv.DictReader(open(p), delimiter="\t"):
        g, c, s = r["gold_file"].strip(), r["candidate_file"].strip(), r["human_score_0_5"]
        if not g or not c or s in ("", None): continue
        if rename and g in ALIAS:
            g2 = ALIAS[g]; c = g2[:-5] + c[len(g[:-5]):] if c.startswith(g[:-5]) else c; g = g2
        out[(g, c)] = float(s)
    return out

# ---- human rating lists
eth1 = read_labels(VB04/"data/ethan_human_scores_20260425.tsv")      # paper pass1
eth2 = read_labels(VB04/"data/ethan_human_scores_ORIGINAL.tsv")      # paper pass2
vb = [read_labels(HL/f, rename=True) for f in ["participant1_data_correct_prompt.tsv","participant2_data_pass_1.tsv","participant3_data_pass_1.tsv","participant4_data_pass_1.tsv","participant5_data_pass_1.tsv"]]
def lists(dicts, items, need_all):
    out = {}
    for it in items:
        v = [d[it] for d in dicts if it in d]
        if (need_all and len(v) == len(dicts)) or (not need_all and len(v) >= 1):
            out[it] = v
    return out

def isint(v): return all(abs(x - round(x)) < 1e-9 and 0 <= x <= 5 for x in v)

def counts(vals):
    c = np.zeros(6)
    for v in vals: c[int(round(v))] += 1
    return c

def smooth(c, a): q = c + a; return q / q.sum()
def rps(P, Q):
    pc, qc = np.cumsum(P)[:5], np.cumsum(Q)[:5]
    return float(np.mean((qc - pc) ** 2 + pc * (1 - pc)))
def ce(P, Q):
    m = P > 0
    return float("inf") if np.any(Q[m] <= 0) else float(-np.sum(P[m] * np.log(Q[m])))
def tvd(P, Q): return float(0.5 * np.sum(np.abs(Q - P)))

def judge_dist(repeats):
    # bin each repeat score s in [0,1] to category floor(5s+0.5) in 0..5 (nearest of 0,.2,...,1)
    return counts([min(5, max(0, math.floor(5 * s + 0.5 + 1e-12))) for s in repeats])

def load_detail(path):
    out = {}
    for r in csv.DictReader(open(path)):
        if r["row_type"] != "human_eval_union": continue
        g, c = r["item_key"].split("::", 1)
        out.setdefault(r["judge_id"], {})[(g, c)] = (float(r["score_mean"]), json.loads(r["repeat_scores"]))
    return out

def load_ti(path):
    return {r["judge_id"]: float(r["TI_variance_aware"]) for r in csv.DictReader(open(path))}

def spearman(a, b):
    return float(stats.spearmanr(a, b)[0])
PERMS = {}
def perm_p(a, b):
    """exact two-sided permutation p over all n! orderings (n=8 -> 40320)"""
    n = len(a)
    if n not in PERMS: PERMS[n] = np.array(list(itertools.permutations(range(n))))
    obs = spearman(a, b)
    ra, rb = stats.rankdata(a), stats.rankdata(b)
    ra = (ra - ra.mean()) / np.linalg.norm(ra - ra.mean()); rb = rb - rb.mean()
    rb = rb / np.linalg.norm(rb)
    r = rb[PERMS[n]] @ ra
    return float(np.mean(np.abs(r) >= abs(obs) - 1e-12))

res_rows, per_judge = [], []
print("python", sys.version.split()[0], "scipy", scipy.__version__, "numpy", np.__version__, platform.platform())
for fam, (dp, tp) in FAM.items():
    det, ti = load_detail(dp), load_ti(tp)
    judges = [j for j in ti if j in det]
    items_all = set().union(*[set(d) for d in det.values()])
    # human target sets
    pa = lists([eth1, eth2], items_all, True)            # paper's own two old-prompt passes, one annotator
    pavg = {k: (eth1[k] + eth2[k]) / 2 for k in pa}      # paper avg label (scalar) for reproduction
    pb = lists(vb, items_all, True)                      # 5 VeriBench participants
    pc = lists(vb, items_all, False)                     # VeriBench participants 1-5, all ratings available (4-5 per item; p3 rated only 44 of 75)
    targets = {"H_paper_2passes(n_ratings=2, one annotator)": pa, "H_vb_5participants(all 5 rated)": pb, "H_vb_participants_available(4-5 ratings)": pc}
    ti_v = np.array([ti[j] for j in judges])
    # (0) reproduction of scalar human Spearman view (avg labels)
    hs = []
    for j in judges:
        its = [k for k in pavg if k in det[j]]
        hs.append(spearman([det[j][k][0] for k in its], [pavg[k] for k in its]))
    r0 = spearman(ti_v, hs)
    res_rows.append(dict(family=fam, target="paper avg labels (scalar)", alignment="judge Spearman(score, human)", n_judges=len(judges), n_items=len(pavg), rho_TI_vs_alignment=r0, perm_p=perm_p(ti_v, hs)))
    for tname, T in targets.items():
        assert all(isint(v) for v in T.values())
        its = sorted(T)
        for alpha in (0.5, 0.05):
            metr = {"RPS": {}, "CE": {}, "TVD": {}}
            for j in judges:
                R = C = Tv = 0.0
                for k in its:
                    P = counts(T[k]); P = P / P.sum()
                    Q = smooth(judge_dist(det[j][k][1]), alpha)
                    R += rps(P, Q); C += ce(P, Q); Tv += tvd(P, Q)
                metr["RPS"][j], metr["CE"][j], metr["TVD"][j] = R/len(its), C/len(its), Tv/len(its)
                per_judge.append(dict(family=fam, target=tname, alpha=alpha, judge=j, TI=ti[j], n_items=len(its), RPS=R/len(its), CE=C/len(its), TVD=Tv/len(its)))
            for m, d in metr.items():
                if alpha == 0.05 and m != "CE": continue
                al = -np.array([d[j] for j in judges])   # higher = better aligned
                res_rows.append(dict(family=fam, target=tname, alignment=f"-mean {m} (Laplace alpha={alpha})", n_judges=len(judges), n_items=len(its), rho_TI_vs_alignment=spearman(ti_v, al), perm_p=perm_p(ti_v, al)))
        # scalar Spearman of judge score vs human mean on this item set, for comparison
        hs2 = []
        for j in judges:
            hs2.append(spearman([det[j][k][0] for k in its], [np.mean(T[k]) for k in its]))
        res_rows.append(dict(family=fam, target=tname, alignment="judge Spearman(score, mean human)", n_judges=len(judges), n_items=len(its), rho_TI_vs_alignment=spearman(ti_v, hs2), perm_p=perm_p(ti_v, hs2)))
json.dump(res_rows, open(OUT/"rescore_proper_results.json", "w"), indent=1)
for name, rows in (("rescore_proper_results.csv", res_rows), ("rescore_proper_per_judge.csv", per_judge)):
    w = csv.DictWriter(open(OUT/name, "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in res_rows: print(f'{r["family"]:12s} {r["target"][:42]:42s} {r["alignment"]:40s} nj={r["n_judges"]} ni={r["n_items"]} rho={r["rho_TI_vs_alignment"]:+.3f} p={r["perm_p"]:.3f}')
