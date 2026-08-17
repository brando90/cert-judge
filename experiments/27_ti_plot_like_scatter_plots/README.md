# Exp27 — TI_2' scatter plot (reusable)

Reusable matplotlib figure for TI_2', the paper's per-judge human-alignment
criterion (`paper_latex/ICLR_2027_submission/main.tex`, TI_{2'} definition;
`cert_judge_notes/certjudge-revision-memo.md` Sec 1):

```
TI_2'(aj) = ( clip_[0,1](Corr(judge_scores, human_scores)) * (1 - STD) )^0.5
```

One judge configuration, one figure, mapped onto the paper's own m-ladder
(revision memo, "Figure elements map onto the m-ladder"):

| Element | Shows | Rung |
|---|---|---|
| Top/right marginal histograms (discrete-aware, tie-snapped -- **not** a KDE) | calibration gap; range restriction | m0 |
| Central panel: item positions (marker size = # tied items) | alignment, summarized by Spearman rho (+ Kendall tau-b under ties) | m1 |
| Per-position vertical error bars (mean judge repeat-std) | judge self-consistency | m2 |
| Info panel | decomposed `TI_2' = (rho * (1-sigma))^0.5` formula + bootstrap 95% CI on rho + calibration gap (Wasserstein) | — |

**Revision history worth knowing**: the first version of this figure used a
2D Gaussian KDE density wash instead of marginals, and drew a `y=x` reference
line. Both were wrong for this data and got removed after review: a smooth
2D density is the wrong estimator at n=72 over ~9 distinct human values (a
tie-heavy lattice, not a continuum) -- it can make a perfectly-aligned judge
and a shuffled one look visually similar, since shuffling leaves both
marginals unchanged while sending rho to zero. And `y=x` implied a
calibration target the metric doesn't claim: judge and human scores are on
uncalibrated scales, and TI_2' is correlation-based (level-invariant by
construction). See `cert_judge_notes/agent-prompt-bridge-plot.md`, "Revision
notes on the item-level figure already built," for the full critique.

No judge inference, no LLM calls, no spend: `run_ti2prime_demo.py` reuses
per-item judge scores and the audited human labels that already exist on disk
from the ICLR-2027 / workshop submission runs.

**Two diagnostics from that review, answered:**
1. *Which `std` is being computed?* Confirmed: the judge's repeat standard
   deviation (self-consistency across its 3 repeat calls), pooled across
   items -- never the across-item spread of the judge's mean scores. See
   `uutils.stats_uu.validity_stability`'s module docstring for why that
   distinction matters (an across-item measure would reward a judge that
   never varies its score regardless of item quality).
2. *Why does `random_r1` report `sigma = 0.00`?* By design, not a bug --
   confirmed in `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py:231-269`.
   The "random" baseline is a SHA256 hash of the judge id + item content
   (deterministic per item, reproducible across pipeline reruns), not a
   stateful RNG draw, so its 3 "repeats" are the same value 3 times by
   construction. It's random *across items* and stable *within* an item --
   a standard stable-noise-floor-control pattern, not an attempt to model a
   genuinely stochastic judge. Consequence: this control cannot exercise the
   stability conjunct of TI_2' (same for `editdist_e1`).

**Interpreting rho against the estimated ceiling, not against 1.0**
(revision memo, same section): inter-pass Spearman reliability on the 72
items is disputed in-repo -- `AUDIT.md` flags a MISMATCH between what
`main.tex` currently cites (0.249) and a newer recomputation (0.280),
unresolved as of this run. `run_ti2prime_demo.py` reports both. Via the
Spearman-Brown prophecy formula for a 2-pass average
(`reliability = 2r/(1+r)`), the attenuation ceiling on any judge-human
correlation is `sqrt(reliability) ≈ 0.63` (paper-cited) or `≈ 0.66`
(recomputed). A judge at rho=0.48 is therefore at ~76%/73% of the achievable
maximum -- a materially different claim from "0.48 out of 1.0" -- with two
caveats: Spearman-Brown assumes parallel forms (the two passes here are
different rubric-strictness views, not pure replications), and with a single
rater the ceiling conflates rubric sensitivity with rater noise. Both point
the same way, so treat it as a lower bound on what's achievable.

## Where the code lives, and why

The math ("correlation of a proxy to a target, discounted by the proxy's own
repeat-stability") has nothing to do with judges or Lean, so it lives in
`uutils` as **Validity-Stability (VS)** — validity = does the proxy track the
target (correlation); stability = is the proxy internally consistent
(1 - repeat std). cert-judge's TI_2' is a thin, notation-only wrapper on top:

| Layer | Location | What it is |
|---|---|---|
| Generic compute | `ultimate-utils/py_src/uutils/stats_uu/validity_stability.py` | `compute_validity_stability` (M^VS) -> `ValidityStabilityResult`; `compute_validity` (M^C, stability-free, for property-estimator reuse per the memo's "one operator, two ground truths"); `bootstrap_correlation_ci`, `compute_kendall_tau_b`, `compute_calibration_gap` |
| Generic plot | `ultimate-utils/py_src/uutils/plot/validity_stability_scatter.py` | `plot_validity_stability_scatter(...)`, legend symbol defaults to `"VS"` |
| cert-judge notation | `cert-judge/py_src/cert_judge/ti2prime_plot.py` | `compute_ti2prime` / `plot_ti2prime_scatter` — same functions, legend symbol fixed to `TI_2'`, judge/human axis labels |
| This repo's data glue | `run_ti2prime_demo.py` (this dir) | Parses `detail_rows.csv` + `aligned_panel_n75.tsv`, joins on `item_key`, calls the above |

`uutils` is Brando's general-purpose utilities package
(`git@github.com:brando90/ultimate-utils.git`, published on PyPI as `uutils`).
PRs open in both repos: [brando90/cert-judge#38](https://github.com/brando90/cert-judge/pull/38)
and [brando90/ultimate-utils#44](https://github.com/brando90/ultimate-utils/pull/44)
(branch `claude/validity-stability-score`, off `origin/master`).

`cert_judge/ti2prime_plot.py` is **not** re-exported from `cert_judge/__init__.py`
(matching `uutils.stats_uu`'s own submodule convention) because it pulls in
`uutils` + matplotlib + scipy at import time; `import cert_judge` itself must
stay light. Import it explicitly:

```python
from cert_judge.ti2prime_plot import compute_ti2prime, plot_ti2prime_scatter
```

## Usage

```python
from cert_judge.ti2prime_plot import compute_ti2prime, plot_ti2prime_scatter

# judge_scores, human_scores: paired per item, both in [0,1]
# repeat_scores_by_item: item -> that item's raw repeat judge scores (for the
# stability term -- see the module docstring for why this must be repeats,
# not the spread of scores across items)
result = compute_ti2prime(judge_scores, human_scores, repeat_scores_by_item)
print(result.vs_score, result.validity, result.stability)

plot_ti2prime_scatter(
    judge_scores, human_scores, repeat_scores_by_item,
    judge_label="gpt-5.3-codex|P4_CHECKLIST",
    out="results/my_figure",  # writes .png (300dpi) and .pdf
)
```

If you don't have repeat data, pass a precomputed stability figure instead:
`compute_ti2prime(judge_scores, human_scores, std=0.05)`. There is no default
fallback to across-item spread — see the module docstring for why that would
silently reward an uninformative (constant-score) judge.

## Demo (real data, 3 representative judges)

```bash
python3 run_ti2prime_demo.py
```

Reads:
- `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/{detail_rows.csv,summary.json}`
- `experiments/26_human_label_dataset_audit/results/aligned_panel_n75.tsv` (audited source of truth)

Writes `results/ti2prime_scatter_<judge>.{png,pdf}` + `results/ti2prime_demo_summary.json`
for 3 judges spanning the range TI_2' should discriminate (not all 9 — this
is a demo of the plotting code, not a rerun of the full panel):

| Judge | TI_2' | Story |
|---|---|---|
| `gpt-5.3-codex\|P4_CHECKLIST` | 0.675 | Real judge, decent human agreement |
| `claude-sonnet-4-20250514\|P8_STRICT_B` | 0.205 | Passes the behavioral screen (high `cert_index`) but barely correlates with humans — the paper's own cautionary case (revision memo Sec 2.1-2.2) |
| `random_r1` | 0.000 | Uniform-random anchor |

Each judge's freshly-recomputed Spearman correlation is cross-checked against
exp06's already-audited `human_spearman_r_avg` — exact match (`|diff| = 0.0`)
for all three, confirming the item-level join reproduces the audited pipeline.

## Tests

`cert-judge/tests/test_ti2prime_plot.py` (`pytest tests/test_ti2prime_plot.py`).
`uutils`'s own inline tests: `python3 py_src/uutils/stats_uu/validity_stability.py`
and `python3 py_src/uutils/plot/validity_stability_scatter.py` (that package's
existing convention is runnable `_test()` functions under `if __name__ ==
'__main__'`, not a separate `tests/` tree).
