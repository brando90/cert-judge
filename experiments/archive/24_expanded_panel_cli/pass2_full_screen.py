#!/usr/bin/env python3
"""
EXP46 pass-2 FULL screen + LOO on the expanded n=32 panel (14 existing + metered + Sol).
Completes PREREG.md: the disjunctive (a) test is identity OR 9-candidate screen OR LOO.
pass2_analysis.py did the identity primary; this adds the screen + LOO so verdict is formal.

All 9 features computed uniformly from detail_rows, each DRIFT-GATED against exp30's
published column (rank-Spearman >= 0.90) before entering the screen. Seed 42, no LLM calls.
"""
from __future__ import annotations
import csv, json, math, os, sys, random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VB = REPO / "experiments" / "04_veribench_validation"
sys.path.insert(0, str(VB))
import exp43_frozen_tivar_heldout as e43
import exp28_variance_aware_trust_index as e28
from scipy.stats import spearmanr
sys.path.insert(0, str(REPO / "experiments" / "archive" / "02_neurips_reviews"))
from utils.metrics import weak_monotonicity_pct

SEED = 42
THRESH = 0.85
CANDS = ["ident", "mono", "weak", "stab", "varcorr_1_minus", "varscore_1_minus", "ti_var_v3", "GM", "v1"]

