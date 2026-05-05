#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import Ridge
from sklearn.isotonic import IsotonicRegression


def ccc(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mx, my = x.mean(), y.mean()
    vx, vy = x.var(), y.var()
    cov = np.mean((x - mx) * (y - my))
    den = vx + vy + (mx - my) ** 2
    return float((2 * cov / den) if den > 0 else 0.0)


def metrics(yhat, y):
    return {
        "pearson_r": float(pearsonr(yhat, y).statistic),
        "spearman_rho": float(spearmanr(yhat, y).statistic),
        "kendall_tau": float(kendalltau(yhat, y).statistic),
        "ccc": ccc(yhat, y),
    }


def cohens_dz_from_paired_diff(diff: np.ndarray) -> float:
    diff = np.asarray(diff, dtype=float)
    if diff.size < 2:
        return float("nan")
    sd = float(np.std(diff, ddof=1))
    if sd == 0.0:
        return float("nan")
    return float(np.mean(diff) / sd)


def load_human(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, sep="\t")
    d["item_id"] = d["gold_file"].astype(str) + "::" + d["candidate_file"].astype(str)
    d["human"] = pd.to_numeric(d["human_score_0_5"], errors="coerce")
    return d[["item_id", "human"]].dropna()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail-rows", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--n-splits", type=int, default=5)
    args = ap.parse_args()

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.detail_rows)
    df = df[df["row_type"] == "human_eval_union"].copy()
    df = df[df["judge_id"].astype(str).str.startswith("gpt-5.3-codex|")].copy()
    df = df[~df["judge_id"].str.contains("BAD_")].copy()

    df["item_id"] = df["item_key"].astype(str)
    df["prompt"] = df["judge_id"].str.split("|", n=1).str[1]
    df["score"] = pd.to_numeric(df["score_mean"], errors="coerce")
    wide = df.pivot_table(index="item_id", columns="prompt", values="score", aggfunc="mean")
    wide = wide.dropna(axis=0, how="any").reset_index()

    # task group for leakage-safe split
    wide["task"] = wide["item_id"].str.split("::").str[0]

    pass_map = {
        "pass1": Path("experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv"),
        "pass2": Path("experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv"),
        "avg": Path("experiments/04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv"),
    }

    all_rows = []
    pred_rows = []
    effect_rows = []
    for pass_name, hp in pass_map.items():
        h = load_human(hp)
        m = wide.merge(h, on="item_id", how="inner").copy()

        feature_cols = [c for c in m.columns if c not in {"item_id", "task", "human"}]
        X = m[feature_cols].to_numpy(dtype=float)
        y = m["human"].to_numpy(dtype=float)
        groups = m["task"].to_numpy()

        # ensure splits <= groups
        n_groups = len(np.unique(groups))
        n_splits = min(args.n_splits, n_groups)
        gkf = GroupKFold(n_splits=n_splits)

        pred_ridge = np.zeros_like(y)
        pred_iso = np.zeros_like(y)
        pred_best_single = np.zeros_like(y)

        for tr, te in gkf.split(X, y, groups):
            Xtr, Xte = X[tr], X[te]
            ytr, yte = y[tr], y[te]

            # best single prompt selected on train only by Spearman
            train_df = pd.DataFrame(Xtr, columns=feature_cols)
            best_col = None
            best_r = -1e9
            for c in feature_cols:
                r = spearmanr(train_df[c].to_numpy(), ytr).statistic
                if np.isnan(r):
                    r = -1e9
                if r > best_r:
                    best_r = r
                    best_col = c
            pred_best_single[te] = pd.DataFrame(Xte, columns=feature_cols)[best_col].to_numpy()

            # stacked ridge
            ridge = Ridge(alpha=1.0)
            ridge.fit(Xtr, ytr)
            yr = ridge.predict(Xte)
            pred_ridge[te] = yr

            # isotonic on ridge output (train-only fit)
            iso = IsotonicRegression(out_of_bounds="clip")
            iso.fit(ridge.predict(Xtr), ytr)
            pred_iso[te] = iso.predict(yr)

        all_rows.append({"pass": pass_name, "model": "best_single_prompt_cv", **metrics(pred_best_single, y), "n": len(y)})
        all_rows.append({"pass": pass_name, "model": "stacked_ridge_cv", **metrics(pred_ridge, y), "n": len(y)})
        all_rows.append({"pass": pass_name, "model": "stacked_ridge_plus_isotonic_cv", **metrics(pred_iso, y), "n": len(y)})

        # Per-item predictions for auditability.
        pass_pred = pd.DataFrame(
            {
                "pass": pass_name,
                "item_id": m["item_id"].astype(str).to_numpy(),
                "task": m["task"].astype(str).to_numpy(),
                "human": y,
                "pred_best_single_prompt_cv": pred_best_single,
                "pred_stacked_ridge_cv": pred_ridge,
                "pred_stacked_ridge_plus_isotonic_cv": pred_iso,
            }
        )
        pred_rows.append(pass_pred)

        # Practical significance: paired effect sizes on absolute-error reduction.
        err_best = np.abs(pred_best_single - y)
        err_ridge = np.abs(pred_ridge - y)
        err_iso = np.abs(pred_iso - y)

        # Positive diff means model_a has lower error than model_b.
        diff_iso_vs_best = err_best - err_iso
        diff_iso_vs_ridge = err_ridge - err_iso

        effect_rows.append(
            {
                "pass": pass_name,
                "comparison": "stacked_ridge_plus_isotonic_cv vs best_single_prompt_cv",
                "n": int(len(y)),
                "mean_abs_err_model_a": float(np.mean(err_iso)),
                "mean_abs_err_model_b": float(np.mean(err_best)),
                "mean_abs_err_reduction_a_minus_b": float(np.mean(diff_iso_vs_best)),
                "cohens_dz_abs_err_reduction": cohens_dz_from_paired_diff(diff_iso_vs_best),
            }
        )
        effect_rows.append(
            {
                "pass": pass_name,
                "comparison": "stacked_ridge_plus_isotonic_cv vs stacked_ridge_cv",
                "n": int(len(y)),
                "mean_abs_err_model_a": float(np.mean(err_iso)),
                "mean_abs_err_model_b": float(np.mean(err_ridge)),
                "mean_abs_err_reduction_a_minus_b": float(np.mean(diff_iso_vs_ridge)),
                "cohens_dz_abs_err_reduction": cohens_dz_from_paired_diff(diff_iso_vs_ridge),
            }
        )

    out_df = pd.DataFrame(all_rows)
    out_csv = out / "exp31_stacked_calibration_results.csv"
    out_df.to_csv(out_csv, index=False)
    pd.concat(pred_rows, ignore_index=True).to_csv(out / "exp31_stacked_calibration_predictions.csv", index=False)
    pd.DataFrame(effect_rows).to_csv(out / "exp31_stacked_calibration_effect_sizes.csv", index=False)
    print(out_df.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    print(f"\nWrote {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
