#!/usr/bin/env python3
"""
EXP38: Five-rater human mean + per-task isotonic calibration.

Builds the five-participant super-human target, applies within-task isotonic
calibration on cached judge scores, writes metrics/predictions CSVs, and
generates fig3-style scatter plots.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp38_five_human_per_task_isotonic"
DEFAULT_PAPER_FIG_DIR = REPO_ROOT / "paper_latex" / "TMLR_2026" / "figures" / "exp38_five_human_per_task_isotonic"
DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]
DEFAULT_HIGHLIGHT_JUDGES = [
    "gpt-5.3-codex|P11_JSON_FIRST",
    "claude-opus-4-7|P4_CHECKLIST",
    "gpt-5.3-codex|P2_FORMAL",
    "labs-leanstral-2603|P1_BASELINE",
]
FLOAT_TIE_DIGITS = 12

COLORS = {
    "gpt-5.3-codex": "#1f77b4",
    "claude-opus-4-7": "#9467bd",
    "labs-leanstral-2603": "#2ca02c",
    "gpt-4o-mini": "#8c564b",
    "na": "#7f7f7f",
    "random": "#bcbd22",
    "editdist": "#7f7f7f",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP38: five-rater mean + per-task isotonic plots")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--paper-fig-dir", type=Path, default=DEFAULT_PAPER_FIG_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument("--human-target", choices=["mean", "median", "zscore_mean"], default="mean")
    p.add_argument("--highlight-judges", nargs="*", default=DEFAULT_HIGHLIGHT_JUDGES)
    p.add_argument("--copy-paper-figs", action="store_true", default=True)
    p.add_argument("--no-copy-paper-figs", action="store_false", dest="copy_paper_figs")
    p.add_argument("--plots-only", action="store_true", help="Regenerate plots from existing CSV outputs")
    return p.parse_args()


def mean(values: Sequence[float]) -> float:
    vals = [v for v in values if math.isfinite(v)]
    return round(math.fsum(vals) / len(vals), FLOAT_TIE_DIGITS) if vals else float("nan")


def std(values: Sequence[float]) -> float:
    vals = [v for v in values if math.isfinite(v)]
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def median(values: Sequence[float]) -> float:
    vals = sorted(v for v in values if math.isfinite(v))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2.0


def rankdata(values: Sequence[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda item: round(item[1], FLOAT_TIE_DIGITS))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and round(indexed[j][1], FLOAT_TIE_DIGITS) == round(indexed[i][1], FLOAT_TIE_DIGITS):
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return float("nan")
    return num / (den_x * den_y)


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def safe_metrics(xs: Sequence[float], ys: Sequence[float]) -> dict:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return {"n": len(pairs), "spearman_r": float("nan"), "pearson_r": float("nan"), "mae": float("nan")}
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    if len(set(x)) < 2 or len(set(y)) < 2:
        return {"n": len(pairs), "spearman_r": float("nan"), "pearson_r": float("nan"), "mae": float("nan")}
    return {
        "n": len(pairs),
        "spearman_r": spearman(x, y),
        "pearson_r": pearson(x, y),
        "mae": mean([abs(a - b) for a, b in pairs]),
    }


def clean_candidate_and_score(candidate: str, score: str) -> Tuple[str, str]:
    candidate = str(candidate).strip()
    score = str(score).strip()
    if not score and ".lean " in candidate:
        head, tail = candidate.rsplit(" ", 1)
        try:
            float(tail)
        except ValueError:
            return candidate, score
        return head.strip(), tail.strip()
    return candidate, score


def load_participant_labels(human_dir: Path) -> Tuple[Dict[str, Dict[str, float]], List[str]]:
    by_item: Dict[str, Dict[str, float]] = defaultdict(dict)
    raters: List[str] = []
    for path in sorted(human_dir.glob("participant*.tsv")):
        rater = path.stem
        raters.append(rater)
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gold = str(row.get("gold_file", "")).strip()
                cand, score_text = clean_candidate_and_score(row.get("candidate_file", ""), row.get("human_score_0_5", ""))
                try:
                    score = float(score_text) / 5.0
                except (TypeError, ValueError):
                    continue
                if not gold or not cand:
                    continue
                by_item[f"{gold}::{cand}"][rater] = score
    return by_item, raters


def build_human_target(by_item: Dict[str, Dict[str, float]], raters: Sequence[str], method: str) -> Dict[str, dict]:
    rater_stats = {}
    if method == "zscore_mean":
        for rater in raters:
            vals = [rmap[rater] for rmap in by_item.values() if rater in rmap]
            rater_stats[rater] = (mean(vals), std(vals))

    out: Dict[str, dict] = {}
    for item_key, rmap in sorted(by_item.items()):
        vals = [rmap[r] for r in raters if r in rmap]
        if not vals:
            continue
        gold, cand = item_key.split("::", 1)
        if method == "mean":
            score = mean(vals)
        elif method == "median":
            score = median(vals)
        elif method == "zscore_mean":
            zs = []
            for r in raters:
                if r not in rmap:
                    continue
                m, s = rater_stats[r]
                zs.append((rmap[r] - m) / s if s > 1e-9 else 0.0)
            score = mean(zs)
        else:
            score = mean(vals)
        out[item_key] = {
            "item_key": item_key,
            "gold_file": gold,
            "candidate_file": cand,
            "human_score_0_1": score,
            "human_score_0_5": score * 5.0,
            "n_raters": len(vals),
        }
    return out


def load_judge_scores(result_dirs: Iterable[Path]) -> Tuple[Dict[str, dict], Dict[str, Dict[str, float]]]:
    meta: Dict[str, dict] = {}
    scores: Dict[str, Dict[str, float]] = defaultdict(dict)
    for result_dir in result_dirs:
        judge_rows_path = result_dir / "judge_rows.csv"
        detail_rows_path = result_dir / "detail_rows.csv"
        if not judge_rows_path.exists() or not detail_rows_path.exists():
            continue
        with judge_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                jid = row["judge_id"]
                if jid in meta:
                    continue
                meta[jid] = {
                    "judge_id": jid,
                    "kind": row.get("kind", ""),
                    "model": row.get("model", ""),
                    "prompt_name": row.get("prompt_name", ""),
                    "source_dir": str(result_dir.relative_to(REPO_ROOT)),
                    "cert_index_v2": float(row.get("cert_index_v2") or "nan"),
                }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                jid = row["judge_id"]
                ik = row["item_key"]
                if jid not in meta or ik in scores[jid]:
                    continue
                scores[jid][ik] = float(row.get("score_mean") or "nan")
    return meta, scores


def pav_isotonic_fit_predict(x: Sequence[float], y: Sequence[float], x_pred: Sequence[float]) -> List[float]:
    pairs = sorted(zip(x, y), key=lambda t: t[0])
    blocks = [[p[1], 1] for p in pairs]
    xs = [pairs[i][0] for i in range(len(pairs))]
    ys = [blocks[i][0] for i in range(len(blocks))]
    i = 0
    while i < len(blocks) - 1:
        if ys[i] <= ys[i + 1] + 1e-15:
            i += 1
            continue
        new_y = (blocks[i][0] * blocks[i][1] + blocks[i + 1][0] * blocks[i + 1][1]) / (blocks[i][1] + blocks[i + 1][1])
        blocks[i] = [new_y, blocks[i][1] + blocks[i + 1][1]]
        del blocks[i + 1]
        del xs[i + 1]
        ys[i] = new_y
        del ys[i + 1]
        if i:
            i -= 1
    thresholds = xs + [float("inf")]
    out = []
    for xv in x_pred:
        idx = 0
        while idx + 1 < len(thresholds) and xv > thresholds[idx]:
            idx += 1
        idx = min(idx, len(ys) - 1)
        out.append(max(0.0, min(1.0, ys[idx])))
    return out


def per_task_isotonic(item_keys: Sequence[str], x: Sequence[float], y: Sequence[float]) -> List[float]:
    by_task: Dict[str, List[int]] = defaultdict(list)
    for i, k in enumerate(item_keys):
        by_task[k.split("::", 1)[0]].append(i)
    out = list(x)
    for idxs in by_task.values():
        if len(idxs) < 2:
            continue
        xt = [x[i] for i in idxs]
        yt = [y[i] for i in idxs]
        if len(set(xt)) < 2:
            continue
        pred = pav_isotonic_fit_predict(xt, yt, xt)
        for j, i in enumerate(idxs):
            out[i] = pred[j]
    return out


def task_means(item_keys: Sequence[str], scores: Sequence[float]) -> Tuple[List[str], List[float]]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for k, s in zip(item_keys, scores):
        buckets[k.split("::", 1)[0]].append(s)
    tasks = sorted(buckets)
    return tasks, [mean(buckets[t]) for t in tasks]


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


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


def model_color(model: str, kind: str) -> str:
    if kind == "random":
        return COLORS["random"]
    if kind == "editdist":
        return COLORS["editdist"]
    return COLORS.get(model, "#1f77b4")


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
        "P2_FORMAL": "P2 formal",
        "P4_CHECKLIST": "P4 checklist",
        "P11_JSON_FIRST": "P11 JSON-first",
        "P8_STRICT_B": "P8 strict",
        "BAD_STRINGY": "Bad stringy",
    }.get(prompt, prompt.replace("_", " ").title())
    return f"{model_label}\n{prompt_label}"


def finish_axes(ax: plt.Axes) -> None:
    ax.grid(True, color="#d9d9d9", linewidth=0.65, alpha=0.75, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=3.0, width=0.75)


def add_ols(ax: plt.Axes, x: np.ndarray, y: np.ndarray, color: str = "#b22222") -> None:
    keep = np.isfinite(x) & np.isfinite(y)
    if int(keep.sum()) < 2 or float(np.std(x[keep])) <= 1e-12:
        return
    m, b = np.polyfit(x[keep], y[keep], 1)
    xline = np.linspace(float(np.min(x[keep])), float(np.max(x[keep])), 100)
    ax.plot(xline, m * xline + b, "--", color=color, linewidth=1.3, alpha=0.78, zorder=2)


def save_fig(fig: plt.Figure, plots_dir: Path, name: str) -> List[Path]:
    plots_dir.mkdir(parents=True, exist_ok=True)
    out_paths = [plots_dir / f"{name}.png", plots_dir / f"{name}.pdf"]
    for path in out_paths:
        fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return out_paths


def copy_plots_to_paper(plots_dir: Path, paper_dir: Path) -> List[Path]:
    paper_dir.mkdir(parents=True, exist_ok=True)
    copied: List[Path] = []
    for path in sorted(plots_dir.glob("fig_exp38_*")):
        target = paper_dir / path.name
        if target.resolve() != path.resolve():
            shutil.copy2(path, target)
            copied.append(target)
    return copied


def analyze_and_predict(
    human_target: Dict[str, dict],
    judge_meta: Dict[str, dict],
    judge_scores: Dict[str, Dict[str, float]],
) -> Tuple[List[dict], List[dict], List[dict]]:
    metric_rows: List[dict] = []
    pred_rows: List[dict] = []
    task_rows: List[dict] = []

    for jid, j_scores in sorted(judge_scores.items()):
        meta = judge_meta[jid]
        common = sorted(set(j_scores) & set(human_target))
        if len(common) < 3:
            continue
        x = [j_scores[k] for k in common]
        y = [human_target[k]["human_score_0_1"] for k in common]
        x_iso = per_task_isotonic(common, x, y)

        raw_item = safe_metrics(x, y)
        iso_item = safe_metrics(x_iso, y)

        tasks, x_task = task_means(common, x)
        _, y_task = task_means(common, y)
        _, x_iso_task = task_means(common, x_iso)
        raw_task = safe_metrics(x_task, y_task)
        iso_task = safe_metrics(x_iso_task, y_task)

        metric_rows.append(
            {
                "judge_id": jid,
                "kind": meta["kind"],
                "model": meta["model"],
                "prompt_name": meta["prompt_name"],
                "cert_index_v2": meta["cert_index_v2"],
                "source_dir": meta["source_dir"],
                "n_items": raw_item["n"],
                "n_tasks": raw_task["n"],
                "raw_item_spearman_r": raw_item["spearman_r"],
                "raw_item_pearson_r": raw_item["pearson_r"],
                "raw_item_mae": raw_item["mae"],
                "per_task_iso_item_spearman_r": iso_item["spearman_r"],
                "per_task_iso_item_pearson_r": iso_item["pearson_r"],
                "per_task_iso_item_mae": iso_item["mae"],
                "raw_task_spearman_r": raw_task["spearman_r"],
                "raw_task_pearson_r": raw_task["pearson_r"],
                "per_task_iso_task_spearman_r": iso_task["spearman_r"],
                "per_task_iso_task_pearson_r": iso_task["pearson_r"],
            }
        )

        for k, raw, iso, hy in zip(common, x, x_iso, y):
            pred_rows.append(
                {
                    "judge_id": jid,
                    "item_key": k,
                    "gold_file": human_target[k]["gold_file"],
                    "candidate_file": human_target[k]["candidate_file"],
                    "human_score_0_1": hy,
                    "human_score_0_5": hy * 5.0,
                    "raw_judge_score": raw,
                    "per_task_iso_judge_score": iso,
                    "n_raters": human_target[k]["n_raters"],
                }
            )

        for task, jt, ht, jit in zip(tasks, x_task, y_task, x_iso_task):
            task_rows.append(
                {
                    "judge_id": jid,
                    "task": task,
                    "raw_judge_score": jt,
                    "per_task_iso_judge_score": jit,
                    "human_score_0_1": ht,
                    "human_score_0_5": ht * 5.0,
                }
            )

    metric_rows.sort(key=lambda r: (-999 if not math.isfinite(r["per_task_iso_item_spearman_r"]) else -r["per_task_iso_item_spearman_r"], r["judge_id"]))
    return metric_rows, pred_rows, task_rows


def plot_gain(metrics: List[dict], plots_dir: Path) -> List[Path]:
    fig, ax = plt.subplots(1, 1, figsize=(3.55, 2.85))
    xs, ys = [], []
    for row in metrics:
        if row["kind"] not in {"llm", "llm_bad", "editdist", "random"}:
            continue
        if not math.isfinite(row["raw_item_spearman_r"]) or not math.isfinite(row["per_task_iso_item_spearman_r"]):
            continue
        xs.append(row["raw_item_spearman_r"])
        ys.append(row["per_task_iso_item_spearman_r"])
        ax.scatter(
            row["raw_item_spearman_r"],
            row["per_task_iso_item_spearman_r"],
            s=34,
            color=model_color(row["model"], row["kind"]),
            edgecolor="white",
            linewidth=0.55,
            alpha=0.92,
            zorder=3,
        )
    if xs:
        lo = min(min(xs), min(ys))
        hi = max(max(xs), max(ys))
        pad = 0.05
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], "--", color="#808080", linewidth=1.0)
        add_ols(ax, np.array(xs), np.array(ys))
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(lo - pad, hi + pad)
    ax.set_title("Raw vs. per-task isotonic item agreement", pad=6)
    ax.set_xlabel("Raw judge-human Spearman")
    ax.set_ylabel("Per-task isotonic Spearman")
    finish_axes(ax)
    fig.tight_layout()
    return save_fig(fig, plots_dir, "fig_exp38_raw_vs_per_task_isotonic_gain")


def plot_top3_scatter(
    metrics: List[dict],
    pred_rows: List[dict],
    plots_dir: Path,
    preferred_judges: Sequence[str],
) -> List[Path]:
    metric_map = {r["judge_id"]: r for r in metrics}
    top = [metric_map[j] for j in preferred_judges if j in metric_map]
    if len(top) < 3:
        filler = [
            r
            for r in metrics
            if r["kind"] == "llm" and math.isfinite(r["per_task_iso_item_spearman_r"]) and r["judge_id"] not in {t["judge_id"] for t in top}
        ]
        filler.sort(key=lambda r: -r["per_task_iso_item_spearman_r"])
        top.extend(filler[: max(0, 3 - len(top))])
    top = top[:3]
    if not top:
        return []
    pred_by_judge: Dict[str, List[dict]] = defaultdict(list)
    for row in pred_rows:
        pred_by_judge[row["judge_id"]].append(row)

    fig, axes = plt.subplots(1, 3, figsize=(10.1, 2.65), sharex=True, sharey=True)
    for ax, row in zip(axes, top):
        jid = row["judge_id"]
        data = sorted(pred_by_judge[jid], key=lambda r: r["raw_judge_score"])
        xs = np.array([r["raw_judge_score"] for r in data], dtype=float)
        ys = np.array([r["human_score_0_1"] for r in data], dtype=float)
        iso = np.array([r["per_task_iso_judge_score"] for r in data], dtype=float)
        color = model_color(row["model"], row["kind"])
        ax.scatter(xs, ys, s=30, color=color, edgecolor="white", linewidth=0.55, alpha=0.92, zorder=3)
        order = np.argsort(xs)
        ax.plot(xs[order], iso[order], color="#b22222", linewidth=1.7, drawstyle="steps-post", alpha=0.86, zorder=4, label="per-task isotonic")
        ax.plot([0, 1], [0, 1], "--", color="#808080", linewidth=1.0, alpha=0.65, zorder=1)
        ax.set_title(
            f"{short_label(jid)}\n"
            f"rho={row['per_task_iso_item_spearman_r']:.3f}, "
            f"raw={row['raw_item_spearman_r']:.3f}",
            pad=6,
        )
        ax.set_xlabel("Raw judge score")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        finish_axes(ax)

    axes[0].set_ylabel("Five-rater human mean")
    axes[0].legend(loc="lower right", frameon=True, framealpha=0.94, facecolor="white", edgecolor="#cfcfcf", borderpad=0.35)
    fig.suptitle("Per-task isotonic calibration on five-rater human mean", fontsize=8.8, fontweight="bold", y=0.99)
    fig.subplots_adjust(left=0.055, right=0.995, bottom=0.20, top=0.70, wspace=0.14)
    return save_fig(fig, plots_dir, "fig_exp38_per_task_isotonic_top3")


def plot_highlight_panels(
    highlight_judges: Sequence[str],
    metrics: List[dict],
    pred_rows: List[dict],
    plots_dir: Path,
) -> List[Path]:
    metric_map = {r["judge_id"]: r for r in metrics}
    pred_by_judge: Dict[str, List[dict]] = defaultdict(list)
    for row in pred_rows:
        pred_by_judge[row["judge_id"]].append(row)

    judges = [j for j in highlight_judges if j in metric_map and j in pred_by_judge]
    if not judges:
        return []

    fig, axes = plt.subplots(2, len(judges), figsize=(3.0 * len(judges), 5.2), sharex="col", sharey="row")
    if len(judges) == 1:
        axes = np.array([[axes[0]], [axes[1]]])

    for col, jid in enumerate(judges):
        row = metric_map[jid]
        data = pred_by_judge[jid]
        xs = np.array([r["raw_judge_score"] for r in data], dtype=float)
        ys = np.array([r["human_score_0_1"] for r in data], dtype=float)
        iso = np.array([r["per_task_iso_judge_score"] for r in data], dtype=float)
        color = model_color(row["model"], row["kind"])

        ax_raw = axes[0, col]
        ax_iso = axes[1, col]
        ax_raw.scatter(xs, ys, s=26, color=color, edgecolor="white", linewidth=0.5, alpha=0.92)
        add_ols(ax_raw, xs, ys)
        ax_raw.set_title(f"{short_label(jid)}\nraw rho={row['raw_item_spearman_r']:.3f}", pad=5)
        ax_raw.set_xlim(-0.03, 1.03)
        ax_raw.set_ylim(-0.03, 1.03)
        finish_axes(ax_raw)

        order = np.argsort(iso)
        ax_iso.scatter(iso, ys, s=26, color=color, edgecolor="white", linewidth=0.5, alpha=0.92)
        add_ols(ax_iso, iso[order], ys[order])
        ax_iso.set_title(f"calibrated rho={row['per_task_iso_item_spearman_r']:.3f}", pad=5)
        ax_iso.set_xlim(-0.03, 1.03)
        ax_iso.set_ylim(-0.03, 1.03)
        finish_axes(ax_iso)
        ax_iso.set_xlabel("Judge score")

    axes[0, 0].set_ylabel("Human mean")
    axes[1, 0].set_ylabel("Human mean")
    fig.suptitle("Selected judges: raw vs per-task isotonic (item-level)", fontsize=8.8, fontweight="bold", y=0.98)
    fig.subplots_adjust(left=0.07, right=0.995, bottom=0.08, top=0.88, wspace=0.18, hspace=0.35)
    return save_fig(fig, plots_dir, "fig_exp38_selected_judges_raw_vs_iso")


def plot_task_scatter(
    highlight_judges: Sequence[str],
    task_rows: List[dict],
    metrics: List[dict],
    plots_dir: Path,
) -> List[Path]:
    metric_map = {r["judge_id"]: r for r in metrics}
    by_judge: Dict[str, List[dict]] = defaultdict(list)
    for row in task_rows:
        by_judge[row["judge_id"]].append(row)
    judges = [j for j in highlight_judges if j in metric_map and j in by_judge][:4]
    if not judges:
        return []

    fig, axes = plt.subplots(1, len(judges), figsize=(3.0 * len(judges), 2.75), sharex=True, sharey=True)
    if len(judges) == 1:
        axes = [axes]

    for ax, jid in zip(axes, judges):
        row = metric_map[jid]
        data = by_judge[jid]
        xs = np.array([r["raw_judge_score"] for r in data], dtype=float)
        ys = np.array([r["human_score_0_1"] for r in data], dtype=float)
        color = model_color(row["model"], row["kind"])
        ax.scatter(xs, ys, s=36, color=color, edgecolor="white", linewidth=0.55, alpha=0.92)
        add_ols(ax, xs, ys)
        ax.set_title(f"{short_label(jid)}\ntask raw rho={row['raw_task_spearman_r']:.3f}", pad=5)
        ax.set_xlabel("Task-mean judge score")
        finish_axes(ax)

    axes[0].set_ylabel("Task-mean human score")
    fig.suptitle("Task-level agreement (raw, no calibration)", fontsize=8.8, fontweight="bold", y=0.98)
    fig.subplots_adjust(left=0.08, right=0.995, bottom=0.16, top=0.78, wspace=0.18)
    return save_fig(fig, plots_dir, "fig_exp38_task_level_raw_selected")


def _maybe_float(val: str) -> float | str | int:
    if val == "" or val.lower() == "nan":
        return float("nan")
    try:
        if "." in val or "e" in val.lower():
            return float(val)
        return int(val)
    except ValueError:
        return val


def _read_csv_rows(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    float_cols = {
        "human_score_0_1",
        "human_score_0_5",
        "raw_judge_score",
        "per_task_iso_judge_score",
        "raw_judge_score_task",
        "human_score_0_1_task",
    }
    int_cols = {"n_raters", "n_items", "n_tasks"}
    for row in rows:
        for col in float_cols:
            if col in row:
                row[col] = _maybe_float(row[col])
        for col in int_cols:
            if col in row:
                row[col] = int(row[col])
    return rows


def _read_metrics_csv(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    float_cols = {
        "cert_index_v2",
        "raw_item_spearman_r",
        "raw_item_pearson_r",
        "raw_item_mae",
        "per_task_iso_item_spearman_r",
        "per_task_iso_item_pearson_r",
        "per_task_iso_item_mae",
        "raw_task_spearman_r",
        "raw_task_pearson_r",
        "per_task_iso_task_spearman_r",
        "per_task_iso_task_pearson_r",
    }
    int_cols = {"n_items", "n_tasks"}
    for row in rows:
        for col in float_cols:
            if col in row:
                row[col] = _maybe_float(row[col])
        for col in int_cols:
            if col in row:
                row[col] = int(row[col])
    return rows


def write_report(out_dir: Path, summary: dict, metrics: List[dict]) -> None:
    llm = [r for r in metrics if r["kind"] == "llm" and math.isfinite(r["per_task_iso_item_spearman_r"])]
    llm.sort(key=lambda r: -r["per_task_iso_item_spearman_r"])
    lines = [
        "# EXP38: Five-Rater Mean + Per-Task Isotonic Calibration",
        "",
        summary["tldr"],
        "",
        "## Human Target",
        f"- Method: `{summary['human_target_method']}`",
        f"- Items: `{summary['n_human_items']}`",
        f"- Overlap with judge panel: `{summary['n_overlap_items']}` items / `{summary['n_overlap_tasks']}` tasks",
        "",
        "## Top Calibrated LLM Judges (Item-Level)",
        "",
        "| Judge | Raw rho | Per-task iso rho | Raw task rho | n items |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in llm[:12]:
        lines.append(
            f"| `{row['judge_id']}` | {row['raw_item_spearman_r']:.3f} | {row['per_task_iso_item_spearman_r']:.3f} | {row['raw_task_spearman_r']:.3f} | {int(row['n_items'])} |"
        )
    lines += [
        "",
        "## Outputs",
        "- `per_judge_metrics.csv`",
        "- `item_predictions.csv`",
        "- `task_predictions.csv`",
        "- `human_item_targets.csv`",
        "- `plots/`",
        "",
        "## Caveat",
        "Per-task isotonic fits a monotone map on each task's three candidates using the same items used for evaluation (calibration upper bound, analogous to EXP32).",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".matplotlib_cache"))
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = args.out_dir / "plots"

    by_item, raters = load_participant_labels(args.human_dir)
    human_target = build_human_target(by_item, raters, args.human_target)

    if args.plots_only:
        metrics = _read_metrics_csv(args.out_dir / "per_judge_metrics.csv")
        pred_rows = _read_csv_rows(args.out_dir / "item_predictions.csv")
        task_rows = _read_csv_rows(args.out_dir / "task_predictions.csv")
        overlap_items = sorted({r["item_key"] for r in pred_rows})
        overlap_tasks = len({k.split("::", 1)[0] for k in overlap_items})
    else:
        judge_meta, judge_scores = load_judge_scores(args.result_dirs)
        metrics, pred_rows, task_rows = analyze_and_predict(human_target, judge_meta, judge_scores)
        write_csv(args.out_dir / "human_item_targets.csv", list(human_target.values()))
        write_csv(args.out_dir / "per_judge_metrics.csv", metrics)
        write_csv(args.out_dir / "item_predictions.csv", pred_rows)
        write_csv(args.out_dir / "task_predictions.csv", task_rows)
        overlap_items = sorted(set().union(*[set(v) for v in judge_scores.values()]) & set(human_target))
        overlap_tasks = len({k.split("::", 1)[0] for k in overlap_items})
    highlight_metrics = [r for r in metrics if r["judge_id"] in args.highlight_judges and r["kind"] == "llm"]
    highlight_metrics.sort(key=lambda r: -r["per_task_iso_item_spearman_r"])
    best_llm = highlight_metrics[0] if highlight_metrics else next((r for r in metrics if r["kind"] == "llm"), None)
    summary = {
        "experiment": "exp38_five_human_per_task_isotonic",
        "human_target_method": args.human_target,
        "n_human_items": len(human_target),
        "n_overlap_items": len(overlap_items),
        "n_overlap_tasks": overlap_tasks,
        "n_judges": len(metrics),
        "best_llm": best_llm,
        "tldr": (
            f"Five-rater `{args.human_target}` target with per-task isotonic calibration. "
            f"Best LLM item Spearman: `{best_llm['per_task_iso_item_spearman_r']:.3f}` "
            f"({best_llm['judge_id']}) vs raw `{best_llm['raw_item_spearman_r']:.3f}`."
            if best_llm
            else "No LLM judges evaluated."
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    write_report(args.out_dir, summary, metrics)

    plot_paths: List[Path] = []
    setup_style()
    plot_paths.extend(plot_gain(metrics, plots_dir))
    plot_paths.extend(plot_top3_scatter(metrics, pred_rows, plots_dir, args.highlight_judges))
    plot_paths.extend(plot_highlight_panels(args.highlight_judges, metrics, pred_rows, plots_dir))
    plot_paths.extend(plot_task_scatter(args.highlight_judges, task_rows, metrics, plots_dir))
    if args.copy_paper_figs:
        plot_paths.extend(copy_plots_to_paper(plots_dir, args.paper_fig_dir))

    print(f"Wrote {args.out_dir}")
    if best_llm:
        print(
            f"Best LLM: {best_llm['judge_id']} "
            f"raw={best_llm['raw_item_spearman_r']:.3f} "
            f"iso={best_llm['per_task_iso_item_spearman_r']:.3f}"
        )
    print("Plots:")
    for path in plot_paths:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
