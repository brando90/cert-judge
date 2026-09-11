# Mega-QA stage record — Codex GPT-5.6-Sol (fresh context)

**TLDR:** A fresh Codex GPT-5.6-Sol review independently reconstructed the complete Experiment 29 evidence chain and found no scientific or structural defect. It applied one narrow provenance fix: the manuscript build now uses a fixed source epoch and reproduces the same 22-page PDF byte-for-byte.

- Date: 2026-08-27 (America/Los_Angeles)
- Reviewer: Codex GPT-5.6-Sol, fresh ephemeral session, reasoning effort `xhigh`
- Baseline: `codex/iclr2027-final` at `ab791cf35995a9386d1fdb2d846c56dd1affeb03` over `origin/main` `b488de9fc11e87952e05e9e4ecfff38dafbe0c17`; draft PR #40
- Scope: correctness and structural QA only; no experiment scoring rerun, provider API, commit, push, merge, or external-service mutation
- Prior-stage fixes: reviewed as candidate working-tree changes, not presumed correct

## Independent checks

- Reconstructed the complete inventory: 774/774 accepted tasks, 4,728/4,728 unique cells, 14,184 bound records, 100% property/criterion coverage, and zero invalid or quarantined accepted tasks.
- Recomputed every PTI property, 896 ladder diagnostics, all artifact-cluster bootstraps, 24 criterion views over 72 human-labelled items, both headline bridges, role and per-property sensitivities, leave-one-family-out results, and the frozen SESOI simulation.
- Reproduced the primary bridge exactly: Spearman `-0.3535533906`, Kendall tau-b `-0.3162277660`, 95% judge-bootstrap interval `[-1.0, 0.3952847075]`, 6,647/10,000 valid replicates, `n=5`.
- Reproduced 27.10% complete positive-rule power at the `0.5` SESOI.
- Verified exact v4 is `NOT_RUN`; the v5 disclosures distinguish the explicit `gpt-5.6-terra` request from unavailable served-model telemetry and disclose auxiliary `claude-haiku-4-5` telemetry on all accepted Claude calls.
- Verified raw/request bindings, artifact-disjoint batching, fingerprints, frozen content hashes, and commit ordering: pre-result `395efdc` before pre-bridge `6f55c44` before bridge `540c43f`.
- Verified `scores.json` SHA-256 `c51a2ee78c7552af3c021a666ad1c55ba6eeed65f4a91c79d1b0a41d7f36e6c1` is bound into both property and criterion authorities.
- Verified the pre-bridge property table SHA-256 `7a904f31a6dbd626a728e44fd7a00043c61b5e1630937986f111a0be4af15c0a` and original planning archive SHA-256 `7362ab1d1dcc9161fefca3aff87c33276b71941a647f2bd2b7f8e176509d6859`.
- Ran the dependency-aware suite: `79 passed`. The documented bare environment result is `71 passed, 1 skipped` because eight Exp27 plotting tests require the open `ultimate-utils` dependency.
- Passed CLI status, Python byte-compilation, JSON/CSV validation, source/provenance hash checks, direct-provider-API absence review, and a 2,402-file secret scan with zero findings.
- Reviewed structural risk manually because `radon` was unavailable; no correctness-critical god-object or duplication defect was found.
- Rebuilt, extracted, rendered, and visually inspected all 22 manuscript pages. The conclusion ends on page 9, references occupy pages 9–12, and the appendix begins on page 13. No clipping, overlap, unresolved citation/reference, overfull box, anonymity leak, or unsupported positive/certification/savings claim was found.
- Verified the local ICLR style assets match the official archive byte-for-byte.
- Verified live GitHub topology: PR #40 is the canonical draft to `main`, `MERGEABLE/CLEAN`, with local and remote heads equal; PR #39 is closed; PR #38 remains noncanonical and its commits are contained in #40.

## Fix applied

The ordinary `latexmk` recipe embedded volatile PDF timestamps, so visually identical forced builds did not have stable bytes. The reviewer changed only the reproduction documentation and rebuilt the PDF with:

```bash
SOURCE_DATE_EPOCH=1787763818 FORCE_SOURCE_DATE=1 TZ=UTC \
  latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Two forced builds produced the same SHA-256:

`38118fb4a644896fd301a97ae5fa5f78c8b775ce4739347729bdb5d4dcf281ae`

The command and hash are now recorded in `MANUSCRIPT_NUMBER_MAP.md` and `STATUS_PTI_V0_V4.md`. Frozen configuration, transcripts, scores, properties, criterion, bridge, SESOI, and figure source data were untouched.

## Scientific assessment

The evidence supports a complete v5 subscription-CLI execution of the frozen PTI-v0 protocol, but not the preregistered positive bridge. The primary estimate is negative, its interval includes zero, its upper endpoint is below the `0.5` SESOI, and the five-judge complete-rule design has only 27.1% power at the SESOI. No PASS-SCREEN, deployment, causal, certification, or human-savings conclusion is warranted.

```text
VERDICT: FIXED
CRITICAL_ISSUES: 0
MAJOR_ISSUES: 0
FIXES_APPLIED: 1
STRUCTURAL: PASS
SUMMARY: Independent reconstruction and end-to-end paper QA validated the frozen negative/inconclusive result; one PDF reproducibility-documentation defect was fixed without changing scientific evidence.
```

**TLDR-end:** [cj: pti-v0 mega-QA] The second independent review passed with zero critical or major issues after one deterministic-PDF documentation fix; every frozen scientific authority and the negative/inconclusive interpretation remain unchanged.
