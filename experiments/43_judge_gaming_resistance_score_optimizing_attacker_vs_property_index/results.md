# Experiment 43 results: judge-gaming resistance against the label-free property index

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/results.md>

**TLDR:** Protocol locked (commit 36476e9); experiment 39's transport smoke passed; pilot starting.

**Status:** RUNNING (started 09-30-2026 14:04 PDT; skampere1 tmux `cj-e43-gaming-resistance`, branch `e43-gaming-resistance`)
**Last updated:** 09-30-2026 14:25 PDT

| Step | Status | Evidence |
|---|---|---|
| Harness and offline tests (zero calls) | DONE (13 tests pass) | `scripts/`, `scripts/test_e43.py` |
| Protocol lock | DONE, commit 36476e9 | `PROTOCOL.md` |
| Wait gate: experiment 39 transport smoke passed | PASSED 09-30-2026 14:25 PDT (Sol 9/9, Sonnet 5 9/9, Luna 9/9, Opus 5.5 5/5 smokes measured) | `results/wait_gate.json` |
| Pilot (3 items × 2 judges × 4 iterations) | RUNNING | `results/pilot.json` |
| Full run (6 judges × 15 items × 8 iterations) and reference scoring | PENDING | `results/` |
| Analysis, report, landing | PENDING | `REPORT.md`, PR |

Checkpoint: [CKPT_gaming_resistance.md](CKPT_gaming_resistance.md).
