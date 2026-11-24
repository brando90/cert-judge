"""Experiment 67, new set: A3 (new-set human agreement), A6 (counts old/new/pooled, judge-free baselines on the 100 new files, pooled edit-distance baseline).
CPU only, zero model calls. Reads inputs_local/new_ratings/<rater id>.tsv (raters' Sheets as TSV, not committed). Only rater ids are written out.
Run: ~/.venvs/sci/bin/python scripts/run_new.py --packet <.../rating_task_packet/main_rating_task>"""
import sys, csv, json, argparse, re
from pathlib import Path
import numpy as np
from rapidfuzz.distance import Levenshtein
sys.path.insert(0, str(Path(__file__).parent))
from lib import *

ap = argparse.ArgumentParser(); ap.add_argument("--packet", required=True); args = ap.parse_args()
HERE = Path(__file__).resolve().parents[1]; OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
B = 2000
log = open(OUT / "new_log.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); log.write(s + "\n")

# ---- read returned ratings (final_score_0_5 filled only)
R = {}  # (task_folder, candidate_file) -> {rater: score}
per_rater = {}
fl = sorted((HERE / "inputs_local/new_ratings").glob("*.tsv"))
# item_id -> (task_folder, candidate_file) from the rows every Sheet shares (a rater's note can land in the candidate_file cell of one row; item_id is the key)
ITEM = {}
for f in fl:
    for r in csv.DictReader(open(f), delimiter="\t"):
        if r["candidate_file"].endswith(".lean"): ITEM[r["item_id"]] = (r["task_folder"], r["candidate_file"])
for f in fl:
    for r in csv.DictReader(open(f), delimiter="\t"):
        s = (r.get("final_score_0_5") or "").strip()
        if not s: continue
        try: v = float(s)
        except ValueError: continue
        if not (0 <= v <= 5) or abs(v - round(v)) > 1e-9: continue
        key = ITEM[r["item_id"]]
        R.setdefault(key, {})[r["rater_id"]] = int(round(v)); per_rater[r["rater_id"]] = per_rater.get(r["rater_id"], 0) + 1
P("returned ratings per rater id:", dict(sorted(per_rater.items(), key=lambda x: -x[1])), "total", sum(per_rater.values()))
files = sorted(R); tasks = [k[0] for k in files]
P("files with at least one rating:", len(files), "tasks:", len(set(tasks)))

# ---- A3 new: agreement of the two complete raters
a, b = "T05", "T08"
both = [k for k in files if a in R[k] and b in R[k]]
x = np.array([R[k][a] for k in both]); y = np.array([R[k][b] for k in both])
def qwk(x, y, K=6):
    O = np.zeros((K, K))
    for i, j in zip(x, y): O[i, j] += 1
    E = np.outer(O.sum(1), O.sum(0)) / O.sum(); W = np.array([[(i - j) ** 2 for j in range(K)] for i in range(K)]) / (K - 1) ** 2
    return float(1 - (W * O).sum() / (W * E).sum())
bt = [k[0] for k in both]
pt, lo, hi = task_boot(bt, lambda ii: sp(x[ii], y[ii]), B)
r_sp = float(pt)
agree = dict(n_files=len(both), n_tasks=len(set(bt)), spearman=r_sp, spearman_lo=float(lo), spearman_hi=float(hi), exact=float(np.mean(x == y)), within1=float(np.mean(np.abs(x - y) <= 1)), qwk=qwk(x, y), spearman_brown_2raters=2 * r_sp / (1 + r_sp), ceiling_judge_mean_of_2=float(np.sqrt(max(2 * r_sp / (1 + r_sp), 0))))
allr = [v for k in files for v in R[k].values()]
dist = (counts(allr) / len(allr)).round(3).tolist()
agree.update(rating_dist_0to5=dist, share_5=dist[5], share_4_5=dist[4] + dist[5], ratings_per_file_mean=float(np.mean([len(R[k]) for k in files])))
P("A3 new:", json.dumps(agree))

# ---- A6 judge-free baselines on the 100 new files (mean over returned ratings per file)
def sim(k):
    t, c = k; base = Path(args.packet) / t
    g = (base / "gold_lean/reference.lean").read_text(); cand = (base / "agent_lean" / Path(c).name).read_text()
    return Levenshtein.normalized_similarity(cand, g)
ed = np.array([sim(k) for k in files]); rl = [list(R[k].values()) for k in files]
hm = np.array([np.mean(v) for v in rl]); rng = np.random.default_rng(0); rnd = rng.random(len(files))
base = {}
for name, s in (("edit-distance similarity (judge-free)", ed), ("random score (seed 0)", rnd)):
    res = loto(files, tasks, s, rl)
    pt, lo, hi = task_boot(tasks, lambda ii: sp(s[ii], hm[ii]), B)
    ppt, plo, phi = task_boot(tasks, lambda ii: pe(s[ii], hm[ii]), B)
    row = dict(score=name, n_files=len(files), n_tasks=len(set(tasks)), spearman=float(pt), spearman_lo=float(lo), spearman_hi=float(hi), spearman_width=float(hi - lo), pearson=float(ppt), pearson_lo=float(plo), pearson_hi=float(phi))
    for kname, v in res.items():
        m, mlo, mhi = task_boot(tasks, lambda ii, v=v: v[np.asarray(ii)].mean(0), B)
        for n, mn in enumerate(["RPS", "CE", "TVD"]):
            row[f"{kname}_{mn}"] = float(m[n]); row[f"{kname}_{mn}_lo"] = float(mlo[n]); row[f"{kname}_{mn}_hi"] = float(mhi[n])
    base[name] = row
    P("A6", json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}))
