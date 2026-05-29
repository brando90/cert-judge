#!/usr/bin/env python3
"""
EXP36: Super-human pass3 target from all five participant annotators.

Brando plan:
  1. Average participant1..participant5 scores per (gold, candidate) pair.
  2. Treat the aggregate as a single human label set ("super_human_pass3").
  3. Re-run the same pair-level + task-level judge-human analysis used for ethan_avg.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_DATA_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "data"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp36_super_human_pass3"
DEFAULT_SUPER_TSV = DEFAULT_DATA_DIR / "super_human_pass3_avg_five_raters.tsv"
DEFAULT_ETHAN_TSV = DEFAULT_DATA_DIR / "ethan_human_scores_avg_two_passes_20260425.tsv"
FLOAT_TIE_DIGITS = 12
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
    p = argparse.ArgumentParser(description="EXP36: super-human pass3 aggregation and judge-human re-analysis")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--super-tsv", type=Path, default=DEFAULT_SUPER_TSV)
    p.add_argument("--ethan-tsv", type=Path, default=DEFAULT_ETHAN_TSV)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument("--min-raters", type=int, default=1, help="Require at least this many participant ratings per item")
    return p.parse_args()


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


def safe_corr(xs: Sequence[float], ys: Sequence[float]) -> dict:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return {"n": len(pairs), "spearman_r": float("nan"), "pearson_r": float("nan")}
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    if len(set(x)) < 2 or len(set(y)) < 2:
        return {"n": len(pairs), "spearman_r": float("nan"), "pearson_r": float("nan")}
    return {"n": len(pairs), "spearman_r": spearman(x, y), "pearson_r": pearson(x, y)}


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


def build_super_human_tsv(human_dir: Path, out_path: Path, min_raters: int) -> Tuple[List[dict], dict]:
    by_item: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
    participant_files = sorted(human_dir.glob("participant*.tsv"))
    for path in participant_files:
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gold = str(row.get("gold_file", "")).strip()
                cand, score_text = clean_candidate_and_score(row.get("candidate_file", ""), row.get("human_score_0_5", ""))
                try:
                    score = float(score_text)
                except (TypeError, ValueError):
                    continue
                if not gold or not cand:
                    continue
                by_item[(gold, cand)].append(
                    {
                        "rater": path.stem,
                        "human_score_0_5": score,
                    }
                )

    rows: List[dict] = []
    for (gold, cand), ratings in sorted(by_item.items()):
        if len(ratings) < min_raters:
            continue
        avg_0_5 = mean([r["human_score_0_5"] for r in ratings])
        rows.append(
            {
                "gold_file": gold,
                "candidate_file": cand,
                "human_score_0_5": avg_0_5,
                "human_score_0_1": avg_0_5 / 5.0,
                "n_raters": len(ratings),
                "n_labels": len(ratings),
                "raters": "|".join(sorted({r["rater"] for r in ratings})),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["gold_file", "candidate_file", "human_score_0_5"], delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "gold_file": row["gold_file"],
                    "candidate_file": row["candidate_file"],
                    "human_score_0_5": f"{row['human_score_0_5']:.6f}",
                }
            )

    meta = {
        "n_participant_files": len(participant_files),
        "participant_files": [str(p.relative_to(REPO_ROOT)) for p in participant_files],
        "n_items": len(rows),
        "min_raters": min_raters,
        "n_items_with_5_raters": sum(1 for r in rows if r["n_raters"] == 5),
        "n_items_with_4_raters": sum(1 for r in rows if r["n_raters"] == 4),
        "n_items_with_3_raters": sum(1 for r in rows if r["n_raters"] == 3),
        "n_items_with_2_raters": sum(1 for r in rows if r["n_raters"] == 2),
        "n_items_with_1_rater": sum(1 for r in rows if r["n_raters"] == 1),
    }
    return rows, meta


def load_target_tsv(path: Path) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gold = str(row.get("gold_file", "")).strip()
            cand = str(row.get("candidate_file", "")).strip()
            score_text = str(row.get("human_score_0_5", "")).strip()
            if not gold or not cand or not score_text:
                continue
            try:
                score_0_5 = float(score_text)
            except ValueError:
                continue
            item_key = f"{gold}::{cand}"
            out[item_key] = {
                "gold_file": gold,
                "candidate_file": cand,
                "item_key": item_key,
                "human_score": score_0_5 / 5.0,
            }
    return out


def aggregate_tasks(item_targets: Dict[str, dict]) -> Dict[str, dict]:
    by_task: Dict[str, List[float]] = defaultdict(list)
    for row in item_targets.values():
        by_task[row["gold_file"]].append(row["human_score"])
    return {
        task: {"task": task, "human_score": mean(scores), "n_items": len(scores)}
        for task, scores in by_task.items()
    }


def load_judge_scores(result_dirs: Iterable[Path]) -> Tuple[List[dict], Dict[str, Dict[str, float]]]:
    meta_by_judge: Dict[str, dict] = {}
    score_by_judge: Dict[str, Dict[str, float]] = defaultdict(dict)
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
                    "cert_index": float(row.get("cert_index") or "nan"),
                    "cert_index_v2": float(row.get("cert_index_v2") or "nan"),
                    "ethan_avg_human_spearman": float(row.get("human_spearman_r_avg") or "nan"),
                }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                judge_id = row["judge_id"]
                item_key = row["item_key"]
                if judge_id not in meta_by_judge or item_key in score_by_judge[judge_id]:
                    continue
                score_by_judge[judge_id][item_key] = float(row.get("score_mean") or "nan")
    return sorted(meta_by_judge.values(), key=lambda r: r["judge_id"]), score_by_judge


def evaluate_target(
    target_name: str,
    item_targets: Dict[str, dict],
    task_targets: Dict[str, dict],
    judges: List[dict],
    score_by_judge: Dict[str, Dict[str, float]],
) -> Tuple[List[dict], List[dict]]:
    judge_rows: List[dict] = []
    task_score_rows: List[dict] = []
    for judge in judges:
        pair_scores = score_by_judge.get(judge["judge_id"], {})
        common_items = sorted(set(pair_scores) & set(item_targets))
        item_x = [pair_scores[k] for k in common_items]
        item_y = [item_targets[k]["human_score"] for k in common_items]
        item_corr = safe_corr(item_x, item_y)

        by_task: Dict[str, List[float]] = defaultdict(list)
        for item_key, jscore in pair_scores.items():
            task = item_key.split("::", 1)[0]
            if task in task_targets:
                by_task[task].append(jscore)
        common_tasks = sorted(set(by_task) & set(task_targets))
        task_x = [mean(by_task[t]) for t in common_tasks]
        task_y = [task_targets[t]["human_score"] for t in common_tasks]
        task_corr = safe_corr(task_x, task_y)

        judge_rows.append(
            {
                **judge,
                "target_name": target_name,
                "n_pairs": len(common_items),
                "n_tasks": len(common_tasks),
                "pair_spearman_r": item_corr["spearman_r"],
                "pair_pearson_r": item_corr["pearson_r"],
                "task_spearman_r": task_corr["spearman_r"],
                "task_pearson_r": task_corr["pearson_r"],
            }
        )
        for task in common_tasks:
            task_score_rows.append(
                {
                    "target_name": target_name,
                    "judge_id": judge["judge_id"],
                    "task": task,
                    "judge_score": mean(by_task[task]),
                    "human_score": task_targets[task]["human_score"],
                    "n_items": task_targets[task]["n_items"],
                }
            )
    return judge_rows, task_score_rows


def meta_trends(judge_rows: List[dict], target_name: str) -> List[dict]:
    rows = [r for r in judge_rows if r["target_name"] == target_name]
    out = []
    for level, key in [("pair", "pair_spearman_r"), ("task", "task_spearman_r")]:
        for x_metric in ["cert_index", "cert_index_v2"]:
            corr = safe_corr([r[x_metric] for r in rows], [r[key] for r in rows])
            out.append(
                {
                    "target_name": target_name,
                    "level": level,
                    "x_metric": x_metric,
                    "n_judges": corr["n"],
                    "meta_spearman_r": corr["spearman_r"],
                    "meta_pearson_r": corr["pearson_r"],
                }
            )
    return out


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    out_dir: Path,
    super_meta: dict,
    ethan_super_overlap: dict,
    judge_rows: List[dict],
    meta_rows: List[dict],
) -> None:
    def top_llm(target: str, level: str, n: int = 8) -> List[dict]:
        key = "task_spearman_r" if level == "task" else "pair_spearman_r"
        rows = [r for r in judge_rows if r["target_name"] == target and r["kind"] == "llm" and math.isfinite(r[key])]
        rows.sort(key=lambda r: r[key], reverse=True)
        return rows[:n]

    eth_task_meta = next(r for r in meta_rows if r["target_name"] == "ethan_avg" and r["level"] == "task" and r["x_metric"] == "cert_index_v2")
    sup_task_meta = next(r for r in meta_rows if r["target_name"] == "super_human_pass3" and r["level"] == "task" and r["x_metric"] == "cert_index_v2")
    eth_best = top_llm("ethan_avg", "task", 1)[0]
    sup_best = top_llm("super_human_pass3", "task", 1)[0]

    lines = [
        "# EXP36 Report: Super-Human Pass3 (Five-Rater Mean)",
        "",
        "**TLDR:** We averaged participant1..participant5 into one label set (`super_human_pass3`) and re-ran the same pair/task judge-human analysis used for `ethan_avg`. The super-human target does **not** recover the old ~0.7 task-level correlations; best LLM task Spearman stays near **0.54**.",
        "",
        "## Super-Human Target Construction",
        f"- Participant files averaged: {super_meta['n_participant_files']}",
        f"- Items in super-human TSV: `{super_meta['n_items']}`",
        f"- Items with all 5 raters: `{super_meta['n_items_with_5_raters']}`",
        f"- Items with 4 raters: `{super_meta['n_items_with_4_raters']}`",
        f"- Output TSV: `experiments/04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv`",
        "",
        "## Is Super-Human Similar To Ethan?",
        f"- Overlap with `ethan_avg`: `{ethan_super_overlap['n_overlap']}` items",
        f"- Item-level Spearman(super_human, ethan_avg): `{ethan_super_overlap['item_spearman']:.3f}`",
        f"- Mean absolute score difference (0-5 scale): `{ethan_super_overlap['mean_abs_diff_0_5']:.3f}`",
        "",
        "If Brando's assumption held strongly, super-human should behave like ethan_avg in judge-human correlation. It does not.",
        "",
        "## Main Comparison (Same Analysis As Before)",
        "",
        "| Target | Meta task Spearman(cert_v2, human align) | Best LLM task Spearman | Best judge | n tasks |",
        "| --- | ---: | ---: | --- | ---: |",
        f"| `ethan_avg` | {eth_task_meta['meta_spearman_r']:.3f} | {eth_best['task_spearman_r']:.3f} | `{eth_best['judge_id']}` | {eth_best['n_tasks']} |",
        f"| `super_human_pass3` | {sup_task_meta['meta_spearman_r']:.3f} | {sup_best['task_spearman_r']:.3f} | `{sup_best['judge_id']}` | {sup_best['n_tasks']} |",
        "",
        "## Top LLM Judges On Super-Human (Task Level)",
        "",
        "| Judge | cert_v2 | Task Spearman | Pair Spearman | n tasks |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in top_llm("super_human_pass3", "task", 10):
        lines.append(
            f"| {row['judge_id']} | {row['cert_index_v2']:.3f} | {row['task_spearman_r']:.3f} | {row['pair_spearman_r']:.3f} | {row['n_tasks']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "- Super-human pass3 is the five-participant mean treated as one human (`n≈78` items, `n≈20-24` tasks on the cached judge panel).",
        "- Task aggregation still helps relative to pair-level, but much less than on `ethan_avg`.",
        "- Good judges validated on Ethan (e.g. Opus/Codex prompts) can be **negative** against the five-rater mean.",
        "- The old ~0.7 numbers come from `ethan_avg` + task aggregation, not from averaging all annotators.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    super_rows, super_meta = build_super_human_tsv(args.human_dir, args.super_tsv, args.min_raters)
    super_targets = {f"{r['gold_file']}::{r['candidate_file']}": r for r in super_rows}
    super_item_targets = {
        k: {
            "gold_file": v["gold_file"],
            "candidate_file": v["candidate_file"],
            "item_key": k,
            "human_score": v["human_score_0_1"],
        }
        for k, v in super_targets.items()
    }
    super_task_targets = aggregate_tasks(super_item_targets)

    ethan_item_targets = load_target_tsv(args.ethan_tsv)
    ethan_task_targets = aggregate_tasks(ethan_item_targets)

    overlap_keys = sorted(set(super_item_targets) & set(ethan_item_targets))
    overlap_x = [super_item_targets[k]["human_score"] for k in overlap_keys]
    overlap_y = [ethan_item_targets[k]["human_score"] for k in overlap_keys]
    overlap_corr = safe_corr(overlap_x, overlap_y)
    ethan_super_overlap = {
        "n_overlap": len(overlap_keys),
        "item_spearman": overlap_corr["spearman_r"],
        "mean_abs_diff_0_5": mean([abs(a - b) * 5.0 for a, b in zip(overlap_x, overlap_y)]),
    }

    judges, score_by_judge = load_judge_scores(args.result_dirs)
    judge_rows: List[dict] = []
    task_score_rows: List[dict] = []
    for target_name, item_t, task_t in [
        ("super_human_pass3", super_item_targets, super_task_targets),
        ("ethan_avg", ethan_item_targets, ethan_task_targets),
    ]:
        rows, task_rows = evaluate_target(target_name, item_t, task_t, judges, score_by_judge)
        judge_rows.extend(rows)
        task_score_rows.extend(task_rows)

    meta_rows: List[dict] = []
    for target_name in ["super_human_pass3", "ethan_avg"]:
        meta_rows.extend(meta_trends(judge_rows, target_name))

    summary = {
        "experiment": "exp36_super_human_pass3",
        "super_tsv": str(args.super_tsv.relative_to(REPO_ROOT)),
        "ethan_tsv": str(args.ethan_tsv.relative_to(REPO_ROOT)),
        "super_meta": super_meta,
        "ethan_super_overlap": ethan_super_overlap,
    }

    write_csv(args.out_dir / "super_human_item_targets.csv", super_rows)
    write_csv(args.out_dir / "judge_target_metrics.csv", judge_rows)
    write_csv(args.out_dir / "meta_trends.csv", meta_rows)
    write_csv(args.out_dir / "task_level_scores.csv", task_score_rows)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(args.out_dir, super_meta, ethan_super_overlap, judge_rows, meta_rows)

    sup_best = max(
        (r for r in judge_rows if r["target_name"] == "super_human_pass3" and r["kind"] == "llm" and math.isfinite(r["task_spearman_r"])),
        key=lambda r: r["task_spearman_r"],
    )
    eth_best = max(
        (r for r in judge_rows if r["target_name"] == "ethan_avg" and r["kind"] == "llm" and math.isfinite(r["task_spearman_r"])),
        key=lambda r: r["task_spearman_r"],
    )
    print(f"Wrote {args.out_dir}")
    print(f"super_human_pass3: n_items={super_meta['n_items']} best_task={sup_best['task_spearman_r']:.3f} ({sup_best['judge_id']})")
    print(f"ethan_avg: best_task={eth_best['task_spearman_r']:.3f} ({eth_best['judge_id']})")
    print(f"super vs ethan item Spearman={ethan_super_overlap['item_spearman']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
