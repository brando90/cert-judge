# 69B and 69C status, 11-26-2026

**TLDR:** The scripts are tested. No model was called. This VM has no API key and no SNAP SSH config. The $27 cap is in the scorer and has not been spent.

What ran here:

- `items_from_ratings` finds 100 files and 250 scores, and repairs T06 `item020` to `task_16_certificate_hostname/agent_lean/agent_2.lean`.
- `score_native6.py --dry-run` writes 100 rows, source `dry_run`, cost $0, a point mass on digit 5.
- `eval_69b.py` on that file: RPS 0.0843 versus CONST 0.0698, difference +0.0145 [+0.0003, +0.0297], `beats_const_rps` false, status `DRY_RUN`. A constant 5 is a worse forecast than the empirical marginal on this ceiling. Spearman is undefined because every expected score is 5.
- `eval_69c.py` on that file: status `DRY_RUN`. Train and validation selection both pick CONST for RPS, so formulation ③ minus ④ is 0. This does not decide the comparison.

What still needs a host with credentials:

- SNAP: `69b/RUN.md`, backend `vllm`, model `Qwen/Qwen3-8B` or `CJ69_SNAP_MODEL`, packet root = trustworthy-theorem-judges experiment 09 `main_rating_task`. Cost $0.
- API: one non-Gemini model, `--usd-per-call` set from a price card, `--cap 27`. The script stops if 100 calls would pass $27.
- Then the same `eval_69b.py` and `eval_69c.py` commands on the measured forecast file. A `source` other than `dry_run` is what the decision rule reads.
