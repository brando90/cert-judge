"""Canonical numerical implementation of the Proxy Trust Index (PTI-v0).

This module contains no data loading, model calls, or experiment-specific path
logic.  It implements the versioned numerical contract shared by the CLI and
the paper analyses.  Legacy JTI/TIvar functions intentionally remain in
``hsj_scoring.py`` and are not aliases for this module.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise
from numbers import Real

METRIC_VERSION = "PTI_v0"
ABS_TOL = 1e-12
COMPUTED = "COMPUTED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True)
class LadderResult:
    """Per-artifact result for a structurally valid degradation ladder."""

    levels: tuple[float, ...]
    medians: tuple[float, ...]
    rho: float | None
    kendall_tau_b: float | None
    correlation_quality: float
    instability: float | None
    factor: float
    repeat_count: int
    stability_observed: bool
    constant_ladder: bool
    tie_count: int
    adjacent_reversal_rate: float
    metric_version: str = METRIC_VERSION


@dataclass(frozen=True)
class PropertyResult:
    """A property value plus fail-closed score-coverage diagnostics.

    ``required_count`` is the size of the already structurally validated probe
    set.  Structurally invalid probes are removed before this function is
    called.  Missing/unparsable judge scores reduce ``observed_count`` and can
    produce ``NOT_COMPUTABLE``; behavioral constant ladders remain observed
    factors with value zero.
    """

    status: str
    value: float | None
    coverage: float
    required_count: int
    observed_count: int
    missing_count: int
    zero_count: int
    constant_ladder_count: int = 0
    metric_version: str = METRIC_VERSION


@dataclass(frozen=True)
class PTIResult:
    """Four-property PTI-v0 result with explicit computability status."""

    status: str
    value: float | None
    properties: Mapping[str, float | None]
    missing_properties: tuple[str, ...]
    metric_version: str = METRIC_VERSION


def _finite_float(value: Real, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, got {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return result


def _unit_value(value: Real, *, name: str, tol: float = ABS_TOL) -> float:
    result = _finite_float(value, name=name)
    if result < -tol or result > 1.0 + tol:
        raise ValueError(f"{name} must be in [0, 1], got {result}")
    if result < 0.0:
        return 0.0
    if result > 1.0:
        return 1.0
    return result


def stable_geometric_mean(values: Iterable[Real]) -> float:
    """Return the exact-zero-first, log-domain geometric mean.

    Missing, non-finite, out-of-range, and empty inputs are errors.  Positive
    values are never epsilon-floored.
    """

    checked = [_unit_value(v, name=f"values[{i}]") for i, v in enumerate(values)]
    if not checked:
        raise ValueError("geometric mean requires at least one value")
    if any(v == 0.0 for v in checked):
        return 0.0
    return math.exp(math.fsum(math.log(v) for v in checked) / len(checked))


def average_ranks(values: Sequence[Real]) -> tuple[float, ...]:
    """Return one-based average ranks with deterministic tie handling."""

    checked = [_finite_float(v, name=f"values[{i}]") for i, v in enumerate(values)]
    if not checked:
        raise ValueError("ranking requires at least one value")
    order = sorted(range(len(checked)), key=lambda i: (checked[i], i))
    ranks = [0.0] * len(checked)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and checked[order[end]] == checked[order[start]]:
            end += 1
        average = ((start + 1) + end) / 2.0
        for position in range(start, end):
            ranks[order[position]] = average
        start = end
    return tuple(ranks)


def _pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    if len(x) != len(y):
        raise ValueError("paired vectors must have equal length")
    if len(x) < 2:
        raise ValueError("correlation requires at least two paired values")
    x_mean = math.fsum(x) / len(x)
    y_mean = math.fsum(y) / len(y)
    x_centered = [v - x_mean for v in x]
    y_centered = [v - y_mean for v in y]
    x_ss = math.fsum(v * v for v in x_centered)
    y_ss = math.fsum(v * v for v in y_centered)
    if x_ss == 0.0 or y_ss == 0.0:
        return None
    result = math.fsum(a * b for a, b in zip(x_centered, y_centered)) / math.sqrt(
        x_ss * y_ss
    )
    if abs(result - 1.0) <= ABS_TOL:
        return 1.0
    if abs(result + 1.0) <= ABS_TOL:
        return -1.0
    return max(-1.0, min(1.0, result))


def spearman_rho(x: Sequence[Real], y: Sequence[Real]) -> float | None:
    """Tie-aware Spearman correlation, or ``None`` for a constant vector."""

    if len(x) != len(y):
        raise ValueError("paired vectors must have equal length")
    return _pearson(average_ranks(x), average_ranks(y))


def kendall_tau_b(x: Sequence[Real], y: Sequence[Real]) -> float | None:
    """Compute Kendall's tau-b, returning ``None`` when undefined."""

    if len(x) != len(y):
        raise ValueError("paired vectors must have equal length")
    if len(x) < 2:
        raise ValueError("correlation requires at least two paired values")
    x_checked = [_finite_float(v, name=f"x[{i}]") for i, v in enumerate(x)]
    y_checked = [_finite_float(v, name=f"y[{i}]") for i, v in enumerate(y)]
    concordant = discordant = tied_x = tied_y = 0
    for i in range(len(x_checked) - 1):
        for j in range(i + 1, len(x_checked)):
            dx = x_checked[j] - x_checked[i]
            dy = y_checked[j] - y_checked[i]
            if dx == 0.0 and dy == 0.0:
                continue
            if dx == 0.0:
                tied_x += 1
            elif dy == 0.0:
                tied_y += 1
            elif dx * dy > 0.0:
                concordant += 1
            else:
                discordant += 1
    denominator = math.sqrt(
        (concordant + discordant + tied_x) * (concordant + discordant + tied_y)
    )
    if denominator == 0.0:
        return None
    result = (concordant - discordant) / denominator
    if abs(result - 1.0) <= ABS_TOL:
        return 1.0
    if abs(result + 1.0) <= ABS_TOL:
        return -1.0
    return max(-1.0, min(1.0, result))


