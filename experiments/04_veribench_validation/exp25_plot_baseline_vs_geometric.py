#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = REPO_ROOT / "experiments/04_veribench_validation/results_exp16_claude_oauth_haiku45_r3_median/summary.json"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments/04_veribench_validation/results_exp22_geometric_trust_index/haiku_mono_stab_40_60"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot baseline vs geometric trust index trend from Exp16 summary")
    p.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--mono-w", type=float, default=0.4)
    p.add_argument("--stab-w", type=float, default=0.6)
    p.add_argument("--eps", type=float, default=1e-6)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    obj = json.loads(args.summary_json.read_text(encoding="utf-8"))
    rows = obj["judge_rows"]

    # y-axis: judge-human correlation for selected label set
    y = np.asarray([float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float)
    y_lo = np.asarray([float(r[f"human_spearman_ci_lo_{args.label_set}"]) for r in rows], dtype=float)
    y_hi = np.asarray([float(r[f"human_spearman_ci_hi_{args.label_set}"]) for r in rows], dtype=float)

    # Baseline x-axis (v1)
    x_base = np.asarray([float(r["cert_index"]) for r in rows], dtype=float)

    # Geometric x-axis (mono^w * stab^(1-w))
    mono = np.clip(np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in rows], dtype=float), 0.0, 1.0)
    stab = np.clip(np.asarray([1.0 - float(r["flip_rate"]) for r in rows], dtype=float), 0.0, 1.0)
    mono_safe = np.clip(mono, args.eps, 1.0)
    stab_safe = np.clip(stab, args.eps, 1.0)
    x_geom = np.exp(args.mono_w * np.log(mono_safe) + args.stab_w * np.log(stab_safe))

    rho_base = float(spearmanr(x_base, y).statistic)
    rho_geom = float(spearmanr(x_geom, y).statistic)
    width_base = float(np.nanmean(y_hi - y_lo))
    width_geom = width_base  # same y-CIs; shown for readability only

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.0), sharey=True)
    fig.suptitle("Figure 7 Trend Update: Baseline vs Meeting-Aligned Geometric Index")

    for ax, x, title, xlabel, rho, cwidth in [
        (
            axes[0],
            x_base,
            "Baseline Index (v1)",
            "Certification Index v1",
            rho_base,
            width_base,
        ),
        (
            axes[1],
            x_geom,
            "Geometric Trust Index (v3)",
            f"Geometric Trust Index (mono^{args.mono_w:g} * stab^{args.stab_w:g})",
            rho_geom,
            width_geom,
        ),
    ]:
        ax.errorbar(
            x,
            y,
            yerr=[y - y_lo, y_hi - y],
            fmt="o",
            markersize=7,
            alpha=0.95,
            ecolor="#6aa3d0",
            color="#1f77b4",
            capsize=0,
        )

        # regression line
        if len(x) >= 2 and np.std(x) > 0:
            m, b = np.polyfit(x, y, 1)
            xs = np.linspace(float(np.min(x)), float(np.max(x)), 100)
            ax.plot(xs, m * xs + b, "r--", linewidth=1.8)

        for xi, yi, r in zip(x, y, rows):
            ax.text(xi + 0.006, yi + 0.015, r["judge_id"], fontsize=7)

        ax.set_title(f"{title}\nrho={rho:.3f}, CI width={cwidth:.3f}")
        ax.set_xlabel(xlabel)
        ax.grid(alpha=0.25)

    axes[0].set_ylabel("Human Correlation Spearman (avg)")
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    out_png = args.out_dir / "fig7_trend_update_baseline_vs_geom.png"
    fig.savefig(out_png, dpi=180)
    plt.close(fig)

    out_summary = {
        "source_summary": str(args.summary_json),
        "label_set": args.label_set,
        "mono_w": args.mono_w,
        "stab_w": args.stab_w,
        "rho_baseline": rho_base,
        "rho_geometric": rho_geom,
        "mean_y_ci_width": width_base,
        "output_plot": str(out_png),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(out_summary, indent=2), encoding="utf-8")
    print(json.dumps(out_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
