# Experiment 60 protocol: a more rigorous round on the proxy trust index with open-weight judges (follows experiment 59)

**TLDR:** Experiment 59 passed narrowly (label-free index 0.52 plain, 0.45 grouped by model; open-weight fit to the frontier consensus 0.82 on 30 test items). Both rested on few units, 5 model clusters and one 30-item test split. This round adds (1) new open-weight judge units that experiment 59 never saw, which are a prospective replication of the frozen gate; (2) seed replicates of existing units (test-retest); (3) a nested leave-one-task-out evaluation of the fits over all 75 rated items instead of one 30-item split, with repeated random task splits and a permuted-target negative control; (4) model-level robustness of the gate (leave-one-model-out, model bootstrap, within-model); (5) stricter fit ablations (small judges only, no thinking judges, no Qwen family). Free GPUs only, $0, no paid API, no frontier call (frontier targets are the cached experiment-39 scores). Frozen in the commit that adds this file: no experiment-60 judge output existed when it was committed.

**Status:** FROZEN at the commit that adds this file. Judge calls made before it: 0. Later changes are dated addenda at the end.

## 0. Caveat that bounds every claim (unchanged from experiment 59)

The only human ratings are the 75 items: 25 tasks x 3 samples of `claude-3-7-sonnet-20250219`, one zero-shot call. Nothing here is evidence about frontier agents' outputs until the 75-item frontier set (due 2026-11-06); frozen learners are re-tested there without refit. Experiment 59's analysis already used the test split of these items once (30 items); experiment 60's cross-validations reuse all 75 items and so are descriptive about the same human set, not new human evidence. The prospective part is only the new judge units (section 2), scored with the gate and index definitions frozen in experiments 39 and 59.

## 1. Held fixed

Experiment 39's cells, nine prompts, task splits, criterion (`target_expert`) and `C_ms_gold`; experiment 59's `F1_probe`, `F2_item`, `F12`, frontier consensus `T` (mean H2 score of sol6h, sonnet5m, luna6h, gem31h, opus55x), learners L0 best single unit, L1 top-5 mean, L2 ridge, L3 NNLS (definitions and code `59_*/scripts/analyze59.py`, imported unchanged), references R_front, R_validated, R_local_default. Generation rules, parsing, per-cell seeding and over-context rule: experiment 58 PROTOCOL section 4 via `judge_vllm.py`, unchanged. Each model's own `generation_config.json` sampling.

## 2. New judge units (stage 1, local vLLM, free A100 80 GB)

