# Cached score judge selection utility results

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/results.md>

**Status:** DONE — merged and archived
**Last updated:** 10-05-2026 23:20 PDT

The fixed-selector, cached-score analysis is complete. Prior inspection of pooled/subset associations and reuse of human-rated items make this follow-up exploratory.

| Phase | State | Evidence |
|---|---|---|
| Repository refresh | DONE | main fc73f78; layout check passed |
| Input inventory | DONE | frozen item fingerprint and existing harvests located |
| Analysis protocol | DONE | PROTOCOL.md |
| Remote implementation, checks and analysis | DONE | 9 deterministic tests passed; real 10,000 task-cluster-draw analysis completed with seed 44 |
| Report and receipts | DONE | `RESULTS_selection_utility.md`, compact JSON tables, source hashes, frozen criterion matrix, and repeat diagnostics |
| Archive and publication | DONE | final checks passed; pull request #55 merged; landing receipt below |

Corrected ownership receipt: the initially monitored PID was this session, not a separate executor; the interrupted self-monitoring produced no work or input changes. Actual executor was Codex CLI `gpt-5.6-terra` at high effort on skampere1 with `--dangerously-bypass-approvals-and-sandbox`.

Primary full-context/original-45 common-support result (42 items/15 tasks): proxy selection chose `t2_sonnet5|D0` and achieved Spearman 0.768, compared with fixed-H2 0.853 and random 0.784. The paired proxy-minus-H2 difference was -0.086 (95% task-cluster percentile interval [-0.308, 0.058], 10,000/10,000 finite paired draws; p-val=n/a); proxy-minus-random was -0.017 ([-0.162, 0.080]). The train/validation-only transferred-prompt procedure selected H2. Two broad-pool reference-quality comparisons were correctly unavailable at the 90% common-support rule (32/36 and 24/27 items).

Finalization checks added repeat-slot missingness on the current common mask (three declared slots per item), immutable before/after hashes for all frozen source metadata and 60 committed harvest exports (including deterministic controls), and 10,000-draw expected Pearson/Kendall intervals alongside Spearman. The source hash equality gate, 9 deterministic tests (including tied/constant correlation cross-checks against SciPy), archived-path rerun, layout check, and whitespace diff check passed.

**TLDR-end:** [cert-judge: 44_cached_score_judge_selection_utility] The saved-score judge-selection study completed a verified zero-inference cached-score analysis; the frozen proxy did not demonstrate an advantage over the fixed human-mirror rubric in the primary exploratory comparison.

Final verification 10-05-2026 23:14 PDT: all 9 tests, source-revision fingerprint checks, and the corrected archived-path 10,000-draw run passed. These checks passed before publication; no judge inference or new human labels.

Confirmed publication: [pull request #55](https://github.com/brando90/cert-judge/pull/55), merge commit 208b8825db13184e39a4e88103349bc3566c5a02. All owned implementation and verification workers have exited; the study is complete.
