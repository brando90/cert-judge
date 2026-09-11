"""Validation harness for ``PTI_p -> TI_m``: can a label-free proxy predict the
human-grounded trust criterion?

Scope
-----
The project keeps three scientific objects distinct (see ``CLAUDE.md``):

``TW_m``
    the scoped trustworthiness construct;
``TI_m``
    an expensive human-grounded *criterion*, estimated from target-judge labels;
``PTI_p``
    a label-free behavioral *proxy* / screening instrument (currently
    ``PTI_v0``, implemented in :mod:`cert_judge.pti_v0`).

The research claim this module exists to test is a *criterion-validity* claim:
across a panel of units (agents, judge configurations, or agent x judge cells),
does ``PTI_p`` rank units the same way ``TI_m`` does?  If it does, ``PTI_p``
screens new units without paying for fresh human labels.

This module computes ``TI_m``, compares it against a supplied ``PTI_p``, and --
critically -- reports whether the panel is large enough and the labels reliable
enough for the comparison to mean anything.  Two guard rails are built in
rather than left to the caller:

*   every correlation is returned with a bootstrap interval, never bare;
*   every report carries a :class:`PowerReport` stating the resolving power of
    the design, because a correlation over a handful of units with a noisy
    criterion is compatible with almost any true value.

Like :mod:`cert_judge.pti_v0`, this module is pure numerics: no data loading, no
model calls, no experiment paths, and no third-party dependencies.  It reuses
the frozen tie-aware rank primitives from ``pti_v0`` so that rank handling is
identical across the codebase.

Notation follows ``paper_latex/TrustWorthy_Notes/main.tex``.
"""

from __future__ import annotations

import math
import random
from statistics import NormalDist
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from numbers import Real

from cert_judge.pti_v0 import (
    average_ranks,
    kendall_tau_b,
    spearman_rho,
)

VALIDATION_VERSION = "TI_VALIDATION_v2"

COMPUTED = "COMPUTED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
UNDERPOWERED = "UNDERPOWERED"

#: Diagnostic heuristic, not a power calculation or an acceptance threshold.
MIN_TRUSTWORTHY_PANEL = 12

#: Default bootstrap resamples.  10_000 matches the paper's rerun settings.
DEFAULT_BOOTSTRAP = 10_000

_DEFAULT_SEED = 20260911


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _floats(values: Iterable[Real], *, name: str) -> tuple[float, ...]:
    out: list[float] = []
    for index, value in enumerate(values):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"{name}[{index}] is not finite: {value!r}")
        out.append(number)
    return tuple(out)


def _paired(
    x: Sequence[Real], y: Sequence[Real], *, name: str
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if len(x) != len(y):
        raise ValueError(f"{name}: length mismatch {len(x)} != {len(y)}")
    return _floats(x, name=f"{name}.x"), _floats(y, name=f"{name}.y")


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


# ---------------------------------------------------------------------------
# correlation suite
# ---------------------------------------------------------------------------


def pearson_r(x: Sequence[Real], y: Sequence[Real]) -> float | None:
    """Pearson product-moment correlation, or ``None`` if either side is constant."""
    xs, ys = _paired(x, y, name="pearson_r")
    n = len(xs)
    if n < 2:
        return None
    mx, my = _mean(xs), _mean(ys)
    dx = [v - mx for v in xs]
    dy = [v - my for v in ys]
    sxx = math.fsum(v * v for v in dx)
    syy = math.fsum(v * v for v in dy)
    if sxx <= 0.0 or syy <= 0.0:
        return None
    return math.fsum(a * b for a, b in zip(dx, dy, strict=True)) / math.sqrt(sxx * syy)


def lin_ccc(x: Sequence[Real], y: Sequence[Real]) -> float | None:
    """Lin's concordance correlation coefficient.

    Unlike Pearson, this penalises location and scale shifts as well as
    association, so it answers "do these two agree?" rather than "do these two
    covary?".  It is one of the alternatives named in the Trust Index notes for
    the objection that ``1 - std`` is a judge-only marginal quantity and never
    checks whether the judge's spread matches the target's.
    """
    xs, ys = _paired(x, y, name="lin_ccc")
    n = len(xs)
    if n < 2:
        return None
    mx, my = _mean(xs), _mean(ys)
    vx = math.fsum((v - mx) ** 2 for v in xs) / n
    vy = math.fsum((v - my) ** 2 for v in ys) / n
    cov = math.fsum((a - mx) * (b - my) for a, b in zip(xs, ys, strict=True)) / n
    denominator = vx + vy + (mx - my) ** 2
    if denominator <= 0.0:
        return None
    return 2.0 * cov / denominator


@dataclass(frozen=True)
class IccResult:
    """Intraclass correlation for a subjects x raters matrix."""

    icc_1_1: float | None
    icc_2_1: float | None
    icc_3_1: float | None
    icc_2_k: float | None
    icc_3_k: float | None
    n_subjects: int
    n_raters: int

    @property
    def single_rater(self) -> float | None:
        """Reliability of one randomly chosen rater: ICC(2,1)."""
        return self.icc_2_1

    @property
    def averaged_raters(self) -> float | None:
        """Reliability of the mean of all ``n_raters``: ICC(2,k).

        This is the quantity that sets the attenuation ceiling when the target
        label is the average across the rater pool.
        """
        return self.icc_2_k


def icc(ratings: Sequence[Sequence[Real]]) -> IccResult:
    """Intraclass correlations from a fully crossed subjects x raters matrix.

    ``ratings[i][j]`` is rater ``j``'s score for subject (item) ``i``.  Every
    subject must be scored by every rater; ragged input is rejected rather than
    silently imputed, because imputing here would inflate reliability and so
    inflate the ceiling that the rest of this module derives from it.

    Definitions follow Shrout & Fleiss (1979) / McGraw & Wong (1996).  Form 1 is
    one-way random, form 2 two-way random (raters are a sample, so rater bias
    counts against reliability), form 3 two-way mixed (these raters are the
    whole population of interest).  Suffix ``k`` is the reliability of the mean
    of ``k`` raters rather than of a single rater.
    """
    if not ratings:
        return IccResult(None, None, None, None, None, 0, 0)
    n = len(ratings)
    k = len(ratings[0])
    for index, row in enumerate(ratings):
        if len(row) != k:
            raise ValueError(
                f"icc: row {index} has {len(row)} raters, expected {k}; "
                "the design must be fully crossed"
            )
    if n < 2 or k < 2:
        return IccResult(None, None, None, None, None, n, k)

    matrix = [_floats(row, name=f"icc.row[{i}]") for i, row in enumerate(ratings)]
    flat = [value for row in matrix for value in row]
    grand = _mean(flat)
    row_means = [_mean(row) for row in matrix]
    col_means = [_mean([matrix[i][j] for i in range(n)]) for j in range(k)]

    ss_rows = k * math.fsum((m - grand) ** 2 for m in row_means)
    ss_cols = n * math.fsum((m - grand) ** 2 for m in col_means)
    ss_total = math.fsum((v - grand) ** 2 for v in flat)
    ss_error = ss_total - ss_rows - ss_cols
    ss_within = ss_total - ss_rows

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))
    ms_within = ss_within / (n * (k - 1))

    def _safe(numerator: float, denominator: float) -> float | None:
        if denominator == 0.0 or not math.isfinite(denominator):
            return None
        return numerator / denominator

    icc_1_1 = _safe(ms_rows - ms_within, ms_rows + (k - 1) * ms_within)
    icc_2_1 = _safe(
        ms_rows - ms_error,
        ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n,
    )
    icc_3_1 = _safe(ms_rows - ms_error, ms_rows + (k - 1) * ms_error)
    icc_2_k = _safe(ms_rows - ms_error, ms_rows + (ms_cols - ms_error) / n)
    icc_3_k = _safe(ms_rows - ms_error, ms_rows)

    return IccResult(icc_1_1, icc_2_1, icc_3_1, icc_2_k, icc_3_k, n, k)


