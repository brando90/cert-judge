# Experiment 37: warranted current-paper repairs completed and verified

Experiment 37: applied all 12 warranted current-paper repairs; 36 frozen-data diagnostics preserve positive primary-family and negative Leanstral associations; manuscript verified at 19 pages, including nine main-text pages.

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/paper-feedback/experiments/37_openreview_feedback_current_iclr_revision/expt_v1/results/RESULTS_feedback_revision.md>

Date: 09-26-2026. The repository link is the intended address, not a publication claim: this revision is an uncommitted working-tree patch on `codex/paper-feedback`, based on `f73228a9350b59001fb4ed187ef7351d73503e30`.
Implementation and deterministic verification were performed by the requested GPT-6 Astra session; no additional agents, model evaluations, human labels, or provider calls were used.
All writes were confined to the assigned isolated checkout.

## Deliverables and disposition

- [Complete issue table](final_issue_table.md) and [machine-readable dispositions](final_dispositions.json): all 41 stable issue identifiers, original concerns, evidence, decisions, manuscript locations, verification, and remaining gaps.
- [Verification receipt](verification.json), [initial state](initial_state.json), [build receipt](build_receipt.json), and [visual inspection record](visual_inspection.json).
- [Rebuilt manuscript](../../../../paper_latex/ICLR_2027_submission/main.pdf) and [publication figure](../../../../paper_latex/ICLR_2027_submission/figures/expanded_panel_v2_vs_geometric.pdf).
- [Diagnostics](diagnostics.csv), [explicit subset membership and score vectors](subset_membership.json), [repeat/probe audit](panel_audit.json), [cross-pass fit audit](cross_pass_audit.json), [threshold audit](threshold_audit.json), and input hashes in [diagnostic provenance](diagnostic_provenance.json) and [figure provenance](figure_provenance.json).
- Deterministic scripts in [../scripts/](../scripts/); a complete binary-capable patch is saved locally at `../tmp/feedback_revision.patch`, with its application check and hash in `../tmp/patch_receipt.json`. Temporary build/render artifacts and private inputs remain ignored.

Final issue counts are **12 APPLY, 16 ALREADY_ADDRESSED, 8 REMOVED, 3 FUTURE_EVIDENCE, and 2 REJECT**.
The three future-evidence rows do not exhaust the remaining limitations: some implemented reporting repairs also explicitly preserve absent measurements.
No scientific gap is declared solved merely because its review item has a disposition.

| Action | Implemented repair and independently checked interpretation |
|---|---|
| A1 | Added nine exact two-sided permutation probabilities, separate from the unchanged historical Codex resampling table. Explicitly unadjusted across nine descriptive family/pass tests; missing historical Opus/Qwen bootstrap intervals remain unavailable. |
| A2 | Computed the actual five semantic configurations and the three target-family semantic prompts, excluding the lexical control from both. Saved all three label views and fixed original normalization. |
| A3 | Added component-only correlations and the 8/9 higher full-index point correlations; interpretation is descriptive, with no causal or independent validation claim. Missing four-property measurements remain explicit. |
| A4 | Reported threshold-interval overlap without treating it as a significance test; no paired difference test or unique optimality established. |
| A5 | Added the recorded fitted weights, component order, objective, search method, and precise distinction between script defaults and unrecovered actual seed/draw count. |
| A6 | Checked and stated 24 five-level ladders and 96 rewrite rows per configuration across all four covered families; no compilation or semantic-validity guarantee added. |
| A7 | Identified `labs-leanstral-2603`, its eight configurations, three recorded scores per row, median aggregation, and negative semantic-subset result. |
| A8 | Repaired two duplicated author-name citation constructions in related work. |
| A9 | Replotted the expanded panel with descriptive labels and a shared key; all 13 points in each panel and original correlation/interval values preserved. |
| A10 | Added a concise symbolic-checker boundary with the verified Poiroux citation: aligned interfaces or a specified correspondence, encoded implications under assumptions, both human-alignment error types, and no benchmark of such a tool here. |
| A11 | Added the single-call rubric scope per repeat for language-model configurations; multistage judging remains untested. |
| A12 | Corrected the consultation's overbroad identity statement: identity-summary rows use four rewrites, while unedited self-comparisons are present at bug-ladder level zero. |

The author’s abstract and introduction, `main.tex`, frozen data, historical manuscript sources, and existing figures are unchanged.
Eight current section files and the bibliography were edited; the current compiled manuscript and one new figure were produced.
Two local float placements were adjusted to keep the human-agreement table with its section and the final three figures in numerical order.

