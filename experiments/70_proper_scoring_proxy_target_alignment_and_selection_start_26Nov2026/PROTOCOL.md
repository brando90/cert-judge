# PROTOCOL — Experiment 70: Proper-Scoring Proxy-vs-Target Alignment and Selection (`11-26-2026`)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/PROTOCOL.md>

Date: 11-26-2026

**TLDR:** Pre-registered measurement contract, exact formulas, split/tie-breaking/privacy guarantees, and falsifiable predictions (`P1`–`P4`), frozen prior to executing `scripts/run_exp70.py` on held-out test judges. *(Originally pre-registered as Experiment 69 with `seed=69` prior to execution and renumbered to Experiment 70 per `AGENTS.md` after Cursor merged `69_proxy_target_proper_score` onto `main`; `seed=69` and all contract definitions remain unchanged.)*

---

## 1. Scope, Spend, and Privacy Rules

- **Zero API / Valkyrie spend (`$0`):** Strictly offline CPU analysis of saved local harvests/ratings plus read-only HTTPS checks of the 33 accessible public VeriBench Google Sheet CSV exports (`docs.google.com`). No LLM calls (`no internet` for Studies 2–3 and the `E63`/historical checks of Study 4; read-only HTTPS for Study 1 / Study 4 live Sheet verification; `no DT applicable`).
- **Privacy (public repository):** Zero rater names, zero personal emails, zero raw per-rater Sheet rows, and zero participant notes/rationales may appear in any committed JSON, CSV, Markdown, figure, or `.tex` file in `cert-judge`. Only anonymized rater IDs (`T05`, `T08`, ...) and aggregate statistics are exported.
- **No data leakage:**
  - Within-panel item calibration (`CONST`, `CE_fit`, `Pearson_fit`) on `R_v1` (`75` items / `25` tasks) fits strictly on the `30` `train` items (`10` tasks) and evaluates strictly on the `45` held-out (`val + test`, `15` tasks) items.
  - Leave-One-Task-Out (`LOTO`) calibration on `native_main` (`100` items / `25` tasks) holds out all `4` agent artifacts of each task per fold.
  - Meta-level proxy selection (`Meta-Corr` vs `Meta-Proper-RPS`) and meta-level risk/probability calibrators (`Beat-CONST` logistic calibrator, continuous `RPS` monotone/ridge calibrator) fit/select strictly on `train + val` judge families (`38` LLMs, or `38 LLMs + 4 controls`) and evaluate **once** on the `18` held-out `test` judge families (`+ 4` controls).
- **Strictly label-free tie-breaking:** Whenever multiple judge configurations tie at $\max_j P(j)$, Top-1 selection regret and subpool selection regret report the **exact uniform expectation (mean target loss)** over all tied maximizers—never breaking ties using held-out target scores.

---

## 2. Measurement Contract (Committed Before Execution)

