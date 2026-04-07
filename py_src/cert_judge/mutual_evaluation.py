"""
Mutual Evaluation: P8 (Evaluator Replicability) and P9 (Rubric Specification Robustness).

P8 measures inter-rater reliability — whether independent evaluators applying the same
rubric produce consistent conclusions. It complements P4 (intra-rater reliability).

P9 measures whether the rubric's coding scheme produces structured, item-specific signal
rather than noise, using evaluation-welfare (TVD-MI on the response matrix).

Together P8 and P9 form a "meta-reliability" gate (ME factor) that multiplies
the base JTI_{1-7}, discounting trust when the evaluation *process* is unreliable.

Reference: Robertson & Koyejo (arXiv:2508.05469) for TVD-MI and mutual evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

from .hsj_scoring import _clip01, _safe_mean, _rankdata, _pearson_corr


# ---------------------------------------------------------------------------
# P8: Evaluator Replicability (Inter-Rater Reliability)
# ---------------------------------------------------------------------------

@dataclass
class P8Report:
    """Detailed report for P8 computation."""
    p8: float                                       # final score in [0,1]
    mean_pairwise_rho: float                        # raw mean Spearman rho in [-1,1]
    pairwise_rhos: List[Tuple[int, int, float]]     # (judge_i, judge_j, rho)
    conclusion_stability: float                     # fraction of items with unanimous bucket
    k_judges: int
    n_items: int


def _spearman_rho(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rank correlation in [-1,1]."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    x_vals = [float(v) for v in x]
    y_vals = [float(v) for v in y]
    if len(set(x_vals)) == 1 and len(set(y_vals)) == 1:
        return 1.0 if np.isclose(x_vals[0], y_vals[0]) else 0.0
    rx = _rankdata(x_vals)
    ry = _rankdata(y_vals)
    return _pearson_corr(rx, ry)


def compute_p8_evaluator_replicability(
    score_matrix: Sequence[Sequence[float]],
    bucketize_fn: Optional[object] = None,
    n_buckets: int = 3,
) -> P8Report:
    """
    P8 — Evaluator Replicability (Inter-Rater Reliability).

    Parameters
    ----------
    score_matrix : K x N matrix
        score_matrix[k][i] = score from judge k on item i.
        K >= 2 judges, N >= 2 items.
    bucketize_fn : optional callable(float) -> int
        Maps a score to a qualitative bucket index. If None, uses equal-width
        bucketing into n_buckets bins on [0,1].
    n_buckets : int
        Number of equal-width buckets when bucketize_fn is None.

    Returns
    -------
    P8Report with p8 = (mean_pairwise_rho + 1) / 2  in [0,1].
    """
    mat = np.asarray(score_matrix, dtype=float)
    if mat.ndim != 2:
        raise ValueError("score_matrix must be 2-D (K judges x N items)")
    k_judges, n_items = mat.shape
    if k_judges < 2:
        raise ValueError("Need at least 2 judges for P8 (got {})".format(k_judges))
    if n_items < 2:
        raise ValueError("Need at least 2 items for P8 (got {})".format(n_items))

    # --- Pairwise Spearman correlations ---
    pairwise_rhos: List[Tuple[int, int, float]] = []
    for i in range(k_judges):
        for j in range(i + 1, k_judges):
            rho = _spearman_rho(mat[i], mat[j])
            pairwise_rhos.append((i, j, rho))
    mean_rho = _safe_mean([r for _, _, r in pairwise_rhos])

    # --- Conclusion stability ---
    if bucketize_fn is None:
        def _default_bucket(score: float) -> int:
            s = _clip01(score)
            b = int(s * n_buckets)
            return min(b, n_buckets - 1)
        bucketize_fn = _default_bucket

    unanimous = 0
    for col in range(n_items):
        buckets = [bucketize_fn(mat[row, col]) for row in range(k_judges)]
        if len(set(buckets)) == 1:
            unanimous += 1
    conclusion_stability = unanimous / n_items

    p8 = _clip01((mean_rho + 1.0) / 2.0)

    return P8Report(
        p8=p8,
        mean_pairwise_rho=mean_rho,
        pairwise_rhos=pairwise_rhos,
        conclusion_stability=conclusion_stability,
        k_judges=k_judges,
        n_items=n_items,
    )


# ---------------------------------------------------------------------------
# P9: Rubric Specification Robustness (Evaluation-Welfare via TVD-MI)
# ---------------------------------------------------------------------------

@dataclass
class P9Report:
    """Detailed report for P9 computation."""
    p9: float                   # final score in [0,1]
    welfare_raw: float          # raw evaluation-welfare (TVD-MI on response matrix)
    tau: float                  # normalization threshold
    null_95th: float            # 95th percentile of permutation null
    n_items: int
    n_questions: int
    n_permutations: int


def _evaluation_welfare(response_matrix: np.ndarray) -> float:
    """
    Compute evaluation-welfare: TVD-MI between the true item-response distribution
    and the product-of-marginals (shuffled) distribution.

    Uses a leave-one-out nearest-neighbor classifier to estimate TVD lower bound.
    For each item's response vector, test whether the 1-NN (Hamming distance) in
    the remaining data is closer to genuine rows or to shuffled (marginal) rows.

    This follows the Robertson mutual evaluation protocol: high welfare means the
    coding scheme captures item-specific structure; low welfare means noise.
    """
    n_items, n_questions = response_matrix.shape
    if n_items < 3 or n_questions < 1:
        return 0.0

    # Generate marginal-shuffled rows (independently permute each column)
    rng = np.random.default_rng(42)
    shuffled = response_matrix.copy()
    for col in range(n_questions):
        rng.shuffle(shuffled[:, col])

    # Combined dataset: genuine (label=1) + shuffled (label=0)
    combined = np.vstack([response_matrix, shuffled])
    labels = np.array([1] * n_items + [0] * n_items)

    # Leave-one-out 1-NN classifier using Hamming distance
    correct_pos = 0  # correctly classified genuine rows
    correct_neg = 0  # correctly classified shuffled rows
    total_pos = n_items
    total_neg = n_items

    for i in range(len(combined)):
        row = combined[i]
        # Hamming distances to all other rows
        dists = np.sum(combined != row, axis=1).astype(float)
        dists[i] = np.inf  # exclude self
        nn_idx = int(np.argmin(dists))
        pred_label = labels[nn_idx]
        true_label = labels[i]
        if true_label == 1 and pred_label == 1:
            correct_pos += 1
        elif true_label == 0 and pred_label == 0:
            correct_neg += 1

    tpr = correct_pos / max(1, total_pos)
    tnr = correct_neg / max(1, total_neg)
    # Youden's J as TVD lower bound
    return max(0.0, tpr + tnr - 1.0)


def compute_p9_rubric_robustness(
    response_matrix: Sequence[Sequence[Union[int, float]]],
    n_permutations: int = 200,
    seed: int = 42,
) -> P9Report:
    """
    P9 — Rubric Specification Robustness (Evaluation-Welfare).

    Parameters
    ----------
    response_matrix : N x Q matrix
        response_matrix[i][q] = annotation for item i on coding question q.
        Values should be integer-coded categories (e.g., 0/1 for Y/N,
        0/1/2 for Y/N/Partial).
    n_permutations : int
        Number of permutation-null iterations for calibrating tau.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    P9Report with p9 = clip(welfare / tau, 0, 1).
    """
    mat = np.asarray(response_matrix, dtype=float)
    if mat.ndim != 2:
        raise ValueError("response_matrix must be 2-D (N items x Q questions)")
    n_items, n_questions = mat.shape
    if n_items < 3:
        raise ValueError("Need at least 3 items for P9 (got {})".format(n_items))
    if n_questions < 1:
        raise ValueError("Need at least 1 coding question for P9 (got {})".format(n_questions))

    # Compute welfare on the real response matrix
    welfare_raw = _evaluation_welfare(mat)

    # Permutation null: independently shuffle each question column to break
    # item-response structure while preserving per-question marginals.
    rng = np.random.default_rng(seed)
    null_welfares: List[float] = []
    for _ in range(n_permutations):
        perm_mat = mat.copy()
        for col in range(n_questions):
            rng.shuffle(perm_mat[:, col])
        null_welfares.append(_evaluation_welfare(perm_mat))

    null_95th = float(np.percentile(null_welfares, 95)) if null_welfares else 0.0
    # tau = 95th percentile of null, with a floor to avoid division by near-zero
    tau = max(null_95th, 0.01)

    p9 = _clip01(welfare_raw / tau)

    return P9Report(
        p9=p9,
        welfare_raw=welfare_raw,
        tau=tau,
        null_95th=null_95th,
        n_items=n_items,
        n_questions=n_questions,
        n_permutations=n_permutations,
    )


# ---------------------------------------------------------------------------
# ME Factor and JTI' integration (Option B from the plan)
# ---------------------------------------------------------------------------

def compute_me_factor(
    p8: float,
    p9: float,
    alpha: float = 0.5,
) -> float:
    """
    Mutual Evaluation factor: ME = alpha * P8 + (1 - alpha) * P9.

    This acts as a meta-reliability gate that multiplies the base JTI.
    """
    return _clip01(alpha * _clip01(p8) + (1.0 - alpha) * _clip01(p9))


def compute_jti_with_mutual_evaluation(
    jti_base: float,
    p8: float,
    p9: float,
    alpha_me: float = 0.5,
) -> float:
    """
    JTI' = JTI_{1-7} x ME_factor.

    Hierarchical integration (Option B): P1-P7 measure properties of a single
    judge-rubric pair; P8-P9 measure properties of the evaluation *process*.
    Multiplicative combination treats mutual evaluation as a gate.
    """
    me = compute_me_factor(p8, p9, alpha_me)
    return _clip01(_clip01(jti_base) * me)