# learning curve for the judge-free baseline over task counts on the new files
ut = sorted(set(tasks)); tix = {t: [i for i, q in enumerate(tasks) if q == t] for t in ut}
rng = np.random.default_rng(2); curve = []
for k in (5, 10, 15, 20, len(ut)):
    vals = []
    for _ in range(500 if k < len(ut) else 1):
        ii = [i for p in rng.choice(len(ut), k, replace=False) for i in tix[ut[p]]]
        vals.append(sp(ed[ii], hm[ii]))
    v = np.array(vals); v = v[~np.isnan(v)]
    curve.append(dict(k_tasks=k, median=float(np.median(v)), p2_5=float(np.percentile(v, 2.5)), p97_5=float(np.percentile(v, 97.5)), width=float(np.percentile(v, 97.5) - np.percentile(v, 2.5))))
P("A6 new-set edit-distance learning curve", curve)

# ---- pooled counts and pooled edit-distance baseline (old H_vb items + new files), task bootstrap over the union of tasks
eth1, eth2, vb = load_old_labels()
det = load_detail(FAM["Codex"][0]); items_all = set(det[next(iter(det))])
T_vb = lists(vb, items_all, 4); old_items = sorted(T_vb)
old_ed = np.array([det["editdist_e1"][k][0] for k in old_items]); old_hm = np.array([np.mean(T_vb[k]) for k in old_items]); old_tasks = ["old:" + k[0] for k in old_items]
new_tasks = ["new:" + t for t in tasks]
cnt = [dict(set="old (VeriBench participants, corrected prompt)", tasks=len(set(old_tasks)), artifacts=len(old_items), ratings=sum(len(T_vb[k]) for k in old_items), ratings_per_artifact=float(np.mean([len(T_vb[k]) for k in old_items]))),
       dict(set="new (VB-team native files, returned by 11-24-2026 10:05 PST)", tasks=len(set(tasks)), artifacts=len(files), ratings=len(allr), ratings_per_artifact=float(np.mean([len(R[k]) for k in files]))),
       dict(set="new, complete raters only (T05 and T08)", tasks=len(set(bt)), artifacts=len(both), ratings=2 * len(both), ratings_per_artifact=2.0)]
