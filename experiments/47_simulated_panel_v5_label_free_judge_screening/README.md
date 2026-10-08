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
| Reference probes and judge scoring | Active implementation and independent compilation | Criterion-first scheduling under Amendment 04; no new calls yet |
| Recommendations and planning | TODO | No conclusion yet |

See [results.md](results.md) for current evidence and [checkpoint](CKPT_v5_sandbox.md) for recovery.

Cached descriptive output: [RESULTS_cached_descriptive.md](RESULTS_cached_descriptive.md). Exact rendering, admission, and statistical implementation lives in `expt_v1/`; the phase remains active until both scoring subcampaigns and all requested analyses finish.

- 10-08-2026 12:15 PDT: [All cached procedures, structural controls and panel diagnostics](RESULTS_existing_and_controls.md) are complete (90 procedures and 90 diagnostic views, 10,000 task draws each). [Raw-repeat uncertainty](expt_v1/results/existing_repeat_variability_intervals.json) preserves task pairing and missingness. The complete criterion manifest is frozen at 27,000 declared cells across twelve configurations; prompt packing is active. Full probe scoring, selection analysis and whole-study publication remain required.
