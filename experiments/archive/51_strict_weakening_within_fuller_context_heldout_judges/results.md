# Strict weakening within fuller-context judges

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/results.md>

**Status:** DONE (2026-10-18T20:59:14.052754+00:00)

**Last updated:** 10-18-2026

| Phase | State | Result |
|---|---|---|
| Protocol locked | DONE | Gate Spearman ≥ 0.45 and one-sided p-val < 0.05; fuller-context test judges |
| Reproduction of the registered deletion-score test | PASS | tolerance 1e-09 |
| Primary association | DONE | REVERSED: Spearman -0.324 [-0.761, 0.045] p-val=0.8656 on 12 configurations |

Report: [RESULTS_strict_within_family.md](RESULTS_strict_within_family.md). Inputs: `results/input_manifest.json`. Pairs: `results/primary_pairs.json`.

No model calls. No set-N sheets.

**TLDR-end:** [cert-judge: strict weakening within fuller-context judges] REVERSED on 12 held-out fuller-context configurations, Spearman -0.324 [-0.761, 0.045] p-val=0.8656.
