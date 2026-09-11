# EXP17 Property vs Human Analysis

- Label set: `pass1`
- Judges: `13`
- Regression R2: `0.584` (perm p=`0.0811`)

## Per-property correlation (Spearman)
- P1_identity: r=-0.074, perm p=0.8109
- P2_bug_rank: r=0.676, perm p=0.0135
- P3_weak_mono: r=0.461, perm p=0.1135
- P4_stability: r=0.389, perm p=0.1881

## Regression betas (standardized)
- P1_identity: beta=0.055, perm p=0.9789
- P2_bug_rank: beta=0.419, perm p=0.8765
- P3_weak_mono: beta=-0.049, perm p=0.9822
- P4_stability: beta=0.663, perm p=0.0306

## Bad-judge gap: `gpt-5.3-codex|BAD_STRINGY`
- P1-P4 composite percentile: 0.462
- Human corr (pass1): 0.413