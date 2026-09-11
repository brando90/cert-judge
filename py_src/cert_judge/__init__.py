"""
cert_judge: Core scoring utilities for certifying and scoring LLM judges.

Exports
    - HSJInputs, IsotonicCalibrator
    - compute_p1_identity, compute_p2_or_p3_ordering_auc, compute_p4_stability, compute_jti
    - fit_isotonic_calibrator, compute_hsj_scores, compute_alpha
    - efg_judge, EFGResult (Zhang et al. arXiv:2506.10903 baseline)
    - PTI-v0 numerical core (versioned replacement, not a JTI/TIvar alias)

Not re-exported here (opt-in submodule import, matching uutils.stats_uu's own
convention): `from cert_judge.ti2prime_plot import TI2PrimeResult,
compute_ti2prime, plot_ti2prime_scatter` -- item-level judge-vs-human scatter
with the TI_2' formula in the legend. Kept out of the package's top-level
import because it requires uutils + matplotlib + scipy at import time, and
this package's core scoring functions must stay importable without them.
"""

from .efg_judge import (
    EFGResult,
    efg_judge,
)
from .hsj_scoring import (
    HSJInputs,
    IsotonicCalibrator,
    compute_alpha,
    compute_hsj_scores,
    compute_jti,
    compute_p1_identity,
    compute_p2_or_p3_ordering_auc,
    compute_p4_stability,
    fit_isotonic_calibrator,
)
from .pti_v0 import (
    COMPUTED,
    METRIC_VERSION,
    NOT_COMPUTABLE,
    LadderResult,
    PropertyResult,
    PTIResult,
    aggregate_ladder_property,
    aggregate_property_factors,
    alpha_invariance_property,
    average_ranks,
    compute_pti,
    equality_property,
    kendall_tau_b,
    ladder_factor,
    ladder_quality_from_rho,
    median_over_repeats,
    pti_three_property,
    repeat_instability,
    spearman_rho,
    stable_geometric_mean,
)

__all__ = [
    "COMPUTED",
    "METRIC_VERSION",
    "NOT_COMPUTABLE",
    "EFGResult",
    "HSJInputs",
    "IsotonicCalibrator",
    "LadderResult",
    "PTIResult",
    "PropertyResult",
    "aggregate_ladder_property",
    "aggregate_property_factors",
    "alpha_invariance_property",
    "average_ranks",
    "compute_alpha",
    "compute_hsj_scores",
    "compute_jti",
    "compute_p1_identity",
    "compute_p2_or_p3_ordering_auc",
    "compute_p4_stability",
    "compute_pti",
    "efg_judge",
    "equality_property",
    "fit_isotonic_calibrator",
    "kendall_tau_b",
    "ladder_factor",
    "ladder_quality_from_rho",
    "median_over_repeats",
    "pti_three_property",
    "repeat_instability",
    "spearman_rho",
    "stable_geometric_mean",
]
