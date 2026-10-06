# Cached score judge selection utility checkpoint

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/CKPT_selection_utility.md>

**TLDR:** Completed, verified and merged the exploratory cached-score selection-utility study; no judge-inference calls or new labels were needed.

Created: 10-05-2026
Last updated: 10-05-2026 23:20 PDT

- Master chat: `01a10dc2-f9fb-7d82-bdf2-c0f2c75779a9`; local owned checkout: `/Users/brandomiranda/.codex/worktrees/judge-selection-utility/cert-judge`.
- Branch: `codex/cj-e44-selection-utility`; planned remote checkout `/lfs/skampere1/0/brando9/cert-judge_e44`; session `cj-e44-selection-utility`.
- Source revision: `fc73f78696d53551cd57f13094ec6f73fbb1c234`.
- Current phase: COMPLETE; results merged and archived.
- Next command: none; this study is complete.
- Paid inference budget: zero. Existing saved scores only; processor analysis on skampere1.
- Codex account usage observed at dispatch preparation: 34% of weekly allowance used, 66% remaining, ordinary use allowed; observed on the local desktop account; remote allowance was not established by this reading (see recovery correction below). One regular execution worker plus master, no model reviewer. Conservative execution estimate 30k–80k tokens with finishing capacity reserved; no purchased credits or new charges.
- Planned execution worker: Codex CLI gpt-5.6-terra/high (supported in target cached catalog), approved ChatGPT login. Scientific interpretation remains with master. Actual model/effort and full-access mode must be recorded from launch receipt.
- Recovery: master owns supervised bounded recovery, preserving any healthy child. No automatic repeated model dispatch; at most one justified continuation on the same client, then evaluate explicit blocker/eligible fallback. Wrapper records exit and actual output. This is supervised, not a claim of reboot-safe autonomous failover.
- Permissions: `--dangerously-bypass-approvals-and-sandbox`; preserve task scope and all unrelated owners' work.
- No changes to older experiments, human labels, reference artifacts or paper. No messages to collaborators.

- Preflight: skampere1 Codex0.154.0 and authenticated ChatGPT login verified; Python3.12.3/NumPy2.2.6/SciPy1.17.1 available. Health check flagged unused Claude executable and low shared-filesystem percentage free; route checkout/results to node-local storage with about11TB free, avoiding that write dependency. No repair or deletion of shared resources.

## Corrected ownership receipt (10-05-2026 22:37 PDT)

- The supervising master corrected the earlier interpretation: this Codex session is the sole implementation worker in `/lfs/skampere1/0/brando9/cert-judge_e44`; PID 716290/716359 was this session's own `codex exec`, not a separate worker.
- Interrupted attempt: I read the protocol and source inventory, then mistakenly polled `private/worker_final.txt` and the above PID as if it were another worker. The master interrupted that self-monitoring. No implementation had been written, no inference/reviewer/provider call occurred, and no source input was modified.
- Actual continuation executor: Codex CLI `gpt-5.6-terra`, reasoning effort `high`, host `skampere1`, full-access launch mode `codex exec --dangerously-bypass-approvals-and-sandbox`; this is the one justified continuation. There will be no further model launch or delegation.
- Current phase: direct implementation and real cached-score analysis. Next command: write `scripts/analyze_selection_utility.py` and `scripts/test_selection_utility.py`, then execute the declared 10,000 task-cluster-draw analysis.

## Completion checkpoint (10-05-2026 22:56 PDT)

- Completed the sole-worker continuation: 8 offline deterministic tests passed; the final real run used seed 44 and 10,000 task-cluster draws for every available pool/view comparison. `inputs/items.jsonl` remained SHA-256 `ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c` before and after.
- Reconstruction passed for every test judge's frozen original-mask Spearman, Pearson, and Kendall values, and the pooled `C_ms_gold` TEST_RECEIPT association exactly reproduced Spearman 0.5577632121, Pearson 0.6429039315, Kendall 0.3598357858 over 16 configurations.
- Primary full-context/common-support result: proxy Spearman 0.767503 versus H2 0.853411 and random 0.784306; proxy minus H2 -0.085908, 95% task-cluster percentile interval [-0.307920, 0.058196], 10,000 paired finite draws, p-val=n/a. The fixed train/validation-only transferred prompt is H2.
- Final artifacts: `RESULTS_selection_utility.md`, `results/SUMMARY_RECEIPT.json`, source/criterion/repeat manifests and `scripts/`. No provider call, inference, reviewer, new label, source-input modification, or other-study edit occurred.
- Next: archive via `git mv`, run layout/tests/diff checks, then commit, push, create and verify the required merge. This checkpoint is the recovery record if publication interrupts.

