# Pseudo-Formalization Summary And Cert-Judge Contrast
**TLDR:** PF+BV rewrites natural-language mathematical proofs into explicit premise/conclusion/proof modules and asks an LLM to verify each block. Cert-judge is complementary: it certifies whether a Lean-aware LLM judge behaves reliably on theorem/specification scoring tasks through falsifiable properties.

## Paper Metadata

- Paper: "Pseudo-Formalization for Automatic Proof Verification"
- Authors: Slim Barkallah, Luke Bailey, Kaiyue Wen, Mohammed Abouzaid, Tengyu Ma
- Source: [arXiv:2605.20531](https://arxiv.org/abs/2605.20531), submitted 2026-05-19
- Code: [Slim205/pseudo-formalization](https://github.com/Slim205/pseudo-formalization)

## One-Paragraph Summary

The paper introduces Pseudo-Formalization (PF), a structured natural-language proof format made of modules with explicit premises, conclusions, and proofs, plus dependency and scope structure.
Its Block Verification (BV) pipeline translates a natural-language proof into PF, optionally checks/repairs faithfulness, verifies each module independently with an LLM, aggregates block errors through a calibration model, and combines repeated runs pessimistically.
The paper evaluates PF+BV on Hard2Verify and the new ArxivMathGradingBench, a set of 35 arXiv math papers with 40 author-corrected errors, and reports better precision/recall trade-offs than direct LLM-as-judge proof verification.

## Key Method Points

- Representation: proof modules are natural-language tuples of premises, conclusion, and proof, organized by dependency and scope structure.
- Verification: the verifier checks one module at a time, using already verified dependencies as local context.
- Aggregation: repeated verifier rollouts are combined pessimistically, so one flagged error can reject a proof.
- Benchmarking: Hard2Verify supplies step-level proof labels; ArxivMathGradingBench supplies research-paper errors disclosed in later author corrections.
- Baseline: the main comparison is direct LLM-as-judge verification over the original proof.

## Similarities To Cert-Judge

| Axis | PF+BV | cert-judge |
|---|---|---|
| Motivation | Scale proof checking beyond manual review. | Scale trust in LLM judges beyond manual label collection. |
| Use of LLMs | LLM translates, verifies blocks, and calibrates verdicts. | LLM acts as theorem/specification judge; cert-judge tests the judge. |
| Target risk | A verifier may miss or hallucinate proof errors. | A judge may be inconsistent, non-monotone, unstable, or misaligned with humans/provers. |
| Structured checks | Decomposes a proof into local blocks before judging. | Decomposes judge trust into P1-P7 behavioral and alignment properties. |
| Repetition | Uses multiple independent runs with pessimistic aggregation. | Tests repeat stability and can evaluate repeat/aggregation choices as judge configurations. |
| Scalable oversight framing | Makes proofs more legible to a weaker verifier. | Makes judge reliability legible through falsifiable properties and a Trust Index. |

## Differences From Cert-Judge

| Axis | PF+BV | cert-judge |
|---|---|---|
| Primary object | Natural-language mathematical proof. | Lean 4 theorem/specification judge configuration. |
| Main output | Proof verdicts and localized error reports. | Property scores and Judge Trust Index for a judge. |
| Verification guarantee | Explicitly relaxes full formalization; no Lean kernel guarantee for PF blocks. | Anchors scoring tasks in Lean artifacts, gold references, bug ladders, spec-ablation ladders, and prover/human validation where available. |
| Method target | Improve a verifier by rewriting the proof into an easier-to-check format. | Certify whether a chosen verifier/judge is reliable enough to use. |
| Calibration role | A calibration LLM maps block reports to an accept/reject decision or strictness level. | Calibration relates judge behavioral properties to expected human/prover alignment across model/prompt/repeat configurations. |
| Evaluation data | Hard2Verify and ArxivMathGradingBench with known proof errors. | VeriBench-style Lean file pairs, identity pairs, bug ladders, missing-spec ladders, stability repeats, TVD-MI-style diagnostics, and human/prover alignment panels. |
| Failure mode addressed | Whole-proof LLM grading loses local context on long mathematical proofs. | LLM judges can look plausible while failing identity, monotonicity, stability, or cross-configuration reliability checks. |

## Paper-Facing Takeaway

PF+BV is useful related work because it attacks the same broad oversight problem -- how to get reliable automated judgments about hard mathematical reasoning -- but at a different layer.
It is not a competing judge-certification protocol.
It improves the artifact submitted to a verifier by pseudo-formalizing a natural-language proof; cert-judge improves trust in the verifier/judge itself by testing its behavior on controlled Lean-aware perturbations.
The clean contrast is "make proofs easier to judge" versus "certify the judge before using it."

## Integration Decision

The contrast is real and useful.
The appendix should cite PF+BV, but the paragraph should be short and avoid overstating overlap with code-to-Lean autoformalization.
The safest claim is that PF+BV is complementary: it provides a structured natural-language proof-verification pipeline and a research-proof benchmark, while cert-judge and VeriBench certify/evaluate Lean-artifact scoring and code-formalization workflows.
