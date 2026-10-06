# Run the cached score judge selection utility study

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/cc.md>

**TLDR:** Implement and finish the exploratory saved-score study in PROTOCOL.md, including deterministic verification, all declared views, machine-readable receipts and RESULTS_selection_utility.md. Determine whether the frozen proxy improves selection over a fixed human-mirror rubric and random choice; report effect sizes and uncertainty without inventing a success threshold. Publish the complete verified result through a pull request, merge it, and archive this newly completed study. Do not run model inference, change human labels, edit old experiments or revise the paper.

SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).

## Ownership and constraints

You own only the new experiment, its active/archive inventory rows, and any required retirement-map row. Current owned checkout: /lfs/skampere1/0/brando9/cert-judge_e44. Branch: codex/cj-e44-selection-utility. Session: cj-e44-selection-utility. Master is Codex chat 01a10dc2-f9fb-7d82-bdf2-c0f2c75779a9; signal through committed checkpoint and final response, not another chat.

Read ~/agents-config/INDEX_RULES.md and the matching statistics/research/publication sections. The new PROTOCOL.md is the analysis contract; record justified implementation deviations, never silently retune. This dataset and some correlations have already been inspected, so this is exploratory. Finish within this task; do not stop after planning, coding, testing a toy case or launching the analysis.

Model inference budget is exactly zero: no judge calls, no new raters, no credential-loading provider script. Use existing installed Python/NumPy/SciPy on skampere1. No external messages, email, collaboration requests or changes to automations. The master supplies the completion report in chat. Do not start any model reviewers.

## Inputs and fail-closed reconstruction

The current checkout contains committed source experiment39 results. For private/source availability only, read the existing owned-study copies:
- /lfs/skampere1/0/brando9/cert-judge_e39
- /lfs/skampere1/0/brando9/veribench_e39/experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs

Copy the small fingerprint-verified item metadata file into this study's inputs/ for reproducibility and record provenance. Human ratings already appear in these private repositories; preserve them byte-for-byte. Never copy credentials or unrelated private material.

Expected items.jsonl SHA-256: ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c. Expected items75/tasks25; train30, validation15, test30. Criterion subsets: original45/15tasks; no-placeholder36/12; no-ambiguity36/12; neither27/9.

