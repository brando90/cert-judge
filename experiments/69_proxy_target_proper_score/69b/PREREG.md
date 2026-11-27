# PREREG: experiment 69B, native 6-class scores on the 100 new files

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/69_proxy_target_proper_score/69b/PREREG.md>

**Written 11-26-2026 before any judge call.** Brando approved lanes A and B and a cap of $27 (11-26-2026). No Gemini Antigravity (`agy`). This checkout has no API key and no SNAP login, so the calls are not run here.

## Question

On the 250 main ratings (100 files, 25 tasks), does a headline judge's native 6-class forecast beat the constant forecast (CONST) on held-out Ranked Probability Score (RPS)? The 74% mass at score 5 makes CONST strong. Cross-entropy (CE) and total variation distance (TVD) are secondary. Spearman and Pearson are diagnostic.

A native forecast is the renormalized probability of the next-token digits 0 through 5 (one token, temperature 0). It is not three scalar repeats that are later binned.

## Judges

1. `snap_qwen3_8b` — local SNAP vLLM, `$0`. Default model `Qwen/Qwen3-8B`. If `CJ69_SNAP_MODEL` names a local Qwen snapshot, that path is used and written on the receipt. This is the open-weight digit-distribution judge from experiment 63.
2. `api_frontier` — one plan-lane model, not Gemini and not Antigravity. Model id is `CJ69_API_MODEL`. The process stops before a call that would put the running total over $27, including a 2-file probe. If the probe has no dollar cost, the batch does not start.

No other model is admitted. Label-free probe ladders (`C_ms_gold` and the rest) are not rebuilt here; that would be a second call budget.

## Items and join

The 100 files are trustworthy-theorem-judges experiment 09 `rating_task_packet/main_rating_task/`, gold at `{task}/gold_lean/reference.lean`, candidate at the path in the rating CSV. Join ratings on `item_id`. Donald Poindexter Jr (T06) `item020` has `candidate_file` text `this one has borderline spam.`; the path is taken from the other raters' row for that same `item_id` (`task_16_certificate_hostname/agent_lean/agent_2.lean`). The score stays 5.

## Prompt

The rater rubric in that packet (`human_judgements_prompt.md`: statement coverage, scores 0–5, tie-break toward the lower score) plus the gold and candidate Lean text, each truncated at 12,000 characters. The last line is `Answer with ONLY one digit, 0 to 5.`

## Decision

A judge beats CONST when the mean paired task difference `RPS_judge − RPS_CONST` is negative and its 95% task-bootstrap interval excludes 0 (2,000 draws, seed 69, p-val=n/a). A dry-run forecast is labeled `DRY_RUN` and is not this decision.

## Stops

Missing packet, missing key, a Gemini or `agy` model id, a projected total above $27, or a response with no digit logprobs (those items stay unmeasured; they are not filled with 1/6).
