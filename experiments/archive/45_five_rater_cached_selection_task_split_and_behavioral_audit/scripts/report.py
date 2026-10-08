"""Render the concise report from verified result artifacts, without recomputation."""
import json
from pathlib import Path
E=Path(__file__).resolve().parents[1];P=E/'results'
def read(n):return json.loads((P/n).read_text())
def fmt(r):
    if r['value'] is None:return 'unavailable'
    return f"{r['value']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]" if r.get('lo') is not None else f"{r['value']:.3f} [unavailable]"
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(map(str,r))+' |' for r in rows]])
R=[]
def add(s):R.append(s)
add('''# Five-current-rater cached comparison and stronger behavioral study

**Doc link:** [Experiment home](README.md)

**Status:** COMPLETE — cached analysis and prospective design; no new inference or manuscript edits.

Using all five current raters preserves the deletion proxy’s association with judge quality, but does not demonstrate that proxy-based selection beats the fixed human-rating rubric. The new validation-selected procedure cannot be evaluated under its locked coverage rule. The next useful study should improve the validity and difficulty of semantic and gaming controls before purchasing more judge scores.

## Data and interpretation

The audited parser yields **345 current observations on 75 outputs from 25 tasks**: participants 1–5 contribute 75, 75, 45, 75 and 75 ratings. Participant 3’s missing 30 observations are retained as missing; the current-five target averages four or five available ratings per output. The earlier current-three target uses 195 observations. Both targets are normalized from 0–5 to 0–1. Compiled rating files are duplicate aggregations, not extra participants. The parser’s two documented missing-tab repairs are reused unchanged.

The established task split contains 10/5/10 train/validation/test tasks and 30/15/30 outputs. All outputs for each task stay together. Historical participant-one passes are a different instruction regime: only 60 observations on training tasks enter the declared auxiliary sensitivity, with one-half weight on the current-five mean and one-half on the old-pass mean. The other 90 historical observations are excluded from all new fitting, selection and evaluation. No historical validation/test targets are reported here.

All 75 candidate files match the pinned VeriBench input snapshot byte-for-byte; 177 manifest files were hash-verified. Across 25 references, 11 are byte-identical, five retain identical statements and nine have changed statements between reconstructed annotation-era and later snapshots. These are repository reconstructions, not proof of exactly what raters saw. Prior outcomes and this panel have been exposed repeatedly; these analyses are exploratory. Adding two raters changes the target, rather than correcting the previous target or creating an independent holdout.

## Proxy association survives the target change

The frozen gold-statement-deletion component (`C_ms_gold`) measures score decline along the original deletion ladders. We preserve its original values and original train/validation/test **judge-model** partitions from `experiments/39_label_free_proxy_index_train_val_test_over_judge_families/`. These partitions are separate from the task split. In this table, every criterion uses each judge’s supported outputs from the original 45 validation-plus-test outputs (15 tasks), subject to the original 90% criterion coverage gate. The association is between proxy values and judge–human Spearman agreement across judge configurations.

All intervals in this report are percentile 95% task-cluster bootstrap intervals, with 10,000 draws and seed 45; **p-val=n/a** throughout (no hypothesis test performed). They condition on the recorded raters, fixed caches and selectors. Proxy-association intervals additionally condition on the fixed judge panel; they are not the original study’s judge-unit intervals and do not establish transfer to a new population of models.''')
a=read('proxy_associations.json')['comparisons'];rows=[]
for split in ('train','val','test'):
 x=a[f'original45__judge_{split}__C_ms_gold'];rows.append([split,f"{x['included_judges']}/{x['declared_judges']}",fmt(x['association']['three']['spearman']),fmt(x['association']['all5']['spearman']),fmt(x['target_difference']['spearman'])])
