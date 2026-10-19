# Wave-1 candidates versus the May rated pool

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/54_wave1_pinned_candidates_vs_may_rated_pool_structural_screen/RESULTS_wave1_structure.md>

**TLDR:** On experiment 110's file-side criteria, 7 of 13 are in-distribution for the 124 pinned wave-1 files against the 75 May rated files. A task-cluster bootstrap of that count is [5, 8] (10,000 draws, seed 54, pool fixed, p-val=n/a). The shifts are size, test count, and sorry rate: wave-1 files are longer, state more theorems, carry far more executable tests, and almost never use `sorry`.

Rule, inherited from experiment 110: in-distribution means the wave-1 median lies in the May pool's [P5, P95] and at least 0.70 of wave-1 files do too. J1 and J2 are unavailable (no judge scores). The missing Mistral file is not imputed. No model calls.

| Criterion | Wave-1 median | May pool [P5, P95] | Fraction of wave-1 files inside | Reading |
|---|---:|---|---:|---|
| C1 file length (non-blank lines) | 211.500 | [21.700, 105.600] | 0.16 | shift |
| C2 definitions | 15.000 | [3.000, 13.600] | 0.46 | shift |
| C3 theorem and lemma statements | 11.000 | [1.000, 4.000] | 0.04 | shift |
| C4 median statement length | 17.000 | [14.000, 56.900] | 0.71 | in-distribution |
| C5 fraction quantified | 1.000 | [0.500, 1.000] (degenerate pool; interval is min to max) | 0.96 | in-distribution |
| C6 fraction conditional | 0.106 | [0.000, 1.000] | 1.00 | in-distribution |
| C7 fraction ground-instance | 0.000 | [0.000, 0.500] (degenerate pool; interval is min to max) | 0.97 | in-distribution |
| C8 pre/post scaffold (0-3) | 1.000 | [0.000, 3.000] | 1.00 | in-distribution |
| C9 executable tests | 34.000 | [0.000, 6.600] | 0.01 | shift |
| C10 sorry rate | 0.000 | [0.617, 1.000] | 0.02 | shift |
| C11 main-function focus | 0.167 | [0.000, 1.000] | 1.00 | in-distribution |
| C12 lexical overlap with the reference | 0.226 | [0.000, 0.273] | 0.61 | shift |
| C13 statement-count ratio, log2 | 0.335 | [-2.935, 1.000] | 0.75 | in-distribution |

Sensitivity of the 0.70 coverage cut: at 0.60 the in-distribution count is 8; at 0.80 it is 5. The primary count stays 7.

Per generator (descriptive, same rule, that generator's files only):

| Generator | Files | Criteria in-distribution |
|---|---:|---:|
| `t2_astra` | 25 | 6 / 13 |
| `t2_fable51` | 25 | 5 / 13 |
| `t2_glm` | 25 | 7 / 13 |
| `t2_kimik3` | 25 | 7 / 13 |
| `t2_mistral` | 24 | 8 / 13 |

The May pool's sorry rate sits high because those candidates were proof-light. The wave-1 median sorry rate is 0, and only 0.02 of those files fall in the pool interval. Statement count and executable tests move the other way: medians 11 and 34, against pool intervals that top out at 4 and 6.6.
