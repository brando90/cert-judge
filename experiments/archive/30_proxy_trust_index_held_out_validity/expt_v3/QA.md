# Experiment 30 version 3 independent acceptance review

**TLDR:** PASS for the observed scientific diagnostic and cached inventory: all numerical outputs reproduce, and the locked decision is INCONCLUSIVE. Two minor issues below do not alter these results; no critical or major defect was found.

Review started 2026-09-13 11:52:16 PDT (Pacific Daylight Time); completed 2026-09-13 11:58:49 PDT, within the 15-minute bound. Base: `6e9df01368fd7b0c6df927afc0d68e69cf403b09`; reviewed HEAD: `efb402fbdf4810ba82b6fdf54bcbc2f0726ca69a`, including uncommitted version-3 code/results/tests, root README/results/checkpoint and meeting additions. Exact file hashes: `/tmp/cj-review-20260913/reviewed_files.json`.

Reviewer: **gpt-6-astra, ultra, acceptance**, critical/scientific-results classification, one independent round. Actual evidence: `/tmp/cj-review-20260913/codex.log:3–12` reports Codex v0.153.3, `model: gpt-6-astra`, `reasoning effort: ultra`, session `01a09c1c-b40a-75c0-9336-7d79024cca2e`; process 9579 explicitly supplied those overrides. The local default says `high`, but the running invocation and startup header confirm `ultra`. Builder is Codex per the task checkpoint; its exact model/effort is unverified here. The checkpoint reports a failed Claude Fable 5.1/max attempt with error 429; provider-wide exhaustion was not independently established. This fresh same-company review does not establish cross-company diversity. No reference labels were edited and no two-family reference-edit gate is triggered.

## Checks and findings

- Ran the requested suite, adding only `PYTHONDONTWRITEBYTECODE=1` to prevent repository bytecode writes: **88 passed in 0.82s**.
- Reproduced `audit.json`, `pilot_inventory.json` and `report.md` exactly in memory; verified all 11 manifest hashes and byte equality of all nine immutable inputs/dependencies against the original base.
- Independently recomputed all 24 judge/rubric result rows using direct pair enumeration, SciPy Spearman and NumPy residual Pearson; all 15 paired percentile intervals match a separate problem-count-weight implementation, including all 2,000 valid draws and zero undefined draws per interval.
- Confirmed invariance to candidate-row, judge and repeat ordering; equal-problem versus pair-denominator counterexample gives 0.5 versus 0.6; constant judges retain 0.5 pair accuracy; missing, duplicate and nonfinite cached scores are rejected by the loader.
- Centered Pearson is magnitude-sensitive, not rank agreement: a synthetic example correctly orders 23/24 problems (0.9583 pair accuracy) yet has centered Pearson −0.9998; the report appropriately distinguishes these quantities and makes no causal composition claim.
- Hash selection yields six problems/18 candidates; all 144 candidate–judge keys are represented; 168 conceptual requests map to 160 unique judge–cell keys and 480 observed scores, each with repeat identifiers 0,1,2 exactly once; request identities, efforts and payload hashes match frozen sources exactly.

| Rubric | Informative problems | Human-unequal pairs | Human-tied pairs | Decision |
|---|---:|---:|---:|---|
| Average | 22 | 52 | 20 | INCONCLUSIVE |
| Strict | 16 | 37 | 35 | INCONCLUSIVE |
| Lenient | 18 | 39 | 33 | INCONCLUSIVE |

## Nonblocking findings

Paths below are relative to `/private/tmp/cj-proxy-next-20260913/experiments/30_proxy_trust_index_held_out_validity/`.

- **[p 4/10] Explicit repeat provenance is absent**, so `expt_v3/run_audit.py:61–66,74` falls short of the literal `PROTOCOL.md:45–47` inventory requirement: it saves `repeat_count: 3` and aggregate counts, but no per-cell observed repeat identifiers; record `[0,1,2]` from validated cells (current counts are correct because the upstream loader checks complete repeats).
- **[p 3/10] Render undefined intervals safely**, because `expt_v3/run_audit.py:145–146` raises `TypeError: unsupported format string passed to NoneType.__format__` when all human labels tie: analysis correctly returns INCONCLUSIVE with 2,000 undefined draws, but report formatting crashes; render “undefined” as already done for correlation columns (the frozen observed rubrics do not encounter this case).

Inventory coverage is limited: 144 criterion requests, 8 equality requests and 16 alpha-renaming requests, with no bug/missing-specification probes; it is not a complete four-property pilot. No reported result claims otherwise. The inconclusive intervals do not identify task composition or criterion invalidity as the explanation. Broader historical process/schedule assertions in `meeting_2026-09-14.md:26–28` were not verified because their evidence lies outside this review's allowed scope.

## Exact verification commands

```bash
CUDA_VISIBLE_DEVICES='' PYTHONPATH=py_src PYTHONDONTWRITEBYTECODE=1 /Users/sanmikoyejo-mba-1/cert-judge/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_criterion_audit.py tests/test_proxy_followups.py tests/test_ti_validation.py
CUDA_VISIBLE_DEVICES='' PYTHONPATH=py_src PYTHONDONTWRITEBYTECODE=1 /Users/sanmikoyejo-mba-1/cert-judge/.venv/bin/python /tmp/cj-review-20260913/check_diagnostic.py
git diff --check 6e9df01368fd7b0c6df927afc0d68e69cf403b09 -- experiments/30_proxy_trust_index_held_out_validity tests/test_criterion_audit.py
```

All exited 0. Independent-check output: `/tmp/cj-review-20260913/check_diagnostic.log`; the script also reproduces the minor renderer defect. Structural inspection found seven short functions (maximum 44 lines), with no material structural defect; no broad repository refactor or structural measurement was attempted. No experiment inference, credential access, frozen-source edits, repository writes, commits, publication or deletions were performed by this reviewer; only review artifacts under `/tmp/cj-review-20260913/` were written. Publication remains the parent's responsibility.

```text
VERDICT: PASS
CRITICAL_ISSUES: 0
MAJOR_ISSUES: 0
MINOR_ISSUES: 2
FIXES_APPLIED: 0
STRUCTURAL: PASS
SUMMARY: Observed results and cached identities reproduce; the scientific decision remains inconclusive. Two nonblocking provenance/rendering findings are recorded for the parent.
```

## Builder reconciliation

Updated: 2026-09-13 12:03 PDT

Both minor findings were fixed: the inventory now records observed repeat identifiers per judge/cell and rejects missing records, and undefined paired intervals render safely. Two regression tests cover these cases; 90 focused tests pass. The observed audit.json is byte-identical to the reviewed numerical output. The source manifest adds software versions, and the figure renders the reviewed contrast values without a new analysis. Explicitly report that the selected cache has no bug/missing-specification probes; the locked selection and protocol are unchanged. Frozen inputs, earlier versions and human labels remain unchanged.

```text
VERDICT: FIXED
CRITICAL_ISSUES: 0
MAJOR_ISSUES: 0
MINOR_ISSUES: 0
FIXES_APPLIED: 2
STRUCTURAL: PASS
```
