# Experiment 59 status (live; updated by hand at each check)

Caveat first: the human ratings are 75 Claude 3.7 Sonnet zero-shot items only; there are no ratings of frontier-judge outputs until 2026-11-06, so everything here tests agreement with those ratings and with the saved frontier/open reference judges, not agreement on frontier outputs.

## 2026-10-24 21:00 (first look, Part 1 only)

| Lane | Host / GPU | Model (prompts) | State |
|---|---|---|---|
| A | skampere1 GPU 5 (A100 80 GB) | llama31_8b (9 prompts) | done 20:26, 9 of 9 harvested |
| A | same GPU | llama33_70b_awq (H2 only; the open reference) | running since 20:49 (521 cells) |
| A | same GPU, next | q25_14b_awq, q3_30b_a3b_fp8, qwen3_8b, qwen3_14b | queued; each waits for the GPU to be empty (< 500 MiB) |
| B | mercury2 GPU 9 (16 GB) | qwen3_4b (9 prompts, thinking) | running; D0 done, R4 under way at 20:50 (about 40 min per prompt, so about 6 h for the model) |

Notes: Qwen3 4B did not start at the 40,960-token context on the 16 GB card, so it runs at 28,672 (protocol addendum 2). Lane A was re-queued once to run the 70B reference early (addendum 3). Other GPUs on skampere1-3 and mercury1-2 were not empty (>= 2 GiB used), so nothing else was started. Weights live under /dfs/scratch0/brando9/at1209_hf and are deleted per model (llama31_8b's are still there until its run ends).

### First look (Part 1 only, no learner fitted, test split not read; `results/interim_2026-10-24_2105_part1_only/`)

Units: the 9 Llama 3.1 8B prompts (new) plus the 9 saved Qwen3.6-27B units (hosted open-weight, E39), so 18 units from 2 models. Criterion = Spearman of the unit's median-of-3 item score with the three-expert mean over the 45 val+test items (human ratings are Claude 3.7 Sonnet outputs only). Intervals are unit-bootstrap and the model-clustered test is not computable with 2 models, so every verdict here is INCONCLUSIVE by design, not a result.

- Llama 3.1 8B units agree poorly with the experts (criterion rho from -0.30 to 0.44; D0 0.44, H2 0.08); Qwen3.6-27B units are mostly high (H1 0.86, R4 0.83, H0 0.83, H2 0.82, D0 0.73; LEX -0.29).
- Over the 18 units: `F2_item` (agreement with the frontier consensus on the 75 items) 0.971 [0.89, 0.99]; `F1_probe` 0.709 [0.31, 0.88]; frozen `C_ms_gold` 0.664 [0.16, 0.91] (n=15 computable); `TI_var_trainnorm` -0.063. The frozen `C_ms_gold` is high mainly because the two models differ, not within a model: over the 8 computable Llama units alone it is 0.357 and `F1_probe` 0.000, while `F2_item` is 0.933 (n=9).
- Open-reference arm (reference = Qwen3.6-27B, subjects = the 9 Llama units): `F2_item@O_qwen36` 0.950 [0.72, 1.00], `F1_probe@O_qwen36` -0.133. The 70B reference is still running; `O_llama70` and `O_both` appear after it lands.

Read this as a plumbing check and a direction, not as evidence: two models, nine small-model units, one pass.

## 2026-10-24 21:30 (second look, Part 1 only; `results/interim_2026-10-24_2130_part1_only/`)

State: llama31_8b done (9/9); Llama 3.3 70B AWQ H2 done (521/521, but degenerate: 506 of 521 raw scores are 5, all 225 criterion cells score 1.0, so it carries no signal as a reference; protocol addendum 5); q25_14b_awq running (D0, H0, R4 done); qwen3_4b on mercury2 at 2 of 9 prompts (about 50 min per prompt). Next on the A100: Qwen3-32B thinking, FP8, H2 only (the second large open reference, addendum 5), then q3_30b_a3b_fp8, qwen3_8b, qwen3_14b.

Part 1 only, 22 units from 5 models (Llama 3.1 8B, Qwen3 4B x2 prompts, Qwen2.5 14B AWQ x3 prompts as new; Qwen3.6-27B saved as hosted), so still partial and every verdict is INCONCLUSIVE (model-clustered test needs more models):

- `C_ms_gold` vs expert agreement: Spearman 0.717 [0.30, 0.92], n = 18 units; `F1_probe` 0.719 [0.39, 0.88]; `F2_item` 0.952 [0.82, 0.99]; `F12` 0.939 [0.80, 0.98]; frozen PTI_v0 0.058, TI_var -0.038. On the 12 new units alone: C_ms_gold 0.664 (n=11), F1 0.524, F2 0.909.
- Open reference Qwen3.6-27B as the smart judge: it agrees with the frontier consensus (probe cells 0.941, 75 items 0.858) and with the experts (0.817 on the 45 items, the frontier consensus 0.811), so on these items it is as good a judge as the frontier consensus. As the reference for the small judges, `F2_item@O_qwen36` is 0.944 [0.74, 1.00] and `F12@O_qwen36` 0.844 [0.55, 0.95] over 12 units.
- The 70B arm is undefined (constant scores), as above.

Still a plumbing check and a direction: five models, partial prompts, one pass, human ratings are Claude 3.7 Sonnet outputs only.

## 2026-10-24 22:55 (third look, Part 1 only; `results/interim_2026-10-24_2255_part1_only/`)

Done: llama31_8b (9/9), q25_14b_awq (9/9), llama33_70b_awq (H2), qwen3_32b (H2, 521/521, 13 min after load). Running: q3_30b_a3b_fp8 (A100, since 22:41), qwen3_4b (mercury2, 3/9 prompts, about 55 min per prompt, so done about 04:00). Queued: qwen3_8b, qwen3_14b.

Part 1 over 32 open-weight units from 6 models (Llama 3.1 8B x9, Qwen2.5 14B AWQ x9, Qwen3 4B x3, Qwen3-32B H2, Llama 3.3 70B H2, and the saved Qwen3.6-27B x9), still partial and not a verdict (model-clustered test has 1 usable model so far):

- Frozen `C_ms_gold` vs agreement with the experts: Spearman 0.554 [0.17, 0.80] (n = 28 units; it was 0.717 at 22 units, so it moves a lot with the unit set); `F1_probe` 0.712 [0.43, 0.86]; `F2_item` 0.936 [0.84, 0.97]; `F12` 0.903 [0.79, 0.95]; frozen PTI_v0 0.139 [-0.04, 0.40]; TI_var -0.128.
- Qwen3-32B (thinking, FP8) as a judge: agreement with the experts 0.736 on the 45 items (H2); against the frontier consensus 0.867 on probe cells and 0.682 on the 75 items. As a reference (`O_qwen32`): `F2_item` 0.934 [0.83, 0.97], `F12` 0.913 [0.82, 0.95], `F1_probe` 0.688 [0.39, 0.84] over 30 units. Qwen3.6 + Qwen3-32B together (`O_both`, 21 units): `F2_item` 0.929, `F12` 0.839, `F1_probe` 0.458 [0.01, 0.71].
- Llama 3.3 70B AWQ arm: undefined (constant scores).
- Small judges so far agree weakly with the experts (Qwen2.5 14B AWQ: D0 0.56, R4 0.19, H2 0.19; Llama 3.1 8B: up to 0.44; Qwen3 4B: D0 0.46, H0 0.37, R4 0.50).

Reading so far: an agreement-with-a-bigger-open-model index tracks agreement with the human ratings across prompts and models (about 0.9 over the 75 items); the label-free frozen index is weaker and less stable (0.55-0.72 depending on the unit set), and the old PTI/TI_var show nothing. Caveats: partial panel, units differ in model and prompt (the correlation is partly between-model), human ratings are Claude 3.7 Sonnet outputs only, no frontier ratings until Nov 6.
