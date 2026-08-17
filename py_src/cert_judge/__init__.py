"""
cert_judge: Core scoring utilities for certifying and scoring LLM judges.

Exports
    - HSJInputs, IsotonicCalibrator
    - compute_p1_identity, compute_p2_or_p3_ordering_auc, compute_p4_stability, compute_jti
    - fit_isotonic_calibrator, compute_hsj_scores, compute_alpha
    - efg_judge, EFGResult (Zhang et al. arXiv:2506.10903 baseline)

Not re-exported here (opt-in submodule import, matching uutils.stats_uu's own
convention): `from cert_judge.ti2prime_plot import TI2PrimeResult,
compute_ti2prime, plot_ti2prime_scatter` -- item-level judge-vs-human scatter
with the TI_2' formula in the legend. Kept out of the package's top-level
import because it requires uutils + matplotlib + scipy at import time, and
this package's core scoring functions must stay importable without them.
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

