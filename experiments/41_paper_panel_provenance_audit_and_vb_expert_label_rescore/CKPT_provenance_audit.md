# Checkpoint: experiment 41 provenance audit

**Last updated:** 09-30-2026 14:42 PDT

LANDED da61634b2fd32185423059b7753de3f7d622f131 https://github.com/brando90/cert-judge/pull/50 09-30-2026 14:42 PDT
**Worker:** Claude Sonnet 5, effort high, tmux `cj-e41-provenance-audit`, skampere1
**Branch:** `e41-provenance-audit` (clone: `/lfs/skampere1/0/brando9/cert-judge_e41`)
**Model calls so far:** 0 (zero-call analysis; this is a text/data audit)

## Environment
- Python: created `uv venv /lfs/skampere1/0/brando9/venvs/cj_e41` (vb103_venv lacked numpy/scipy/pandas) and
  `uv pip install --python /lfs/skampere1/0/brando9/venvs/cj_e41/bin/python numpy scipy pandas` (numpy 2.4.6,
  scipy 1.17.1, pandas 3.1.0rc0).
- Read-only VeriBench clone: `/lfs/skampere1/0/brando9/veribench_e41` (never commit there).
- Did not touch experiment 39's folder, checkout (`cert-judge_e39`), Valkyrie benchmark, or ports 8990-8998.

## Progress
- [x] Step 0: snap_health.sh run (WARNs are pre-existing on unrelated shared-dfs repos, not this task).
- [x] Step 1: branch `e41-provenance-audit` created off `origin/main`; this checkpoint created; `results.md` set to RUNNING.
- [x] Step 2: label identity matching (`results/label_identity.json`) — confirms cc.md's claims exactly:
  paper pass1 == VeriBench old_prompt participant1 pass_2 on 75/75 items; paper pass2 ==
  old_prompt participant1 pass_1 on 72/75 items (72/75 because 2026-05-05 commit bc8d19c
  "changed pass1 replicated ratings" touched 3 items after the paper's copy was frozen).
- [x] Step 3+4: rating dates + judge-seen/rater-seen references (`results/provenance_by_task.csv`,
  `scripts/provenance_audit.py`). Method: (a) judge-seen = cert-judge's own vendored gold copy
  `data/veribench_dataset/lean_src/veribench/` (DEFAULT_VERIBENCH_ROOT in
  exp16_multi_judge_human_sets.py), untouched in git since 2026-04-12 -- i.e. BEFORE VeriBench's
  own annotation window even starts (2026-04-21); (b) rater-seen = VeriBench origin/main gold
  bytes as-of the git commit date that introduced each label TSV (pass1/pass2 both added in the
  same commit 2026-05-03T15:11:53, so pass1/pass2 cannot be distinguished by date -- documented
  as a limitation, not resolved further). Result: of 25 paper tasks, 1
  (0_unsafeMultiply_safe.lean) was silently skipped by the frozen judge pipeline itself
  (`skipped_pairs.csv` reason=missing_gold -- the file was renamed to 1_unsafeMultiply_safe.lean
  before 2026-04-12 and the label TSVs use the stale name), leaving 24 scored tasks; of those,
  only 7 have judge-seen bytes == rater-seen bytes (spot-checked binary_search.lean: a
  2026-05-03T02:35 "Add gold-standard binary search and DFS proofs" rewrite, well after the
  2026-04-12 vendor freeze, is the mismatch mechanism there). This is a DIFFERENT, stricter
  comparison than experiment 100's provenance.json (which compares its own 2026-09 snapshot to
  the 2026-04-20 window start and finds 9/25 differ) -- report both, do not conflate.
- [x] Step 5: Gate G0 (`results/G0_reproduction.json`, `scripts/gate_g0.py`) -- **PASS**. Codex
  avg/pass1/pass2 rho_ti_vs_human = 0.833333/0.904762/0.738095, matching the paper's quoted
  0.833/0.905/0.738 to 3dp exactly. Also recorded (not paper-quoted, for reference): Claude Opus
  0.643/0.810/0.595, Qwen3-Coder 0.905/0.476/0.857.
- [IN PROGRESS] Step 6: Views V1-V5, S1, S3 (`scripts/rescore.py`, running -- task-clustered
  bootstrap with N_BOOT=10000 x 3 families x 5 views in pure Python is slow, ~5+ min).
  `scripts/test_rescore.py` written (6 tests: spearman/kendall/pearson vs scipy, constant-input
  NaN, exact permutation p on a known case + brute-force cross-check, bootstrap seed
  reproducibility) -- not yet run pending rescore.py module import working.
  S4 needs no new computation: `results_exp19_low_variance_replot/bug_reversal_rates.csv`
  (already frozen, archived) shows BAD_STRINGY (the lexical judge) reverses on 20/24 bug ladders,
  matching README's S4 claim exactly; bug ladders are built directly from the frozen gold file
  and scored with no human label or cross-file reference involved, so this check is
  architecturally unaffected by reference provenance -- will cite, not recompute.
- [x] Step 6 (rest): views V1-V5, S1, S3 computed via `scripts/rescore.py` (vectorized after an
  initial pure-Python version was too slow (killed after 13min still running); rewrote the
  bootstrap's per-judge Spearman with a numpy-only `_fast_spearman`, cross-checked against scipy
  in `test_rescore.py::test_fast_spearman_matches_scipy`; second run completed in 6.5 min).
  8/8 offline tests pass. Reading: INCONCLUSIVE (V3: Codex +0.333, Qwen +0.667, Opus -0.381 --
  one family negative, not two; not all three positive).
- [x] Step 7: REPORT.md written (G0, label identity, provenance table, V1-V5 table, S1/S2/S3/S4,
  drafted §5.1/§6 replacement sentences, unmeasured items disclosed). `results.md` set to DONE,
  experiment README status line added, `experiments/README.md` row updated.
- [x] Step 8: landed. PR #50 merged via `gh pr merge --rebase --match-head-commit --delete-branch`,
  confirmed MERGED via `gh pr view 50 --json state,mergeCommit,url` (state=MERGED, merge commit
  da61634). Rebase diff review (`git diff e41-backup-09-30-2026-1458 HEAD`) showed zero content
  loss -- only main's new unrelated file appeared. Remote task branch confirmed deleted
  (`git ls-remote --exit-code --heads origin refs/heads/e41-provenance-audit` -> exit 2). Local
  `main` fast-forwarded to da61634. Email receipt + `private/DONE`: next.

## Notes / deviations
(none yet)

## Resume instructions
If interrupted, re-read this file and `results.md`, then continue from the first unchecked step above.
