#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--summary-json", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--mono-w", type=float, default=0.4)
    p.add_argument("--stab-w", type=float, default=0.6)
    p.add_argument("--eps", type=float, default=1e-6)
    return p.parse_args()


def _build_x(summary_rows: list[dict], mono_w: float, stab_w: float, eps: float):
    x_base = np.asarray([float(r["cert_index"]) for r in summary_rows], dtype=float)
    mono = np.clip(np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in summary_rows], dtype=float), 0.0, 1.0)
    stab = np.clip(np.asarray([1.0 - float(r["flip_rate"]) for r in summary_rows], dtype=float), 0.0, 1.0)
    x_geom = np.exp(mono_w * np.log(np.clip(mono, eps, 1.0)) + stab_w * np.log(np.clip(stab, eps, 1.0)))
    return x_base, x_geom


def _plot(out_png: Path, rows: list[dict], x_base: np.ndarray, x_geom: np.ndarray, y: np.ndarray, yerr: np.ndarray, title_suffix: str, label_set: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rho_base = float(spearmanr(x_base, y).statistic)
    rho_geom = float(spearmanr(x_geom, y).statistic)

    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.0), sharey=True)
    fig.suptitle(f"Figure 7 Trend Update ({title_suffix})")

    for ax, x, title, xlabel, rho in [
        (axes[0], x_base, "Baseline Index (v1)", "Certification Index v1", rho_base),
        (axes[1], x_geom, "Geometric Trust Index (v3)", "Geometric Trust Index (mono^0.4 * stab^0.6)", rho_geom),
    ]:
        ax.errorbar(x, y, yerr=yerr, fmt="o", markersize=7, alpha=0.95, ecolor="#6aa3d0", color="#1f77b4", capsize=0)
        if len(x) >= 2 and np.std(x) > 0:
            m, b = np.polyfit(x, y, 1)
            xs = np.linspace(float(np.min(x)), float(np.max(x)), 100)
            ax.plot(xs, m * xs + b, "r--", linewidth=1.8)
        for xi, yi, r in zip(x, y, rows):
            ax.text(xi + 0.006, yi + 0.015, r["judge_id"], fontsize=7)
        ax.set_title(f"{title}\nrho={rho:.3f}")
        ax.set_xlabel(xlabel)
        ax.grid(alpha=0.25)

    axes[0].set_ylabel(f"Human Correlation Spearman ({label_set})")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    obj = json.loads(args.summary_json.read_text(encoding="utf-8"))
    rows = obj["judge_rows"]

    y = np.asarray([float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float)
    y_lo = np.asarray([float(r[f"human_spearman_ci_lo_{args.label_set}"]) for r in rows], dtype=float)
    y_hi = np.asarray([float(r[f"human_spearman_ci_hi_{args.label_set}"]) for r in rows], dtype=float)

    x_base, x_geom = _build_x(rows, args.mono_w, args.stab_w, args.eps)

    # Variant 1: 95% CI half-width (original)
    yerr_ci = np.maximum(y_hi - y, y - y_lo)
    _plot(args.out_dir / "fig7_trend_update_baseline_vs_geom_ci95.png", rows, x_base, x_geom, y, yerr_ci, "95% CI", args.label_set)

    # Variant 2: approximate 1SE from CI width
    yerr_1se = (y_hi - y_lo) / (2 * 1.96)
    _plot(args.out_dir / "fig7_trend_update_baseline_vs_geom_1se.png", rows, x_base, x_geom, y, yerr_1se, "1SE (from CI)", args.label_set)

    # Variant 3: repeat-noise proxy SE from CI (shrunken)
    yerr_repeat = yerr_1se / np.sqrt(3.0)
    _plot(args.out_dir / "fig7_trend_update_baseline_vs_geom_repeat_noise_se.png", rows, x_base, x_geom, y, yerr_repeat, "repeat-noise SE proxy", args.label_set)

    out = {
        "summary_json": str(args.summary_json),
        "label_set": args.label_set,
        "outputs": {
            "ci95": str(args.out_dir / "fig7_trend_update_baseline_vs_geom_ci95.png"),
            "1se": str(args.out_dir / "fig7_trend_update_baseline_vs_geom_1se.png"),
            "repeat_noise_se": str(args.out_dir / "fig7_trend_update_baseline_vs_geom_repeat_noise_se.png"),
        },
        "note": "Uncertainty display variants only; correlations unchanged.",
    }
    (args.out_dir / "summary_lowvar_plotting.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
