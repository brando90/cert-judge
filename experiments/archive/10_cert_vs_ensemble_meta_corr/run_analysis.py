#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np
from scipy.stats import pearsonr, spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Folder 10: cert-v1 vs ensemble meta-correlation")
    p.add_argument("--exp06-summary", type=Path, required=True)
    p.add_argument("--exp09-summary", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--label", type=str, default="median")
    return p.parse_args()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ols_fit(y: np.ndarray, X: np.ndarray) -> Dict[str, object]:
    # X already includes intercept as first column.
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    resid = y - yhat
    n, p = X.shape
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - y.mean()) ** 2))
    r2 = float("nan") if sst <= 0 else 1.0 - sse / sst

    dof = max(n - p, 1)
    sigma2 = sse / dof
    xtx_inv = np.linalg.pinv(X.T @ X)
    cov = sigma2 * xtx_inv
    se = np.sqrt(np.diag(cov))

    return {
        "beta": beta.tolist(),
        "se": se.tolist(),
        "r2": r2,
        "n": int(n),
        "p": int(p),
    }


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    exp06 = load_json(args.exp06_summary)
    exp09 = load_json(args.exp09_summary)

    cert_v1 = {}
    for jr in exp06.get("judge_rows", []):
        cert_v1[jr["judge_id"]] = float(jr.get("cert_index", float("nan")))

    comparison = [r for r in exp09.get("comparison_rows", []) if r.get("label_set") == "union_avg"]
    rho_by_method = {r["method"]: float(r.get("spearman_r", float("nan"))) for r in comparison}

    all_llm = exp09.get("selection", {}).get("all_llm_judges", [])
    cert_llm = exp09.get("selection", {}).get("certified_llm_judges", [])

    # Build methods table: all single llm judges + ensemble methods from exp09.
    rows: List[dict] = []
    for j in all_llm:
        if j in cert_v1:
            # get single-judge human corr from exp06 summary (avg/union proxy)
            hr = float("nan")
            for jr in exp06.get("judge_rows", []):
                if jr.get("judge_id") == j:
                    # On these artifacts, avg field is available and aligned with union labels.
                    hr = float(jr.get("human_spearman_r_avg", float("nan")))
                    break
            rows.append({
                "method_id": j,
                "method_type": "single",
                "is_ensemble": 0,
                "cert_v1": cert_v1[j],
                "rho_human": hr,
            })

    # Ensemble cert-v1 definitions.
    w_all = np.array([max(cert_v1[j], 0.0) for j in all_llm], dtype=float)
    w_cert = np.array([max(cert_v1[j], 0.0) for j in cert_llm], dtype=float)
    all_vals = np.array([cert_v1[j] for j in all_llm], dtype=float) if all_llm else np.array([])
    cert_vals = np.array([cert_v1[j] for j in cert_llm], dtype=float) if cert_llm else np.array([])

    ens_cert = {
        "ens_all_llm_uniform": float(np.mean(all_vals)) if all_vals.size else float("nan"),
        "ens_certified_uniform": float(np.mean(cert_vals)) if cert_vals.size else float("nan"),
        "ens_all_llm_certv2_weighted": float(np.dot(all_vals, w_all) / w_all.sum()) if w_all.sum() > 0 else (float(np.mean(all_vals)) if all_vals.size else float("nan")),
        "ens_certified_certv2_weighted": float(np.dot(cert_vals, w_cert) / w_cert.sum()) if w_cert.sum() > 0 else (float(np.mean(cert_vals)) if cert_vals.size else float("nan")),
    }

    for m, c in ens_cert.items():
        if m in rho_by_method:
            rows.append({
                "method_id": m,
                "method_type": "ensemble",
                "is_ensemble": 1,
                "cert_v1": c,
                "rho_human": rho_by_method[m],
            })

    # Keep finite rows only.
    rows = [r for r in rows if math.isfinite(r["cert_v1"]) and math.isfinite(r["rho_human"])]

    x = np.array([r["cert_v1"] for r in rows], dtype=float)
    y = np.array([r["rho_human"] for r in rows], dtype=float)
    z = np.array([r["is_ensemble"] for r in rows], dtype=float)

    sp = float(spearmanr(x, y).statistic) if len(rows) >= 3 else float("nan")
    pr = float(pearsonr(x, y).statistic) if len(rows) >= 3 else float("nan")

    # Model A: y ~ 1 + cert
    XA = np.column_stack([np.ones(len(rows)), x]) if len(rows) else np.zeros((0, 2))
    fitA = ols_fit(y, XA) if len(rows) >= 3 else None

    # Model B: y ~ 1 + cert + is_ensemble
    XB = np.column_stack([np.ones(len(rows)), x, z]) if len(rows) else np.zeros((0, 3))
    fitB = ols_fit(y, XB) if len(rows) >= 4 else None

    with (args.out_dir / "methods_table.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["method_id", "method_type", "is_ensemble", "cert_v1", "rho_human"])
        w.writeheader()
        w.writerows(rows)

    summary = {
        "experiment": "10_cert_vs_ensemble_meta_corr",
        "label": args.label,
        "inputs": {
            "exp06_summary": str(args.exp06_summary),
            "exp09_summary": str(args.exp09_summary),
        },
        "n_methods": len(rows),
        "corr": {
            "spearman_cert_v1_vs_rho_human": sp,
            "pearson_cert_v1_vs_rho_human": pr,
        },
        "model_a_rho_on_cert": fitA,
        "model_b_rho_on_cert_plus_ensemble": fitB,
    }

    with (args.out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    lines = []
    lines.append(f"# Folder 10 Report ({args.label})")
    lines.append("")
    lines.append(f"- n_methods: {len(rows)}")
    lines.append(f"- Spearman(cert_v1, rho_human): {sp:.3f}")
    lines.append(f"- Pearson(cert_v1, rho_human): {pr:.3f}")
    lines.append("")
    if fitA is not None:
        b = fitA["beta"]
        se = fitA["se"]
        lines.append("## Model A: rho ~ 1 + cert_v1")
        lines.append(f"- beta_intercept = {b[0]:.4f} (se {se[0]:.4f})")
        lines.append(f"- beta_cert_v1 = {b[1]:.4f} (se {se[1]:.4f})")
        lines.append(f"- R^2 = {fitA['r2']:.4f}")
        lines.append("")
    if fitB is not None:
        b = fitB["beta"]
        se = fitB["se"]
        lines.append("## Model B: rho ~ 1 + cert_v1 + is_ensemble")
        lines.append(f"- beta_intercept = {b[0]:.4f} (se {se[0]:.4f})")
        lines.append(f"- beta_cert_v1 = {b[1]:.4f} (se {se[1]:.4f})")
        lines.append(f"- beta_is_ensemble = {b[2]:.4f} (se {se[2]:.4f})")
        lines.append(f"- R^2 = {fitB['r2']:.4f}")

    with (args.out_dir / "report.md").open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"done: {args.out_dir}")


if __name__ == "__main__":
    main()