## Frozen-data diagnostics

The numerical object remains the historical variance-aware trust index, `TI_var`, rather than the newer behavioral proxy.
Every family has eight configurations: three semantic prompts for its target model, its deliberately lexical `BAD_STRINGY` prompt, two GPT-4o-mini prompts, edit distance, and random.
The five-configuration subset removes the last three controls: `BAD_STRINGY`, edit distance, and random.
The three-configuration subset contains only the target model's baseline, checklist, and strict semantic prompts.
The consultation's six/four subsets retained `BAD_STRINGY`; they were omitted because they would not answer the semantic-only question.

All numbers below are Spearman rank correlations with human agreement.
Each cell lists **full eight / semantic five / target semantic three**; values are rounded to three decimals for display.

| Family | Averaged labels | Pass 1 | Pass 2 |
|---|---|---|---|
| Codex | 0.833 / 0.900 / 1.000 | 0.905 / 0.900 / 1.000 | 0.738 / 0.800 / 0.500 |
| Claude Opus | 0.643 / 0.600 / 0.500 | 0.810 / 0.800 / 0.500 | 0.595 / 0.600 / 0.500 |
| Qwen3-Coder | 0.905 / 0.900 / 0.500 | 0.476 / 0.400 / 0.500 | 0.857 / 0.900 / 0.500 |
| Leanstral | −0.095 / −0.900 / −0.500 | −0.119 / −0.900 / −0.500 | −0.048 / −0.500 / 0.500 |

This is **36/36 expected family × label-view × subset rows**, including 27 primary-family rows and nine Leanstral rows.
Average ranks handle ties on saved full-precision values; ranks are never formed from rounded displays.
The original eight-configuration variance normalization is fixed before subsetting, with no new fitting or selection of a better normalization.
There are zero undefined final subset correlations; the historical omission of constant bug ladders is retained (23 included ladders for Leanstral baseline and checklist, 24 for all other configurations).
The script independently checks correlations through NumPy rank-vector correlation and reconstructs each of the 96 saved family/pass/configuration component vectors and indices within absolute tolerance `1e-12`.

Positive associations among three or five observations do not establish precise discrimination among useful judges.
The two GPT-4o-mini controls remain in the five-configuration subset, and label reuse, family-panel dependence, and selection of the historical protocol remain limitations.
Leanstral's negative five-configuration association is retained on every label view.

### Exact permutation procedure and component comparison

For each of the nine primary-family/pass cells, all **40,320 labeled permutations** of human-agreement values are enumerated.
The two-sided tail includes absolute rank correlations at least as large as observed.
Integer products of centered doubled average ranks avoid floating-point decisions at the tail boundary; ties count with their labeled multiplicity.
This deterministic enumeration uses no random seed and no Monte Carlo correction.

| Family | Averaged labels | Pass 1 | Pass 2 |
|---|---|---|---|
| Codex | 620/40320 = 0.0153769841 | 184/40320 = 0.0045634921 | 1848/40320 = 0.0458333333 |
| Claude Opus | 3878/40320 = 0.0961805556 | 878/40320 = 0.0217757937 | 5334/40320 = 0.1322916667 |
| Qwen3-Coder | 184/40320 = 0.0045634921 | 9800/40320 = 0.2430555556 | 432/40320 = 0.0107142857 |

These are unadjusted post-hoc descriptive probabilities across nine tests, not independent confirmation of a selected protocol.
No additional tests were performed for Leanstral or the subsets.
The historical Codex 10,000-permutation results and bootstrap intervals are unchanged; their probabilities differ from the new exact values by less than 0.002.
Historical Opus and Qwen bootstrap intervals remain unavailable, and no alternative bootstrap procedure was substituted for them.

The mean transformed bug-correlation component, `C_f`, has averaged-label correlations of **0.642857, 0.467074, and 0.690476** for Codex, Opus, and Qwen.
The full index's point correlation is higher in eight of nine primary cells; the exception is Qwen pass 2, which falls from **0.904762 to 0.857143**.
These comparisons do not isolate a causal effect of variance penalties or supply independent validation.
The panels lack missing-specification ladders, so a measured four-property comparison is unavailable.

## Repeat, probe, fit, and threshold verification

