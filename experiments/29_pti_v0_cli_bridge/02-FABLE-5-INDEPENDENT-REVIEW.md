# CertJudge PTI-v0 — independent Claude Fable 5 review

You are the independent scientific and software reviewer. Work in a fresh Claude Code session. Load repository rules, then inspect the completed Codex PRs and all raw outputs. Do not assume the PR descriptions or `STATUS` file are correct.

## First pass is read-only

Do not edit, commit, push, or merge. Produce `FABLE_PTI_V0_REVIEW.md` with severity-ranked findings and exact evidence.

## Required independent checks

### Repository provenance

- confirm base/head SHAs, dependency PR #44/#38 state, and no accidental historical-tree edits;
- confirm Exp27 was reused rather than duplicated;
- confirm stale AGENTS/CLAUDE project descriptions were corrected without weakening safety rules.

### Numerical implementation

Independently recompute or property-test:

- median repeat aggregation;
- `(1-rho)/2` and prohibited alternatives;
- tie-aware Spearman/Kendall behavior;
- `2*sd(ddof=0)`;
- `K_aj=1 => factor=C`;
- exact-zero log-space GM and no hidden epsilon in headline;
- endpoint snapping and unit ranges;
- structural-invalid exclusion versus valid constant-score `C=0`;
- missing/coverage behavior.

Run the reference vectors and adversarial randomized tests.

### Data and probes

- verify every repaired panel key and 75=25x3 count;
- verify strict/lenient/average lineage;
- verify alpha transforms compile and preserve binding structure;
- check no paid optional diagnostic was run under alpha approval;
- inspect cache accounting and actual spend.

### Statistics

Recompute from raw outputs:

- each judge's properties and PTI;
- each judge's `TI_m1`;
- primaries-only and pooled bridge statistics;
- bootstrap units, valid replicate counts, and CIs;
- SESOI simulation;
- family/role and three-vs-four-property sensitivities.

Check for selection on results, pseudo-replication, dropped judges/ladders, undefined correlations, and outcome-targeted choices.

### Figures

- outer bridge is one point per judge;
- no `y=x` or PTI/TI level MAE;
- Exp27 item-level figure uses paired data, tie-aware markers, and within-item repeat std;
- figure source data exactly regenerate the committed assets.

### Manuscript

Audit every quantitative statement against committed machine-readable evidence. Check:

- construct/criterion/proxy separation;
- scoped Route A/B necessity language;
- legacy TIvar not relabeled PTI-v0;
- negative and criterion-drift results retained;
- uncertainty and sample sizes adjacent to claims;
- no hidden “certifies trustworthiness” overclaim;
- ICLR page limit, anonymity, AI-use statement, references, and unresolved placeholders.

## Verdict

Return one of:

- `PASS`;
- `PASS WITH MINOR FIXES`;
- `REQUEST CHANGES`;
- `BLOCK`.

For every non-pass finding give file:line, why it matters, exact correction, and the test that proves it fixed. Only after Brando explicitly asks should you implement fixes.
