# -*- coding: utf-8 -*-
# tvd_mi_tools.py
# ------------------------------------------------------------------
# Implementations inspired by Robertson & Koyejo (2025) "Let's Measure
# Information Step-by-Step: LLM-Based Evaluation Beyond Vibes".
#
# This module provides:
# 1) TVD–MI lower-bound estimation via a categorical critic:
#       I_TVD >= TPR + TNR - 1  (Youden's J)  [Eq. (3)–(5)]
# 2) Item-level AUC utilities for decomposability tests.
# 3) κ (Cohen's kappa) ↔ TVD relationships (Appendix F.1).
# 4) Tamper-suite reporting for robustness experiments (format/padding/
#    case-flip/pattern), reporting score inflation and discrimination drops.
# 5) Optional "effective rank" computation to study the inverted‑U
#    phenomenon relating mechanism performance to information structure.
#
# References: see paper sections 3.4, 5.2, Tables 3–5, and Appendix F.1–F.2.
# CITATION HANDLE FOR PAPER (in-chat): fileciteturn2file0
#
# NOTE: This file is self-contained (numpy/scipy optional). It expects that
# the *categorical critic outputs* already exist (e.g., from an LLM calling
# convention). We map critic labels to accept/reject and compute TPR/TNR
# against pair ground-truth (same-source vs different-source).

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Literal, Mapping, Optional, Sequence, Tuple, Union
import math
import numpy as np


CriticLabel = Literal["Significant Gain", "Little Gain", "No Gain"]
# Map critic labels to acceptance of "same-source" hypothesis A (paper Sec. 3.4)
DEFAULT_ACCEPT_SET = {"Significant Gain"}


@dataclass
class TVDMIReport:
    tpr: float
    tnr: float
    youdens_j: float       # J = TPR + TNR - 1  (equals TVD lower bound)
    tvd_lower_bound: float # alias of J
    n_pos: int
    n_neg: int


def tvd_mi_from_critic(
    y_true_same_source: Sequence[bool],
    y_pred_labels: Sequence[CriticLabel],
    accept_set: Optional[Iterable[str]] = None,
) -> TVDMIReport:
    """
    Compute TVD–MI lower bound via type-based test r on pair labels.
    Implements Eq. (3)-(5): I_TVD >= TPR + TNR - 1 = Youden's J.
    See: Sec. 3.4 and Appendix F.1 of the paper. fileciteturn2file0

    Parameters
    ----------
    y_true_same_source : sequence of bool
        Ground truth per pair: True if the two responses are from the same source (P+),
        False if independently sourced (P-).
    y_pred_labels : sequence of {"Significant Gain","Little Gain","No Gain"}
        Critic outputs. We "accept" (same-source) when label ∈ accept_set.
    accept_set : optional iterable of labels to accept; default = {"Significant Gain"}.

    Returns
    -------
    TVDMIReport with TPR, TNR, J (Youden's J), and counts.
    """
    if accept_set is None:
        accept_set = DEFAULT_ACCEPT_SET

    y_true = np.asarray(y_true_same_source, dtype=bool)
    y_pred_accept = np.array([lbl in accept_set for lbl in y_pred_labels], dtype=bool)

    pos = y_true.sum()
    neg = (~y_true).sum()
    if pos == 0 or neg == 0:
        raise ValueError("y_true must contain both positive (same-source) and negative (independent) pairs.")

    # TPR: accept when truly same-source
    tpr = (y_pred_accept & y_true).sum() / pos
    # TNR: reject when truly independent
    tnr = ((~y_pred_accept) & (~y_true)).sum() / neg

    j = tpr + tnr - 1.0
    return TVDMIReport(tpr=float(tpr), tnr=float(tnr), youdens_j=float(j), tvd_lower_bound=float(j),
                       n_pos=int(pos), n_neg=int(neg))