The audit reads **9,216/9,216 score rows**: four families × eight configurations × 288 rows.
Each configuration has 72 human-evaluation rows, 120 bug rows (24 references × five levels), and 96 identity rows (24 references × four rewrite types).
All primary model and all Leanstral rows contain three recorded scores; Codex's two non-model controls instead contain nine repeated, identical values.
The saved field named `score_mean` matches the median of each array within `5.1e-7`, consistent with six-decimal serialization.
Repeat lengths, mean within-row population standard deviations, included-ladder counts, and level-zero scores are saved per configuration and row type in `panel_audit.json`.
Identical repeated values for the random control are not evidence of robustness to newly sampled randomness.

Inspection of the generator and scoring driver establishes that `build_bug_ladder` begins with the extracted reference text and that the candidate at level zero is scored against that same reference.
Thus there are **24 unedited self-comparisons per configuration** in bug rows, even though no literal-self row type occurs among the 96 rewrite-based identity rows.
The sentence in the paper is scoped to the four audited families.
The historical edits were not compilation-validated; none of this audit certifies their semantic direction or repairs malformed alpha rewrites.

The six-component geometric fit maximizes judge-level Spearman association on the fitting pass, starting with four fixed vectors and then uniform Dirichlet draws.
In component order `(ident, mono, weak, stab, anti, subtle)`, pass 1 stores exactly `(0, 0.4, 0, 0.6, 0, 0)`.
Pass 2 stores `(0.1675571445814022, 0.037758386457350135, 0.17080715295157373, 0.6016894568050665, 0.007821515501013468, 0.014366343703593994)`.
Saved weights reproduce all stored scores within `1e-12` and fitting/other-pass correlations **0.880952/0.809524** and **0.857143/0.785714**.
Rounding pass-2 weights to six decimals changes a score by up to **4.8614856718e-7**; it happens to preserve rankings here but is not an exact replacement.
The script defaults to seed 42 and 200,000 draws, but the saved fit summaries do not record those actual run settings and no historical invocation was recovered.
No search was rerun, and the second label pass over the same pairs is not a test set.

The recorded threshold sweep covers **six** values from 0.60 through 0.85 in 0.05 steps, using 176 files, three scores, mean aggregation, and 1,000 recorded bootstrap iterations.
The observed flip rate changes from **0.058081** at 0.60 to **0.046086** at 0.85; 0.85 is the observed minimum, with interval **[0.037247, 0.056818]**.
Its interval overlaps all five other intervals.
No paired difference test was performed, and overlap establishes neither absence of a reduction nor statistical non-significance; unique optimality is unestablished.

## Primary source and publication figure

