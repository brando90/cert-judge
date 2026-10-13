# Experiments

Only currently pursued experiments belong directly in this directory.

Experiments 33a–33e, 34, and 38 finished and moved to `archive/` on 09-28-2026.
The unstarted catalog of reviewer-requested experiments moved to [ideas/35_missing_experiments_from_reviews](ideas/35_missing_experiments_from_reviews/EXPERIMENTS.md); it is the menu for the next pick, and a picked item gets its own numbered folder here.

| Active experiment | Current task |
|---|---|
| (none) | No experiment is active on 10-13-2026. The four 09-30-2026 studies (39, 41, 42, 43) are DONE and archived below; the paper rewrite that uses them is `docs/PAPER_FRAMING_DECISION_10-13-2026.md`. |

The completed proxy studies are archived; the suggested new-family follow-up
has not started and is not an active run. This is a repository classification,
not a claim about processes on remote machines.

| Location | Purpose |
|---|---|
| [archive/](archive/README.md) | Completed, superseded, or parked studies, including recent results. |
| [human_labels/](human_labels/) | Shared human-label data; not an experiment. |
| [ethan_hand_labels/](ethan_hand_labels/) | Shared human-label data; not an experiment. |
| [ideas/](ideas/README.md) | Optional, deferred research ideas; recording one does not launch it. |

The ignored local `keys/` directory is credential storage, not an experiment.

## Recent completed work

- [43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index](archive/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/REPORT.md): DONE 09-30-2026, archived 10-13-2026 — GPT-6 Luna attacked six Claude Sonnet 5 judge configurations on 15 low-coverage items for eight Lean-checked rounds (90 cells, 720 attempts, $60.21 Vals-reported); gaming gaps against the validated H2 reference ensemble were −0.162 to +0.033 with no task-bootstrap 95% interval above zero, but 59 of 62 edited candidates carry a deterministic flag (50 of 62 ground statements) that the reference also credited, and the label-free index did not predict resistance (`C_ms_gold` ρ +0.600, one-sided p 0.912; `TI_var` −0.086; `PTI_v0` not computable).

- [42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges](archive/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/REPORT.md): DONE 09-30-2026, archived 10-13-2026 — 194 Lean-validated vacuity, weakening, over-constraint and formatting probes scored by experiment 39's 56 judge configurations (32,592 Valkyrie calls, $656.15); 15 of 56 pass the locked semantic screen; weakening directional accuracy tracks experiment 39's expert criterion (Spearman 0.73 [0.55, 0.86] over 38 train + validation configurations; 0.72 [0.31, 0.92] over 18 test configurations, post hoc) and adds nothing to `C_ms_gold` on train + validation (Δ −0.06 [−0.16, 0.04]).

- [41_paper_panel_provenance_audit_and_vb_expert_label_rescore](archive/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md): DONE 09-30-2026, archived 10-13-2026 — zero model calls; gate G0 reproduces the paper's 0.833 / 0.905 / 0.738; the paper's labels are VeriBench participant 1's superseded old-prompt passes; 1 of 25 tasks was never scored (stale gold filename) and only 7 of the 24 scored tasks have reference bytes matching what the rater saw; the re-score on matched items against the corrected three-expert labels is inconclusive (Codex +0.333, Qwen3-Coder +0.667, Claude Opus −0.381; every bootstrap interval crosses zero).

- [39_label_free_proxy_index_train_val_test_over_judge_families](archive/39_label_free_proxy_index_train_val_test_over_judge_families/results.md): DONE 10-01-2026, archived 10-13-2026 — pre-registered PASS: the label-free gold deletion-monotonicity component `C_ms_gold`, selected on the train judges (Spearman 0.761, 18 configurations) and checked on validation (0.762, 20), predicts judge–human agreement on the held-out test judges with Spearman 0.558 [0.078, 0.762], one-sided permutation p 0.0127 (16 of 18 declared configurations; 56 configurations, 28,591 Lean-validated probe cells, $574 Vals-reported); the paper's frozen `PTI_v0` (−0.274, 9 configurations) and `TI_var` (−0.332, 18) do not transfer; only 3 of 75 rated candidates elaborate under Lean 4.22, so the candidate-side components are near-empty.

- [46_tvdmi_inspired_properties_cached_judge_validation](archive/46_tvdmi_inspired_properties_cached_judge_validation/RESULTS_information_properties.md): completed 10-08-2026 — zero-inference historical measured-cache analysis of 56 judge configurations. Repeat total variation distance selected historical-test Spearman 0.844 [0.472, 0.951] versus fixed H2 0.826 [0.507, 0.934] (paired difference +0.018 [−0.127, +0.186], 29/30 common files, 10 tasks, 10,000 task-bootstrap draws); the comparison is exploratory and inconclusive. Deletion total variation is unavailable under the frozen two-repeat rule because cached gold-deletion levels each have one repeat.

- [45_five_rater_cached_selection_task_split_and_behavioral_audit](archive/45_five_rater_cached_selection_task_split_and_behavioral_audit/RESULTS_five_rater_comparison.md): completed 10-07-2026 — 345 current ratings, original task splits, zero inference; five-rater test-only frozen proxy-minus-fixed-rubric Spearman difference −0.012 [−0.198, 0.186], p-val=n/a (29/30 outputs, 10 tasks, 10,000 task-bootstrap draws, 9,999 finite). New validation selection unavailable at 13/15 shared outputs versus 14 required. Includes stronger weakening/gaming plan and proposed methods disclosure; manuscript unchanged.

