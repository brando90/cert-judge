# Experiment 63: can a small open-weight judge be trained to track the expert ratings? (prompt optimization vs LoRA SFT vs RL pilot)

**TLDR:** Qwen3-8B (thinking off, one-digit 0-5 readout) judged 30 expert-rated test items from 10 held-out tasks. Zero-shot it is anti-correlated with the experts (Spearman -0.16). Prompt optimization did not transfer (-0.13 / -0.21). LoRA SFT on the frontier-judge consensus reaches human Spearman 0.65-0.89 per seed (3-seed mean 0.76, SD 0.12; seed ensemble 0.78 [0.44, 0.90]). SFT with expert labels mixed into the target (the human-mix variant) reaches 0.81-0.85 (mean 0.83, SD 0.03). The RL pilot reaches 0.51-0.59 (mean 0.54, SD 0.04). The shuffled-label control scores 0.02, so the SFT gain is not leakage. With 10 test tasks every CI is wide and no arm has a lower CI end above 0.75, so this is promising, not validated. The 75 frontier-output ratings due Nov 6 are the confirmatory test.

The board called this E61 and the run directory E62; folder 61 and 62 in this repo were already taken (gaming candidates, label-free selection), so it lives here as 63. Protocol: `PROTOCOL.md`, written before any arm produced a number.

