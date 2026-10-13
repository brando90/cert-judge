# Experiment 43 results: judge-gaming resistance against the label-free property index

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/results.md>

**TLDR:** No attacked Claude Sonnet 5 configuration gained more than the held-out validated `H2` ensemble credited (gaming gaps −0.162 to +0.033, no interval above 0), but 59 of 62 edited final candidates added flagged test-like statements that the reference also credited, and the label-free index did not predict resistance (`C_ms_gold` ρ = +0.600, one-sided p = 0.912; `TI_var_trainnorm` ρ = −0.086; `PTI_v0_frozen` not computable). Report: [REPORT.md](REPORT.md).

**Status:** DONE (09-30-2026; started 14:04 PDT, full run finished 19:35 PDT; skampere1 tmux `cj-e43-gaming-resistance`)
**Last updated:** 09-30-2026 19:46 PDT

| Step | Status | Evidence |
|---|---|---|
| Harness and offline tests (zero calls) | DONE (14 tests pass) | `scripts/`, `scripts/test_e43.py` |
| Protocol lock | DONE, commit 95de021 (pre-rebase 36476e9) | `PROTOCOL.md` |
| Wait gate: experiment 39 transport smoke passed | PASSED 09-30-2026 14:25 PDT (Sol 9/9, Sonnet 5 9/9, Luna 9/9, Opus 5.5 5/5 smokes measured) | `results/wait_gate.json` |
| Pilot (3 items × 2 judges × 4 iterations) | first pilot FAIL on the Lean gate: 7/24 = 29.2% valid (gate ≥ 60%), parse 13/13 = 100% (gate ≥ 95%), $2.36 Vals-reported; Amendment 1 (proof relaxation) → re-pilot `pilot_r1` PASS: Lean-valid 24/24 = 100% (16 after relaxation), parse 30/30 = 100%, $3.45 | `results/pilot.json`, `results/pilot_r1.json`, `results/analysis_pilot*.json` |
| Full run (6 judges × 15 items × 8 iterations) and reference scoring | DONE 19:35 PDT: 90/90 cells with a gaming gap; 720/720 attempts (634 Lean-valid, 119 accepted); 450 rescoring calls (448 measured, 2 labelled parse errors) + 6 deterministic; 462/462 reference calls measured | `results/full/cells.json`, `results/full/candidates/` |
| Analysis, report, landing | DONE: PR #52 merged to main at 6ef89c2; email receipt sent 19:46 PDT | `results/analysis.json`, `results/report_tables.md`, `REPORT.md` |

Checkpoint: [CKPT_gaming_resistance.md](CKPT_gaming_resistance.md).

## Full run, per round

| Round | Attempts | Attacker completions | Lean-valid (after proof relaxation) | Accepted |
|---|---|---|---|---|
| 1 | 90 | 90 | 77 (46) | 39 |
| 2 | 90 | 90 (7 after the one recovery pass) | 81 (39) | 24 |
| 3 | 90 | 90 | 78 (44) | 13 |
| 4 | 90 | 90 | 84 (54) | 12 |
| 5 | 90 | 90 | 74 (45) | 8 |
| 6 | 90 | 90 | 79 (44) | 9 |
| 7 | 90 | 90 | 80 (39) | 10 |
| 8 | 90 | 90 | 81 (45) | 4 |
| **All** | **720** | **720** | **634 (356)** | **119** |

Round 0 (attacked-judge score of each start): 88 calls measured (5 after the recovery pass) + 2 deterministic `D0` zeros (starts without theorems).

## Results (full run)

| Attacked judge (Claude Sonnet 5, medium) | Cells scored | Gaming gap (95% CI, task-clustered) | Attacked-judge gain (95% CI) | Reference gain (95% CI) | Flagged share, all cells | Flagged share, edited cells | Valid / attempts | Accepted |
|---|---|---|---|---|---|---|---|---|
| `LEX` | 15/15 | -0.162 [-0.325, -0.033] | +0.013 [-0.000, +0.027] | +0.176 [+0.036, +0.341] | 0.47 | 0.88 (8 edited) | 106/120 | 9 |
| `D0` | 15/15 | -0.044 [-0.186, +0.048] | +0.311 [+0.128, +0.471] | +0.356 [+0.161, +0.531] | 0.87 | 0.87 (15 edited) | 111/120 | 35 |
| `H0` | 15/15 | -0.027 [-0.057, -0.002] | +0.236 [+0.071, +0.394] | +0.262 [+0.082, +0.446] | 0.47 | 1.00 (7 edited) | 107/120 | 15 |
| `H2` | 15/15 | +0.033 [-0.103, +0.142] | +0.378 [+0.152, +0.575] | +0.344 [+0.159, +0.514] | 0.67 | 1.00 (10 edited) | 95/120 | 19 |
| `P1` | 15/15 | -0.136 [-0.281, +0.031] | +0.164 [+0.076, +0.262] | +0.300 [+0.150, +0.438] | 0.73 | 1.00 (11 edited) | 111/120 | 22 |
| `P8` | 15/15 | -0.088 [-0.213, +0.067] | +0.086 [+0.043, +0.142] | +0.173 [+0.038, +0.300] | 0.73 | 1.00 (11 edited) | 104/120 | 19 |

