# Breadth screen: which other Lean 4 benchmarks can carry the judge probes? (CLEVER, FVAPPS, miniCodeProps)

**TLDR:** A zero-spend structural screen that tries to build the paper's gold-derived probes on three more Lean 4 benchmarks and counts how many probes are valid per property. It turns "why not benchmark X?" into a table: which benchmarks support which properties, and why the others do not. It runs no model calls.

**Execution:** DEFERRED — NOT RUN · **Paper inclusion:** UNDECIDED · **Priority:** 3 of 5 · **Recorded:** 09-22-2026 · **Issue:** <https://github.com/brando90/cert-judge/issues/45> · **Prompt:** [cc.md](cc.md)

**Would become:** `experiments/<NN>_lean_benchmark_probe_structural_screen/`.

## Hypothesis

- CLEVER supports the specification-removal and alpha probes on nearly all 161 problems, but bug ladders on at most about 44, because 117 of 161 reference implementations are `sorry`.
- FVAPPS supports specification-removal only, since there is no Lean reference implementation.
- miniCodeProps supports alpha only, since it is a proof-only task on fixed programs.

## Benchmarks (facts checked 09-22-2026)

| Benchmark | Size | Gold in Lean | Toolchain | License |
|---|---|---|---|---|
| [CLEVER](https://github.com/trishullab/clever) ([arXiv 2505.13938](https://arxiv.org/abs/2505.13938)) | 161 (from HumanEval) | `problem_spec` for all 161; 117/161 implementations are `sorry`; 4/161 complete proofs | v4.27.0 + Mathlib | MIT |
| [FVAPPS](https://github.com/quinn-dougherty/fvapps) ([arXiv 2502.05714](https://arxiv.org/abs/2502.05714)) | 4,715 (1,083 curated) | Specifications as `sorry` theorems and tests; no Lean implementation (Python reference only) | v4.12.0 | MIT (Hugging Face card) |
| [miniCodeProps](https://github.com/cmu-l3/minicodeprops-eval) ([arXiv 2406.11915](https://arxiv.org/abs/2406.11915)) | 177 (v1), 201 (v2) | Programs plus one property theorem each; proof-only task | v4.9.0 + Mathlib | BSD-3 / MIT |

VeriContest looked like a candidate but is Rust/Verus; it is covered by the [non-Lean idea](../non_lean_dafny_verus_transfer/README.md).

## Minimal comparison (zero spend)

A benchmark × property table of valid probe counts, with failure reasons, built with the same builders as the Verina idea and elaborated under each benchmark's own pinned toolchain. Then a short recommendation of which benchmark, if any, deserves a paid scoring run, with an exact quote.

## Key uncertainty

Old toolchains (FVAPPS v4.12, miniCodeProps v4.9) may not build on the current machine; that is itself a result to record, not a reason to drop the benchmark.

## Revisit condition

When a reviewer names one of these benchmarks, or after the Verina transfer idea if it succeeds and more breadth is wanted.
