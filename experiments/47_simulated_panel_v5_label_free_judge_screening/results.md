# Simulated-panel v5 screening results ledger

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/47_simulated_panel_v5_label_free_judge_screening/results.md>

**TLDR:** The zero-call v5 target reconstruction is verified against frozen saved targets after recovery precedence. No judge criterion, new model call, or property recommendation exists yet.

Status: RUNNING — 10-08-2026.

- Source manifests distinguish old G00 anchor data from 50 fresh tasks; fresh groups are analyzed separately under the protocol.
- Frozen S2 recovery precedence admitted 3,847 recovery receipts and retained 44 non-admitted recovery receipts; it never replaces a measured or parser-error original cell. The resolver uses declared manifest model identity rather than deriving a model name from recovery run labels.
- Zero-call target reconstruction retained all 691 nonblank fresh rows: each has the primary equal-family persona target, instructions-only target, and common target excluding the Anthropic and Alibaba judge-pool families. Blank rows are deterministically zero under the frozen source rule, yielding 750/750 defined target rows.
- The reconstruction matches the 650 fresh G01–G13 saved v5 targets at six-decimal precision (0 mismatches); no saved target file is available for the 100 late G16/G17 rows. This is simulated-panel data only.
- The receipt [zero_call_inventory.json](expt_v1/results/zero_call_inventory.json) records pinned input hashes and 28 raw-cell hashes without provider-private contents; [targets_reconstructed.json](expt_v1/results/targets_reconstructed.json) is the source-hash-bound target table.
- Cached v5 cells verified every declared nonblank receipt for `opus55x|H0` and `opus55x|H2` (4,146 cells total; 691/691 scorable nonblank items per configuration). They are two members of the declared 12-configuration pool, not the historical ensemble or a rebuilt fold-specific judge; the other ten configurations remain declared missing conditions. Receipt: [cached_primary_pool_inventory.json](expt_v1/results/cached_primary_pool_inventory.json).
- Primary pool contains 12 historical configurations over three base models and two provider families. This is a limitation on judge-population uncertainty.
- File length and theorem-count ratio are item-level controls, not judge-ranking signals on shared inputs.
- Stanford Network Analysis Project node skampere1 has a live full-access supervisor and a verified `gpt-5.6-terra` high-reasoning implementation executor. The executor is not a measured judge.
- No set-N, v6, set-B prediction or private rating file has been accessed by this helper.

Measured scores, intervals, complete inventory and recommendations: pending remote execution. None should be inferred from this preparation ledger.
