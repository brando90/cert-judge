# EXP17 Property vs Human Analysis

- Label set: `avg`
- Judges: `13`
- Regression R2: `0.537` (perm p=`0.1154`)

## Per-property correlation (Spearman)
- P1_identity: r=0.006, perm p=0.9897
- P2_bug_rank: r=0.687, perm p=0.0120
- P3_weak_mono: r=0.517, perm p=0.0713
- P4_stability: r=0.272, perm p=0.3649

## Regression betas (standardized)
- P1_identity: beta=0.303, perm p=0.8844
- P2_bug_rank: beta=0.161, perm p=0.9521
- P3_weak_mono: beta=0.308, perm p=0.8864
- P4_stability: beta=0.488, perm p=0.1411

## Bad-judge gap: `gpt-5.3-codex|BAD_STRINGY`
- P1-P4 composite percentile: 0.462
- Human corr (avg): 0.472