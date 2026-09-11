#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN = REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "ethan_human_scores_20260425.tsv"
DEFAULT_JUDGE = REPO_ROOT / "experiments" / "03_human_validation" / "results" / "ethan_human_vs_judge" / "scored_rows.csv"
DEFAULT_OUT = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp15_human_corr_refresh"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP15: refresh human-vs-judge correlation with updated 0-5 labels")
    p.add_argument("--human-tsv", type=Path, default=DEFAULT_HUMAN)
    p.add_argument("--judge-csv", type=Path, default=DEFAULT_JUDGE)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--perm-iters", type=int, default=20000)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _read_human(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            g = str(r.get("gold_file", "")).strip()
            c = str(r.get("candidate_file", "")).strip()
            hs = str(r.get("human_score_0_5", "")).strip()
            if not g or not c or not hs:
                continue
            rows.append(
                {
                    "gold_file": g,
                    "candidate_file": c,
                    "human_score_0_5": float(hs),
                }
            )
    if not rows:
        raise ValueError(f"No rows loaded from {path}")
    return rows


def _read_judge(path: Path) -> Dict[Tuple[str, str], dict]:
    out: Dict[Tuple[str, str], dict] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            g = str(r.get("gold_ref", "")).strip()
            c = str(r.get("candidate_file", "")).strip()
            s = str(r.get("judge_score", "")).strip()
            split = str(r.get("split", "")).strip()
            if not g or not c or not s:
                continue
            try:
                score = float(s)
            except ValueError:
                continue
            out[(g, c)] = {"judge_score_0_1": score, "split": split}
    return out


def _corr_spearman(x: np.ndarray, y: np.ndarray) -> float:
    return float(spearmanr(x, y).statistic)


def _corr_pearson(x: np.ndarray, y: np.ndarray) -> float:
    return float(pearsonr(x, y).statistic)


def _corr_kendall(x: np.ndarray, y: np.ndarray) -> float:
    return float(kendalltau(x, y).statistic)


def _bootstrap_ci(
    x: np.ndarray,
    y: np.ndarray,
    problem_ids: np.ndarray,
    fn: Callable[[np.ndarray, np.ndarray], float],
    n_boot: int,
    seed: int,
) -> Tuple[float, float]:
    # Cluster bootstrap at problem level for robust uncertainty.
    rng = np.random.default_rng(seed)
    unique_probs = np.unique(problem_ids)
    vals: List[float] = []
    for _ in range(n_boot):
        sampled = rng.choice(unique_probs, size=len(unique_probs), replace=True)
        idx: List[int] = []
        for p in sampled:
            idx.extend(np.where(problem_ids == p)[0].tolist())
        if len(idx) < 3:
            continue
        xb = x[idx]
        yb = y[idx]
        v = fn(xb, yb)
        if math.isfinite(v):
            vals.append(float(v))
    if not vals:
        return (float("nan"), float("nan"))
    arr = np.sort(np.asarray(vals, dtype=float))
    lo = float(arr[int(0.025 * (len(arr) - 1))])
    hi = float(arr[int(0.975 * (len(arr) - 1))])
    return (lo, hi)