## Setup (all frozen before the test split was scored)
- Model Qwen3-8B, prompt = experiment 39's `H2` judge prompt with the answer instruction replaced by "Answer with ONLY one digit, 0 to 5"; score = expected value (EV) of the digit distribution, rescaled to [0, 1]. Deterministic, no sampling at test time.
- Split from experiment 58: train 97 prompts / val 50 / test 102 prompts; the 30 human-rated test items (Claude 3.7 Sonnet outputs, 10 tasks) are the human test. The test pack was copied to the cluster only after every run had a `FROZEN.json` (sha256 in `results/pack_manifest.json`). One scoring pass per arm, no refit.
- Teacher target = mean of five frontier H2 units over the cells sharing a prompt. Human labels were used only for evaluation, except in the labelled human-mix SFT variant (train items' expert mean mixed 50/50 into the target; epoch chosen on val human rho).
- Arms: (1) prompt optimization, reflective search of a guidance block, 2 independent searches x 80 candidates; (2) LoRA SFT r=16, lr 2e-4, 4 epochs, 3 seeds, epoch chosen on val teacher Spearman; (2b) human-mix SFT, 2 seeds, epoch chosen on val human Spearman; (3) RL pilot, GRPO-style on the digit distribution, group 8, KL 0.02, lr 5e-5, 3 epochs, 3 seeds.
- Compute: mercury1 and mercury2 free A4000 16 GB cards (3 GPUs per 8B run, model-parallel), free hardware only, no paid API. W&B logged offline (`wandb/` stayed on the cluster; curves are in `curves.json` and `train_log.jsonl`).

## Test results: agreement with the expert mean on the 30 human-rated test items
Full table with Pearson, Kendall, ICC(C,1), ICC(A,1) and task-cluster bootstrap 95% CIs (10 tasks as clusters; 10,000 draws for Spearman, 2,000 for the rest, seed 62): `results/report_test.md` (json beside it).

| arm | seeds | Spearman, each seed | mean | SD across seeds | seed-ensemble Spearman [95% CI] | teacher rho (102 prompts) |
|---|---|---|---|---|---|---|
| zero-shot Qwen3-8B | 1 | -0.16 [-0.57, 0.55] | -0.16 | | | 0.29 |
| prompt optimization | 2 searches | -0.13, -0.21 | -0.17 | 0.05 | -0.18 [-0.60, 0.47] | 0.26-0.28 |
| LoRA SFT (teacher only) | 3 | 0.89, 0.65, 0.75 | 0.76 | 0.12 | 0.78 [0.44, 0.90] | 0.85-0.89 |
| LoRA SFT + expert labels (human-mix) | 2 | 0.85, 0.81 | 0.83 | 0.03 | 0.82 [0.41, 0.96] | 0.87-0.90 |
| RL pilot | 3 | 0.51, 0.52, 0.59 | 0.54 | 0.04 | 0.56 [0.31, 0.76] | 0.66-0.69 |
| shuffled-label control (SFT) | 1 | 0.02 [-0.36, 0.47] | 0.02 | | | -0.10 |

Per-judge SD (how much a judge's score varies): SD of Spearman across seeds in the table; mean per-prompt SD of EV across seeds (EV on [0,1]): SFT 0.046, human-mix 0.051, RL 0.073, prompt search 0.027 (`results/report_ensembles.md`). For scale, the spread of EV over test prompts is about 0.24-0.34.

Success rule from the protocol: test human rho >= 0.75 AND the paired task-cluster CI of the difference to 0.60 above 0. Result: no arm passes on the lower-CI part (only SFT seed 0, 0.89 [0.65, 0.96], has a lower end above 0.60). By seed means, SFT (0.76) and human-mix SFT (0.83) clear 0.75; RL and prompt optimization do not. Honest summary: SFT-type training clearly helps over zero-shot and over the prompt search; whether it beats the earlier 0.60 open-weight baseline is not settled at n = 30 items from 10 tasks.

## Sanity checks (every one required before a number counted) - `results/sanity.json`, `results/runs/*/curves.json`
- Loss goes down: SFT train loss per epoch falls monotonically for s0 and s2 (2.35 -> 0.67, 1.85 -> 0.56), s1 (1.83 -> 0.54), human-mix s0 (2.50 -> 0.75); human-mix s1 had a bump in epoch 3 (0.98 -> 1.07, then 0.64). Start prior cross-entropy (uniform-ish baseline) is 1.67-1.70. The RL "loss" is a policy-gradient surrogate and is not comparable; its signal is validation Spearman with the teacher, 0.51 at start to 0.86-0.87 at epoch 3 on all three seeds, with reward rising.
- Tiny-batch overfit test: 4 prompts, loss 2.79 -> 0.20 (7% of start, bar < 25%): passed (`runs/sft_overfit/OVERFIT_TEST.json`).
- Shuffled-label control: val teacher rho 0.11 and test human rho 0.02: passed (no leakage from the recipe).
- Output sanity: digit mass on 0-5 on the test pass is >= 0.996 for every run (1.000 for zero-shot, prompt search and RL; lowest SFT s1 0.9961); parse is by construction (first-token digit distribution). No collapse of the score: EV spread over test prompts 0.27-0.34 vs 0.24 zero-shot. One caveat: the RL policy entropy fell during training (s0 0.64 -> 0.53, s1 0.55 -> 0.23, s2 0.64 -> 0.003, i.e. s2 became almost deterministic), and KL to the base model ended at 2.2 (s0), 0.23 (s1), 0.48 (s2); mean training reward rose from about 0.76 to 0.89 (s0), 0.87 (s1), 0.81 (s2).
- Gradient norm and LR: LR follows warmup + cosine (SFT 2e-5 -> 2e-4, RL 5e-6 -> 5e-5). SFT grad-norm medians 4-6, with the largest values in the first steps (e.g. 105 at step 3 of SFT s0); RL medians 10-15 with spikes up to 120 (RL s1). No NaN and no divergence, but RL grad norms are large and spiky, so treat RL as a pilot with untuned optimization, not a verdict on RL.
- Same frozen split and the same scoring script (`code/score62.py`) for every arm.

## Caveats
- 30 items from 10 tasks: CIs are 0.4-0.6 wide. The 15 human-rated val items used to pick the human-mix epoch are also noisy (the shuffled control scored 0.60 on them at epoch 1 by chance).
- All 75 human-rated items are Claude 3.7 Sonnet outputs; transfer to frontier-agent outputs is untested until the Nov 6 ratings arrive.
- Human-mix SFT sees train-item expert labels, so it is a labelled-data method, not label-free.
- Prompt optimization selected on train Spearman with the teacher (0.57-0.59 train) and val teacher 0.2-0.4 with val human negative: the search overfit the 97 train prompts.
- One base model (Qwen3-8B) and one readout (first-token digit). Larger sharded models were not run (the 8B arms used 3 GPUs each).

## Files
`PROTOCOL.md`; `code/` (build_pack.py, sft_lora.py, search_arm1.py, vllm_eval.py, score62.py, launch and eval scripts, sanity.py, ensembles.py); `results/report_test.md|json`, `results/report_ensembles.md|json`, `results/sanity.json`, `results/runs/<run>/{FROZEN.json,curves.json,train_log.jsonl,eval_test.json}`, `results/pack_manifest.json`. LoRA adapters stay on the cluster at `/dfs/scratch0/brando9/e62/runs/<run>/ep<N>` (SNAP).
