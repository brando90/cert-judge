# Experiment 38: rewrite checkpoint

**TLDR:** Body rewrite to the approved abstract is complete, verified, and pushed; only the experiment-37 appendix/figure merge remains, owned by that experiment's coordinator.

Created: 09-26-2026 12:55 PDT
Last updated: 09-26-2026 13:20 PDT

- Base commit on `main`: `32c7a23`; abstract unchanged from `c118d7c`.
- Rewritten: `01`–`07`; appended: `990` (judge-level diagnostics table); one sentence in `08`; `refs.bib` gains `ribeiro2020checklist`, `chen1998metamorphic`, `poiroux2025beq` (metadata verified against the ACL Anthology and the arXiv API on 09-26-2026).
- Verification: see `results.md`; PDF SHA-256 `7078029f…121d41`, 19 pages, main text ends on page 9.
- Experiment 37's Astra worker (branch `codex/paper-feedback`) started from `f73228a`; its main-text hunks are superseded by this rewrite (same numbers, from `analysis/results/judge_level_diagnostics.csv`); merge only its appendix items A5–A7, its regenerated figure (A9), and its diagnostics scripts.
- Next (if resumed): re-run the layout check and a scratch build after any merge; never `latexmk` in the paper directory.
