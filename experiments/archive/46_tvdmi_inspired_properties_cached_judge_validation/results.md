# Live results: information-inspired historical judge properties

**Doc link:** [experiment](https://github.com/brando90/cert-judge/tree/codex/cj-e46-tvdmi-properties/experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation).
**Summary:** Corrected offline analysis over allowlisted measured caches completed; no inference was performed.
Status: COMPLETE and archived pending landing (started 10-08-2026 10:04 PDT; corrected evaluation completed 10-08-2026 10:26 PDT).
Inference budget and route: zero calls, zero new inference charges; approved authenticated Codex command-line worker for implementation only.
Set N, new rating sheets, private sealed files, simulated v5 pre-runs and manuscript edits are out of scope.

Launch target: skampere1; dedicated checkout cert-judge_e46; persistent session codex-cert-judge-e46-tvdmi.
Expected worker: gpt-5.6-terra / high, full access and no routine approvals. Actual launch receipt pending.

| Phase | Status | Evidence |
| --- | --- | --- |
| Protocol and allowlist inspection | DONE | `PROTOCOL.md` read; only experiments 39, 42, archived 44, and archived 45 sources are in scope. |
| Source freeze | DONE | `results/input_manifest.json` freezes 155 allowlisted source and code hashes before cache analysis. |
| First-pass preservation | DONE | The exited PID 3947201 was verified absent; its generated outputs were copied to `diagnostics/first_pass_invalid_20261008T102133_PDT_results/` with a SHA-256 receipt before replacement. Those results are invalid/superseded. |
| Implementation corrections | DONE | Repeat eligibility now uses any >=2 complete three-repeat candidates while retaining declared task denominators; the prior semantic baseline calls E45's exact `semantic_rows`, `semantic`, and `measure_rows` helpers. |
| Pure functions and deterministic tests | DONE | Eight deterministic tests pass: exact 0.5 balanced/reversed repeat controls, constant/cube controls, duplicate rejection, repeat subset eligibility, all coverage rules, semantic ties, direction gates, and unequal cluster bootstrap handling. |
| Selector freeze | DONE | `results/selectors.json` contains train-only weights for 56 configurations and the fixed 12-configuration pool before outcome evaluation. |
| Offline property calculation and bootstrap | DONE | 56 configuration rows and a 10,000-draw paired task-cluster evaluation were recomputed after the corrections. |
| Archive | DONE | Moved with `git mv` to `experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/`; archive layout check passed. |
| Landing | PENDING | Commit, push, pull request, exact-head rebase merge, and landed receipt. |

Key historical-test result: repeat-TVD selection gives Spearman 0.844 [0.472, 0.951] versus fixed H2 0.826 [0.507, 0.934], paired difference +0.018 [-0.127, +0.186]; it is inconclusive and exploratory.
Deletion-TVD is unavailable for all 56 configurations because cached `ms_gold` levels intentionally have one accepted repeat where the frozen property requires two; [ERRATA.md](ERRATA.md) corrects the frozen ladder wording without changing `PROTOCOL.md` bytes.

Next command: `git add -- <owned paths>; git diff --cached --check; git commit -- <same-owned-pathspecs>`.

**TLDR-end:** [cert-judge: e46 historical measured-cache information properties] The zero-inference study is running from the frozen protocol and allowlist; source hashes are the immediate next artifact.

**Snapshot:** The active analysis is limited to published measured caches and rater artifacts; no provider credential or inference route is used.
