# Fable 5 independent pre-result review

Date: 2026-08-25
Scope: CLI v5 runner, tests, frozen config, score/criterion/batch manifests, and
compatibility with the canonical experiment-04 PTI implementation.
Mode: fresh `claude-fable-5[1m]`, effort `max`, read-only; no scoring calls.
Initial verdict: **REQUEST CHANGES**.

## Verified before findings

- The freeze/build replay was byte-identical.
- Counts reconciled: 780 property + 72 criterion points per judge, eight judges,
  6,816 conceptual cells, 4,728 unique cells, and no cross-judge collision.
- The 72-row criterion mapping, strict/lenient average lineage, median repeat
  aggregation, tie-aware Spearman, fail-closed parsing, and atomic resume writes
  were sound.
- No provider SDK/HTTP call existed in experiment 29.
- v4 and v5 were labeled distinctly; no benchmark response had been produced.

## Blocking findings and resolution

1. **Canonical property command crashed.** The v5 config omitted the
   `score_policy` mapping required by experiment 04. Resolved by binding v4's
   unchanged score policy and adding an end-to-end empty-score compatibility
   test.
2. **CLI children inherited provider-key environment variables.** Resolved by
   removing every `*_API_KEY` plus explicit provider-key name before both child
   launches, checking ChatGPT/claude.ai subscription auth, and adding tests.
3. **Some ladder levels shared a batch.** This could reveal ordering within a
   probe and inflate the property. Resolved by deterministic artifact-disjoint
   packing and an all-batch invariant test.

## Additional findings and resolution

- Codex provenance/tool use was insufficient: JSONL is now retained and any
  non-message/reasoning item is rejected; Claude remains safe-mode/tool-less;
  stdout/stderr and model usage are retained and hash-bound.
- Claude structured output could live outside `result`: the parser now prefers
  `structured_output` and falls back only when absent.
- Resume identity omitted model/backend/effort: all are now part of batch
  identity and raw-result validation.
- Request/config/batch/panel drift gates were incomplete: commands now verify
  all embedded fingerprints and source hashes.
- Criterion bootstrapping repeatedly re-imported the v4 module: the loader is
  memoized and criterion seeds/Kendall/bootstrap now align with v4.
- The original asymmetric Terra/Luna/Sonnet panel confounded model and prompt:
  v5 now mirrors v4's 3+2 structure (Terra P8/P4/P1; Sonnet P8/P4).
- Boolean/string scores were coercible and partial cells counted complete:
  both are rejected/fixed, with regression tests.
- Concurrent score processes could duplicate quota: an exclusive score lock is
  now required.

The complete first-pass transcript was returned in the Codex session. This file
records its evidence-backed findings and their pre-result disposition without
copying account identifiers or any secret-bearing environment values.
