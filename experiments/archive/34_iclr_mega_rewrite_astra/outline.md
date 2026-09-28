# Core manuscript outline and evidence plan

**Doc link:** <https://github.com/brando90/cert-judge/blob/astra/iclr-mega-rewrite/experiments/34_iclr_mega_rewrite_astra/outline.md>

**TLDR:** One human validation set motivates a four-property screen of new judges without new labels. The evidence supports screening, not a generalization guarantee or an index-only certificate; the source audit requires correcting several inherited numeric labels.

## Claim and page budget

| Section | Argument | Budget (pages) |
|---|---|---:|
| Abstract and title | Checking AI-written checks; one-time labels plus automated falsification; qualified validation result | 0.65 |
| Introduction | Test-oracle problem, limits of execution, reuse of labels and adaptive selection, contributions | 1.15 |
| Related work | Human agreement, code judges, formal-statement judges; gap attached to each comparison | 0.55 |
| Problem setup | Intent, specification, gold and judge tuple; fidelity rather than proof success | 0.65 |
| Property protocol | Four checks, workflow diagram, exact fixed-weight index and panel normalization | 1.35 |
| Experiments | Panel, property behavior, corrected scatter/table, lexical failures, index comparison, component association and threshold | 3.0 |
| Limitations and conclusion | Criterion mismatch, failed screens, locked test, untested classes, short conclusion | 1.05 |
| Total target | Standard template fonts and margins | 8.5 |

Statements follow the conclusion on a new page; References follows the statements.
Keep the current title pending Brando's choice.

## Mandatory corrections discovered in the artifact audit

1. The original scatter and configuration table use the six-weight exp30 index, but titles/headlines name the equal-weight exp28 index. Rebuild from `results_exp28_varaware_*/judge_trust_vector.csv`.
2. Canonical Qwen pass2 is 0.857, not 0.905. The latter belongs to the other index.
3. The per-property table's `P3_weak_mono` is computed from `bug_weak_mono_pct`, not the missing-specification ladder. Relabel by the measured statistic; do not claim P3 is the strongest component.
4. The geometric comparison uses weights (0.4, 0.6) selected on pass1. Identify it as such; TI_var remains fixed and equal-weight.
5. TI_var uses bug rows only; its normalized variances depend on the current family panel, it omits undefined constant ladders, and it clips components at 1e-6. State these implementation facts and their limitations.
6. Canonical index values for lexical and edit-distance controls can be high. Property checks expose their reversals; the scalar alone is not a certificate.
7. Inter-pass human agreement is not a demonstrated upper bound on judge agreement. Remove the ceiling claim.

## Numeric evidence ledger (planned retention)

All abbreviated paths in this table are rooted at `experiments/archive/04_veribench_validation/`; final REPORT.md expands paths and includes generated figure/table inventories.

