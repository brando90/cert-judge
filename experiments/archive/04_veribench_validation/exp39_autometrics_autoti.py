#!/usr/bin/env python3
"""
EXP39: AutoMetrics-inspired learned AutoTI over the five-human target.

Treat each prompt/evaluator score as a candidate metric, then learn a small
ridge/PLS-style composition per model family. Reports same-item upper bounds
and leave-one-task-out estimates so high correlations are not confused with
held-out generalization.
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
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp39_autometrics_autoti"
DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]
FLOAT_TIE_DIGITS = 12
RIDGE_ALPHAS = [0.0, 0.01, 0.1, 1.0, 10.0, 100.0]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP39: AutoMetrics-inspired AutoTI for five human labels")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument("--target", choices=["mean", "median", "zscore_mean"], default="mean")
    p.add_argument("--min-raters", type=int, default=1)
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
    return num / (den_x * den_y) if den_x > 0 and den_y > 0 else float("nan")


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def safe_spearman(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, int]:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(float(x)) and math.isfinite(float(y))]
    if len(pairs) < 3:
        return float("nan"), len(pairs)
    x = [float(p[0]) for p in pairs]
    y = [float(p[1]) for p in pairs]
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


def load_participant_labels(human_dir: Path, target: str, min_raters: int) -> Dict[str, dict]:
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
                if gold and cand:
                    by_item[f"{gold}::{cand}"][rater] = score

    rater_stats = {}
    if target == "zscore_mean":
        for rater in raters:
            vals = [rmap[rater] for rmap in by_item.values() if rater in rmap]
            rater_stats[rater] = (mean(vals), std(vals))

    out: Dict[str, dict] = {}
    for item_key, rmap in sorted(by_item.items()):
        vals = [rmap[r] for r in raters if r in rmap]
        if len(vals) < min_raters:
            continue
        if target == "median":
            score = median(vals)
        elif target == "zscore_mean":
            zs = []
            for r in raters:
                if r not in rmap:
                    continue
                m, s = rater_stats[r]
                zs.append((rmap[r] - m) / s if s > 1e-9 else 0.0)
            score = mean(zs)
        else:
            score = mean(vals)
        gold, cand = item_key.split("::", 1)
        out[item_key] = {
            "item_key": item_key,
            "task": gold,
            "candidate_file": cand,
            "human_score": score,
            "n_raters": len(vals),
        }
    return out


def load_metric_bank(result_dirs: Iterable[Path]) -> Tuple[Dict[str, dict], Dict[str, Dict[str, float]]]:
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
                if row.get("kind") not in {"llm", "llm_bad"} or jid in meta:
                    continue
                meta[jid] = {
                    "judge_id": jid,
                    "kind": row.get("kind", ""),
                    "model": row.get("model", jid.split("|", 1)[0]),
                    "prompt_name": row.get("prompt_name", jid.split("|", 1)[-1]),
                    "cert_index_v2": float(row.get("cert_index_v2") or "nan"),
                    "source_dir": str(result_dir.relative_to(REPO_ROOT)),
                }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                jid = row.get("judge_id", "")
                if jid not in meta:
                    continue
                scores[jid][row["item_key"]] = float(row.get("score_mean") or "nan")
    return meta, scores


def zscore_train_test(x_train: List[List[float]], x_test: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
    n_features = len(x_train[0])
    mus = [mean([row[j] for row in x_train]) for j in range(n_features)]
    sigmas = []
    for j in range(n_features):
        vals = [row[j] for row in x_train]
        s = std(vals)
        sigmas.append(s if s > 1e-9 else 1.0)
    return (
        [[(row[j] - mus[j]) / sigmas[j] for j in range(n_features)] for row in x_train],
        [[(row[j] - mus[j]) / sigmas[j] for j in range(n_features)] for row in x_test],
    )


def solve_linear_system(a: List[List[float]], b: List[float]) -> List[float]:
    n = len(b)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            aug[pivot][col] = 1e-12
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [v / div for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor == 0.0:
                continue
            aug[r] = [v - factor * pv for v, pv in zip(aug[r], aug[col])]
    return [aug[i][-1] for i in range(n)]


def fit_ridge_predict(x_train: List[List[float]], y_train: List[float], x_pred: List[List[float]], alpha: float) -> Tuple[List[float], List[float]]:
    xz, xp = zscore_train_test(x_train, x_pred)
    design = [[1.0] + row for row in xz]
    n_coef = len(design[0])
    xtx = [[0.0 for _ in range(n_coef)] for _ in range(n_coef)]
    xty = [0.0 for _ in range(n_coef)]
    for row, y in zip(design, y_train):
        for i in range(n_coef):
            xty[i] += row[i] * y
            for j in range(n_coef):
                xtx[i][j] += row[i] * row[j]
    for i in range(1, n_coef):
        xtx[i][i] += alpha
    beta = solve_linear_system(xtx, xty)
    pred_design = [[1.0] + row for row in xp]
    preds = [sum(b * v for b, v in zip(beta, row)) for row in pred_design]
    return preds, beta


def subset_rows(x: List[List[float]], idxs: Sequence[int]) -> List[List[float]]:
    return [x[i] for i in idxs]


def subset_vals(x: Sequence[float], idxs: Sequence[int]) -> List[float]:
    return [float(x[i]) for i in idxs]


def choose_alpha_by_loocv(x: List[List[float]], y: List[float]) -> float:
    best_alpha = RIDGE_ALPHAS[0]
    best_rho = -float("inf")
    for alpha in RIDGE_ALPHAS:
        pred = [0.0 for _ in y]
        for i in range(len(y)):
            train = [j for j in range(len(y)) if j != i]
            p, _ = fit_ridge_predict(subset_rows(x, train), subset_vals(y, train), [x[i]], alpha)
            pred[i] = p[0]
        rho, _ = safe_spearman(pred, y)
        score = rho if math.isfinite(rho) else -float("inf")
        if score > best_rho:
            best_rho = score
            best_alpha = alpha
    return best_alpha


def leave_one_task_out(x: List[List[float]], y: List[float], tasks: Sequence[str], alpha: float) -> List[float]:
    pred = [float("nan") for _ in y]
    for task in sorted(set(tasks)):
        test_idx = [i for i, t in enumerate(tasks) if t == task]
        train_idx = [i for i, t in enumerate(tasks) if t != task]
        if len(train_idx) < 3 or len(test_idx) == 0:
            continue
        p, _ = fit_ridge_predict(subset_rows(x, train_idx), subset_vals(y, train_idx), subset_rows(x, test_idx), alpha)
        for idx, val in zip(test_idx, p):
            pred[idx] = val
    return pred


def task_level_corr(item_keys: Sequence[str], pred: Sequence[float], y: Sequence[float]) -> Tuple[float, int]:
    pred_b: Dict[str, List[float]] = defaultdict(list)
    y_b: Dict[str, List[float]] = defaultdict(list)
    for k, p, yy in zip(item_keys, pred, y):
        task = k.split("::", 1)[0]
        pred_b[task].append(float(p))
        y_b[task].append(float(yy))
    tasks = sorted(set(pred_b) & set(y_b))
    return safe_spearman([mean(pred_b[t]) for t in tasks], [mean(y_b[t]) for t in tasks])


def analyze_model(
    model: str,
    judge_ids: Sequence[str],
    human: Dict[str, dict],
    scores: Dict[str, Dict[str, float]],
    meta: Dict[str, dict],
) -> Tuple[List[dict], List[dict]]:
    item_keys = sorted(set(human).intersection(*(set(scores[j]) for j in judge_ids)))
    if len(item_keys) < 5 or len(judge_ids) < 2:
        return [], []
    x = [[scores[j][k] for j in judge_ids] for k in item_keys]
    y = [human[k]["human_score"] for k in item_keys]
    tasks = [human[k]["task"] for k in item_keys]

    rows: List[dict] = []
    pred_rows: List[dict] = []
    for jid in judge_ids:
        raw = [scores[jid][k] for k in item_keys]
        rho, n = safe_spearman(raw, y)
        trho, tn = task_level_corr(item_keys, raw, y)
        rows.append(
            {
                "model": model,
                "method": "single_metric_raw",
                "metric_id": jid,
                "n_features": 1,
                "n_items": n,
                "n_tasks": tn,
                "alpha": "",
                "item_spearman_r": rho,
                "task_spearman_r": trho,
                "cert_index_v2": meta[jid]["cert_index_v2"],
                "feature_weights": "",
            }
        )

    alpha = choose_alpha_by_loocv(x, y)
    pred_in, beta = fit_ridge_predict(x, y, x, alpha)
    pred_loto = leave_one_task_out(x, y, tasks, alpha)
    for method, pred in [("autoti_ridge_same_items", pred_in), ("autoti_ridge_leave_one_task_out", pred_loto)]:
        rho, n = safe_spearman(pred, y)
        trho, tn = task_level_corr(item_keys, pred, y)
        weights = ";".join(f"{jid}={w:.6g}" for jid, w in zip(judge_ids, beta[1:]))
        rows.append(
            {
                "model": model,
                "method": method,
                "metric_id": f"{model}|AutoTI_RIDGE",
                "n_features": len(judge_ids),
                "n_items": n,
                "n_tasks": tn,
                "alpha": alpha,
                "item_spearman_r": rho,
                "task_spearman_r": trho,
                "cert_index_v2": "",
                "feature_weights": weights,
            }
        )
        for k, p, yy in zip(item_keys, pred, y):
            pred_rows.append(
                {
                    "model": model,
                    "method": method,
                    "item_key": k,
                    "task": human[k]["task"],
                    "human_score": yy,
                    "predicted_score": p,
                    "n_features": len(judge_ids),
                    "alpha": alpha,
                }
            )
    return rows, pred_rows


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(out_dir: Path, rows: List[dict], target: str, min_raters: int) -> None:
    same = sorted([r for r in rows if r["method"] == "autoti_ridge_same_items"], key=lambda r: r["item_spearman_r"], reverse=True)
    loto = sorted([r for r in rows if r["method"] == "autoti_ridge_leave_one_task_out"], key=lambda r: r["item_spearman_r"], reverse=True)
    raw = sorted([r for r in rows if r["method"] == "single_metric_raw"], key=lambda r: r["item_spearman_r"], reverse=True)
    lines = [
        "# EXP39: AutoMetrics-Inspired AutoTI",
        "",
        f"**TLDR:** Learns a ridge composition over prompt-level judge scores against the five-human `{target}` target. Same-item AutoTI tests the achievable upper bound; leave-one-task-out tests whether it generalizes to unseen tasks.",
        "",
        f"- Human target: `{target}`, min raters per item: `{min_raters}`.",
        f"- Best raw single metric: `{raw[0]['item_spearman_r']:.3f}` item Spearman for `{raw[0]['metric_id']}`." if raw else "- No raw single metrics.",
        f"- Best same-item AutoTI: `{same[0]['item_spearman_r']:.3f}` item Spearman for `{same[0]['model']}`." if same else "- No same-item AutoTI rows.",
        f"- Best leave-one-task-out AutoTI: `{loto[0]['item_spearman_r']:.3f}` item Spearman for `{loto[0]['model']}`." if loto else "- No leave-one-task-out rows.",
        "",
        "## Learned AutoTI By Model",
        "",
        "| Model | Method | Item rho | Task rho | n items | n tasks | alpha | n features |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted([r for r in rows if r["method"].startswith("autoti")], key=lambda r: (r["model"], r["method"])):
        lines.append(
            f"| {row['model']} | {row['method']} | {row['item_spearman_r']:.3f} | {row['task_spearman_r']:.3f} | {row['n_items']} | {row['n_tasks']} | {row['alpha']} | {row['n_features']} |"
        )
    lines += [
        "",
        "## Best Raw Single Metrics",
        "",
        "| Metric | Item rho | Task rho | n items | cert_v2 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in raw[:12]:
        lines.append(
            f"| {row['metric_id']} | {row['item_spearman_r']:.3f} | {row['task_spearman_r']:.3f} | {row['n_items']} | {row['cert_index_v2']:.3f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "- Same-item learned AutoTI is an AutoMetrics-style calibration upper bound, not a held-out validity claim.",
        "- Leave-one-task-out is the safer number for paper claims. If it does not clear 0.7, report the high same-item result as calibration capacity only.",
        "- Compare against EXP38 per-task isotonic: that method can exceed 0.7 for LeanStral, but it also boosts random/edit-distance baselines, so it should be labeled as an oracle diagnostic.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    human = load_participant_labels(args.human_dir, args.target, args.min_raters)
    meta, scores = load_metric_bank(args.result_dirs)
    by_model: Dict[str, List[str]] = defaultdict(list)
    for jid, m in meta.items():
        by_model[m["model"]].append(jid)

    rows: List[dict] = []
    pred_rows: List[dict] = []
    for model, judge_ids in sorted(by_model.items()):
        model_rows, model_preds = analyze_model(model, sorted(judge_ids), human, scores, meta)
        rows.extend(model_rows)
        pred_rows.extend(model_preds)

    rows.sort(key=lambda r: (r["model"], r["method"], str(r["metric_id"])))
    write_csv(args.out_dir / "autoti_metrics.csv", rows)
    write_csv(args.out_dir / "autoti_predictions.csv", pred_rows)
    summary = {
        "target": args.target,
        "min_raters": args.min_raters,
        "n_human_items": len(human),
        "n_metric_rows": len(rows),
        "best_same_item": max((r for r in rows if r["method"] == "autoti_ridge_same_items"), key=lambda r: r["item_spearman_r"], default=None),
        "best_leave_one_task_out": max(
            (r for r in rows if r["method"] == "autoti_ridge_leave_one_task_out"),
            key=lambda r: r["item_spearman_r"],
            default=None,
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    write_report(args.out_dir, rows, args.target, args.min_raters)
    print(f"Wrote {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
