# Which other Lean benchmarks can host the probes

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/55_lean_benchmark_probe_structural_screen/RESULTS_structural_screen.md>

**TLDR:** CLEVER can host specification removal and alpha-renaming on 161 of 161 files, and a real implementation for a bug ladder on 44 of 161. miniCodeProps can host specification removal and alpha-renaming on its 201 property theorems and has no per-task implementation. FVAPPS tasks are not in the GitHub checkout. No model calls, and no file was elaborated.

## Counts

A family is supported when at least 80 percent of the benchmark's task units have the ingredient. Commits are the shallow clones measured on 10-18-2026.

| Benchmark | Units | Specification removal | Bug ladder | Alpha-renaming | Toolchain |
|---|---:|---|---|---|---|
| CLEVER | 161 | 161/161, supported | 44/161 (0.273), not supported | 161/161, supported | leanprover/lean4:v4.27.0 |
| miniCodeProps | 201 | 201/201, supported | 0/201, not supported | 200/201 (0.995), supported | leanprover/lean4:v4.9.0 |
| FVAPPS | 0 in git | not measured | not measured | not measured | leanprover/lean4:v4.12.0 |

CLEVER implementations are `sorry` in 117 of 161 files and a real body in 44. That matches the 09-22-2026 expectation of at most about 44 bug ladders. miniCodeProps is not alpha-only: each task is one theorem, so specification removal is supported too. Its programs sit in 7 shared Lean files, so there is no per-task implementation to mutate. FVAPPS publishes the tasks as the Hugging Face dataset `quinn-dougherty/fvapps`; this checkout has scaffolding only, so the expectation that it supports specification removal only is not measured here.

None of the three pinned toolchains is installed (this machine has Lean v4.18.0, v4.22.0, and v4.24.0). Elaboration is not measured.

Receipt: `results/structural_counts.json`.

**TLDR-end:** [cert-judge: lean benchmark structural screen] CLEVER supports specification removal and alpha-renaming on 161/161 files and a bug ladder on 44/161; miniCodeProps supports the first two on 201 theorems and has no per-task implementation; FVAPPS tasks are not in the checkout.
