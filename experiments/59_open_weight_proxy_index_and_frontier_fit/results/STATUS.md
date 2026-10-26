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

## 2026-10-25 01:20 (fourth look, Part 1 only; `results/interim_2026-10-25_0120_part1_only/`)

Done: llama31_8b, q25_14b_awq, q3_30b_a3b_bf16 (the bf16 replacement of the crashed FP8 run, addendum 6), qwen3_8b (all 9/9), llama33_70b_awq and qwen3_32b (H2). Running: qwen3_14b on skampere1 GPU 5 (D0 started 01:03; 9 prompts, thinking), qwen3_4b on mercury2 GPU 9 (7 of 9 harvested, P8 under way). No learner is fitted and the test split is not read (`--part1-only`).

Part 1 over 54 open-weight units from 8 models (7 new models plus the saved Qwen3.6-27B), criterion = Spearman with the three-expert mean on the 45 val+test items (human ratings are Claude 3.7 Sonnet outputs only):

- Frozen primary `C_ms_gold`: Spearman 0.453 [0.16, 0.68], n = 50 units, plain permutation p 0.0005, but the model-clustered check is 0.169 (p 0.33, only 3 models fully computable), so the verdict is INCONCLUSIVE (plain PASS, clustered not). On the new units only: 0.356.
- `F1_probe` (agreement with the frontier consensus on probe cells) 0.652 [0.42, 0.82]; `F2_item` (agreement on the 75 items) 0.937 [0.88, 0.96]; `F12` 0.925 [0.87, 0.95]; frozen `PTI_v0` 0.221 [0.05, 0.41]; `TI_var` 0.038.
- Open-weight smart reference instead of the frontier consensus: `F12@O_qwen36` 0.877 [0.79, 0.92] (model-clustered p 0.041), `F12@O_qwen32` 0.931 [0.88, 0.95] (p 0.010), `F12@O_both` 0.908 [0.83, 0.94] (p 0.041). Qwen3.6-27B agrees with the frontier consensus (0.858 on 75 items) and with the experts (0.817); Qwen3-32B 0.682 and 0.736. Llama 3.3 70B AWQ is constant (undefined).
- Reading: an index that asks "does this small judge agree with a bigger open judge" works about as well as asking it against the frontier consensus, and far better than the label-free index; caveat: much of this is between-model and the experts themselves agree with the reference at about 0.8, so it is partly the reference and the experts agreeing with each other. Not a protocol verdict (qwen3_14b and qwen3_4b still running; the full analysis incl. Part 2 runs at the 07:00 cutoff).

## 2026-10-25 04:30 (FINAL: full analysis, Part 1 + Part 2 + open-reference arms; `results/final_2026-10-25_0430/`)

All lanes finished (llama31_8b, q25_14b_awq, q3_30b_a3b_bf16, qwen3_8b, qwen3_14b, qwen3_4b all 9/9 prompts; llama33_70b_awq and qwen3_32b H2 only). GPU 5 on skampere1 and GPU 9 on mercury2 are free and the downloaded weights are deleted. `analyze59.py` ran once, 10,000 draws, no frontier or paid call. Settings per model (checkpoint@revision, quantization, context, sampling, vLLM) are in the first table of `RESULTS_open_weight_proxy_fit.md`. Caveat first: the human ratings are 75 Claude 3.7 Sonnet zero-shot items only; frontier-judge outputs are first rated on 2026-11-06, where the frozen fits get their real test (no refit).

**Part 1 (does a label-free index rank open-weight judge units by agreement with the expert ratings?): PASS.** 65 units from 9 models (7 new plus saved Qwen3.6-27B; criterion = Spearman with the 3-expert mean on the 45 val+test items).
- Frozen primary `C_ms_gold`: Spearman 0.522 [0.29, 0.70], Kendall 0.358, Pearson 0.460, n = 61 units, permutation p 0.0001; model-clustered over 5 models: 0.452 [0.07, 0.62], p 0.026. This clears the gate (rho >= 0.45, p < 0.05), but narrowly: the clustered interval reaches 0.07, and on the 54 new units alone it is 0.468.
- New agreement indices (need the frontier consensus, still label-free): `F1_probe` 0.677 [0.47, 0.82]; `F2_item` 0.937 [0.89, 0.96]; `F12` 0.925 [0.87, 0.95] (Kendall 0.78, Pearson 0.92). Old `PTI_v0` 0.193 [0.04, 0.37] (p 0.10) and `TI_var` -0.005 [-0.26, 0.24]: no signal.
- Caveat on the 0.93: much of it is between-model (small vs large judges); the experts agree with the frontier consensus at 0.81, so part of it is the reference and the experts agreeing with each other.

