# Training-only margin checkpoint

Created: 10-19-2026 12:03 PDT
Last updated: 10-19-2026 12:41 PDT

## Goal
- Diagnose why semantic margin fails to track human agreement, using cached training scores only, and test two revisions fixed before those scores are read.

## What ran
- 10-19-2026: Codex parent thread `01a118c4-de44-7cf1-9f11-24398173c5b0` died with HTTP 401 before analysis. Remote tmux `codex-cj-e56-training-margin` on skampere1 is dead. Cursor continued in this worktree.
- Definitions, tests, and the train-only source manifest are frozen. Human scores and judge scores have not been read by the analysis yet.

## Results
- none yet

## Stuck / blocked
- nothing

## Next steps
1. `python3 experiments/56_semantic_margin_training_only_diagnosis_and_revisions/scripts/train_only_projection.py --project`
2. `python3 experiments/56_semantic_margin_training_only_diagnosis_and_revisions/scripts/analyze_training_margin.py`

## Brando to-do
- none

## Log
10-19-2026 12:41 PDT -- Froze the protocol, two revisions, and the training-only source manifest before reading scores. Took over after the Codex parent returned HTTP 401.
