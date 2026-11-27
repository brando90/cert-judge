# PREREG: experiment 69A, proxy–target proper-score selection (zero-spend)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/69_proxy_target_proper_score/PREREG.md>

**Written 11-26-2026, committed before `scripts/run_69a.py` was run.** CPU only. No Vals, Valkyrie, or other paid judge call. $0.

What was already public when this was written: experiment 67 and experiment 68 results, including their published Ranked Probability Score (RPS), cross-entropy (CE), and total variation distance (TVD) tables, and the inventory counts in the attached 2026-11-26 snapshot README (250 main scores, 74% at 5, attestations 118 yes / 100 partial / 32 blank). Those counts are claims to check, not results of this script. No selection regret for this protocol had been computed.

## Question

On judges that already have saved scores, does a label-free proxy pick a judge with better held-out proper scores than the constant forecast (CONST), and what is its paired RPS regret against the judge that looks best on the validation tasks (best-on-val)?

The target is the conditional expert-rating distribution. The primary score is the normalized individual-rating RPS. CE and TVD are secondary. Spearman and Pearson are diagnostic only. Proxy–target similarity is this selection comparison. It is not Spearman(proxy, judge–human Spearman).

## Frozen inputs

- **New human snapshot N250.** `data/cert-judge-data/`, the attached archive `cert-judge-data-2026-11-26.tar.gz`, sha256 `e5b6fb2317a6aade71f9858c91430e673768ec8e50ec5d90f75ac2fab701a251`. Canonical owner: trustworthy-theorem-judges experiment 09, live sync commit `460466dd` (sheet readback 2026-11-26 15:29 America/Los_Angeles). Analysis rows are `source_label=main` with an integer `final_score_0_5`. Warm-up rows are stored and not analyzed. Names and attestations stay as recorded. Expected check, stop if it fails: 250 numeric main scores, T05 100, T08 100, T12 30, T06 16, V04 3, V02 1.
- **59-artifact panel P59.** Corrected-prompt ratings in `experiments/human_labels/participant{1..5}_data_correct_prompt.tsv` (and `participant1_data_correct_prompt.tsv`). An artifact is kept when at least 4 of those raters scored it. Saved judge scores: the three detail files named in experiment 67 `scripts/lib.py` (`FAM`). Task id is the gold file. This is the only panel in this checkout where saved judge scores and human ratings share items. The 100 new files have no saved cert-judge scores, so no proxy is scored against N250.
- **Proxies, higher is better, label-free (not `human_spearman`).**
  - Paper series: `TI_variance_aware` from the three `judge_trust_vector.csv` files named in experiment 67.
  - Experiment 39 units (`results/units_train_val.json`, `results/units_test.json`): `C_ms_gold`, `TI_var_trainnorm`, `PTI_v0_frozen`, `C_bm_gold`. A null index drops that unit from that proxy only.
  - `semantic_margin_train`: `experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/results/configuration_overview.json` → `properties.train.semantic_margin.value` when `status=COMPUTED`.
- Experiment 39 critic scores are the `kind=crit` cells in `experiments/39_.../results/harvest/*.json` (status `measured` or `deterministic`), joined to P59 on the candidate stem with `.lean` removed. A unit enters a pool only if it scores every artifact in that pool's intersection.

## Pools

1. `paper_all` — the saved paper series that join to P59 (expected 24).
2. `paper_<family>` — Codex, Claude Opus, Qwen3-Coder separately.
3. `e39_test_llm` — experiment 39 units with `split=test` and `kind=llm`. **Primary pool for `C_ms_gold`, `TI_var_trainnorm`, `PTI_v0_frozen`, `C_bm_gold`, and `semantic_margin_train`.** These judges were held out of the original index search.
4. `e39_all_llm` — all experiment 39 `kind=llm` units with full coverage. Secondary, because train and validation judges were used when `C_ms_gold` was chosen.

Controls stay out of these pools.

## Metrics and selectors

Forecasts use experiment 68 `scripts/metrics.py`: judge repeats in [0, 1] are binned with `binned_repeats_to_probs(..., alpha=0.5)`. RPS is `rps_item` (normalized individual-rating RPS). CE is `ce_item`. TVD is `tvd_item` (once against the artifact empirical distribution). Lower is better.

Leave-one-task-out (LOTO), equal weight on artifacts inside a task, then equal weight on tasks:

- **CONST:** Laplace-smoothed (0.5) empirical distribution of every individual training-task rating, one forecast for every held-out artifact.
- **best-on-val:** on the training tasks, the eligible judge with the lowest mean individual-rating RPS. Ties break by sorted judge id.
- **proxy:** the eligible judge with the highest frozen proxy. Ties break by sorted judge id. The proxy does not change by fold.

Paired task vectors: `RPS_proxy − RPS_CONST` and regret `RPS_proxy − RPS_best_on_val` (positive regret means the proxy is worse). The same differences are stored for CE and TVD. The 95% interval is the 2.5 and 97.5 percentiles of the mean of 2,000 task resamples (seed 69) of those task-level paired differences. The selector is not refit inside the resample.

Diagnostic, not the decision: Spearman and Pearson of the proxy against minus held-out RPS across judges, and each selected judge's Spearman against the artifact mean rating.

## Frozen success rule

A proxy **passes** on a pool only if both hold for RPS:

1. Mean paired `RPS_proxy − RPS_CONST` is negative and its 95% task interval excludes 0 (the proxy beats CONST).
2. Mean paired regret `RPS_proxy − RPS_best_on_val` has a 95% task interval that excludes 0.

The sign of (2) is reported. An interval entirely above 0 meets the literal wording and means the proxy is significantly worse than best-on-val. An interval entirely below 0 means it is significantly better. An interval that covers 0 is not a pass.

N250 has no judge scores. Its block reports the rating distribution, attestations, T05 versus T08 agreement, and LOTO CONST proper scores, including the share of 5s. It has no pass/fail on a proxy.

## Stops

- If the 250-count check fails, write the mismatch and do not interpret selection.
- If a pool has fewer than 8 judges after the coverage rule, that pool is `NOT_COMPUTABLE`.
- No analysis is added after seeing the numbers except a dated addendum that does not change this rule.
