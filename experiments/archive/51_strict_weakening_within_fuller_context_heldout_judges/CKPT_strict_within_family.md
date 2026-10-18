# Checkpoint: strict weakening within fuller-context judges

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/CKPT_strict_within_family.md>

Created: 10-18-2026 09:06 PDT
Last updated: 10-18-2026 09:14 PDT

## State

1. **Goal** — test whether experiment 42's strict weakening accuracy meets the 0.45 / p-val < 0.05 gate on fuller-context held-out judges.
2. **Now** — done. Reading REVERSED. Archived after the verdict.
3. **Results** — Spearman −0.324 [−0.761, 0.045] p-val=0.8656 on 12 test configurations; 10/12 scores are exactly 1. Validation descriptive pass does not replace the test.
4. **Blocked** — nothing. Zero inference.
5. **Next** — stop fitting new scores on this cache. The December path is the fixed human-style rubric and the ratings already being collected.

## Log

- 10-18-2026 09:06 PDT: Locked the question, population, gate and stop rule in PROTOCOL.md before joining the cached scores.
- 10-18-2026 09:14 PDT: Reproduction of experiment 39's registered test passed. Primary reading REVERSED. Archived.