#: Correlation functions offered by :func:`correlation_suite`.
CORRELATION_FUNCTIONS: dict[str, Callable[[Sequence[Real], Sequence[Real]], float | None]] = {
    "pearson": pearson_r,
    "spearman": spearman_rho,
    "kendall_tau_b": kendall_tau_b,
    "lin_ccc": lin_ccc,
}


# ---------------------------------------------------------------------------
# uncertainty
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Estimate:
    """A point estimate with a percentile bootstrap interval."""

    name: str
    value: float | None
    ci_low: float | None
    ci_high: float | None
    n: int
    resamples: int

    @property
    def ci_width(self) -> float | None:
        if self.ci_low is None or self.ci_high is None:
            return None
        return self.ci_high - self.ci_low

    @property
    def excludes_zero(self) -> bool:
        """True only if the whole interval sits strictly on one side of zero."""
        if self.ci_low is None or self.ci_high is None:
            return False
        return self.ci_low > 0.0 or self.ci_high < 0.0

    def __str__(self) -> str:  # pragma: no cover - display helper
        if self.value is None:
            return f"{self.name}=n/a"
        if self.ci_low is None:
            return f"{self.name}={self.value:.3f}"
        return f"{self.name}={self.value:.3f} [{self.ci_low:.3f}, {self.ci_high:.3f}]"


def bootstrap_ci(
    x: Sequence[Real],
    y: Sequence[Real],
    statistic: Callable[[Sequence[Real], Sequence[Real]], float | None],
    *,
    name: str = "statistic",
    resamples: int = DEFAULT_BOOTSTRAP,
    alpha: float = 0.05,
    seed: int = _DEFAULT_SEED,
) -> Estimate:
    """Paired percentile bootstrap over units.

    Resampling is over pairs, so it propagates the sampling error of the panel
    itself.  It does *not* propagate the error in each unit's ``TI_m``
    estimate; that second source is reported separately by
    :func:`resolving_power`, and at small panel sizes it usually dominates.
    """
    xs, ys = _paired(x, y, name=name)
    n = len(xs)
    point = statistic(xs, ys)
    if n < 3 or point is None or resamples <= 0:
        return Estimate(name, point, None, None, n, 0)

    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        value = statistic([xs[i] for i in idx], [ys[i] for i in idx])
        if value is not None and math.isfinite(value):
            draws.append(value)
    if len(draws) < 2:
        return Estimate(name, point, None, None, n, len(draws))

    draws.sort()
    lo_index = max(0, min(len(draws) - 1, int(math.floor((alpha / 2) * len(draws)))))
    hi_index = max(0, min(len(draws) - 1, int(math.ceil((1 - alpha / 2) * len(draws))) - 1))
    return Estimate(name, point, draws[lo_index], draws[hi_index], n, len(draws))


