# ICLR 2027 core manuscript rewrite

**Doc link:** <https://github.com/brando90/cert-judge/blob/astra/iclr-mega-rewrite/experiments/34_iclr_mega_rewrite_astra/results.md>

**Status:** RUNNING (started 09-22-2026 18:01 PDT)
**Last updated:** 09-22-2026 18:01 PDT

| Phase | Status | Evidence |
|---|---|---|
| Audit | IN PROGRESS | Binding rules, decision ledger, all four complaint files and current manuscript read; baseline PDF has 25 pages, References starts on page 8. |
| Outline and provenance | IN PROGRESS | Auditing numeric artifacts before rewriting. |
| Main text | PENDING | Target 8–9 pages, with one protocol claim. |
| Appendix archive | PENDING | Preserve removed source and unreferenced figures. |
| Statements and bibliography | PENDING | Anonymous reproducibility, ethics and provisional usage statements. |
| Verification and report | PENDING | Build, sentence layout, reference checks, provenance and rendered pages. |

## Scope and ownership

Worktree `/Users/brandomiranda/cert-judge-astra`, branch `astra/iclr-mega-rewrite`; root agent owns every manuscript edit and commit.
Short read-only subagent lookups cover artifact provenance and bibliographic verification; they do not run inference or edit the paper.
No provider calls, new experiments, credential reads, main-branch changes or merges are authorized.
The existing registration in `experiments/archive/layout.json` is correct; the layout check passes with eight active experiments.

## Audit findings

- The fourth review round is populated: all 55 complaint rows are in scope.
- The claim that inter-pass agreement bounds judge agreement is unsupported and will be removed.
- The protocol must disclose label-informed index, prompt, aggregation and threshold selection.
- Preliminary artifact lookup found that the current scatter coordinates use a different index from the equal-weight headline statistic. Resolving this is mandatory before drafting the result narrative.

**TLDR-end:** [cj: experiments/34_iclr_mega_rewrite_astra] Audit running on the isolated branch; baseline is 25 PDF pages with References on page 8. Numeric provenance is being reconciled before the rewrite.