Read results/panel.json, harvest/*.json, units_train_val.json, units_test.json, probe_manifest.json, SELECTION.json, FINALISTS.json and TEST_RECEIPT.json from source experiment39. Unit exports contain42 open units (38 model configurations plus4 controls) and18 test units. Practical study excludes controls.

Harvest criterion cells have kind=crit, key/item joins to item, task, level0, repeat, status, score. Accept only measured/deterministic nonnull normalized score; never divide score by rubric scale again. Aggregate median available repeats, matching source analysis_lib.Scores and criterion; retain missing-repeat counts. Reproduce stored per-judge heldout Spearman/Pearson/Kendall and coverage exactly before utility analysis. Values may be undefined for constant scores; preserve null.

Read source analysis_lib.py for frozen numerics, but make the new script robust to archive moves (locate repo root by pyproject.toml/.git and source study by active/archive alternatives, do not use hard-coded parent counts). No inference imports. A compact exported criterion matrix plus manifest is acceptable, but must be deterministically reconstructed from source harvests with hashes.

## Implement and run

Implement a transparent deterministic script and meaningful tests under scripts/. Follow every pool, selector, missingness, tie, shared-support and bootstrap rule in PROTOCOL.md. Five selectors, three main candidate pools, five criterion views, proxy-eligible sensitivity, leave-one-base-model-out and single-call/agent-only diagnostics. Report all unavailable comparisons instead of dropping them.

Vectorize/cache bootstrap correlation matrices where sensible; 10,000 task-cluster draws should be bounded processor work. Record valid draws. Do not resample individual candidate generations independently. Primary uncertainty conditions on the fixed candidate pool and fixed selected methods; no independence claim for models. The transferred-prompt baseline is selected only from judge-train/validation; document chosen prompt, candidates and support before evaluating utility.

Keep the index frozen even when changing criterion items. A missing proxy excludes that configuration from that selector only; it remains in random, H2 and oracle. H2 is uniformly selected individual configuration, never a newly evaluated ensemble. Retain exact ties uniformly. Show source per-judge criteria versus common-item criteria so the reader can see support effects. Report proxy margins: near-tied maximum rankings can be unstable even when source scores are not exactly tied.

Produce:
- source and execution manifests, compact candidate/selector/comparison tables, summary receipt;
- RESULTS_selection_utility.md with the practical decision first, interpretable primary table, sensitivity summaries, missingness and limits;
- live results.md and CKPT_selection_utility.md updates with timestamps, real commands, source revision, actual executor/model/effort/permissions and verification.

Tests should independently exercise aggregation, invalid-status filtering, coverage, tie averaging, missing-proxy oracle retention, shared-support threshold, grouped task resampling, undefined correlations, prompt selection not reading test rows, and original frozen-statistic reconstruction. Use SciPy as independent statistical cross-check where appropriate. Run the final declared analysis on real cached data, not only tests.

## Progress and publication

A long or dispatched run keeps results.md live in the repo — not a report at the end. The canonical ledger is experiments/archive/44_cached_score_judge_selection_utility/results.md; update it at meaningful milestones, commit exact owned files and push, with Last updated and phase states. The dispatcher owns mirroring if transport prevents your push.

Before each commit inspect exact staged filenames and full staged diff for credentials or unrelated changes; never git add -A or sweep shared work. Run git diff --check, relevant tests and python3 py_src/cert_judge/experiment_layout.py --check. Compare input hashes before/after; frozen source inputs must not change.

When finished, git mv this new study into experiments/archive/44_cached_score_judge_selection_utility in the verdict commit, remove its active inventory row, add retired mapping/archive index row and completed row in experiments/README.md. Do not archive any older study. Ensure scripts/reproduction commands still work after this move and external inputs are locatable. Change document links to intended main archive paths at finalization. Preserve the protocol's historical identity and numerical records.

Push the branch and create a concise pull request with exact change purpose, verification commands and report/checkpoint links using gh --body-file. Fetch origin/main, integrate if needed in this owned checkout, preserve backup before rebase, inspect range-diff and owned-file diff, rerun affected checks, then head-match merge immediately after verification. No force pushes to main. If rebasing a published branch, use explicit force-with-lease for its recorded old tip only. Preserve other owners' changes.

Confirm the pull request is MERGED and its actual merge commit. Record LANDED <commit> <url> <timestamp> in the archived checkpoint; publish the small receipt via an allowed docs-only change. Do not call a queued merge complete. Do not delete this active worktree. Final response gives measured result, uncertainty, exact report path, pull request URL and any remaining limitation. Write private/DONE only after verified completion; on failure preserve private/BLOCKED with concise cause and exact continuation.

TL;DR: Execute the frozen exploratory cached-score analysis without inference, verify it, and publish one complete selection-utility report and reproducible artifacts.


## Master implementation checks (10-05-2026, before publication)

The supervising master inspected the first implementation draft. These completion checks implement the existing protocol; do not change selectors/outcomes:

- score_diagnostics must use the CURRENT pool/view common mask, not all 75 entries in item_map. Populate both judge/human means, missing repeat counts and raw-repeat sample standard deviations; one repeat means unavailable SD. Do not leave placeholder null means where data exist.
- Report selector expected Pearson/Kendall alongside Spearman, selection margins, exact ties and individual member utilities. Prompt selection table needs contributing train/validation counts/configurations.
- Reproduce original pooled test association against TEST_RECEIPT as well as each judge. Assert null equality, denominators, duplicate configuration/item-cell keys, item-task joins and frozen source hashes. Fingerprint required source panel/units/probe/selection/test files and compare before/after.
- Make EXP archive-safe using script location. Reproduction cannot depend only on private e39 harvests: prefer committed sources when available and export a compact criterion/raw-repeat matrix with source hashes if harvests are private, retaining deterministic reconstruction support.
- Same-eligible and model/harness sensitivities need statuses, counts, selected members and paired differences; retain unavailable rows.
- Tests must catch diagnostics mask error and raw-repeat SD/counts, numeric reconstruction, task multiplicity, fixed selector weights, strict oracle and train/validation prompt isolation. Run final real 10,000 draws after fixes and fulfill every protocol field before merge.

Master appended these notes while worker owned scripts/results; master did not modify implementation or results.

Additional report check: escape vertical bars in configuration IDs inside Markdown tables so columns render correctly; lead with the measured practical verdict and paired interval, not a conditional template. The protocol asks to recompute all correlations in task draws: include Pearson/Kendall expected values and their uncertainty where computed, explicitly marking any genuinely uncomputed intervals. Preserve the original registered verdict and call this follow-up exploratory.

Follow-up on draft diagnostics (master, 10-05-2026): available_repeat_counts currently sums all raw_repeats[c].values(), so it still includes off-mask items. Sum only k in the current mask. missing_repeat_counts currently counts items with zero repeats, which is always zero on the common mask and misses partial coverage. Count missing declared repeat slots (expected 3 per criterion item; verify source) and separately list per-item repeat counts. Add assertions to the diagnostics test for off-mask exclusion and a one-of-three-repeat item contributing two missing slots. Also verify and report before/after frozen-source hash equality, not just final hashes.
