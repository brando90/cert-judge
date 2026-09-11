#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "summary.json"
DEFAULT_DETAIL = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "detail_rows.csv"
DEFAULT_SPLIT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp23_pass_split_for_brando" / "splits"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp23_calibrated_val_test"

COMP_ORDER = ["ident", "mono", "weak", "stab", "anti", "subtle"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calibrate cert-index weights on val and report held-out test correlation")
    p.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--detail-csv", type=Path, default=DEFAULT_DETAIL)
    p.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--search-iters", type=int, default=200000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eps", type=float, default=1e-6)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return p.parse_args()


def load_human_scores(path: Path) -> Dict[str, float]:
    out: Dict[str, float] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            k = f"{row['gold_file']}::{row['candidate_file']}"
            out[k] = float(row["human_score_0_5"])
    return out


def load_judge_scores(detail_csv: Path) -> Dict[str, Dict[str, float]]:
    # judge_id -> item_key -> score_mean
    out: Dict[str, Dict[str, float]] = {}
    with detail_csv.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("row_type") != "human_eval_union":
                continue
            j = row["judge_id"]
            k = row["item_key"]
            s = float(row["score_mean"])
            out.setdefault(j, {})[k] = s
    return out


def components_from_summary(summary_json: Path) -> Tuple[List[str], np.ndarray]:
    obj = json.loads(summary_json.read_text(encoding="utf-8"))
    rows = obj["judge_rows"]
    judge_ids = [r["judge_id"] for r in rows]
    ident = np.clip(np.asarray([float(r["identity_mean"]) for r in rows], dtype=float), 0.0, 1.0)
    mono = np.clip(np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in rows], dtype=float), 0.0, 1.0)
    weak = np.clip(np.asarray([float(r["bug_weak_mono_pct"]) / 100.0 for r in rows], dtype=float), 0.0, 1.0)
    stab = np.clip(np.asarray([1.0 - float(r["flip_rate"]) for r in rows], dtype=float), 0.0, 1.0)
    anti = np.clip(np.asarray([float(r.get("anti_string_score", 0.0)) for r in rows], dtype=float), 0.0, 1.0)
    subtle = np.clip(np.asarray([float(r.get("subtle_bug_sensitivity", 0.0)) for r in rows], dtype=float), 0.0, 1.0)
    comp = np.vstack([ident, mono, weak, stab, anti, subtle])
    return judge_ids, comp


def human_corr_per_judge(
    judge_ids: List[str],
    judge_scores: Dict[str, Dict[str, float]],
    human_scores: Dict[str, float],
) -> np.ndarray:
    ys: List[float] = []
    keys = set(human_scores.keys())
    for j in judge_ids:
        js = judge_scores.get(j, {})
        overlap = sorted(keys.intersection(js.keys()))
        if len(overlap) < 3:
            ys.append(float("nan"))
            continue
        x = np.asarray([js[k] for k in overlap], dtype=float)
        y = np.asarray([human_scores[k] for k in overlap], dtype=float)
        r = float(spearmanr(x, y).statistic)
        ys.append(r)
    return np.asarray(ys, dtype=float)


def geo_index(comp: np.ndarray, w: np.ndarray, eps: float) -> np.ndarray:
    safe = np.clip(comp, eps, 1.0)
    return np.exp(np.sum(np.log(safe) * w[:, None], axis=0))


def fit_weights_random_search(comp: np.ndarray, y: np.ndarray, iters: int, seed: int, eps: float) -> Tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    best_w = np.ones(comp.shape[0], dtype=float) / comp.shape[0]
    best_r = float("-inf")

    # include a few structured priors first
    candidates = [
        np.array([1, 0, 0, 0, 0, 0], dtype=float),
        np.array([0, 1, 0, 0, 0, 0], dtype=float),
        np.array([0, 0, 1, 0, 0, 0], dtype=float),
        np.array([0, 0, 0, 1, 0, 0], dtype=float),
        np.array([0, 0.4, 0, 0.6, 0, 0], dtype=float),
        np.array([0.25, 0.25, 0.2, 0.15, 0.1, 0.05], dtype=float),
    ]

    for w in candidates:
        w = w / np.sum(w)
        x = geo_index(comp, w, eps)
        r = float(spearmanr(x, y).statistic)
        if math.isfinite(r) and r > best_r:
            best_r = r
            best_w = w.copy()

    for _ in range(iters):
        w = rng.dirichlet(np.ones(comp.shape[0], dtype=float))
        x = geo_index(comp, w, eps)
        r = float(spearmanr(x, y).statistic)
        if math.isfinite(r) and r > best_r:
            best_r = r
            best_w = w

    return best_w, best_r


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    val_tsv = args.split_dir / f"val_{args.label_set}.tsv"
    test_tsv = args.split_dir / f"test_{args.label_set}.tsv"

    human_val = load_human_scores(val_tsv)
    human_test = load_human_scores(test_tsv)
    judge_scores = load_judge_scores(args.detail_csv)
    judge_ids, comp = components_from_summary(args.summary_json)

    y_val = human_corr_per_judge(judge_ids, judge_scores, human_val)
    y_test = human_corr_per_judge(judge_ids, judge_scores, human_test)

    valid = np.isfinite(y_val)
    if np.sum(valid) < 4:
        raise ValueError("Not enough judges with finite val correlation to calibrate")

    comp_valid = comp[:, valid]
    y_val_valid = y_val[valid]

    best_w, best_val_r = fit_weights_random_search(comp_valid, y_val_valid, args.search_iters, args.seed, args.eps)

    x_all = geo_index(comp, best_w, args.eps)
    val_r = float(spearmanr(x_all[valid], y_val[valid]).statistic)

    valid_test = np.isfinite(y_test)
    test_r = float(spearmanr(x_all[valid_test], y_test[valid_test]).statistic)

    out = {
        "experiment": "exp23_calibrated_val_report_test",
        "label_set": args.label_set,
        "inputs": {
            "summary_json": str(args.summary_json),
            "detail_csv": str(args.detail_csv),
            "split_dir": str(args.split_dir),
            "val_tsv": str(val_tsv),
            "test_tsv": str(test_tsv),
        },
        "search": {
            "iters": args.search_iters,
            "seed": args.seed,
            "eps": args.eps,
            "best_val_r_from_search": best_val_r,
        },
        "weights": {k: float(best_w[i]) for i, k in enumerate(COMP_ORDER)},
        "results": {
            "val_corr_spearman": val_r,
            "test_corr_spearman": test_r,
            "n_judges_val": int(np.sum(valid)),
            "n_judges_test": int(np.sum(valid_test)),
        },
        "per_judge": [
            {
                "judge_id": j,
                "cert_index_calibrated": float(x_all[i]),
                "human_corr_val": float(y_val[i]) if math.isfinite(y_val[i]) else None,
                "human_corr_test": float(y_test[i]) if math.isfinite(y_test[i]) else None,
            }
            for i, j in enumerate(judge_ids)
        ],
        "formula": "TI = exp(sum_i w_i * log(max(eps, v_i)))",
        "components_order": COMP_ORDER,
    }

    out_path = args.out_dir / f"summary_{args.label_set}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
