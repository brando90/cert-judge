#!/usr/bin/env python3
"""EXP35: sweep human-target aggregation strategies for judge-human correlation."""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp35_aggregation_sweep"
DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]
PARTICIPANT_PREFIX = "participant"
CALIBRATION_FILES = {"lenient_set_data.tsv", "expert_harsh_set_data.tsv"}
FLOAT_TIE_DIGITS = 12


def mean(values: Sequence[float]) -> float:
    vals = [v for v in values if math.isfinite(v)]
    return round(math.fsum(vals) / len(vals), FLOAT_TIE_DIGITS) if vals else float("nan")


def median(values: Sequence[float]) -> float:
    vals = sorted(v for v in values if math.isfinite(v))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2.0


def std(values: Sequence[float]) -> float:
    vals = [v for v in values if math.isfinite(v)]
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


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


def safe_corr(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, int]:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return float("nan"), len(pairs)
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    if len(set(x)) < 2 or len(set(y)) < 2:
        return float("nan"), len(pairs)
    return spearman(x, y), len(pairs)


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


def load_labels(human_dir: Path, include_old_prompt: bool, rater_filter: Callable[[str], bool]) -> List[dict]:
    files = sorted(human_dir.glob("*.tsv"))
    if include_old_prompt:
        files += sorted((human_dir / "old_prompt").glob("*.tsv"))
    rows: List[dict] = []
    for path in files:
        if not rater_filter(path.name):
            continue
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
                rows.append(
                    {
                        "rater": path.stem,
                        "gold_file": gold,
                        "candidate_file": cand,
                        "item_key": f"{gold}::{cand}",
                        "score_0_1": score / 5.0,
                    }
                )
    return rows


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
                    "cert_index_v2": float(row.get("cert_index_v2") or "nan"),
                }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                jid = row["judge_id"]
                item_key = row["item_key"]
                if jid not in meta or item_key in scores[jid]:
                    continue
                scores[jid][item_key] = float(row.get("score_mean") or "nan")
    return meta, scores


def zscore_by_rater(labels: List[dict]) -> List[dict]:
    by_rater: Dict[str, List[float]] = defaultdict(list)
    for row in labels:
        by_rater[row["rater"]].append(row["score_0_1"])
    stats = {r: (mean(vals), std(vals)) for r, vals in by_rater.items()}
    out = []
    for row in labels:
        m, s = stats[row["rater"]]
        z = (row["score_0_1"] - m) / s if s > 1e-9 else 0.0
        out.append({**row, "score_0_1": z})
    return out


def trimmed_mean(values: Sequence[float], trim: int = 1) -> float:
    vals = sorted(v for v in values if math.isfinite(v))
    if len(vals) <= 2 * trim:
        return mean(vals)
    return mean(vals[trim:-trim])


def build_targets(labels: List[dict], item_agg: Callable[[List[float]], float], task_agg: Callable[[List[float]], float], min_raters: int = 1, max_item_std: float | None = None) -> Tuple[Dict[str, float], Dict[str, float]]:
    by_item: Dict[str, List[float]] = defaultdict(list)
    item_task: Dict[str, str] = {}
    for row in labels:
        by_item[row["item_key"]].append(row["score_0_1"])
        item_task[row["item_key"]] = row["gold_file"]
    item_targets: Dict[str, float] = {}
    for item_key, vals in by_item.items():
        raters = len(vals)
        if raters < min_raters:
            continue
        if max_item_std is not None and std(vals) > max_item_std:
            continue
        item_targets[item_key] = item_agg(vals)
    by_task: Dict[str, List[float]] = defaultdict(list)
    for item_key, score in item_targets.items():
        by_task[item_task[item_key]].append(score)
    task_targets = {task: task_agg(vals) for task, vals in by_task.items()}
    return item_targets, task_targets


def eval_strategy(name: str, item_targets: Dict[str, float], task_targets: Dict[str, float], judge_scores: Dict[str, Dict[str, float]], judge_meta: Dict[str, dict]) -> List[dict]:
    rows: List[dict] = []
    for jid, pair_scores in judge_scores.items():
        common_items = sorted(set(pair_scores) & set(item_targets))
        if len(common_items) >= 3:
            item_x = [pair_scores[k] for k in common_items]
            item_y = [item_targets[k] for k in common_items]
            item_rho, item_n = safe_corr(item_x, item_y)
        else:
            item_rho, item_n = float("nan"), len(common_items)
        by_task: Dict[str, List[float]] = defaultdict(list)
        for item_key, jscore in pair_scores.items():
            task = item_key.split("::", 1)[0]
            if task in task_targets:
                by_task[task].append(jscore)
        common_tasks = sorted(set(by_task) & set(task_targets))
        if len(common_tasks) >= 3:
            task_x = [mean(by_task[t]) for t in common_tasks]
            task_y = [task_targets[t] for t in common_tasks]
            task_rho, task_n = safe_corr(task_x, task_y)
        else:
            task_rho, task_n = float("nan"), len(common_tasks)
        rows.append(
            {
                "strategy": name,
                "judge_id": jid,
                "kind": judge_meta[jid]["kind"],
                "cert_index_v2": judge_meta[jid]["cert_index_v2"],
                "item_spearman": item_rho,
                "item_n": item_n,
                "task_spearman": task_rho,
                "task_n": task_n,
            }
        )
    return rows


