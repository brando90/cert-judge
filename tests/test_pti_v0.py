"""Conformance and edge-case tests for the canonical PTI-v0 core."""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.pti_v0 import (
    COMPUTED,
    NOT_COMPUTABLE,
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
    pti_v0,
    repeat_instability,
    spearman_rho,
    stable_geometric_mean,
)

VECTORS = json.loads(
    (REPO_ROOT / "tests" / "data" / "PTI_V0_TEST_VECTORS_v4.json").read_text()
)
TOL = VECTORS["absolute_tolerance"]


@pytest.mark.parametrize(
    "vector", VECTORS["geometric_mean_vectors"], ids=lambda v: v["name"]
)
def test_geometric_mean_vectors(vector: dict) -> None:
    assert stable_geometric_mean(vector["factors"]) == pytest.approx(
        vector["expected"], abs=TOL
    )


@pytest.mark.parametrize("vector", VECTORS["ladder_vectors"], ids=lambda v: v["name"])
def test_ladder_vectors(vector: dict) -> None:
    result = ladder_factor(vector["scores"])
    assert result.constant_ladder is vector["expected_constant"]
    if vector.get("expected_rho") is None:
        assert result.rho is None
    else:
        assert result.rho == pytest.approx(vector["expected_rho"], abs=TOL)
    assert result.correlation_quality == pytest.approx(
        vector["expected_quality"], abs=TOL
    )
    assert result.factor == pytest.approx(vector["expected_factor"], abs=TOL)
    if "expected_instability" in vector:
        assert result.instability == pytest.approx(
            vector["expected_instability"], abs=TOL
        )
    if "expected_medians" in vector:
        assert result.medians == pytest.approx(vector["expected_medians"], abs=TOL)


@pytest.mark.parametrize("vector", VECTORS["coverage_vectors"], ids=lambda v: v["name"])
def test_coverage_vectors(vector: dict) -> None:
    result = aggregate_property_factors(
        vector["factors"],
        required_count=vector["required_count"],
        min_coverage=vector["min_coverage"],
        constant_ladder_count=vector["constant_ladder_count"],
    )
    assert result.status == vector["expected_status"]
    assert result.coverage == pytest.approx(vector["expected_coverage"], abs=TOL)
    if vector["expected_value"] is None:
        assert result.value is None
    else:
        assert result.value == pytest.approx(vector["expected_value"], abs=TOL)


def test_zero_rank_signal_permutation() -> None:
    rho = spearman_rho([0, 1, 2, 3, 4], [0, 4, 3, 2, 1])
    assert rho == pytest.approx(0.0, abs=TOL)
    assert ladder_quality_from_rho(rho or 0.0) == pytest.approx(0.5, abs=TOL)


def test_average_tie_ranks_and_kendall_tau_b() -> None:
    assert average_ranks([10, 20, 20, 40]) == pytest.approx((1.0, 2.5, 2.5, 4.0))
    assert kendall_tau_b([0, 1, 2, 3], [4, 3, 2, 1]) == -1.0
    assert kendall_tau_b([0, 1, 2], [0.4, 0.4, 0.4]) is None


def test_single_repeat_uses_quality_without_sqrt() -> None:
    result = ladder_factor([[1.0], [0.7], [0.6], [0.2]])
    assert result.instability is None
    assert not result.stability_observed
    assert result.factor == result.correlation_quality


def test_repeat_instability_is_within_level_population_sd() -> None:
    assert repeat_instability([[0.0, 1.0], [0.0, 1.0]]) == 1.0
    assert repeat_instability([[0.4], [0.2]]) is None


def test_constant_ladder_remains_in_property_as_zero() -> None:
    ideal = ladder_factor([[1.0], [0.5], [0.0]])
    constant = ladder_factor([[0.4], [0.4], [0.4]])
    result = aggregate_ladder_property([ideal, constant], required_count=2)
    assert result.status == COMPUTED
    assert result.value == 0.0
    assert result.constant_ladder_count == 1
    assert result.zero_count == 1


def test_tiny_but_nonzero_ladder_difference_is_not_constant() -> None:
    result = ladder_factor([[0.4], [0.4 + 1e-14], [0.4]])

    assert result.constant_ladder is False
    assert result.rho is not None


def test_missing_ladder_score_is_not_zero() -> None:
    ideal = ladder_factor([[1.0], [0.5], [0.0]])
    result = aggregate_ladder_property([ideal], required_count=2, min_coverage=1.0)
    assert result.status == NOT_COMPUTABLE
    assert result.value is None
    assert result.zero_count == 0


def test_equality_alpha_and_pti_formulas() -> None:
    assert equality_property([1.0, 0.8]) == pytest.approx(math.sqrt(0.8), abs=TOL)
    assert alpha_invariance_property([0.8], [0.6]) == pytest.approx(0.8, abs=TOL)
    assert pti_v0(1.0, 1.0, 1.0, 0.5) == pytest.approx(0.8408964152537145, abs=TOL)
    assert pti_three_property(1.0, 0.8, 0.6) == pytest.approx(
        (0.48) ** (1 / 3), abs=TOL
    )


def test_compute_pti_propagates_not_computable() -> None:
    computed = aggregate_property_factors([1.0], required_count=1)
    missing = aggregate_property_factors([], required_count=1)
    result = compute_pti(
        {"P_eq": computed, "P_bm": computed, "P_ms": missing, "P_eqalpha": computed}
    )
    assert result.status == NOT_COMPUTABLE
    assert result.value is None
    assert result.missing_properties == ("P_ms",)


@pytest.mark.parametrize(
    "values",
    [[], [1.0, float("nan")], [1.1, 0.9], [-0.1, 0.9]],
)
def test_geometric_mean_rejects_invalid_inputs(values: list[float]) -> None:
    with pytest.raises(ValueError):
        stable_geometric_mean(values)


def test_ladder_rejects_bad_shapes_levels_and_ranges() -> None:
    with pytest.raises(ValueError, match="same repeat count"):
        ladder_factor([[0.9, 0.8], [0.5]])
    with pytest.raises(ValueError, match="strictly increasing"):
        ladder_factor([[0.9], [0.5], [0.1]], levels=[0, 2, 1])
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        median_over_repeats([[4.0], [3.0]])


def test_randomized_tie_heavy_correlations_match_scipy() -> None:
    scipy_stats = pytest.importorskip("scipy.stats")
    generator = random.Random(0)
    for _ in range(200):
        size = generator.randint(3, 20)
        x = [float(index) for index in range(size)]
        y = [float(generator.randrange(5)) for _ in range(size)]
        if len(set(y)) == 1:
            continue
        expected_rho = float(scipy_stats.spearmanr(x, y).statistic)
        expected_tau = float(scipy_stats.kendalltau(x, y, variant="b").statistic)
        assert spearman_rho(x, y) == pytest.approx(expected_rho, abs=1e-12)
        assert kendall_tau_b(x, y) == pytest.approx(expected_tau, abs=1e-12)
