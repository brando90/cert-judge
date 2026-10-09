# experiments/archive — retired experiment folders

**TLDR:** Folders here are finished or superseded. History is preserved via `git mv`; live docs, tests, keepers, and the PTI-v0 (Proxy Trust Index version 0) CLI callers were rewritten to `experiments/archive/<dir>`. Do not start new results from here. Only currently pursued work belongs under `experiments/`; shared label directories are data support.

Archived 2026-09-10 (Trigger Rule 39: `experiments/` holds active work only).

| Folder | What it was | Last commit | Archived |
|---|---|---|---|
| [47_simulated_panel_v5_label_free_judge_screening](47_simulated_panel_v5_label_free_judge_screening/RESULTS_full_campaign.md) | Complete frozen 12-configuration simulated-panel campaign: 128 full derivations, 192 criterion views and 84 repeat-information analyses. No strong-follow-up shortlist; common support 0/691 fails the frozen 90% gate; gains and 95% intervals undefined (p-val=n/a). Original failures and unknown charges retained. | 1a5773bede0de3551ddec37a8b7bfa00ea03004b (PR #62) | 10-09-2026 |
| [44_cached_score_judge_selection_utility](44_cached_score_judge_selection_utility/RESULTS_selection_utility.md) | Exploratory zero-inference cached-score utility comparison of frozen `C_ms_gold` proxy selection against fixed H2, random, identity, and transferred-prompt selectors. Primary 12-configuration, 42-item/15-task common-support proxy-minus-H2 difference: -0.086, 95% task-cluster interval [-0.308, 0.058], 10,000 draws; no resolved proxy advantage. | Recorded with this archive update | 10-05-2026 |
| [40_best_of_k_judge_selection_bias_validation_set](40_best_of_k_judge_selection_bias_validation_set/REPORT.md) | Item 35.3: how much choosing the best of K judge configurations on the 72-pair validation set overstates the winner's human agreement, from 109 frozen configurations (no inference). Best of 8 overstated by 0.15 on half-panels, about 0.10 on all 72 pairs; index-form adjustment leaves 4 of 9 judge-level cells below 0.05. Drafted as PR #47 under the number 39 (branch `claude/bold-fermat-atoesg`); renumbered 40 because 39 is `39_label_free_proxy_index_train_val_test_over_judge_families`. | Recorded with this archive update | 09-30-2026 |
| [38_iclr_body_rewrite_to_trust_artifact_abstract](38_iclr_body_rewrite_to_trust_artifact_abstract/results.md) | Body sections 1–7 rewritten by Claude Fable 5.1 to the approved trust-artifact abstract from frozen evidence, deterministic diagnostics only; 19 pages, main text ends on page 9, 0 overfull boxes and 0 undefined references. Only the diagnostics script's repository-root depth changed; its rerun from here is byte-identical. | b4e3db0 | 09-28-2026 |
| [34_iclr_mega_rewrite_astra](34_iclr_mega_rewrite_astra/results.md) | Core-only ICLR rewrite by Codex GPT-6 Astra (ultra), merged at 63fb935, plus anonymous-submission packaging; PDF and supplement uploaded into the OpenReview revision form on 09-24-2026, final Submit not recorded in the repo. Scripts repointed to this path; a scratch rebuild of the supplement from here reproduces the frozen ZIP byte-for-byte (SHA-256 4caf85a2…). | c118d7c | 09-28-2026 |
| [33a_ai4math_reviews](33a_ai4math_reviews/README.md) | ICML 2026 AI4Math reviews (verbatim) and 29 A26-* complaint rows; one of the five ledgers covering 55 complaints (25 addressed, 18 disclosed, 5 deferred, 7 superseded, 0 unknown). | 9066e10 | 09-28-2026 |
| [33b_or_ledger](33b_or_ledger/results.md) | Hub for the 33a–33e ledgers: edits E1–E10 (landed e0631b6 and 5201653), prompts 01–04, fetch log, OpenReview form abstract; all four review rounds done. | c118d7c | 09-28-2026 |
| [33c_dl4c_reviews](33c_dl4c_reviews/README.md) | ICML 2026 DL4C reviews, pasted by Brando and ingested 09-22-2026; 9 D26-* rows (1 addressed, 6 disclosed, 2 deferred). | 9066e10 | 09-28-2026 |
| [33d_mathai_reviews](33d_mathai_reviews/README.md) | NeurIPS 2025 MATH-AI reviews (verbatim) and 14 N25-* complaint rows. | 9066e10 | 09-28-2026 |
| [33e_tmlr_desk_reject](33e_tmlr_desk_reject/README.md) | TMLR 2026 desk-reject record and 3 T26-* rows; form-abstract lesson applied. | 9066e10 | 09-28-2026 |
| [37_openreview_feedback_current_iclr_revision](37_openreview_feedback_current_iclr_revision/FINAL_REPORT.md) | Old OpenReview automated feedback assessed against the current manuscript by Claude Fable; 12 warranted repairs implemented by Astra Ultra and integrated with Experiment 38. All 41 issues dispositioned; 19 pages, 9 main text, zero build errors. | Recorded with this archive update | 09-26-2026 |
| [31_final_iclr_paper_writing](31_final_iclr_paper_writing/README.md) | Earlier manuscript wording, terminology, literature research, and page reduction; superseded by Experiment 34's corrected rewrite. All ten existing files retained, including the user's uncommitted message-history additions; only the analysis script's repository-root depth changed. | b468a00; local notes preserved in this archive commit | 09-25-2026 |
| `36_vals_gateway_cert_judge_smoke` | One real Vals gateway Astra xhigh judgment on SNAP; 1/1 completed, identity score 1.0, reported cost $0.0394425. Former active root `experiments/36_vals_gateway_cert_judge_smoke/`; no scientific validity claim. | Recorded with this archive update | 09-24-2026 |
| `32_veribench_ranking_certified_judge` | Re-score the VeriBench agent ranking (paper §5.4) with a certified judge prompt via subscription CLI; stopped after repeat layer 0 because §5.4/Table 5 was removed from the ICLR paper (carried-over VeriBench ICML 2025 result, uncertified Claude 3.7 judge) | d7f37c3 | 2026-09-22 |
| `00_overall_cert_judge_metric_with_properties` | Full P1–P7 Judge Trust Index (JTI) evaluation pipeline; superseded by PTI-v0 and not relabeled as such | 2025-10-31 | 2026-09-10 |
| `01_no_gold_ref_metric` | No-gold-reference metric sketch; unused by the frozen PTI-v0 protocol | 2025-10-22 | 2026-09-10 |
| `03_human_validation` | Early human-vs-judge agreement prompts/scripts; current labels live in `experiments/human_labels/` | 2026-04-07 | 2026-09-10 |
| `04_mutual_evalutation` | Mutual-evaluation sketch (folder name misspelled); unused by the live CLI | 2026-04-07 | 2026-09-10 |
| `04_veribench_validation` | Frozen PTI-v0 v4 CLI (`run_pti_v0.py`), probe/pool manifests, and historical JTI/TIvar VeriBench runs. Live callers now point at this archive path | 2026-08-26 | 2026-09-10 |
| `05_claude_code_properties_all_vb` | Claude Code property sweep across VeriBench; historical workshop figure source | 2026-04-21 | 2026-09-10 |
| `06_cert_index_vs_human_judge_corr_and_low_var` | Cert-index vs human-judge correlation and low-variance analysis; exp 27 still reads `full_run/mean/` from here | 2026-04-28 | 2026-09-10 |
| `07_property_vs_expected_behavior_corr` | Property vs expected-behavior correlation analysis; closed | 2026-04-29 | 2026-09-10 |
| `08_p2_bug_ladder_with_ci` | P2 bug-ladder with confidence intervals; historical | 2026-04-28 | 2026-09-10 |
| `09_single_certified_judge_vs_ensemble` | Single certified judge vs ensemble comparison; historical | 2026-04-29 | 2026-09-10 |
| `10_cert_vs_ensemble_meta_corr` | Cert-index vs ensemble meta-correlation; historical | 2026-04-29 | 2026-09-10 |
| `11_claude_replication_exp16_exp19` | Claude replication of Exp16 (multi-judge trend) and Exp19 (low-variance replots) | 2026-05-01 | 2026-09-10 |
| `13_qwen_replication_exp16_exp19` | Qwen3.6-27B replication of Exp16 / Exp19 / Exp25 | 2026-05-01 | 2026-09-10 |
| `14_handwritten_judge_metric_notes` | Handwritten notes on judge metrics; related-work scratch | 2026-08-13 | 2026-09-10 |
| `15_autometrics_related_work` | AutoMetrics related-work contrast; closed | 2026-08-13 | 2026-09-10 |
| `17_autojudge_human_corr_val_test` | Autojudge human-correlation val/test split; historical | 2026-05-27 | 2026-09-10 |
| `17_pseudo_formalization_related_work` | Pseudo-formalization related-work contrast; closed | 2026-05-27 | 2026-09-10 |
| `18_human_judgment_study` | Symlink to VeriBench `experiments/archive/41_human_judgment_study`; resolves when the sibling VeriBench checkout is present | 2026-06-04 | 2026-09-10 |
| `19_trust_index_vs_correlation_human_judge` | Trust Index vs human-judge correlation study; historical | 2026-06-04 | 2026-09-10 |
| `20` | Bare folder with motivation notes for why LLM judges are used | 2026-08-24 | 2026-09-10 |
| `20_fixed_judge_across_agents` | Fixed-judge-across-VeriBench-agents study; historical | 2026-06-04 | 2026-09-10 |
| `21_tmlr_submission` | TMLR 2026 submission packet; venue work closed | 2026-08-13 | 2026-09-10 |
| `22_pooled_heldout_and_noise_ceiling` | Pooled held-out analysis and noise-ceiling audit; registered null plus labeling-protocol-drift finding | 2026-07-21 | 2026-09-10 |
| `23_reanchored_calibration` | First registered calibration screen (`n=14`, underpowered) | 2026-07-21 | 2026-09-10 |
| `24_expanded_panel_cli` | Expanded-panel registered screen (`n=32`, Holm-negative) | 2026-08-01 | 2026-09-10 |
| `25_motivation_llm_judges` | Motivation writeup for LLM judges; superseded by the paper intro | 2026-08-11 | 2026-09-10 |
| `26_human_label_dataset_audit` | Human-label dataset audit (75-vs-72 panel); exp 27/29 still read the audited TSV from here | 2026-08-14 | 2026-09-10 |

## Lifecycle cleanup — 09-17-2026

There are no active numbered experiments in this checkout. The previous retention
list treated finished paper inputs and dormant runbooks as active; that policy is
superseded. Shared human-label folders remain data support. Core metric and plotting
functions remain in `py_src/cert_judge/`; historical runners stay reproducible here.

| Former root under `experiments/` | Canonical home | Outcome / reason |
|---|---|---|
| `02_neurips_reviews/` | `experiments/archive/02_neurips_reviews/` | Historical reviewer-response results retained; no current continuation recorded. |
| `03_tvdmi/` | `experiments/archive/03_tvdmi/` | Offline elicitation comparison and figures complete. |
| `04_efg_baseline/` | `experiments/archive/04_efg_baseline/` | Parked baseline implementation; no current run recorded. Not declared completed. |
| `12_leanstral/` | `experiments/archive/12_leanstral/` | Parked replication runbook; no current run recorded. Not declared completed. |
| `18_icml_reviews/` | `experiments/archive/18_icml_reviews/` | Historical review-feedback packet; retained for reference. |
| `27_trust_plots/` | `experiments/archive/27_trust_plots/` | Existing-data figures complete; reusable plotting code is in the core package. |
| `29_proxy_validation/` | `experiments/archive/29_proxy_validation/` | Complete: accepted scores and negative/inconclusive proxy validation preserved. |
| `30_proxy_trust_index_held_out_validity/` | `experiments/archive/30_proxy_trust_index_held_out_validity/` | Versions 2–3 complete; proposed fresh-family evaluation unstarted. |

No open pull requests were listed at cleanup. Older local branches still reference
retired paths (including `codex/exp29-release-megaqa-20260914`); their checkouts and
commits were not altered. Any future merge must route additions through
`layout.json` and pass the layout check, rather than recreate retired roots.

Ignored local leftovers are reconciled through the retirement map. Conflicting
files are preserved separately under ignored `.local_leftovers/`; no frozen result
payload is rewritten.

## Renames of retained experiment folders

These were retained on 2026-09-10 and moved to the archive on 09-17-2026. The table below preserves the earlier rename history; `layout.json` gives current destinations.
Frozen result payloads retain historical paths so their recorded hashes remain
valid; executable commands, live documentation, and tests use the current names.

| Former name | Current name | Purpose |
|---|---|---|
| `27_ti_plot_like_scatter_plots` | `experiments/27_trust_plots` | Plot paired judge/human scores and within-output judge repeatability. |
| `29_pti_v0_cli_bridge` | `experiments/29_proxy_validation` | Test whether the behavioral Proxy Trust Index predicts human agreement across judge configurations. |
| `02_reviewer_response_neurips_math_ai_2026` | `experiments/02_neurips_reviews` | Reviewer feedback and response experiments. |
| `03_tvdmi_elicitation_crossover` | `experiments/03_tvdmi` | Compare information-based elicitation with direct scoring. |
| `12_leanstral_replication_exp16_exp19` | `experiments/12_leanstral` | Replicate judge scoring with Leanstral. |
| `18_open_revievew_feedback_ICML_2026_mathai_ws` | `experiments/18_icml_reviews` | Reviewer feedback and response packet. |
| `27_judge_human_agreement_and_stability_plots` | `experiments/27_trust_plots` | Plot human agreement and repeat stability. |
| `29_proxy_trust_index_vs_human_agreement` | `experiments/29_proxy_validation` | Validate the proxy against human agreement. |

## Current read-only entry points

Older experiment documents retain historical commands and provenance paths. Use
these current locations to inspect the retained runners without starting inference:

```bash
python experiments/archive/04_veribench_validation/run_pti_v0.py --help
python experiments/archive/29_proxy_validation/run_pti_v0_cli.py --help
```

For new work, create a registered active experiment with its own output directory.
The reusable baseline cache lives in ignored `.cache/efg_judge/`, outside the archive.

Verification on 09-17-2026: all tracked files accounted for after relocation; frozen
result/configuration/table/figure contents unchanged. The mutable runner relocation
record was refreshed after checking that its scientific configuration is identical.
144 local leftover entries were relocated without overwriting destination files.

## Rename record — 09-22-2026

| Old root | Current home | Reason |
|---|---|---|
| `18_icml_reviews` → `18_icml_2026_reviews` | `experiments/33a_ai4math_reviews` | Re-activated from `archive/18_icml_reviews` on 2026-09-22 (commit ff22793), renamed, then moved into the per-venue review folders (33a–33e) the same day. |
| `33_openreview_complaints_all_venues_to_iclr2027_paper` | `experiments/33b_or_ledger` (hub) + `33c_dl4c_reviews`, `33d_mathai_reviews`, `33e_tmlr_desk_reject` | Split by venue on 2026-09-22 at Brando's request; the long name was retired. |

- [45_five_rater_cached_selection_task_split_and_behavioral_audit](45_five_rater_cached_selection_task_split_and_behavioral_audit/README.md): completed 10-07-2026 — five-current-rater cached comparison preserves proxy association but does not demonstrate selection utility; 34/42 views computed, eight unavailable by frozen coverage, no new inference. Archived from `experiments/45_five_rater_cached_selection_task_split_and_behavioral_audit`.
