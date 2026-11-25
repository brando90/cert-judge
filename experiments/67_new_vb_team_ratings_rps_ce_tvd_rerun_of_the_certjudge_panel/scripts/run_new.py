"""Experiment 67, new set: A3 (new-set human agreement), A6 (counts old/new/pooled, judge-free baselines on the 100 new files, pooled edit-distance baseline).
CPU only, zero model calls. Reads inputs_local/new_ratings/<rater id>.tsv (raters' Sheets as TSV, not committed). Only rater ids are written out.
Run: ~/.venvs/sci/bin/python scripts/run_new.py --packet <.../rating_task_packet/main_rating_task>"""
import sys, csv, json, argparse, re
from pathlib import Path
import numpy as np
from rapidfuzz.distance import Levenshtein
sys.path.insert(0, str(Path(__file__).parent))
from lib import *

ap = argparse.ArgumentParser(); ap.add_argument("--packet", required=True)
ap.add_argument("--judge-scores", default=None, help="dir with out_gpt.jsonl, out_opus.jsonl, out_qwen.jsonl (judge repeats on the 100 files); adds the judge-scored tables")
ap.add_argument("--judged-only", action="store_true", help="skip the judge-free baselines and edit-distance curves (already in the committed results); only counts, A3 and the judge-scored tables")
ap.add_argument("--out-tag", default="", help="write to results/<tag>/ instead of results/ (interim runs)")
args = ap.parse_args()
HERE = Path(__file__).resolve().parents[1]; OUT = HERE / "results" / args.out_tag; OUT.mkdir(parents=True, exist_ok=True)
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
a, b = "T05", "T08"  # the two complete raters at the 11-24 reads; interim reads use the same pair
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

if not args.judged_only:
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
if not args.judged_only:
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
if not args.judged_only:
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

