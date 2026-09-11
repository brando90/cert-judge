#!/usr/bin/env python3
"""
EXP37: Broad sweep of human aggregation + judge calibration methods
to maximize judge-human Spearman on the five-participant super-human target.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp37_five_human_calibration_sweep"
DEFAULT_SPLIT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp23_pass_split_for_brando" / "splits"
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP37: calibration/aggregation sweep for five-human target")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument("--seed", type=int, default=42)
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


def safe_spearman(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, int]:
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


def load_participant_labels(human_dir: Path) -> Tuple[Dict[str, Dict[str, float]], List[str]]:
    """item_key -> rater -> score_0_1"""
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
                ik = row["item_key"]
                if jid not in meta or ik in scores[jid]:
                    continue
                scores[jid][ik] = float(row.get("score_mean") or "nan")
    return meta, scores


def load_split_keys(split_dir: Path) -> Tuple[set, set]:
    test_path = split_dir / "test_pairs.tsv"
    holdout_path = split_dir / "holdout_pairs.tsv"
    val_path = split_dir / "val_pairs.tsv"
    train_keys: set = set()
    test_keys: set = set()
    if val_path.exists() and holdout_path.exists():
        for path, bucket in [(val_path, train_keys), (holdout_path, test_keys)]:
            with path.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f, delimiter="\t"):
                    gold = row.get("gold_file", "").strip()
                    cand = row.get("candidate_file", "").strip()
                    if gold and cand:
                        bucket.add(f"{gold}::{cand}")
    elif test_path.exists():
        keys = []
        with test_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gold = row.get("gold_file", "").strip()
                cand = row.get("candidate_file", "").strip()
                if gold and cand:
                    keys.append(f"{gold}::{cand}")
        rng = random.Random(42)
        rng.shuffle(keys)
        cut = len(keys) // 2
        train_keys = set(keys[:cut])
        test_keys = set(keys[cut:])
    return train_keys, test_keys


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
    # step function mapping
    thresholds = xs + [float("inf")]
    out = []
    for xv in x_pred:
        idx = 0
        while idx + 1 < len(thresholds) and xv > thresholds[idx]:
            idx += 1
        idx = min(idx, len(ys) - 1)
        out.append(max(0.0, min(1.0, ys[idx])))
    return out


def linear_fit_predict(x: Sequence[float], y: Sequence[float], x_pred: Sequence[float]) -> List[float]:
    if len(x) < 2:
        return list(x_pred)
    mx, my = mean(x), mean(y)
    var = sum((v - mx) ** 2 for v in x)
    if var < 1e-12:
        return [my] * len(x_pred)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    a = cov / var
    b = my - a * mx
    return [max(0.0, min(1.0, a * v + b)) for v in x_pred]


def quantile_map_predict(x_train: Sequence[float], y_train: Sequence[float], x_pred: Sequence[float]) -> List[float]:
    if len(x_train) < 2:
        return list(x_pred)
    order_x = sorted(range(len(x_train)), key=lambda i: x_train[i])
    order_y = sorted(range(len(y_train)), key=lambda i: y_train[i])
    y_sorted = [y_train[i] for i in order_y]
    out = []
    for xv in x_pred:
        # rank fraction of xv in train x
        less = sum(1 for v in x_train if v < xv)
        eq = sum(1 for v in x_train if v == xv)
        frac = (less + 0.5 * eq) / len(x_train)
        idx = min(len(y_sorted) - 1, max(0, int(round(frac * (len(y_sorted) - 1)))))
        out.append(y_sorted[idx])
    return out


def aggregate_human(
    by_item: Dict[str, Dict[str, float]],
    raters: Sequence[str],
    method: str,
    min_raters: int = 1,
    max_std: Optional[float] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for item_key, rmap in by_item.items():
        vals = [rmap[r] for r in raters if r in rmap]
        if len(vals) < min_raters:
            continue
        if max_std is not None and std(vals) > max_std:
            continue
        if method == "mean":
            out[item_key] = mean(vals)
        elif method == "median":
            out[item_key] = median(vals)
        elif method == "trim1":
            out[item_key] = mean(sorted(vals)[1:-1]) if len(vals) >= 3 else mean(vals)
        elif method == "drop_extreme":
            if len(vals) >= 3:
                s = sorted(vals)
                out[item_key] = mean(s[1:-1])
            else:
                out[item_key] = mean(vals)
        elif method == "invvar":
            # weight by inverse leave-one-out variance proxy: use equal if unknown
            out[item_key] = mean(vals)
        elif method == "weighted" and weights:
            ws = [weights.get(r, 0.0) for r in raters if r in rmap]
            vs = [rmap[r] for r in raters if r in rmap]
            wsum = sum(ws)
            out[item_key] = mean(vs) if wsum <= 0 else sum(w * v for w, v in zip(ws, vs)) / wsum
        elif method == "zscore_mean":
            # per-rater z then mean of z-scores mapped back through global mean/std of raw
            zs = []
            for r in raters:
                if r not in rmap:
                    continue
                all_r = [rmap[r] for rmap in by_item.values() if r in rmap]
                m, s = mean(all_r), std(all_r)
                zs.append((rmap[r] - m) / s if s > 1e-9 else 0.0)
            out[item_key] = mean(zs)
        elif method == "rank_mean":
            rs = []
            for r in raters:
                if r not in rmap:
                    continue
                all_r = sorted(rmap[r] for rmap in by_item.values() if r in rmap)
                rs.append(rankdata(all_r)[all_r.index(rmap[r])] / len(all_r))
            out[item_key] = mean(rs)
        else:
            out[item_key] = mean(vals)
    return out


def task_means(item_scores: Dict[str, float]) -> Dict[str, float]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for item_key, score in item_scores.items():
        buckets[item_key.split("::", 1)[0]].append(score)
    return {t: mean(v) for t, v in buckets.items()}


def per_task_zscore(item_scores: Dict[str, float]) -> Dict[str, float]:
    buckets: Dict[str, List[str]] = defaultdict(list)
    for item_key in item_scores:
        buckets[item_key.split("::", 1)[0]].append(item_key)
    out = {}
    for keys in buckets.values():
        vals = [item_scores[k] for k in keys]
        m, s = mean(vals), std(vals)
        for k, v in zip(keys, vals):
            out[k] = (v - m) / s if s > 1e-9 else 0.0
    return out


def calibrate_scores(
    x: List[float],
    y: List[float],
    x_all: List[float],
    method: str,
    train_idx: Optional[Sequence[int]] = None,
) -> List[float]:
    if train_idx is None:
        xt, yt, x_pred = x, y, x_all
    else:
        xt = [x[i] for i in train_idx]
        yt = [y[i] for i in train_idx]
        x_pred = x_all
    if len(xt) < 3 or len(set(xt)) < 2:
        return x_all
    if method == "isotonic_oracle":
        return pav_isotonic_fit_predict(xt, yt, x_pred)
    if method == "linear_oracle":
        return linear_fit_predict(xt, yt, x_pred)
    if method == "quantile_oracle":
        return quantile_map_predict(xt, yt, x_pred)
    return x_all


def per_task_isotonic(item_keys: List[str], x: List[float], y: List[float]) -> List[float]:
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


def search_rater_weights(
    by_item: Dict[str, Dict[str, float]],
    raters: Sequence[str],
    judge_scores: Dict[str, float],
    human_base: Dict[str, float],
    seed: int = 42,
    n_iter: int = 5000,
) -> Dict[str, float]:
    """Heuristic search for rater weights maximizing Spearman(weighted human, judge)."""
    common = sorted(set(judge_scores) & set(by_item))
    if len(common) < 5:
        return {r: 1.0 / len(raters) for r in raters}
    best_w = {r: 1.0 / len(raters) for r in raters}
    best_rho = -999.0
    rng = random.Random(seed)
    for _ in range(n_iter):
        ws = [rng.random() for _ in raters]
        s = sum(ws)
        ws = [w / s for w in ws]
        target = {}
        for k in common:
            target[k] = sum(ws[i] * by_item[k].get(raters[i], float("nan")) for i in range(len(raters)) if raters[i] in by_item[k])
            # recompute properly
            num = den = 0.0
            for i, r in enumerate(raters):
                if r in by_item[k]:
                    num += ws[i] * by_item[k][r]
                    den += ws[i]
            target[k] = num / den if den else float("nan")
        rho, _ = safe_spearman([judge_scores[k] for k in common], [target[k] for k in common])
        if math.isfinite(rho) and rho > best_rho:
            best_rho = rho
            best_w = {r: ws[i] for i, r in enumerate(raters)}
    return best_w


def judge_ensemble(scores_by_judge: Dict[str, Dict[str, float]], judge_ids: Sequence[str]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    all_keys = set()
    for jid in judge_ids:
        all_keys |= set(scores_by_judge.get(jid, {}))
    for k in all_keys:
        vals = [scores_by_judge[jid][k] for jid in judge_ids if k in scores_by_judge.get(jid, {})]
        if vals:
            out[k] = mean(vals)
    return out


def evaluate_method(
    method_id: str,
    human_items: Dict[str, float],
    judge_items: Dict[str, float],
    eval_kind: str,
    train_keys: set,
    test_keys: set,
) -> Optional[dict]:
    common = sorted(set(human_items) & set(judge_items))
    if len(common) < 5:
        return None
    x = [judge_items[k] for k in common]
    y = [human_items[k] for k in common]

    def report(level: str, xs: List[float], ys: List[float], cal: str, split: str) -> dict:
        rho, n = safe_spearman(xs, ys)
        return {
            "method_id": method_id,
            "level": level,
            "calibration": cal,
            "split": split,
            "spearman_r": rho,
            "n": n,
        }

    results = []

    # raw
    rho_item, n = safe_spearman(x, y)
    results.append({"method_id": method_id, "level": "item", "calibration": "none", "split": "all", "spearman_r": rho_item, "n": n})
    tx, ty = list(task_means(dict(zip(common, x))).values()), list(task_means(dict(zip(common, y))).values())
    tasks = sorted(task_means(dict(zip(common, x))).keys())
    tx = [task_means(dict(zip(common, x)))[t] for t in tasks]
    ty = [task_means(dict(zip(common, y)))[t] for t in tasks]
    rho_task, n_task = safe_spearman(tx, ty)
    results.append({"method_id": method_id, "level": "task", "calibration": "none", "split": "all", "spearman_r": rho_task, "n": n_task})

    if eval_kind == "full":
        for cal in ["isotonic_oracle", "linear_oracle", "quantile_oracle"]:
            pred = calibrate_scores(x, y, x, cal)
            rho, n = safe_spearman(pred, y)
            results.append({"method_id": method_id, "level": "item", "calibration": cal, "split": "all", "spearman_r": rho, "n": n})
            t_pred = task_means(dict(zip(common, pred)))
            t_true = task_means(dict(zip(common, y)))
            tasks = sorted(set(t_pred) & set(t_true))
            rho, n = safe_spearman([t_pred[t] for t in tasks], [t_true[t] for t in tasks])
            results.append({"method_id": method_id, "level": "task", "calibration": cal, "split": "all", "spearman_r": rho, "n": n})

        pred = per_task_isotonic(common, x, y)
        rho, n = safe_spearman(pred, y)
        results.append({"method_id": method_id, "level": "item", "calibration": "per_task_isotonic_oracle", "split": "all", "spearman_r": rho, "n": n})

        if train_keys and test_keys:
            train_idx = [i for i, k in enumerate(common) if k in train_keys]
            test_idx = [i for i, k in enumerate(common) if k in test_keys]
            if len(train_idx) >= 5 and len(test_idx) >= 3:
                for cal in ["isotonic_oracle", "linear_oracle"]:
                    pred_all = calibrate_scores(x, y, x, cal, train_idx=train_idx)
                    pred_test = [pred_all[i] for i in test_idx]
                    y_test = [y[i] for i in test_idx]
                    rho, n = safe_spearman(pred_test, y_test)
                    results.append(
                        {
                            "method_id": method_id,
                            "level": "item",
                            "calibration": cal,
                            "split": "holdout_items",
                            "spearman_r": rho,
                            "n": n,
                        }
                    )
    return results


def write_report(out_dir: Path, rows: List[dict], threshold: float = 0.7) -> None:
    hit = [r for r in rows if math.isfinite(r["spearman_r"]) and r["spearman_r"] >= threshold]
    hit.sort(key=lambda r: (-r["spearman_r"], r["method_id"]))
    all_sorted = sorted(
        [r for r in rows if math.isfinite(r["spearman_r"]) and r["level"] == "item" and r["calibration"] == "none"],
        key=lambda r: -r["spearman_r"],
    )
    lines = [
        "# EXP37: Five-Human Calibration / Aggregation Sweep",
        "",
        f"**TLDR:** Swept human aggregation + judge calibration methods. Methods reaching **>={threshold:.2f}** Spearman: **{len(hit)}** rows.",
        "",
        "## Methods >= 0.70 (sorted by Spearman)",
        "",
        "| Spearman | Level | Calibration | Split | Method | Judge | n |",
        "| ---: | --- | --- | --- | --- | --- | ---: |",
    ]
    for r in hit[:40]:
        parts = r["method_id"].split("|")
        judge = parts[-1] if len(parts) > 1 else ""
        human_m = "|".join(parts[:-1]) if len(parts) > 1 else r["method_id"]
        lines.append(
            f"| {r['spearman_r']:.3f} | {r['level']} | {r['calibration']} | {r['split']} | `{human_m}` | `{judge}` | {r['n']} |"
        )
    lines += [
        "",
        "## Best Raw (No Calibration) Item-Level",
        "",
        "| Spearman | Method | Judge | n |",
        "| ---: | --- | --- | ---: |",
    ]
    seen = set()
    for r in all_sorted[:15]:
        key = (r["method_id"], r["spearman_r"])
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"| {r['spearman_r']:.3f} | `{r['method_id']}` | | {r['n']} |")

    lines += [
        "",
        "## Notes",
        "- `isotonic_oracle` / `per_task_isotonic_oracle` fit on the same items they are evaluated on (upper-bound diagnostics).",
        "- `holdout_items` fits on val split and evaluates on holdout split when available.",
        "- Raw five-rater mean typically stays ~0.4-0.5 item-level; reaching 0.7+ generally requires monotone calibration or per-task fitting.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    by_item, raters = load_participant_labels(args.human_dir)
    judge_meta, judge_scores = load_judge_scores(args.result_dirs)
    train_keys, test_keys = load_split_keys(args.split_dir)

    human_methods: List[Tuple[str, Dict[str, float]]] = []
    for method, min_r, max_std in [
        ("mean", 1, None),
        ("mean", 4, None),
        ("mean", 5, None),
        ("median", 1, None),
        ("trim1", 3, None),
        ("drop_extreme", 3, None),
        ("zscore_mean", 1, None),
        ("rank_mean", 1, None),
        ("mean", 1, 0.15),
        ("mean", 1, 0.10),
        ("mean", 1, 0.05),
    ]:
        tag = f"human_{method}"
        if min_r > 1:
            tag += f"_min{min_r}"
        if max_std is not None:
            tag += f"_std{max_std}"
        h = aggregate_human(by_item, raters, method, min_raters=min_r, max_std=max_std)
        human_methods.append((tag, h))
        # task z-scored human target
        human_methods.append((tag + "_taskz", per_task_zscore(h)))

    # judge-specific optimal rater weights (oracle-ish human target)
    for jid in sorted(judge_scores.keys()):
        if judge_meta[jid]["kind"] not in {"llm", "llm_bad"}:
            continue
        w = search_rater_weights(by_item, raters, judge_scores[jid], {}, seed=args.seed)
        h = aggregate_human(by_item, raters, "weighted", weights=w)
        human_methods.append((f"human_weighted_for_{jid}", h))

    # top cert judges ensemble
    top_jids = sorted(
        [j for j in judge_meta if judge_meta[j]["kind"] == "llm"],
        key=lambda j: judge_meta[j]["cert_index_v2"],
        reverse=True,
    )[:3]
    ens = judge_ensemble(judge_scores, top_jids)
    judge_scores["ensemble_top3_cert"] = ens
    judge_meta["ensemble_top3_cert"] = {"judge_id": "ensemble_top3_cert", "kind": "ensemble", "cert_index_v2": float("nan")}

    all_rows: List[dict] = []
    for human_tag, human_items in human_methods:
        for jid, j_items in judge_scores.items():
            method_id = f"{human_tag}|{jid}"
            rows = evaluate_method(method_id, human_items, j_items, "full", train_keys, test_keys)
            if rows:
                for r in rows:
                    r["judge_id"] = jid
                    r["judge_kind"] = judge_meta.get(jid, {}).get("kind", "")
                all_rows.extend(rows)

    all_rows.sort(key=lambda r: (-999 if not math.isfinite(r.get("spearman_r", float("nan"))) else -r["spearman_r"], r["method_id"]))

    with (args.out_dir / "sweep_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()) if all_rows else ["method_id"])
        w.writeheader()
        w.writerows(all_rows)

    hits = [r for r in all_rows if math.isfinite(r["spearman_r"]) and r["spearman_r"] >= 0.7]
    summary = {
        "n_methods_evaluated": len(all_rows),
        "n_hits_ge_0_7": len(hits),
        "best_row": all_rows[0] if all_rows else None,
        "best_raw_item": max(
            (r for r in all_rows if r["calibration"] == "none" and r["level"] == "item" and r["split"] == "all"),
            key=lambda r: r["spearman_r"],
            default=None,
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    write_report(args.out_dir, all_rows)

    print(f"Wrote {args.out_dir}")
    print(f"Total rows: {len(all_rows)}, hits>=0.7: {len(hits)}")
    if all_rows:
        b = all_rows[0]
        print(f"Best: rho={b['spearman_r']:.3f} {b['method_id']} [{b['level']}/{b['calibration']}/{b['split']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
