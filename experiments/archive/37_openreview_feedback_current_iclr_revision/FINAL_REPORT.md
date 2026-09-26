# Experiment 37: OpenReview feedback applied to the current manuscript

**TLDR:** Claude Fable recommended 12 selective repairs after comparing the old automated review with the current International Conference on Learning Representations (ICLR) 2027 paper. GPT-6 Astra at ultra reasoning implemented them; the coordinator merged the verified changes into the concurrent body rewrite at `fee0915`, preserving its newer prose. The integrated paper has 19 pages, with 9 pages of main text and no compilation errors, unresolved references, or overflowing text boxes.

## Feedback and decision

The review's main concerns were reproducibility of the index, control-driven correlations, invalid perturbations, optimistic validation, unsupported formal-methods claims, and presentation defects. Many concerns referred to removed or already corrected material in the old 28-page submission. The current analysis covers **41 issue rows: 12 apply, 16 already addressed, 8 removed, 3 future evidence, and 2 rejected**.

- [Feedback summary](FEEDBACK_SUMMARY.md)
- [Reusable agent prompt](PROMPT_fix_feedback.md)
- [Claude Fable assessment](expt_v1/results/claude_fable_assessment.md)
- [Current issue table](expt_v1/results/final_issue_table.md)
- [Detailed Astra implementation report](expt_v1/results/RESULTS_feedback_revision.md)

The consultation used `claude-fable-5-1` with maximum effort requested; the runtime confirmed that model and bypass-permissions mode. The implementation runtime confirmed `gpt-6-astra`, `ultra`, unrestricted filesystem access, and approval policy `never`. Both used authenticated local command-line clients.

## Repairs that matter

1. Added exact permutation probabilities, component-only comparisons, and true semantic-only subsets from frozen scores. The five-configuration subset removes random, edit distance, and the lexical negative control; the target-model subset contains three semantic prompts. The consultation's six/four subsets still contained the lexical control.
2. Clarified threshold uncertainty, the fitted-weight search, exact model identifiers, repeat counts, probe counts, and absent compilation checks. Script defaults are not asserted as recovered historical runtime settings.
3. Corrected the identity account: the identity summaries use four rewrites, while **24 unedited self-comparisons per configuration occur at bug-ladder level 0**.
4. Added the scope and limitations of symbolic comparison, kept unsuccessful proof search distinct from inequivalence, and scoped the single-call description to language-model configurations.
5. Replaced the expanded-panel figure's internal run codes with readable labels while preserving every coordinate, correlation, and interval. Repaired surviving citation constructions.

## Integration with the concurrent rewrite

Experiment 38 landed its main-text rewrite while Astra worked in an isolated checkout. The coordinator applied the evidence-backed repair content to that newer body rather than replacing it wholesale. The current abstract, introduction, related-work rewrite, conclusion, statements, bibliography, and `main.tex` remain byte-identical to `fee0915`. The appendix's overlapping diagnostic table was consolidated into one corrected table; both sets of reference labels resolve. The experiment-38 six/four-configuration calculations remain valid calculations for their stated membership, but they include the lexical control and are not used as the paper's semantic-only comparison.

The original Fable assessment and Astra phase reports are historical records of their input revisions. `build_receipt.json`, `visual_inspection.json`, and `verification.json` describe Astra's isolated deliverable; **`integration_receipt.json` describes the final combined paper**. The current issue table points to the integrated source.

## Verification

- 36/36 family × label-view × subset rows; all 72 index/component correlations independently reproduced with SciPy within absolute tolerance `1e-14`.
- 9/9 exact two-sided permutation probabilities independently reproduced; each enumerates 40,320 permutations. These are unadjusted descriptive tests on reused labels.
- 9,216/9,216 score rows audited; 96 saved component/index vectors reconstructed within absolute tolerance `1e-12`.
- The replacement figure preserves 13 points per panel, both correlations, and all four interval endpoints.
- The combined paper was compiled in a scratch copy and all 19 pages inspected. Main text ends on page 9; statements start on page 10. Zero errors, unresolved references/citations, question-mark placeholders, or overfull boxes. Non-fatal spacing/float warnings are retained in the receipt.
- Frozen source data and historical manuscripts remain unchanged. No new benchmark inference or human annotations were created.

| Family | Averaged-label Spearman correlation, five semantic configurations |
|---|---:|
| Codex | 0.900 |
| Claude Opus | 0.600 |
| Qwen3-Coder | 0.900 |
| Leanstral | -0.900 |

These five-observation associations do not establish precise discrimination or transfer. The negative Leanstral result is retained.

## Evidence still needed

Independent ratings under a matched rubric, a new benchmark, a symbolic-baseline comparison, valid canonicalization followed by new scoring, and structured multi-stage judges remain future work. The original annotation rubric, historical Opus/Qwen bootstrap intervals, and actual fitted-search seed/draw count remain unrecovered. No edit creates a test-set result or validates a unique threshold.

## Reproduction

On this laptop, the worker used the x86-64 Python package installation; reproduce it with `arch -x86_64 /usr/local/bin/python3`. The coordinator independently checked the numbers using the working native Python environment. No environment settings were changed.

The deterministic scripts under `expt_v1/scripts/` locate the repository independently of archive depth. `derive_diagnostics.py` reproduces the 36 rows; `plot_expanded_panel.py` preserves the frozen figure data; `write_dispositions.py` checks all 41 current-source anchors; `verify_integration.py` checks the integrated artifact and data hashes. `verify_revision.py` and `create_patch.py` are retained tools for the original isolated worker phase and require its original branch/base. The dispatch prompts and receipts retain their original paths as historical evidence. New model work requires a newly registered active experiment.

**TLDR-end:** [cert-judge: Experiment 37] The 12 worthwhile repairs are integrated and verified; all 41 feedback items have a disposition. The paper remains explicit about its missing independent evidence.

**Snapshot:**
```text
Issues: 41 = 12 apply + 16 addressed + 8 removed + 3 future + 2 reject
Diagnostics: 36 rows; 72 correlations; 9 exact permutation tests reproduced
Data audit: 9,216 / 9,216 rows
Integrated paper: 19 pages; main text 9 / 9; errors 0; unresolved 0
```
