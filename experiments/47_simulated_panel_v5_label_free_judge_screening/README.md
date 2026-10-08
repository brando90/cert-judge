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
| Reference probes and judge scoring | All20,250 pending criterion cells admitted; probes compiling independently |12/12 original smokes strictly accepted; exact slice recovery preserved every declared task |
| Recommendations and planning | Implemented; awaiting complete measurements | All required views and provenance gates tested; no full-pool conclusion yet |

See [results.md](results.md) for current evidence and [checkpoint](CKPT_v5_sandbox.md) for recovery.

Cached descriptive output: [RESULTS_cached_descriptive.md](RESULTS_cached_descriptive.md). Exact rendering, admission, and statistical implementation lives in `expt_v1/`; the phase remains active until both scoring subcampaigns and all requested analyses finish.

- 10-08-2026 12:15 PDT: [All cached procedures, structural controls and panel diagnostics](RESULTS_existing_and_controls.md) are complete (90 procedures and 90 diagnostic views, 10,000 task draws each). [Raw-repeat uncertainty](expt_v1/results/existing_repeat_variability_intervals.json) preserves task pairing and missingness. The complete criterion manifest is frozen at 27,000 declared cells across twelve configurations; prompt packing is active. Full probe scoring, selection analysis and whole-study publication remain required.

Reconstruct frozen code dependencies with `python3 expt_v1/prepare_frozen_vendor.py`, then `python3 expt_v1/fetch_dependencies.py` against the pinned source clone. Both use exact named Git blobs, and runtime admission verifies their hashes. Input/receipt data retained privately are identified by the committed provenance manifests; this public repository does not distribute raw provider-private ratings or credentials.

Current measured-admission evidence: [criterion run receipt](expt_v1/results/criterion/scoring_admission_receipt.json). Read-only [artifact recovery](expt_v1/results/criterion/harvest_recovery_1.json) recovered original responses without repeated calls. The [task-selection transport condition](expt_v1/results/criterion/infrastructure_admission_recovery_1.json) replaces a 166,242-byte failed task query with verified equivalent dataset slices; it changes no prompts, judge settings or scientific cells.

Adopt the existing named criterion driver and automatic follow-through before starting any new process. After criterion reconciliation, the follow-through runs all 192 criterion views and 84 repeat analyses, then generates the criterion report. The three target views run in independent ordinary Python processes; [synthetic serial-equivalence checks](expt_v1/results/implementation_parallel_verification.json) preserve every result. Full reporting requires current-input derivation receipts for all required views and refuses stale score inputs, missing transfers/planning conditions, substituted structural evidence or unreconciled phases. Final publication and whole-study completion remain separate verified gates.

After verified probe integration, complete its frozen rendering, packing, quote and deployment. From `expt_v1/`, run `python3 verify_task_slices.py --phase probes` before admitting the complete probe workload through the named driver. Once both scoring phases are reconciled, run `python3 run_offline.py --name full_analysis -- python3 analyze_campaign.py --probe-manifest probes/probe_manifest.json`, then `python3 report_campaign.py --probe-manifest probes/probe_manifest.json`. The criterion and full reports must both pass their provenance checks before publication.

At probe-driver launch, also start a named full follow-through from `expt_v1/` with `python3 run_offline.py --name full_followthrough -- python3 after_full_campaign.py --probe-manifest probes/probe_manifest.json`. It waits for both existing scoring phases, runs all full analyses, verifies the criterion dependency and generates the reports. Its `runtime/FULL_ANALYSIS_READY_FOR_PUBLICATION.json` requests final inspection/publication; it is not whole-study completion. Do not launch it before probe admission, since the dependency-only wait must remain available while the independent compiler runs.
