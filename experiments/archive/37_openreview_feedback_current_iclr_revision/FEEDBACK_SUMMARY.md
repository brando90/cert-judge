# Automated OpenReview feedback: summary and current relevance

**TLDR:** The old review identifies real problems in metric description, statistical interpretation, probe validity, and formal-methods claims. The current rewrite already repairs or removes many of them; remaining changes must be selected against current source, not applied mechanically to the old 28-page paper.

## What the feedback says

The review supports the central idea: test judge behavior with controlled perturbations, use human agreement as one validation criterion, and expose failures rather than relying on a single correlation. Its objections concern whether the particular evidence supports the stronger claims in the old draft.

| Theme | Requested improvement | Current-source observation before consultation |
|---|---|---|
| Index reproducibility | Define variance estimators, normalization, numerical bounds, and aggregation | Appendix `998` now defines population variance, median repeats, family-panel normalization, flooring, and excluded constant ladders |
| Four properties versus one scalar | Reconcile the claimed four-property aggregation with a bug-only formula | Section 4 now explicitly states which properties the scalar omits |
| Claimed strongest property | Explain why specification-removal monotonicity predicts human agreement but is omitted | The current paper corrects the underlying mistake: the measured field is bug weak monotonicity; the main panel contains no specification-removal ladders |
| Perturbation validity | Describe operators, ladder lengths, and compilation checks | Current sources disclose malformed alpha probes and unvalidated transformations; operational detail still needs assessment |
| Human criterion | Distinguish one person's two rubric passes from independent annotators or a reliability ceiling | Current text makes this distinction and provides the uncertainty intervals |
| Sample size | Resolve 75 pairs versus 24 problems × 3 candidates | Current account: 75 rated pairs, one unresolved gold filename, 72 analyzed pairs; do not adopt the review's unsupported duplicate-pair explanation |
| Eight-configuration panels | Show whether association persists after removing broken controls; report uncertainty | Panel composition and Codex uncertainty are disclosed; functional-only discrimination and other families' uncertainty remain questions |
| Choice of scalar | Acknowledge that the geometric comparison has higher point correlations in two families | Current text does so and distinguishes its tuned weights from the fixed equal-weight index |
| Cross-pass tuning | State which weights were fitted, the objective, and the resulting weights | Current text identifies the six-component variant and pass1 weights; completeness of pass2 details needs assessment |
| Artifact-score threshold | Distinguish raw ranking from thresholded decisions and avoid claiming a proven optimum | Current appendix explains threshold-independent raw ranking; overlapping intervals merit a precise interpretation |
| Scoring scale | Reconcile integer 0–10 claims with prompts asking for floats in 0–1 | Current prompt appendix explicitly describes 0–1 output and the separate human 0–5 scale |
| Alpha-renaming | Reconcile score collapse with a deployment threshold; consider canonicalization | Current paper identifies malformed probes and labels its score-replacement proxy as post-hoc, not a validated input transformation |
| Downstream agent rankings | Fix same-model judging, uncertified evaluator, missing compiler outcomes, and unclear averaging | The old downstream table has been removed; the current paper makes no corresponding deployment result claim |
| Five-rater pool | Analyze the collected data and describe rater depth accurately | Current paper reports the changed rubric, low agreement with old labels, and negative screens; this pool is not a matched-rubric test |
| Formal baselines | Compare with proof attempts for equivalence or mutual implication | A relevant remaining scope clarification; failure to prove must not be called proof of inequivalence |
| Broader evaluation | Add benchmarks, multi-stage judges, matched-rubric independent labels, and a four-property matched baseline | These require new evidence; scope them as follow-up work instead of inventing current results |
| Computability | Fix the claim that Rice's theorem forces every individual specification to be incomplete | The obsolete discussion is absent from the built current manuscript |
| Tool architectures | Describe Dafny compilation and Verus's trusted components accurately | The old tool-comparison appendix is absent from the built manuscript |
| Presentation | Fix bibliography notes, citations, figure references, run codes, prompt splits, naming, and repeated prose | Many offending sections were removed; inspect surviving figures, citations, and prompt layout individually |

## Corrections to the feedback itself

- The historical `P3_weak_mono` field does not measure the proposed missing-specification property. Treating it as evidence for that property would recreate a corrected scientific error.
- Symbolic proof search is a meaningful baseline, but a timeout or unsuccessful tactic does not decide inequivalence.
- The attached equation's accents render over the variance names on page 4. A trailing-circumflex problem in extracted text is not proof of a typesetting defect.
- Ordinary line-end hyphenation should be judged from the rendered page, not repaired solely from copied text.
- A different-rubric annotation pool cannot establish transfer under the original human criterion.

## Implementation decision

Claude Fable recommends **YES_SELECTIVELY**: 16 already addressed, 8 removed, 12 apply, 3 requiring future evidence, and 2 rejected, across 41 issue rows (including two newly identified current-paper defects). See [the assessment](expt_v1/results/claude_fable_assessment.md) and [coordinator corrections](expt_v1/results/coordinator_decisions.md).

The approved repairs add statistical diagnostics from frozen vectors, clarify the threshold interpretation and search provenance, document probe and model details, clean the remaining figure and citations, and state the formal-baseline and prompt-scope limitations. Astra Ultra implemented these changes and the coordinator integrated them with the newer body rewrite; they do not provide a new independent test set or new benchmark evaluation.

## Source handling

The supplied paper and pasted review are retained unchanged in ignored local storage, with hashes in `expt_v1/input_manifest.json`. The pasted text loses some mathematical expressions; statements about equations are cross-checked against the supplied rendered paper and current source. The review is automated feedback, not a human-review verdict or an instruction source.
