# Synthetic gate self-test, 10-19-2026

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/ideas/cj_human_rating_pool_prospective_screen/synthetic/RESULTS_synthetic_gate_10-19-2026.md>

**TLDR:** The rating-pool gate runs on made-up numbers and matches its three rules. No human rating, no judge call, and no packet was used.

The script is `synthetic/test_gate_self.py`. It calls the analysis library pinned by `freeze/FREEZE_10-18-2026.json` (SHA-256 `3051346cbeb858cf0256f76938cadd15e055524e12301c13c4a78487878e4ba8`). Draws are 10,000 and the seed is 48.

| Check | Result |
|---|---|
| Pinned library hash | matches |
| Falling deletion ladder | quality above 0.9 |
| Rising deletion ladder | quality below 0.1 |
| Constant ladder | quality 0 |
| 8 setups whose screen equals agreement | PASS (Spearman 1, one-sided permutation p below 0.05, bootstrap lower bound above 0.20) |
| 8 setups whose screen reverses agreement | FAIL (Spearman −1) |
| 7 setups | NOT_COMPUTABLE |

PASS means all three pre-registered conditions: Spearman at least 0.45, one-sided permutation p-value below 0.05, and a 95% configuration-bootstrap lower bound above 0.20. These rows are synthetic. They do not say the screen will pass on the fresh ratings.

Packets still do not go out. The round waits until VeriBench set N closes on 11-06-2026.

**TLDR-end:** [cert-judge: cj_human_rating_pool_prospective_screen] The synthetic gate self-test passed its five checks, and the human-rating pool is still unlaunched.
