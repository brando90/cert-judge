# Evidence audit of the core manuscript

Scope: read-only inspection of main sections 00–07, appendices 990 and 994–998, `analysis/rebuild_paper_evidence.py`, its saved outputs, and the cited frozen artifacts on 2026-09-22. No manuscript edits, inference, archived-output mutation, or new experiment was performed. This report is the only file written by this audit.

## Result

The rewritten numerical tables and the two regenerated figures use the intended fixed equal-weight index consistently. The earlier index mixing, Qwen pass2 value, misleading P3 label, arithmetic-v1 Pearson/Kendall attribution, and mixed model/heuristic sanity plot have been corrected. The remaining issues below concern wording and provenance precision rather than a newly identified numerical error.

## Corrections recommended before finalization

1. In `paper_latex/ICLR_2027_submission/00_abstract.tex`, “we test identity, bug monotonicity, missing-specification monotonicity, and stability” can imply all four were tested in the retained three-family evaluation. Section 5 correctly says missing-specification ladders are absent from the eight-configuration panels. Use “the protocol specifies” or “we define” for the four properties. Source: `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv` has only `human_eval_union`, `property_identity`, and `property_bug` row types; Opus/Qwen use the same construction.
2. The abstract's “expected score changes follow from controlled edits” is stronger than the verified probe validity. The paper now correctly discloses that historical edits lack semantic validation and that the alpha routine is malformed. Prefer “tests specified responses to controlled edits,” or otherwise mark these directions as intended. Sources: `experiments/archive/02_neurips_reviews/utils/variant_generator.py` and `experiments/archive/02_neurips_reviews/utils/veribench_variance_utils.py:64`.
3. In `06_limitations.tex` and `997_appendix_human_alignment.tex`, “strongest [Spearman] association” for −0.39 should mean “largest absolute association.” The largest signed coefficient in the screen is +0.1285, while −0.3911 has the greatest magnitude. Source: `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json`, `primary_screen_9candidate`.
4. In `998_appendix_index_definitions.tex`, `anti` is computed from normalized Levenshtein **distance**, not similarity. Taking the absolute Spearman correlation makes the complement numerically invariant to replacing distance with one-minus-distance, but matching the source term avoids ambiguity. Source: `experiments/archive/04_veribench_validation/exp16_multi_judge_human_sets.py:535,581–582` and `experiments/archive/02_neurips_reviews/utils/metrics.py`.
5. The rebuild script's input-byte verification compares every input against `HEAD`, while its `input_revision` is hard-coded to `8d2e005`. Input hashes and blob identifiers are recorded correctly. For precise reproducibility, the same explicit revision should control both the byte comparison and reported revision, or the output should distinguish source-baseline revision from execution revision. File: `experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py`, `read()` and final `payload`.

## Root resolution

All five wording/provenance recommendations above were applied before the final build. The abstract now distinguishes proposed properties from measured coverage; edit directions are targets; the negative association is described by magnitude; the index definition names edit distance; and input-byte checks use the same pinned revision recorded in their manifest. These corrections do not validate historical probes or supply a test set.

## Numerical checks

All paths below are repository-relative. The current tables preserve the shown artifact rounding.

| Claim | Inspected source | Outcome |
|---|---|---|
| Three families, eight configurations per family, 72 analyzed pairs | `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`; `results_exp16_opus47_r3_median/summary.json`; `experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/summary.json` | Consistent; shared controls are disclosed. |
| Codex index associations avg/pass1/pass2 = 0.833/0.905/0.738 | `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_{avg_newindex,pass1,pass2_newindex}/summary.json` | Consistent. |
| Opus associations = 0.643/0.810/0.595 | `experiments/archive/04_veribench_validation/results_exp28_varaware_opus_{avg,pass1,pass2}_newindex/summary.json` | Consistent. |
| Qwen associations = 0.905/0.476/0.857 | `experiments/archive/04_veribench_validation/results_exp28_varaware_qwen_{avg,pass1,pass2}/summary.json` | Consistent; erroneous old pass2 0.905 has been corrected. |
| Codex Pearson/Kendall = 0.868/0.643 | `experiments/34_iclr_mega_rewrite_astra/analysis/results/summary.json`, `family_metrics.codex.avg`; input `results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv` | Rebuild script computes these from canonical index vectors, rather than arithmetic v1. |
| Codex bootstrap intervals and permutation probabilities | `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` | All bounds, probabilities, 10,000 resamples/permutations and seed 42 agree. |
| New scatter plot | `analysis/results/scatter_coordinates.csv`; canonical experiment 28 vectors for each family | Coordinates use `TI_variance_aware`; unequal-weight experiment 30 coordinates are no longer used. |
| Codex configuration table and reversal counts | `results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv`; `results_exp19_low_variance_replot/bug_reversal_rates.csv`, both under `experiments/archive/04_veribench_validation/` | All displayed entries agree. |
| Alpha mean 0.179 and zero baseline/checklist means | `analysis/results/clean_rewrite_statistics.csv`; `results_exp16_final_robust_r9_median/detail_rows.csv` | Consistent; code aggregates repeat medians across 24 problems. |
| Alpha replacement proxy 0.250 → 0.070 | `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json` | Values are 0.2501182499 and 0.0697055495; score replacement limitation is now explicit. |
| Arithmetic v1/v2 table | Family experiment 16 summaries above, `trend_by_set.avg` | All entries agree. |
| Geometric 0.857/0.714/0.786 | `results_exp22_geometric_trust_index/median_mono_stab_40_60/summary.json`; `opus47_r3_median_mono_stab_40_60_avg/summary.json`; Qwen `results/exp25_geometric_qwen_r3_median_mono_stab_40_60_avg/summary.json` | Correctly labeled selected weights 0.4/0.6. |
| Cross-pass 0.881/0.810 and 0.857/0.786 | `experiments/archive/04_veribench_validation/results_exp23_cross_pass_calibration/summary_fit_{pass1,pass2}.json` | Correctly separated from fixed equal-weight index and test-set evidence. |
| Expanded panel 13, 0.769 [0.34,0.95] | `experiments/archive/04_veribench_validation/results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json` | Correctly labeled selected geometric variant; original figure also labels formula correctly. |
| Per-diagnostic correlations | `experiments/archive/04_veribench_validation/results_exp17_final_robust_{pass1,pass2,avg}/per_property_correlations.csv` | Values agree; bug weak monotonicity is no longer mislabeled missing-specification monotonicity. |
| Inter-pass statistics and intervals | `experiments/archive/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` | All retained values agree. The unsupported correlation-ceiling assertion has been removed. |
| Threshold 0.60–0.85, flips/pass rates and intervals | `experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/threshold_metrics.csv` and `summary.json` | Agree; 176 files and mean aggregation correctly distinguished from primary panels. |
| Twelve weight triples and nine sensitivity ranges | `analysis/rebuild_paper_evidence.py`; `analysis/results/weight_sensitivity.csv`; `weight_sensitivity_summary.csv` | Grid enumerates weights from {0.2,0.3,0.4,0.5} summing to one; all printed ranges agree. It does not include exactly equal thirds, and is appropriately described as a surrounding grid rather than a new selected index. |
| Leanstral −0.1190/−0.0476/−0.0952 | `experiments/archive/04_veribench_validation/results_exp28_varaware_leanstral_{pass1,pass2,avg}/summary.json` | All agree; negative result remains disclosed. |

