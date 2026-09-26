# Experiment 37: applicability of the OpenReview automated feedback to the current ICLR 2027 manuscript

**TLDR:** Verdict `YES_SELECTIVELY`. The 28-page submission that received the Paper Assistant Tool (PAT) feedback no longer exists; the current 16-page manuscript (commit `c118d7c`, eight main-text pages) already fixes or removes most substantive concerns. Twelve small, evidence-backed repairs remain worthwhile, five of them in the main text: exact permutation probabilities for the Opus and Qwen cells, a controls-excluded association, the bug-component-only association that isolates the variance penalties, a threshold-interval overlap clause, and two duplicated author-name citations. Nothing requires new model inference, new human labels, or touching frozen archives.

Written 09-26-2026 by the consultation session (model identification in the last section). Working tree: `/Users/brandomiranda/cert-judge`, `main` at `c118d7c`; the experiment's source snapshot is byte-identical to `paper_latex/ICLR_2027_submission/*.tex` (checked with `cmp`).

## 1. Verdict and smallest worthwhile scope

`YES_SELECTIVELY`.

- Do not restore any deleted section (downstream agent table, Rice's theorem, Dafny/Verus/TLA+ appendix, extended related work, old plots). Those deletions were correct and most feedback items died with them.
- Apply Tier 1 (five items, main text, all deterministic): A1 exact permutation probabilities for the six non-Codex cells; A2 controls-excluded association; A3 bug-component-only association (archived field `rho_Cf_vs_human`); A4 flip-rate interval overlap clause; A8 `\citet` for two self-duplicating citations.
- Apply Tier 2 (four items, reproducibility and presentation, appendix): A5 cross-pass search objective, procedure, and pass2-fitted weights; A6 ladder length and probe counts; A7 Leanstral model identifier; A9 regenerate the 13-configuration appendix figure without internal run codes.
- Tier 3 is optional and low priority (A10 symbolic-equivalence boundary sentence, A11 single-call-prompt limitation, A12 how P1 was actually measured, plus two one-clause options).

Main-body page-limit risk: low. The rendered main text ends on page 8 of 16 with roughly 28 free lines on page 8, the required statements start on page 9 (they do not count), and the ICLR 2027 style states a strict nine-page main-text limit (`iclr2027_conference.tex:121`). Tier 1 adds about eight sentences; the implementation must confirm the Conclusion still ends by page 9.

## 2. Answers to the four questions

**Q1. Valid for the old draft, already fixed or removed.** The four-property narrative versus the bug-only scalar, the undefined variance penalties, the "P3 is the strongest predictor" claim (the archived field `P3_weak_mono` is a bug statistic), the multiplicative-collapse claim, the single-annotator "human-human ceiling" framing, 75 versus 72 pairs, the integer-versus-float score claim, the 0.881 citation mismatch, the GM-versus-TI_var overstatement, the pre-threshold `rho_bug` invariance, the six-versus-four threshold mismatch, the alpha-renaming "0.399" failure claim (withdrawn because the historical alpha generator emits malformed Lean), the held-out-pool mischaracterization and duplicated paragraphs, the downstream Table 7 and every concern attached to it, Rice's theorem, the Verus "kernel" and Dafny "cannot run" claims, the bibliography editorial note, the undefined `anti`/`subtle` components, the prompt-listing float split, the broken "Figures A.1--A.3" references, and all listed typos in deleted text. Evidence lines are in the tables below.

**Q2. Defects that remain and are worth fixing now.**
- Scientific precision: no uncertainty for six of the nine headline cells (A1); no evidence that the association survives removing the non-LLM controls (A2); no isolation of what the variance penalties add (A3, available from archived `rho_Cf_vs_human`); the threshold caption claims a reduction whose intervals overlap (A4).
- Reproducibility: the cross-pass fit states neither its objective nor the pass2-fitted weights (A5); ladder length and probe counts are absent (A6); the Leanstral model identifier is absent (A7).
- Readability/presentation: two citations render as "Bavaresco et al. (Bavaresco et al., 2025)" and "Schroeder and Wood-Doughty (Schroeder & Wood-Doughty, 2024)" (A8); the appendix figure `fig7_trend_update_baseline_vs_geom_13judge_avg.png` still carries "EXP25 / EXP22-GM", "cert-index v2", "ρ_spearman" and raw identifiers such as `editdist_e1` (A9).

**Q3. Suggested experiments that need evidence we do not have.** A symbolic-equivalence or property-based-testing baseline (no run exists); transfer to other Lean benchmarks; rescoring canonicalized (de Bruijn or renamed) text; structured multi-stage judges; a matched-rubric multi-rater test set; bootstrap intervals for Opus and Qwen (computable deterministically but larger than the permutation fix, so optional); a four-property geometric baseline (impossible on these panels because no missing-specification ladders were scored). The five-rater pool (343 labels, 78 pairs) uses a different rubric and agrees with the panel labels at only about 0.13 on 63 shared pairs; the two registered screens on it were null (n=14 underpowered; n=32 strongest |rho|=0.391, Holm p=0.248, leave-one-out rho=0.242, p=0.491). It must not be relabeled as a matched-rubric test, and the current text already says so (`06_limitations.tex:7-15`).

**Q4. Feedback not accepted at face value.** (i) Symbolic tactics can prove some equivalences but do not decide equivalence in general, and they cannot be applied across differing interfaces, which is the paper's setting; the recommended sentence (A10) states the boundary and claims no baseline. (ii) Line-end hyphenation in the extracted PDF text ("thresh-old", "proto-col") is ordinary typesetting, not typos: `REJECT`. (iii) The historical alpha rewrites duplicate `:=` and rename signatures without updating bodies; their low scores show nothing about valid alpha-renaming, so the "operational conflict with t=0.85" dissolves once the invalid evidence is withdrawn, which the current text already does.

## 3. Issue inventory: current-paper dispositions

Line references are to `paper_latex/ICLR_2027_submission/` files at `c118d7c`. Dispositions: `APPLY`, `ALREADY_ADDRESSED`, `REMOVED`, `FUTURE_EVIDENCE`, `REJECT`.

| ID | Feedback concern | Current evidence | Disposition | Rationale | Exact recommended repair |
|---|---|---|---|---|---|
| F01 | Four properties narrated, but TI_var contains only the bug ladder plus variance penalties; "multiplicative, so one low property collapses the index" | `00_abstract.tex:15,17`; `01_introduction.tex:38-39`; `04_property_protocol.tex:62,73-75`; `07_conclusion.tex:4-5`; `998_appendix_index_definitions.tex:18` | ALREADY_ADDRESSED | The scalar is now stated to use only bug-ladder scores, to omit P1, P3 and rewrite invariance, and to act as a smooth conjunction floored at 1e-6, so no collapse claim remains | None |
| F02 | VarCorr/VarScore lack closed forms, sample dimensions, normalization and log-domain bounds | `04_property_protocol.tex:67-71`; `998:4-19` versus `experiments/archive/04_veribench_validation/exp28_variance_aware_trust_index.py:34-56,83-132` | ALREADY_ADDRESSED | Text matches code: per-file Spearman transformed by clip((1-rho)/2,0,1); V_c is the population variance of those values; V_s is the pooled within-level population variance over repeats; min-max across the family panel with constant column mapped to 0; ladders with <3 levels or non-finite Spearman skipped; each factor clipped to [1e-6,1] | None |
| F03 | Ladder construction, operator taxonomy, ladder lengths, compile status of perturbed files | `04:51-58`; `996_appendix_judge_cert_plots.tex:4-10`; `results_exp16_final_robust_r9_median/detail_rows.csv` (24 files x levels L0-L4 per judge; 4 rewrite types x 24 files) | APPLY (Tier 2, A6) | Operators and the absence of elaboration checks are stated; ladder length, probe counts and the consequence of unchecked compilation are not | Add to `996` after line 8: "Each recorded panel has 24 ladders with five levels, the original artifact plus four cumulative edits, and four rewrite probes per artifact." and "Compilation of the edited text was not checked, so a score drop can reflect malformed text rather than semantic damage." |
| F04 | One annotator, two rubric passes described as "human-human agreement ceiling"; CI spans zero | `05_experiments.tex:5,8-10`; `06:5`; `997_appendix_human_alignment.tex:4-7,15` | ALREADY_ADDRESSED | Passes are described as two judgments by one person; the text states they cannot bound judge agreement; the table shows [-0.015,0.489] | None (optional: one appendix sentence that the three duplicated pass2 rows for one problem were averaged, which is why MAE is 0.771 rather than the old 0.778; source `archive/26_human_label_dataset_audit/results/PANEL_TRACE.md`) |
| F05a | No discussion of deterministic symbolic equivalence checks and where LLM judges are needed | `01:13-16`; `03_problem_setup.tex:14-18` (no sentence on when symbolic checks apply); coordinator's `primary_source_notes.md` verifies Poiroux et al., EMNLP 2025 (BEq+, proof attempts in both implication directions; DOI 10.18653/v1/2025.emnlp-main.907) as a primary source | APPLY (Tier 3, A10) | The intro argues representation mismatch but never states that interface-compatible equivalence can sometimes be checked mechanically; a scoping sentence preempts the baseline question without claiming a result. A successful proof establishes the submitted obligation under its assumptions only; a failed attempt does not show inequivalence | Add to `03` after line 15: "When a candidate shares the reference's interface, automated proof attempts in both implication directions can sometimes establish equivalence with the reference specification~\citep{lahiri2024evaluating,poiroux2025beq}." / "Such checks do not decide equivalence in general, a failed attempt does not show inequivalence, and they do not apply across differing representations, which is the setting studied here." Add a `poiroux2025beq` entry to `refs.bib` from the verified metadata |
| F05b | Evaluate the LLM judge against symbolic baselines | none | FUTURE_EVIDENCE | No such run exists; would need new probe construction and inference | None |
| F06 | n=8 panels pool degenerate controls; bimodality may drive rho | `05:52-53,62,96-103`; `06:5`; recomputation from committed `judge_trust_vector.csv` (Section 5) | APPLY (Tier 1, A2) | Removing edit distance and random leaves six configurations with averaged-label rho 0.771 (Codex), 0.486 (Opus), 0.943 (Qwen); among the four same-model prompts alone the index does not resolve the order (0.400, 0.000, 0.800). Both facts are deterministic and answer the concern honestly | Add after `05:62`: "Removing the two non-LLM controls leaves six configurations per family, with averaged-label associations of $0.771$ for Codex, $0.486$ for Claude Opus, and $0.943$ for Qwen3-Coder." / "Among the four same-model prompts alone, the index does not resolve their order of human agreement." / "The association therefore does not rest only on separating the non-LLM controls, but it is coarse among semantic prompts." Put all nine sub-panel values in a small `990` table |
| F07 | Report p-values and CIs for every Table 3 cell; several are below the n=8 significance threshold | `05:85-86,92` (Codex only; "corresponding intervals for the other families are not reported"); exact 8! permutation: Opus 0.096/0.022/0.132, Qwen 0.005/0.243/0.011; Codex exact 0.015/0.005/0.046 agrees with archived 0.017/0.005/0.045 | APPLY (Tier 1, A1) | The reviewer's point is correct: Opus avg and pass2 and Qwen pass1 are not individually significant; the exact permutation test is deterministic and cheap | Add after `05:62`: "Exact permutation probabilities over all $8!$ orderings are $0.096$, $0.022$, and $0.132$ for Claude Opus and $0.005$, $0.243$, and $0.011$ for Qwen3-Coder on averaged, pass1, and pass2 labels." / "Only some cells are individually distinguishable from a random ordering at the $0.05$ level." Keep the frozen Codex rows unchanged; note in `990` that the exact Codex values agree with the archived resampled values to within 0.002. Bootstrap intervals for Opus and Qwen are optional deterministic work |
| F08 | Move the expanded 13-judge panel into the main text for power | `05:131-133`; `997:28-31` | REJECT | That panel plots a pass1-selected geometric variant, not TI_var, on reused validation labels; the text says so. Promoting it would conflate objects | None |
| F09 | n=75 single benchmark; test transfer on other Lean benchmarks | `06:26-27` | FUTURE_EVIDENCE | Already disclosed; no data | None |
| F10 | Downstream Table 7: self-evaluation confound, uncertified Claude 3.7, no kernel statistics, problem- versus theorem-level averaging, caption capitalization, VeriBench citation conflation | grep of all section files: no DSPy, Trace, Claude 3.7, 857-theorem breakdown | REMOVED | Table and Section 5.7 deleted in the rewrite (number map: no machine-readable authority located) | None; do not restore |
| F11a | Alpha-renaming drops scores to 0.399 yet t=0.85 is recommended | `05:23-26,37-44`; `06:20`; `996:4-7`; `05:166-169` | ALREADY_ADDRESSED | The 0.399 claim was withdrawn as invalid evidence; the threshold now measures repeatability of artifact decisions, not correctness | None |
| F11b | Test AST canonicalization (de Bruijn) before grading | `05:40-44` (score-replacement proxy 0.250 to 0.070, disclosed as not a fix) | FUTURE_EVIDENCE | Requires rescoring canonicalized text. A validated alpha generator exists in `py_src/cert_judge/probe_validation.py` for the separate PTI-v0 object; per project rules it must not be relabeled into this manuscript | None |
| F12 | Only basic prompt variants; no structured multi-stage judges | `995_appendix_judge_prompts.tex` (all four prompts single-call) | APPLY (Tier 3, A11) + FUTURE_EVIDENCE | A one-clause limitation is supported; the experiment is not | Add to `06` after line 19: "All configurations are single-call rubric prompts, so structured multi-stage judges~\citep{TongZhang2024CodeJudge} are untested." |
| F13 | GM beats TI_var on Codex and Opus; qualify the "more reliable" claim | `05:127-133` | ALREADY_ADDRESSED | The text states GM is numerically higher for Codex and Opus and that TI_var is retained for its explicit penalties, "not because these data establish its superiority" | None |
| F14 | Isolate the variance penalties' contribution (four-property geometric baseline) | `998:34`; archived `results_exp28_varaware_*/summary.json:correlations.rho_Cf_vs_human`: Codex 0.643/0.690/0.667, Opus 0.467/0.527/0.575, Qwen 0.690/0.048/0.905 | APPLY (Tier 1, A3); literal four-property baseline FUTURE_EVIDENCE | The archived runs already contain the bug-component-only association; adding the penalties raises the association in eight of nine cells (exception Qwen pass2, 0.905 to 0.857). A four-property geometric baseline is impossible because P3 was not scored on these panels | Add to `05` "Choice of index" after line 130: "The bug-monotonicity component alone has averaged-label associations of $0.643$, $0.467$, and $0.690$, so the two variance penalties raise the association in eight of the nine family--pass cells (Appendix~\ref{app:moved-results})." Add the nine archived values as a table in `990` |
| F15 | Cross-pass tuning: parameterization, objective, fitted weights | `990:3-7`; `998:39-41`; `exp23_cross_pass_calibration.py:25-28,85-103`; `results_exp23_cross_pass_calibration/summary_fit_pass2.json` | APPLY (Tier 2, A5) | Parameterization is stated; the objective, search, and pass2 weights are not | Add to `990` after line 5: "The search maximizes the judge-level Spearman correlation on the fitting pass over four seeded weight vectors and 200{,}000 Dirichlet draws with seed 42." / "The pass1 optimum coincides with the seeded vector $(0,0.4,0,0.6,0,0)$; the pass2-fitted weights are $0.17$ (ident), $0.04$ (mono), $0.17$ (weak), $0.60$ (stab), $0.01$ (anti), and $0.01$ (subtle)." |
| F16a | `rho_bug=-0.790 at all t` is trivial if computed pre-threshold | `990:27` | ALREADY_ADDRESSED | Now framed as independence of the raw ranking from the threshold | None |
| F16b | Text lists six thresholds, table shows four | `05:166`; `990:25,43`; `archive/02_neurips_reviews/results/threshold_calibration_sweep/threshold_metrics.csv` (six rows; 0.85 flip 0.046086 is the minimum; 0.65 0.049242, 0.75 0.048611, 0.80 0.051136) | ALREADY_ADDRESSED | The current text says "selected points"; the minimum claim is verified against all six recorded thresholds | Optional one clause in `990:25`: "The sweep covered six thresholds from $0.60$ to $0.85$ in steps of $0.05$." |
| F16c | Flip-rate intervals overlap, so the reduction is within sampling error | `05:167`; `990:42-43` (caption asserts a reduction; 0.60 [0.048,0.069] versus 0.85 [0.037,0.057]) | APPLY (Tier 1, A4) | The caption and sentence state a reduction that the recorded intervals do not establish | Change `05:168` to: "The selected threshold is $0.85$, which has the lowest observed flip rate in that sweep, although its interval overlaps those of every other threshold." Change `990:42-43` caption accordingly |
| F17 | Judge output integer in {0..10} versus float prompts | `03:21`; `995:6` | ALREADY_ADDRESSED | "All model prompts request scores in [0,1], not integers on a 0--10 scale"; the integer claim belonged to the deleted Table 7 | None |
| F18 | "rho=0.881 across 8 judges" mismatches the headline | `05`, `06` (no such sentence); `990:15` (0.881 only as the pass1 fit value) | REMOVED | Sentence deleted | None |
| F19 | Unanalyzed 5-rater pool; "substantially broader" (+3 pairs); repeated 6.1/6.2 paragraphs; compute the zero-shot correlation | `06:7-15`; `997:45-46`; `archive/22_pooled_heldout_and_noise_ceiling/REPORT.md` Findings B-C; `archive/23_reanchored_calibration/REPORT.md`; `archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` | ALREADY_ADDRESSED | The pool is described by rater and pair counts, its rubric drift (about 0.13 on 63 shared pairs) is disclosed, and both registered screens are reported as null without relabeling the pool as a test set; no duplicated paragraph remains | None |
| F20 | Rice's theorem misapplied to gold incompleteness | no "Rice" in any section file | REMOVED | Appendix D deleted | None |
| F21 | Verus described as having a "larger kernel" | no "Verus" in any section file | REMOVED | Appendix B deleted | None |
| F22 | Dafny cannot "natively run" verified programs | no "Dafny" in any section file | REMOVED | Appendix B deleted | None |
| F23 | `anti` and `subtle` undefined in v2 | `998:32` | ALREADY_ADDRESSED | Both defined with clipping | None |
| F24 | Leanstral absent from the configuration registry | `05:134`; `997:42-44`; `995:3` (three identifiers only); `results_exp28_varaware_leanstral_avg/judge_trust_vector.csv` judge ids `labs-leanstral-2603|...` | APPLY (Tier 2, A7) | The registry table is gone, but the Leanstral identifier is never given | Add to `997` after line 42: "That panel uses the model \texttt{labs-leanstral-2603} in the same eight-configuration form." Verify the repeat count from the archived exp16 summary that `results_exp28_varaware_leanstral_avg/summary.json:inputs` names before stating it |
| F25 | Bibliography entry contains an editorial note (Liu et al. 2025) | `refs.bib` (19 entries, 17 cited; no `note` fields; no Liu 2025 entry) | REMOVED | Entry dropped with the extended related work | None |
| F26 | Internal run identifiers in captions and figure titles (`results_exp16_final_robust_r9_median`, `EXP25 / EXP22-GM`, `EXP16 [repeat1]`, `EXP17:`, `EXP19 Failure Mode:`) | `997:35` still includes `figures/fig7_trend_update_baseline_vs_geom_13judge_avg.png`, whose rendered title reads "EXP25 / EXP22-GM: baseline vs geometric trust index — label_set=avg / Δρ = +0.203 (geometric beats baseline)", panels "Baseline cert-index v2 ρ_spearman = 0.566 [-0.05,0.93]" and "Geometric (mono^0.4 · stab^0.6) ρ_spearman = 0.769 [0.34,0.95]", labels `editdist_e1`, `random_r1`, `P11_JSON_FIRST`; the five PDF figures are clean (pdftotext); no "EXP" token in `main.pdf` text | APPLY (Tier 2, A9) | One instance survives; the archived `results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json` holds all 13 rows (`judge_id`, `geo_trust_index`, `baseline_v2`, `human_spearman`) and both intervals, so a deterministic re-plot needs no recomputation | Regenerate as `figures/expanded_panel_v2_vs_geometric.pdf` from the archived JSON with titles "Arithmetic $v2$: $\rho=0.566$ [$-0.05$, $0.93$]" and "Geometric $\mathrm{mono}^{0.4}\mathrm{stab}^{0.6}$: $\rho=0.769$ [$0.34$, $0.95$]", descriptive point labels, no run codes; update `997:35`; keep the caption's values |
| F27 | Figure 7 caption formula has an unmatched parenthesis | `997:36-38` (typeset math) | ALREADY_ADDRESSED in LaTeX; the PNG title still has the ASCII form | Covered by F26 | See A9 |
| F28 | BAD_STRINGY prompt split across pages by a figure | rendered pages 11-12 contain the prompt listings and no figure or table caption | ALREADY_ADDRESSED | Prompts are non-floating listings; diagnostics figures follow in Appendix E | None |
| F29 | "Figures A.1--A.3" broken references | no such text; `main.pdf` text contains no "??" | REMOVED | Appendix F deleted | None |
| F30 | Circumflex accents typeset outside parentheses | `04:64` uses `\widetilde V_c`, `\widetilde V_s` | ALREADY_ADDRESSED | Correct math accents | None |
| F31 | `mono` versus `mono_rank` naming | `998:29,37,39` use `mono` throughout | ALREADY_ADDRESSED | Consistent | None |
| F32 | Line-break hyphenation "artifacts" ("thresh-old", "specifica-tion", "type-checking" glyph) | PDF text extraction of a justified layout | REJECT | Ordinary end-of-line hyphenation and font-extraction artifacts, not source typos | None |
| F33 | Old typos and phrasing in deleted text: "theorem-s/tests", "vectorsand", "A user state", "soundness problem", "(Robertson & Koyejo, 2025) study", missing period after "Scalable Oversight with LLM Judges", "without oracles Nie et al. (2025)", stacked prepositions, mismatched quotes around `True`, "Lean-semantics", "preceding paragraph", "Pass@k", arrow spacing, BAD_STRINGY "≈0.45" ambiguity, Table 7 header case | none of the strings occur in the section files; `04:52` reads "theorem statements and unit tests"; `05:98` gives 0.435 explicitly; `995:28` uses backticks | REMOVED | All in deleted or rewritten text | None |
| F34 | 75 pairs versus 72 analyzed; explain the difference in Section 5.1 | `05:6-7`; `archive/26_human_label_dataset_audit/results/PANEL_TRACE.md` (three pairs of `0_unsafeMultiply_safe` dropped for a stale gold filename) | ALREADY_ADDRESSED | Stated in the first paragraph of the experiments section | None |
| F35 | Table 4/Table 6 text-table harmonization items | covered by F15 and F16b | ALREADY_ADDRESSED | See those rows | None |

### Current-paper defects outside the feedback inventory (found during the audit)

| ID | Defect | Evidence | Disposition | Exact repair |
|---|---|---|---|---|
| X01 | Author names duplicated by `\citep` after a textual author mention | `02_related_work.tex:5-6`; rendered page 2: "Bavaresco et al. (Bavaresco et al., 2025)", "Schroeder and Wood-Doughty (Schroeder & Wood-Doughty, 2024)" | APPLY (Tier 1, A8) | Replace `Bavaresco et al.~\citep{Kocmi2024HumanVsLLM}` with `\citet{Kocmi2024HumanVsLLM}` and `Schroeder and Wood-Doughty~\citep{Li2024TrustLLMJudgments}` with `\citet{Li2024TrustLLMJudgments}` |
| X02 | P1 is defined as a literal self-comparison, but the recorded panels score only the four rewrite probes | `04:49` versus `detail_rows.csv` row types (`property_identity` keys are `RENAME`, `REORDER`, `STYLE`, `ALPHA` only; 768 = 8 x 24 x 4); `998:29` | APPLY (Tier 3, A12) | Add to `04` after line 49: "In the recorded panels, P1 is assessed through the four rewrite probes; no literal self-comparison was scored." Verify the same for the Opus and Qwen `detail_rows.csv` before applying |

## 4. Historical-paper defects (valid for the 28-page draft, moot now)

These were real defects of the submitted draft and are recorded so the coordinator can close them without re-reading the old paper. None warrants restoring text.

| Old location | Defect | Why it is moot |
|---|---|---|
| Abstract, Sec. 1, 4.1, Table 1, Sec. 6.2 | Four-property narrative versus the bug-only TI_var; "single low property collapses the index" | Rewritten (F01) |
| Sec. 4.1, App. G.5 | VarCorr/VarScore undefined; `anti`/`subtle` undefined | Defined (F02, F23) |
| Sec. 5.4, Fig. 9 | "P3 weak monotonicity is the strongest predictor" rested on a bug-ladder field named `P3_weak_mono` | Corrected: "this table contains no P3 missing-specification result" (`05:143-147,161`) |
| Sec. 5.7, Table 7 | Claude 3.7 judged Claude 3.7 agents; judge never certified; integer scores; ambiguous averaging; conflated citations | Deleted (F10) |
| Sec. 5.6, Table 2, 6.2 | Alpha-renaming mean 0.399 treated as a real invariance failure | Withdrawn as malformed-probe evidence (F11a) |
| Sec. 6.1/6.2 | Pool called "substantially broader"; paragraph duplicated; "0.881 across 8 judges" | Rewritten (F18, F19) |
| App. B | Verus "larger kernel"; Dafny "cannot natively run"; grammar | Deleted (F21, F22) |
| App. D | Rice's theorem implies gold incompleteness | Deleted (F20) |
| App. E-G, Table 10 | Prompt split by a float; broken "Figures A.1--A.3"; Leanstral missing from registry; run codes in captions; Table 9 "ceiling" | Deleted or rewritten; one figure title remains (F26) |
| References | Editorial note in Liu et al. 2025 | Entry removed (F25) |

## 5. Supporting deterministic recomputation (no inference)

The numbers behind A1, A2 and A3 were computed from the committed component vectors with the script below (pure Python, average ranks for ties, exact enumeration of all 40,320 orderings). The implementation must re-run it, commit the script and its CSV output under this experiment's `expt_v1/results/`, and cite that artifact for the new sentences. Archived `rho_Cf_vs_human` fields agree with the recomputed `rho(C_f, y)` column to three decimals.

| Family | Pass | TI_var rho (n=8, frozen) | Exact permutation p | rho(C_f, y) (archived) | rho without edit/random (n=6) | rho among four same-model prompts (n=4) |
|---|---|---:|---:|---:|---:|---:|
| Codex | avg | 0.833 | 0.015 | 0.643 | 0.771 | 0.400 |
| Codex | pass1 | 0.905 | 0.005 | 0.690 | 0.886 | 0.800 |
| Codex | pass2 | 0.738 | 0.046 | 0.667 | 0.657 | 0.000 |
| Claude Opus | avg | 0.643 | 0.096 | 0.467 | 0.486 | 0.000 |
| Claude Opus | pass1 | 0.810 | 0.022 | 0.527 | 0.829 | 0.600 |
| Claude Opus | pass2 | 0.595 | 0.132 | 0.575 | 0.486 | 0.000 |
| Qwen3-Coder | avg | 0.905 | 0.005 | 0.690 | 0.943 | 0.800 |
| Qwen3-Coder | pass1 | 0.476 | 0.243 | 0.048 | 0.600 | 0.600 |
| Qwen3-Coder | pass2 | 0.857 | 0.011 | 0.905 | 0.943 | 0.800 |

Input directories under `experiments/archive/04_veribench_validation/`: `results_exp28_varaware_codex_{avg_newindex,pass1_newindex,pass2_newindex}`, `results_exp28_varaware_opus_{avg,pass1,pass2}_newindex`, `results_exp28_varaware_qwen_{avg,pass1,pass2}`; file `judge_trust_vector.csv`, columns `judge_id`, `human_spearman`, `C_f_mean`, `TI_variance_aware`, `n_files_with_corr` (24 in every row of every file). `results_exp28_varaware_codex_pass1` (without `_newindex`) gives identical values.

```python
import csv, itertools, math
from pathlib import Path
def rank(v):
    idx = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v); i = 0
    while i < len(idx):
        j = i
        while j+1 < len(idx) and v[idx[j+1]] == v[idx[i]]: j += 1
        for k in range(i, j+1): r[idx[k]] = (i+j)/2 + 1
        i = j + 1
    return r
def pearson(a, b):
    n = len(a); ma = sum(a)/n; mb = sum(b)/n
    sa = math.sqrt(sum((x-ma)**2 for x in a)); sb = math.sqrt(sum((y-mb)**2 for y in b))
    return float('nan') if sa == 0 or sb == 0 else sum((x-ma)*(y-mb) for x, y in zip(a, b))/(sa*sb)
def spearman(a, b): return pearson(rank(a), rank(b))
def perm_p(a, b):
    obs = spearman(a, b); ra = rank(a); rb = rank(b); cnt = tot = 0
    for p in itertools.permutations(range(len(b))):
        tot += 1
        if abs(pearson(ra, [rb[i] for i in p])) >= abs(obs) - 1e-12: cnt += 1
    return cnt/tot
def stats(csv_path):
    rows = list(csv.DictReader(open(csv_path)))
    ids = [r['judge_id'] for r in rows]
    y = [float(r['human_spearman']) for r in rows]
    ti = [float(r['TI_variance_aware']) for r in rows]
    cf = [float(r['C_f_mean']) for r in rows]
    keep6 = [i for i, j in enumerate(ids) if not j.startswith(('editdist', 'random'))]
    keep4 = [i for i in keep6 if not ids[i].startswith('gpt-4o-mini')]
    sub = lambda v, k: [v[i] for i in k]
    return dict(rho8=spearman(ti, y), perm_p=perm_p(ti, y), rho_cf=spearman(cf, y),
                rho6=spearman(sub(ti, keep6), sub(y, keep6)), rho4=spearman(sub(ti, keep4), sub(y, keep4)))
```

Threshold sweep record used for A4 (`experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/threshold_metrics.csv`, `gpt-5.3-codex`, `P8_STRICT_B`, 176 files, 3 repeats, 1,000 bootstrap draws; selection rule "min threshold_flip_rate, tie-break by pass_rate closest to 0.5"):

| Threshold | Flip rate [95% interval] | Pass rate |
|---:|---|---:|
| 0.60 | 0.058 [0.048, 0.069] | 0.583 |
| 0.65 | 0.049 [0.040, 0.059] | 0.571 |
| 0.70 | 0.049 [0.040, 0.059] | 0.559 |
| 0.75 | 0.049 [0.039, 0.059] | 0.551 |
| 0.80 | 0.051 [0.042, 0.061] | 0.544 |
| 0.85 | 0.046 [0.037, 0.057] | 0.536 |

Cross-pass fit record used for A5 (`results_exp23_cross_pass_calibration/summary_fit_pass{1,2}.json`; script defaults `--iters 200000 --seed 42 --eps 1e-6`; seeded starts `(1,0,0,0,0,0)`, `(0,1,0,0,0,0)`, `(0,0.4,0,0.6,0,0)`, `(0.25,0.25,0.2,0.15,0.1,0.05)`; objective `spearmanr(geo_index, y)` on the fitting pass): pass1 weights `(0, 0.4, 0, 0.6, 0, 0)` with fit 0.881 and other-pass 0.810; pass2 weights `(0.168, 0.038, 0.171, 0.602, 0.008, 0.014)` with fit 0.857 and other-pass 0.786.

## 6. Ordered implementation brief (Astra Ultra)

Edit only the named section files; one sentence per line; keep the `% !TEX root = main.tex` first line; never touch `experiments/archive/**`; build in a scratch copy; commit with explicit pathspecs.

1. **A1 (05_experiments.tex, after line 62).** Two sentences with the exact permutation probabilities for Opus and Qwen (values in Section 5). Keep the frozen Codex table rows; add one sentence to `990_appendix_additional_results.tex` noting the exact Codex values 0.015/0.005/0.046 agree with the archived resampled values to within 0.002.
2. **A2 (05_experiments.tex, after A1).** Three sentences on the controls-excluded (n=6) and same-model (n=4) associations; a nine-cell table in `990` (label it descriptive; no p-values for n=6 or n=4).
3. **A3 (05_experiments.tex "Choice of index", after line 130; table in 990).** One sentence with the averaged-label `rho(C_f, y)` values 0.643/0.467/0.690 and "eight of nine cells"; state that a four-property geometric baseline is unavailable because P3 was not scored on these panels only if space permits (the "Coverage of P3" paragraph already implies it).
4. **A4 (05_experiments.tex:168; 990 lines 42-43).** Add the interval-overlap clause; soften "slightly reduces" in the caption to "has the lowest observed flip rate, with overlapping intervals".
5. **A8 (02_related_work.tex:5-6).** `\citet` replacements.
6. **A5 (990 lines 3-7).** Objective, search procedure, pass1 seeded coincidence, pass2 weights.
7. **A6 (996 after line 8).** Ladder length, probe counts, unchecked compilation consequence.
8. **A7 (997 after line 42).** Leanstral identifier `labs-leanstral-2603`; state the repeat count only after reading the archived exp16 summary named in `results_exp28_varaware_leanstral_avg/summary.json`.
9. **A9 (997:35 and figures/).** Regenerate the expanded-panel figure from `results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json` with descriptive titles and labels; the plotting script goes under this experiment (`expt_v1/results/` or a `scripts/` subfolder), not under the archive; values and intervals must be read from the JSON, never recomputed.
10. **Tier 3, only if the coordinator approves:** A10 (03 after line 15, citing `lahiri2024evaluating` and a new `poiroux2025beq` bib entry built from the coordinator's verified metadata), A11 (06 after line 19), A12 (04 after line 49, after verifying Opus and Qwen `detail_rows.csv`), the duplicate-row policy sentence (997), and the "six thresholds in steps of 0.05" clause (990:25).

Brando's standing rule that the ICLR writing pass is main-text only applies to Tier 2 and Tier 3 appendix edits; the coordinator should confirm they are wanted. Tier 1 is main text except the two small appendix tables that hold the new numbers.

## 7. Unresolved evidence and required deterministic checks

Unresolved (do not invent):
- Bootstrap intervals for the Opus and Qwen headline cells are not archived; computing them needs pair-level resampling from the family `detail_rows.csv` files and is optional.
- The Leanstral repeat count and panel composition beyond the identifier are not verified here.
- Whether the Opus and Qwen `detail_rows.csv` files also lack literal self-comparison rows (A12) is not verified here.
- The pool association "approximately 0.13 on 63 shared pairs" is supported by the committed exp22 `REPORT.md` prose, not by an exact JSON field (as the rewrite's evidence audit already notes).

Checks the implementation must run and report with output:
1. `cd paper_latex/ICLR_2027_submission && python3 ~/agents-config/scripts/latex_sentence_lines.py --check main.tex 0*.tex 99*.tex` (passes at `c118d7c`; must still pass).
2. Scratch build: copy the paper directory to a temporary folder, `latexmk -pdf -interaction=nonstopmode main.tex`; zero errors; `grep -c "undefined\|multiply defined" main.log` = 0; `pdftotext main.pdf - | grep -c "??"` = 0; `pdfinfo main.pdf` page count; confirm the Conclusion ends on page 9 or earlier and the statements follow.
3. `pdftotext main.pdf - | grep -n "Bavaresco et al. (Bavaresco\|Wood-Doughty (Schroeder"` = no matches (A8).
4. `pdftotext figures/<new figure>.pdf - | grep -c "EXP"` = 0 and `pdftotext main.pdf - | grep -c "EXP[0-9]"` = 0 (A9); the 13 plotted points and both intervals equal the archived JSON values.
5. Re-run the Section 5 script; the nine `rho8` values must equal the frozen table to three decimals and `rho_cf` must equal the archived `rho_Cf_vs_human` fields; commit script and CSV under this experiment.
6. `python3 py_src/cert_judge/experiment_layout.py --check` (passes now: "Layout OK: 8 active experiments").
7. `git diff --stat` limited to the intended section files, the new figure, and task-owned artifacts; `git status` shows no change under `experiments/archive/`.
8. Copy the rebuilt `main.pdf` back only after the semantic checks pass; record the new page count and SHA-256 in the experiment's `results.md`.

## 8. Model identification

- Runtime log `expt_v1/logs/claude_fable.jsonl`, first `system` init record: `model: claude-fable-5-1`, `permissionMode` present, `claude_code_version` field present (value not copied here); no other model value appears in the log.
- Dispatch command (`expt_v1/logs/claude_fable_process.json`): `claude -p --dangerously-skip-permissions --model claude-fable-5-1 --effort max --output-format stream-json --verbose --max-turns 48`; client `claude 2.1.283` per `expt_v1/dispatch_manifest.json`.
- The session's own system prompt names the model Claude Fable 5.1 (`claude-fable-5-1`). Effort `max` is a requested flag; served-model telemetry beyond the init record is not visible from inside the session.
- No subagents, provider keys, external messages, or new inference were used; all numbers above come from committed files and pure-Python recomputation.

**TLDR-end:** [cert-judge: feedback revision] `YES_SELECTIVELY`: the current manuscript already resolves most of the automated feedback; apply five deterministic main-text repairs (permutation probabilities for the non-Codex cells, controls-excluded and component-only associations, threshold-interval overlap, two `\citet` fixes) plus four appendix reproducibility and presentation items, and defer everything that needs new inference or a matched-rubric test set.
