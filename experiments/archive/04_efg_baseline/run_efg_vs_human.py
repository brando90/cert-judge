#!/usr/bin/env python3
"""
Run EFG baseline (Zhang et al., arXiv:2506.10903) against Ethan's human labels
and certify the judge via cert-judge properties P1-P7 / JTI.

Steps:
  1) Load human labels from experiments/ethan_hand_labels/*.csv
  2) Join each row to gold/candidate Lean files
  3) Score every joinable pair with the EFG judge (direct + oap_wa modes)
  4) Compute correlations with human scores (Pearson/Spearman/Kendall/R^2)
  5) Compute cert-judge properties:
       P1  — Identity: score(X, X) on correct_file_dir
       P2  — Bug monotonicity: AUC on bug ladder
       P3  — Spec monotonicity: AUC on spec ladder
       P4  — Stability: variance across repeated evaluations
       P6  — Human correlation (Spearman, scaled)
  6) Compute JTI from P1-P4 + P6
  7) Save results, plots, and summary
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.efg_judge import efg_judge, efg_judge_direct, efg_judge_oap_wa, EFGResult
from cert_judge.hsj_scoring import (
    compute_p1_identity,
    compute_p2_or_p3_ordering_auc,
    compute_p4_stability,
    compute_jti,
    compute_spearman_scaled,
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EFG baseline vs human labels + cert-judge certification")
    p.add_argument("--labels-dir", type=Path, default=REPO_ROOT / "experiments" / "ethan_hand_labels")
    p.add_argument("--generated-dir", type=Path, default=REPO_ROOT / "data" / "generated_agents")
    p.add_argument("--gold-root", type=Path, default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench")
    p.add_argument("--bug-ladder-dir", type=Path, default=REPO_ROOT / "data" / "file_equiv_08_19_2025" / "my_add_file_eq_with_bugs")
    p.add_argument("--spec-ladder-dir", type=Path, default=REPO_ROOT / "data" / "file_equiv_08_19_2025" / "my_add_file_eq_with_missing_specs")
    p.add_argument("--identity-dir", type=Path, default=REPO_ROOT / "data" / "file_equiv_08_19_2025" / "correct_file_dir")
    p.add_argument("--out-dir", type=Path, default=REPO_ROOT / "experiments" / "archive" / "04_efg_baseline" / "results")
    p.add_argument("--model", type=str, default="gpt-4o-mini")
    p.add_argument("--mode", type=str, default="oap_wa", choices=["direct", "oap_wa", "both"])
    p.add_argument("--n-repeats", type=int, default=3, help="Repeats for P4 stability")
    p.add_argument("--max-rows", type=int, default=0, help="0 = use all")
    p.add_argument("--bootstrap-iters", type=int, default=2000)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


# ---------------------------------------------------------------------------
# Label loading (same logic as 03_human_validation)
# ---------------------------------------------------------------------------
@dataclass
class LabelRow:
    split: str
    gold_ref: str
    candidate_file: str
    human_score: float


def _clean(s: Optional[str]) -> str:
    return (s or "").strip().strip("\ufeff")


def _parse_score(s: str) -> Optional[float]:
    s = _clean(s)
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def _pick(row: Dict[str, str], *keys: str) -> str:
    normalized = {k.strip().lower().replace("\t", ""): v for k, v in row.items()}
    for key in keys:
        k = key.strip().lower().replace("\t", "")
        if k in normalized:
            v = _clean(normalized[k])
            if v:
                return v
    return ""


def load_labels(labels_dir: Path) -> List[LabelRow]:
    rows: List[LabelRow] = []
    for csv_path in sorted(labels_dir.glob("*.csv")):
        split = csv_path.stem
        with csv_path.open(newline="") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                gold_ref = _pick(raw, "gold ref", "gold")
                candidate = _pick(raw, "agent item", "candidate")
                score_str = _pick(raw, "score", "human_score")
                score = _parse_score(score_str)
                if not gold_ref or not candidate or score is None:
                    continue
                rows.append(LabelRow(split=split, gold_ref=gold_ref, candidate_file=candidate, human_score=score))
    return rows


def resolve_gold(gold_root: Path, split: str, gold_ref: str) -> Optional[Path]:
    base = gold_root / split
    p = base / gold_ref
    if p.exists():
        return p
    for q in base.rglob(gold_ref):
        return q
    return None


# ---------------------------------------------------------------------------
# Correlation stats
# ---------------------------------------------------------------------------
def _bootstrap_ci(xs: Sequence[float], ys: Sequence[float], metric: str, n_boot: int = 2000) -> Tuple[float, float]:
    import random
    from scipy.stats import pearsonr, spearmanr, kendalltau

    n = len(xs)
    if n < 3:
        return (float("nan"), float("nan"))

    vals: List[float] = []
    for _ in range(n_boot):
        idxs = [random.randrange(n) for _ in range(n)]
        bx = [xs[i] for i in idxs]
        by = [ys[i] for i in idxs]
        try:
            if metric == "pearson":
                v = float(pearsonr(bx, by).statistic)
            elif metric == "spearman":
                v = float(spearmanr(bx, by).statistic)
            elif metric == "kendall":
                v = float(kendalltau(bx, by).statistic)
            else:
                raise ValueError(metric)
            if math.isfinite(v):
                vals.append(v)
        except Exception:
            continue

    if not vals:
        return (float("nan"), float("nan"))
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return (float(lo), float(hi))


def corr_stats(xs: Sequence[float], ys: Sequence[float], n_boot: int = 2000) -> Dict[str, float]:
    from scipy.stats import pearsonr, spearmanr, kendalltau

    if len(xs) < 3 or len(xs) != len(ys):
        return {"n": len(xs), "pearson_r": float("nan"), "spearman_r": float("nan"),
                "kendall_tau": float("nan"), "r2": float("nan")}

    pr = pearsonr(xs, ys)
    sr = spearmanr(xs, ys)
    kt = kendalltau(xs, ys)
    pr_lo, pr_hi = _bootstrap_ci(xs, ys, "pearson", n_boot)
    sr_lo, sr_hi = _bootstrap_ci(xs, ys, "spearman", n_boot)

    return {
        "n": len(xs),
        "pearson_r": float(pr.statistic),
        "pearson_p": float(pr.pvalue),
        "spearman_r": float(sr.statistic),
        "spearman_p": float(sr.pvalue),
        "kendall_tau": float(kt.statistic),
        "kendall_p": float(kt.pvalue),
        "r2": float(pr.statistic ** 2),
        "pearson_ci_lo": pr_lo,
        "pearson_ci_hi": pr_hi,
        "spearman_ci_lo": sr_lo,
        "spearman_ci_hi": sr_hi,
    }


# ---------------------------------------------------------------------------
# Cert-judge property evaluation
# ---------------------------------------------------------------------------
def eval_p1_identity(identity_dir: Path, model: str, mode: str) -> Tuple[float, List[float]]:
    """P1: Score identity pairs (file scored against itself). Should be high."""
    scores: List[float] = []
    for lean_file in sorted(identity_dir.glob("*.lean")):
        text = lean_file.read_text()
        result = efg_judge(text, text, model=model, mode=mode,
                           cache_namespace=f"efg_p1_{mode}")
        scores.append(result.overall_score)
        print(f"  P1 identity: {lean_file.name} -> {result.overall_score:.3f}")
    p1 = compute_p1_identity(scores)
    return p1, scores


def eval_p2_bug_ladder(bug_dir: Path, model: str, mode: str) -> Tuple[float, List[float]]:
    """P2: Bug monotonicity — scores should decrease as bugs increase."""
    # Reference = 0 bugs file
    ref_file = bug_dir / "my_add_0_bugs.lean"
    if not ref_file.exists():
        return 0.0, []
    ref_text = ref_file.read_text()

    counts: List[int] = []
    scores: List[float] = []
    for lean_file in sorted(bug_dir.glob("my_add_*_bugs.lean")):
        m = re.search(r"_(\d+)_bugs\.lean$", lean_file.name)
        if not m:
            continue
        n_bugs = int(m.group(1))
        gen_text = lean_file.read_text()
        result = efg_judge(ref_text, gen_text, model=model, mode=mode,
                           cache_namespace=f"efg_p2_{mode}")
        counts.append(n_bugs)
        scores.append(result.overall_score)
        print(f"  P2 bug ladder: {lean_file.name} (bugs={n_bugs}) -> {result.overall_score:.3f}")

    p2 = compute_p2_or_p3_ordering_auc(counts, scores)
    return p2, scores


def eval_p3_spec_ladder(spec_dir: Path, model: str, mode: str) -> Tuple[float, List[float]]:
    """P3: Spec monotonicity — scores should decrease as specs are removed."""
    ref_file = spec_dir / "my_add_0_bugs.lean"
    if not ref_file.exists():
        return 0.0, []
    ref_text = ref_file.read_text()

    counts: List[int] = []
    scores: List[float] = []
    for lean_file in sorted(spec_dir.glob("my_add_*_bugs.lean")):
        m = re.search(r"_(\d+)_bugs\.lean$", lean_file.name)
        if not m:
            continue
        n_missing = int(m.group(1))
        gen_text = lean_file.read_text()
        result = efg_judge(ref_text, gen_text, model=model, mode=mode,
                           cache_namespace=f"efg_p3_{mode}")
        counts.append(n_missing)
        scores.append(result.overall_score)
        print(f"  P3 spec ladder: {lean_file.name} (missing={n_missing}) -> {result.overall_score:.3f}")

    p3 = compute_p2_or_p3_ordering_auc(counts, scores)
    return p3, scores


def eval_p4_stability(
    identity_dir: Path, model: str, mode: str, n_repeats: int = 3,
) -> Tuple[float, Dict[str, List[float]]]:
    """P4: Stability — low variance across repeated evaluations."""
    repeat_scores: Dict[str, List[float]] = {}
    for lean_file in sorted(identity_dir.glob("*.lean"))[:3]:  # use a few files
        text = lean_file.read_text()
        item_scores: List[float] = []
        for rep in range(n_repeats):
            result = efg_judge(text, text, model=model, mode=mode,
                               cache_namespace=f"efg_p4_{mode}_r{rep}")
            item_scores.append(result.overall_score)
        repeat_scores[lean_file.name] = item_scores
        print(f"  P4 stability: {lean_file.name} -> scores={item_scores}")

    p4 = compute_p4_stability(repeat_scores, tau=0.05)
    return p4, repeat_scores


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------
def save_plots(scored_rows: List[Dict], out_dir: Path, overall_stats: Dict) -> None:
    try:
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib/numpy not available, skipping plots")
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    human = [r["human_score"] for r in scored_rows]
    judge = [r["efg_score"] for r in scored_rows]

    # Overall scatter
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(human, judge, alpha=0.7, edgecolors="k", linewidths=0.3)
    if len(human) > 1:
        z = np.polyfit(human, judge, 1)
        x = np.linspace(min(human), max(human), 100)
        ax.plot(x, z[0] * x + z[1], "r--", lw=1.5, label="Linear fit")
    pr = overall_stats.get("pearson_r", float("nan"))
    sr = overall_stats.get("spearman_r", float("nan"))
    ax.set_title(f"EFG Judge vs Human (Pearson r={pr:.3f}, Spearman r={sr:.3f})")
    ax.set_xlabel("Human Score")
    ax.set_ylabel("EFG Judge Score")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "fig_efg_vs_human_scatter.png", dpi=180)
    plt.close(fig)

    # Per-split scatter
    splits = sorted(set(r["split"] for r in scored_rows))
    cols = min(3, len(splits))
    rows_n = int(math.ceil(len(splits) / cols)) if cols > 0 else 1
    fig, axes = plt.subplots(rows_n, cols, figsize=(5.5 * cols, 4.5 * rows_n), squeeze=False)
    for i, split in enumerate(splits):
        r_idx, c_idx = divmod(i, cols)
        ax = axes[r_idx][c_idx]
        sdf = [r for r in scored_rows if r["split"] == split]
        sh = [r["human_score"] for r in sdf]
        sj = [r["efg_score"] for r in sdf]
        ax.scatter(sh, sj, alpha=0.7)
        ax.set_title(f"{split} (n={len(sdf)})")
        ax.set_xlabel("Human")
        ax.set_ylabel("EFG")
        ax.grid(True, alpha=0.25)
    for j in range(len(splits), rows_n * cols):
        r_idx, c_idx = divmod(j, cols)
        axes[r_idx][c_idx].axis("off")
    fig.suptitle("EFG vs Human by Split", y=1.01)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_efg_per_split_scatter.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Aspect score distribution
    aspects = ["LP", "MC", "FV", "FQ"]
    aspect_vals = {a: [r.get(f"efg_{a}", 0) for r in scored_rows] for a in aspects}
    fig, ax = plt.subplots(figsize=(8, 5))
    positions = range(len(aspects))
    bp = ax.boxplot([aspect_vals[a] for a in aspects], positions=positions, widths=0.6, patch_artist=True)
    ax.set_xticks(positions)
    ax.set_xticklabels(aspects)
    ax.set_title("EFG Aspect Score Distributions")
    ax.set_ylabel("Score")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_efg_aspect_distributions.png", dpi=180)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    import random

    args = parse_args()
    random.seed(args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    modes = ["direct", "oap_wa"] if args.mode == "both" else [args.mode]

    print("=" * 72)
    print("EFG Baseline (Zhang et al. 2025) vs Human Labels + Cert-Judge")
    print(f"model={args.model}  modes={modes}")
    print("=" * 72)

    for mode in modes:
        print(f"\n{'='*72}")
        print(f"  MODE: {mode}")
        print(f"{'='*72}")

        # --- Phase 1: Score human-labelled pairs ---
        print("\n--- Phase 1: Scoring human-labelled pairs ---")
        label_rows = load_labels(args.labels_dir)
        print(f"Loaded {len(label_rows)} label rows")

        scored_rows: List[Dict[str, Any]] = []
        joinable = 0
        for i, r in enumerate(label_rows):
            candidate_path = args.generated_dir / r.candidate_file
            gold_path = resolve_gold(args.gold_root, r.split, r.gold_ref)

            if not candidate_path.exists() or gold_path is None:
                continue
            joinable += 1

            if args.max_rows and joinable > args.max_rows:
                break

            gold_text = gold_path.read_text()
            candidate_text = candidate_path.read_text()

            result = efg_judge(
                reference_impl=gold_text,
                generated_theorem=candidate_text,
                model=args.model,
                mode=mode,
                cache_namespace=f"efg_human_{mode}",
            )

            row: Dict[str, Any] = {
                "split": r.split,
                "gold_ref": r.gold_ref,
                "candidate_file": r.candidate_file,
                "human_score": r.human_score,
                "efg_score": result.overall_score,
                "efg_LP": result.aspect_scores.get("LP", 0),
                "efg_MC": result.aspect_scores.get("MC", 0),
                "efg_FV": result.aspect_scores.get("FV", 0),
                "efg_FQ": result.aspect_scores.get("FQ", 0),
                "efg_mode": mode,
            }
            scored_rows.append(row)

            print(f"  [{joinable}] {r.split}/{r.candidate_file} | "
                  f"human={r.human_score} efg={result.overall_score:.3f} "
                  f"(LP={result.aspect_scores.get('LP',0):.2f} "
                  f"MC={result.aspect_scores.get('MC',0):.2f} "
                  f"FV={result.aspect_scores.get('FV',0):.2f} "
                  f"FQ={result.aspect_scores.get('FQ',0):.2f})")

        if not scored_rows:
            print("ERROR: no joinable rows")
            return 1

        # Normalize human scores to [0,1] for correlation (they are on 1-5 scale)
        human_scores_raw = [r["human_score"] for r in scored_rows]
        efg_scores = [r["efg_score"] for r in scored_rows]
        # Normalize human to [0,1]: (score - 1) / 4
        human_scores_norm = [(s - 1.0) / 4.0 for s in human_scores_raw]

        # --- Phase 2: Correlation with human labels ---
        print("\n--- Phase 2: Correlation with human labels ---")
        overall_stats = corr_stats(human_scores_norm, efg_scores, args.bootstrap_iters)

        per_split: Dict[str, Dict] = {}
        for split in sorted(set(r["split"] for r in scored_rows)):
            sdf = [r for r in scored_rows if r["split"] == split]
            sh = [(r["human_score"] - 1.0) / 4.0 for r in sdf]
            sj = [r["efg_score"] for r in sdf]
            per_split[split] = corr_stats(sh, sj, args.bootstrap_iters)

        print(f"\nOverall (n={overall_stats['n']}):")
        print(f"  Pearson r  = {overall_stats.get('pearson_r', float('nan')):.4f}")
        print(f"  Spearman r = {overall_stats.get('spearman_r', float('nan')):.4f}")
        print(f"  Kendall τ  = {overall_stats.get('kendall_tau', float('nan')):.4f}")
        print(f"  R²         = {overall_stats.get('r2', float('nan')):.4f}")

        print("\nPer split:")
        for split, stats in sorted(per_split.items()):
            print(f"  {split:16s} n={stats['n']:>3d} | "
                  f"pearson={stats.get('pearson_r', float('nan')):.3f} | "
                  f"spearman={stats.get('spearman_r', float('nan')):.3f}")

        # --- Phase 3: Cert-judge properties ---
        print("\n--- Phase 3: Cert-judge property certification ---")

        print("\n  Computing P1 (Identity)...")
        p1, p1_scores = eval_p1_identity(args.identity_dir, args.model, mode)
        print(f"  P1 = {p1:.4f}")

        print("\n  Computing P2 (Bug Monotonicity)...")
        p2, p2_scores = eval_p2_bug_ladder(args.bug_ladder_dir, args.model, mode)
        print(f"  P2 = {p2:.4f}")

        print("\n  Computing P3 (Spec Monotonicity)...")
        p3, p3_scores = eval_p3_spec_ladder(args.spec_ladder_dir, args.model, mode)
        print(f"  P3 = {p3:.4f}")

        print("\n  Computing P4 (Stability)...")
        p4, p4_repeats = eval_p4_stability(args.identity_dir, args.model, mode, args.n_repeats)
        print(f"  P4 = {p4:.4f}")

        # P6: Human correlation (Spearman, scaled to [0,1])
        p6 = compute_spearman_scaled(human_scores_norm, efg_scores)
        print(f"\n  P6 (Human Correlation, Spearman scaled) = {p6:.4f}")

        # JTI
        jti = compute_jti(p1, p2, p3, p4, p6=p6)
        print(f"\n  JTI = {jti:.4f}")

        # --- Phase 4: Compare with existing judge baseline ---
        # Load the existing gpt-4o-mini coarse-grained results for comparison
        existing_summary_path = (
            REPO_ROOT / "experiments" / "archive" / "03_human_validation" / "results"
            / "ethan_human_vs_judge" / "summary.json"
        )
        comparison = {}
        if existing_summary_path.exists():
            existing = json.loads(existing_summary_path.read_text())
            comparison = {
                "coarse_grained_judge": {
                    "model": existing.get("model", "unknown"),
                    "pearson_r": existing.get("overall", {}).get("pearson_r"),
                    "spearman_r": existing.get("overall", {}).get("spearman_r"),
                    "kendall_tau": existing.get("overall", {}).get("kendall_tau"),
                    "r2": existing.get("overall", {}).get("r2"),
                },
                "efg_judge": {
                    "model": args.model,
                    "mode": mode,
                    "pearson_r": overall_stats.get("pearson_r"),
                    "spearman_r": overall_stats.get("spearman_r"),
                    "kendall_tau": overall_stats.get("kendall_tau"),
                    "r2": overall_stats.get("r2"),
                },
            }
            print("\n--- Comparison: EFG vs Coarse-Grained Judge ---")
            for name, vals in comparison.items():
                print(f"  {name}: pearson={vals.get('pearson_r', 'N/A'):.4f} "
                      f"spearman={vals.get('spearman_r', 'N/A'):.4f}")

        # --- Save all outputs ---
        mode_out_dir = args.out_dir / mode
        mode_out_dir.mkdir(parents=True, exist_ok=True)

        # Scored rows CSV
        try:
            import pandas as pd
            pd.DataFrame(scored_rows).to_csv(mode_out_dir / "scored_rows.csv", index=False)
        except ImportError:
            with (mode_out_dir / "scored_rows.json").open("w") as f:
                json.dump(scored_rows, f, indent=2)

        # Summary JSON
        summary = {
            "experiment": "efg_baseline_vs_human",
            "paper": "Zhang et al., arXiv:2506.10903",
            "model": args.model,
            "mode": mode,
            "n_scored_rows": len(scored_rows),
            "correlation_overall": overall_stats,
            "correlation_per_split": per_split,
            "cert_judge_properties": {
                "P1_identity": p1,
                "P2_bug_monotonicity": p2,
                "P3_spec_monotonicity": p3,
                "P4_stability": p4,
                "P6_human_correlation": p6,
                "JTI": jti,
            },
            "cert_judge_raw": {
                "p1_scores": p1_scores,
                "p2_scores": p2_scores,
                "p3_scores": p3_scores,
                "p4_repeat_scores": {k: list(v) for k, v in p4_repeats.items()},
            },
            "comparison_with_coarse_judge": comparison,
            "efg_weights": {"LP": 0.25, "MC": 0.19, "FV": 0.32, "FQ": 0.24},
        }

        with (mode_out_dir / "summary.json").open("w") as f:
            json.dump(summary, f, indent=2)

        # Plots
        save_plots(scored_rows, mode_out_dir, overall_stats)

        # --- Final report ---
        print(f"\n{'='*72}")
        print(f"  RESULTS SUMMARY — EFG {mode} ({args.model})")
        print(f"{'='*72}")
        print(f"  Human correlation:")
        print(f"    Pearson  r = {overall_stats.get('pearson_r', float('nan')):.4f}")
        print(f"    Spearman r = {overall_stats.get('spearman_r', float('nan')):.4f}")
        print(f"    Kendall  τ = {overall_stats.get('kendall_tau', float('nan')):.4f}")
        print(f"    R²         = {overall_stats.get('r2', float('nan')):.4f}")
        print(f"  Cert-judge properties:")
        print(f"    P1 (Identity)          = {p1:.4f}")
        print(f"    P2 (Bug Monotonicity)  = {p2:.4f}")
        print(f"    P3 (Spec Monotonicity) = {p3:.4f}")
        print(f"    P4 (Stability)         = {p4:.4f}")
        print(f"    P6 (Human Corr)        = {p6:.4f}")
        print(f"    JTI                    = {jti:.4f}")
        print(f"  Outputs: {mode_out_dir}")
        print(f"{'='*72}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
