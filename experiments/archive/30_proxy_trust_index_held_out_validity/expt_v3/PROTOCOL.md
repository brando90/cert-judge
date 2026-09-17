# Experiment 30 — Within-problem criterion audit

**TLDR:** Test whether the string-matching control's human agreement is primarily a between-problem effect, and prepare a small, deterministic development-pilot inventory. This is an exploratory audit of already exposed labels; it changes neither the frozen proxy nor the human criterion and makes no new model calls.

## Scientific question (locked)

The central uncertainty is whether the apparent advantage of the string-matching
control survives comparison of candidate answers to the same problem. If it
does, growing the judge panel alone does not explain the disagreement between
our intended notion of quality and the criterion. If it disappears, problem
composition becomes a concrete candidate explanation. Neither outcome proves
that the labels or the control are wrong.

This protocol is recorded before running this version, after earlier pooled
results were observed. It is not a preregistration on unseen data. Preserve it
after execution and record deviations in the report.

## Locked parameters and decision rule

- Use all 72 existing candidates, all eight original judges, all three observed
  repeats, and average/strict/lenient human views separately.
- Preserve the exact eight judge identities and effort settings from experiment
  29. No new model, prompt, label, reference or proxy definition is selected.
- Report pooled Spearman for reconciliation only; report Pearson correlation
  after separately subtracting each problem's mean from judge and human scores.
  Call the latter within-problem centered Pearson, not partial Spearman.
- Report within-problem pairwise ordering accuracy on human-unequal pairs:
  correct=1, judge tie=0.5, incorrect=0. Exclude human ties from this ordering
  estimand and report their count. Average pair scores within each informative
  problem, then weight informative problems equally.
- Form 2,000 shared bootstrap draws of all 24 problems, seed 20260913; retain
  all candidate and repeat vectors within each drawn problem. Report percentile
  95% intervals for the string control minus each primary judge in pairwise
  accuracy. Count undefined draws; these intervals condition on observed
  labels, calls and judge configurations and do not cover future families.
- If the control's average-rubric pairwise advantage has a positive interval
  against every primary judge, prioritize a blinded criterion/content audit;
  if it is negative against every primary judge, prioritize problem-composition
  sensitivity; otherwise record inconclusive. These five diagnostic intervals
  are not multiplicity-adjusted, confirmatory tests or posterior probabilities.
- Produce a six-problem development-pilot inventory by sorting the existing
  problem identifiers by SHA-256("20260913|" + identifier), taking six, and
  retaining every candidate and valid probe request for those problems.
  Selection cannot depend on human scores or diagnostic results.
- Save original judge IDs, source cell IDs, exact repeats and payload hashes in
  the inventory. Report conceptual requests, unique cells, observed-score
  availability and the conservative one-cell-per-call workload (three repeats).
  This is a replay inventory, not permission to rerun cached cells or a quote
  for any unchosen new model. Fresh-family execution remains unstarted.

## Scale verification (no further normalization)

Use experiment30 version2's validated input loader. Human scores on [0,5] are
divided by five exactly once; judge scores are already on [0,1]. Aggregate
repeats by their median for ordering; never normalize within a problem before
subtracting the mean. Constant or tied scores retain their defined treatment.

## Verified data layout

The input loader verifies experiment29's scores, requests, criterion manifest,
property summaries and frozen probe manifest, with judge-and-cell joins and
exact reconstruction checks. Problem identity is gold_file; generation slots
agent0/1/2 are not evidence of generator-model provenance. Version2 source and
all inputs are hashed in the output manifest. No new human pool is opened.

## Preconditions and execution bound

Use the existing local Python environment and committed data, no credentials,
language-model calls or graphics devices. Expected runtime is under one minute;
stop and diagnose incomplete joins, source drift or non-finite score input.
The implementation must pass synthetic tie and between/within-problem
counterexamples and independent review before its findings are accepted.

## Fresh-family continuation contract

A later inference run needs a distinct locked panel manifest identifying actual
model, client, effort, prompt, family grouping, exact requests, repeats, retry
cap, allowance evidence and review acceptance. Test problems/families must be
reserved before model selection; the exposed 72 candidates remain development
data. Never modify experiment29's frozen runner to accept a new identity.
Use a versioned runner with a disjoint output directory. A fresh-run workload
and any required spending approval must refer to that exact manifest.

## Identity / contact crib

Repository: brando90/cert-judge, verified from the configured GitHub remote.
No external collaborator communication or credential access is needed.
