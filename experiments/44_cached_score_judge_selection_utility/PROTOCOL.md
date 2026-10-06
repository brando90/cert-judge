# Cached score judge selection utility protocol

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/cj-e44-selection-utility/experiments/44_cached_score_judge_selection_utility/PROTOCOL.md>

**TLDR:** Test whether choosing a judge by the frozen gold-deletion proxy improves human agreement relative to practical label-free selectors. This is an exploratory reanalysis of already inspected data, not a fresh registered test; preserve the original study's verdict.

## Scientific question (locked)

Does selecting the maximum frozen deletion-monotonicity proxy choose a better judge than selecting a fixed human-mirror rubric or a random candidate, when candidate judges receive comparable reference context?

The main decision is whether to proceed to prospective human confirmation of this proxy, repair it, or collect data to resolve remaining uncertainty. No universal threshold is imposed. Report paired differences and uncertainty: evidence of an advantage must persist in the full-context pool and relevant criterion sensitivities; absence of a resolved advantage is not proof of equivalence. Never replace the original registered result with these post hoc findings.

## Scope and frozen inputs

- Source study: `39_label_free_proxy_index_train_val_test_over_judge_families`, revision `fc73f78696d53551cd57f13094ec6f73fbb1c234`.
- Read its panel, harvests, unit tables, probe manifest, selection and test receipts. Do not mutate them or recompute the selected proxy on altered probe sets.
- Human inputs: VeriBench `100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/items.jsonl`, SHA-256 `ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c`.
- Zero inference, zero new human labels, zero new probes. Execution on skampere1; ordinary processor analysis only.
- Record exact input hashes, software versions, source revisions, seeds and missingness in machine-readable outputs.

## Outcomes and candidate pools

Primary human criterion: the original 45 candidate files / 15 tasks (item validation + test), using available participants 1–3 mean normalized to [0,1]. Median available judge repeats and the original 90% coverage rule remain unchanged. These same labels helped select the proxy on train/validation judges; this is held-out-judge evaluation on a reused item panel.

Report four criterion views without changing the proxy: original45; remove placeholder references (36/12); remove ambiguous-reference tasks (36/12); remove both (27/9). Report existing item-test-only30/10 as a secondary view, not a new independent test.

Candidate pools use declared test configurations, excluding deterministic controls:
1. Primary: full-context D0/H0/H1/H2/R4 (12 declared, 10 proxy-computable).
2. Same human-mirror rubric H2 (4 declared, 3 proxy-computable).
3. Original broad panel (18 declared, 16 proxy-computable).

Configurations with missing proxy values remain in the declared pool, other selectors and hindsight oracle. Add a same-eligible-pool sensitivity restricting every selector to proxy-computable configurations. Missing scores are never zero-imputed.

For fair comparisons use the common observed-item mask across a candidate pool, chosen solely from availability, and report retained item/task counts. Require at least 90% of each declared criterion subset on that common mask; otherwise mark the pool/view comparison unavailable. Reproduce per-judge original-mask results separately to distinguish support differences.

## Selectors fixed before new utility computations

1. Frozen gold-deletion proxy: maximize `C_ms_gold`.
2. Identity check: maximize frozen `C_ident`.
3. Fixed human-mirror rubric: uniform choice among H2 configurations in the pool. This is an exact expectation over individual judges, not an ensemble and not the best H2 judge.
4. Random: uniform choice over all configurations in the pool, evaluated by exact expectation.
5. Transferred prompt: on judge-train configurations rank prompts by mean original-criterion Spearman, retain three; choose the highest mean on judge-validation configurations (ties lexicographic). Then uniformly choose test configurations bearing that prompt. Record the full train/validation selection table. This comparator uses no test-judge labels for selection; its rubric inventory was known and it is exploratory.

For maxima use exact floating-point ties, uniform choice over tied configurations. Do not introduce an outcome-fitted tolerance. Report tied members, proxy margins, individual utilities, expected utility, range and unavailable candidates. A selector with no eligible candidate abstains.

## Statistics

Per selector report selected members/probabilities; expected Spearman, Pearson and Kendall agreement; regret (best hindsight Spearman in the declared pool minus expected selected Spearman); paired Spearman difference versus H2 and random. The oracle is optimistic hindsight, not a deployable method.

Give selected-judge score diagnostics separately: mean absolute error, mean bias (judge minus human; positive means lenient), both means, available repeat counts and within-item raw-repeat sample standard deviation. These do not change the ranking target.

Use 10,000 paired task-cluster bootstrap draws, seed44, jointly resampling tasks for all judges/selectors within each view. Keep selectors/proxy values fixed, recompute all correlations and hindsight oracle for each draw, use the same finite-draw intersection for a paired statistic, and report valid/undefined draws. Percentile 95% intervals quantify task uncertainty conditional on the fixed pool; they omit model-population, index-selection and annotation-process uncertainty. Do not treat configurations as independent. Report p-val=n/a rather than inventing a threshold test. Secondary correlation analyses must name their resampling unit and limitations.

Base-model sensitivity: leave one test base model out at a time, grouping single-call and agent versions together; separately single-call-only and agent-only summaries. These are descriptive because the test pool has few independent base models. No pooled cluster-bootstrap claim over model populations.

## Deterministic verification and interpretation

Fail closed on input-hash mismatch, duplicate item/cell/configuration keys, nonnormalized scores, inconsistent item-task joins or changed frozen proxy values. Reproduce original per-judge criterion statistics, denominators and original pooled test Spearman to tight numeric tolerance before computing utility. Unit tests must cover ties, missing proxy candidates retained in the oracle, missing repeats, invalid statuses, shared support, task rather than item resampling, undefined constant correlations, and train/validation-only prompt choice.

One report, one summary receipt, compact per-judge/selector/comparison tables, a reproducible analysis command and meaningful tests. Preserve all declared views and unavailable outcomes; no tuning or dropping unfavorable views. Archive this study upon completion while preserving reproducible paths.