## Pool and registered-screen provenance

- **343 independent labels, 78 exact-key items, five raters:** `experiments/archive/22_pooled_heldout_and_noise_ceiling/results/results.json`, `B_noise_ceiling.n_labels`, `.n_items`, `.n_raters`. `experiments/archive/26_human_label_dataset_audit/CAMPAIGN_INVENTORY.md` confirms that aggregate files duplicate participant ratings and must not increase the independent-label denominator.
- **Approximately 0.13 on 63 shared pairs:** the corrected committed `experiments/archive/22_pooled_heldout_and_noise_ceiling/REPORT.md`, Finding C, explicitly reports old averaged panel labels versus five-rater pool mean, exact-key join, repeat labels averaged. `experiments/archive/26_human_label_dataset_audit/CAMPAIGN_INVENTORY.md` repeats the same comparison. This value is traceable to committed prose; it is not stored as an exact numeric field in experiment 22's `results/results.json`. Do not substitute `PANEL_TRACE.md`'s 0.128 on 62 pairs, which compares against one revised-protocol annotator rather than the pool.
- **14-configuration registered screen:** `experiments/archive/23_reanchored_calibration/results/results.json` gives `n_real=14`, registered outcome `c`, and no qualifying positive association. Its report calls this suggestive/underpowered. The manuscript's description is consistent.
- **32-configuration registered screen:** `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` gives `n_real=32`, greatest-magnitude correlation −0.3911, Holm probability 0.2484, leave-one-out association 0.2416 and probability 0.4908. Displayed −0.39/0.25/0.24/0.49 are consistent. These screens evaluated multiple historical statistics, including `ti_var_v3`; the manuscript correctly describes them generically rather than claiming a canonical `TI_var` test.

## Formula and interpretation checks

The fixed index definition matches `experiments/archive/04_veribench_validation/exp28_variance_aware_trust_index.py:69–132`: only bug rows; median repeat score per level; per-ladder transformed Spearman; population variance; skipped short/constant ladders; within-family min–max normalization; all arguments clipped to [10^-6,1]; weights 1/3. The appendix correctly records empty-coverage defaults and the absence of an exact zero. Arithmetic v1/v2 coefficients match `exp16_multi_judge_human_sets.py:342–370`. The main text now distinguishes a high index from a validated rejection cutoff.

The historical generators remain the principal scientific limitation: the alpha routine is malformed, other rewrites lack capture/dependency checks, and bug severity is an intended rather than validated order. The rewritten methods and limitations now say so. Strong claims in the abstract should use the same scope.

**TLDR-end:** [cj: evidence-audit] Retained numbers and formulas are consistent with inspected artifacts; five targeted wording/provenance clarifications are listed above. The pool denominator and approximate cross-protocol comparison have distinct, traceable sources.

**Snapshot:** Canonical Qwen pass2 = 0.8571428571; pool = 343 labels / 78 exact-key items / 5 raters; largest-magnitude expanded-screen association = −0.3911, Holm p = 0.2484; weight grid = 12 triples.

## Final rendered-figure correction

The root visual cross-check found that the inherited reversal PNG did not match the canonical CSV even though the main table did. The three appendix diagnostic plots were regenerated from committed detail rows/CSV, and their originals archived. This supersedes the earlier implication that inspecting numeric CSV values also validated the inherited image bytes.

The retained expanded-panel PNG was independently checked against its originating image, all 13 coordinates, the selected-weight formula, both correlations and intervals. No mismatch was found; its SHA-256 is `5bc7e78ec6165763bef54e538c25368971d8691c8b913fe58d929943e22c76ab`.
