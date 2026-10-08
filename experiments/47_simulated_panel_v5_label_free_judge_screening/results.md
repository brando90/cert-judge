# Simulated-panel v5 screening results ledger

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/47_simulated_panel_v5_label_free_judge_screening/results.md>

**TLDR:** Protocol preparation and metadata inventory only. No new criterion result, model call or property recommendation exists yet.

Status: RUNNING — 10-08-2026.

- Source manifests distinguish old G00 anchor data from 50 fresh tasks; fresh groups are analyzed separately under the protocol.
- Zero-call target reconstruction retained 691/750 fresh rows (all 691 nonblank rows): all have the primary equal-family persona target, instructions-only target, and the common target excluding the Anthropic and Alibaba judge-pool families. This is simulated-panel data only.
- The receipt [zero_call_inventory.json](expt_v1/results/zero_call_inventory.json) records six pinned input hashes and 22 raw-cell hashes without provider-private contents; [targets_reconstructed.json](expt_v1/results/targets_reconstructed.json) is the source-hash-bound target table.
- Primary pool contains 12 historical configurations over three base models and two provider families. This is a limitation on judge-population uncertainty.
- File length and theorem-count ratio are item-level controls, not judge-ranking signals on shared inputs.
- Stanford Network Analysis Project node skampere1 passed relevant health checks; authentication metadata reports a ChatGPT login, but useful executor action remains unverified.
- No set-N, v6, set-B prediction or private rating file has been accessed by this helper.

Measured scores, intervals, complete inventory and recommendations: pending remote execution. None should be inferred from this preparation ledger.
