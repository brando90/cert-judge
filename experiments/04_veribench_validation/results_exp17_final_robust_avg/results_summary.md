# EXP17 Property vs Human Analysis

- Label set: `avg`
- Judges: `8`
- Regression R2: `0.889` (perm p=`0.0812`)

## Per-property correlation (Spearman)
- P1_identity: r=-0.024, perm p=0.9771
- P2_bug_rank: r=0.714, perm p=0.0557
- P3_weak_mono: r=0.747, perm p=0.0432
- P4_stability: r=0.135, perm p=0.7578

## Regression betas (standardized)
- P1_identity: beta=2.110, perm p=0.4491
- P2_bug_rank: beta=-2.233, perm p=0.5621
- P3_weak_mono: beta=2.255, perm p=0.4260
- P4_stability: beta=-0.033, perm p=0.9842

## Bad-judge gap: `gpt-5.3-codex|BAD_STRINGY`
- P1-P4 composite percentile: 0.625
- Human corr (avg): 0.449