add(table(['Judge-model partition','Included / declared','Three-rater Spearman','Five-rater Spearman','Paired target change'],rows))
x=a['original45__judge_test__C_ms_gold'];add(f"For the 16 included test-judge configurations, five-rater Pearson is {fmt(x['association']['all5']['pearson'])} and Kendall tau-b is {fmt(x['association']['all5']['kendall'])}, p-val=n/a. All 10,000 draws are defined. The two missing deletion proxies remain excluded explicitly. On task-test outputs alone, the same frozen proxy has Spearman {fmt(a['test__judge_test__C_ms_gold']['association']['all5']['spearman'])}, p-val=n/a (9,999 finite draws). This is sensitivity analysis, not a newly selected index.")
rows=[]
for k,name in [('C_ident','Identity-score component'),('PTI_v0_frozen','Frozen behavioral proxy version 0'),('TI_var_trainnorm','Historical variance-aware index')]:
 x=a[f'original45__judge_test__{k}'];rows.append([name,f"{x['included_judges']}/{x['declared_judges']}",fmt(x['association']['three']['spearman']),fmt(x['association']['all5']['spearman'])])
add(table(['Frozen comparator','Test judges','Three-rater Spearman','Five-rater Spearman'],rows))
add('''The identity component is a descriptive comparator, not a replacement selected on these outcomes. Every train/validation/test judge-panel result, Pearson and Kendall statistic, support mask and undefined-draw count is in [proxy_associations.json](results/proxy_associations.json).

## Selection utility remains unresolved

The frozen deletion selector picks `t2_sonnet5|D0` (Terminus2 agent harness with Claude Sonnet 5 and its original D0 rubric). The fixed human-rating-rubric baseline (`H2`) is uniform selection among four H2 judges, **not an ensemble of their scores**. The primary pool has 12 configurations; exact score ties receive uniform weights. Both targets use the same common-support masks. Values below are expected individual-judge Spearman agreement.''')
rows=[]
for view in ('original45','test'):
 r=read('comparisons/primary_full_context__declared__'+view+'.json')
 for target in ('three','all5'):
  q=r['analysis'][target];rows.append([view,target,f"{r['common_items']}/{r['declared_items']}; {r['common_tasks']} tasks",fmt(q['selectors']['proxy_C_ms_gold']['metrics']['spearman']),fmt(q['selectors']['human_mirror_H2']['metrics']['spearman']),fmt(q['contrasts']['proxy_C_ms_gold-human_mirror_H2'])])
add(table(['Task view','Human target','Outputs; tasks','Frozen proxy','Fixed H2','Paired difference'],rows))
add('''The five-rater paired differences span zero; superiority remains unresolved, not disproved and not equivalent performance. The original three-rater point result reproduces the preceding utility study. The original-45 view has 10,000 finite paired draws; test-only has 9,999, with one undefined draw from a constant resample. No zero-correlation significance tests are used. The locked primary new selector has no result, so its planned randomization test cannot be performed; the fixed-H2 baseline is a randomized multi-judge expectation, for which the protocol leaves p-val=n/a without a defined joint swap.

Five-rater test-only score levels on 29 outputs / 10 tasks are below. Mean absolute error and bias use the 0–1 scale; **bias = judge minus human, positive means lenient**. Means refer to that same mask.''')
r=read('comparisons/primary_full_context__declared__test.json');q=r['analysis']['all5']['selectors'];rows=[]
for k in ('pearson','kendall','mae','bias','judge_mean','human_mean'):
 rows.append([k,fmt(q['proxy_C_ms_gold']['metrics'][k]),fmt(q['human_mirror_H2']['metrics'][k])])
