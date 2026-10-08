# Simulated-panel v5 label-free judge screening

**Doc link:** <https://github.com/brando90/cert-judge/tree/main/experiments/47_simulated_panel_v5_label_free_judge_screening>

**TLDR:** Screen frozen cert-judge properties on VeriBench experiment 106 v5's 50 fresh tasks and simulated raters. This helper produces simulated-panel agreement, selection utility and planning sensitivities; it does not validate against humans or access the prospective rating set.

Goal: determine whether frozen reference properties and the explicitly candidate-dependent geometric-mean and repeat-information properties help select judges beyond the fixed human-mirror prompt. The locked [protocol](PROTOCOL.md) defines eligibility, uncertainty, dropping and inconclusive rules before criterion computations. The October 7 chat owns the project and total-variation-distance mutual-information definitions; this helper owns only experiment 47.

```text
PROTOCOL.md          frozen scientific and analysis contract
results.md           live evidence ledger
CKPT_v5_sandbox.md   continuation and recovery
expt_v1/             scripts, hashed inputs, admission manifests, results
assets/              original user handoff and provenance
```

Method: inventory and copy frozen v5 sources; reconstruct equal-family targets; validate reference probes with Lean; score the exact historical primary 12-judge pool through Valkyrie; analyze paired uncertainty and transfer; recommend candidates only where evidence supports them.

Dependencies: experiment 39 frozen functions and configurations; archived experiments 44/45; read-only VeriBench v5 revision in the protocol; Stanford Network Analysis Project execution; Vals-funded Valkyrie for measured calls. No provider keys on the host.

| Phase | Status | Evidence |
|---|---|---|
| Protocol and ownership | Frozen, amendments additive | Reserved number 47; owner notified; protocol precedes computations |
| Source inventory and target reconstruction | Verified zero-call phase | 28 raw-cell files, frozen recovery precedence, and 650/650 saved main targets match at six decimals |
| Original criterion scoring | All 20,250 admitted occurrences reconciled offline after terminal run errors | 4,312 original score repeats accepted; missing/parser/uncertified outputs retained; 22 harvest files unchanged on rerun |
| Reference and candidate probes | Independent two-worker compiler remains active | Final integration requires complete frozen outcomes, exact transformed bytes and matching terminal compiler receipts |
| Criterion analysis | All 192 descriptive views and 84 repeat-information analyses verified | Complete-pool shared coverage 0/691; selection gains and conditional power unavailable |
| Full recommendations and planning | Implemented; awaiting the required probe campaign | All required views and provenance gates tested; no full-study shortlist |

See [results.md](results.md) for current evidence and [checkpoint](CKPT_v5_sandbox.md) for recovery.

Cached descriptive output: [RESULTS_cached_descriptive.md](RESULTS_cached_descriptive.md). Exact rendering, admission, and statistical implementation lives in `expt_v1/`; the phase remains active until both scoring subcampaigns and all requested analyses finish.

- 10-08-2026 12:15 PDT: [All cached procedures, structural controls and panel diagnostics](RESULTS_existing_and_controls.md) are complete (90 procedures and 90 diagnostic views, 10,000 task draws each). [Raw-repeat uncertainty](expt_v1/results/existing_repeat_variability_intervals.json) preserves task pairing and missingness. The complete criterion manifest is frozen at 27,000 declared cells across twelve configurations; prompt packing is active. Full probe scoring, selection analysis and whole-study publication remain required.

Reconstruct frozen code dependencies with `python3 expt_v1/prepare_frozen_vendor.py`, then `python3 expt_v1/fetch_dependencies.py` against the pinned source clone. Both use exact named Git blobs, and runtime admission verifies their hashes. Input/receipt data retained privately are identified by the committed provenance manifests; this public repository does not distribute raw provider-private ratings or credentials.

Current measured-admission evidence: [criterion run receipt](expt_v1/results/criterion/scoring_admission_receipt.json). Read-only [artifact recovery](expt_v1/results/criterion/harvest_recovery_1.json) recovered original responses without repeated calls. The [task-selection transport condition](expt_v1/results/criterion/infrastructure_admission_recovery_1.json) replaces a 166,242-byte failed task query with verified equivalent dataset slices; it changes no prompts, judge settings or scientific cells.

The original criterion driver died during a verified host reboot; do not restart its admission loop. `harvest_original_artifacts.py` reconciles the ten original archives without transport calls, using unchanged ledger identities and the frozen parser only after exact request and written-file checks. Missing artifacts never establish absence of an earlier verdict and never authorize readmission. The deterministic criterion follow-through finished successfully under the new boot. Its [192 criterion views](RESULTS_criterion_campaign.md) and [84 repeat-information analyses](RESULTS_criterion_repeat_information.md) have current-input provenance and verified report hashes. Shared score coverage is 0/691 nonblank items across the complete pool, below the frozen 90% gate; full-pool selection gains remain unavailable. The follow-through must not be restarted from an obsolete process receipt. The three target views run in independent ordinary Python processes; [synthetic serial-equivalence checks](expt_v1/results/implementation_parallel_verification.json) preserve every result. Full reporting requires current-input derivation receipts for all required views and refuses stale score inputs, missing transfers/planning conditions, substituted structural evidence or unreconciled phases. Final publication and whole-study completion remain separate verified gates.

`dependency_wait.py` verifies the helper run and process identities and calls `verify_probe_artifacts.py` before integration. This gate replays only the frozen builder's pure schema against existing compiler-cache answers, verifies every expected outcome and unavailable placeholder, and checks actual transformed bytes. It performs no compilation or artifact writes. The independent owner retains exclusive control of `expt_v1/probes/`.

After verified probe integration, complete its frozen rendering, packing, quote and deployment. From `expt_v1/`, run `python3 verify_task_slices.py --phase probes` before admitting the complete probe workload through the named driver. Once both scoring phases are reconciled, run `python3 run_offline.py --name full_analysis -- python3 analyze_campaign.py --probe-manifest probes/probe_manifest.json`, then `python3 report_campaign.py --probe-manifest probes/probe_manifest.json`. The criterion and full reports must both pass their provenance checks before publication.

At probe-driver launch, also start a named full follow-through from `expt_v1/` with `python3 run_offline.py --name full_followthrough -- python3 after_full_campaign.py --probe-manifest probes/probe_manifest.json`. It waits for both existing scoring phases, runs all full analyses, verifies the criterion dependency and generates the reports. Its `runtime/FULL_ANALYSIS_READY_FOR_PUBLICATION.json` requests final inspection/publication; it is not whole-study completion. Do not launch it before probe admission, since the dependency-only wait must remain available while the independent compiler runs.
