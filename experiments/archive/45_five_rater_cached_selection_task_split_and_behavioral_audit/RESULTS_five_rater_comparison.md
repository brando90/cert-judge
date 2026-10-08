# Five-current-rater cached comparison and stronger behavioral study

**Doc link:** [Experiment home](README.md)

**Status:** COMPLETE — cached analysis and prospective design; no new inference or manuscript edits.

Using all five current raters preserves the deletion proxy’s association with judge quality, but does not demonstrate that proxy-based selection beats the fixed human-rating rubric. The new validation-selected procedure cannot be evaluated under its locked coverage rule. The next useful study should improve the validity and difficulty of semantic and gaming controls before purchasing more judge scores.

## Data and interpretation

The audited parser yields **345 current observations on 75 outputs from 25 tasks**: participants 1–5 contribute 75, 75, 45, 75 and 75 ratings. Participant 3’s missing 30 observations are retained as missing; the current-five target averages four or five available ratings per output. The earlier current-three target uses 195 observations. Both targets are normalized from 0–5 to 0–1. Compiled rating files are duplicate aggregations, not extra participants. The parser’s two documented missing-tab repairs are reused unchanged.

The established task split contains 10/5/10 train/validation/test tasks and 30/15/30 outputs. All outputs for each task stay together. Historical participant-one passes are a different instruction regime: only 60 observations on training tasks enter the declared auxiliary sensitivity, with one-half weight on the current-five mean and one-half on the old-pass mean. The other 90 historical observations are excluded from all new fitting, selection and evaluation. No historical validation/test targets are reported here.

All 75 candidate files match the pinned VeriBench input snapshot byte-for-byte; 177 manifest files were hash-verified. Across 25 references, 11 are byte-identical, five retain identical statements and nine have changed statements between reconstructed annotation-era and later snapshots. These are repository reconstructions, not proof of exactly what raters saw. Prior outcomes and this panel have been exposed repeatedly; these analyses are exploratory. Adding two raters changes the target, rather than correcting the previous target or creating an independent holdout.

## Proxy association survives the target change

The frozen gold-statement-deletion component (`C_ms_gold`) measures score decline along the original deletion ladders. We preserve its original values and original train/validation/test **judge-model** partitions from `experiments/39_label_free_proxy_index_train_val_test_over_judge_families/`. These partitions are separate from the task split. In this table, every criterion uses each judge’s supported outputs from the original 45 validation-plus-test outputs (15 tasks), subject to the original 90% criterion coverage gate. The association is between proxy values and judge–human Spearman agreement across judge configurations.

All intervals in this report are percentile 95% task-cluster bootstrap intervals, with 10,000 draws and seed 45; **p-val=n/a** throughout (no hypothesis test performed). They condition on the recorded raters, fixed caches and selectors. Proxy-association intervals additionally condition on the fixed judge panel; they are not the original study’s judge-unit intervals and do not establish transfer to a new population of models.

| Judge-model partition | Included / declared | Three-rater Spearman | Five-rater Spearman | Paired target change |
|---|---|---|---|---|
| train | 18/18 | 0.761 [0.626, 0.822] | 0.742 [0.604, 0.816] | -0.019 [-0.080, 0.045] |
| val | 20/20 | 0.762 [0.632, 0.844] | 0.741 [0.588, 0.830] | -0.021 [-0.074, 0.026] |
| test | 16/18 | 0.558 [0.402, 0.756] | 0.555 [0.420, 0.786] | -0.003 [-0.081, 0.160] |

For the 16 included test-judge configurations, five-rater Pearson is 0.636 [0.477, 0.734] and Kendall tau-b is 0.360 [0.243, 0.577], p-val=n/a. All 10,000 draws are defined. The two missing deletion proxies remain excluded explicitly. On task-test outputs alone, the same frozen proxy has Spearman 0.506 [0.318, 0.796], p-val=n/a (9,999 finite draws). This is sensitivity analysis, not a newly selected index.

