# PTI-v0 final Mega-QA prompt

**TLDR:** Perform a fresh, adversarial, end-to-end review of the direct-to-main PTI-v0 experiment and ICLR 2027 paper. Independently verify the frozen evidence and claims, apply only proven minimal fixes, run deterministic checks, and return the exact verdict block below.

You are one fresh-context stage in the mandatory sequential Mega-QA chain for
`brando90/cert-judge`. Work from the repository root on branch
`codex/iclr2027-final`; review the complete diff against `origin/main` and the
current workspace inherited from the prior stage.

Read and obey the repository `AGENTS.md`. This is a QA pass, not a new
experiment. Never invoke a provider API, load an LLM-provider key, rerun the
774 subscription-CLI scoring tasks, alter Git history, commit, push, merge, or
change external services. You may run deterministic local computations and
tests. You are empowered to apply minimal fixes directly when an issue is
proved. Do not rewrite immutable raw transcripts or frozen generated results
merely for style; if a frozen artifact is wrong, stop and report the exact
authority conflict and downstream impact.

## Authority and scope

Review the complete chain, not merely the latest commit:

- Planning and rulings:
  `experiments/29_pti_v0_cli_bridge/00-CODEX-SOL-MAX-PREFLIGHT.md` through
  `05-ICLR2027-FINALIZATION-CHECKLIST.md`, especially
  `03-SPEC-OVERRIDES-R41-R49.md`.
- Frozen execution authority:
  `experiments/29_pti_v0_cli_bridge/PROTOCOL.md`, `frozen_config.json`,
  `batch_score_schema.json`, manifests, score requests, raw batches, and
  `results/scores.json`.
- Implementations and tests:
  `experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py`,
  `experiments/archive/04_veribench_validation/run_pti_v0.py`,
  `py_src/cert_judge/pti_v0.py`, `py_src/cert_judge/ti2prime_plot.py`, and all
  five relevant test files under `tests/`.
- Derived evidence:
  property, criterion, bridge, SESOI, diagnostic, figure-source, timestamped
  summary, W&B-push, and QA artifacts under the Experiment 29 directory.
- Human-facing reports:
  `results.md`, `REPORT.md`, `RESULTS_QA.md`, `PAPER_QA.md`,
  `MANUSCRIPT_NUMBER_MAP.md`, and `STATUS_PTI_V0_V4.md`.
- Paper:
  `paper_latex/ICLR_2027_submission/main.tex`, `main.pdf`, both included
  figures, bibliography/style assets, and
  `ANONYMIZED_SUPPLEMENT_ALLOWLIST.md`.
- GitHub topology: draft PR #40 must be the sole canonical PR, target `main`,
  be mergeable, and contain the latest pushed head; closed PR #39 is historical.

## Required correctness checks

1. Independently reconstruct record bindings, median repeat aggregation,
   per-artifact factors, all four PTI properties, zero-first geometric means,
   artifact-cluster intervals, the 72-item human criterion, tie-aware
   Spearman/Kendall, judge bootstrap, leave-family-out behavior, role
   sensitivity, and the frozen SESOI simulation. Do not accept markdown numbers
   as proof.
2. Reconcile every JSON/CSV/report/paper number and status. Expected authorities
   to verify include 774/774 tasks, 4,728/4,728 cells, 14,184 records, 100%
   coverage, zero provider-API spend, five primaries, primary Spearman
   `-0.3535533906`, Kendall `-0.3162277660`, 95% interval
   `[-1.0, 0.3952847075]`, 6,647/10,000 valid replicates, and 27.1% complete-rule
   power at the 0.5 SESOI.
3. Verify exact v4 is `NOT_RUN`; the actual v5 model IDs are reported exactly;
   every accepted Claude call's auxiliary `claude-haiku-4-5` telemetry is
   disclosed; no Sonnet-only, positive bridge, PASS-SCREEN, deployment,
   causal, or human-savings claim leaks through.
4. Verify the Experiment 29 folder is self-contained as far as practical:
   plan, preflight, blocker, reviews, version prompt/report, runner, raw outputs,
   normalized records, derived evidence, figures, QA, decision guidance, and
   original reference archive are present; no tracked Experiment 28 artifact or
   stale active path remains. External shared inputs must be explicit and
   content-bound rather than silently copied.
5. Verify frozen hashes and provenance links, including score JSON, pre-bridge
   property table, figures, source sidecar, original planning archive, PDF, and
   the pre-result/pre-bridge commit ordering. Check for secrets and direct-API
   paths without printing any credential value.
6. Run the full 79-test suite, relevant byte-compilation, CLI status, JSON/CSV
   schema checks, and structural QA. Flag god functions/duplication only when it
   creates a real correctness or maintenance risk; make no speculative rewrite.
7. Build the ICLR paper, inspect compiler warnings and extracted text, render
   and visually inspect all 22 pages, verify page boundaries and the nine-page
   main-text limit, table/figure readability, citations, metadata, anonymity,
   supplement exclusions, and exact source-to-manuscript number agreement.
8. Assess the scientific decision: distinguish what the evidence supports from
   what would require a new, separately frozen experiment. Be willing to return
   FAIL if the evidence bundle or paper is materially unsound.

If you edit any LaTeX or figure source, rebuild and include the current
`main.pdf`. Keep fixes minimal and preserve frozen scientific authorities.

End your response with exactly:

```text
VERDICT: PASS | FAIL | FIXED
CRITICAL_ISSUES: [count]
MAJOR_ISSUES: [count]
FIXES_APPLIED: [count]
STRUCTURAL: PASS | IMPROVED | SKIP
SUMMARY: [1-2 sentences]
```
