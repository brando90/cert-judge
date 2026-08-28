# Final Mega-QA stage record — Codex GPT-5.6-Sol substitute (fresh context)

**TLDR:** The final fresh-context review independently reconstructed the complete frozen evidence bundle, verified the live PR topology and manuscript, and corrected two material claim-language defects. No unresolved critical or major issue remains, and no frozen scientific authority changed.

- Date: 2026-08-28 (America/Los_Angeles)
- Reviewer: Codex GPT-5.6-Sol, fresh ephemeral session, reasoning effort `xhigh`
- Role in chain: fail-closed substitute for the planned final Claude Fable 5 stage after Claude returned HTTP 429 weekly-quota exhaustion without a verdict or edit
- Baseline: `codex/iclr2027-final` at `ab791cf35995a9386d1fdb2d846c56dd1affeb03` over `origin/main` `b488de9fc11e87952e05e9e4ecfff38dafbe0c17`; draft PR #40
- Scope: correctness and structural QA only; no scoring rerun, provider API, Git mutation, credential access, or external-service mutation

## Independent reconstruction

- Rebound every accepted raw task to the frozen requests and rebuilt the normalized inventory: 774/774 tasks, 4,728/4,728 unique cells, 14,184 records, 10,638 LLM bindings, 3,546 deterministic local-control bindings, zero invalid accepted tasks, and zero quarantined tasks.
- Recomputed median repeat aggregation, all four PTI properties, 896 ladder diagnostics, 80,000 property-bootstrap series, 24 criterion views and 240,000 criterion-bootstrap series, both headline bridges, per-property and role sensitivities, leave-family-out behavior, and all nine SESOI rows.
- Reproduced the primary bridge exactly: Spearman `-0.3535533906`, Kendall tau-b `-0.3162277660`, 95% judge-bootstrap interval `[-1.0, 0.3952847075]`, 6,647/10,000 valid replicates, `n=5`.
- Reproduced the complete positive-rule power at the `0.5` SESOI: 27.1% of 10,000 simulations.
- Regenerated `score_requests.json`, `batch_manifest.json`, and `criterion_manifest.json` byte-for-byte; parsed 793 JSON files and five CSV authorities with strict shape and schema checks.
- Verified frozen hashes, score/property/criterion bindings, raw artifact hashes, planning archive, figure source data, and the commit order `395efdc` (freeze) → `6f55c44` (properties) → `540c43f` (bridge).
- Verified exact v4 is `NOT_RUN`; the actual v5 execution disclosures include auxiliary `claude-haiku-4-5` telemetry on all 258 accepted Claude invocations and do not claim Sonnet-only execution.
- Ran the dependency-aware suite: 79 passed. Python byte-compilation, CLI status, changed-file secret/direct-provider scans, and live PR #40 topology passed.
- Built the manuscript deterministically twice, yielding the byte-identical 22-page PDF SHA-256 `4fc679f36cd4d33f7e2ccc3788b9c98d4c19cc6723456cbe2c73f660dbf53718`; every page was rendered and visually inspected.

## Proven fixes

1. Experiment 29 was described as “held-out across judges,” although the frozen configuration identifies a validation analysis and disclaims held-out generalization. Active Experiment 29 reports and the paper now call it a pre-specified judge-level validation analysis and explicitly deny an out-of-sample or held-out generalization claim.
2. `RESULTS_QA.md` called `gpt-5.6-terra` requested/observed even though Codex JSONL has no served-model field. It now states that Terra is bound by the explicit CLI argument rather than observed served-model telemetry.

The reviewer's first scratch manifest assertion and one overly strict report-reconciliation assertion were corrected inside the temporary audit harness. They were reviewer-harness defects, not repository or evidence defects, and caused no repository change.

## Scientific assessment

The frozen v5 run is complete and reproducible. Its bridge is negative, below the `0.5` SESOI, and inconclusive about zero. It does not support positive validation, PASS-SCREEN thresholds, deployment, certification, causal, human-savings, or held-out generalization claims. Those require a separately frozen follow-up with a larger judge panel and repaired zero-saturating probes.

```text
VERDICT: FIXED
CRITICAL_ISSUES: 0
MAJOR_ISSUES: 0
FIXES_APPLIED: 2
STRUCTURAL: PASS
SUMMARY: Independent reconstruction validated the frozen negative/inconclusive result, and two material report-language defects were corrected with no unresolved critical or major issues.
```

**TLDR-end:** [cj: pti-v0 mega-QA] The final substitute stage passed after two evidence-wording corrections; all frozen numerics, provenance bindings, tests, PR topology, and 22 manuscript pages were independently verified.
