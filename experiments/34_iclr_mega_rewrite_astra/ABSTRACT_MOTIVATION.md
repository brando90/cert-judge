# Abstract motivation: independent code formalizations

Created: 09-25-2026

## Adopted opening

> Correct end-to-end code autoformalizations need not share a reference's interfaces or theorem statements, motivating validated language-model judges to assess their guarantees.

Scope: change only the abstract's opening sentence and its explanatory source comment, then align the introduction's motivation and cite VeriBench there, not in the abstract. Preserve all other abstract claims and numbers.

## Evidence and claim boundaries

- VeriBench's current manuscript, `paper_latex/ICLR_2027_VeriBench/03_veribench.tex` in the sibling VeriBench repository, defines the Python-to-Lean task as joint generation of implementations, tests, formal statements, and proofs. Its schema does not require the reference's exact theorem decomposition.
- The same manuscript's `04_eval_metric.tex` records representation mismatches as a source of false negatives when applying reference tests and statements directly to generated code. Its coverage judge estimates coverage; it does not prove implications, and the deployed judge is not described as having passed its human-agreement gate.
- The sibling repository's `experiments/98_literature_review_test_generation_correctness/RESULTS_test_quality_taxonomy.md`, especially its joint-artifact comparison and semantic-alignment discussion, supports the distinction between shared-interface testing and evaluation across independently generated representations.
- Execution-based specification evaluation does exist: [nl2postcond, Section 2.1](https://arxiv.org/html/2310.01831) tests generated postconditions on reference and buggy executions. The revised opening therefore does not dismiss tests as incapable of supplying correctness evidence.
- Semantic comparison is the unmet evaluation step; language-model judging is one practical empirical strategy. Independently validated adapters, formal correspondence proofs, or human review remain alternatives. No claim is made that every other benchmark fixes signatures, every signature is acceptable, or VeriBench has universal novelty priority.
- The existing VeriBench bibliography entry is cited in third person in the introduction. No claim is added that the deployed VeriBench judge has already been validated successfully.

## Alternate openings considered

1. End-to-end code autoformalization can express the same guarantees through different interfaces and theorem statements, making semantic evaluation essential.
2. Correct autoformalizations need not resemble their references, so language-model judges must assess guarantees across different interfaces and theorem statements.

The adopted sentence names the concrete mismatch and the validation requirement together, without implying that a language-model judge is logically indispensable.

## Verification

- Opening: one sentence, 21 whitespace-separated words; no abstract citation. The remaining eight abstract sentences are unchanged.
- Source layout: `latex_sentence_lines.py --check` passed for both edited section files (exit 0).
- Scratch compilation: `latexmk -pdf -interaction=nonstopmode -halt-on-error` passed (exit 0), producing 16 pages.
- Final compilation log: zero TeX errors, undefined references/citations, and overfull boxes. Existing underfull-box notices remain.
- Rendered pages 1 and 2 inspected: opening, introduction, citation, and section transition are legible without clipping or overlap.
- `git diff --check` passed; exact source diff reviewed. No empirical results or judge settings changed.

OpenReview is not updated by this source edit; any earlier upload remains a separate submission artifact.
