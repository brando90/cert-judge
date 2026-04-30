#!/usr/bin/env python3
"""
EXP21: Sweep certification-index formulations for EXP16 trend quality.

Search over many cert-index formulas using existing per-judge summary rows
(no new LLM calls) and report candidates that improve:
  - trend Spearman correlation with human correlation
  - bootstrap CI width of that trend
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "summary.json"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp21_cert_index_sweep"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sweep cert-index formulas for EXP16 trend")
    p.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--bootstrap-iters", type=int, default=8000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--min-rho", type=float, default=0.7)
    p.add_argument("--weight-step", type=float, default=0.1)
    p.add_argument("--max-weight-vectors-per-subset", type=int, default=120)
    p.add_argument("--max-components", type=int, default=6)
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


def _norm_nonneg(v: np.ndarray) -> np.ndarray:
    return np.clip(v, 0.0, 1.0)


def _components(rows: List[dict]) -> Dict[str, np.ndarray]:
    identity = _norm_nonneg(np.asarray([float(r["identity_mean"]) for r in rows], dtype=float))
    mono = _norm_nonneg(np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in rows], dtype=float))
    weak = _norm_nonneg(np.asarray([float(r["bug_weak_mono_pct"]) / 100.0 for r in rows], dtype=float))
    stability = _norm_nonneg(np.asarray([1.0 - float(r["flip_rate"]) for r in rows], dtype=float))
    anti = _norm_nonneg(np.asarray([float(r.get("anti_string_score", 0.0)) for r in rows], dtype=float))
    subtle = _norm_nonneg(np.asarray([float(r.get("subtle_bug_sensitivity", 0.0)) for r in rows], dtype=float))
    return {
        "ident": identity,
        "mono": mono,
        "weak": weak,
        "stab": stability,
        "anti": anti,
        "subtle": subtle,
    }


def _weight_vectors(n: int, step: float, max_vectors: int, rng: np.random.Generator) -> List[np.ndarray]:
    inv = int(round(1.0 / step))
    out: List[np.ndarray] = []
    for ints in itertools.product(range(inv + 1), repeat=n):
        if sum(ints) != inv:
            continue
        w = np.asarray(ints, dtype=float) / float(inv)
        if np.count_nonzero(w) < 2:
            continue
        out.append(w)
    if len(out) > max_vectors:
        idx = rng.choice(len(out), size=max_vectors, replace=False)
        out = [out[i] for i in idx.tolist()]
    return out


def _score_formula(arr: np.ndarray, weights: np.ndarray, agg: str) -> np.ndarray:
    if agg == "arith":
        return np.sum(arr * weights[:, None], axis=0)
    # weighted geometric mean
    safe = np.clip(arr, 1e-8, 1.0)
    return np.exp(np.sum(np.log(safe) * weights[:, None], axis=0))


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    obj = json.loads(args.summary_json.read_text(encoding="utf-8"))
    rows = obj["judge_rows"]
    y = np.asarray([float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float)

    comps = _components(rows)
    comp_names = sorted(comps.keys())
    baseline = obj["trend_by_set"][args.label_set]["trend_v1"]
    rng = np.random.default_rng(args.seed + 777)

    all_results: List[dict] = []
    formula_id = 0
    k_max = min(int(args.max_components), len(comp_names))
    for k in range(2, k_max + 1):
        for subset in itertools.combinations(comp_names, k):
            arr = np.vstack([comps[name] for name in subset])
            ws = _weight_vectors(
                n=k,
                step=args.weight_step,
                max_vectors=int(args.max_weight_vectors_per_subset),
                rng=rng,
            )
            for w in ws:
                for agg in ("arith", "geom"):
                    formula_id += 1
                    x = _score_formula(arr, w, agg)
                    rho = float(spearmanr(x, y).statistic)
                    ci_lo, ci_hi = _bootstrap_ci_spearman(x, y, args.bootstrap_iters, args.seed + formula_id)
                    width = float(ci_hi - ci_lo) if (math.isfinite(ci_lo) and math.isfinite(ci_hi)) else float("nan")
                    all_results.append(
                        {
                            "formula_id": formula_id,
                            "agg": agg,
                            "components": "|".join(subset),
                            "weights": "|".join(f"{z:.3f}" for z in w.tolist()),
                            "n_components": k,
                            "spearman_r": rho,
                            "spearman_ci_lo": ci_lo,
                            "spearman_ci_hi": ci_hi,
                            "spearman_ci_width": width,
                            "objective_r_minus_0p25w": float(rho - 0.25 * width) if math.isfinite(width) else float("nan"),
                        }
                    )

    all_results.sort(
        key=lambda r: (
            -float(r["objective_r_minus_0p25w"]) if math.isfinite(float(r["objective_r_minus_0p25w"])) else float("-inf"),
            -float(r["spearman_r"]),
        )
    )

    winners = [
        r for r in all_results
        if math.isfinite(float(r["spearman_r"])) and math.isfinite(float(r["spearman_ci_width"])) and float(r["spearman_r"]) >= args.min_rho
    ]
    winners.sort(key=lambda r: (float(r["spearman_ci_width"]), -float(r["spearman_r"])))

    csv_path = args.out_dir / "sweep_rows.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
        w.writeheader()
        w.writerows(all_results)

    summary = {
        "experiment": "exp21_cert_index_sweep",
        "source_summary": str(args.summary_json),
        "label_set": args.label_set,
        "n_judges": len(rows),
        "search": {
            "component_pool": comp_names,
            "weight_step": args.weight_step,
            "max_weight_vectors_per_subset": args.max_weight_vectors_per_subset,
            "max_components": args.max_components,
            "bootstrap_iters": args.bootstrap_iters,
            "min_rho": args.min_rho,
        },
        "baseline_trend_v1": baseline,
        "top_by_objective": all_results[:20],
        "top_meeting_min_rho_sorted_by_narrow_ci": winners[:20],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# EXP21 Cert-Index Sweep")
    lines.append("")
    lines.append(f"- source: `{args.summary_json}`")
    lines.append(f"- label set: `{args.label_set}`")
    lines.append(
        f"- baseline v1: rho={baseline['spearman_r']:.3f}, "
        f"CI=[{baseline['spearman_ci_lo']:.3f}, {baseline['spearman_ci_hi']:.3f}], "
        f"width={baseline['spearman_ci_hi'] - baseline['spearman_ci_lo']:.3f}"
    )
    lines.append("")
    lines.append("## Best objective (rho - 0.25*CI_width)")
    for r in all_results[:10]:
        lines.append(
            f"- id={r['formula_id']} {r['agg']} comps={r['components']} w={r['weights']} | "
            f"rho={r['spearman_r']:.3f} CI=[{r['spearman_ci_lo']:.3f},{r['spearman_ci_hi']:.3f}] "
            f"width={r['spearman_ci_width']:.3f}"
        )
    lines.append("")
    lines.append("## Candidates with rho >= min_rho (sorted by CI width)")
    if winners:
        for r in winners[:10]:
            lines.append(
                f"- id={r['formula_id']} {r['agg']} comps={r['components']} w={r['weights']} | "
                f"rho={r['spearman_r']:.3f} CI=[{r['spearman_ci_lo']:.3f},{r['spearman_ci_hi']:.3f}] "
                f"width={r['spearman_ci_width']:.3f}"
            )
    else:
        lines.append("- none found at current min_rho threshold")
    (args.out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
