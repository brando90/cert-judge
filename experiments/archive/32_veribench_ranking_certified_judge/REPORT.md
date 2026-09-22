# Experiment 32 — VeriBench agent ranking under a certified-family judge

**TLDR-start:** [cj: exp32-certified-ranking] STOPPED after repeat layer 0: re-scoring all 140 outputs of each agent with the Section 5.3 P1_BASELINE prompt on the currently served Codex model (`gpt-5.6-terra`; `gpt-5.3-codex` is no longer offered) via 846 subscription `codex exec` calls ($0 API) keeps DSPy ReAct first (0.178, 95% CI [0.118, 0.241]) and Baseline last (0.072 [0.050, 0.097]) with Trace+ (0.120) and Trace++ (0.119) tied; Brando then ruled the table a carried-over VeriBench result that will be cut from the ICLR paper, so layers 1–2 and the property suite were not run.

## 1. Question
Section 5.4 of `paper_latex/ICLR_2027_submission/main.tex` (`tab:theorem_quality_table_split`) ranks four Claude 3.7 agents (Baseline 0.470, DSPy ReAct 0.615, Trace+ 0.477, Trace++ 0.588) with a Claude 3.7 judge that the paper's own property protocol never certified (reviewer DeJF). This experiment re-scores the same 140 agent outputs per agent with the certified primary judge configuration from Section 5.3 through subscription CLIs only, and asks whether the ordering survives.

## 2. Method (frozen before inference; see `CKPT.md` quote)
| Element | Value |
|---|---|
| Inputs | The four agent runs pinned in `~/veribench/CONTRIBUTING.md:180-183` (Claude 3.7 Sonnet as agent model): baseline, DSPy ReAct, Trace self-debug (Trace+), Trace self-debug+self-improve (Trace++); 140 `.lean` candidates per agent over `easy_set` 41, `cs_set` 10, `real_code` 5, `humaneval_set` 56, `security_6858` 22, `security_python` 6. Same basenames in all four runs. `inputs_manifest.json` holds paths and SHA-256s. |
| Golds | Frozen PTI-v0 precedence (legacy root first): every candidate resolved to a unique gold in `data/veribench_dataset/lean_src/veribench`; the newest root was never needed. |
| Judge configuration | `P1_BASELINE` prompt (paper appendix `app:judge-prompts`; `experiments/archive/02_neurips_reviews/utils/sensitivity_sweep.py`), reference = last theorem/lemma block of the gold (frozen Exp16 regex), candidate = full file, 3 repeats, mean over repeats. Chosen because among the three certified gpt-5.3-codex primaries it has the highest TI_var (0.9208 vs P4 0.9199, P8 0.8919; `results_exp30_tivar_v3_all_models/judge_trust_vector_codex_avg.csv`), the highest human Spearman on averaged labels (0.466), flip rate 0.0, and bug-ladder reversal rate 0.00. |
| Model actually used | **`gpt-5.6-terra`** via `codex exec -m gpt-5.6-terra -c model_reasoning_effort="low"` (codex-cli 0.155.1, ChatGPT subscription). `gpt-5.3-codex` is no longer offered by the CLI (`~/.codex/models_cache.json` lists gpt-6-astra, gpt-reserve, gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna, gpt-5.5, codex-auto-review; exp29 records the CLI rejecting the exact ID). gpt-5.6-terra is the regular-tier Codex model that agents-config Hard Rule 8 assigns to experiment workloads and the model on which `experiments/archive/29_proxy_validation` already ran the same prompts at the same effort. Codex `--json` output carries no served-model field and no `model:` header, so — exactly as exp29 documented — the model identity rests on the explicit `-m` flag and the CLI's rejection of unknown IDs; every raw record stores `model_requested`, `model_observed_header` (null) and the CLI usage block. |
| Execution | One `codex exec` call per (item, agent, repeat) cell, empty read-only temp workspace, `--ephemeral --ignore-user-config --ignore-rules --output-schema score_schema.json`; all `*_API_KEY` variables scrubbed from the child environment; parallelism 8; up to 3 attempts per cell. Raw response for every cell in `results/raw/<split>__<stem>__<agent>__r<k>.json`. Provider API spend: $0. |
| Aggregation | Per (item, agent): mean of the repeats; per split: mean over items; Avg: macro-average over the five table splits (Easy, CS, Real, HE, Sec = `security_6858`); ItemMean: mean over all 140 items. Scores are the prompt-native [0,1] floats (the Claude 3.7 judge emitted integers 0–10 divided by 10). 95% percentile bootstrap over items within split (10,000 draws, seed 0), paired across agents; pairwise agent differences and full-ordering frequencies from the same draws. |

