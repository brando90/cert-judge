# Experiment 59: proxy indices on open-weight judges, and fitting them to frontier judges

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/59_open_weight_proxy_index_and_frontier_fit/README.md>

**TLDR:** While frontier human ratings are pending (due 2026-11-06), this tests (1) whether label-free indices (experiment 39's frozen `C_ms_gold` and new frontier-agreement indices) rank open-weight judges by their agreement with the expert ratings, and (2) whether open-weight judge scores can be stacked and fit to the frontier consensus (no human labels in the fit) to track the humans on held-out tasks. Free GPUs only, cached frontier scores only. Read `PROTOCOL.md` (frozen before any judge call). Human ratings are 75 Claude 3.7 Sonnet zero-shot items only.

| Path | What |
|---|---|
| `PROTOCOL.md` | Frozen protocol, decision rules, dated addenda. |
| `scripts/register59.py` | Adds two models to experiment 58's panel at runtime and lists the stage-1 lanes. |
| `scripts/judge59.py`, `fetch59.py` | Experiment 58's vLLM driver and fetcher on this panel (E39 cells, nine prompts). |
| `slurm/e59_lane.sh` | The lane script run with nohup on skampere1 GPU 5 and mercury2 GPU 9 (empty GPUs only). |
| `scripts/analyze59.py` | The frozen analysis (needs numpy, scipy); writes `results/ANALYSIS.json` and `results/RESULTS_open_weight_proxy_fit.md`. |
| `results/` | Harvests and reports once stage 1 is collected. |

Run: `python scripts/analyze59.py --run <runs/main> [--run <runs/other>]` (a run directory holds `harvest/e39/*.json`).
Self-test (no new data): rename a copy of the cached `qwen36` harvests to a fake model, run with `--hosted-open ""`.

## Status

| Step | Status |
|---|---|
| Protocol frozen and pushed | Done 10-24-2026 (before any judge call) |
| Stage 1 judging (6 models x 9 prompts on E39 cells) | Running from 10-24-2026 19:35 (lane A skampere1 GPU 5: llama31_8b, q25_14b_awq, q3_30b_a3b_fp8, qwen3_8b, qwen3_14b; lane B mercury2 GPU 9: qwen3_4b) |
| Analysis script | Written, tested on fake units |
| Results | Pending |
