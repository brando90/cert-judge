#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
THIS_DIR = REPO_ROOT / "experiments" / "04_veribench_validation"
sys.path.insert(0, str(THIS_DIR))

import exp32_new_human_isotonic_certjudge as exp32  # noqa: E402


DEFAULT_OUT_DIR = THIS_DIR / "results_exp33_tivar_protocol_new_human_stress"
DEFAULT_TIVAR_DIR = THIS_DIR / "results_exp30_tivar_v3_all_models"
DEFAULT_EXP32_DIR = THIS_DIR / "results_exp32_new_human_isotonic_certjudge"
DEFAULT_QWEN_DIR = REPO_ROOT / "experiments" / "13_qwen_replication_exp16_exp19" / "results" / "exp16_qwen_r3_median"
DEFAULT_RESULT_DIRS = exp32.DEFAULT_RESULT_DIRS + [DEFAULT_QWEN_DIR]
DEFAULT_PAPER_FIG_DIR = (
    REPO_ROOT / "paper_latex" / "ICML_2026_AI4Math" / "figures" / "exp33_tivar_protocol_new_human_stress"
)

FAMILIES = ["codex", "claude_opus", "qwen", "leanstral"]
LABEL_SETS = ["pass1", "pass2", "avg"]

FAMILY_TITLES = {
    "codex": "GPT-5.3 Codex",
    "claude_opus": "Claude Opus 4.7",
    "qwen": "Qwen3-Coder",
    "leanstral": "LeanStral",
}

COLORS = {
    "P8": "#1f77b4",
    "P4": "#2ca02c",
    "P1": "#ff7f0e",
    "BAD": "#d62728",
    "4o-P8": "#9467bd",
    "4o-P4": "#8c564b",
    "edit": "#7f7f7f",
    "rand": "#bcbd22",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EXP33: Figure-3-style TI_var protocol plus expanded new-human stress test"
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--tivar-dir", type=Path, default=DEFAULT_TIVAR_DIR)
    parser.add_argument("--exp32-dir", type=Path, default=DEFAULT_EXP32_DIR)
    parser.add_argument("--human-dir", type=Path, default=exp32.DEFAULT_HUMAN_DIR)
    parser.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    parser.add_argument("--paper-fig-dir", type=Path, default=DEFAULT_PAPER_FIG_DIR)
    parser.add_argument("--include-old-prompt", action="store_true")
    return parser.parse_args()


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 8.2,
            "axes.labelsize": 7.8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 6.5,
            "figure.dpi": 180,
            "savefig.dpi": 240,
            "axes.linewidth": 0.8,
        }
    )


def safe_corr(x: Iterable[float], y: Iterable[float]) -> dict:
    xv = np.asarray(list(x), dtype=float)
    yv = np.asarray(list(y), dtype=float)
    mask = np.isfinite(xv) & np.isfinite(yv)
    xv = xv[mask]
    yv = yv[mask]
    if len(xv) < 3 or len(np.unique(xv)) < 2 or len(np.unique(yv)) < 2:
        return {"n_judges": int(len(xv)), "spearman": math.nan, "pearson": math.nan, "kendall": math.nan}
    return {
        "n_judges": int(len(xv)),
        "spearman": float(spearmanr(xv, yv).statistic),
        "pearson": float(pearsonr(xv, yv).statistic),
        "kendall": float(kendalltau(xv, yv).statistic),
    }


def short_label(judge_id: str) -> str:
    if judge_id == "editdist_e1":
        return "edit"
    if judge_id == "random_r1":
        return "rand"
    if judge_id.startswith("gpt-4o-mini|"):
        return {"P4_CHECKLIST": "4o-P4", "P8_STRICT_B": "4o-P8"}.get(judge_id.split("|", 1)[1], "4o")
    if "|BAD_STRINGY" in judge_id:
        return "BAD"
    if "|P1_BASELINE" in judge_id:
        return "P1"
    if "|P4_CHECKLIST" in judge_id:
        return "P4"
    if "|P8_STRICT_B" in judge_id:
        return "P8"
    return judge_id.split("|")[-1][:8]


def finish_axis(ax: plt.Axes) -> None:
    ax.grid(True, color="#dddddd", linewidth=0.65, alpha=0.72, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=3.0, width=0.75)


def add_ols(ax: plt.Axes, x: np.ndarray, y: np.ndarray) -> None:
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 2 or float(np.std(x[mask])) <= 1e-12:
        return
    m, b = np.polyfit(x[mask], y[mask], 1)
    xline = np.linspace(float(np.min(x[mask])), float(np.max(x[mask])), 100)
    ax.plot(xline, m * xline + b, "--", color="#b22222", linewidth=1.25, alpha=0.78, zorder=2)