def _perm_pvalue(
    x: np.ndarray,
    y: np.ndarray,
    fn: Callable[[np.ndarray, np.ndarray], float],
    n_perm: int,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    obs = fn(x, y)
    if not math.isfinite(obs):
        return float("nan")
    vals = []
    for _ in range(n_perm):
        yp = rng.permutation(y)
        v = fn(x, yp)
        if math.isfinite(v):
            vals.append(abs(v))
    if not vals:
        return float("nan")
    vals_arr = np.asarray(vals, dtype=float)
    return float((1 + np.sum(vals_arr >= abs(obs))) / (1 + len(vals_arr)))


def _metric_block(
    x: np.ndarray,
    y: np.ndarray,
    problem_ids: np.ndarray,
    n_boot: int,
    n_perm: int,
    seed: int,
) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for name, fn in [
        ("spearman", _corr_spearman),
        ("pearson", _corr_pearson),
        ("kendall", _corr_kendall),
    ]:
        point = fn(x, y)
        lo, hi = _bootstrap_ci(x, y, problem_ids, fn, n_boot, seed)
        p = _perm_pvalue(x, y, fn, n_perm, seed + 7)
        out[name] = {
            "r": float(point),
            "ci_lo": float(lo),
            "ci_hi": float(hi),
            "perm_p": float(p),
        }
    return out


def _split_from_name(gold_file: str) -> str:
    g = gold_file.lower()
    if g.startswith("humaneval_"):
        return "humaneval_set"
    if "unsafe" in g or "pathtraversal" in g or "formatstring" in g:
        return "security_6858"
    if "my" in g:
        return "easy_set"
    if any(k in g for k in ["bisect", "heap", "json_decoder"]):
        return "real_code"
    if any(k in g for k in ["sort", "binary_search"]):
        return "cs_set"
    return "unknown"


def _save_scatter(rows: List[dict], out_path: Path) -> None:
    xs = np.array([r["human_score_0_5"] for r in rows], dtype=float)
    ys = np.array([r["judge_score_0_5"] for r in rows], dtype=float)
    plt.figure(figsize=(7, 6))
    plt.scatter(xs, ys, alpha=0.8, s=40, c="#1f77b4")
    m, b = np.polyfit(xs, ys, 1)
    xline = np.linspace(xs.min(), xs.max(), 100)
    plt.plot(xline, m * xline + b, c="#d62728", linewidth=2)
    plt.xlabel("Human score (0-5)")
    plt.ylabel("Judge score rescaled to 0-5")
    plt.title("EXP15: Human vs Judge Scores (Updated Labels)")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def _save_split_bars(split_stats: Dict[str, float], out_path: Path) -> None:
    labels = list(split_stats.keys())
    vals = [split_stats[k] for k in labels]
    plt.figure(figsize=(8, 4))
    plt.bar(labels, vals, color="#2ca02c")
    plt.ylim(-1.0, 1.0)
    plt.ylabel("Spearman(human, judge)")
    plt.title("EXP15: Per-Split Human Alignment")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    human = _read_human(args.human_tsv)
    judge_map = _read_judge(args.judge_csv)

    merged: List[dict] = []
    missing: List[dict] = []
    for r in human:
        key = (r["gold_file"], r["candidate_file"])
        j = judge_map.get(key)
        if j is None:
            missing.append(r)
            continue
        merged.append(
            {
                "gold_file": r["gold_file"],
                "candidate_file": r["candidate_file"],
                "problem_id": Path(r["gold_file"]).stem,
                "split": j["split"] or _split_from_name(r["gold_file"]),
                "human_score_0_5": float(r["human_score_0_5"]),
                "human_score_0_1": float(r["human_score_0_5"]) / 5.0,
                "judge_score_0_1": float(j["judge_score_0_1"]),
                "judge_score_0_5": 5.0 * float(j["judge_score_0_1"]),
            }
        )

    if len(merged) < 10:
        raise ValueError(f"Too few merged rows: {len(merged)}")

    x = np.asarray([r["human_score_0_5"] for r in merged], dtype=float)
    y = np.asarray([r["judge_score_0_5"] for r in merged], dtype=float)
    pids = np.asarray([r["problem_id"] for r in merged], dtype=object)

    metrics = _metric_block(
        x=x,
        y=y,
        problem_ids=pids,
        n_boot=args.bootstrap_iters,
        n_perm=args.perm_iters,
        seed=args.seed,
    )

    mae = float(np.mean(np.abs(x - y)))
    rmse = float(np.sqrt(np.mean((x - y) ** 2)))

    # Per-split Spearman only (for readability).
    split_rows: Dict[str, List[dict]] = {}
    for r in merged:
        split_rows.setdefault(r["split"], []).append(r)
    split_stats: Dict[str, float] = {}
    for split, rows in sorted(split_rows.items()):
        xs = np.asarray([rr["human_score_0_5"] for rr in rows], dtype=float)
        ys = np.asarray([rr["judge_score_0_5"] for rr in rows], dtype=float)
        split_stats[split] = float(spearmanr(xs, ys).statistic) if len(rows) >= 3 else float("nan")

    # Save merged rows.
    merged_csv = args.out_dir / "merged_rows.csv"
    with merged_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "split",
                "problem_id",
                "gold_file",
                "candidate_file",
                "human_score_0_5",
                "human_score_0_1",
                "judge_score_0_1",
                "judge_score_0_5",
            ],
        )
        writer.writeheader()
        for r in merged:
            writer.writerow(r)

    miss_csv = args.out_dir / "missing_pairs.csv"
    with miss_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["gold_file", "candidate_file", "human_score_0_5"])
        writer.writeheader()
        for r in missing:
            writer.writerow(r)

    _save_scatter(merged, args.out_dir / "fig_human_vs_judge_scatter.png")
    _save_split_bars(split_stats, args.out_dir / "fig_per_split_spearman.png")

    summary = {
        "experiment": "exp15_human_corr_refresh",
        "n_merged_rows": len(merged),
        "n_missing_pairs": len(missing),
        "bootstrap_iters": args.bootstrap_iters,
        "perm_iters": args.perm_iters,
        "seed": args.seed,
        "overall_metrics_0to5": metrics,
        "error_metrics_0to5": {"mae": mae, "rmse": rmse},
        "per_split_spearman_0to5": split_stats,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = []
    md.append("# EXP15: Updated Human Correlation (0-5)")
    md.append("")
    md.append(f"- Merged rows: {len(merged)}")
    md.append(f"- Missing pairs: {len(missing)}")
    md.append(f"- MAE (0-5): {mae:.3f}")
    md.append(f"- RMSE (0-5): {rmse:.3f}")
    md.append("")
    for k in ["spearman", "pearson", "kendall"]:
        m = metrics[k]
        md.append(
            f"- {k.capitalize()}: r={m['r']:.3f}, 95% CI [{m['ci_lo']:.3f}, {m['ci_hi']:.3f}], perm p={m['perm_p']:.4f}"
        )
    md.append("")
    md.append("## Per-Split Spearman")
    md.append("")
    for split, r in sorted(split_stats.items()):
        md.append(f"- {split}: {r:.3f}")
    (args.out_dir / "results_summary.md").write_text("\n".join(md), encoding="utf-8")

    print("========================================================================")
    print("EXP15: Updated Human Correlation (0-5)")
    print(f"merged_rows={len(merged)} missing_pairs={len(missing)}")
    for k in ["spearman", "pearson", "kendall"]:
        m = metrics[k]
        print(f"  {k}: r={m['r']:.3f} CI=[{m['ci_lo']:.3f},{m['ci_hi']:.3f}] perm_p={m['perm_p']:.4f}")
    print(f"  MAE={mae:.3f} RMSE={rmse:.3f}")
    print(f"Wrote: {args.out_dir}")


if __name__ == "__main__":
    main()
