# Search Judge task results

**TLDR:** The local zero-spend Search Judge smoke validates five new focused tests and a cached 0.57-score example; remote confirmation and commit remain.

Status: RUNNING
Source: `brando90/cert-judge` at `85e6dd3` on `search-judge-smoke-10-21-2026`.

## Plan

1. Inspect the actual judge surface and its tests, then identify the smallest deterministic end-to-end path.
2. Run the focused and full deterministic suites locally and from a named remote tmux job on `skampere2`.
3. Fix one bounded robustness gap with regression coverage, re-run checks, commit only owned artifacts, and record ranked follow-ups.

## Live ledger

| Event | Command / artifact | Result |
|---|---|---|
| 10-21-2026 08:22 PDT | `git status --short --branch`; project/test inspection | Owned branch confirmed at `85e6dd3`; package surface includes `py_src/cert_judge/efg_judge.py`; no EFG-specific test existed. |
| 10-21-2026 08:22 PDT | provider budget decision | Deterministic/cache-only path selected; live provider-backed example remains unverified because its incremental budget is $0. |
| 10-21-2026 08:30 PDT | `PYTHONPATH=py_src python -m pytest -q tests/test_efg_judge.py` | PASS: 5/5 regression tests, covering response parsing, cache hits, uncached direct-mode orchestration with a mock client, caller-weight recomputation, and answer-order-invariant aggregation. |
| 10-21-2026 08:30 PDT | cached direct example | PASS: `LP=1, MC=0, FV=1, FQ=0` produced `0.57`, with no client construction or provider request. |
| 10-21-2026 08:30 PDT | deterministic repository suite excluding unavailable optional plot extra | PARTIAL: 205 passed / 3 failed / 208 total. Failures predate this change: two archived W&B publisher tests hit an installed W&B/protobuf mismatch; one Lean test could not fetch its pinned dependency. |
| 10-21-2026 08:30 PDT | implementation change | Fixed parser explanation extraction so it stops before `Judgement:`; fixed cached results to recompute the requested weighted aggregate rather than reuse an aggregate made under earlier weights. |

## Pending evidence

- Remote named-tmux receipt and scanned commit hash.

## Weak points and remaining work

1. [p 8/10] Bound input-order and input-length sensitivity with a fixed cached or explicitly approved live corpus; cache aggregation is order invariant, but a model's raw verdict has not been measured.
2. [p 7/10] Replace hard-coded provider credential discovery with an injected provider/credential interface while preserving the established live implementation.
3. [p 6/10] Repair the pinned W&B/protobuf environment and Lean dependency checkout so all repository tests run in one reproducible environment.
