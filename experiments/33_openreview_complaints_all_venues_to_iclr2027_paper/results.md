# results.md — experiment 33 (OpenReview complaints → ICLR 2027 paper)

**Status:** RUNNING (started 09-22-2026 14:58 PDT)
**Last updated:** 09-22-2026 15:20 PDT

| Phase | Status | Evidence |
|---|---|---|
| 1. Locate every OpenReview forum | DONE | search API hits recorded in `reviews/fetch_attempts.md` (4 forums) |
| 2. Capture reviews verbatim | DONE for 3 venues; BLOCKED for DL4C | `reviews/*.md`; DL4C skeleton + 13 logged fetch attempts |
| 3. Ledger (one row per complaint) | DONE v1 | `complaints_ledger.md`: 14 `N25-*`, 3 `T26-*`, 29 `A26-*`, `D26-*` placeholders, 3 open items |
| 4. Prompts 01–04 | DONE | `prompts/` |
| 5. Paper edits E1–E9 | IN PROGRESS | see the per-edit table below |
| 6. DL4C ingestion + re-audit | PENDING (needs paste) | `prompts/03_…` |

## Ledger counts (v1, before edits)

| Status | Rows |
|---|---|
| Addressed | 15 |
| Disclosed | 9 |
| Partial → E# | 15 |
| Deferred | 6 |
| Superseded | 1 |
| Unknown (DL4C) | placeholders |

## Edits

| Edit | Landed? | Commit |
|---|---|---|
| E1 weak-monotonicity wording + cumulative-ladder sentence | pending | |
| E2 Fig. 1 "vs." → "w.r.t." | pending | |
| E3 Codex headline CIs / permutation p | pending | |
| E4 alpha canonicalization proxy (0.250 → 0.070) | pending | |
| E5 pre-registered screens disclosed (n=14 underpowered; n=32 verdict b) | pending | |
| E6 untested failure classes + Lean-only scope | pending | |
| E7 nine repeats, median (Codex panel) | pending | |
| E8 appendix agreement statistics on 72 overlapping pairs; MAE/MSE from the artifact | pending | |
| E9 refs.bib hygiene | pending | |

**TLDR-end:** [cj: or-complaints] Reviews from three of four OpenReview rounds are captured verbatim and every complaint has a ledger row with a status against the ICLR 2027 manuscript; the DL4C reviews need Brando's paste, and the nine paper edits are being applied next.
