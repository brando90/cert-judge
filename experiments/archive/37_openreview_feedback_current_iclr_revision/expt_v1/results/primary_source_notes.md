# Primary source notes for formal baselines

**TLDR:** The relevant symbolic comparison attempts proofs in both directions; its errors and human-agreement target require careful interpretation. This literature supports a scoped baseline discussion, not a claim that symbolic tools decide arbitrary semantic equivalence.

Verified 09-26-2026 from the original paper and publisher metadata:

- [Poiroux et al., Reliable Evaluation and Benchmarks for Statement Autoformalization (2025)](https://aclanthology.org/2025.emnlp-main.907/).
- [Full paper, version 3, Section 3.1 and Appendix A.6](https://arxiv.org/html/2406.07222v3).
- Section 3.1 describes BEq+ as alternative proof strategies in each implication direction. Appendix A.6 discusses both human-alignment false positives and unsuccessful proof search on equivalent statements.
- Therefore, say a successful proof establishes the submitted logical obligation under its assumptions. Do not equate that result with faithful intent or complete reference coverage, and do not equate a failed attempt with inequivalence.
- Metadata: Auguste Poiroux, Gail Weiss, Viktor Kunčak, Antoine Bosselut; Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing; pages 17947–17969; DOI 10.18653/v1/2025.emnlp-main.907.
