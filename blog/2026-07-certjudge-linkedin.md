# CertJudge — EN LinkedIn

**TLDR:** Draft LinkedIn announcement for CertJudge (ICML 2026 Math-AI workshop), CoDaPO-style. For co-author review — do not post.

> Links: GitHub = `github.com/brando90/cert-judge` (⚠️ currently PRIVATE — make public first); arXiv = `[TODO]`.
> ⚠️ Post only after acceptance/de-anonymization is public (double-blind submission).
> `[TODO: author list + naming policy — submission anonymized everywhere; Stanford-led credit used below]`

---

We are excited to share our new paper at the ICML 2026 Math-AI workshop: **"CertJudge: Evaluating Lean Formal-Code With Falsifiable Properties"**!

This work was led by researchers at Stanford University. `[TODO: full collaboration credit once the author list is confirmed]`

LLM judges are increasingly used to evaluate AI-generated code, tests, theorems, and formal specifications. In our setting, a judge scores the quality of a candidate Lean 4 artifact against a gold reference — but validating each new judge, prompt, model, or threshold with fresh human ratings is expensive and does not scale. The Lean kernel cannot close the gap either: it checks that a proof is correct, not that the *right* theorem was proposed. We ask: can one human calibration be amortized across every future judge through checks that are automatic and falsifiable?

**First, the certification protocol.**
Instead of treating human agreement as the only validation signal, CertJudge tests whether a judge behaves correctly under controlled perturbations of Lean files — no gold labels required:

➡️ **P1 Identity:** an artifact scored against itself gets the maximum.
➡️ **P2 Bug monotonicity:** scores fall as semantic bugs are injected.
➡️ **P3 Spec monotonicity:** scores fall as theorems/tests are removed.
➡️ **P4 Stability:** scores stay invariant across repeats and semantics-preserving rewrites.

These aggregate into **TI_var**, a variance-aware trust index: unstable judges are penalized, and one failed property collapses the index. Calibration uses a single n=75 candidate–gold panel (one annotator, two rubric passes) and 8 judge configurations per family panel.

**Empirical Results**
- TI_var strongly predicts judge-level human alignment on the primary 8-configuration panel: validation-set Spearman **0.833** (avg labels), **0.905** (pass1), **0.738** (pass2); the trend replicates across the GPT-5.3-Codex, Claude Opus 4.7, and Qwen3-Coder judge families (6 of 9 family/pass combinations exceed 0.7).
- It catches what agreement misses: an intentionally broken judge still reaches ≈0.45 human Spearman yet fails weak monotonicity (12.5%).
- Known failure mode surfaced: aggressive α-renaming scores 0.399 vs ≥0.849 for milder rewrites — LLM judges key on surface strings the Lean kernel ignores.
- Downstream, the certified judge ranks theorem-generation agents on VeriBench: DSPy ReAct 0.615 > Trace++ 0.588 > Trace+ 0.477 > baseline 0.470.

Crucially, these results are validation-set calibration evidence — not a claim of universal reliability; a locked held-out test (5 raters, 343 labels, 78 pairs) is next.

**Explore the work:**
- 📄 Paper: [TODO: arXiv link]
- 💻 GitHub: https://github.com/brando90/cert-judge

We welcome contributions and feedback!

#LLM #LLMasaJudge #FormalVerification #Lean4 #TrustworthyAI #ICML2026 #MachineLearning #OpenSource
