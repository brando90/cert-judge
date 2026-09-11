# Experiment 29 PTI-v0 results

**TLDR-start:** [cj: pti-v0] Experiment 29 v5 is complete: 774/774 CLI tasks, 4,728/4,728 cells, and `$0` provider-API spend. The primary outer bridge is Spearman `-0.3536` with 95% CI `[-1.0000, 0.3953]` (`n=5`), below the preregistered `0.5` SESOI and inconclusive about zero. This does not support a positive PTI-v0 bridge.

**Status:** COMPLETE — integrated on `main`
**Last updated:** 2026-09-10 14:44 PDT

Latest authoritative local report:
[results_summary_2026-08-26__03-40-50.md](expt_v5/results/results_summary_2026-08-26__03-40-50.md)

Permanent W&B Report:
[Experiment 29 — PTI-v0 v5 outer bridge](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-29-%E2%80%94-PTI-v0-v5-outer-bridge--VmlldzoxNzgyMzE2MA==)

Release state:

- cert-judge pull requests #38 and #40 are merged into `main`.
- [ultimate-utils 0.10.9](https://pypi.org/project/ultimate-utils/0.10.9/) is public, and the tracked dependency lock resolves that exact release.
- The canonical W&B report was updated in place with the accepted-task provenance wording on 2026-09-10.
- One preliminary full-mode closeout invocation resumed/logged the nine existing runs, created artifact version `v2`, and created a private unlinked noncanonical report (`VmlldzoxNzkxMDU2OA==`). The duplicate awaits explicit deletion authorization; the canonical report and frozen local result authorities are unchanged.

Key facts:

- Four of five primary `PTI_v0` values are exact zero; Sonnet + P8 is `0.8114`
  (95% artifact bootstrap `[0.7820, 0.8391]`).
- Pooled controls are also below-SESOI/inconclusive: Spearman `-0.2474`, 95% CI
  `[-0.8165, 0.2568]`, `n=8`.
- The frozen positive-decision power at a true Spearman `0.5` is only `27.1%`.
- Exact v4 is `NOT_RUN`; these are v5 results from `gpt-5.6-terra` and requested/
  scoring `claude-sonnet-5`.
- Claude telemetry records an auxiliary `claude-haiku-4-5` helper on all 258
  accepted Claude CLI tasks; Sonnet-only execution is not claimed.
- Codex CLI telemetry exposes no served-model field; the `gpt-5.6-terra`
  identity rests on the hash-bound explicit `-m` argument and the CLI's
  rejection of unsupported model IDs.
- Independent numerical QA passed and retained that provenance issue as one
  major limitation.

Decision implications:

- **Supported now:** an honest measurement/audit paper reporting a failed
  positive bridge, exact-zero failure modes, wide judge-level uncertainty, and
  an underpowered five-judge outer validation.
- **Not supported now:** claiming PTI-v0 is positively validated, setting a
  deployment/PASS-SCREEN threshold, claiming causal effects, or claiming saved
  human-validation effort.
- **If a positive validation result is required:** run a separately frozen
  follow-up with a substantially larger independent judge panel and repair or
  redesign the zero-saturating property probes before revealing its bridge.
- **Exact-v4 replication:** remains optional future work if the registered
  model identifiers become executable; it is not needed to inspect or reproduce
  this v5 result.

**TLDR-end:** [cj: pti-v0] The run itself is complete and audited; its scientific outcome is below-SESOI and inconclusive, so it cannot justify a positive bridge, a deployment threshold, or a human-validations-saved claim.