| Quantity | Values/coverage | Committed artifact |
|---|---|---|
| Human panel | 75 rated, 25 problems × 3 generations; 72 analyzed, 24 problems; one annotator, two passes, 0–5 | `results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`; `results_exp16_final_robust_r9_median/summary.json`; annotation audit under `experiments/archive/26_human_label_dataset_audit/` |
| Human inter-pass agreement | Spearman 0.249, QWK 0.372, MAE 0.771; retained appendix Pearson/Kendall/CIs | `results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` |
| Judge panels | Three families × eight configurations; exact IDs, three LLM repeats and nine controls in Codex | `results_exp16_final_robust_r9_median/detail_rows.csv`; family summaries |
| Fixed index association | Codex avg/pass1/pass2 0.833/0.905/0.738; Opus 0.643/0.810/0.595; Qwen 0.905/0.476/0.857 | `results_exp28_varaware_codex_{avg_newindex,pass1,pass2_newindex}/summary.json`; corresponding Opus `_newindex` and Qwen directories |
| Headline intervals and p | [0.24,1.00]/0.017; [0.41,1.00]/0.005; [0.11,1.00]/0.045; 10,000 samples, seed42 | `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` |
| Per-configuration index and agreement | All eight rows in each family, directly regenerated | `results_exp28_varaware_*/judge_trust_vector.csv` |
| Bug reversals | 20/24 lexical; rates for all eight Codex configurations | `results_exp19_low_variance_replot/bug_reversal_rates.csv` |
| Component association | Identity, bug rank, BUG weak monotonicity, repeat decision stability (all table cells) | `results_exp17_final_robust_{pass1,pass2,avg}/per_property_correlations.csv`; definition in `exp17_property_human_analysis.py` |
| Rewrite scores and main property curves | Existing 0.936/0.849/0.982/0.399; variance 0.005/0.029/0.001/0.096; pooled rho -0.808/-0.899, rates 52.2%/89.1% | Codex property-run summary (exact path being resolved) |
| Canonicalization proxy | 0.250 → 0.070; eight judges | `results_exp24_alpha_canonicalized_identity/summary.json` |
| Tuned geometric cross-pass | 0.881/0.810 and 0.857/0.786, same labels; six possible component weights | `results_exp23_cross_pass_calibration/summary_fit_pass{1,2}.json` |
| Expanded tuned panel | 13 configurations; rho 0.769; CI [0.34,0.95] | expanded-panel/CI artifacts (exact path being resolved) |
| Threshold sweep | 0.60–0.85; flip 0.058→0.046, pass 0.583→0.536; rho -0.790 | committed threshold sweep CSV and significance summary (exact path being resolved) |
| Independent pool | 343 labels, five raters, 78 pairs; rho about0.13, 63 shared | `experiments/archive/22_pooled_heldout_and_noise_ceiling/` |
| Failed registered screens | 14 / 32 configs; -0.39, adjusted p0.25; leave-one-out0.24, p0.49 | `experiments/archive/23_reanchored_calibration/REPORT.md`; `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` |
| Index weights and numeric constants | 1/3 each; floor1e-6; component/range definitions | `exp28_variance_aware_trust_index.py`; arithmetic/geometric scripts |
| Optional weight sensitivity | Deterministic simplex grid over committed component vectors only | New committed `analysis/rebuild_paper_evidence.py` and generated JSON/CSV |

## Appendix keep/archive decisions

| Existing file/content | Decision | Reason |
|---|---|---|
| 990 additional results | Keep cross-pass and threshold tables, correct split labels | Main-text claims depend on them |
| 991 related work continuation | Archive whole file | Unneeded literature survey, HCI, scalable-oversight digressions |
| 992 formal verification context | Archive whole file | Main setup supplies the needed bridge |
| 993 relative scores/Rice | Archive whole file | Gold-relative limitation retained without invalid inference that every gold is incomplete |
| 994 tests as ground theorems | Keep compact definition note | Explicitly referenced from setup |
| 995 judge prompts | Keep exact templates, add input extraction/scale/model details | Reproduction requires these |
| 996 additional plots | Preserve original; keep only current Codex/Opus diagnostics actually cited | Old Sonnet prompt iterations are irrelevant |
| 997 human alignment | Preserve original; retain agreement statistics and cited failure/expanded-panel plots | Remove blind baseline, cross-model status, redundant figures, unjustified ceiling prose |
| Index definitions | Extract into dedicated 998 appendix file | Exact formulas, constant handling and normalization are essential |
| Leanstral | Prefer one short negative-control paragraph with artifact-backed values | Retain negative evidence without a long speculative subsection |
| Unreferenced figures | Move to archive/figures with original relative paths | Preserve all removed material |

No old figure that contains a mislabeled metric will remain merely because the original paper cited it.
All archived fragments are excluded from the build and indexed with zero active citations.

## Audit resolution before drafting

The planned retention list above was narrowed after source verification. The 184-file mixed model/heuristic curves and rewrite table are archived. Their replacement is a zero-inference plot of the committed 24-problem panel. The alpha generator's malformed output prevents a semantic-invariance conclusion, which is now explicitly disclosed. The missing-specification component association is unavailable, so the retained component table is labeled by its actual bug statistics. The exact source paths and corrected figures are recorded in `analysis/results/summary.json`; REPORT.md will provide the final retained-number inventory.
