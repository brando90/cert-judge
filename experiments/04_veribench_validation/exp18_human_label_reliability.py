#!/usr/bin/env python3
"""
EXP18A: Human-label reliability analysis (pass1 vs pass2).

Outputs:
  - summary.json
  - pair_rows.csv
  - per_problem_disagreement.csv
  - fig_pass1_vs_pass2_scatter.png
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr
from sklearn.metrics import cohen_kappa_score


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "data"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp18_human_label_reliability"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP18A human label reliability")
    p.add_argument("--pass1-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_20260425.tsv")
    p.add_argument("--pass2-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_ORIGINAL.tsv")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _load_scores(path: Path) -> Dict[Tuple[str, str], float]:
    vals: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            g = str(row.get("gold_file", "")).strip()
            c = str(row.get("candidate_file", "")).strip()
            s = str(row.get("human_score_0_5", "")).strip()
            if not g or not c or not s:
                continue
            vals[(g, c)].append(float(s))
    return {k: float(sum(v) / len(v)) for k, v in vals.items()}


def _bootstrap_ci(x: np.ndarray, y: np.ndarray, fn, n_boot: int, seed: int) -> Tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(x)
    vals: List[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        try:
            v = float(fn(x[idx], y[idx]))
        except Exception:
            continue
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    vals = np.sort(np.asarray(vals))
    lo = float(vals[int(0.025 * (len(vals) - 1))])
    hi = float(vals[int(0.975 * (len(vals) - 1))])
    return (lo, hi)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    p1 = _load_scores(args.pass1_tsv)
    p2 = _load_scores(args.pass2_tsv)

    keys_overlap = sorted(set(p1) & set(p2))
    keys_p1_only = sorted(set(p1) - set(p2))
    keys_p2_only = sorted(set(p2) - set(p1))
    if not keys_overlap:
        raise ValueError("No overlapping labeled pairs between pass1 and pass2")

    rows: List[dict] = []
    x: List[float] = []
    y: List[float] = []
    for g, c in keys_overlap:
        s1 = float(p1[(g, c)])
        s2 = float(p2[(g, c)])
        x.append(s1)
        y.append(s2)
        rows.append(
            {
                "gold_file": g,
                "candidate_file": c,
                "score_pass1": s1,
                "score_pass2": s2,
                "abs_diff": abs(s1 - s2),
                "signed_diff": (s2 - s1),
            }
        )

    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)

    sp = float(spearmanr(xa, ya).statistic)
    pe = float(pearsonr(xa, ya).statistic)
    ke = float(kendalltau(xa, ya).statistic)
    qwk = float(cohen_kappa_score(xa.astype(int), ya.astype(int), weights="quadratic"))
    mae = float(np.mean(np.abs(xa - ya)))
    rmse = float(np.sqrt(np.mean((xa - ya) ** 2)))

    sp_ci = _bootstrap_ci(xa, ya, lambda a, b: spearmanr(a, b).statistic, args.bootstrap_iters, args.seed + 11)
    pe_ci = _bootstrap_ci(xa, ya, lambda a, b: pearsonr(a, b).statistic, args.bootstrap_iters, args.seed + 13)
    ke_ci = _bootstrap_ci(xa, ya, lambda a, b: kendalltau(a, b).statistic, args.bootstrap_iters, args.seed + 17)
    qwk_ci = _bootstrap_ci(
        xa,
        ya,
        lambda a, b: cohen_kappa_score(a.astype(int), b.astype(int), weights="quadratic"),
        args.bootstrap_iters,
        args.seed + 19,
    )

    # Per-problem disagreement
    by_problem: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        pid = Path(r["gold_file"]).stem
        by_problem[pid].append(float(r["abs_diff"]))
    prob_rows = [
        {
            "problem_id": pid,
            "n_pairs": len(v),
            "mean_abs_diff": float(np.mean(v)),
            "max_abs_diff": float(np.max(v)),
        }
        for pid, v in sorted(by_problem.items())
    ]
    prob_rows.sort(key=lambda z: (-z["mean_abs_diff"], z["problem_id"]))

    # Write CSVs
    with (args.out_dir / "pair_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with (args.out_dir / "per_problem_disagreement.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(prob_rows[0].keys()))
        w.writeheader()
        w.writerows(prob_rows)

    # Plot
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    ax.scatter(xa, ya, s=28, alpha=0.8)
    ax.plot([0, 5], [0, 5], "k--", linewidth=1.0)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)
    ax.set_xlabel("Pass1 human score (0-5)")
    ax.set_ylabel("Pass2 human score (0-5)")
    ax.set_title(f"Human label reliability (n={len(rows)})\nSpearman={sp:.3f}, QWK={qwk:.3f}, MAE={mae:.3f}")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_pass1_vs_pass2_scatter.png", dpi=200)
    plt.close(fig)

    summary = {
        "experiment": "exp18_human_label_reliability",
        "n_pass1_pairs": len(p1),
        "n_pass2_pairs": len(p2),
        "n_overlap_pairs": len(rows),
        "n_pass1_only": len(keys_p1_only),
        "n_pass2_only": len(keys_p2_only),
        "metrics": {
            "spearman_r": sp,
            "spearman_ci_lo": float(sp_ci[0]),
            "spearman_ci_hi": float(sp_ci[1]),
            "pearson_r": pe,
            "pearson_ci_lo": float(pe_ci[0]),
            "pearson_ci_hi": float(pe_ci[1]),
            "kendall_tau": ke,
            "kendall_ci_lo": float(ke_ci[0]),
            "kendall_ci_hi": float(ke_ci[1]),
            "quadratic_weighted_kappa": qwk,
            "qwk_ci_lo": float(qwk_ci[0]),
            "qwk_ci_hi": float(qwk_ci[1]),
            "mae_0_5": mae,
            "rmse_0_5": rmse,
        },
        "notes": {
            "overlap_only": "all reliability metrics computed on overlapping pair labels",
            "score_scale": "0-5 ordinal",
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=" * 72)
    print("EXP18A: Human label reliability")
    print(f"n_pass1={len(p1)} n_pass2={len(p2)} overlap={len(rows)} p1_only={len(keys_p1_only)} p2_only={len(keys_p2_only)}")
    print(f"Spearman={sp:.3f} [{sp_ci[0]:.3f},{sp_ci[1]:.3f}]")
    print(f"Pearson={pe:.3f} [{pe_ci[0]:.3f},{pe_ci[1]:.3f}]")
    print(f"Kendall={ke:.3f} [{ke_ci[0]:.3f},{ke_ci[1]:.3f}]")
    print(f"QWK={qwk:.3f} [{qwk_ci[0]:.3f},{qwk_ci[1]:.3f}] | MAE={mae:.3f} RMSE={rmse:.3f}")
    print(f"Wrote: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
