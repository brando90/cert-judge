# Vals-funded spending pause and restart checkpoint

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/CKPT_vals_spend_pause.md>

**TLDR:** Pause Valkyrie and Vals application programming interface (API) inference while spending is reviewed. Local models on Stanford Network Analysis Project (SNAP) nodes, existing non-Vals funding within its old limits, subscription coding, cached analysis and human-rating administration remain eligible.

Created: 10-15-2026 09:41:46 PDT
Last updated: 10-15-2026 09:43:31 PDT

## Goal

- Prevent nonessential Vals-funded admissions and preserve recoverable experiment state; no paid condition is newly exempted.

## What ran

- Checked the hosted account and the SNAP client: each reported zero in-progress and zero stopping runs on 10-15-2026.
- Stopped only the verified pilot admission driver on skampere2 (process 3873691); saved original states, checkpoint and hashes first.
- Audited five hourly Codex schedules; restored their prior ACTIVE state after the funding-scope clarification and added a Vals-only inference hold.

## Results

- Pilot process absent; saved controller has 30/30 terminal run entries and judge state has 209/209 terminal entries. These are run-record counts, not successful scientific results.
- Local-model jobs stopped: 0. No paid run, retry or model call was launched by this pause task.
- Complete cert-judge studies remain complete; their active-looking folder names are not evidence of live jobs.

## Stuck / blocked

- Vals-funded execution is user-paused. A nonzero per-run cap has not been specified; no enforceable nonzero cap is claimed.
- The current service listings do not prove that an inaccessible historical deployment or every other account has no outstanding billable job.

## Next steps

- Continue local inference under its existing limits, deterministic analysis and fresh human-rating administration; preserve earlier scientific holds.
- Before any paid resumption, record the essential condition, payer, numerical cap and enforcement covering admissions, retries, recovery and concurrent calls; reconcile existing run IDs first.
- Use the lane-specific continuation records below. Never replay completed or uncertain cells, reset ledgers, or restore a whole historical scheduler configuration.

## Brando to-do

- A per-run budget is needed only if paid execution should resume; no action is needed for local-model continuation.

## Runtime pause receipts and exact continuation boundaries

| Lane | Verified state and saved continuation |
|---|---|
| VeriBench `experiments/112_human_lean_software_verification_repo_catalog_for_unsaturated_vb/112A_mother_plans_john_santi_vbvX/pilot_t2_valkyrie/` | On skampere2, root `/lfs/skampere2/0/brando9/veribench_vb112/` plus that path. Driver process 3873691 was `/lfs/skampere2/0/brando9/vb106_venv/bin/python -u scripts/driver112.py`; stopped with SIGTERM at 09:39:49 PDT. `CKPT_vals_spend_pause.md`, `private/HOLD_VALS_SPEND`, `private/HOLD_ADMISSIONS`, and `private/spend_pause_10-15-2026/pause_receipt.json` preserve the boundary. All controller/judge records were terminal. |
| VeriBench `experiments/109_full_vbv1_896_2026_frontier_and_open_models_terminus2_valkyrie/` | On skampere3, root `/lfs/skampere3/0/brando9/veribench_vb109/` plus that path. No driver/worker session, admission process or experiment cron was found. Saved `CKPT_vals_spend_pause.md` and missing `private/HOLD_VALS_SPEND`, `HOLD_ADMISSIONS`, `STOP_DRIVER` markers. Local Lean verification processes remain intact. |
| VeriBench `experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge/` | skampere1 runtime has `results/DONE`, no worker loop process. Existing watchdog exits on DONE; its cron is preserved. |
| VeriBench `experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/` | skampere1 phase-7 runtime has `results/phase7/DONE`, no worker loop process. Existing watchdog exits on DONE; its cron is preserved. |

The pilot driver is not a read-only monitor: `judge_step` can admit judging before consulting `HOLD_ADMISSIONS`. Keep it stopped while paused. After paid resumption and cap enforcement, inspect the saved states and exact service first, then use `tmux new-session -d -s vb112-main -c <pilot-directory> '/lfs/skampere2/0/brando9/vb106_venv/bin/python -u scripts/driver112.py'` only if that owner session remains absent.

