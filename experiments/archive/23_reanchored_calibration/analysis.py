#!/usr/bin/env python3
"""
EXP45 (dir 23): Pre-registered protocol re-anchoring analysis.

Implements EXACTLY the analyses registered in PREREG.md (committed 241f3de,
2026-07-21T17:55:33-07:00, BEFORE this file produced any number).
Deterministic (seed 42), no LLM calls, existing artifacts only.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments" / "04_veribench_validation"))
sys.path.insert(0, str(REPO / "experiments" / "22_pooled_heldout_and_noise_ceiling"))

import exp43_frozen_tivar_heldout as e43  # noqa: E402
import analysis as d22  # noqa: E402  (dir-22 loaders: load_rows, unique_config_rows, is_control_or_bad)

try:
    from scipy.stats import spearmanr

    def sp(xs, ys):
        r = spearmanr(xs, ys).statistic
        return float(r)
except Exception:  # pragma: no cover
    def sp(xs, ys):
        return e43._spearman(list(xs), list(ys))

SEED = 42
N_PERM_SCREEN = 20000
N_PERM_LOO = 2000
CANDIDATES = ["ident", "mono", "weak", "stab", "varcorr_1_minus",
              "varscore_1_minus", "ti_var_v3", "GM", "v1"]


# ---------------------------------------------------------------------------
# Predictors x: exp30 frozen trust vectors, averaged across panels per config
# ---------------------------------------------------------------------------

def load_x():
    base = REPO / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models"
    acc = defaultdict(lambda: defaultdict(list))
    for fam in ["codex", "claude_opus", "qwen", "leanstral"]:
        p = base / f"judge_trust_vector_{fam}_avg.csv"
        with p.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                jid = row["judge_id"]
                for col in ["ident", "mono", "weak", "stab",
                            "varcorr_1_minus", "varscore_1_minus", "ti_var_v3"]:
                    try:
                        acc[jid][col].append(float(row[col]))
                    except (KeyError, ValueError):
                        pass
    out = {}
    for jid, cols in acc.items():
        v = {c: sum(vals) / len(vals) for c, vals in cols.items() if vals}
        if len(v) < 7:
            continue
        v["GM"] = (max(v["ident"], 1e-9) * max(v["mono"], 1e-9)
                   * max(v["weak"], 1e-9) * max(v["stab"], 1e-9)) ** 0.25
        v["v1"] = 0.30 * v["ident"] + 0.30 * v["mono"] + 0.25 * v["weak"] + 0.15 * v["stab"]
        out[jid] = v
    return out


# ---------------------------------------------------------------------------
# Outcomes y (pool anchor, from dir-22 pipeline) and y2 (strict-set anchor)
# ---------------------------------------------------------------------------

def load_strict_labels():
    p = REPO / "experiments" / "human_labels" / "expert_harsh_set_data.tsv"
    acc = {}
    with p.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gold = str(row.get("gold_file", "")).strip()
            cand = str(row.get("candidate_file", "")).strip()
            st = str(row.get("human_score_0_5", "")).strip()
            if not st and ".lean " in cand:
                head, tail = cand.rsplit(" ", 1)
                try:
                    float(tail)
                    cand, st = head.strip(), tail.strip()
                except ValueError:
                    pass
            try:
                v = float(st) / 5.0
            except (TypeError, ValueError):
                continue
            acc.setdefault(f"{gold}::{cand}", []).append(v)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def load_y_and_y2():
    rows, participant_mean, _ = d22.load_rows()
    uniq_y = {r["judge_id"]: r["rho_heldout_items"] for r in d22.unique_config_rows(rows)}

    strict = load_strict_labels()
    acc2 = defaultdict(list)
    for panel in e43.PANELS:
        scores = e43.load_judge_item_scores(panel["detail_rows_csv"])
        for jid, sc in scores.items():
            common = sorted(set(sc) & set(strict))
            if len(common) >= 5:
                acc2[jid].append(sp([sc[k] for k in common], [strict[k] for k in common]))
    uniq_y2 = {jid: sum(v) / len(v) for jid, v in acc2.items()}
    return uniq_y, uniq_y2


# ---------------------------------------------------------------------------
# Registered analyses
# ---------------------------------------------------------------------------

def perm_p(xs, ys, rho_obs, n_perm, rng):
    cnt = 0
    ys2 = list(ys)
    for _ in range(n_perm):
        rng.shuffle(ys2)
        r = sp(xs, ys2)
        if math.isfinite(r) and abs(r) >= abs(rho_obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    m = len(pvals)
    prev = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvals[i])
        prev = max(prev, val)
        adj[i] = prev
    return adj


def screen(configs, x, y, n_perm, seed):
    out = []
    ys = [y[j] for j in configs]
    for cand in CANDIDATES:
        xs = [x[j][cand] for j in configs]
        rho = sp(xs, ys)
        rng = random.Random(seed)
        p = perm_p(xs, ys, rho, n_perm, rng)
        out.append({"candidate": cand, "rho": rho, "perm_p": p, "n": len(configs)})
    padj = holm([o["perm_p"] for o in out])
    for o, a in zip(out, padj):
        o["holm_p"] = a
    return out


def loo_selection(configs, x, y, rng_seed):
    def run_once(ys_map):
        preds = {}
        for held in configs:
            train = [j for j in configs if j != held]
            ty = [ys_map[j] for j in train]
            best, best_abs, best_sign = None, -1.0, 1.0
            for cand in CANDIDATES:
                tx = [x[j][cand] for j in train]
                r = sp(tx, ty)
                if math.isfinite(r) and abs(r) > best_abs:
                    best, best_abs, best_sign = cand, abs(r), (1.0 if r >= 0 else -1.0)
            preds[held] = best_sign * x[held][best]
        return sp([preds[j] for j in configs], [ys_map[j] for j in configs])

    obs = run_once(y)
    rng = random.Random(rng_seed)
    ys_vals = [y[j] for j in configs]
    cnt = 0
    for _ in range(N_PERM_LOO):
        shuffled = ys_vals[:]
        rng.shuffle(shuffled)
        r = run_once(dict(zip(configs, shuffled)))
        if math.isfinite(r) and abs(r) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, (cnt + 1) / (N_PERM_LOO + 1)


def apply_criteria(screen_real, loo_rho, loo_p, screen_y2):
    a_screen = any(o["rho"] >= 0.60 and o["holm_p"] < 0.05 for o in screen_real)
    a_loo = (loo_rho >= 0.50 and loo_p < 0.05)
    b_screen = all(abs(o["rho"]) <= 0.35 for o in screen_real)
    b_loo = loo_rho <= 0.35
    a2 = any(o["rho"] >= 0.60 and o["holm_p"] < 0.05 for o in screen_y2)
    b2 = all(abs(o["rho"]) <= 0.35 for o in screen_y2)
    primary = "a" if (a_screen or a_loo) else ("b" if (b_screen and b_loo) else "c")
    anchor2 = "a" if a2 else ("b" if b2 else "c")
    outcome = primary if primary == anchor2 or anchor2 == "c" or primary == "c" else "c"
    if primary == anchor2:
        outcome = primary
    return {"primary_pool_anchor": primary, "strict_anchor": anchor2, "registered_outcome": outcome}


def main():
    out_dir = HERE / "results"
    out_dir.mkdir(exist_ok=True)

    x = load_x()
    y, y2 = load_y_and_y2()

    all_configs = sorted(set(x) & set(y) & set(y2))
    real = [j for j in all_configs if not d22.is_control_or_bad(j)]
    controls = [j for j in all_configs if d22.is_control_or_bad(j)]

    screen_real = screen(real, x, y, N_PERM_SCREEN, SEED)
    loo_rho, loo_p = loo_selection(real, x, y, SEED)
    screen_y2_real = screen(real, x, y2, N_PERM_SCREEN, SEED)
    screen_all = screen(all_configs, x, y, N_PERM_SCREEN, SEED)

    real_med = {c: sorted(x[j][c] for j in real)[len(real) // 2] for c in CANDIDATES}
    controls_check = {
        "controls_y": {j: y[j] for j in controls},
        "candidate_ranks_controls_below_real_median": {
            c: sum(1 for j in controls if x[j][c] < real_med[c]) for c in CANDIDATES
        },
        "n_controls": len(controls),
    }

    verdict = apply_criteria(screen_real, loo_rho, loo_p, screen_y2_real)

    results = {
        "prereg_commit": "241f3de",
        "seed": SEED,
        "n_all_configs": len(all_configs),
        "n_real": len(real),
        "real_configs": real,
        "analysis1_screen_real_pool_anchor": screen_real,
        "analysis2_loo": {"predictive_spearman": loo_rho, "perm_p": loo_p,
                          "n_perm": N_PERM_LOO},
        "analysis3a_screen_real_strict_anchor": screen_y2_real,
        "analysis3b_screen_all20_pool_anchor": screen_all,
        "analysis4_controls": controls_check,
        "registered_verdict": verdict,
        "y_pool": {j: y[j] for j in all_configs},
        "y2_strict": {j: y2[j] for j in all_configs},
    }
    (out_dir / "results.json").write_text(json.dumps(results, indent=2))

    print(json.dumps({k: v for k, v in results.items()
                      if k not in ("y_pool", "y2_strict", "real_configs")}, indent=2))


if __name__ == "__main__":
    main()
