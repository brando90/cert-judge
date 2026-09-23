# Prompt — Structural probe screen on CLEVER, FVAPPS and miniCodeProps (zero spend)

**TLDR:** Make the agent promote this idea into a numbered experiment, pin CLEVER, FVAPPS and miniCodeProps at recorded commits, build each one's Lean project with its own toolchain, and try to construct the paper's gold-derived probes on every problem. The probes are a 4-level bug ladder on implementation `def`s, 4-level removal of theorem statements and unit tests, and alpha-renaming. Success: a benchmark × property table of valid, invalid and failure-reason counts covering every problem in each benchmark (1,083 curated FVAPPS problems, not all 4,715), plus a recommendation with an exact spend quote for the best candidate. Deliverable: the experiment folder with builders, validity manifests, quote and live `results.md`, pushed to `main`. Load-bearing constraint: zero model calls.

Follow `~/agents-config/INDEX_RULES.md` (pull it first) and the repo `CLAUDE.md`.

If it runs on a Stanford Network Analysis Project (SNAP) node, this line applies verbatim:
`SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).`

## Steps

1. **Promote.** Allocate the next free experiment number, `git mv` this idea to `experiments/<NN>_lean_benchmark_probe_structural_screen/`, register it in `layout.json` and `experiments/README.md`, update the ideas index, run the layout check, and start a live `results.md` (closes with a tagged `**TLDR-end:**`).
2. **Pin and build.** Clone each benchmark at a recorded commit with its license: CLEVER <https://github.com/trishullab/clever> (v4.27.0), FVAPPS <https://github.com/quinn-dougherty/fvapps> (v4.12.0; use the 1,083-problem curated subset and record how it is identified), miniCodeProps <https://github.com/cmu-l3/minicodeprops-eval> (v4.9.0; use v2 if it is the default). Build each with `elan` and its own `lean-toolchain`. If a toolchain will not build, record the error and keep that benchmark's problems in the denominator as structural failures.
3. **Build probes.** Use the same operators as the Verina idea (`build_bug_ladder`, `generate_variants`, and the missing-specification ladder in `py_src/cert_judge/probe_validation.py`), copied into the experiment's `src/` rather than modified in place. Rules:
   - Bug ladder only where a non-`sorry` reference implementation exists.
   - Specification removal deletes theorem statements and unit tests (`example`, `#eval`, `#guard`, `#test`) cumulatively; describe them in those words, not as "specifications" (repo `CLAUDE.md` § Specification).
   - Every level must elaborate; reject no-op and duplicate levels; record every rejection with its reason.
4. **Sizes.** Record prompt byte sizes per probe, for the quote.
5. **Recommend and quote.** Pick the benchmark with the most valid probes on the properties TI_var uses (bug ladder and repeat stability; the latter needs candidates, so note how they would be generated). Write an exact `spend_quote.json` for the Codex-family panel (see `experiments/ideas/verina_property_transfer_no_new_labels/COST_QUOTE.md`). Do not score.
6. **Report.** The benchmark × property table, failure reasons, and a reading against the hypothesis in the README, in `results.md`.
7. **Land.** Commit with explicit pathspecs (the index is shared), `git pull --rebase --autostash`, push to `main`, and tick issue #45.

## Guardrails

- Zero LLM or provider calls; nothing that reads `~/keys/*`.
- Every problem stays in its benchmark's denominator, including toolchain failures.
- Do not modify `py_src/cert_judge/` or anything under `experiments/archive/`.

TL;DR: Builds and compiles the paper's gold-derived probes on CLEVER, FVAPPS (curated 1,083) and miniCodeProps under their own toolchains, and reports a benchmark × property validity table plus an unexecuted scoring quote for the best candidate; no model calls.
