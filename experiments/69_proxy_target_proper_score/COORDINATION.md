# Coordination: experiment 69A

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/69_proxy_target_proper_score/COORDINATION.md>

**TLDR:** Experiment 69A lives in `experiments/69_proxy_target_proper_score/` on `main`. Trustworthy-theorem-judges experiment 09 owns the canonical human ratings. Do not start a competing correlation sweep.

- This folder is the zero-spend run (69A). It reads the frozen 2026-11-26 snapshot and saved judge scores. It does not call a judge. Experiment 69B, any paid scoring of the 100 new files, waits on Brando because of the 10-15-2026 Vals / Valkyrie spending pause.
- Canonical ratings: [trustworthy-theorem-judges experiment 09](https://github.com/brando90/trustworthy-theorem-judges/tree/main/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026), live sync `460466dd`. The copy under `data/` is that snapshot for this analysis, not a second collection. Later exports come from that experiment.
- Cursor, Claude Code, and Gemini Antigravity (`agy`) share this folder's `PREREG.md`. One writer at a time. Read `PREREG.md` and `RESULTS.md` before editing.
- Do not run a correlation-maximization search over prompts, proxies, or judge families against these ratings. The decision metric is held-out normalized individual-rating Ranked Probability Score (RPS), with cross-entropy and total variation distance secondary. Spearman is diagnostic only.