| Metric | Code path | Range / Direction | Oracle judge | Intended strong LLM judge | Literal compliance (probabilistic / rubric LLM) | Degenerate / adversarial controls (`editdist`, `name_jaccard`, `count_ratio`, `random`, `LEX`) | Constant baseline (`CONST_train`) |
|---|---|---|---|---|---|---|---|
| Item `RPS` | `proxy_metrics.py` / `metrics.py` | `[0, 1]`, lower better | `<= 0.147` (`LORO` floor on `R_v1`) | `~0.125–0.145` (`CE_fit`) | Matches `~0.13–0.16` when calibrated | `0.174–0.37` (`>= CONST` or `~CONST`) | `0.1739` (`R_v1`), `0.070` (`native_main`) |
| Item `CE` | `proxy_metrics.py` / `metrics.py` | `[0, inf)` nats, lower better | `~1.45–1.67` (`LORO`) | `~1.48–1.65` (`CE_fit`) | Finite, well-calibrated (`< 1.75`) | `>= 1.75` (up to `5+` if overconfident) | `1.7537` (`R_v1`), `~0.88` (`native_main`) |
| Item `Brier` (6-class) | `proxy_metrics.py` / `metrics.py` | `[0, 2]`, lower better | `~0.72–0.79` | `~0.74–0.80` | Finite (`< 0.82`) | `>= 0.82` | `0.8248` (`R_v1`) |
| `P_e42_fullcov_brier` | `proxy_metrics.py` | `[0, 1]`, higher better | `1.000` (exact indicator `1` on covered, `0` on degraded) | `~0.85–0.96` | `>= 0.85` (penalizes vacuity/weakening/overconstraint, credits formatting/identity) | `<= 0.78` (e.g. `editdist` / `LEX` / `count_ratio` / `name_jaccard` fail semantic weakenings or formatting invariance) | `0.750` (uniform `q=0.5` has Brier `0.25`) |
| `P_e39_fullcov_brier` | `proxy_metrics.py` | `[0, 1]`, higher better | `1.000` | `~0.85–0.97` | `>= 0.85` | `editdist ~0.82–0.90`; `name_jaccard` / `count_ratio` up to `0.95+` (E39-only lacks semantic weakenings) | `0.750` |
| `P_dsti_proper` | `proxy_metrics.py` | `[0, 1]`, higher better | `1.000` | `~0.86–0.96` | `>= 0.85` | `<= 0.80` (`E42` semantic screen blocks lexical controls) | `0.750` |
| `Top-1 RPS Regret` | `proxy_metrics.py` | `[0, 1]`, lower better (`0` = oracle) | `0.000` | `< 0.015` (LLM-only & `+ctrl`) | `< 0.015` | `C_ms_gold` on `+ctrl`: `> 0.03` (picks `name_jaccard`/`editdist`/`count_ratio`) | Pool mean (`~0.03–0.05`) |
| `UWA_RPS` | `proxy_metrics.py` | `[0, 1]`, higher better | `1.000` | `> 0.75` | `> 0.75` | `~0.50` (`random`), `< 0.50` (`TI_var` if inverted) | `0.500` (uninformative) |
| `Beat-CONST Meta-Brier` | `proxy_metrics.py` | `[0, 1]`, lower better | `0.000` | `< base_rate_brier` | `< base_rate_brier` | `>= base_rate_brier` | `p_bar * (1 - p_bar)` |

---

## 3. Exact Mathematical Definitions

### 3.1 Human Target Metrics $T(j)$ (Lower is Better for Proper Losses)

Over discrete rating categories $c \in \{0, 1, 2, 3, 4, 5\}$, for artifact $i \in \{1, \dots, N\}$ with $R_i$ individual human ratings $r_{i,1}, \dots, r_{i,R_i}$, empirical distribution $\hat p_i(c)$, and judge forecast $q_i \in \Delta^5$ (with cumulative distribution $F_{q_i}(k) = \sum_{c=0}^k q_i(c)$):
- **Normalized Individual-Rating `RPS`** (primary):
  $$\mathrm{RPS}_i(q_i) = \frac{1}{R_i} \sum_{j=1}^{R_i} \frac{1}{5} \sum_{k=0}^4 \bigl(F_{q_i}(k) - \mathbf{1}\{r_{i,j} \le k\}\bigr)^2 \in [0, 1].$$
- **Cross-Entropy (`CE`)**: $\mathrm{CE}_i(q_i) = -\frac{1}{R_i}\sum_{j=1}^{R_i}\log \max(q_i(r_{i,j}), 10^{-12})$ (nats).
- **Total Variation Distance (`TVD`)**: $\mathrm{TVD}_i(q_i) = \frac{1}{2}\sum_{c=0}^5 |q_i(c) - \hat p_i(c)| \in [0, 1]$.
- **6-Class `Brier`**: $\mathrm{Brier}_i(q_i) = \sum_{c=0}^5 q_i(c)^2 - 2\sum_{c=0}^5 \hat p_i(c) q_i(c) + 1 \in [0, 2]$.
- **Raw vs Calibrated Forecasts:**
  - `raw`: repeat scores $s_{i,1}, \dots, s_{i,m} \in [0, 1]$ binned via $\lfloor 5 s + 0.5 \rfloor$ with symmetric Laplace smoothing $\alpha = 0.5$.
  - `ce_cal` / `pe_cal`: cumulative ordinal logit (`fit_ce_ordinal`) or Gaussian-truncated (`fit_pearson_gauss`) map fit strictly on `train` tasks (`30` items on `R_v1`, or `LOTO` on `native_main`).
- **Scalar agreement diagnostics:** `MAE_05`, `bias_05` (`judge_mean_05 - human_mean_05`, positive = lenient), `ICC(A,1)` (absolute agreement), `ICC(C,1)` (consistency), `Spearman`, `Kendall`, `Pearson`.

