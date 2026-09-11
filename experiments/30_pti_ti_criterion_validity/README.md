# 30 — PTI → TI_m criterion validity

Does the label-free proxy predict the human-grounded criterion well enough to
replace fresh human validation for each new judge?

That is a criterion-validity question about three objects the project keeps
distinct (`CLAUDE.md`):

| object | role | cost |
| --- | --- | --- |
| `TW_m` | the scoped trustworthiness construct | not directly measurable |
| `TI_m` | human-grounded criterion | expensive, needs labels |
| `PTI_p` | label-free behavioral proxy | cheap, no labels |

The claim worth publishing is that `PTI_p` ranks units the same way `TI_m`
does, on units the calibration has never seen. Everything here exists to test
that claim honestly, including refusing to report it when the design cannot
support it.

## The criterion

Following `paper_latex/TrustWorthy_Notes/main.tex`:

```
TI_m1(aj)  = Corr(judge scores, target scores)
TI_2'(aj)  = sqrt( Corr * (1 - std) )
```

Two implementation points that are easy to get wrong and are pinned by tests:

- **`std` is repeat noise, not score spread.** It is the mean over items of the
  per-item standard deviation across repeated judge calls. Using the pooled
  standard deviation of a judge's scores instead would penalise a judge for
  telling good artifacts from bad ones, inverting the metric.
- **A negative correlation clamps `TI_2'` to zero** rather than producing an
  undefined square root. The signed correlation is kept alongside, so the clamp
  never hides the direction.

Sanmi's objection to the stability term is recorded in the notes: `1 - std` is
a judge-only quantity that never checks whether the judge's spread matches the
target's. `compute_ti_m` therefore also reports `scale_ratio` and Lin's
concordance coefficient, which do penalise location and scale mismatch.

## Run it

Design check on the submission's published parameters, no input needed:

```bash
python experiments/30_pti_ti_criterion_validity/design_check.py --demo
```

Full validation on a panel of your own:

```bash
python experiments/30_pti_ti_criterion_validity/design_check.py \
    --input panel.json --output report.json
```

`panel_template.json` shows the input shape. Its numbers are placeholders, not
results. Neither mode performs inference or loads credentials.

## What the report tells you, in order

**1. Ceiling.** A judge cannot correlate with labels better than the labels
correlate with themselves. Reliability is estimated by ICC(2,k) from a crossed
items × raters matrix, or extrapolated by Spearman-Brown from summary
agreement; the attainable correlation is its square root. If the acceptance
threshold sits above that ceiling, the fix is more raters, and the report says
how many. Worth knowing before attributing a low number to the judge.

**2. Resolving power.** Two things have to hold before a panel correlation
means anything: enough units, and a criterion spread larger than the error on
each unit's own estimate. When spread and error are comparable, the ranking
being predicted is mostly noise, and the correlation against it is
uninformative however it lands, including when it lands high.

**3. Criterion validity.** Pearson, Spearman, Kendall tau-b and Lin's CCC, each
with a percentile bootstrap interval, plus pairwise ranking accuracy, top-k
overlap and mean rank displacement, since rankings are the deliverable. The
four correlations share a sample and are a robustness check, not four
independent confirmations. Tau-b is the conservative one and usually reads
lowest.

Any report whose design fails check 2 comes back `UNDERPOWERED` even when the
point estimate is high. That is deliberate.

## Splits

`leave_one_group_out` holds out one whole agent or judge family at a time. This
is the split that matches the claim: the held-out family is unseen at fit time,
so a proxy that only works in-panel fails here. Splits that hold out items or
rubric passes while keeping every family on both sides do not test that claim,
however they are labelled — in particular, training on one rubric pass and
testing on the other is a rubric-robustness check, since it is the same raters
scoring the same items.

With few families each fold is tiny, so per-fold correlations are unusable.
`pooled_leave_one_group_out` fixes the arithmetic without weakening the
protocol: it fits a calibration on the other families, predicts the held-out
one, pools every out-of-group prediction and correlates once over the whole
panel. Quote that number.

`grouped_three_way_split` partitions whole families into train, validation and
test. Choose the index form and every other free parameter on validation. Open
test once.

## Tests

```bash
pytest tests/test_ti_validation.py
```

The intraclass correlations are checked against the six published values of the
Shrout & Fleiss (1979) worked example, and the ceiling logic against the
inter-pass agreement reported in Appendix G.2 of the submission, so drift shows
up as disagreement with a number someone else can look up.
