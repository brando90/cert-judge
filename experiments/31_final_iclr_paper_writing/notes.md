# 31_final_iclr_paper_writing — ledger

**TLDR:** "Calibration" is already removed from every paper tree (PR #44, commit `be4449a`, 2026-09-13,
wording-only). No full rewrite. The *concept* still leaks in ~4 places in the ICLR main text; fix is a
targeted pass on abstract / §1 / §4 opening / §5.3 / §6.1 / §7 (~25–30 sentences). Appendix untouched.

Target file: `paper_latex/ICLR_2027_submission/main.tex` (09-16 verbatim port of the accepted ICML DL4C paper;
main text = lines 104–719, `\appendix` at 791). Build: `latexmk -pdf main.tex`.

## Audit 2026-09-22 (calibration concept, main text only)

| # | Where (main.tex) | Problem | Fix |
|---|---|---|---|
| 1 | `:107` abstract, `:336` §5.3 header, `:596`, `:603` | "predicts" / "predictor" for an n=8 development-set association where the index form was chosen with the labels in view | "is associated with" / "tracks … on the development panel"; §5.3 header → "TI_var tracks judge-level human alignment on the development panel" |
| 2 | `:107` "weightings discovered on n=75", `:138` "fits the pooled development corpus", `:712` "we fit and select once" | Say TI_var is *fitted*. It is not: §4 `:221` and App. `app:index-definitions` define it with fixed equal 1/3 weights. Only the index *form* was selected on the panel. | "selected" / "the reported values are development-set associations of a fixed-weight index" |
| 3 | `:560–572` Table `tab:cross_pass_generalization` + `:572` "when TI_var is fit using one human pass" | The Fit/Test numbers (0.881/0.810, 0.857/0.786) come from `exp23_cross_pass_calibration.py`, a 200k-iter random search over **six** weights (`ident,mono,weak,stab,anti,subtle`); pass1-fit weights = (mono 0.4, stab 0.6). That is a *tuned-weight geometric variant*, not TI_var. | Caption + sentence: "a weight-tuned geometric variant (Appendix …)"; never call it TI_var |
| 4 | `:688` "the answer (ρ=0.881 across 8 judges)" | Quotes the exp23 tuned *in-sample* fit as TI_var's headline; abstract headline is 0.833/0.905/0.738 | Replace with the avg-label 0.833 (or the trio) and say "development-set association" |
| 5 | `:342` "within each regression" | No regression is run; figure is a Spearman scatter | "within each family panel" |
| 6 | `:142,:144,:156,:198,:596,:706` | "human-agreement assessment protocol/panel" is a mechanical drop-in for "calibration protocol/panel"; reads badly | Rewrite prose: "one-time human panel", "development panel", "property–human-agreement link" as fits |

Evidence for #3: `experiments/archive/04_veribench_validation/results_exp23_cross_pass_calibration/summary_fit_pass1.json`
(`fit_corr_spearman=0.88095`, `test_corr_spearman=0.80952`, weights mono 0.4 / stab 0.6) and `summary_fit_pass2.json`
(`0.85714` / `0.78571`, six non-zero weights).

## Decision (Trigger Rule 57 — decided, not asked)

TI_var is the **fixed equal-weight** index; the cross-pass table is a **separate tuned-weight variant** and will be
labeled as such. Headline stays 0.833 / 0.905 / 0.738 (avg / pass1 / pass2). Operation names per
`docs/terminology_cleanup_20260913.md`: development-set association (headline), index-form selection (what the panel
did), fitted score mapping (only exp23's tuned variant), threshold selection (§5.5). Nothing is called a prediction,
generalization, or calibration in the main text.

## Plan

1. Rewrite abstract + §1 (also the biggest page-cut opportunity; main text is 11 pp vs 9 limit — `OPEN_QUESTIONS.md` #1).
2. §4 opening paragraph + Table `tab:protocol_workflow` caption.
3. §5.3 header + "Takeaway" paragraph; cross-pass table caption/sentence.
4. §6.1 + `:688`; §7.
5. `latexmk -pdf`; grep main text for `predict|fit|regression|calibrat`; diff --stat; page count.
6. Leanstral fix (Brando's task list) is separate — not in this pass.

## Status

- 2026-09-22: audit done, experiment registered in `experiments/archive/layout.json` + `experiments/README.md`.
  Rewrite not started. `experiment_layout.py --check` currently fails only on Brando's pre-existing uncommitted
  moves of `18_icml_reviews` / `20` (not touched here).

## 2026-09-22 — abstract "fresh human ratings" claim

- Abstract: "least scalable way possible: fresh human ratings for every new judge, prompt, model, and threshold" → "Practitioners typically establish their reliability through agreement with human ratings and must repeat that check for every new judge, prompt, model, and domain."
- Dropped "threshold": picking a threshold reuses existing labels, so it does not need fresh ratings (and §5.5 picks one on the dev panel). Replaced with "domain" (Bavaresco et al. 2024: agreement varies across datasets and properties).
- Intro: cited the per-judge human-validation practice (G-Eval, MT-Bench) and why it is necessary (Bavaresco et al. 2024, bib key `Kocmi2024HumanVsLLM`). Deleted the duplicate uncited restatement in the ¶ starting "Property certification amortizes".
- refs.bib: `Li2024TrustLLMJudgments` author fixed to Schroeder & Wood-Doughty (checked against arXiv 2412.12509).
- Open: `% TODO(internal-review)` in the intro asks why a new judge on the same domain can't just reuse the n=75 labels. Also, Related Work says "Cronbach's α" for 2412.12509, but that paper uses McDonald's ω.

## 2026-09-22 — "specification" definition (decided by Brando)

- Adopted the formal-methods experts' definition: formal specification = theorem statements about the implementation (+ the Prop predicates they use). Unit tests are not specification. NL problem statement = "intent".
- Brando's competing view (a unit test is a ground theorem, e.g. `example : myAdd 1 2 = 3 := by native_decide`) is stated only in new appendix `app:spec-vs-tests` (App. E) and is not adopted.
- main.tex: definition added to §3 "Task"; §3 retitled "Judging Lean Formal-Specification Quality"; P3 text/§1/§5/App. figures now say "theorem statements and unit tests" (the ladder removes both); abstract no longer lists theorems apart from formal specs.
- Rule recorded in CLAUDE.md + AGENTS.md ("Specification" has one meaning here).
