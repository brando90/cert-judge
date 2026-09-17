**Thesis:** Certify (falsify or validate) an LLM-based judge for scoring AI-generated Lean 4 theorems by verifying it satisfies fundamental logical properties — identity and monotonicity.

---

## Points to Address (Reviewers ivJs + 36Hd)

### Substantive

- [ ] Explain why Claude 3.5 is used in Section 3 and Claude 3.7 in Section 4 (and both in Appendix D); justify or unify the model choice.
- [ ] Provide full judge implementation details: exact model, prompt structure, input format (what two things are compared), output format (score + reasoning?).
- [ ] Clarify Section 4 agentic setup: what is the input/output pipeline, how DSPy/Trace are used, and how Lean 4 compilation/checking is actually invoked.
- [ ] Reframe monotonicity: drop strict-ordering definition; account for severity of perturbations (not all changes are equal).
- [ ] Address the "edit distance" critique: argue why identity/monotonicity tests are non-trivial proxies for the real alignment problem, not just string similarity.
- [ ] Discuss generalization limits: finite perturbations on one benchmark — how does certification extend to novel theorem types or adversarial inputs?
- [ ] Compare against at least one other LLM judge or baseline to support generality claims (or explicitly scope the claim).
- [ ] Add or discuss human validation: do expert assessments agree with the judge on at least a subset of pairs?
- [ ] Address novelty: position the *certification protocol* (not the judge itself) as the contribution — the judge being an LLM is intentional, the certification methodology is new.

### Presentation / Typos

- [ ] Fix Figure 1 readability (too small / unreadable).
- [ ] Figure 1: change `vs.` → `w.r.t.`
- [ ] Appendix B: fix typo "Lean 4 verus Verus" → "versus".
- [ ] Appendix C: fix incomplete text `**`.
- [ ] Add missing references in the Appendix.

---

**TL;DR:** Address missing judge/pipeline details, reframe monotonicity, justify model choices, and fix Figure 1 + typos to respond to both reviewers.