def correlation_suite(
    x: Sequence[Real],
    y: Sequence[Real],
    *,
    methods: Sequence[str] | None = None,
    resamples: int = DEFAULT_BOOTSTRAP,
    alpha: float = 0.05,
    seed: int = _DEFAULT_SEED,
) -> dict[str, Estimate]:
    """Run several correlation definitions on one pair of vectors.

    Reporting more than one is a robustness check, not extra evidence: the
    estimates share a sample, so they rise and fall together and must not be
    read as independent confirmations.  Kendall's tau-b is the conservative
    choice on small panels and will usually read lowest.
    """
    chosen = tuple(methods) if methods is not None else tuple(CORRELATION_FUNCTIONS)
    report: dict[str, Estimate] = {}
    for offset, method in enumerate(chosen):
        if method not in CORRELATION_FUNCTIONS:
            raise KeyError(f"unknown correlation method: {method!r}")
        report[method] = bootstrap_ci(
            x,
            y,
            CORRELATION_FUNCTIONS[method],
            name=method,
            resamples=resamples,
            alpha=alpha,
            seed=seed + offset,
        )
    return report


# ---------------------------------------------------------------------------
# the human-grounded criterion TI_m
# ---------------------------------------------------------------------------


def mean_within_item_std(repeats_by_item: Sequence[Sequence[Real]]) -> float | None:
    """Judge instability: the mean over items of the per-item std across repeats.

    This is the ``std`` intended by ``TI_2'``.  It is emphatically **not** the
    standard deviation of the judge's scores pooled over items: that quantity
    grows when a judge successfully separates good artifacts from bad ones, so
    penalising it would reward a judge for being uninformative.  The two differ
    whenever a judge discriminates at all, and confusing them silently inverts
    the stability term.
    """
    per_item: list[float] = []
    for index, repeats in enumerate(repeats_by_item):
        values = _floats(repeats, name=f"mean_within_item_std.item[{index}]")
        if len(values) < 2:
            continue
        mean = _mean(values)
        variance = math.fsum((v - mean) ** 2 for v in values) / (len(values) - 1)
        per_item.append(math.sqrt(variance))
    if not per_item:
        return None
    return _mean(per_item)


@dataclass(frozen=True)
class TrustIndex:
    """The human-grounded criterion ``TI_m`` for one unit, with its parts."""

    unit: str
    status: str
    ti_m1: float | None
    ti_2prime: float | None
    correlation: float | None
    correlation_method: str
    instability: float | None
    stability: float | None
    judge_std_pooled: float | None
    target_std_pooled: float | None
    scale_ratio: float | None
    lin_ccc: float | None
    n_items: int
    correlation_clamped: bool = False
    stability_clamped: bool = False
    metric_version: str = VALIDATION_VERSION

    @property
    def value(self) -> float | None:
        """The working criterion: ``TI_2'``."""
        return self.ti_2prime


def ti_m1(
    judge_scores: Sequence[Real],
    target_scores: Sequence[Real],
    *,
    method: str = "spearman",
) -> float | None:
    """``TI_{m1}`` -- common practice: correlation between judge and target."""
    if method not in CORRELATION_FUNCTIONS:
        raise KeyError(f"unknown correlation method: {method!r}")
    return CORRELATION_FUNCTIONS[method](judge_scores, target_scores)


def ti_2prime(correlation: Real | None, instability: Real | None) -> tuple[float | None, bool, bool]:
    """``TI_{2'} = sqrt(Corr * (1 - std))`` -- validity combined with stability.

    Returns the value together with two flags recording whether either factor
    had to be clamped into ``[0, 1]``.

    A negative correlation makes the geometric mean undefined.  Rather than
    return a complex number or drop the unit, the correlation factor is clamped
    to zero, which sends ``TI_2'`` to zero: a judge that ranks against the
    target is maximally untrustworthy, so zero is the right trust score.  The
    raw signed correlation is preserved separately on :class:`TrustIndex` so
    the clamp never hides the direction.
    """
    if correlation is None or instability is None:
        return None, False, False
    corr = float(correlation)
    inst = float(instability)
    if not (math.isfinite(corr) and math.isfinite(inst)):
        return None, False, False

    corr_clamped = corr < 0.0 or corr > 1.0
    stability = 1.0 - inst
    stab_clamped = stability < 0.0 or stability > 1.0
    return math.sqrt(_clamp(corr) * _clamp(stability)), corr_clamped, stab_clamped


def compute_ti_m(
    unit: str,
    judge_scores: Sequence[Real],
    target_scores: Sequence[Real],
    *,
    judge_repeats_by_item: Sequence[Sequence[Real]] | None = None,
    instability: Real | None = None,
    method: str = "spearman",
) -> TrustIndex:
    """Assemble ``TI_m`` for one unit from its judge scores and target labels.

    Supply either ``judge_repeats_by_item`` (per-item repeated judge calls, from
    which instability is derived) or a precomputed ``instability``.  With
    neither, ``TI_2'`` is ``NOT_COMPUTABLE`` while ``TI_{m1}`` is still
    reported, because a correlation alone is a legitimate weaker criterion.
    """
    judge, target = _paired(judge_scores, target_scores, name=f"compute_ti_m[{unit}]")
    n_items = len(judge)

    if instability is not None and judge_repeats_by_item is not None:
        raise ValueError("supply repeats or precomputed instability, not both")
    if instability is not None and (not math.isfinite(float(instability)) or not 0 <= float(instability) <= 1):
        raise ValueError("precomputed instability must be normalized to [0,1]")
    if instability is None and judge_repeats_by_item is not None:
        if len(judge_repeats_by_item) != n_items:
            raise ValueError("repeat rows must align one-to-one with scored items")
        if any(len(row) < 2 for row in judge_repeats_by_item):
            raise ValueError("every scored item needs at least two repeats")
        if any(not 0.0 <= value <= 1.0 for row in judge_repeats_by_item
               for value in _floats(row, name="judge_repeats")):
            raise ValueError("repeat scores must be normalized to [0,1]")
        instability = mean_within_item_std(judge_repeats_by_item)

    correlation = ti_m1(judge, target, method=method) if n_items >= 2 else None
    value, corr_clamped, stab_clamped = ti_2prime(correlation, instability)

    def _pooled(values: Sequence[float]) -> float | None:
        if len(values) < 2:
            return None
        mean = _mean(values)
        return math.sqrt(math.fsum((v - mean) ** 2 for v in values) / (len(values) - 1))

    judge_std = _pooled(judge)
    target_std = _pooled(target)
    scale_ratio = (
        judge_std / target_std if judge_std is not None and target_std else None
    )

    status = COMPUTED if value is not None else NOT_COMPUTABLE
    stability = None if instability is None else _clamp(1.0 - float(instability))

    return TrustIndex(
        unit=unit,
        status=status,
        ti_m1=correlation,
        ti_2prime=value,
        correlation=correlation,
        correlation_method=method,
        instability=None if instability is None else float(instability),
        stability=stability,
        judge_std_pooled=judge_std,
        target_std_pooled=target_std,
        scale_ratio=scale_ratio,
        lin_ccc=lin_ccc(judge, target) if n_items >= 2 else None,
        n_items=n_items,
        correlation_clamped=corr_clamped,
        stability_clamped=stab_clamped,
    )