def main() -> int:
    out_dir = DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    judge_meta, judge_scores = load_judge_scores(DEFAULT_RESULT_DIRS)

    label_sets = {
        "all_files": lambda name: True,
        "participants_only": lambda name: name.startswith(PARTICIPANT_PREFIX),
        "no_calibration": lambda name: name not in CALIBRATION_FILES,
        "participants_no_calibration": lambda name: name.startswith(PARTICIPANT_PREFIX),
        "participant1_only": lambda name: name.startswith("participant1_data"),
    }

    agg_specs: List[Tuple[str, Callable[[List[dict]], List[dict]], Callable[[List[float]], float], Callable[[List[float]], float], dict]] = []
    for label_name, rater_filter in label_sets.items():
        base = lambda labels: labels  # noqa: E731
        agg_specs.append((f"{label_name}|item_mean_task_mean", base, mean, mean, {"min_raters": 1}))
        agg_specs.append((f"{label_name}|item_median_task_median", base, median, median, {"min_raters": 1}))
        agg_specs.append((f"{label_name}|item_trim1_task_mean", base, lambda v: trimmed_mean(v, 1), mean, {"min_raters": 3}))
        agg_specs.append((f"{label_name}|zscore_item_mean_task_mean", zscore_by_rater, mean, mean, {"min_raters": 1}))
        agg_specs.append((f"{label_name}|zscore_item_median_task_median", zscore_by_rater, median, median, {"min_raters": 1}))
        for min_r in (3, 5, 6):
            agg_specs.append((f"{label_name}|min_raters_{min_r}_mean", base, mean, mean, {"min_raters": min_r}))
        for max_std in (0.15, 0.10, 0.05):
            agg_specs.append((f"{label_name}|lowvar_{max_std}_mean", base, mean, mean, {"min_raters": 2, "max_item_std": max_std}))

    all_rows: List[dict] = []
    strategy_summary: List[dict] = []
    for label_name, rater_filter in label_sets.items():
        for include_old in (False, True):
            if label_name == "participant1_only" and include_old:
                suffix = "_with_old_prompt"
            elif include_old:
                suffix = "_with_old_prompt"
            else:
                suffix = ""
            labels = load_labels(DEFAULT_HUMAN_DIR, include_old_prompt=include_old, rater_filter=rater_filter)
            if not labels:
                continue
            for spec_name, pre, item_agg, task_agg, kwargs in agg_specs:
                if not spec_name.startswith(label_name + "|"):
                    continue
                transformed = pre(labels)
                item_targets, task_targets = build_targets(transformed, item_agg, task_agg, **kwargs)
                strat_name = spec_name + suffix
                rows = eval_strategy(strat_name, item_targets, task_targets, judge_scores, judge_meta)
                all_rows.extend(rows)
                good = [r for r in rows if r["kind"] == "llm" and math.isfinite(r["task_spearman"])]
                best = max(good, key=lambda r: r["task_spearman"], default=None)
                meta_rows = [r for r in rows if math.isfinite(r["task_spearman"])]
                meta = safe_corr([r["cert_index_v2"] for r in meta_rows], [r["task_spearman"] for r in meta_rows])[0]
                strategy_summary.append(
                    {
                        "strategy": strat_name,
                        "n_labels": len(labels),
                        "n_items": len(item_targets),
                        "n_tasks": len(task_targets),
                        "best_task_spearman": best["task_spearman"] if best else float("nan"),
                        "best_judge": best["judge_id"] if best else "",
                        "best_judge_kind": best["kind"] if best else "",
                        "meta_task_spearman_cert_v2": meta,
                        "n_llm_judges": len(good),
                    }
                )

    strategy_summary.sort(key=lambda r: (-999 if not math.isfinite(r["best_task_spearman"]) else -r["best_task_spearman"], r["strategy"]))
    all_rows.sort(key=lambda r: (r["strategy"], -999 if not math.isfinite(r["task_spearman"]) else -r["task_spearman"]))

    with (out_dir / "strategy_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(strategy_summary[0].keys()))
        w.writeheader()
        w.writerows(strategy_summary)
    with (out_dir / "judge_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    top = [s for s in strategy_summary if s["best_judge_kind"] == "llm"][:15]
    lines = [
        "# EXP35: Aggregation Strategy Sweep",
        "",
        "Goal: find human-target aggregations that raise judge-human task Spearman toward 0.7+.",
        "",
        "## Top strategies (LLM judges only, by best task Spearman)",
        "",
        "| Strategy | Best task rho | Best judge | Meta rho (cert_v2) | n tasks |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for s in top:
        lines.append(
            f"| `{s['strategy']}` | {s['best_task_spearman']:.3f} | `{s['best_judge']}` | {s['meta_task_spearman_cert_v2']:.3f} | {s['n_tasks']} |"
        )
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps({"top5": top[:5]}, indent=2), encoding="utf-8")
    print(f"Wrote {out_dir}")
    for s in top[:8]:
        print(f"  {s['best_task_spearman']:.3f}  {s['strategy']}  ({s['best_judge']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
