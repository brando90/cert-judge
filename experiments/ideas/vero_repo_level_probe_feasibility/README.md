# Vero: can the property probes and the judge work on multi-module Lean repositories?

**TLDR:** A zero-spend feasibility study that adapts the bug ladder, the specification-removal ladder and alpha-renaming to Vero's multi-module Lake projects. It counts how many probes still elaborate under Vero's Lean v4.29.1 and decides how to present a repository to a judge within its context limit. Paid scoring is a separate, later decision.

**Execution:** DEFERRED — NOT RUN · **Paper inclusion:** UNDECIDED · **Priority:** 4 of 5 · **Recorded:** 09-22-2026 · **Issue:** <https://github.com/brando90/cert-judge/issues/45> · **Prompt:** [cc.md](cc.md)

**Would become:** `experiments/<NN>_vero_repo_level_probe_feasibility/`.

## Hypothesis

Gold-derived perturbation ladders can be built for most Vero instances: at least 30 of 43 instances would yield one or more compile-valid 4-level bug ladders and specification-removal ladders. A per-API slice (one implementation function plus the `spec_*` definitions that mention it) fits a judge prompt, where whole repositories do not.

## Motivation

- Vero ([arXiv 2608.13522](https://arxiv.org/abs/2608.13522), [repo](https://github.com/sunblaze-ucb/vero), Apache-2.0 except 3 LGPL instances) comes from the Verina group and is repository-level: 43 instances, 743 APIs, 2,705 specifications.
- A reviewer who names Verina will likely name Vero next; the limitations section names both.
- Our judges have only been shown single files.

## What is different from VeriBench and Verina

- Each instance is its own Lake project: `Impl/`, `Spec/`, `Harness.lean` (`canonical : RepoImpl`), `Test.lean`, `manifest.json`; Lean v4.29.1, mostly without Mathlib.
- Specifications are `def spec_* : Prop` definitions, not `theorem` statements, so "remove theorem statements" becomes "remove `spec_*` definitions and their manifest entries".
- Reference implementations are released; reference specification proofs ship only for the BankLedger exemplar.
- Size: `semver` alone has `Spec/Version.lean` at 34 KB (53 `spec_*`), too long to judge whole.
- No model-generated solutions are released.

## Minimal comparison (zero spend)

Per instance: the number of structurally valid bug, specification-removal and alpha probes (compile under the pinned Vero toolchain), the failure reasons, and prompt byte sizes for whole-repository versus per-API slices. The output is a go/no-go table plus an exact spend quote for scoring the valid slices.

## Key uncertainty

- Whether removing a `spec_*` definition leaves the project compiling (the harness and manifest may reference it).
- Whether per-API slicing changes what the judge is being asked, which would make scores incomparable with single-file benchmarks.

## Revisit condition

After the Verina transfer idea shows whether single-file transfer holds; if it fails there, Vero is moot.