## 3. Results
**Final state (STOPPED 2026-09-22 23:50 UTC, see Section 8):** 826 of the 1,680 quoted cells were completed from 846 CLI invocations (17 cells needed a retry; 0 failed cells; 12.76 M input / 111 k output tokens; mean 46 s per call under the subscription rate limit; $0 provider-API spend). Repeat layer 0 is complete for every (item, agent) pair (560/560); repeat coverage over the 560 pairs: {'1': 308, '2': 238, '3': 14} (pairs with 1 / 2 / 3 repeats). Numbers below are the `median_available_repeats` analysis of `results/ranking.json` (median over the repeats present), Sec = `security_6858`; `aggregate_ranking.py` regenerates them from `results/raw/`.

| Agent | Easy (41) | CS (10) | Real (5) | HE (56) | Sec (22) | **Avg** [95% CI] | ItemMean (140) [95% CI] |
|---|---|---|---|---|---|---|---|
| Baseline | 0.077 | 0.040 | 0.125 | 0.067 | 0.053 | **0.072** [0.050, 0.097] | 0.065 [0.053, 0.078] |
| DSPy ReAct | 0.184 | 0.065 | 0.450 | 0.119 | 0.072 | **0.178** [0.118, 0.241] | 0.136 [0.110, 0.165] |
| Trace+ | 0.083 | 0.075 | 0.220 | 0.127 | 0.094 | **0.120** [0.081, 0.163] | 0.105 [0.088, 0.123] |
| Trace++ | 0.145 | 0.060 | 0.190 | 0.118 | 0.081 | **0.119** [0.082, 0.159] | 0.114 [0.093, 0.137] |

Per-split 95% CIs: Baseline Easy [0.057, 0.098], CS [0.015, 0.070], Real [0.020, 0.235], HE [0.045, 0.091], Sec [0.030, 0.081]; DSPy ReAct Easy [0.120, 0.260], CS [0.030, 0.100], Real [0.180, 0.740], HE [0.093, 0.147], Sec [0.020, 0.149]; Trace+ Easy [0.050, 0.122], CS [0.040, 0.115], Real [0.050, 0.410], HE [0.107, 0.146], Sec [0.043, 0.159]; Trace++ Easy [0.102, 0.195], CS [0.025, 0.100], Real [0.040, 0.350], HE [0.095, 0.146], Sec [0.022, 0.175].

Pairwise Avg differences (paired item bootstrap, 10,000 draws): Baseline − DSPy ReAct = -0.105 [-0.179, -0.038] (p = 0.000); Baseline − Trace+ = -0.047 [-0.099, -0.008] (p = 0.008); Baseline − Trace++ = -0.046 [-0.098, +0.004] (p = 0.071); DSPy ReAct − Trace+ = +0.058 [-0.026, +0.147] (p = 0.197); DSPy ReAct − Trace++ = +0.059 [-0.020, +0.146] (p = 0.162); Trace+ − Trace++ = +0.001 [-0.035, +0.035] (p = 0.943).

Variants: with Sec = `security_6858` + `security_python`, Avg = Baseline 0.071, DSPy ReAct 0.178, Trace+ 0.118, Trace++ 0.116 (ordering DSPy ReAct > Trace+ > Trace++ > Baseline); ItemMean over all 140 items: Baseline 0.065, DSPy ReAct 0.136, Trace+ 0.105, Trace++ 0.114 (ordering DSPy ReAct > Trace++ > Trace+ > Baseline). Score distribution is near-binary at the low end (0.0 and 0.1 dominate; see caveat 3).

## 4. Ordering agreement with the Claude 3.7 table
Claude 3.7 table (Avg): DSPy ReAct 0.615 > Trace++ 0.588 > Trace+ 0.477 > Baseline 0.470.
This run (Avg): DSPy ReAct 0.178 > Trace+ 0.120 > Trace++ 0.119 > Baseline 0.072.

- Identical full ordering: **no** — the middle pair (Trace+ / Trace++) is swapped. Spearman over the four Avg values 0.800, Kendall tau 0.667.
- The endpoints agree and are supported: DSPy ReAct is first in 88% of bootstrap draws (top orderings: DSPy ReAct > Trace++ > Trace+ > Baseline 42.7%; DSPy ReAct > Trace+ > Trace++ > Baseline 41.6%; Trace+ > Trace++ > DSPy ReAct > Baseline 3.9%); Baseline is last in 96%; Baseline is below DSPy ReAct and Trace+ with CIs excluding zero.
- The Trace+ / Trace++ swap is not a disagreement the data can support either way: their difference is +0.001 with CI [-0.035, +0.035], and the Claude 3.7 table's own ordering of the two is not backed by any reported interval.
- Per split, no split reproduces the Claude 3.7 ordering exactly (per-split Spearman: Easy 0.80, CS -0.40, Real 0.80, HE 0.40, Sec 0.20); the smallest splits have 5–22 items and near-binary scores, so split-level orderings are noisy. Spearman over the 20 split cells is -0.05: the two judges agree on which agent is best and worst overall, not on split-level levels.

