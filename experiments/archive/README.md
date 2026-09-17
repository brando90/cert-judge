# experiments/archive — retired experiment folders

**TLDR:** Folders here are finished or superseded. History is preserved via `git mv`; live docs, tests, keepers, and the PTI-v0 (Proxy Trust Index version 0) CLI callers were rewritten to `experiments/archive/<dir>`. Do not start new results from here. Only currently pursued work belongs under `experiments/`; shared label directories are data support.

Archived 2026-09-10 (Trigger Rule 39: `experiments/` holds active work only).

| Folder | What it was | Last commit | Archived |
|---|---|---|---|
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
