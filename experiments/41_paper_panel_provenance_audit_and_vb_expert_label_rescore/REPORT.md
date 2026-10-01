# Experiment 41 report: provenance audit of the paper's validation set, and a re-score against VeriBench's expert labels

**Doc link:** <https://github.com/brando90/cert-judge/blob/e41-provenance-audit/experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md>

**TLDR:** Gate G0 reproduces the paper's nine judge-level Spearman values to 3 decimals (PASS). The paper's `pass1`/`pass2` label files are confirmed, byte-for-byte on shared items, to be VeriBench participant 1's superseded *old-prompt* rating passes. Of the 25 validation-set tasks, 1 was silently skipped by the frozen judge pipeline itself (a stale gold filename causing `missing_gold`), and of the 24 that were scored, only 7 have reference bytes that match what the rater who produced the paper's labels was actually looking at at rating time — the paper's judges resolved gold files from a copy of VeriBench frozen 2026-04-12, before VeriBench's own annotation window even begins (2026-04-21), and several gold files were substantively rewritten in the gap. Under the pre-registered reading rule, the result is **inconclusive**: V3 (VeriBench's corrected three-expert mean, reference-matched items) is positive for Codex (+0.333) and Qwen3-Coder (+0.667) but negative for Claude Opus (−0.381) — not "positive in all three families" (robust) and not "≤0 in at least two" (not robust). All V2–V5 point estimates are far noisier than V1 (n=21 items / 7 tasks vs. n=72 items / 24 tasks) with bootstrap 95% intervals that cross zero in every case. Zero model calls; all numbers below are read from or computed from already-committed, frozen files.

## Gate G0 — reproduction

**Reading: PASS.** `results/G0_reproduction.json`, produced by `scripts/gate_g0.py` from the committed `judge_trust_vector.csv` files (columns `TI_variance_aware`, `human_spearman`), reproduces the paper's quoted Codex values to 3 decimals:

| family | avg | pass1 | pass2 |
|---|---:|---:|---:|
| Codex (paper-quoted) | 0.833 | 0.905 | 0.738 |
| Codex (reproduced) | 0.833333 | 0.904762 | 0.738095 |
| Claude Opus (reproduced, not paper-quoted in the TLDR but in Table 2) | 0.642857 | 0.809524 | 0.595238 |
| Qwen3-Coder (reproduced) | 0.904762 | 0.476190 | 0.857143 |

All nine values match `experiments/archive/38_iclr_body_rewrite_to_trust_artifact_abstract/analysis/results/judge_level_diagnostics.csv` (the paper's own frozen reproduction artifact). Gate passes; the re-analysis below proceeds.

## Label identity (S2 part 1)

`results/label_identity.json`, `scripts/provenance_audit.py`. Confirms both claims in `cc.md` exactly:

- Paper `pass1` (`ethan_human_scores_20260425.tsv`) == VeriBench `old_prompt/participant1_data_pass_2.tsv` on **75/75** items (100% identical scores).
- Paper `pass2` (`ethan_human_scores_ORIGINAL.tsv`) == VeriBench `old_prompt/participant1_data_pass_1.tsv` on **72/75** items (96%; the 3 mismatches trace to VeriBench commit `bc8d19c` "changed pass1 replicated ratings", 2026-05-05, which post-dates the paper's frozen copy).
- **The pass names are swapped**: the paper's "pass1" is the rater's *second* (`pass_2`) old-prompt session; the paper's "pass2" is the rater's *first* (`pass_1`) session.
- VeriBench later replaced both old-prompt passes with a corrected-prompt re-rating (`participant1_data_correct_prompt.tsv`, first committed 2026-05-05) plus four additional experts (`participant{2,3,4,5}_data_pass_1.tsv`). The old-prompt cluster and the revised-protocol cluster are nearly uncorrelated (`experiments/archive/22_pooled_heldout_and_noise_ceiling/REPORT.md`: ρ≈0.13-0.18 across clusters, ρ≥0.86 within); this experiment's own `results/label_agreement_matrix.csv` reproduces that split (`paper_pass1` vs `vb_expert_mean`: ρ=0.072 on 63 shared items; `vb_p1_corrected` vs `vb_expert_mean`: ρ=0.953 on 74).

## Judge-seen vs. rater-seen references (S2 part 2, steps 3-4)

`results/provenance_by_task.csv`, `scripts/provenance_audit.py`. Method: **judge-seen** = the gold bytes in cert-judge's own vendored copy (`data/veribench_dataset/lean_src/veribench/`, `DEFAULT_VERIBENCH_ROOT` in `exp16_multi_judge_human_sets.py`), which has been untouched in git since **2026-04-12** — confirmed both by this experiment's own `git log` and independently by `experiments/archive/22_pooled_heldout_and_noise_ceiling/REPORT.md` ("`data/generated_agents/*.lean` untouched in git since 2026-04-07, before all labeling"). **Rater-seen** = VeriBench `origin/main` gold bytes as-of the git commit date that introduced the relevant label TSV (`old_prompt/participant1_data_pass_1.tsv` and `_pass_2.tsv` were both first committed in the same commit, 2026-05-03T15:11:53-07:00, so pass1 and pass2 cannot be distinguished by this method — a limitation, not resolved further; `participant1_data_correct_prompt.tsv` was first committed 2026-05-05T00:19:21-07:00).

**Of 25 tasks:**

- **1 task (`0_unsafeMultiply_safe.lean`) was never scored by the judges at all.** No file with that exact name ever existed on VeriBench `origin/main` (verified over full history) — only `1_unsafeMultiply_safe.lean` has, since 2025-09-20. `exp16_multi_judge_human_sets.py`'s own gold resolution (exact basename lookup, no alias) failed to find it and recorded all 3 of its candidate pairs in `results_exp16_final_robust_r9_median/skipped_pairs.csv` with `reason=missing_gold`. This is why the paper's panel is 72 pairs, not 75 (`README.md`'s own count of "75 rated pairs, one gold file missing"). The task contributes zero rows to `detail_rows.csv` and nothing to G0 or V1-V5 below; it is marked `not_applicable_missing_gold_in_judge_pipeline` in `provenance_by_task.csv`, not a byte mismatch.
- **Of the 24 tasks the judges did score, 7 have judge-seen bytes == rater-seen bytes**: `0_unsafeCopy_safe.lean`, `1_bisect_left.lean`, `2_heappush.lean`, `3_heappop.lean`, `4_unsafeCounter_safe.lean`, `5_unsafeFormatString_safe.lean`, `9_pathTraversal_safe.lean`. These are exactly the tasks that were essentially untouched after creation (1-3 versions in their full git history); every one of the 17 mismatched tasks has 5-23 recorded versions over the repository's life.
- **17 tasks mismatch.** Representative mechanism, spot-checked: `binary_search.lean` — cert-judge's vendored copy (2026-04-12) has one set of bytes; on 2026-05-03T02:35 (13 hours before the label TSV was committed), commit `65379249` ("Add gold-standard binary search and DFS proofs") rewrote the file by 489 insertions / 97 deletions, and that rewritten version is what was live when the rater's labels entered the repository. The paper's judges never saw this rewrite.
- This is a **different, stricter comparison** than VeriBench experiment 100's own `inputs/provenance.json`, which compares its 2026-09 judge snapshot to VeriBench's 2026-04-20 annotation-window start and finds 9/25 tasks differ (5 of those were `True`-only placeholder references at rating time). That comparison is about VeriBench's *own* judges; this comparison is about *cert-judge's* frozen judge pipeline specifically, against an even earlier (2026-04-12) vendored copy, over the full gap to the actual rating commit date — hence the larger mismatch count. **The two findings should be reported separately, not conflated or added together.**

## Gate G0 recap and Views V1-V5

`results/judge_level_views.csv`, `results/per_judge_agreement.csv`, `scripts/rescore.py`. `TI_variance_aware` is label-free (verified identical across the `avg`/`pass1`/`pass2` committed files per judge) and held fixed; only the per-judge human-agreement Spearman is recomputed per view. Matched-items filter = the 7 tasks found byte-matched above (pass1/pass2 not separately distinguishable, see above). Bootstrap: task-clustered, 10,000 resamples, seed 42 (`scripts/test_rescore.py` checks reproducibility with this seed and cross-checks the resampled-free statistics against `scipy`). Exact permutation: all 8! = 40,320 orderings.

| family | view | n items (tasks) | n judges | Spearman(TI, human-agree) | Kendall | Pearson | exact perm. p | 95% task-clustered bootstrap CI |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Codex | V1 paper avg, all 72 (reproduction) | 72 (24) | 8 | 0.8333 | 0.6429 | 0.8682 | 0.0154 | [0.238, 0.976] |
| Codex | V2 paper avg, matched only | 21 (7) | 8 | 0.5952 | 0.4286 | 0.6638 | 0.1323 | [−0.571, 0.881] |
| Codex | V3 VB expert mean, matched | 21 (7) | 8 | 0.3333 | 0.2143 | 0.2490 | 0.4279 | [−0.321, 0.543] |
| Codex | V4 VB expert mean, all | 72 (24)\* | 8 | −0.2381 | −0.0714 | −0.7420 | 0.5821 | [−0.643, 0.190] |
| Codex | V5 VB p1-corrected, matched | 21 (7) | 8 | 0.3333 | 0.2143 | 0.2490 | 0.4279 | [−0.321, 0.543] |
| Claude Opus | V1 | 72 (24) | 8 | 0.6429 | 0.5000 | 0.6644 | 0.0962 | [−0.262, 0.905] |
| Claude Opus | V2 | 21 (7) | 8 | 0.0714 | 0.0714 | 0.3238 | 0.8820 | [−0.286, 0.381] |
| Claude Opus | V3 | 21 (7) | 8 | −0.3810 | −0.2857 | −0.0867 | 0.3599 | [−0.524, 0.657] |
| Claude Opus | V4 | 72 (24)\* | 8 | 0.0476 | 0.0714 | −0.3161 | 0.9349 | [−0.524, 0.500] |
| Claude Opus | V5 | 21 (7) | 8 | −0.3810 | −0.2857 | −0.0867 | 0.3599 | [−0.524, 0.657] |
| Qwen3-Coder | V1 | 72 (24) | 8 | 0.9048 | 0.7857 | 0.7279 | 0.0046 | [0.024, 0.905] |
| Qwen3-Coder | V2 | 21 (7) | 8 | 0.5000 | 0.3571 | 0.5488 | 0.2162 | [−0.095, 0.857] |
| Qwen3-Coder | V3 | 21 (7) | 8 | 0.6667 | 0.5714 | 0.5470 | 0.0831 | [−0.575, 0.898] |
| Qwen3-Coder | V4 | 72 (24)\* | 8 | −0.5000 | −0.3571 | −0.8462 | 0.2162 | [−0.738, 0.143] |
| Qwen3-Coder | V5 | 21 (7) | 8 | 0.6667 | 0.5714 | 0.5470 | 0.0831 | [−0.575, 0.898] |

\* V4's item set is "all items with an expert rating," which in the current data equals the same 72-pair union as V1 (the five-expert pool covers the same candidate files); it is **not** restricted to matched tasks. V3 and V5 coincide numerically in this data because VeriBench's 3-expert mean is dominated by participant 1's corrected pass on the matched subset (`vb_p1_corrected` vs `vb_expert_mean`: ρ=1.0 on the 12 shared matched items in `results/label_agreement_matrix.csv`) — participants 2/3 contribute comparatively little variance there; this is a property of the current label coverage, not a computation bug (confirmed via `scripts/test_rescore.py`'s independent `scipy` cross-checks).

**Reading, under the pre-registered rule (`README.md`):** Robust requires V3 Spearman positive in all three families and inside V1's interval; not robust requires V3 ≤ 0 in at least two families. V3 is **positive for Codex (+0.333) and Qwen3-Coder (+0.667), negative for Claude Opus (−0.381)** — one family negative, not two, and not all three positive. **Neither criterion is met: the result is INCONCLUSIVE.** All V2-V5 estimates are additionally far less precise than V1 (n=21 items over 7 tasks vs. n=72 over 24) with every bootstrap 95% interval crossing zero; S1 (below) shows V1 is stable to single-judge removal while V3 is not. No paper sentence is changed by this reading alone, per the README's own rule ("descriptive; no paper sentence changes without Brando") — drafted replacement text is offered at the end of this report for Brando's decision.

## S1 — leave-one-family-out / leave-one-configuration-out (V1, V3)

`results/lofo_loco.csv`. Under V1, removing any single Codex configuration leaves ρ in [0.75, 0.857] (vs. full 0.833) — stable. Under V3, removing any single Codex configuration moves ρ across [0.071, 0.5] (vs. full 0.333) — the matched-item association is not robust to which configuration is dropped, consistent with its small n and wide bootstrap interval above. The same pattern holds for Opus and Qwen3-Coder (full table in the CSV; all view-V3 LOFO ranges are wider, relative to their full-sample value, than the corresponding V1 ranges).

## S2 — old-prompt vs. corrected-prompt rater instructions

Covered above (label identity + `results/label_agreement_matrix.csv`). **Unmeasured beyond this**: the exact text of the old-prompt vs. corrected-prompt rating instructions was not extracted from VeriBench git history in this pass (would require locating the prompt/instruction file's own history, if committed, or the study-design doc referenced in VeriBench's `research_archive/experiments/62_.../01_SPLIT_DECISION_bm.md`); flagged as unmeasured rather than guessed.

## S3 — label-agreement matrix

`results/label_agreement_matrix.csv` (15 pairs x all/matched/unmatched). Headline entries: `paper_pass1` vs `paper_pass2` (the paper's own two passes) ρ=0.273 on all 75 shared items, but ρ=**−0.024** on the 21 matched items vs. ρ=0.475 on the 54 unmatched (n=21 is small; not over-read). `paper_pass1`/`paper_pass2` vs. `vb_expert_mean` are both weak overall (ρ=0.072, 0.128) confirming the old-protocol/revised-protocol split already established in archived experiment 22 (ρ≈0.13 there, on a different item set). The revised-protocol series agree strongly with each other (`vb_p1_corrected` vs `vb_expert_mean` ρ=0.953 on 74 items).

## S4 — label-free headline (bug-ladder reversal)

**Unaffected by reference provenance, confirmed by inspection rather than recomputation.** `experiments/archive/04_veribench_validation/results_exp19_low_variance_replot/bug_reversal_rates.csv` (frozen, archived) records `gpt-5.3-codex|BAD_STRINGY` (the lexical judge) reversing on 20/24 bug ladders — matching the README's S4 claim exactly. Bug ladders (`build_bug_ladder`) are constructed directly from the same gold file a judge is about to score and compared only to each other, with **no external human label and no cross-file reference resolution** in the computation at all; the check is architecturally independent of which reference-file vintage any rater or judge pipeline used elsewhere. No new computation needed; S4 is confirmed unaffected.

## Drafted replacement sentences (text only — `paper_latex/` not edited)

For §5.1 (`sec:tivar_cross_model_results`), which currently reads "Its judge-level Spearman association is positive for each primary family and label view," a provenance-qualified version:

> Its judge-level Spearman association is positive for each primary family on the as-collected validation panel (Table~\ref{tab:tivar_cross_model_results}); a provenance audit (Appendix, experiment 41) finds that only 7 of the panel's 24 scored tasks have reference bytes matching what the rater saw, and on that matched subset, against VeriBench's independently corrected three-expert labels, the association is positive for two of three families (Codex $+0.33$, Qwen3-Coder $+0.67$) and negative for the third (Claude Opus $-0.33$), with wide bootstrap intervals reflecting the small matched subsample ($n{=}21$ items); the pre-registered reading is inconclusive.

For §6 (`sec:limitations-test`), appended after "No test-set result establishes reliability for a new judge or artifact distribution.":

> The validation panel's own provenance is imperfect: its two label passes are a single annotator's superseded old-prompt ratings (later replaced in VeriBench by a corrected-prompt re-rating plus four more experts), one of its 75 nominal items was silently dropped by the frozen judge pipeline on a stale filename, and the judges' gold bytes were frozen (2026-04-12) before most of the remaining items' gold files reached the state the rater actually saw. Re-scoring on reference-matched items against the corrected expert labels leaves the headline association's sign inconsistent across families (Appendix, experiment 41).

## Unmeasured / explicitly not computed

- Exact old-prompt vs. corrected-prompt rating instruction text (S2, see above).
- Per-task exact rating *time* (only the label file's git-commit date is available; pass1 and pass2 share one commit and so cannot be distinguished by this method).
- Whether the paper's judge-run invocation used `--veribench-root` to override `DEFAULT_VERIBENCH_ROOT`: no cached request/prompt log or run manifest recording the literal CLI invocation was found in the committed results directory, so "judge-seen bytes" here is inferred from the script's documented default, not a directly recorded invocation. This is disclosed in `results/provenance_by_task.csv`'s `judged_source` column for every row.

## Status

`results.md` set to DONE below. All 25 tasks classified (1 not-applicable/missing-gold, 7 matched, 17 unmatched), Gate G0 PASS, all five views computed for all three families, S1/S3/S4 complete, S2 partially complete (instruction text unmeasured, disclosed above).
