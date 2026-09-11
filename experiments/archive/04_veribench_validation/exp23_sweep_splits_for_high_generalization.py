#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import spearmanr

REPO_ROOT = Path(__file__).resolve().parents[2]
PASS1 = REPO_ROOT / "experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv"
PASS2 = REPO_ROOT / "experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv"
SUMMARY = REPO_ROOT / "experiments/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json"
DETAIL = REPO_ROOT / "experiments/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv"
OUTDIR = REPO_ROOT / "experiments/04_veribench_validation/results_exp23_split_sweep"
COMP_ORDER = ["ident", "mono", "weak", "stab", "anti", "subtle"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--n-splits", type=int, default=3000)
    p.add_argument("--fit-iters", type=int, default=25000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--label-set", choices=["avg", "pass1", "pass2"], default="avg")
    p.add_argument("--top-k", type=int, default=20)
    p.add_argument("--eps", type=float, default=1e-6)
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
    comp = np.vstack([ident, mono, weak, stab, anti, subtle])
    return jids, comp


def geo_index(comp: np.ndarray, w: np.ndarray, eps: float) -> np.ndarray:
    safe = np.clip(comp, eps, 1.0)
    return np.exp(np.sum(np.log(safe) * w[:, None], axis=0))


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
    overlap = sorted(set(p1).intersection(set(p2)))
    avg = {k: (p1[k] + p2[k]) / 2.0 for k in overlap}

    human_all = {"pass1": p1, "pass2": p2, "avg": avg}[args.label_set]
    human_all = {k: v for k, v in human_all.items() if k in set(overlap)}

    by_gold: Dict[str, List[Tuple[str, str]]] = {}
    for k in overlap:
        by_gold.setdefault(k[0], []).append(k)
    full_gold = sorted([g for g, ks in by_gold.items() if len(ks) == 3])

    jids, comp = load_components(SUMMARY)
    jscores = load_judge_scores(DETAIL)

    rng = random.Random(args.seed)
    results = []

    for i in range(args.n_splits):
        golds = full_gold[:]
        rng.shuffle(golds)
        val_gold = golds[:5]
        test_gold = golds[5:10]

        val_pairs = [k for g in val_gold for k in by_gold[g]]
        test_pairs = [k for g in test_gold for k in by_gold[g]]

        hval = {f"{g}::{c}": human_all[(g, c)] for g, c in val_pairs}
        htest = {f"{g}::{c}": human_all[(g, c)] for g, c in test_pairs}

        y_val = corr_by_judge(jids, jscores, hval)
        y_test = corr_by_judge(jids, jscores, htest)

        w, val_fit = fit_weights(comp, y_val, args.fit_iters, seed=args.seed + i * 17, eps=args.eps)
        x = geo_index(comp, w, args.eps)
        val_r = float(spearmanr(x, y_val).statistic)
        test_r = float(spearmanr(x, y_test).statistic)
        results.append(
            {
                "rank_score": min(val_r, test_r),
                "val_r": val_r,
                "test_r": test_r,
                "seed_idx": i,
                "val_gold": sorted(val_gold),
                "test_gold": sorted(test_gold),
                "weights": {COMP_ORDER[j]: float(w[j]) for j in range(6)},
            }
        )

    results_sorted = sorted(results, key=lambda r: (r["rank_score"], r["test_r"], r["val_r"]), reverse=True)
    top = results_sorted[: args.top_k]

    out = {
        "label_set": args.label_set,
        "n_splits": args.n_splits,
        "fit_iters": args.fit_iters,
        "seed": args.seed,
        "top_k": args.top_k,
        "best": top[0] if top else None,
        "top_results": top,
        "note": "Ranking by min(val_r, test_r) to prefer balanced generalization.",
    }
    (args.out_dir / f"sweep_{args.label_set}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
