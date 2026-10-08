"""Pure numerical adaptations of total-variation information for scalar scores.

The functions in this module intentionally know nothing about experiments, files, or
human outcomes.  Experiment 46 supplies eligibility and coverage rules around them.
"""
from __future__ import annotations

from collections import Counter
from itertools import permutations
import math
import statistics
from typing import Mapping, Sequence


TIE_TOLERANCE = 1e-12
N_BINS = 5


def score_bin(score: float) -> int:
    """Place a finite [0, 1] score in one of the protocol's five fixed bins."""
    if not math.isfinite(score) or score < 0.0 or score > 1.0:
        raise ValueError(f"score must be finite and in [0, 1], got {score!r}")
    return min(4, math.floor(5.0 * score))


def total_variation(p: Mapping[object, float], q: Mapping[object, float]) -> float:
    """Return 0.5 * L1 for finite probability mappings, checking normalization."""
    keys = set(p) | set(q)
    if any(v < -TIE_TOLERANCE or not math.isfinite(v) for v in (*p.values(), *q.values())):
        raise ValueError("probabilities must be finite and non-negative")
    if not math.isclose(sum(p.values()), 1.0, abs_tol=1e-10) or not math.isclose(sum(q.values()), 1.0, abs_tol=1e-10):
        raise ValueError("probability mappings must each sum to one")
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def semantic_auc_task(semantic_gaps: Sequence[float], formatting_gaps: Sequence[float]) -> float:
    """Return 2*AUC-1 for signed semantic versus absolute formatting changes."""
    if not semantic_gaps or not formatting_gaps:
        raise ValueError("semantic and formatting gaps must both be nonempty")
    wins = 0.0
    for semantic in semantic_gaps:
        for formatting in formatting_gaps:
            if semantic > formatting + TIE_TOLERANCE:
                wins += 1.0
            elif abs(semantic - formatting) <= TIE_TOLERANCE:
                wins += 0.5
    return 2.0 * wins / (len(semantic_gaps) * len(formatting_gaps)) - 1.0


def semantic_acceptance_gaps(semantic_gaps: Sequence[float], formatting_gaps: Sequence[float], thresholds: Sequence[float]) -> dict[float, float]:
    """Fixed-threshold semantic-minus-format acceptance gaps for one task."""
    if not semantic_gaps or not formatting_gaps:
        raise ValueError("semantic and formatting gaps must both be nonempty")
    return {
        float(t): sum(x > t for x in semantic_gaps) / len(semantic_gaps) - sum(x > t for x in formatting_gaps) / len(formatting_gaps)
        for t in thresholds
    }


def _histogram(values: Sequence[float]) -> dict[int, float]:
    if not values:
        raise ValueError("empty score sequence")
    counts = Counter(score_bin(float(v)) for v in values)
    return {b: counts[b] / len(values) for b in range(N_BINS)}


def repeat_tvd_task(candidate_repeats: Mapping[str, Mapping[int, float]], expected_repeats: Sequence[int] = (1, 2, 3)) -> float:
    """Empirical repeat dependence, averaged equally over ordered repeat pairs.

    Each candidate contributes uniformly to both joint and product distributions;
    equal candidate indices are deliberately retained in the product pairing.
    """
    candidates = sorted(candidate_repeats)
    if len(candidates) < 2:
        raise ValueError("at least two candidates are required")
    repeats = tuple(expected_repeats)
    if len(set(repeats)) != len(repeats) or len(repeats) < 2:
        raise ValueError("repeat indices must be distinct and contain at least two values")
    if any(set(candidate_repeats[c]) != set(repeats) for c in candidates):
        raise ValueError("every candidate must have exactly the declared repeat indices")
    joint: Counter[tuple[int, int]] = Counter()
    product: Counter[tuple[int, int]] = Counter()
    ordered = list(permutations(repeats, 2))
    candidate_count = len(candidates)
    for left, right in ordered:
        for candidate in candidates:
            joint[(score_bin(candidate_repeats[candidate][left]), score_bin(candidate_repeats[candidate][right]))] += 1.0 / (len(ordered) * candidate_count)
        left_hist = _histogram([candidate_repeats[c][left] for c in candidates])
        right_hist = _histogram([candidate_repeats[c][right] for c in candidates])
        for a in range(N_BINS):
            for b in range(N_BINS):
                product[(a, b)] += left_hist[a] * right_hist[b] / len(ordered)
    # The rational mixture weights can leave a one-unit-last-place artifact (for
    # example 0.49999999999999994 for the balanced binary control).  Canonicalize
    # far below the protocol's 1e-12 comparison tolerance so exact fixtures stay
    # exact without affecting a reported property value.
    return round(total_variation(joint, product), 15)


