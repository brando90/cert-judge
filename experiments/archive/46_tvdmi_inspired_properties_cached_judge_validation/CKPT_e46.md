# Checkpoint: historical measured-score information properties

**Doc link:** [experiment](https://github.com/brando90/cert-judge/tree/codex/cj-e46-tvdmi-properties/experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation).
**Summary:** Exact definitions are being executed offline from frozen measured caches.
Last updated: 10-08-2026 10:31 PDT.

## Ownership

Master: cert-judge owner chat, owned worktree /Users/brandomiranda/.codex/worktrees/tvdmi-properties/cert-judge, branch codex/cj-e46-tvdmi-properties.
Worker target: skampere1, /lfs/skampere1/0/brando9/cert-judge_e46, persistent session codex-cert-judge-e46-tvdmi. One worker writer after dispatch. No scheduled automation created. Master watches while active; remote wrapper allows one bounded restart if worker fails, never overlaps writers. This is not a reboot-persistence claim.
Parallel helper owns experiment 47 simulated v5 sandbox; it consumes this protocol and does not own these definitions or measured historical run.

## Verified preflight

SNAP health completed with exit 0: node reachable, enough node-local disk, Python 3.12.3 with NumPy 2.2.6 and SciPy 1.17.1, approved Codex 0.154.0 logged in. Canonical runtime advertises gpt-5.6-terra/high. Distributed filesystem utilization warning does not prevent this small node-local job. Remote agents-config has unrelated dirty files; preserve them. Local original checkout has unrelated untracked files; use owned worktree.
Estimated new inference spend: $0. Three historical score functions, all 56 measured configurations, fixed 12-configuration utility pool; no sampling to save cost. Execution-worker subscription tokens only, bounded to task completion and available account allowance. Do not purchase credits or use provider keys.

## Correction receipt and continue

- 10-08-2026 10:21 PDT: verified old evaluation PID 3947201 had exited. Preserved first-pass generated outputs as invalid/superseded diagnostics at `diagnostics/first_pass_invalid_20261008T102133_PDT_results/`, with `diagnostics/first_pass_invalid_20261008T102133_PDT_sha256.txt`; no first-pass value is used as a claim.
- 10-08-2026 10:24 PDT: corrected repeat eligibility to use at least two complete candidates while retaining task denominators and reporting exclusions. Corrected the prior semantic baseline through direct calls to E45 `semantic_rows()`, `semantic()`, and `measure_rows()`, retaining all valid formatting probes and both 80% family denominators.
- 10-08-2026 10:26 PDT: refreshed 155-file source/code SHA-256 manifest, froze selectors before ratings, and recomputed 56 configurations with 10,000 paired task-cluster draws. A varying 2/3-file cluster bug in the first corrected evaluator was fixed by same-length vectorized draw buckets; no inference or source-data change occurred.
- Runtime receipt is authoritative: both the initial and correction Codex session metadata report `gpt-5.6-terra`, `high`, `approval_policy=never`, and `sandbox_policy.type=danger-full-access`; see `results/runtime.json`.
- `PROTOCOL.md` SHA-256 remains `64c1ae05fe294c3115f5714934eed7ddda399acd95366fb0d126f77f47cc8568`, matching the frozen manifest. `ERRATA.md` corrects its deletion-ladder prose without modifying it.
- 10-08-2026 10:31 PDT: archived with `git mv` at `experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/`, updated `experiments/archive/layout.json` and `experiments/README.md`, made the offline scripts archive-aware, and reran the full 10,000-draw analysis. Eight tests, the archive-layout check, `git diff --check`, and all 155 frozen source/code hash comparisons passed.

## Next exact command

`git add -- experiments/README.md experiments/archive/layout.json experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation py_src/cert_judge/information_properties.py tests/test_information_properties.py && git diff --cached --check && git commit -- <same-owned-pathspecs>`

## Execution receipt and current checkpoint

- 10-08-2026 10:07 PDT: first useful work completed: read the local `PROTOCOL.md`, input schemas, local `AGENTS.md`, and refreshed `~/agents-config/INDEX_RULES.md`.
- Host: `skampere1.stanford.edu`; Codex CLI `0.154.0`; authoritative session identifiers are in `results/runtime.json`.
- Effective session policy observed: `approval_policy=never`, `sandbox_policy.type=danger-full-access`; configured master defaults remain `gpt-6-astra/ultra` and were not changed.
- Actual execution receipt is `gpt-5.6-terra/high` in both initial and correction session metadata; raw environment traces are not used as model pins.
- No worker was dispatched and no provider/model call, credential load, private path, or disallowed experiment path was used.
- 10-08-2026 10:18 PDT: wrote the initial source receipt before calculations; the final archive-aware receipt contains 155 allowlisted source/code hashes.
- Superseded next command: `python3 experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/scripts/freeze_inputs.py && PYTHONPATH=py_src python3 -m unittest tests/test_information_properties.py -v`.
