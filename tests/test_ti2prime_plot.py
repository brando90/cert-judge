"""Tests for cert_judge.ti2prime_plot -- the TI_2' wrapper over uutils' Validity-Stability score.

Requires uutils importable (py_src/uutils on the path), matching this
module's own runtime dependency -- skipped otherwise rather than failing the
whole suite, since cert_judge's core scoring package stays importable without
uutils (see py_src/cert_judge/__init__.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

pytest.importorskip("uutils")

from cert_judge.ti2prime_plot import compute_ti2prime, plot_ti2prime_scatter  # noqa: E402


def _perfectly_aligned_stable_data():
    judge = [0.1, 0.4, 0.6, 0.9, 0.2, 0.7, 0.5, 0.3]
    human = [0.0, 0.3, 0.5, 1.0, 0.1, 0.8, 0.4, 0.2]
    repeats = {i: [v, v, v] for i, v in enumerate(judge)}
    return judge, human, repeats


def test_ti2prime_perfect_alignment_and_stability_is_one():
    judge, human, repeats = _perfectly_aligned_stable_data()
    result = compute_ti2prime(judge, human, repeats)
    assert result.vs_score == pytest.approx(1.0, abs=1e-9)
    assert result.validity == pytest.approx(1.0, abs=1e-9)
    assert result.stability == pytest.approx(1.0, abs=1e-9)


def test_ti2prime_matches_hand_computed_formula():
    # 5 items, deliberately imperfect correlation, explicit stability term so
    # the expected number is easy to hand-check: TI_2' = (corr * (1-std))^0.5.
    judge = [0.1, 0.5, 0.3, 0.9, 0.6]
    human = [0.2, 0.4, 0.3, 0.8, 0.5]
    result = compute_ti2prime(judge, human, std=0.1)
    expected = (result.validity * 0.9) ** 0.5
    assert result.vs_score == pytest.approx(expected, abs=1e-9)
    assert result.stability == pytest.approx(0.9, abs=1e-9)


def test_ti2prime_negative_correlation_clips_to_zero():
    judge = [0.9, 0.7, 0.5, 0.3, 0.1]
    human = [0.1, 0.3, 0.5, 0.7, 0.9]  # perfectly anti-correlated
    result = compute_ti2prime(judge, human, std=0.0)
    assert result.validity_raw == pytest.approx(-1.0, abs=1e-9)
    assert result.validity == 0.0  # clip_[0,1], never negative
    assert result.vs_score == 0.0  # zero-annihilating


def test_ti2prime_requires_a_stability_term():
    judge = [0.1, 0.5, 0.3, 0.9, 0.6]
    human = [0.2, 0.4, 0.3, 0.8, 0.5]
    with pytest.raises(ValueError, match="stability"):
        compute_ti2prime(judge, human)  # no `std=` and no `repeat_scores_by_item=`


def test_ti2prime_legend_uses_paper_notation():
    judge, human, repeats = _perfectly_aligned_stable_data()
    result = compute_ti2prime(judge, human, repeats)
    assert result.formula_str(symbol=r"\mathrm{TI}_{2'}").startswith(r"$\mathrm{TI}_{2'}")


def test_plot_ti2prime_scatter_builds_headlessly():
    judge, human, repeats = _perfectly_aligned_stable_data()
    fig = plot_ti2prime_scatter(judge, human, repeats, judge_label="unit-test-judge")
    assert fig is not None
    matplotlib.pyplot.close(fig)


def test_plot_ti2prime_scatter_writes_files_with_dots_in_the_stem(tmp_path):
    # Regression test: Path.with_suffix() mangles a stem containing a dot
    # (e.g. a model name like "gpt-5.3-codex"), silently writing to the
    # wrong filename. See uutils/plot/validity_stability_scatter.py.
    judge, human, repeats = _perfectly_aligned_stable_data()
    out_stem = tmp_path / "ti2prime_scatter_gpt-5.3-codex_P4_CHECKLIST"
    plot_ti2prime_scatter(judge, human, repeats, out=out_stem)
    assert (tmp_path / "ti2prime_scatter_gpt-5.3-codex_P4_CHECKLIST.png").exists()
    assert (tmp_path / "ti2prime_scatter_gpt-5.3-codex_P4_CHECKLIST.pdf").exists()
