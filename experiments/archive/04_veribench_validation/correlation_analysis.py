#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pointbiserialr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = REPO_ROOT / "experiments" / "04_veribench_validation" / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Correlation analysis for VeriBench validation")
    p.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    p.add_argument("--bootstrap-iters", type=int, default=3000)
    return p.parse_args()


def _bootstrap_ci(x: np.ndarray, y: np.ndarray, fn, n_boot: int = 3000) -> Tuple[float, float]:
    if len(x) < 3:
        return float("nan"), float("nan")
    vals = []
    n = len(x)
    rng = np.random.default_rng(0)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        try:
            v = fn(x[idx], y[idx])
        except Exception:
            continue
        if np.isfinite(v):
            vals.append(v)
    if not vals:
        return float("nan"), float("nan")
    vals = np.sort(np.array(vals))
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return float(lo), float(hi)


def _sp(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    r, p = spearmanr(x, y)
    return float(r), float(p)


def _fmt_rp(r: float, p: float, lo: float, hi: float) -> str:
    return f"r={r:.3f} (p={p:.4f}, 95% CI [{lo:.3f}, {hi:.3f}])"


def analyze(results_dir: Path, bootstrap_iters: int) -> Dict[str, object]:
    equiv = pd.read_csv(results_dir / "equivalence_results.csv")
    judge = pd.read_csv(results_dir / "judge_results.csv")
    human = pd.read_csv(results_dir / "human_judgments.csv")

    equiv["proof_compiles"] = equiv["proof_compiles"].astype(bool)
    judge = judge.dropna(subset=["judge_score"]).copy()
    judge["judge_score"] = judge["judge_score"].astype(float)

    merged_hp = human.merge(equiv, on=["split", "problem_id", "agent"], how="inner")
    merged_hj = human.merge(judge, on=["split", "problem_id", "agent"], how="inner")
    merged_jp = judge.merge(equiv, on=["split", "problem_id", "agent"], how="inner")

    rows = []
    split_summary = {}

    for split in sorted(human["split"].unique()):
        hp = merged_hp[merged_hp["split"] == split]
        hj = merged_hj[merged_hj["split"] == split]
        jp = merged_jp[merged_jp["split"] == split]

        hp_x = hp["proof_compiles"].astype(int).to_numpy()
        hp_y = hp["human_mean"].to_numpy(dtype=float)
        r_hp, p_hp = pointbiserialr(hp_x.astype(int), hp_y)
        lo_hp, hi_hp = _bootstrap_ci(hp_x, hp_y, lambda a, b: pointbiserialr(a.astype(int), b).statistic, bootstrap_iters)

        hj_x = hj["human_mean"].to_numpy(dtype=float)
        hj_y = hj["judge_score"].to_numpy(dtype=float)
        r_hj, p_hj = _sp(hj_x, hj_y)
        lo_hj, hi_hj = _bootstrap_ci(hj_x, hj_y, lambda a, b: spearmanr(a, b).statistic, bootstrap_iters)
        mae_hj = float(np.mean(np.abs(hj_x - hj_y))) if len(hj_x) else float("nan")

        jp_x = jp["proof_compiles"].astype(int).to_numpy()
        jp_y = jp["judge_score"].to_numpy(dtype=float)
        r_jp, p_jp = pointbiserialr(jp_x.astype(int), jp_y)
        lo_jp, hi_jp = _bootstrap_ci(jp_x, jp_y, lambda a, b: pointbiserialr(a.astype(int), b).statistic, bootstrap_iters)

        high_human = hp["human_mean"] >= 3.0
        proves = hp["proof_compiles"]
        high_and_proves = int((high_human & proves).sum())
        high_total = int(high_human.sum())
        proves_total = int(proves.sum())

        pct_high_to_proof = (100.0 * high_and_proves / high_total) if high_total else float("nan")
        pct_proof_to_high = (100.0 * high_and_proves / proves_total) if proves_total else float("nan")

        row = {
            "split": split,
            "human_prover_r": float(r_hp),
            "human_prover_p": float(p_hp),
            "human_prover_ci_lo": lo_hp,
            "human_prover_ci_hi": hi_hp,
            "human_judge_r": float(r_hj),
            "human_judge_p": float(p_hj),
            "human_judge_ci_lo": lo_hj,
            "human_judge_ci_hi": hi_hj,
            "judge_prover_r": float(r_jp),
            "judge_prover_p": float(p_jp),
            "judge_prover_ci_lo": lo_jp,
            "judge_prover_ci_hi": hi_jp,
            "n": int(len(hp)),
            "human_judge_mae": mae_hj,
            "human_ge3_and_proof_count": high_and_proves,
            "human_ge3_count": high_total,
            "proof_count": proves_total,
            "pct_human_ge3_with_proof": pct_high_to_proof,
            "pct_proof_with_human_ge3": pct_proof_to_high,
        }
        rows.append(row)
        split_summary[split] = row

    pooled_x = merged_hj["human_mean"].to_numpy(dtype=float)
    pooled_y = merged_hj["judge_score"].to_numpy(dtype=float)
    pooled_r, pooled_p = _sp(pooled_x, pooled_y)
    pooled_lo, pooled_hi = _bootstrap_ci(pooled_x, pooled_y, lambda a, b: spearmanr(a, b).statistic, bootstrap_iters)

    per_split_df = pd.DataFrame(rows).sort_values("split")
    per_split_df.to_csv(results_dir / "per_split_correlations.csv", index=False)

    pooled = {
        "spearman_r": float(pooled_r),
        "p": float(pooled_p),
        "ci_lo": pooled_lo,
        "ci_hi": pooled_hi,
        "n": int(len(merged_hj)),
    }

    out = {"per_split": rows, "pooled_human_judge": pooled}
    (results_dir / "analysis_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    for split in sorted(human["split"].unique()):
        m = merged_hj[merged_hj["split"] == split].merge(
            equiv[["split", "problem_id", "agent", "proof_compiles"]],
            on=["split", "problem_id", "agent"],
            how="left",
        )
        plt.figure(figsize=(6, 5))
        for pc, c, lbl in [(True, "#1f77b4", "proof compiles"), (False, "#d62728", "proof fails")]:
            sub = m[m["proof_compiles"] == pc]
            if len(sub) == 0:
                continue
            plt.scatter(sub["human_mean"], sub["judge_score"], s=70, alpha=0.8, c=c, label=lbl)
        plt.xlabel("Human mean")
        plt.ylabel("Judge score")
        plt.title(f"{split.capitalize()}: Human vs Judge")
        plt.legend()
        plt.grid(alpha=0.25)
        plt.tight_layout()
        plt.savefig(results_dir / f"scatter_{split}.png", dpi=180)
        plt.close()

    lines = []
    lines.append("=== THREE-WAY VALIDATION SUMMARY ===")
    lines.append(f"{'Split':<12} {'Human↔Prover':<40} {'Human↔Judge':<40} {'Judge↔Prover':<40} {'n'}")
    lines.append("-" * 150)
    for r in rows:
        lines.append(
            f"{r['split']:<12} "
            f"{_fmt_rp(r['human_prover_r'], r['human_prover_p'], r['human_prover_ci_lo'], r['human_prover_ci_hi']):<40} "
            f"{_fmt_rp(r['human_judge_r'], r['human_judge_p'], r['human_judge_ci_lo'], r['human_judge_ci_hi']):<40} "
            f"{_fmt_rp(r['judge_prover_r'], r['judge_prover_p'], r['judge_prover_ci_lo'], r['judge_prover_ci_hi']):<40} "
            f"{r['n']}"
        )
    table_txt = "\n".join(lines)
    (results_dir / "three_way_table.txt").write_text(table_txt, encoding="utf-8")

    return {"per_split": split_summary, "pooled": pooled, "table_text": table_txt}


def write_markdown(results_dir: Path, summary: Dict[str, object]) -> None:
    ps = summary["per_split"]
    pooled = summary["pooled"]

    md = []
    md.append("# VeriBench Validation Summary")
    md.append("")
    md.append("## Per-Split Results")
    md.append("")
    for split in ["easy", "cs", "security"]:
        if split not in ps:
            continue
        r = ps[split]
        md.append(f"### {split.capitalize()}")
        md.append(f"- Human vs Prover (point-biserial): r={r['human_prover_r']:.3f}, p={r['human_prover_p']:.4f}, 95% CI [{r['human_prover_ci_lo']:.3f}, {r['human_prover_ci_hi']:.3f}], n={r['n']}")
        md.append(f"- Human vs Judge (Spearman): r={r['human_judge_r']:.3f}, p={r['human_judge_p']:.4f}, 95% CI [{r['human_judge_ci_lo']:.3f}, {r['human_judge_ci_hi']:.3f}], MAE={r['human_judge_mae']:.2f}")
        md.append(f"- Judge vs Prover (point-biserial): r={r['judge_prover_r']:.3f}, p={r['judge_prover_p']:.4f}, 95% CI [{r['judge_prover_ci_lo']:.3f}, {r['judge_prover_ci_hi']:.3f}]")
        md.append(f"- Human≥3 with proof: {r['human_ge3_and_proof_count']}/{r['human_ge3_count']} ({r['pct_human_ge3_with_proof']:.1f}%)")
        md.append(f"- Proof with Human≥3: {r['human_ge3_and_proof_count']}/{r['proof_count']} ({r['pct_proof_with_human_ge3']:.1f}%)")
        md.append("")

    md.append("## Pooled (All Splits)")
    md.append("")
    md.append(f"- Human vs Judge (Spearman): r={pooled['spearman_r']:.3f}, p={pooled['p']:.4f}, 95% CI [{pooled['ci_lo']:.3f}, {pooled['ci_hi']:.3f}], n={pooled['n']}")
    md.append("- Interpretation: pooled correlation may be inflated by between-split variance (easy vs security difficulty gap).")
    md.append("")
    md.append("## Three-Way Table")
    md.append("")
    md.append("```text")
    md.append(summary["table_text"])
    md.append("```")

    (results_dir / "results_summary.md").write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    args = parse_args()
    summary = analyze(args.results_dir, args.bootstrap_iters)
    write_markdown(args.results_dir, summary)
    print("Wrote per_split_correlations.csv, analysis_summary.json, three_way_table.txt, results_summary.md, and split scatter plots")


if __name__ == "__main__":
    main()
