# Experiment 70 Report — Proper-Scoring Proxy-vs-Target Alignment & Selection (`11-26-2026`)

Date: 11-26-2026

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/RESULTS_proper_scoring_proxy_target_11-26-2026.md>

## Bottom Line

Optimizing or validating label-free behavioral proxies by double rank correlation (`Spearman(P, Spearman(s_j, H))`) discards distributional calibration, harshness bias, and adversarial control sensitivity, and lets rank-only deletion proxies like `C_ms_gold` be hijacked (`Top-1 ce_cal_all5_rps regret = 0.0390`; `raw_all5_rps regret = 0.1243`) by deterministic string heuristics (`ctl|count_ratio`, `ctl|name_jaccard`, `ctl|editdist`) while dropping the #1 and #2 held-out test judges (`qwen36|H2`, `qwen36|R4`). Across four CPU-only studies (`$0` API spend, read-only public Sheet CSV verification): (1) live VeriBench `native_main` holds `250` non-`A1` ratings across `100` files / `25` tasks (`33/33` public Sheets unchanged vs `trustworthy-theorem-judges` `460466d`; `T30` `401 Unauthorized`; `T05–T08` `ICC(A,1)=0.7589`, `QWK=0.7571`; `74.0%` score-5 ceiling; `CONST_loto RPS=0.0698`); (2) label-free proper-scoring E42 proxies beat `TI_var_trainnorm` (`UWA = 0.3362`), `PTI_v0_frozen` (`0.3896`), and control-hijacked `C_ms_gold` (`+ctrl UWA = 0.6795` `ce_cal` / `0.5637` `raw`), reaching `UWA_RPS = 0.8614` (`ce_cal`) / `0.9173` (`raw`) for `P_e42_probe_rps` and `Beat-CONST Meta-Brier = 0.0549` (vs base `0.256`, `AUROC = 0.883`) for `P_e42_strict_brier` on `test_llm`; (3) `P_e39_fullcov_brier` replicates on `E60` open-weight harvests (`e60_seed1_36` `UWA = 0.8514`, `Spearman = 0.6969`, `p = 0.0002` vs `C_ms_gold` `UWA = 0.6164`, `Spearman = 0.3344`); and (4) calibrated `H2`/`H3` beat `CONST_loto` (`0.0433–0.0440` vs `0.0698`, `p = 0.0005`) while Exp 67 `P8_STRICT_B` fails `CONST` (`0.1263–0.2428`). At the same time, two honest negative findings stand out: `ctl|editdist` scores `P_e42_fullcov_brier = 0.8195` (`> 0.78` protocol bound) because change detectors reject edited defective files, and `P_dsti_gated` selected by `Arm B` on `train+val` underperforms `P_e42_strict_brier` (`top1 = 0.0379` vs `0.0146`, `Sub-10 = 0.0237` vs `0.0138`) on `test_llm`.

For mathematical proofs, complete tables (`test_llm`, `test_llm_plus_ctrl`, `common_support_test_llm`), and rendered plots, see [derivation/proxy_target_proper_scoring_derivation.pdf](derivation/proxy_target_proper_scoring_derivation.pdf), [results.md](results.md), [figures/fig1_proxy_vs_proper_target_e39_e42.png](figures/fig1_proxy_vs_proper_target_e39_e42.png), [figures/fig2_meta_metrics_comparison_and_regret.png](figures/fig2_meta_metrics_comparison_and_regret.png), and [figures/fig3_native_main_100files_bridge.png](figures/fig3_native_main_100files_bridge.png).

---

## Summary CSV Artifacts

- [results/study2_meta_comparison.csv](results/study2_meta_comparison.csv)
- [results/study2_e39_e42_units.csv](results/study2_e39_e42_units.csv)
- [results/study3_e60_meta.csv](results/study3_e60_meta.csv)
- [results/study4_native_main_bridge.csv](results/study4_native_main_bridge.csv)

## Key Scientific Takeaways

1. **Double correlation (`Spearman(P, Spearman)`) is affine- and bias-blind:** Rescaling judge logits by `0.1x` or miscalibrating class probabilities leaves inner/outer Spearman identical while destroying `RPS`, `CE`, `Brier`, and `ICC(A,1)`. Evaluating proxies by `UWA_RPS`, `Top-1 / Subpool-10 / LOFO Regret`, `Beat-CONST Meta-Brier/CE`, and `Meta-RMSE` resolves this.
2. **Label-free Brier/RPS behavioral scoring captures coverage, calibration, and adversarial robustness:** Unlike `C_ms_gold` (which ties controls at `1.0000` and drops `qwen36|H2`/`R4`), `P_e42_fullcov_brier`, `P_e42_strict_brier`, and `P_e42_probe_rps` score all `18/18` test LLMs and all `22/22` `+ctrl` units cleanly. On equalized `common_support_test_llm` (`n=16`), `P_e42_probe_rps` matches `C_ms_gold` Top-1 (`0.0071`) while beating it on `Subpool-10` (`0.0074` vs `0.0111`) and `UWA_RPS` (`0.8531` vs `0.8264`).
3. **Formatting invariance matters when screening change detectors:** `ctl|editdist` attains `P_e42_fullcov_brier = 0.8195` (`> 0.78`) solely because string edit distance flags any non-identical probe; incorporating formatting false-alarm penalties (`P_e42_disc`, `0.8654` `UWA_RPS` on `+ctrl` `ce_cal_all5_rps`, `0.9059` on `raw_all5_rps`) and using Top-1 selection (which prefers `0.9553–0.9844` LLMs) blocks this failure mode.
4. **Live VeriBench data needs more diverse items and free local inference:** `native_main` (`250` non-`A1` ratings, `T05–T08` `ICC(A,1)=0.7589`) has `74.0%` score-5 ratings, so fresh multi-quality rating tasks (`T30` & incomplete raters) plus local open-weight judge runs (`E58`/`E60` models on `N=100`) are the highest-leverage next steps.

**TLDR-end:** [cert-judge: exp70 proper-scoring proxy-target] Live Sheets unchanged (`250` ratings); E42 proper-scoring proxies (`P_e42_probe_rps` `UWA=0.8614`/`0.9173`, `P_e42_strict_brier` `Meta-Brier=0.0549`) and E39 Brier (`E60 seed1` `UWA=0.8514` vs `C_ms_gold` `0.6164`) fix `C_ms_gold`'s control hijack (`0.0390`/`0.1243` regret) and zero-coverage drops; `ctl|editdist` (`0.8195`) exposes change-detector loophole and `P_dsti_gated` loses out-of-sample to `P_e42_strict_brier`; `$0` spend.
