#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp29_task_aggregated_human_alignment"

DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_claude_oauth_haiku45_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]

DEFAULT_HUMAN_FILES = {
    "ethan_pass1": REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "ethan_human_scores_20260425.tsv",
    "ethan_pass2": REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "ethan_human_scores_ORIGINAL.tsv",
    "ethan_avg": REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "ethan_human_scores_avg_two_passes_20260425.tsv",
    "jolene_pass1": REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "jolene_data_pass_1.tsv",
    "steven_pass1": REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "steven_data_pass_1.tsv",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP29: task-aggregated human alignment re-analysis")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument(
        "--result-dirs",
        nargs="*",
        type=Path,
        default=DEFAULT_RESULT_DIRS,
        help="Directories containing EXP16-style judge_rows.csv and detail_rows.csv",
    )
    return p.parse_args()


def read_tsv_scores(path: Path) -> Dict[Tuple[str, str], float]:
    rows: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gold = str(row.get("gold_file", "")).strip()
            cand = str(row.get("candidate_file", "")).strip()
            score = str(row.get("human_score_0_5", "")).strip()
            if not gold or not cand or not score:
                continue
            try:
                score_val = float(score)
            except ValueError:
                continue
            rows[(gold, cand)].append(score_val / 5.0)
    return {k: float(sum(v) / len(v)) for k, v in rows.items()}


def safe_corr(xs: Sequence[float], ys: Sequence[float]) -> Dict[str, float]:
    if len(xs) < 2:
        return {
            "spearman_r": float("nan"),
            "spearman_p": float("nan"),
            "pearson_r": float("nan"),
            "pearson_p": float("nan"),
            "kendall_tau": float("nan"),
            "kendall_p": float("nan"),
        }
    sx, sp = spearmanr(xs, ys)
    if len(xs) < 3:
        kx, kp = (float("nan"), float("nan"))
    else:
        k = kendalltau(xs, ys)
        kx, kp = (float(k.statistic), float(k.pvalue))
    try:
        px, pp = pearsonr(xs, ys)
    except Exception:
        px, pp = (float("nan"), float("nan"))
    return {
        "spearman_r": float(sx),
        "spearman_p": float(sp),
        "pearson_r": float(px),
        "pearson_p": float(pp),
        "kendall_tau": float(kx),
        "kendall_p": float(kp),
    }


def aggregate_pairs_to_tasks(pair_scores: Dict[Tuple[str, str], float]) -> Dict[str, float]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for (gold, _cand), score in pair_scores.items():
        buckets[gold].append(float(score))
    return {task: float(sum(vals) / len(vals)) for task, vals in buckets.items() if vals}


def intersect_pair_scores(
    judge_pairs: Dict[Tuple[str, str], float], human_pairs: Dict[Tuple[str, str], float]
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]:
    keys = sorted(set(judge_pairs) & set(human_pairs))
    return ({k: judge_pairs[k] for k in keys}, {k: human_pairs[k] for k in keys})


def ensemble_task_target(
    rater_task_maps: Dict[str, Dict[str, float]], raters: Sequence[str]
) -> Dict[str, float]:
    common_tasks = set.intersection(*[set(rater_task_maps[r]) for r in raters])
    out: Dict[str, float] = {}
    for task in sorted(common_tasks):
        out[task] = float(np.mean([rater_task_maps[r][task] for r in raters]))
    return out


