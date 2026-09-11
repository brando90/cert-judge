# Branch consolidation onto main

**TLDR:** The two local development branches are integrated into main. Superseded remote proposals are retained as main ancestors with their original files recoverable by commit, while the current accepted papers, scoring code, and results are retained.

This is historical consolidation, not activation of every old branch proposal. No old experiment is run, no old paper replaces a newer paper, and no new scoring behavior is introduced. Unmerged blog drafts, raw rescue results, and dormant proposals are retained in Git history rather than copied into active directories.

## Snapshot and scope

- Captured: 2026-09-10 20:35 PDT
- Remote base: `c20027dc2b10758b8128adca5d5b93eeacba2653`.
- Local notes tip: `38b1eeaf55dd6919d6968bbfc9d3569b9b78d3e1`.
- Original local main: `d6bc5182a177232f2684fff5726379da56382078`.
- Another process began an experiment-archive reorganization in the shared checkout during this task. That work subsequently landed on the notes branch as `ab96a2014cb7bdd84a2955d0ce0f5e258722974e` and is included by a separate normal merge. Its exact tree is preserved before adding this record; no archive rewrite was authored in this consolidation.

The notes branch and its newly created remote pointer advanced during the task to `ab96a2014cb7bdd84a2955d0ce0f5e258722974e`; both are included in the final ancestry checks. The table below deliberately retains the original snapshot.

## Original branches and disposition

