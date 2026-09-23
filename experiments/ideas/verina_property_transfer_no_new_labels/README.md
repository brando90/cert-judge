# Verina: does the paper's TI_var judge ranking transfer? (no new human labels)

**TLDR:** Re-run the paper's exact TI_var pipeline on Verina with the Codex-family judge panel and compare each configuration's TI_var and property scores with its VeriBench values. It needs 72 agent-generated Verina candidates and about 5,184 judge calls (about $23 at API prices; see [COST_QUOTE.md](COST_QUOTE.md)), and no human labels. This is the cheapest answer to "why only VeriBench?".

**Execution:** DEFERRED — NOT RUN · **Paper inclusion:** UNDECIDED · **Priority:** 1 of 5 (highest) · **Recorded:** 09-22-2026 · **Issue:** <https://github.com/brando90/cert-judge/issues/45> · **Prompt:** [cc.md](cc.md)

**Would become:** `experiments/<NN>_verina_tivar_transfer_codex_family_no_new_labels/` (next free number at promotion time).

## Hypothesis

Across the eight Codex-family configurations, the TI_var ranking on Verina agrees with the VeriBench ranking (Spearman ρ ≥ 0.5), the two controls (`editdist_e1`, `random_r1`) stay at the bottom, and the known failure repeats: BAD_STRINGY reverses on most bug ladders (20 of 24 on VeriBench).

## Motivation

- The paper says "Applied to VeriBench" (`00_abstract.tex`) and "All experiments use VeriBench" (`05_experiments.tex:4`); the limitations now say Verina and Vero are untested (`06_limitations.tex`, commit 543c524).
- NeurIPS 2025 MATH-AI reviewer ivJs: "finite perturbations on one benchmark" (`experiments/33_openreview_complaints_all_venues_to_iclr2027_paper/complaints_ledger.md`, row N25-ivJs-1).
- ICML 2026 AI4Math reviewers asked about "new Lean domains" and "other proof assistants or formal languages beyond Lean 4" (`experiments/18_icml_reviews/pre_prompt.md` lines 103 and 229).

## Why Verina first

Verina ([arXiv 2505.23135](https://arxiv.org/abs/2505.23135), [repo](https://github.com/sunblaze-ucb/verina), Apache-2.0) has 189 single-file problems, each with gold code, precondition, postcondition and proof blocks in one `task.lean`, which is the closest match to the VeriBench layout.
Only 46 of the 189 gold proofs are free of `sorry`; that is fine, because VeriBench golds also use `sorry`.
Verina releases no model-generated solutions, so candidates must be generated.

## Minimal comparison

1. Sample 24 Verina items with a fixed seed, stratified over the basic and advanced splits.
2. Generate 3 candidates per item (72 pairs) with three coding agents.
3. Score pairs, rewrite probes and bug ladders with the exact exp16 pipeline, prompts, decoding and 3 repeats.
4. Report per-configuration TI_var and each property on Verina next to the published VeriBench values, and the cross-benchmark Spearman and Kendall correlations over configurations, with a bootstrap over Verina items.

## Key uncertainty

- With eight configurations, a cross-benchmark rank correlation is low-powered; report it as descriptive.
- The paper's judges were called through provider APIs. An identical configuration needs Brando to approve the dollar ceiling (Hard Rule 9); the command-line fallback changes the configuration (see COST_QUOTE.md).
- The provenance of VeriBench's three generator agents (`data/generated_agents`, agent0–2) must be recovered so the Verina candidates come from comparable generators.

## Side finding recorded while planning (not part of this idea)

In code, the paper's P3 "weak" term is the weak-monotonicity rate over the bug ladder (`experiments/archive/04_veribench_validation/exp17_property_human_analysis.py:99`), while `04_property_protocol.tex` describes P3 as removing theorem statements and unit tests.
TI_var itself does not use P3, but the v1/v2 baseline indices do.

Second, the TI_var figure script (`experiments/archive/04_veribench_validation/make_fig2_tivar_cross_model.py:21–31`) plots the six-term weighted `ti_var_v3` from `results_exp30_tivar_v3_all_models/` (Codex average ρ = 0.762), while the paper defines TI_var as the three-term equal-weight index and quotes exp28's 0.833 / 0.905 / 0.738.

## Revisit condition

After the ICLR main text is frozen, or at once if rebuttal reviewers ask for a second benchmark.
