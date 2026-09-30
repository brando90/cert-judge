# Cost quote: experiment 39 judge campaign (planning estimate from the dry run)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/COST_QUOTE.md>

**TLDR:** 45,136 judge calls over 50 LLM configurations (upper bound: the dry run could not elaborate probes, so no probe was excluded), expected about **$1,084** on Vals-reported charges, of which the two test models cost $641 (Claude Opus 5.5 at max effort alone $579). Hard cap $1,600 (`scripts/e39.py` `CAP_USD`). The exact quote is regenerated on SNAP by `scripts/quote.py` after Lean validation and lands in `results/QUOTE.json`.

**Status:** PLANNING ESTIMATE, nothing spent · **Date:** 09-30-2026 · **Source:** `results/planning_dryrun/QUOTE.json` (dry run in the cloud container against the local VeriBench checkout, `--no-lean`, `--allow-unvalidated`)

## Calls per configuration (before Lean exclusions)

| Cell kind | Cells | Repeats | Calls | Note |
|---|---:|---:|---:|---|
| crit (75 rated candidates) | 75 | 3 | 225 | criterion items; level 0 of the candidate ladders |
| ident (gold as candidate) | 25 | 3 | 75 | identity; level 0 of the gold ladders |
| blank | 25 | 1 | 25 | deterministic 0.0 under D0 (no call) |
| ms_gold (statement deletion, ≤ 4 levels) | 57 | 1 | 57 | |
| ms_cand (statement deletion, ≤ 3 levels) | 122 | 1 | 122 | |
| bm_gold (bug ladder, ≤ 4 levels) | 58 | 3 | 174 | 42 declared levels had no compile-valid mutation even before Lean |
| alpha | 67 | 1 | 67 | 8 candidates have no conservative binder to rename |
| reorder | 27 | 1 | 27 | only candidates with ≥ 2 theorem declarations |
| sorry | 73 | 1 | 73 | |
| spam | 75 | 1 | 75 | |
| **Total** | | | **920** | D0 configurations: 776 calls + 112 deterministic + 32 unmeasured (extraction) |

## Quote by judge model

| Model (split) | Configurations | Calls | Expected USD | Basis |
|---|---:|---:|---:|---|
| GPT-6 Sol high (train) | 9 | 8,136 | 97.63 | measured $0.012/call (experiment 100 receipts; experiment 103 route $0.0115–0.0142) |
| Claude Sonnet 5 medium (train) | 9 | 8,136 | 130.18 | measured $0.016/call (experiment 100 `ab_R4_sonnet5`) |
| GPT-6 Luna high (val) | 9 | 8,136 | 9.09 | $0.1 / $0.5 per M tokens, bytes/3.5 input + 1,500 output tokens |
| Gemini 3.1 Pro high (val) | 9 | 8,136 | 206.24 | $2 / $12 per M tokens, same token assumption |
| Claude Opus 5.5 max (test) | 5 | 4,456 | 579.28 | measured $0.13/call (experiment 100 $0.106–0.131; experiment 103/105 route $0.112–0.154) |
| Qwen3.6-27B (test) | 9 | 8,136 | 61.87 | $0.6 / $3.6 per M tokens, same token assumption |
| **Total** | **50** | **45,136** | **1,084.28** | train $227.81 · val $215.33 · test $641.15 |

Worst-case admission bound (every call billed at `max_tokens` output, experiment 100's reservation rule): $20,022. It is not an estimate of spend; actual output is 300–4,000 tokens per call. Vals-reported charges are the record; the cap applies to them.

## What could move the number

- Lean validation removes every probe derived from a candidate that does not elaborate (the 2026-05 Claude 3.7 samples include non-compiling files), so the real count is lower.
- A substitute selector (PROTOCOL.md) changes that model's price; Luna-5.6 is $0.2 / $1.2 per M tokens.
- Opus 5.5 reasoning length dominates: its per-call mean ranged $0.106–$0.166 across experiment 100's runs.

## Route and approval

Every call goes through Valkyrie (`valk run start --agent vb103_judge ...`), Vals-funded; no personal or provider key. The cap $1,600 is the approved spend for this experiment; the worker writes `private/HOLD_JUDGE_ADMISSIONS` when reported charges reach it.
