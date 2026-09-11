#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
FLOAT_TIE_DIGITS = 12
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp34_all_human_task_aggregation"
DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP34: aggregate all new human labels and re-correlate cached judge scores")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument("--include-old-prompt", action="store_true")
    return p.parse_args()


def to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def mean(values: Sequence[float]) -> float:
    vals = [v for v in values if math.isfinite(v)]
    return round(math.fsum(vals) / len(vals), FLOAT_TIE_DIGITS) if vals else float("nan")


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


def kendall_tau_b(xs: Sequence[float], ys: Sequence[float]) -> float:
    concordant = discordant = ties_x = ties_y = 0
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            dx = (xs[i] > xs[j]) - (xs[i] < xs[j])
            dy = (ys[i] > ys[j]) - (ys[i] < ys[j])
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                ties_x += 1
            elif dy == 0:
                ties_y += 1
            elif dx == dy:
                concordant += 1
            else:
                discordant += 1
    den = math.sqrt((concordant + discordant + ties_x) * (concordant + discordant + ties_y))
    return (concordant - discordant) / den if den else float("nan")


def safe_corr(xs: Sequence[float], ys: Sequence[float]) -> dict:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return {"n": len(pairs), "spearman_r": float("nan"), "pearson_r": float("nan"), "kendall_tau": float("nan")}
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    if len(set(x)) < 2 or len(set(y)) < 2:
        return {"n": len(pairs), "spearman_r": float("nan"), "pearson_r": float("nan"), "kendall_tau": float("nan")}
    return {"n": len(pairs), "spearman_r": spearman(x, y), "pearson_r": pearson(x, y), "kendall_tau": kendall_tau_b(x, y)}


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


def load_human_labels(human_dir: Path, include_old_prompt: bool) -> Tuple[List[dict], List[dict]]:
    files = sorted(human_dir.glob("*.tsv"))
    if include_old_prompt:
        files += sorted((human_dir / "old_prompt").glob("*.tsv"))
    rows: List[dict] = []
    dropped: List[dict] = []
    for path in files:
        with path.open(newline="", encoding="utf-8") as f:
            for line_no, row in enumerate(csv.DictReader(f, delimiter="\t"), start=2):
                gold = str(row.get("gold_file", "")).strip()
                cand, score_text = clean_candidate_and_score(row.get("candidate_file", ""), row.get("human_score_0_5", ""))
                score = to_float(score_text)
                if not gold or not cand or not math.isfinite(score):
                    dropped.append({"source_file": str(path.relative_to(REPO_ROOT)), "line_no": line_no, "gold_file": gold, "candidate_file": cand, "human_score_0_5": score_text})
                    continue
                rows.append(
                    {
                        "source_file": str(path.relative_to(REPO_ROOT)),
                        "rater": path.stem,
                        "gold_file": gold,
                        "candidate_file": cand,
                        "item_key": f"{gold}::{cand}",
                        "human_score_0_5": score,
                        "human_score_0_1": score / 5.0,
                    }
                )
    if not rows:
        raise ValueError(f"No usable human labels under {human_dir}")
    return rows, dropped


def load_judge_scores(result_dirs: Iterable[Path]) -> Tuple[List[dict], Dict[str, Dict[str, dict]]]:
    meta_by_judge: Dict[str, dict] = {}
    score_by_judge: Dict[str, Dict[str, dict]] = defaultdict(dict)
    for result_dir in result_dirs:
        judge_rows_path = result_dir / "judge_rows.csv"
        detail_rows_path = result_dir / "detail_rows.csv"
        if not judge_rows_path.exists() or not detail_rows_path.exists():
            continue
        with judge_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                judge_id = row["judge_id"]
                if judge_id in meta_by_judge:
                    continue
                meta_by_judge[judge_id] = {
                    "judge_id": judge_id,
                    "kind": row.get("kind", ""),
                    "model": row.get("model", ""),
                    "prompt_name": row.get("prompt_name", ""),
                    "source_dir": str(result_dir.relative_to(REPO_ROOT)),
                    "cert_index": to_float(row.get("cert_index")),
                    "cert_index_v2": to_float(row.get("cert_index_v2")),
                }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                judge_id = row["judge_id"]
                item_key = row["item_key"]
                if judge_id not in meta_by_judge or item_key in score_by_judge[judge_id]:
                    continue
                gold_file, candidate_file = item_key.split("::", 1)
                score_by_judge[judge_id][item_key] = {
                    "judge_id": judge_id,
                    "gold_file": gold_file,
                    "candidate_file": candidate_file,
                    "item_key": item_key,
                    "judge_score": to_float(row.get("score_mean")),
                }
    return sorted(meta_by_judge.values(), key=lambda r: r["judge_id"]), score_by_judge