| Frozen comparator | Test judges | Three-rater Spearman | Five-rater Spearman |
|---|---|---|---|
| Identity-score component | 18/18 | 0.697 [0.586, 0.753] | 0.682 [0.603, 0.763] |
| Frozen behavioral proxy version 0 | 9/18 | -0.274 [-0.274, -0.137] | -0.274 [-0.411, -0.134] |
| Historical variance-aware index | 18/18 | -0.332 [-0.454, -0.111] | -0.344 [-0.458, -0.084] |

The identity component is a descriptive comparator, not a replacement selected on these outcomes. Every train/validation/test judge-panel result, Pearson and Kendall statistic, support mask and undefined-draw count is in [proxy_associations.json](results/proxy_associations.json).

## Selection utility remains unresolved

The frozen deletion selector picks `t2_sonnet5|D0` (Terminus2 agent harness with Claude Sonnet 5 and its original D0 rubric). The fixed human-rating-rubric baseline (`H2`) is uniform selection among four H2 judges, **not an ensemble of their scores**. The primary pool has 12 configurations; exact score ties receive uniform weights. Both targets use the same common-support masks. Values below are expected individual-judge Spearman agreement.

| Task view | Human target | Outputs; tasks | Frozen proxy | Fixed H2 | Paired difference |
|---|---|---|---|---|---|
| original45 | three | 42/45; 15 tasks | 0.768 [0.396, 0.931] | 0.853 [0.646, 0.931] | -0.086 [-0.309, 0.056] |
| original45 | all5 | 42/45; 15 tasks | 0.794 [0.457, 0.933] | 0.834 [0.594, 0.926] | -0.040 [-0.212, 0.095] |
| test | three | 29/30; 10 tasks | 0.798 [0.319, 0.964] | 0.848 [0.557, 0.942] | -0.050 [-0.309, 0.119] |
| test | all5 | 29/30; 10 tasks | 0.815 [0.411, 0.950] | 0.826 [0.494, 0.936] | -0.012 [-0.198, 0.186] |

The five-rater paired differences span zero; superiority remains unresolved, not disproved and not equivalent performance. The original three-rater point result reproduces the preceding utility study. The original-45 view has 10,000 finite paired draws; test-only has 9,999, with one undefined draw from a constant resample. No zero-correlation significance tests are used. The locked primary new selector has no result, so its planned randomization test cannot be performed; the fixed-H2 baseline is a randomized multi-judge expectation, for which the protocol leaves p-val=n/a without a defined joint swap.

Five-rater test-only score levels on 29 outputs / 10 tasks are below. Mean absolute error and bias use the 0–1 scale; **bias = judge minus human, positive means lenient**. Means refer to that same mask.

| Metric | Frozen proxy | Fixed H2 expectation |
|---|---|---|
| pearson | 0.826 [0.505, 0.954] | 0.855 [0.650, 0.952] |
| kendall | 0.666 [0.315, 0.866] | 0.704 [0.408, 0.844] |
| mae | 0.197 [0.119, 0.289] | 0.142 [0.100, 0.196] |
| bias | -0.120 [-0.247, -0.008] | 0.038 [-0.017, 0.092] |
| judge_mean | 0.469 [0.256, 0.676] | 0.627 [0.452, 0.779] |
| human_mean | 0.589 [0.449, 0.715] | 0.589 [0.449, 0.715] |

Criterion scores retain the original median-of-available-repeats rule. The selected judge has 87/87 cached repeats (three per item); mean within-item sample standard deviation is 0.077. H2 members have 87, 81, 82 and 87 of 87 expected repeats; their mean within-item standard deviations are 0.012, 0.060, 0.037 and 0.050. These are raw-score variability, not repeatability of independently collected aggregate batches, which was not measured.

