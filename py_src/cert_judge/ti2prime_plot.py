"""
TI_2' scatter figure: cert-judge's instantiation of the generic
Validity-Stability construct (uutils.stats_uu.validity_stability), specialized
to judge-vs-human per-item alignment.

    TI_2'(aj) = ( clip_[0,1](Corr(judge_scores, human_scores)) * (1 - STD) )^0.5

`Corr` runs over items (the aligned human-annotated panel b') for one judge
configuration `aj`; `STD` is the judge-side repeat-instability conjunct --
variance under resampling the judge (repeats / prompt paraphrase), NOT the
spread of the judge's scores across items (see
uutils.stats_uu.validity_stability's module docstring for why). Source of
truth:
experiments/27_ti_plot_like_scatter_plots/cert_judge_notes/certjudge-revision-memo.md
Sec 1 ("Stability appears once on each side, measuring different things") and
paper_latex/ICLR_2027_submission/main.tex (TI_{2'} definition).

The general "correlation of a proxy to a target, discounted by the proxy's
own stability" math and plotting live in uutils
(uutils.stats_uu.validity_stability / uutils.plot.validity_stability_scatter,
"VS") because that construct has nothing to do with judges or Lean; this
module is only the cert-judge-specific notation on top (TI_2', judge/human
axis labels). The data loading specific to this repo's result files
(detail_rows.csv, aligned_panel_n75.tsv) lives in
experiments/27_ti_plot_like_scatter_plots/, not here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Optional, Sequence, Union

import matplotlib.pyplot as plt

from uutils.stats_uu.validity_stability import (
    ValidityStabilityResult,
    compute_validity_stability,
)
from uutils.plot.validity_stability_scatter import plot_validity_stability_scatter

# TI_2' is cert-judge's named instance of the generic Validity-Stability score.
TI2PrimeResult = ValidityStabilityResult
_TI2PRIME_SYMBOL = r"\mathrm{TI}_{2'}"


def compute_ti2prime(
    judge_scores: Sequence[float],
    human_scores: Sequence[float],
    repeat_scores_by_item: Optional[Mapping[object, Sequence[float]]] = None,
    *,
    std: Optional[float] = None,
    corr_method: str = "spearman",
) -> TI2PrimeResult:
    """TI_2'(aj) -- cert-judge's Validity-Stability instance. See module docstring."""
    return compute_validity_stability(
        judge_scores, human_scores, repeat_scores_by_item, std=std, corr_method=corr_method,
    )


def plot_ti2prime_scatter(
    judge_scores: Sequence[float],
    human_scores: Sequence[float],
    repeat_scores_by_item: Optional[Mapping[object, Sequence[float]]] = None,
    *,
    std: Optional[float] = None,
    corr_method: str = "spearman",
    judge_label: str = "",
    x_label: str = "Human score",
    y_label: str = "Judge score",
    show_diagonal: bool = False,
    show_calibration_gap: bool = False,
    n_boot: int = 2000,
    ax: Optional[plt.Axes] = None,
    legend_loc: str = "best",
    seed: int = 0,
    out: Optional[Union[str, Path]] = None,
) -> plt.Figure:
    """
    TI_2' scatter -- cert-judge's Validity-Stability instance. See module docstring.

    `show_diagonal` defaults False: judge (LLM rubric) and human (1-5 rubric)
    scores are on uncalibrated scales, and TI_2' is correlation-based --
    invariant to a level offset by construction -- so a y=x line would imply a
    calibration target the criterion does not claim. See
    uutils.plot.validity_stability_scatter's module docstring.
    """
    return plot_validity_stability_scatter(
        judge_scores, human_scores, repeat_scores_by_item,
        std=std, corr_method=corr_method, symbol=_TI2PRIME_SYMBOL, label=judge_label,
        x_label=x_label, y_label=y_label, show_diagonal=show_diagonal,
        show_calibration_gap=show_calibration_gap, n_boot=n_boot,
        ax=ax, legend_loc=legend_loc, seed=seed, out=out,
    )