### 3.2 Label-Free Proper-Scoring Behavioral Proxies $P(j)$

All proxies below use **zero human ratings** and are computed solely from Lean-validated probe harvests in `E39`, `E42`, and `E60`:
- Let a probe $p$ have measured repeat scores $s_{p,1}, \dots, s_{p,m} \in [0, 1]$. Define its Laplace-smoothed full-coverage probability:
  $$\hat q_{\text{full}}(p) = \frac{\sum_{r=1}^m \mathbf{1}\{s_{p,r} \ge 0.999\} + 0.5}{m + 1} \in (0, 1),$$
  its mean score $\bar s_p = \frac{1}{m}\sum_{r=1}^m s_{p,r}$, and its 6-bin distribution $q_p = \text{binned\_repeats\_to\_probs}(s_p, \alpha=0.5)$.
- **`P_e42_fullcov_brier`** (`1 - balanced Brier` on Lean-verified E42 semantic probes, `194` probes):
  - Positive class ($y_{\text{full}} = 1$, reference-equivalent Lean declarations): `identity` (`24` probes) and `formatting` (`38` probes: `fmt_comments`, `fmt_layout`), weighted equally ($0.5 \cdot \overline{\text{Brier}}_{\text{ident}} + 0.5 \cdot \overline{\text{Brier}}_{\text{fmt}}$).
  - Negative class ($y_{\text{full}} = 0$, Lean-proved defective or vacuous specifications): `vacuity` (`38` probes), `weakening` (`57` probes), and `overconstraint` (`37` probes), weighted equally across the three families ($\frac{1}{3}\overline{\text{Brier}}_{\text{vac}} + \frac{1}{3}\overline{\text{Brier}}_{\text{weak}} + \frac{1}{3}\overline{\text{Brier}}_{\text{overc}}$).
  - Overall score: $P_{\text{e42\_fullcov\_brier}} = 1 - \bigl(0.5\,\overline{\text{Brier}}_{+} + 0.5\,\overline{\text{Brier}}_{-}\bigr) \in [0, 1]$.
  - Variants reported beside it: **`P_e42_fullcov_ce`** (negative balanced binary cross-entropy), **`P_e42_score_brier`** (using $\bar s_p$ instead of $\hat q_{\text{full}}$), **`P_e42_strict_brier`** (excluding file-level redundant weakenings as sensitivity), and **`P_e42_disc`** (E42 Amendment 1 discrimination).
- **`P_e39_fullcov_brier`** & **`P_e39_probe_rps`** (E39-only probes, applicable to `E60` open-weight harvests):
  - Positive class ($y_{\text{full}} = 1$): valid `ident` (`24` probes).
  - Negative class ($y_{\text{full}} = 0$): valid `blank` (`25` probes) and max-level `ms_gold` leaves (all theorem statements removed, `24` probes).
  - **`P_e39_probe_rps`**: $1 - \text{mean\_balanced\_RPS}(q_p, y \in \{5 \text{ for ident}, 0 \text{ for blank/leaf}\})$.
  - **`P_e39_curve_rps`**: $1 - \text{mean\_RPS}(q_p, \text{round}(5(1 - \ell / \ell_{\max})))$ across valid `ident` ($\ell=0$) and `ms_gold` ladder levels ($\ell=1\dots\ell_{\max}$).
  - **`P_e39_ms_margin`**: mean continuous downward score margin $(\bar s_{\ell-1} - \bar s_\ell)$ on `ms_gold` ladders (sensitive to step magnitude rather than sign-only rank).
- **`P_dsti_proper`** (Distributional-Semantic Trust Index):
  - $P_{\text{dsti\_proper}} = 0.5 \cdot P_{\text{e39\_fullcov\_brier}} + 0.5 \cdot P_{\text{e42\_fullcov\_brier}}$.
  - Multiplicative lexical-screened variant: $P_{\text{dsti\_gated}} = P_{\text{e42\_fullcov\_brier}} \cdot \max(0, C_{\text{ms\_gold}})$.
- **Coverage rule:** Compute `P_e39_*` / `P_e42_*` when at least `80%` of declared valid probes in each family are measured (`deterministic` included); otherwise mark `None` (`NOT_COMPUTABLE`), and report both full available `n` and common-support pools.

