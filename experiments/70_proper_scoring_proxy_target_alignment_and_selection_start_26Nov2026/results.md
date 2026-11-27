# Experiment 70 Ledger — Proper-Scoring Proxy-vs-Target Alignment & Selection (`11-26-2026`)

**Status:** DONE (`11-26-2026 17:00 PST`; `$0` API / Valkyrie spend, CPU-only + read-only public CSV Sheet verification; 3-stage Mega QA `PASS` on `e643cef` + final comment nit applied)
**Renumbering & coordination note (`AGENTS.md`):** Originally pre-registered as Experiment 69 (`seed=69`) and renumbered to `70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026` after Cursor's `69_proxy_target_proper_score` landed on `main` (`3755590`); both independently confirm identical `native_main` N250 stats (`250` ratings, `T05–T08` QWK `0.757`, `CONST_loto RPS = 0.0698`).
**Pre-Exp-70 base on `main` (`QA_BASE`):** `3755590e19f38012da111d0d343bd465c5b0566b` (`seed=69` kept from initial freeze prior to execution)

**Doc links:**
- [PROTOCOL.md](PROTOCOL.md)
- [RESULTS_proper_scoring_proxy_target_11-26-2026.md](RESULTS_proper_scoring_proxy_target_11-26-2026.md)
- [GDOC_COMPANION_11-26-2026.md](GDOC_COMPANION_11-26-2026.md)
- [Derivation PDF](derivation/proxy_target_proper_scoring_derivation.pdf) ([source .tex](derivation/proxy_target_proper_scoring_derivation.tex))
- [Mega Tech Report PDF](../../latex/mega_tech_report.pdf) ([LaTeX fragment](../../latex/results/70_proper_scoring_proxy_target_alignment.tex))

---

## Phase Progress Table

| Phase | Outcome | Verified Evidence / Outputs |
|---|---|---|
| Phase 0 — Sync, Rules & Live Sheets | DONE | `33/33` public VeriBench Google Sheets unchanged vs `trustworthy-theorem-judges` `460466d`; `250` non-`A1` ratings (`T30` `401 Unauthorized` checked manually via local ID, omitted from repo); `agent-sync` claimed |
| Phase 1 — Freeze Protocol | DONE | Pre-registered `PROTOCOL.md` before execution; renumbered `69` -> `70` on `3755590`; `experiment_layout.py --check` (`17 active experiments`) |
| Phase 2 — Implement & Unit-Test | DONE | Vectorized `proxy_metrics.py`, leak-free `run_exp70.py`, `6/6` `unittest` cases `OK` (covering O(n^2) UWA parity & repo-wide privacy scan) |
| Phase 3 — Run All 4 Studies & Derivation | DONE | All 4 parity checks passed (`0.0`, `2.22e-16`, `0.0`); generated `4` JSONs, `4` CSVs, `3` PNGs, and `derivation/proxy_target_proper_scoring_derivation.pdf` (4 pages) |
| Phase 4 — Reports, Mega Tech Report & Mega QA | DONE | Built `mega_tech_report.pdf` (`130/130` decimal tokens matched); 3-stage `agy` Mega QA completed (`Stage 1 NEEDS_FIX` -> `Stage 2 NEEDS_FIX` -> `Stage 3 PASS`, receipt saved, `missing_company_diversity: true`) |

---

## Pre-Registered Predictions vs Observed Results (`P1`–`P4`)

