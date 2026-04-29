# Folder 06 — PROTOCOL (LOCKED before any expensive run)

This file freezes the protocol before any LLM-budget-spending run begins.
It is written PRIOR to seeing any results. Any deviation observed during
execution is documented in `REPORT.md` → "Open questions for Ethan",
not by editing this file.

## Scientific question (locked)

Across LLM judges, does our trust index predict each judge's correlation
with human ratings, AND is the relationship reliable (low variance) under
the deployed protocol?

A judge is trustworthy iff BOTH (a) high human correlation across the
full metric panel and (b) low variance under repeated calls. The judge
unit is `(LLM + prompt + n_repeats + aggregation)`.

## Locked parameters

- `JUDGE_REPEATS = 9`
- `REPEAT_AGG = median` (primary), `mean` reported as ablation
- Trust-index v1 = headline; v2 = appendix ablation
- Bootstrap iters = 10000 (item-level)
- Permutation iters = 20000
- Per-judge human-Spearman: report 95% CI and SE
- Headline figure (paper Fig 7) uses v1 on x-axis
- Label sets: pass1, pass2, avg — headline = avg

## Pre-commit reasoning for v1 headline

v1 is the canonical certification index defined first in §2 of the paper.
v2 is an extension introduced as an ablation. Keeping v1 as the headline
is the conservative pre-commit choice — using the simpler/canonical
form for the main story and the extension as the ablation. This choice
is locked BEFORE this run, regardless of which has higher correlation
in the final results.

## Scale verification (no further normalization)

- Judge scores: returned in [0,1] by `_score_once`
  (`exp16_multi_judge_human_sets.py:222–248`).
- Human labels: 1–5 raw; loader divides by 5 (`:598`: `float(h)/5.0`).
- Both inputs are already in [0,1] before ICC/CCC.
- Do NOT divide by 10 or apply additional re-scaling.
- Smoke test will confirm; any deviation → `REPORT.md` "Open questions
  for Ethan".

## Judge panel (locked)

Smoke test (mixed Claude+Codex to catch model-dispatch breaks cheaply):
```
llm:claude-sonnet-4-20250514:P8_STRICT_B
llm:claude-sonnet-4-20250514:P4_CHECKLIST
llm:claude-sonnet-4-20250514:P1_BASELINE
llm_bad:claude-sonnet-4-20250514:BAD_STRINGY
llm:gpt-5.3-codex:P8_STRICT_B
editdist:e1:na
random:r1:na
```

Full run (expanded panel):
```
llm:claude-sonnet-4-20250514:P8_STRICT_B
llm:claude-sonnet-4-20250514:P4_CHECKLIST
llm:claude-sonnet-4-20250514:P1_BASELINE
llm_bad:claude-sonnet-4-20250514:BAD_STRINGY
llm:gpt-5.3-codex:P8_STRICT_B
llm:gpt-5.3-codex:P4_CHECKLIST
llm:gpt-5.3-codex:P1_BASELINE
editdist:e1:na
random:r1:na
```

## Cost / cache notes

- LLM judging is cached at
  `experiments/02_reviewer_response_neurips_math_ai_2026/utils/results/judge_cache.json`
  with key `"exp16:{judge_id}|{model}|{prompt_hash}|{gold_hash}|{cand_hash}"`
  (`judge_caller.py:258–263`).
- The cache key does NOT depend on `REPEAT_AGG`, so the mean ablation
  hits cache for every LLM call and does not re-spend budget — only
  the post-aggregation pipeline reruns.
- Codex judges may already be partially cached from prior EXP16 runs
  (`results_exp16_final_robust/`); fresh Claude calls are uncached.

## Estimated wall-clock

- Smoke (3 repeats, 1K bootstrap): ~30–60 min
- Full median (9 repeats, 10K bootstrap, expanded panel): ~2–5 h
- Full mean (cache reuse): ~minutes
- Exp17 (6 invocations): ~minutes total
- Exp19 replot: ~seconds
- Full trust-metric panel (new script): ~minutes

## Pass/fail / abort rules

- Smoke must produce a valid `summary.json` (judges listed, no NaN flood,
  plausible correlations) before the full run is launched.
- During Step 4 (mean ablation), if any LLM call shows `cached: false`,
  STOP and document the cause before proceeding.
- No silent post-hoc parameter changes. Every variant tried goes in
  `REPORT.md`. Defensible best-effort decisions on ambiguities go in
  `REPORT.md` → "Open questions for Ethan."

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
- Anthropic key path: `~/keys/anthropic_bm_key_koyejolab.txt`
