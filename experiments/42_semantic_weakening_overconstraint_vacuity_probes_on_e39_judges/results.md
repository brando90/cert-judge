# Experiment 42 results: semantic weakening, over-constraint and vacuity probes

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/results.md>

**TLDR:** Running on skampere1: 194 Lean-validated probes (24 identity anchors, 38 vacuity, 57 weakening, 37 over-constraint, 38 formatting over 24 tasks) are built and the protocol is locked; all 32,592 judge cells are scored ($656.15 Vals-reported); 15 of 56 LLM configurations pass the locked semantic screen; the index association waits for experiment 39's criterion.

**Status:** RUNNING (started 09-30-2026 14:06 PDT; skampere1 tmux `cj-e42-semantic-probes`, branch `e42-semantic-probes`; no judge call made yet)
**Last updated:** 09-30-2026 19:53 PDT

| Step | Status | Evidence |
|---|---|---|
| Probe construction and Lean validation (zero judge calls) | DONE 09-30-2026: 194 valid of 250 declared (ident 24/25, vac_true 19/25, vac_hyp 19/25, weak 57/75, overc 37/50, fmt_comments 19/25, fmt_layout 19/25) | `results/semantic_probe_manifest.json`, `probe_edits/` |
| Protocol lock | DONE 09-30-2026 (commit noted in `CKPT_semantic_probes.md`) | `PROTOCOL.md` |
| Wait gate: experiment 39 transport smoke passed | DONE 09-30-2026 (experiment 39 `origin/e39-proxy-index-search` 4ad11de: all 56 smokes measured, all 56 main runs admitted) | `private/GATE_OPEN` |
| Scoring through Valkyrie | DONE 09-30-2026 19:51 PDT: 56/56 configurations merged; 32,592/32,592 cells reconciled one-to-one (0 missing); measured 32,381 (99.35%), parse_error 209, model_error 2 after the single recovery_1 pass (45 recovery runs); Vals-reported charges $655.14 main + recovery, $1.01 smoke, **$656.15 total** | `results/judge_progress.json`, `results/harvest/` |
| Semantic screen (locked rule) | DONE: 16/60 configurations pass (15 LLM + the edit-distance control) | `results/semantic_screen.json`, `results/RESULTS_semantic_screen.md` |
| Index association with experiment 39's criterion | WAITING for experiment 39's committed `results/units_train_val.json` | `results/index_association.json` |
| Report, landing | PENDING | `REPORT.md`, PR |

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

## Charges and coverage per configuration (Vals-reported)

