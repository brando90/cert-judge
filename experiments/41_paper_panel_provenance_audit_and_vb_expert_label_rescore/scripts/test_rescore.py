#!/usr/bin/env python3
"""Offline tests for rescore.py's statistics (no model calls, no network)."""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rescore  # noqa: E402


def test_spearman_matches_scipy():
    rng = np.random.default_rng(0)
    for _ in range(20):
        n = rng.integers(3, 12)
        a = rng.normal(size=n)
        b = rng.normal(size=n)
        got = rescore.spearman(a, b)
        want = stats.spearmanr(a, b).statistic
        assert math.isclose(got, want, abs_tol=1e-9), (got, want)


def test_kendall_matches_scipy():
    rng = np.random.default_rng(1)
    for _ in range(20):
        n = rng.integers(3, 12)
        a = rng.normal(size=n)
        b = rng.normal(size=n)
        got = rescore.kendall(a, b)
        want = stats.kendalltau(a, b).statistic
        assert math.isclose(got, want, abs_tol=1e-9), (got, want)


def test_pearson_matches_scipy():
    rng = np.random.default_rng(2)
    for _ in range(20):
        n = rng.integers(3, 12)
        a = rng.normal(size=n)
        b = rng.normal(size=n)
        got = rescore.pearson(a, b)
        want = stats.pearsonr(a, b).statistic
        assert math.isclose(got, want, abs_tol=1e-9), (got, want)


def test_constant_input_returns_nan():
    a = np.array([1.0, 1.0, 1.0, 1.0])
    b = np.array([1.0, 2.0, 3.0, 4.0])
    assert math.isnan(rescore.spearman(a, b))
    assert math.isnan(rescore.pearson(a, b))
    assert math.isnan(rescore.kendall(a, b))


def test_exact_permutation_p_known_case():
    # Perfectly correlated data: observed |rho|=1 is the maximum possible, so only the identity
    # and reverse-identity permutations (if reverse also gives |rho|=1) can match or exceed it.
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([1.0, 2.0, 3.0, 4.0])
    p = rescore.exact_permutation_p(a, b)
    # For n=4, only 2 of the 4!=24 orderings give |rho|=1 (identity and full reversal).
    assert math.isclose(p, 2 / 24, abs_tol=1e-9), p


def test_exact_permutation_p_matches_brute_force():
    rng = np.random.default_rng(3)
    a = rng.normal(size=5)
    b = rng.normal(size=5)
    got = rescore.exact_permutation_p(a, b)
    obs = abs(rescore.spearman(a, b))
    ra = rescore.rankdata(a)
    rb = rescore.rankdata(b)
    cnt = tot = 0
    for perm in itertools.permutations(range(5)):
        tot += 1
        r = rescore.pearson(ra, [rb[i] for i in perm])
        if abs(r) >= obs - 1e-12:
            cnt += 1
    assert math.isclose(got, cnt / tot, abs_tol=1e-9)


def test_bootstrap_reproducible_with_seed():
    # Build a tiny synthetic family_scores / label_map / item_filter and confirm that two
    # independent RNGs seeded identically give identical bootstrap distributions.
    items = [("g1.lean", f"g1__a{i}.lean") for i in range(3)] + [
        ("g2.lean", f"g2__a{i}.lean") for i in range(3)
    ]
    rng_vals = np.random.default_rng(123)
    label_map = {it: float(v) for it, v in zip(items, rng_vals.normal(size=len(items)))}
    family_scores = {}
    for j in range(5):
        rv = np.random.default_rng(1000 + j)
        family_scores[f"judge{j}"] = {it: float(v) for it, v in zip(items, rv.normal(size=len(items)))}
    ti_vector = np.linspace(0, 1, 5)
    item_filter = set(items)

    boot1 = rescore.task_clustered_bootstrap(
        family_scores, list(family_scores.keys()), label_map, item_filter, ti_vector, np.random.default_rng(999)
    )
    boot2 = rescore.task_clustered_bootstrap(
        family_scores, list(family_scores.keys()), label_map, item_filter, ti_vector, np.random.default_rng(999)
    )
    assert len(boot1) == len(boot2)
    assert np.allclose(boot1, boot2)


def run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    run_all()
