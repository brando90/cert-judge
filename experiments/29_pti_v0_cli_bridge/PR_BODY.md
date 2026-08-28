# Experiment 29 PTI-v0 finalization

**TLDR:** Completes the frozen PTI-v0 v5 run, audited negative/inconclusive bridge, sequential Mega-QA, deterministic manuscript, and corrected results publication in one direct-to-`main` PR.

## Summary

- Completes the frozen Experiment 29 PTI-v0 v5 subscription-CLI run: 774/774 tasks, 4,728/4,728 score cells, and 14,184 bound records at `$0` provider-API spend.
- Keeps the exact v4 panel explicitly `NOT_RUN` and reports the executed v5 model provenance without a Sonnet-only or observed-Terra claim.
- Adds the independently reconstructed property, criterion, bridge, bootstrap, SESOI, figure-source, and decision artifacts under one self-contained experiment directory.
- Reports the pre-specified primaries-only validation bridge honestly: Spearman `-0.3536`, 95% CI `[-1.0000, 0.3953]`, `n=5`, below the `0.5` SESOI and inconclusive about zero.
- Integrates the audited results into the ICLR 2027 manuscript with anonymized provenance, deterministic PDF generation, and readable tied-point figures.
- Includes the complete sequential Mega-QA prompt, stage records, consolidated verdict, and manuscript visual-QA record.
- Preserves Experiment 27 history from [PR #38](https://github.com/brando90/cert-judge/pull/38); the plotting tests use the open [ultimate-utils PR #44](https://github.com/brando90/ultimate-utils/pull/44) checkout on `PYTHONPATH`.
- Does not merge, claim deployment readiness, or claim positive validation, certification, causal benefit, human savings, or held-out generalization.

## Test plan

- Run the five PTI/CLI/probe/plot test modules with the documented `uutils` checkout on `PYTHONPATH`; expected result: 79 passed.
- Run CLI status, byte-compilation, JSON/CSV/schema/hash reconciliation, changed-file secret/direct-provider scans, and deterministic manuscript builds; expected result: all pass with zero provider calls.
- Render and inspect all 22 PDF pages; verify the main-text boundary, references/appendix transition, anonymity, citations, and figure/table readability.

Results: [consolidated Mega-QA report](https://github.com/brando90/cert-judge/blob/codex/iclr2027-final/experiments/29_pti_v0_cli_bridge/MEGA_QA_REPORT.md) · [W&B report](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-29-%E2%80%94-PTI-v0-v5-outer-bridge--VmlldzoxNzgyMzE2MA==)
