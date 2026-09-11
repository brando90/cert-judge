#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Exp28: variance-aware trust index using C_f, Var(Corr), Var(Scores)."
    )
    p.add_argument("--exp16-summary", type=Path, required=True)
    p.add_argument("--detail-rows", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--repeat-agg", choices=["mean", "median"], default="median")
    p.add_argument("--w-corr", type=float, default=1.0 / 3.0)
    p.add_argument("--w-vcorr", type=float, default=1.0 / 3.0)
    p.add_argument("--w-vscore", type=float, default=1.0 / 3.0)
    p.add_argument("--eps", type=float, default=1e-6)
    return p.parse_args()


def _agg(vals: np.ndarray, mode: str) -> float:
    return float(np.mean(vals) if mode == "mean" else np.median(vals))


def _load_detail_rows(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _parse_bug_item_key(item_key: str) -> Tuple[str, int]:
    # format: "<problem>::L<k>"
    left, right = item_key.split("::")
    if not right.upper().startswith("L"):
        raise ValueError(f"Unexpected bug item_key format: {item_key}")
    return left, int(right[1:])


def _norm_01(x: np.ndarray) -> np.ndarray:
    lo = float(np.min(x))
    hi = float(np.max(x))
    if hi <= lo + 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    exp16 = json.loads(args.exp16_summary.read_text(encoding="utf-8"))
    rows = exp16["judge_rows"]
    judge_ids = [r["judge_id"] for r in rows]
    human = np.asarray([float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float)

    detail = _load_detail_rows(args.detail_rows)
    # judge -> file -> level -> (robust_score, repeat_var)
    bug_map: Dict[str, Dict[str, Dict[int, Tuple[float, float]]]] = {}
    for r in detail:
        if r["row_type"] != "property_bug":
            continue
        jid = r["judge_id"]
        file_id, lvl = _parse_bug_item_key(r["item_key"])
        rep = np.asarray(json.loads(r["repeat_scores"]), dtype=float)
        robust = _agg(rep, args.repeat_agg)
        rep_var = float(np.var(rep))
        bug_map.setdefault(jid, {}).setdefault(file_id, {})[lvl] = (robust, rep_var)

    cf_list: List[float] = []
    vf_list: List[float] = []
    vs_list: List[float] = []
    n_files_list: List[int] = []

    for jid in judge_ids:
        by_file = bug_map.get(jid, {})
        corr_vals: List[float] = []
        score_vars: List[float] = []
        for _, ladder in by_file.items():
            lvls = sorted(ladder.keys())
            if len(lvls) < 3:
                continue
            xs = np.asarray(lvls, dtype=float)
            ys = np.asarray([ladder[l][0] for l in lvls], dtype=float)
            r_sp = float(spearmanr(xs, ys).statistic)
            if not math.isfinite(r_sp):
                continue
            # convert to higher-better monotonicity score in [0,1]
            corr_vals.append(float(np.clip((-r_sp + 1.0) / 2.0, 0.0, 1.0)))
            for l in lvls:
                score_vars.append(float(ladder[l][1]))

        if len(corr_vals) == 0:
            cf = 0.0
            vf = 1.0
        else:
            cf = float(np.mean(corr_vals))
            vf = float(np.var(corr_vals))
        if len(score_vars) == 0:
            vs = 1.0
        else:
            vs = float(np.mean(score_vars))

        cf_list.append(cf)
        vf_list.append(vf)
        vs_list.append(vs)
        n_files_list.append(len(corr_vals))

    cf = np.asarray(cf_list, dtype=float)
    vf = np.asarray(vf_list, dtype=float)
    vs = np.asarray(vs_list, dtype=float)

    vf_n = _norm_01(vf)
    vs_n = _norm_01(vs)
    s_vf = 1.0 - vf_n
    s_vs = 1.0 - vs_n

    ti = np.exp(
        args.w_corr * np.log(np.clip(cf, args.eps, 1.0))
        + args.w_vcorr * np.log(np.clip(s_vf, args.eps, 1.0))
        + args.w_vscore * np.log(np.clip(s_vs, args.eps, 1.0))
    )
    rho_ti = float(spearmanr(ti, human).statistic)
    rho_cf = float(spearmanr(cf, human).statistic)
    rho_vf = float(spearmanr(vf, human).statistic)
    rho_vs = float(spearmanr(vs, human).statistic)

    # CSV: per judge
    out_rows = []
    for i, jid in enumerate(judge_ids):
        out_rows.append(
            {
                "judge_id": jid,
                "human_spearman": float(human[i]),
                "C_f_mean": float(cf[i]),
                "VarCorr_V_f": float(vf[i]),
                "VarScore_V_s": float(vs[i]),
                "VarCorr_norm": float(vf_n[i]),
                "VarScore_norm": float(vs_n[i]),
                "VarCorr_stability_1_minus": float(s_vf[i]),
                "VarScore_stability_1_minus": float(s_vs[i]),
                "TI_variance_aware": float(ti[i]),
                "n_files_with_corr": int(n_files_list[i]),
            }
        )

    with (args.out_dir / "judge_trust_vector.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    # Aggregate metrics
    per_prop = [
        {"metric": "C_f_mean", "mean": float(np.mean(cf)), "std": float(np.std(cf))},
        {"metric": "VarCorr_V_f", "mean": float(np.mean(vf)), "std": float(np.std(vf))},
        {"metric": "VarScore_V_s", "mean": float(np.mean(vs)), "std": float(np.std(vs))},
    ]
    with (args.out_dir / "per_property_stats.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "mean", "std"])
        w.writeheader()
        w.writerows(per_prop)

    # Plots
    def _scatter(x: np.ndarray, y: np.ndarray, title: str, xlabel: str, out_name: str) -> None:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.scatter(x, y, s=60)
        for i, jid in enumerate(judge_ids):
            ax.annotate(jid, (x[i], y[i]), fontsize=7, alpha=0.75, xytext=(3, 3), textcoords="offset points")
        if len(x) >= 2 and float(np.std(x)) > 1e-12:
            m, b = np.polyfit(x, y, 1)
            xs = np.linspace(float(np.min(x)), float(np.max(x)), 100)
            ax.plot(xs, m * xs + b, "r--", alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(f"Human Spearman ({args.label_set})")
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(args.out_dir / out_name, dpi=200)
        plt.close(fig)

    _scatter(vf, human, f"Var(Corr) vs Human (rho={rho_vf:.3f})", "Var(Corr) across files", "fig_varcorr_vs_human.png")
    _scatter(vs, human, f"Var(Scores) vs Human (rho={rho_vs:.3f})", "Mean repeat-score variance", "fig_varscore_vs_human.png")
    _scatter(ti, human, f"Variance-aware Trust vs Human (rho={rho_ti:.3f})", "TI_var", "fig_trust_index_vs_human.png")

    summary = {
        "experiment": "exp28_variance_aware_trust_index",
        "label_set": args.label_set,
        "inputs": {"exp16_summary": str(args.exp16_summary), "detail_rows": str(args.detail_rows)},
        "weights": {"w_corr": args.w_corr, "w_vcorr": args.w_vcorr, "w_vscore": args.w_vscore},
        "correlations": {
            "rho_TI_vs_human": rho_ti,
            "rho_Cf_vs_human": rho_cf,
            "rho_VarCorr_vs_human": rho_vf,
            "rho_VarScore_vs_human": rho_vs,
        },
        "means": {
            "C_f_mean_across_judges": float(np.mean(cf)),
            "VarCorr_mean_across_judges": float(np.mean(vf)),
            "VarScore_mean_across_judges": float(np.mean(vs)),
        },
        "outputs": {
            "judge_trust_vector_csv": str(args.out_dir / "judge_trust_vector.csv"),
            "per_property_stats_csv": str(args.out_dir / "per_property_stats.csv"),
            "fig_varcorr_vs_human": str(args.out_dir / "fig_varcorr_vs_human.png"),
            "fig_varscore_vs_human": str(args.out_dir / "fig_varscore_vs_human.png"),
            "fig_trust_index_vs_human": str(args.out_dir / "fig_trust_index_vs_human.png"),
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