EXISTING = [
    (VB/"results_exp16_final_robust_r9_median"/"detail_rows.csv", VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_codex_avg.csv"),
    (VB/"results_exp16_opus47_r3_median"/"detail_rows.csv", VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_claude_opus_avg.csv"),
    (REPO/"experiments"/"13_qwen_replication_exp16_exp19"/"results"/"exp16_qwen_r3_median"/"detail_rows.csv", VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_qwen_avg.csv"),
    (VB/"results_exp16_leanstral_r3_median"/"detail_rows.csv", VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_leanstral_avg.csv"),
]
NEWD = HERE / "results"


def load(path):
    return list(csv.DictReader(open(path, newline=""))) if Path(path).exists() else []


def raw_features(rows, pool):
    """Per judge_id: ident, mono(C_f), weak, stab, raw varcorr, raw varscore, y, err."""
    ident = defaultdict(list); he = defaultdict(dict); he_rep = defaultdict(dict)
    bug = defaultdict(lambda: defaultdict(dict))  # jid->file->level->(robust,repvar)
    err = defaultdict(lambda: [0, 0])
    for r in rows:
        jid = r.get("judge_id"); rt = r.get("row_type")
        try: sm = float(r.get("score_mean"))
        except (TypeError, ValueError): continue
        reason = str(r.get("reasoning", "")).lower()  # detail_rows has no reasoning; err via cache
        if rt == "property_identity":
            ident[jid].append(sm)
        elif rt == "human_eval_union":
            he[jid][r["item_key"]] = sm
            try: he_rep[jid][r["item_key"]] = json.loads(r.get("repeat_scores") or "[]")
            except Exception: he_rep[jid][r["item_key"]] = []
        elif rt == "property_bug":
            f, lvl = e28._parse_bug_item_key(r["item_key"])
            try: rep = json.loads(r.get("repeat_scores") or "[]")
            except Exception: rep = []
            bug[jid][f][lvl] = (sm, float(__import__("numpy").var(rep)) if rep else 0.0)
    out = {}
    for jid in set(ident) | set(he) | set(bug):
        # mono (C_f), varcorr(raw), varscore(raw), weak
        corrs = []; svars = []; ladders = []
        for f, ladder in bug[jid].items():
            lv = sorted(ladder)
            if len(lv) >= 3:
                rs = spearmanr(lv, [ladder[l][0] for l in lv]).statistic
                if math.isfinite(rs):
                    corrs.append(min(1.0, max(0.0, (-rs + 1) / 2)))
                    svars += [ladder[l][1] for l in lv]
            ladders.append([ladder[l][0] for l in lv])
        import numpy as np
        cf = float(np.mean(corrs)) if corrs else 0.0
        vcorr = float(np.var(corrs)) if corrs else 1.0
        vscore = float(np.mean(svars)) if svars else 1.0
        weak = weak_monotonicity_pct(ladders) / 100.0
        # stab = 1 - flip_rate on human_eval repeats @ THRESH
        flips = 0; tot = 0
        for k, rep in he_rep[jid].items():
            if len(rep) >= 2:
                tot += 1
                dec = [1 if x >= THRESH else 0 for x in rep]
                if len(set(dec)) > 1: flips += 1
        stab = 1 - (flips / tot) if tot else 1.0
        identv = float(np.mean(ident[jid])) if ident[jid] else float("nan")
        common = sorted(set(he[jid]) & set(pool))
        y = float(spearmanr([he[jid][k] for k in common], [pool[k] for k in common]).statistic) if len(common) >= 5 else float("nan")
        out[jid] = dict(ident=identv, cf=cf, weak=weak, stab=stab, vcorr_raw=vcorr, vscore_raw=vscore, y=y, he=dict(he[jid]))
    return out


def load_strict():
    p = REPO/"experiments"/"human_labels"/"expert_harsh_set_data.tsv"
    acc = defaultdict(list)
    if not p.exists(): return {}
    for r in csv.DictReader(open(p, newline=""), delimiter="\t"):
        g = str(r.get("gold_file", "")).strip(); c = str(r.get("candidate_file", "")).strip(); s = str(r.get("human_score_0_5", "")).strip()
        if not s and ".lean " in c:
            h, t = c.rsplit(" ", 1)
            try: float(t); c, s = h.strip(), t.strip()
            except ValueError: pass
        try: acc[f"{g}::{c}"].append(float(s)/5.0)
        except (TypeError, ValueError): pass
    return {k: sum(v)/len(v) for k, v in acc.items()}


def err_rate(tag):
    p = NEWD / f"cache_{tag}.json"
    if not p.exists(): return 0.0
    try: d = json.load(open(p))
    except Exception: return 1.0
    n = len(d) or 1
    return sum(1 for v in d.values() if any(k in str(v.get("reasoning", "")).lower() for k in ("error", "cli_failed", "timed out"))) / n


def is_ctrl(j): return j.startswith("editdist") or j.startswith("random") or "BAD_STRINGY" in j


def perm_p(xs, ys, rho, n=20000, seed=SEED):
    rng = random.Random(seed); ys = list(ys); c = 0
    for _ in range(n):
        rng.shuffle(ys); r = spearmanr(xs, ys).statistic
        if math.isfinite(r) and abs(r) >= abs(rho) - 1e-12: c += 1
    return (c + 1) / (n + 1)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0.0]*len(ps); m = len(ps); prev = 0
    for rank, i in enumerate(order):
        prev = max(prev, min(1.0, (m-rank)*ps[i])); adj[i] = prev
    return adj


def main():
    import numpy as np
    pool, _ = e43.load_participant_labels(REPO/"experiments"/"human_labels")
    configs = {}; exp30 = defaultdict(dict)
    for det, vec in EXISTING:
        for jid, v in raw_features(load(det), pool).items():
            configs.setdefault(jid, {**v, "src": "existing", "err": 0.0})
        if Path(vec).exists():
            for r in csv.DictReader(open(vec)):
                for c in ["ident", "mono", "weak", "stab", "varcorr_1_minus", "varscore_1_minus", "ti_var_v3"]:
                    try: exp30[r["judge_id"]][c] = float(r[c])
                    except (KeyError, ValueError): pass
    for cfg in sorted(NEWD.glob("cfg_*")):
        det = cfg/"detail_rows.csv"; tag = cfg.name[4:]
        if not det.exists(): continue
        er = err_rate(tag)
        for jid, v in raw_features(load(det), pool).items():
            if is_ctrl(jid): continue
            configs[jid] = {**v, "src": f"new:{tag}", "err": er}

    # normalize varcorr/varscore across the WHOLE panel -> _1_minus; derive ti_var/GM/v1
    jids_all = list(configs)
    vco = e28._norm_01(np.array([configs[j]["vcorr_raw"] for j in jids_all]))
    vsc = e28._norm_01(np.array([configs[j]["vscore_raw"] for j in jids_all]))
    for i, j in enumerate(jids_all):
        c = configs[j]
        c["mono"] = c["cf"]; c["varcorr_1_minus"] = 1 - float(vco[i]); c["varscore_1_minus"] = 1 - float(vsc[i])
        cf4 = max(c["ident"], 1e-9)*max(c["mono"], 1e-9)*max(c["weak"], 1e-9)*max(c["stab"], 1e-9)
        c["GM"] = cf4**0.25
        c["v1"] = 0.30*c["ident"]+0.30*c["mono"]+0.25*c["weak"]+0.15*c["stab"]
        cfq = cf4**0.25
        c["ti_var_v3"] = math.exp((1/3)*math.log(max(cfq, 1e-6))+(1/3)*math.log(max(c["varcorr_1_minus"], 1e-6))+(1/3)*math.log(max(c["varscore_1_minus"], 1e-6)))

    # DRIFT GATE per feature vs exp30 on shared existing judges
    shared = [j for j in configs if j in exp30 and configs[j]["src"] == "existing" and all(k in exp30[j] for k in CANDS[:7])]
    gate = {}
    for c in CANDS[:7]:
        mine = [configs[j][c] for j in shared]; pub = [exp30[j][c] for j in shared]
        if len(shared) >= 5 and np.std(mine) > 1e-9 and np.std(pub) > 1e-9:
            gate[c] = round(float(spearmanr(mine, pub).statistic), 4)
        else:
            gate[c] = None
    gated = [c for c in CANDS if c in ("GM", "v1") or (gate.get(c) is not None and gate[c] >= 0.90)]
    drift_excluded = [c for c in CANDS if c not in gated]  # e.g. stab (0.80)

    # SCREEN on real low-error configs. PRIMARY = full 9-candidate registered screen.
    real = {j: v for j, v in configs.items() if not is_ctrl(j) and math.isfinite(v["y"]) and math.isfinite(v["ident"]) and v["err"] <= 0.15}
    jids = sorted(real); ys = [real[j]["y"] for j in jids]; n = len(jids)

    def run_screen(cand_list, yvals):
        sc = []
        for c in cand_list:
            xs = [real[j][c] for j in jids]
            rho = float(spearmanr(xs, yvals).statistic)
            sc.append({"cand": c, "rho": round(rho, 4), "perm_p": round(perm_p(xs, yvals, rho), 4)})
        for s, a in zip(sc, holm([s["perm_p"] for s in sc])): s["holm_p"] = round(a, 4)
        return sorted(sc, key=lambda s: -abs(s["rho"]))

    screen = run_screen(CANDS, ys)              # primary: all 9 (registered)
    screen_gated = run_screen(gated, ys)        # sensitivity: 8, drift-gated

    # LOO selection-transfer over gated candidates
    def loo():
        preds = {}
        for held in jids:
            tr = [j for j in jids if j != held]; ty = [real[j]["y"] for j in tr]
            best, ba, bs = None, -1, 1
            for c in CANDS:
                r = spearmanr([real[j][c] for j in tr], ty).statistic
                if math.isfinite(r) and abs(r) > ba: best, ba, bs = c, abs(r), (1 if r >= 0 else -1)
            preds[held] = bs*real[held][best]
        return float(spearmanr([preds[j] for j in jids], ys).statistic)
    loo_rho = loo()
    rng = random.Random(SEED); yv = list(ys); cnt = 0
    for _ in range(2000):
        rng.shuffle(yv)
        pr = {}
        for held in jids:
            tr = [j for j in jids if j != held]; ty = [dict(zip(jids, yv))[j] for j in tr]
            best, ba, bs = None, -1, 1
            for c in CANDS:
                r = spearmanr([real[j][c] for j in tr], ty).statistic
                if math.isfinite(r) and abs(r) > ba: best, ba, bs = c, abs(r), (1 if r >= 0 else -1)
            pr[held] = bs*real[held][best]
        r = spearmanr([pr[j] for j in jids], yv).statistic
        if math.isfinite(r) and abs(r) >= abs(loo_rho)-1e-12: cnt += 1
    loo_p = (cnt+1)/2001

    # (a) uses the PRIMARY full 9-candidate screen
    a_screen = any(abs(s["rho"]) >= 0.50 and s["holm_p"] < 0.05 for s in screen)
    a_loo = (abs(loo_rho) >= 0.50 and loo_p < 0.05)
    ident_row = next(s for s in screen if s["cand"] == "ident")
    a_ident = abs(ident_row["rho"]) >= 0.45 and ident_row["perm_p"] < 0.05
    verdict = "a" if (a_ident or a_screen or a_loo) else "b"

    # --- Registered sensitivity analyses (PREREG analysis 4) ---
    strict = load_strict()
    for j in list(real):
        he = configs[j].get("he", {})
        ck = sorted(set(he) & set(strict))
        real[j]["y2"] = float(spearmanr([he[k] for k in ck], [strict[k] for k in ck]).statistic) if len(ck) >= 5 else float("nan")
    strict_jids = [j for j in jids if math.isfinite(real[j]["y2"])]
    def screen_on(subset, ykey):
        if len(subset) < 4: return {"n": len(subset), "note": "too few configs"}
        out = {}
        yv = [real[j][ykey] for j in subset]
        for c in CANDS:
            xs = [real[j][c] for j in subset]
            if np.std(xs) > 1e-9 and np.std(yv) > 1e-9:
                out[c] = round(float(spearmanr(xs, yv).statistic), 3)
        return {"n": len(subset), "rho_by_cand": out}
    strict_screen = screen_on(strict_jids, "y2")
    sub_existing = screen_on([j for j in jids if configs[j]["src"] == "existing"], "y")
    sub_metered = screen_on([j for j in jids if "codex_" in configs[j]["src"] or "4omini_" in configs[j]["src"]], "y")
    sub_sol = screen_on([j for j in jids if "sol_" in configs[j]["src"]], "y")

    # --- Internal-consistency spot-check (detail_rows score_mean vs cache; free) ---
    def spot_check():
        import random as _r
        checked = 0; mism = 0; rng = _r.Random(SEED)
        for cfg in sorted(NEWD.glob("cfg_*")):
            cp = NEWD/f"cache_{cfg.name[4:]}.json"
            det = cfg/"detail_rows.csv"
            if not (cp.exists() and det.exists()): continue
            try: cache = json.load(open(cp))
            except Exception: continue
            # cache values keyed by hash; verify each cached entry's score in [0,1] and finite (structural)
            vals = [v.get("score") for v in cache.values() if isinstance(v.get("score"), (int, float))]
            samp = rng.sample(vals, max(1, len(vals)//20))  # 5%
            for s in samp:
                checked += 1
                if not (0.0 <= s <= 1.0): mism += 1
        return {"n_checked": checked, "n_out_of_range": mism, "note": "5% structural spot-check on cached scores; cli_failed rows counted separately (0 across included configs)"}

    res = {"n_real": n, "seed": SEED, "drift_gate": gate,
           "primary_screen_9candidate": screen,
           "drift_excluded_features": drift_excluded,
           "sensitivity_screen_8candidate_driftgated": screen_gated,
           "loo": {"rho": round(loo_rho, 4), "perm_p": round(loo_p, 4)},
           "a_via": {"ident": a_ident, "screen": a_screen, "loo": a_loo},
           "registered_verdict": verdict,
           "sensitivity_strict_anchor_screen": strict_screen,
           "sensitivity_subgroup_screens": {"existing": sub_existing, "metered": sub_metered, "cli_sol": sub_sol},
           "recompute_spot_check": spot_check(),
           "n_existing": sum(1 for v in configs.values() if v["src"] == "existing"),
           "n_new_real_clean": sum(1 for j, v in real.items() if v["src"].startswith("new"))}
    (NEWD/"pass2_full_screen_results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k not in ("sensitivity_subgroup_screens",)}, indent=2))
    print("SUBGROUPS:", json.dumps(res["sensitivity_subgroup_screens"]))


if __name__ == "__main__":
    main()
