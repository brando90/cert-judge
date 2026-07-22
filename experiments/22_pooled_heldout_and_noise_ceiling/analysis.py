#!/usr/bin/env python3
"""
EXP44 (dir 22): Pooled frozen held-out analysis + held-out-pool noise ceiling.

Decision analysis for the TMLR submission. Two questions, using ONLY existing
artifacts (no new judge scoring, no LLM calls, no new human labels):

  A. POOLED POWER: exp43 reported frozen-TIvar held-out correlations per family
     (n=8 judges each, CIs spanning zero — uninformative). Pooling all family
     panels raises n. Does the pooled/frozen relationship look positive, null,
     or negative once power increases?
     NOTE: pooling was chosen AFTER seeing the per-family nulls -> this is an
     EXPLORATORY (post-hoc) analysis. It informs the submit/hold decision; it
     is not a pre-registered confirmatory result.

  B. NOISE CEILING: the held-out target is the mean of participant1-5 labels.
     If raters barely agree with each other, no judge can correlate highly with
     their mean. Estimate the achievable ceiling via inter-rater agreement +
     Spearman-Brown, and compare judges against leave-one-rater-out humans.

Reuses exp43's exact loaders (imported, not copied) so data handling is
identical to the published stress test. Deterministic: seed 42 everywhere.

Outputs (in results/):
  results.json     - all numbers, machine-readable
  REPORT.md        - human-readable report with decision recommendation
  pooled_scatter.png (if matplotlib available)
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments" / "04_veribench_validation"))

import exp43_frozen_tivar_heldout as e43  # noqa: E402  (loaders + _spearman)

SEED = 42
N_BOOT = 5000
N_PERM = 20000
CONTROL_IDS = ("editdist_e1", "random_r1")


def is_control_or_bad(jid: str) -> bool:
    return jid in CONTROL_IDS or "BAD_STRINGY" in jid


# ---------------------------------------------------------------------------
# Load per-judge rows exactly as exp43 does, but keep every (family, judge) row
# ---------------------------------------------------------------------------

def load_rows():
    participant_mean, per_rater = e43.load_participant_labels(e43.DEFAULT_HUMAN_DIR)
    rows = []
    for panel in e43.PANELS:
        tivar = e43.load_tivar(panel["tivar_csv"])
        item_scores = e43.load_judge_item_scores(panel["detail_rows_csv"])
        heldout = e43.compute_heldout_human_spearman(item_scores, participant_mean)
        calib = e43.load_calib_human_spearman(panel["judge_rows_csv"])
        common = sorted(set(tivar) & set(heldout) & set(calib))
        for j in common:
            rows.append({
                "family": panel["family_key"],
                "judge_id": j,
                "tivar": tivar[j],
                "rho_heldout_items": heldout[j],
            })
    return rows, participant_mean, per_rater


# ---------------------------------------------------------------------------
# A. Pooled analyses
# ---------------------------------------------------------------------------

def pooled_spearman(rows):
    xs = [r["tivar"] for r in rows]
    ys = [r["rho_heldout_items"] for r in rows]
    return e43._spearman(xs, ys)


def clustered_bootstrap_ci(rows, n=N_BOOT, seed=SEED, alpha=0.05):
    """Bootstrap resampling CLUSTERS = unique judge configs (shared configs
    appear in several family panels and are not independent)."""
    rng = random.Random(seed)
    clusters = defaultdict(list)
    for r in rows:
        clusters[r["judge_id"]].append(r)
    keys = sorted(clusters)
    rhos = []
    for _ in range(n):
        sample_rows = []
        for _ in keys:
            sample_rows.extend(clusters[rng.choice(keys)])
        rho = pooled_spearman(sample_rows)
        if math.isfinite(rho):
            rhos.append(rho)
    rhos.sort()
    lo = rhos[int(alpha / 2 * len(rhos))]
    hi = rhos[min(int((1 - alpha / 2) * len(rhos)), len(rhos) - 1)]
    return lo, hi


def within_family_centered(rows):
    """Subtract family means from x and y -> removes family-level confounds."""
    fam_x = defaultdict(list)
    fam_y = defaultdict(list)
    for r in rows:
        fam_x[r["family"]].append(r["tivar"])
        fam_y[r["family"]].append(r["rho_heldout_items"])
    mx = {f: sum(v) / len(v) for f, v in fam_x.items()}
    my = {f: sum(v) / len(v) for f, v in fam_y.items()}
    return [
        {**r,
         "tivar": r["tivar"] - mx[r["family"]],
         "rho_heldout_items": r["rho_heldout_items"] - my[r["family"]]}
        for r in rows
    ]


def permutation_p_within_family(rows, n=N_PERM, seed=SEED):
    """Two-sided permutation test shuffling y within family blocks."""
    rng = random.Random(seed)
    obs = pooled_spearman(within_family_centered(rows))
    fams = defaultdict(list)
    for i, r in enumerate(rows):
        fams[r["family"]].append(i)
    ys = [r["rho_heldout_items"] for r in rows]
    count = 0
    for _ in range(n):
        perm_y = ys[:]
        for f, idxs in fams.items():
            vals = [ys[i] for i in idxs]
            rng.shuffle(vals)
            for i, v in zip(idxs, vals):
                perm_y[i] = v
        perm_rows = [
            {**r, "rho_heldout_items": perm_y[i]} for i, r in enumerate(rows)
        ]
        rho = pooled_spearman(within_family_centered(perm_rows))
        if math.isfinite(rho) and abs(rho) >= abs(obs) - 1e-12:
            count += 1
    return obs, (count + 1) / (n + 1)


def unique_config_rows(rows):
    """Collapse shared configs (mean of x and of y across their panels)."""
    grp = defaultdict(list)
    for r in rows:
        grp[r["judge_id"]].append(r)
    out = []
    for j, rs in sorted(grp.items()):
        out.append({
            "family": "shared" if len(rs) > 1 else rs[0]["family"],
            "judge_id": j,
            "tivar": sum(r["tivar"] for r in rs) / len(rs),
            "rho_heldout_items": sum(r["rho_heldout_items"] for r in rs) / len(rs),
        })
    return out


def simple_bootstrap_ci(rows, n=N_BOOT, seed=SEED, alpha=0.05):
    xs = [r["tivar"] for r in rows]
    ys = [r["rho_heldout_items"] for r in rows]
    return e43.bootstrap_ci(xs, ys, n=n, seed=seed, alpha=alpha)


# ---------------------------------------------------------------------------
# B. Noise ceiling of the participant pool
# ---------------------------------------------------------------------------

def noise_ceiling(per_rater):
    raters = sorted(per_rater)
    pairwise = []
    for i in range(len(raters)):
        for j in range(i + 1, len(raters)):
            a, b = per_rater[raters[i]], per_rater[raters[j]]
            common = sorted(set(a) & set(b))
            if len(common) < 10:
                continue
            rho = e43._spearman([a[k] for k in common], [b[k] for k in common])
            pairwise.append({"pair": f"{raters[i]}~{raters[j]}",
                             "n_overlap": len(common), "spearman": rho})
    if not pairwise:
        return None
    tot = sum(p["n_overlap"] for p in pairwise)
    rbar = sum(p["spearman"] * p["n_overlap"] for p in pairwise) / tot
    rbar_unw = sum(p["spearman"] for p in pairwise) / len(pairwise)

    items = set()
    for r in raters:
        items |= set(per_rater[r])
    k_per_item = [sum(1 for r in raters if it in per_rater[r]) for it in items]
    k_eff = sum(k_per_item) / len(k_per_item)

    def rel(k, r):
        return k * r / (1 + (k - 1) * r) if r > 0 else float("nan")

    # Leave-one-rater-out: each rater vs mean of the others (empirical human bar)
    loo = []
    for r in raters:
        xs, ys = [], []
        for it in per_rater[r]:
            others = [per_rater[o][it] for o in raters if o != r and it in per_rater[o]]
            if others:
                xs.append(per_rater[r][it])
                ys.append(sum(others) / len(others))
        if len(xs) >= 10:
            loo.append({"rater": r, "n": len(xs), "spearman_vs_rest": e43._spearman(xs, ys)})

    return {
        "n_raters": len(raters),
        "n_items": len(items),
        "n_labels": sum(len(per_rater[r]) for r in raters),
        "k_eff_raters_per_item": k_eff,
        "pairwise": pairwise,
        "mean_pairwise_spearman_weighted": rbar,
        "mean_pairwise_spearman_unweighted": rbar_unw,
        "reliability_mean_of_k_eff": rel(k_eff, rbar),
        "reliability_mean_of_5": rel(5, rbar),
        "ceiling_rho_vs_mean_k_eff": math.sqrt(rel(k_eff, rbar)) if rbar > 0 else float("nan"),
        "ceiling_rho_vs_mean_5": math.sqrt(rel(5, rbar)) if rbar > 0 else float("nan"),
        "leave_one_rater_out": loo,
        "loo_mean": (sum(l["spearman_vs_rest"] for l in loo) / len(loo)) if loo else float("nan"),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = HERE / "results"
    out_dir.mkdir(exist_ok=True)

    rows, participant_mean, per_rater = load_rows()
    uniq = unique_config_rows(rows)

    # --- A: pooled ---
    rho_pooled = pooled_spearman(rows)
    ci_pooled = clustered_bootstrap_ci(rows)
    rho_uniq = pooled_spearman(uniq)
    ci_uniq = simple_bootstrap_ci(uniq)
    rho_cent, p_cent = permutation_p_within_family(rows)
    uniq_real = [r for r in uniq if not is_control_or_bad(r["judge_id"])]
    rho_uniq_real = pooled_spearman(uniq_real)
    ci_uniq_real = simple_bootstrap_ci(uniq_real)

    # --- B: ceiling ---
    ceil = noise_ceiling(per_rater)

    # Judge-vs-pool context: how close do judges get to the human LOO bar?
    real = [r for r in uniq if not is_control_or_bad(r["judge_id"])]
    real_sorted = sorted(real, key=lambda r: r["rho_heldout_items"], reverse=True)
    judge_context = {
        "n_unique_configs": len(uniq),
        "n_real_judges": len(real),
        "best_real_judge": real_sorted[0] if real_sorted else None,
        "median_real_judge_rho": (
            sorted(r["rho_heldout_items"] for r in real)[len(real) // 2] if real else float("nan")
        ),
        "all_real_judges": real_sorted,
    }

    results = {
        "seed": SEED, "n_bootstrap": N_BOOT, "n_permutation": N_PERM,
        "n_rows_pooled": len(rows),
        "n_unique_configs": len(uniq),
        "A_pooled": {
            "rho_pooled_all_rows": rho_pooled,
            "ci_clustered_bootstrap": list(ci_pooled),
            "rho_unique_configs": rho_uniq,
            "ci_unique_configs": list(ci_uniq),
            "rho_unique_real_judges_only": rho_uniq_real,
            "ci_unique_real_judges_only": list(ci_uniq_real),
            "rho_within_family_centered": rho_cent,
            "permutation_p_two_sided_within_family": p_cent,
        },
        "B_noise_ceiling": ceil,
        "judge_context": judge_context,
        "rows": rows,
    }
    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({k: v for k, v in results.items() if k != "rows"}, indent=2))

    # Optional scatter
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        colors = {"codex": "#1f77b4", "claude_opus": "#9467bd",
                  "qwen": "#d62728", "leanstral": "#2ca02c"}
        fig, ax = plt.subplots(figsize=(6, 5))
        for r in rows:
            ax.scatter(r["tivar"], r["rho_heldout_items"],
                       color=colors.get(r["family"], "gray"), alpha=0.75, s=48)
        ax.set_xlabel("Frozen TI_var (exp30 weighting)")
        ax.set_ylabel("Held-out human Spearman (participant mean)")
        ax.set_title(
            f"Pooled frozen held-out: rho={rho_pooled:.3f} "
            f"CI[{ci_pooled[0]:.2f},{ci_pooled[1]:.2f}] (n={len(rows)} rows, "
            f"{len(uniq)} unique configs)")
        ax.axhline(0, color="gray", lw=0.5)
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(out_dir / "pooled_scatter.png", dpi=150)
        print("wrote pooled_scatter.png")
    except Exception as exc:  # matplotlib optional
        print(f"plot skipped: {exc}")


if __name__ == "__main__":
    main()
