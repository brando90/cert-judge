# V5 sandbox checkpoint

**Doc link:** [Experiment README](README.md)
Created: 10-08-2026 10:05 PDT
Last updated: 10-08-2026 10:48 PDT

- Objective: finish `47_simulated_panel_v5_label_free_judge_screening`, without accessing prospective data.
- Master: Codex desktop chat `01a11c71-b74c-7dd3-a249-ca3d28526f39` (local orchestrator, full access / never approvals).
- Local owned checkout: `/Users/brandomiranda/.codex/worktrees/cj-v5-sandbox/cert-judge`.
- Branch: `codex/cj-e47-v5-simulated-sandbox`; base `d012e140d7c53f3db4cb7be9db11faf436d3d8e3`.
- Reserved remote checkout: `/dfs/scratch0/brando9/cert-judge-e47-v5-sandbox`; worker session `codex-cj-e47-v5-sandbox` on skampere1.
- Source: VeriBench `ccd86d467fd7577826c4b549df2c532bf43b1892`; strict v5 allowlist in PROTOCOL.md.
- Protocol: frozen at commit `d38359a673dbc762e18488f3b9d6e6bd45622ecd`, SHA-256 `513f394cfdf00f1fbc45b84026746af11e40cd003a639246ae354eacb29eb174`; amendment 01 is present. No criterion statistic or experiment-47 measured call has run.
- Owner handoff: `AMENDMENT_01_owner_information_properties.md` freezes the October 7 owner's `repeat_tvd` and `deletion_tvd` definitions; `semantic_auc` remains pending audited strict-weakening and formatting probes. Do not invent replacements.
- Remote health: skampere1 relevant checks PASS; shared storage warning has 4.4 TiB free, bounded expected work under 100 GiB; no cleanup needed.
- Executor selection: attempt 1 (`gpt-6.1-sol`, high) was rejected as unsupported before useful work; attempt 2 is live as `gpt-5.6-terra`, high, with `--dangerously-bypass-approvals-and-sandbox`, verified by the supervisor process tree and recorded in `expt_v1/runtime/worker_ack.json`. Exact historical measured judges remain unchanged.
- Preliminary measured-call estimate: zero in phase 1; later likely tens of thousands of calls, approximately USD 1,500–5,000 using prior experiment-39 cost per call as an order-of-magnitude anchor, uncertain for agent judges. Worker must replace with exact frozen-manifest quote before admission. Estimate is NOT a cap; no spend-triggered stops or sample/model reductions. Vals-funded Valkyrie only.
- Source boundary: owned no-checkout clone at `expt_v1/sources/veribench_v5`, `git ls-files` count 0, has pinned commit `ccd86d467fd7577826c4b549df2c532bf43b1892`; only the v5 allowlist and named v5 helpers have been inspected with `git show`. The source host `skampere2` is reachable by SSH, but its live checkout HEAD is `39a75301160f38137a702ded9e84363a0e30be99`, so committed metadata stays pinned and each copied runtime input must carry its source-host hash.
- Zero-call reconstruction: verified from 28 copied, hash-recorded v5 runtime cell files, including six recovery streams. The frozen resolver accepted 3,847 recovery receipts and ignored 44; it uses canonical declared model identity and does not let recovery overwrite measured/parser-error originals. The fresh pool has 750 declared rows (G01–G13 plus G16/G17), 691 nonblank rows, and complete primary persona, instructions-only, and common-family-excluded targets for all 691 nonblank rows; blank rows are frozen deterministic zero. G00's 75 old-anchor rows are explicitly excluded. Reconstructed G01–G13 targets match all 650 saved frozen targets at six-decimal precision; late G16/G17 have no saved target file. Receipt: `expt_v1/results/zero_call_inventory.json`; targets: `expt_v1/results/targets_reconstructed.json`.
- Input provenance: all six pinned v5 metadata files were compared on skampere2 with `git show ccd86d...:<allowed-path>` before copy; each working-file SHA-256 equals the pinned object content SHA-256. Raw cells and late candidates are kept ignored under `expt_v1/private/`; their individual SHA-256 values are in the sanitized receipt.
- Amendment 02: mailbox/source verification established `GM_mono2 = geometric_mean(ms_gold, ms_cand)`, not reference deletion plus bug monotonicity. `AMENDMENT_02_frozen_GM_mono2_erratum.md` was written before property/criterion measurement; candidate deletion ladders and their declared cells are required. It is candidate-dependent for group/task transfer as specified there.
- Verified checks: `python3 expt_v1/test_analyze_cached.py`; `python3 expt_v1/analyze_cached.py --check`; `python3 -m py_compile expt_v1/analyze_cached.py`; `git diff --check`.
- Next: implement exact historical 12-configuration cache-overlap parsing and missing-cell manifest using copied E39 selectors, harness receipts, and v5 H0/H2 cells. Build/validate all reference and candidate-deletion ladders before freezing the scoring manifest.
- Completion: all declared outputs reconciled, deterministic checks, pull request merged, landing receipt verified. A finished phase is not whole-task completion.
