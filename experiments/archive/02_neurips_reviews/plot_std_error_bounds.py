#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _std(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def _make_identity_plot(rows: list[dict], out_png: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    by_variant: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        by_variant[r["variant_type"]].append(float(r["judge_mean"]))

    variant_order = ["RENAME", "REORDER", "STYLE", "ALPHA"]
    labels = [v for v in variant_order if v in by_variant] + [
        v for v in sorted(by_variant.keys()) if v not in variant_order
    ]
    means = [_mean(by_variant[v]) for v in labels]
    stds = [_std(by_variant[v]) for v in labels]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.bar(x, means, yerr=stds, capsize=5, color="#4c78a8", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Judge Score")
    ax.set_title("Identity Property (With Std Dev Error Bounds)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def _make_ladder_plot(rows: list[dict], title: str, out_png: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    by_level: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        by_level[int(r["level"])].append(float(r["judge_mean"]))

    levels = sorted(by_level.keys())
    means = [_mean(by_level[l]) for l in levels]
    stds = [_std(by_level[l]) for l in levels]

    x = np.array(levels)
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.plot(x, means, color="#1f77b4", marker="o", linewidth=2.2)
    ax.fill_between(x, np.array(means) - np.array(stds), np.array(means) + np.array(stds), alpha=0.2)
    ax.errorbar(x, means, yerr=stds, fmt="none", ecolor="#1f77b4", elinewidth=1.5, capsize=4)
    ax.set_xticks(x)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("Degradation Level")
    ax.set_ylabel("Judge Score")
    ax.set_title(title)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create additional sanity-property plots with std-dev error bounds.")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("experiments/archive/02_neurips_reviews/results/codex_api_gpt53_r3_20260418_230027"),
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=Path("experiments/archive/02_neurips_reviews/figures/codex_api_gpt53_r3_20260418_230027"),
    )
    args = parser.parse_args()

    identity_rows = _read_csv(args.results_dir / "identity_rows.csv")
    bug_rows = _read_csv(args.results_dir / "bug_ladder_rows.csv")
    missing_rows = _read_csv(args.results_dir / "missing_ladder_rows.csv")

    _make_identity_plot(identity_rows, args.figures_dir / "identity_property_with_std_error_bounds.png")
    _make_ladder_plot(
        bug_rows,
        "Monotonicity vs Bugs (With Std Dev Error Bounds)",
        args.figures_dir / "monotonicity_bugs_with_std_error_bounds.png",
    )
    _make_ladder_plot(
        missing_rows,
        "Monotonicity vs Missing Specs (With Std Dev Error Bounds)",
        args.figures_dir / "monotonicity_missing_specs_with_std_error_bounds.png",
    )

    print(args.figures_dir / "identity_property_with_std_error_bounds.png")
    print(args.figures_dir / "monotonicity_bugs_with_std_error_bounds.png")
    print(args.figures_dir / "monotonicity_missing_specs_with_std_error_bounds.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

