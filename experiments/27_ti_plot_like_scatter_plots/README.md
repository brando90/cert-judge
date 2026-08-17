# Exp27 — TI_2' scatter plot (reusable)

Reusable matplotlib figure for TI_2', the paper's per-judge human-alignment
criterion (`paper_latex/ICLR_2027_submission/main.tex`, TI_{2'} definition;
`cert_judge_notes/certjudge-revision-memo.md` Sec 1):

```
TI_2'(aj) = ( clip_[0,1](Corr(judge_scores, human_scores)) * (1 - STD) )^0.5
```

One judge configuration, one panel: item-level (human, judge) score scatter
with a light 2D density wash (not a separate marginal-histogram panel) and a
legend showing the formula with that judge's real numbers plugged in, e.g.
`TI_2' = (0.48 x (1-0.05))^0.5 = 0.675`.

No judge inference, no LLM calls, no spend: `run_ti2prime_demo.py` reuses
per-item judge scores and the audited human labels that already exist on disk
from the ICLR-2027 / workshop submission runs.

## Where the code lives, and why

The math ("correlation of a proxy to a target, discounted by the proxy's own
repeat-stability") has nothing to do with judges or Lean, so it lives in
`uutils` as **Validity-Stability (VS)** — validity = does the proxy track the
target (correlation); stability = is the proxy internally consistent
(1 - repeat std). cert-judge's TI_2' is a thin, notation-only wrapper on top:

| Layer | Location | What it is |
|---|---|---|
| Generic compute | `ultimate-utils/py_src/uutils/stats_uu/validity_stability.py` | `compute_validity_stability(proxy, target, repeat_scores_by_item)` -> `ValidityStabilityResult` |
| Generic plot | `ultimate-utils/py_src/uutils/plot/validity_stability_scatter.py` | `plot_validity_stability_scatter(...)`, legend symbol defaults to `"VS"` |
| cert-judge notation | `cert-judge/py_src/cert_judge/ti2prime_plot.py` | `compute_ti2prime` / `plot_ti2prime_scatter` — same functions, legend symbol fixed to `TI_2'`, judge/human axis labels |
| This repo's data glue | `run_ti2prime_demo.py` (this dir) | Parses `detail_rows.csv` + `aligned_panel_n75.tsv`, joins on `item_key`, calls the above |

`uutils` is Brando's general-purpose utilities package
(`git@github.com:brando90/ultimate-utils.git`, published on PyPI as `uutils`).
The new module is on branch `claude/validity-stability-score` there
(branched off `origin/master`), **committed nowhere yet** — only in the
working tree, same as the cert-judge side. Nothing has been pushed.

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
