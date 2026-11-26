# Experiment 69A results (11-26-2026)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/69_proxy_target_proper_score/RESULTS.md>

**TLDR:** On the primary pools, no label-free proxy passes the frozen rule. `TI_var` on the 24 paper series is worse than the constant forecast. On the held-out experiment 39 judges, `C_ms_gold` and the training semantic margin beat the constant forecast on Ranked Probability Score (RPS), and their regret against best-on-val is unresolved. Spend $0. Full tables: `results/tables.md`. Machine summary: `results/summary.json`.

Pre-registration: `PREREG.md`, committed before this run. Intervals are 95% task-bootstrap percentile intervals, 2,000 draws, seed 69. p-val=n/a (the decision is the interval, not a separate named test). Lower RPS, cross-entropy (CE), and total variation distance (TVD) are better. Positive regret means the proxy-selected judge is worse than best-on-val.

## N250 snapshot check

The frozen count check passes: 250 main scores, T05 100, T08 100, T12 30, T06 16, V04 3, V02 1. Histogram: 0:0, 1:7, 2:1, 3:15, 4:42, 5:185. Share at 5 is 185/250 = 0.74. Mean score is 4.588. Attestations: 118 yes, 100 partial, 32 blank.

T05 versus T08 on 100 files: Spearman 0.635, Pearson 0.826, quadratic weighted kappa 0.757, exact agreement 66/100, within one point 99/100.

Leave-one-task-out constant forecast on the 100 files and 25 tasks: RPS 0.0698 [0.0425, 0.0989], CE 0.8716 [0.6186, 1.1377], TVD 0.3636 [0.3078, 0.4226]. The mass at 5 keeps this constant loss small. Experiment 68 reported RPS 0.0699 [0.0452, 0.0972] on the 11-24 snapshot. No saved judge score exists on these 100 files, so no proxy is scored against them.

## Selection on the 59-artifact panel

59 artifacts, 20 tasks, at least 4 corrected-prompt ratings, and a saved paper-panel score. RPS below is the mean over tasks of the mean individual-rating RPS.

| Pool | Proxy | n | Selected | RPS | vs CONST | Regret vs best-on-val | Pass |
|---|---|---:|---|---:|---|---|---|
| paper_all | `TI_var` | 24 | Qwen3-Coder `BAD_STRINGY` | 0.2710 | +0.0964 [+0.0412, +0.1488] | +0.0559 [+0.0144, +0.0951] | no |
| paper Codex | `TI_var` | 8 | `gpt-5.3-codex\|P1_BASELINE` | 0.2497 | +0.0751 [+0.0260, +0.1221] | +0.0504 [+0.0168, +0.0822] | no |
| paper Claude Opus | `TI_var` | 8 | `claude-opus-4-7\|P1_BASELINE` | 0.2056 | +0.0309 [−0.0015, +0.0605] | −0.0173 [−0.0398, +0.0059] | no |
| paper Qwen3-Coder | `TI_var` | 8 | `BAD_STRINGY` | 0.2710 | +0.0964 [+0.0412, +0.1488] | +0.0577 [+0.0175, +0.0965] | no |
| e39 test LLM | `C_ms_gold` | 11 | `opus55x\|H2` | 0.1450 | −0.0296 [−0.0581, −0.0055] | −0.0020 [−0.0113, +0.0071] | no |
| e39 test LLM | `semantic_margin_train` | 13 | `qwen36\|H0` | 0.1404 | −0.0342 [−0.0579, −0.0126] | −0.0072 [−0.0173, +0.0036] | no |
| e39 test LLM | `TI_var_trainnorm` | 13 | `opus55x\|H0` | 0.1572 | −0.0174 [−0.0481, +0.0131] | +0.0096 [−0.0066, +0.0278] | no |
| e39 test LLM | `C_bm_gold` | 13 | `opus55x\|H0` | 0.1572 | −0.0174 [−0.0481, +0.0131] | +0.0096 [−0.0066, +0.0278] | no |
| e39 test LLM | `PTI_v0_frozen` | 6 | — | — | — | — | not computable |
| e39 all LLM | `semantic_margin_train` | 46 | `qwen36\|H0` | 0.1404 | −0.0342 [−0.0579, −0.0126] | −0.0119 [−0.0226, −0.0017] | yes |

Constant-forecast RPS on this panel is 0.1746. Best-on-val RPS is between 0.1470 and 0.2228 depending on the pool.

`TI_var` on the 24 paper series selects a harsh `BAD_STRINGY` configuration. Its RPS, CE (+0.4966 [+0.2928, +0.6741]), and the RPS regret are worse than the comparators, with those RPS and CE intervals excluding 0. Spearman of `TI_var` with minus RPS on the 24 series is −0.589.

`C_ms_gold` on the 11 held-out experiment 39 judges with full coverage selects `opus55x|H2`. It beats the constant forecast on RPS. The regret interval covers 0, so the frozen conjunction fails. The same pool's CE difference versus the constant forecast is +0.0597 [−0.1201, +0.2399], and the TVD regret is +0.0519 [+0.0003, +0.1042]. Diagnostic Spearman of `C_ms_gold` with minus RPS is +0.645.

Training semantic margin on those held-out judges selects `qwen36|H0` and also beats the constant forecast on RPS. Its regret interval covers 0. CE versus CONST is −0.1190 [−0.2547, +0.0212]. Diagnostic Spearman with minus RPS is +0.719.

The only pass is the secondary pool of all 46 experiment 39 language-model judges, which includes the train and validation judges used when indices were chosen. There, training semantic margin selects `qwen36|H0`, beats CONST, and the regret interval lies below 0 (the selected judge is better than best-on-val on this panel). That pool is the optimistic one named in the pre-registration.

`PTI_v0_frozen` is not computable on the held-out test judges: 6 have a value and full coverage, below the frozen minimum of 8. Across the 36 covered judges in the all-LLM pool the stored value is 0, so the index does not rank them (Spearman undefined). The two language-model units with `PTI_v0_frozen` above 0 (`sonnet5m|D0`, `opus55x|D0`) do not score every one of the 59 artifacts.

## Implementation notes

The run matches the pre-registration after two loader fixes found before the reported numbers were kept: blank label cells arrive as missing values and are skipped, and each paper series keeps its family prefix so the 24 series stay distinct. The 59 artifacts are the files with at least 4 corrected ratings and a saved paper-panel score.