## 5. Property evidence for the substitute judge (fallback status)
The runbook fallback asks for the four property checks on the substitute model. The exp16-style suite (TI_var inputs) was **not run in this session** (quoted in `CKPT.md`: 864 calls; the ranking was prioritized). The property evidence that exists for exactly this configuration (`gpt-5.6-terra|P1_BASELINE`, effort low, 3 repeats, same CLI) is the PTI-v0 suite of `experiments/archive/29_proxy_validation` (`results/properties/property_table.csv`, `ladder_diagnostics.csv`):
- P_eqalpha (alpha-renaming invariance) = 0.939.
- Missing-specification ladders (P_ms probes, 63 ladders): mean Spearman −0.80, median −0.87, 98% of ladders with rho ≤ −0.5, mean adjacent reversal rate 0.016, 10 constant ladders.
- Bug ladders (P_bm probes, 49 ladders): 42 of 49 are constant (the judge returns the same median score at all five bug levels, typically 0.0 or 1.0), mean Spearman on the non-constant ladders −0.31; PTI-v0's zero-first geometric mean therefore reports P_bm = P_eq = 0 and PTI_v0 = 0 for this configuration.
- Human criterion (72-pair validation set, averaged labels): Spearman 0.338, 95% CI [0.093, 0.551] — the highest of the exp29 primaries.
So the substitute is alpha-invariant, strongly monotone under removed specifications, and positively human-aligned, but its low-effort scores are near-binary and insensitive to injected bugs on most PTI-v0 ladders. It is therefore *not* a certified configuration under either the paper's TI_var protocol (not computed) or PTI-v0 (zero), and the ranking below should be described as produced by "the certified prompt on the currently available Codex model", not by a certified judge, until the exp16-style suite is run (`CKPT.md` quote, resume instructions).

## 6. Caveats
1. **Model substitution.** The certified panel ran `gpt-5.3-codex`; that model is no longer served by the Codex CLI, so this run uses `gpt-5.6-terra` (regular-tier Codex, effort low). The prompt, reference preprocessing, repeat count (3) and median aggregation are the certified panel's; the model is not. The CLI's `--json` output does not name the served model, so the identity claim rests on the explicit `-m` flag and the CLI's rejection of unknown IDs (exp29 documented the same limitation).
2. **Certification status of the substitute.** The exp16-style property suite (TI_var inputs) for `gpt-5.6-terra|P1_BASELINE` has not been run (quoted at 864 calls in `CKPT.md`). The PTI-v0 evidence from exp29 (Section 5) shows alpha invariance and missing-spec monotonicity but near-binary, bug-insensitive scores on most PTI-v0 bug ladders (PTI_v0 = 0). The paper must not call this judge "certified" until the exp16-style suite is run and reported.
3. **Reference preprocessing.** The certified configuration compares the full candidate file against the *last theorem/lemma block* of the gold (frozen Exp16 regex). Candidates that formalize the program under different names or with different theorem statements are therefore scored near zero even when they are reasonable specifications; the absolute level of the scores (mostly 0.0–0.2) is not comparable to the Claude 3.7 table's 0.34–0.76 (a whole-file, 0–10 integer rubric), only the ordering is.
4. **Scale and rubric differences.** Claude 3.7 emitted integers 0–10 over five calls (mean); this judge emits [0,1] floats over three calls (median primary, mean secondary). Ties at 0.0 are frequent, which widens bootstrap intervals for the small splits (Real: 5 items, CS: 10 items).
5. **Which Trace++ run.** `~/veribench/CONTRIBUTING.md` pins the 2025-09-24 self-debug+self-improve run; it is byte-identical to the 2025-09-23 run (`diff -rq` empty), so the choice does not matter.
6. **Security split.** The table's Sec column is `security_6858` (22 candidates, 11 vulnerable/safe pairs); `security_python` (6 candidates) is scored too and reported as a variant, because the Claude 3.7 table does not say whether it was included (its Avg column is reproducible neither as the macro-average of its five printed columns nor as the item-weighted mean of them).
7. **Coverage.** See Section 3 for how many of the 1,680 quoted cells completed before this report was written; the resume command in `CKPT.md` finishes the rest and `aggregate_ranking.py` regenerates every number here.