def load_legacy_tivar(tivar_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    summaries = []
    for family in FAMILIES:
        for label_set in LABEL_SETS:
            path = tivar_dir / f"judge_trust_vector_{family}_{label_set}.csv"
            if not path.exists():
                continue
            df = pd.read_csv(path)
            df["family"] = family
            df["label_set"] = label_set
            rows.append(df)
            corr = safe_corr(df["ti_var_v3"], df["human_spearman"])
            summaries.append(
                {
                    "panel": "legacy_aligned",
                    "family": family,
                    "label_set": label_set,
                    "n_judges": corr["n_judges"],
                    "n_items_per_judge": 75,
                    "ti_var_human_spearman": corr["spearman"],
                    "ti_var_human_pearson": corr["pearson"],
                    "ti_var_human_kendall": corr["kendall"],
                    "source": str(path.relative_to(REPO_ROOT)),
                }
            )
    if not rows:
        raise FileNotFoundError(f"No judge_trust_vector CSVs found under {tivar_dir}")
    return pd.concat(rows, ignore_index=True), pd.DataFrame(summaries)


def load_expanded_new_panel(human_dir: Path, result_dirs: list[Path], include_old_prompt: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    labels, targets, dropped = exp32.load_new_human_labels(human_dir, include_old_prompt)
    meta, scores = exp32.load_judges(result_dirs)
    rows = scores.merge(targets[["item_key", "gold_file", "human_mean_0_1"]], on="item_key", how="inner")
    align_rows = []
    for judge_id, group in rows.groupby("judge_id"):
        item_metrics = exp32.safe_metrics(group["score_mean"], group["human_mean_0_1"])
        by_task = (
            group.groupby(["judge_id", "gold_file"], as_index=False)
            .agg(score_mean=("score_mean", "mean"), human_mean_0_1=("human_mean_0_1", "mean"))
        )
        task_metrics = exp32.safe_metrics(by_task["score_mean"], by_task["human_mean_0_1"])
        align_rows.append(
            {
                "judge_id": judge_id,
                "n_items": item_metrics["n"],
                "n_tasks": task_metrics["n"],
                "human_spearman_item": item_metrics["spearman_rho"],
                "human_pearson_item": item_metrics["pearson_r"],
                "human_kendall_item": item_metrics["kendall_tau"],
                "human_spearman_task": task_metrics["spearman_rho"],
                "human_pearson_task": task_metrics["pearson_r"],
                "human_kendall_task": task_metrics["kendall_tau"],
            }
        )
    align = pd.DataFrame(align_rows).merge(meta[["judge_id", "model", "prompt_name", "kind"]], on="judge_id", how="left")
    return labels, targets, align


def summarize_expanded_new_panel(tivar_dir: Path, align: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    summaries = []
    for family in FAMILIES:
        tv_path = tivar_dir / f"judge_trust_vector_{family}_avg.csv"
        if not tv_path.exists():
            continue
        tv = pd.read_csv(tv_path)
        panel = tv[["judge_id", "ti_var_v3"]].merge(align, on="judge_id", how="inner")
        panel["family"] = family
        rows.append(panel)
        for target_col, target_name in [
            ("human_spearman_item", "item"),
            ("human_spearman_task", "task"),
        ]:
            corr = safe_corr(panel["ti_var_v3"], panel[target_col])
            summaries.append(
                {
                    "panel": "expanded_new_human",
                    "family": family,
                    "label_set": f"avg_{target_name}",
                    "n_judges": corr["n_judges"],
                    "n_items_per_judge": int(panel["n_items"].min()) if not panel.empty else 0,
                    "n_tasks_per_judge": int(panel["n_tasks"].min()) if not panel.empty else 0,
                    "ti_var_human_spearman": corr["spearman"],
                    "ti_var_human_pearson": corr["pearson"],
                    "ti_var_human_kendall": corr["kendall"],
                    "source": "new human TSVs aggregated by item",
                }
            )
    return pd.concat(rows, ignore_index=True), pd.DataFrame(summaries)


def rater_diagnostics(labels: pd.DataFrame) -> pd.DataFrame:
    mat = labels.pivot_table(index="item_key", columns="rater", values="human_score_0_1", aggfunc="mean")
    rows = []
    for rater in mat.columns:
        others = mat.drop(columns=[rater]).mean(axis=1)
        mask = mat[rater].notna() & others.notna()
        corr = safe_corr(mat.loc[mask, rater], others.loc[mask])
        rows.append(
            {
                "rater": rater,
                "n_overlap_items": int(mask.sum()),
                "spearman_vs_other_raters_mean": corr["spearman"],
                "pearson_vs_other_raters_mean": corr["pearson"],
            }
        )
    return pd.DataFrame(rows).sort_values("spearman_vs_other_raters_mean", ascending=False)


def plot_family_scatter(
    panel: pd.DataFrame,
    summary: pd.DataFrame,
    out_path: Path,
    title: str,
    target_col: str,
    families: list[str],
    paper_fig_dir: Path | None = None,
) -> None:
    fig, axes = plt.subplots(1, len(families), figsize=(3.35 * len(families), 2.65), sharex=True, sharey=True)
    if len(families) == 1:
        axes = [axes]
    for ax, family in zip(axes, families):
        df = panel.loc[panel["family"] == family].copy()
        for _, row in df.iterrows():
            label = short_label(row["judge_id"])
            color = COLORS.get(label, "#1f77b4")
            ax.scatter(
                row["ti_var_v3"],
                row[target_col],
                s=30,
                color=color,
                edgecolor="white",
                linewidth=0.55,
                alpha=0.94,
                zorder=3,
            )
            ax.annotate(label, (row["ti_var_v3"], row[target_col]), xytext=(3, 3), textcoords="offset points", fontsize=6.4)
        add_ols(ax, df["ti_var_v3"].to_numpy(dtype=float), df[target_col].to_numpy(dtype=float))
        row = summary.loc[(summary["family"] == family)]
        rho = float(row["ti_var_human_spearman"].iloc[0]) if not row.empty else math.nan
        ax.set_title(f"{FAMILY_TITLES.get(family, family)} rho={rho:.3f}", pad=6)
        ax.set_xlabel(r"$\mathrm{TI}_{\mathrm{var}}$")
        finish_axis(ax)
        ax.set_xlim(0.0, 1.0)
    axes[0].set_ylabel("Human Spearman")
    fig.suptitle(title, fontsize=8.8, fontweight="bold", y=0.985)
    fig.subplots_adjust(left=0.065, right=0.995, bottom=0.20, top=0.76, wspace=0.16)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    saved_paths = [out_path.with_suffix(".png"), out_path.with_suffix(".pdf")]
    for path in saved_paths:
        fig.savefig(path, bbox_inches="tight")
    if paper_fig_dir is not None:
        paper_fig_dir.mkdir(parents=True, exist_ok=True)
        for path in saved_paths:
            shutil.copy2(path, paper_fig_dir / path.name)
    plt.close(fig)


def copy_isotonic_appendix(exp32_dir: Path, out_dir: Path) -> list[str]:
    appendix_dir = out_dir / "appendix_isotonic_oracle"
    appendix_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in [
        "test_isotonic_oracle_per_judge.csv",
        "test_isotonic_oracle_predictions.csv",
        "summary.json",
    ]:
        src = exp32_dir / name
        if src.exists():
            dst = appendix_dir / name
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(REPO_ROOT)))
    plot_dir = exp32_dir / "plots"
    if plot_dir.exists():
        for src in sorted(plot_dir.glob("fig_exp32_test_isotonic_top3_fig3_style.*")):
            dst = appendix_dir / src.name
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(REPO_ROOT)))
    return copied