# ---------------------------------------------------------------------------
# reliability ceiling -- what the labels allow before any judge is run
# ---------------------------------------------------------------------------


def spearman_brown(reliability: Real, k: Real) -> float | None:
    """Reliability of a mean of ``k`` raters given single-rater ``reliability``."""
    rho = float(reliability)
    k = float(k)
    if k <= 0 or not math.isfinite(rho) or rho <= 0.0:
        return None
    denominator = 1.0 + (k - 1.0) * rho
    if denominator <= 0.0:
        return None
    return _clamp(k * rho / denominator)


def attenuation_ceiling(reliability: Real | None) -> float | None:
    """Largest correlation observable against labels of this reliability.

    Classical correction for attenuation: an observed correlation cannot exceed
    ``sqrt(reliability_of_the_target)``.  When the target is the mean of ``k``
    raters, pass ``ICC(2,k)``; for a single rater pass ``ICC(2,1)``.
    """
    if reliability is None:
        return None
    rho = float(reliability)
    if rho <= 0.0:
        return 0.0
    return math.sqrt(_clamp(rho))


def disattenuate(
    observed: Real | None,
    reliability_y: Real | None,
    reliability_x: Real | None = None,
) -> float | None:
    """Correct an observed correlation for measurement error in its inputs.

    ``reliability_x`` defaults to 1.0, the usual choice when ``x`` is a
    deterministic instrument such as ``PTI_p`` computed at fixed settings.  The
    result can exceed 1.0 when reliabilities are themselves underestimated;
    that is a signal the reliability estimate is too low, not a valid
    correlation, so callers should report it as-is rather than clipping.
    """
    if observed is None or reliability_y is None:
        return None
    rel_y = float(reliability_y)
    rel_x = 1.0 if reliability_x is None else float(reliability_x)
    if rel_y <= 0.0 or rel_x <= 0.0:
        return None
    return float(observed) / math.sqrt(rel_y * rel_x)


@dataclass(frozen=True)
class CeilingReport:
    """What the target labels permit, independent of judge quality."""

    single_rater_reliability: float | None
    averaged_reliability: float | None
    n_raters: int
    ceiling_single: float | None
    ceiling_averaged: float | None
    target_threshold: float | None
    threshold_reachable: bool | None
    raters_needed_for_threshold: int | None


def ceiling_report(
    ratings: Sequence[Sequence[Real]] | None = None,
    *,
    single_rater_reliability: Real | None = None,
    n_raters: int | None = None,
    target_threshold: Real | None = 0.70,
    max_raters: int = 200,
) -> CeilingReport:
    """Classical-error Pearson ceiling sensitivity under supplied assumptions.

    Pass a fully crossed ``ratings`` matrix to estimate reliability by ICC, or
    supply ``single_rater_reliability`` and ``n_raters`` directly when only
    summary agreement is available.

    This calculation assumes a matching measurement, independent additive
    errors and parallel raters. It is not a ceiling for rank correlation or
    for correlations between derived judge-level criteria. Cross-rubric
    agreement cannot establish reliability for a new annotation protocol.
    """
    averaged: float | None
    if ratings is not None:
        result = icc(ratings)
        single = result.single_rater
        averaged = result.averaged_raters
        k = result.n_raters
    else:
        if single_rater_reliability is None or n_raters is None:
            raise ValueError(
                "ceiling_report needs either ratings or "
                "(single_rater_reliability, n_raters)"
            )
        single = float(single_rater_reliability)
        k = int(n_raters)
        averaged = spearman_brown(single, k)

    ceiling_single = attenuation_ceiling(single)
    ceiling_averaged = attenuation_ceiling(averaged)

    threshold = None if target_threshold is None else float(target_threshold)
    reachable: bool | None = None
    needed: int | None = None
    if threshold is not None and ceiling_averaged is not None:
        reachable = ceiling_averaged >= threshold
        if single is not None and single > 0.0:
            required_reliability = threshold * threshold
            for candidate in range(1, max_raters + 1):
                value = spearman_brown(single, candidate)
                if value is not None and value >= required_reliability:
                    needed = candidate
                    break

    return CeilingReport(
        single_rater_reliability=single,
        averaged_reliability=averaged,
        n_raters=k,
        ceiling_single=ceiling_single,
        ceiling_averaged=ceiling_averaged,
        target_threshold=threshold,
        threshold_reachable=reachable,
        raters_needed_for_threshold=needed,
    )


# ---------------------------------------------------------------------------
# resolving power -- can this design detect anything?
# ---------------------------------------------------------------------------