# ------------------------------------------------------------------
# Item-level AUC utilities (Sec. 5.2). We compute AUC between classes
# of pairs per item, then macro-average across items. Critic scores
# can be any real-valued scalar (e.g., mapped from labels).
# ------------------------------------------------------------------

def _auc_binary(scores_pos: np.ndarray, scores_neg: np.ndarray) -> float:
    """
    Classic AUC = P(score_pos > score_neg) + 0.5*P(=). Stable and fast.
    """
    a = np.asarray(scores_pos, dtype=float).reshape(-1, 1)
    b = np.asarray(scores_neg, dtype=float).reshape(1, -1)
    diffs = a - b
    greater = (diffs > 0).sum()
    ties = (diffs == 0).sum()
    total = diffs.size
    if total == 0:
        return 0.5
    return (greater + 0.5 * ties) / total


def per_item_auc_macro(
    item_ids: Sequence[Union[str, int]],
    pair_scores: Sequence[float],
    pair_class: Sequence[int],
) -> Tuple[float, List[Tuple[Union[str, int], float]]]:
    """
    Compute per-item AUCs and macro-average across items.
    - pair_class: 1 for positive (e.g., Faithful–Faithful), 0 for negative (e.g., Faithful–Problematic).
    - pair_scores: critic scores per pair (e.g., mapped label score or calibrated TVD-MI evidence).
    Returns (macro_auc, per_item_list).

    Mirrors Sec. 5.2 item-level AUC analysis. fileciteturn2file0
    """
    item_ids = np.asarray(item_ids)
    scores = np.asarray(pair_scores, dtype=float)
    classes = np.asarray(pair_class, dtype=int)

    aucs: List[Tuple[Union[str, int], float]] = []
    for iid in np.unique(item_ids):
        mask = (item_ids == iid)
        s = scores[mask]
        c = classes[mask]
        if (c == 1).sum() == 0 or (c == 0).sum() == 0:
            continue
        auc = _auc_binary(s[c == 1], s[c == 0])
        aucs.append((iid, float(auc)))
    if not aucs:
        return 0.5, []
    macro = float(np.mean([a for _, a in aucs]))
    return macro, aucs


# ------------------------------------------------------------------
# Kappa ↔ TVD relationships (Appendix F.1).  κ ≤ 2*TVD / (1 - p_e).
# We also provide lower bounds and helper conversions to/from Youden's J.
# ------------------------------------------------------------------

def kappa_upper_bound_from_tvd(tvd: float, p_e: float) -> float:
    """
    Given TVD(P, P_X P_Y) and chance agreement p_e, return κ upper bound:
        κ ≤ 2*TVD / (1 - p_e)
    See Appendix F.1. fileciteturn2file0
    """
    if not (0.0 <= tvd <= 1.0):
        raise ValueError("tvd must be in [0,1]")
    if not (0.0 <= p_e < 1.0):
        raise ValueError("p_e must be in [0,1)")
    return min(1.0, (2.0 * tvd) / (1.0 - p_e + 1e-12))


def tvd_lower_bound_from_kappa(kappa: float, p_e: float) -> float:
    """
    From Appendix F.1: TVD ≥ 0.5 * κ * (1 - p_e).
    """
    if not (-1.0 <= kappa <= 1.0):
        raise ValueError("kappa must be in [-1,1]")
    if not (0.0 <= p_e <= 1.0):
        raise ValueError("p_e must be in [0,1]")
    return max(0.0, 0.5 * kappa * (1.0 - p_e))


def j_from_auc(auc: float) -> float:
    """
    Youden's J = 2*(AUC - 0.5) for symmetric ROC (Appendix F.1). fileciteturn2file0
    """
    return 2.0 * (auc - 0.5)


# ------------------------------------------------------------------
# Tamper-suite reporting (Sec. 5.3, Table 4–5). We compute score
# inflation and discrimination degradation for multiple transformations.
# ------------------------------------------------------------------