For the full-benchmark lane, safe inspection is `python3 scripts/driver109.py --status`. `--once` and `--no-admit` are unsafe as observation during a pause: `harvests()` can call `never_started.py --admit`. After a separately authorized paid restart, inspect `scripts/run_driver.sh`, `scripts/worker_loop_109.sh`, the original checkpoint and the existing ledger before rearming anything.

The official control command, if an actual paid run is discovered later, is `valkyrie run stop RUN_ID` (inspect `--help` first). A stopped admission process alone does not stop already admitted hosted jobs. In this inspection the current hosted listing and the SNAP client each returned zero in-progress/stopping runs, so no run-stop request was necessary.

## Codex follow-ups and funding scope

Exact before/after settings and `automation_verification.json` are retained privately in `/Users/brandomiranda/.codex/task-tracking/spend-pause-10-15-2026/`. All five schedules retain their original hourly cadence, target chat and ACTIVE state. Each now explicitly blocks Vals-funded admissions/retries/recovery. The temporary initial broad pause was reversed after Brando clarified funding scope.

| Canonical experiment | Schedule and allowed work |
|---|---|
| VeriBench `experiments/75_J1_validating_formal_spec_judge_train_val_test/` | `experiment-75-finish-theorem-coverage-judge-search`: deterministic preparation continues; the proposed 255-call Vals-funded condition remains unadmitted. Resume state: `CKPT_completion_tracker.md`. |
| VeriBench `experiments/91_lean_to_python_hopefully_unsaturated_vb/` | `experiment-91-finish-full-source-evaluation-scoring`: local Qwen work and existing non-Vals Gemini lane remain outside this spending pause; old uncertain-call reservations remain. Resume state: `expt_v5_full_source/scoring_consumer/recovery_stop_marker_v2/CKPT.md`. |
| VeriBench `research_archive/experiments/91c_eval_vsb_2_vbv2_using_gemini/` | `experiment-91c-finish-gemini-solver-results`: existing Allen Gemini route is outside the pause; historical Vals/Valkyrie judging remains held. Preserve the parent's prior scheduler pause and shared inclusive $5,000 ceiling. Resume: `CKPT_full_access_closeout.md`, `expt_v2/CURRENT_BUDGET_NOTICE.md`. |
| VeriBench `research_archive/experiments/92c_gemini_tc_judge_vbv2/` | `experiment-92c-finish-gemini-coverage-and-validation`: existing Allen Gemini receipt reconciliation remains eligible; preserve shared ledger, scientific holds and parent pause. Resume: `CKPT.md`, `RESULTS_continuation_readiness_10-13-2026.md`. |
| VeriBench `research_archive/experiments/93_qwen38_flash_next_vbv2_five_tasks/` | `experiment-93-finish-qwen-five-task-evaluation`: documented self-hosted inference is outside the Vals pause; previous failed control and admission conditions still apply. Resume: `README.md`, `results.md`, `expt_v3_prospective_full_procedure/ADMISSION_PREPARATION.md`. |

## Essential work retained

Fresh human-rating administration and analysis of already cached judge outputs remain the useful cert-judge priorities. The new human-data round must preserve its registered protocol, sealed predictions and human/agent provenance. This pause does not authorize revising paper claims or labelling archived findings as new test evidence. Local-model experiments and local training are unaffected by this spending task.

The completed cert-judge studies retain their original checkpoints: `experiments/39_label_free_proxy_index_train_val_test_over_judge_families/CKPT_proxy_index_search.md`, `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/CKPT_provenance_audit.md`, `experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/CKPT_semantic_probes.md`, and `experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/CKPT_gaming_resistance.md`. No rerun was needed or started.

## Event log

- 10-15-2026 09:41:46 PDT: Applied Brando's spending pause with his clarification limiting it to Valkyrie/Vals API keys; stopped one admission driver, preserved local models, scoped five schedules, and saved runtime/checkpoint evidence.
- 10-15-2026 09:43:31 PDT: Verified hosted service again (zero running/stopping), five schedule scope notices with original targets/cadence, instruction checks and experiment layout.
