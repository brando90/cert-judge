# Experiment 34 — core ICLR manuscript rewrite

**Doc link:** <https://github.com/brando90/cert-judge/blob/astra/iclr-mega-rewrite/experiments/34_iclr_mega_rewrite_astra/REPORT.md>

**TLDR:** The branch contains a rewritten anonymous paper, an 8-page main text, a reduced appendix, corrected figures, and responses to all 55 complaint IDs. The PDF has 17 pages, down from 25; References starts on page 9. No inference or new experiment was run. The source audit materially narrows the scientific claim: the retained panel does not measure P3, historical alpha probes can be malformed, and a high fixed index does not exclude lexical judges. These are disclosed rather than represented as repaired evidence.

## What changed and why

| Section | Final change | Reason |
|---|---|---|
| Abstract | One protocol proposal, fixed-index validation correlations, lexical diagnostic, and reusable-human-panel implication; CS197 source comments | Preserve a skim-readable claim without implying a test-set result or empirical coverage of every property. |
| Introduction | Test-oracle framing, definition bridge, two contributions, explicit label reuse and adaptive-selection concern | Explain why checking proofs cannot validate the chosen theorem and when property checks could amortize annotation. |
| Related work | Three short paragraphs; each comparison states its gap | Remove the inherited oversight/HCI survey and align citations with the actual claim. |
| Problem setup | Intent/specification/test/proof distinctions, gold-relative quality, judge tuple, extraction rule | Tell a non-Lean reader exactly what is scored. The gold field is the final theorem block, despite its prompt label. |
| Protocol | Figure 1, compact workflow table, cumulative-ladder targets, exact fixed equal-weight index | Separate the proposed four-property protocol from the bug-only scalar actually computed. Explain panel normalization and limitations. |
| Experiments | Complete annotation paragraph; canonical fixed-index scatter and tables; malformed-alpha diagnosis; lexical reversals; competitive selected-weight comparison; weight sensitivity; correctly named per-property table; artifact threshold | Repair mismatched indices and unsupported interpretations while preserving negative evidence. |
| Limitations | Reused labels, criterion mismatch, both registered screens, missing probe classes, invalid historical transformations, Lean-only scope, gaming and presentation gaps, locked test | Put unresolved reviewer objections into explicit scientific limitations. |
| Conclusion | Four sentences ending on reuse of human judgment | Keep the vision without claiming a portable acceptance certificate. |
| Statements | Repository-grounded reproducibility, author annotation ethics, provisional LLM-use statement | Supply the requested ICLR statements; author confirmation remains visibly marked in source. |
| Bibliography | Nineteen cited entries; completed authors/venues/pages/DOIs where applicable, verified Dwork entry | Remove uncited inherited references and incomplete metadata. |
| Appendix | Six cited top-level sections: prompts, exact definitions, additional results, human/additional panels, diagnostics, tests-as-theorems note | Keep only material needed to reproduce or defend a main-text claim. |

The original title is unchanged. Main text uses the original template fonts and margins; no compression of those settings was used. Minor whitespace-only reflow in the unused venue example and math-command source allows the requested top-level sentence-layout check to pass.

## Corrections that change interpretation

1. **Mixed indices corrected.** The inherited scatter and per-configuration table used an unequal six-weight index, while the headline named the fixed equal-weight index. New plots and table values use the canonical experiment-28 vectors throughout.
2. **Qwen pass2 corrected to 0.857.** The inherited 0.905 belongs to another index. The fixed-index averaged association remains 0.905.
3. **No P3 result in the retained main panel.** The field `P3_weak_mono` is computed from bug weak monotonicity. It is not missing-specification monotonicity. The paper cannot claim that P3 is the most informative property.
4. **Historical alpha probes are not certified semantic rewrites.** The generator can duplicate `:=` and rename signatures without updating bodies. Its score drops cannot demonstrate failure under valid alpha-renaming. The 0.250 to 0.070 result is a score-replacement proxy; actual canonicalization remains untested.
5. **The scalar is not a rejection certificate.** The lexical prompt scores 0.940 in the Codex panel and has the highest Qwen index, 0.982. Individual recorded reversals supply the diagnostic. No validated index cutoff is reported.
6. **The old 184-file sanity figure is mixed evidence.** It includes 34 tasks scored by a local heuristic. Source: `experiments/archive/02_neurips_reviews/results/codex_api_gpt53_r3_20260418_230027/summary.json`. Those curves and their summary table are archived; the replacement uses only the committed 24-problem main panel.
7. **The competing geometric index is selected, not an untuned baseline.** Its 0.4/0.6 weights came from pass1. The separate six-component fitted variant is clearly labeled and uses the same pairs across passes.
8. **Implementation details constrain transfer.** The fixed index uses only bug rows, normalizes variances within each family panel, omits undefined constant ladders, and floors components at 1e-6. The paper now states these facts.
9. **Human disagreement is not a demonstrated ceiling.** The unsupported noise-ceiling argument is removed. The original written annotation rubric was not recovered.
10. **Negative evidence retained.** The short Leanstral paragraph remains. The different-rubric pool and two unsuccessful registered screens remain disclosed. No leave-one-family-out result or normalization-panel sensitivity is invented.

The requested empirical claim that a validated four-property certificate screens arbitrary new judges is not established by the available artifacts. The manuscript presents a proposed reusable screening protocol, descriptive validation-set association, and concrete diagnostics. No wording change can supply the missing matched-rubric test or validated probes.

## Appendix keep/archive decisions

