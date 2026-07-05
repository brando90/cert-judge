# CertJudge — EN Twitter / X Thread

**TLDR:** Draft 8-tweet announcement thread for CertJudge (ICML 2026 Math-AI workshop), CoDaPO-style. For co-author review — do not post.

> Requirement: each tweet ≤ 280 characters (checked; counts in PR/email).
> Links: GitHub = `github.com/brando90/cert-judge` (⚠️ repo currently PRIVATE — make public first); arXiv = `[TODO: arXiv link]`.
> Author @-handles intentionally omitted for now. `[TODO: confirm author list — submission is double-blind]`
> ⚠️ Post only after acceptance/de-anonymization is public.

---

1/8: Overview 🚨

LLM judges now grade AI-generated Lean 4 theorems. But who judges the judge? Every judge/prompt/threshold change normally demands a fresh human study. CertJudge amortizes ONE small calibration across every future judge — ρ=0.833 with human agreement. 🧵

---

2/8: The problem 🔍

Judge validation via human agreement doesn't scale: each config change invalidates the last study. And the Lean kernel can't help — it checks proofs, not whether the RIGHT theorem was proposed. Code can typecheck yet be under-specified or vacuous.

---

3/8: The idea 💡

Certify judges with automatic, falsifiable behavioral checks instead of re-labeling:
1️⃣ P1 Identity
2️⃣ P2 Bug monotonicity
3️⃣ P3 Spec monotonicity
4️⃣ P4 Stability
Controlled perturbations of Lean artifacts — no new human labels needed.

---

4/8: The trust index ⚙️

Properties aggregate into TI_var, a variance-aware trust index — unstable judges are penalized; one failed property collapses the index. Calibration: n=75 candidate–gold pairs, single annotator, two rubric passes; 8 configs per judge family.
<!-- attach: pull_fig (pipeline + amortized cost) -->

---

5/8: Results 📊

TI_var predicts judge-level human alignment: validation-set Spearman 0.833 (avg labels), 0.905 (pass1), 0.738 (pass2) on the primary 8-config panel — and the trend replicates across Codex, Opus & Qwen judge families (6/9 family-pass combos >0.7).
<!-- attach: 3-family scatter -->

---

6/8: Catches what agreement misses 🛑

A deliberately broken judge still hits ≈0.45 human Spearman — yet fails weak monotonicity (12.5%). Known failure mode: aggressive α-renaming scores 0.399 vs ≥0.849 for milder rewrites. Judges key on surface strings the kernel ignores.

---

7/8: Downstream + scope 📈

The certified judge ranks theorem-generation agents on VeriBench: DSPy ReAct 0.615 > Trace++ 0.588 > Trace+ 0.477 > baseline 0.470. Scope: validation-set calibration evidence — not universal reliability. A locked held-out test is next.

---

8/8: Open source 🤝

Certify the judge — don't re-label it.
📄 Paper: [TODO: arXiv]
💻 Code: github.com/brando90/cert-judge
ICML 2026 Math-AI workshop. Feedback welcome!

---

## Alternate hooks (pick one for 1/8)

- **Hook A (question-first, above):** "But who judges the judge? …"
- **Hook B (cost-first):** "Validating an LLM judge with a fresh human study for every prompt/model/threshold change doesn't scale. CertJudge: rate a small panel ONCE, then certify every future judge with automatic falsifiable checks. TI_var hits ρ=0.833 with human agreement. 🧵"
- **Hook C (failure-first):** "We built a deliberately broken LLM judge. It still reached ≈0.45 Spearman with humans — agreement alone can't catch it. Our falsifiable property checks did (12.5% weak monotonicity). Meet CertJudge. 🧵"
