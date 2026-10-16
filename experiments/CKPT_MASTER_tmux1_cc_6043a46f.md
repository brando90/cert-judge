# cert-judge master checkpoint (tmux 1, personal Claude Code, session 6043a46f)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/CKPT_MASTER_tmux1_cc_6043a46f.md>

**TLDR:** All four SNAP experiments dispatched on 09-30-2026 are done and merged; no worker or watch is left running.
- **39:** a new label-free index, `C_ms_gold`, passes on held-out judges (test Spearman 0.558); the paper's `TI_var` and `PTI_v0` fail there.
- **41:** the paper's 72-pair evidence rests on mismatched references (7 of 24 tasks match), and the re-score against corrected labels is inconclusive.
- **42:** only 15 of 56 judges pass the semantic screen.
- **43:** no judge was gamed beyond what the validated reference also credited, and the index did not predict gaming resistance.
- **Waiting on Brando:** what the paper should now claim.

Created: 09-30-2026 14:00 PDT
Last updated: 09-30-2026 21:50 PDT (verified on skampere1 at 21:46 PDT and on GitHub `ce3b595`)

## 1. Identity and recovery

- Host: Brando's MacBook Pro; cwd `/Users/brandomiranda/cert-judge`; conversation `6043a46f-1196-4fb0-a7a2-8ae11843f7c8`; profile `cc` (personal); model `claude-opus-5-5`, effort max; tmux session `1`.
- Session title, set by Brando with `/rename`: "cert-judge exps 39–43: 39 PASS (C_ms_gold ρ 0.558), paper TI_var fails; 42–43 running". It is now stale (42 and 43 are done); only Brando can rename the session.
- Resume: `clauded --resume 6043a46f-1196-4fb0-a7a2-8ae11843f7c8`.

## 2. Results (all DONE, all merged to `main`)

| Experiment | Finished | Landed | Headline (measured) |
|---|---|---|---|
| `39_label_free_proxy_index_train_val_test_over_judge_families` | 09-30 17:27 PDT | PR #51 | **PASS.** 56 judge configurations, 28,591 probe cells, $574 Vals-reported. Selected `C_ms_gold` (missing-statement monotonicity on golds): train ρ 0.76, val ρ 0.76, **test ρ 0.558 [0.08, 0.76], permutation p 0.0127**. Paper's frozen indices on the same held-out judges: `PTI_v0` −0.27, `TI_var` −0.33. |
| `41_paper_panel_provenance_audit_and_vb_expert_label_rescore` | 09-30 14:55 PDT | PR #50 | Gate G0 PASS (0.833/0.905/0.738 reproduced). Paper labels = VeriBench participant 1's superseded old-prompt passes. 1 of 25 tasks never scored (stale filename); only 7 of 24 scored tasks have references matching what the rater saw. Corrected-expert re-score on matched items: Codex 0.333, Claude Opus −0.381, Qwen3-Coder 0.667 → **inconclusive**. |
| `42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges` | 09-30 19:58 PDT | PR #54 | 194 Lean-validated probes; 32,592/32,592 cells reconciled (99.35% measured), $656.15. **15 of 56** LLM configurations pass the semantic screen. Weakening directional accuracy tracks experiment 39's expert criterion: ρ 0.73 [0.55, 0.86] (train + val), 0.72 [0.31, 0.92] (test, post hoc). It adds nothing to `C_ms_gold` (Δ −0.06 [−0.16, 0.04] train + val). |
| `43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index` | 09-30 19:46 PDT | PRs #52, #53 | 90/90 cells, 720 attacker attempts, $60.21. Gaming gaps −0.162 to +0.033 for the 6 attacked Claude Sonnet 5 configurations (no interval above 0). 59 of 62 edited candidates were stuffed with test-like statements that the validated reference also credited. The index did not predict resistance: `C_ms_gold` ρ +0.600 (one-sided p 0.912), `TI_var` −0.086; `PTI_v0` not computable. |

## 3. Hazards a successor must know first

- **The paper's main claims are contradicted or unsupported** by experiments 39 and 41. Do not edit `paper_latex/` before Brando picks the framing.
- **ICLR 2027 status: withdrawn; nothing to do** (settled 10-13-2026 from the repository: the forum read withdrawn on 09-26 per experiment 37's README, and the full submission was never submitted per experiment 34's SUBMISSION_STATUS). Earlier text: ICLR 2027 status is unverified. `experiments/archive/37_openreview_feedback_current_iclr_revision/README.md:18` (09-26) says the live forum `yoLB5iP7Pn` showed *withdrawn*. The `uutils.openreview_uu` fetcher (ultimate-utils `c1ff4ea`, env `~/uv_envs/openreview-uu`) needs `~/keys/openreview_credentials.txt` from Brando; the alternative is `/chrome`.
- **skampere1 root disk filled once** (experiment 43, 15:55 PDT): 32 GB of stale Claude Code temp files were cleared. Root disk is now 75% used (213 GB free).
- **Shared checkout:** commit with explicit pathspecs from a private worktree.

## 4. Workers and watches

- No workers remain. All four tmux sessions (`cj-e39-proxy-index-search`, `cj-e41-provenance-audit`, `cj-e42-semantic-probes`, `cj-e43-gaming-resistance`) are idle at their prompts with `private/DONE` present. `cj-e42` still holds one finished background shell; leave it until it is idle for more than 24 hours (Trigger Rule 12).
- The cron watchdogs (`cj_e39_watchdog.sh`, `cj_worker_watchdog.sh` × 3) were **removed** at 21:47 PDT. The scripts remain in `/lfs/skampere1/0/brando9/bin/` for reuse.

## 5. Decisions waiting on Brando

- [p 10/10] **What the paper claims now.** Strongest supported story:
  - one human panel plus a label-free screen selected on train judges predicts held-out judges' agreement (`C_ms_gold`, 0.558);
  - the paper's original `TI_var` does not transfer (−0.33);
  - the semantic screen and gaming results go in as characterization.
  The 72-pair validation-set numbers would move to the appendix with the provenance caveat.
- [p 9/10] ICLR 2027 submission 35334: withdrawn or under review (credentials file or `/chrome`).
- [p 6/10] New human raters (catalog items 35.10 and 35.11): still the only route to a test over new items rather than new judges.

## 6. Ranked next dispatches (not started)

- [p 7/10] Text-only rewrite plan from experiments 39, 41, 42 and 43, once Brando picks the framing (no `paper_latex/` edits before that).
- [p 4/10] Verina transfer without labels (`experiments/ideas/verina_property_transfer_no_new_labels/`), reusing experiment 39's proven pipeline.
- [p 5/10] Archive experiments 39, 41, 42 and 43 together. They are DONE, and Trigger Rule 39 says the verdict commit should have moved them; the runbooks did not ask the workers to. Scripts in 42 and 43 reference experiment 39's folder by path (`42…/scripts/{e42,legacy,local_controls,analyze}.py`, `43…/scripts/{analyze,test_e43}.py`), so repoint them in the same commit and re-run their tests.

## 7. Not committed, and why

- `experiments/archive/34_iclr_mega_rewrite_astra/results/astra_last_message.md` and `astra_pid` are untracked 09-22 Astra leftovers, not this session's work. They are left untracked on purpose.
- 10-16-2026 13:05 PDT -- open by design, unmerged: PR #64 (interim result-consistent draft; plan of record = more human data) and PR #65 (pre-registered human rating-pool proposal: 25 tasks x 5 files, 51 new judge configurations); nothing running; Brando's personal Claude credits are out until 10-20-2026 00:00 PDT.
