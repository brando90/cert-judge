# Experiment 29 PTI-v0 finalization

**TLDR:** Records the frozen PTI-v0 v5 run, audited negative/inconclusive bridge, sequential Mega-QA, deterministic manuscript, public dependency release, and corrected results publication merged through one direct-to-`main` PR.

## Summary

- Completes the frozen Experiment 29 PTI-v0 v5 subscription-CLI run: 774/774 tasks, 4,728/4,728 score cells, and 14,184 bound records at `$0` provider-API spend.
- Keeps the exact v4 panel explicitly `NOT_RUN` and reports the executed v5 model provenance without a Sonnet-only or observed-Terra claim.
- Adds the independently reconstructed property, criterion, bridge, bootstrap, SESOI, figure-source, and decision artifacts under one self-contained experiment directory.
- Reports the pre-specified primaries-only validation bridge honestly: Spearman `-0.3536`, 95% CI `[-1.0000, 0.3953]`, `n=5`, below the `0.5` SESOI and inconclusive about zero.
- Integrates the audited results into the ICLR 2027 manuscript with anonymized provenance, deterministic PDF generation, and readable tied-point figures.
- Includes the complete sequential Mega-QA prompt, stage records, consolidated verdict, and manuscript visual-QA record.
- Preserves Experiment 27 history from merged [PR #38](https://github.com/brando90/cert-judge/pull/38); its repaired dependency [ultimate-utils PR #44](https://github.com/brando90/ultimate-utils/pull/44) is merged to `master` and [published as 0.10.9](https://pypi.org/project/ultimate-utils/0.10.9/).
- Records the preliminary closeout publisher side effects and one private unlinked noncanonical W&B report; the canonical report and frozen scientific authorities remain unchanged, and duplicate deletion awaits explicit authorization.
- Merged to `main` without claiming deployment readiness, positive validation, certification, causal benefit, human savings, or held-out generalization.

## Test plan

- Run the six PTI/CLI/probe/plot/publisher test modules with the reviewed `uutils` checkout on `PYTHONPATH`; expected result: 83 passed. The dependency's own fail-closed suite has 17 passing tests.
- Run CLI status, byte-compilation, JSON/CSV/schema/hash reconciliation, changed-file secret/direct-provider scans, and deterministic manuscript builds; expected result: all pass with zero provider calls.
- Render and inspect all 22 PDF pages; verify the main-text boundary, references/appendix transition, anonymity, citations, and figure/table readability.

Results: [consolidated Mega-QA report](https://github.com/brando90/cert-judge/blob/main/experiments/29_proxy_validation/MEGA_QA_REPORT.md) · [W&B report](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-29-%E2%80%94-PTI-v0-v5-outer-bridge--VmlldzoxNzgyMzE2MA==)