def median_over_repeats(
    scores_by_level_and_repeat: Sequence[Sequence[Real]],
) -> tuple[float, ...]:
    """Take the median over judge repeats separately at each ladder level."""

    if not scores_by_level_and_repeat:
        raise ValueError("a ladder requires at least one level")
    medians: list[float] = []
    repeat_count: int | None = None
    for level_index, row in enumerate(scores_by_level_and_repeat):
        if not row:
            raise ValueError(f"level {level_index} has no repeat scores")
        if repeat_count is None:
            repeat_count = len(row)
        elif len(row) != repeat_count:
            raise ValueError("every ladder level must have the same repeat count")
        checked = [
            _unit_value(v, name=f"scores[{level_index}][{repeat_index}]")
            for repeat_index, v in enumerate(row)
        ]
        medians.append(float(statistics.median(checked)))
    return tuple(medians)


def ladder_quality_from_rho(rho: Real) -> float:
    """Orient degradation correlation so a decreasing ladder scores higher."""

    value = _finite_float(rho, name="rho")
    if value < -1.0 - ABS_TOL or value > 1.0 + ABS_TOL:
        raise ValueError(f"rho must be in [-1, 1], got {value}")
    if abs(value - 1.0) <= ABS_TOL:
        value = 1.0
    elif abs(value + 1.0) <= ABS_TOL:
        value = -1.0
    return _unit_value((1.0 - value) / 2.0, name="correlation_quality")


