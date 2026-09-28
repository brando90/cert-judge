# QA of the exp-34 Astra rewrite — Claude Fable 5.1, 2026-09-24

**TLDR:** Every substantive claim in Astra's `REPORT.md` "Corrections that change interpretation" was re-derived from the frozen artifacts and holds. The most consequential: the old paper's "P3 most informative property" was a bug-ladder statistic (`P3_weak_mono` ← `bug_weak_mono_pct`, exp17); the old Figure 2 plotted the six-term unequal-weight `ti_var_v3` (exp30) under panel titles quoting the equal-weight index's ρ (exp28); the alpha-renaming probes are malformed (`:=:=`, 184/184; exp29 preflight, 2026-08-20); under the paper's actual equal-weight index the lexical judge scores 0.940 (Codex) / 0.982 (Qwen), so only the recorded reversals expose it. Build, archive byte-preservation, number provenance, complaint coverage, and the writing-guide checks all pass. No paper edits were needed.

Scope: Brando asked for a Fable QA of "the changes Astra claimed" (not an opposite-agent round). Checks were run on `main` at `1cac976` (merge `63fb935`) against `experiments/archive/`. No LLM calls, no new experiments.

## Verdicts on the eleven corrections

| # | Astra's claim | Independent check | Verdict |
|---|---|---|---|
| 1 | Old scatter/table used an unequal six-weight index under equal-weight titles | Old Figure 2 x-values (8d2e005): P1 0.9208, P4 0.9199, P8 0.8919, BAD_STRINGY 0.6964, 4o-mini 0.4709/0.1141, editdist 0.0595, random 0.0083 = exactly `ti_var_v3` = exp(0.2 ln ident + 0.2 ln mono + 0.2 ln weak + 0.15 ln stab + 0.125 ln varcorr + 0.125 ln varscore) from `results_exp30_tivar_v3_all_models` (reproduced to 9e-10 by exp32's `compute_property_suite.py`). Equal-weight `TI_var` (exp28 `judge_trust_vector.csv`): P1 0.9578, P4 0.9576, P8 0.9498, BAD_STRINGY 0.9403, 4o-mini 0.3245/0.0070, editdist 0.9283, random 0.0079 — these are the values now plotted. Panel titles' ρ (0.833) were always exp28's. | **CONFIRMED** |
| 2 | Qwen pass2 is 0.857, not 0.905 | exp28 `qwen_pass2/summary.json` rho_TI_vs_human = 0.8571; `qwen_avg` = 0.9048 (the 0.905 belonged to averaged labels) | **CONFIRMED** |
| 3 | No P3 result in the retained panel; `P3_weak_mono` is bug weak-monotonicity | `exp17_property_human_analysis.py:99,192,198`: `"P3_weak_mono" = clip(bug_weak_mono_pct/100)`; `per_property_correlations.csv` (avg) row `P3_weak_mono` 0.747 is that bug statistic | **CONFIRMED** — the old "P3 most informative" claim was mislabeled |
| 4 | Historical alpha probes malformed; 0.250→0.070 is a score-replacement proxy | `29_proxy_validation/PREFLIGHT_PTI_V0_V4.md` (2026-08-20): 184/184 alpha artifacts contain `:=:=`, bound occurrences not renamed consistently, 163/163 dependency-free ones fail Lean 4.22 elaboration. The paper's alpha table came from that 184-file pool (`02_neurips_reviews/results/codex_api_gpt53_r3_20260418_230027/identity_rows.csv`). exp24 `summary.json`: mean_std 0.2501 → 0.0697, `alpha_policy` clip, n_judges 8 (a replacement of alpha scores, not a rescoring) | **CONFIRMED** |
| 5 | The scalar is not a rejection certificate (lexical judge 0.940 Codex / 0.982 Qwen) | exp28 codex_avg BAD_STRINGY 0.9403 (vs P1 0.9578); qwen_avg BAD_STRINGY 0.9823 (highest in the family). The old "0.70, ranked below all prompted judges" came from `ti_var_v3`, whose 'weak' term (0.208 for BAD_STRINGY) is the bug weak-monotonicity statistic | **CONFIRMED** |
| 6 | The 184-file sanity figure mixed 34 heuristic-scored tasks | `codex_api_gpt53_r3_20260418_230027/summary.json` notes: "Rows include appended datapoints for 34 added tasks … (local-mode scoring for appended subset)" | **CONFIRMED** |
| 7 | "Plain geometric" comparator's 0.4/0.6 weights were selected on pass1 | exp23 `summary_fit_pass1.json` weights {mono 0.4, stab 0.6, others 0}; fit 0.881 / test 0.810 | **CONFIRMED** |
| 8 | Fixed index uses only bug rows, per-panel normalization, 1e-6 floor | exp28 summaries: weights 1/3 each over C_f, VarCorr_norm, VarScore_norm; `judge_trust_vector.csv` columns are bug-ladder terms only; exp32 reproduction notes the clip to [1e-6, 1−1e-6] | **CONFIRMED** |
| 9 | Inter-pass agreement is not a demonstrated ceiling | exp18 `metrics`: spearman 0.2486, QWK 0.3718, MAE 0.7708 (n_overlap 72) — numbers correct; the "ceiling" inference had no artifact behind it | **CONFIRMED** (removal justified) |
| 10 | Stale reversal plots replaced from the frozen CSV | exp19 `bug_reversal_rates.csv`: P1 0/24, P4 0/24, P8 4/24, BAD_STRINGY 20/24, 4o-mini 18/24 and 16/24, editdist 24/24, random 24/24 — matches the new Table 3 | **CONFIRMED** |
| 11 | Negative evidence retained (Leanstral, pool, screens) | exp28 leanstral pass1/pass2/avg −0.119/−0.0476/−0.0952; exp25 geom 0.769 [0.343, 0.949]; CIs `21_tmlr_submission/ci_provenance/headline_cis.json` 0.833 [0.241, 1.0] p 0.0167 | **CONFIRMED** |

## Mechanical gates (re-run independently)

- Scratch build of `main` at `1cac976`: latexmk exit 0; 0 errors, 0 undefined refs/citations, 0 overfull boxes, 0 BibTeX warnings; 17 pages; References p. 9; Reproducibility statement p. 14.
- Archive byte-preservation: all 9 archived `.tex` + `refs.bib` are byte-identical to `8d2e005` (`cmp`).
- Banned words in active `.tex`: `calibrat*` 0, "development panel" 0, DSPy 0, Trace+ 0, "Claude 3.7" 0, `\bPTI\b` 0; `latex_sentence_lines.py --check` passes.
- Complaint coverage: 55 = 29 (A26) + 14 (N25) + 3 (T26) + 9 (D26); every row has a quoted manuscript sentence with a file:line anchor.
- Analysis scripts (`analysis/*.py`) import only hashlib/json/csv/re/subprocess/numpy/scipy/matplotlib — no provider or network modules; `subprocess` is used for git/latexmk/pdftotext only.
- Corrected numbers are present in the text: 0.857 (05_experiments:61,81,136), 0.940/0.982/0.928/0.958 (05_experiments:100–117), and the "Coverage of P3" paragraph (05_experiments:45–48, 144).

## Writing-guide checks on the new abstract and introduction

- No sentence over 25 words in the abstract or introduction; no AI-tell/hype words (leverage, seamless, delve, robust, novel, frontier, …); no `while`-as-`and`; no "predict"; `% CS197 move` comments present (abstract 9, intro 6).
- Abstract numbers agree with the artifacts (0.833/0.905/0.738 Codex; 72 pairs; one annotator; three families × eight configurations). The lexical-judge sentence is accurate: BAD_STRINGY's human ρ (0.435) exceeds P4 (0.419) and P8 (0.365), reversals 20/24, index 0.940.
- Style notes (not applied — Brando's call): the abstract has no memorable hook or coined term; "leaving each new judge configuration dependent on human validation" is slightly abstract; the closing sentence lost "per-judge annotation cost", which was the concrete "from X" of the vision.

## Open items (unchanged from REPORT.md)

LLM-usage statement facts (`08_statements.tex:19`); recovery of Ethan's original panel rubric; the scientific gaps that only new experiments can close (exp 35: probes for vacuity/weakening/over-constraint, real canonicalization rescoring, a matched-rubric held-out test).
