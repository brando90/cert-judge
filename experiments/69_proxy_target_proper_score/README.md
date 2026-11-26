# Experiment 69: proxy–target proper-score selection

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/69_proxy_target_proper_score/README.md>

**TLDR:** Zero-spend experiment 69A is done. No primary-pool proxy passes the frozen rule. `TI_var` on the 24 paper series is worse than the constant forecast. Held-out `C_ms_gold` beats that forecast and is unresolved against best-on-val. Numbers: `RESULTS.md`.

Canonical human ratings remain trustworthy-theorem-judges experiment 09. Coordination with other agents, including Gemini Antigravity (`agy`), is `COORDINATION.md`.

```bash
PYTHONPATH=experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts \
  python3 experiments/69_proxy_target_proper_score/scripts/run_69a.py
```

Results land in `results/` and `RESULTS.md` after the pre-registration commit.
