# Experiment 64: Nov 6 confirmatory test of the frozen cert-judge candidates on fresh set-N human ratings (pre-registration)

**TLDR:** Four things are frozen before any set-N rating is read: the 11 trained Qwen3-8B judges (5 human-mix, 6 teacher-only), the Qwen3.6-27B checklist+thinking judge, and the C_ms_gold index. One script (`code/confirm64.py`) scores them once on the new ratings. Success and null rules are below; nothing is refit, reselected or re-thresholded afterwards.

**Status:** written 2026-10-31 (PT) before any set-N rating was read by the author of this protocol (the A1 sheet had 0 of 125 ratings when last checked; no rater sheet was opened). Anything later is a dated addendum, never an edit of sections 1 to 6. CPU only, no paid API, no model calls in this experiment's folder as written; the model calls that produce judge outputs on set N (section 4) come later and are free-hardware only.

## 1. What is tested
Set N = 25 VeriBench task folders x 5 agent files = 125 files (experiment 102, human round; closes Fri 2026-11-06). These are new units: none is among the 30 old E63 test items (their ids are in `FREEZE.json`, `old_test_items`; the script stops if a rating row carries one). The human score of a file = mean of its qualified raters' scores (needs >= 2 qualified ratings; A1 = Brando is a sensitivity rater, never part of the primary mean).
This supersedes the older line in E63's PROTOCOL ("75 frontier-output ratings due 11-06"): the round is set N.

## 2. Frozen candidates (hashes in `FREEZE.json`, adapters re-verified on SNAP with `sha256sum -c`, `results/adapter_sha256_snap_2026-10-31.txt`)
- **A. Human-mix SFT, 5 seeds** (`sft_q3_8b_hm_s0..s4`, Qwen3-8B + LoRA r16, epochs picked on val in E63: s0 ep3, s1 ep4, s2 ep4, s3 ep4, s4 ep3).
- **B. Teacher-only SFT, 6 seeds** (`sft_q3_8b_s0..s5`, epochs s0 ep4, s1 ep2, s2 ep3, s3 ep2, s4 ep2, s5 ep3).
- **C. Qwen3.6-27B-FP8, checklist prompt, thinking on, `stated` score** (veribench commit 6d838cfb, `docs/judge-validation`). The max-min pick is not frozen.
- **D. Index `C_ms_gold`** with its E58 values on the 13 judges x 9 prompts (units in `ANALYSIS.json`, sha in `FREEZE.json`).
Not candidates here: RL arm, prompt-optimization arm, shuffled control, base zero-shot (descriptive only, may be run, never gate anything). The Qwen3-14B human-mix pilot (AT-2179) is exploratory and outside this test unless it is frozen by an addendum before the ratings are read.

## 3. Hypotheses, primary metric, null
Metric for A, B, C: Spearman between the judge's expected 0-5 score (EV) and the human score over the evaluated items, 95% bootstrap CI resampling the 25 task folders (10,000 draws, seed 1106). A and B are reported as the mean over seeds, the CI from the folder resamples of the seed-mean.
- **Null (A and C):** true rho <= 0.60 (the best label-free single judge in E59/E63).
- **Success tiers for A and for C separately:**
  - PASS: mean rho >= 0.75 and CI lower bound > 0.45 (the project bar).
  - PARTIAL: mean rho >= 0.60 and CI lower bound > 0.
  - FAIL: anything else. A FAIL is reported as a failed replication, not repaired.
- **Human-mix beats teacher-only (secondary):** A minus B, paired on the same folder resamples; yes if the CI lower bound > 0.
- **Index (D):** the E39/E58 gate, unchanged: Spearman across units between C_ms_gold and the unit's judge-vs-human Spearman on set N >= 0.45 with permutation p < 0.05, both plain and model-clustered (frozen `analyze58.gate_block`, 10,000 draws). PASS needs both; units need >= 90% of items scored (E58 rule). Fewer than 80 units or 10 models: NOT_EVALUABLE, not FAIL. Leave-one-model-out is descriptive only. TVD-MI is exploratory and never part of the verdict.
- **Not evaluable:** fewer than 60 primary items or 12 folders for A/B/C: reported as NOT_EVALUABLE; the sensitivity analysis on A1 (all rated items) is still reported next to it. No rule is relaxed after seeing data.
- **Descriptive only:** rater-pair Spearman (human ceiling), per-seed rho, per-agent rho, seed SD. These carry no verdict.

## 4. Procedure (one pass, no refit)
1. After the round closes, export the ratings once to `setN_ratings.csv` with columns `item_id, folder, agent, rater, score, qualified` (the sealed set-N key maps files to folders and agents). Raw export is committed with its sha256 beside the result.
2. Each frozen judge scores every set-N file once: same prompt template as in `FREEZE.json` (E39 H2 with the one-digit instruction for A and B; the veribench judge-validation prompt for C), deterministic EV, no sampling-dependent selection, no prompt or adapter edits after seeing any set-N rating. Output `judges/<candidate>.json` = `{"ev": {item_id: score}}`; for D, `units_scores.json` = `{"<model>|<prompt>": {item_id: score}}` for the 13 x 9 units. Failed or truncated judge calls are counted per judge and reported; an item missing for a judge drops for all judges of that analysis.
3. `confirm64.py --ratings setN_ratings.csv --judges judges --units units_scores.json --freeze FREEZE.json --out results/` runs once. Its sha256 and the ratings' sha256 go into `CONFIRMATORY_RESULT.json`. A rerun is allowed only for a crash and is logged.
4. Result written into this folder's README as a dated addendum, takeaway first. No other number is called a result.

## 5. Rules that keep it clean
- No set-N rating is read, counted or plotted before the freeze commit of this folder exists on main. Brando's own A1 ratings are not shown to any judge, prompt, or selection step.
- No test reads on the 30 old test items in E64 (no re-scoring, selection or refit on them).
- No model, adapter, prompt, epoch, seed set, threshold or analysis code changes after this commit. Changes need a new numbered experiment, not an edit.
- CPU for analysis; judge scoring on free hardware only (mercury/skampere GPUs, FarmShare, Sherlock); no paid API, no Valkyrie.
- Post hoc analyses (TVD-MI covariate, leave-one-out, per-agent, ablations) are labelled exploratory.

## 6. What this does and does not show
A pass says the judges track the fresh expert ratings on set N at the stated bar, with folder-clustered uncertainty from 25 folders. It does not show the judges work on other task families, other raters, or other agents. E63 was one split of 30 items from 10 tasks (CIs 0.4 to 0.6 wide); this is the first fresh-unit replication.

## 7. Open before the ratings arrive (not part of the frozen rules)
- Prompt rendering of set-N files into the frozen H2 and checklist templates (mechanical; code to be added as `code/render_setN.py` with its sha256 in a pre-ratings addendum).
- Judge compute plan for A, B, C (11 + 1 judges x 125 files) and D (117 units x 125 files) on free GPUs.
- Brando's confirmation that the set-N rating rubric is the same 0-5 FSC criterion the E39 criterion items were rated on (assumed here).
