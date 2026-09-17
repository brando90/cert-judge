# Experiment 29 final Mega-QA report

**TLDR:** Experiment 29 and its ICLR 2027 manuscript passed the original sequential Mega-QA after 13 proven stage fixes and one publication synchronization. A 2026-08-31 integration audit qualified accepted-task provenance wording and added fail-closed provenance and repeat-alignment tests without changing any frozen scientific value. The 2026-09-10 closeout published ultimate-utils 0.10.9, updated the canonical W&B report in place, resolved the dependency lock, and recorded the already-merged `main` state. The result itself remains negative/below-SESOI and inconclusive—not a deployment or generalization pass.

- Date completed: 2026-08-28 (America/Los_Angeles)
- Integration audit completed: 2026-08-31 (America/Los_Angeles)
- Release closeout: 2026-09-10 (America/Los_Angeles)
- Experiment home: `experiments/29_proxy_validation/`
- Canonical branch: `main`
- Canonical pull request: [cert-judge #40](https://github.com/brando90/cert-judge/pull/40), merged directly into `main` at `03946b83d85af2530971322ec6dfcdba80e0bacd`
- Permanent results report: [Experiment 29 — PTI-v0 v5 outer bridge](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-29-%E2%80%94-PTI-v0-v5-outer-bridge--VmlldzoxNzgyMzE2MA==)

## Sequential review chain

| Stage | Fresh reviewer | Result | Proven fixes | Record |
|---|---|---:|---:|---|
| 1 | Claude Fable 5, effort `max` | `FIXED`; 0 critical, 4 major; structural `PASS` | 10 | `MEGA_QA_FABLE.md` |
| 2 | Codex GPT-5.6-Sol, effort `xhigh` | `FIXED`; 0 critical, 0 major; structural `PASS` | 1 | `MEGA_QA_CODEX.md` |
| 3 planned attempt | Claude Fable 5, effort `max` | No verdict or edit: HTTP 429 weekly quota exhaustion after approximately 24.5 minutes | 0 | Recorded here as a degraded stage attempt |
| 3 fail-closed substitute | Codex GPT-5.6-Sol, effort `xhigh` | `FIXED`; 0 critical, 0 major; structural `PASS` | 2 | `MEGA_QA_FINAL_CODEX.md` |

The planned final Claude stage was not silently skipped. It ran until the service returned a hard weekly-quota error with no verdict. The workflow then used a fresh-context Codex substitute, documented the degradation, and required that substitute to repeat the full end-to-end reconstruction.

## Release evidence

- Scoring execution: 774/774 accepted subscription-CLI tasks.
- Score coverage: 4,728/4,728 unique cells and 14,184 bound records.
- Derived coverage: 100% for all property and 72-row criterion outputs; zero invalid or quarantined accepted tasks.
- Provider API spend: `$0`; no provider API was used during Mega-QA.
- Exact v4 model panel: `NOT_RUN`.
- Actual v5 disclosure: Codex was requested with `-m gpt-5.6-terra`, but its JSONL has no served-model field; Claude requested/scored `claude-sonnet-5`, with auxiliary `claude-haiku-4-5` telemetry on all 258 accepted Claude invocations.
- Primary validation bridge: Spearman `-0.3535533906`, Kendall tau-b `-0.3162277660`, 95% judge-bootstrap interval `[-1.0, 0.3952847075]`, 6,647/10,000 valid replicates, `n=5`.
- Power at the frozen `0.5` SESOI: 27.1% for the complete positive decision rule.
- Test suite: 83 passed with the documented `uutils` dependency path (81 scientific/pipeline tests plus two release-closeout publisher tripwires).
- Manuscript: 22 letter-size pages; conclusion/statements/references begin or end on page 9 as documented, appendix begins on page 13, and all pages passed visual inspection.
- Deterministic manuscript PDF SHA-256: `a35e582f936635dbdf6d21b1a17aba27ad5d5d9494d5459b7c477da8ba23644` after the accepted-task wording correction; the reviewed pre-integration build was `4fc679f36cd4d33f7e2ccc3788b9c98d4c19cc6723456cbe2c73f660dbf53718`.
- W&B publication: the canonical report was updated in place on 2026-09-10 with the accepted-task provenance wording, readable tied-point figure, exact protocol label, requested-not-observed Terra disclosure, and no held-out-generalization claim. The publisher now validates the report target before other mutations, defaults to report-only operation, and requires an explicit full-publication flag for run/artifact logging.
- W&B closeout audit: before those safeguards were added, one preliminary full-mode invocation resumed/logged the eight judge runs and summary run, created artifact version `v2`, and created private unlinked duplicate report `VmlldzoxNzkxMDU2OA==`. The duplicate remains pending explicit deletion authorization; it is noncanonical and did not alter any frozen local scientific authority.

## Frozen-authority hashes

| Authority | SHA-256 |
|---|---|
| `results/scores.json` | `c51a2ee78c7552af3c021a666ad1c55ba6eeed65f4a91c79d1b0a41d7f36e6c1` |
| `results/properties/property_table.csv` | `7a904f31a6dbd626a728e44fd7a00043c61b5e1630937986f111a0be4af15c0a` |
| `results/bridge/bridge_pti_v0.json` | `8213e21dfe91fd0a7bf0ab0b3906f89139b3ff4f66f52df5406ade629515bc5b` |
| `results/figures/outer_bridge_source_data.json` | `99fdd99b9eaaf10effcce3b1515b56b2394da8f21b1028005a646f62f49b8f1e` |
| Original planning archive | `7362ab1d1dcc9161fefca3aff87c33276b71941a647f2bd2b7f8e176509d6859` |

No frozen configuration, raw accepted transcript, normalized score, property, criterion, bridge, SESOI, or figure-source value changed during Mega-QA.

## Post-handoff integration audit

The 2026-08-31 audit independently reconstructed all execution counts, score bindings, coverage values, bridge statistics, bootstrap interval, SESOI power, and frozen hashes. It found no critical or major numerical defect. It tightened claims from all Claude calls to all 258 accepted Claude tasks because retry and failed-attempt evidence proves more attempt-level invocations, and it changed the future runner to leave `usage.observed_model` null when Codex emits no served-model header. A dependency audit also made repeat-score coverage and item identity fail closed. Frozen raw artifacts remain untouched. The two integration-audit regression tests raised the five-module total from 79 to 81. The wording-only manuscript rebuild is deterministic and passed a fresh all-page visual inspection. On 2026-09-10, the corrected W&B script updated the canonical report in place through its report-only path; two additional tripwire tests now prove that report-only mode performs no run/artifact writes and that a mismatched report target fails before any full-mode mutation.

## Fix summary

The 13 stage fixes addressed an occluded tied point in the headline figure, removal of a legacy raster with unsupported certification/savings text, the required AI-use heading, deterministic PDF bytes, precise retry accounting, stale paths and protocol labels, citation punctuation, legacy appendix labeling, Terra provenance wording, and the false held-out-generalization characterization. The final release pass then synchronized those proven corrections to the W&B script and report. The figure source data and all scientific values remain unchanged.

## Decision

The execution and evidence package are complete and audit-ready. Scientifically, the result fails to establish the intended positive surrogate bridge: the point estimate is negative, the interval includes zero, its upper endpoint is below the `0.5` SESOI, and the five-judge design has only 27.1% power at that SESOI. A positive bridge, PASS-SCREEN threshold, deployment claim, causal claim, human-savings claim, or held-out generalization claim requires a new independently frozen experiment.

```text
VERDICT: FIXED
CRITICAL_ISSUES: 0
MAJOR_ISSUES: 0
FIXES_APPLIED: 14
STRUCTURAL: PASS
SUMMARY: The complete Experiment 29 evidence and manuscript passed three completed fresh-context reviews, with a documented Claude-quota substitution and no unresolved critical or major defects. Thirteen stage fixes plus one final publication synchronization preserve the audited negative/below-SESOI and inconclusive conclusion.
```
