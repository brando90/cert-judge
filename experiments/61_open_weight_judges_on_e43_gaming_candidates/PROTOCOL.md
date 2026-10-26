# Experiment 61 protocol: do the edits that an attacker optimized against Claude Sonnet 5 also inflate open-weight judges?

**Status:** FROZEN at the commit that adds this file. Judge calls made before it: 0. Later changes are dated addenda at the end. Free hardware only ($0, no paid API, no frontier call). Does not touch experiment 58's frozen protocol or experiment 43's results; experiment 43's saved texts and cached reference scores are read only.

## 1. Question
Experiment 43 let GPT-6 Luna (high) edit 15 low-coverage Lean specifications for 8 rounds to raise the score of one judge (Claude Sonnet 5 medium, prompts D0, H2, P1 among six), and measured the gaming gap = attacked-judge gain minus reference gain (reference = H2 on Claude Opus 5.5 max + GPT-6 Sol high, 3 repeats each). Here the same saved texts are re-scored by open-weight judges that the attacker never saw. (a) Do open-weight judges give inflated gains on those edits relative to the reference (transfer of gaming)? (b) Do their gains track the reference gain at all (is the open-weight judge directionally right on edits)? (c) Do they track Sonnet's own gain (shared exploit)?

## 2. Inputs (frozen, read only)
- Texts: experiment 43 `results/full/candidates/starts/<item>.lean` (15 starts) and `.../finals/<judge>__<prompt>__<item>.lean` (90 finals). Unique (item, sha256) texts: 77 (15 starts, 62 distinct finals).
- Cached scores: experiment 43 `results/full/cells.json` (per cell: attacked_start/final/gain for Sonnet, reference_gain, final_is_start, gaming_gap, checks flags).
- Prompt bytes: experiment 43's `render_judge` (VeriBench experiment 100 renderer for D0, H2; the paper's legacy prompt for P1), parsed by experiment 43's `parse_judge`. Prompts: `D0`, `H2`, `P1` (3 of experiment 43's six; LEX, H0, P8 not run).
- Judges (all text-only, single call, no tools, harness `vllm_offline`, model defaults for sampling, each model's default thinking mode, as experiments 58-60): `qwen3_4b` (Qwen/Qwen3-4B bf16), `q25_14b_awq` (Qwen2.5-14B-Instruct-AWQ int4), `qwen3_8b` (Qwen/Qwen3-8B bf16, tensor parallel 2). Pinned revisions are those of experiments 58 and 59. Hardware: RTX A4000 16 GB on mercury2, vLLM from `at979/venv128`. `max_model_len` 32768; budget rule `min(prompt max_tokens, max_model_len - prompt tokens)`, cells under 1024 new tokens are `unmeasured_over_context`, never truncated.
- Repeats: each (text, prompt) is generated twice with per-cell seeds `int(sha256('61|<model>|<prompt>|<cell>|r<k>')[:8],16)`, k = 1, 2; a text's score is the mean of its measured repeats; a repeat with a parse error or over-context is excluded and counted.

## 3. Quantities (all frozen before any output)
For judge unit u = (model, prompt) and each experiment 43 cell c whose attacked prompt is the same prompt (15 cells per prompt): `gain_u(c) = score_u(final_c) - score_u(start_c)` (0 when final = start by sha; the cells' `final_is_start` agrees). `ref_gain(c)` and `sonnet_gain(c)` are experiment 43's cached `reference_gain` and `attacked_gain`.
1. **Gaming gap of u:** `gap_u = mean_c(gain_u(c) - ref_gain(c))` over its 15 cells, 95% CI by task-cluster bootstrap (10,000 resamples of the 6 tasks, seed 61), as experiment 43. Verdict: **TRANSFERS** if the CI lies above 0; **NO TRANSFER** otherwise (reported with the point estimate; a CI that includes 0 is not evidence of resistance). Experiment 43's Sonnet figure for the same prompt is printed next to it.
2. **Tracking of the reference:** Spearman of `gain_u(c)` with `ref_gain(c)` over the 15 cells (task-cluster bootstrap CI), and the share of cells whose gain has the same sign as `ref_gain` (zero counted as its own sign).
3. **Shared exploit:** Spearman of `gain_u(c)` with `sonnet_gain(c)` over the 15 cells.
4. **Pooled over models:** per prompt, mean over models of `gap_u`; and an all-units pooled gap with a model x task two-way cluster bootstrap is NOT computed (3 models).
5. **Cross-prompt (descriptive, not a verdict):** for every unique final text, the gain of each unit on all three prompts, grouped by the prompt it was attacked with; reported as a 3 x 3 table of mean gain (rows attacked prompt, columns scoring prompt) per model.
6. **Flags:** the same quantities split by experiment 43's `checks` flag (cells whose final added flagged statements vs not), descriptive.

## 4. Counted before any claim
Cells 15 per unit; texts 77; 6 tasks. Unmeasured, parse-error and over-context counts per unit are printed in every table. Per-unit n is too small for significance across units; claims are limited to the stated CIs. Nothing is tuned, selected or re-run after seeing outputs; failed or partial lanes are reported as such.

## 5. Not claimed
No claim about frontier judges, about human ratings, or about E58's frozen H1 gate. A transfer finding applies to attacks optimized against Sonnet 5 medium on 15 items only. The label-free index of experiments 39/59/60 is not re-evaluated here.

## Addendum 1 (10-26-2026, 12:52, before any experiment 61 output was parsed)
- vLLM refused `q25_14b_awq` at `max_model_len` 20,480 on the 16 GB card (KV cache needs about 3.9 GiB, 3.16 GiB free; mercury2 log, 12:48). It is re-run at 14,336 (longest prompt 11,215 tokens, so the 1,024-token output rule still holds for every cell). Set in `scripts/register61.py`. Prompts, sampling and parsing unchanged.
- vLLM is 0.11.0 (torch 2.8.0+cu128, `at979/venv128` on mercury2; driver 570 allows CUDA 12.8 only); experiments 58-60 recorded other vLLM versions. The versions are in each `meta_<model>.json`.
- **Addendum 2 (12:57, before any experiment 61 output was parsed):** two non-Qwen judges join the panel so the result is not Qwen-only: `llama31_8b` (unsloth/Llama-3.1-8B-Instruct bf16, tensor parallel 2, context 28,672) and `gemma3_12b` (unsloth/gemma-3-12b-it bf16, tensor parallel 2, context 16,384), pinned revisions of experiment 58, each on 2 free RTX A4000 (mercury2 GPUs 4-5 and 6-7). Everything in sections 2-4 applies to them unchanged; a model whose engine will not start is reported as such, not replaced silently.