def repeat_instability(
    scores_by_level_and_repeat: Sequence[Sequence[Real]],
) -> float | None:
    """Return mean ``2*sd(ddof=0)`` across levels, or ``None`` for K=1."""

    medians = median_over_repeats(scores_by_level_and_repeat)
    del medians  # validates shape/range without duplicating that logic below
    repeat_count = len(scores_by_level_and_repeat[0])
    if repeat_count == 1:
        return None
    scaled_stds = []
    for level_index, row in enumerate(scores_by_level_and_repeat):
        checked = [
            _unit_value(v, name=f"scores[{level_index}][{repeat_index}]")
            for repeat_index, v in enumerate(row)
        ]
        mean = math.fsum(checked) / repeat_count
        variance = math.fsum((v - mean) ** 2 for v in checked) / repeat_count
        scaled_stds.append(2.0 * math.sqrt(variance))
    return _unit_value(
        math.fsum(scaled_stds) / len(scaled_stds),
        name="instability",
    )


def ladder_factor(
    scores_by_level_and_repeat: Sequence[Sequence[Real]],
    *,
    levels: Sequence[Real] | None = None,
) -> LadderResult:
    """Compute one structurally valid ladder's PTI-v0 factor.

    Structural validation is a pipeline responsibility and must happen before
    judge scores reach this function.  A constant median score sequence is
    behavioral evidence and therefore remains in the property with factor 0.
    """

    medians = median_over_repeats(scores_by_level_and_repeat)
    if len(medians) < 2:
        raise ValueError("a ladder requires at least two levels")
    if levels is None:
        checked_levels = tuple(float(i) for i in range(len(medians)))
    else:
        if len(levels) != len(medians):
            raise ValueError("levels and score rows must have equal length")
        checked_levels = tuple(
            _finite_float(v, name=f"levels[{i}]") for i, v in enumerate(levels)
        )
        if any(b <= a for a, b in pairwise(checked_levels)):
            raise ValueError("ladder levels must be strictly increasing")

    repeat_count = len(scores_by_level_and_repeat[0])
    constant = all(value == medians[0] for value in medians[1:])
    if constant:
        rho = None
        tau = None
        quality = 0.0
    else:
        rho = spearman_rho(checked_levels, medians)
        if rho is None:
            raise AssertionError(
                "non-constant ladder unexpectedly has undefined Spearman"
            )
        tau = kendall_tau_b(checked_levels, medians)
        quality = ladder_quality_from_rho(rho)

    instability = repeat_instability(scores_by_level_and_repeat)
    stability_observed = instability is not None
    factor = (
        quality if instability is None else math.sqrt(quality * (1.0 - instability))
    )
    factor = _unit_value(factor, name="ladder factor")
    adjacent_reversals = sum(b > a for a, b in pairwise(medians))
    return LadderResult(
        levels=checked_levels,
        medians=medians,
        rho=rho,
        kendall_tau_b=tau,
        correlation_quality=quality,
        instability=instability,
        factor=factor,
        repeat_count=repeat_count,
        stability_observed=stability_observed,
        constant_ladder=constant,
        tie_count=len(medians) - len(set(medians)),
        adjacent_reversal_rate=adjacent_reversals / (len(medians) - 1),
    )


def aggregate_property_factors(
    factors: Sequence[Real],
    *,
    required_count: int | None = None,
    min_coverage: float = 1.0,
    constant_ladder_count: int = 0,
) -> PropertyResult:
    """Aggregate observed factors with explicit fail-closed coverage.

    The v4 execution protocol defaults to complete score coverage
    (``min_coverage=1``).  Callers may use another *pre-frozen* threshold, but
    cannot turn missing scores into zero-valued evidence.
    """

    min_coverage = _unit_value(min_coverage, name="min_coverage")
    observed_count = len(factors)
    if required_count is None:
        required_count = observed_count
    if required_count <= 0:
        raise ValueError("required_count must be positive")
    if observed_count > required_count:
        raise ValueError("observed_count cannot exceed required_count")
    if constant_ladder_count < 0 or constant_ladder_count > observed_count:
        raise ValueError("constant_ladder_count is inconsistent with observed factors")
    checked = [_unit_value(v, name=f"factors[{i}]") for i, v in enumerate(factors)]
    coverage = observed_count / required_count
    missing_count = required_count - observed_count
    zero_count = sum(v == 0.0 for v in checked)
    if not checked or coverage + ABS_TOL < min_coverage:
        return PropertyResult(
            status=NOT_COMPUTABLE,
            value=None,
            coverage=coverage,
            required_count=required_count,
            observed_count=observed_count,
            missing_count=missing_count,
            zero_count=zero_count,
            constant_ladder_count=constant_ladder_count,
        )
    return PropertyResult(
        status=COMPUTED,
        value=stable_geometric_mean(checked),
        coverage=coverage,
        required_count=required_count,
        observed_count=observed_count,
        missing_count=missing_count,
        zero_count=zero_count,
        constant_ladder_count=constant_ladder_count,
    )


