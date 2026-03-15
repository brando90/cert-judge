# Review Summary — NeurIPS 2025 Workshop MATH-AI (Submission #161)

**Paper:** Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean 4
**Venue:** NeurIPS 2025 MATH-AI Workshop
**OpenReview:** https://openreview.net/forum?id=9WAWDdwqpC

---

## Overall Outcome

| Reviewer | Rating | Confidence | Verdict |
|----------|--------|------------|---------|
| ivJs | 6 / 10 | 4 / 5 | Marginally above acceptance threshold |
| 36Hd | 3 / 10 | 3 / 5 | Clear rejection |

---

## Reviewer ivJs (Rating: 6 — Marginally Accept)

**Positives:**
- Praised the certification methodology as principled and novel — falsifiable property-based validation (identity + monotonicity) goes beyond typical human correlation studies.
- Strong empirical results: R²=1.000 for identity, high negative correlations for monotonicity.
- Addresses a genuine bottleneck in evaluating agentic systems that synthesize formal specifications.

**Concerns:**
- **Generalization**: Certification uses finite perturbations on one benchmark; unclear how it handles novel theorem types or adversarial cases.
- **Single architecture**: No comparison with other LLM judges or ensemble methods limits generality claims.
- **No human validation**: Doesn't confirm judge alignment with expert human assessments of theorem quality.

---

## Reviewer 36Hd (Rating: 3 — Clear Rejection)

**Positives:**
- Recognizes the specification adequacy problem as important in formal verification.
- Using an LLM for this gap seems natural.

**Main Criticisms:**
- **Missing details**: Judge implementation details are sparse — just Claude 3.5 or 3.7 with no further description. Unclear why different models are used in Section 3 vs. Section 4.
- **Weak experiments (Section 3)**: Identity/monotonicity tests resemble edit distance over strings more than the real problem; severity of changes is not accounted for in monotonicity.
- **Unclear agentic setup (Section 4)**: Input/output and role of DSPy/Trace are not explained; it is unclear how Lean 4 is actually used.
- **Novelty concern**: Using an LLM as a judge is not novel on its own.

**Specific Fixes Requested:**
- Monotonicity should not be defined as a strict ordering (Section 3).
- Figure 1 is unreadable.
- Figure 1: `vs.` should be `w.r.t.`
- Missing references in Appendix.
- Appendix B: "Lean 4 verus Verus" (typo).
- Appendix C: `**` (incomplete text).

---

## Key Themes to Address for Revision

1. **Clarify implementation details** — specify exactly which Claude model is used where and why, and provide a clear description of judge inputs/outputs.
2. **Strengthen Section 4** — explain the agentic setup: how DSPy/Trace are used, what Lean 4's role is, what the input/output pipeline looks like.
3. **Improve monotonicity framing** — account for severity of perturbations; avoid strict ordering definition.
4. **Add generalization analysis** — discuss limitations of finite perturbation-based certification and how the method extends to novel theorem types.
5. **Fix all typos and figure readability** — especially Figure 1.
