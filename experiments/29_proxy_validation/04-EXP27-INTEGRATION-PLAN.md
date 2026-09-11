# Integrating `experiments/27_trust_plots`

## Two figures, two index sets

The paper needs two visually related but statistically different figures.

### Figure A — outer bridge, one point per judge

Purpose: test whether the label-free proxy orders judges like the human criterion.

- x-axis: `PTI_v0(aj)` in `[0,1]`.
- y-axis: raw `TI_m1(aj)` in `[-1,1]`.
- unit: one judge configuration.
- primary statistic: Spearman over judges.
- uncertainty: bootstrap over judges; report `n_judges` and valid replicates.
- encodings: model family and primary/control role.
- no `y=x`; no level-gap MAE.

This is the main surrogate-gap figure.

### Figure B — inner criterion diagnostic, one figure per judge

Purpose: show what `TI_m1`/`TI_2'` means at item level and where a particular judge fails.

Reuse PR #38's Exp27 implementation:

- x/y: paired human and judge item scores;
- count-sized markers for ties;
- discrete-aware marginals;
- vertical repeat-std error bars;
- Spearman, Kendall tau-b, and CI;
- no 2D KDE dependence claim and no identity line on uncalibrated scales.

Place one representative panel in Methods or an appendix; provide the remaining judges in supplementary material.

## Dependency procedure

1. Review and test `brando90/ultimate-utils#44`.
2. Review and test `brando90/cert-judge#38` against the updated dependency.
3. Merge or stack explicitly; never copy-paste the utility into a second module.
4. Cross-check Exp27's recomputed item-level Spearman against the canonical `TI_m1` table after the 72→75 panel repair. Differences must be explained by item-set or aggregation changes, not hand-waved.

## Required tests

- constant human or judge vector produces an explicit undefined/zero-validity result according to the criterion policy, never a fabricated correlation;
- tied discrete values render without bin degeneration;
- repeated-score error bars come from within-item repeats, never across-item score dispersion;
- item-key join has a one-to-one audit and reports dropped/duplicated keys;
- figure-generation commands are deterministic.
