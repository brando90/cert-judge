# Excluded manuscript material

These files preserve the pre-rewrite text and figures. None is an input to `main.tex`, and no active manuscript reference resolves to this archive. Historical claims here are not claims of the rewritten paper. The original source bytes are preserved.

| File | Original section titles | Why archived | Active citations |
|---|---|---|---|
| `04_property_protocol.tex` | Property Certification Protocol | Superseded index/protocol account; canonical implementation is now stated explicitly. | None |
| `05_experiments.tex` | Experiments; Data and human panel; Property sanity checks on GPT-5.3-Codex; \texorpdfstring{\(\mathrm{TI | Superseded mixed-index table, mixed model/heuristic plots, and invalid alpha interpretation. | None |
| `990_appendix_additional_results.tex` | Additional Validation-Set Results | Original additional-results source preserved; retained tables were corrected and condensed. | None |
| `991_appendix_related_work_cont.tex` | Related Work (Cont.); Related Work: Scalable Oversight; HCI for Solving Scalable Oversight | Extended scalable-oversight and HCI survey is unnecessary for the core claim. | None |
| `992_appendix_formal_verification.tex` | Formal verification context and tooling | Unneeded tooling survey; the main setup supplies the necessary definitions. | None |
| `993_appendix_spec_relative_scores.tex` | Why Judge Scores Are Specification-Relative | Long reference-relative argument removed; the main limitations state the supported claim. | None |
| `995_appendix_judge_prompts.tex` | Judge Prompt Templates | Preserve the original scale/input description before correction; prompt templates remain active. | None |
| `996_appendix_judge_cert_plots.tex` | Judge Certification: Additional Plots | Original plotting collection preserved; only cited, correctly scoped diagnostics remain active. | None |
| `997_appendix_human_alignment.tex` | Validation-Set Human Alignment Appendix; Naive Codex-Style Blind Baseline; Human-Human Agreement Ceiling Context; Cross-Model Validation Status (Full vs Preliminary); Leanstral Negative-Control Reaggregation (AM/GM/Variance-Aware); Index Definitions; Failure Modes Found by Certification | Blind baseline, status survey, extended Leanstral discussion and unsupported ceiling claim removed; definitions and necessary evidence retained in corrected form. | None |
| `refs.bib` | Original bibliography | Preserves removed entries; active bibliography contains cited works only. | None |
| `OPEN_QUESTIONS.md` | Original decision sheet | Replaced with current author decisions. | None |

## Figures

Original paths are preserved below `archive/figures/`. Some archived sources refer to figures retained by the active manuscript; those historical sources are preservation records, not a standalone second build.

| Original figure path | Reason | Active citations |
|---|---|---|
| `figures/3.5_bugs.png` | Superseded or uncited diagnostic. | None |
| `figures/3.5_specs_missing.png` | Historical missing-specification study excluded from the core panel. | None |
| `figures/3.7_specs_missing.png` | Historical missing-specification study excluded from the core panel. | None |
| `figures/codex_api_gpt53_r3_20260418_230027/monotonicity_bugs_lowvar_se_bounds.png` | Study combines model-scored and heuristic-scored tasks; not a pure Codex result. | None |
| `figures/codex_api_gpt53_r3_20260418_230027/monotonicity_missing_specs_lowvar_se_bounds.png` | Study combines model-scored and heuristic-scored tasks; not a pure Codex result. | None |
| `figures/exp16_final_robust/fig_cert_vs_human_scatter_avg.png` | Plot used a different index from the fixed-index headline; regenerated from canonical vectors. | None |
| `figures/exp16_final_robust/fig_cert_vs_human_scatter_pass1.png` | Plot used a different index from the fixed-index headline; regenerated from canonical vectors. | None |
| `figures/exp16_final_robust/fig_cert_vs_human_scatter_pass2.png` | Plot used a different index from the fixed-index headline; regenerated from canonical vectors. | None |
| `figures/exp16_final_robust/fig_human_corr_by_judge_and_labelset.png` | Superseded or uncited diagnostic. | None |
| `figures/exp17_final_robust/fig_property_vs_human_bars_avg.png` | Property naming conflated bug weak monotonicity with P3; replaced by correctly labeled table. | None |
| `figures/exp17_final_robust/fig_property_vs_human_bars_pass1.png` | Property naming conflated bug weak monotonicity with P3; replaced by correctly labeled table. | None |
| `figures/exp17_final_robust/fig_property_vs_human_bars_pass2.png` | Property naming conflated bug weak monotonicity with P3; replaced by correctly labeled table. | None |
| `figures/fig3_style_claude_opus_monotonicity.png` | Superseded or uncited diagnostic. | None |
| `figures/fig3_style_gpt53_codex_monotonicity.png` | Study combines model-scored and heuristic-scored tasks; not a pure Codex result. | None |
| `figures/fig_main_monotonicity_lowvar_codex.png` | Study combines model-scored and heuristic-scored tasks; not a pure Codex result. | None |

The complete Leanstral discussion is preserved in `997_appendix_human_alignment.tex`; its negative fixed-index result remains in one active paragraph. Archive figures retain their original bytes.

The local `.gitattributes` preserves pre-existing terminal blank lines in the original TeX sources; all other whitespace checks remain enabled.