The full declared grid contains **42 views: 34 computed and eight unavailable** at the frozen 90% common-support requirement. The same-rubric test-only sensitivity has all 30 outputs; proxy-minus-H2 is 0.015 [-0.114, 0.178], p-val=n/a. All masks, missing items, repeat counts and reference-quality sensitivities are retained in [comparisons/](results/comparisons/).

## Why the new selection procedure is unavailable

The frozen full-context validation mask contains **13/15 outputs**, below the 90% rule’s required **14/15**. Missing D0 criterion scores are `2_heappush__agent0` and `binary_search__agent2`; the test mask lacks `4_json_decoder__agent0`. These are pre-inference extraction failures. More calls with the unchanged extraction contract cannot repair them. We did not drop the rubric, relax the gate or choose a validation winner from the incomplete mask.

Training-task-only deletion and joint selectors tie across four D0 configurations. Strict-weakening discrimination ties eleven of twelve configurations at 1.0: its strict probes cover only 11 examples on five training tasks, with one judge observing 10/11. The remaining judge scores 10/11. This screen offers little resolution among these configurations. Its final weights were frozen before test evaluation; the three rule sensitivities remain available, but none is relabeled a validation-selected winner.

| Training-only rule | Five-rater test Spearman | Paired difference versus H2 |
|---|---|---|
| train_deletion | 0.700 [0.389, 0.851] | -0.127 [-0.280, 0.112] |
| train_strict_weakening | 0.768 [0.451, 0.887] | -0.059 [-0.158, 0.056] |
| train_joint | 0.700 [0.389, 0.851] | -0.127 [-0.280, 0.112] |

The current-only supervised training shortlist is `qwen36|H2`, `t2_sonnet5|H2`, `qwen36|H1`; adding the fixed historical-training sensitivity changes it to `qwen36|D0`, `qwen36|H2`, `t2_sonnet5|H2`. Both validation winners and final supervised weights remain unavailable. Thus the historical signal changes the shortlist, but this run cannot establish a final selection benefit.

## Individual raters and historical-score sensitivity

Individual values and missingness are preserved in [individual_current_ratings.json](results/individual_current_ratings.json). Each row below compares one current rater with the mean of the other available current raters over that rater’s supported outputs. These conditional agreements are not guaranteed upper bounds on judge performance.

| Participant | Outputs; tasks | Spearman | Mean absolute error | Rater-minus-others bias |
|---|---|---|---|---|
| 1 | 75; 25 | 0.793 [0.646, 0.868] | 0.146 [0.120, 0.174] | -0.059 [-0.112, -0.007] |
| 2 | 75; 25 | 0.833 [0.675, 0.911] | 0.204 [0.159, 0.252] | -0.117 [-0.192, -0.043] |
| 3 | 45; 15 | 0.485 [-0.014, 0.806] | 0.187 [0.153, 0.218] | -0.133 [-0.194, -0.059] |
| 4 | 75; 25 | 0.507 [0.156, 0.748] | 0.248 [0.186, 0.315] | 0.221 [0.149, 0.297] |
| 5 | 75; 25 | 0.298 [-0.029, 0.586] | 0.221 [0.169, 0.279] | 0.035 [-0.056, 0.123] |

Here positive bias means that participant is more lenient than the other-rater mean; the full JSON also reports both means, Pearson, Kendall and train/validation/test intervals. More raters do not automatically yield a more valid target.

The earlier `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/` already included all-five secondary comparisons; this work does not claim those labels were unused. The new contribution is the task-grouped frozen selection-utility comparison and its reproducible sensitivities. The fixed historical eight-prompt score panels were also recomputed against current targets without using old validation/test labels. The reference-matched subset has 21 outputs / seven tasks. Associations of its fixed historical variance-aware index with judge–human Spearman are:

| Historical score family (eight prompts each) | Three-rater association | Five-rater association | Finite draws / 10,000 |
|---|---|---|---|
| Codex | -0.476 [-0.619, 0.119] | -0.405 [-0.667, 0.455] | 6664 |
| Claude_Opus | 0.048 [-0.333, 0.429] | 0.119 [-0.167, 0.500] | 8850 |
| Qwen3_Coder | 0.143 [-0.524, 0.667] | -0.143 [-0.500, 0.405] | 9724 |

