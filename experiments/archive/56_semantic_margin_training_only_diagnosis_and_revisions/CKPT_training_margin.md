# Training-only margin checkpoint

Created: 10-19-2026 12:03 PDT
Last updated: 10-19-2026 13:13 PDT

## Goal
- Diagnose why semantic margin fails to track human agreement, using cached training scores only, and test two revisions fixed before those scores are read.

## What ran
- 10-19-2026: Codex parent thread `01a118c4-de44-7cf1-9f11-24398173c5b0` died with HTTP 401. Remote tmux `codex-cj-e56-training-margin` is dead. Cursor finished the cached analysis in this worktree.
- Freeze commit `0032fcc` is pushed. Training analysis completed locally. New inference spend: $0.

## Results
- Formatting penalty 0/59 task values; identity baseline 1.000, so headroom equals the original margin on 12/12 configurations.
- Margin vs current-five training agreement: Spearman -0.378, Pearson -0.219, Kendall -0.303, n=12 correlated configurations, p-val=n/a.
- Pooled selection unavailable: 25/30 files, frozen requirement 27. Specificity uses 3 tasks and does not reverse the direction.
- Repeat total variation on the same rows: 0.111 to 0.267; Spearman with training agreement 0.210, p-val=n/a. Identical-repeat rate versus agreement is Spearman -0.158.

## Stuck / blocked
- nothing

## Next steps
- none. The study is complete and archived in this completion commit.

## Brando to-do
- none

## Log
10-19-2026 12:41 PDT -- Froze the protocol, two revisions, and the training-only source manifest before reading scores. Took over after the Codex parent returned HTTP 401.
10-19-2026 12:46 PDT -- Training diagnosis completed. Both revisions are algebraically idle on this cache, and the margin association with agreement is negative. Selection stays unavailable under the 90% rule.
10-19-2026 13:13 PDT -- Addendum: gold-free repeat total variation on the frozen training rows spans 0.111 to 0.267 and does not track agreement. No new formula and no validation or test rows.