### 3.3 Meta-Similarity Metrics Between Proxy $P(j)$ and Target $T(j)$

1. **Top-1 Selection Regret** (in `RPS`, `CE`, `TVD`, `Brier`): $\mathbb{E}_{j^* \in \arg\max P}[T(j^*)] - \min_j T(j)$ (exact uniform mean over ties).
2. **Expected Subpool Selection Regret & Beat-`CONST` Rate:** Over $2{,}000$ seeded draws (`seed=69`) of subpools of size $m \in \{5, 10\}$ (and full `LOFO` over judge families), mean regret of $\arg\max_{j \in S} P(j)$ and fraction of draws beating `CONST`.
3. **Utility-Weighted Pairwise Decision Accuracy (`UWA`):**
   $$\mathrm{UWA}_T(P) = \frac{\sum_{j_1 < j_2} |T(j_1) - T(j_2)| \cdot \bigl(\mathbf{1}\{\text{correct order}\} + 0.5\,\mathbf{1}\{P(j_1)=P(j_2)\}\bigr)}{\sum_{j_1 < j_2} |T(j_1) - T(j_2)|}.$$
4. **Proper-Scoring Meta-Prediction of `Beat-CONST` (`RPS < RPS_CONST`) and `Top-Quartile`:** 1D logistic regression fit strictly on `train + val` judge families, evaluated on `test` judge families by **Meta-Brier**, **Meta-CE**, **Meta-Brier Skill**, and **AUROC**.
5. **Continuous Target-Risk Prediction (`P -> RPS`):** 1D ridge linear / isotonic map fit strictly on `train + val` judge families, evaluated on `test` judge families by **Meta-MAE**, **Meta-RMSE**, **Meta-$R^2$**, and **Meta-ICC(A,1)**.
6. **Secondary Rank Diagnostics:** `Spearman`, `Kendall`, `Pearson` with config-bootstrap (`2,000`), family-cluster bootstrap (`2,000`), two-level bootstrap (`2,000`), and exact/Monte Carlo (`10,000`) permutation and within-family permutation `p-val`.

---

## 4. Pre-Registered Predictions (`P1`–`P4`)

- **P1 (Control vulnerability of `C_ms_gold` vs protection by `P_e42_fullcov_brier` / `P_dsti_proper`):** On control-inclusive pools (`test_llm_plus_ctrl`, `all_plus_ctrl`), `C_ms_gold` selects a deterministic lexical control (`name_jaccard` / `editdist` / `count_ratio`) with Top-1 `ce_cal_all5_rps` regret `> 0.030`, whereas `P_e42_fullcov_brier` and `P_dsti_proper` reject all 4 controls (`control score <= 0.78`) and achieve Top-1 regret `< 0.015`.
- **P2 (Proper-score advantage on raw & calibrated targets):** On `test_llm` (`n=18`), `P_e42_fullcov_brier` and `P_dsti_proper` achieve lower `Top-1 / Subpool RPS Regret`, higher `UWA_RPS`, and lower `Beat-CONST Meta-Brier` than `TI_var_trainnorm` and `PTI_v0_frozen` on both `raw_all5_rps` and `ce_cal_all5_rps`, and match or outperform `C_ms_gold` on `raw_all5_rps` (where scale/harshness matters).
- **P3 (`E60` open-weight replication):** On `e60_harv0.tgz` (`26` seed-0 units) and `e60_harv1.tgz` (`36` seed-1 replicates), `P_e39_fullcov_brier` / `P_e39_probe_rps` beat `TI_var` and `PTI_v0` on `UWA_RPS` and `Subpool Regret`, and maintain high seed-0 vs seed-1 rank & Brier stability.
- **P4 (`native_main` `N=100` bridge):** On the `11-26-2026` live-verified `native_main` ratings (`250` non-`A1` ratings, `100` files / `25` tasks), `H2_astra`, `H2_opus`, and `H3_astra` (CE-calibrated) beat `CONST_loto` (`RPS ~0.030–0.055` vs `0.070`), whereas `P8_STRICT_B` (`Codex`, `Opus`, `Qwen3-Coder`) fails to beat `CONST_loto` (`raw RPS 0.126–0.243`), and `P_e42_fullcov_brier` / `P_dsti_proper` separate `H2` from `P8_STRICT_B` and lexical controls (subject to the `72.8%` score-5 ceiling caveat).
