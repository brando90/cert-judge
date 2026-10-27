# Cert judge project assessment

**TLDR:** Continue testing whether a Proxy Trust Index (PTI) predicts the human-grounded Trust Index (TI), but prioritize its ability to select useful new judges. The completed pooled test is promising; prompt-group differences, limited independent judges, and unresolved criterion validity prevent a general claim that the proxy replaces human evaluation.

**Completed follow-up (10-05-2026).** The proposed cached-score study is now complete, verified and merged: [44_cached_score_judge_selection_utility](../experiments/archive/44_cached_score_judge_selection_utility/RESULTS_selection_utility.md), [pull request #55](https://github.com/brando90/cert-judge/pull/55). In the primary pool of 12 configurations, evaluated on 42 shared files from 15 tasks, proxy selection achieved Spearman 0.768 versus 0.853 for uniform selection among fixed human-mirror H2 configurations. The paired difference was -0.086 [-0.308, 0.058], p-val=n/a, using 10,000 task-cluster bootstrap draws conditional on this fixed pool. This does not demonstrate a selection advantage, and it preserves the original registered association result. Nine tests passed; no new judge calls or human labels were used. All workers started for this study have exited. The assessment below records the earlier reasoning that motivated this now-completed study.

Assessment date: 10-05-2026. Repository revision: `fc73f78696d53551cd57f13094ec6f73fbb1c234`, also the fetched `origin/main`. This is a local assessment, not a published manuscript update.

The [weekly notes](https://docs.google.com/document/d/1xkEn8vW800jBucuJANuXD8ph-sMQMofwNZw_nJzjJls/edit?tab=t.0) still contain the pasted certjudge block under 10-02-2026. The newest 10-05-2026 section emphasizes VeriBench human ratings and generalization to unseen candidate-generating agents. Those can supply useful shared data, but testing a judge on new generators and testing a proxy on new judges are different evaluations.

**What the project should establish.** I interpret the user's “TTI” as the expensive human-grounded criterion called TI in the repository. The [frozen definition](spec/PTI_V0.md) separates underlying trustworthiness, its measured human criterion, and the proxy. The current primary criterion is a judge's Spearman rank correlation with human ratings across candidate files. The outer correlation asks whether proxy scores rank judge configurations by that human agreement. It does not predict the numerical agreement value, establish a deployment threshold, or incorporate stability into the target. If trustworthiness requires both human agreement and repeatability, both must appear in the future acceptance criterion. Label-free describes evaluating a subsequent judge; humans were used to select the proxy itself.

**The central result.** [39_label_free_proxy_index_train_val_test_over_judge_families](../experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/RESULTS_proxy_index_train_val_test.md) selected `C_ms_gold`, the single component measuring whether scores decrease as theorem statements are deleted from reference artifacts. This is a new candidate proxy, not the original four-property PTI version zero (`PTI_v0`) or the historical variance-aware index (`TI_var`).

| Judge split | Configurations contributing | Spearman | Pearson | Kendall |
|---|---:|---:|---:|---:|
| Train | 18 | 0.761 | 0.643 | 0.569 |
| Validation | 20 | 0.762 | 0.759 | 0.537 |
| Test | 16 of 18 declared | 0.558 [0.078, 0.762] | 0.643 | 0.360 |

Source: [selection and test receipt](../experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/TEST_RECEIPT.json). The test Spearman has p-val=0.0127, a one-sided positive-association permutation test. Train/validation intervals and p-values are unavailable in this receipt; these splits selected the index. Test Pearson/Kendall intervals are unavailable. The 95% interval uses 10,000 configuration bootstrap samples, seed 39. It does not account for shared model/prompt clusters or uncertainty in the estimated human-agreement targets.

The recorded pass is legitimate under the [predeclared rule](../experiments/39_label_free_proxy_index_train_val_test_over_judge_families/PROTOCOL.md): point correlation at least 0.45, plus positive-association permutation p below 0.05. **The p-value does not test that the population correlation exceeds 0.45.** The lower confidence limit is 0.078. Preserve the registered verdict while reporting this distinction.

The criterion reuses 45 rated candidates from 15 tasks, with available corrected expert ratings averaged and judge scores aggregated over three repeats. The held-out dimension is judge configuration. Test includes two unseen single-call models plus agent configurations; Sonnet's underlying model occurs in train and the agent harness occurs in validation. Prompt families and human-rated items recur across the judge splits. This supports conditional transfer to new configurations on this panel, not generalization to new candidate generators, domains, or independent human panels.

The frozen criterion includes 9/45 candidates from three placeholder-reference tasks and 9/45 from three other tasks whose reference statements changed within the annotation window. Eighteen candidates have two expert ratings and 27 have three. These are read-only counts from VeriBench's [100_karpathy_recipe_tc_judge_search_human_train_val_test input file](/Users/brandomiranda/veribench/experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/items.jsonl), filtered to `split` equal to `val` or `test`. Its SHA-256 fingerprint (`ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c`) matches the committed [probe manifest](../experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/probe_manifest.json). The source study already warns about placeholder-driven agreement. That does not establish inflation of this experiment's outer correlation, but checking the criterion without placeholder or ambiguous-reference tasks is necessary before broadening the claim.

The advertised 28,591 count is scoring-call cells, including repeats and criterion calls, not distinct Lean-validated probes. The [ledger](../experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results.md) records only 3/75 original candidates elaborating with the selected Lean toolchain. Originals remain in criterion scoring; transformed probes must elaborate. Candidate-side invariance components therefore have very thin coverage, and reordering has none. These failures do not prove the original artifacts are intrinsically invalid under their own environments.

The frozen PTI has test Spearman -0.274 [-0.753, 0.111], p-val=0.779, on only 9/18 configurations; eight values are zero. Only 6,517/10,000 bootstrap draws retain variation. The historical variance-aware index has -0.332 [-0.636, 0.135], p-val=0.914, on 18 configurations. These are the receipt's positive-association tests and configuration intervals. They provide no positive transfer validation; comparing them directly to the selected proxy's 16 configurations is not a paired superiority test.

**A practical screening concern from the saved results.** Post hoc read-only calculations for this assessment restrict the existing test rows by their recorded prompt identifiers:

| Test subset | Measured configurations | Spearman [95% configuration interval] | Positive-association permutation p-val |
|---|---:|---:|---:|
| Original pooled result | 16 | 0.558 [0.078, 0.762] | 0.0127 |
| Exclude the deliberately lexical prompt | 14 | 0.453 [-0.177, 0.825] | 0.0551 |
| Fuller-context prompts D0/H0/H1/H2/R4 | 10 | -0.371 [-0.787, 0.304] | 0.8615 |

The lexical-excluded row has Pearson 0.824 and Kendall 0.331; the fuller-context row has Pearson -0.319 and Kendall -0.225. Intervals for these secondary statistics were not computed. These exploratory calculations use the existing statistics functions, 10,000 draws and seed 39; they retain the original dependence limitations and do not replace the registered test. The fuller-context subset still contains different rubrics and models; it is not a controlled causal comparison. The primary human-mirror rubric H2 alone has only three measured test configurations, below the protocol's eight-unit minimum.

The [legacy prompts](../experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts/legacy.py) see only the reference's last theorem block. Thus the pooled positive association can reflect differences between rendering groups without providing reliable rankings within the set of judges one would actually consider deploying. The evidence warrants testing that explanation; the small negative subset estimate does not prove the proxy fails generally.

**What the other completed studies contribute.**

| Experiment and record | State and implication |
|---|---|
| [41_paper_panel_provenance_audit_and_vb_expert_label_rescore](../experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md) | Done. Confirms the old paper used one annotator's superseded label passes. Its reconstructed provenance matches only 7/24 scored tasks; corrected-label results on 21 items are inconclusive. Exact rating times and historical judge invocation are unavailable, so this is a serious provenance concern, not certain reconstruction of every viewed byte. It concerns the legacy paper and does not directly invalidate the newer criterion. |
| [42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges](../experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/REPORT.md) | Done. 15/56 pass the combined semantic screen. However, 31/57 weakening probes preserve the whole file's guarantee through redundant statements; unchanged scores can be appropriate. On 25 strictly weaker probes, Sol/H2 accuracy rises from 0.39 to 0.84 and Luna/H2 from 0.44 to 0.92. These are sensitivity point estimates; intervals are not provided in the report's comparison. Prioritize semantic validity of the screen over more volume. |
| [43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index](../experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/REPORT.md) | Done. Six prompts of one judge model, one attacker, 15 items from six tasks. No configuration's mean gaming-gap 95% task-bootstrap interval lies wholly above zero. One estimate is +0.033 [-0.103, +0.142], p-val=n/a; individual gaps can be positive. The reference is a model ensemble, and final edited candidates have no human ratings. Shared errors remain possible. |
| [archive/40_best_of_k_judge_selection_bias_validation_set](../experiments/archive/40_best_of_k_judge_selection_bias_validation_set/REPORT.md) | Done and archived. Choosing among eight judges on 12/24 historical problems overstates agreement by 0.153 on average over 4,000 splits. Monte Carlo standard error is 0.004–0.005; the 95% split range is [-0.334, 0.689], not a confidence interval for the population mean, p-val=n/a. It motivates independent selection/evaluation, not a universal 0.15 correction. |

The semantic study reports weakening association 0.73 [0.55, 0.86], p-val<0.001, over 38 train/validation configurations and 0.72 [0.31, 0.92], p-val=0.001, over 18 test configurations. These positive-association tests and intervals resample configurations; the test analysis is post hoc and models are shared. Adding its semantic score to the selected index gives a test difference +0.11 [-0.13, 0.39], p-val=n/a, with no established incremental benefit.

The gaming summary also needs correction: 59/62 edited candidates have **any** deterministic flag; 50/62 have ground statements, meaning unit tests expressed as theorems. Files mix legitimate properties and flagged additions. The data do not establish that every score increase was caused by test stuffing or that every judge was fooled. “No statistically resolved excess over another model judge” is the defensible result; “never beaten” is too strong.

The [master checkpoint](../experiments/CKPT_MASTER_tmux1_cc_6043a46f.md) records all four recent studies completed and merged, with workers idle and watches removed as last checked on 09-30-2026. Remote processes were not re-inspected for this assessment. The four folders still appear active in the inventory because archiving is overdue; the layout checker passes its current structural inventory, which does not make these runs active.

**What to do next.** Priority scores below are judgments about value for this project's stated goal, not measured quantities.

1. **[p 10/10] Establish whether the existing signal is useful for choosing judges.** Preserve the registered result and document sensitivity to prompt/input groups, missing configurations, model/harness clustering, and criterion items. Compare choosing by the proxy with a fixed human-mirror rubric, simple heuristics, and random selection; report the human-agreement loss relative to the best available judge. Check ordinary reference tasks separately from placeholder or provenance-ambiguous tasks. This can use stored scores before requesting more inference.
2. **[p 9/10] Freeze a prospective screening test with fresh human evidence.** Specify whether the output is a ranking, a predicted numerical agreement, or an accept/reject decision. Freeze the proxy, probe validity, rubric, exact reference/candidate bytes, missingness, repeats, and success criterion before new labels or test results are examined. Include genuinely new judges with matched information access and contemporary candidate generators. If a deployment screen is intended, measure false acceptance and selection loss in addition to correlation, with thresholds justified by the intended use. Choose sample size using clustered precision/power rather than an arbitrary judge count.
3. **[p 8/10] Update the manuscript's scientific story.** The active [abstract](../paper_latex/ICLR_2027_submission/00_abstract.tex) still centers the old variance-aware index and 72-pair panel; [limitations](../paper_latex/ICLR_2027_submission/06_limitations.tex) still describe now-completed semantic/gaming work as untested. Incorporate the old indices' failures, provenance uncertainty, selected-proxy result, and practical-screening limits together. A number substitution would leave the argument wrong.
4. **[p 5/10] Use semantic and gaming studies to design the new human panel.** Include truly weaker whole-file specifications and edited candidates that both model judges reward. Human adjudication here directly tests a shared blind spot. More attacks evaluated only against the same model reference would not resolve it.
5. **[p 2/10] Archive completed studies and refresh the inventory.** Preserve frozen evidence and update executable references in one later maintenance change. This improves project visibility but is not the research bottleneck.

One shared human panel can support both VeriBench and cert-judge if its rubric and bytes match both questions. Simulated raters can help debug or design the procedure; agreement with them cannot establish agreement with people. A successful screen would amortize human labels over subsequent judges within a validated scope, not remove the need to check major distribution changes.

**Suggested replacement for the weekly project line.** Certjudge: a selected label-free deletion-monotonicity score passed the recorded held-out-judge rule on 16 configurations (Spearman 0.56 [0.08, 0.76], p-val=0.013 under configuration permutation), but useful screening among comparable judges is still unresolved. The pooled result weakens after separating input/prompt groups, the original indices lack positive transfer evidence, and semantic/gaming studies expose validity limits. Next: existing-score robustness and selection-utility analysis, then a frozen prospective evaluation with fresh human ratings.

**Reproduce the assessment's two subset checks.** This reads committed scores and performs no model calls; it writes no experiment outputs and leaves the frozen protocol unchanged.

```python
import json
import sys
from pathlib import Path

repo = Path('/Users/brandomiranda/cert-judge')
study = repo / 'experiments/39_label_free_proxy_index_train_val_test_over_judge_families'
sys.path.insert(0, str(study / 'scripts'))
import analysis_lib as analysis

units = json.loads((study / 'results/units_test.json').read_text())['units']
subsets = {
    'without_lexical': [u for u in units if u['config'].split('|')[1] != 'LEX'],
    'fuller_context': [u for u in units if u['config'].split('|')[1]
                       in {'D0', 'H0', 'H1', 'H2', 'R4'}],
}
for name, rows in subsets.items():
    result = analysis.association(rows, 'C_ms_gold', draws=10000, seed=39)
    print(name, json.dumps(result, sort_keys=True))
```


**Live execution check, 10-05-2026 at 10:20 p.m. Pacific.** Read-only inspection of skampere1 found completion markers for all four recent studies, zero cert-judge watchdog entries in the user crontab, and only shell/sleep processes in their checkouts; no scoring or analysis worker was observed. Existing terminal sessions are remnants, not evidence of continued experimentation. The separate Codex chat titled “Experiment 29: release published; post-release review 0/3,…” was actively auditing project status at this moment; its activity was not an experiment launch. This check covers the known execution host and workers, not every possible remote service or unregistered job.