| Configuration | Selector | Measured | Parse error | Other | Recovered | Charges $ |
|---|---|---|---|---|---|---|
| `gem31h|D0` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 6 | 12.12 |
| `gem31h|R4` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 6 | 15.37 |
| `gem31h|H0` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 6 | 17.28 |
| `gem31h|H1` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 7 | 17.20 |
| `gem31h|H2` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 2 | 18.66 |
| `gem31h|P1` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 2 | 5.12 |
| `gem31h|P4` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 6 | 5.63 |
| `gem31h|P8` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 3 | 5.02 |
| `gem31h|LEX` | google/gemini-3.1-pro-preview | 582 | 0 | 0 | 4 | 6.24 |
| `luna6h|D0` | openai/gpt-6-luna-high | 582 | 0 | 0 | 2 | 0.40 |
| `luna6h|R4` | openai/gpt-6-luna-high | 582 | 0 | 0 | 1 | 0.46 |
| `luna6h|H0` | openai/gpt-6-luna-high | 582 | 0 | 0 | 2 | 0.50 |
| `luna6h|H1` | openai/gpt-6-luna-high | 582 | 0 | 0 | 0 | 0.49 |
| `luna6h|H2` | openai/gpt-6-luna-high | 582 | 0 | 0 | 0 | 0.48 |
| `luna6h|P1` | openai/gpt-6-luna-high | 580 | 2 | 0 | 3 | 0.18 |
| `luna6h|P4` | openai/gpt-6-luna-high | 582 | 0 | 0 | 1 | 0.27 |
| `luna6h|P8` | openai/gpt-6-luna-high | 579 | 3 | 0 | 1 | 0.16 |
| `luna6h|LEX` | openai/gpt-6-luna-high | 582 | 0 | 0 | 0 | 0.16 |
| `opus55x|H2` | anthropic/claude-opus-5-5-no-fallback | 582 | 0 | 0 | 0 | 61.71 |
| `opus55x|H0` | anthropic/claude-opus-5-5-no-fallback | 582 | 0 | 0 | 2 | 74.85 |
| `opus55x|D0` | anthropic/claude-opus-5-5-no-fallback | 582 | 0 | 0 | 0 | 50.05 |
| `opus55x|P4` | anthropic/claude-opus-5-5-no-fallback | 580 | 0 | 2 | 10 | 47.53 |
| `opus55x|LEX` | anthropic/claude-opus-5-5-no-fallback | 582 | 0 | 0 | 1 | 23.56 |
| `qwen36|D0` | alibaba/qwen3.6-27b | 574 | 8 | 0 | 3 | 5.08 |
| `qwen36|R4` | alibaba/qwen3.6-27b | 574 | 8 | 0 | 0 | 6.36 |
| `qwen36|H0` | alibaba/qwen3.6-27b | 565 | 17 | 0 | 1 | 5.94 |
| `qwen36|H1` | alibaba/qwen3.6-27b | 569 | 13 | 0 | 2 | 6.20 |
| `qwen36|H2` | alibaba/qwen3.6-27b | 549 | 33 | 0 | 1 | 6.63 |
| `qwen36|P1` | alibaba/qwen3.6-27b | 574 | 8 | 0 | 2 | 3.17 |
| `qwen36|P4` | alibaba/qwen3.6-27b | 575 | 7 | 0 | 2 | 3.61 |
| `qwen36|P8` | alibaba/qwen3.6-27b | 577 | 5 | 0 | 2 | 2.96 |
| `qwen36|LEX` | alibaba/qwen3.6-27b | 540 | 42 | 0 | 0 | 3.19 |
| `sol6h|D0` | openai/gpt-6-sol-high | 582 | 0 | 0 | 2 | 5.32 |
| `sol6h|R4` | openai/gpt-6-sol-high | 582 | 0 | 0 | 2 | 7.26 |
| `sol6h|H0` | openai/gpt-6-sol-high | 582 | 0 | 0 | 2 | 7.72 |
| `sol6h|H1` | openai/gpt-6-sol-high | 582 | 0 | 0 | 1 | 7.78 |
| `sol6h|H2` | openai/gpt-6-sol-high | 582 | 0 | 0 | 1 | 7.57 |
| `sol6h|P1` | openai/gpt-6-sol-high | 582 | 0 | 0 | 0 | 2.79 |
| `sol6h|P4` | openai/gpt-6-sol-high | 582 | 0 | 0 | 2 | 3.36 |
| `sol6h|P8` | openai/gpt-6-sol-high | 582 | 0 | 0 | 3 | 3.14 |
| `sol6h|LEX` | openai/gpt-6-sol-high | 582 | 0 | 0 | 0 | 3.33 |
| `sonnet5m|D0` | anthropic/claude-sonnet-5-medium | 582 | 0 | 0 | 4 | 12.67 |
| `sonnet5m|R4` | anthropic/claude-sonnet-5-medium | 576 | 6 | 0 | 0 | 15.88 |
| `sonnet5m|H0` | anthropic/claude-sonnet-5-medium | 579 | 3 | 0 | 3 | 15.90 |
| `sonnet5m|H1` | anthropic/claude-sonnet-5-medium | 580 | 2 | 0 | 0 | 14.70 |
| `sonnet5m|H2` | anthropic/claude-sonnet-5-medium | 561 | 21 | 0 | 2 | 16.45 |
| `sonnet5m|P1` | anthropic/claude-sonnet-5-medium | 582 | 0 | 0 | 3 | 6.19 |
| `sonnet5m|P4` | anthropic/claude-sonnet-5-medium | 582 | 0 | 0 | 1 | 6.34 |
| `sonnet5m|P8` | anthropic/claude-sonnet-5-medium | 582 | 0 | 0 | 2 | 6.21 |
| `sonnet5m|LEX` | anthropic/claude-sonnet-5-medium | 577 | 5 | 0 | 2 | 6.24 |
| `t2_luna|H2` | openai/gpt-6-luna-high | 580 | 2 | 0 | 15 | 1.38 |
| `t2_luna|D0` | openai/gpt-6-luna-high | 582 | 0 | 0 | 11 | 0.85 |
| `t2_qwen|H2` | alibaba/qwen3.6-27b | 561 | 21 | 0 | 6 | 20.56 |
| `t2_qwen|D0` | alibaba/qwen3.6-27b | 579 | 3 | 0 | 3 | 14.80 |
| `t2_sonnet5|H2` | anthropic/claude-sonnet-5-medium | 582 | 0 | 0 | 15 | 38.77 |
| `t2_sonnet5|D0` | anthropic/claude-sonnet-5-medium | 582 | 0 | 0 | 10 | 23.35 |
| **total** | | 32381 | 209 | | | **655.14** (+ 1.01 smoke) |

Per-configuration metrics with intervals: [results/RESULTS_semantic_screen.md](results/RESULTS_semantic_screen.md).

## Deviations and open questions for Brando

- 09-30-2026, before any call: the declared weakening check ("original implies weakened") is proved theorem by theorem; the file-level audit shows about half of the weakening and over-constraint probes leave the file's overall guarantee unchanged because the references restate the same property in separate theorems. The primary metrics keep every Lean-valid probe (as the README declares); the strict-only view is reported beside them.
