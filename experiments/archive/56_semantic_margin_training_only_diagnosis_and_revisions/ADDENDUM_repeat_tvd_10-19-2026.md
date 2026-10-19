# Addendum, 10-19-2026: gold-free repeat total variation on the same training rows

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/56_semantic_margin_training_only_diagnosis_and_revisions/ADDENDUM_repeat_tvd_10-19-2026.md>

**TLDR:** On the same frozen training projection, repeat total variation (the gold-free adaptation of total variation distance mutual information) spans only 0.111 to 0.267 across the 12 judge setups and does not rank them by human agreement. A judge that repeats itself is not the judge that agrees with people.

This note uses only the training rows already written by `experiments/archive/56_semantic_margin_training_only_diagnosis_and_revisions`. It does not open validation or test outcomes, and it does not introduce a new formula. Repeat total variation is the frozen definition in `py_src/cert_judge/information_properties.py`: five-bin total variation between a judge's paired repeat scores and the product of those repeat margins. It does not use a gold reference.

## What the training rows show

Repeat total variation versus current-five training agreement, across 12 correlated setups: Spearman 0.210, Pearson 0.090, Kendall 0.121. p-val=n/a. No configuration-level interval, because the setups share the same tasks. The values themselves run from 0.111 (`qwen36|H0`) to 0.267 (`opus55x|H2`).

Among files with all three accepted repeats:

| Setup | Files | Identical repeats | All three scores equal 1 | Mean repeat SD | Repeat total variation | Training Spearman |
|---|---:|---:|---:|---:|---:|---:|
| opus55x\|D0 | 30 | 16 | 0 | 0.029 | 0.226 | 0.544 |
| opus55x\|H0 | 30 | 20 | 5 | 0.031 | 0.244 | 0.625 |
| opus55x\|H2 | 30 | 29 | 5 | 0.003 | 0.267 | 0.767 |
| qwen36\|D0 | 29 | 10 | 4 | 0.119 | 0.187 | 0.742 |
| qwen36\|H0 | 25 | 11 | 4 | 0.066 | 0.111 | 0.733 |
| qwen36\|H1 | 26 | 9 | 3 | 0.081 | 0.234 | 0.791 |
| qwen36\|H2 | 26 | 9 | 3 | 0.074 | 0.248 | 0.808 |
| qwen36\|R4 | 26 | 6 | 4 | 0.095 | 0.144 | 0.660 |
| t2_qwen\|D0 | 29 | 15 | 5 | 0.072 | 0.202 | 0.657 |
| t2_qwen\|H2 | 27 | 15 | 3 | 0.050 | 0.185 | 0.518 |
| t2_sonnet5\|D0 | 30 | 10 | 6 | 0.045 | 0.200 | 0.628 |
| t2_sonnet5\|H2 | 30 | 18 | 5 | 0.049 | 0.167 | 0.777 |

The share of files whose three repeats are identical, versus training agreement: Spearman −0.158, Pearson −0.037, Kendall −0.137 (n=12, p-val=n/a). Mean within-file repeat standard deviation versus agreement: Spearman 0.392, Pearson 0.278, Kendall 0.303 (same n, p-val=n/a). The share of files scored 1 on all three repeats versus agreement: Spearman 0.025, Pearson 0.331, Kendall −0.063 (p-val=n/a).

## Reading

`opus55x|H2` repeats itself on 29 of 30 files and has the highest repeat total variation, 0.267, with training Spearman 0.767 [0.415, 0.923]. `qwen36|H2` repeats itself on 9 of 26 files and has the highest training Spearman, 0.808 [0.570, 0.944], at repeat total variation 0.248. The ceiling is not the cause: at most 6 of 30 files are scored 1 on every repeat. The gold-free score moves in a narrow band, and human agreement is not the same thing as a judge repeating its own score.

The historical test of this property remains the one in `experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation`: paired difference versus fixed H2 of +0.018 [−0.127, +0.186] on 29/30 files from 10 tasks (p-val=n/a). This addendum does not replace that test and does not choose a new screen.

**TLDR-end:** [cert-judge: experiments/archive/56_semantic_margin_training_only_diagnosis_and_revisions] Repeat total variation, the gold-free score, stays between 0.111 and 0.267 on the training judges and does not track human agreement.
