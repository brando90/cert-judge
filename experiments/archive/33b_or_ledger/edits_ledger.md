# Edits ledger — reviewer-driven changes to the ICLR 2027 paper

> **Re-anchored 09-24-2026.** Brando merged the core-only rewrite of experiment 34 into `main` (merge `63fb935`, retitle `1cac976`: "Checking the Checks: Behavioral Screens for LLM Judges of Formal Specifications"). Its `experiments/34_iclr_mega_rewrite_astra/REPORT.md` § "Complete reviewer-complaint checklist" re-handles every row below against the new section files and quotes the exact manuscript sentence for each, so it is now the authoritative per-row status. The Evidence cells below describe the pre-rewrite manuscript (HEAD `d7cbb17`, 09-22-2026) and are kept as the record of that pass. Two corrections from the rewrite affect rows here: (1) the Qwen3-Coder pass2 value of the fixed index is **0.857**, not 0.905 (0.905 was another index's value inherited in the old Table 2; the reviewer quote of 0.905 is preserved verbatim); (2) the retained eight-configuration panel contains no missing-specification ladders, so the paper no longer claims P3 is the most informative property (the old `P3_weak_mono` field was bug-ladder weak monotonicity).

**TLDR:** Cross-venue record of the paper edits made in response to reviewer complaints (E1–E9, each with the artifact that supplies its numbers and the commit that landed it), the open non-reviewer items found while auditing, and the index of the per-venue complaint ledgers: `../33a_ai4math_reviews/complaints.md` (29 rows), `../33c_dl4c_reviews/complaints.md` (placeholders until the DL4C paste), `../33d_mathai_reviews/complaints.md` (14 rows), `../33e_tmlr_desk_reject/complaints.md` (3 rows).

## Per-venue complaint ledgers

| Folder | Venue | Forum | Rows | Verbatim source |
|---|---|---|---|---|
| `33a_ai4math_reviews` | ICML 2026 AI4Math workshop, Accept (Poster) | `xmHP3UhGQ8` | 29 `A26-*` | `pre_prompt.md` |
| `33c_dl4c_reviews` | ICML 2026 DL4C workshop, Accept (Poster) | `gGR1gE7x3a` | `D26-*` placeholders | `reviews_gGR1gE7x3a.md` (empty until pasted) |
| `33d_mathai_reviews` | NeurIPS 2025 MATH-AI workshop, no accept tag | `9WAWDdwqpC` | 14 `N25-*` | `reviews_9WAWDdwqpC.md` |
| `33e_tmlr_desk_reject` | TMLR 2026, desk reject 07-31-2026 | `WKVtlskjeQ` | 3 `T26-*` | `desk_reject_WKVtlskjeQ.md` |

## Edits applied in this pass (traceable numbers)

| Edit | Where | What | Number source |
|---|---|---|---|
| E1 | `04_property_protocol.tex`, Properties paragraph | P2/P3 stated as weak (non-increasing) targets; ladders are cumulative, so the expected ordering holds by construction regardless of per-edit severity | definitional; probe construction in `py_src/cert_judge/probe_validation.py` (cumulative ladders) |
| E2 | `04_property_protocol.tex`, Fig. 1 subcaptions (b),(c) | "vs." → "w.r.t." for the monotonicity panels, matching the appendix captions | none |
| E3 | `05_experiments.tex`, §5.3 after the Pearson/Kendall sentence | Bootstrap 95% CIs and permutation p for the Codex headline trio | `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` (seed 42, 10,000 resamples/permutations): avg 0.833 [0.241, 1.0] p=0.0167; pass1 0.905 [0.407, 1.0] p=0.0054; pass2 0.738 [0.114, 1.0] p=0.0451 |
| E4 | `05_experiments.tex`, §5.2 alpha-renaming paragraph | Post-hoc binder-canonicalization proxy: mean within-item std 0.250 → 0.070, median reduction 64%, eight Codex configurations; a real fix must rescore canonicalized text | `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json` (`mean_std_original` 0.2501, `mean_std_alpha_canon` 0.0697, `median_pct_std_reduction` 64.28, `n_judges` 8) |
| E5 | `06_limitations.tex`, "Validation set, not a test set" paragraph | Disclose the two pre-registered screens against the five-rater pool: n=14 underpowered; n=32 no candidate met the registered bar (strongest Spearman −0.39, Holm p=0.25; LOO transfer ρ=0.24, p=0.49) | `experiments/archive/23_reanchored_calibration/REPORT.md` (verdict c, n=14); `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` (`n_real` 32, `primary_screen_9candidate[0]` rho −0.3911 holm_p 0.2484, `loo` rho 0.2416 perm_p 0.4908, `registered_verdict` "b") |
| E6 | `06_limitations.tex`, "What certification does not cover" | Name the untested failure classes (vacuous, weakened, over-constrained statements; formatting-only edits beyond Table 1) and the Lean-4-only scope | none (scope statement) |
| E7 | `05_experiments.tex`, §5.3 first paragraph | State the aggregation behind the Codex panel: median over repeated calls per pair, three stored calls for the LLM judges and nine for the edit-distance and random controls (the run was configured for nine, but the judge-call cache held three per pair for LLM judges; flagged by session cert-judge-57, verified from the detail rows) | `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json` (`repeat_agg` median, `judge_repeats` 9 as configured) and `detail_rows.csv` (`repeat_scores` length: 3 for all six LLM configurations × 288 rows, 9 for `editdist_e1` and `random_r1`) |
| E8 | `997_appendix_human_alignment.tex` (ceiling paragraph and table) and `05_experiments.tex` §5.1 | Inter-pass agreement statistics are computed on the 72 overlapping pairs, not 75 | `…/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` (`n_overlap_pairs` 72; `n_pass2_only` 3) |
| E9 | `refs.bib` | Delete the uncited anonymous "NeurIPS (to appear)" self-entry; fix `bach2022trusthci` (first author is Tita Alissa Bach, add DOI/arXiv), `ding2025citations` (full authors, volume/pages, arXiv), `bowman2022scalable` (arXiv URL) | arXiv 2304.08795 / DOI 10.1080/10447318.2022.2138826; AAAI 39(22):23787–23795, arXiv 2501.01303; arXiv 2211.03540 |

| E10 | `05_experiments.tex`, §5.3 after the "Six of the nine family--pass correlations" sentence | Acknowledge that family-level values move between rating passes (Qwen3-Coder 0.476 on pass1 vs 0.905 on pass2 as the pre-rewrite Table 2 read; the rewrite corrected pass2 to 0.857 and kept the sentence at `05_experiments.tex:61`) as expected with eight configurations and only moderate inter-pass agreement (DL4C reviewer birm) | Table 2 (`tab:tivar_cross_model_results`, values already in the paper; Qwen family from `experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/`); inter-pass agreement from `…/exp18_human_label_reliability/summary.json` |

E10 landed in commit `5201653` (05_experiments.tex, main.pdf; scratch build 0 undefined citations/references). All nine edits landed in commit `e0631b6` (main.tex, main.pdf, refs.bib), built in a scratch copy: 27 pages, 0 undefined citations/references, 0 BibTeX warnings, one-sentence-per-line check passed.

## Open items found while auditing (not reviewer complaints)

| ID | Item | Evidence | Proposed handling |
|---|---|---|---|
| O1 | §5.1 and the appendix quote inter-pass MAE 0.778 and MSE 1.139, but the reliability artifact reports MAE 0.771 and RMSE 1.059 on the 72 overlapping pairs; no artifact containing 0.778/1.139 was found | `exp18_human_label_reliability/summary.json` (`mae_0_5` 0.7708, `rmse_0_5` 1.0590); grep of `experiments/` for `0.778`/`1.139` | Resolved by E8 on 09-22-2026: §5.1 and the appendix table now quote MAE 0.771 / MSE 1.121 on the 72 overlapping pairs (mean-of-duplicates convention, exp18 artifact); the pass histogram still uses the 75-pair files (owner: experiment 31) |
| O2 | Appendix ceiling table "Best validation-set Spearman (avg labels) 0.480 / pass1 0.559" vs Table 3 P1 avg 0.47 (0.4664 in `judge_rows`) | `results_final_stat_reliability_suite/exp18_identity_alpha_ablation/judge_rows_alpha_ablation.csv` contains 0.480/0.559 | Different run (alpha-ablation panel); label the appendix rows with their source or drop them; owner: experiment 31 (appendix) |
| O3 | Intro `% TODO(internal-review)` at `:146` (why a new judge on the same domain cannot reuse existing labels) | `main.tex:146` | Owner: experiment 31 |

## Where E1–E10 live after the 09-24-2026 rewrite (merge `63fb935`)

| Edit | Survives as | Location now |
|---|---|---|
| E1 | "P2 (bug monotonicity) requires non-increasing scores as errors accumulate"; "P3 (missing-specification monotonicity) requires non-increasing scores as theorem statements and unit tests are removed"; cumulative-ladder sentence re-expressed as "Each ladder extends the preceding level …" (REPORT checklist rows N25-36Hd-3, N25-36Hd-6) | `04_property_protocol.tex:50–52` |
| E2 | Superseded: the old three-panel Fig. 1 (184-file mixed-evidence sanity figure) was archived and replaced by `figures/codex_property_checks.pdf` built from the 24-problem panel (REPORT correction 6) | `05_experiments.tex:28–35` |
| E3 | Codex 95% intervals `[0.24,1.00] / [0.41,1.00] / [0.11,1.00]` and permutation p `0.017 / 0.005 / 0.045` moved into Table 2; "The Codex bootstrap intervals are wide, and the resampling does not correct for the earlier protocol selection." | `05_experiments.tex:60`, table rows `:85–86` |
| E4 | Canonicalization proxy 0.250 → 0.070 kept, now framed as a score-replacement proxy with the added caveat that the historical alpha generator can produce malformed Lean text (REPORT correction 4) | `05_experiments.tex:37–43` |
| E5 | "Two pre-registered screens asked whether property indices tracked agreement with that pool." + the 14/32-configuration outcome | `06_limitations.tex:11–12` |
| E6 | Re-expressed: untested probe classes ("The probes do not establish sensitivity to …") and "The protocol could be instantiated for another proof assistant, but …" (checklist rows A26-c7ev-12, A26-DeJF-7) | `06_limitations.tex` |
| E7 | "Scores are medians over three repeated calls for language-model judges; Codex-panel controls use nine repeats, and the other panels use three." | `05_experiments.tex:55` |
| E8 | "Inter-pass agreement is Spearman 0.249, quadratic-weighted κ=0.372, and mean absolute error 0.771 on the shared pairs"; appendix ceiling table on the 72 overlapping pairs | `05_experiments.tex:9`, `997_appendix_human_alignment.tex` |
| E9 | `refs.bib` entries unchanged by the rewrite | `refs.bib` |
| E10 | "Pass-to-pass differences also matter: Qwen's Spearman association changes from 0.476 on pass1 to 0.857 on pass2." (corrected value) | `05_experiments.tex:61` |
