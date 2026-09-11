# PTI-v0 manuscript QA

**TLDR:** A fresh read-only `gpt-5.6-sol` reviewer at `xhigh` effort independently reproduced the complete PTI, criterion, bridge, bootstrap, and SESOI evidence, then returned `REQUEST CHANGES` for four manuscript/submission issues. The paper branch applies every deterministic correction below; the scientific result remains below-SESOI and inconclusive about zero.

## Reviewer route

The requested fresh Fable 5 review was attempted first and rejected before repository review because the independent session quota was capped until 05:40 America/Los_Angeles. The documented fallback was a fresh ephemeral Codex review using `gpt-5.6-sol`, reasoning effort `xhigh`, and a read-only sandbox. The reviewer made no repository changes.

## Independently verified evidence

- Recomputed all eight judges' four properties, exact-zero diagnoses, and `PTI_v0` values from the 14,184 normalized records; maximum discrepancy was floating-point noise.
- Recomputed all five primary 72-item criterion correlations and their 10,000-replicate paired-item intervals exactly.
- Recomputed the primary and pooled judge-level Spearman/Kendall statistics, intervals, and valid replicate counts exactly: `-0.3535533906`, `[-1,0.3952847075]`, 6,647/10,000 (`n=5`), and `-0.2474358297`, `[-0.8164965809,0.2567762955]`, 6,521/10,000 (`n=8`).
- Recomputed the frozen SESOI simulation exactly, including 27.1% positive-rule power at true Spearman `0.5`.
- Verified exact v4 is `NOT_RUN`; v5 Terra and Claude Sonnet-plus-auxiliary-Haiku provenance is accurately disclosed.
- Verified legacy/malformed probe evidence is excluded or labeled, outer and inner figure hashes match their authorities, the plotting-unit contracts hold, and the PDF build has resolved citations/references with no overfull boxes.

## Verdict and resolution ledger

The read-only verdict was `REQUEST CHANGES`:

1. **Blinding:** a public 40-hex VCS identifier in the PDF could resolve to author identity; supplement-adjacent artifacts also contained W&B/local-path identity strings. The PDF now omits the identifier, the result map uses content hashes, the reused inner diagnostic has a repository-relative sidecar, and an explicit supplement allowlist requires sanitized derivatives and identity scans.
2. **Cost/claim scope:** total inference cost was incorrectly described as constant in screened judges. The paper now states only the human-annotation component is conditionally constant after a successful bridge, inference remains linear, the current result demonstrates no savings, and the legacy overview is explicitly conceptual rather than PTI-v0 evidence.
3. **Uncertainty:** four zero point estimates were presented without adjacent PTI intervals, hiding Sonnet--P4's `[0,0.8467228651]` interval. The main table now reports every judge's PTI interval and the appendix reports all 32 per-property intervals.
4. **Candidate count:** three passages conflated the nominal 471 grid with the 470 observed artifacts. They now state 470 observed typed candidates over 157 items, nominally 471 with one documented missing candidate.
5. **Minor provenance:** the CLI protocol identifier, page-boundary status, and inner Kendall/interval authority were corrected; the new sidecar binds the latter to source hashes and exact fields.

No second independent reviewer round was run; the workflow prescribed one paper-review round followed by deterministic fixes. Final build, text/anonymity scans, tests, and file/hash checks are recorded in `STATUS_PTI_V0_V4.md`.
