# Experiment 54 — PROTOCOL (LOCKED before any structural number is computed)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/54_wave1_pinned_candidates_vs_may_rated_pool_structural_screen/PROTOCOL.md>

**TLDR:** Do the 124 pinned wave-1 candidate files sit inside the 75-file May rated pool on experiment 110's file-side structural criteria? No model calls. Judge-side criteria are not computed.

Written 10-18-2026 19:25 PDT, before any criterion value for these 124 files was computed.

## Question

The rating pool will ask humans to rate these files. Experiment 110's rule says a file set is in-distribution on a criterion when its median lies in the pool's 5th–95th percentile and at least 70% of its files do too. The planning simulation says rank agreement collapses if files bunch at full coverage. This experiment asks the prior question that does not need ratings: are these files structurally like the May pool?

## Inputs

- Wave 1: the 124 files in `freeze/CANDIDATE_PIN_10-18-2026.json` whose `collected_sha256` matches `solution.lean` on skampere3. The missing Mistral cell stays missing and is not imputed.
- Pool: the 75 candidates in VeriBench experiment 100 `inputs/items.jsonl`, with the annotation-era reference and Python.
- Extractor: VeriBench experiment 110 `scripts/extract_criteria.py` `features`, unchanged. File-side criteria C1–C13 only. J1 and J2 are unavailable (no judge scores on the wave-1 files).

## Rule (inherited, not refit)

A criterion is in-distribution when the wave-1 median lies in the pool interval [P5, P95] (NumPy percentile, linear / type 7) and at least 0.70 of wave-1 files lie in that interval. If P5 equals P95, the interval is [min, max]. Sensitivity at 0.60 and 0.80 is reported beside the primary count. Source: experiment 110 `CRITERIA.md` § 4. The 0.70 coverage cut is that document's convention.

## Headline

The count of C1–C13 that are in-distribution, out of 13, with a 95% task-cluster bootstrap (wave-1 tasks resampled, pool fixed; 10,000 draws, seed 54). p-val=n/a. Per-generator counts are descriptive.

## Stop

No judge calls. A structural shift does not change the 0.45 gate or the accept threshold.