## Finalization continuation (10-05-2026 23:00 PDT)

- Session: `cj-e44-finalize`; the supervising master authorized this one bounded completion continuation under the existing sole-worker session, with shared allowance verified 41% used / 59% remaining and 20k–40k tokens reserved for finishing. It is not a new experiment, model launch, reviewer, or inference run.
- Scope before publication: repair current-mask repeat-slot accounting; assert immutable before/after hashes for labels, frozen source metadata, and harvests; add task-draw Pearson/Kendall uncertainty and cross-checks; make all sensitivity status/support/difference fields explicit; repair Markdown table escaping and measured conclusion; run exactly one final archived-path 10,000-draw analysis and then land the result.

## Final analysis receipt (10-05-2026 23:08 PDT)

- Completed the one final archived-path real analysis: `python3 experiments/archive/44_cached_score_judge_selection_utility/scripts/analyze_selection_utility.py --draws 10000`. It passed immutable before/after source hashes for labels, panel, units, probes, selection/finalist/test receipts, and all 60 source harvest exports (including deterministic controls); no frozen source changed.
- `python3 .../scripts/test_selection_utility.py` passed 9 tests, including the repeat-slot mask check and vectorized Spearman/Pearson/Kendall tie/constant cross-check against SciPy. Layout and `git diff --check` passed; the copied labels remain SHA-256 `ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c`.
- Publication continuation: inspect exact staged owned paths and secret scan; commit, push, create pull request, integrate/recheck if needed, head-match merge, then append `LANDED <commit> <url> <timestamp>` and create `private/DONE` only after confirmed merge.


## Deterministic completion recovery (10-05-2026 23:11 PDT)

- The remote Codex worker exited with code1 after applying the Pearson constant-input fix because its subscription allowance was exhausted. Its pane is dead; no other implementation writer or healthy analysis child remains. The master is taking over final verification and publication under the owner-gone recovery rule, using only deterministic commands in the same owned SNAP checkout.
- Correction to earlier capacity notes: the 34%/41% usage observations came from the local desktop account; they did not establish available allowance for the remote authenticated account. No credits were bought, limits reset, or further model calls launched.
- Final verification session: cj-e44-verify; source/selection/scientific settings remain unchanged. The master added only report explanations/diagnostic formatting and this recovery record after the owner exited. Next: run 9 tests and final 10,000-draw analysis, verify unchanged sources and the exact staged diff, then publish and record LANDED.


## Final verified state (10-05-2026 23:14 PDT)

- Constant-input regression fixed and 9 tests passed. Corrected full analysis completed in named session cj-e44-verify, whose pane is now exited.
- Verified all 68 source fingerprints before/after; committed source files also match revision fc73f78696d53551cd57f13094ec6f73fbb1c234. The 75-item label file matches the protocol fingerprint.
- Publication is the only remaining phase. Main remains fc73f78; no rebase is needed. Verified result: proxy-minus-H2 Spearman -0.0859078215130098 with 95% task-bootstrap [-0.307920,0.058196], 10,000 valid paired draws.


## Confirmed publication (10-05-2026 23:20 PDT)

LANDED 208b8825db13184e39a4e88103349bc3566c5a02 https://github.com/brando90/cert-judge/pull/55 10-05-2026 23:20 PDT

- GitHub confirmed MERGED, with verified branch head 640e8809d7d73e43cfd3effd73da9c9a1f8648ff. Main publication contains the complete final artifacts, all 9 passing tests and the 10,000-draw run. The deterministic verification session has exited.
- This docs-only receipt is published by a normal fast-forward push to unprotected main; it changes no scientific artifact. No external messages were sent.