def complete_repeat_candidates(
    candidate_repeats: Mapping[str, Mapping[int, float]], expected_repeats: Sequence[int] = (1, 2, 3)
) -> tuple[dict[str, Mapping[int, float]], list[str]]:
    """Return exact-repeat candidates and the declared candidates excluded from a task.

    Experiment 46 declares a task before inspecting score availability.  Its repeat
    property may use a complete subset of that task's candidates, provided at least
    two have all three accepted repeats.  This helper deliberately does not impose
    that coverage threshold; the experiment layer owns the task-level rule.
    """
    repeats = tuple(expected_repeats)
    if len(set(repeats)) != len(repeats) or len(repeats) < 2:
        raise ValueError("repeat indices must be distinct and contain at least two values")
    complete = {candidate: values for candidate, values in candidate_repeats.items() if set(values) == set(repeats)}
    excluded = sorted(candidate for candidate in candidate_repeats if candidate not in complete)
    return complete, excluded


def deletion_tvd_task(level_repeats: Mapping[int, Sequence[float]]) -> dict[str, float]:
    """Return normalized information, orientation, and direction-gated value.

    Levels are equally weighted and scores within a level are uniformly weighted.
    """
    levels = sorted(level_repeats)
    if len(levels) < 2 or any(len(level_repeats[level]) < 2 for level in levels):
        raise ValueError("at least two levels with at least two repeats each are required")
    k = len(levels)
    joint: Counter[tuple[int, int]] = Counter()
    score_marginal: Counter[int] = Counter()
    for level in levels:
        values = level_repeats[level]
        for score in values:
            joint[(level, score_bin(float(score)))] += 1.0 / (k * len(values))
            score_marginal[score_bin(float(score))] += 1.0 / (k * len(values))
    product = {(level, bin_id): (1.0 / k) * score_marginal[bin_id] for level in levels for bin_id in range(N_BINS)}
    information = total_variation(joint, product) / (1.0 - 1.0 / k)
    medians = {level: statistics.median(level_repeats[level]) for level in levels}
    signs = []
    for earlier_index, earlier in enumerate(levels):
        for later in levels[earlier_index + 1 :]:
            difference = medians[earlier] - medians[later]
            signs.append(1.0 if difference > TIE_TOLERANCE else -1.0 if difference < -TIE_TOLERANCE else 0.0)
    orientation = sum(signs) / len(signs)
    return {"information": information, "orientation": orientation, "value": max(0.0, orientation) * information}


def gold_deletion_monotonicity(level_medians: Mapping[int, float]) -> float:
    """Historical C_ms_gold ladder quality, including the defined constant value zero."""
    levels = sorted(level_medians)
    values = [float(level_medians[level]) for level in levels]
    if len(values) < 2:
        raise ValueError("at least two levels are required")
    if all(abs(value - values[0]) <= TIE_TOLERANCE for value in values[1:]):
        return 0.0
    # Tie-aware Spearman, written locally to keep this module dependency-free.
    def ranks(xs: Sequence[float]) -> list[float]:
        ordered = sorted(enumerate(xs), key=lambda pair: pair[1])
        out = [0.0] * len(xs)
        start = 0
        while start < len(ordered):
            end = start + 1
            while end < len(ordered) and abs(ordered[end][1] - ordered[start][1]) <= TIE_TOLERANCE:
                end += 1
            rank = (start + 1 + end) / 2.0
            for index, _ in ordered[start:end]:
                out[index] = rank
            start = end
        return out
    x, y = ranks([float(level) for level in levels]), ranks(values)
    mx, my = sum(x) / len(x), sum(y) / len(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    if denominator == 0.0:
        return 0.0
    return (1.0 - numerator / denominator) / 2.0
