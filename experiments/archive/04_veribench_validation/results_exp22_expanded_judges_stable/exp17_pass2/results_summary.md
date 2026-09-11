# EXP17 Property vs Human Analysis

- Label set: `pass2`
- Judges: `13`
- Regression R2: `0.558` (perm p=`0.1017`)

## Per-property correlation (Spearman)
- P1_identity: r=-0.080, perm p=0.7968
- P2_bug_rank: r=0.720, perm p=0.0073
- P3_weak_mono: r=0.631, perm p=0.0241
- P4_stability: r=0.177, perm p=0.5624

## Regression betas (standardized)
- P1_identity: beta=0.597, perm p=0.7692
- P2_bug_rank: beta=-0.329, perm p=0.9055
- P3_weak_mono: beta=0.891, perm p=0.6783
- P4_stability: beta=0.275, perm p=0.4199

## Bad-judge gap: `gpt-5.3-codex|BAD_STRINGY`
- P1-P4 composite percentile: 0.462
- Human corr (pass2): 0.312