These small-panel descriptive intervals can have many undefined draws; they do not replace any historical experiment’s acceptance rule. All 15 family/subset views and original repeat evidence remain in [legacy/](results/legacy/).

## Behavioral evidence and next experiment

The semantic audit reproduces all 60 cached configurations (56 model configurations plus four controls) to maximum absolute difference below 1.4×10⁻¹⁷. Its 194 valid probes include 57 weakening probes: 25 audited strict, 31 redundant at whole-file level, one unclear. Compilation and forward implication are insufficient to prove strict weakening; failure to prove the reverse implication is not a countermodel. No Lean compilation was rerun for this cache audit.

The gaming audit reproduces **90 cells / 720 attempts**, spanning six tasks: 36 validation cells and 54 test cells, **zero training cells**. Of 62 edited candidates, 59 are flagged by the existing artifact checks. Original human ratings cannot serve as labels for those edited or repaired files. The reference judge may also reward superficial edits; a small attacked-minus-reference gain therefore does not certify resistance. Per-judge attacked gains, reference gains and their differences, with task intervals, are in [gaming_audit.json](results/gaming_audit.json).

**[p 9/10] First build stronger, certified training-task probes without inference:** require a correct nonvacuous baseline, prove each adjacent implication over whole-file guarantees, and exhibit a countermodel for the reverse. Pair weakening with harmless renaming/formatting and equivalent gaming edits. This tackles the observed redundant/easy-probe and attack-validity gaps together.

**[p 8/10] Then evaluate selection utility under a separately frozen extraction contract and scope:** compare the finite training-screen rule set on validation tasks, freeze selection, and evaluate agreement with current humans on the original test outputs against fixed H2. Retain all failed or missing cells. A positive lower paired task-bootstrap bound is the proposed success criterion; merely causing scores to fall is insufficient.

**[p 7/10] Add adaptive attacks only after equivalent fixed attacks are validated:** certified equivalent edits permit measuring score inflation without fabricating human labels. Certificates automate formal relations; they cannot certify alignment of the baseline with informal human intent or transfer beyond this reused population.

The [prospective plan](PROSPECTIVE_PLAN.md) and [manifest](results/followup_manifest.json) enumerate 300 task/configuration cells, with a full-study maximum of 17,700 calls. This is an upper-bound design, **not a launch or spending authorization**; cost is unquoted and every cell is blocked on admission conditions. The cheapest next stage is the zero-call probe-validity work. [Proposed methods wording](PROPOSED_METHODS.md) contains a verified primary-source dataset-reuse citation and remains separate from the manuscript.

## Reproducibility and limits

The audited input inventory, protocol, selection seal, immutable-source hashes, 10,000-draw outputs and completion receipts are included. The main and supplementary computations completed on skampere2 with Python 3.12.3, NumPy 1.26.4 and SciPy 1.11.4. Four numerical/coverage tests passed; an independent verifier cross-checked 2,408 selector point statistics with SciPy, 177 input hashes, all view counts and all individual current labels. The portable verification and full reproduction commands are in [README.md](README.md).

The report preserves the original protocol, source caches and manuscript. It does not infer unseen outcomes, claim independence from earlier exposure, or convert unavailable validation selection into a negative result. The historical-score and proxy/rater completion summaries are documented post-protocol additions in [SUPPLEMENT.md](SUPPLEMENT.md).

**TLDR-end:** [cert-judge: 45_five_rater_cached_selection_task_split_and_behavioral_audit] Five-current-rater cached comparisons preserve the deletion proxy’s association with judge quality but do not demonstrate selection utility over the fixed human-rating rubric. The stronger next study should first establish meaningful weakening and equivalent gaming controls; new scoring remains unlaunched.
