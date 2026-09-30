# Experiment 43 results: judge-gaming resistance against the label-free property index

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/results.md>

**TLDR:** The first pilot failed its Lean-validity gate (7/24 = 29.2% < 60%; judge parse rate 100%), so PROTOCOL.md Amendment 1 adds proof relaxation to the Lean guard and the single re-pilot is running.

**Status:** RUNNING (started 09-30-2026 14:04 PDT; skampere1 tmux `cj-e43-gaming-resistance`, branch `e43-gaming-resistance`)
**Last updated:** 09-30-2026 15:13 PDT

| Step | Status | Evidence |
|---|---|---|
| Harness and offline tests (zero calls) | DONE (13 tests pass) | `scripts/`, `scripts/test_e43.py` |
| Protocol lock | DONE, commit 36476e9 | `PROTOCOL.md` |
| Wait gate: experiment 39 transport smoke passed | PASSED 09-30-2026 14:25 PDT (Sol 9/9, Sonnet 5 9/9, Luna 9/9, Opus 5.5 5/5 smokes measured) | `results/wait_gate.json` |
| Pilot (3 items × 2 judges × 4 iterations) | first pilot FAIL on the Lean gate: 7/24 = 29.2% valid (gate ≥ 60%), parse 13/13 = 100% (gate ≥ 95%), $2.36 Vals-reported; Amendment 1 (proof relaxation) → re-pilot `pilot_r1` RUNNING | `results/pilot.json`, `results/pilot_r1.json` |
| Full run (6 judges × 15 items × 8 iterations) and reference scoring | PENDING | `results/` |
| Analysis, report, landing | PENDING | `REPORT.md`, PR |

Checkpoint: [CKPT_gaming_resistance.md](CKPT_gaming_resistance.md).

## Deviations and amendments

- 09-30-2026, before any call: the Lean-valid start rule needs a fifth repair stage (`S4_prune_failing_spec_and_tests`, deleting failing specification/test commands, never implementation) because the strict four-stage ladder yields only 12 eligible criterion items; with it, 20 are eligible and 15 are used (PROTOCOL.md section 3).
- 09-30-2026, after the first pilot: PROTOCOL.md Amendment 1, proof relaxation in the Lean guard (failing proofs → `by sorry`, statements byte-identical), then one re-pilot `pilot_r1`.

## Charges (Vals-reported, cumulative)

| Stage | Attacker | Judge (loop) | Rescore | Reference | Total |
|---|---|---|---|---|---|
| First pilot | $0.068 | $0.212 | $0.250 | $1.834 | $2.364 |
