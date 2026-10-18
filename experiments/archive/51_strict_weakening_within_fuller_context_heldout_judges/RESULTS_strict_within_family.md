# Strict weakening inside fuller-context held-out judges

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/RESULTS_strict_within_family.md>

**TLDR:** On the fuller-context held-out judges (12 configurations), strict weakening accuracy versus the existing human-agreement criterion is Spearman -0.324 [-0.761, 0.045] p-val=0.8656 (one-sided configuration permutation, 10000 draws, seed 51). Reading: **REVERSED** against experiment 39's gate (Spearman ≥ 0.45, p-val < 0.05). Pearson -0.265, Kendall -0.275. No new judge calls and no new ratings.

## Question

Does file-level strict weakening accuracy rank the judges one would deploy, on configurations that were not used to choose experiment 39's deletion screen?

## Reproduction

Experiment 39's registered `C_ms_gold` test association reproduced: **PASS** (absolute tolerance 1e-09).

## Primary result

Population: experiment 39 test-split configurations with prompts D0, H0, H1, H2 or R4, joined to experiment 42's stored `file_level_strict_only.weakening` value and to `criteria.heldout` (status COMPUTED). The interval resamples configurations, which share judge models, so it is narrower than a model-cluster interval.

| Statistic | Value |
|---|---|
| Configurations | 12 |
| Spearman [95% configuration bootstrap] | -0.324 [-0.761, 0.045] |
| Pearson | -0.265 |
| Kendall tau-b | -0.275 |
| One-sided permutation p-val | 0.8656 |
| Reading | REVERSED |
| Strict-accuracy values exactly 1 | 10 of 12 (min 0.960, max 1.000) |
| Finite configuration-bootstrap draws | 8842 of 10000 |

The configuration interval's upper end is above zero, so this is not a demonstration that the population correlation is negative. The reading REVERSED is the locked point-estimate rule (Spearman ≤ 0). The one-sided p-value tests a positive association. 10 of 12 held-out fuller-context judges score exactly 1 on strict weakening, so the score has almost no room to rank them.

Within-model sensitivity (not part of the gate): p-val=1.0000 by permuting the criterion inside each judge model ({'opus55x': 3, 'qwen36': 5, 't2_qwen': 2, 't2_sonnet5': 2}). The association is not resolved within judge models.

Model-cluster interval (resample judge-model keys, 10,000 draws, seed 51; p-val=n/a): -0.757 to -0.225 (6808 finite draws, 4 models).

## Same configurations, other cached scores

These rows use the primary configuration list. They are comparators, not a second gate.

| Score | n | Spearman [95% configuration bootstrap] | Pearson | Kendall | p-val | Reading |
|---|---:|---|---:|---:|---:|---|
| strict weakening (headline) | 12 | -0.324 [-0.761, 0.045] | -0.265 | -0.275 | 0.8656 | REVERSED |
| primary weakening, all probes | 12 | 0.259 [-0.445, 0.828] | -0.064 | 0.198 | 0.2103 | FAIL |
| C_ms_gold | 10 | -0.371 [-0.788, 0.317] | -0.319 | -0.225 | 0.8584 | REVERSED |

## Descriptive splits (not the verdict)

| Split | n | At 1 | Min score | Spearman [95% configuration bootstrap] | p-val | Reading |
|---|---:|---:|---:|---|---:|---|
| train | 10 | 2 | 0.800 | 0.427 [-0.430, 0.911] | 0.1101 | FAIL |
| val | 12 | 5 | 0.600 | 0.614 [-0.019, 0.947] | 0.0197 | PASS |

Train and validation were locked as descriptive. The validation split meets the numerical gate and the test split does not; the validation split does not replace the test.

## What was excluded

```
{
 "not_fuller": 6,
 "wrong_split": 0,
 "control": 0,
 "missing_screen": 0,
 "missing_strict": 0,
 "criterion_not_computed": 0,
 "split_mismatch": 0
}
```

## Scope

This is a cached association on the judges and ratings experiment 39 already used. It does not change that experiment's registered pass, and it is not a test on new items or new raters. A pass would still need a prospective check. A failure means these probes do not supply a within-family screen.

**TLDR-end:** [cert-judge: strict weakening within fuller-context judges] REVERSED: Spearman -0.324 [-0.761, 0.045] p-val=0.8656 on 12 held-out fuller-context configurations.
