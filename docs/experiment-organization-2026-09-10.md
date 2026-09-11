# Experiment archive completion and descriptive names

**TLDR:** The 00–26 archive cleanup is complete with all five requested exception folders retained, and experiments 27 and 29 now state their purpose in their names. Frozen results are preserved; the incomplete archive move’s runtime paths and frozen-configuration integrity were repaired.

**Last updated:** 2026-09-10 21:19 PDT
**Status:** COMPLETE — verified and ready to publish on main.

## Organization

The prior archive work landed in `ab96a20` and its live index in `add161b`.
There are 27 archived directories/links numbered 00–26, including duplicate
numeric prefixes that represent different experiments. Five exceptions stay
under `experiments/`: both reviewer-feedback folders, Leanstral replication,
Total Variation Distance Mutual Information (TVD-MI), and the Epistemically
and Formally Grounded (EFG) baseline. Shared human-label directories remain.

The two retained later experiments are:
- `experiments/27_judge_human_agreement_and_stability_plots/`: plots of paired human/judge scores and repeated-judgment variation.
- `experiments/29_proxy_trust_index_vs_human_agreement/`: the completed test of the Proxy Trust Index against human agreement, including its frozen scoring runner and results.

Former-to-current names are recorded only in `experiments/archive/README.md`.
Live command examples, tests, figure-module documentation and supplement paths
point to the renamed directories. The archived human-study link now resolves
to the corresponding archived directory in the sibling VeriBench checkout.

## Integrity and runtime repairs

All 2,423 tracked files in the two renamed trees are still present. Raw results,
reference packets, figures, numerical tables, requests and accepted score
records are byte-identical to the state before this task.

The earlier archive commit rewrote provenance paths inside the frozen
configuration without updating its embedded fingerprint. Restored the exact
pre-archive file (file hash
`933920bd349a28c7ae088abf4c532483eb46ab39ff05dc510c9931ce23b7691f`),
retaining configuration fingerprint
`735bd5951d4e6f8e9bf5f0d5e374028e1e46d92077b64584a7f89ff30981be9e`.
`runtime_relocation.json` pins this authority to the complete current runtime
fingerprint, including runner and source-input hashes. Unknown runtime changes
or a modified/rehashed authority fail verification. Its listed metadata changes
cover only paths and the source hashes affected by relocation repairs.

Corrected repository-root depth and input defaults in archived scripts still
used by the retained Leanstral runbook and human-label audit. No new judge
inference, human relabeling, numerical-method changes, or remote report writes
were performed.

## Verification

- 70 tests passed across the metric, pipeline, publisher and plotting suites.
- 19 probe-validation unit tests passed; one real Lean-toolchain integration test was excluded after the broader run timed out initializing the pre-existing local project dependencies (60 seconds); no Lean source changed.
- All three experiment-27 demo plots reproduced in a temporary output directory; each correlation matched the stored result exactly.
- Experiment 29 reproduced all eight judges’ point estimates, counts and coverage for three human-rating views exactly; the check used 20 bootstrap iterations in temporary files rather than overwriting the frozen 10,000-iteration uncertainty estimates.
- Renamed-runner status: 774/774 completed command-line tasks, zero invalid raw tasks, 4,728 unique score cells, zero remaining inference tasks.
- Full outer-correlation reconstruction matches the frozen result exactly, including all analyses and 10,000-iteration uncertainty intervals, after restoring historical-commit verification across directory renames.
- Required retained directories and archived Leanstral input/import paths resolve.
- Staged credential scan and whitespace checks passed before publication.

## Independent quality assurance

Review scope: base `add161bd669683ebeb29d51f5b329fd95a2517f3` through this task’s
staged changes. Claude `claude-fable-5-1` at maximum effort returned a usage-credit
error before review. Under the critical-change fallback procedure, the acceptance
review uses a fresh Codex `gpt-6-astra` context at ultra effort; cross-company
review is therefore unavailable for this change. No paid model-provider keys or
extra credits were used.

Reviewer verdict: FAIL with 0 critical issues and 1 major issue: the pre-result
Git commit records the properties file under its former directory name, so
verification at its renamed path failed. Fixed by resolving a unique same-named,
byte-identical blob in that historical commit when the current path is absent;
the ancestor requirement and exact content checks remain enforced. Four real
Git-repository test cases cover moved/unmoved and intact/modified authorities.
The complete outer-correlation result was then reconstructed exactly.

Final reconciled verdict: **FIXED; CRITICAL_ISSUES: 0; unresolved major issues: 0.**
Reviewer model: `gpt-6-astra`, ultra effort, acceptance role. Original review
session: `01a08eab-9d8b-7372-8c39-6df77dbea83d`. This was one independent review
round followed by deterministic verification of the fix; no second round.