def aggregate_human_targets(labels: List[dict]) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    by_item: Dict[str, List[dict]] = defaultdict(list)
    for row in labels:
        by_item[row["item_key"]].append(row)
    item_targets: Dict[str, dict] = {}
    for item_key, rows in by_item.items():
        gold = rows[0]["gold_file"]
        cand = rows[0]["candidate_file"]
        item_targets[item_key] = {
            "gold_file": gold,
            "candidate_file": cand,
            "item_key": item_key,
            "human_score": mean([r["human_score_0_1"] for r in rows]),
            "n_labels": len(rows),
            "n_raters": len({r["rater"] for r in rows}),
        }
    by_task: Dict[str, List[dict]] = defaultdict(list)
    for row in item_targets.values():
        by_task[row["gold_file"]].append(row)
    task_targets = {
        task: {
            "task": task,
            "human_score": mean([r["human_score"] for r in rows]),
            "n_items": len(rows),
            "n_labels": sum(int(r["n_labels"]) for r in rows),
        }
        for task, rows in by_task.items()
    }
    return item_targets, task_targets


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(out_dir: Path, summary: dict, judge_metrics: List[dict], meta_metrics: List[dict]) -> None:
    top_task = sorted(
        [r for r in judge_metrics if r["target_name"] == "all_human_mean" and r["level"] == "task"],
        key=lambda r: (r["spearman_r"], r["pearson_r"]),
        reverse=True,
    )[:10]
    item_meta = next(r for r in meta_metrics if r["level"] == "item" and r["x_metric"] == "cert_index_v2")
    task_meta = next(r for r in meta_metrics if r["level"] == "task" and r["x_metric"] == "cert_index_v2")
    best_task_text = (
        f"`{top_task[0]['spearman_r']:.3f}` for `{top_task[0]['judge_id']}`"
        if top_task
        else "`nan` because no task-level judge overlaps were found"
    )
    lines = [
        "# EXP34 Report: All-Human Task Aggregation",
        "**TLDR:** Aggregates all current human labels by item and task, then correlates cached judge scores with the aggregate human target. The task-level view gives the strongest absolute judge-human agreement, while trust-index meta-correlation remains modest.",
        "",
        "## Data",
        f"- Human label files used: {summary['n_human_files_used']}",
        f"- Usable human labels: {summary['n_usable_labels']}",
        f"- Distinct labeled items: {summary['n_distinct_items']}",
        f"- Distinct labeled tasks: {summary['n_distinct_tasks']}",
        f"- Items overlapping cached judge scores: {summary['n_overlap_items']}",
        f"- Tasks overlapping cached judge scores: {summary['n_overlap_tasks']}",
        "",
        "## Main Result",
        f"- Item-level meta-Spearman between `cert_index_v2` and judge-human alignment: `{item_meta['meta_spearman_r']:.3f}`.",
        f"- Task-level meta-Spearman between `cert_index_v2` and judge-human alignment: `{task_meta['meta_spearman_r']:.3f}`.",
        f"- Best task-level judge-human Spearman over the all-rater target: {best_task_text}.",
        "",
        "## Top Task-Level Judges",
        "| Judge | cert_v2 | Task Spearman | Task Pearson | n tasks | Source |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in top_task:
        lines.append(
            f"| {row['judge_id']} | {row['cert_index_v2']:.3f} | {row['spearman_r']:.3f} | {row['pearson_r']:.3f} | {int(row['n'])} | {row['source_dir']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "- Aggregating all current human raters by task gives the strongest aggregate judge-human agreement in this run, but it remains moderate rather than 0.7+.",
        "- This should be written as task-level agreement with the aggregate human evaluation function; it is smoother than item-level agreement.",
        "- The trust-index-to-human-alignment meta-correlation remains modest, so this supports reporting the strongest task-level judge-human agreement separately from any claim that the trust index alone ranks judges across the panel.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    labels, dropped = load_human_labels(args.human_dir, args.include_old_prompt)
    judges, score_by_judge = load_judge_scores(args.result_dirs)
    item_targets, task_targets = aggregate_human_targets(labels)

    judge_metrics: List[dict] = []
    item_score_rows: List[dict] = []
    task_score_rows: List[dict] = []
    for judge in judges:
        pair_scores = score_by_judge.get(judge["judge_id"], {})
        common_items = sorted(set(pair_scores) & set(item_targets))
        item_x = [pair_scores[k]["judge_score"] for k in common_items]
        item_y = [item_targets[k]["human_score"] for k in common_items]
        item_corr = safe_corr(item_x, item_y)
        judge_metrics.append({**judge, "target_name": "all_human_mean", "level": "item", **item_corr})
        for k in common_items:
            item_score_rows.append({**pair_scores[k], "human_score": item_targets[k]["human_score"], "n_labels": item_targets[k]["n_labels"], "n_raters": item_targets[k]["n_raters"]})

        by_task: Dict[str, List[float]] = defaultdict(list)
        for row in pair_scores.values():
            if row["gold_file"] in task_targets:
                by_task[row["gold_file"]].append(row["judge_score"])
        common_tasks = sorted(set(by_task) & set(task_targets))
        task_x = [mean(by_task[t]) for t in common_tasks]
        task_y = [task_targets[t]["human_score"] for t in common_tasks]
        task_corr = safe_corr(task_x, task_y)
        judge_metrics.append({**judge, "target_name": "all_human_mean", "level": "task", **task_corr})
        for task in common_tasks:
            task_score_rows.append(
                {
                    "judge_id": judge["judge_id"],
                    "task": task,
                    "judge_score": mean(by_task[task]),
                    "human_score": task_targets[task]["human_score"],
                    "n_items": task_targets[task]["n_items"],
                    "n_labels": task_targets[task]["n_labels"],
                }
            )

    meta_metrics: List[dict] = []
    for level in ["item", "task"]:
        rows = [r for r in judge_metrics if r["level"] == level]
        for x_metric in ["cert_index", "cert_index_v2"]:
            corr = safe_corr([r[x_metric] for r in rows], [r["spearman_r"] for r in rows])
            meta_metrics.append(
                {
                    "target_name": "all_human_mean",
                    "level": level,
                    "x_metric": x_metric,
                    "n_judges": corr["n"],
                    "meta_spearman_r": corr["spearman_r"],
                    "meta_pearson_r": corr["pearson_r"],
                    "meta_kendall_tau": corr["kendall_tau"],
                }
            )

    judge_metrics.sort(key=lambda r: (r["target_name"], r["level"], -999 if not math.isfinite(r["spearman_r"]) else -r["spearman_r"], r["judge_id"]))
    summary = {
        "experiment": "exp34_all_human_task_aggregation",
        "include_old_prompt": bool(args.include_old_prompt),
        "n_human_files_used": len({r["source_file"] for r in labels}),
        "n_usable_labels": len(labels),
        "n_dropped_labels": len(dropped),
        "n_distinct_items": len(item_targets),
        "n_distinct_tasks": len(task_targets),
        "n_overlap_items": len(set().union(*[set(v) for v in score_by_judge.values()]) & set(item_targets)),
        "n_overlap_tasks": len({row["gold_file"] for scores in score_by_judge.values() for row in scores.values()} & set(task_targets)),
        "n_judges": len(judges),
        "result_dirs": [str(p.relative_to(REPO_ROOT)) for p in args.result_dirs],
    }

    write_csv(args.out_dir / "human_labels_cleaned.csv", labels)
    write_csv(args.out_dir / "dropped_human_labels.csv", dropped)
    write_csv(args.out_dir / "all_human_item_targets.csv", list(item_targets.values()))
    write_csv(args.out_dir / "all_human_task_targets.csv", list(task_targets.values()))
    write_csv(args.out_dir / "judge_alignment_metrics.csv", judge_metrics)
    write_csv(args.out_dir / "meta_trends.csv", meta_metrics)
    write_csv(args.out_dir / "item_level_scores.csv", item_score_rows)
    write_csv(args.out_dir / "task_level_scores.csv", task_score_rows)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(args.out_dir, summary, judge_metrics, meta_metrics)
    print(f"Wrote {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
