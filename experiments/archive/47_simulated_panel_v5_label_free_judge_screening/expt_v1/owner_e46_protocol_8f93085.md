# Total-variation-information-inspired properties on historical measured judges

**Doc link:** [canonical experiment](https://github.com/brando90/cert-judge/tree/codex/cj-e46-tvdmi-properties/experiments/46_tvdmi_inspired_properties_cached_judge_validation).
**Summary:** Define three scalar-score adaptations, then evaluate all three against existing human ratings using measured caches and no new inference. This is exploratory reuse of historical data, not the forthcoming prospective test.
**Frozen before computation:** 10-08-2026. Hash this file and all inputs before computing new property values. Correct implementation defects with explicit deviation records; do not silently change definitions after viewing outcomes.

## Source, scope and ownership

Source: Robertson and Koyejo, [Let's Measure Information Step-by-Step: AI-Based Evaluation Beyond Vibes, version 4](https://arxiv.org/html/2508.05469v4), revised 06-22-2026.
The paper measures dependence between response pairs using a language-model critic. Our adaptations operate on existing scalar judge scores and are not a reproduction of that critic.
Definitions below are owned by this experiment and may be reused by the separate simulated-rater sandbox (experiment 47). This experiment performs no simulated-rater pre-run.
Never access VeriBench set N, v6, set-B predictions, any private/sealed directory, or any new human sheet. Do not recruit raters, edit reference artifacts or manuscript, or call inference providers. Inputs are explicitly allowlisted below. Paid inference calls: zero. Execution: Stanford Network Analysis Project (SNAP), skampere1, named full-access worker.

## Normalization and the claim being tested

For finite distributions, total variation is D(P,Q)=0.5 sum_x |P(x)-Q(x)|, in [0,1]. The paper's information object compares a joint distribution with the product of its marginals. A fixed critic acceptance event E yields G=P_joint(E)-P_product(E), bounded above by population total variation. An empirical gap is a noisy estimate, not a certified population bound.
Information can be preserved by an incorrect or reversed judge. The data-processing inequality does not prove that coverage scores decrease after a semantic edit. The orientation gates below are additional domain hypotheses.
Do not confuse 2*AUC-1 (area under a receiver operating characteristic curve transformed to [-1,1]) with the maximum threshold-specific Youden statistic. Existing legacy code is not authority for that equality.

## Allowed historical evidence

- experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/{panel.json,probe_manifest.json,units_train_val.json,units_test.json,harvest/*.json}; its scripts/analysis_lib.py may be reused after inspection.
- experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/results/{semantic_probe_manifest.json,harvest/*.json}, and probe_edits/audit/*.json. Strict/redundant labels are existing audits, not new formal countermodel proofs.
- experiments/archive/44_cached_score_judge_selection_utility/inputs/items.jsonl (metadata only) and scripts/analyze_selection_utility.py (pool and score parsing helpers).
- experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit/results/individual_current_ratings.json and inventory.json. Reuse scripts/analyze.py numerical helpers if useful, but never call its label-loading or inventory entry points or access other VeriBench data.
- Published protocols/reports in these four experiments may be read as context. Historical archive/03_tvdmi simulated scores are NOT measured evidence.

Use only accepted measured/deterministic cells, scores in [0,1], unique cell IDs, and frozen valid probes. Preserve rejected/missing counts. Probe medians require at least two of three repeats. Criterion medians retain the historical parser's coverage rule and report repeat counts. No imputation. Five current-rater mean is the primary target; three current-rater mean is sensitivity. Targets and split labels come from the self-contained published 75-row rating artifact. Keep original train/val/test task splits (10/5/10 tasks, 30/15/30 candidate files). No auxiliary old-prompt passes.

## Exact property definitions

All reported scalar properties average eligible tasks equally. For each split, the property is available only if at least ceil(0.8 * declared eligible tasks) are observed. Report numerator, denominator and reasons. Declare task eligibility from metadata before reading judge outputs. Constants remain in denominators.

### 1. Semantic-over-format discrimination (semantic_auc)

Declared tasks contain at least one valid audit-strict weakening probe and at least one valid formatting probe. A task is observed when its identity baseline, every declared formatting probe and at least 80% of its strict weakening probes have medians. The identity baseline in experiment 42 is kind ident, level 1.
For each weakening probe define d_sem = identity_median - weakening_median (signed). For formatting define d_fmt = abs(identity_median - formatting_median). Within each task compare every available strict weakening/formatting pair: AUC_task = mean(1[d_sem>d_fmt] + 0.5*1[d_sem=d_fmt]). Use numerical tie tolerance 1e-12. Property = mean_tasks(2*AUC_task-1). Range [-1,1]; a constant judge scores 0, reversed semantic responses score <=0.
Also report fixed acceptance gaps mean_tasks(P(d_sem>t)-P(d_fmt>t)), t in {0,.01,.05,.10,.20}; do not select a threshold. The existing threshold-zero strict-weakening-minus-directional-formatting baseline is reported separately, using the previous experiment's exact aggregate definition. This new property tests score magnitudes and charges formatting changes in either direction.

### 2. Within-task repeat information (repeat_tvd)

Declare every historical task with at least two candidate files. Observe a task only with all three accepted criterion repeats for at least two candidates. Keep true repeat indices, and reject duplicates. Bin s in [0,1] with q(s)=min(4,floor(5*s)); five fixed bins, no fitted edges.
For each ordered pair of distinct repeat indices (r,s), form P_rs(a,b) by choosing a candidate uniformly and pairing its two scores. Form Q_rs(a,b) by choosing each candidate independently (INCLUDING equal candidates); Q_rs equals the product of corresponding empirical marginal histograms. P and Q are the equal mixtures over the six repeat-index pairs. The task value is D(P,Q); property = mean_tasks D(P,Q), range [0,1]. Do not pool across task IDs: a task-ID-only signal must score zero.
This empirical dependence is positively biased in tiny samples and can reward arbitrary candidate IDs. It is a diagnostic, not a standalone certification. Report per-task candidate counts and the deterministic constant / reversed-bin / candidate-ID fixtures. Do not subtract an outcome-selected null estimate.

### 3. Direction-gated deletion information (deletion_tvd)

Use valid gold deletion ladders from experiment 39, with identity level 0 as baseline, and every declared valid ms_gold level in increasing deletion order. The frozen ladder removes theorem statements AND unit tests; structural validity does not prove each removal changes the overall guarantee. Declare tasks with at least one valid deletion level; observe only complete ladders with at least two accepted repeats at every level.
For a task with K levels, P(L,S) chooses level uniformly and then one of its accepted repeats uniformly, using the same five score bins. Q=P_L*P_S. Set I=D(P,Q)/(1-1/K), in [0,1]. Define orientation O as the mean over all earlier/later level pairs of sign(median_earlier-median_later), with 1e-12 ties. Task property=max(0,O)*I; scalar property=mean_tasks of those task values. Report I and O separately. Constants score zero; a perfectly reversed ladder is rejected by the direction gate.
Compare to frozen gold deletion monotonicity C_ms_gold, computed on the same split with the historical helper (also report its own coverage). Do not rename these adaptations PTI-v0.

## Evaluation and decision rules

Calculate all three properties on each task split for all 56 measured language-model configurations. Primary selection pool is the existing 12 primary_full_context configurations returned by experiment 44's pools helper; never redefine it after outcomes. Each property separately selects the maximum TRAIN-only property in this pool, distributing weight uniformly across ties within 1e-12. Missing property configurations are ineligible for that selector only. Do not pick a winning property using validation or test ratings.
Baselines: maximum train C_ms_gold; maximum prior train strict-minus-format property; uniformly choosing any of the 12 configurations; uniformly choosing one of the four fixed H2-rubric configurations. These are expected utilities of selecting one judge, not score ensembles. Preserve all pool members for common criterion support. Evaluate val and test separately; primary interpretation is the historical test split. Require >=ceil(.9*declared files) common criterion support across the full 12-configuration pool per split or mark comparison unavailable. No relaxing this rule. Keep each unavailable result and reason.
For each selector report expected Spearman, Pearson and Kendall correlations, mean absolute error, mean bias (judge minus human), judge mean and human mean on the same files, plus paired differences from H2. Report counts/tasks and repeated-score sample standard deviations. Compute 95% percentile intervals with 10,000 paired task-cluster bootstrap draws, fixed selected weights, seed 20261008. Report finite/undefined draw counts, p-val=n/a (descriptive intervals, no significance decision). Intervals condition on the selected pool, cached scores and raters; they omit selector uncertainty, model-population uncertainty and new-rater uncertainty.
Secondary association: across the same 12 configurations, associate each train property with test human-agreement Spearman using Spearman, Pearson and Kendall, requiring >=3 finite configurations. Bootstrap test task clusters with properties fixed, report conditional intervals and limitations. The 56-configuration overview shows property distributions, coverage and saturation; do not imply these correlated prompt variants are independent model replications.
No universal pass threshold is claimed. A candidate is useful for follow-up if it has correct controls, nontrivial spread and interpretable complementary behavior. Evidence of useful selection requires an actual paired utility improvement; an interval crossing zero is inconclusive. Report every property even if negative, saturated or unavailable. This reused historical test is exploratory and cannot establish prospective generalization.

## Required artifacts and verification

Create reusable pure numerical property functions, an offline allowlisted analysis command, and meaningful deterministic tests: hand-computed independent/perfect/constant finite distributions; invertible-bin relabeling invariance; bin coarsening cannot increase total variation; correct/reversed ladders; semantic ties/formatting changes in both directions; product pairing includes equal candidate indices; task-ID-only control zero and candidate-ID-only counterexample positive; coverage and duplicate failures.
Save input SHA-256 inventory, frozen selector weights before human metric evaluation, per-task properties, configuration overview, full bootstrap summaries, controls, runtime model/effort/permissions receipt, results.md and RESULTS.md. Make a small scientific figure if it clarifies the outcome. Record software versions and code revision. All computation on SNAP. Before publication verify input hashes unchanged, relevant tests and experiment layout, and inspect exact staged changes for secrets. Archive completed work, preserving frozen protocol bytes and updating executable root discovery, inventory and index. Do not modify unrelated active experiments or manuscript.
