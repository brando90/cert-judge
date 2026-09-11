# EXP17 Property vs Human Analysis

- Label set: `pass2`
- Judges: `8`
- Regression R2: `0.454` (perm p=`0.6846`)

## Per-property correlation (Spearman)
- P1_identity: r=0.048, perm p=0.9173
- P2_bug_rank: r=0.524, perm p=0.1962
- P3_weak_mono: r=0.651, perm p=0.0920
- P4_stability: r=-0.013, perm p=0.9870

## Regression betas (standardized)
- P1_identity: beta=0.238, perm p=0.8548
- P2_bug_rank: beta=-0.011, perm p=0.9956
- P3_weak_mono: beta=0.629, perm p=0.6561
- P4_stability: beta=-0.058, perm p=0.8988

## Bad-judge gap: `claude-opus-4-7|BAD_STRINGY`
- P1-P4 composite percentile: 0.625
- Human corr (pass2): 0.269