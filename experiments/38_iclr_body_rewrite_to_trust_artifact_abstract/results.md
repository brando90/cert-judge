# Experiment 38: live results

**Status:** COMPLETE (started 09-26-2026 12:20 PDT; verified 09-26-2026 13:20 PDT)
**Last updated:** 09-26-2026 13:20 PDT

| Phase | Status | Evidence |
|---|---|---|
| Read story, body, ledgers; baseline build | DONE | Scratch build of `32c7a23`: exit 0, 16 pages, 0 overfull |
| Deterministic diagnostics | DONE | `analysis/results/judge_level_diagnostics.csv`: nine rows match the experiment-37 assessment to three decimals |
| Rewrite sections 1–7 | DONE | `01`–`07` rewritten to the abstract's six moves; `990` gains the diagnostics table; `08` gains one sentence; three verified bibliography entries |
| Verification | DONE | Scratch `latexmk`: exit 0; 19 pages; 0 overfull, 0 undefined references or citations, 0 `??`, 0 BibTeX warnings; conclusion ends on page 9 with 32 free lines; statements and references start on page 10; appendix on page 13; sentence-layout check passes; banned-word grep clean (`certif*`, `calibrat*`, development set, predict, DSPy, Trace+, Claude 3.7, PTI, AI-tell words) |
| Rendered pages | DONE | Pages 1, 3, 4, 6, 7, 16 inspected at low resolution: no clipping or overlap |
| Form abstract | DONE | Abstract unchanged; generator output byte-identical to `experiments/33b_or_ledger/openreview_form_abstract.txt` |
| Commit and push | DONE | See the commit on `main` referenced in the checkpoint |

## What changed

- **Story.** Every section now follows the abstract: trust artifacts (Section 1 and 3), the end-to-end autoformalization instance and the two matching questions (Section 1), the per-judge human-validation assumption (Sections 1 and 2), the flip to one panel plus falsifiable properties (Sections 1 and 4), the Lean instantiation with the smooth-conjunction index (Section 4), the validation-set evidence and the lexical judge (Section 5, with a new subsection "Human agreement alone can miss a bad judge"), and the vision closing (Section 7).
- **Vocabulary.** "Certification" is gone from prose, including the old Section 4 heading; "screen" names the property checks, "validation" the human-agreement evidence; P1 covers identity and meaning-preserving rewrites, P4 repeat stability, matching the archived `ident` and `stab` fields.
- **Related work.** New paragraph on behavioral tests with a known direction (metamorphic testing, CheckList), with the paper's properties framed as metamorphic relations on the judge; `\citet` fixes for the two duplicated author names.
- **Experiment-37 main-text repairs folded in** from my recomputation: exact permutation probabilities for Opus and Qwen (A1), controls-excluded and same-model associations (A2), bug-component-only association (A3), threshold-interval overlap (A4), `\citet` (A8), the BEq+ scope sentences (A10), the single-call-prompt limitation (A11), and how P1 was measured (A12). Appendix items A5–A7 and A9 are left to the Astra worker.
- **Numbers.** No frozen number changed. New numbers come only from `analysis/exact_permutation_and_subsets.py` over committed `judge_trust_vector.csv` files (input hashes in `analysis/results/judge_level_diagnostics.json`).

## Final artifact

- `paper_latex/ICLR_2027_submission/main.pdf`: 19 pages, SHA-256 `7078029fe6eb8f1a60bb405fe19218c9f151f991a0e321f0f8c2fd240a121d41`.

**TLDR-end:** [cj: exp38 body rewrite] The ICLR body now follows the approved abstract end to end, builds clean at 19 pages with the main text ending on page 9, and every new number is a deterministic recomputation from committed vectors.
