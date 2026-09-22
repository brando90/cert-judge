# PTI-v0 on other Lean 4 benchmarks (Verina, Vero, ...)

**Execution:** DEFERRED — NOT RUN · **Paper inclusion:** UNDECIDED · **Recorded:** 09-22-2026 · **Issue:** <https://github.com/brando90/cert-judge/issues/45>

## Hypothesis

The CertJudge protocol is not VeriBench-specific: on a second Lean 4 benchmark, the PTI-v0 probes (bug ladder, missing-specification ladder, exact equality, alpha-renaming) can be built from its golds, and the judge ordering by PTI-v0 agrees with the VeriBench ordering.

## Motivation

The ICLR 2027 abstract (`paper_latex/ICLR_2027_submission/main.tex:115`) says "Applied to \textsc{VeriBench}, the protocol illustrates development-set human agreement ...".
Reviewers will likely ask "why only VeriBench, not Verina or Vero?".
The ICML workshop reviews (`experiments/18_icml_reviews/pre_prompt.md`) did not name another benchmark, but raised the neighbouring concern:
generalization "to new human raters, new Lean domains, or unseen judge families" (line 103), "domain-specific semantic mismatch" (line 135), and "other proof assistants or formal languages beyond Lean 4" (line 229).
The ICML camera-ready plan deferred this to future work (`experiments/18_icml_reviews/agent_prompt.md:48`).

## Candidate benchmarks

- Verina — arXiv:2505.23135 (Lean 4, per-problem code + formal specification + proof).
- Vero — arXiv:2608.13522, <https://github.com/sunblaze-ucb/vero> (repository-level Lean 4, 43 instances, 2,705 specifications; multi-module, so probe builders need adaptation).
- VeriContest — arXiv:2605.08553 (competitive-programming verifiable code generation); others to be checked.

## Minimal comparison

1. **Proxy only (no new human labels):** build PTI-v0 probes from Verina golds with the frozen builders in `py_src/cert_judge/probe_validation.py`; score the existing judge panel; report per-property PTI-v0 and the cross-benchmark Spearman of judge rankings (VeriBench vs. Verina).
2. **Optional criterion check:** a small human-labeled Verina panel to test whether the TI_var association with human agreement carries over.

## Key uncertainty

Whether Verina/Vero golds elaborate under our Lean toolchain and fit the probe builders (the bug ladder mutates implementation `def`s; the missing-specification ladder removes theorem statements and unit tests), and whether we have or must generate candidate artifacts on those benchmarks.
Paid judge inference needs an exact call/cost quote and explicit approval before running.

## Revisit condition

After the ICLR main text is frozen, or immediately if reviewers ask for another benchmark during rebuttal.
