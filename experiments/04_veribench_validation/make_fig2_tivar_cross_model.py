#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "paper_latex" / "ICML_2026" / "figures" / "fig_tivar_scatter_3models_avg_labeled_ci.png"


PANELS = [
    {
        "title": "GPT-5.3-Codex",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_codex_avg.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "judge_rows.csv",
    },
    {
        "title": "Claude Opus 4.7",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_claude_opus_avg.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median" / "judge_rows.csv",
    },
    {
        "title": "Qwen3-Coder-30B",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_qwen_avg.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "13_qwen_replication_exp16_exp19" / "results" / "exp16_qwen_r3_median" / "judge_rows.csv",
    },
]


def short_label(judge_id: str) -> str:
    if judge_id == "editdist_e1":
        return "edit"
    if judge_id == "random_r1":
        return "rand"
    if judge_id.startswith("gpt-4o-mini|"):
        suffix = judge_id.split("|", 1)[1]
        return {
            "P8_STRICT_B": "4o-P8",
            "P4_CHECKLIST": "4o-P4",
        }.get(suffix, f"4o-{suffix}")
    if "|BAD_STRINGY" in judge_id:
        return "BAD"
    if "|P1_BASELINE" in judge_id:
        return "P1"
    if "|P4_CHECKLIST" in judge_id:
        return "P4"
    if "|P8_STRICT_B" in judge_id:
        return "P8"
    return judge_id.split("|")[-1][:10]


def load_panel(tivar_csv: Path, judge_rows_csv: Path) -> list[dict]:
    with tivar_csv.open(newline="", encoding="utf-8") as f:
        trust_rows = {r["judge_id"]: r for r in csv.DictReader(f)}
    with judge_rows_csv.open(newline="", encoding="utf-8") as f:
        judge_rows = {r["judge_id"]: r for r in csv.DictReader(f)}
    common = sorted(set(trust_rows) & set(judge_rows))
    out: list[dict] = []
    for jid in common:
        t = trust_rows[jid]
        j = judge_rows[jid]
        y = float(j["human_spearman_r_avg"])
        lo = float(j["human_spearman_ci_lo_avg"])
        hi = float(j["human_spearman_ci_hi_avg"])
        out.append(
            {
                "judge_id": jid,
                "label": short_label(jid),
                "x": float(t["ti_var_v3"]),
                "y": y,
                "yerr_low": max(0.0, y - lo),
                "yerr_high": max(0.0, hi - y),
            }
        )
    return out


def plot() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.8), sharey=True)
    colors = {
        "P8": "#1f77b4",
        "P4": "#2ca02c",
        "P1": "#ff7f0e",
        "BAD": "#d62728",
        "4o-P8": "#9467bd",
        "4o-P4": "#8c564b",
        "edit": "#7f7f7f",
        "rand": "#bcbd22",
    }

    for ax, panel in zip(axes, PANELS):
        rows = load_panel(panel["tivar_csv"], panel["judge_rows_csv"])
        xs = np.asarray([r["x"] for r in rows], dtype=float)
        ys = np.asarray([r["y"] for r in rows], dtype=float)
        yerr_low = np.asarray([r["yerr_low"] for r in rows], dtype=float)
        yerr_high = np.asarray([r["yerr_high"] for r in rows], dtype=float)

        for i, r in enumerate(rows):
            color = colors.get(r["label"], "#1f77b4")
            ax.scatter(r["x"], r["y"], s=42, color=color, zorder=3)
            ax.errorbar(
                r["x"],
                r["y"],
                yerr=[[yerr_low[i]], [yerr_high[i]]],
                fmt="none",
                ecolor=color,
                alpha=0.55,
                elinewidth=1.0,
                capsize=2,
                zorder=2,
            )
            ax.annotate(
                r["label"],
                (r["x"], r["y"]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=7,
                alpha=0.9,
            )

        if len(xs) >= 2 and float(np.std(xs)) > 1e-12:
            m, b = np.polyfit(xs, ys, 1)
            xline = np.linspace(float(np.min(xs)), float(np.max(xs)), 100)
            ax.plot(xline, m * xline + b, "--", color="#444444", linewidth=1.2, alpha=0.85)

        rho = float(spearmanr(xs, ys).statistic)
        ax.set_title(f"{panel['title']}\n$\\rho$={rho:.3f}", fontsize=10)
        ax.set_xlabel(r"$\mathrm{TI}_{\mathrm{var}}$")
        ax.grid(alpha=0.2, zorder=1)

    axes[0].set_ylabel("Human Spearman (avg labels)")
    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    plot()