def aggregate_ladder_property(
    ladders: Sequence[LadderResult],
    *,
    required_count: int | None = None,
    min_coverage: float = 1.0,
) -> PropertyResult:
    """Aggregate ladder factors; behavioral constants remain zero factors."""

    return aggregate_property_factors(
        [result.factor for result in ladders],
        required_count=required_count,
        min_coverage=min_coverage,
        constant_ladder_count=sum(result.constant_ladder for result in ladders),
    )


def equality_property(self_pair_medians: Sequence[Real]) -> float:
    """Compute ``P_eq`` from median scores on exact self-pairs."""

    return stable_geometric_mean(self_pair_medians)


def alpha_invariance_property(
    original_medians: Sequence[Real],
    alpha_medians: Sequence[Real],
) -> float:
    """Compute ``P_eqalpha`` from paired original/alpha median scores."""

    if len(original_medians) != len(alpha_medians):
        raise ValueError("original and alpha vectors must have equal length")
    if not original_medians:
        raise ValueError("alpha property requires at least one paired score")
    factors = []
    for i, (original, alpha) in enumerate(zip(original_medians, alpha_medians)):
        original_value = _unit_value(original, name=f"original_medians[{i}]")
        alpha_value = _unit_value(alpha, name=f"alpha_medians[{i}]")
        factors.append(1.0 - abs(original_value - alpha_value))
    return stable_geometric_mean(factors)


def pti_v0(
    p_eq: Real,
    p_bm: Real,
    p_ms: Real,
    p_eqalpha: Real,
) -> float:
    """Compute the four-property PTI-v0 scalar."""

    return stable_geometric_mean([p_eq, p_bm, p_ms, p_eqalpha])


def compute_pti(properties: Mapping[str, PropertyResult]) -> PTIResult:
    """Compute PTI-v0 from named property results, preserving missing status."""

    required = ("P_eq", "P_bm", "P_ms", "P_eqalpha")
    absent = tuple(name for name in required if name not in properties)
    if absent:
        raise ValueError(f"missing property records: {', '.join(absent)}")
    missing = tuple(name for name in required if properties[name].status != COMPUTED)
    values = {name: properties[name].value for name in required}
    if missing:
        return PTIResult(
            status=NOT_COMPUTABLE,
            value=None,
            properties=values,
            missing_properties=missing,
        )
    return PTIResult(
        status=COMPUTED,
        value=pti_v0(*(values[name] for name in required)),  # type: ignore[arg-type]
        properties=values,
        missing_properties=(),
    )


def pti_three_property(p_eq: Real, p_bm: Real, p_ms: Real) -> float:
    """Explicitly labeled fallback when alpha is blocked or declined."""

    return stable_geometric_mean([p_eq, p_bm, p_ms])


__all__ = [
    "ABS_TOL",
    "COMPUTED",
    "METRIC_VERSION",
    "NOT_COMPUTABLE",
    "LadderResult",
    "PTIResult",
    "PropertyResult",
    "aggregate_ladder_property",
    "aggregate_property_factors",
    "alpha_invariance_property",
    "average_ranks",
    "compute_pti",
    "equality_property",
    "kendall_tau_b",
    "ladder_factor",
    "ladder_quality_from_rho",
    "median_over_repeats",
    "pti_three_property",
    "pti_v0",
    "repeat_instability",
    "spearman_rho",
    "stable_geometric_mean",
]
