# Experiment 38: rewrite the ICLR 2027 paper body to the trust-artifact abstract

**TLDR:** The abstract of `paper_latex/ICLR_2027_submission/00_abstract.tex` (commit `c118d7c`, 09-25-2026) tells the paper's story: agents write their own trust artifacts, end-to-end autoformalization forces a language-model judge, the standard evidence for trusting that judge is per-judge human agreement, and we flip it to one human panel plus falsifiable property screens. The body (introduction through conclusion) still carried the earlier "test-oracle" framing, the word "certification", and prose written by several agents. This experiment rewrites every main-text section file to that story from the frozen evidence, without new inference or new numbers beyond deterministic recomputation from committed vectors.

## Goal and decision criterion

The consequential uncertainty is whether the body can carry the new abstract's claims with the evidence we have. It can if every sentence in sections 1–7 (a) follows the abstract's six moves, (b) uses the adopted vocabulary (trust artifact, intent, formal specification, validation, screen; never "certification" in prose), and (c) keeps every number traceable to a committed artifact. The check is deterministic: scratch build with zero errors, undefined references, and overfull boxes; main text at most 9 pages; sentence-layout check; banned-word greps; number provenance unchanged from experiment 34 plus the diagnostics script here.

## Inputs

- Story: `00_abstract.tex` at `c118d7c` (kept verbatim), `experiments/34_iclr_mega_rewrite_astra/ABSTRACT_MOTIVATION.md`, `msgs_sent_to_bots.md`, and Brando's handwritten note `notes/abstract_moves_1_2_handwritten_09-25-2026.jpg`.
- Evidence: the number-provenance table in `experiments/34_iclr_mega_rewrite_astra/REPORT.md` and the frozen artifacts it names under `experiments/archive/`.
- Pending repairs from experiment 37 (Claude Fable assessment `expt_v1/results/claude_fable_assessment.md`): the main-text items A1–A4, A8, A10–A12 are folded into this rewrite from my own recomputation (`analysis/exact_permutation_and_subsets.py`); the appendix items A5–A7, A9 are left to the Astra worker so its appendix hunks still apply.
- Rules: `CLAUDE.md` terminology, `~/agents-config/writing/ml_research/ml_research_writing.md`.

## Method

1. Read the abstract, the body, the ledgers, and the reviewer checklists; baseline scratch build (16 pages, 0 overfull).
2. Recompute the exp37 Tier-1 diagnostics from committed `judge_trust_vector.csv` files (`analysis/`); all nine rows agree with the assessment to three decimals.
3. Rewrite `01`–`07` section by section to the abstract's moves; append the diagnostics table to appendix `990`; add three verified bibliography entries (CheckList, metamorphic testing, BEq+).
4. Scratch build, layout and banned-word checks, rendered-page inspection; copy `main.pdf` back; commit with explicit pathspecs; push.

## Decisions (Trigger Rule 57, recorded here)

- **Abstract unchanged.** Brando approved it; the body follows it.
- **Rewrite on `main` while the experiment-37 Astra worker runs.** Its patch (branch `codex/paper-feedback`) will conflict in the main-text files; the numbers it derives are the same as `analysis/results/judge_level_diagnostics.csv`, so its main-text sentences are superseded by this rewrite and its appendix and figure work can be merged on top. Flagged to Brando in the session reply.
- **Appendix churn minimized.** Only appended material and label-preserving edits, so experiment 37's appendix hunks still apply.
- **"Certification" removed from prose**, including the Section 4 heading; "screen" is the property check, "validation" is the human-agreement evidence.

| Artifact | Purpose |
|---|---|
| `results.md` | Live results and phase status |
| `CKPT_rewrite.md` | Resumable checkpoint |
| `analysis/exact_permutation_and_subsets.py` | Deterministic judge-level diagnostics (exact permutation p, component-only and controls-excluded associations) |
| `analysis/results/judge_level_diagnostics.{csv,json}` | Its output with input hashes |
