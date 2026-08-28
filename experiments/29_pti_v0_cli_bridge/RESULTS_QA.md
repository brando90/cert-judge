# PTI-v0 v5 independent results QA

**TLDR-start:** [cj: pti-v0] A fresh Codex Sol read-only audit reproduced the complete score inventory, every property and criterion statistic, all bootstrap summaries, and the CSV/JSON bindings. The audit recorded one major provenance limitation: all accepted Claude CLI runs disclose a small auxiliary `claude-haiku-4-5` call alongside the requested and scoring `claude-sonnet-5` model.

## Verdict

`FAIL` under the literal preregistered claim that only the exact requested model
appears in execution telemetry. Numerical and structural QA passed.

- Critical issues: 0
- Major issues: 1 (Claude auxiliary-model provenance)
- Structural status: PASS
- Fixes applied to frozen artifacts: 0

This finding does not permit a post-result change to the metric, scores, judge
IDs, or frozen config. Downstream reports must describe the Claude execution as
Sonnet scoring with a CLI-internal Haiku helper and must not claim
"Sonnet-only" execution or claim that the helper was proven unable to affect
execution.

## Reproduced checks

- Pre-result authority: commit `395efdc00584cad32f6e9a525a8dbd9b201ff2a7`.
- Frozen inputs and runner matched that commit with no tracked drift.
- CLI tasks: 774/774 accepted; 129/129 for each of six LLM configurations.
- Cells: 4,728/4,728 complete; 3,546 nonlocal cells and 1,182 local controls.
- Records: 14,184, with exactly repeats `{0,1,2}` per cell.
- Invalid/quarantined accepted tasks: 0/0.
- Historical failed attempts: 4; all excluded and replaced by validated accepted
  artifacts.
- Authentication: ChatGPT subscription and first-party `claude.ai` Max
  subscription; provider API spend recorded as `$0`.
- Structural sets: `P_eq=86`, `P_bm=49`, `P_ms=63`, `P_eqalpha=67`, all at
  100% score coverage.
- Property outputs: all eight JSON/CSV rows and 896 ladder diagnostics
  reconstructed with the canonical implementation.
- Exact-zero behavior: every zero property contains at least one observed
  exact-zero factor; no missing value was converted to zero.
- Property bootstrap: all requested 10,000 replicates reproduced.
- Human criterion: 72 unique paired artifact clusters; exact three-repeat
  medians; all 24 tie-aware Spearman/Kendall judge-view estimates reproduced.
- Criterion bootstrap: all eight primary average-view 10,000-replicate paired
  cluster bootstraps reproduced.
- Property-table SHA-256:
  `7a904f31a6dbd626a728e44fd7a00043c61b5e1630937986f111a0be4af15c0a`.

Focused read-only reviewer tests: `31 passed, 2 deselected`. The excluded tests
required temporary-file writes; the reviewer replaced them with stronger
in-memory whole-artifact reconstruction checks. The builder's writable test
suite is run separately before the pre-bridge commit.

## Provenance limitation

All 258 accepted Claude batch-repeat artifacts report both canonical model IDs:

```text
claude-sonnet-5
claude-haiku-4-5
```

The Sonnet entry contains the scoring output. The Haiku entry is consistently
small and appears in structured-output/tool-schema handling. Claude tools were
disabled, `permission_denials` and server web-tool counts were empty, and
subagent count was zero. That evidence supports an auxiliary-helper
interpretation but cannot establish non-influence. A representative accepted
artifact is
`results/raw_batches/a0f9cc99d0f563c202941aab6ad1d905399be37cafd0682273591863e0885e03__r0.json`.

Codex accepted 516 invocations requested as `gpt-5.6-terra`; the Codex JSONL exposes no served-model field, so Terra is requested-by-argument rather than observed telemetry.

## Gate decision

The numerical hard gate is open (`bridge_allowed=true`). The independent audit
does not authorize an exact-model-only claim. The property table must be
committed byte-identically before the bridge command is run, and all bridge,
W&B, figure, and manuscript outputs must carry this provenance disclosure.

**TLDR-end:** [cj: pti-v0] Numerical and structural artifacts reconcile exactly; the sole major QA finding is transparent auxiliary Haiku telemetry in every Claude CLI run, which is retained and disclosed rather than rewritten.
