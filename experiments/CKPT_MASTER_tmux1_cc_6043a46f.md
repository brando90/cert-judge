# cert-judge master checkpoint (tmux 1, personal Claude Code, session 6043a46f)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/CKPT_MASTER_tmux1_cc_6043a46f.md>

**TLDR:** Two of the four SNAP experiments have landed.
- Experiment 39 **passed** its held-out test. A new label-free index, `C_ms_gold`, predicts judge–human agreement on unseen judge models at Spearman 0.558. The paper's frozen indices **fail** on the same held-out judges (`PTI_v0` −0.27, `TI_var` −0.33).
- Experiment 41 found that the paper's judges saw the raters' reference bytes on only 7 of 24 tasks. Re-scored against VeriBench's corrected expert labels, the paper's association is inconclusive.
- Experiments 42 (semantic probes) and 43 (gaming resistance) are still running on skampere1 with watchdogs.
- Brando's main open decision is what the paper now claims.

Created: 09-30-2026 14:00 PDT
Last updated: 09-30-2026 18:10 PDT (verified on skampere1 at 17:53 PDT and on GitHub at 18:07 PDT)

## 1. Identity and recovery

- Host: Brando's MacBook Pro; cwd `/Users/brandomiranda/cert-judge`; conversation `6043a46f-1196-4fb0-a7a2-8ae11843f7c8`; profile `cc` (personal); model `claude-opus-5-5`, effort max; tmux session `1`.
- Resume: `clauded --resume 6043a46f-1196-4fb0-a7a2-8ae11843f7c8`.

## 2. Current state (verified 09-30-2026 17:53–18:07 PDT)