The implementer independently checked [Poiroux et al.'s publisher record](https://aclanthology.org/2025.emnlp-main.907/) and [primary paper, Section 3 and Appendix A.6](https://arxiv.org/html/2406.07222v3).
The bibliography now uses the verified 2025 conference publication, authors, pages 17947–17969, and digital object identifier `10.18653/v1/2025.emnlp-main.907`.
The paper reports both human-alignment false positives and false negatives for BEq+; the latter can arise from unsuccessful bounded proof search even for equivalent statements.
Successful proofs establish their encoded implications under their assumptions, not faithful natural-language intent.
Different representations can be related through a specified correspondence; comparison does not categorically require identical representations.
This study has not benchmarked that checker against its graded human reference-coverage criterion.
The original consultation and its source notes remain unchanged.

The expanded-panel figure reads the archived 13-row summary directly.
It preserves 26 actual plotted coordinate pairs, the arithmetic correlation **0.5659340659340659**, the geometric correlation **0.7692307692307693**, and the stored intervals **[−0.05027932960893855, 0.9271708683473389]** and **[0.34302325581395343, 0.9491525423728815]**.
Correlations display to three decimals and interval endpoints to two; full precision is retained in `figure_provenance.json`.
The script asserts equality against the rendered plot artists and performs no resampling or estimate recomputation.
The historical image is untouched; the replacement uses descriptive labels, letter keys, and vector output.
This separately tuned geometric comparison is not relabeled as the fixed index or promoted as independent validation.

## Build, preservation, and reproduction

The required portable document format artifact-operation marker succeeded once before artifact authoring, with `edit`, expected output count 1, and format `pdf`.
The paper was compiled only in an experiment-owned scratch copy using `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
The final build has **19 pages**, conclusion ending on page **9**, and statements starting on page **10**; the conference style's nine-page main-body limit is met.
There are **zero** LaTeX errors, undefined references/citations, unresolved question-mark placeholders, or overfull boxes.
Thirteen non-fatal warnings remain: twelve underfull spacing warnings and one automatic `h` to `ht` float adjustment.
The complete log is retained rather than treating exit zero as sufficient evidence.

Every affected page was rendered at 115 dots per inch and visually inspected.
Pages 3–4 and 15–19 were reinspected after the final edits; other affected pages were confirmed byte-identical to previously inspected renderings, and page 1 was also inspected.
Tables, mathematical accents, citation names, prompt listings, figure labels, and appendix transitions are readable without clipping or overlapping text.
The last two figures float onto page 19 after the appendix discussion, in numerical order.
Page 9 has substantial white space and page 12 has one trailing bibliography entry; these are retained layout limitations, not rendering failures.
Only after these checks was the scratch-built `main.pdf` copied beside its source.

`verification.json` records source and output hashes, exact checks, preservation counts, and the final file manifest.
All 18 consultation manuscript hashes matched at the start.
The author-protected files, historical manuscripts, old figure, frozen Codex table, input artifacts, and repository index are independently checked against their initial or committed contents.
The sentence-layout check, experiment-layout check, and `git diff --check` pass.
No commit, push, shared-checkout edit, global-setting change, experiment archival, or OpenReview mutation was performed.

Run the following from the repository root using Python 3.10 or later with NumPy and Matplotlib; this host used `/usr/local/bin/python3` (Python 3.11, NumPy 2.4.2, Matplotlib 3.10.8).
SciPy is not required.
The usual unqualified Python executable on this host could not load its installed binary packages; no environment settings were changed.

```bash
/usr/local/bin/python3 experiments/37_openreview_feedback_current_iclr_revision/expt_v1/scripts/derive_diagnostics.py
/usr/local/bin/python3 experiments/37_openreview_feedback_current_iclr_revision/expt_v1/scripts/plot_expanded_panel.py
/usr/local/bin/python3 experiments/37_openreview_feedback_current_iclr_revision/expt_v1/scripts/write_dispositions.py
/usr/local/bin/python3 experiments/37_openreview_feedback_current_iclr_revision/expt_v1/scripts/build_manuscript.py
```

The build script creates a new scratch directory and renders its pages; it deliberately does not copy the document back or declare visual approval.
Inspect the new rendering, record its actual hash and visual findings, then copy the successful scratch `main.pdf` to the paper directory and update the build receipt.
The saved visual receipt belongs to this delivered document, not to arbitrary future builds.
After finalizing the document and receipts, run:

```bash
/usr/local/bin/python3 experiments/37_openreview_feedback_current_iclr_revision/expt_v1/scripts/verify_revision.py
/usr/local/bin/python3 experiments/37_openreview_feedback_current_iclr_revision/expt_v1/scripts/create_patch.py
```

The diagnostics and figure are deterministic for the recorded inputs and runtime.
TeX output can differ bytewise on rerun because of build metadata; compare the source hashes, numerical outputs, structure, and rendered pages rather than assuming an invariant manuscript hash.
Input hashes are checked before final delivery; archived model-calling scripts are read as evidence only and never imported or executed.

## Evidence gaps retained

A matched-rubric, independently rated test set is still absent.
The original single-annotator rubric text remains unavailable, and the five-rater pool's changed rubric prevents its negative results from becoming a matched-rubric transfer test.
Cross-benchmark transfer, a symbolic-baseline benchmark, validated canonicalization followed by new scoring, and structured multistage judges remain unmeasured.
Missing-specification ladders are absent from the historical panels, and malformed or unchecked rewrites cannot establish valid-transformation invariance.
Historical Opus/Qwen bootstrap intervals and the fitted search's actual seed/draw count remain unrecovered.
Three/five-configuration associations, component comparisons, and threshold intervals do not establish precise discrimination, causal penalty benefits, or unique optimality.

**TLDR-end:** [cert-judge: Experiment 37] All 12 warranted reporting repairs and all 41 dispositions are complete in the isolated working tree; the 19-page manuscript passes the nine-page main-body limit and deterministic/rendered checks. The scientific limitations and negative Leanstral diagnostics remain explicit.

**Snapshot:**
```text
Issues: 41 = 12 apply + 16 addressed + 8 removed + 3 future + 2 reject
Diagnostics: 36/36 rows; nine exact tests, each 40,320 permutations
Scores audited: 9,216/9,216; no new inference
Semantic-five averaged correlations: 0.900 / 0.600 / 0.900 / -0.900
Final document: 19 pages; main body 9/9; errors 0; unresolved references 0
```