- [44_cached_score_judge_selection_utility](archive/44_cached_score_judge_selection_utility/RESULTS_selection_utility.md): completed 10-05-2026 — zero-inference cached-score selection-utility analysis. In the primary 12-configuration, 42-item/15-task common-support comparison, the frozen `C_ms_gold` proxy selected Spearman 0.768 versus fixed H2 0.853 (paired difference -0.086, 95% task-cluster interval [-0.308, 0.058], 10,000 draws; p-val=n/a); two broad-pool reference-quality comparisons were unavailable under the fixed 90% support rule.

- [40_best_of_k_judge_selection_bias_validation_set](archive/40_best_of_k_judge_selection_bias_validation_set/REPORT.md): completed 09-26-2026, landed 09-30-2026 (drafted as PR #47 under the number 39) — choosing the best of 8 judge configurations on half the validation problems overstates its Spearman agreement by 0.15 (about 0.10 on all 72 pairs); adjusting for the index-form choice leaves 4 of 9 judge-level cells below 0.05. Zero inference; drafted paper text awaits the paper owner.

- [38_iclr_body_rewrite_to_trust_artifact_abstract](archive/38_iclr_body_rewrite_to_trust_artifact_abstract/results.md): completed 09-26-2026 — Claude Fable 5.1 rewrote body sections 1–7 to the approved trust-artifact abstract from frozen evidence, with no inference; the build has 19 pages, the main text ends on page 9, and it has 0 overfull boxes and 0 undefined references.

- [37_openreview_feedback_current_iclr_revision](archive/37_openreview_feedback_current_iclr_revision/FINAL_REPORT.md): completed 09-26-2026 — Claude Fable assessed 41 feedback items; Astra Ultra implemented 12 repairs, integrated with the current body rewrite. Verified 19 total pages, 9 main-text pages, and all 72 correlations / 9 exact tests.

- [31_final_iclr_paper_writing](archive/31_final_iclr_paper_writing/README.md): archived 09-25-2026 — earlier manuscript writing and research superseded by Experiment 34's corrected rewrite and submission preparation; original notes, research, and exploratory output preserved.

- [34_iclr_mega_rewrite_astra](archive/34_iclr_mega_rewrite_astra/results.md): completed 09-24-2026 (merged at `63fb935`) — Codex GPT-6 Astra (ultra) rewrote the paper core-only and answered or disclosed all 55 review complaints; the anonymous PDF and supplement were uploaded into the OpenReview revision form on 09-24-2026, but no final Submit is recorded in the repo ([submission status](archive/34_iclr_mega_rewrite_astra/submission/SUBMISSION_STATUS.md)).

- [36_vals_gateway_cert_judge_smoke](archive/36_vals_gateway_cert_judge_smoke/results.md): completed 09-24-2026 — 1/1 real GPT-6 Astra xhigh identity judgment via Vals gateway on SNAP; score 1.0, reported cost $0.0394425. Infrastructure smoke only.

- OpenReview complaint ledgers [33a_ai4math_reviews](archive/33a_ai4math_reviews/README.md), [33b_or_ledger](archive/33b_or_ledger/results.md), [33c_dl4c_reviews](archive/33c_dl4c_reviews/README.md), [33d_mathai_reviews](archive/33d_mathai_reviews/README.md), and [33e_tmlr_desk_reject](archive/33e_tmlr_desk_reject/README.md): done 09-22-2026, re-anchored 09-24-2026 — 55 complaints from four review rounds: 25 addressed, 18 disclosed, 5 deferred, 7 superseded, 0 unknown; DL4C reviews ingested 09-22-2026.

- [32_veribench_ranking_certified_judge](archive/32_veribench_ranking_certified_judge/REPORT.md): stopped 2026-09-22 — re-ranked VeriBench agents with a certified prompt on gpt-5.6-terra (826 cells, $0 API); superseded when §5.4/Table 5 (a carried-over VeriBench result) was cut from the paper.
- [29_proxy_validation](archive/29_proxy_validation/README.md): completed behavioral-proxy validation; negative/inconclusive finding.
- [30_proxy_trust_index_held_out_validity](archive/30_proxy_trust_index_held_out_validity/README.md): completed combined-target and within-problem diagnostics; new-family validation remains unstarted.
- [27_trust_plots](archive/27_trust_plots/README.md): completed figures from existing scores; reusable plotting functions remain in `py_src/cert_judge/`.

## Layout maintenance

Register new active work in [the inventory](archive/layout.json) with a concrete
current task, and add it here. Archive finished or parked work promptly; a future
idea or a paper citation does not make a finished experiment active.

Git moves tracked files but leaves ignored caches and local outputs behind. After
a pull, check and reconcile those leftovers without deleting unique evidence:

```bash
python3 py_src/cert_judge/experiment_layout.py --check
python3 py_src/cert_judge/experiment_layout.py --reconcile
```

Reconciliation never overwrites existing files; collisions are preserved under
`archive/.local_leftovers/` and remain ignored. Frozen records retain their original
provenance paths; executable consumers use the current archive locations.

Completed on 10-09-2026: [47_simulated_panel_v5_label_free_judge_screening](archive/47_simulated_panel_v5_label_free_judge_screening/RESULTS_full_campaign.md) is archived with all original evidence and analyses. No strong-follow-up shortlist; complete-pool common support 0/691, below the frozen 90% gate, leaves gains and 95% intervals undefined (p-val=n/a).
