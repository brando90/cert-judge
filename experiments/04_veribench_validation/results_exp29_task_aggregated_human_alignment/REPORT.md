# EXP29 Report: Task-Aggregated Human Alignment

## Protocol

Primary target:

```math
H(t) = \frac{1}{|A|}\sum_{a \in A} h(t,a), \qquad J(t) = \frac{1}{|A|}\sum_{a \in A} j(t,a)
```

We correlate `H(t)` and `J(t)` across tasks, not across individual candidate files. This makes the target explicit: the judge is evaluated as a proxy for the aggregate human evaluation function used to compare tasks.

The ensemble analysis reports two targets: a 20-task 2-rater ensemble over `ethan_avg` and `jolene_pass1`, and a 10-task 3-rater robustness slice that additionally includes `steven_pass1`. Each task score is defined as the mean of the three candidate files for each rater and then averaged across raters.

## Main Results

- Moving from candidate-file-level to task-level aggregation weakens the `ethan_avg` trust plot: meta-Spearman(`cert_index_v2`, human alignment) changes from `0.396` to `0.201`, and meta-Pearson changes from `0.397` to `0.194`.
- The 2-rater ensemble target (`ethan_avg` + `jolene_pass1`, 20 tasks) is essentially flat: meta-Spearman(`cert_index_v2`, human alignment) = `-0.016`, meta-Pearson = `-0.201`.
- The 3-rater ensemble target (`ethan_avg` + `jolene_pass1` + `steven_pass1`, 10 tasks) is somewhat more positive but still unstable: meta-Spearman(`cert_index_v2`, human alignment) = `0.299`, meta-Pearson = `0.055`.

## Important Plots

- [Trust vs task-level Ethan average](./fig_trust_vs_task_ethan_avg.png)
- [Trust vs task-level 2-rater human ensemble](./fig_trust_vs_task_human_ensemble_2r.png)
- [Trust vs task-level 3-rater human ensemble](./fig_trust_vs_task_human_ensemble_3r.png)
- [Pair-level vs task-level alignment for Ethan average](./fig_pair_vs_task_ethan_avg.png)
- [Per-judge task-level scatter panels for selected judges](./fig_task_scatter_ethan_avg_selected_judges.png)

## Best Judges On Ethan Avg Task Target

| Judge | cert_v2 | Task Spearman | Task Pearson | Source |
| --- | ---: | ---: | ---: | --- |
| claude-opus-4-7|P4_CHECKLIST | 0.883 | 0.693 | 0.711 | experiments/04_veribench_validation/results_exp16_opus47_r3_median |
| claude-opus-4-7|BAD_STRINGY | 0.716 | 0.631 | 0.597 | experiments/04_veribench_validation/results_exp16_opus47_r3_median |
| gpt-5.3-codex|P11_JSON_FIRST | 0.880 | 0.616 | 0.581 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| gpt-5.3-codex|BAD_STRINGY | 0.699 | 0.608 | 0.588 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| gpt-5.3-codex|P2_FORMAL | 0.879 | 0.581 | 0.585 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| gpt-5.3-codex|P3_CONCISE | 0.865 | 0.511 | 0.513 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| gpt-4o-mini|P1_BASELINE | 0.745 | 0.463 | 0.500 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| claude-opus-4-7|P1_BASELINE | 0.884 | 0.442 | 0.484 | experiments/04_veribench_validation/results_exp16_opus47_r3_median |

## Notable Outlier Movement

- `gpt-4o-mini|P1_BASELINE` improves from pair-level Spearman `0.287` to task-level Spearman `0.463` on `ethan_avg`.
- `gpt-4o-mini|P4_CHECKLIST` improves from `0.065` to `0.233` on `ethan_avg`.
- `labs-leanstral-2603|P4_CHECKLIST` improves from `0.206` to `0.301` on `ethan_avg`, but the other LeanStral prompts remain near zero or negative.

## Relation To VeriBench Appendix

- VeriBench Appendix H/G explicitly reports that task-level averaging can raise judge-human correlation into the `~0.85` range, while also warning that these aggregated numbers are more flattering than the stricter item-level held-out result.
- EXP29 is consistent with that logic. Task aggregation can improve absolute judge scores here too: for example, `claude-opus-4-7|P4_CHECKLIST` rises from pair-level Spearman `0.451` to task-level Spearman `0.693` on `ethan_avg`, and `gpt-4o-mini|P1_BASELINE` rises from `0.287` to `0.463`.
- But the same aggregation can also make weak or obviously suspect judges look better. In this panel, `claude-opus-4-7|BAD_STRINGY` rises to task-level Spearman `0.631` on `ethan_avg`, despite being a deliberately bad lexical-overlap judge.
- So aggregation is usable as an auxiliary diagnostic of the aggregate human evaluation function, but it is not a safe substitute for stricter item-level evaluation when the scientific claim is about genuine judge quality rather than smoothed task-level agreement.

## Can We Use Aggregation To Get Better Judge Scores?

- Yes, if the target is explicitly the task-level aggregate human function `H(t)`, then task-level aggregation is a legitimate target and can produce higher absolute judge-human correlations.
- No, if the goal is to claim stronger judge validity without qualification. Aggregation removes within-task noise, but it also compresses the evaluation problem and can reward judges that get coarse task ordering right for the wrong reasons.
- In this run, aggregation helps some plausible judges, but it also helps `BAD_STRINGY`; that is the main reason not to treat the aggregated number alone as the headline quality metric.
- The defensible use is: report task-level aggregated correlation as a secondary diagnostic, keep stricter item-level held-out alignment as the main honesty check, and avoid conflating absolute judge-human correlation with trust-index meta-correlation across judges.

## Notes

- This analysis reuses saved EXP16 per-pair judge scores only; it does not make new judge calls.
- Because the saved EXP16 judge runs cover 72 candidate pairs, `ethan_avg` is evaluated on the corresponding 24-task subset rather than the full 25-task file.
- `jolene_pass1` overlaps with the EXP16 subset on 20 tasks; `steven_pass1` has numeric labels on only 10 of those tasks.
