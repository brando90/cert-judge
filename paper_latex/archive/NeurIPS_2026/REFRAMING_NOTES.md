# NeurIPS 2026 Idea3 Reframing Notes
**TLDR:** Reframed the 2026 NeurIPS paper around property certification as amortized scalable oversight, and relabeled the current human-rating evidence as development-set evidence of human agreement with held-out test results explicitly in progress.

## Section-by-section changes

- Title: changed to `Trust the Judge: Certifying LLM Judges via Falsifiable Properties`; preserved the previous title as a commented-out line above it.
- Abstract: replaced the abstract with the six-part Idea3 skeleton, using the existing validation numbers: JTI-v1 `rho = 0.881`, permutation `p = 0.008`, pass1/pass2 `rho = 0.810`, P3 `rho = 0.747`, and P2 `rho = 0.714`.
- Section 1 Introduction: rewrote the first three paragraphs to lead with agent-generated code/tests/theorems, per-judge human validation cost, and property certification as an amortized human-agreement assessment protocol.
- Contributions: replaced the prior contribution list with the requested amortized trust-validation protocol, development-set human-agreement result, and VeriBench application bullets.
- Section 3 Methodology: added `Human-Agreement Assessment Protocol` before the LLM-judge motivation paragraph; framed P1--P4 as behavioral targets and JTI as a graded trust index.
- Section 4 Results: renamed the Exp16/Exp17 human-alignment subsection to `Validation-Set Human Alignment`; relabeled captions and prose for Table `tab:exp16_final_trend`, Figure `fig:exp16_exp17_main`, and the Exp16/Exp17 interpretation.
- Section 5 Discussion/Limitations: added `Validation vs. Test Protocol` and `Graded JTI, not binary certification`; strengthened limitations with single-annotator scope, Elyas as planned second annotator, held-out test in progress, BAD_STRINGY behavior, and compositional certification as future work.
- Section 6 Related Work: added `Single-judge certification vs. peer-prediction consensus` to distinguish property certification from TVD-MI-style consensus methods.
- Appendix: renamed `Final Robust Human-Alignment Appendix` to `Validation-Set Human Alignment Appendix` and relabeled the Exp16/Exp17 appendix captions and table text.

## Phrases relabeled

- `human correlation`, `human agreement`, and `human Spearman` for the n=8 judge / n=72 pair results were relabeled to `validation-set human Spearman` or `validation-set human-alignment`.
- `certification score` near Exp16/JTI was relabeled to `JTI`, `trust-index composite`, or `graded property composite`.
- `top certified judges` and `Lower-certification baselines` were relabeled to `top JTI-ranked judges` and `Lower-JTI baselines`.
- Binary-sounding language around JTI was softened: P1--P4 are `behavioral targets`; JTI is a graded signal, not a hard pass/fail gate.
- Appendix diagnostics now say `validation-set` where they discuss the current human-rating labels.

## Deliberately left alone

- No empirical numbers, tables, figures, plots, or experimental methodology were changed.
- The current validation numbers are still reported, but not presented as held-out test evidence.
- No held-out test result was invented; the test split is described as in progress.
- The inductive/edit-graph certification idea remains a future-work sentence only.
- TVD-MI remains related-work context only; no TVD-MI experiments or main-story pivot were added.
- The paper does not claim that humans are insufficient; the framing is that humans are expensive and property checks amortize their annotation cost.

## Open questions for Ethan and Elyas

- Terminology normalization: should the paper keep `development set` in the Idea3 framing and `validation set` in the methodology/results split, or should one term be used everywhere?
- Discussion placement: should `Validation vs. Test Protocol` and `Graded JTI, not binary certification` stay in the main Discussion section, or should some caveat text move to the appendix?
- Limitation wording: should the BAD_STRINGY sentence keep the inline approximate values (`~0.45`, `12.5%`) in the main text, or should that caveat point readers to the appendix diagnostics instead?
