# Proxy validation

**TLDR:** This experiment tests whether the Proxy Trust Index (PTI), a behavioral score without human labels, tracks a human-grounded Trust Index (TI). The follow-up computes agreement plus repeat stability; current data contain five primary judge configurations from only two model families, so they cannot establish transfer to arbitrary agents.

## Goal and scope

The goal is a cheap measure that agrees with the expensive human-grounded
criterion on unseen outputs and agents. A judge configuration is the unit in
these current analyses; a generator agent is a different unit and requires
verified generator provenance and an appropriate held-out split.

Keep the underlying trustworthiness construct, its human-grounded criterion,
and the proxy distinct. A high score on behavioral properties does not prove
agreement with humans. Likewise, stability alone can reward a deterministic
but inaccurate control.

## Current continuation

Version3 is complete and independently reviewed. It audits whether the string-control advantage survives within-problem comparison and prepares a six-problem cached-pilot inventory; the selected cache lacks bug and missing-specification probes, and no fresh-family inference is launched. See [protocol](expt_v3/PROTOCOL.md), [report](expt_v3/results/report.md) and [meeting note](meeting_2026-09-14.md). Version2 remains frozen and complete.

## Versions and structure

```text
README.md                 scope and entry points
FINDINGS.md               corrected historical agreement-only analysis
results.md                current findings and execution status
CKPT_proxy_followups.md    resumable progress
build_panel_from_exp29.py  historical agreement-only panel extraction
design_check.py           earlier diagnostic harness and synthetic illustration
panels/                   preserved historical panels
expt_v2/
  PROTOCOL.md              exploratory follow-up definitions
  run_diagnostics.py       joint target, zero handling, uncertainty, family checks
  render_report.py         figures and readable tables
  results/                JSON, CSV, figures, and timestamped reports
```

## Method

1. Join frozen scores to 72 labeled candidates from 24 problems, retaining all three repeats and keeping the two rubric passes separate.
2. Report Pearson, Spearman, Kendall tau-b and intraclass correlation (ICC); use explicit absolute-agreement and consistency forms rather than treating all correlations as interchangeable.
3. Combine nonnegative human agreement with one minus mean within-candidate sample standard deviation, on normalized scores; retain signed correlations and the separate factors.
4. Compare the frozen proxy with declared zero-handling sensitivities, and keep primary judges separate from controls.
5. Jointly resample problems to preserve shared observations across judges; report what these conditional intervals omit.
6. Diagnose family-held-out fitted prediction against a training-mean baseline and simulate how independence affects sample-size requirements.

The combined criterion's sample standard deviation is different from the frozen
proxy's twice-population-standard-deviation convention; both are reported as
explicit alternatives. The original proxy definition and files remain frozen.

## Interpretation limits

The two rubric passes were not independent raters, and their Spearman agreement
is not measured reliability for the revised annotation pool. The square root
of reliability is a conditional classical-error Pearson calculation, not a
universal ceiling for rank correlations or for correlations across derived
judge-level criteria. The harness no longer automatically applies item-label
reliability to those outer correlations. Choose an ICC form to match the
measurement design ([Koo and Li](https://pmc.ncbi.nlm.nih.gov/articles/PMC4913118/)).

The earlier panel-size floor and tie flags are diagnostic heuristics, not
empirical power calculations. Pooled out-of-family fitted prediction can reverse a
proxy's direction and can extrapolate far outside the observed target range;
it tests that fitted prediction procedure. Its folds are dependent, and a
bootstrap of completed prediction pairs does not account for overlapping fits
([Bengio and Grandvalet](https://www.jmlr.org/papers/v5/grandvalet04a.html)).

The follow-up therefore reports raw scores, nonnegative-slope fitted linear mapping,
unrestricted fitted linear mapping, and the training-mean baseline separately, without
claiming an independent-family uncertainty interval from two families. No
whole-family train/validation/test split is available. Generation-slot labels
also do not establish generator-model families.

## Run

Use the repository's Python environment; these commands perform no model inference:

```bash
PYTHONPATH=py_src .venv/bin/python experiments/30_proxy_trust_index_held_out_validity/expt_v2/run_diagnostics.py
.venv/bin/python experiments/30_proxy_trust_index_held_out_validity/expt_v2/render_report.py
PYTHONPATH=py_src .venv/bin/python -m pytest tests/test_ti_validation.py tests/test_proxy_followups.py
```

The older `design_check.py --demo` is explicitly a synthetic sensitivity
illustration. The panel builder remains agreement-only for historical
reproduction; use the follow-up for the combined target.

## Dependencies and status

Inputs are the committed experiment-29 scores, requests, criterion manifest,
property outputs, and frozen structural-probe manifest. The follow-up uses
NumPy, SciPy and Matplotlib, performs no inference, and loads no credentials.

| Phase | Status |
|---|---|
| Historical agreement-only analysis | Complete, interpretation corrected |
| Combined criterion and aggregation diagnostics | Complete; see results.md for review status |
| Conditional uncertainty and family/design diagnostics | Complete; see results.md |
| New-family train/validation/test evaluation | Not run; current family coverage insufficient |
