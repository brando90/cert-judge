# Independent Fable 5 rereview — PTI-v0 v4

**TLDR:** A fresh read-only Claude Fable 5 maximum-effort rereview returned `PASS WITH MINOR FIXES`. It independently reproduced every first-pass repair, found no high- or medium-severity issue, and identified seven low-severity precision/portability nits; all seven were resolved before final deterministic QA.

- Review date: 2026-08-21 (America/Los_Angeles)
- Baseline: `cbd31f2ca0dbd4fe68ef7fbf632dfce4d160ab47` plus the unstaged PTI-v0 implementation
- Reviewer: Claude Fable 5, fresh non-persistent CLI session, effort `max`
- Mode: read-only; only `Read`, `Bash`, `Glob`, and `Grep` enabled
- Verdict: **PASS WITH MINOR FIXES**

## Independently reproduced

- Exact historical criterion lineage: seven judges remain clean at 72/72; `gpt-5.3-codex|P8_STRICT_B` has 64 verified rows, eight HTTP-401 fallback rows, 0.8889 coverage, and `NOT_COMPUTABLE` under the frozen 100% rule.
- The actual SESOI decision rule: point Spearman at least 0.5 and a 95% judge-bootstrap lower bound above zero. An independent 400,000-draw check estimated power 0.1479 at the SESOI, consistent with the frozen 10,000-draw result 0.1492.
- Lean provenance and failure accounting: 384 base failures split into 118 unresolved imports, 135 parse failures, 21 termination failures, 59 type/elaboration failures, and 51 other elaboration failures. The Lake manifest, 7,075-module sorted olean inventory, prepared local modules, and four rejected timeouts were all present and consistent.
- Cache inventory: 148 potential model/content matches, 94 prompt/content/model matches, 80 three-repeat matches, two fallback matches, and zero admissible PTI-v0 calls.
- Route-B limitation, exact-constant behavior, config/request/probe fingerprint chain, zero-spend gates, editable import, and wheel contents.
- A full clean-room zero-spend regeneration matched 20 artifacts byte-for-byte; the only normalized difference was the intentionally recorded absolute local-control score path.
- The reviewer ran the three PTI-focused test files (`62 passed`), Ruff, `git diff --check`, a secret-pattern scan, a wheel build/content inspection, fingerprint recomputation, and nine pinned-Lean spot recompilations.

## Reviewer findings and builder disposition

No high- or medium-severity findings remained.

1. **Legacy reasoning scope:** the cache stores only first-repeat reasoning, so later-repeat parse recovery is not independently classifiable. The spec, protocol, results, and frozen criterion policy now state this limitation explicitly.
2. **Fallback-prefix completeness:** `extracted bare number:` was a latent unclassified parse-recovery prefix. It is now fail-closed in the classifier and frozen policy, with a regression test. There were zero current-cache occurrences, so scientific values did not change.
3. **Filesystem portability:** lowercase `veribench` source/olean paths coexist with uppercase `VeriBench` imports and rely on the audited case-insensitive filesystem. The structural manifest now binds platform and measured case sensitivity; the protocol/results warn that a case-sensitive regeneration may yield a different valid set.
4. **Config re-freeze policy:** metric and transformer source hashes intentionally remain strict fingerprint gates. The config and docs now state that any byte change requires deterministic re-freeze/regeneration, while pipeline semantics are represented by `PIPELINE_VERSION` and the raw pipeline SHA remains provenance.
5. **QA status precision:** the status now separates the 64 PTI-focused tests from eight preserved Exp27 compatibility tests and records the actual final QA commands/results.
6. **Top-level export shadowing:** the bare `pti_v0` function is no longer re-exported from `cert_judge.__init__`, so `import cert_judge.pti_v0` resolves to the module. The function remains available from `cert_judge.pti_v0`.
7. **SESOI interpretation:** results and status now state that with four valid primaries the bootstrap interval excludes zero only for a perfect rank order; 0.1492 is therefore the probability of that discrete event, not a smooth asymptotic power curve.

## Residual limitations accepted by the reviewer

- Paid inference, dependency PRs #44/#38, the gated bridge statistic, manuscript edits, and figures were intentionally outside the review because their preconditions are not satisfied.
- SESOI agreement is Monte Carlo rather than bit-identical because the cross-check deliberately used a different random stream.
- The legacy single-reasoning cache contract cannot retrospectively expose a parse fallback isolated to repeat 1 or 2; exact score agreement and the stored repeat-0 reasoning are the available evidence.

The rereview did not authorize or execute provider-backed experiment inference. Actual PTI-v0 provider/API calls and spend remain zero.