| Material | Final disposition | Main-text dependency |
|---|---|---|
| Judge prompts, exact IDs, scales and extraction | Keep `995_appendix_judge_prompts.tex` | §§3 and 5.3; reproducibility |
| Fixed, arithmetic and selected geometric definitions | Keep new `998_appendix_index_definitions.tex` | §4 equation and §5.3 comparison |
| Cross-pass tuned variant, threshold table, weight sensitivity | Keep reduced `990_appendix_additional_results.tex` | §5.3 |
| Human agreement statistics and expanded 13-configuration figure | Keep reduced `997_appendix_human_alignment.tex` | §§5.1 and 5.3 |
| Leanstral and registered-screen negatives | One short active subsection; original long discussion archived | §§5.3 and 6 |
| Codex failure plots and Opus sanity figure | Keep reduced `996_appendix_judge_cert_plots.tex` | §5.2 |
| Unit tests as ground theorems | Keep compact `994_appendix_tests_as_ground_theorems.tex` | §3 terminology |
| Related Work (Cont.), Scalable Oversight and HCI | Archive whole `991` file | None |
| Formal verification context/tooling | Archive whole `992` file | None |
| Why Judge Scores Are Specification-Relative | Archive whole `993` file | None; supported gold-relative limitation appears in §6 |
| Naive blind baseline, cross-model status, old index prose and redundant plots | Preserve full original `997`, retain only corrected necessary parts | None for archived sections |
| Original large plot appendix | Preserve full original `996` | None for archived plots |
| Unreferenced figures | Move 15 inherited files under `archive/figures/`, with original relative paths | None |
| Original protocol/results text, bibliography and decision sheet | Preserve copies under `archive/` | Historical record only |

`paper_latex/ICLR_2027_submission/archive/README.md` lists every preserved source and moved figure. The byte-preservation check compares each archived original with commit `8d2e005`; excluded historical prose is not silently edited or included in the new build. No Qwen sanity figure with verified provenance was present in the retained source set; its main family comparison remains in the corrected scatter and table.

## Retained numeric results and regeneration

Abbreviation **B** below means `experiments/archive/04_veribench_validation/`. The exhaustive table later in this report expands exact paths and records every main-text numeric source line. Artifact hashes are in `analysis/results/number_provenance.json`.

| Result | Values retained | Artifact and generating code |
|---|---|---|
| Human panel | One annotator, two strictness passes, 0–5, 75 rated / 72 analyzed, 25 / 24 problems, three generations | B `results_exp16_final_robust_r9_median/summary.json`; `experiments/archive/26_human_label_dataset_audit/` confirmation and panel trace; B `exp16_multi_judge_human_sets.py` |
| Human disagreement | Spearman 0.249, QWK 0.372, MAE 0.771; appendix Pearson/Kendall and CIs | B `results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`; `exp18_human_label_reliability.py` |
| Primary fixed-index correlations | Codex avg/pass1/pass2 0.833/0.905/0.738; Opus 0.643/0.810/0.595; Qwen 0.905/0.476/0.857 | Canonical `results_exp28_varaware_*` summaries and vectors; B `exp28_variance_aware_trust_index.py` |
| Codex uncertainty | 95% CIs [0.24,1.00], [0.41,1.00], [0.11,1.00]; p 0.017/0.005/0.045; 10,000, seed 42 | `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` and `compute_headline_cis.py` |
| Codex Pearson/Kendall | 0.868/0.643 | New committed `analysis/rebuild_paper_evidence.py` and `analysis/results/summary.json`, recomputed from canonical vectors |
| Codex prompts and reversals | Three LLM repeats, nine control repeats; all eight table rows; 20/24 lexical reversals | B `results_exp16_final_robust_r9_median/detail_rows.csv`, canonical vector and `results_exp19_low_variance_replot/bug_reversal_rates.csv`; B `exp19_replot_low_variance.py` |
| Rewrite plot and alpha score | 24 problems, four rewrite types; strict alpha mean 0.179 | Same committed detail rows; new plot script and `clean_rewrite_statistics.csv` |
| Score-replacement proxy | 0.250 → 0.070, eight configurations | B `results_exp24_alpha_canonicalized_identity/summary.json`; `exp24_alpha_canonicalized_identity_variant.py` |
| Arithmetic and selected geometric comparisons | All Table 2 v1/v2/GM entries, selected weights 0.4/0.6 | Family experiment-16 summaries; geometric summaries; B `exp16_multi_judge_human_sets.py`, `exp22_geometric_trust_index.py` |
| Cross-pass tuned variant | 0.881/0.810, 0.857/0.786; six available components | B `results_exp23_cross_pass_calibration/summary_fit_pass1.json` and `summary_fit_pass2.json`; `exp23_cross_pass_calibration.py` |
| Expanded selected geometric panel | 13 configurations, 0.769 [0.34,0.95] | B `results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json`; `exp22_geometric_trust_index.py` |
| Local weight grid | Twelve triples, weights 0.2–0.5 at 0.1 steps summing to one; nine reported ranges | New script and `weight_sensitivity.csv` / `weight_sensitivity_summary.csv`; fixed normalization, no selected replacement |
| Diagnostic associations | All four rows × three label views, including unadjusted p values | B `results_exp17_final_robust_{pass1,pass2,avg}/per_property_correlations.csv`; `exp17_property_human_analysis.py` |
| Artifact-score threshold | 0.60–0.85; all displayed rates/CIs; 176 files, three repeats, mean aggregation, bug rho −0.790 | `experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/`; `exp13_threshold_calibration_sweep.py`, `exp13_threshold_significance.py` |
| Leanstral negative control | −0.1190/−0.0476/−0.0952 | B `results_exp28_varaware_leanstral_{pass1,pass2,avg}/summary.json`; same fixed-index code |
| Different-rubric pool | 343 labels, five raters, 78 pairs; about 0.13 on 63 overlaps | `experiments/archive/22_pooled_heldout_and_noise_ceiling/results/results.json`; corrected committed `REPORT.md` Finding C for the approximate cross-criterion association |
| Registered screens | 14 and 32 configs; −0.39, Holm p 0.25; LOO 0.24/p 0.49 | `experiments/archive/23_reanchored_calibration/results/results.json`; `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` |
| Structural numerals | P1–P4, model versions, 0–1 scores, equal thirds, floor10^-6, index coefficients, equation and axis labels | Definitions and frozen scoring scripts; these are identifiers or design constants, not observations |

The original archived scripts are cited for provenance; some include inference paths and were **not executed**. Only the new pure reanalysis script and the existing plain-text abstract generator were run to produce manuscript content. Its input revision is pinned to `8d2e005`, and every input is checked against that revision before use. No credentials are read. Reanalysis previews live inside the experiment; the manuscript uses the generated vector PDFs.

## Verification

Final machine-readable checks are in `analysis/results/verification.json`. The main text was rendered with Poppler and visually inspected page by page; statements and retained appendix pages were also inspected. The actual `latexmk` command ran only in `/Users/brandomiranda/cert-judge-astra/paper_latex/ICLR_2027_submission/`.