## 7. Drafted text (not applied to the paper)
Section 5.4 replacement (two sentences, one per line; conditional on the wording in caveat 2 — do not call the judge "certified" until the exp16-style suite is run):

```
Re-scoring the same 140 outputs per agent with the Section~\ref{sec:validation-human-alignment} P1 prompt on the currently served Codex model (\texttt{gpt-5.6-terra}, median over repeated calls, 95\% item-bootstrap intervals) preserves the ends of the ranking: DSPy ReAct scores highest (\(0.178\), \([0.119, 0.240]\)) and plain prompting lowest (\(0.076\), \([0.050, 0.106]\)), while Trace+ (\(0.119\)) and Trace++ (\(0.112\)) are statistically indistinguishable (difference \(0.007\), \([-0.031, 0.042]\)).
Absolute scores are lower than in Table~\ref{tab:theorem_quality_table_split} because this judge compares each file against only the gold's final theorem block, so the two judges agree on the ordering of the best and worst agents, not on score levels.
```

Candidate abstract line (only if the exp16-style property suite for `gpt-5.6-terra|P1_BASELINE` is run and passes; otherwise omit):

```
The same prompt-level protocol, applied to a currently served Codex judge, reproduces the best and worst agents of an earlier, uncertified ranking of four \textsc{VeriBench} agents.
```

## 8. STOPPED 2026-09-22 (coordinator, relaying Brando)
**Reason:** the Baseline / DSPy ReAct / Trace+ / Trace++ ranking is a VeriBench (ICML 2025) result carried over from the DL4C version of this paper and is not relevant to the ICLR 2027 submission; Section 5.4 / Table 5 is being cut from the paper instead of reinforced. Repeat layers 1–2 and the exp16-style P1–P4 property suite for the substitute judge were therefore **not run** (the suite's 864-call quote in `CKPT.md` was never executed: `results/property_raw/` does not exist and `property_requests.json` holds only the locally built probe texts).
**What was actually run:** 826 ok cells (layer 0 complete 560/560; layer 1: 252; layer 2: 14) from 846 `codex exec` invocations on `gpt-5.6-terra` (effort low, P1_BASELINE), 0 failed cells, $0 provider-API spend; every raw response is in `results/raw/`. `results/ranking.json` and `results/ranking_table.md` were regenerated from exactly those cells after the stop.
**Consequence for Section 7:** the drafted replacement sentences are moot if the section is cut; they are left in place only as a record.
**Resume (only if ever revived; not planned):**
```bash
cd ~/cert-judge && python3 experiments/32_veribench_ranking_certified_judge/run_ranking_cli.py --workers 8            # finishes layers 1-2 (skips cached cells)
~/uv_envs/cert-judge/bin/python3 experiments/32_veribench_ranking_certified_judge/aggregate_ranking.py
~/uv_envs/cert-judge/bin/python3 experiments/32_veribench_ranking_certified_judge/run_property_suite_cli.py --workers 8   # 864-call P1-P4 suite (quote in CKPT.md)
~/uv_envs/cert-judge/bin/python3 experiments/32_veribench_ranking_certified_judge/compute_property_suite.py            # TI_var on the Section 5.3 panel scale (panel reproduced to 1e-9)
```

**TLDR-end:** [cj: exp32-certified-ranking] Layer 0 of the quoted run (826 cells, 846 CLI calls, $0 API) reproduces the Claude 3.7 ordering at its endpoints (DSPy ReAct first, Baseline last) with Trace+/Trace++ statistically tied; the experiment was stopped because Section 5.4 is being cut from the paper, the substitute judge was never property-certified under TI_var, and the resume commands above are the only path to finishing it.

**Snapshot:**
- `results/ranking.json` → `calls`: `{"ok_cells": 826, "expected_cells": 1680, "failed_cell_files": 0, "total_cli_invocations_including_retries": 846, "provider_api_spend_usd": 0.0}`; repeat coverage {'1': 308, '2': 238, '3': 14}
- `results/ranking_table.md`: `| DSPy ReAct | 0.184 | 0.065 | 0.450 | 0.119 | 0.072 | **0.178** [0.118, 0.241] |`
- `results/raw/`: 826 `*__r<k>.json` files, 0 `*.failed.json`; e.g. `easy_set__10_MyEvenSumParity__baseline__r0.json`: `"model_requested": "gpt-5.6-terra", "model_observed_header": null, "score": 0.0`
- `results/property_raw/`: absent (suite never started); `compute_property_suite.py` panel check: max |Δ ti_var_v3| = 9.2e-10 over the 8 Codex configs
- `inputs_manifest.json`: `"n_items": 140, "n_agents": 4, "n_candidate_rows": 560`