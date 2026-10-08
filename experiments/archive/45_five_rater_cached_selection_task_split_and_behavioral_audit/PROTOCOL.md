# Five-rater cached selection and behavioral audit protocol

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex-cj-five-rater-recovery/experiments/45_five_rater_cached_selection_task_split_and_behavioral_audit/PROTOCOL.md>

**TLDR:** Recompute frozen cached comparisons against five current raters and the original three-rater control, then evaluate training-task behavioral selectors against the fixed human-mirror rubric. This is retrospective reuse of exposed data, not a pristine test or a replacement for frozen prior results.

## Question and decision criterion

Does behavioral screening select judges with greater human agreement than uniform selection among the fixed H2 human-rating-rubric configurations? Primary outcome: selected expected Spearman rank correlation minus H2 expected Spearman on common supported test-task items, targeting the available five-current-rater mean / 5. A positive lower 95% task-bootstrap bound is evidence supporting further confirmation; otherwise an advantage is unresolved. This criterion is an analysis decision set before new computations, not a retrospective replacement of any prior experiment's gate. Report Pearson, Kendall tau-b, mean absolute error, bias (judge minus human; positive means lenient), both means, missingness and repeat variation. No correlation-against-zero significance test.

## Scope and data-use boundary

- Exactly the existing 25 task groups, all 3 candidates per task together, with the established VeriBench 10/5/10 train/validation/test assignment. Use the audited parser without changing raw inputs.
- Current participants 1–5 supply main targets; participants 1–3 supply the paired control. Missing scores are omitted, never zero-filled. Participants are stored identifiers; qualifications/person mapping are not independently verified.
- Historical participant-one passes: exactly 60 observations on 30 training items eligible for an auxiliary sensitivity. Exclude all 90 observations on validation/test tasks from fitting, selection and evaluation. The two passes are one historical participant, not two people.
- Initial inventory computes counts/hashes and equality checks, emitting no held-out target values. Historical published summaries have already exposed outcomes. After this protocol lock, use validation only for selection; persist a separate selection receipt before opening test outcomes for this recovery's new comparisons.
- Read-only sources: experiments 39, 41, 42, 43 and archive/44 plus VeriBench experiments 75 and 100 and original human-study artifacts. Reference snapshots are reconstructed repository bytes, not proof of what each human saw.
- Zero inference, no benchmark/reference changes and no manuscript edits. One executor. Bounded processor-only computations are expressly authorized locally by latest runbook steering while the remote cluster is unreachable. Any genuinely long job remains blocked pending remote access.

## Frozen comparison (preserve original choices)

Use experiment 39's frozen deletion-monotonicity component (`C_ms_gold`), identity component and judge-model split, preserving original aggregation and proxy values. Candidate pools are experiment 44's full-context test judges (12), H2-only (4) and broad test judges (18), plus each pool restricted to proxy-computable judges. Missing proxies remain in declared pools, H2/random baselines and hindsight oracle. Uniform exact ties; no outcome-fitted tolerances. H2 is an expectation over individual judges, not an ensemble.

For each pool report train, validation, test, and the historical validation+test combined view. Also report experiment 44's three reference sensitivities on the combined view: exclude placeholder references, exclude ambiguous references, exclude both. All-five and three-rater targets use identical availability masks. Require at least 90% of each declared subset shared across the pool; otherwise report unavailable, including the exact dropped items. Median available accepted criterion repeats; preserve the original allowance for fewer than 3 repeats and report it. Reproduce stored original three-rater per-judge point estimates before interpreting new results.

## Task-grouped selection experiment

Restrict to the 12 full-context experiment-39 test-judge configurations, keeping the judge-model and task split axes separate. Compute three candidate behavioral rules on TRAINING TASKS ONLY:

1. Mean original deletion-ladder quality, with constant ladders zero and 80% valid-ladder coverage.
2. File-level-strict semantic weakening directional accuracy minus formatting false-alarm rate, clipped below at zero; require 80% observed coverage separately for both components. Strictness uses the existing experiment-42 audit labels and does not promote them to new formal proofs.
3. Geometric mean of the two preceding components, computable only if both are.

Each rule uniformly selects the judges attaining its exact maximum. Select one rule by highest expected all-five validation Spearman on the common pool mask; ties use the names lexicographically. Freeze its weights before test. Report all three rules as sensitivity views regardless of sign. The original global deletion selector is a retrospective comparator, not task-isolated screening.

Human-supervised controls: rank the same 12 judges by training Spearman, retain three, choose the largest validation Spearman (lexicographic ties). Run once on current-five training targets and once with an auxiliary training target = mean(current-five mean, old-pass mean). The auxiliary regime therefore has fixed half weight; it is not a seven-person average. Validation and test targets remain current-five in both conditions. This is finite cached judge selection, not model-weight training. No fitted score mapping or new prompt inference.

## Behavioral evidence audit

Recompute experiment-42 directional scores on each task partition and file-level strict/redundant/unclear subsets from all cached judge harvests. Check the original full-sample point metrics against the frozen semantic-screen receipt. Compilation receipts establish elaboration; forward implication plus failure to prove reverse does not establish strictness. Document missing countermodels and the near-empty candidate alpha-renaming support.

Recompute experiment-43 per-cell attacked gain, reference gain and gaming gap from the fresh repeat arrays; verify frozen means and count flagged edited files. Report task-partition coverage. Original human ratings apply to originals, not edited attacks or repaired starts. Do not create all-five human targets for edited files. The absence of training-task attacks prevents using these gaming outcomes as a clean training selector; record that missing evidence rather than fitting on validation/test attacks. Prepare one integrated prospective weakening-and-gaming follow-up after inspecting cached results.

## Statistics and reproducibility

Use 10,000 paired task-cluster bootstrap draws, seed 45. Copy all retained rows of a sampled task with multiplicity; keep selector weights fixed. Percentile 95% intervals are conditional on observed raters, fixed score caches and choices, and omit selection/model-population/annotation-process uncertainty. Report valid and undefined draw counts. For the primary selected-versus-H2 test contrast compute a two-sided paired task-block randomization p-value by swapping selected and H2 score blocks under the null of exchangeable methods; for randomized multi-judge selectors report p-val=n/a unless an exactly defined joint swap is implemented. Other descriptive values use p-val=n/a. Report raw-repeat sample standard deviation and counts; independent repeat batches of aggregate scores are unavailable.

Fail closed on source hash changes, duplicate keys, inconsistent task joins, invalid accepted score ranges, target reconstruction mismatch or frozen-statistic reproduction failures. Missing source caches remain missing. The analysis writes only this experiment and the owned recovery ledger/checkpoint. Record deviations without changing this locked file after new outcomes are computed.
