#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "results_exp32_new_human_isotonic_certjudge"
)
PLOTS_DIR = RESULTS_DIR / "plots"
PAPER_FIG_DIR = (
    REPO_ROOT
    / "paper_latex"
    / "ICML_2026_AI4Math"
    / "figures"
    / "exp32_new_human_isotonic"
)


COLORS = {
    "gpt-5.3-codex": "#1f77b4",
    "claude-opus-4-7": "#9467bd",
    "labs-leanstral-2603": "#2ca02c",
    "gpt-4o-mini": "#8c564b",
    "na": "#7f7f7f",
    "random": "#bcbd22",
}


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 8.2,
            "axes.labelsize": 7.8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 6.6,
            "figure.dpi": 180,
            "savefig.dpi": 240,
            "axes.linewidth": 0.8,
        }
    )


def model_color(model: object, kind: object | None = None) -> str:
    model_s = str(model) if pd.notna(model) else "na"
    kind_s = str(kind) if kind is not None and pd.notna(kind) else ""
    if kind_s == "random" or "random" in model_s:
        return COLORS["random"]
    return COLORS.get(model_s, "#1f77b4")


def short_label(judge_id: str) -> str:
    if judge_id == "editdist_e1":
        return "Edit distance"
    if judge_id == "random_r1":
        return "Random"
    if "|" not in judge_id:
        return judge_id
    model, prompt = judge_id.split("|", 1)
    model_label = {
        "gpt-5.3-codex": "GPT-5.3 Codex",
        "claude-opus-4-7": "Claude Opus 4.7",
        "labs-leanstral-2603": "LeanStral",
        "gpt-4o-mini": "GPT-4o mini",
    }.get(model, model)
    prompt_label = {
        "P1_BASELINE": "P1 baseline",
        "P4_CHECKLIST": "P4 checklist",
        "P8_STRICT_B": "P8 strict",
        "BAD_STRINGY": "Bad stringy",
        "P20_TC_RATER_CARD": "TC rater",
    }.get(prompt, prompt.replace("_", " ").title())
    return f"{model_label}\n{prompt_label}"


def add_ols(ax: plt.Axes, x: np.ndarray, y: np.ndarray, color: str = "#b22222") -> None:
    keep = np.isfinite(x) & np.isfinite(y)
    if int(keep.sum()) < 2 or float(np.std(x[keep])) <= 1e-12:
        return
    m, b = np.polyfit(x[keep], y[keep], 1)
    xline = np.linspace(float(np.min(x[keep])), float(np.max(x[keep])), 100)
    ax.plot(xline, m * xline + b, "--", color=color, linewidth=1.3, alpha=0.78, zorder=2)


def finish_axes(ax: plt.Axes) -> None:
    ax.grid(True, color="#d9d9d9", linewidth=0.65, alpha=0.75, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=3.0, width=0.75)


def save_both(fig: plt.Figure, name: str) -> list[Path]:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG_DIR.mkdir(parents=True, exist_ok=True)
    out_paths = [PLOTS_DIR / f"{name}.png", PLOTS_DIR / f"{name}.pdf"]
    for out_path in out_paths:
        fig.savefig(out_path, bbox_inches="tight")
    copied = []
    for out_path in out_paths:
        target = PAPER_FIG_DIR / out_path.name
        shutil.copy2(out_path, target)
        copied.append(target)
    return out_paths + copied


def plot_certjudge_train_test() -> list[Path]:
    rows = pd.read_csv(RESULTS_DIR / "train_certjudge_weight_search.csv")
    summary = pd.read_csv(RESULTS_DIR / "certjudge_index_correlations.csv")
    opt = summary.loc[summary["index_name"] == "certjudge_train_optimized"].iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.65), sharex=True, sharey=True)
    panels = [
        ("Train calibration", "human_spearman_train", float(opt["train_spearman"])),
        ("Held-out test", "human_spearman_test", float(opt["test_spearman"])),
    ]

    for ax, (title, y_col, reported_rho) in zip(axes, panels):
        for _, row in rows.iterrows():
            color = model_color(row["model"], row["kind"])
            ax.scatter(
                row["certjudge_train_optimized"],
                row[y_col],
                s=34,
                color=color,
                edgecolor="white",
                linewidth=0.55,
                alpha=0.92,
                zorder=3,
            )
        x = rows["certjudge_train_optimized"].to_numpy(dtype=float)
        y = rows[y_col].to_numpy(dtype=float)
        add_ols(ax, x, y)
        ax.set_title(f"{title} rho={reported_rho:.3f}", pad=6)
        ax.set_xlabel("Optimized CertJudge index")
        finish_axes(ax)
        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(-0.25, 0.50)

    axes[0].set_ylabel("Human Spearman")

    legend_items = [
        ("GPT-5.3 Codex", COLORS["gpt-5.3-codex"]),
        ("Claude Opus 4.7", COLORS["claude-opus-4-7"]),
        ("LeanStral", COLORS["labs-leanstral-2603"]),
        ("GPT-4o mini", COLORS["gpt-4o-mini"]),
        ("Edit distance", COLORS["na"]),
        ("Random", COLORS["random"]),
    ]
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markersize=5.2,
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=0.55,
            label=label,
        )
        for label, color in legend_items
    ]
    axes[0].legend(
        handles=handles,
        loc="upper left",
        frameon=True,
        framealpha=0.94,
        facecolor="white",
        edgecolor="#cfcfcf",
        borderpad=0.35,
        handletextpad=0.45,
    )
    fig.suptitle(
        "CertJudge index vs. judge-level human alignment",
        fontsize=8.8,
        fontweight="bold",
        y=0.985,
    )
    fig.subplots_adjust(left=0.075, right=0.995, bottom=0.20, top=0.74, wspace=0.16)
    paths = save_both(fig, "fig_exp32_certjudge_train_test_fig3_style")
    plt.close(fig)
    return paths


