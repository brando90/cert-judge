# EXP17 Property vs Human Analysis

- Label set: `pass2`
- Judges: `8`
- Regression R2: `0.765` (perm p=`0.2184`)

## Per-property correlation (Spearman)
- P1_identity: r=0.024, perm p=0.9776
- P2_bug_rank: r=0.667, perm p=0.0823
- P3_weak_mono: r=0.783, perm p=0.0300
- P4_stability: r=-0.233, perm p=0.5723

## Regression betas (standardized)
- P1_identity: beta=1.984, perm p=0.4685
- P2_bug_rank: beta=-2.136, perm p=0.5765
- P3_weak_mono: beta=2.316, perm p=0.3858
- P4_stability: beta=-0.370, perm p=0.7017

## Bad-judge gap: `gpt-5.3-codex|BAD_STRINGY`
- P1-P4 composite percentile: 0.625
- Human corr (pass2): 0.299