# Experiment 32 — VeriBench agent ranking under a certified-family judge

**TLDR-start:** [cj: exp32-certified-ranking] Re-scoring all 140 outputs of each of the four agents with the Section 5.3 P1_BASELINE prompt on the currently served Codex model (`gpt-5.6-terra`, `gpt-5.3-codex` is no longer offered by the CLI) via 611 subscription `codex exec` calls ($0 API) keeps DSPy ReAct on top (0.178, 95% CI [0.119, 0.240]) and Baseline at the bottom (0.076 [0.050, 0.106]); Trace+ (0.119) and Trace++ (0.112) swap places relative to the Claude 3.7 table but are statistically indistinguishable (diff 0.007, CI [−0.031, 0.042]). Only repeat layer 0 (560/1,680 cells) is complete; the run is still going and the substitute judge is not yet property-certified (Section 5).

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
Status at report time (2026-09-22 23:31 UTC): 591 of the 1,680 quoted cells are complete — repeat layer 0 is complete for every (item, agent) pair (560/560), plus 31 cells of layers 1–2 — from 611 CLI invocations (17 cells needed a retry; 0 failed cells; 8.81 M input / 79 k output tokens; mean 47 s per call under the subscription rate limit). The background run continues (`CKPT.md`); `aggregate_ranking.py` regenerates all numbers. Numbers below are the `median_available_repeats` analysis of `results/ranking.json` (median over the repeats present, which is the single repeat for 543 of 560 pairs), Sec = `security_6858`.

| Agent | Easy (41) | CS (10) | Real (5) | HE (56) | Sec (22) | **Avg** [95% CI] | ItemMean (140) [95% CI] |
|---|---|---|---|---|---|---|---|
| Baseline | 0.076 | 0.050 | 0.140 | 0.071 | 0.043 | **0.076** [0.050, 0.106] | 0.066 [0.053, 0.080] |
| DSPy ReAct | 0.189 | 0.060 | 0.450 | 0.112 | 0.080 | **0.178** [0.119, 0.240] | 0.136 [0.110, 0.166] |
| Trace+ | 0.078 | 0.070 | 0.220 | 0.135 | 0.091 | **0.119** [0.080, 0.162] | 0.106 [0.089, 0.124] |
| Trace++ | 0.123 | 0.060 | 0.180 | 0.112 | 0.084 | **0.112** [0.077, 0.149] | 0.105 [0.083, 0.130] |

Per-split 95% CIs: Baseline Easy [0.055, 0.098], CS [0.020, 0.080], Real [0.020, 0.280], HE [0.047, 0.096], Sec [0.018, 0.073]; DSPy ReAct [0.123, 0.267], [0.030, 0.090], [0.180, 0.750], [0.084, 0.141], [0.023, 0.159]; Trace+ [0.050, 0.107], [0.030, 0.110], [0.050, 0.410], [0.113, 0.158], [0.036, 0.157]; Trace++ [0.082, 0.172], [0.020, 0.100], [0.040, 0.320], [0.083, 0.145], [0.023, 0.180].

Pairwise Avg differences (paired item bootstrap, 10,000 draws): Baseline − DSPy ReAct = −0.102 [−0.177, −0.034] (p < 0.001); Baseline − Trace+ = −0.043 [−0.097, −0.001] (p = 0.040); Baseline − Trace++ = −0.036 [−0.087, +0.017] (p = 0.19); DSPy ReAct − Trace+ = +0.059 [−0.022, +0.146] (p = 0.18); DSPy ReAct − Trace++ = +0.066 [−0.008, +0.149] (p = 0.089); Trace+ − Trace++ = +0.007 [−0.031, +0.042] (p = 0.70).

Variants: with Sec = `security_6858` + `security_python`, Avg = DSPy ReAct 0.178, Trace+ 0.117, Trace++ 0.109, Baseline 0.075 (same ordering); ItemMean over all 140 items gives the same ordering (DSPy ReAct 0.136 > Trace+ 0.106 > Trace++ 0.105 > Baseline 0.066). Score distribution is near-binary at the low end (0.0 and 0.1 dominate; see caveat 3).

## 4. Ordering agreement with the Claude 3.7 table
Claude 3.7 table (Avg): DSPy ReAct 0.615 > Trace++ 0.588 > Trace+ 0.477 > Baseline 0.470.
This run (Avg): DSPy ReAct 0.178 > Trace+ 0.119 > Trace++ 0.112 > Baseline 0.076.

- Identical full ordering: **no** — the middle pair is swapped. Spearman over the four Avg values 0.800, Kendall tau 0.667.
- The endpoints agree and are supported: DSPy ReAct is first in 88% of bootstrap draws (DSPy > Trace+ > Trace++ > Baseline 47.9%, DSPy > Trace++ > Trace+ > Baseline 32.5%), Baseline is last in ~92% of draws, and Baseline is below DSPy ReAct and Trace+ with CIs excluding zero.
- The Trace+ / Trace++ swap is not a disagreement the data can support either way: their difference is 0.007 with CI [−0.031, +0.042] here, and the Claude 3.7 table's own ordering of the two is not backed by any reported interval.
- Per split, no split reproduces the Claude 3.7 ordering exactly (per-split Spearman: Easy 0.80, Real 0.80, HE 0.32, Sec 0.20, CS −0.32); the five smallest splits have 5–22 items and near-binary scores, so split-level orderings are noisy. Spearman over the 20 split cells is −0.07, i.e. the two judges agree on which agent is best and worst overall, not on split-level levels.

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

**TLDR-end:** [cj: exp32-certified-ranking] With the certified P1 prompt on `gpt-5.6-terra` (repeat layer 0 complete, 560 cells; 611 CLI calls; $0 API) the agent ranking keeps DSPy ReAct first (0.178 [0.119, 0.240]) and Baseline last (0.076 [0.050, 0.106]), the middle pair Trace+/Trace++ is a statistical tie (0.119 vs 0.112), so the Claude 3.7 ordering is reproduced at its endpoints but not in full; the substitute model is not yet property-certified and the paper text must say so.

**Snapshot:** 
- `results/ranking_table.md` (regenerated 23:31 UTC): `| DSPy ReAct | 0.189 | 0.060 | 0.450 | 0.112 | 0.080 | **0.178** [0.119, 0.240] | 0.136 [0.110, 0.166] |`
- `results/ranking.json` → `calls`: `{"ok_cells": 591, "expected_cells": 1680, "failed_cell_files": 0, "total_cli_invocations_including_retries": 611, "provider_api_spend_usd": 0.0}`
- `results/raw/easy_set__10_MyEvenSumParity__baseline__r0.json`: `"model_requested": "gpt-5.6-terra", "model_observed_header": null, "score": 0.0, "usage": {"input_tokens": 13806, ..., "output_tokens": 149}`
- `inputs_manifest.json`: `"n_items": 140, "n_agents": 4, "n_candidate_rows": 560`, all `gold_resolution` values in `data/veribench_dataset/lean_src/veribench`
- `judge_config.json`: `"certified_configuration_requested": "gpt-5.3-codex|P1_BASELINE"`, `"model_requested_by_cli_flag": "gpt-5.6-terra"`, `"reasoning_effort": "low"`, `"n_repeats": 3`