# =====================================================================================
# B: judge-scored tables on the 100 new files (addendum PREREG_addendum_interim_judged_11-24-2026.md); skipped without --judge-scores
# =====================================================================================
if args.judge_scores:
    JS = Path(args.judge_scores); NAMES = {"Codex": "out_gpt.jsonl", "Claude Opus": "out_opus.jsonl", "Qwen3-Coder": "out_qwen.jsonl"}
    def key_of(k): return f"{k[0]}/{Path(k[1]).name}"
    NEWJ, FAILS, COST = {}, {}, {}
    for fam, fn in NAMES.items():
        rows = [json.loads(l) for l in open(JS / fn)] if (JS / fn).exists() else []
        d = {}
        for r in rows:
            if r["score"] is not None: d.setdefault(r["key"], {})[r["rep"]] = r["score"]
        NEWJ[fam] = {k: [v[i] for i in sorted(v)] for k, v in d.items()}
        FAILS[fam] = dict(calls=len(rows), failed=sum(1 for r in rows if r["score"] is None), files_with_3=sum(1 for v in NEWJ[fam].values() if len(v) == 3))
        COST[fam] = dict(list_usd=sum((r["meta"].get("list_usd") or 0) for r in rows), input_tokens=sum((r["meta"].get("inp") or 0) for r in rows), output_tokens=sum((r["meta"].get("out") or 0) for r in rows))
    P("B judge calls", json.dumps(FAILS), "usage", json.dumps(COST))
    old_rl = [T_vb[k] for k in old_items]; new_rl = [list(R[k].values()) for k in files]
    old_H = [hum_dist(v) for v in old_rl]; new_H = [hum_dist(v) for v in new_rl]
    old_hm_a = np.array([np.mean(v) for v in old_rl]); new_hm_a = np.array([np.mean(v) for v in new_rl])
    B1, B2, B3, B4 = [], [], [], []
    rows_out = {}
    for fam in NAMES:
        if FAILS[fam]["files_with_3"] < len(files): P("B skip", fam, "incomplete", FAILS[fam]); continue
        jid = HEADLINE[fam]; detf = load_detail(FAM[fam][0])
        s_old = np.array([detf[jid][k][0] for k in old_items]); rp_old = [detf[jid][k][1] for k in old_items]
        rp_new = [NEWJ[fam][key_of(k)] for k in files]; s_new = np.array([float(np.median(r)) for r in rp_new])
        M_old = np.array([scores(old_H[i], smooth(judge_dist(rp_old[i]), 0.5)) for i in range(len(old_items))])
        M_new = np.array([scores(new_H[i], smooth(judge_dist(rp_new[i]), 0.5)) for i in range(len(files))])
        C_old = loto(old_items, old_tasks, s_old, old_rl); C_new = loto(files, new_tasks, s_new, new_rl)   # set-aware constants and calibrated fits, fitted inside each set
        sets_ = np.array(["old"] * len(old_items) + ["new"] * len(files)); ptasks_ = old_tasks + new_tasks
        s_p = np.concatenate([s_old, s_new]); hm_p = np.concatenate([old_hm_a, new_hm_a]); M_p = np.vstack([M_old, M_new])
        const_p = np.vstack([C_old["CONST"], C_new["CONST"]])
        w_s, w_h = within(s_p, sets_), within(hm_p, sets_)
        def z(x):
            o = np.zeros(len(x))
            for g in ("old", "new"):
                m = sets_ == g; o[m] = (x[m] - x[m].mean()) / (x[m].std() or 1.0)
            return o
        z_s, z_h = z(s_p), z(hm_p)
        # B1 per set and B2 pooled: (name, index mask over pooled arrays, tasks)
        for name, mask in (("old (H_vb)", sets_ == "old"), ("new (interim)", sets_ == "new"), ("pooled old+new", np.ones(len(sets_), bool))):
            ix = np.where(mask)[0]; tk = [ptasks_[i] for i in ix]
            def f(ii, ix=ix, name=name):
                jj = ix[np.asarray(ii)]
                if name.startswith("pooled"): sp_, pe_ = sp(w_s[jj], w_h[jj]), pe(z_s[jj], z_h[jj])
                else: sp_, pe_ = sp(s_p[jj], hm_p[jj]), pe(s_p[jj], hm_p[jj])
                return np.concatenate([M_p[jj].mean(0), const_p[jj].mean(0), (M_p[jj] - const_p[jj]).mean(0), [sp_, pe_]])
            pt, lo, hi = task_boot(tk, f, B)
            r = dict(family=fam, judge=jid, set=name, n_files=len(ix), n_tasks=len(set(tk)), mean_judge_score=float(s_p[ix].mean()), mean_human=float(hm_p[ix].mean()))
            for n, nm in enumerate(["RPS", "CE", "TVD", "constRPS", "constCE", "constTVD", "dRPS_vs_const", "dCE_vs_const", "dTVD_vs_const", "Spearman", "Pearson"]):
                r[nm] = float(pt[n]); r[nm + "_lo"] = float(lo[n]); r[nm + "_hi"] = float(hi[n])
            r["Spearman_width"] = r["Spearman_hi"] - r["Spearman_lo"]; r["RPS_width"] = r["RPS_hi"] - r["RPS_lo"]
            B1.append(r); P("B1", json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}))
        # B3 calibrated forecasters, new set alone and pooled-with-set-fits
        for name, parts in (("new", [(C_new, new_tasks)]), ("pooled (fits inside each set)", [(C_old, old_tasks), (C_new, new_tasks)])):
            tk = sum([t for _, t in parts], []); cv = {k: np.vstack([c[k] for c, _ in parts]) for k in FITTERS}
            for a_, b_ in (("CE-fit", "CONST"), ("CE-fit", "Pearson-fit"), ("Pearson-fit", "CONST")):
                pt, lo, hi = task_boot(tk, lambda ii: (cv[a_][np.asarray(ii)] - cv[b_][np.asarray(ii)]).mean(0), B)
                r = dict(family=fam, set=name, comparison=f"{a_} minus {b_}", n_tasks=len(set(tk)))
                for n, nm in enumerate(["dRPS", "dCE", "dTVD"]): r[nm] = float(pt[n]); r[nm + "_lo"] = float(lo[n]); r[nm + "_hi"] = float(hi[n])
                B3.append(r)
            r = dict(family=fam, set=name, comparison="levels", n_tasks=len(set(tk)))
            for k in FITTERS:
                for n, nm in enumerate(["RPS", "CE", "TVD"]): r[f"{k}_{nm}"] = float(cv[k][:, n].mean())
            B3.append(r)
        # B4 learning curves: Spearman and RPS-minus-constant over random k tasks (new alone; pooled with within-set ranks)
        rng = np.random.default_rng(10)
        for name, mask, ks in (("new", sets_ == "new", (5, 10, 15, 20, 25)), ("pooled", np.ones(len(sets_), bool), (10, 20, 30, 40, 45))):
            ix = np.where(mask)[0]; utk = sorted(set(ptasks_[i] for i in ix)); tix = {t: [i for i in ix if ptasks_[i] == t] for t in utk}
            for k in ks:
                vs, ds = [], []
                for _ in range(500 if k < len(utk) else 1):
                    jj = [i for p_ in rng.choice(len(utk), k, replace=False) for i in tix[utk[p_]]]
                    vs.append(sp(w_s[jj], w_h[jj]) if name == "pooled" else sp(s_p[jj], hm_p[jj])); ds.append((M_p[jj, 0] - const_p[jj, 0]).mean())
                vs = np.array(vs); vs = vs[~np.isnan(vs)]; ds = np.array(ds)
                B4.append(dict(family=fam, set=name, k_tasks=k, spearman_median=float(np.median(vs)), spearman_width=float(np.percentile(vs, 97.5) - np.percentile(vs, 2.5)) if len(vs) > 1 else float("nan"), dRPS_median=float(np.median(ds)), dRPS_width=float(np.percentile(ds, 97.5) - np.percentile(ds, 2.5)) if len(ds) > 1 else float("nan")))
        # distinct-score share (ties) on the new files and per-rater-free sanity
        rows_out[fam] = dict(distinct_scores_new=int(len(set(np.round(s_new, 3)))), tie_share_new=float(1 - len(set(np.round(s_new, 3))) / len(s_new)), repeat_sd_new=float(np.mean([np.std(r) for r in rp_new])))
        P("B extra", fam, json.dumps(rows_out[fam]))
    def wcsv(name, rows):
        if not rows: return
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(OUT / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    wcsv("judged_B1_per_set_and_pooled.csv", B1); wcsv("judged_B3_calibrated.csv", B3); wcsv("judged_B4_learning_curves.csv", B4)
    json.dump(dict(calls=FAILS, usage=COST, extra=rows_out, n_ratings=sum(per_rater.values()), per_rater=per_rater, n_files=len(files), n_tasks=len(set(tasks))), open(OUT / "judged_summary.json", "w"), indent=1)
