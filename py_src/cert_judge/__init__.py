"""
cert_judge: Core scoring utilities for certifying and scoring LLM judges.

Exports
    - HSJInputs, IsotonicCalibrator
    - compute_p1_identity, compute_p2_or_p3_ordering_auc, compute_p4_stability, compute_jti
    - fit_isotonic_calibrator, compute_hsj_scores, compute_alpha
    - efg_judge, EFGResult (Zhang et al. arXiv:2506.10903 baseline)
"""

from .hsj_scoring import (
    HSJInputs,
    IsotonicCalibrator,
    compute_p1_identity,
    compute_p2_or_p3_ordering_auc,
    compute_p4_stability,
    compute_jti,
    fit_isotonic_calibrator,
    compute_hsj_scores,
    compute_alpha,
)

from .efg_judge import (
    efg_judge,
    EFGResult,
)

__all__ = [
    "HSJInputs",
    "IsotonicCalibrator",
    "compute_p1_identity",
    "compute_p2_or_p3_ordering_auc",
    "compute_p4_stability",
    "compute_jti",
    "fit_isotonic_calibrator",
    "compute_hsj_scores",
    "compute_alpha",
    "efg_judge",
    "EFGResult",
]