def load_judge_data(result_dirs: Iterable[Path]) -> Tuple[List[dict], Dict[str, Dict[Tuple[str, str], float]], Dict[str, str]]:
    judge_meta: Dict[str, dict] = {}
    judge_pair_scores: Dict[str, Dict[Tuple[str, str], float]] = defaultdict(dict)
    judge_sources: Dict[str, str] = {}

    for result_dir in result_dirs:
        judge_rows_path = result_dir / "judge_rows.csv"
        detail_rows_path = result_dir / "detail_rows.csv"
        if not judge_rows_path.exists() or not detail_rows_path.exists():
            continue

        with judge_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                judge_id = row["judge_id"]
                if judge_id in judge_meta:
                    continue
                judge_meta[judge_id] = {
                    "judge_id": judge_id,
                    "kind": row.get("kind", ""),
                    "model": row.get("model", ""),
                    "prompt_name": row.get("prompt_name", ""),
                    "cert_index": float(row.get("cert_index", "nan")),
                    "cert_index_v2": float(row.get("cert_index_v2", "nan")),
                    "candidate_level_human_spearman_avg": float(row.get("human_spearman_r_avg", "nan")),
                }
                judge_sources[judge_id] = str(result_dir.relative_to(REPO_ROOT))

        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                judge_id = row["judge_id"]
                if judge_id not in judge_meta:
                    continue
                if judge_id in judge_pair_scores and judge_pair_scores[judge_id]:
                    existing_keys = judge_pair_scores[judge_id]
                else:
                    existing_keys = None
                item_key = row["item_key"]
                gold_file, candidate_file = item_key.split("::", 1)
                pair_key = (gold_file, candidate_file)
                if pair_key in judge_pair_scores[judge_id]:
                    continue
                judge_pair_scores[judge_id][pair_key] = float(row["score_mean"])

    judges = sorted(judge_meta.values(), key=lambda row: row["judge_id"])
    return judges, judge_pair_scores, judge_sources


def family_name(judge_id: str) -> str:
    if "|" in judge_id:
        return judge_id.split("|", 1)[0]
    return judge_id


def make_plots(
    out_dir: Path,
    judge_target_rows: List[dict],
    meta_rows: List[dict],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)

    def plot_trust_scatter(target_name: str, filename: str) -> None:
        rows = [r for r in judge_target_rows if r["target_name"] == target_name]
        xs = [r["cert_index_v2"] for r in rows]
        ys = [r["task_spearman_r"] for r in rows]
        fig, ax = plt.subplots(figsize=(9.2, 6.2))
        ax.scatter(xs, ys, s=72)
        for row in rows:
            ax.annotate(row["judge_id"], (row["cert_index_v2"], row["task_spearman_r"]), xytext=(4, 4), textcoords="offset points", fontsize=7)
        if len(xs) >= 2:
            z = np.polyfit(xs, ys, 1)
            xline = np.linspace(min(xs), max(xs), 100)
            ax.plot(xline, z[0] * xline + z[1], "r--", linewidth=1.5)
        meta = next(r for r in meta_rows if r["target_name"] == target_name and r["level"] == "task" and r["x_metric"] == "cert_index_v2")
        ax.set_xlabel("Judge Trust Index / cert_index_v2")
        ax.set_ylabel("Task-level human alignment (Spearman)")
        ax.set_title(
            f"{target_name}: trust vs task-level alignment\n"
            f"Spearman across judges = {meta['meta_spearman_r']:.3f}, Pearson = {meta['meta_pearson_r']:.3f}"
        )
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    plot_trust_scatter("ethan_avg", "fig_trust_vs_task_ethan_avg.png")
    plot_trust_scatter("human_ensemble_2r", "fig_trust_vs_task_human_ensemble_2r.png")
    plot_trust_scatter("human_ensemble_3r", "fig_trust_vs_task_human_ensemble_3r.png")

    rows = [r for r in judge_target_rows if r["target_name"] == "ethan_avg"]
    fig, ax = plt.subplots(figsize=(8.0, 8.0))
    xs = [r["pair_spearman_r"] for r in rows]
    ys = [r["task_spearman_r"] for r in rows]
    ax.scatter(xs, ys, s=72)
    for row in rows:
        ax.annotate(row["judge_id"], (row["pair_spearman_r"], row["task_spearman_r"]), xytext=(4, 4), textcoords="offset points", fontsize=7)
    lo = min(xs + ys)
    hi = max(xs + ys)
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1.0)
    ax.set_xlabel("Candidate-file-level human alignment (Spearman)")
    ax.set_ylabel("Task-level human alignment (Spearman)")
    ax.set_title("Ethan avg target: pair-level vs task-level judge alignment")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_pair_vs_task_ethan_avg.png", dpi=180)
    plt.close(fig)


