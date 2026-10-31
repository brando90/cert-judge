#!/usr/bin/env python3
"""E64 confirmatory scoring on the fresh set-N human ratings (run ONCE after the ratings close, no refit, no model calls).
Inputs (formats in PROTOCOL.md section 4): --ratings setN_ratings.csv, --judges DIR (one <candidate>.json per frozen judge),
--units units_scores.json (optional, test D), --freeze FREEZE.json (checked), --out DIR.
Candidates and success rule are fixed in PROTOCOL.md; this script takes no threshold from the command line."""
import argparse, csv, hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

SEED = 1106                      # 11-06-2026
DRAWS = 10000
MIN_ITEMS, MIN_FOLDERS = 60, 12  # below this the test is "not evaluable", never a pass or a fail
BAR_POINT, BAR_LOWER, BAR_NULL = 0.75, 0.45, 0.60
GATE_RHO, GATE_P = 0.45, 0.05    # E39/E58 gate for the index, unchanged
MIN_UNITS, MIN_MODELS = 80, 10   # test D: below this "not evaluable"
GROUPS = {"A_human_mix_sft": [f"sft_q3_8b_hm_s{i}" for i in range(5)],
          "B_teacher_only_sft": [f"sft_q3_8b_s{i}" for i in range(6)],
          "C_qwen36_27b_checklist_think": ["qwen36_27b__checklist__think__stated"]}

