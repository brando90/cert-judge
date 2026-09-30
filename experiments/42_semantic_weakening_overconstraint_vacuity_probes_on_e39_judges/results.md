# Experiment 42 results: semantic weakening, over-constraint and vacuity probes

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/results.md>

**TLDR:** Running on skampere1: 194 Lean-validated probes (24 identity anchors, 38 vacuity, 57 weakening, 37 over-constraint, 38 formatting over 24 tasks) are built and the protocol is locked; judging (56 configurations × 582 cells = 32,592 Valkyrie calls) is next; no judge call made yet.

**Status:** RUNNING (started 09-30-2026 14:06 PDT; skampere1 tmux `cj-e42-semantic-probes`, branch `e42-semantic-probes`; no judge call made yet)
**Last updated:** 09-30-2026 15:21 PDT

| Step | Status | Evidence |
|---|---|---|
| Probe construction and Lean validation (zero judge calls) | DONE 09-30-2026: 194 valid of 250 declared (ident 24/25, vac_true 19/25, vac_hyp 19/25, weak 57/75, overc 37/50, fmt_comments 19/25, fmt_layout 19/25) | `results/semantic_probe_manifest.json`, `probe_edits/` |
| Protocol lock | DONE 09-30-2026 (commit noted in `CKPT_semantic_probes.md`) | `PROTOCOL.md` |
| Wait gate: experiment 39 transport smoke passed | PENDING | experiment 39 `results.md` |
| Scoring through Valkyrie | PENDING | `results/harvest/` |
| Analysis, report, landing | PENDING | `REPORT.md`, PR |

## Probe construction (step 2, zero judge calls)

| Kind | Valid / declared | Invalid reasons (count) |
|---|---|---|
| `ident` (reference as its own candidate) | 24 / 25 | reference `1_MyAdd` does not elaborate (1) |
| `vac_true` (every theorem statement → `True`) | 19 / 25 | proved equivalent: `*_safe` references are already `Post := True` (5); no anchor (1) |
| `vac_hyp` (premises kept, conclusion `True`) | 19 / 25 | same as `vac_true` (5 + 1) |
| `weak` L1–L3 (cumulative, Lean-proved reference ⇒ probe) | 57 / 75 | no weakening possible for the 5 `*_safe` tasks (15); no anchor (3) |
| `overc` L1–L2 (unsatisfiable hypothesis, Lean-proved) | 37 / 50 | no eligible binder (5: the `*_safe` tasks); L2 would equal L1 (6); no anchor (2) |
| `fmt_comments` / `fmt_layout` (identical `#print` of every declaration) | 19 / 25 each | nothing to change in the 7-line `*_safe` files (5 each); no anchor (1 each) |

- Weakening edits were proposed by Claude Code subagents (claude-opus-5-5, subscription) under `probe_edits/PROPOSER_BRIEF.md` and entered only through the Lean checks; 0 of 57 levels proved equivalent.
- File-level audit (pre-registered sensitivity, `probe_edits/audit/`): weakening 25 strict / 31 redundant / 1 unclear; over-constraint 20 strict / 16 redundant / 1 unclear. Redundant = another unchanged theorem of the same file restates what was dropped.
- Findings recorded before any call: the `18_MyFibonacci` reference is self-contradictory (`fibonacci_increasing_thm` at n = 1 conflicts with F0 = 0 and the recurrence); `humaneval_13__gcd`'s `maximality_thm` is false at a = b = 0 (both `sorry`-proved in the reference).

## Deviations and open questions for Brando

- 09-30-2026, before any call: the declared weakening check ("original implies weakened") is proved theorem by theorem; the file-level audit shows about half of the weakening and over-constraint probes leave the file's overall guarantee unchanged because the references restate the same property in separate theorems. The primary metrics keep every Lean-valid probe (as the README declares); the strict-only view is reported beside them.
