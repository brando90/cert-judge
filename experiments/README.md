# Experiments

Only currently pursued experiments belong directly in this directory.

Experiments 33a–33e, 34, and 38 finished and moved to `archive/` on 09-28-2026.
The unstarted catalog of reviewer-requested experiments moved to [ideas/35_missing_experiments_from_reviews](ideas/35_missing_experiments_from_reviews/EXPERIMENTS.md); it is the menu for the next pick, and a picked item gets its own numbered folder here.

| Active experiment | Current task |
|---|---|
| [39_label_free_proxy_index_train_val_test_over_judge_families](39_label_free_proxy_index_train_val_test_over_judge_families/README.md) | **DONE 10-01-2026 — pre-registered PASS; archiving deferred while experiment 42 (semantic probes on these judges) consumes its judges and harvests.** 56 judge configurations (six single-call models × VeriBench + cert-judge prompts, six Terminus2 agent judges) judged 28,591 Lean-validated probe cells through Valkyrie ($574). The label-free index selected on the train judge models, `C_ms_gold` (gold missing-statement monotonicity; train ρ 0.761, val ρ 0.762), predicts judge–human agreement on the held-out test judges with Spearman 0.558 [0.08, 0.76], permutation p 0.0127 (gates ρ ≥ 0.45, p < 0.05); the paper's frozen `PTI_v0` (−0.27) and `TI_var` (−0.33) do not transfer. Only 3/75 rated candidates elaborate under Lean 4.22, so the candidate-side probe components are near-empty (see `results.md` deviations). Ledger: [results.md](39_label_free_proxy_index_train_val_test_over_judge_families/results.md); report: [RESULTS_proxy_index_train_val_test.md](39_label_free_proxy_index_train_val_test_over_judge_families/results/RESULTS_proxy_index_train_val_test.md). |
| [41_paper_panel_provenance_audit_and_vb_expert_label_rescore](41_paper_panel_provenance_audit_and_vb_expert_label_rescore/README.md) | **DONE 09-30-2026 on skampere1, zero model calls.** Gate G0 reproduces the paper's nine judge-level Spearman values to 3dp (PASS). Paper labels confirmed = VeriBench participant 1's superseded old-prompt passes. Of 24 scored validation-set tasks (1/25 silently skipped by the judge pipeline on a stale gold filename), only 7 have judge-seen reference bytes matching what the rater saw; re-scored on those matched items against VeriBench's corrected three-expert labels, the association is inconclusive under the pre-registered rule (Codex +0.333, Qwen3-Coder +0.667, Claude Opus −0.381). Full report: [REPORT.md](41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md), live ledger: [results.md](41_paper_panel_provenance_audit_and_vb_expert_label_rescore/results.md). |
| [42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges](42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/README.md) | **DONE 09-30-2026 (skampere1).** 194 Lean-validated vacuity, weakening, over-constraint and formatting probes from the VeriBench references, scored by experiment 39's 56 judge configurations through Valkyrie (32,592 calls, $656.15): 15/56 pass the semantic screen; vacuity is caught by nearly all, weakening separates judges (VeriBench rubrics: Sonnet 5 0.95, Qwen3.6 0.91, GPT-6 Sol 0.38; legacy prompts ≈ 0.06); weakening accuracy vs experiment 39's criterion ρ 0.73 train + val, 0.72 test (post hoc), no gain over its selected index. Answers reviewer rows c7ev-5/11/12 and ivJs-1. [REPORT.md](42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/REPORT.md), [results.md](42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/results.md). |
| [43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index](43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/README.md) | **DONE 09-30-2026 (skampere1).** GPT-6 Luna attacked 6 Claude Sonnet 5 judge configurations on 15 low-coverage items for 8 Lean-checked rounds (90 cells, 720 attempts). Gaming gaps vs the validated `H2` ensemble were −0.162 to +0.033 (none above 0), but 59/62 edited specifications were test-stuffed and credited by the reference too. Experiment 39's index did not predict resistance (`C_ms_gold` ρ = +0.60, p = 0.91; `TI_var` ρ = −0.09; `PTI_v0` not computable). $60.21 Vals. Report: [REPORT.md](43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/REPORT.md). |

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