| Prediction | Pre-registered criterion | Observed outcome | Verdict |
|---|---|---|---|
| **P1** (Control hijack vs proper E42 protection on `+ctrl`) | `C_ms_gold` picks lexical control with Top-1 `ce_cal_all5_rps` regret `> 0.030`; `P_e42_fullcov_brier <= 0.78` and `P_dsti_proper <= 0.80` on all 4 controls with Top-1 regret `< 0.015` | On `test_llm_plus_ctrl`, `C_ms_gold` ties 3 controls (`1.0000`) -> Top-1 `ce_cal` regret `0.0390` (`raw` `0.1243`), `UWA_RPS` drops `0.8264 -> 0.6795` (`raw` `0.8307 -> 0.5637`). Proper E42 proxies reject ALL 4 controls at Top-1 (`P_e42_strict_brier` regret `0.0146 < 0.015`, `UWA = 0.8501` `ce_cal` / `0.9049` `raw`; `P_e42_fullcov_brier` regret `0.0202`, `UWA = 0.8591` `ce_cal` / `0.8904` `raw`; `P_e42_probe_rps` regret `0.0084`, `UWA = 0.8847` `ce_cal` / `0.9282` `raw`). **However**, `ctl\|editdist` scores `P_e42_fullcov_brier = 0.8195 > 0.78` and `P_dsti_proper = 0.8902 > 0.80` because change detection flags every degraded edit and formatting layout change alike (only `ctl\|count_ratio`/`name_jaccard`/`random` sit `<= 0.6094` / `0.7852`). | **PARTIALLY CONFIRMED** (Top-1 hijack fixed & `strict_brier`/`probe_rps` `< 0.015`; literal `editdist` upper bound refuted) |
| **P2** (`test_llm` `n=18`: Proper-score advantage over `TI_var`/`PTI_v0` & `C_ms_gold`) | Beat `TI_var`/`PTI_v0`; match or beat `C_ms_gold` on `raw_all5_rps` and proper meta-metrics | Overwhelmingly beat `TI_var_trainnorm` (`UWA = 0.3362`, Top-1 `0.0392`, `Sp = -0.2554`) and `PTI_v0_frozen` (`UWA = 0.3896`, `n=9`). vs `C_ms_gold` (`n=16`, blind to #1/#2 test judges `qwen36\|H2` & `qwen36\|R4`): `P_e42_strict_brier` wins `Beat-CONST Meta-Brier` on `raw_all5_rps` (`0.0549` vs `0.0673`), `P_e42_fullcov_brier` wins `Meta-RMSE` (`0.0282` vs `0.0392` `raw`; `0.0134` vs `0.0142` `ce_cal`), and `P_e42_probe_rps` reaches highest `UWA_RPS` (`0.8614` `ce_cal` / `0.9173` `raw` vs `C_ms_gold` `0.8264` / `0.8307`) & lowest `Subpool-10` regret (`0.0061` / `0.0084` vs `0.0111` / `0.0153`). On `common_support_test_llm` (`n=16`, identical oracle), `P_e42_probe_rps` ties `C_ms_gold` Top-1 (`0.0071`) while beating it on `Subpool-10` (`0.0074` vs `0.0111`) and `UWA` (`0.8531` vs `0.8264`). Yet `C_ms_gold` retains lower Top-1 regret (`0.0071` vs `0.0202`) than unweighted `P_e42_fullcov_brier` & `P_dsti_proper` on reduced `n=16`. | **PARTIALLY CONFIRMED** (`P_e42_probe_rps`/`strict_brier`/`fullcov_brier` beat `C_ms_gold` on UWA, coverage, Meta-Brier, Meta-RMSE; unweighted `fullcov_brier` does not beat `C_ms_gold` on Top-1 regret) |
| **P3** (`E60` open-weight replication: `26` seed-0 & `36` seed-1 units) | `P_e39_fullcov_brier` / `probe_rps` beat `TI_var` and `PTI_v0` on `UWA` & regret with seed-0/1 stability | Confirmed across both seeds. On `e60_seed0_26` (`ce_cal_all5_rps`), `P_e39_fullcov_brier` achieves `UWA = 0.8651`, `Sub-10 = 0.0100`, `Sp = 0.5810` (`[0.229, 0.812]`, `p = 0.0032`) vs `TI_var` (`UWA = 0.3642`). On `e60_seed1_36` (`n=36`), `P_e39_fullcov_brier` **beats `C_ms_gold` too**: `ce_cal` `UWA = 0.7686`, `Sub-10 = 0.0107`, `Sp = 0.5271` (`[0.258, 0.715]`, `p = 0.0016`) vs `C_ms_gold` (`UWA = 0.6755`, `Sp = 0.3073`, `p = 0.0688` NS); `raw` `UWA = 0.8514`, `Sp = 0.6969` (`[0.450, 0.857]`, `p = 0.0002`) vs `C_ms_gold` (`0.6164`). | **CONFIRMED** |
| **P4** (`native_main` `N=100`, `250` ratings bridge) | Calibrated `H2`/`H3` beat `CONST_loto` (`0.0698`), `P8_STRICT_B` fails `CONST`, E42/DSTI separate `H2` from `P8_STRICT_B` | `H2_astra` (`LOTO RPS = 0.0433`, `dRPS = -0.0266`, `p = 0.0005`), `H2_opus` (`0.0440`, `p = 0.0005`), and `H3_astra_native_probs` (`raw = 0.0414`, `LOTO = 0.0433`, `p = 0.0005`) all beat `CONST_loto` (`0.0698`) and empirical LORO (`0.0580`). Exp 67 `P8_STRICT_B` (`raw RPS` `0.1263`–`0.2428`) fails `CONST` and maps to lower E42 proxies (`0.7581`–`0.8058`) than `H2` (`0.8440`–`0.9553`). Caveat: `74.0%` score-5 ceiling (`185/250`) lets `length_ratio_capped` reach `LOTO = 0.0652` (`dRPS = -0.0046`, `p = 0.0090`) even though `raw RPS = 0.1643`. | **CONFIRMED** (with score-5 ceiling caveat; `P8_STRICT_B` uses same-family `opus55x\|P4` ref for Opus) |

---

## Harness, Model, Internet, and DT Labels

- **Studies 1–4 CPU offline analysis (`run_exp70.py`):** Local Python 3.11 (`numpy`, `scipy`), zero LLM API calls (`no internet` for Studies 2–3 and `E63`/historical checks; read-only HTTPS GET to public `docs.google.com/spreadsheets/.../export?format=csv` for Study 1 / Study 4 live rating check; `no DT applicable`).
- **Cached judges analyzed:** `E39`/`E42` (`60` units = `56` LLMs across OpenAI/GPT-6 Sol, Claude Opus 5.5/Sonnet 5, Gemini 3.1 Pro, Qwen3.6, Grok 4.2 + Terminus2 agent harness, plus `4` deterministic controls, `no internet`, `no DT`); `E60` (`26` seed-0 + `36` seed-1 local vLLM harvests); `E58` (`117` open-weight local vLLM units); `E63` (`Qwen3-8B` 6 fine-tuning/RL arms); `Exp 27` `H2_astra`/`H2_opus`/`H3_astra` and `Exp 67` `P8_STRICT_B` (`gpt-5.3-codex`, `claude-opus-4-7`, `Qwen/Qwen3-Coder-30B-A3B-Instruct`) on `native_main` (`N=100`).

---

## Study 1: Live VeriBench Cohorts (`native_main` vs `R_v1`)

| Cohort (Anonymized IDs only) | Items / Tasks | Ratings | Share `score = 5` | Empirical LORO `RPS` [95% CI] | Empirical LORO `TVD` | `LORO` Spearman | `CONST` `RPS` / `CE` / `TVD` / `Brier` | Pairwise Inter-Rater Agreement |
|---|---|---|---|---|---|---|---|---|
| `native_main` (`11-26-2026 16:17 PST`, `33/33` public Sheets unchanged vs `460466d`, `T30` `401` pre-checked without storing ID) | `100` / `25` | `250` non-`A1` (`T05=100`, `T08=100`, `T12=30`, `T06=16`, `V04=3`, `V02=1`) | `74.0%` (`185/250`) | `0.0580` `[0.0350, 0.0810]` | `0.3100` | `0.5098` `[0.461, 0.552]` | `LOTO`: `0.0698` / `0.8716` / `0.3636` / `0.4424` | `T05–T08` (`n=100`): `ICC(A,1)=0.7589`, `QWK=0.7571`, `MAE=0.3500`, `Sp=0.6351` `[0.427, 0.785]`, `r=0.8263`; `T05–T12` (`30`): `ICC=0.8505`; `T08–T12` (`30`): `ICC=0.8849` |
| `R_v1` (`E39`/`E42`/`E63` panel) | `75` / `25` | `345` (`all5`) | `18.3%` (`63/345`) | `0.1512` `[0.1274, 0.1761]` | `0.7013` | `0.5441` `[0.399, 0.662]` | Held-out (`45`): `0.1739` / `1.7537` / `0.5025` / `0.8248` | Diverse non-ceiling coverage |

---

## Study 2: Proper-Scoring Proxy-vs-Target Similarity (`E39 + E42`, `R_v1` `n=45` Held-Out Items)

### Table 2A — Controls vs Top Test Judges (`ce_cal_all5_rps`, `CONST = 0.1739`)

| Unit (`split`) | `C_ms_gold` | `P_e42_fullcov_brier` | `P_e42_strict_brier` | `P_dsti_proper` | `TI_var` | `ce_cal_RPS` | `raw_RPS` | `ce_cal_CE` | `raw_TVD` | `raw_ICC(A,1)` | `raw_Sp` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ctl\|count_ratio` (`train`) | `1.0000` | `0.6094` | `0.6094` | `0.7852` | `0.0100` | `0.1605` | `0.1987` | `1.6999` | `0.6056` | `0.3639` | `0.4698` |
| `ctl\|editdist` (`train`) | `1.0000` | `0.8195` | `0.8363` | `0.8902` | `1.0000` | `0.1689` | `0.2531` | `1.7228` | `0.6696` | `-0.1042` | `-0.4186` |
| `ctl\|name_jaccard` (`train`) | `1.0000` | `0.6094` | `0.6094` | `0.7852` | `0.0100` | `0.1740` | `0.3107` | `1.7547` | `0.7204` | `0.0000` | `nan` |
| `ctl\|random` (`train`) | `0.1250` | `0.6022` | `0.6155` | `0.5993` | `0.0100` | `0.1807` | `0.2494` | `1.7908` | `0.6615` | `-0.2592` | `-0.2741` |
| `qwen36\|H2` (`test`, #1 `ce_cal`) | `None` | `0.9666` | `0.9786` | `0.9622` | `0.0074` | `0.1275` | `0.1333` | `1.4944` | `0.4163` | `0.8216` | `0.8046` |
| `qwen36\|R4` (`test`, #2 `ce_cal`) | `None` | `0.9591` | `0.9760` | `0.9587` | `0.0074` | `0.1288` | `0.1360` | `1.5062` | `0.4744` | `0.8087` | `0.8285` |
| `t2_sonnet5\|H2` (`test`, #3) | `0.9920` | `0.9844` | `0.9844` | `0.9727` | `0.0075` | `0.1288` | `0.1318` | `1.5031` | `0.4352` | `0.7927` | `0.8499` |
| `opus55x\|H2` (`test`, #4) | `0.9942` | `0.9553` | `0.9844` | `0.9581` | `0.0075` | `0.1297` | `0.1361` | `1.5022` | `0.4819` | `0.7800` | `0.8483` |
| `qwen36\|H0` (`test`, #1 `raw_RPS`) | `0.9862` | `0.9733` | `0.9795` | `0.9670` | `0.0999` | `0.1300` | `0.1298` | `1.5142` | `0.4156` | `0.8153` | `0.8086` |

### Table 2B — Proxy Meta-Evaluation on `test_llm` (`n<=18`), `test_llm_plus_ctrl` (`n<=22`), and `common_support_test_llm` (`n=16`)

(`Meta-Brier` & `Meta-RMSE` trained strictly on `38` `train+val` LLMs only — zero test/control leakage. Note `Top-1` and `Subpool` evaluate within each proxy's valid support; `common_support_test_llm` enforces identical `n=16` non-`PTI_v0` common support with oracle `0.1288`, whereas `PTI_v0_frozen` alone has `n=9` in JSON/CSV.)

| Subset & Target | Proxy | `n` | Top-1 Regret | `Subpool` Regret (`m`) | `LOFO` Regret | `UWA_RPS` `[95% CI]` | `Beat-CONST` `Meta-Brier` (`base`) | `Meta-RMSE` (`const`) | Spearman `[95% CI]` | `perm p` | Within-fam `p` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `test_llm` / `ce_cal_all5_rps` | `TI_var_trainnorm` | `18` | `0.0392` | `0.0321` (`m=10`) | `0.0299` | `0.3362` `[0.131, 0.568]` | `0.1154` (`0.116`) | `0.0206` (`0.021`) | `-0.2554` `[-0.654, 0.208]` | `0.3107` | `0.2893` |
| `test_llm` / `ce_cal_all5_rps` | `PTI_v0_frozen` | `9` | `0.0379` | `0.0379` (`m=9`) | `0.0288` | `0.3896` `[0.118, 0.500]` | `0.1110` (`0.118`) | `0.0239` (`0.021`) | `-0.2739` `[-0.743, 0.106]` | `0.6613` | `0.8066` |
| `test_llm` / `ce_cal_all5_rps` | `C_ms_gold` | `16` | `0.0071` | `0.0111` (`m=10`) | `0.0101` | `0.8264` `[0.608, 0.949]` | `0.0865` (`0.123`) | `0.0142` (`0.021`) | `0.5887` `[0.096, 0.826]` | `0.0200` | `0.0944` |
| `test_llm` / `ce_cal_all5_rps` | `P_e42_fullcov_brier` | `18` | `0.0202` | `0.0162` (`m=10`) | `0.0199` | `0.8171` `[0.580, 0.955]` | `0.1106` (`0.116`) | `0.0134` (`0.021`) | `0.6020` `[0.162, 0.811]` | `0.0110` | `0.0160` |
| `test_llm` / `ce_cal_all5_rps` | `P_e42_strict_brier` | `18` | `0.0146` | `0.0138` (`m=10`) | `0.0135` | `0.8173` `[0.574, 0.956]` | `0.1133` (`0.116`) | `0.0139` (`0.021`) | `0.5600` `[0.066, 0.809]` | `0.0160` | `0.0056` |
| `test_llm` / `ce_cal_all5_rps` | `P_e42_probe_rps` | `18` | `0.0084` | `0.0061` (`m=10`) | `0.0063` | `0.8614` `[0.650, 0.974]` | `0.0994` (`0.116`) | `0.0162` (`0.021`) | `0.6388` `[0.197, 0.862]` | `0.0072` | `0.0128` |
| `test_llm` / `ce_cal_all5_rps` | `P_dsti_proper` | `18` | `0.0202` | `0.0169` (`m=10`) | `0.0199` | `0.8039` `[0.562, 0.953]` | `0.1215` (`0.116`) | `0.0159` (`0.021`) | `0.5607` `[0.080, 0.795]` | `0.0182` | `0.0248` |
| `test_llm` / `ce_cal_all5_rps` | `P_e39_ms_margin` | `18` | `0.0000` | `0.0073` (`m=10`) | `0.0005` | `0.7888` `[0.576, 0.954]` | `0.1161` (`0.116`) | `0.0180` (`0.021`) | `0.5046` `[0.021, 0.803]` | `0.0330` | `0.0730` |
| `test_llm` / `raw_all5_rps` | `TI_var_trainnorm` | `18` | `0.0495` | `0.0470` (`m=10`) | `0.0376` | `0.3594` `[0.134, 0.621]` | `0.2400` (`0.256`) | `0.0555` (`0.056`) | `-0.1892` `[-0.608, 0.292]` | `0.4503` | `0.4177` |
| `test_llm` / `raw_all5_rps` | `C_ms_gold` | `16` | `0.0110` | `0.0153` (`m=10`) | `0.0144` | `0.8307` `[0.686, 0.926]` | `0.0673` (`0.254`) | `0.0392` (`0.054`) | `0.5607` `[0.035, 0.751]` | `0.0266` | `0.0538` |
| `test_llm` / `raw_all5_rps` | `P_e42_fullcov_brier` | `18` | `0.0257` | `0.0201` (`m=10`) | `0.0252` | `0.8681` `[0.691, 0.959]` | `0.0700` (`0.256`) | `0.0282` (`0.056`) | `0.6866` `[0.256, 0.869]` | `0.0018` | `0.0024` |
| `test_llm` / `raw_all5_rps` | `P_e42_strict_brier` | `18` | `0.0183` | `0.0170` (`m=10`) | `0.0169` | `0.8810` `[0.704, 0.961]` | `0.0549` (`0.256`) | `0.0311` (`0.056`) | `0.5725` `[0.074, 0.809]` | `0.0166` | `0.0022` |
| `test_llm` / `raw_all5_rps` | `P_e42_probe_rps` | `18` | `0.0110` | `0.0084` (`m=10`) | `0.0093` | `0.9173` `[0.742, 0.981]` | `0.1286` (`0.256`) | `0.0329` (`0.056`) | `0.6656` `[0.177, 0.904]` | `0.0038` | `0.0068` |
| `test_llm` / `raw_all5_rps` | `P_dsti_proper` | `18` | `0.0257` | `0.0209` (`m=10`) | `0.0252` | `0.8737` `[0.685, 0.969]` | `0.0816` (`0.256`) | `0.0337` (`0.056`) | `0.6598` `[0.207, 0.870]` | `0.0042` | `0.0042` |
| `test_llm_plus_ctrl` / `ce_cal_all5_rps` | `C_ms_gold` (`ctrl`) | `20` | `0.0390` | `0.0353` (`m=10`) | `0.0324` | `0.6795` `[0.427, 0.870]` | `0.1129` (`0.162`) | `0.0204` (`0.020`) | `0.3789` `[-0.136, 0.704]` | `0.0950` | `0.0218` |
| `test_llm_plus_ctrl` / `ce_cal_all5_rps` | `P_e42_strict_brier` | `22` | `0.0146` | `0.0136` (`m=10`) | `0.0137` | `0.8501` `[0.711, 0.946]` | `0.1316` (`0.153`) | `0.0157` (`0.021`) | `0.6600` `[0.359, 0.810]` | `0.0010` | `0.0044` |
| `test_llm_plus_ctrl` / `ce_cal_all5_rps` | `P_e42_probe_rps` | `22` | `0.0084` | `0.0068` (`m=10`) | `0.0067` | `0.8847` `[0.754, 0.962]` | `0.1263` (`0.153`) | `0.0183` (`0.021`) | `0.7173` `[0.453, 0.850]` | `0.0004` | `0.0050` |
| `test_llm_plus_ctrl` / `raw_all5_rps` | `C_ms_gold` (`ctrl`) | `20` | `0.1243` | `0.1106` (`m=10`) | `0.1013` | `0.5637` `[0.300, 0.850]` | `0.1597` (`0.248`) | `0.0773` (`0.056`) | `0.1379` `[-0.380, 0.609]` | `0.5455` | `0.3255` |
| `test_llm_plus_ctrl` / `raw_all5_rps` | `P_e42_fullcov_brier` | `22` | `0.0257` | `0.0188` (`m=10`) | `0.0253` | `0.8904` `[0.802, 0.951]` | `0.0630` (`0.251`) | `0.0411` (`0.057`) | `0.7662` `[0.511, 0.872]` | `0.0002` | `0.0022` |
| `test_llm_plus_ctrl` / `raw_all5_rps` | `P_e42_strict_brier` | `22` | `0.0183` | `0.0166` (`m=10`) | `0.0172` | `0.9049` `[0.823, 0.963]` | `0.0453` (`0.251`) | `0.0486` (`0.057`) | `0.7169` `[0.383, 0.848]` | `0.0002` | `0.0024` |
| `test_llm_plus_ctrl` / `raw_all5_rps` | `P_e42_probe_rps` | `22` | `0.0110` | `0.0090` (`m=10`) | `0.0096` | `0.9282` `[0.861, 0.972]` | `0.1052` (`0.251`) | `0.0568` (`0.057`) | `0.7840` `[0.497, 0.898]` | `0.0002` | `0.0034` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `TI_var_trainnorm` | `16` | `0.0379` | `0.0324` (`m=10`) | `0.0287` | `0.3679` `[0.147, 0.600]` | `0.1211` (`0.123`) | `0.0200` (`0.021`) | `-0.1681` `[-0.591, 0.301]` | `0.5299` | `0.4829` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `C_ms_gold` | `16` | `0.0071` | `0.0111` (`m=10`) | `0.0101` | `0.8264` `[0.608, 0.949]` | `0.0865` (`0.123`) | `0.0142` (`0.021`) | `0.5887` `[0.096, 0.826]` | `0.0200` | `0.0944` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `P_e42_fullcov_brier` | `16` | `0.0189` | `0.0166` (`m=10`) | `0.0187` | `0.8152` `[0.559, 0.959]` | `0.1242` (`0.123`) | `0.0139` (`0.021`) | `0.6152` `[0.103, 0.839]` | `0.0120` | `0.0302` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `P_e42_strict_brier` | `16` | `0.0133` | `0.0128` (`m=10`) | `0.0123` | `0.8365` `[0.611, 0.964]` | `0.1269` (`0.123`) | `0.0139` (`0.021`) | `0.6747` `[0.235, 0.866]` | `0.0044` | `0.0112` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `P_e42_probe_rps` | `16` | `0.0071` | `0.0074` (`m=10`) | `0.0054` | `0.8531` `[0.611, 0.973]` | `0.1092` (`0.123`) | `0.0162` (`0.021`) | `0.6118` `[0.100, 0.852]` | `0.0118` | `0.0356` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `P_dsti_proper` | `16` | `0.0189` | `0.0166` (`m=10`) | `0.0187` | `0.8149` `[0.556, 0.963]` | `0.1359` (`0.123`) | `0.0161` (`0.021`) | `0.6240` `[0.101, 0.859]` | `0.0114` | `0.0254` |
| `common_support_test_llm` / `ce_cal_all5_rps` | `P_dsti_gated` | `16` | `0.0379` | `0.0237` (`m=10`) | `0.0282` | `0.8022` `[0.549, 0.954]` | `0.0963` (`0.123`) | `0.0124` (`0.021`) | `0.5971` `[0.115, 0.845]` | `0.0160` | `0.0556` |
| `common_support_test_llm` / `raw_all5_rps` | `C_ms_gold` | `16` | `0.0110` | `0.0153` (`m=10`) | `0.0144` | `0.8307` `[0.686, 0.926]` | `0.0673` (`0.254`) | `0.0392` (`0.054`) | `0.5607` `[0.035, 0.751]` | `0.0266` | `0.0538` |
| `common_support_test_llm` / `raw_all5_rps` | `P_e42_strict_brier` | `16` | `0.0183` | `0.0172` (`m=10`) | `0.0169` | `0.8865` `[0.704, 0.965]` | `0.0601` (`0.254`) | `0.0325` (`0.054`) | `0.6359` `[0.114, 0.847]` | `0.0086` | `0.0080` |
| `common_support_test_llm` / `raw_all5_rps` | `P_e42_probe_rps` | `16` | `0.0110` | `0.0098` (`m=10`) | `0.0077` | `0.9165` `[0.718, 0.984]` | `0.1413` (`0.254`) | `0.0339` (`0.054`) | `0.7235` `[0.213, 0.935]` | `0.0014` | `0.0114` |

### Table 2C — Locked Meta-Selection Head-to-Head (`Arm A: Meta-Corr` vs `Arm B: Meta-Proper-RPS`)

- **`llm_selected_zero_overlap` (selected on `38` `train+val` LLMs only; evaluated unseen on `test_llm` and `test_llm_plus_ctrl`):**
  - `Arm A` (`Meta-Corr`) picks **`P_e42_strict_brier`** (`Sp = 0.8536` on `train+val`): on `test_llm` (`ce_cal`), Top-1 `0.0146`, `Sub-10 = 0.0138`, `UWA = 0.8173` (`+ctrl`: `0.0146`, `0.0136`, `UWA = 0.8501`).
  - `Arm B` (`Meta-Proper-RPS`) picks **`P_dsti_gated`** (`P_e42 * C_ms_gold`, `Sub-10 = 0.0066` on `train+val`): misses `qwen36\|H2`/`R4` and loses out-of-sample with Top-1 `0.0379`, `Sub-10 = 0.0237`, `UWA = 0.8022` on `test_llm` (`+ctrl`: `0.0379`, `0.0204`, `UWA = 0.8490`).
  - `Arm B_raw` picks **`P_dsti_proper`**: on `test_llm` (`raw_all5_rps`), Top-1 `0.0257`, `Sub-10 = 0.0209`, `UWA = 0.8737` (vs `Arm A` `0.0183`, `0.0170`, `UWA = 0.8810`).
- **`trainval_with_ctrl_selected` (`controls_overlap_trainval_and_stress_pool = True` secondary robustness check):** `Arm A` picks **`P_e39_curve_rps`**, which gets **hijacked by controls** on `test_llm_plus_ctrl` (`top1 = 0.0397` picking `ctl|count_ratio` & `ctl|name_jaccard`, `UWA = 0.7350`) while `Arm B` (`P_dsti_gated`) holds controls off (`top1 = 0.0379`, `UWA = 0.8490`).

---

## Study 3: Open-Weight Replication (`E60` Streaming Tarballs + `E58` `117`-Unit Check)

| Cohort & Target | Proxy | `n` | Top-1 Regret | `Subpool-10` Regret | `LOFO` Regret | `UWA` | Spearman `[95% CI]` | `perm p` |
|---|---|---|---|---|---|---|---|---|
| `e60_seed0_26` / `ce_cal_all5_rps` | `TI_var_trainnorm` | `26` | `0.0332` | `0.0333` | `0.0326` | `0.3642` | `-0.2841` `[-0.615, 0.090]` | `0.1726` |
| `e60_seed0_26` / `ce_cal_all5_rps` | `C_ms_gold` | `26` | `0.0000` | `0.0092` | `0.0038` | `0.8832` | `0.7094` `[0.460, 0.852]` | `0.0002` |
| `e60_seed0_26` / `ce_cal_all5_rps` | `P_e39_fullcov_brier` | `26` | `0.0127` | `0.0100` | `0.0130` | `0.8651` | `0.5810` `[0.229, 0.812]` | `0.0032` |
| `e60_seed1_36` / `ce_cal_all5_rps` | `TI_var_trainnorm` | `36` | `0.0155` | `0.0199` | `0.0157` | `0.4104` | `-0.2077` `[-0.493, 0.114]` | `0.2266` |
| `e60_seed1_36` / `ce_cal_all5_rps` | `C_ms_gold` | `36` | `0.0321` | `0.0142` | `0.0263` | `0.6755` | `0.3073` `[-0.081, 0.603]` | `0.0688` |
| `e60_seed1_36` / `ce_cal_all5_rps` | `P_e39_fullcov_brier` | `36` | `0.0165` | `0.0107` | `0.0154` | `0.7686` | `0.5271` `[0.258, 0.715]` | `0.0016` |
| `e60_seed1_36` / `raw_all5_rps` | `C_ms_gold` | `36` | `0.0695` | `0.0297` | `0.0550` | `0.6164` | `0.3344` `[0.007, 0.588]` | `0.0470` |
| `e60_seed1_36` / `raw_all5_rps` | `P_e39_fullcov_brier` | `36` | `0.0268` | `0.0187` | `0.0251` | `0.8514` | `0.6969` `[0.450, 0.857]` | `0.0002` |
| `E58` (`117` units) / `raw_exp3_spearman` | `C_ms_gold` | `114` | `0.0770` | `0.1465` | `0.0815` | `0.7362` | `0.4599` `[0.293, 0.605]` | `0.0002` |
| `E58` (`117` units) / `raw_exp3_spearman` | `P_e42_disc` | `115` | `0.4255` | `0.1990` | `0.4178` | `0.8264` | `0.6523` `[0.535, 0.741]` | `0.0002` |
| `E58` (`117` units) / `raw_exp3_spearman` | `TI_var_trainnorm` | `115` | `0.7511` | `0.5079` | `0.7568` | `0.4474` | `-0.0921` `[-0.265, 0.079]` | `0.3241` |

`E62` parity (`seed0` `C_ms_gold` max diff `2.22e-16`, `Spearman` `0.0`). `E60` `seed0 vs seed1` `C_ms_gold` `|diff|` mean `0.0349` (`n=36`).

---

## Study 4: `native_main` (`N=100`, `250` Ratings) Bridge & `E63` Check

(`CONST_loto RPS = 0.0698`, `CE = 0.8716`, `TVD = 0.3636`; Empirical LORO ceiling `RPS = 0.0580`.)

| Judge / Baseline (`native_main` `100` files) | `raw RPS` `[95% CI]` | `raw CE` | `raw TVD` | `ICC(A,1)` | `MAE_05` | `bias_05` | `LOTO CE-fit RPS` `[95% CI]` | `LOTO CE` / `TVD` | `dRPS` vs `CONST` (`p-val`) | Proxy Ref (`P_e42_fullcov_brier` / `P_dsti_proper` / `C_ms_gold`) |
|---|---|---|---|---|---|---|---|---|---|---|
| `H2_astra` | `0.0913` `[0.0833, 0.1006]` | `0.9896` | `0.4533` | `0.8242` | `0.2617` | `0.0517` | `0.0433` `[0.0282, 0.0601]` | `0.6564` / `0.2771` | `-0.0266` (`p=0.0005`) | `sol6h\|H2` (`0.8440` / `0.8998` / `0.9778`) |
| `H2_opus` | `0.0861` `[0.0814, 0.0917]` | `0.9370` | `0.4375` | `0.8576` | `0.2417` | `0.1117` | `0.0440` `[0.0298, 0.0595]` | `0.6712` / `0.2959` | `-0.0258` (`p=0.0005`) | `opus55x\|H2` (`0.9553` / `0.9581` / `0.9942`) |
| `H3_astra_native_probs` | `0.0414` `[0.0262, 0.0577]` | `0.7652` | `0.2246` | `0.8224` | `0.2750` | `0.0117` | `0.0433` `[0.0286, 0.0592]` | `0.6544` / `0.2768` | `-0.0265` (`p=0.0005`) | `sol6h\|H2` (`0.8440` / `0.8998` / `0.9778`) |
| `edit_similarity` | `0.3702` `[0.3452, 0.3935]` | `2.0794` | `0.8275` | `0.0014` | `4.4191` | `-4.4191` | `0.0697` `[0.0419, 0.0993]` | `0.8713` / `0.3599` | `-0.0001` (`p=0.6712`) | `ctl\|editdist` (`0.8195` / `0.8902` / `1.0000`) |
| `length_ratio_capped` | `0.1643` `[0.1566, 0.1724]` | `1.2811` | `0.6150` | `0.3798` | `0.3981` | `0.2635` | `0.0652` `[0.0389, 0.0937]` | `0.8383` / `0.3448` | `-0.0046` (`p=0.0090`) | `ctl\|count_ratio` (`0.6094` / `0.7852` / `1.0000`) |
| `seeded_random_uniform` | `0.2695` `[0.2453, 0.2929]` | `1.9165` | `0.7692` | `0.0259` | `2.0325` | `-1.9343` | `0.0702` `[0.0422, 0.1000]` | `0.8762` / `0.3618` | `0.0004` (`p=0.2369`) | `ctl\|random` (`0.6022` / `0.5993` / `0.1250`) |
| `gpt-5.3-codex\|P8_STRICT_B` (Exp 67) | `0.2428` `[0.2050, 0.2826]` | `2.0539` | `0.7492` | `—` | `—` | `—` | `not computed` | `not computed` | `+0.1730` (`raw` vs `CONST`) | `sol6h\|P8` (`0.7581` / `0.8165` / `0.8666`) |
| `claude-opus-4-7\|P8_STRICT_B` (Exp 67) | `0.2169` `[0.1748, 0.2609]` | `1.8377` | `0.6908` | `—` | `—` | `—` | `not computed` | `not computed` | `+0.1471` (`raw` vs `CONST`) | `opus55x\|P4` same-fam (`0.8058` / `0.8534` / `0.6662`) |
| `Qwen3-Coder-30B\|P8_STRICT_B` (Exp 67) | `0.1263` `[0.1116, 0.1422]` | `1.3898` | `0.5625` | `—` | `—` | `—` | `not computed` | `not computed` | `+0.0565` (`raw` vs `CONST`) | `qwen36\|P8` (`0.8001` / `0.8805` / `0.8329`) |

`E63` (`6` arms, `R_v1` `test` `n=25`) max parity diff vs Exp 68 `study_a` = `0.0` (`human_mix_sft` `RPS=0.1416`, `CE=1.6205`, `TVD=0.3850`, `Brier=0.7447`, `ICC=0.7400` vs `rl_grpo` `RPS=0.2133`, `CE=5.5558`, `Spearman=0.5427`). The three `Exp 67` `P8_STRICT_B` interim rows (`set = "new (interim)"`) come from the `11-24-2026` `247`-rating snapshot on the same `100` files / `25` tasks (prior to `V04`'s `3` ratings in `460466d`; `CONST_loto RPS` rounds to `0.0698` on both).

---

## Key Caveats & Deviations from `PROTOCOL.md`

1. **Zero-leakage hardening (stricter than initial draft):** `beat_const_meta_pred`, `risk_meta_pred`, and the primary `head_to_head` pool (`llm_selected_zero_overlap`) fit/select strictly on the `38` `train+val` LLMs (excluding `ctl|*`), so all `4` controls remain completely unseen in `test_llm_plus_ctrl`.
2. **`P_e42_strict_brier` & finite-`m` ceilings:** `P_e42_strict_brier` uses `E42/probe_edits/audit/*.json` (`25` strict `weakening`, `20` strict `overconstraint`, plus `identity`, `formatting`, `vacuity`). With `alpha = 0.5`, `P_e42_*` (`m=3`) has a finite-sample ceiling of `0.9844`, whereas `P_e39_fullcov_brier` (`m=3` on `ident` vs `m=1` on `blank`/`leaf`) has a finite-sample ceiling of `0.9609` (and `P_dsti_proper` `0.9727`), approaching `1.000` only as `m -> infinity`.
3. **Reduced-support oracle discounting:** `top1_regret_label_free` and `expected_subpool_regret` evaluate within each proxy's valid support (`n=16` for `C_ms_gold`/`P_dsti_gated`, omitting #1/#2 test judges `qwen36|H2`/`R4`, and `m=9` for `PTI_v0_frozen`); `common_support_test_llm` (`n=16`) equalizes support directly.
4. **`ctl|editdist` change-detector failure of literal `<= 0.78` bound:** Levenshtein edit similarity achieves `P_e42_fullcov_brier = 0.8195` and `P_dsti_proper = 0.8902` despite `calRPS = 0.1689` (`rawRPS = 0.2531`); only `P_e42_disc` (which subtracts formatting false alarms) or Top-1 LLM ordering separates LLMs (`0.9553–0.9844`) cleanly from `ctl|editdist`.
5. **Native-main score-5 ceiling:** `74.0%` (`185/250`) human ratings on `native_main` are `5`, limiting separation against lenient or constant baselines until more multi-quality human ratings land.
6. **Google Drive & Gmail OAuth Connectors + `T30`:** Both MCP connectors returned `Unauthorized: rejected by transport`; `GDOC_COMPANION_11-26-2026.md` is staged locally and email notification uses `uutils.emailing` SMTP. The private `T30` Sheet URL is omitted from committed files (`t30_status = skipped_no_local_id` in automated re-runs; manually verified `401 Unauthorized`).
7. **Fresh judge calls paused:** Per `10-15-2026` Valkyrie spend pause, fresh probe cells for `P8_STRICT_B` and new-cohort `N=100` judge inferences remain unrun; `claude-opus-4-7|P8_STRICT_B` maps to same-family `opus55x|P4`.

---

## 3-Stage Mega QA Summary (Verbatim Audit Record)

- **Receipt:** [results/MEGA_QA_RECEIPT_11-26-2026.json](results/MEGA_QA_RECEIPT_11-26-2026.json)
- **Company diversity disclosure:** `missing_company_diversity: true` (all 3 sequential stages ran via included `agy` subscription on Google-family models: `gemini-pro-orchestrator`, `gemini-4-carbon-high`, and fresh `gemini-pro-orchestrator`).
- **Stage 1 (`gemini-pro-orchestrator`, [qa_stage1_orchestrator_carbon_11-26-2026.txt](results/qa_stage1_orchestrator_carbon_11-26-2026.txt)):** `VERDICT: NEEDS_FIX` (`1 BLOCKER, 4 MAJOR, 6 MINOR`) — caught hardcoded participant name/domains/Sheet ID in initial script/tests, `[0.258, 0.715]` Study 3 CI typo, table truncation-vs-rounding differences, omitted `common_support_test_llm` table & negative head-to-head finding in `.tex`, raw vs calibrated `AUROC` split, and finite-`m` ceilings. All reconciled and pipeline re-run cleanly.
- **Stage 2 (`gemini-4-carbon-high`, [qa_stage2_carbon_high_11-26-2026.txt](results/qa_stage2_carbon_high_11-26-2026.txt)):** `VERDICT: NEEDS_FIX` (`2 BLOCKER, 0 MAJOR, 5 MINOR`) — verified zero remaining math/split-leakage/rounding defects; caught quoted Sheet ID in Stage 1 log, unpushed pre-rebase git history PII, `brando90` URL typo, CSV `beat_const_calibrated_auroc` omission, strict-subset coverage guard, and Exp 67 `247`-rating provenance note. Resolved cleanly by squashing onto `origin/main` `3755590` and renumbering to Experiment `70` (`e643cef3`).
- **Stage 3 (`gemini-pro-orchestrator` fresh context, [qa_stage3_orchestrator_carbon_fresh_11-26-2026.txt](results/qa_stage3_orchestrator_carbon_fresh_11-26-2026.txt)):** **`VERDICT: PASS`** (`0 BLOCKER, 0 MAJOR, 2 MINOR`) — verified `6/6` unit tests (`test_exp70.py`), `0` PII/secrets/Sheet-IDs across `git diff 3755590..e643cef` and compiled PDFs, `Layout OK` (`17` active experiments), and `0` parity mismatches across JSON/CSV/Markdown/LaTeX. Resolved Minor #1 inline comment (`247`-rating snapshot) in `run_exp70.py:885`.

**TLDR-end:** [cert-judge: exp70 proper-scoring proxy-target] Live VeriBench `native_main` remains at `250` non-`A1` ratings (`33/33` public Sheets unchanged, `CONST_loto RPS=0.0698`). On `E39+E42` (`n=60`), `C_ms_gold` is hijacked on `+ctrl` (`Top-1 ce_cal RPS regret=0.0390`, `raw=0.1243`) and blind to #1/#2 test judges (`qwen36|H2`/`R4`), whereas proper-scoring label-free behavioral proxies (`P_e42_probe_rps` `UWA=0.8614`/`0.9173`, `P_e42_strict_brier` `Meta-Brier=0.0549` vs `0.256` on `rawRPS`, `P_e42_fullcov_brier` `Meta-RMSE=0.0282` vs `0.056`, `E60 seed1` `UWA=0.8514` vs `C_ms_gold` `0.6164`) reject controls at Top-1 and calibrate risk across raw & calibrated targets, while `ctl|editdist` (`0.8195`) exposes a change-detector loophole and `74.0%` native score-5 ceiling limits `N=100` discrimination (`$0` spend, CPU-only + read-only public Sheets; 3-stage `agy` Mega QA `PASS`).
