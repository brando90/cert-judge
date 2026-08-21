# PTI-v0 v4 execution status

**TLDR:** PR-A engineering and zero-spend evidence are complete and published as draft PR #39; primary PTI and the outer bridge remain honestly `NOT_COMPUTABLE`, actual provider/API spend is `$0`, and paper work has not started.

## Provenance

| Item | Revision |
|---|---|
| Local pre-change branch baseline | `cbd31f2ca0dbd4fe68ef7fbf632dfce4d160ab47` |
| `origin/main` audited base | `c1021bfcd5ad9deee7dba97a8b9bac635b2962c2` |
| Exp27 / cert-judge PR #38 head | `edf627426d6d0740dbd6a793e4ff985fc4e6e3fa` |
| ultimate-utils PR #44 head | `c8a6a9a70e32073d6cde2193958d570f08fd935e` |
| Global rules revision used | `8190074918da0c2b39e6763b1d46ba04e8215ec2` |
| PTI branch | `codex/pti-v0-final` |
| Implementation commit | `dd4f7968c8d535fe37e1d395f269af68a00a8c36` |

Dependency PR #44 and then PR #38 remain open review dependencies. This branch preserves and stacks on the existing Exp27 work rather than recreating it.

## Preflight blockers and resolutions

- The invalid historical probe generators were replaced with conservative builders that fail closed; the new row-level pinned-Lean audit produced valid subsets `P_eq=86`, `P_bm=49`, `P_ms=63`, and `P_eqalpha=67` over 470 candidates. It prepares three local modules, binds the Lake manifest/7,075-module olean inventory, classifies all base failures, and records four rejected bug-mutation timeouts.
- The supplied inconsistent/absent conformance implementation was replaced with versioned `PTI_v0` code, coherent v4 vectors, randomized tie-heavy tests, and a formal score schema.
- The typed pool is frozen at 470 observed artifacts from 157 items, with one explicit missing member of the nominal 471 grid.
- Statistical choices, five-primary/three-control roles, 100% property coverage, bootstrap behavior, Route B claim language, and the SESOI DGP are frozen.
- The unsupported unsafeMultiply rename was not applied; the evidence-backed panel remains 72.
- Legacy cache ambiguity was not worked around: 94 prompt/content and 80 three-score matches are reported, two matching fallbacks are identified, and admissible cached calls remain zero.
- Independent QA found eight historical HTTP-401 fallback rows for one primary criterion. They are now quarantined; that judge is `NOT_COMPUTABLE` at 64/72 instead of being reported with a contaminated value.

## Alpha and spend

- Alpha structural status: 67 conservative non-no-op transformations elaborate under pinned Lean 4.22.
- Approval status: `NOT_REQUESTED` / not approved.
- Exact conservative quotes: alpha transformed side 918 calls / `$7.6127427`; uncached original+alpha 1,836 calls / `$15.2020962`; full paid set 9,396 calls / `$85.0848855`.
- Optional RENAME/REORDER/STYLE diagnostics: `NOT_QUOTABLE_UNVALIDATED_TRANSFORM`.
- Actual provider/API calls and spend: **0 / `$0`**.

## Computed results

- The second independent maximum-effort review returned `PASS WITH MINOR FIXES`: no high/medium findings remained, and all first-pass repairs reproduced. Its documentation, fallback-prefix, filesystem-provenance, fingerprint-policy, export, and SESOI-interpretation nits were applied before final QA.
- Panel: 72 included pairs, three provenance-failed unsafeMultiply rows excluded, zero post-policy checked-average mismatches.
- Deterministic local controls: both have full structural-set coverage; `editdist_e1 PTI_v0=0`, `random_r1 PTI_v0=0`.
- Human criterion: seven judge configurations computed on 72/72 paired rows; `gpt-5.3-codex|P8_STRICT_B` is `NOT_COMPUTABLE` at 64/72 after eight fallback rows are excluded.
- Frozen SESOI simulation: completed at seed 0 with 10,000 draws per target and the complete decision rule. Positive-rule power at `rho=0.5` is 0.1492 with four valid primaries, a pre-bridge underpowered result; at this sample size the interval excludes zero only for a perfect rank order.
- Primary `PTI_eq_bm_ms`: `NOT_COMPUTABLE`.
- Primary four-property `PTI_v0`: `NOT_COMPUTABLE`.
- Outer bridge: `NOT_COMPUTABLE`; `bridge_statistic_computed=false`.
- Sensitivity analyses requiring primary PTI: not computed. Predeclared control and human-view outputs remain available without being promoted to a bridge.

## Final QA

- Independent adversarial QA: first pass `REQUEST CHANGES`; targeted second pass `PASS WITH MINOR FIXES`; every second-pass low-severity item was resolved before this deterministic run.
- Tests: 64 PTI-v0 numerical/transformation/schema/pipeline tests plus eight preserved Exp27 compatibility tests, **72 passed** total.
- Static checks: Ruff check and format-check passed for all seven new/modified PTI-v0 Python files; `git diff --check` passed.
- Lean: the pinned Lean 4.22 project build passed, the full 470-row structural audit completed, and valid counts remained 86/49/63/67.
- Packaging: editable install/import passed; `cert_judge.pti_v0` resolves to the module; the wheel contains `pti_v0.py`, `probe_validation.py`, and the existing package modules.
- Reproducibility: 20 downstream artifacts regenerated byte-for-byte in a clean temporary tree; `properties_local_controls/properties.json` matched after normalizing its intentionally recorded absolute `score_path`. Config/probe fingerprints and all five bound source hashes recomputed exactly.
- Data hygiene: all canonical JSON parsed, no stale audit locks remained, and staged secret scanning is repeated immediately before commit.

## Pull requests and manuscript

- PR A: [draft #39](https://github.com/brando90/cert-judge/pull/39), head `codex/pti-v0-final`, base `claude/ti2prime-validity-stability-scatter`; final QA is complete, and the draft must not merge before dependency review.
- PR B: not created; it must stack on PR A only after committed bridge evidence exists.
- Active manuscript: unchanged.
- Build/page/anonymity status: not applicable to this blocked result phase; the preflight temporary build remains historical evidence only.
- Outer figure: not generated.
- W&B Report: N/A because the approved paid experiment did not run.

## Remaining human decisions

1. Review/resolve ultimate-utils #44 and cert-judge #38 in that order.
2. Decide whether to approve one exact frozen scoring scope after reviewing the quote artifacts.
3. Decide whether to rerate or explicitly redefine the three unsafeMultiply rows; otherwise retain the 72-pair panel.
4. Decide whether to quote/approve 24 criterion re-score calls for the quarantined primary judge or proceed transparently with four valid primary criteria.
5. After a complete committed property table, authorize the gated bridge and subsequent stacked manuscript work.
