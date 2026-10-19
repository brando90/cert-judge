#!/usr/bin/env python3
"""TLDR: Frozen O1, O2 and O3 calculations for the cert-judge rating pool. No model calls.
The rank statistics are experiment 39's analysis_lib. The accept threshold is read from the freeze file."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = next(q for q in HERE.parents if (q / "py_src" / "cert_judge").is_dir())
E39 = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts/analysis_lib.py"
FREEZE = REPO / "experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/FREEZE_10-18-2026.json"

GATE_RHO = 0.45
GATE_P = 0.05
GATE_LO = 0.20
MISSING_LIMIT = 14
WIDTH_LIMIT = 1.2
DECLARED = 51


def load_analysis():
    spec = importlib.util.spec_from_file_location("e39_analysis_lib", E39)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def frozen_tau() -> float:
    return float(json.loads(FREEZE.read_text())["accept_threshold"]["tau"])


def o1_gate(screen, criterion, n_declared=DECLARED, draws=10000, seed=48):
    """Reading for the outer association. screen and criterion are parallel lists; None is missing."""
    A = load_analysis()
    pairs = [(float(a), float(b)) for a, b in zip(screen, criterion) if a is not None and b is not None]
    missing = n_declared - len(pairs)
    base = {"n_declared": n_declared, "n_computable": len(pairs), "n_missing": missing,
            "spearman": None, "kendall": None, "pearson": None, "ci": None, "permutation_p": None}
    if missing > MISSING_LIMIT:
        base["reading"] = "INCONCLUSIVE"
        base["reason"] = "more than 14 of the declared units lack a screen or a criterion"
        return base
    if len(pairs) < A.MIN_UNITS:
        base["reading"] = "INCONCLUSIVE"
        base["reason"] = "fewer than 8 computable units"
        return base
    x = [a for a, _ in pairs]
    y = [b for _, b in pairs]
    rho, tau, r = A.spearman(x, y), A.kendall(x, y), A.pearson(x, y)
    ci = A.bootstrap_ci(x, y, A.spearman, draws, seed)
    p = A.permutation_p(x, y, A.spearman, draws, seed)
    base.update(spearman=rho, kendall=tau, pearson=r, ci=ci, permutation_p=p)
    width = None if ci["lo"] is None or ci["hi"] is None else ci["hi"] - ci["lo"]
    if width is not None and width > WIDTH_LIMIT:
        base["reading"] = "INCONCLUSIVE"
        base["reason"] = "bootstrap interval wider than 1.2"
        return base
    passed = rho is not None and rho >= GATE_RHO and p is not None and p < GATE_P and ci["lo"] is not None and ci["lo"] > GATE_LO
    base["reading"] = "PASS" if passed else "FAIL"
    base["reason"] = "all three gates hold" if passed else "a computable association missed at least one gate"
    return base


def absolute_agreement(judge, human):
    """One judge against one human target. Bias is judge minus human."""
    A = load_analysis()
    pairs = [(float(a), float(b)) for a, b in zip(judge, human) if a is not None and b is not None]
    n = len(pairs)
    if n < 2:
        return {"n": n, "spearman": None, "mae": None, "bias": None, "judge_mean": None, "human_mean": None,
                "icc_c1": None, "icc_a1": None}
    j = np.array([a for a, _ in pairs])
    h = np.array([b for _, b in pairs])
    mae = float(np.mean(np.abs(j - h)))
    bias = float(np.mean(j - h))
    icc_c, icc_a = icc_two_column(j, h)
    return {"n": n, "spearman": A.spearman(j.tolist(), h.tolist()), "mae": mae, "bias": bias,
            "judge_mean": float(j.mean()), "human_mean": float(h.mean()), "icc_c1": icc_c, "icc_a1": icc_a}


def icc_two_column(x, y):
    """ICC(C,1) and ICC(A,1) for two columns and n rows. Shrout-Fleiss two-way formulas."""
    m = np.column_stack([np.asarray(x, dtype=float), np.asarray(y, dtype=float)])
    n, k = m.shape
    grand = m.mean()
    row = m.mean(axis=1)
    col = m.mean(axis=0)
    msr = k * np.sum((row - grand) ** 2) / (n - 1)
    msc = n * np.sum((col - grand) ** 2) / (k - 1)
    sse = np.sum((m - row[:, None] - col[None, :] + grand) ** 2)
    mse = sse / ((n - 1) * (k - 1))
    icc_c = (msr - mse) / (msr + (k - 1) * mse)
    icc_a = (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)
    return float(icc_c), float(icc_a)


def meets_human_gate(criterion, lower_bound) -> bool:
    return criterion is not None and lower_bound is not None and criterion >= GATE_RHO and lower_bound > GATE_LO


def false_acceptance(screen, meets, tau):
    """Among units with a screen at or above tau, the share that fail the human gate.
    Base rate is that share among every unit with a known gate."""
    rows = [(s, m) for s, m in zip(screen, meets) if s is not None and m is not None]
    accepted = [m for s, m in rows if s >= tau]
    if not rows or not accepted:
        return {"n": len(rows), "n_accepted": len(accepted), "false_acceptance": None, "base_rate": None}
    fa = 1.0 - sum(accepted) / len(accepted)
    base = 1.0 - sum(m for _, m in rows) / len(rows)
    return {"n": len(rows), "n_accepted": len(accepted), "false_acceptance": fa, "base_rate": base,
            "difference_base_minus_accepted": base - fa}


def finite(v):
    return v is not None and isinstance(v, (int, float)) and math.isfinite(v)
