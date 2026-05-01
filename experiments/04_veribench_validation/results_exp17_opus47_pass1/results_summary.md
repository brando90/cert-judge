# EXP17 Property vs Human Analysis

- Label set: `pass1`
- Judges: `8`
- Regression R2: `0.658` (perm p=`0.3697`)

## Per-property correlation (Spearman)
- P1_identity: r=-0.132, perm p=0.7645
- P2_bug_rank: r=0.476, perm p=0.2403
- P3_weak_mono: r=0.331, perm p=0.4131
- P4_stability: r=0.761, perm p=0.0415

## Regression betas (standardized)
- P1_identity: beta=0.455, perm p=0.7399
- P2_bug_rank: beta=-0.199, perm p=0.9206
- P3_weak_mono: beta=0.477, perm p=0.7285
- P4_stability: beta=0.678, perm p=0.1509

## Bad-judge gap: `claude-opus-4-7|BAD_STRINGY`
- P1-P4 composite percentile: 0.625
- Human corr (pass1): 0.258