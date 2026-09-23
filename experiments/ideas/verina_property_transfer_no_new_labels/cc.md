# Prompt — Verina transfer of the paper's TI_var judge ranking (Codex family, no new human labels)

**TLDR:** Make the agent promote this idea into a numbered experiment, rebuild the paper's exact TI_var pipeline (exp16 protocol) for 24 Verina items, generate 72 Verina candidates with three coding agents, build an exact per-request quote, and, only within Brando's approved dollar ceiling, score all eight Codex-family configurations with 3 repeats. Success: every one of the 5,184 declared judge calls and 72 generation cells has a terminal receipt. The report puts per-configuration TI_var and properties on Verina next to the published VeriBench values, with the cross-benchmark Spearman and Kendall correlations. Deliverable: the new experiment folder with `PROTOCOL.md` (locked before spending), a live `results.md`, the exact quote, and the comparison table and figure, committed and pushed to `main`. Load-bearing constraints: never run a script that loads `~/keys/*` unless `APPROVED_SPEND_USD` below is filled in, and never author new API-calling code (Hard Rule 9).

Follow `~/agents-config/INDEX_RULES.md` (pull it first), the repo `CLAUDE.md`, and [the experiment workflow](~/agents-config/workflows/expts-and-results.md).

```
APPROVED_SPEND_USD: <Brando fills in before pasting; blank = zero-spend steps only, stop at the quote gate>
EXECUTION_PATH: <API (identical to the paper; recommended) | CLI (codex exec / claude -p; then VeriBench must be rescored the same way)>
```

If any part runs on a Stanford Network Analysis Project (SNAP) node, this line applies verbatim:
`SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).`
The dollar ceiling above is the budget; SNAP pre-approval does not raise it.

## Scientific question

Does the paper's label-free judge-certification signal rank judge configurations the same way on a second Lean 4 benchmark?
Primary quantity: Spearman ρ between the eight Codex-family configurations' TI_var on Verina and on VeriBench (published values: `experiments/archive/04_veribench_validation/results_exp30_tivar_v3_all_models/judge_trust_vector_*_avg.csv`, column `ti_var_v3`).
Pre-registered reading: ρ ≥ 0.5 with both controls ranked last = "consistent with transfer"; otherwise "not shown". With n = 8 this is descriptive, not a significance test.
Secondary: each property (identity, bug-ladder Spearman, weak monotonicity, flip rate, the two variance terms) per configuration on both benchmarks, and BAD_STRINGY's bug-ladder reversal count (VeriBench: 20 of 24).

## Context you must read first

