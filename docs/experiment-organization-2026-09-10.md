# Experiment archive completion and shorter names

**TLDR:** The 00–26 archive cleanup is complete with all five requested exception folders retained, and six active folders now have shorter names explained in the experiment index. Frozen results are preserved, and the relocated runners reproduce the accepted results.

**Last updated:** 2026-09-10 22:01 PDT
**Status:** COMPLETE — shorter names and concurrent main changes verified together.

## Organization

The prior archive work landed in `ab96a20` and its live index in `add161b`.
There are 27 archived directories/links numbered 00–26, including duplicate
numeric prefixes that represent different experiments. Five exceptions stay
under `experiments/`: both reviewer-feedback folders, Leanstral replication,
Total Variation Distance Mutual Information (TVD-MI), and the Epistemically
and Formally Grounded (EFG) baseline. Shared human-label directories remain.

The two retained later experiments are:
- `experiments/27_trust_plots/`: plots of paired human/judge scores and repeated-judgment variation.
- `experiments/29_proxy_validation/`: the completed test of the Proxy Trust Index against human agreement, including its frozen scoring runner and results.

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

## Shorter names follow-up

Six retained folders now use short names, with full purposes in
`experiments/README.md` and rename history in `experiments/archive/README.md`.
All 2,756 tracked files in these folders remain present: 2,728 are byte-identical,
and 28 contain only path, documentation, or runtime-relocation metadata updates.
Frozen configurations, raw results, reference packets, figures, numerical tables,
and saved execution metadata remain byte-identical.

All 89 relevant tests passed; the same pre-existing Lean integration test was
excluded because this change touches no Lean source. The complete outer-correlation
reconstruction, including 10,000-bootstrap uncertainty intervals, exactly matches
the frozen analyses and source rows. The runner still reports 774/774 completed
tasks, zero invalid tasks, and zero remaining tasks. Both changed shell scripts
pass syntax checks, current executable references contain no obsolete names,
and all directory links in the experiment index resolve.

The relocation record additionally records the moved prompt-source path; the
prompt source itself and all numerical protocol fields remain unchanged. The
original frozen-configuration file retains its SHA-256 hash recorded above.

Short-name review: **PASS; CRITICAL_ISSUES: 0; MAJOR_ISSUES: 0.** The independent
reviewer was Codex `gpt-6-astra`, ultra effort, acceptance role, session
`01a08ed3-8d03-7c91-af20-41d70af5f5d7`, against base
`97ef020e752fb001654eb36b8ad67c8b10024999`. Claude's strongest reviewer had already
returned a usage-credit error in this session, so the configured strongest-model
fallback was used; cross-company review was unavailable. It independently
confirmed exact path-only executable changes, unchanged frozen authority and
prompts, strict runtime-drift rejection, and preservation of the symbolic link.
The staged scan found no literal credentials; its one pattern match at
`experiments/02_neurips_reviews/utils/judge_caller.py:475` is an existing function
call, confirmed from the Python syntax tree and unchanged from the base.

## Concurrent main synchronization

Fetched and merged the newer `origin/main` at `7060f6e`, preserving the newly
landed experiment 30 and its numerical validation module. The index conflict was
resolved by retaining every entry and command from both sides. Experiment 30's
reader and findings link now use experiment 29's shorter path; its saved panel
files retain their original provenance. No upstream numerical code was changed.

After integration, **162 tests passed and 1 unchanged Lean integration test was
excluded**. Both experiment-30 saved panels reproduced exactly except for their
updated source-directory metadata; the saved panel files were not overwritten.
Incoming numerical code, tests, and data remain byte-identical to `origin/main`.
All merge conflicts were resolved, and the 11 staged merge files passed the
credential scan and whitespace checks. The short-name change is committed as
`7c7c19f`; the integration retains the fetched upstream commit as a merge parent.
