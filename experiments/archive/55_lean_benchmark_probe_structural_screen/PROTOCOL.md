# Structural screen of three other Lean benchmarks

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/55_lean_benchmark_probe_structural_screen/PROTOCOL.md>

**TLDR:** Zero-spend check of whether CLEVER, FVAPPS, and miniCodeProps have the ingredients for the paper's probes. No model calls. Scoring stays blocked by the Vals spend pause.

## Question

Which of these three benchmarks can carry a bug ladder (needs a real implementation), a specification-removal ladder (needs a theorem or specification definition), and an alpha-renaming probe (needs a binder on that specification)?

## Rule, locked before the counts

A Lean file supports specification removal if it contains a `theorem` or a `def` whose type ends in `Prop`. It supports a bug ladder if it contains a non-`Prop` `def` whose body is not `sorry`. It supports alpha-renaming if a supported specification declaration has an explicit binder. A benchmark supports a probe family when at least 80 percent of its `.lean` files support that family. Toolchain elaboration is attempted on one file per benchmark and recorded; a failed install is a result, not a dropped benchmark.

The 09-22-2026 expectations being remeasured: CLEVER supports specification removal and alpha on nearly all 161 problems and bug ladders on at most about 44; FVAPPS supports specification removal only; miniCodeProps supports alpha only.
