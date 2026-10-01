# cert-judge master checkpoint (tmux 1, personal Claude Code, session 6043a46f)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/CKPT_MASTER_tmux1_cc_6043a46f.md>

**TLDR:** This session coordinates the reviewer-driven cert-judge experiments dispatched on 09-30-2026: 41 (provenance audit and re-score against VeriBench's expert labels, zero calls), 42 (semantic weakening/over-constraint/vacuity probes) and 43 (judge-gaming resistance). All three run on skampere1 with model-free cron watchdogs. It also watches experiment 39's SNAP worker, which the MacBook Air dispatcher owns. The open decisions for Brando are the ICLR 2027 status (the forum may show "withdrawn") and OpenReview access for agents.

Created: 09-30-2026 14:00 PDT
Last updated: 09-30-2026 14:00 PDT

## 1. Identity and recovery

- Host: Brando's MacBook Pro; cwd `/Users/brandomiranda/cert-judge`; conversation `6043a46f-1196-4fb0-a7a2-8ae11843f7c8`; profile `cc` (personal); model `claude-opus-5-5`, effort max; tmux session `1`.
- Resume: `clauded --resume 6043a46f-1196-4fb0-a7a2-8ae11843f7c8`.

## 2. Hazards a successor must know first

- **ICLR 2027 status is unverified.** `experiments/archive/37_openreview_feedback_current_iclr_revision/README.md:18` (09-26) says the live forum `yoLB5iP7Pn` showed *withdrawn*. The last submission record (`experiments/archive/34_iclr_mega_rewrite_astra/submission/SUBMISSION_STATUS.md`, 09-24) left the final Submit pending. The paper deadline (Sep 25 AoE) has passed.
- **No browser or OpenReview credentials in this CLI.** Brando can run `/chrome` in this session (Claude in Chrome), or store `~/keys/openreview_credentials.txt` for the uutils fetcher (being built by a background subagent).
- **The paper's labels are VeriBench participant 1's old-prompt passes.** Paper `pass1` = `old_prompt/participant1_data_pass_2.tsv` (75/75 identical scores); paper `pass2` = `old_prompt/participant1_data_pass_1.tsv` (72/75). Experiment 41 audits the consequences.
- **Lean environment.** Experiment 39's probe build found that 72 of 75 candidates import a `VeriBench` module the grading project lacks (249 of 677 probes valid at 12:21 PDT). Experiments 42 and 43 are told to reuse its fix.
- **Shared checkout.** Other sessions push to `main`: commit with explicit pathspecs and rebase before push.

## 3. Workers this session owns (all on skampere1, personal Claude profile, full access)

| tmux session | Experiment | Model / effort | Runbook | State at 14:00 PDT |
|---|---|---|---|---|
| `cj-e41-provenance-audit` | `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/` | claude-sonnet-5 / high | `cc.md` | working (launched 13:56) |
| `cj-e42-semantic-probes` | `experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/` | claude-opus-5-5 / high | `cc.md` | working (launched 13:56) |
| `cj-e43-gaming-resistance` | `experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/` | claude-opus-5-5 / high | `cc.md` | working (launched 13:56) |

Each worker lands its own PR (Trigger Rule 46), emails `brando.science@gmail.com`, and touches `private/DONE`. If its model is quota-blocked, it switches to claude-sonnet-5 high and records the switch. Experiment 39's worker (`cj-e39-proxy-index-search`, Claude Fable 5.1 max) belongs to the MacBook Air session "Cert-judge experiment 39 dispatch". At 13:50 PDT this session only told it to merge `origin/main` (Amendment 1, `c97be81`), and it acknowledged.

## 4. Watches (survive this session; cron on skampere1)

- `/lfs/skampere1/0/brando9/bin/cj_e39_watchdog.sh` at minutes 0 and 30, plus at reboot. It restarts `cj-e39-proxy-index-search` from its checkpoint if the session dies (max 3). It types one continue nudge if the worker is idle with no monitor or driver running and `results.md` is older than 60 minutes (max 8). It ends when `results/TEST_RECEIPT.json` exists. Heartbeat: `/lfs/skampere1/0/brando9/snap_jobs/cj-e39-watchdog.jsonl`.
- `/lfs/skampere1/0/brando9/bin/cj_worker_watchdog.sh <session> <checkout> <dir> <brief> <model> <effort>` for 41, 42 and 43, at minutes 5/35, 10/40 and 15/45, plus at reboot. Same rules; each ends at `private/DONE`. Heartbeats: `/lfs/skampere1/0/brando9/snap_jobs/<session>-watchdog.jsonl`.
- Inspect: `ssh skampere1 'tmux ls; tail -n2 /lfs/skampere1/0/brando9/snap_jobs/*watchdog.jsonl; crontab -l | grep cj_'`. Remove a watch: `crontab -l | grep -v <script> | crontab -`.

## 5. Decisions waiting on Brando

- [p 10/10] Confirm what OpenReview shows for ICLR 2027 submission 35334 (withdrawn or under review). It decides whether the November revision window exists for this paper.
- [p 8/10] Give agents OpenReview access: `/chrome` in this session, or the credential file for `uutils.openreview_uu`.
- [p 7/10] Check the ICLR reviewer console. Expertise and bidding were due 09-30 04:59 PDT, and reciprocal-review duties apply to his other ICLR 2027 papers.
- [p 6/10] New human raters (catalog 35.10 and 35.11) need people. VeriBench's three-expert labels partly substitute for them (experiments 39 and 41).

## 6. Ranked next dispatches (not started)

- [p 5/10] Verina transfer, labels not needed (`experiments/ideas/verina_property_transfer_no_new_labels/`), after experiment 39's pipeline is proven.
- [p 3/10] Dafny/Verus structural pilot (`experiments/ideas/non_lean_dafny_verus_transfer/`, catalog 35.9).
- [p 3/10] Nov-revision prose pass, after experiments 39, 41, 42 and 43 land.
