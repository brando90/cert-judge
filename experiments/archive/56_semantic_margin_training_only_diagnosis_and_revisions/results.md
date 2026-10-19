# Training-only semantic-margin diagnosis

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/cj-e56-training-margin/experiments/56_semantic_margin_training_only_diagnosis_and_revisions/RESULTS_training_diagnosis.md>

**TLDR:** On the historical training split, the two frozen revisions do not improve semantic margin. The formatting penalty is 0 on 59/59 observed task values and the identity baseline is 1, so headroom normalization equals the original margin on all 12 configurations. That margin's association with current-five training agreement is Spearman -0.378, Pearson -0.219, Kendall -0.303 across 12 correlated configurations (p-val=n/a; no configuration-level interval). The pooled judge-selection comparison is unavailable: 25/30 files have two accepted repeats for every configuration, below the frozen requirement of 27.

Full table: [RESULTS_training_diagnosis.md](RESULTS_training_diagnosis.md). The gold-free repeat total variation on the same rows spans 0.111 to 0.267 and has Spearman 0.210 with training agreement (n=12 correlated setups, p-val=n/a): [ADDENDUM_repeat_tvd_10-19-2026.md](ADDENDUM_repeat_tvd_10-19-2026.md).

**TLDR-end:** [cert-judge: 56 semantic margin training diagnosis] Cached training scores show the original semantic margin and both pre-specified revisions fail to rank judges by human agreement, without using validation or test outcomes.