| Experiment | Host / tmux | State | Landed | Result |
|---|---|---|---|---|
| `39_label_free_proxy_index_train_val_test_over_judge_families` | skampere1 / `cj-e39-proxy-index-search` (worker owned by the MacBook Air session "Cert-judge experiment 39 dispatch") | **DONE** 17:27 PDT; `private/DONE` present | PR #51, merge `5d4379f`, receipt `267ef29` | 56 judge configurations; 28,591 Lean-validated probe cells through Valkyrie, $574 Vals-reported. Selected index `C_ms_gold` (missing-statement monotonicity on golds): train ρ 0.76, val ρ 0.76, **test ρ 0.558 [0.08, 0.76], permutation p 0.0127, PASS**. Paper's frozen indices on test: `PTI_v0` −0.27, `TI_var` −0.33. |
| `41_paper_panel_provenance_audit_and_vb_expert_label_rescore` | skampere1 / `cj-e41-provenance-audit` | **DONE** 14:55 PDT; `private/DONE` present | PR #50 (`da61634` … `9ac12b7`) | Gate G0 PASS (Codex 0.833/0.905/0.738 reproduced exactly). Paper labels = VeriBench participant 1's superseded old-prompt passes (75/75, 72/75). One task (`0_unsafeMultiply_safe`) never scored (stale gold filename). Only 7 of 24 scored tasks have judge-seen reference bytes equal to rater-seen bytes. View V3 (corrected expert mean, matched items, n=21): Codex 0.333, Claude Opus −0.381, Qwen3-Coder 0.667 → **inconclusive** under the locked rule. |
| `42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges` | skampere1 / `cj-e42-semantic-probes` (Claude Opus 5.5 high) | **RUNNING** since 14:06 PDT; no judge call recorded as of its 16:25 ledger; a stage driver was running at 17:40 PDT | branch `origin/e42-semantic-probes` @ `5754248` (17:11, vendors experiment 39's harvester) | pending |
| `43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index` | skampere1 / `cj-e43-gaming-resistance` (Claude Opus 5.5 high) | **RUNNING** since 14:04 PDT; full run in progress (rounds 1–2 at 17:21) | branch `origin/e43-gaming-resistance` @ `eac3879` | pending |

Each running worker lands its own PR (Trigger Rule 46), emails `brando.science@gmail.com`, and touches `private/DONE`.

## 3. Hazards a successor must know first

- **The paper's main claims are now contradicted or unsupported.** Experiment 39: the paper's `TI_var` and `PTI_v0` do not transfer to held-out judges, while `C_ms_gold` does. Experiment 41: the paper's 72-pair evidence rests on mismatched references (17 of 24 tasks) and superseded labels. Do not edit `paper_latex/` without Brando's decision.
- **ICLR 2027 status is unverified.** `experiments/archive/37_openreview_feedback_current_iclr_revision/README.md:18` (09-26) says the live forum `yoLB5iP7Pn` showed *withdrawn*. The paper deadline (Sep 25 AoE) has passed.
- **OpenReview access.** The `uutils.openreview_uu` fetcher is ready (ultimate-utils `c1ff4ea`, 33 offline tests pass, env `~/uv_envs/openreview-uu`). It needs Brando to create `~/keys/openreview_credentials.txt` in his own terminal (command in the fetcher's error message). The alternative is `/chrome` in this session.
- **Shared checkout.** Other sessions push to `main`. Commit with explicit pathspecs from a private worktree; never rebase the shared checkout.

## 4. Watches (cron on skampere1; they survive this session)

| Script | Schedule | Last heartbeat | Stops when |
|---|---|---|---|
| `/lfs/skampere1/0/brando9/bin/cj_e39_watchdog.sh` | minutes 0 and 30, plus at reboot | `done` 00:30Z | `results/TEST_RECEIPT.json` exists (now a no-op) |
| `cj_worker_watchdog.sh cj-e41-provenance-audit …` | minutes 5 and 35 | `done` 00:35Z | `private/DONE` (now a no-op) |
| `cj_worker_watchdog.sh cj-e42-semantic-probes …` | minutes 10 and 40 | `driver_running` 00:40Z | `private/DONE` |
| `cj_worker_watchdog.sh cj-e43-gaming-resistance …` | minutes 15 and 45 | `working` 00:45Z | `private/DONE` |

- Rules: restart a dead tmux session from its brief plus checkpoint (max 3); one continue nudge if the worker is idle with no monitor or driver running and `results.md` is older than 60 minutes (max 8).
- Heartbeats: `/lfs/skampere1/0/brando9/snap_jobs/*watchdog.jsonl`.
- Inspect: `ssh skampere1 'tmux ls; tail -n1 /lfs/skampere1/0/brando9/snap_jobs/*watchdog.jsonl; crontab -l | grep cj_'`.
- After 42 and 43 land, remove all four entries: `crontab -l | grep -vE 'cj_e39_watchdog|cj_worker_watchdog' | crontab -`.

## 5. Decisions waiting on Brando

- [p 10/10] What the paper claims now. Options:
  - re-centre it on the held-out result (`C_ms_gold`, test ρ 0.558, p 0.013);
  - report the frozen `TI_var` / `PTI_v0` failure on held-out judges;
  - demote the 72-pair validation-set evidence (provenance mismatch; inconclusive re-score).
  Experiments 42 and 43 add to whichever framing is chosen.
- [p 9/10] ICLR 2027 submission 35334: withdrawn or under review? Run the fetcher once the credentials exist, or use `/chrome`.
- [p 6/10] New human raters (catalog items 35.10 and 35.11). VeriBench's three-expert labels partly substitute (experiments 39 and 41).

## 6. Ranked next dispatches (not started)

- [p 6/10] Paper rewrite plan from experiments 39, 41, 42 and 43, once Brando picks the framing (text-only draft; no `paper_latex/` edits before that decision).
- [p 5/10] Verina transfer without labels (`experiments/ideas/verina_property_transfer_no_new_labels/`), reusing experiment 39's now-proven pipeline.
- [p 3/10] Dafny/Verus structural pilot (`experiments/ideas/non_lean_dafny_verus_transfer/`, catalog 35.9).

## 7. Not committed, and why

- `experiments/archive/34_iclr_mega_rewrite_astra/results/astra_last_message.md` and `astra_pid` are untracked leftovers of the 09-22 Astra run (not this session's work). They are left untracked on purpose: a stale PID file and an unreviewed agent message.
