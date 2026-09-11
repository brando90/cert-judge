# PTI-v0 CLI protocol v5 (frozen before benchmark scoring)

This protocol preserves the PTI-v0 mathematical, probe, panel, missingness,
bootstrap, and bridge contracts frozen in experiment 04 v4. It replaces only
the execution/model panel because the approved ChatGPT-backed Codex CLI rejects
both v4 model IDs (`gpt-5.3-codex` and `gpt-4o-mini`) and repository Hard Rule 9
forbids the non-Brando-authored compatible provider caller.

## Frozen judge panel

Five primaries:

- `gpt-5.6-terra|P8_STRICT_B`
- `gpt-5.6-terra|P4_CHECKLIST`
- `gpt-5.6-terra|P1_BASELINE`
- `claude-sonnet-5|P8_STRICT_B`
- `claude-sonnet-5|P4_CHECKLIST`

Three controls:

- `gpt-5.6-terra|BAD_STRINGY`
- `editdist_e1`
- `random_r1`

The exact machine-readable authority is `frozen_config.json`. Workload effort
is `low`: these are bulk judge calls, not reasoning/QA dispatches.

## Execution contract

- LLM work uses only locally authenticated `codex exec` and `clauded`.
- There is no provider SDK, HTTP client, LLM key path, or environment-key read.
- Before either child starts, the runner removes every inherited `*_API_KEY`
  variable plus explicit provider-key names and verifies ChatGPT/claude.ai
  subscription authentication with each CLI's non-inference auth-status command.
- Every repeat is a fresh ephemeral CLI process.
- Decoding uses each subscription CLI's default sampling because this protocol
  has no stable provider-temperature control; repeat variation is measured from
  three fresh processes and this is an execution departure from v4.
- Cases are packed deterministically into artifact-disjoint batches: no two
  score cells for the same typed artifact can occur in one prompt. Each batch
  has no more than 16 cases or 180,000 UTF-8 prompt bytes.
- The same fixed batch assignment is used for all three independent repeats.
- The batch wrapper explicitly requires independent case scoring; batching is
  an execution limitation and is reported as such, never conflated with v4.
- Every response is structured-output constrained, checked for exact IDs,
  uniqueness, finiteness, range, and one result per case, then atomically saved.
- Codex JSONL is rejected if it contains command, file, MCP, or web-tool use;
  Claude runs with safe mode and an empty tool set. CLI stdout/stderr transcripts
  and model-usage provenance are retained beside every accepted raw batch.
- Exhausted/invalid batches remain missing; no `0.5` or other fallback is used.
- The run is resumable from validated raw batch artifacts.
- Provider API spend is exactly `$0`; subscription usage/token telemetry is
  retained when the CLI exposes it.

Batching is an execution-level departure from v4's one-case calls. The fixed,
artifact-disjoint design prevents a model from seeing another level or alpha
partner of the same probe, but unrelated cases still share a context. This is
reported as a protocol limitation and v5 is never pooled with or relabeled v4.

The panel mirrors v4's 3+2 primary structure: Terra is crossed with P8/P4/P1,
and Sonnet with P8/P4. This holds prompt composition constant relative to v4's
design while replacing its inaccessible two model families. Family-leave-one-
out analyses are expected to be `NOT_COMPUTABLE` or extremely discrete at the
resulting `n=2`/`n=3`; they remain diagnostics, not headline evidence.

The frozen request surface contains 258 batches (43 per LLM configuration) and
774 fresh CLI invocations across three repeats. Rendered benchmark prompts total
55,870,182 UTF-8 bytes over the full run (about 16 million text tokens at 3.5
bytes/token, before CLI system/cache overhead). This is subscription quota use,
not a free computation, despite the `$0` provider-API-spend invariant.

## Unchanged scientific contract

- 470 typed candidate artifacts and the v4 Lean 4.22 structural manifest.
- Structural valid sets: `P_eq=86`, `P_bm=49`, `P_ms=63`, `P_eqalpha=67`.
- Three scores per score cell; local median aggregation.
- Exact-zero-first log geometric means, no headline epsilon.
- Structurally valid constant ladders receive `C=0`.
- Required property and human-criterion coverage is 100%.
- Human panel is the evidence-backed 72-row average view, with strict and
  lenient secondary views.
- 10,000 percentile bootstrap replicates, seed 0.
- Primary bridge is primaries-only Spearman; Kendall tau-b, pooled controls,
  family leave-one-out, three-property, and per-property analyses are frozen
  robustness/exploratory analyses.
- SESOI is Spearman `rho=0.5`; no deployment threshold or human-savings claim.
- The bridge is forbidden until the byte-identical property table is committed.

## Abort rules

- Any config/source/schema drift before scoring requires regeneration and a new
  pre-result commit.
- Any unsupported/substituted model, malformed batch, missing case, duplicate,
  non-finite/out-of-range score, CLI quota failure, or incomplete repeat remains
  missing and is retried only under the frozen retry policy.
- If completeness cannot be restored, the affected property/criterion is
  `NOT_COMPUTABLE`; missingness is never converted into a behavioral zero.
- v4 remains `NOT_RUN`; v5 results are never presented as the v4 exact-model run.