| Original reference | Original commit | Disposition |
|---|---|---|
| `refs/heads/iclr2027-port` | `9f6fb13f3d46af432e0ca2c1698c4da53dca7be1` | Already an ancestor of remote main; no content merge needed. |
| `refs/heads/main` | `d6bc5182a177232f2684fff5726379da56382078` | Integration base; local main contains the original notes commit. |
| `refs/heads/notes-trust-index-sanmi-stability` | `38b1eeaf55dd6919d6968bbfc9d3569b9b78d3e1` | Normal merge; exact same notes bytes as original local main, rebased onto newer remote main. |
| `refs/remotes/origin/appendix-formal-methods-scalable-oversight` | `2e6d830d722823a44498fe684cac4ac4aacf20be` | Only outstanding commit is the patch-equivalent secret-ignore addition; retain newer ignore rules. |
| `refs/remotes/origin/claude/check-agents-config-Ld8Aj` | `a6ed459f06f44013ba14425c625ceba6a40d340a` | Only outstanding commit is the patch-equivalent secret-ignore addition; retain newer ignore rules. |
| `refs/remotes/origin/claude/document-paper-properties-7Wwx9` | `76b849294035969f92e9b11aa77bc338a79bfc5c` | Older seven-property README proposal; current README was replaced by d99c9f9. Retain proposal in history, preserve current documented interface. |
| `refs/remotes/origin/claude/exp16-19-22-opus47-replication` | `e6db982c1ac472a2a3b0a3f5644bb5d43b546e71` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/claude/exp25-geometric-trust-index-reanalysis` | `a1707a26471497b4368774b08b3b4f94b91d05b7` | Closed #17: superseded by current generator and expanded geometric-index results. Preserve original six Haiku artifacts in history. |
| `refs/remotes/origin/claude/exp26-human-label-audit` | `d5e0b136f6637254ce3402b2220dbc2d529fa8b1` | Squash-merged as c1021bf (#37); exact patch equivalent. |
| `refs/remotes/origin/claude/review-project-experiments-78Bdb` | `c352fdde328cd24478551be5354e980e5a20f0d6` | Unmerged April scaled-bug-ladder proposal uses direct provider calls; dormant under current subscription-command-only policy. Preserve original proposal and code in history. |
| `refs/remotes/origin/claude/verify-experiment-files-lxQQn` | `0745509149d440160ff2cebcf574dee2e75a2e2d` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/codex/autojudge-human-corr-val-test` | `1983724cfa076596a5853263fcf5cf3eca9c03ad` | Closed #29: superseded by experiments 41–43 and subsequent label audit. Preserve original implementation/results in history. |
| `refs/remotes/origin/codex/exp12-leanstral-rescue-results-20260501-163023` | `f7a055791ca4806dc8694412c368796f202d96b4` | Closed #21: redundant rescue-run result; original raw run and cache remain recoverable in history. |
| `refs/remotes/origin/codex/handwritten-judge-metric-notes` | `07820c8f160dcf04ce2ead8e5dbd2784117f6ef8` | Closed #25: needed notes salvaged in 932b4d3; retain current papers, preserving prior paper versions in history. |
| `refs/remotes/origin/codex/held-out-human-label-test` | `f0daba23818a581753e0049dee4dc726161022bf` | Closed #27: needed results salvaged in 932b4d3; later held-out analyses supersede this implementation. Preserve dormant style-benchmark proposal in history. |
| `refs/remotes/origin/exp12-leanstral-20260501-1455` | `e364e36fcadd6fe2ea3a192ae6a480473a0fb154` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/exp12-leanstral-20260501-1456` | `5c13a9eb92e95c45c765b2bc2ebf0831d7ef2c04` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/exp13-qwen3.6-27b-20260501-1312` | `8aa713d907ea25c188225e4404fe3bd134a677f4` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/experiments-06-07-cc-prompts` | `ec6195e1fab79ee2417bc0e8402ef3a96cc9e2d2` | Closed #12: old prompts and renamed notes conflict with later cleanup 53fcef6. Preserve original prompts in history without reactivating them. |
| `refs/remotes/origin/feat/mutual-evaluation-p8-p9` | `549b63a1b4fa23ebfb2c03d56bbbb00a5950240c` | Closed #5: unaccepted mutual-evaluation extension. Preserve complete implementation/tests in history without altering the current scoring interface. |
| `refs/remotes/origin/feat/paper-claude-cross-model-validation` | `b10baefd53bdc00eb1236f1bc52da75590a69a02` | Only outstanding commit is the patch-equivalent secret-ignore addition; retain newer ignore rules. |
| `refs/remotes/origin/feat/veribench-p1-p4-scaling` | `54895a0f8e0e5ba37941c533578c851538d8974a` | Only outstanding commit is the patch-equivalent secret-ignore addition; retain newer ignore rules. |
| `refs/remotes/origin/folder-08-p2-bug-ladder-with-ci` | `070958b317b3c74886325eb4a37f786388d095ad` | Only outstanding commit is the patch-equivalent secret-ignore addition; retain newer ignore rules. |
| `refs/remotes/origin/folders-06-07-full-run` | `117dbbdf0865c41586d21c57bdbeaa485d2f849e` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/iclr2027-port` | `9f6fb13f3d46af432e0ca2c1698c4da53dca7be1` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/icml2026-mathai-certjudge-poster` | `798f96abb1b1479425020be2b14607692356ed2b` | Closed #31: main contains the shipped poster. Preserve alternate poster and unmerged announcement drafts in history. |
| `refs/remotes/origin/main` | `c20027dc2b10758b8128adca5d5b93eeacba2653` | Remote integration base. |
| `refs/remotes/origin/paper-neurips2026-clean-migration` | `c087b3ff4d4c1aa8016baab614ae4b20ac9c7cbd` | Already an ancestor of remote main; no content merge needed. |
| `refs/remotes/origin/paper/idea3-amortized-framing-and-val-test-honesty` | `5212cfa31ba45a6161e7edda927cf9104afc7438` | Paper reframing and ignore rules patch-equivalent upstream; ultimate-utils already present in current pyproject.toml. Preserve current paper version. |

## Evidence and recovery

The prior closure decisions are recorded in pull requests [5](https://github.com/brando90/cert-judge/pull/5), [12](https://github.com/brando90/cert-judge/pull/12), [17](https://github.com/brando90/cert-judge/pull/17), [21](https://github.com/brando90/cert-judge/pull/21), [25](https://github.com/brando90/cert-judge/pull/25), [27](https://github.com/brando90/cert-judge/pull/27), [29](https://github.com/brando90/cert-judge/pull/29), and [31](https://github.com/brando90/cert-judge/pull/31). Commit `932b4d33a8303f23a1e2c18da7e6d052b5fe1f41` records the earlier artifact salvage. Closure is evidence of the prior project disposition, not a new instruction to execute.

Every listed commit remains reachable from main after consolidation. To read a retained original file, run `git show <full-commit>:<repository-relative-path>`; to inspect the original changes, run `git show <full-commit>`. For example, `git show 798f96abb1b1479425020be2b14607692356ed2b:blog/2026-07-certjudge-x-thread.md` retrieves the older announcement draft. Branch deletion therefore removes pointers, not the preserved work.

## Verification

- The normal local merge tree is byte-identical to the notes branch before adding this record.
- The normal archive merge and historical merge each preserve the exact tree of `ab96a20`; this record is the only additional file.
- The exact notes source compiled with Tectonic; no TeX errors or undefined references/citations. The existing committed document remains paired with unchanged source.
- The net change versus remote main passes `git diff --check`; whitespace findings relative to stale local main are already present upstream.
- Secret scans passed: 44 original incoming commits (one pre-existing function-name false positive), all 2,481 files in the initial staged merge, and all files in the later archive merge. No credential values were printed.
- Before branch deletion, confirm every captured tip is an ancestor of published main; delete remote pointers with exact old-value guards.

Independent integration review: **PASS; CRITICAL_ISSUES: 0**, fresh `gpt-6-astra` at `ultra`, read-only. The reviewer checked the normal notes merge and the historical-retention plan, including all 29 originally captured references, patch-equivalence claims, and recovered artifacts. Claude Fable 5.1 (`claude-fable-5-1`, max) was usage-blocked; Claude Sonnet 5 (`claude-sonnet-5`, high) exhausted the bounded tool-turn limit after encountering concurrent checkout changes and returned no verdict. The acceptance fallback is same-company and is not claimed as cross-company approval.

The later archive commit `ab96a2014cb7bdd84a2955d0ce0f5e258722974e` is outside the independent review snapshot. It is integrated unchanged from the concurrent author: deterministic integration checks establish that the complete merged tree matches that commit, apart from this consolidation record. This merge does not claim a fresh audit of the archive reorganization's scientific or runtime behavior.

Final verification: every original branch tip and the later archive tip must be ancestors of published main, and its tree must equal the archive tip plus this record. No inference or experiment is executed by this consolidation.