**Part 2 (fit open-weight units to the frontier consensus T, no human labels in the fit): FIT-PASS.** 504 rows; chosen by validation: L3 (NNLS; validation 0.853). Test = 30 items (10 tasks), fit on train+val, tested once; intervals are task-cluster bootstrap:
- L0 best single unit (qwen3_14b|H1) 0.603 [0.20, 0.89]; L1 top-5 mean 0.799 [0.48, 0.94]; L2 ridge 0.870 [0.64, 0.95]; **L3 NNLS (chosen) 0.821 [0.54, 0.91]** (Pearson 0.847, Kendall 0.671, ICC(C,1) 0.846); L4 human-fit diagnostic 0.753 [0.37, 0.91].
- References on the same test items: frontier consensus `R_front` 0.814 [0.38, 0.95]; validated judge `R_validated` 0.814 [0.26, 0.96]; local default (Qwen2.5-14B-AWQ single call) `R_local_default` 0.260 [-0.37, 0.77]; best single open unit chosen with test peeking (oracle) 0.867.
- So a stacked open-weight fit (0.82) matches the frontier consensus (0.81) with intervals that overlap fully (paired L3 - R_front [-0.19, 0.28]); it beats the best single open unit (L3 - L0 [-0.13, 0.59], not clearly) and the local default clearly in point terms. Fitting to humans (L4) did not beat fitting to the frontier consensus (L4 - L2 [-0.40, 0.05]). 30 test items are few: read this as consistent with, not proof of, parity.
- Descriptive 5-fold task-grouped CV over all 75 items: L0 0.538, L1 0.622, L2 0.739, L3 0.756 vs R_front 0.750 [0.54, 0.88].

**Open-weight smart reference instead of the frontier consensus (Brando's 19:58 request):**
- Reference Qwen3.6-27B (`O_qwen36`): agrees with the frontier consensus 0.941 (probe cells) / 0.858 (75 items) and with the experts 0.817; `F12@O_qwen36` 0.888 [0.81, 0.93] (clustered p 0.002); Part 2 FIT-PASS, chosen L3 test 0.765 [0.39, 0.94] vs frontier arm 0.821: SUBSTITUTE-OK.
- Reference Qwen3-32B thinking (`O_qwen32`): `F12` 0.928 [0.88, 0.95] (p 0.0005); Part 2 chosen L2 test 0.865 [0.63, 0.96] (paired L2 - R_ref [0.01, 0.28]): SUBSTITUTE-OK. Both together (`O_both`): `F12` 0.910; chosen L2 0.837 [0.60, 0.96].
- Llama 3.3 70B AWQ: constant scores (506 of 521 raw scores are 5), so `F2`/`F12` are undefined, Part 2 FIT-NO-GAIN: NOT SUBSTITUTE-OK; it is no use as a reference.

**Answer to the two questions:** (1) Yes: indices that ask "does this small judge agree with a bigger judge (frontier or open)" rank open-weight judge units by agreement with the human ratings far better (Spearman about 0.92-0.94) than the label-free index `C_ms_gold` (0.52, narrowly clearing the gate) or the old PTI/TI_var (about 0). (2) Yes, with a small test: ridge/NNLS stacks of open-weight units fitted only to the frontier consensus reach about 0.82-0.87 on the 30 held-out items, equal to the frontier consensus itself (0.81), with no paid call and no human label; an open-weight reference (Qwen3.6-27B or Qwen3-32B) substitutes for the frontier consensus. Open: the human set is Claude 3.7 Sonnet outputs only, the test is 30 items, and everything must be re-tested without refit on the Nov 6 frontier ratings.
