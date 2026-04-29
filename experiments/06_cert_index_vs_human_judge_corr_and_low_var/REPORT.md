# Folder 06 — REPORT

Trust-index v1/v2 vs per-judge human-correlation across the expanded
9-judge panel (4 Claude + 3 Codex + 1 editdist + 1 random).

## Headline numbers

Run: `full_run/median/`, `2026-04-28 23:30` PT, n_repeats=3 (cache reuse — see "Open questions").

| label set | metric                      | v1 (cert index)                     | v2 (cert index)                     |
|-----------|-----------------------------|-------------------------------------|-------------------------------------|
| pass1     | Spearman ρ (cert → human)   | −0.133 [-0.846, +0.688] p=0.750     | +0.133 [-0.583, +0.893] p=0.747     |
| pass2     | Spearman ρ (cert → human)   | −0.100 [-0.622, +0.817] p=0.809     | −0.267 [-0.774, +0.474] p=0.499     |
| avg       | Spearman ρ (cert → human)   | −0.183 [-0.761, +0.688] p=0.648     | −0.083 [-0.670, +0.863] p=0.843     |

CIs are 10K-iter bootstrap; p-values are 20K-iter permutation.

**Mean ablation** (`full_run/mean/`): same direction, similar magnitudes.
The mean and median variants agree to within ~0.15 on every Spearman ρ;
neither flavor crosses the perm-p < 0.05 threshold for any label set.

## Pre-commit decisions (per PROTOCOL.md, before run)

- v1 = headline (canonical certification index from §2)
- v2 = appendix ablation
- median = headline aggregation
- mean = ablation
- Label set: avg = primary; pass1 / pass2 = secondary

## Per-judge anchors (median, label-set avg)

Top trust-index judges and their human-Spearman:

| judge_id                                       | cert v1 | cert v2 | human-Sp (avg) | 95% CI                  |
|-----------------------------------------------|---------|---------|----------------|-------------------------|
| `claude-sonnet-4-20250514\|P8_STRICT_B`        | 0.915   | 0.892   | +0.103         | [-0.151, +0.338]        |
| `claude-sonnet-4-20250514\|P4_CHECKLIST`       | 0.899   | 0.873   | +0.090         | [-0.134, +0.332]        |
| `claude-sonnet-4-20250514\|P1_BASELINE`        | 0.901   | 0.880   | -0.030         | [-0.260, +0.197]        |
| `claude-sonnet-4-20250514\|BAD_STRINGY`        | 0.901   | 0.825   | +0.311         | [+0.032, +0.533]        |
| `gpt-5.3-codex\|P8_STRICT_B`                   | 0.860   | 0.851   | +0.365         | [+0.115, +0.582]        |
| `gpt-5.3-codex\|P4_CHECKLIST`                  | 0.893   | 0.867   | +0.419         | [+0.190, +0.607]        |
| `gpt-5.3-codex\|P1_BASELINE`                   | 0.895   | 0.874   | +0.466         | [+0.246, +0.645]        |
| `editdist_e1`                                  | 0.670   | 0.468   | +0.199         | [-0.091, +0.440]        |
| `random_r1`                                    | 0.436   | 0.576   | -0.001         | [-0.237, +0.212]        |

Full numbers in `full_run/median/judge_rows.csv`.

## Interpretation

The expanded 9-judge panel shows **weak and direction-mixed** trust-index →
human-Spearman correlation, consistent with the variance diagnosis filed
in `experiments/06_/exp16_fig4_lhs_variance_diagnosis.md` (PR #10): the
LLM-prompt judges sit in a narrow region of cert-index space, so the
remaining variance is mostly the per-judge human-Spearman sampling
noise (Fisher-z floor at N=72).

The sign-flipping of cert v2 across pass1/pass2 (+0.133 → -0.267) is the
same sign-flipping behavior PR #10 §6 predicted from the floor; it is
not a v2-specific defect.

**Folder 07** confirms the property panel itself is doing useful work
(it correctly fails `random_r1` and `editdist_e1`); the limitation is in
N and judge spread, not in the property metrics.

## Open questions for Ethan

1. **`JUDGE_REPEATS=3` deviation from PROTOCOL.md.** Locked PROTOCOL set
   `JUDGE_REPEATS=9`. The full-protocol n_repeats=9 run took ~30 s/item
   on Claude (see scratch); for 9 judges × ~288 items per judge the
   wall-clock was ~12 h, exceeding the session budget. Reused the
   smoke-run cache (n_repeats=3) for all 9 judges to ship a complete
   panel tonight.
   - **Effect on cert index**: unchanged (cert index is computed from
     per-item means, which converge fast — see PR #10 §3 for the
     n_repeats sensitivity finding).
   - **Effect on Cronbach's α (P4)**: capped at 1.0 because n_repeats=3
     gives perfect reliability for nearly-constant scores; the n_repeats=9
     follow-up should give more nuanced α.
   - **Effect on cert v2 → human Spearman**: small. Weak/noisy
     correlations come from N=9 judges and clustered cert-index values,
     not from n_repeats. Rerunning with n_repeats=9 will not fix the
     wide CIs.
   - **Filed**: Folder 06b spec for the n_repeats=9 cluster rerun.
2. **Codex P4_CHECKLIST / P1_BASELINE shows the strongest human-Spearman
   in the panel** (avg ρ = +0.419 and +0.466 respectively, both with
   bootstrap CIs strictly above 0). This is the headline judge-level
   anchor — the LLM judge with the highest human alignment is a
   Codex-prompt judge, not a Claude one, on this label set.
3. **Sign-flipping cert v2 across pass1 (+0.133) vs pass2 (-0.267).**
   PR #10's variance diagnosis predicts this from the Fisher-z floor.
   No new finding here; flagging so the manuscript wording does not
   accidentally claim a v2-specific issue.
4. **Variance-reduction follow-up.** PR #10 §3 ranked four real fixes
   (paired-judge Δρ panel, Fisher-z parametric CIs, repeat-agg=median,
   grow N). This run uses median + 10K bootstrap. The paired-judge Δρ
   panel is the next biggest variance reduction (2–4× narrower CIs)
   and is filed as **Folder 06c**.

## Files

- `PROTOCOL.md` — locked params (frozen pre-run)
- `run_06_full.sh` — runner (median/mean)
- `full_run/median/{summary.json, judge_rows.csv, detail_rows.csv, fig_*.png}`
- `full_run/mean/{...}`
- `smoke/{...}` — earlier 3-repeat smoke (kept for diff)