def correlation_se(n_items: int) -> float | None:
    """Approximate standard error of a correlation estimated on ``n_items``."""
    if n_items < 3:
        return None
    return 1.0 / math.sqrt(n_items - 1)


def fisher_ci(rho: Real, n: int, *, alpha: float = 0.05) -> tuple[float, float] | None:
    """Approximate Pearson interval for independent bivariate-normal pairs."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between zero and one")
    r = float(rho)
    if n <= 3 or abs(r) >= 1.0:
        return None
    z = 0.5 * math.log((1.0 + r) / (1.0 - r))
    half = NormalDist().inv_cdf(1.0 - alpha / 2) / math.sqrt(n - 3)

    def _inverse(value: float) -> float:
        return math.tanh(value)

    return _inverse(z - half), _inverse(z + half)


def min_units_for_ci_width(
    rho: Real, target_width: Real, *, max_units: int = 5000
) -> int | None:
    """Smallest panel size whose Fisher interval around ``rho`` is this narrow."""
    width = float(target_width)
    for n in range(4, max_units + 1):
        interval = fisher_ci(rho, n)
        if interval is not None and (interval[1] - interval[0]) <= width:
            return n
    return None


#: Legacy diagnostic threshold for limited ranking resolution, not zero information.
MAX_PREDICTOR_TIE_FRACTION = 0.5


@dataclass(frozen=True)
class PowerReport:
    """Heuristic design warnings; these do not replace a power calculation."""

    n_units: int
    criterion_spread: float | None
    criterion_se: float | None
    resolving_ratio: float | None
    ci_width_at_point: float | None
    underpowered: bool
    predictor_distinct_values: int | None = None
    predictor_tie_fraction: float | None = None
    predictor_degenerate: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


def predictor_tie_fraction(values: Sequence[Real]) -> float | None:
    """Share of units sitting on the single most common proxy value.

    A multiplicative index collapses to exactly zero whenever any one property
    is zero, so a panel can easily arrive with most of its proxy values tied at
    the floor.  Rank correlations still return a number in that situation, but
    it is decided entirely by the handful of untied units, and it is not
    evidence about the proxy.  This makes the condition visible instead of
    letting it read as a weak correlation.
    """
    xs = _floats(values, name="predictor_tie_fraction")
    if not xs:
        return None
    counts: dict[float, int] = {}
    for value in xs:
        counts[value] = counts.get(value, 0) + 1
    return max(counts.values()) / len(xs)


def resolving_power(
    criterion_values: Sequence[Real],
    *,
    n_items_per_unit: int | None = None,
    criterion_se: Real | None = None,
    observed_rho: Real | None = None,
    predictor_values: Sequence[Real] | None = None,
    min_panel: int = MIN_TRUSTWORTHY_PANEL,
    max_tie_fraction: float = MAX_PREDICTOR_TIE_FRACTION,
) -> PowerReport:
    """Compare between-unit signal against within-unit estimation noise.

    ``resolving_ratio`` is the spread of ``TI_m`` across units divided by the
    standard error of a single unit's ``TI_m``.  When it approaches or falls
    below 1, the ordering of units is mostly noise, and the correlation between
    any proxy and that ordering is uninformative however it comes out -- a
    proxy that ranks every unit perfectly will still produce scattered,
    frequently negative correlations.  Values above roughly 3 are needed before
    a panel ranking carries real information.

    Passing ``predictor_values`` adds the matching check on the other axis: a
    proxy whose values are mostly tied cannot order the panel at all, so the
    design fails before the criterion is even consulted.
    """
    values = _floats(criterion_values, name="resolving_power")
    n_units = len(values)
    spread = (max(values) - min(values)) if n_units >= 2 else None

    se = None if criterion_se is None else float(criterion_se)
    if se is None and n_items_per_unit is not None:
        se = correlation_se(n_items_per_unit)

    ratio = None
    if spread is not None and se is not None and se > 0.0:
        ratio = spread / se

    ci_width = None
    if observed_rho is not None:
        interval = fisher_ci(observed_rho, n_units)
        if interval is not None:
            ci_width = interval[1] - interval[0]

    notes: list[str] = []
    underpowered = False

    distinct: int | None = None
    tie_fraction: float | None = None
    degenerate = False
    if predictor_values is not None:
        proxy = _floats(predictor_values, name="resolving_power.predictor")
        distinct = len(set(proxy))
        tie_fraction = predictor_tie_fraction(proxy)
        if tie_fraction is not None and tie_fraction > max_tie_fraction:
            degenerate = True
            underpowered = True
            tied = round(tie_fraction * len(proxy))
            notes.append(
                f"proxy is flagged degenerate by the legacy tie heuristic: "
                f"{tied} of {len(proxy)} units share one value and only "
                f"{distinct} distinct values occur; report limited ranking "
                "resolution without inferring absence of screening information"
            )

    if n_units < min_panel:
        underpowered = True
        notes.append(
            f"panel of {n_units} units is below the {min_panel}-unit floor; "
            "this heuristic flag is not a formal power calculation"
        )
    if ratio is not None and ratio < 3.0:
        underpowered = True
        notes.append(
            f"criterion spread is only {ratio:.2f}x its own standard error; "
            "paired criterion covariance is needed to assess ranking uncertainty"
        )
    if ci_width is not None and ci_width > 0.6:
        underpowered = True
        notes.append(
            f"95% interval spans {ci_width:.2f}; report the interval, not the point"
        )

    return PowerReport(
        n_units=n_units,
        criterion_spread=spread,
        criterion_se=se,
        resolving_ratio=ratio,
        ci_width_at_point=ci_width,
        underpowered=underpowered,
        predictor_distinct_values=distinct,
        predictor_tie_fraction=tie_fraction,
        predictor_degenerate=degenerate,
        notes=tuple(notes),
    )


# ---------------------------------------------------------------------------
# ranking agreement -- rankings are the deliverable
# ---------------------------------------------------------------------------


def pairwise_rank_accuracy(
    predicted: Sequence[Real], actual: Sequence[Real]
) -> float | None:
    """Fraction of unit pairs the proxy orders the same way as the criterion.

    Pairs tied under the criterion are excluded, since they impose no ordering
    to get right.  A tie in the prediction over an untied criterion pair counts
    as half credit, matching the convention behind tau-b.
    """
    pred, act = _paired(predicted, actual, name="pairwise_rank_accuracy")
    n = len(pred)
    if n < 2:
        return None
    comparable = 0
    correct = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if act[i] == act[j]:
                continue
            comparable += 1
            if pred[i] == pred[j]:
                correct += 0.5
            elif (pred[i] > pred[j]) == (act[i] > act[j]):
                correct += 1.0
    if comparable == 0:
        return None
    return correct / comparable


def top_k_overlap(
    predicted: Sequence[Real], actual: Sequence[Real], k: int
) -> float | None:
    """Expected top-k overlap with independent uniform boundary tie breaking.

    Each side selects exactly k units; a constant predictor receives chance
    overlap rather than credit for selecting the entire panel.
    """
    pred, act = _paired(predicted, actual, name="top_k_overlap")
    n = len(pred)
    if k <= 0 or k > n:
        return None

    def _top(values: Sequence[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: values[i], reverse=True)
        cutoff = values[order[k - 1]]
        above = sum(value > cutoff for value in values)
        tied = sum(value == cutoff for value in values)
        probability = (k - above) / tied
        return [1.0 if v > cutoff else probability if v == cutoff else 0.0
                for v in values]

    return math.fsum(p * a for p, a in zip(_top(pred), _top(act), strict=True)) / k


def mean_rank_displacement(
    predicted: Sequence[Real], actual: Sequence[Real]
) -> float | None:
    """Mean absolute difference in rank position between proxy and criterion."""
    pred, act = _paired(predicted, actual, name="mean_rank_displacement")
    if len(pred) < 2:
        return None
    pred_ranks = average_ranks(pred)
    act_ranks = average_ranks(act)
    return _mean([abs(a - b) for a, b in zip(pred_ranks, act_ranks, strict=True)])


# ---------------------------------------------------------------------------
# generalization splits
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Split:
    """One train / validation / test partition over unit names."""

    name: str
    train: tuple[str, ...]
    validation: tuple[str, ...]
    test: tuple[str, ...]


def leave_one_group_out(
    units: Sequence[str], group_of: Mapping[str, str]
) -> tuple[Split, ...]:
    """Hold out one whole group at a time.

    This is the split that matches the claim "screen a *new* agent or judge
    family without fresh labels": the held-out group is unseen at fit time, so
    a proxy that only works in-panel fails here.  Splits that hold out items or
    rubric passes while keeping every group in both halves do not test that
    claim, however they are labelled.
    """
    missing = [unit for unit in units if unit not in group_of]
    if missing:
        raise KeyError(f"units without a group assignment: {sorted(missing)}")
    groups = sorted({group_of[unit] for unit in units})
    if len(groups) < 2:
        raise ValueError("leave_one_group_out needs at least two distinct groups")
    splits: list[Split] = []
    for held in groups:
        test = tuple(u for u in units if group_of[u] == held)
        train = tuple(u for u in units if group_of[u] != held)
        splits.append(Split(name=f"holdout:{held}", train=train, validation=(), test=test))
    return tuple(splits)


def grouped_three_way_split(
    units: Sequence[str],
    group_of: Mapping[str, str],
    *,
    validation_groups: int = 1,
    test_groups: int = 1,
    seed: int = _DEFAULT_SEED,
) -> Split:
    """Partition whole groups into train / validation / test.

    Groups, not units, are partitioned, so no group appears on both sides of the
    boundary.  Use validation for choosing the index form and every other free
    parameter, and open test exactly once.
    """
    missing = [unit for unit in units if unit not in group_of]
    if missing:
        raise KeyError(f"units without a group assignment: {sorted(missing)}")
    groups = sorted({group_of[unit] for unit in units})
    if len(groups) < validation_groups + test_groups + 1:
        raise ValueError(
            f"need at least {validation_groups + test_groups + 1} groups for a "
            f"three-way split; got {len(groups)}"
        )
    rng = random.Random(seed)
    shuffled = list(groups)
    rng.shuffle(shuffled)
    test_set = set(shuffled[:test_groups])
    validation_set = set(shuffled[test_groups : test_groups + validation_groups])

    def _members(selector: Callable[[str], bool]) -> tuple[str, ...]:
        return tuple(u for u in units if selector(group_of[u]))

    return Split(
        name="grouped-three-way",
        train=_members(lambda g: g not in test_set and g not in validation_set),
        validation=_members(lambda g: g in validation_set),
        test=_members(lambda g: g in test_set),
    )


# ---------------------------------------------------------------------------
# top-level validation report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PooledHoldoutReport:
    """Cross-validated criterion validity pooled over leave-one-group-out folds.

    Per-fold correlations are unusable when groups are few, because each fold
    holds out only one group's units: four agent families give four folds of a
    handful of units each, and a correlation over that many points can only
    take a few discrete values.  Pooling fixes the arithmetic without weakening
    the protocol.  Every prediction here still comes from a calibration that
    never saw the predicted unit's group, so the pooled correlation is a
    genuine held-out number, computed once over the whole panel.
    """

    units: tuple[str, ...]
    predicted: tuple[float, ...]
    actual: tuple[float, ...]
    correlations: dict[str, Estimate]
    pairwise_rank_accuracy: float | None
    n_folds: int
    skipped_units: tuple[str, ...]
    power: PowerReport
    status: str
    metric_version: str = VALIDATION_VERSION

    @property
    def headline(self) -> Estimate | None:
        return self.correlations.get("spearman")


def _fit_linear(
    x: Sequence[float], y: Sequence[float]
) -> tuple[float, float] | None:
    """Ordinary least squares slope and intercept, or ``None`` if degenerate."""
    n = len(x)
    if n < 2:
        return None
    mx, my = _mean(x), _mean(y)
    sxx = math.fsum((v - mx) ** 2 for v in x)
    if sxx <= 0.0:
        return None
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True))
    slope = sxy / sxx
    return slope, my - slope * mx


def pooled_leave_one_group_out(
    pti_by_unit: Mapping[str, Real],
    ti_by_unit: Mapping[str, Real | None],
    group_of: Mapping[str, str],
    *,
    methods: Sequence[str] | None = None,
    n_items_per_unit: int | None = None,
    resamples: int = DEFAULT_BOOTSTRAP,
    seed: int = _DEFAULT_SEED,
    min_panel: int = MIN_TRUSTWORTHY_PANEL,
) -> PooledHoldoutReport:
    """Predict each group's ``TI_m`` from a calibration fit on the other groups.

    For every group in turn a linear calibration from ``PTI_p`` to ``TI_m`` is
    fit on all *other* groups and applied to the held-out group.  Predictions
    are pooled across folds and correlated against the true criterion once.

    This is the estimate that answers the operative question: shown a judge
    family it has never seen, does the proxy place it correctly?  A panel that
    scores well in-sample and poorly here has a proxy that memorised the panel
    rather than a screening instrument.

    Units whose fold has a degenerate training set, or that lack a criterion
    value, are reported in ``skipped_units`` rather than silently dropped.
    """
    usable = [
        unit
        for unit in sorted(set(pti_by_unit) & set(ti_by_unit) & set(group_of))
        if ti_by_unit[unit] is not None
    ]
    groups = sorted({group_of[unit] for unit in usable})
    if len(groups) < 2:
        raise ValueError("pooled_leave_one_group_out needs at least two groups")

    units: list[str] = []
    predicted: list[float] = []
    actual: list[float] = []
    skipped: list[str] = []

    for held in groups:
        train = [u for u in usable if group_of[u] != held]
        test = [u for u in usable if group_of[u] == held]
        fit = _fit_linear(
            [float(pti_by_unit[u]) for u in train],
            [float(ti_by_unit[u]) for u in train],  # type: ignore[arg-type]
        )
        if fit is None:
            skipped.extend(test)
            continue
        slope, intercept = fit
        for unit in test:
            units.append(unit)
            predicted.append(slope * float(pti_by_unit[unit]) + intercept)
            actual.append(float(ti_by_unit[unit]))  # type: ignore[arg-type]

    if len(units) < 3:
        return PooledHoldoutReport(
            units=tuple(units),
            predicted=tuple(predicted),
            actual=tuple(actual),
            correlations={},
            pairwise_rank_accuracy=None,
            n_folds=len(groups),
            skipped_units=tuple(skipped),
            power=resolving_power(
                actual,
                n_items_per_unit=n_items_per_unit,
                predictor_values=predicted,
                min_panel=min_panel,
            ),
            status=NOT_COMPUTABLE,
        )

    correlations = correlation_suite(
        predicted, actual, methods=methods, resamples=resamples, seed=seed
    )
    spearman_point = (
        correlations["spearman"].value if "spearman" in correlations else None
    )
    power = resolving_power(
        actual,
        n_items_per_unit=n_items_per_unit,
        observed_rho=spearman_point,
        predictor_values=predicted,
        min_panel=min_panel,
    )
    return PooledHoldoutReport(
        units=tuple(units),
        predicted=tuple(predicted),
        actual=tuple(actual),
        correlations=correlations,
        pairwise_rank_accuracy=pairwise_rank_accuracy(predicted, actual),
        n_folds=len(groups),
        skipped_units=tuple(skipped),
        power=power,
        status=UNDERPOWERED if power.underpowered else COMPUTED,
    )


@dataclass(frozen=True)
class ValidationReport:
    """Does ``PTI_p`` predict ``TI_m`` on this panel?"""

    split_name: str
    units: tuple[str, ...]
    correlations: dict[str, Estimate]
    pairwise_rank_accuracy: float | None
    top_k_overlap: float | None
    mean_rank_displacement: float | None
    power: PowerReport
    ceiling: CeilingReport | None
    disattenuated: dict[str, float | None]
    status: str
    metric_version: str = VALIDATION_VERSION

    @property
    def headline(self) -> Estimate | None:
        """Spearman, the rank criterion the leaderboard claim rests on."""
        return self.correlations.get("spearman")

    def summary_lines(self) -> tuple[str, ...]:  # pragma: no cover - display helper
        lines = [f"[{self.split_name}] n_units={len(self.units)} status={self.status}"]
        lines.extend(f"  {estimate}" for estimate in self.correlations.values())
        if self.pairwise_rank_accuracy is not None:
            lines.append(f"  pairwise_rank_accuracy={self.pairwise_rank_accuracy:.3f}")
        for note in self.power.notes:
            lines.append(f"  ! {note}")
        return tuple(lines)


def validate_pti(
    pti_by_unit: Mapping[str, Real],
    ti_by_unit: Mapping[str, Real | None],
    *,
    split_name: str = "all",
    methods: Sequence[str] | None = None,
    top_k: int = 3,
    n_items_per_unit: int | None = None,
    ceiling: CeilingReport | None = None,
    resamples: int = DEFAULT_BOOTSTRAP,
    seed: int = _DEFAULT_SEED,
    min_panel: int = MIN_TRUSTWORTHY_PANEL,
) -> ValidationReport:
    """Correlate a label-free proxy against the human-grounded criterion.

    Units present in only one mapping, or whose ``TI_m`` is ``None``, are
    dropped and excluded from ``units``; dropping is silent in the return value
    but visible as a reduced ``n_units``, which feeds the power check.

    The returned status is ``UNDERPOWERED`` whenever the design cannot support
    the claim, even if the point estimate looks strong.  That is the intended
    behaviour: on a panel this size a high correlation is not evidence, and the
    report should not let it read as such.
    """
    shared = [
        unit
        for unit in sorted(set(pti_by_unit) & set(ti_by_unit))
        if ti_by_unit[unit] is not None
    ]
    proxy = [float(pti_by_unit[u]) for u in shared]
    criterion = [float(ti_by_unit[u]) for u in shared]  # type: ignore[arg-type]

    if len(shared) < 3:
        return ValidationReport(
            split_name=split_name,
            units=tuple(shared),
            correlations={},
            pairwise_rank_accuracy=None,
            top_k_overlap=None,
            mean_rank_displacement=None,
            power=resolving_power(
                criterion,
                n_items_per_unit=n_items_per_unit,
                predictor_values=proxy,
                min_panel=min_panel,
            ),
            ceiling=ceiling,
            disattenuated={},
            status=NOT_COMPUTABLE,
        )

    correlations = correlation_suite(
        proxy, criterion, methods=methods, resamples=resamples, seed=seed
    )
    spearman_point = correlations["spearman"].value if "spearman" in correlations else None
    power = resolving_power(
        criterion,
        n_items_per_unit=n_items_per_unit,
        observed_rho=spearman_point,
        predictor_values=proxy,
        min_panel=min_panel,
    )

    # Item-label reliability is not the reliability of judge-level criteria.
    # Keep the supplied diagnostic, but never silently correct these outer
    # correlations (especially rank/CCC statistics) using that different scale.
    disattenuated: dict[str, float | None] = {}

    return ValidationReport(
        split_name=split_name,
        units=tuple(shared),
        correlations=correlations,
        pairwise_rank_accuracy=pairwise_rank_accuracy(proxy, criterion),
        top_k_overlap=top_k_overlap(proxy, criterion, min(top_k, len(shared))),
        mean_rank_displacement=mean_rank_displacement(proxy, criterion),
        power=power,
        ceiling=ceiling,
        disattenuated=disattenuated,
        status=UNDERPOWERED if power.underpowered else COMPUTED,
    )


def validate_pti_across_splits(
    pti_by_unit: Mapping[str, Real],
    ti_by_unit: Mapping[str, Real | None],
    splits: Sequence[Split],
    *,
    methods: Sequence[str] | None = None,
    n_items_per_unit: int | None = None,
    ceiling: CeilingReport | None = None,
    resamples: int = DEFAULT_BOOTSTRAP,
    seed: int = _DEFAULT_SEED,
) -> dict[str, dict[str, ValidationReport]]:
    """Run :func:`validate_pti` on each portion of each split.

    Returns ``{split_name: {"train"|"validation"|"test": report}}``, omitting
    empty portions.  The train report is a pipeline sanity check: a negative
    correlation there means a bug, not a finding.  Only the test report speaks
    to generalization, and only if it is opened once.
    """
    out: dict[str, dict[str, ValidationReport]] = {}
    for split in splits:
        portions = {
            "train": split.train,
            "validation": split.validation,
            "test": split.test,
        }
        per_split: dict[str, ValidationReport] = {}
        for portion, members in portions.items():
            if not members:
                continue
            subset = set(members)
            per_split[portion] = validate_pti(
                {k: v for k, v in pti_by_unit.items() if k in subset},
                {k: v for k, v in ti_by_unit.items() if k in subset},
                split_name=f"{split.name}/{portion}",
                methods=methods,
                n_items_per_unit=n_items_per_unit,
                ceiling=ceiling,
                resamples=resamples,
                seed=seed,
            )
        out[split.name] = per_split
    return out


__all__ = [
    "COMPUTED",
    "CORRELATION_FUNCTIONS",
    "DEFAULT_BOOTSTRAP",
    "MAX_PREDICTOR_TIE_FRACTION",
    "MIN_TRUSTWORTHY_PANEL",
    "NOT_COMPUTABLE",
    "UNDERPOWERED",
    "VALIDATION_VERSION",
    "CeilingReport",
    "Estimate",
    "IccResult",
    "PooledHoldoutReport",
    "PowerReport",
    "Split",
    "TrustIndex",
    "ValidationReport",
    "attenuation_ceiling",
    "bootstrap_ci",
    "ceiling_report",
    "compute_ti_m",
    "correlation_se",
    "correlation_suite",
    "disattenuate",
    "fisher_ci",
    "grouped_three_way_split",
    "icc",
    "leave_one_group_out",
    "lin_ccc",
    "mean_rank_displacement",
    "mean_within_item_std",
    "min_units_for_ci_width",
    "pairwise_rank_accuracy",
    "pearson_r",
    "pooled_leave_one_group_out",
    "predictor_tie_fraction",
    "resolving_power",
    "spearman_brown",
    "ti_2prime",
    "ti_m1",
    "top_k_overlap",
    "validate_pti",
    "validate_pti_across_splits",
]
