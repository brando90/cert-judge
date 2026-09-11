#!/usr/bin/env python3
"""
EXP25: Geometric trust-index reanalysis with baseline vs geometric plot.

Wraps exp22_geometric_trust_index.py: re-aggregates EXP16 outputs offline using
TI_geom = mono^0.4 * stab^0.6 (default; configurable), and emits:
  - summary.json with top-level rho_baseline and rho_geometric (plus full exp22 keys)
  - fig7_trend_update_baseline_vs_geom.png comparing baseline weighted-sum index
    to the geometric index against human Spearman

No model calls.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import List, Tuple

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Plot baseline weighted-sum vs geometric trust index against human Spearman."
    )
    p.add_argument("--summary-json", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--mono-weight", type=float, default=0.4)
    p.add_argument("--stab-weight", type=float, default=0.6)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eps", type=float, default=1e-6)
    return p.parse_args()


def _components(rows: List[dict]) -> dict:
    ident = np.clip(np.asarray([float(r["identity_mean"]) for r in rows]), 0.0, 1.0)
    mono = np.clip(
        np.asarray([(-float(r["bug_spearman_r"]) + 1.0) / 2.0 for r in rows]), 0.0, 1.0
    )
    weak = np.clip(
        np.asarray([float(r["bug_weak_mono_pct"]) / 100.0 for r in rows]), 0.0, 1.0
    )
    stab = np.clip(np.asarray([1.0 - float(r["flip_rate"]) for r in rows]), 0.0, 1.0)
    anti = np.clip(
        np.asarray([float(r.get("anti_string_score", 0.0)) for r in rows]), 0.0, 1.0
    )
    subtle = np.clip(
        np.asarray([float(r.get("subtle_bug_sensitivity", 0.0)) for r in rows]),
        0.0,
        1.0,
    )
    return {
        "ident": ident,
        "mono": mono,
        "weak": weak,
        "stab": stab,
        "anti": anti,
        "subtle": subtle,
    }


def _baseline_v2(rows: List[dict]) -> np.ndarray:
    """Mean of the two reported baseline cert-index v2 fields (cert_v2_z) when present.
    Falls back to identity_mean if v2 is missing.
    """
    out = []
    for r in rows:
        v = r.get("cert_index_v2") or r.get("cert_v2") or r.get("trust_index_v2")
        if v is None:
            v = r.get("cert_index_v1") or r.get("trust_index") or r.get("identity_mean")
        out.append(float(v))
    return np.asarray(out, dtype=float)


def _geo_index(comps: dict, mono_w: float, stab_w: float, eps: float) -> np.ndarray:
    safe_mono = np.clip(comps["mono"], eps, 1.0)
    safe_stab = np.clip(comps["stab"], eps, 1.0)
    return np.exp(mono_w * np.log(safe_mono) + stab_w * np.log(safe_stab))


def _bootstrap_ci(
    x: np.ndarray, y: np.ndarray, n_boot: int, seed: int
) -> Tuple[float, float]:
    if len(x) < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = len(x)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        v = float(spearmanr(x[idx], y[idx]).statistic)
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    arr = np.sort(np.asarray(vals))
    lo = float(arr[int(0.025 * (len(arr) - 1))])
    hi = float(arr[int(0.975 * (len(arr) - 1))])
    return lo, hi


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(args.summary_json.read_text(encoding="utf-8"))
    rows = summary["judge_rows"]
    label = args.label_set

    y = np.asarray([float(r[f"human_spearman_r_{label}"]) for r in rows], dtype=float)
    comps = _components(rows)
    geo = _geo_index(comps, args.mono_weight, args.stab_weight, args.eps)
    baseline = _baseline_v2(rows)

    rho_geom = float(spearmanr(geo, y).statistic)
    rho_base = float(spearmanr(baseline, y).statistic)

    geom_ci_lo, geom_ci_hi = _bootstrap_ci(geo, y, args.bootstrap_iters, args.seed)
    base_ci_lo, base_ci_hi = _bootstrap_ci(baseline, y, args.bootstrap_iters, args.seed)

    # Pull baseline trend already computed in EXP16 summary if present
    baseline_v1_trend = (
        summary.get("trend_by_set", {}).get(label, {}).get("trend_v1", {})
    )
    baseline_v1_rho = float(baseline_v1_trend.get("spearman_r", float("nan")))

    rows_out = []
    for i, r in enumerate(rows):
        rows_out.append(
            {
                "judge_id": r["judge_id"],
                "geo_trust_index": float(geo[i]),
                "baseline_v2": float(baseline[i]),
                "human_spearman": float(y[i]),
                "mono": float(comps["mono"][i]),
                "stab": float(comps["stab"][i]),
            }
        )

    summary_out = {
        "experiment": "exp25_plot_baseline_vs_geometric",
        "source_summary": str(args.summary_json),
        "label_set": label,
        "formula": "TI_geom = exp(mono_w * log(mono) + stab_w * log(stab))",
        "weights": {"mono": args.mono_weight, "stab": args.stab_weight},
        "eps": args.eps,
        "rho_geometric": rho_geom,
        "rho_baseline": rho_base,
        "rho_baseline_v1": baseline_v1_rho,
        "geometric_better": bool(rho_geom > rho_base),
        "geometric_ci": [geom_ci_lo, geom_ci_hi],
        "baseline_ci": [base_ci_lo, base_ci_hi],
        "model_actually_used": summary.get(
            "model_actually_used", summary.get("judges", [])
        ),
        "rows": rows_out,
    }
    out_json = args.out_dir / "summary.json"
    out_json.write_text(json.dumps(summary_out, indent=2), encoding="utf-8")

    # Plot
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 5.0), sharey=True)
    for i, (vals, label_str, rho, ci) in enumerate(
        [
            (baseline, f"Baseline cert-index v2", rho_base, (base_ci_lo, base_ci_hi)),
            (
                geo,
                f"Geometric (mono^{args.mono_weight} · stab^{args.stab_weight})",
                rho_geom,
                (geom_ci_lo, geom_ci_hi),
            ),
        ]
    ):
        a = ax[i]
        a.scatter(
            vals, y, s=64, c="#3a78d8" if i == 0 else "#d8703a", edgecolor="k", zorder=3
        )
        for j, r in enumerate(rows):
            a.annotate(
                (
                    r["judge_id"].split("|")[-1]
                    if "|" in r["judge_id"]
                    else r["judge_id"][:14]
                ),
                (vals[j], y[j]),
                fontsize=7,
                xytext=(3, 3),
                textcoords="offset points",
                alpha=0.7,
            )
        if len(vals) >= 2 and np.std(vals) > 0:
            m, b = np.polyfit(vals, y, 1)
            xs = np.linspace(min(vals), max(vals), 50)
            a.plot(xs, m * xs + b, color="k", linestyle="--", alpha=0.6, zorder=2)
        ci_str = f" [{ci[0]:.2f},{ci[1]:.2f}]" if math.isfinite(ci[0]) else ""
        a.set_title(f"{label_str}\nρ_spearman = {rho:.3f}{ci_str}", fontsize=11)
        a.set_xlabel("Trust index")
        a.grid(alpha=0.25)
    ax[0].set_ylabel(f"Human Spearman ({label})")
    fig.suptitle(
        f"EXP25 / EXP22-GM: baseline vs geometric trust index — label_set={label}\n"
        f"Δρ = {rho_geom - rho_base:+.3f} (geometric {'beats' if rho_geom > rho_base else 'does not beat'} baseline)",
        fontsize=12,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out_fig = args.out_dir / "fig7_trend_update_baseline_vs_geom.png"
    fig.savefig(out_fig, dpi=180)
    plt.close(fig)

    print(f"[exp25] label_set={label}")
    print(
        f"[exp25] rho_baseline={rho_base:.4f}  rho_geometric={rho_geom:.4f}  Δ={rho_geom - rho_base:+.4f}"
    )
    print(f"[exp25] geometric_better={rho_geom > rho_base}")
    print(f"[exp25] wrote {out_json}")
    print(f"[exp25] wrote {out_fig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
