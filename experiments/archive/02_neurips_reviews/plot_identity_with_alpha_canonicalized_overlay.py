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


def _make_overlay_plot(rows: list[dict], out_png: Path, policy: str) -> dict:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    # Map by file so ALPHA can be canonicalized using STYLE from same file.
    by_file: dict[str, dict[str, float]] = defaultdict(dict)
    for r in rows:
        by_file[r["file"]][r["variant_type"].upper()] = float(r["judge_mean"])

    variant_order = ["RENAME", "REORDER", "STYLE", "ALPHA"]

    original_by_variant: dict[str, list[float]] = defaultdict(list)
    canon_by_variant: dict[str, list[float]] = defaultdict(list)

    for _, vmap in by_file.items():
        for v in variant_order:
            if v in vmap:
                original_by_variant[v].append(vmap[v])

        # canonicalized proxy: keep all non-ALPHA unchanged, canonicalize ALPHA
        for v in variant_order:
            if v == "ALPHA":
                if "ALPHA" not in vmap:
                    continue
                if policy == "drop":
                    # dropped from canonicalized aggregate
                    continue
                # clip policy: replace ALPHA with STYLE score from same file if available
                if "STYLE" in vmap:
                    canon_by_variant[v].append(vmap["STYLE"])
                else:
                    canon_by_variant[v].append(vmap["ALPHA"])
            else:
                if v in vmap:
                    canon_by_variant[v].append(vmap[v])

    labels = [v for v in variant_order if v in original_by_variant]
    orig_means = [_mean(original_by_variant[v]) for v in labels]
    orig_stds = [_std(original_by_variant[v]) for v in labels]

    canon_means = []
    canon_stds = []
    for v in labels:
        # Only show the canonicalized overlay on ALPHA (far-right bar).
        if v != "ALPHA":
            canon_means.append(float("nan"))
            canon_stds.append(0.0)
            continue
        vals = canon_by_variant.get(v, [])
        canon_means.append(_mean(vals) if vals else float("nan"))
        canon_stds.append(_std(vals) if vals else 0.0)

    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.bar(
        x - width / 2,
        orig_means,
        yerr=orig_stds,
        capsize=5,
        color="#4c78a8",
        alpha=0.88,
        width=width,
        label="Original",
    )
    ax.bar(
        x + width / 2,
        canon_means,
        yerr=canon_stds,
        capsize=5,
        color="#f58518",
        alpha=0.88,
        width=width,
        label=f"Alpha-canonicalized ({policy})",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Judge Score")
    ax.set_title("Identity Property (With Std Dev Error Bounds)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)

    # Summaries specifically for ALPHA variance reduction
    out = {
        "policy": policy,
        "alpha_original_mean": _mean(original_by_variant.get("ALPHA", [])),
        "alpha_original_std": _std(original_by_variant.get("ALPHA", [])),
        "alpha_canon_mean": _mean(canon_by_variant.get("ALPHA", [])) if canon_by_variant.get("ALPHA") else None,
        "alpha_canon_std": _std(canon_by_variant.get("ALPHA", [])) if canon_by_variant.get("ALPHA") else None,
        "variants": labels,
        "output_plot": str(out_png),
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Overlay original vs alpha-canonicalized identity error-bar plot")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("experiments/02_neurips_reviews/results/codex_api_gpt53_r3_20260418_230027"),
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=Path("paper_latex/NeurIPS_2025/figures/codex_api_gpt53_r3_20260418_230027"),
    )
    parser.add_argument("--alpha-policy", choices=["clip", "drop"], default="clip")
    args = parser.parse_args()

    identity_rows = _read_csv(args.results_dir / "identity_rows.csv")
    out_png = args.figures_dir / f"identity_property_with_std_error_bounds_alpha_{args.alpha_policy}_overlay.png"
    summary = _make_overlay_plot(identity_rows, out_png, policy=args.alpha_policy)

    summary_path = args.figures_dir / f"identity_property_alpha_overlay_{args.alpha_policy}_summary.json"
    summary_path.write_text(__import__("json").dumps(summary, indent=2), encoding="utf-8")

    print(out_png)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