add(table(['Metric','Frozen proxy','Fixed H2 expectation'],rows))
add('''Criterion scores retain the original median-of-available-repeats rule. The selected judge has 87/87 cached repeats (three per item); mean within-item sample standard deviation is 0.077. H2 members have 87, 81, 82 and 87 of 87 expected repeats; their mean within-item standard deviations are 0.012, 0.060, 0.037 and 0.050. These are raw-score variability, not repeatability of independently collected aggregate batches, which was not measured.

The full declared grid contains **42 views: 34 computed and eight unavailable** at the frozen 90% common-support requirement. The same-rubric test-only sensitivity has all 30 outputs; proxy-minus-H2 is ''')
rr=read('comparisons/same_H2__declared__test.json');add(fmt(rr['analysis']['all5']['contrasts']['proxy_C_ms_gold-human_mirror_H2'])+', p-val=n/a. All masks, missing items, repeat counts and reference-quality sensitivities are retained in [comparisons/](results/comparisons/).')
add('''## Why the new selection procedure is unavailable

The frozen full-context validation mask contains **13/15 outputs**, below the 90% rule’s required **14/15**. Missing D0 criterion scores are `2_heappush__agent0` and `binary_search__agent2`; the test mask lacks `4_json_decoder__agent0`. These are pre-inference extraction failures. More calls with the unchanged extraction contract cannot repair them. We did not drop the rubric, relax the gate or choose a validation winner from the incomplete mask.

Training-task-only deletion and joint selectors tie across four D0 configurations. Strict-weakening discrimination ties eleven of twelve configurations at 1.0: its strict probes cover only 11 examples on five training tasks, with one judge observing 10/11. The remaining judge scores 10/11. This screen offers little resolution among these configurations. Its final weights were frozen before test evaluation; the three rule sensitivities remain available, but none is relabeled a validation-selected winner.''')
rows=[]
for k in ('train_deletion','train_strict_weakening','train_joint'):
 rows.append([k,fmt(r['analysis']['all5']['selectors'][k]['metrics']['spearman']),fmt(r['analysis']['all5']['contrasts'][k+'-human_mirror_H2'])])
add(table(['Training-only rule','Five-rater test Spearman','Paired difference versus H2'],rows))
add('''The current-only supervised training shortlist is `qwen36|H2`, `t2_sonnet5|H2`, `qwen36|H1`; adding the fixed historical-training sensitivity changes it to `qwen36|D0`, `qwen36|H2`, `t2_sonnet5|H2`. Both validation winners and final supervised weights remain unavailable. Thus the historical signal changes the shortlist, but this run cannot establish a final selection benefit.

## Individual raters and historical-score sensitivity

Individual values and missingness are preserved in [individual_current_ratings.json](results/individual_current_ratings.json). Each row below compares one current rater with the mean of the other available current raters over that rater’s supported outputs. These conditional agreements are not guaranteed upper bounds on judge performance.''')
h=read('rater_agreement.json')['entries'];rows=[]
for i in range(1,6):
 x=h[f'all__participant{i}'];rows.append([i,f"{x['items']}; {x['tasks']}",fmt(x['metrics']['spearman']),fmt(x['metrics']['mae']),fmt(x['metrics']['bias'])])
add(table(['Participant','Outputs; tasks','Spearman','Mean absolute error','Rater-minus-others bias'],rows))
add('''Here positive bias means that participant is more lenient than the other-rater mean; the full JSON also reports both means, Pearson, Kendall and train/validation/test intervals. More raters do not automatically yield a more valid target.

The earlier `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/` already included all-five secondary comparisons; this work does not claim those labels were unused. The new contribution is the task-grouped frozen selection-utility comparison and its reproducible sensitivities. The fixed historical eight-prompt score panels were also recomputed against current targets without using old validation/test labels. The reference-matched subset has 21 outputs / seven tasks. Associations of its fixed historical variance-aware index with judge–human Spearman are:''')
rows=[]
for family in ('Codex','Claude_Opus','Qwen3_Coder'):
 x=read('legacy/'+family+'__matched.json');rows.append([family,fmt(x['analysis']['three']['index_vs_agreement']['spearman']),fmt(x['analysis']['all5']['index_vs_agreement']['spearman']),x['analysis']['all5']['index_vs_agreement']['spearman']['valid_draws']])
add(table(['Historical score family (eight prompts each)','Three-rater association','Five-rater association','Finite draws / 10,000'],rows))
add('''These small-panel descriptive intervals can have many undefined draws; they do not replace any historical experiment’s acceptance rule. All 15 family/subset views and original repeat evidence remain in [legacy/](results/legacy/).

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
''')
report='\n\n'.join(part.strip() for part in R).strip()+'\n'
report=report.replace('proxy-minus-H2 is\n\n','proxy-minus-H2 is ')
(E/'RESULTS_five_rater_comparison.md').write_text(report)
print('Rendered RESULTS_five_rater_comparison.md')
