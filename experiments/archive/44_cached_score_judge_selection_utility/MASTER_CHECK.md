# Master deterministic check

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/MASTER_CHECK.md>

**TLDR:** The optimized Pearson constant-input defect is fixed; its regression test and the complete analysis passed before publication.

Status: VERIFIED_FIXED (worker update, 10-05-2026).

Calling `draw_correlations(np.array([np.full(42, .1)]), np.arange(42, dtype=float), np.arange(42))` returned Pearson 0.0 while Spearman/Kendall were undefined. A constant score has undefined Pearson, never zero. The same failure occurs at lengths25,29,45 because floating-point mean subtraction leaves a tiny nonzero denominator. In `pearson_rows`, explicitly require `np.ptp(values, axis=1) > 0` and `np.ptp(target) > 0` (in addition to denominator checks), and add this case to the SciPy cross-check tests. Then run final analysis with correct undefined-member handling. Update this receipt with the verified fix/test result before publication.

Worker applied the `np.ptp` nonconstant guard and extended the tied/constant SciPy cross-check to a 42-item constant score vector. The required final archived-path 10,000-draw rerun and verification remain before publication.

Master verified the exact constant-input regression test and complete 10,000-draw rerun on 10-05-2026 23:14 PDT. All 9 tests and layout/diff checks passed.
