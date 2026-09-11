#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DETAIL = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "detail_rows.csv"
DEFAULT_OUT = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp24_alpha_canonicalized_identity"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP24: alpha-canonicalized identity variance diagnostic")
    p.add_argument("--detail-rows", type=Path, default=DEFAULT_DETAIL)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--alpha-policy", choices=["drop", "clip"], default="drop",
                   help="drop: remove ALPHA rows; clip: winsorize ALPHA rows to STYLE median per judge")
    p.add_argument("--dpi", type=int, default=180)
    return p.parse_args()


def _extract_variant(item_key: str) -> str:
    parts = item_key.split("::")
    return parts[-1].upper().strip() if len(parts) >= 2 else ""


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # judge -> variant -> scores
    by_judge_variant: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    with args.detail_rows.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("row_type") != "property_identity":
                continue
            jid = row["judge_id"]
            variant = _extract_variant(row["item_key"])
            try:
                score = float(row["score_mean"])
            except Exception:
                continue
            by_judge_variant[jid][variant].append(score)

    judge_ids = sorted(by_judge_variant.keys())
    rows: List[dict] = []

    for jid in judge_ids:
        vmap = by_judge_variant[jid]
        all_scores = np.asarray([s for arr in vmap.values() for s in arr], dtype=float)
        base_mean = float(np.mean(all_scores)) if len(all_scores) else float("nan")
        base_std = float(np.std(all_scores)) if len(all_scores) else float("nan")

        # canonicalized proxy
        canon_vals: List[float] = []
        style_med = float(np.median(np.asarray(vmap.get("STYLE", [base_mean]), dtype=float)))
        for v, arr in vmap.items():
            if v == "ALPHA":
                if args.alpha_policy == "drop":
                    continue
                if args.alpha_policy == "clip":
                    canon_vals.extend([style_med] * len(arr))
            else:
                canon_vals.extend(arr)

        canon_arr = np.asarray(canon_vals, dtype=float)
        canon_mean = float(np.mean(canon_arr)) if len(canon_arr) else float("nan")
        canon_std = float(np.std(canon_arr)) if len(canon_arr) else float("nan")

        alpha_arr = np.asarray(vmap.get("ALPHA", []), dtype=float)
        alpha_std = float(np.std(alpha_arr)) if len(alpha_arr) else float("nan")

        rows.append(
            {
                "judge_id": jid,
                "identity_mean_original": base_mean,
                "identity_std_original": base_std,
                "identity_mean_alpha_canon": canon_mean,
                "identity_std_alpha_canon": canon_std,
                "alpha_only_std": alpha_std,
                "delta_std": canon_std - base_std,
                "pct_std_reduction": (100.0 * (base_std - canon_std) / base_std) if base_std > 0 else 0.0,
            }
        )

    # Write CSV summary.
    csv_path = args.out_dir / "identity_alpha_canonicalized_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fn = [
            "judge_id",
            "identity_mean_original",
            "identity_std_original",
            "identity_mean_alpha_canon",
            "identity_std_alpha_canon",
            "alpha_only_std",
            "delta_std",
            "pct_std_reduction",
        ]
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)

    # Plot comparison bars (std before vs canonicalized).
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [r["judge_id"] for r in rows]
    orig = [r["identity_std_original"] for r in rows]
    canon = [r["identity_std_alpha_canon"] for r in rows]

    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(max(10.5, 0.75 * len(labels)), 5.2))
    ax.bar(x - width / 2, orig, width=width, label="Original identity std", color="#4C78A8")
    ax.bar(x + width / 2, canon, width=width, label=f"Alpha-canonicalized std ({args.alpha_policy})", color="#59A14F")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Std dev of identity scores")
    ax.set_title("EXP24: Identity Variance Before vs Alpha-Canonicalized Proxy")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    plot_path = args.out_dir / "fig_identity_std_before_vs_alpha_canonicalized.png"
    fig.savefig(plot_path, dpi=args.dpi)
    plt.close(fig)

    agg = {
        "n_judges": len(rows),
        "alpha_policy": args.alpha_policy,
        "mean_std_original": float(np.mean(np.asarray(orig, dtype=float))),
        "mean_std_alpha_canon": float(np.mean(np.asarray(canon, dtype=float))),
        "median_pct_std_reduction": float(np.median(np.asarray([r["pct_std_reduction"] for r in rows], dtype=float))),
        "mean_pct_std_reduction": float(np.mean(np.asarray([r["pct_std_reduction"] for r in rows], dtype=float))),
        "inputs": {"detail_rows": str(args.detail_rows)},
        "outputs": {"csv": str(csv_path), "plot": str(plot_path)},
        "note": "Alpha-canonicalized is a post-hoc proxy; true canonicalization requires rescoring canonicalized theorem text.",
    }

    (args.out_dir / "summary.json").write_text(json.dumps(agg, indent=2), encoding="utf-8")
    print(json.dumps(agg, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
