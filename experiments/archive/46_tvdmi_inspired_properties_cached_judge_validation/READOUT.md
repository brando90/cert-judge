# Information-inspired judge properties: what the historical run establishes

**Doc link:** [canonical readout](https://github.com/brando90/cert-judge/blob/main/experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/READOUT.md).
**Summary:** Two new properties were tested using measured historical scores. Neither establishes better judge selection than the fixed human-style rubric. A third property could not be measured under its frozen repeat requirement. No new judge inference or set-N access occurred.

The study is `46_tvdmi_inspired_properties_cached_judge_validation`, completed on 10-08-2026 on the Stanford Network Analysis Project cluster.
It implements scalar-score adaptations inspired by total variation distance mutual information, not a reproduction of the paper's text-pair language-model critic.
Read the [paper summary](PAPER_SUMMARY.md), [frozen definitions](PROTOCOL.md), [prose erratum](ERRATA.md), and [full measured report](RESULTS_information_properties.md).
The reusable implementation is [information_properties.py](../../../py_src/cert_judge/information_properties.py).

## Properties and results

1. **Semantic changes versus formatting:** compare the score drop caused by an audited strict weakening with the absolute score change caused by harmless formatting. A good judge should react more to the meaning change. The centered area-under-curve statistic ranges from -1 to 1. Eleven of the twelve primary configurations tied at the maximum train value, so this probe set provided little selection power.
2. **Within-task repeat information:** compare scores for the same candidate across repeats with independently paired candidate scores from the same task. This avoids rewarding a constant judge or a task-identity-only signal. It still rewards stable arbitrary candidate identities, so dependence alone cannot establish correctness. This selector picked the Opus 5.5 judge with the fixed human-style rubric, internally named H2.
3. **Direction-gated deletion information:** measure whether scores distinguish deletion levels, then require scores to decrease as declarations are removed. The property requires at least two accepted repeats at every level; the measured cache has one deletion repeat. It is unavailable for all 56 configurations, not a measured zero.

All 56 measured configurations received property and coverage rows. Selection compared the same twelve configurations, using train properties without human outcomes. Evaluation used the available current ratings from five raters. The historical test comparison has 29/30 files across 10 tasks; validation is unavailable at 13/15 files against a requirement of 14.

| Selection rule | Test Spearman correlation | Difference from fixed rubric |
|---|---|---|
| Fixed human-style rubric, uniform selection among four judges | 0.826 [0.507, 0.934] | Reference |
| Maximum train repeat information | 0.844 [0.472, 0.951] | +0.018 [-0.127, +0.186] |
| Maximum train semantic discrimination, uniform selection among eleven tied judges | 0.768 [0.455, 0.888] | -0.059 [-0.156, +0.054] |
| Maximum train deletion information | Unavailable | Unavailable |

These are expected utilities of selecting one judge, not correlations of averaged judge scores. Intervals are 95% percentile intervals from 10,000 paired task-cluster bootstrap draws; all 10,000 draws for the displayed available metrics are finite, p-val=n/a. Both paired differences include zero. The intervals condition on the fixed selectors, cached scores, judge pool, and raters; they omit uncertainty from selecting the rule or sampling new judge models and raters. This is exploratory reuse of historical data, not an independent prospective result.

| Selection rule | Mean absolute error, 0–1 scale | Mean bias, judge minus human | Judge mean / human mean |
|---|---|---|---|
| Fixed rubric | 0.142 [0.100, 0.195] | +0.038 [-0.016, +0.093] | 0.627 / 0.589 |
| Repeat information | 0.148 [0.102, 0.196] | +0.087 [+0.020, +0.145] | 0.676 / 0.589 |
| Semantic discrimination | 0.173 [0.136, 0.212] | -0.006 [-0.059, +0.053] | 0.583 / 0.589 |

Positive bias means leniency. The repeat-selected judge has a slightly higher point estimate for ranking agreement and a slightly higher absolute-error point estimate; an improvement is not established. Its judge mean is 0.676 [0.500, 0.828] and the human mean is 0.589 [0.453, 0.723], p-val=n/a under the same conditional task bootstrap. It has 87/87 accepted repeat scores on these 29 files; mean within-file sample standard deviation is 0.012.

## Interpretation and next work

- **[p 9/10] Make the semantic probe set harder before adding more aggregate formulas.** Verify that each proposed weakening changes the guarantee of the whole file, using counterexamples or entailment checks where possible, and pair it with harmless edits. The eleven-way tie is direct evidence that the present semantic discrimination property cannot choose among most members of the primary pool.
- **[p 8/10] Retain repeat information as a secondary diagnostic with constant, reversed and candidate-identity controls.** A perfectly stable wrong judge can carry information. Fixed score bins also discard distinctions; a bijection of bin labels preserves information, but replacing raw scores by one minus the score need not preserve this particular bin partition at boundaries. Low information can also be legitimate when candidates have genuinely similar coverage.
- **[p 7/10] Collect the missing deletion repeats in a declared future Valkyrie batch if this property remains worth testing.** Keep the existing frozen unavailability result. A new repeat-complete run needs its own registration and cannot be described as a result already obtained here.

The prospective human evaluation is the existing VeriBench set-N round. No separate cert-judge raters should be recruited. Freeze panel scores, property values, selection rule, minimum useful improvement and analysis before reading any set-N sheet; keep judge outputs sealed from Brando until his rating sheet is finished. Set-N ratings evaluate that frozen procedure once and cannot tune it. The frozen report's generic phrase about freezing “before collecting new ratings” should be read with this access-based requirement: collection is already underway in the shared round.

The archived numerical artifacts and frozen analysis code remain unchanged by this interpretation. The full measured report was renamed without changing its bytes to avoid a case-insensitive filesystem collision with the live ledger; the original renderer remains part of the historical record. The [erratum](ERRATA.md) separately corrects the deletion-probe description without rewriting the frozen protocol.

**TLDR-end:** [cert-judge: 46_tvdmi_inspired_properties_cached_judge_validation] The information-inspired pre-run gives two empirical tests and an explicit missing-repeat result; useful judge selection remains unproven. Strengthen semantic probes while preserving the sealed set-N evaluation.
**Snapshot:**
```text
Measured judge configurations: 56
Primary selection pool: 12
Historical test support: 29/30 files, 10 tasks
Repeat selection minus fixed rubric: +0.018 [-0.127, +0.186]
Semantic selection: 11/12 tied for maximum train value
Deletion-information coverage: 0/56 configurations
New judge calls: 0
```
