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

### Addendum 2026-10-31 (pre-ratings): prompt rendering and compute plan
Written before any set-N rating was read or opened; no model call was made. Sections 1 to 6 are unchanged.

**Rendering code.** `code/render_setN.py` (sha256 `99b9b51b33863e04b15331982a817a2fb077d18f493d7f2c337c3b4d2f1ac442`) renders the 125 set-N files (packet v7, `FILES.sha256` digest `c54b194093b3e42f7f33aaf32f14936277b9c9e87ca94e35b6cc0aca30047ca8`, all 179 listed files verified) into:
- the E39 `H2` prompt with E63's one-digit answer instruction (judges A and B), via experiment 100's own `prompts.render`, from the VeriBench commit E39 rendered from (`d7d36c319dc7`, skampere1 `veribench_e39`; later commits edited the reference files and would change the demos' gold text);
- the judge-validation `checklist` prompt (judge C), via `jv.prompts.render` at VeriBench `e9530795796e` (`docs/judge-validation/code` is unchanged since the frozen `6d838cfb`).
Check (`render_setN.py check`, output in `results/render_setN_check_2026-10-31.txt`): the H2 renderer reproduces the stored E63 prompts of the 30 old test items byte for byte, and the pack's own `pid` (sha256 of system + NUL + user) matches on all 30, 30/30. The checklist renderer matches `jv`'s own loader on the same 30 items, 30/30; no stored checklist prompts exist, so that check is against the code, not against stored bytes. A second `render` run is byte-identical. The prompts are private; `results/PROMPTS_MANIFEST.json` holds the sha256 of every prompt (125 per family), of the three prompt files and of the packet digest. Item ids are the blinded file stems `N01a` to `N25e` (folder = the stem's first three characters); the sealed key maps them to agents when the ratings are exported.

**Rubric.** The packet's `human_judgements_prompt.md` (sha256 `b29e9cafdab10463d29b6ffdbb4700b46ead0e6023278b9b7b69d9ef0ab350af`) is byte-identical to the file whose text the E39 H2 prompt embeds as the rater instructions. What stays assumed is that the raters followed it as the criterion raters did; Brando's confirmation remains open.

**Defaults taken (changeable until the ratings are read, not afterwards).**
1. Length. Median H2 prompt 13.8k tokens, longest 44.0k (E63's longest was 18.5k). 18 of 125 exceed 24k, 7 exceed 32.8k, 2 exceed 40,960 (Qwen3-8B's native window; the two longest files by size are N17a and N17e, final ids from the tokenizer at scoring). E63's `sft_lora.py` cuts to its last 24,000 tokens by default (`--maxtok`), which would silently drop the start of the instructions: set-N scoring must pass `--maxtok 50000`. A and B score every prompt up to 40,960 tokens untruncated; a prompt over 40,960 is not scored for A or B and, by section 4, drops for all judges (125 becomes 123, above the 60-item minimum). No truncation, no rope scaling.
2. Judge C. The frozen config (`checklist__think`) samples at temperature 0.6 with thinking, one sample, 10,000 output tokens; section 4's "deterministic" cannot hold for it. Default: run exactly that config once, fixed seed 1106, one sample per file, log the finish reason per call. Only the engine's context allowance changes, `max_model_len` 32768 to 52000 (the longest checklist prompt is 40.3k tokens, 3 exceed 32.8k).
3. A and B engine. Use E63's route unchanged (`sft_lora.py --eval_pack` on `pack_setN.jsonl`, sha256 `c418002410d12894547c0c8f08f8bb5a1bd81cc9ea2e836f5123e4038a886290`, same Qwen3-8B base and frozen adapters, EV from the first-token digit distribution). A vLLM LoRA route would be faster but is a different numeric path; it is not used unless it first matches the HF route on E63 validation prompts (not the old test items, which section 5 closes).

**Compute plan (free hardware only; estimates, not measurements).**
- A and B: 11 adapters x 125 prompts = 2.03M prompt tokens each. E63's HF route scored 0.90M tokens in about 10 min on 3 balanced GPUs, so about 25 min per adapter, about 4.6 h on 3 GPUs for all 11 (about 14 GPU-h); three 3-GPU lanes finish in about 1.7 h. Memory at 44k tokens is untested: first run the longest prompt once with the base model on one lane before queueing the 11. This needs only the prompt file, no rating.
- C: 1.57M prompt tokens plus up to 10k thinking tokens per file; about 1 to 2 h on one 80 GB GPU (Qwen3.6-27B-FP8; skampere1 or an L40S/H100 on FarmShare/Sherlock).
- D: 117 units (13 judges x 9 prompts) x 125 files = 14,625 calls. Scaling E58's `GPU_HOURS.md` by cells (1,125 vs 9,862 per model), about 10 to 16 GPU-h (decode dominates; longer set-N prompts add prefill). The renderer for the other eight prompt families (H0, H1, D0, R4, P1, P4, P8, LEX) is not part of this addendum; it follows `e39.render_cells` and needs its own check against E58's rebuilt prompts. Qwen3-family units run in a 40,960 window, so their over-context cells are unscored under E58's rule; a unit needs at least 90% of items scored.
- Hosts: skampere1/2 GPUs were mostly busy on 2026-10-31 08:40 (other jobs of ours); schedule A/B and C into free GPUs or FarmShare/Sherlock slots well before Nov 6 so a failed lane can rerun.

### Addendum 2026-10-31 (pre-ratings, second): the nine E39 prompt families for the 117 E58 units
Written before any set-N rating was read or opened; no model call was made. Sections 1 to 6 and the first addendum are unchanged.

**Code.** `code/render_setN_families.py` (sha256 `4b555a75cdce9bfaf76d9ea65d0345319bbb0a490785868bb22088abcc22b7a2`) renders the 125 set-N files into the nine E39 families D0, R4, H0, H1, H2, P1, P4, P8, LEX with the branch E58's `rebuild_prompts.render_cells` uses (experiment 100's `prompts.render` for the VeriBench families, E39's `legacy.render` with the gold's last theorem block for the P and LEX families, the same `Unmeasured` handling). Prompt hash = E39's `sha256(system + "\n\n" + user)`. Source checkout: the VeriBench clone E58 rebuilt from (`9a857c3dcd7c640216128d05d5f7f29ca2ddc7be`; its `items.jsonl` sha256 `ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c` equals `REBUILD_REPORT.json`'s, file sha256 `636cd9af...`); packet v7, `FILES.sha256` digest `c54b1940...` as in the first addendum.
- **Check against E58.** `render_setN_families.py check` renders all 75 E39 criterion items in all nine families (675 prompts) and compares status and prompt sha256 with (a) E39's committed `results/cells/*__<prompt>.json`, the hashes E58's rebuild matched 4689/4689 before any judge call, and (b) E58's own `render_cells` run on the same items: 675/675 identical in both (including the 9 D0 `unmeasured_extraction` statuses), `results/render_setN_families_check_2026-10-31.txt`. The check runs on the criterion items (kind `crit`, level 0), the only E39 cells that are plain candidate files; probe-built cells (ladders, blanks) need E39's probe builder and are not set-N inputs.
- **H2 cross-check.** The H2 family here keeps E39's JSON answer instruction (the E58 route). Its text up to that instruction equals `render_setN.py`'s H2 prompt (the one-digit variant for judges A and B, built from the d7d36c31 checkout) on 125/125 files, so both routes read the same reference, demos and candidate bytes. Judges A and B keep the one-digit H2 of the first addendum; unit H2 in D uses the E58 H2.
- **Determinism.** Two `render` runs: `FAMILIES_MANIFEST.json` and all nine `families/<P>.jsonl.gz` byte-identical. The prompts are private (not committed); `results/FAMILIES_MANIFEST.json` (sha256 `d76fa679928607b8682fb699523fce2caaea3a3388f9c0dd6bd6ce075730325c`) holds the sha256 of each family file and of every prompt (9 x 125) and the status counts.
- **Statuses.** 1,121 of 1,125 cells render; 4 are `unmeasured_extraction` under D0 (N09d: `open ... in command` needs explicit extraction support; N12c, N17a, N25b: tactic-generated statement type needs Lean elaboration), no `deterministic` cells. E39's criterion items had 9 of 225 D0 cells in this status.

