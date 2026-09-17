#!/usr/bin/env python3
"""
Create publication-style plots for TVD-MI elicitation crossover results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _load_report(path: Path) -> Dict:
    return json.loads(path.read_text())


def _extract_ladder(report: Dict, condition: str, family: str) -> tuple[np.ndarray, np.ndarray]:
    means = report[condition]["means_by_item"]
    key_prefix = "bugs_" if family == "bugs" else "missing_"
    levels = []
    scores = []
    for k, v in means.items():
        if k.startswith(key_prefix):
            levels.append(int(k.split("_")[1]))
            scores.append(float(v))
    order = np.argsort(levels)
    return np.asarray(levels)[order], np.asarray(scores)[order]


def _extract_identity(report: Dict, condition: str) -> List[float]:
    means = report[condition]["means_by_item"]
    out = []
    for i in range(10):
        out.append(float(means[f"identity_{i}"]))
    return out


def plot_ladders(report: Dict, out_dir: Path) -> None:
    plt.style.use("ggplot")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

    for idx, fam in enumerate(["bugs", "missing_specs"]):
        ax = axes[idx]
        fam_key = "bugs" if fam == "bugs" else "missing_specs"
        for condition, color, label in [
            ("direct", "#CC3311", "Direct"),
            ("tvd_mi", "#0077BB", "TVD-MI"),
        ]:
            levels, scores = _extract_ladder(report, condition, "bugs" if fam == "bugs" else "missing")
            ax.plot(levels, scores, marker="o", linewidth=2.5, color=color, label=label)

        title = "Bug Ladder" if fam_key == "bugs" else "Missing-Spec Ladder"
        ax.set_title(title)
        ax.set_xlabel("Perturbation Level")
        ax.set_xticks(range(10))
        ax.set_ylim(-0.02, 1.03)
        if idx == 0:
            ax.set_ylabel("Mean Judge Score")
        ax.legend(frameon=True)

    fig.suptitle("Score Ladders by Elicitation Protocol", y=1.02, fontsize=16)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_ladders.png", dpi=180, bbox_inches="tight")
    fig.savefig(out_dir / "fig_ladders.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_identity(report: Dict, out_dir: Path) -> None:
    plt.style.use("ggplot")
    direct_vals = _extract_identity(report, "direct")
    tvd_vals = _extract_identity(report, "tvd_mi")

    fig, ax = plt.subplots(figsize=(7, 5.5))
    x = np.array([0] * len(direct_vals) + [1] * len(tvd_vals), dtype=float)
    y = np.array(direct_vals + tvd_vals, dtype=float)

    # Box + jitter
    ax.boxplot(
        [direct_vals, tvd_vals],
        positions=[0, 1],
        widths=0.45,
        showfliers=False,
        patch_artist=True,
        boxprops=dict(facecolor="#EEEEEE"),
    )
    jitter = np.random.default_rng(0).normal(0, 0.05, size=len(x))
    colors = ["#CC3311" if xi < 0.5 else "#0077BB" for xi in x]
    ax.scatter(x + jitter, y, c=colors, alpha=0.85, s=40)

    ax.axhline(0.95, linestyle="--", color="gray", linewidth=1.2, label="Identity threshold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Direct", "TVD-MI"])
    ax.set_ylabel("Identity Score")
    ax.set_ylim(0.80, 1.02)
    ax.set_title("Identity Scores (Meaning-Preserving Inputs)")
    ax.legend(frameon=True, loc="lower right")
    fig.tight_layout()
    fig.savefig(out_dir / "fig_identity_scores.png", dpi=180, bbox_inches="tight")
    fig.savefig(out_dir / "fig_identity_scores.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_violation_bars(report: Dict, out_dir: Path) -> None:
    plt.style.use("ggplot")
    categories = [
        "Identity\nViolation",
        "Monotonicity\nViolation",
        "Inter-run\nPooled Std",
    ]
    direct_vals = [
        float(report["direct"]["identity_violation_rate"]),
        float(report["direct"]["monotonicity_violation_rate"]),
        float(report["direct"]["inter_run_pooled_std"]),
    ]
    tvd_vals = [
        float(report["tvd_mi"]["identity_violation_rate"]),
        float(report["tvd_mi"]["monotonicity_violation_rate"]),
        float(report["tvd_mi"]["inter_run_pooled_std"]),
    ]

    x = np.arange(len(categories))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(x - width / 2, direct_vals, width=width, color="#CC3311", label="Direct")
    ax.bar(x + width / 2, tvd_vals, width=width, color="#0077BB", label="TVD-MI")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Lower is better")
    ax.set_title("Certification Error/Variance Metrics")
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_violation_reliability_bars.png", dpi=180, bbox_inches="tight")
    fig.savefig(out_dir / "fig_violation_reliability_bars.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_reliability_scatter(report: Dict, out_dir: Path) -> None:
    plt.style.use("ggplot")
    direct_stds = report["direct"]["stds_by_item"]
    tvd_stds = report["tvd_mi"]["stds_by_item"]
    keys = sorted(direct_stds.keys())
    x = np.array([float(direct_stds[k]) for k in keys], dtype=float)
    y = np.array([float(tvd_stds[k]) for k in keys], dtype=float)

    fig, ax = plt.subplots(figsize=(6.6, 6))
    ax.scatter(x, y, s=45, alpha=0.85, color="#009988")
    maxv = max(float(np.max(x)), float(np.max(y)), 0.02)
    ax.plot([0, maxv], [0, maxv], linestyle="--", color="gray", linewidth=1.5, label="y=x")
    ax.set_xlabel("Direct per-item run std")
    ax.set_ylabel("TVD-MI per-item run std")
    ax.set_title("Per-item Reliability: TVD-MI vs Direct")
    ax.legend(frameon=True, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_dir / "fig_reliability_scatter.png", dpi=180, bbox_inches="tight")
    fig.savefig(out_dir / "fig_reliability_scatter.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(__file__).parent / "results" / "tvdmi_elicitation_crossover_report.json",
        help="Path to experiment JSON report.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).parent / "figures",
        help="Directory where figures are written.",
    )
    args = parser.parse_args()

    report = _load_report(args.report)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    plot_ladders(report, args.out_dir)
    plot_identity(report, args.out_dir)
    plot_violation_bars(report, args.out_dir)
    plot_reliability_scatter(report, args.out_dir)
    print(f"Wrote figures to: {args.out_dir}")


if __name__ == "__main__":
    main()
