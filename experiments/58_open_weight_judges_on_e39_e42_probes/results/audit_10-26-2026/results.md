# E58 audit: live execution record

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/e58-frozen-analysis-fixes/experiments/58_open_weight_judges_on_e39_e42_probes/results/audit_10-26-2026/results.md>

Updated 10-26-2026. Owner: Codex; no model inference or provider charges.

| Check | Status | Receipt |
|---|---|---|
| Full E58 deterministic suite | 32 passed, 0 skipped | Local uv environment, 46.00 seconds |
| Frozen prompt rebuild | 9,927/9,927 hashes match | Original rebuild receipt preserved |
| Empty-run analysis | Both panels retain 117 units, gates NOT_COMPUTABLE | Ignored `private/audit_10-26-2026/empty_analysis/` |
| E60 26-unit compatibility check | Exit 0; exact primary object match | [REPRODUCTION.json](REPRODUCTION.json) |
| Full E60 saved-data reproduction | Dispatched; checking completion | SNAP session `cj-e60-reproduction-01a179a8`; one CPU, 3 GiB, 1,800 seconds |

[Findings and protocol gaps](../../RESULTS_analysis_audit.md) · [checkpoint](../../CKPT_analysis_audit.md).

**TLDR-end:** [cert-judge: analysis audit] E58 fixes pass deterministic checks and preserve the saved primary statistic. The independent full E60 reproduction is additional verification of existing data.
