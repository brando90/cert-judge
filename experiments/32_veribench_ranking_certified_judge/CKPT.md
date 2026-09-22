# CKPT — 32_veribench_ranking_certified_judge

**TLDR-start:** [cj: exp32-certified-ranking] Quote written before any inference; ranking run = 140 items x 4 agents x 3 repeats = 1,680 single-case `codex exec` calls (ChatGPT subscription, model `gpt-5.6-terra`, effort low, prompt P1_BASELINE), $0 provider-API spend.

## Status (update on every checkpoint)
- 2026-09-22 — inputs located and manifested (`inputs_manifest.json`: 140 items, 560 candidate rows, all golds resolved in the frozen legacy root); `judge_config.json`, `score_schema.json`, `run_ranking_cli.py` written. NOTHING RUN YET.
- 2026-09-22 22:16 UTC — probe: 4 cells OK (scores 0.0/0.0/0.1/…, 13–19 s per call, usage ~13.8k input / ~150 output tokens per call). Codex JSONL emits no served-model field and no `model:` header under `--json`; model identity rests on the explicit `-m gpt-5.6-terra` flag (same limitation exp29 documented). A benign `error` item ("Skill descriptions were shortened to fit the skills context budget") appears on some calls; the runner now records it as `benign_warnings` and does not retry on it.
- 2026-09-22 22:25 UTC — throughput at 8 workers is ~34 s per call (server-side queueing; 13–19 s at 2 workers), i.e. ~14 cells/min, so the full 1,680 cells need ~2 h. DECISION: jobs are now ordered repeat-major (all 560 item x agent cells of repeat 0, then repeat 1, then repeat 2; items shuffled with seed 0) so an interrupted run leaves complete repeat layers; the aggregator reports both the all-3-repeats analysis and an all-available-repeats analysis with the repeat coverage histogram. Restarted at 22:24:40 UTC (cached cells kept).
- 2026-09-22 22:33 UTC — coordinator fact: the certified §5.3 Codex panel used the MEDIAN over THREE repeated calls per pair for LLM judges (9 repeats only for the edit-distance/random controls; main.tex e0631b6). Primary aggregation switched to median-of-3 (judge_config.json, aggregate_ranking.py); mean-of-3 kept as the secondary (Claude 3.7 table rule). No change to the run itself (3 repeats were already quoted).
- 2026-09-22 22:42 UTC — throughput fell to ~5–8 cells/min (per-call latency 40→60–120 s at 8 workers; 2 workers earlier gave 13–19 s per call, i.e. the same ~7 cells/min): a server-side subscription rate limit, not local contention. DECISION: keep the single-case protocol (no batching, so every cell stays comparable to the certified single-pair calls), let repeat layer 0 (560 item x agent cells) finish first, aggregate whatever is complete before Brando returns, and leave the remaining layers to the resume command. Runner restarted 22:39 UTC with the reconnect-benign fix (pid 25117).
- 2026-09-22 22:23 UTC — FULL RUN RUNNING in background (`nohup python3 run_ranking_cli.py --workers 8`, log `results/run.log`, stdout `results/run_stdout.log`). Completed cells are cached in `results/raw/`; if the process dies, re-run the resume command below (it skips cached cells). `aggregate_ranking.py` written (bootstrap CIs, ordering agreement with the Claude 3.7 table) — run it on partial data at any time.

## Quote (written BEFORE the first inference call — Hard Rule 9 / runbook step 4)
| Field | Value |
|---|---|
| CLI | `/usr/local/bin/codex` (codex-cli 0.155.1), `codex exec`, ChatGPT subscription login (`codex login status` = "Logged in using ChatGPT") |
| Model flag | `-m gpt-5.6-terra`, `-c model_reasoning_effort="low"` (gpt-5.3-codex is not offered by the CLI; see judge_config.json `model_fallback_reason`) |
| Prompt | `P1_BASELINE` (certified primary with the highest TI_var = 0.9208) |
| Cells | 140 items x 4 agents x 3 repeats = **1,680 calls** (one case per call), plus up to 3 retries per failed cell and 2 probe cells that are part of the 1,680 (cached) |
| Parallelism | 8 |
| Provider API spend | **$0** (subscription CLI only; no `~/keys/*`, all `*_API_KEY` scrubbed from child env) |
| Property-suite fallback calls (exp16-style P1–P4 for the substitute, NOT started) | exp16 per-judge cell count from `results_exp16_final_robust_r9_median/detail_rows.csv`: 120 bug-ladder cells (24 files x 5 levels) + 96 identity/rewrite cells (24 x 4 variants) + 72 human-union pairs = 288 cells; at 3 repeats = **864 `codex exec` calls** (648 without the human-union pairs). Same CLI/model/effort as above, $0 API. Runs AFTER the ranking (runbook Fallback: ranking first). exp29 already ran the PTI-v0 property suite for `gpt-5.6-terra|P1_BASELINE` at effort low via the same CLI (774 batch tasks, $0); its numbers are cited in REPORT.md. |

Brando pre-approved subscription-CLI runs ("go!"); no API spend is requested.

## Resume command
```bash
cd ~/cert-judge && python3 experiments/32_veribench_ranking_certified_judge/run_ranking_cli.py --workers 8
# then
~/uv_envs/cert-judge/bin/python3 experiments/32_veribench_ranking_certified_judge/aggregate_ranking.py   # needs numpy+scipy (the default python3 on this Mac has a broken numpy); the runner itself is stdlib-only
```
The runner skips every cell whose `results/raw/<split>__<stem>__<agent>__r<k>.json` has `status: ok`; failed cells are written as `*.failed.json` and re-attempted on the next run.

## Layout check
`python3 py_src/cert_judge/experiment_layout.py --check` reports only pre-existing failures that are not mine: `experiments/18_icml_reviews`, `experiments/33_openreview_complaints_all_venues_to_iclr2027_paper` (another session's new dir), and the missing archived homes for 18 / 20.

**TLDR-end:** [cj: exp32-certified-ranking] Quote = 1,680 subscription `codex exec` calls to `gpt-5.6-terra` (low) with P1_BASELINE; $0 API spend; nothing has run yet.