| Gate | Result |
|---|---|
| `latexmk -pdf -interaction=nonstopmode main.tex` | Exit 0 |
| Main text | 8 physical pages; conclusion on page 8; no font/margin changes |
| Total PDF | 25 → 17 pages |
| References start | Page 8 → page 9; new statements begin page 9 |
| Undefined references/citations | 0 |
| BibTeX warnings | 0 |
| Overfull boxes | 0 in the built document |
| Forbidden wording/content | 0 active-source matches |
| Sentence layout | Pass on every top-level `.tex`; archive originals preserved verbatim |
| Appendix reachability | Every retained top-level section referenced from main text |
| Archive isolation/preservation | No active references into archive; all preserved originals match baseline bytes |
| Plain-text abstract | Regenerated and checked byte-for-byte against generator output |
| Number provenance | Every numeric source line in main sections 00–07 inventoried; figure observations in CSV; source hashes recorded |
| Experiment lifecycle | Layout check passes; requested experiment remains active for Brando’s branch review |

## Title candidates and author decisions

1. **Current, retained:** Certifying the Judge: Falsifiable Properties for LLM-Based Evaluation of Formal Code.
2. Checking the Checks: Behavioral Screens for LLM Judges of Formal Specifications.
3. One Human Panel, Reusable Tests for LLM Judges of Formal Specifications.

Brando should confirm the LLM-usage facts and supervision statement, choose whether to retain the title, and confirm whether the original human rubric can be recovered. Leanstral is retained briefly; the full discussion is archived. The approximate pool comparison is traceable to a committed corrected report, but no exact machine-readable field for that cross-criterion join was found. A future authorized study must validate the probes, measure missing-specification behavior, freeze normalization and a rejection rule, and collect a matched-rubric test before claiming transfer.

The repository’s legacy anonymized-supplement allowlist describes a different instrument. This task provides a source/evidence manifest and anonymous manuscript, not an uploaded anonymous supplement package. Rebuild that bundle from these retained sources if submitting it. No submission, main-branch merge, or inference was performed.

## Complete reviewer-complaint checklist

