# Prompt — Vero repository-level probe feasibility (zero spend)

**TLDR:** Make the agent promote this idea into a numbered experiment, pin Vero, and adapt the three gold-derived probes (bug ladder on `Impl/`, removal of `spec_*` definitions with their manifest entries, alpha-renaming) to multi-module Lake projects. It elaborates every probe with Vero's Lean v4.29.1 toolchain and measures prompt sizes for whole-repository versus per-API judge inputs. Success: a per-instance table for all 43 instances with valid, invalid and failure-reason counts per probe type, plus a go/no-go recommendation and an exact spend quote for scoring. Deliverable: the experiment folder with the probe builders, validity manifest, quote and live `results.md`, pushed to `main`. Load-bearing constraint: zero model calls; this prompt only builds, compiles and counts.

Follow `~/agents-config/INDEX_RULES.md` (pull it first) and the repo `CLAUDE.md`.

If it runs on a Stanford Network Analysis Project (SNAP) node, this line applies verbatim:
`SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).`

## Steps

1. **Promote.** Allocate the next free experiment number, `git mv` this idea to `experiments/<NN>_vero_repo_level_probe_feasibility/`, register it in `layout.json` and `experiments/README.md`, update the ideas index, run the layout check, and start a live `results.md` (closes with a tagged `**TLDR-end:**`).
2. **Pin Vero.** Clone <https://github.com/sunblaze-ucb/vero> at a recorded commit, keep the license files (note the 3 LGPL instances), and build every instance's reference project with its own `lean-toolchain` (expect v4.29.1). Record which reference projects build; a reference that does not build is a structural failure for every probe of that instance.
3. **Write the builders** in the experiment's own `src/` (reuse ideas from `py_src/cert_judge/probe_validation.py`, but do not modify it):
   - Bug ladder: 4 cumulative, distinct, compile-valid mutations of implementation `def`s under `Impl/`, using the same mutation operators as `build_bug_ladder`.
   - Specification-removal ladder: remove `def spec_*` definitions and their `manifest.json` entries cumulatively, 4 levels. Record whether `Harness.lean` or `Test.lean` breaks.
   - Alpha: a conservative binder rename that is not a no-op.
   - Every level must elaborate; reject no-op and duplicate levels. Record every rejection with its reason. Never hide a failure.
4. **Judge-input sizes.** For each instance, measure UTF-8 bytes for (a) the whole repository (`Impl/` + `Spec/`), and (b) per-API slices, meaning one `Impl` function plus the `spec_*` definitions that mention it. Report the distributions against the 3.6 KB VeriBench pair mean.
5. **Quote.** Using the frozen token rule (input ≤ bytes + 128 tokens, output ≤ 256) and the Codex-family panel from `experiments/ideas/verina_property_transfer_no_new_labels/COST_QUOTE.md`, write an exact `spend_quote.json` for scoring the valid per-API probes with 3 repeats. Do not score anything.
6. **Report.** A per-instance table, totals, failure reasons, and a go/no-go reading against the hypothesis (≥ 30 of 43 instances with valid bug and specification-removal ladders) in `results.md`.
7. **Land.** Commit with explicit pathspecs (the index is shared), `git pull --rebase --autostash`, push to `main`, and tick issue #45.

## Guardrails

- Zero LLM or provider calls; nothing that reads `~/keys/*`.
- Keep all 43 instances in the denominator.
- Do not modify `py_src/cert_judge/probe_validation.py` or anything under `experiments/archive/`.

TL;DR: Builds and compiles bug, specification-removal and alpha probes for all 43 Vero Lake projects, measures judge-input sizes, and produces a go/no-go table plus an exact (unexecuted) scoring quote; no model calls.
