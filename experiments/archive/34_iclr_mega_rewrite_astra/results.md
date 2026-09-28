# ICLR 2027 core manuscript rewrite

**Doc link:** <https://github.com/brando90/cert-judge/blob/astra/iclr-mega-rewrite/experiments/34_iclr_mega_rewrite_astra/results.md>

**Status:** COMPLETE (started 09-22-2026 18:01 PDT; completed 09-22-2026 21:39 PDT; awaiting Brando’s branch review)
**Last updated:** 09-22-2026 21:39 PDT

| Phase | Status | Evidence |
|---|---|---|
| Audit | DONE | Binding rules, decision ledger, all four complaint files and current manuscript read; baseline PDF has 25 pages, References starts on page 8. |
| Outline and provenance | DONE | `outline.md`; mandatory corrections below. |
| Main text | DONE | Eight pages; one protocol proposal, corrected fixed-index evidence and explicit coverage limits. |
| Appendix archive | DONE | Six cited sections; original source and 19 inherited figures preserved under archive/. |
| Statements and bibliography | DONE | Three statements, nineteen complete cited entries; usage facts await author confirmation. |
| Verification and report | DONE | Build and visual review complete; main 8/total 17 pages; References 9; zero overfull boxes, undefined references or citations; zero BibTeX warnings; 75 numeric lines and all 55 complaints indexed. |

## Scope and ownership

Worktree `/Users/brandomiranda/cert-judge-astra`, branch `astra/iclr-mega-rewrite`; root agent owns every manuscript edit and commit.
Short read-only subagent lookups cover artifact provenance and bibliographic verification; they do not run inference or edit the paper.
No provider calls, new experiments, credential reads, main-branch changes or merges are authorized.
The existing registration in `experiments/archive/layout.json` is correct; the layout check passes with eight active experiments.

## Audit findings

- The fourth review round is populated: all 55 complaint rows are in scope.
- The claim that inter-pass agreement bounds judge agreement is unsupported and will be removed.
- The protocol must disclose label-informed index, prompt, aggregation and threshold selection.
- The original scatter/table used an unequal six-weight index, but captions reported equal-weight correlations. Coordinates and the configuration table have been rebuilt from canonical committed vectors.

- Canonical Qwen pass2 is 0.857, not the inherited 0.905.
- The archived per-property P3 field is bug weak monotonicity, not missing-specification monotonicity; no P3 rows exist in the eight-configuration panel.
- The geometric comparison uses pass1-selected weights (0.4, 0.6), not an untuned equal-weight baseline.
- The old 184-file figure mixes model scores with 34 heuristic-scored additions. It is archived, not reported as a pure model study.
- Historical ALPHA probes can duplicate `:=` and rename signatures without updating proof bodies. The new manuscript explicitly says their score drops cannot establish failure on valid alpha-renaming.
- Canonical lexical and edit-distance index scores remain high. The failure diagnostics, not an index cutoff, identify local reversals.
- A local 12-triple weight grid, using committed vectors only, preserves positive associations. Average-label ranges: Codex 0.738–0.857, Opus 0.643–0.714, Qwen 0.881–0.976.
- Preserved Leanstral negative evidence; no leave-one-family-out transfer claim is made.

**TLDR-end:** [cj: experiments/34_iclr_mega_rewrite_astra] Audit complete; the rewrite corrects mixed indices, a mislabeled property, and invalid alpha probes. Main text, reduced appendix, statements and report are written; the main rewrite is pushed at `23b9773`; the regenerated appendix diagnostics also pass the final build and data checks.

Final visual cross-check found a stale reversal PNG. Its canonical CSV agrees with the corrected main table; the diagnostic images were regenerated from committed rows, with originals preserved.

Final PDF SHA-256: `9c7fe1dd00939294cf37c6ad70cd83c186f5a7f6228f8914ea8eaf3e7a8b2b0a`. All 55 complaint IDs are covered; 75 numeric source lines map to 14 evidence groups. The source/figure milestone is `23b9773`; the final correction and handoff commit follows it. No judge inference, key access, new experiment, main-branch edit, or merge occurred.

**Coordinator verification (main, 2026-09-24):** independent scratch build of the branch at `b9ee320`: latexmk exit 0, 0 errors / undefined / overfull / BibTeX warnings, 17 pages, References p. 9. Merged into `main` on Brando's instruction; title changed to candidate 2 in the follow-up commit.