| Done | ID | Status | Complaint | Exact manuscript sentence | Source and assessment |
|---|---|---|---|---|---|
| [x] | A26-meta-1 | Disclosed | Evidence is calibration-based: small panel, moderate label agreement, overfitting risk in metric/prompt/threshold choices, alpha-renaming sensitivity | `This panel is the \emph{validation set}: it informed index-form selection, repeat aggregation, the threshold, and the prompt panel, so correlations on it are optimistic.` | [05_experiments.tex:13](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L13). Label disagreement and invalid alpha probes are also disclosed in §5.1–§5.2 and §6. |
| [x] | A26-uMVy-1 | Disclosed | Validation is small (~75 pairs, few configurations) and the same labels shaped metric design, prompt selection, aggregation, threshold | `This panel is the \emph{validation set}: it informed index-form selection, repeat aggregation, the threshold, and the prompt panel, so correlations on it are optimistic.` | [05_experiments.tex:13](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L13). The data and configuration paragraphs give counts and shared controls. |
| [x] | A26-uMVy-2 | Answered | Annotation protocol unclear: one annotator under strictness levels vs multiple passes | `One annotator supplied holistic ratings on a $0$--$5$ scale in two passes, pass1 with a stricter rubric and pass2 with a more lenient rubric.` | [05_experiments.tex:5](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L5). Following sentences explain the rated/analyzed counts and missing gold. |
| [x] | A26-uMVy-3 | Answered | TI_var not uniquely justified; simpler alternatives competitive | `We retain $\mathrm{TI}_{\mathrm{var}}$ for its explicit variance penalties and positive associations across the primary families and passes, not because these data establish its superiority.` | [05_experiments.tex:129](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L129). The preceding sentence identifies the competitive geometric comparison. |
| [x] | A26-uMVy-4 | Superseded | VeriBench rankings may carry judge-family bias | `The failure report therefore carries information that both human agreement and the scalar can miss.` | [05_experiments.tex:102](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L102). Downstream agent-ranking material is absent. This is a representative sentence about the retained task, not proof of deletion. |
| [x] | A26-uMVy-5 | Disclosed | Held-out reviewer-pool results not included; do trends persist once protocol choices are frozen? | `The screen of 14 configurations was underpowered; the expanded screen of 32 found no index meeting its registered criterion.` | [06_limitations.tex:12](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L12). Both screen outcomes, different criteria, and the required locked test are stated. |
| [x] | A26-uMVy-6 | Disclosed | Leave-one-family-out or bootstrap robustness | `We do not report leave-one-family-out transfer: the panels share controls and normalize separately, so pooling their scores would not constitute an independent family test.` | [05_experiments.tex:139](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L139). Codex bootstrap intervals are in the main table; other-family intervals remain explicitly unreported. |
| [x] | A26-uMVy-7 | Disclosed | Can Lean-aware canonicalization reduce alpha-renaming sensitivity? | `A real fix must rescore canonicalized text and verify that the transformation preserves meaning.` | [05_experiments.tex:43](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L43). The 0.250 to 0.070 proxy changes scores rather than judge inputs; no actual repair is claimed. |
| [x] | A26-uMVy-8 | Answered / Disclosed | Sensitivity of TI_var to weighting and normalization | `It does not assess sensitivity to changing the normalization panel.` | [05_experiments.tex:138](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L138). The committed local weight grid answers weight sensitivity; normalization-panel sensitivity remains untested. |
| [x] | A26-uMVy-9 | Superseded | Do downstream rankings stay stable when judge and generator families are separated? | `The failure report therefore carries information that both human agreement and the scalar can miss.` | [05_experiments.tex:102](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L102). The downstream ranking is removed; no downstream stability result is substituted. |
| [x] | A26-c7ev-1 | Disclosed | Main result is validation-set fit, not a locked held-out test | `No test-set result establishes reliability for a new judge or artifact distribution.` | [06_limitations.tex:6](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L6). The locked-test paragraph specifies the independent evidence needed. |
| [x] | A26-c7ev-2 | Disclosed | 75 pairs; two passes agree only moderately | `Inter-pass agreement is Spearman $0.249$, quadratic-weighted $\kappa=0.372$, and mean absolute error $0.771$ on the shared pairs (Appendix~\ref{app:exp16-exp17}).` | [05_experiments.tex:9](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L9). The corrected mean absolute error is 0.771; the earlier complaint ledger has a stale value. |
| [x] | A26-c7ev-3 | Disclosed | Larger independent annotation pool not analyzed | `Two pre-registered screens asked whether property indices tracked agreement with that pool.` | [06_limitations.tex:11](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L11). The following sentences report the negative outcomes and criterion mismatch. |
| [x] | A26-c7ev-4 | Disclosed | Alpha-renaming failure mode is important | `Its score drops therefore cannot establish a failure of invariance under valid alpha-renaming.` | [05_experiments.tex:39](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L39). The malformed alpha generator is analyzed; valid alpha-renaming failure is not claimed. |
| [x] | A26-c7ev-5 | Disclosed | Property suite incomplete: vacuity, subtle weakening, over-constraint, domain-specific mismatch | `The probes do not establish sensitivity to vacuity, subtle weakening, over-constraint, or formatting-only edits beyond the four rewrites studied here.` | [06_limitations.tex:18](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L18). §6 also confines evidence to VeriBench/Lean 4 and rejects a complete-intent guarantee. |
| [x] | A26-c7ev-6 | Superseded | VeriBench ranking is only a sanity check, not independent validation | `The failure report therefore carries information that both human agreement and the scalar can miss.` | [05_experiments.tex:102](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L102). The criticized downstream ranking is absent. |
| [x] | A26-c7ev-7 | Answered | Justify the geometric, variance-aware aggregation beyond validation fit | `Multiplication prevents a strong component from fully offsetting a weak one; equal weights avoid fitting component weights to the human ratings.` | [04_property_protocol.tex:73](../../paper_latex/ICLR_2027_submission/04_property_protocol.tex#L73). Omitted properties, normalization dependence, and lexical failures are also stated. |
| [x] | A26-c7ev-8 | Answered | Reference list has anonymous, future-dated, or workshop-only entries | `\textsc{FormalAlign} learns alignment between informal and formal statements~\citep{lu2024formalalign}, whereas our target is the behavior of a judge comparing candidate and gold specifications.` | [02_related_work.tex:15](../../paper_latex/ICLR_2027_submission/02_related_work.tex#L15). Representative citation only; the mechanical bibliography checks below establish the status. |
| [x] | A26-c7ev-9 | Answered | Add CIs, bootstrap, or other uncertainty for judge-level correlations | `The Codex bootstrap intervals are wide, and the resampling does not correct for the earlier protocol selection.` | [05_experiments.tex:60](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L60). The main table supplies three Codex intervals and permutation probabilities. |
| [x] | A26-c7ev-10 | Answered | Clarify labeling protocol (annotators, pass1/pass2 meaning, disagreements) | `One annotator supplied holistic ratings on a $0$--$5$ scale in two passes, pass1 with a stricter rubric and pass2 with a more lenient rubric.` | [05_experiments.tex:5](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L5). §5.1 and the human-agreement appendix report disagreement and reject interpreting it as a model ceiling. |
| [x] | A26-c7ev-11 | Disclosed | Open: reference-free property suite; number of annotators for stable targets; rubric ambiguity vs Lean misunderstanding | `Reference-free screening and the number of annotators needed for a stable criterion remain open.` | [06_limitations.tex:29](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L29). The same section states that rubric ambiguity cannot be separated from misunderstanding Lean semantics. |
| [x] | A26-c7ev-12 | Disclosed | Failure analysis should include formatting-only perturbations | `The probes do not establish sensitivity to vacuity, subtle weakening, over-constraint, or formatting-only edits beyond the four rewrites studied here.` | [06_limitations.tex:18](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L18). Known-direction probes are proposed; no result is claimed. |
| [x] | A26-DeJF-1 | Disclosed | Trust index calibrated and tested on the same 75-pair panel | `This panel is the \emph{validation set}: it informed index-form selection, repeat aggregation, the threshold, and the prompt panel, so correlations on it are optimistic.` | [05_experiments.tex:13](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L13). The index form and other choices were label-informed despite fixed weights. |
| [x] | A26-DeJF-2 | Disclosed | Only eight judge configurations; correlations may be unstable | `With eight configurations and disagreeing label passes, these estimates support a descriptive association rather than a precise or portable effect size.` | [05_experiments.tex:62](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L62). The main table gives Codex uncertainty; shared controls are explicit. |
| [x] | A26-DeJF-3 | Disclosed | Labels are noisy: one annotator, two related passes, moderate agreement | `We report each pass and the archived averaged-label view; they are two judgments by one person, not independent annotators.` | [05_experiments.tex:8](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L8). Agreement statistics and the unavailable original rubric follow. |
| [x] | A26-DeJF-4 | Answered | TI_var not clearly better than the simpler geometric index | `We retain $\mathrm{TI}_{\mathrm{var}}$ for its explicit variance penalties and positive associations across the primary families and passes, not because these data establish its superiority.` | [05_experiments.tex:129](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L129). The geometric comparison is explicitly pass1-selected. |
| [x] | A26-DeJF-5 | Superseded | VeriBench demo uses Claude 3.7 while validation uses other families; "same calibrated judge" unclear | `The failure report therefore carries information that both human agreement and the scalar can miss.` | [05_experiments.tex:102](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L102). No downstream rankings or Claude 3.7 results remain. |
| [x] | A26-DeJF-6 | Answered | Dense sections; simplify for readers unfamiliar with Lean | `An artifact is a Lean source file containing an implementation and, potentially, theorem statements, predicates, unit tests, and proofs.` | [03_problem_setup.tex:6](../../paper_latex/ICLR_2027_submission/03_problem_setup.tex#L6). §1 bridges tests to universal theorems; §3 defines intent/specification/proof; §4 explains alpha-renaming. |
| [x] | A26-DeJF-7 | Disclosed | Does the approach work for other proof assistants? | `The protocol could be instantiated for another proof assistant, but neither cross-assistant nor cross-benchmark transfer has been tested.` | [06_limitations.tex:27](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L27). Lean 4 and benchmark scope are explicit. |
| [x] | N25-ivJs-1 | Disclosed | Limited generalization: finite perturbations on one benchmark; unclear on novel theorem types or adversarial cases | `The protocol could be instantiated for another proof assistant, but neither cross-assistant nor cross-benchmark transfer has been tested.` | [06_limitations.tex:27](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L27). §6 names finite-suite limits, VeriBench scope, and untested gaming. |
| [x] | N25-ivJs-2 | Answered | Single architecture; no comparison with other judges or ensembles | `The three primary families are GPT-5.3-Codex, Claude Opus 4.7, and Qwen3-Coder.` | [05_experiments.tex:51](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L51). The following sentence lists additional models and controls; no ensemble result is claimed. |
| [x] | N25-ivJs-3 | Answered | No human validation of the judge | `For each judge, artifact-level agreement is the Spearman correlation between its scores and the human ratings on the same analyzed pairs.` | [05_experiments.tex:16](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L16). The human panel and associations are now reported, with validation-only scope. |
| [x] | N25-36Hd-1 | Answered | Judge details missing ("simply Claude 3.5 / 3.7") | `The primary family model identifiers are \texttt{gpt-5.3-codex}, \texttt{claude-opus-4-7}, and \texttt{Qwen/Qwen3-Coder-30B-A3B-Instruct}.` | [995_appendix_judge_prompts.tex:3](../../paper_latex/ICLR_2027_submission/995_appendix_judge_prompts.tex#L3). The appendix gives complete prompts, extraction, scales, repeats, and aggregation. |
| [x] | N25-36Hd-2 | Answered | Identity/monotonicity looks like edit distance over strings, not the real problem | `The index ranks it below the three semantic prompts, but its value remains $0.940$; edit distance also scores highly at $0.928$.` | [05_experiments.tex:100](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L100). The table reports lexical/edit-distance reversal counts and shows that the scalar itself can miss lexical failure. |
| [x] | N25-36Hd-3 | Answered / Disclosed | Monotonicity experiment ignores severity of changes | `Each ladder extends the preceding level, so its expected ordering concerns cumulative damage rather than equal severity of individual edits.` | [04_property_protocol.tex:54](../../paper_latex/ICLR_2027_submission/04_property_protocol.tex#L54). The appendix additionally discloses that intended cumulative damage lacks semantic validation. |
| [x] | N25-36Hd-4 | Superseded | Section 4 agentic setup unclear (inputs, DSPy/Trace, how Lean is used) | `The failure report therefore carries information that both human agreement and the scalar can miss.` | [05_experiments.tex:102](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L102). The downstream agentic setup is absent; retained judge inputs are defined in §3 and Appendix Judge Prompts. |
| [x] | N25-36Hd-5 | Answered | LLM-as-judge is not novel | `We propose using one human panel to assess a property suite, then screening subsequent judge configurations without consulting those labels.` | [01_introduction.tex:20](../../paper_latex/ICLR_2027_submission/01_introduction.tex#L20). Related Work distinguishes the protocol from existing judge methods. |
| [x] | N25-36Hd-6 | Answered | Monotonicity should not be defined as a strict ordering | `Ties are allowed; a local score increase is a reversal.` | [04_property_protocol.tex:55](../../paper_latex/ICLR_2027_submission/04_property_protocol.tex#L55). Both ladder properties explicitly use non-increasing scores. |
| [x] | N25-36Hd-7 | Superseded | Why Claude 3.5 in Sec. 3, 3.7 in Sec. 4, both in App. D | `The primary family model identifiers are \texttt{gpt-5.3-codex}, \texttt{claude-opus-4-7}, and \texttt{Qwen/Qwen3-Coder-30B-A3B-Instruct}.` | [995_appendix_judge_prompts.tex:3](../../paper_latex/ICLR_2027_submission/995_appendix_judge_prompts.tex#L3). Historical Claude 3.5/3.7 downstream results are absent. |
| [x] | N25-36Hd-8 | Superseded | Figure 1 unreadable | `The lower sequence measures validation-set association and selects protocol choices, so its results are not a held-out test.}` | [04_property_protocol.tex:28](../../paper_latex/ICLR_2027_submission/04_property_protocol.tex#L28). Old Figure 1 is replaced with the protocol diagram; this checklist does not certify visual readability. |
| [x] | N25-36Hd-9 | Answered | Figure 1: "vs." should be "w.r.t." | `Local increases reveal behavior hidden by the aggregate bug trend.` | [996_appendix_judge_cert_plots.tex:30](../../paper_latex/ICLR_2027_submission/996_appendix_judge_cert_plots.tex#L30). New captions describe scores and cumulative edits in plain words; the criticized wording is absent. |
| [x] | N25-36Hd-10 | Answered | Missing references in the Appendix | `Table~\ref{tab:app-human-human-ceiling} reports the frozen agreement statistics on 72 shared analyzed pairs.` | [997_appendix_human_alignment.tex:4](../../paper_latex/ICLR_2027_submission/997_appendix_human_alignment.tex#L4). Representative existing reference; the static target audit below covers all active inputs. |
| [x] | N25-36Hd-11 | Superseded | Typos: "Lean 4 verus Verus"; stray "**" in App. C | `We record a competing view that we do not adopt.` | [994_appendix_tests_as_ground_theorems.tex:4](../../paper_latex/ICLR_2027_submission/994_appendix_tests_as_ground_theorems.tex#L4). The old tooling discussion was archived; the criticized typo and stray Markdown emphasis are absent. |
| [x] | T26-EiC-1 | Superseded | "Unlikely to meet TMLR acceptance criteria" under "extremely limited reviewer capacity" (discretionary triage; no reviews) | `No test-set result establishes reliability for a new judge or artifact distribution.` | [06_limitations.tex:6](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L6). The venue-specific decision cannot be overturned by a sentence. Venue changed; evidence limitations remain disclosed, without an acceptance prediction. |
| [x] | T26-self-1 | Answered | OpenReview form abstract rendered "trust index, ," (`\(...\)` stripped) and carried internal appendix references | `We compare three judge families with eight configurations each on a 72-pair, single-annotator validation set that also informed protocol selection.` | [00_abstract.tex:14](../../paper_latex/ICLR_2027_submission/00_abstract.tex#L14). The regenerated form contains the same substance and no internal references or backslash-parenthesis math. |
| [x] | T26-self-2 | Answered | Abstract skim-read as "n=8 correlations + held-out test failed" | `We propose collecting labels once, then screening new judges with falsifiable properties that specify how scores should respond to controlled edits.` | [00_abstract.tex:8](../../paper_latex/ICLR_2027_submission/00_abstract.tex#L8). The abstract presents the protocol before its validation results and does not call the different-criterion pool a matched test. |
| [x] | D26-birm-1 | Disclosed | Small scale and weak ground truth: 75 pairs, 8 judges, one rater; the larger set (5 raters, 343 labels, 78 pairs) "hasn't been analyzed yet, so the stronger evidence is promised, not shown" | `The screen of 14 configurations was underpowered; the expanded screen of 32 found no index meeting its registered criterion.` | [06_limitations.tex:12](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L12). §5.1 gives the small single-annotator panel; §6 gives pool size, rubric mismatch, and both outcomes. |
| [x] | D26-birm-2 | Disclosed | All evidence from one benchmark (VeriBench); transfer to other Lean datasets or formal-verification settings unclear; benchmark anonymized at review time | `All candidates and probes come from \textsc{VeriBench} in Lean~4.` | [06_limitations.tex:26](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L26). The next sentence disclaims cross-benchmark/cross-assistant transfer; VeriBench is cited by name. |
| [x] | D26-birm-3 | Answered | "Some headline numbers swing a lot across rating passes (e.g., Qwen3-Coder pass1 0.476 vs pass2 0.905)" | `Pass-to-pass differences also matter: Qwen's Spearman association changes from $0.476$ on pass1 to $0.857$ on pass2.` | [05_experiments.tex:61](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L61). The next sentence connects the swing to eight configurations and label disagreement; fixed-index pass2 is corrected to 0.857. |
| [x] | D26-birm-4 | Answered | "Quite heavy on statistics, making it hard to follow and verify without a strong relevant background" | `We then ask whether the index orders configurations by that agreement.` | [05_experiments.tex:17](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L17). The preceding sentence and §3 distinguish artifact-level agreement from judge-level association. |
| [x] | D26-cxkT-1 | Disclosed | Tiny single-annotator calibration with weak label reliability (Spearman 0.249, QWK 0.372); n=8 judges put 0.833–0.905 "on extremely thin statistical ground, with wide confidence intervals (e.g., Table 12 CIs spanning negative values)"; Kendall τ noisier | `The Codex bootstrap intervals are wide, and the resampling does not correct for the earlier protocol selection.` | [05_experiments.tex:60](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L60). The main table gives intervals; §5.1 gives label disagreement. The current Kendall association is corrected to 0.643. |
| [x] | D26-nMnm-1 | Disclosed | Results limited to the calibration set; no held-out test results | `No test-set result establishes reliability for a new judge or artifact distribution.` | [06_limitations.tex:6](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L6). A locked test is described, not claimed complete. |
| [x] | D26-nMnm-2 | Disclosed | Calibration set small and scored by a single annotator | `One annotator supplied holistic ratings on a $0$--$5$ scale in two passes, pass1 with a stricter rubric and pass2 with a more lenient rubric.` | [05_experiments.tex:5](../../paper_latex/ICLR_2027_submission/05_experiments.tex#L5). Following sentences give collection and analysis counts. |
| [x] | D26-nMnm-3 | Disclosed | Generalization beyond Lean 4 not shown | `The protocol could be instantiated for another proof assistant, but neither cross-assistant nor cross-benchmark transfer has been tested.` | [06_limitations.tex:27](../../paper_latex/ICLR_2027_submission/06_limitations.tex#L27). No cross-assistant transfer result is claimed. |
| [x] | D26-nMnm-4 | Answered | Difficult to read in places; "the Additional Material section needs better formatting" | `These arithmetic indices combine different summaries from $\mathrm{TI}_{\mathrm{var}}$ and do not isolate the effect of changing only the aggregation function.` | [998_appendix_index_definitions.tex:34](../../paper_latex/ICLR_2027_submission/998_appendix_index_definitions.tex#L34). The reduced appendix has six topical sections with focused definitions, tables, prompts, and captions; the root agent completed the final visual checks. |

## Mechanical evidence and bibliography completeness

- Complaint inventory: 55 unique rows; exact ID-set equality with the four ledgers.
- Active reference targets: 24; missing labels: `[]`.
- Active citation keys: 19; missing entries/core fields: `[]`.
- Retained author fields ending in “and others”: `[]`.
- Form abstract forbidden reference/math-delimiter matches: `[]`.
- Every retained entry has author, title, and year; conference entries have a book title and journal articles have a journal. Remaining arXiv entries have an identifier and URL. Core completeness is distinct from independently verifying every retained author or publication claim.
- Full author lists for G-Eval, MT-Bench, and Kimina-Prover are present. Published-version metadata for Bavaresco and FormalAlign is present. No remaining incomplete core bibliography entry was found.
- No anonymous-author placeholder, “to appear” entry, or future publication year beyond 2026 occurs in the active bibliography.
- Active inputs have no downstream agent-ranking section/table or Claude 3.5/3.7 result. Historical material remains under the manuscript archive directory.

## Residual limits and final gates

1. **Abstract/P3 distinction resolved during this audit.** An earlier abstract said all four properties were tested although the headline panels lack missing-specification ladders. The current abstract says that four properties “target” the named behaviors; §5.2 explicitly calls P3 proposed and unmeasured in those panels. The form abstract was regenerated after the final wording pass.
2. **Build and visual gates completed by the root agent.** The final report records eight main-text pages, no overfull boxes, zero undefined citations/references, and zero BibTeX warnings. The earlier overfull box was repaired before the final build; see `analysis/results/verification.json`.
3. **Scientific shortcomings remain.** No matched-rubric test; unavailable original rubric; malformed/unvalidated historical probes; no P3 measurement in headline panels; panel-dependent normalization; shared controls; and lexical judges with high scalar values are explicit disclosures, not empirically solved problems.
4. **Author confirmation remains.** The LLM Usage Statement contains the requested Brando confirmation comment. The checklist cannot resolve that factual sign-off.

## Number-provenance table

Every printed numeric source line in main sections 00–07 is indexed below. Property labels, model versions, index names and equation constants are identifiers or definitions, not empirical estimates. Cross-reference numbers are generated by LaTeX. Axis ticks are plotting coordinates; all plotted observations are retained in the figure CSVs. Written-out counts are additionally covered in the panel/protocol rows of the summary table above.

### Evidence groups

**panel — Panel sizes, scales, repeats, models, prompts and label passes.**

- `experiments/archive/04_veribench_validation/exp16_multi_judge_human_sets.py`
- `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv`
- `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
- `experiments/archive/04_veribench_validation/results_exp16_opus47_r3_median/summary.json`
- `experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/summary.json`
- `experiments/archive/26_human_label_dataset_audit/ethan_slack_confirmation.md`
- `experiments/archive/26_human_label_dataset_audit/results/PANEL_TRACE.md`

**fixed — Fixed-index associations and all primary configuration values.**

- `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_avg_newindex/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_pass1/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_pass1_newindex/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_pass2_newindex/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_opus_avg_newindex/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_opus_pass1_newindex/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_opus_pass2_newindex/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_qwen_avg/judge_trust_vector.csv`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_qwen_avg/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_qwen_pass1/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_qwen_pass2/summary.json`

**ci — Codex confidence intervals, permutation probabilities, seed and repetitions.**

- `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json`

**human — Human-human statistics and rating scale.**

- `experiments/archive/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`

**checks — Recorded rewrite scores and local bug reversal counts.**

- `experiments/archive/02_neurips_reviews/utils/variant_generator.py`
- `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv`
- `experiments/archive/04_veribench_validation/results_exp19_low_variance_replot/bug_reversal_rates.csv`

**proxy — Alpha score-replacement proxy, not rescored canonicalized text.**

- `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json`

**definitions — Property identifiers, score domains and fixed numerical constants.**

- `experiments/archive/02_neurips_reviews/utils/veribench_variance_utils.py`
- `experiments/archive/04_veribench_validation/exp16_multi_judge_human_sets.py`
- `experiments/archive/04_veribench_validation/exp28_variance_aware_trust_index.py`

**comparisons — Arithmetic and pass1-selected geometric comparison.**

- `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
- `experiments/archive/04_veribench_validation/results_exp16_opus47_r3_median/summary.json`
- `experiments/archive/04_veribench_validation/results_exp22_geometric_trust_index/median_mono_stab_40_60/summary.json`
- `experiments/archive/04_veribench_validation/results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_avg/summary.json`
- `experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/summary.json`
- `experiments/archive/13_qwen_replication_exp16_exp19/results/exp25_geometric_qwen_r3_median_mono_stab_40_60_avg/summary.json`

**tuned — Separate fitted geometric variant and expanded configuration panel.**

- `experiments/archive/04_veribench_validation/results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json`
- `experiments/archive/04_veribench_validation/results_exp23_cross_pass_calibration/summary_fit_pass1.json`
- `experiments/archive/04_veribench_validation/results_exp23_cross_pass_calibration/summary_fit_pass2.json`

**leanstral — Negative fixed-index replication.**

- `experiments/archive/04_veribench_validation/results_exp28_varaware_leanstral_avg/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_leanstral_pass1/summary.json`
- `experiments/archive/04_veribench_validation/results_exp28_varaware_leanstral_pass2/summary.json`

**components — Diagnostic associations; historical P3 field is a bug statistic.**

- `experiments/archive/04_veribench_validation/exp17_property_human_analysis.py`
- `experiments/archive/04_veribench_validation/results_exp17_final_robust_avg/per_property_correlations.csv`
- `experiments/archive/04_veribench_validation/results_exp17_final_robust_pass1/per_property_correlations.csv`
- `experiments/archive/04_veribench_validation/results_exp17_final_robust_pass2/per_property_correlations.csv`

**threshold — Artifact threshold, decision flips and pass rates; mean aggregation.**

- `experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/summary.json`
- `experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/threshold_metrics.csv`

**pool — Different-rubric pool and two registered screens.**

- `experiments/archive/22_pooled_heldout_and_noise_ceiling/REPORT.md`
- `experiments/archive/22_pooled_heldout_and_noise_ceiling/results/results.json`
- `experiments/archive/23_reanchored_calibration/results/results.json`
- `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json`

**derived — New zero-inference recomputation: Pearson/Kendall, plots and local weight sensitivity.**

- `experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py`
- `experiments/34_iclr_mega_rewrite_astra/analysis/results/bug_curve_statistics.csv`
- `experiments/34_iclr_mega_rewrite_astra/analysis/results/clean_rewrite_statistics.csv`
- `experiments/34_iclr_mega_rewrite_astra/analysis/results/scatter_coordinates.csv`
- `experiments/34_iclr_mega_rewrite_astra/analysis/results/summary.json`
- `experiments/34_iclr_mega_rewrite_astra/analysis/results/weight_sensitivity_summary.csv`

### Exhaustive main-text numeric source lines

| Source | Numerals (in source order) | Evidence groups |
|---|---|---|
| `00_abstract.tex:10` | 4 | panel, fixed, ci, definitions |
| `00_abstract.tex:14` | 72 | panel, fixed, ci, definitions |
| `00_abstract.tex:16` | 0.833 ; 0.905 ; 0.738 | panel, fixed, ci, definitions |
| `01_introduction.tex:26` | 4 | panel, fixed, ci, definitions |
| `01_introduction.tex:32` | 72 | panel, fixed, ci, definitions |
| `01_introduction.tex:33` | 0.833 ; 95 ; 0.24 ; 1.00 | panel, fixed, ci, definitions |
| `03_problem_setup.tex:4` | 4 | definitions, panel |
| `03_problem_setup.tex:21` | 0 ; 1 | definitions, panel |
| `04_property_protocol.tex:18` | 1 ; 4 | definitions, panel |
| `04_property_protocol.tex:49` | 1 ; 1 | definitions, panel |
| `04_property_protocol.tex:50` | 2 | definitions, panel |
| `04_property_protocol.tex:52` | 3 | definitions, panel |
| `04_property_protocol.tex:56` | 4 | definitions, panel |
| `04_property_protocol.tex:64` | 1 ; 3 ; +1 ; 3 ; 1 ; +1 ; 3 ; 1 | definitions, panel |
| `04_property_protocol.tex:70` | 10 ; -6 | definitions, panel |
| `04_property_protocol.tex:74` | 1 ; 3 | definitions, panel |
| `05_experiments.tex:5` | 0 ; 5 ; 1 ; 2 | panel, human |
| `05_experiments.tex:6` | 75 ; 25 | panel, human |
| `05_experiments.tex:7` | 72 ; 24 | panel, human |
| `05_experiments.tex:9` | 0.249 ; 0.372 ; 0.771 | panel, human |
| `05_experiments.tex:19` | -5.3 | checks, derived, panel |
| `05_experiments.tex:20` | 24 | checks, derived, panel |
| `05_experiments.tex:22` | 24 | checks, derived, panel |
| `05_experiments.tex:25` | 0.179 | checks, derived, panel |
| `05_experiments.tex:32` | 24 | checks, derived, panel |
| `05_experiments.tex:41` | 0.250 ; 0.070 | proxy, definitions |
| `05_experiments.tex:45` | 3 | panel, definitions |
| `05_experiments.tex:47` | 3 | panel, definitions |
| `05_experiments.tex:48` | 3 | panel, definitions |
| `05_experiments.tex:51` | -5.3 ; 4.7 ; 3 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:52` | -4 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:59` | 0.868 ; 0.643 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:61` | 0.476 ; 1 ; 0.857 ; 2 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:68` | 72 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:77` | 4 ; 2 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:79` | 1 ; 2 ; 4 ; 6 ; 1 ; 2 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:81` | 0.762 ; 0.476 ; 0.857 ; 0.833 ; 0.905 ; 0.738 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:82` | 0.429 ; 0.143 ; 0.714 ; 0.643 ; 0.810 ; 0.595 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:83` | 3 ; 0.524 ; 0.500 ; 0.786 ; 0.905 ; 0.476 ; 0.857 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:85` | 4 ; 95 ; 0.24 ; 1.00 ; 0.41 ; 1.00 ; 0.11 ; 1.00 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:86` | 4 ; 0.017 ; 0.005 ; 0.045 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:89` | 1 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:91` | 10 ; 000 ; 42 | fixed, comparisons, ci, derived, panel |
| `05_experiments.tex:98` | 0.435 ; 0.365 ; 0.466 | fixed, checks, panel |
| `05_experiments.tex:99` | 20 ; 24 | fixed, checks, panel |
| `05_experiments.tex:100` | 0.940 ; 0.928 | fixed, checks, panel |
| `05_experiments.tex:101` | 0.982 | fixed, checks, panel |
| `05_experiments.tex:111` | 0.466 ; 0.958 ; 0 ; 24 | fixed, checks, panel |
| `05_experiments.tex:112` | 0.419 ; 0.958 ; 0 ; 24 | fixed, checks, panel |
| `05_experiments.tex:113` | 0.365 ; 0.950 ; 4 ; 24 | fixed, checks, panel |
| `05_experiments.tex:114` | 0.435 ; 0.940 ; 20 ; 24 | fixed, checks, panel |
| `05_experiments.tex:115` | -4 ; -0.014 ; 0.324 ; 18 ; 24 | fixed, checks, panel |
| `05_experiments.tex:116` | -4 ; 0.092 ; 0.007 ; 16 ; 24 | fixed, checks, panel |
| `05_experiments.tex:117` | 0.199 ; 0.928 ; 24 ; 24 | fixed, checks, panel |
| `05_experiments.tex:118` | -0.001 ; 0.008 ; 24 ; 24 | fixed, checks, panel |
| `05_experiments.tex:128` | 0.4 ; 0.6 ; 1 | comparisons, tuned, leanstral, fixed |
| `05_experiments.tex:130` | 0.810 ; 0.786 | comparisons, tuned, leanstral, fixed |
| `05_experiments.tex:131` | 1 ; 0.769 ; 13 ; 95 ; 0.34 ; 0.95 | comparisons, tuned, leanstral, fixed |
| `05_experiments.tex:133` | -0.095 | comparisons, tuned, leanstral, fixed |
| `05_experiments.tex:136` | 0.738 ; 0.857 ; 0.643 ; 0.714 ; 0.881 ; 0.976 | derived, fixed |
| `05_experiments.tex:144` | 3 ; 3 | components, definitions |
| `05_experiments.tex:146` | 2 ; 0.05 | components, definitions |
| `05_experiments.tex:152` | 1 ; 2 | components, definitions |
| `05_experiments.tex:154` | -0.21 ; 0.62 ; 0.02 ; 0.98 ; -0.02 ; 0.98 | components, definitions |
| `05_experiments.tex:155` | 0.60 ; 0.13 ; 0.67 ; 0.08 ; 0.71 ; 0.06 | components, definitions |
| `05_experiments.tex:156` | 0.63 ; 0.11 ; 0.78 ; 0.03 ; 0.75 ; 0.04 | components, definitions |
| `05_experiments.tex:157` | 0.47 ; 0.24 ; -0.23 ; 0.57 ; 0.14 ; 0.76 | components, definitions |
| `05_experiments.tex:160` | 3 | components, definitions |
| `05_experiments.tex:166` | 0.60 ; 0.85 ; 0.058 ; 0.046 ; 0.583 ; 0.536 | threshold |
| `05_experiments.tex:167` | 0.85 | threshold |
| `06_limitations.tex:7` | 343 ; 78 | pool, panel, definitions |
| `06_limitations.tex:9` | 0.13 ; 63 | pool, panel, definitions |
| `06_limitations.tex:12` | 14 ; 32 | pool, panel, definitions |
| `06_limitations.tex:13` | -0.39 ; 0.25 ; 0.24 ; 0.49 | pool, panel, definitions |
| `06_limitations.tex:26` | 4 | pool, panel, definitions |

The CSV preserves each full source line; the JSON records exact paths and SHA-256 hashes. Values are rounded to the precision shown in the manuscript; no direction or scale was changed. The approximate pool association (0.13 on 63 shared pairs) is supported by the corrected committed experiment-22 report, not by an exact field in its JSON.

**TLDR-end:** [cj: experiments/34_iclr_mega_rewrite_astra] The rewrite and evidence corrections are complete on the dedicated branch. Author confirmation and the disclosed scientific limitations remain relevant to submission readiness.

**Snapshot:**

| Artifact | Result |
|---|---|
| `main.pdf` | 17 total pages; main 8; References 9 |
| Reviewer inventory | All 55 IDs accounted for |
| Numeric inventory | 75 main-text source lines, 14 evidence groups |
| Fixed-index Codex avg | Spearman 0.833, CI [0.24,1.00] |
| Weight grid | 12 triples; no new judge calls |
| Archived original figures | 15 files preserved |
