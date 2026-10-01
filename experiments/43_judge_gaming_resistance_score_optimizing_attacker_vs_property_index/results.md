# Experiment 43 results: judge-gaming resistance against the label-free property index

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/results.md>

**TLDR:** After Amendment 1 (proof relaxation), the re-pilot passed both gates (Lean-valid 24/24 = 100%, judge parse 30/30 = 100%); the full run (6 judges × 15 items × 8 rounds) is running.

**Status:** RUNNING (started 09-30-2026 14:04 PDT; skampere1 tmux `cj-e43-gaming-resistance`, branch `e43-gaming-resistance`)
**Last updated:** 09-30-2026 18:05 PDT

| Step | Status | Evidence |
|---|---|---|
| Harness and offline tests (zero calls) | DONE (13 tests pass) | `scripts/`, `scripts/test_e43.py` |
| Protocol lock | DONE, commit 36476e9 | `PROTOCOL.md` |
| Wait gate: experiment 39 transport smoke passed | PASSED 09-30-2026 14:25 PDT (Sol 9/9, Sonnet 5 9/9, Luna 9/9, Opus 5.5 5/5 smokes measured) | `results/wait_gate.json` |
| Pilot (3 items × 2 judges × 4 iterations) | first pilot FAIL on the Lean gate: 7/24 = 29.2% valid (gate ≥ 60%), parse 13/13 = 100% (gate ≥ 95%), $2.36 Vals-reported; Amendment 1 (proof relaxation) → re-pilot `pilot_r1` PASS: Lean-valid 24/24 = 100% (16 after relaxation), parse 30/30 = 100%, $3.45 | `results/pilot.json`, `results/pilot_r1.json`, `results/analysis_pilot*.json` |
| Full run (6 judges × 15 items × 8 iterations) and reference scoring | RUNNING since 09-30-2026 16:03 PDT | `results/full/` |
| Analysis, report, landing | PENDING | `REPORT.md`, PR |

Checkpoint: [CKPT_gaming_resistance.md](CKPT_gaming_resistance.md).

## Full run, live (updated 09-30-2026 18:05 PDT)

| Round | Attempts | Attacker completions | Lean-valid (after proof relaxation) | Accepted |
|---|---|---|---|---|
| 1 | 90 | 90 | 77 (46) | 39 |
| 2 | 90 | 90 (7 after the one recovery pass) | 81 (39) | 24 |
| 3 | 90 | 90 | 78 (44) | 13 |
| 4 | 90 | 90 | 84 (54) | 12 |

Round 0 (attacked-judge score of each start): 88 calls measured (5 after the recovery pass) + 2 deterministic `D0` zeros (starts without theorems).

## Deviations and amendments

- 09-30-2026, before any call: the Lean-valid start rule needs a fifth repair stage (`S4_prune_failing_spec_and_tests`, deleting failing specification/test commands, never implementation) because the strict four-stage ladder yields only 12 eligible criterion items; with it, 20 are eligible and 15 are used (PROTOCOL.md section 3).
- 09-30-2026, after the first pilot: PROTOCOL.md Amendment 1, proof relaxation in the Lean guard (failing proofs → `by sorry`, statements byte-identical), then one re-pilot `pilot_r1`.

## Charges (Vals-reported, cumulative)

| Stage | Attacker | Judge (loop) | Rescore | Reference | Total |
|---|---|---|---|---|---|
| First pilot | $0.068 | $0.212 | $0.250 | $1.834 | $2.364 |
| Re-pilot (`pilot_r1`) | $0.059 | $0.510 | $0.279 | $2.604 | $3.452 |
