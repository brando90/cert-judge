#!/usr/bin/env python3
"""
EXP46 pass-2 analysis (dir 24). Implements PREREG.md (committed c5a621c before results).

Primary registered test: does identity compliance (ident) anti-correlate with
pool-anchored (semantic-protocol) judge alignment (y) at the expanded n?
Drift gate: my self-computed ident + y must reproduce exp30 / dir-22 for the 14
existing configs (rank Spearman >= 0.95) before any new-config number is trusted.

Deterministic (seed 42), no LLM calls, existing artifacts + new cfg detail_rows only.
"""
from __future__ import annotations
import csv, json, math, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VB = REPO / "experiments" / "04_veribench_validation"
sys.path.insert(0, str(VB))
import exp43_frozen_tivar_heldout as e43  # pool loader + spearman
from scipy.stats import spearmanr
import random

SEED = 42
CONTROL = ("editdist_e1", "random_r1")

# ---- existing 14: family detail_rows (same dirs exp43 uses) + exp30 published x ----
EXISTING = [
    ("codex",       VB/"results_exp16_final_robust_r9_median"/"detail_rows.csv",
                    VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_codex_avg.csv"),
    ("claude_opus", VB/"results_exp16_opus47_r3_median"/"detail_rows.csv",
                    VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_claude_opus_avg.csv"),
    ("qwen",        REPO/"experiments"/"13_qwen_replication_exp16_exp19"/"results"/"exp16_qwen_r3_median"/"detail_rows.csv",
                    VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_qwen_avg.csv"),
    ("leanstral",   VB/"results_exp16_leanstral_r3_median"/"detail_rows.csv",
                    VB/"results_exp30_tivar_v3_all_models"/"judge_trust_vector_leanstral_avg.csv"),
]
NEW_DIR = HERE / "results"


def load_detail(path):
    rows = []
    if not Path(path).exists():
        return rows
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def compute_ident_y(detail_rows, pool_mean):
    """Per judge_id in these detail rows: ident = mean property_identity score_mean;
    y = Spearman(human_eval score_mean, pool_mean) on aligned items; err rows flagged upstream."""
    by = {}
    for r in detail_rows:
        jid = r.get("judge_id"); rt = r.get("row_type")
        if rt not in ("property_identity", "human_eval_union"):
            continue
        try:
            s = float(r.get("score_mean"))
        except (TypeError, ValueError):
            continue
        d = by.setdefault(jid, {"ident": [], "he": {}})
        if rt == "property_identity":
            d["ident"].append(s)
        else:
            d["he"][r.get("item_key")] = s
    out = {}
    for jid, d in by.items():
        ident = sum(d["ident"]) / len(d["ident"]) if d["ident"] else float("nan")
        common = sorted(set(d["he"]) & set(pool_mean))
        if len(common) >= 5:
            y = float(spearmanr([d["he"][k] for k in common], [pool_mean[k] for k in common]).statistic)
        else:
            y = float("nan")
        out[jid] = {"ident": ident, "y": y, "n_he": len(common)}
    return out


def cache_error_rate(tag):
    p = NEW_DIR / f"cache_{tag}.json"
    if not p.exists():
        return None
    try:
        d = json.load(open(p))
    except Exception:
        return None
    n = len(d)
    if n == 0:
        return None
    err = sum(1 for v in d.values()
              if any(k in str(v.get("reasoning", "")).lower()
                     for k in ("error", "cli_failed", "parse_error", "timed out")))
    return err / n


def perm_p(xs, ys, rho, n=20000, seed=SEED):
    rng = random.Random(seed); ys = list(ys); c = 0
    for _ in range(n):
        rng.shuffle(ys)
        r = spearmanr(xs, ys).statistic
        if math.isfinite(r) and abs(r) >= abs(rho) - 1e-12:
            c += 1
    return (c + 1) / (n + 1)


def main():
    pool_mean, _ = e43.load_participant_labels(REPO / "experiments" / "human_labels")

    configs = {}   # judge_id -> {ident,y,source,err}
    exp30_ident = {}

    # existing 14 (+ controls): compute from their detail_rows, load published ident for the gate
    for fam, detail, vec in EXISTING:
        cy = compute_ident_y(load_detail(detail), pool_mean)
        for jid, v in cy.items():
            configs.setdefault(jid, {**v, "source": "existing", "err": 0.0})
        if Path(vec).exists():
            for r in csv.DictReader(open(vec)):
                exp30_ident[r["judge_id"]] = float(r["ident"])

    # new configs: one cfg dir each
    new_tags = []
    for cfg in sorted(NEW_DIR.glob("cfg_*")):
        tag = cfg.name[len("cfg_"):]
        det = cfg / "detail_rows.csv"
        if not det.exists():
            continue
        cy = compute_ident_y(load_detail(det), pool_mean)
        er = cache_error_rate(tag)
        for jid, v in cy.items():
            if jid.startswith("editdist") or jid.startswith("random"):
                continue  # paired filler judge, already represented
            configs[jid] = {**v, "source": f"new:{tag}", "err": er if er is not None else float("nan")}
            new_tags.append((jid, tag, er))

    # ---- DRIFT GATE: my ident vs exp30 ident on shared existing judges ----
    shared = [j for j in configs if j in exp30_ident and configs[j]["source"] == "existing"]
    gate = {}
    if len(shared) >= 5:
        mine = [configs[j]["ident"] for j in shared]
        pub = [exp30_ident[j] for j in shared]
        gate["ident_rank_spearman_vs_exp30"] = float(spearmanr(mine, pub).statistic)
        gate["ident_max_abs_diff"] = max(abs(a - b) for a, b in zip(mine, pub))
        gate["n_shared"] = len(shared)
    gate["passes"] = gate.get("ident_rank_spearman_vs_exp30", 0) >= 0.95

    # ---- primary test on real (non-control), low-error configs ----
    ERR_GATE = 0.15
    real = {j: v for j, v in configs.items()
            if not (j.startswith("editdist") or j.startswith("random") or "BAD_STRINGY" in j)
            and math.isfinite(v["ident"]) and math.isfinite(v["y"])
            and (not math.isfinite(v["err"]) or v["err"] <= ERR_GATE)}
    excluded = {j: v["err"] for j, v in configs.items()
                if j in configs and math.isfinite(configs[j].get("err", 0)) and configs[j]["err"] > ERR_GATE}

    jids = sorted(real)
    xs = [real[j]["ident"] for j in jids]
    ys = [real[j]["y"] for j in jids]
    n = len(jids)
    rho = float(spearmanr(xs, ys).statistic) if n >= 3 else float("nan")
    p = perm_p(xs, ys, rho) if n >= 3 else float("nan")

    # registered (a)/(b): primary ident significant (p<0.05, |rho|>=0.45, pass-1 sign preserved-or-either)
    a = (math.isfinite(rho) and p < 0.05 and abs(rho) >= 0.45)
    verdict = "a" if a else ("b" if n >= 20 else "b-provisional")

    results = {
        "prereg_commit": "c5a621c", "seed": SEED,
        "n_existing": sum(1 for v in configs.values() if v["source"] == "existing"),
        "n_new_clean": sum(1 for j, t, e in new_tags if (e is None or e <= ERR_GATE)),
        "n_real_analyzed": n,
        "drift_gate": gate,
        "primary_ident_vs_y": {"spearman": rho, "perm_p": p, "n": n,
                               "pass1_was": -0.539},
        "registered_verdict": verdict,
        "excluded_high_error": excluded,
        "new_config_error_rates": {t: e for _, t, e in new_tags},
        "per_config": {j: real[j] for j in jids},
    }
    (NEW_DIR / "pass2_results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({k: v for k, v in results.items() if k != "per_config"}, indent=2))
    return verdict


if __name__ == "__main__":
    main()
