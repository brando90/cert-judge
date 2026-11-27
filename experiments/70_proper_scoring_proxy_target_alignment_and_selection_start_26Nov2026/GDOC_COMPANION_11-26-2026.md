# Experiment 70 — Google Doc Companion (`11-26-2026`)

Date: 11-26-2026

> **Sync note (Rule 16 disclosure):** At run time, the `google-drive` and `gmail` MCP connectors returned `Unauthorized: rejected by transport`, so live Google Doc API append is pending OAuth reconnect. This Markdown artifact is upload/paste-ready with zero rater names or private links.

**Bottom line:** Live VeriBench `native_main` remains at `250` non-`A1` anonymized ratings across `100` files (`33/33` public CSV sheets unchanged as of `11-26-2026 16:17 PST`; `74.0%` score-5 ceiling; `T05–T08` `ICC(A,1)=0.7589`, `QWK=0.7571`; `CONST_loto RPS=0.0698`). Using proper scoring (`RPS`, `CE`, `TVD`, `Brier`) and decision-theoretic meta-metrics (`Top-1 / Subpool-10 / LOFO Regret`, `UWA_RPS`, `Beat-CONST Meta-Brier`, `Meta-RMSE`) on `E39+E42` (`60` units), `E60` (`62` open-weight harvests), `E58` (`117` units), and `E63` (`6` arms) shows that:
1. `C_ms_gold` fails on control-inclusive pools (`Top-1` regret `0.0390` `ce_cal` / `0.1243` `raw` by tying lexical controls at `1.0000`) and drops the #1 and #2 held-out test judges (`qwen36|H2`, `qwen36|R4`).
2. Label-free proper-scoring behavioral proxies (`P_e42_fullcov_brier`, `P_e42_strict_brier`, `P_e42_probe_rps`) evaluate all `18/18` test LLMs and reject controls at Top-1 (`UWA_RPS = 0.8614` `ce_cal` / `0.9173` `raw` for `P_e42_probe_rps`; `Beat-CONST Meta-Brier = 0.0549` vs `0.256` base rate for `P_e42_strict_brier` on `rawRPS`; `Meta-RMSE = 0.0282` vs `0.056` for `P_e42_fullcov_brier`). On equalized `common_support_test_llm` (`n=16`), `P_e42_probe_rps` matches `C_ms_gold` Top-1 (`0.0071`) while improving `Sub-10` (`0.0074` vs `0.0111`) and `UWA_RPS` (`0.8531` vs `0.8264`).
3. On `E60 seed1` (`n=36`), `P_e39_fullcov_brier` outperforms `C_ms_gold` (`UWA = 0.7686` vs `0.6755` `ce_cal`; `0.8514` vs `0.6164` `raw`; Spearman `0.5271` `[0.258, 0.715]` `p=0.0016` vs `0.3073` `p=0.0688` on `ce_cal`, `0.6969` `p=0.0002` vs `0.3344` `p=0.0470` on `raw`).
4. On `native_main`, calibrated `H2_astra`, `H2_opus`, and `H3_astra_native_probs` beat `CONST_loto` (`0.0433–0.0440` vs `0.0698`, `p=0.0005`), whereas `P8_STRICT_B` fails `CONST` (`0.1263–0.2428` `raw RPS`).

## Caveats

- Zero API spend (`$0`); all proper-scoring targets/proxies computed offline on CPU from saved `E39`, `E42`, `E58`, `E60`, `E63`, `Exp 27`, and `Exp 67` harvests (`no internet` except read-only public Google Sheet CSV check).
- `ctl|editdist` scores `P_e42_fullcov_brier = 0.8195` (`> 0.78` protocol bound) because string edit distance flags non-identical degraded probes (only `formatting` invariance penalizes it via `P_e42_disc`).
- Strictly zero-leakage primary head-to-head fits/selects on `38` `train+val` LLMs only; `P_dsti_gated` (selected by `Arm B` on `train+val`, inherits `C_ms_gold` missingness) lost out-of-sample to `P_e42_strict_brier` (`top1 = 0.0379` vs `0.0146`, `Sub-10 = 0.0237` vs `0.0138`).

## Appendix: Harness, Models, Split, and Artifacts

- Code & tests: `experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/{scripts/proxy_metrics.py,scripts/run_exp70.py,tests/test_exp70.py}`.
- Mathematical derivation PDF: `derivation/proxy_target_proper_scoring_derivation.pdf`.
- Mega Tech Report: `~/cert-judge/latex/mega_tech_report.pdf`.
- 3-stage `agy` Mega QA (`PASS`, `missing_company_diversity: true`): `results/MEGA_QA_RECEIPT_11-26-2026.json`.
