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
PASS1 = REPO_ROOT / "experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv"
PASS2 = REPO_ROOT / "experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv"
SUMMARY = REPO_ROOT / "experiments/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json"
DETAIL = REPO_ROOT / "experiments/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv"
OUTDIR = REPO_ROOT / "experiments/04_veribench_validation/results_exp23_cross_pass_calibration"
COMP_ORDER = ["ident", "mono", "weak", "stab", "anti", "subtle"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--fit-on", choices=["pass1", "pass2"], default="pass1")
    p.add_argument("--iters", type=int, default=200000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eps", type=float, default=1e-6)
    p.add_argument("--summary-json", type=Path, default=SUMMARY)
    p.add_argument("--detail-csv", type=Path, default=DETAIL)
    p.add_argument("--out-dir", type=Path, default=OUTDIR)
    return p.parse_args()


def read_tsv(path: Path) -> Dict[Tuple[str, str], float]:
    out = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            out[(row["gold_file"], row["candidate_file"])] = float(row["human_score_0_5"])
    return out


def load_judge_scores(path: Path) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("row_type") != "human_eval_union":
                continue
            out.setdefault(row["judge_id"], {})[row["item_key"]] = float(row["score_mean"])
    return out


def load_components(path: Path) -> Tuple[List[str], np.ndarray]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    rows = obj["judge_rows"]
    jids = [r["judge_id"] for r in rows]
    ident = np.clip(np.asarray([float(r["identity_mean"]) for r in rows]), 0, 1)
    mono = np.clip(np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in rows]), 0, 1)
    weak = np.clip(np.asarray([float(r["bug_weak_mono_pct"]) / 100.0 for r in rows]), 0, 1)
    stab = np.clip(np.asarray([1.0 - float(r["flip_rate"]) for r in rows]), 0, 1)
    anti = np.clip(np.asarray([float(r.get("anti_string_score", 0.0)) for r in rows]), 0, 1)
    subtle = np.clip(np.asarray([float(r.get("subtle_bug_sensitivity", 0.0)) for r in rows]), 0, 1)
    return jids, np.vstack([ident, mono, weak, stab, anti, subtle])


def corr_by_judge(jids: List[str], judge_scores: Dict[str, Dict[str, float]], human: Dict[str, float]) -> np.ndarray:
    ys = []
    keys = set(human.keys())
    for j in jids:
        js = judge_scores[j]
        overlap = sorted(keys.intersection(js.keys()))
        x = np.asarray([js[k] for k in overlap], dtype=float)
        y = np.asarray([human[k] for k in overlap], dtype=float)
        ys.append(float(spearmanr(x, y).statistic))
    return np.asarray(ys, dtype=float)


def geo_index(comp: np.ndarray, w: np.ndarray, eps: float) -> np.ndarray:
    safe = np.clip(comp, eps, 1.0)
    return np.exp(np.sum(np.log(safe) * w[:, None], axis=0))


def fit_weights(comp: np.ndarray, y: np.ndarray, iters: int, seed: int, eps: float) -> Tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    best_w = np.array([0, 0.4, 0, 0.6, 0, 0], dtype=float)
    best_w = best_w / best_w.sum()
    best_r = float(spearmanr(geo_index(comp, best_w, eps), y).statistic)
    starts = [
        np.array([1, 0, 0, 0, 0, 0], dtype=float),
        np.array([0, 1, 0, 0, 0, 0], dtype=float),
        np.array([0, 0.4, 0, 0.6, 0, 0], dtype=float),
        np.array([0.25, 0.25, 0.2, 0.15, 0.1, 0.05], dtype=float),
    ]
    for w in starts:
        w = w / w.sum()
        r = float(spearmanr(geo_index(comp, w, eps), y).statistic)
        if math.isfinite(r) and r > best_r:
            best_r, best_w = r, w.copy()
    for _ in range(iters):
        w = rng.dirichlet(np.ones(6))
        r = float(spearmanr(geo_index(comp, w, eps), y).statistic)
        if math.isfinite(r) and r > best_r:
            best_r, best_w = r, w
    return best_w, best_r


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    p1 = read_tsv(PASS1)
    p2 = read_tsv(PASS2)
    overlap = set(p1).intersection(p2)
    human1 = {f"{g}::{c}": p1[(g, c)] for (g, c) in overlap}
    human2 = {f"{g}::{c}": p2[(g, c)] for (g, c) in overlap}

    fit_human = human1 if args.fit_on == "pass1" else human2
    test_human = human2 if args.fit_on == "pass1" else human1
    test_name = "pass2" if args.fit_on == "pass1" else "pass1"

    jids, comp = load_components(args.summary_json)
    jscores = load_judge_scores(args.detail_csv)
    y_fit = corr_by_judge(jids, jscores, fit_human)
    y_test = corr_by_judge(jids, jscores, test_human)

    w, fit_r = fit_weights(comp, y_fit, args.iters, args.seed, args.eps)
    x = geo_index(comp, w, args.eps)
    fit_corr = float(spearmanr(x, y_fit).statistic)
    test_corr = float(spearmanr(x, y_test).statistic)

    out = {
        "fit_on": args.fit_on,
        "report_on": test_name,
        "n_overlap_pairs": len(overlap),
        "summary_json": str(args.summary_json),
        "detail_csv": str(args.detail_csv),
        "weights": {COMP_ORDER[i]: float(w[i]) for i in range(6)},
        "fit_corr_spearman": fit_corr,
        "test_corr_spearman": test_corr,
        "formula": "TI = exp(sum_i w_i * log(max(eps, v_i)))",
        "per_judge": [
            {
                "judge_id": jids[i],
                "cert_index": float(x[i]),
                "human_corr_fit": float(y_fit[i]),
                "human_corr_test": float(y_test[i]),
            }
            for i in range(len(jids))
        ],
    }
    out_path = args.out_dir / f"summary_fit_{args.fit_on}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
