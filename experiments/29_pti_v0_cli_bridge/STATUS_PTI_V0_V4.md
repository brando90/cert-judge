# PTI-v0 final execution and ICLR 2027 manuscript status

**TLDR-start:** [cj: pti-v0] The exact v4 panel is honestly `NOT_RUN`, but the frozen metric/probe/analysis protocol was completed as subscription-CLI execution v5: 774/774 tasks, 4,728/4,728 cells, 14,184 records, full coverage, and `$0` provider-API spend. The primary outer bridge is Spearman `-0.3536` with 95% CI `[-1.0000, 0.3953]` (`n=5`): below the `0.5` SESOI and inconclusive about zero. Draft #40 is the canonical direct-to-`main` integration PR; superseded PR #39 is closed.

## Provenance and dependencies

| Item | Revision / state |
|---|---|
| ultimate-utils dependency PR #44 | `c8a6a9a70e32073d6cde2193958d570f08fd935e`, open |
| cert-judge Exp27 dependency PR #38 | `edf627426d6d0740dbd6a793e4ff985fc4e6e3fa`, open |
| Historical PR A experiment branch | `codex/pti-v0-final` at `540c43f5877c02c50334bc98e1c238a2ba30f558`; superseded by direct PR #40 |
| Pre-result experiment commit | `395efdc00584cad32f6e9a525a8dbd9b201ff2a7` |
| Mandatory pre-bridge results commit | `6f55c44299eadda78db5738c7913475d06ea671f` |
| Pre-bridge property-table SHA-256 | `7a904f31a6dbd626a728e44fd7a00043c61b5e1630937986f111a0be4af15c0a` |
| PR A final experiment commit | `540c43f5877c02c50334bc98e1c238a2ba30f558` |
| Paper integration commit | `ec04890da5ae272770400695c5b55aa5505d1ce7` |
| Consolidated experiment commit | `fb045ab3b76eb347b56c0626db817280e26cfbb6` |
| Latest-main synchronization commit | `232c2a5cea170d1ae29b44cadecf64a30876999e` over `origin/main` `b488de9fc11e87952e05e9e4ecfff38dafbe0c17` |
| Canonical integration branch / PR | `codex/iclr2027-final`, draft [#40](https://github.com/brando90/cert-judge/pull/40), base `main` |
| Global rules revision used | `8190074918da0c2b39e6763b1d46ba04e8215ec2` |

The canonical direct-to-`main` branch contains the reviewed Exp27 commits plus the complete PTI-v0 experiment and paper update. Its external ultimate-utils/PR #44 dependency remains explicit. Nothing is auto-merged.

All task-specific planning, preflight, blocker, independent-review, execution,
raw-output, derived-result, QA, and decision artifacts now live together under
`experiments/29_pti_v0_cli_bridge/`. The original planning archive is retained
byte-for-byte as `ref/files (22).zip` with SHA-256
`7362ab1d1dcc9161fefca3aff87c33276b71941a647f2bd2b7f8e176509d6859`.

## Preflight verdict and blocker resolution

The original zero-spend preflight verdict was `BLOCKED`. All executable blockers required for a sound run were then resolved before v5 scoring:

- Replaced malformed historical transforms with fail-closed structural builders bound to Lean `v4.22.0`; valid sets are `P_eq=86`, `P_bm=49`, `P_ms=63`, and `P_eqalpha=67` over 470 typed candidates.
- Excluded construction defects judge-free; retained a structurally valid constant-score ladder as behavioral `C=0` rather than dropping it.
- Implemented and tested median repeat aggregation, tie-aware Spearman/Kendall, `(1-rho)/2`, `2*sd(ddof=0)`, the one-level ladder rule, zero-first log-domain geometric means, missingness/coverage behavior, and exact metric-version fields.
- Kept the evidence-backed human criterion at 72 paired items; no label was edited to force 75 analyzed rows.
- Froze five primaries, three controls, the bootstrap units/method/seeds, the `0.5` SESOI, role sensitivities, and the no-threshold/no-PASS-SCREEN claim before the bridge was revealed.
- Rejected unavailable exact v4 model identifiers rather than silently substituting them; only the execution/model panel was versioned to v5.
- Removed legacy malformed-probe figures and an unbound downstream table from the final manuscript rather than relabeling them as PTI-v0 evidence.

## Alpha status and spend

- Structural alpha status: 67 conservative non-no-op transformations elaborate under the pinned Lean toolchain.
- Paid provider-API alpha quote approval: `NOT_REQUESTED`; no paid API route was used.
- Actual execution: alpha was included in the explicitly authorized subscription-CLI v5 scope.
- Provider API calls/spend: **0 / `$0`**.
- Subscription usage is real quota usage even though provider-API spend is zero.
- Historical warning: the workshop-era alpha generator was malformed, so its `0.399` mean is excluded from the evidentiary chain.

## Experiment execution and conformance

| Quantity | Result |
|---|---:|
| Accepted CLI tasks | 774 / 774 |
| Tasks per LLM judge configuration | 129 / 129 |
| Unique score cells | 4,728 / 4,728 |
| Bound score records | 14,184 |
| Nonlocal / local-control cells | 3,546 / 1,182 |
| Invalid accepted / quarantined tasks | 0 / 0 |
| Excluded failed attempts | 4, all retried successfully |
| Human criterion rows | 72 per judge |
| Property/criterion coverage | 100% |
| Bootstrap replicates | 10,000 |

The conformance suite passed **79 tests** across PTI core, randomized/adversarial vectors, the v5 CLI pipeline, structural probes, schema binding, and preserved Exp27 plotting behavior. Python byte-compilation and `git diff --check` passed. Ruff was unavailable in the active uv environment and is not reported as passing.

## Models actually run

- Exact v4 (`gpt-5.3-codex`, `gpt-4o-mini`): `NOT_RUN` because those IDs were rejected by the approved ChatGPT-backed CLI.
- v5 Codex scoring: `gpt-5.6-terra`.
- v5 Claude requested/scoring model: `claude-sonnet-5`.
- Provenance limitation: every one of the 258 accepted Claude invocations also records auxiliary `claude-haiku-4-5` telemetry. The results therefore do not claim Sonnet-only execution or prove that the helper could not influence execution.

## Frozen property and criterion results

All properties are `COMPUTED` with coverage `1.0` for every judge. Four of five primary `PTI_v0` point estimates are exactly zero. Sonnet–P8 is `0.8114197682` with 95% artifact-cluster interval `[0.7820434991, 0.8390616239]`; Sonnet–P4 is `0` with the consequentially wide interval `[0, 0.8467228651]`. Independent reconstruction verified a directly observed exact-zero artifact factor behind every zero aggregate; missingness was never substituted as zero.

Primary average-view `TI_m1` values are:

| Judge | Spearman | 95% paired-item interval | Kendall tau-b |
|---|---:|---:|---:|
| Terra–P8 | 0.0105 | [-0.2294, 0.2475] | 0.0082 |
| Terra–P4 | 0.2106 | [-0.0338, 0.4425] | 0.1772 |
| Terra–P1 | 0.3377 | [0.0933, 0.5514] | 0.2861 |
| Sonnet–P8 | 0.0886 | [-0.1463, 0.3291] | 0.0685 |
| Sonnet–P4 | 0.2098 | [-0.0396, 0.4426] | 0.1656 |

## Headline bridge and sensitivities

| Analysis | Spearman | Kendall tau-b | 95% judge-bootstrap interval | Valid / 10,000 | n | Status |
|---|---:|---:|---:|---:|---:|---|
| Primaries, four-property `PTI_v0` | -0.3536 | -0.3162 | [-1.0000, 0.3953] | 6,647 | 5 | Below SESOI; inconclusive about zero |
| Primaries, `PTI_eq,bm,ms` | -0.3536 | -0.3162 | [-1.0000, 0.3953] | 6,647 | 5 | Same tie pattern; labeled sensitivity |
| Primaries + controls | -0.2474 | -0.2143 | [-0.8165, 0.2568] | 6,521 | 8 | Secondary; below SESOI/inconclusive |

- Family leave-one-out: both `NOT_COMPUTABLE` (constant Terra PTI after removing Sonnet; only two judges after removing Terra).
- Per-property exploratory Spearman: `P_eq=-0.3536`, `P_bm=-0.2236`, `P_ms=-0.2236`, `P_eqalpha=0.6000`; every interval includes zero.
- At true Spearman `0.5`, the frozen SESOI simulation gives 27.10% complete positive-rule power, mean realized Spearman `0.4747`, 60.67% point-threshold rate, 25.83% false-pass rate, and 45.31% top-1 retention.
- Scientific interpretation: no positive bridge, PASS-SCREEN, deployment threshold, causal effect, or human-validations-saved claim is supported.

## Independent QA

The fresh read-only numerical audit in `experiments/29_pti_v0_cli_bridge/RESULTS_QA.md` reconstructed every score binding, property, criterion, bootstrap, and CSV/JSON output. All numerical and structural checks passed. Its formal verdict is `FAIL` only under the literal exact-model-only provenance claim, with one major finding: Claude's auxiliary Haiku telemetry. The final report and manuscript retain the narrower evidence-backed model claim.

The fresh paper audit in `experiments/29_pti_v0_cli_bridge/PAPER_QA.md` used ephemeral read-only `gpt-5.6-sol` at `xhigh` after the requested Fable 5 session was quota-capped before review. It independently reproduced all scientific numbers and returned `REQUEST CHANGES` for blinding, cost-claim scope, omitted PTI uncertainty, the 470/471 count, and three minor provenance facts. Every deterministic correction was applied; the workflow intentionally used one reviewer round rather than claiming an unperformed re-review.

The manuscript number map is `experiments/29_pti_v0_cli_bridge/MANUSCRIPT_NUMBER_MAP.md`. It binds every new manuscript number to the committed authorities and records the deterministic commands. The sanitized inner-figure sidecar binds Kendall/interval/source hashes, and `paper_latex/ICLR_2027_submission/ANONYMIZED_SUPPLEMENT_ALLOWLIST.md` excludes identity-bearing VCS, W&B, status, authentication, and local-path artifacts from double-blind distribution.

## Pull requests, W&B, and manuscript

- Superseded intermediate PR: closed [cert-judge #39](https://github.com/brando90/cert-judge/pull/39), retained only for historical review context.
- Canonical integration PR: draft [cert-judge #40](https://github.com/brando90/cert-judge/pull/40), head `codex/iclr2027-final`, base `main`.
- Permanent W&B Report: [Experiment 29 — PTI-v0 v5 outer bridge](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-29-%E2%80%94-PTI-v0-v5-outer-bridge--VmlldzoxNzgwOTk0Ng==).
- Active manuscript: `paper_latex/ICLR_2027_submission/main.tex`, revised in place.
- Official ICLR 2027 style files: local `.sty`/`fancyhdr.sty`/`natbib.sty` hashes match the current official archive.
- Build: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` passes with no undefined references/citations or overfull boxes.
- PDF: 22 pages total; the conclusion ends on page 9, uncounted statements continue on page 10, references begin on page 10, and the appendix begins on page 13. The nine-page submission main-text limit is therefore satisfied.
- Reviewed PDF SHA-256: `f465c51c877071c5ef2470bf9e9ad483b7420669e8e00611334d61ae21ba96fe`.
- Visual QA: all 22 pages rendered and inspected; no clipping, overlap, misleading identity line, PTI/TI level MAE, or smoothed paired-density evidence.
- Anonymity: anonymous author block; no public VCS identifier, repository link, local path, W&B link, TODO/TBD, or unresolved placeholder in the submitted PDF. Self-work is cited in the third person; the separate allowlist governs supplement packaging.
- Mandatory AI-use statement, reproducibility statement, and an ethics statement are present before the references.

## Remaining human decisions and submission actions

1. Review and merge ultimate-utils #44, then review and merge canonical cert-judge PR #40 to `main`; its diff contains the previously separate Exp27/PR #38 work. No agent merge is authorized.
2. Perform the authors' final scientific read and explicitly accept the auxiliary-Haiku provenance limitation and the negative/inconclusive interpretation.
3. Submit a genuine title/abstract and lock the complete author list in OpenReview by **September 18, 2026, 11:59 PM AoE**; upload the paper and anonymized supplement by **September 25, 2026 AoE**.
4. Ensure all authors have current OpenReview profiles and designate/register at least one eligible reciprocal reviewer when ICLR sends the post-abstract registration request.
5. Before upload, run the final PDF/anonymity/secret scan once more and verify that the uploaded PDF hash matches the reviewed artifact.

**TLDR-end:** [cj: pti-v0] The experiment and manuscript implementation are complete; the honest result is below-SESOI/inconclusive and the sole major audit limitation is Claude auxiliary-model provenance. What remains is human review, ordered PR merges, and OpenReview submission—not another experiment run.