def plot_isotonic_top3() -> list[Path]:
    metrics = pd.read_csv(RESULTS_DIR / "test_isotonic_oracle_per_judge.csv")
    preds = pd.read_csv(RESULTS_DIR / "test_isotonic_oracle_predictions.csv")
    top = metrics.sort_values(
        ["test_isotonic_oracle_spearman_rho", "test_isotonic_oracle_pearson_r"],
        ascending=False,
    ).head(3)

    fig, axes = plt.subplots(1, 3, figsize=(10.1, 2.65), sharex=True, sharey=True)
    for ax, (_, row) in zip(axes, top.iterrows()):
        judge_id = row["judge_id"]
        data = preds.loc[preds["judge_id"] == judge_id].copy()
        color = model_color(row["model"], row["kind"])
        ax.scatter(
            data["score_mean"],
            data["human_mean_0_1"],
            s=30,
            color=color,
            edgecolor="white",
            linewidth=0.55,
            alpha=0.92,
            zorder=3,
        )

        order = np.argsort(data["score_mean"].to_numpy(dtype=float))
        xs = data["score_mean"].to_numpy(dtype=float)[order]
        ys = data["test_isotonic_oracle_pred"].to_numpy(dtype=float)[order]
        ax.plot(
            xs,
            ys,
            color="#b22222",
            linewidth=1.7,
            drawstyle="steps-post",
            alpha=0.86,
            zorder=4,
            label="isotonic fit",
        )
        ax.plot([0, 1], [0, 1], "--", color="#808080", linewidth=1.0, alpha=0.65, zorder=1)
        ax.set_title(
            f"{short_label(judge_id)}\n"
            f"rho={row['test_isotonic_oracle_spearman_rho']:.3f}, "
            f"r={row['test_isotonic_oracle_pearson_r']:.3f}",
            pad=6,
        )
        ax.set_xlabel("Raw judge score")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        finish_axes(ax)

    axes[0].set_ylabel("Human mean score")
    axes[0].legend(
        loc="lower right",
        frameon=True,
        framealpha=0.94,
        facecolor="white",
        edgecolor="#cfcfcf",
        borderpad=0.35,
    )
    fig.suptitle(
        "Test-set isotonic oracle calibration on the new human panel",
        fontsize=8.8,
        fontweight="bold",
        y=0.99,
    )
    fig.subplots_adjust(left=0.055, right=0.995, bottom=0.20, top=0.70, wspace=0.14)
    paths = save_both(fig, "fig_exp32_test_isotonic_top3_fig3_style")
    plt.close(fig)
    return paths


def plot_isotonic_gain() -> list[Path]:
    metrics = pd.read_csv(RESULTS_DIR / "test_isotonic_oracle_per_judge.csv")

    fig, ax = plt.subplots(1, 1, figsize=(3.55, 2.85))
    for _, row in metrics.iterrows():
        color = model_color(row["model"], row["kind"])
        ax.scatter(
            row["raw_spearman_rho"],
            row["test_isotonic_oracle_spearman_rho"],
            s=34,
            color=color,
            edgecolor="white",
            linewidth=0.55,
            alpha=0.92,
            zorder=3,
        )
    lo = min(metrics["raw_spearman_rho"].min(), metrics["test_isotonic_oracle_spearman_rho"].min())
    hi = max(metrics["raw_spearman_rho"].max(), metrics["test_isotonic_oracle_spearman_rho"].max())
    pad = 0.05
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], "--", color="#808080", linewidth=1.0)
    x = metrics["raw_spearman_rho"].to_numpy(dtype=float)
    y = metrics["test_isotonic_oracle_spearman_rho"].to_numpy(dtype=float)
    rho = float(spearmanr(x, y).statistic)
    add_ols(ax, x, y)
    ax.set_title(f"Raw vs. isotonic test agreement rho={rho:.3f}", pad=6)
    ax.set_xlabel("Raw judge-human Spearman")
    ax.set_ylabel("Isotonic oracle Spearman")
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    finish_axes(ax)
    fig.tight_layout()
    paths = save_both(fig, "fig_exp32_isotonic_gain_fig3_style")
    plt.close(fig)
    return paths


def main() -> None:
    setup_style()
    all_paths = []
    all_paths.extend(plot_certjudge_train_test())
    all_paths.extend(plot_isotonic_top3())
    all_paths.extend(plot_isotonic_gain())
    print("Wrote plots:")
    for path in all_paths:
        print(path)


if __name__ == "__main__":
    main()