**Context rules and run plan (E58 rules unchanged: chat template, `max_tokens = min(prompt max_tokens, max_model_len - prompt tokens)`, below 1,024 is `unmeasured_over_context`, never truncated).** `render_setN_families.py plan` tokenizes every prompt through each of the 13 models' own chat template (tokenizer files only); `results/RUN_PLAN_setN_E58_2026-10-31.json` (sha256 `28932e2bb2d28174cc09b3e8614acc0404613bf6b0b01cd42928b20c13696a6c`) has counts and token totals per model and prompt, no text.
- Calls: 14,323 of 14,625 (117 units x 125): 302 cells are not called (4 x 13 D0 extraction cells = 52, plus 250 over context).
- Longest prompt, tokens: D0 198,547 (median 17,581, the D0 user message carries all public obligations), H2 44,130 (median 13,897), H1 40,310, H0 40,043, R4 39,960, P1/P4/P8/LEX about 20,000 (median about 5,850).
- Over context in the four Qwen3 models (40,960 window): D0 26, H2 2 (N17a, N17e), H1 2, H0 1, R4 1, none in P1 to LEX. In the 65,536-window models: D0 only, 13 (Llama 3.1/3.3, OLMo 3) or 14 (Qwen3.6, Gemma 3, gpt-oss).
- **The 90% rule (section 3, E58): D0 fails it for all 13 models** (scored share 0.76 for the four Qwen3, 0.856 to 0.864 for the other nine), so the 13 D0 units drop from the index analysis, leaving 104 units over 13 models, above the NOT_EVALUABLE floor (80 units, 10 models). Every other unit scores at least 98.4% of the 125 files. Default taken (changeable until ratings are read): apply E58's rule as frozen, no D0 truncation or windowing, and report the 13 dropped D0 units by name. Whether to keep D0 by raising `max_model_len` for the models that allow it is a protocol change and is not made here.
- **Compute (estimate, E58 `GPU_HOURS.md` assumed throughputs and mean output lengths applied to these call and token counts; not measured):** about 13 GPU-hours for all 14,323 calls (one replica per model; 2-GPU models counted twice): 12 to 13.5 M prompt tokens per model; slowest, OLMo 3 32B Think 3.0 GPU-h and Qwen3.6-27B and Qwen3-32B about 3 GPU-h each. This is the decode-dominated assumption E58's table used; E58's own runs were slower than assumed on shared A4000s, so plan for twice this. Run order as in E58 (`GPU_HOURS.md`): smoke on the longest non-D0 prompt (H2 N17b, 40k tokens) per model first.
- D is independent of the A, B and C runs; it needs the E58 package (`scripts/judge_vllm.py`) pointed at the set-N family files, which is one more small driver and is not written here.
