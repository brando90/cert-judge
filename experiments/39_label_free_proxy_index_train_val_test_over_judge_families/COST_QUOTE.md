# Cost quote: experiment 39 judge campaign (planning estimate from the dry run)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/COST_QUOTE.md>

**TLDR:** 51,500 judge calls over 56 LLM configurations — 46,316 single-call cells plus 5,184 Terminus2 agent-judge cells (upper bound: the dry run could not elaborate probes, so no probe was excluded) — expected about **$1,421** on Vals-reported charges, of which the test split costs $958 (Claude Opus 5.5 at max effort $594, the Terminus2 + Sonnet 5 agent judge $249). No automatic spend cap (PROTOCOL.md Amendment 1; `scripts/e39.py` `CAP_USD = None`). Every call, single or agent, goes through Valkyrie. The exact quote is regenerated on SNAP by `scripts/quote.py` after Lean validation and lands in `results/QUOTE.json`.

**Status:** PLANNING ESTIMATE, nothing spent · **Date:** 09-30-2026 · **Source:** `results/planning_dryrun/QUOTE.json` (dry run in the cloud container against the local VeriBench checkout, `--no-lean`, `--allow-unvalidated`)

## Calls per configuration (before Lean exclusions)

| Cell kind | Cells | Repeats | Calls | Note |
|---|---:|---:|---:|---|
| crit (75 rated candidates) | 75 | 3 | 225 | criterion items; level 0 of the candidate ladders |
| ident (gold as candidate) | 25 | 3 | 75 | identity; level 0 of the gold ladders |
| blank | 25 | 1 | 25 | deterministic 0.0 under D0 (no call) |
| ms_gold (statement deletion, ≤ 4 levels) | 83 | 1 | 83 | after the 09-30-2026 finder fix (57 before it) |
| ms_cand (statement deletion, ≤ 3 levels) | 122 | 1 | 122 | |
| bm_gold (bug ladder, ≤ 4 levels) | 58 | 3 | 174 | 42 declared levels had no compile-valid mutation even before Lean |
| alpha | 67 | 1 | 67 | 8 candidates have no conservative binder to rename |
| reorder | 27 | 1 | 27 | only candidates with ≥ 2 theorem declarations |
| sorry | 73 | 1 | 73 | |
| spam | 75 | 1 | 75 | |
| **Total** | | | **946** | D0 configurations: 782 calls + 132 deterministic + 32 unmeasured (extraction) |

## Quote by judge model

| Model (split) | Configurations | Calls | Expected USD | Basis |
|---|---:|---:|---:|---|
| GPT-6 Sol high (train) | 9 | 8,350 | 100.18 | measured $0.012/call (experiment 100 receipts; experiment 103 route $0.0115–0.0142) |
| Claude Sonnet 5 medium (train) | 9 | 8,350 | 133.63 | measured $0.016/call (experiment 100 `ab_R4_sonnet5`) |
| GPT-6 Luna high (val) | 9 | 8,350 | 9.36 | $0.1 / $0.5 per M tokens, bytes/3.5 input + 1,500 output tokens |
| Gemini 3.1 Pro high (val) | 9 | 8,350 | 211.82 | $2 / $12 per M tokens, same token assumption |
| Claude Opus 5.5 max (test) | 5 | 4,566 | 593.58 | measured $0.13/call (experiment 100 $0.106–0.131; experiment 103/105 route $0.112–0.154) |
| Qwen3.6-27B (test) | 9 | 8,350 | 63.55 | $0.6 / $3.6 per M tokens, same token assumption |
| Terminus2 agent + GPT-6 Luna (val) | 2 | 1,728 | 8.31 | agent: 4 turns × (bytes/3.5 + 3,000) input tokens + 2,000 output tokens per cell (assumption) |
| Terminus2 agent + Claude Sonnet 5 (test) | 2 | 1,728 | 249.14 | same agent assumption at $3 / $15 per M tokens |
| Terminus2 agent + Qwen3.6-27B (test) | 2 | 1,728 | 51.90 | same agent assumption at $0.6 / $3.6 per M tokens |
| **Total** | **56** | **51,500** | **1,421.43** | train $233.81 · val $229.49 · test $958.17 |

Worst-case admission bound (every call billed at `max_tokens` output, experiment 100's reservation rule): $21,566. It is not an estimate of spend; actual output is 300–4,000 tokens per call. Vals-reported charges are the record.

## What could move the number

- Lean validation removes every probe derived from a candidate that does not elaborate (the 2026-05 Claude 3.7 samples include non-compiling files), so the real count is lower.
- A substitute selector (PROTOCOL.md) changes that model's price; Luna-5.6 is $0.2 / $1.2 per M tokens.
- Opus 5.5 reasoning length dominates: its per-call mean ranged $0.106–$0.166 across experiment 100's runs.
- The agent-judge estimate has no measured basis: a Terminus2 judge episode may take fewer than 4 turns (cheaper) or loop (the bundle's `max_turns` kwarg, 20 where exposed, bounds it).

## Route and approval

Every call goes through Valkyrie (`valk run start --agent vb103_judge ...` for single-call judges, `--agent <recorded Terminus2 bundle>` for agent judges), Vals-funded; no personal or provider key. There is no automatic spend cap (PROTOCOL.md Amendment 1, 09-30-2026): charges never hold admissions; the worker records Vals-reported charges in `results.md` after every merge.