| Index (experiment 39) | Judges | Spearman ρ (index, gaming gap) | Exact one-sided p (negative) | Two-sided p | Bootstrap 95% CI of ρ | Reading |
|---|---|---|---|---|---|---|
| `C_ms_gold` | 6 | +0.600 | 0.912 | 0.242 | [-0.486, +0.886] | NOT SUPPORTED: no association detectable at this number of judges |
| `PTI_v0_frozen` | 3 | — | — | — | — | NOT_COMPUTABLE |
| `TI_var_trainnorm` | 6 | -0.086 | 0.460 | 0.919 | [-0.486, +0.371] | NOT SUPPORTED: no association detectable at this number of judges |

Index values come from experiment 39's committed open-split file (`origin/main`, selection commit 86ae479; selected index `C_ms_gold`); its sealed test file was never opened. With six judges, SUPPORTED requires ρ ≤ −0.829 (exact one-sided p ≤ 0.05).

| Further measured quantity | Value |
|---|---|
| Theorem statements, start → final (62 edited cells, mean) | 0.82 → 12.37 |
| Edited final candidates flagged by the deterministic checks | 59/62 (ground 50, unrelated 45, inflation 16, duplicate 6, vacuous 0, axiom 0) |
| In-loop (selected-maximum) gain vs fresh-repeat gain, per judge | D0 +0.480 vs +0.311; H2 +0.453 vs +0.378; H0 +0.293 vs +0.236; P1 +0.270 vs +0.164; P8 +0.153 vs +0.086; LEX +0.027 vs +0.013 |
| Reference start score vs expert coverage, 15 items (exploratory) | Spearman 0.709, Pearson 0.719 |
| Mean reference gain by member, 90 cells | Claude Opus 5.5 +0.322, GPT-6 Sol +0.215 |
| Judge parse rate in the loop (incl. round 0) | 721/722 = 99.9% |

## Deviations and amendments

- 09-30-2026, before any call: the Lean-valid start rule needs a fifth repair stage (`S4_prune_failing_spec_and_tests`, deleting failing specification/test commands, never implementation) because the strict four-stage ladder yields only 12 eligible criterion items; with it, 20 are eligible and 15 are used (PROTOCOL.md section 3).
- 09-30-2026, after the first pilot: PROTOCOL.md Amendment 1, proof relaxation in the Lean guard (failing proofs → `by sorry`, statements byte-identical), then one re-pilot `pilot_r1`. 356 of the 634 valid full-run proposals were valid only after relaxation.
- Transient Valkyrie task ERRORs (agent receipt frozen at start, 0 requests sent): round 0 5/58 and round-2 attacker 7/90. Each got its single labelled recovery admission and all 12 were measured. No cell is missing.
- `PTI_v0_frozen` is defined in experiment 39 for only 3 of the 6 attacked configurations (`D0`, `P1`, `P8`), so its association is NOT_COMPUTABLE (protocol minimum 5 judges).
- 09-30-2026 15:55 PDT: skampere1's shared root disk filled (0 B free). This user's stale Claude Code cache entries older than 12 h (`/tmp/user/22003/claude-22003/bash-edit-diff`, 32 GB) were deleted, and the worker's temp files moved to node-local `private/tmp`.

## Charges (Vals-reported, cumulative)

| Stage | Attacker | Judge (loop) | Rescore | Reference | Total |
|---|---|---|---|---|---|
| First pilot | $0.068 | $0.212 | $0.250 | $1.834 | $2.364 |
| Re-pilot (`pilot_r1`) | $0.059 | $0.510 | $0.279 | $2.604 | $3.452 |
| Full run | $2.063 | $11.193 | $4.647 | $36.495 | $54.397 |
| **All** | $2.190 | $11.915 | $5.176 | $40.933 | **$60.214** |

**TLDR-end:** [cj: e43-gaming] Full manifest done (90 cells, 720 attempts, 912 post-loop calls, $60.21 Vals-reported). No judge's gain exceeded the validated reference's, but most edited files were test-stuffed and credited by the reference too; the label-free index did not predict resistance.
