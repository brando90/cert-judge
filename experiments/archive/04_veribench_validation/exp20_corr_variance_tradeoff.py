#!/usr/bin/env python3
"""
EXP20: Correlation-Variance tradeoff analysis for judge algorithms.

Goal:
  Evaluate (judge, #calls, aggregation) -> (human correlation, variance, behavior-correlation).

This is an offline analysis over EXP16 detail rows with repeated scores.
No API calls are made.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "data"
DEFAULT_DETAIL_ROWS = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "detail_rows.csv"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp20_corr_variance_tradeoff"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP20 corr-variance tradeoff analysis")
    p.add_argument("--detail-rows", type=Path, default=DEFAULT_DETAIL_ROWS)
    p.add_argument("--pass1-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_20260425.tsv")
    p.add_argument("--pass2-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_ORIGINAL.tsv")
    p.add_argument("--avg-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_avg_two_passes_20260425.tsv")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--trials", type=int, default=500)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-k", type=int, default=9)
    return p.parse_args()


def _load_tsv_scores(path: Path) -> Dict[str, float]:
    rows: Dict[Tuple[str, str], List[float]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            g = str(row.get("gold_file", "")).strip()
            c = str(row.get("candidate_file", "")).strip()
            s = str(row.get("human_score_0_5", "")).strip()
            if not g or not c or not s:
                continue
            rows.setdefault((g, c), []).append(float(s))
    out: Dict[str, float] = {}
    for (g, c), vals in rows.items():
        out[f"{g}::{c}"] = float(sum(vals) / len(vals))
    return out


def _weak_monotonicity_pct(ladders: List[List[float]]) -> float:
    if not ladders:
        return float("nan")
    ok = 0
    total = 0
    for seq in ladders:
        if len(seq) < 2:
            continue
        total += 1
        non_inc = True
        for a, b in zip(seq[:-1], seq[1:]):
            if b > a + 1e-12:
                non_inc = False
                break
        if non_inc:
            ok += 1
    if total == 0:
        return float("nan")
    return 100.0 * ok / total


def _agg(arr: np.ndarray, mode: str) -> float:
    if mode == "median":
        return float(np.median(arr))
    return float(np.mean(arr))


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    human_sets = {
        "pass1": _load_tsv_scores(args.pass1_tsv),
        "pass2": _load_tsv_scores(args.pass2_tsv),
        "avg": _load_tsv_scores(args.avg_tsv),
    }

    # Read detail rows and parse repeats.
    by_judge_type: Dict[str, Dict[str, List[Tuple[str, np.ndarray]]]] = defaultdict(lambda: defaultdict(list))
    rep_lens: Dict[str, List[int]] = defaultdict(list)
    with args.detail_rows.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            jid = row["judge_id"]
            rt = row["row_type"]
            key = row["item_key"]
            reps = np.asarray(json.loads(row["repeat_scores"]), dtype=float)
            by_judge_type[jid][rt].append((key, reps))
            rep_lens[jid].append(len(reps))

    out_rows: List[dict] = []
    agg_modes = ["mean", "median"]

    for jid in sorted(by_judge_type.keys()):
        human_rows = by_judge_type[jid].get("human_eval_union", [])
        bug_rows = by_judge_type[jid].get("property_bug", [])
        if not human_rows:
            continue
        min_rep = min(len(reps) for _, reps in human_rows)
        max_k = min(args.max_k, min_rep)
        for k in range(1, max_k + 1):
            for agg_mode in agg_modes:
                # Track score variance at item-level and corr variance across trials.
                item_vals: Dict[str, List[float]] = defaultdict(list)
                corr_trials: Dict[str, List[float]] = {"pass1": [], "pass2": [], "avg": []}
                bug_spear_trials: List[float] = []
                bug_weak_trials: List[float] = []

                for _ in range(args.trials):
                    # Human rows trial scores
                    score_map: Dict[str, float] = {}
                    for item_key, reps in human_rows:
                        idx = rng.choice(len(reps), size=k, replace=False)
                        s = _agg(reps[idx], agg_mode)
                        score_map[item_key] = s
                        item_vals[item_key].append(s)

                    for label_set, hmap in human_sets.items():
                        xs: List[float] = []
                        ys: List[float] = []
                        for ik, s in score_map.items():
                            if ik in hmap:
                                xs.append(s)
                                ys.append(hmap[ik])
                        if len(xs) >= 3:
                            corr_trials[label_set].append(float(spearmanr(xs, ys).statistic))

                    # Behavior monotonicity for bug rows
                    b_levels: List[int] = []
                    b_scores: List[float] = []
                    by_problem: Dict[str, Dict[int, float]] = defaultdict(dict)
                    for item_key, reps in bug_rows:
                        parts = item_key.split("::")
                        if len(parts) != 2:
                            continue
                        problem, lvl_txt = parts
                        if not lvl_txt.startswith("L"):
                            continue
                        try:
                            lvl = int(lvl_txt[1:])
                        except Exception:
                            continue
                        idx = rng.choice(len(reps), size=k, replace=False)
                        s = _agg(reps[idx], agg_mode)
                        b_levels.append(lvl)
                        b_scores.append(s)
                        by_problem[problem][lvl] = s

                    if len(b_levels) >= 3:
                        bug_spear_trials.append(float(spearmanr(b_levels, b_scores).statistic))
                    ladders: List[List[float]] = []
                    for _, lv in by_problem.items():
                        seq = []
                        ok = True
                        for lv_idx in [0, 1, 2, 3, 4]:
                            if lv_idx not in lv:
                                ok = False
                                break
                            seq.append(lv[lv_idx])
                        if ok:
                            ladders.append(seq)
                    bug_weak_trials.append(_weak_monotonicity_pct(ladders))

                # summarize
                avg_item_var = float(
                    np.mean([np.var(np.asarray(v, dtype=float), ddof=1) for v in item_vals.values() if len(v) > 1])
                )
                row = {
                    "judge_id": jid,
                    "k_calls": k,
                    "aggregation": agg_mode,
                    "trials": args.trials,
                    "n_human_items": len(human_rows),
                    "repeat_len_min": min_rep,
                    "repeat_len_mode": int(np.bincount(np.asarray(rep_lens[jid], dtype=int)).argmax()),
                    "item_score_variance_mean": avg_item_var,
                }
                for label_set in ["pass1", "pass2", "avg"]:
                    arr = np.asarray(corr_trials[label_set], dtype=float)
                    row[f"human_spearman_{label_set}_mean"] = float(np.nanmean(arr)) if len(arr) else float("nan")
                    row[f"human_spearman_{label_set}_std"] = float(np.nanstd(arr, ddof=1)) if len(arr) > 1 else 0.0
                bs = np.asarray(bug_spear_trials, dtype=float)
                bw = np.asarray(bug_weak_trials, dtype=float)
                row["bug_spearman_mean"] = float(np.nanmean(bs)) if len(bs) else float("nan")
                row["bug_spearman_std"] = float(np.nanstd(bs, ddof=1)) if len(bs) > 1 else 0.0
                row["bug_weak_mono_pct_mean"] = float(np.nanmean(bw)) if len(bw) else float("nan")
                row["bug_weak_mono_pct_std"] = float(np.nanstd(bw, ddof=1)) if len(bw) > 1 else 0.0

                # Objective examples (higher is better)
                row["objective_avg_corr_minus_std"] = row["human_spearman_avg_mean"] - row["human_spearman_avg_std"]
                row["objective_pass2_corr_minus_std"] = row["human_spearman_pass2_mean"] - row["human_spearman_pass2_std"]
                out_rows.append(row)

    # Write detailed rows.
    fieldnames = list(out_rows[0].keys()) if out_rows else []
    out_csv = args.out_dir / "config_tradeoff_rows.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    # Top configs summary.
    def top_rows(metric: str, n: int = 12) -> List[dict]:
        arr = [r for r in out_rows if np.isfinite(r.get(metric, np.nan))]
        arr.sort(key=lambda r: float(r[metric]), reverse=True)
        return arr[:n]

    summary = {
        "experiment": "exp20_corr_variance_tradeoff",
        "detail_rows": str(args.detail_rows),
        "trials": int(args.trials),
        "search_space": {
            "k_calls_range": [1, int(args.max_k)],
            "aggregation": agg_modes,
        },
        "note": (
            "If repeat_len_min for an LLM judge is 3, then larger k are not available due to cached 3-repeat calls. "
            "Rerun EXP16 with a fresh cache namespace to truly analyze k>3 for LLMs."
        ),
        "top_by_objective_avg_corr_minus_std": top_rows("objective_avg_corr_minus_std"),
        "top_by_objective_pass2_corr_minus_std": top_rows("objective_pass2_corr_minus_std"),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Markdown report
    lines = []
    lines.append("# EXP20 Corr-Variance Tradeoff")
    lines.append("")
    lines.append(f"- detail_rows: `{args.detail_rows}`")
    lines.append(f"- trials per config: {args.trials}")
    lines.append("")
    lines.append("## Top configs (avg corr - std)")
    for r in summary["top_by_objective_avg_corr_minus_std"][:8]:
        lines.append(
            f"- {r['judge_id']} | k={r['k_calls']} | {r['aggregation']} | "
            f"avg_corr={r['human_spearman_avg_mean']:.3f} ± {r['human_spearman_avg_std']:.3f} | "
            f"item_var={r['item_score_variance_mean']:.5f}"
        )
    lines.append("")
    lines.append("## Top configs (pass2 corr - std)")
    for r in summary["top_by_objective_pass2_corr_minus_std"][:8]:
        lines.append(
            f"- {r['judge_id']} | k={r['k_calls']} | {r['aggregation']} | "
            f"pass2_corr={r['human_spearman_pass2_mean']:.3f} ± {r['human_spearman_pass2_std']:.3f} | "
            f"item_var={r['item_score_variance_mean']:.5f}"
        )
    lines.append("")
    lines.append("## Caveat")
    lines.append(
        "- LLM repeats appear to be cached at 3 in this detail file; to evaluate true k>3 LLM behavior, rerun EXP16 with a fresh cache namespace."
    )
    (args.out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print("=" * 72)
    print("EXP20: corr-variance tradeoff analysis")
    print(f"rows={len(out_rows)}")
    print(f"Wrote: {out_csv}")
    print(f"Wrote: {args.out_dir / 'summary.json'}")
    print(f"Wrote: {args.out_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