- Idea folder (this file's folder): `README.md`, `COST_QUOTE.md`, `cost_quote.py`.
- Pipeline: `experiments/archive/04_veribench_validation/exp16_multi_judge_human_sets.py` (scoring; defaults at lines 131–138), `exp17_property_human_analysis.py`, `exp28_variance_aware_trust_index.py`, `make_fig2_tivar_cross_model.py`; judge client `experiments/archive/02_neurips_reviews/utils/judge_caller.py`; probe builders `utils/veribench_variance_utils.py:64` (`build_bug_ladder`) and `utils/variant_generator.py:127` (`generate_variants`).
- Paper method: `paper_latex/ICLR_2027_submission/04_property_protocol.tex` (TI_var definition) and `05_experiments.tex` (Codex-family table).
- Verina: <https://github.com/sunblaze-ucb/verina> (Apache-2.0, 189 problems, Lean v4.18.0 + Mathlib v4.18.0, one `task.lean` per problem with `!benchmark` markers around code, precondition, postcondition and proof).
- Terminology: repo `CLAUDE.md` (formal specification = theorem statements and the `Prop` predicates they use; tests are not specification; the human panel is the "validation set").

## Steps

1. **Promote the idea.** Allocate the next free experiment number (check `experiments/`, `experiments/archive/`, `experiments/archive/layout.json`, open branches). `git mv` this idea folder to `experiments/<NN>_verina_tivar_transfer_codex_family_no_new_labels/`, register it as active in `layout.json` and `experiments/README.md`, remove its row from `experiments/ideas/README.md` (leave a pointer), and run `python3 py_src/cert_judge/experiment_layout.py --check`. Create `results.md` now with `**Status:** RUNNING (started <ts>)` and keep it live (Trigger Rule 37; it closes with a tagged `**TLDR-end:**`, no opening TLDR).
2. **Pin Verina.** Clone it into the experiment's `data/` at a recorded commit, with its license file. Record the commit hash, the file count (expect 189) and the SHA-256 of every `task.lean`.
3. **Sample items.** Draw 24 items with a fixed seed (record it), stratified proportionally over Verina's basic and advanced splits. Freeze the list in `item_manifest.json`.
4. **Build golds and probes.** A gold is the Verina `task.lean` with its reference code and specification blocks. Run the unchanged exp16 builders (`build_bug_ladder`, `generate_variants`) on each gold. Record every probe's hash and every builder failure. Do not edit the builders; if a Verina construct breaks one, record it as a structural failure and keep it in the denominator.
5. **Recover the VeriBench generators.** Find which models or agents produced `data/generated_agents/*__agent{0,1,2}.lean` (git log, older experiment READMEs, `experiments/archive/04_veribench_validation/data`). If you cannot establish it, choose three current coding agents through subscription command-line tools, record the choice and why (Trigger Rule 57), and flag it as a comparability limit.
6. **Generate candidates.** 3 agents × 24 items = 72 cells, one attempt each, with a fixed per-cell time and turn budget stated in `PROTOCOL.md`. Give each agent the Verina description and signature only, never the gold. Every generation prompt, first and continuation, includes the solver completion reminder below. Compile each candidate in a Verina Lean v4.18 project and record the result, but keep non-compiling candidates: the VeriBench pairs also include them.
7. **Freeze the protocol.** Write `PROTOCOL.md` in the mandatory format (`~/agents-config/workflows/expts-and-results.md` § PROTOCOL.md). Lock the judges (8 Codex-family configurations: `gpt-5.3-codex` × {P1_BASELINE, P4_CHECKLIST, P8_STRICT_B, BAD_STRINGY}, `gpt-4o-mini` × {P8_STRICT_B, P4_CHECKLIST}, controls `editdist_e1` and `random_r1`), decoding (temperature 1.0, 256 output tokens, as in the paper), 3 repeats, the full cell manifest (5,184 LLM judge calls plus controls) and the analysis above. Commit it before any paid call.
8. **Exact quote gate.** Render every request, count its UTF-8 bytes, and write `spend_quote.json` with per-model calls, token bounds and USD, using the same rule as `COST_QUOTE.md`. Check that both models are still served. If `APPROVED_SPEND_USD` is blank, or the exact quote exceeds it, stop here: report the quote and the path to it, and set `results.md` to `BLOCKED — awaiting spend approval`.
9. **Score.** Run the full manifest through `EXECUTION_PATH` using the existing client code only, keeping a durable per-cell ledger and cumulative spend. Stop only on the approved ceiling, an explicit cancellation, or a pre-registered abort rule. Keep failed and missing cells in the denominator, and never impute zeros.
10. **Analyse.** Compute per-configuration properties and TI_var with the unchanged exp16/exp17/exp28/exp30 code paths; exact-zero and missing values stay explicit. Produce the comparison table (Verina next to VeriBench), the cross-benchmark Spearman and Kendall correlations with a bootstrap over Verina items (10,000 replicates, seed 0), and a Figure-2-style plot.
11. **Report.** Update `results.md` with measured numbers, expected / attempted / terminal / clean / incomplete / interrupted counts for both the generation and scoring manifests, and a one-paragraph reading against the pre-registered criterion. Add a ≤ 3-sentence paper-ready summary, but do not edit `paper_latex/`.
12. **Land.** Commit with explicit pathspecs (`git commit -m "…" -- <paths>`; the checkout and index are shared with other sessions), `git pull --rebase --autostash`, push to `main`, and tick the matching box in issue #45.

## Solver completion reminder (include verbatim in every generation prompt)

> Solve the entire assigned task, including every required file, question and subtask. Produce the complete required deliverable in the specified output location or response format; an outline, partial draft, progress report or claim of completion is not a substitute. Write/save the output, inspect the actual saved artifact or final response, and run the allowed checks, tests or compilation required by the task. Within the declared time, token, call and tool limits, continue working and fixing errors until the requirements are met or a declared terminal condition is reached. Follow the fixed continuation procedure without resetting budgets. If anything remains unresolved, preserve the best current deliverable and report the exact remaining failures and checks that did not pass; never claim success or invent verification.

## Guardrails

- Hard Rule 9: no new API-calling code; do not execute anything that reads `~/keys/*` without a filled `APPROVED_SPEND_USD`; scrub `*_API_KEY` from subprocess environments for command-line runs.
- Full declared set: every cell of both manifests reaches a terminal status; a clean subset is not a completed evaluation.
- Never write into `experiments/archive/`; import or copy what you need into the new experiment folder.
- Do not change the paper, the frozen VeriBench results, or the probe builders.
- Name the models and effort you actually used in `results.md` (Hard Rule 8).

TL;DR: Promotes the Verina idea into a numbered experiment, generates 72 Verina candidates with three coding agents, gates on an exact spend quote, then (within Brando's ceiling) scores the eight Codex-family judge configurations through the paper's exp16 pipeline, and reports TI_var and property rankings next to VeriBench in a live `results.md`.
