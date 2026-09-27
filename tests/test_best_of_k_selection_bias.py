import importlib.util
import itertools
import json
import statistics
import subprocess
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "experiments/archive/39_best_of_k_judge_selection_bias_validation_set/analysis/best_of_k_selection_bias.py"
spec = importlib.util.spec_from_file_location("best_of_k_selection_bias_test", path)
sb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sb)


def test_spearman_matches_scipy_with_ties_and_broadcasting():
    rng = np.random.default_rng(0)
    x = rng.integers(0, 4, size=(5, 30)).astype(float)
    y = rng.integers(0, 6, size=30).astype(float)
    got = sb.spearman_last_axis(x, y[None, :])
    want = [stats.spearmanr(row, y).statistic for row in x]
    assert got == pytest.approx(want, abs=1e-12)
    z = sb.standardized_ranks(x) @ sb.standardized_ranks(y)
    assert z == pytest.approx(want, abs=1e-12)


def test_spearman_is_nan_for_constant_vectors():
    assert np.isnan(sb.spearman_last_axis(np.ones(6), np.arange(6.0)))


def test_block_permutation_moves_whole_problems():
    blocks = [np.arange(3 * i, 3 * i + 3) for i in range(8)]
    idx = sb.block_permutation(blocks, np.random.default_rng(1))
    assert sorted(idx) == list(range(24))
    for target in blocks:
        sources = {int(j) // 3 for j in idx[target]}
        assert len(sources) == 1


def test_block_permutation_null_is_centered():
    rng = np.random.default_rng(2)
    blocks = [np.arange(3 * i, 3 * i + 3) for i in range(24)]
    labels = np.repeat(rng.normal(size=24), 3) + rng.normal(size=72)
    judge = labels + rng.normal(size=72)
    rhos = [sb.spearman_last_axis(judge, labels[sb.block_permutation(blocks, rng)]) for _ in range(2000)]
    assert abs(np.mean(rhos)) < 0.02


def test_nested_best_uses_prefixes_and_skips_undefined():
    values = np.array([[0.1, np.nan, 0.5, 0.2], [np.nan, np.nan, 0.3, 0.9]])
    best = sb.nested_best(values, (1, 2, 3, 4))
    assert best[1].tolist() == [0, -1]
    assert best[2].tolist() == [0, -1]
    assert best[3].tolist() == [2, 2]
    assert best[4].tolist() == [2, 3]


def test_discretize_reproduces_the_empirical_marginal():
    observed = np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5], dtype=float)
    cuts, levels = sb.cut_points(observed)
    draws = sb.discretize(np.random.default_rng(3).standard_normal(200_000), cuts, levels)
    want = np.unique(observed, return_counts=True)[1] / len(observed)
    got = np.array([np.mean(draws == v) for v in levels])
    assert got == pytest.approx(want, abs=0.005)


def test_icc_variants_agree_and_hit_known_values():
    rng = np.random.default_rng(4)
    values = np.repeat(rng.normal(size=10), 3) + 0.5 * rng.normal(size=30)
    groups = np.repeat(np.arange(10), 3)
    assert sb.icc_oneway(values, groups) == pytest.approx(float(sb.icc_oneway_batched(values.reshape(10, 3))))
    assert sb.icc_oneway(np.repeat(np.arange(10.0), 3), groups) == pytest.approx(1.0)


def test_exact_permutation_table_matches_brute_force():
    rng = np.random.default_rng(5)
    forms = {f: rng.normal(size=6) for f in sb.FORMS}
    target = rng.normal(size=6)
    res = sb.exact_permutation_table(forms, target)
    obs = {f: stats.spearmanr(x, target).statistic for f, x in forms.items()}
    perms = [np.array(p) for p in itertools.permutations(range(6))]
    permuted = [{f: stats.spearmanr(x, target[p]).statistic for f, x in forms.items()} for p in perms]
    one = np.mean([d["tivar"] >= obs["tivar"] - 1e-12 for d in permuted])
    adj = np.mean([max(d.values()) >= obs["tivar"] - 1e-12 for d in permuted])
    two = np.mean([abs(d["tivar"]) >= abs(obs["tivar"]) - 1e-12 for d in permuted])
    assert res["n_permutations"] == 720
    assert res["p_tivar_one_sided"] == pytest.approx(one)
    assert res["p_tivar_adjusted_one_sided"] == pytest.approx(adj)
    assert res["p_tivar_two_sided"] == pytest.approx(two)
    assert res["p_tivar_adjusted_one_sided"] >= res["p_tivar_one_sided"]


def test_explain_deviation_detects_float_ties():
    # Equal decimal means of different repeat multisets differ in the last bit of the binary mean.
    repeats = [[0.7, 0.7, 0.8], [0.6, 0.8, 0.8], [0.1, 0.1, 0.1], [0.9, 0.9, 0.9], [0.4, 0.5, 0.5], [0.3, 0.3, 0.3]]
    float_means = np.array([statistics.mean(r) for r in repeats])
    assert float_means[0] != float_means[1]
    recorded = np.round(float_means, 6)
    labels = {v: np.array([4.0, 3.0, 1.0, 5.0, 2.0, 2.0]) for v in sb.VIEWS}
    frozen = {v: float(stats.spearmanr(float_means, labels[v]).statistic) for v in sb.VIEWS}
    cfg = {"scores": recorded, "repeats": repeats,
           "rho": {v: float(stats.spearmanr(recorded, labels[v]).statistic) for v in sb.VIEWS}}
    assert max(abs(cfg["rho"][v] - frozen[v]) for v in sb.VIEWS) > 1e-6
    assert sb.explain_deviation(cfg, labels, [], frozen) == "float_tie(statistics.mean)"


def test_pool_and_reproduction_gate_on_frozen_data(tmp_path):
    commit = subprocess.run(["git", "cat-file", "-e", sb.OLD_AVG_LABELS[0] + "^{commit}"], cwd=ROOT, capture_output=True)
    if commit.returncode != 0:
        pytest.skip("historical label commit not in this clone; the gate fails closed there by design")
    assert sb.main(["--pool-only", "--out-dir", str(tmp_path)]) == 0
    gate = json.loads((tmp_path / "results/reproduction_gate.json").read_text())
    assert gate["passed"] and gate["paper_codex_all_match"]
    assert gate["n_kept"] == 109
    assert not any(k.startswith("unexplained") for k in gate["all_explanations"])