def rho(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0: return float("nan")
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_ratings(path, old_test_items):
    rows = list(csv.DictReader(open(path)))
    need = {"item_id", "folder", "agent", "rater", "score", "qualified"}
    if not rows or need - set(rows[0]): sys.exit(f"STOP: ratings need columns {sorted(need)}")
    bad = {r["item_id"] for r in rows} & set(old_test_items)
    if bad: sys.exit(f"STOP: {len(bad)} ratings are old E63 test items (no test reads on them): {sorted(bad)[:5]}")
    by = {}
    for r in rows:
        d = by.setdefault(r["item_id"], {"folder": r["folder"], "q": [], "a1": None})
        s = float(r["score"])
        if r["rater"] == "A1": d["a1"] = s
        elif r["qualified"] in ("1", "true", "True"): d["q"].append(s)
    prim = {i: dict(folder=d["folder"], h=float(np.mean(d["q"]))) for i, d in by.items() if len(d["q"]) >= 2}
    a1 = {i: dict(folder=d["folder"], h=d["a1"]) for i, d in by.items() if d["a1"] is not None}
    pair = [(d["q"][0], d["q"][1]) for d in by.values() if len(d["q"]) >= 2]
    return prim, a1, pair

def load_judge(path): return json.load(open(path))["ev"]

def boot_groups(scores, human, folders, draws=DRAWS):
    """scores: {name: {item: ev}}; returns per-name rho and, for resampled folders, per-name rho arrays (shared draws)."""
    items = sorted(i for i in human if all(i in s for s in scores.values()))
    f = np.array([human[i]["folder"] for i in items]); y = np.array([human[i]["h"] for i in items])
    X = {n: np.array([s[i] for i in items]) for n, s in scores.items()}
    uf = sorted(set(f)); idx = {u: np.where(f == u)[0] for u in uf}
    point = {n: rho(X[n], y) for n in X}
    rng = np.random.default_rng(SEED); draws_r = {n: [] for n in X}
    for _ in range(draws):
        ii = np.concatenate([idx[uf[j]] for j in rng.integers(0, len(uf), len(uf))])
        for n in X: draws_r[n].append(rho(X[n][ii], y[ii]))
    return items, uf, point, {n: np.array(v) for n, v in draws_r.items()}

def ci(v): v = v[~np.isnan(v)]; return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

def verdict(point, lo):
    if point >= BAR_POINT and lo > BAR_LOWER: return "PASS"
    if point >= BAR_NULL and lo > 0: return "PARTIAL"
    return "FAIL"

def judges_block(judge_dir, human, label):
    scores = {}
    for g, names in GROUPS.items():
        for n in names:
            p = Path(judge_dir) / f"{n}.json"
            if not p.exists(): sys.exit(f"STOP: missing frozen judge output {p}")
            scores[n] = load_judge(p)
    items, uf, point, dr = boot_groups(scores, human, None)
    out = {"label": label, "n_items": len(items), "n_folders": len(uf)}
    if len(items) < MIN_ITEMS or len(uf) < MIN_FOLDERS:
        out["status"] = "NOT_EVALUABLE"; return out
    gm = {}
    for g, names in GROUPS.items():
        pr = [point[n] for n in names]; mean_draw = np.nanmean(np.vstack([dr[n] for n in names]), 0)
        m = float(np.mean(pr)); c = ci(mean_draw)
        gm[g] = mean_draw
        out[g] = {"per_seed_rho": dict(zip(names, pr)), "mean_rho": m, "ci95": c, "sd_across_seeds": float(np.std(pr, ddof=1)) if len(pr) > 1 else None,
                  "verdict": verdict(m, c[0]), "p_null_rho_le_0.60": float(np.mean(mean_draw <= BAR_NULL))}
    d = gm["A_human_mix_sft"] - gm["B_teacher_only_sft"]
    out["A_minus_B"] = {"diff": out["A_human_mix_sft"]["mean_rho"] - out["B_teacher_only_sft"]["mean_rho"], "ci95": ci(d), "A_beats_B": bool(ci(d)[0] > 0)}
    out["status"] = "EVALUATED"; return out

def index_block(units_path, human, freeze):
    sys.path[:0] = [str(Path(__file__).resolve().parents[2] / "58_open_weight_judges_on_e39_e42_probes/scripts")]
    import analyze58, e58                                       # frozen E58 code, sha in FREEZE.json
    A = e58.analysis_lib()
    ana = json.load(open(freeze["index"]["analysis_json_path"]))
    units = ana["units"]; sc = json.load(open(units_path)); kept = []
    for u in units:
        s = sc.get(u["config"]); idx_ok = u["indices"].get("C_ms_gold") is not None
        if s is None or not idx_ok: continue
        its = [i for i in human if i in s]
        if len(its) < 0.9 * len(human): continue                # E58's 90% coverage rule
        u = json.loads(json.dumps(u)); r = rho([s[i] for i in its], [human[i]["h"] for i in its])
        u["criteria"] = {"heldout": {"spearman": r, "n_items": len(its), "status": "COMPUTED"}}; kept.append(u)
    models = {u["model_key"] for u in kept}
    out = {"n_units": len(kept), "n_models": len(models)}
    if len(kept) < MIN_UNITS or len(models) < MIN_MODELS: out["status"] = "NOT_EVALUABLE"; return out
    g = analyze58.gate_block(A, kept, DRAWS); out.update(gate=g, status="EVALUATED",
        verdict="PASS" if g["plain_PASS"] and g["model_clustered_PASS"] else "FAIL")
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ratings", required=True); ap.add_argument("--judges", required=True)
    ap.add_argument("--units"); ap.add_argument("--freeze", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); freeze = json.load(open(a.freeze)); Path(a.out).mkdir(parents=True, exist_ok=True)
    prim, a1, pair = load_ratings(a.ratings, freeze["old_test_items"]["item_ids"])
    res = {"seed": SEED, "draws": DRAWS, "ratings_sha256": sha(a.ratings), "script_sha256": sha(__file__),
           "rater_pair_spearman_descriptive": rho([p[0] for p in pair], [p[1] for p in pair]) if len(pair) > 3 else None,
           "primary": judges_block(a.judges, prim, "primary: items with >=2 qualified ratings, human = mean of qualified raters"),
           "sensitivity_A1": judges_block(a.judges, a1, "sensitivity: A1 (Brando) ratings, all rated items")}
    if a.units: res["D_index_C_ms_gold"] = index_block(a.units, prim, freeze)
    json.dump(res, open(Path(a.out) / "CONFIRMATORY_RESULT.json", "w"), indent=1)
    print(json.dumps({k: (v.get("status"), {g: v[g]["verdict"] for g in GROUPS if g in v}) if isinstance(v, dict) and "status" in v else None for k, v in res.items() if k in ("primary", "sensitivity_A1", "D_index_C_ms_gold")}, indent=1))

if __name__ == "__main__": main()
