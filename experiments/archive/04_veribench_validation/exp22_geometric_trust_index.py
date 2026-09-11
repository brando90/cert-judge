#!/usr/bin/env python3
"""
EXP22: Geometric trust-index re-aggregation for EXP16 outputs.

Implements the meeting formulation:
  TI = prod_i v_i ^ w_i
     = exp(sum_i w_i * log(v_i))

Uses existing EXP16 summary judge rows (no model calls).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "summary.json"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_geometric_trust_index"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute geometric trust index from EXP16 summary")
    p.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    # Weights over: ident, mono, weak, stab, anti, subtle (must sum to ~1)
    p.add_argument("--weights", type=str, default="0.25,0.25,0.2,0.15,0.1,0.05")
    p.add_argument("--eps", type=float, default=1e-6)
    return p.parse_args()


def _bootstrap_ci_spearman(x: np.ndarray, y: np.ndarray, n_boot: int, seed: int) -> Tuple[float, float]:
    if len(x) < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = len(x)
    vals: List[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        v = float(spearmanr(x[idx], y[idx]).statistic)
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    vals_arr = np.sort(np.asarray(vals, dtype=float))
    lo = float(vals_arr[int(0.025 * (len(vals_arr) - 1))])
    hi = float(vals_arr[int(0.975 * (len(vals_arr) - 1))])
    return (lo, hi)


def _components(rows: List[dict]) -> Dict[str, np.ndarray]:
    ident = np.clip(np.asarray([float(r["identity_mean"]) for r in rows], dtype=float), 0.0, 1.0)
    mono = np.clip(np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in rows], dtype=float), 0.0, 1.0)
    weak = np.clip(np.asarray([float(r["bug_weak_mono_pct"]) / 100.0 for r in rows], dtype=float), 0.0, 1.0)
    stab = np.clip(np.asarray([1.0 - float(r["flip_rate"]) for r in rows], dtype=float), 0.0, 1.0)
    anti = np.clip(np.asarray([float(r.get("anti_string_score", 0.0)) for r in rows], dtype=float), 0.0, 1.0)
    subtle = np.clip(np.asarray([float(r.get("subtle_bug_sensitivity", 0.0)) for r in rows], dtype=float), 0.0, 1.0)
    return {"ident": ident, "mono": mono, "weak": weak, "stab": stab, "anti": anti, "subtle": subtle}


def _parse_weights(raw: str) -> np.ndarray:
    parts = [float(x.strip()) for x in raw.split(",") if x.strip()]
    if len(parts) != 6:
        raise ValueError("weights must contain 6 comma-separated values: ident,mono,weak,stab,anti,subtle")
    w = np.asarray(parts, dtype=float)
    if np.any(w < 0):
        raise ValueError("weights must be non-negative")
    s = float(np.sum(w))
    if s <= 0:
        raise ValueError("weights sum must be > 0")
    return w / s


def _geo_index(comp_arr: np.ndarray, w: np.ndarray, eps: float) -> np.ndarray:
    safe = np.clip(comp_arr, eps, 1.0)
    return np.exp(np.sum(np.log(safe) * w[:, None], axis=0))


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(args.summary_json.read_text(encoding="utf-8"))
    rows = summary["judge_rows"]
    y = np.asarray([float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float)

    comps = _components(rows)
    order = ["ident", "mono", "weak", "stab", "anti", "subtle"]
    arr = np.vstack([comps[k] for k in order])
    w = _parse_weights(args.weights)
    x = _geo_index(arr, w, eps=float(args.eps))

    rho = float(spearmanr(x, y).statistic)
    ci_lo, ci_hi = _bootstrap_ci_spearman(x, y, args.bootstrap_iters, args.seed)

    out_rows = []
    for i, r in enumerate(rows):
        out_rows.append(
            {
                "judge_id": r["judge_id"],
                "geo_trust_index": float(x[i]),
                "human_spearman": float(y[i]),
                "ident": float(arr[0, i]),
                "mono": float(arr[1, i]),
                "weak": float(arr[2, i]),
                "stab": float(arr[3, i]),
                "anti": float(arr[4, i]),
                "subtle": float(arr[5, i]),
            }
        )

    result = {
        "experiment": "exp22_geometric_trust_index",
        "source_summary": str(args.summary_json),
        "label_set": args.label_set,
        "formula": "TI = exp(sum_i w_i * log(max(eps, v_i)))",
        "components_order": order,
        "weights": {k: float(w[i]) for i, k in enumerate(order)},
        "eps": float(args.eps),
        "trend": {
            "spearman_r": rho,
            "spearman_ci_lo": ci_lo,
            "spearman_ci_hi": ci_hi,
            "spearman_ci_width": float(ci_hi - ci_lo) if math.isfinite(ci_lo) and math.isfinite(ci_hi) else float("nan"),
        },
        "baseline_v1_trend": summary["trend_by_set"][args.label_set]["trend_v1"],
        "rows": out_rows,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

