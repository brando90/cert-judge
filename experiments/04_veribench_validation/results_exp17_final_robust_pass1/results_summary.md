# EXP17 Property vs Human Analysis

- Label set: `pass1`
- Judges: `8`
- Regression R2: `0.927` (perm p=`0.0531`)

## Per-property correlation (Spearman)
- P1_identity: r=-0.214, perm p=0.6199
- P2_bug_rank: r=0.595, perm p=0.1328
- P3_weak_mono: r=0.627, perm p=0.1083
- P4_stability: r=0.466, perm p=0.2447

## Regression betas (standardized)
- P1_identity: beta=1.968, perm p=0.4770
- P2_bug_rank: beta=-2.142, perm p=0.5834
- P3_weak_mono: beta=2.042, perm p=0.4636
- P4_stability: beta=0.212, perm p=0.8405

## Bad-judge gap: `gpt-5.3-codex|BAD_STRINGY`
- P1-P4 composite percentile: 0.625
- Human corr (pass1): 0.411