cnt.append(dict(set="pooled old + new", tasks=cnt[0]["tasks"] + cnt[1]["tasks"], artifacts=cnt[0]["artifacts"] + cnt[1]["artifacts"], ratings=cnt[0]["ratings"] + cnt[1]["ratings"], ratings_per_artifact=(cnt[0]["ratings"] + cnt[1]["ratings"]) / (cnt[0]["artifacts"] + cnt[1]["artifacts"])))
P("counts", json.dumps(cnt))
ped = np.concatenate([old_ed, ed]); phm = np.concatenate([old_hm, hm]); ptasks = old_tasks + new_tasks
pool = {}
for name, s, h, t in (("old only", old_ed, old_hm, old_tasks), ("new only", ed, hm, new_tasks), ("pooled", ped, phm, ptasks)):
    pt, lo, hi = task_boot(t, lambda ii: sp(s[ii], h[ii]), B)
    pool[name] = dict(n_tasks=len(set(t)), n_artifacts=len(t), spearman=float(pt), lo=float(lo), hi=float(hi), width=float(hi - lo))
    P("pooled editdist", name, json.dumps(pool[name]))
# pooled learning curve on the union of tasks
ut2 = sorted(set(ptasks)); tix2 = {t: [i for i, q in enumerate(ptasks) if q == t] for t in ut2}
rng = np.random.default_rng(3); pc = []
for k in (10, 20, 30, 40, len(ut2)):
    vals = []
    for _ in range(500 if k < len(ut2) else 1):
        ii = [i for p in rng.choice(len(ut2), k, replace=False) for i in tix2[ut2[p]]]
        vals.append(sp(ped[ii], phm[ii]))
    v = np.array(vals); v = v[~np.isnan(v)]
    pc.append(dict(k_tasks=k, median=float(np.median(v)), p2_5=float(np.percentile(v, 2.5)), p97_5=float(np.percentile(v, 97.5)), width=float(np.percentile(v, 97.5) - np.percentile(v, 2.5))))
P("pooled learning curve (edit-distance baseline)", pc)
# pooled with within-set ranks (removes the between-set level difference; raw pooling above mixes two populations)
from scipy.stats import rankdata
def within(x, sets):
    out = np.zeros(len(x)); sets = np.asarray(sets)
    for g in set(sets): m = sets == g; out[m] = (rankdata(x[m]) - 0.5) / m.sum()
    return out
sets = np.array(["old"] * len(old_items) + ["new"] * len(files))
wed, whm = within(ped, sets), within(phm, sets)
pt, lo, hi = task_boot(ptasks, lambda ii: sp(wed[ii], whm[ii]), B)
pool["pooled, within-set ranks"] = dict(n_tasks=len(set(ptasks)), n_artifacts=len(ptasks), spearman=float(pt), lo=float(lo), hi=float(hi), width=float(hi - lo))
P("pooled editdist within-set ranks", json.dumps(pool["pooled, within-set ranks"]))
rng = np.random.default_rng(4); pc2 = []
for k in (10, 20, 30, 40, len(ut2)):
    vals = []
    for _ in range(500 if k < len(ut2) else 1):
        ii = [i for p in rng.choice(len(ut2), k, replace=False) for i in tix2[ut2[p]]]
        vals.append(sp(wed[ii], whm[ii]))
    v = np.array(vals); v = v[~np.isnan(v)]
    pc2.append(dict(k_tasks=k, median=float(np.median(v)), p2_5=float(np.percentile(v, 2.5)), p97_5=float(np.percentile(v, 97.5)), width=float(np.percentile(v, 97.5) - np.percentile(v, 2.5))))
P("pooled learning curve, within-set ranks", pc2)
P("mean human rating old / new:", float(old_hm.mean()), float(hm.mean()), "mean edit similarity old / new:", float(old_ed.mean()), float(ed.mean()))
json.dump(dict(per_rater=per_rater, agree=agree, baselines=base, new_curve=curve, counts=cnt, pooled_editdist=pool, pooled_curve=pc, pooled_curve_within=pc2), open(OUT / "new_summary.json", "w"), indent=1)