@dataclass
class TamperResult:
    score_delta_mean: float
    auc_before: float
    auc_after: float
    auc_delta: float


def tamper_suite_report(
    base_scores: Sequence[float],
    base_labels_pos1_neg0: Sequence[int],
    transformed: Mapping[str, Sequence[float]],
) -> Mapping[str, TamperResult]:
    """
    Given baseline pair scores and class labels (1=positive, 0=negative), and
    a dict of transformed scores {name: scores}, compute for each transform:
      - mean score delta
      - AUC before/after and delta.
    This mirrors the reporting style of Table 4–5 (Sec. 5.3). fileciteturn2file0
    """
    base_scores = np.asarray(base_scores, dtype=float)
    y = np.asarray(base_labels_pos1_neg0, dtype=int)
    auc_before = _auc_binary(base_scores[y == 1], base_scores[y == 0])

    out = {}
    for name, sc in transformed.items():
        sc = np.asarray(sc, dtype=float)
        if sc.shape != base_scores.shape:
            raise ValueError(f"Shape mismatch for transform '{name}'.")
        delta = float(np.mean(sc - base_scores))
        auc_after = _auc_binary(sc[y == 1], sc[y == 0])
        out[name] = TamperResult(score_delta_mean=delta, auc_before=float(auc_before),
                                 auc_after=float(auc_after), auc_delta=float(auc_after - auc_before))
    return out


# ------------------------------------------------------------------
# Optional: Effective rank (information structure) to study inverted‑U
# performance vs. structure (Appendix B.1, Fig. 2). This does not compute
# performance; it gives the structural descriptor (effective rank).
# ------------------------------------------------------------------

def effective_rank(matrix: np.ndarray, eps: float = 1e-12) -> float:
    """
    Effective rank of a matrix via entropy of singular values:
       r_eff = exp( H(p) ), where p_i = s_i / sum_j s_j (s_i singular values).
    r_eff ∈ [1, min(n_rows, n_cols)].
    Useful to study inverted‑U trend vs. mechanism performance. fileciteturn2file0
    """
    # Use singular values of |matrix|; works for non-square.
    s = np.linalg.svd(matrix, compute_uv=False)
    s = np.maximum(s, 0.0)
    s_sum = s.sum()
    if s_sum <= eps:
        return 1.0
    p = s / s_sum
    h = -(p * np.log(p + eps)).sum()
    return float(np.exp(h))


# -------------------- Tiny demo (synthetic) --------------------

if __name__ == "__main__":
    # Synthetic critic outputs for 100 pairs (50 same-source, 50 different).
    rng = np.random.default_rng(7)
    y_true = np.array([True]*50 + [False]*50)
    # Simulate a decent critic
    labels = []
    for t in y_true:
        if t:
            labels.append(rng.choice(["Significant Gain","Little Gain","No Gain"], p=[0.75,0.20,0.05]))
        else:
            labels.append(rng.choice(["Significant Gain","Little Gain","No Gain"], p=[0.10,0.25,0.65]))

    rep = tvd_mi_from_critic(y_true, labels)
    print("TVD-MI lower bound (Youden's J):", rep.tvd_lower_bound)

    # Simulate item-level AUC: suppose we have per-item pair scores
    item_ids = np.repeat(np.arange(10), 10)         # 10 items, 10 pairs each
    pair_scores = rng.normal(loc=0.6, scale=0.15, size=100)
    pair_class = np.array([1,0]*50)                 # toy alternating labels
    macro_auc, per_item = per_item_auc_macro(item_ids, pair_scores, pair_class)
    print("Macro AUC:", macro_auc)

    # Tamper example: add padding noise
    transformed = {
        "padding": pair_scores + rng.normal(0.02, 0.01, size=100),
        "caseflip": pair_scores - rng.normal(0.03, 0.01, size=100),
    }
    tamper = tamper_suite_report(pair_scores, pair_class, transformed)
    for k, v in tamper.items():
        print(k, v)