def write_report(
    out_dir: Path,
    judge_target_rows: List[dict],
    meta_rows: List[dict],
    ensemble_2r_tasks: Dict[str, float],
    ensemble_3r_tasks: Dict[str, float],
) -> None:
    def meta_line(target_name: str, level: str) -> dict:
        return next(r for r in meta_rows if r["target_name"] == target_name and r["level"] == level and r["x_metric"] == "cert_index_v2")

    eth_pair = meta_line("ethan_avg", "pair")
    eth_task = meta_line("ethan_avg", "task")
    ens2_task = meta_line("human_ensemble_2r", "task")
    ens3_task = meta_line("human_ensemble_3r", "task")

    if eth_task["meta_spearman_r"] > eth_pair["meta_spearman_r"]:
        eth_direction = "strengthens"
    elif eth_task["meta_spearman_r"] < eth_pair["meta_spearman_r"]:
        eth_direction = "weakens"
    else:
        eth_direction = "leaves unchanged"

    top_ethan = sorted(
        [r for r in judge_target_rows if r["target_name"] == "ethan_avg"],
        key=lambda r: (r["task_spearman_r"], r["task_pearson_r"]),
        reverse=True,
    )[:8]

    lines: List[str] = []
    lines.append("# EXP29 Report: Task-Aggregated Human Alignment")
    lines.append("")
    lines.append("## Protocol")
    lines.append("")
    lines.append("Primary target:")
    lines.append("")
    lines.append("```math")
    lines.append("H(t) = \\frac{1}{|A|}\\sum_{a \\in A} h(t,a), \\qquad J(t) = \\frac{1}{|A|}\\sum_{a \\in A} j(t,a)")
    lines.append("```")
    lines.append("")
    lines.append("We correlate `H(t)` and `J(t)` across tasks, not across individual candidate files. This makes the target explicit: the judge is evaluated as a proxy for the aggregate human evaluation function used to compare tasks.")
    lines.append("")
    lines.append("The ensemble analysis reports two targets: a 20-task 2-rater ensemble over `ethan_avg` and `jolene_pass1`, and a 10-task 3-rater robustness slice that additionally includes `steven_pass1`. Each task score is defined as the mean of the three candidate files for each rater and then averaged across raters.")
    lines.append("")
    lines.append("## Main Results")
    lines.append("")
    lines.append(f"- Moving from candidate-file-level to task-level aggregation {eth_direction} the `ethan_avg` trust plot: meta-Spearman(`cert_index_v2`, human alignment) changes from `{eth_pair['meta_spearman_r']:.3f}` to `{eth_task['meta_spearman_r']:.3f}`, and meta-Pearson changes from `{eth_pair['meta_pearson_r']:.3f}` to `{eth_task['meta_pearson_r']:.3f}`.")
    lines.append(f"- The 2-rater ensemble target (`ethan_avg` + `jolene_pass1`, 20 tasks) is essentially flat: meta-Spearman(`cert_index_v2`, human alignment) = `{ens2_task['meta_spearman_r']:.3f}`, meta-Pearson = `{ens2_task['meta_pearson_r']:.3f}`.")
    lines.append(f"- The 3-rater ensemble target (`ethan_avg` + `jolene_pass1` + `steven_pass1`, 10 tasks) is somewhat more positive but still unstable: meta-Spearman(`cert_index_v2`, human alignment) = `{ens3_task['meta_spearman_r']:.3f}`, meta-Pearson = `{ens3_task['meta_pearson_r']:.3f}`.")
    lines.append("")
    lines.append("## Important Plots")
    lines.append("")
    lines.append(f"- [Trust vs task-level Ethan average](./fig_trust_vs_task_ethan_avg.png)")
    lines.append(f"- [Trust vs task-level 2-rater human ensemble](./fig_trust_vs_task_human_ensemble_2r.png)")
    lines.append(f"- [Trust vs task-level 3-rater human ensemble](./fig_trust_vs_task_human_ensemble_3r.png)")
    lines.append(f"- [Pair-level vs task-level alignment for Ethan average](./fig_pair_vs_task_ethan_avg.png)")
    lines.append("")
    lines.append("## Best Judges On Ethan Avg Task Target")
    lines.append("")
    lines.append("| Judge | cert_v2 | Task Spearman | Task Pearson | Source |")
    lines.append("| --- | ---: | ---: | ---: | --- |")
    for row in top_ethan:
        lines.append(
            f"| {row['judge_id']} | {row['cert_index_v2']:.3f} | {row['task_spearman_r']:.3f} | {row['task_pearson_r']:.3f} | {row['source_dir']} |"
        )
    lines.append("")
    lines.append("## Notable Outlier Movement")
    lines.append("")
    lines.append("- `gpt-4o-mini|P1_BASELINE` improves from pair-level Spearman `0.287` to task-level Spearman `0.463` on `ethan_avg`.")
    lines.append("- `gpt-4o-mini|P4_CHECKLIST` improves from `0.065` to `0.233` on `ethan_avg`.")
    lines.append("- `labs-leanstral-2603|P4_CHECKLIST` improves from `0.206` to `0.301` on `ethan_avg`, but the other LeanStral prompts remain near zero or negative.")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This analysis reuses saved EXP16 per-pair judge scores only; it does not make new judge calls.")
    lines.append("- Because the saved EXP16 judge runs cover 72 candidate pairs, `ethan_avg` is evaluated on the corresponding 24-task subset rather than the full 25-task file.")
    lines.append("- `jolene_pass1` overlaps with the EXP16 subset on 20 tasks; `steven_pass1` has numeric labels on only 10 of those tasks.")
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    human_pair_maps = {name: read_tsv_scores(path) for name, path in DEFAULT_HUMAN_FILES.items()}
    judges, judge_pair_scores, judge_sources = load_judge_data(args.result_dirs)

    human_task_maps = {name: aggregate_pairs_to_tasks(scores) for name, scores in human_pair_maps.items()}

    ensemble_2r_raters = ["ethan_avg", "jolene_pass1"]
    ensemble_3r_raters = ["ethan_avg", "jolene_pass1", "steven_pass1"]
    ensemble_2r_tasks = ensemble_task_target(human_task_maps, ensemble_2r_raters)
    ensemble_3r_tasks = ensemble_task_target(human_task_maps, ensemble_3r_raters)

    target_pair_maps: Dict[str, Dict[Tuple[str, str], float]] = dict(human_pair_maps)
    target_task_maps: Dict[str, Dict[str, float]] = dict(human_task_maps)
    target_task_maps["human_ensemble_2r"] = ensemble_2r_tasks
    target_task_maps["human_ensemble_3r"] = ensemble_3r_tasks

    judge_target_rows: List[dict] = []
    task_level_score_rows: List[dict] = []

    for judge in judges:
        judge_id = judge["judge_id"]
        pair_scores = judge_pair_scores.get(judge_id, {})
        if not pair_scores:
            continue

        for target_name, human_pairs in target_pair_maps.items():
            judge_pairs_overlap, human_pairs_overlap = intersect_pair_scores(pair_scores, human_pairs)
            if len(judge_pairs_overlap) < 2:
                continue
            pair_corr = safe_corr(
                [judge_pairs_overlap[k] for k in judge_pairs_overlap],
                [human_pairs_overlap[k] for k in judge_pairs_overlap],
            )
            judge_tasks = aggregate_pairs_to_tasks(judge_pairs_overlap)
            human_tasks = aggregate_pairs_to_tasks(human_pairs_overlap)
            common_tasks = sorted(set(judge_tasks) & set(human_tasks))
            task_corr = safe_corr(
                [judge_tasks[t] for t in common_tasks],
                [human_tasks[t] for t in common_tasks],
            )
            judge_target_rows.append(
                {
                    **judge,
                    "source_dir": judge_sources.get(judge_id, ""),
                    "family": family_name(judge_id),
                    "target_name": target_name,
                    "n_pairs": len(judge_pairs_overlap),
                    "n_tasks": len(common_tasks),
                    "pair_spearman_r": pair_corr["spearman_r"],
                    "pair_spearman_p": pair_corr["spearman_p"],
                    "pair_pearson_r": pair_corr["pearson_r"],
                    "pair_pearson_p": pair_corr["pearson_p"],
                    "pair_kendall_tau": pair_corr["kendall_tau"],
                    "task_spearman_r": task_corr["spearman_r"],
                    "task_spearman_p": task_corr["spearman_p"],
                    "task_pearson_r": task_corr["pearson_r"],
                    "task_pearson_p": task_corr["pearson_p"],
                    "task_kendall_tau": task_corr["kendall_tau"],
                }
            )

        for ensemble_target_name in ["human_ensemble_2r", "human_ensemble_3r"]:
            human_tasks = target_task_maps[ensemble_target_name]
            judge_tasks_all = aggregate_pairs_to_tasks(
                {k: v for k, v in pair_scores.items() if k[0] in human_tasks}
            )
            common_tasks = sorted(set(judge_tasks_all) & set(human_tasks))
            task_corr = safe_corr(
                [judge_tasks_all[t] for t in common_tasks],
                [human_tasks[t] for t in common_tasks],
            )
            judge_target_rows.append(
                {
                    **judge,
                    "source_dir": judge_sources.get(judge_id, ""),
                    "family": family_name(judge_id),
                    "target_name": ensemble_target_name,
                    "n_pairs": len([k for k in pair_scores if k[0] in common_tasks]),
                    "n_tasks": len(common_tasks),
                    "pair_spearman_r": float("nan"),
                    "pair_spearman_p": float("nan"),
                    "pair_pearson_r": float("nan"),
                    "pair_pearson_p": float("nan"),
                    "pair_kendall_tau": float("nan"),
                    "task_spearman_r": task_corr["spearman_r"],
                    "task_spearman_p": task_corr["spearman_p"],
                    "task_pearson_r": task_corr["pearson_r"],
                    "task_pearson_p": task_corr["pearson_p"],
                    "task_kendall_tau": task_corr["kendall_tau"],
                }
            )

            for task in common_tasks:
                task_level_score_rows.append(
                    {
                        "judge_id": judge_id,
                        "target_name": ensemble_target_name,
                        "task": task,
                        "judge_task_score": judge_tasks_all[task],
                        "human_task_score": human_tasks[task],
                    }
                )

    meta_rows: List[dict] = []
    for target_name in sorted({row["target_name"] for row in judge_target_rows}):
        rows = [r for r in judge_target_rows if r["target_name"] == target_name]
        for x_metric in ["cert_index", "cert_index_v2"]:
            xs = np.asarray([r[x_metric] for r in rows], dtype=float)
            for level, y_key in [("pair", "pair_spearman_r"), ("task", "task_spearman_r")]:
                ys = np.asarray([r[y_key] for r in rows], dtype=float)
                mask = np.isfinite(xs) & np.isfinite(ys)
                corr = safe_corr(xs[mask].tolist(), ys[mask].tolist())
                meta_rows.append(
                    {
                        "target_name": target_name,
                        "x_metric": x_metric,
                        "level": level,
                        "n_judges": int(mask.sum()),
                        "meta_spearman_r": corr["spearman_r"],
                        "meta_spearman_p": corr["spearman_p"],
                        "meta_pearson_r": corr["pearson_r"],
                        "meta_pearson_p": corr["pearson_p"],
                        "meta_kendall_tau": corr["kendall_tau"],
                        "meta_kendall_p": corr["kendall_p"],
                    }
                )

    judge_target_rows.sort(key=lambda r: (r["target_name"], -r["task_spearman_r"] if math.isfinite(r["task_spearman_r"]) else -999, r["judge_id"]))

    with (args.out_dir / "judge_target_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(judge_target_rows[0].keys()))
        w.writeheader()
        w.writerows(judge_target_rows)

    with (args.out_dir / "meta_trends.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(meta_rows[0].keys()))
        w.writeheader()
        w.writerows(meta_rows)

    with (args.out_dir / "task_level_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(task_level_score_rows[0].keys()))
        w.writeheader()
        w.writerows(task_level_score_rows)

    summary = {
        "experiment": "exp29_task_aggregated_human_alignment",
        "n_unique_judges": len(judges),
        "result_dirs": [str(p.relative_to(REPO_ROOT)) for p in args.result_dirs],
        "human_targets": list(DEFAULT_HUMAN_FILES.keys()) + ["human_ensemble_2r", "human_ensemble_3r"],
        "ensemble_2r_raters": ensemble_2r_raters,
        "ensemble_2r_n_tasks": len(ensemble_2r_tasks),
        "ensemble_3r_raters": ensemble_3r_raters,
        "ensemble_3r_n_tasks": len(ensemble_3r_tasks),
        "meta_trends": meta_rows,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    make_plots(args.out_dir, judge_target_rows, meta_rows)
    write_report(args.out_dir, judge_target_rows, meta_rows, ensemble_2r_tasks, ensemble_3r_tasks)

    print(f"Wrote {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