- **New models (prospective replication set P):** `gemma3_27b` (Gemma 3 27B it, bf16, unsloth mirror, no thinking; context 32,768), `gpt_oss_20b` (OpenAI gpt-oss-20b, reasoning, harmony format, context 65,536), and `qwen3_32b` on the eight prompts not run in experiment 59 (D0, R4, H0, H1, P1, P4, P8, LEX; thinking, fp8 weight-only load, context 32,768), each x 9 prompts (`qwen3_32b|H2` is experiment 59's). Repos and pinned revisions: experiment 58's `e58.MODELS` through `scripts/register60.py`. If a model fails to load or crashes the engine, it is recorded as failed and dropped; nothing is substituted after seeing results.
- **Seed replicates (test-retest):** `q25_14b_awq`, `q3_30b_a3b_bf16`, `qwen3_14b`, `qwen3_8b` x 9 prompts, same checkpoints and settings as experiment 59, only the sampling seed changes (`E60_SEED = 1058`; per-cell seed = int(sha256('1058|<config>|<cell>')[:8], 16)). Run in this priority order; a replicate not finished by 2026-10-25 18:00 is reported as incomplete and excluded.
- Lane order (one A100 each, empty GPUs only, released after each model): lane A `gemma3_27b`, `qwen3_32b` (8 prompts); lane B `q25_14b_awq@s1`, `q3_30b_a3b_bf16@s1`, `gpt_oss_20b`, `qwen3_14b@s1`, `qwen3_8b@s1`.

## 3. Part A: prospective replication of the frozen gate (new units only)

Over the new-model units P (excluding seed replicates and experiment 59's `qwen3_32b|H2`): Spearman between `C_ms_gold` and the criterion (45 criterion items per unit, as experiment 59), one-sided permutation p, 10,000 draws, seed 60; PASS iff rho >= 0.45 and p < 0.05, exactly the experiment-39 gate. Reported also: `F1_probe`, `F2_item`, `F12` (labelled exploratory), model-clustered permutation and model bootstrap (3 clusters, so clustered p is reported but cannot reach below ~0.17 and is not a gate), Kendall, Pearson, ICC. Secondary: the same over P plus experiment 59's units pooled (all open-weight units, now >= 8 model clusters) with the clustered gate p < 0.10.

## 4. Part B: model-level robustness of the experiment-59 gate

Leave-one-model-out Spearman and range, jackknife SE over models, model-level bootstrap (resample models, then their units; 10,000 draws), the mean of within-model Spearmans (Fisher z, each model's prompt units only), and the same with `qwen36` excluded. No new gate; reported as an interval and a verdict sentence: "robust" iff the leave-one-model-out minimum is >= 0.35 and the model bootstrap lower bound is > 0.

## 5. Part C: nested leave-one-task-out evaluation of the fits (all 75 items)

Units: all open-weight units available (experiment 59's 65, plus new units that are complete). Learners L0-L3 as in experiment 59, refit on the cells of 24 tasks and predicting the held-out task's items, for each of the 25 tasks (`alpha` of L2 chosen by inner 5-fold task-grouped CV on the training tasks; NNLS/L1 no hyper-parameter; L0's unit chosen by `F1_probe` on training tasks). Pooled out-of-fold item predictions: Spearman, Pearson, Kendall, ICC(C,1), ICC(A,1) vs the criterion with task-clustered bootstrap CIs (10,000 draws, seed 60), paired differences L-minus-reference with CIs, references R_front, R_validated, R_local_default (which have no fit). Also: (i) 200 random 17/8 task splits (seed 60): distribution of held-out Spearman per learner and the share of splits with rho >= 0.45 and rho >= R_front; (ii) negative control: the same pipeline with `T` replaced by `T` shuffled across tasks (cells of a task keep their joint T but tasks swap targets, seed 60), expected near 0; (iii) ablations of the unit set: units of models <= 14B only; non-thinking units only; non-Qwen families only (Llama, Gemma, gpt-oss, plus none else); seed-averaged units where replicates exist.
Decision rule (frozen): **FIT-ROBUST** iff the best of L2/L3 (by inner-CV, not by the held-out items) has pooled Spearman >= 0.45 with CI lower bound > 0, and beats L0 and the negative control by a paired CI excluding 0; **PARITY** with the frontier consensus iff the paired CI of (learner - R_front) contains 0; **WEAKENED** if an ablation drops the point estimate below 0.45; all stated per ablation.

## 6. Part D: test-retest of the judge units

For each replicated unit: cell-level Spearman and ICC(A,1) between the two seeds, item-median Spearman, and the difference in `C_ms_gold` and `F12` between seeds. A unit-index range across seeds is reported as the reliability of the index; the experiment-59 gate Spearman is recomputed with seed-1 units replacing seed-0 units, and with the seed average.

## 7. Compute and reporting

Free only: skampere1 empty A100 80 GB GPUs (3 and 5 at launch), `vllm_env` (vLLM 0.21). Weights on /dfs/scratch0 deleted after each model. Every table reports harness (single-call LLM, no tools; Pi is not used here), model and checkpoint, settings, N, judge (the unit), CI method and seed. Zero paid or hosted calls. Deliverables: `results/RESULTS_rigor_round.md`, `results/ANALYSIS.json`, the experiment-log Doc entry, and a text to Brando.

## Addenda (dated, the sections above unchanged)

### Addendum 1 (2026-10-25, before any experiment-60 judge output was read)
- Negative control redefined. The shuffle-within-cell-kind control of section 5 (ii) was exercised on a partial experiment-59 harvest (28 units, no new data, no experiment-60 judge output) and is not a null: it keeps the probe-kind structure that any competent judge reproduces, so even L0 scored 0.66. Replacement: (a) `T` shuffled across all rows (20 shuffles, the null) and (b) `T` replaced by its per-kind mean (a target with no per-cell judgment; an informative control: if the fit still reaches ~0.5, frontier per-cell judgments are not what the fit transfers). The FIT-ROBUST condition "above the negative-control max" refers to (a).
- `llama33_70b_awq` (degenerate, H2 only) is excluded from all units, as experiment 59 already argued; `qwen3_32b|H2` (experiment 59) joins experiment 60's `qwen3_32b` units in parts B and C but is not in part A's replication set.
- Ablation unit sets use the model facts in `scripts/analyze60.py::INFO` (<= 15B: Llama 3.1 8B, Qwen2.5-14B, Qwen3-14B/8B/4B; non-thinking: Llama, Qwen2.5-14B, Qwen3-30B-A3B-Instruct, Gemma 3 27B; non-Qwen: Llama, Gemma, gpt-oss).
- The partial-harvest dry run printed Part B and Part C numbers for 28 units; they are discarded and not used for any decision. Final run: all experiment-59 final harvests plus experiment-60 harvests available at the cutoff.