def write_readme(out_dir: Path, summary: dict, legacy_summary: pd.DataFrame, expanded_summary: pd.DataFrame) -> None:
    legacy_avg = legacy_summary.loc[
        (legacy_summary["panel"] == "legacy_aligned")
        & (legacy_summary["label_set"] == "avg")
        & (legacy_summary["family"].isin(["codex", "claude_opus", "qwen"]))
    ].copy()
    expanded_item = expanded_summary.loc[expanded_summary["label_set"] == "avg_item"].copy()

    lines = [
        "# EXP33 TI-var Protocol and New-Human Stress Test",
        "**TLDR:** This run restores the Figure-3-style TI_var judge-selection protocol on the legacy aligned panel, then evaluates the same TI_var scores on the larger new-human panel as a held-out stress test. The legacy aligned panel supports the high judge-level correlations; the expanded new-human panel does not, so the isotonic oracle is kept as an appendix-only diagnostic.",
        "",
        "## What changed",
        "- Uses `TI_var` from EXP30 rather than the quick EXP32 optimized CertJudge index.",
        "- Reports separate model-family panels instead of pooling heterogeneous judges.",
        f"- Expands the new-human held-out target from 15 test items to {summary['expanded_new_human']['n_overlap_items']} overlapping items.",
        "- Keeps test-set isotonic oracle artifacts in `appendix_isotonic_oracle/`.",
        "",
        "## Legacy aligned-panel TI_var correlations",
    ]
    for _, row in legacy_avg.sort_values("family").iterrows():
        lines.append(
            f"- `{row['family']}` avg labels: Spearman={row['ti_var_human_spearman']:.3f}, "
            f"Pearson={row['ti_var_human_pearson']:.3f}, n_judges={int(row['n_judges'])}."
        )
    lines += [
        "",
        "## Expanded new-human held-out stress test",
        "These correlations are not headline-ready; they are the larger held-out check requested after EXP32.",
    ]
    for _, row in expanded_item.sort_values("family").iterrows():
        lines.append(
            f"- `{row['family']}` item-level avg: Spearman={row['ti_var_human_spearman']:.3f}, "
            f"Pearson={row['ti_var_human_pearson']:.3f}, n_items={int(row['n_items_per_judge'])}."
        )
    lines += [
        "",
        "## Outputs",
        "- `legacy_tivar_family_label_summary.csv`",
        "- `expanded_new_human_tivar_summary.csv`",
        "- `expanded_new_human_judge_alignment.csv`",
        "- `new_human_rater_diagnostics.csv`",
        "- `fig_legacy_tivar_avg_fig3_style.{png,pdf}`",
        "- `fig_expanded_new_human_tivar_item_fig3_style.{png,pdf}`",
        "- `appendix_isotonic_oracle/`",
    ]
    out_dir.joinpath("README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    setup_style()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    legacy_panel, legacy_summary = load_legacy_tivar(args.tivar_dir)
    labels, targets, expanded_align = load_expanded_new_panel(args.human_dir, args.result_dirs, args.include_old_prompt)
    expanded_panel, expanded_summary = summarize_expanded_new_panel(args.tivar_dir, expanded_align)
    raters = rater_diagnostics(labels)
    isotonic_files = copy_isotonic_appendix(args.exp32_dir, args.out_dir)

    legacy_panel.to_csv(args.out_dir / "legacy_tivar_panel_rows.csv", index=False)
    legacy_summary.to_csv(args.out_dir / "legacy_tivar_family_label_summary.csv", index=False)
    expanded_align.to_csv(args.out_dir / "expanded_new_human_judge_alignment.csv", index=False)
    expanded_panel.to_csv(args.out_dir / "expanded_new_human_tivar_panel_rows.csv", index=False)
    expanded_summary.to_csv(args.out_dir / "expanded_new_human_tivar_summary.csv", index=False)
    raters.to_csv(args.out_dir / "new_human_rater_diagnostics.csv", index=False)

    legacy_avg = legacy_panel.loc[(legacy_panel["label_set"] == "avg") & legacy_panel["family"].isin(["codex", "claude_opus", "qwen"])]
    legacy_avg_summary = legacy_summary.loc[(legacy_summary["label_set"] == "avg") & legacy_summary["family"].isin(["codex", "claude_opus", "qwen"])]
    plot_family_scatter(
        legacy_avg,
        legacy_avg_summary,
        args.out_dir / "fig_legacy_tivar_avg_fig3_style",
        r"$\mathrm{TI}_{\mathrm{var}}$ vs human alignment on the aligned validation panel",
        "human_spearman",
        ["codex", "claude_opus", "qwen"],
        args.paper_fig_dir,
    )

    expanded_item_summary = expanded_summary.loc[expanded_summary["label_set"] == "avg_item"]
    plot_family_scatter(
        expanded_panel,
        expanded_item_summary,
        args.out_dir / "fig_expanded_new_human_tivar_item_fig3_style",
        r"Held-out new-human stress test: $\mathrm{TI}_{\mathrm{var}}$ vs human alignment",
        "human_spearman_item",
        ["codex", "claude_opus", "qwen", "leanstral"],
        args.paper_fig_dir,
    )

    summary = {
        "experiment": "exp33_tivar_protocol_new_human_stress",
        "inputs": {
            "tivar_dir": str(args.tivar_dir),
            "human_dir": str(args.human_dir),
            "include_old_prompt": bool(args.include_old_prompt),
            "result_dirs": [str(p) for p in args.result_dirs],
        },
        "legacy_aligned": {
            "n_family_label_rows": int(len(legacy_summary)),
            "avg_label_rows": legacy_summary.loc[legacy_summary["label_set"] == "avg"].to_dict(orient="records"),
        },
        "expanded_new_human": {
            "n_usable_labels": int(len(labels)),
            "n_distinct_items": int(len(targets)),
            "n_overlap_items": int(expanded_align["n_items"].min()) if not expanded_align.empty else 0,
            "n_overlap_tasks": int(expanded_align["n_tasks"].min()) if not expanded_align.empty else 0,
            "summary_rows": expanded_summary.to_dict(orient="records"),
            "rater_diagnostics": raters.to_dict(orient="records"),
        },
        "isotonic_appendix_files": isotonic_files,
        "interpretation": {
            "headline": "Use the legacy aligned-panel TI_var protocol for judge-selection claims.",
            "held_out_check": "The expanded new-human panel is larger but does not reproduce high TI_var-human correlations.",
            "isotonic": "The EXP32 test-set isotonic oracle remains an appendix-only upper-bound calibration diagnostic.",
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_readme(args.out_dir, summary, legacy_summary, expanded_summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
