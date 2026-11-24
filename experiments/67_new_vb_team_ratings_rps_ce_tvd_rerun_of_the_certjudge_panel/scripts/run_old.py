"""Experiment 67, old set: A1 raw table, A2 calibrated LOTO, A3 human ceiling, A4 learning curve, A5 why the old numbers looked odd.
CPU only, zero model calls. Run: ~/.venvs/sci/bin/python scripts/run_old.py"""
import sys, json, csv, itertools
from pathlib import Path
import numpy as np
from scipy import stats
sys.path.insert(0, str(Path(__file__).parent))
from lib import *

OUT = Path(__file__).resolve().parents[1] / "results"; OUT.mkdir(exist_ok=True)
B = 2000
eth1, eth2, vb = load_old_labels()
log = open(OUT / "old_log.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); log.write(s + "\n")

def rows_csv(name, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

A1, A2, A5 = [], [], []
curve, ceil = [], []
summary = {}
for fam, (dp, tp) in FAM.items():
    det, ti = load_detail(dp), load_ti(tp)
    judges = [j for j in ti if j in det]
    items_all = set().union(*[set(d) for d in det.values()])
    T_vb = lists(vb, items_all, 4)
    T_pp = lists([eth1, eth2], items_all, 2)
    for tname, T in (("H_vb", T_vb), ("H_paper", T_pp)):
        its = sorted(T); tasks = [k[0] for k in its]; rl = [T[k] for k in its]
        hm = np.array([np.mean(v) for v in rl]); H = [hum_dist(v) for v in rl]
        # constant forecast (LOTO marginal) reference
        for j in judges:
            s_sc = np.array([det[j][k][0] for k in its])
            D = [smooth(judge_dist(det[j][k][1]), 0.5) for k in its]
            M = np.array([scores(H[i], D[i]) for i in range(len(its))])
            def f(ii, M=M, s_sc=s_sc, hm=hm):
                ii = np.asarray(ii)
                return np.concatenate([M[ii].mean(0), [sp(s_sc[ii], hm[ii]), pe(s_sc[ii], hm[ii])]])
            pt, lo, hi = task_boot(tasks, f, B)
            r = dict(family=fam, target=tname, judge=j, TI_var=ti[j], n_items=len(its), n_tasks=len(set(tasks)))
            for n, nm in enumerate(["RPS", "CE", "TVD", "Spearman", "Pearson"]):
                r[nm] = pt[n]; r[nm + "_lo"] = lo[n]; r[nm + "_hi"] = hi[n]
            A1.append(r)
        # A2 calibrated LOTO (H_vb only: primary target)
        if tname == "H_vb":
            for j in judges:
                s_sc = np.array([det[j][k][0] for k in its])
                res = loto(its, tasks, s_sc, rl)
                for ref, other in (("CONST", "CE-fit"), ("CONST", "Pearson-fit"), ("Pearson-fit", "CE-fit")):
                    d = res[other] - res[ref]   # negative = other better
                    pt, lo, hi = task_boot(tasks, lambda ii, d=d: d[np.asarray(ii)].mean(0), B)
                    A2.append(dict(family=fam, judge=j, comparison=f"{other} minus {ref}", dRPS=pt[0], dRPS_lo=lo[0], dRPS_hi=hi[0], dCE=pt[1], dCE_lo=lo[1], dCE_hi=hi[1], dTVD=pt[2], dTVD_lo=lo[2], dTVD_hi=hi[2]))
                for k_, v in res.items():
                    pt, lo, hi = task_boot(tasks, lambda ii, v=v: v[np.asarray(ii)].mean(0), B)
                    A2.append(dict(family=fam, judge=j, comparison=f"heldout level {k_}", dRPS=pt[0], dRPS_lo=lo[0], dRPS_hi=hi[0], dCE=pt[1], dCE_lo=lo[1], dCE_hi=hi[1], dTVD=pt[2], dTVD_lo=lo[2], dTVD_hi=hi[2]))
    # A3 ceiling on H_vb
    its = sorted(T_vb); rl = [T_vb[k] for k in its]; tasks = [k[0] for k in its]
    rng = np.random.default_rng(0); rs = []
    for _ in range(500):
        a, b = [], []
        for v in rl:
            idx = rng.permutation(len(v)); h = len(v) // 2
            a.append(np.mean([v[i] for i in idx[:h]])); b.append(np.mean([v[i] for i in idx[h:2 * h]]))
        rs.append(sp(a, b))
    r_half = float(np.nanmean(rs)); r_sb = 2 * r_half / (1 + r_half)
    ceil.append(dict(family=fam, n_items=len(its), n_tasks=len(set(tasks)), ratings_per_item=float(np.mean([len(v) for v in rl])), split_half_spearman=r_half, spearman_brown=r_sb, ceiling_judge_human=float(np.sqrt(max(r_sb, 0)))))
    # A4 learning curve: headline judge on H_vb
    hj = HEADLINE[fam]; s_sc = np.array([det[hj][k][0] for k in its]); hm = np.array([np.mean(v) for v in rl])
    ut = sorted(set(tasks)); tix = {t: [i for i, x in enumerate(tasks) if x == t] for t in ut}
    rng = np.random.default_rng(1)
    for k in (4, 8, 12, 16, 20):
        if k > len(ut): continue
        vals = []
        for _ in range(500):
            pick = rng.choice(len(ut), k, replace=False); ii = [i for p in pick for i in tix[ut[p]]]
            vals.append(sp(s_sc[ii], hm[ii]))
        v = np.array(vals); v = v[~np.isnan(v)]
        curve.append(dict(family=fam, judge=hj, k_tasks=k, median=float(np.median(v)), p2_5=float(np.percentile(v, 2.5)), p97_5=float(np.percentile(v, 97.5)), width=float(np.percentile(v, 97.5) - np.percentile(v, 2.5)), sd=float(v.std())))
    # full-task point and task-bootstrap width
    pt, lo, hi = task_boot(tasks, lambda ii: sp(s_sc[ii], hm[ii]), B)
    curve.append(dict(family=fam, judge=hj, k_tasks=len(ut), median=float(pt), p2_5=float(lo), p97_5=float(hi), width=float(hi - lo), sd=float("nan")))
    # LOTO range of headline spearman
    loo = [sp(np.delete(s_sc, tix[t]), np.delete(hm, tix[t])) for t in ut]
    # A5 TI vs alignment, with task-bootstrap interval of the correlation
    tiv = np.array([ti[j] for j in judges])
    sc = {j: np.array([det[j][k][0] for k in its]) for j in judges}
    Dj = {j: [smooth(judge_dist(det[j][k][1]), 0.5) for k in its] for j in judges}
    Hh = [hum_dist(v) for v in rl]
    def align(ii, kind, j):
        ii = np.asarray(ii)
        if kind == "Spearman": return sp(sc[j][ii], hm[ii])
        m = np.mean([scores(Hh[i], Dj[j][i]) for i in ii], axis=0)
        return -m[{"RPS": 0, "CE": 1, "TVD": 2}[kind]]
    def perm_p(a, b):
        n = len(a); obs = sp(a, b)
        ra, rb = stats.rankdata(a), stats.rankdata(b)
        ra = (ra - ra.mean()) / np.linalg.norm(ra - ra.mean()); rb = (rb - rb.mean()) / np.linalg.norm(rb - rb.mean())
        perms = np.array(list(itertools.permutations(range(n))))
        return float(np.mean(np.abs(rb[perms] @ ra) >= abs(obs) - 1e-12))
    for kind in ("Spearman", "RPS", "CE", "TVD"):
        def f(ii, kind=kind):
            al = [align(ii, kind, j) for j in judges]
            return sp(tiv, al)
        pt, lo, hi = task_boot(tasks, f, 500)
        al0 = [align(range(len(its)), kind, j) for j in judges]
        loj = [sp(np.delete(tiv, q), np.delete(al0, q)) for q in range(len(judges))]
        A5.append(dict(family=fam, alignment=("judge Spearman" if kind == "Spearman" else f"-mean {kind}") + " vs H_vb", n_judges=len(judges), rho_TI=pt, lo=lo, hi=hi, perm_p=perm_p(tiv, al0), loo_min=float(np.nanmin(loj)), loo_max=float(np.nanmax(loj))))
    # tie share
    ties = float(np.mean([len(set(np.round(det[hj][k][0], 6) for k in its)) / len(its) for _ in [0]]))
    hs_task_loo = (float(np.nanmin(loo)), float(np.nanmax(loo)))
    summary[fam] = dict(headline_judge=hj, loto_spearman_range=hs_task_loo, distinct_score_share=ties)
    # paper labels vs participant mean on shared items
    sh = [k for k in T_pp if k in T_vb]
    summary[fam]["paper_vs_vb_spearman"] = sp([np.mean(T_pp[k]) for k in sh], [np.mean(T_vb[k]) for k in sh]); summary[fam]["n_shared"] = len(sh)
    # share of ratings at each level in H_vb
    summary[fam]["vb_rating_dist"] = (counts([x for v in rl for x in v]) / sum(len(v) for v in rl)).round(3).tolist()

rows_csv("old_A1_raw_per_judge.csv", A1); rows_csv("old_A2_calibrated_loto.csv", A2)
rows_csv("old_A3_ceiling.csv", ceil); rows_csv("old_A4_learning_curve.csv", curve); rows_csv("old_A5_TI_vs_alignment.csv", A5)
json.dump(summary, open(OUT / "old_summary.json", "w"), indent=1)
P("A3 ceiling"); [P(r) for r in ceil]
P("A4 curve"); [P({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}) for r in curve]
P("A5"); [P({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}) for r in A5]
P("summary", json.dumps(summary))
