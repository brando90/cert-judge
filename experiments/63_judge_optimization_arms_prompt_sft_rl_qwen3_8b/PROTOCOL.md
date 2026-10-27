# Experiment 63 (board label E61, internal run name E62): trustworthy small judges by prompt optimization, LoRA SFT and an RL pilot

**TLDR:** Can a small open-weight judge (Qwen3-8B first) be made to track the expert ratings by learning from the frontier-judge consensus, on free GPUs only? Three arms (prompt optimization with frozen weights, LoRA SFT, a GRPO-style RL pilot) on ONE frozen task split and ONE scoring script. The experiment board called this "E61"; experiment 61 in this repo is the E43 gaming-candidate run, so the folder is 62.

**Status:** protocol written 2026-10-26 about 23:20 PT, before any arm produced a number. Anything later is a dated addendum.

## Frozen inputs (all from experiment 39/58/59, nothing new is bought)
- Prompt: experiment 39's `H2` judge prompt (system rubric + 4 rated demos from train tasks, then the item). Only its final answer instruction is replaced by "Answer with ONLY one digit, 0 to 5" so that every arm reads a 0-5 score from the first answer token (thinking off). Score of a prompt = expected value of the digit distribution (EV, rescaled to [0,1]), deterministic.
- Teacher T per prompt: mean of the `score_raw` of the five frontier H2 units (`sol6h sonnet5m luna6h gem31h opus55x`) over the cells that share the prompt (3 repeats of crit and bm_gold and ident cells share one prompt). Teacher histogram over 0..5 = SFT target.
- Split (from experiment 58 `criterion_items.json`, unchanged): train 10 tasks / 30 items, val 5 / 15, test 10 / 30; the 75 human-rated items are Claude 3.7 Sonnet outputs. 249 unique prompts: train 97, val 50, test 102 (30 human-rated items among them). `pack_trainval.jsonl` is the only file arms see; `pack_test.jsonl` is not copied to any cluster before every arm is frozen (FROZEN.json written).
- Human labels: used only for evaluation, except the labelled "human-mix" variant (train items' expert mean mixed into the target, selected on val human rho).

## Arms (<= 6 configurations per arm picked on validation only)
1. Prompt optimization (Qwen3-8B frozen, thinking off): reflective search of an `<additional_guidance>` block. Proposer = the same model, shown the 6 worst train disagreements with the teacher's rationale. Objective: Spearman(EV, T) over the 97 train prompts. Up to 40 candidates per independent search, 5 independent searches (different seeds, different GPU pairs) = about 200 candidates; the top 6 of each search by train objective are scored on val teacher-Spearman; the val-best is frozen. The spread across the 5 searches is the judge SD.
2. LoRA SFT (Qwen3-8B, bf16, r=16 on all linear layers, lr 2e-4 cosine, 5 epochs, batch 8): soft cross-entropy of the digit distribution against the teacher histogram on train prompts. Epoch picked by val teacher-Spearman (<= 5 configs). 3 seeds.
3. RL pilot (same LoRA, same prompts): GRPO-style policy gradient on the digit distribution, group of 8 samples per prompt, reward = 1 - |digit - 5T|/5, KL 0.02 to the base model; capped to a few GPU-hours. Same selection rule. This is a pilot, not full RL (the action is one token).

## Controls, required for any number to count
Training: start loss vs prior (trivial) loss, train and val loss curves, tiny-batch overfit test (4 prompts must reach < 25% of start loss), shuffled-label control (same recipe on permuted teacher labels; if it still scores well on val the arm is discarded), digit mass on 0-5 near 1 (outputs not collapsed, parse is by construction), gradient norm and LR logged; W&B offline plus jsonl. Search: Spearman against a fixed shuffled teacher vector is logged for every candidate (selection-inflation null).

## Scoring (one script, `score62.py`)
On the 30 test items: Spearman, Pearson, Kendall, ICC(C,1), ICC(A,1) of EV against the expert mean, task-cluster bootstrap 95% CI (10,000 draws Spearman, 2,000 others, seed 62), plus teacher agreement over all 102 test prompts and per-judge SD across seeds/searches. Baselines on the same split: untouched Qwen3-8B with the same prompt (zero-shot), and the cached numbers of E59 (open-weight stack 0.82 [0.54, 0.91]; best label-free single judge 0.60; project bar 0.45).
Success: test human rho >= 0.75, CI lower end > 0 and paired task-cluster CI of the difference to 0.60 above 0. Null: no arm beats 0.60. Final fresh test: the 75 frontier-output ratings due 2026-11-06, scored once, no refit.

## Compute
Free GPUs only, never another user's and never another of Brando's jobs: mercury1 GPUs (vLLM 0.11, TP=2 per search), skampere1 A100-80GB for LoRA. No Duo, no paid API.
