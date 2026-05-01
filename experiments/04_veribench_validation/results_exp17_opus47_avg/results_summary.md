# EXP17 Property vs Human Analysis

- Label set: `avg`
- Judges: `8`
- Regression R2: `0.475` (perm p=`0.6609`)

## Per-property correlation (Spearman)
- P1_identity: r=0.192, perm p=0.6476
- P2_bug_rank: r=0.405, perm p=0.3270
- P3_weak_mono: r=0.368, perm p=0.3620
- P4_stability: r=0.330, perm p=0.4331

## Regression betas (standardized)
- P1_identity: beta=0.272, perm p=0.8505
- P2_bug_rank: beta=0.135, perm p=0.9450
- P3_weak_mono: beta=0.425, perm p=0.7645
- P4_stability: beta=0.211, perm p=0.6607

## Bad-judge gap: `claude-opus-4-7|BAD_STRINGY`
- P1-P4 composite percentile: 0.625
- Human corr (avg): 0.324