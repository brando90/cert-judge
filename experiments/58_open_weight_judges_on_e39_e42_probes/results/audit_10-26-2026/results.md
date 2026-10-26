# E58 audit: live execution record

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/e58-frozen-analysis-fixes/experiments/58_open_weight_judges_on_e39_e42_probes/results/audit_10-26-2026/results.md>

Updated 10-26-2026. Owner: Codex; no model inference or provider charges.

| Check | Status | Receipt |
|---|---|---|
| Full E58 deterministic suite | 32 passed, 0 skipped | Local uv environment, 46.00 seconds |
| Frozen prompt rebuild | 9,927/9,927 hashes match | Original rebuild receipt preserved |
| Empty-run analysis | Both panels retain 117 units, gates NOT_COMPUTABLE | Ignored `private/audit_10-26-2026/empty_analysis/` |
| E60 26-unit compatibility check | Exit 0; exact primary object match | [REPRODUCTION.json](REPRODUCTION.json) |
| Actual E58 mercury1 smoke | Exit 0; 117 units retained; gates NOT_COMPUTABLE | [MERCURY1_SMOKE.json](MERCURY1_SMOKE.json) |
| Full E60 saved-data reproduction, including extra appendix | Both commands exit 0; all 2,567 scalar values match exactly | [E60_FULL_REPRODUCTION.json](E60_FULL_REPRODUCTION.json); input counts 47/9/26/36 |
| E60 missing/empty input check | 8 tests pass; 6 regression failures before fix | [PR 84](https://github.com/brando90/cert-judge/pull/84) |
| Newly published FarmShare partial, processed-unit gate check | Exit 0; all four gate/statistic fields match exactly | [E58_FARMSHARE_GATE_CHECK.json](E58_FARMSHARE_GATE_CHECK.json); raw harvest verification pending archive |
| Combined E58/E60 tests | 40 passed, 0 skipped, 52.74 seconds | Python 3.12; isolated E60 imports |

Initial full-reproduction attempt used the archive parent instead of its nested `seed0`/`seed1` run roots; it exited 0 with no new units and is not counted as a reproduction. Paths were corrected before interpreting results.

[Findings and protocol gaps](../../RESULTS_analysis_audit.md) · [checkpoint](../../CKPT_analysis_audit.md).

**TLDR-end:** [cert-judge: analysis audit] E58 fixes pass deterministic checks and preserve the saved primary statistic. The independent full E60 reproduction is additional verification of existing data.
