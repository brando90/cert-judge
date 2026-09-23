# Beyond Lean 4: judge probes on Verus (VeriContest) and Dafny (DafnyBench)

**TLDR:** Port the gold-derived probes to Rust/Verus and Dafny and check structural validity with each language's verifier. This answers the ICML reviewer question "does the same property-based approach work for other proof assistants or formal languages beyond Lean 4?". The first phase is zero-spend; scoring is a later, separately quoted decision. Lowest priority, because the paper's scope is Lean 4.

**Execution:** DEFERRED — NOT RUN · **Paper inclusion:** UNDECIDED · **Priority:** 5 of 5 · **Recorded:** 09-22-2026 · **Issue:** <https://github.com/brando90/cert-judge/issues/45> · **Prompt:** [cc.md](cc.md)

**Would become:** `experiments/<NN>_verus_dafny_probe_structural_screen/`.

## Hypothesis

The three gold-derived probes (implementation mutation, removal of specification clauses and tests, binder renaming) have direct analogues in Verus (`requires`/`ensures` clauses, `proof fn`, `exec fn`) and Dafny (`requires`/`ensures`/`invariant`). Most gold programs yield verifier-checked valid ladders.

## Motivation

- ICML 2026 AI4Math reviewer question (`experiments/18_icml_reviews/pre_prompt.md:229`).
- The limitations section lists "artifacts from proof assistants other than Lean 4" as uncovered (`06_limitations.tex`).

## Benchmarks (facts checked 09-22-2026)

| Benchmark | Language | Size | Gold | Toolchain | License |
|---|---|---|---|---|---|
| [VeriContest](https://github.com/HIPREL-Group/VeriContest) ([arXiv 2605.08553](https://arxiv.org/abs/2605.08553)) | Rust/Verus | 946 (690 LeetCode, 256 Codeforces) | `spec.rs`, `code.rs`, `verified.rs` with full proofs, positive and negative tests | Verus 0.2026.04.10 | Apache-2.0 repo; Hugging Face data CC-BY-4.0 (about 50 GB) |
| [DafnyBench](https://github.com/sun-wendy/DafnyBench) ([arXiv 2406.08467](https://arxiv.org/abs/2406.08467)) | Dafny | 782 programs (about 53k lines) | Ground-truth programs plus hint-removed versions; ships LLM hint reconstructions (not candidates for this task) | Dafny | Apache-2.0 |

## Minimal comparison (zero spend)

A per-benchmark table of valid, invalid and failure-reason counts per probe type, checked with the Verus or Dafny verifier. Start with a fixed-seed sample of 100 VeriContest problems (not the 50 GB full set) and all 782 DafnyBench programs.

## Key uncertainty

- The judge prompts are Lean-specific; scoring would need a prompt port, which is a new judge configuration, not the paper's.
- Verifier run time at this scale is unknown.

## Revisit condition

Only if a reviewer presses on proof assistants beyond Lean, or after the Lean ideas are done.
