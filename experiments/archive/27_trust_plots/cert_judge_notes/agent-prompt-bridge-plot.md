# AGENT PROMPT — Build the PTI ↔ TI bridge association figure

## Goal

Implement a reusable plotting utility in the `cert-judge` repository that visualizes the
central empirical claim of the project: that the **label-free proxy** $\mathrm{PTI}_{2'}$
tracks the **human-grounded criterion** $\mathrm{TI}_{2'}$ across judge configurations. One
point per judge. This is the paper's Figure 1 candidate.

Context you need (do not re-derive it):

- $\mathrm{TI}_{2'}(aj) = \big[\mathrm{Corr}(\hat S_{aj},\, \hat S^*_H)\cdot(1-\mathrm{std}(\hat S_{aj}))\big]^{1/2}$
  — computed on the human-annotated subset $b'$; needs labels; **y-axis (target)**.
- $\mathrm{PTI}_{2'}(aj) = $ geometric mean of property scores $\{P_\mathrm{rfl}, P_\mathrm{mb},
  P_\mathrm{mms}, P_{\alpha SI}\}$ — computed on the full benchmark $b$; label-free;
  **x-axis (proxy)**.
- Both live in $[0,1]$, higher is better. The unit of observation is the **judge
  configuration**, not the item.

## Hard rules

1. New branch `bridge-plot`. Open a PR; do not merge, do not push to `main`.
2. **No API-key-loading runs and no judge inference.** This task only consumes numbers that
   already exist in results files, or synthetic data you generate. If the real per-judge values
   are not on disk, build against synthetic data and say so — do not invent plausible numbers
   and do not run anything that spends money.
3. Deterministic: fix seeds for any bootstrap or jitter; identical inputs must produce
   byte-identical figures.
4. Pure matplotlib + numpy + pandas (+ scipy if already a dependency). Do not add seaborn or
   any new dependency without asking.

## Data contract

Define one tidy input schema and validate it on load:

| column | type | meaning |
|---|---|---|
| `judge_id` | str | e.g. `gpt5.3-codex-P8_STRICT_B` |
| `family` | str | e.g. `codex`, `opus`, `qwen`, `gpt-4o-mini`, `non-llm` |
| `role` | enum | `primary` \| `control` \| `anchor` |
| `pti` | float [0,1] | proxy value |
| `pti_lo`, `pti_hi` | float | bootstrap CI over probe items (nullable) |
| `ti` | float [0,1] | criterion value |
| `ti_lo`, `ti_hi` | float | bootstrap CI over annotated items (nullable) |
| `label_view` | enum | `strict` \| `lenient` \| `avg` |

`role = control` covers deliberately bad judges (random, edit-distance, lexical-only
baselines). `role = anchor` covers reference points such as a uniform-random judge and a
known-good judge. Ship a synthetic generator producing a realistic frame (≈10 primaries across
3 families, 3 controls, 2 anchors) so the figure can be developed and tested end-to-end without
the real numbers.

## Stage 1 — two plain figures first

Deliberately simple, so each piece is verifiable before merging:

- **Fig A `bridge_scatter`**: `pti` on x, `ti` on y, one marker per judge, axes fixed to
  $[0,1]$, the $y=x$ diagonal as a thin dashed reference line, judges labeled.
- **Fig B `bridge_marginals`**: the two marginal distributions (histogram + KDE if scipy is
  available) of `pti` and of `ti`.

## Stage 2 — the merged figure

A joint plot: central scatter with a marginal density panel on the top (for `pti`) and on the
right (for `ti`), sharing axes with the central panel. Required elements:

1. **Error bars on both axes** wherever CI columns are present. With ~10 judges the
   uncertainty is the story; a bare scatter overstates precision.
2. **The $y=x$ diagonal**, dashed and unobtrusive — level agreement, which is a stronger
   property than the rank agreement the bridge claim requires.
3. **A fit line with a bootstrap band** (resample judges, not items). Label it explicitly as a
   visual guide, not a causal or predictive model.
4. **Markers distinguish `role`**: filled for `primary`, hollow for `control`, starred for
   `anchor`; color encodes `family`. Colorblind-safe palette, and the encoding must survive
   grayscale printing (vary marker shape, not just hue).
5. **Statistics box** reporting, for the current `label_view`:
   - `n_judges` (primaries; and total)
   - Spearman ρ **computed twice: primaries only, and all judges including controls** — with
     bootstrap 95% CIs for both
   - Pearson r, same two ways
   - mean $|{\mathrm{PTI}-\mathrm{TI}}|$ (distance from the diagonal), primaries only
   The two-way reporting is mandatory: controls span most of the unit square, so a correlation
   computed with them included can be carried almost entirely by the negative controls. Never
   display only the flattering number.
6. **Annotation of anchors** with short text labels (e.g. "uniform-random judge", "reference
   good judge") placed so they never overlap data.
7. A `label_view` parameter that regenerates the whole figure for `strict` / `lenient` / `avg`,
   plus a `panel=True` mode producing all three side by side.

## API

```python
plot_bridge(
    df,                      # tidy frame per the schema above
    label_view="avg",
    show_controls=True,
    show_diagonal=True,
    show_fit=True,
    annotate="anchors",      # "none" | "anchors" | "all"
    out=None,                # path stem; writes .pdf and .png at 300 dpi
    seed=0,
) -> matplotlib.figure.Figure
```

Place it in the repo's existing utilities module (find where plotting helpers already live and
follow that convention rather than creating a parallel structure). Return the figure so callers
can compose; write files only when `out` is given.

## Deliverables

1. The plotting module, with a docstring stating the axis semantics (proxy vs criterion) and
   the unit of observation (judge configuration).
2. `make_synthetic_bridge_frame(seed)` returning a valid frame for tests and demos.
3. Tests: schema validation rejects out-of-range values and unknown roles; the figure builds
   headlessly (Agg backend) for all three label views; identical seeds produce identical
   summary statistics.
4. A short `README` section showing the call and embedding the synthetic-data example figure.
5. In the PR description: the figure rendered on synthetic data, plus a note stating explicitly
   whether real per-judge values were found on disk (with paths) or whether everything shown is
   synthetic.

## What not to do

- Do not fit or display any level-mapping model from PTI to TI. At this judge count that is
  overfitting; the honest object is the raw scatter.
- Do not extrapolate the fit beyond the observed range or into a predicted-value readout.
- Do not silently drop judges with missing CIs — plot them without whiskers and note the count.
- Do not tune plot limits to make the trend look stronger; axes stay $[0,1]$ on both.

---
END OF AGENT INSTRUCTIONS

```
TL;DR (for the human reader; the agent should ignore this block):
This prompt has the agent build the "really cool plot" from your notes: a joint
figure with PTI_2' (label-free proxy) on x, TI_2' (human criterion) on y, one point
per judge configuration, marginal densities on the top and right, error bars on both
axes, the y=x diagonal, a bootstrap fit band, and your two anchor judges (uniform-
random bottom-left, good judge top-right) annotated. It starts with the two simple
matplotlib figures you asked for, then merges them. The one addition worth knowing
about: it reports Spearman/Pearson twice — primaries only and with controls — because
random and edit-distance controls sit near (0,0) and can carry the correlation on
their own, which is exactly the objection a reviewer would raise. Hard rules: no
inference runs, no spend, synthetic data if the real per-judge numbers aren't on disk,
and no level-mapping model fitted at n≈10 judges.
```
