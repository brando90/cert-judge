#!/usr/bin/env python3
"""Compute exp16-style property metrics and the exp30 TI_var (v3) for the exp32 substitute judge, placed on the
Section 5.3 Codex panel scale. No inference, no credentials.

Panel reproduction: the eight Codex-panel judges are recomputed from
results_exp16_final_robust_r9_median/detail_rows.csv and checked against results_exp30_tivar_v3_all_models/
judge_trust_vector_codex_avg.csv (ident, mono, weak, stab, varcorr_1_minus, varscore_1_minus, ti_var_v3).

Frozen formulas:
  ident  = mean identity-variant score (24 x 4 rows), repeat-median per row
  mono   = clip((1 - rho_bug)/2, 0, 1) with rho_bug the POOLED Spearman between bug level and median score over all 24 x 5 bug rows
           (this reproduces results_exp30 exactly: mono == (1 - judge_rows.bug_spearman_r)/2; the per-file mean C_f of the paper
           appendix is reported alongside as cf_mono and differs by <= 0.02 on the panel)
  weak   = fraction of bug ladders that are non-increasing (utils.metrics.weak_monotonicity_pct / 100)
  stab   = 1 - flip_rate, flip_rate = fraction of all 288 rows whose repeats straddle the 0.85 accept threshold
  varcorr_raw  = variance over files of the per-file corr terms;  varscore_raw = mean over bug rows of the repeat variance
  varcorr_1_minus / varscore_1_minus = 1 - min-max normalization of the raw values across the panel (exp28 _norm_01)
  ti_var_v3 = exp(0.2 ln ident + 0.2 ln mono + 0.2 ln weak + 0.15 ln stab + 0.125 ln varcorr_1_minus + 0.125 ln varscore_1_minus),
              every term clipped to [1e-6, 1 - 1e-6]  (results_exp30_tivar_v3_all_models/summary.json weights)
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

EXP_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXP_DIR.parents[1]
V04 = REPO_ROOT / "experiments/archive/04_veribench_validation"
PANEL_DETAIL = V04 / "results_exp16_final_robust_r9_median/detail_rows.csv"
PANEL_TIVAR = V04 / "results_exp30_tivar_v3_all_models/judge_trust_vector_codex_avg.csv"
PANEL_JUDGE_ROWS = V04 / "results_exp16_final_robust_r9_median/judge_rows.csv"
RAW_DIR = EXP_DIR / "results/property_raw"
REQUESTS = EXP_DIR / "property_requests.json"
CFG = json.loads((EXP_DIR / "judge_config.json").read_text())
OUT_JSON = EXP_DIR / "results/property_suite.json"
OUT_MD = EXP_DIR / "results/property_suite.md"
THRESH = 0.85
EPS = 1e-6
W = {"ident": 0.2, "mono": 0.2, "weak": 0.2, "stab": 0.15, "varcorr": 0.125, "varscore": 0.125}
NEW_JUDGE_ID = f"{CFG['model_requested_by_cli_flag']}|{CFG['prompt_name']}"


def clip(x: float) -> float:
    return min(1.0 - EPS, max(EPS, float(x)))


def norm01(v: np.ndarray) -> np.ndarray:
    lo, hi = float(np.min(v)), float(np.max(v))
    return np.zeros_like(v) if hi <= lo + 1e-12 else (v - lo) / (hi - lo)


def weak_monotonicity_pct(ladders) -> float:
    if not ladders:
        return 0.0
    passed = sum(1 for l in ladders if len(l) <= 1 or all(l[i] >= l[i + 1] for i in range(len(l) - 1)))
    return 100.0 * passed / len(ladders)


def levenshtein_normalized(a: str, b: str) -> float:
    import Levenshtein
    if not a and not b:
        return 0.0
    return Levenshtein.distance(a, b) / max(len(a), len(b))


def features_from_rows(rows: list[dict], repeat_agg: str = "median") -> dict:
    """rows: dicts with row_type, item_key, repeat_scores (list). Returns exp16 metrics + raw TI_var inputs."""
    agg = (lambda v: float(np.median(v))) if repeat_agg == "median" else (lambda v: float(np.mean(v)))
    ident, flips, bug = [], [], {}
    human = {}
    lvl1_drops = []
    for r in rows:
        reps = [float(x) for x in r["repeat_scores"]]
        s = agg(reps)
        decs = {x >= THRESH for x in reps}
        flips.append(len(decs) > 1)
        if r["row_type"] == "property_identity":
            ident.append((r["item_key"], s))
        elif r["row_type"] == "property_bug":
            f, lvl = r["item_key"].split("::")
            bug.setdefault(f, {})[int(lvl[1:])] = (s, float(np.var(reps)))
        elif r["row_type"] == "human_eval_union":
            human[r["item_key"]] = s
    corrs, svars, ladders, levels_flat, scores_flat, const_ladders = [], [], [], [], [], 0
    for f in sorted(bug):
        lv = sorted(bug[f])
        ys = [bug[f][l][0] for l in lv]
        ladders.append(ys)
        levels_flat += lv; scores_flat += ys
        if len(set(ys)) == 1:
            const_ladders += 1
        if len(lv) >= 3:
            rs = spearmanr(lv, ys).statistic
            if math.isfinite(rs):
                corrs.append(min(1.0, max(0.0, (-rs + 1) / 2)))
                svars += [bug[f][l][1] for l in lv]
        if len(ys) >= 2:
            lvl1_drops.append(max(0.0, ys[0] - ys[1]))
    bug_r, bug_p = spearmanr(levels_flat, scores_flat) if len(levels_flat) > 2 else (float("nan"), float("nan"))
    flip_rate = sum(flips) / max(1, len(flips))
    ident_scores = [s for _, s in ident]
    out = {
        "n_rows": len(rows), "n_identity": len(ident), "n_bug_ladders": len(ladders), "n_human": len(human),
        "identity_mean": float(np.mean(ident_scores)) if ident_scores else float("nan"),
        "identity_std": float(statistics.stdev(ident_scores)) if len(ident_scores) > 1 else 0.0,
        "identity_by_variant": {v: float(np.mean([s for k, s in ident if k.endswith("::" + v)])) for v in ("RENAME", "REORDER", "STYLE", "ALPHA")} if ident else {},
        "bug_spearman_r": float(bug_r), "bug_spearman_p": float(bug_p),
        "bug_weak_mono_pct": weak_monotonicity_pct(ladders),
        "bug_constant_ladders": const_ladders,
        "bug_ladders_with_local_increase": sum(1 for l in ladders if any(l[i] < l[i + 1] for i in range(len(l) - 1))),
        "bug_level_means": [float(np.mean([l[k] for l in ladders])) for k in range(5)] if ladders else [],
        "flip_rate": float(flip_rate),
        "lvl1_mean_drop": float(np.mean(lvl1_drops)) if lvl1_drops else 0.0,
        "cf_mono": float(np.mean(corrs)) if corrs else 0.0,
        "mono_flat": min(1.0, max(0.0, (1.0 - float(bug_r)) / 2.0)) if math.isfinite(float(bug_r)) else 0.0,
        "n_files_with_corr": len(corrs),
        "varcorr_raw": float(np.var(corrs)) if corrs else 1.0,
        "varscore_raw": float(np.mean(svars)) if svars else 1.0,
        "human_scores": human,
    }
    out["subtle_bug_sensitivity"] = max(0.0, min(1.0, out["lvl1_mean_drop"] / 0.25))
    return out


def tivar(ident, mono, weak, stab, varcorr_1m, varscore_1m) -> float:
    return math.exp(W["ident"] * math.log(clip(ident)) + W["mono"] * math.log(clip(mono)) + W["weak"] * math.log(clip(weak))
                    + W["stab"] * math.log(clip(stab)) + W["varcorr"] * math.log(clip(varcorr_1m)) + W["varscore"] * math.log(clip(varscore_1m)))


def load_panel_rows() -> dict[str, list[dict]]:
    by = {}
    with PANEL_DETAIL.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by.setdefault(r["judge_id"], []).append({"row_type": r["row_type"], "item_key": r["item_key"], "repeat_scores": json.loads(r["repeat_scores"])})
    return by


def load_new_rows() -> tuple[list[dict], dict]:
    req = json.loads(REQUESTS.read_text())
    cells = {}
    meta = {"ok": 0, "failed": 0, "attempts": 0, "elapsed": []}
    for p in RAW_DIR.glob("*.json"):
        if p.name.endswith(".failed.json"):
            meta["failed"] += 1; continue
        d = json.loads(p.read_text())
        if d.get("status") != "ok":
            continue
        meta["ok"] += 1; meta["attempts"] += int(d.get("attempt", 1)); meta["elapsed"].append(float(d.get("elapsed_seconds", 0)))
        cells.setdefault((d["row_type"], d["item_key"]), {})[int(d["repeat"])] = float(d["score"])
    rows, incomplete = [], 0
    for r in req["rows"]:
        reps = cells.get((r["row_type"], r["item_key"]), {})
        if len(reps) < CFG["n_repeats"]:
            incomplete += 1
            if not reps:
                continue
        rows.append({"row_type": r["row_type"], "item_key": r["item_key"], "repeat_scores": [reps[k] for k in sorted(reps)], "human": r.get("human")})
    meta["rows_with_all_repeats"] = len(req["rows"]) - incomplete
    meta["rows_total"] = len(req["rows"])
    meta["mean_elapsed"] = float(np.mean(meta["elapsed"])) if meta["elapsed"] else None
    return rows, meta


def human_alignment(rows: list[dict], human_scores: dict) -> dict:
    out = {}
    rng = np.random.default_rng(42)
    for label in ("pass1", "pass2", "avg"):
        pairs = [(r["human"][label] / 5.0, human_scores[r["item_key"]]) for r in rows if r["row_type"] == "human_eval_union" and r.get("human") and r["human"].get(label) is not None and r["item_key"] in human_scores]
        if len(pairs) < 3:
            out[label] = {"n": len(pairs)}; continue
        h = np.array([p[0] for p in pairs]); j = np.array([p[1] for p in pairs])
        r, p = spearmanr(h, j)
        boots = []
        for _ in range(5000):
            idx = rng.integers(0, len(h), len(h))
            v = spearmanr(h[idx], j[idx]).statistic
            if math.isfinite(v):
                boots.append(v)
        boots = np.sort(np.array(boots))
        out[label] = {"n": len(pairs), "spearman_r": float(r), "p": float(p), "ci_lo": float(boots[int(0.025 * (len(boots) - 1))]), "ci_hi": float(boots[int(0.975 * (len(boots) - 1))])}
    return out


def main() -> None:
    panel = load_panel_rows()
    panel_feat = {j: features_from_rows(rows) for j, rows in panel.items()}
    pub = {r["judge_id"]: r for r in csv.DictReader(PANEL_TIVAR.open(newline="", encoding="utf-8"))}
    jids = [j for j in pub if j in panel_feat]
    vco = norm01(np.array([panel_feat[j]["varcorr_raw"] for j in jids]))
    vsc = norm01(np.array([panel_feat[j]["varscore_raw"] for j in jids]))
    panel_table, max_abs_diff = [], 0.0
    for i, j in enumerate(jids):
        f = panel_feat[j]
        terms = dict(ident=f["identity_mean"], mono=f["mono_flat"], weak=f["bug_weak_mono_pct"] / 100.0, stab=1.0 - f["flip_rate"], varcorr_1_minus=1.0 - float(vco[i]), varscore_1_minus=1.0 - float(vsc[i]))
        ti = tivar(terms["ident"], terms["mono"], terms["weak"], terms["stab"], terms["varcorr_1_minus"], terms["varscore_1_minus"])
        diff = abs(ti - float(pub[j]["ti_var_v3"]))
        max_abs_diff = max(max_abs_diff, diff)
        panel_table.append({"judge_id": j, **{k: round(v, 6) for k, v in terms.items()}, "ti_var_v3_recomputed": round(ti, 6), "ti_var_v3_published": float(pub[j]["ti_var_v3"]), "abs_diff": round(diff, 6),
                            "bug_spearman_r": round(f["bug_spearman_r"], 4), "bug_constant_ladders": f["bug_constant_ladders"], "bug_ladders_with_local_increase": f["bug_ladders_with_local_increase"]})
    panel_raw_range = {"varcorr_raw": [float(min(panel_feat[j]["varcorr_raw"] for j in jids)), float(max(panel_feat[j]["varcorr_raw"] for j in jids))],
                       "varscore_raw": [float(min(panel_feat[j]["varscore_raw"] for j in jids)), float(max(panel_feat[j]["varscore_raw"] for j in jids))]}

    new_rows, meta = load_new_rows()
    result = {"schema_version": "exp32_property_suite_v1", "judge_id": NEW_JUDGE_ID, "formula": __doc__.strip(), "weights": W, "threshold": THRESH,
              "panel_reproduction": {"max_abs_diff_ti_var_v3": round(max_abs_diff, 6), "rows": panel_table, "raw_normalization_range": panel_raw_range},
              "new_judge": {"cells": meta}}
    if new_rows:
        nf = features_from_rows(new_rows)
        def place(vc_raw, vs_raw, lo_hi):
            def n(x, lo, hi):
                return 0.0 if hi <= lo + 1e-12 else (x - lo) / (hi - lo)
            return 1.0 - n(vc_raw, *lo_hi["varcorr_raw"]), 1.0 - n(vs_raw, *lo_hi["varscore_raw"])
        # (a) fixed panel scale: normalize with the 8-judge panel min/max (values outside the range are clipped to [0,1])
        vc1, vs1 = place(nf["varcorr_raw"], nf["varscore_raw"], panel_raw_range)
        vc1, vs1 = min(1.0, max(0.0, vc1)), min(1.0, max(0.0, vs1))
        terms_fixed = dict(ident=nf["identity_mean"], mono=nf["mono_flat"], weak=nf["bug_weak_mono_pct"] / 100.0, stab=1.0 - nf["flip_rate"], varcorr_1_minus=vc1, varscore_1_minus=vs1)
        ti_fixed = tivar(**terms_fixed)
        # (b) 9-judge renormalization (panel + new judge)
        all_ids = jids + [NEW_JUDGE_ID]
        vco9 = norm01(np.array([panel_feat[j]["varcorr_raw"] for j in jids] + [nf["varcorr_raw"]]))
        vsc9 = norm01(np.array([panel_feat[j]["varscore_raw"] for j in jids] + [nf["varscore_raw"]]))
        ti9 = {}
        for i, j in enumerate(all_ids):
            f = panel_feat[j] if j in panel_feat else nf
            ti9[j] = tivar(f["identity_mean"], f["mono_flat"], f["bug_weak_mono_pct"] / 100.0, 1.0 - f["flip_rate"], 1.0 - float(vco9[i]), 1.0 - float(vsc9[i]))
        published = {j: float(pub[j]["ti_var_v3"]) for j in jids}
        rank_fixed = 1 + sum(1 for v in published.values() if v > ti_fixed)
        ha = human_alignment(new_rows, nf["human_scores"])
        result["new_judge"].update({
            "exp16_metrics": {k: v for k, v in nf.items() if k != "human_scores"},
            "ti_var_terms_fixed_panel_scale": terms_fixed,
            "ti_var_v3_fixed_panel_scale": ti_fixed,
            "rank_among_8_codex_panel_configs_fixed_scale": rank_fixed,
            "ti_var_v3_9judge_renormalized": ti9,
            "controls_reference": {j: published[j] for j in jids if j in ("gpt-5.3-codex|BAD_STRINGY", "editdist_e1", "random_r1")},
            "human_alignment": ha,
            "cert_index_v1": 0.30 * min(1, max(0, nf["identity_mean"])) + 0.30 * min(1, max(0, (-nf["bug_spearman_r"] + 1) / 2)) + 0.25 * nf["bug_weak_mono_pct"] / 100 + 0.15 * (1 - nf["flip_rate"]),
        })
    OUT_JSON.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    lines = [f"# Property suite — {NEW_JUDGE_ID} (effort {CFG['reasoning_effort']}, 3 repeats, median)", "",
             f"Panel reproduction check (8 Codex configs recomputed from exp16 r9_median detail rows vs exp30 CSV): max |Δ ti_var_v3| = {max_abs_diff:.2e}", "",
             "| judge | ident | mono | weak | stab | varcorr_1m | varscore_1m | TI_var recomputed | published | bug ρ | const ladders |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in panel_table:
        lines.append(f"| {r['judge_id']} | {r['ident']:.3f} | {r['mono']:.3f} | {r['weak']:.3f} | {r['stab']:.3f} | {r['varcorr_1_minus']:.3f} | {r['varscore_1_minus']:.3f} | {r['ti_var_v3_recomputed']:.4f} | {r['ti_var_v3_published']:.4f} | {r['bug_spearman_r']:.3f} | {r['bug_constant_ladders']} |")
    if new_rows:
        nj = result["new_judge"]; nf = nj["exp16_metrics"]; t = nj["ti_var_terms_fixed_panel_scale"]
        lines += ["", f"## New judge: cells ok {meta['ok']}, rows with all 3 repeats {meta['rows_with_all_repeats']}/{meta['rows_total']}, CLI invocations {meta['attempts']}, failed {meta['failed']}", "",
                  f"| {NEW_JUDGE_ID} | {t['ident']:.3f} | {t['mono']:.3f} | {t['weak']:.3f} | {t['stab']:.3f} | {t['varcorr_1_minus']:.3f} | {t['varscore_1_minus']:.3f} | **{nj['ti_var_v3_fixed_panel_scale']:.4f}** (fixed panel scale; rank {nj['rank_among_8_codex_panel_configs_fixed_scale']}/9) | 9-judge renorm {nj['ti_var_v3_9judge_renormalized'][NEW_JUDGE_ID]:.4f} | {nf['bug_spearman_r']:.3f} | {nf['bug_constant_ladders']} |", "",
                  f"- exp16 metrics: identity_mean {nf['identity_mean']:.3f} (by variant {json.dumps({k: round(v,3) for k,v in nf['identity_by_variant'].items()})}), bug Spearman {nf['bug_spearman_r']:.3f} (p={nf['bug_spearman_p']:.2e}), weak monotonicity {nf['bug_weak_mono_pct']:.1f}%, ladders with a local increase {nf['bug_ladders_with_local_increase']}/{nf['n_bug_ladders']}, constant ladders {nf['bug_constant_ladders']}/{nf['n_bug_ladders']}, flip rate {nf['flip_rate']:.4f}, level-1 mean drop {nf['lvl1_mean_drop']:.3f}, bug-level means {[round(x,3) for x in nf['bug_level_means']]}",
                  f"- human alignment (72-pair validation set): " + "; ".join(f"{k}: ρ={v.get('spearman_r', float('nan')):.3f} [{v.get('ci_lo', float('nan')):.3f}, {v.get('ci_hi', float('nan')):.3f}] n={v['n']}" for k, v in nj['human_alignment'].items()),
                  f"- controls (published TI_var): {json.dumps({k: round(v,3) for k,v in nj['controls_reference'].items()})}"]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD.read_text())


if __name__ == "__main__":
    main()
