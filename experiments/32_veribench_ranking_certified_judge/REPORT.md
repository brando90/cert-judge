# Experiment 32 — VeriBench agent ranking under a certified-family judge

**TLDR-start:** [cj: exp32-certified-ranking] PENDING_TLDR_START

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
PENDING_RESULTS

## 4. Ordering agreement with the Claude 3.7 table
PENDING_AGREEMENT

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
PENDING_DRAFT

**TLDR-end:** [cj: exp32-certified-ranking] PENDING_TLDR_END

**Snapshot:** PENDING_SNAPSHOT
