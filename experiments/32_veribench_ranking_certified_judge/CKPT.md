# CKPT — 32_veribench_ranking_certified_judge

**TLDR-start:** [cj: exp32-certified-ranking] Quote written before any inference; ranking run = 140 items x 4 agents x 3 repeats = 1,680 single-case `codex exec` calls (ChatGPT subscription, model `gpt-5.6-terra`, effort low, prompt P1_BASELINE), $0 provider-API spend.

## Status (update on every checkpoint)
- 2026-09-22 — inputs located and manifested (`inputs_manifest.json`: 140 items, 560 candidate rows, all golds resolved in the frozen legacy root); `judge_config.json`, `score_schema.json`, `run_ranking_cli.py` written. NOTHING RUN YET.

## Quote (written BEFORE the first inference call — Hard Rule 9 / runbook step 4)
| Field | Value |
|---|---|
| CLI | `/usr/local/bin/codex` (codex-cli 0.155.1), `codex exec`, ChatGPT subscription login (`codex login status` = "Logged in using ChatGPT") |
| Model flag | `-m gpt-5.6-terra`, `-c model_reasoning_effort="low"` (gpt-5.3-codex is not offered by the CLI; see judge_config.json `model_fallback_reason`) |
| Prompt | `P1_BASELINE` (certified primary with the highest TI_var = 0.9208) |
| Cells | 140 items x 4 agents x 3 repeats = **1,680 calls** (one case per call), plus up to 3 retries per failed cell and 2 probe cells that are part of the 1,680 (cached) |
| Parallelism | 8 |
| Provider API spend | **$0** (subscription CLI only; no `~/keys/*`, all `*_API_KEY` scrubbed from child env) |
| Property-suite fallback calls | NOT yet quoted; ranking first (runbook Fallback). exp29 already ran the PTI-v0 property suite for `gpt-5.6-terra|P1_BASELINE` at effort low via the same CLI (774 tasks); see REPORT.md caveats. |

Brando pre-approved subscription-CLI runs ("go!"); no API spend is requested.

## Resume command
```bash
cd ~/cert-judge && python3 experiments/32_veribench_ranking_certified_judge/run_ranking_cli.py --workers 8
# then
python3 experiments/32_veribench_ranking_certified_judge/aggregate_ranking.py
```
The runner skips every cell whose `results/raw/<split>__<stem>__<agent>__r<k>.json` has `status: ok`; failed cells are written as `*.failed.json` and re-attempted on the next run.

## Layout check
`python3 py_src/cert_judge/experiment_layout.py --check` reports only pre-existing failures that are not mine: `experiments/18_icml_reviews`, `experiments/33_openreview_complaints_all_venues_to_iclr2027_paper` (another session's new dir), and the missing archived homes for 18 / 20.

**TLDR-end:** [cj: exp32-certified-ranking] Quote = 1,680 subscription `codex exec` calls to `gpt-5.6-terra` (low) with P1_BASELINE; $0 API spend; nothing has run yet.
