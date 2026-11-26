# How to run experiment 69B

This checkout did not call a model. There is no API key and no SNAP SSH config on the Cursor VM. The commands below are the ones to run where the credentials and the GPUs are.

Packet (not copied here; it is large Lean text owned by trustworthy-theorem-judges experiment 09):

```bash
git clone --depth 1 https://github.com/brando90/trustworthy-theorem-judges.git
export CJ69_PACKET="$PWD/trustworthy-theorem-judges/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026/rating_task_packet/main_rating_task"
```

From the cert-judge root.

## Lane B, SNAP, $0, no network inside the process

On a free SNAP GPU (mercury or skampere), after the Lean files are on that host:

```bash
python3 experiments/69_proxy_target_proper_score/69b/scripts/score_native6.py \
  --backend vllm \
  --model "${CJ69_SNAP_MODEL:-Qwen/Qwen3-8B}" \
  --packet-root "$CJ69_PACKET" \
  --out experiments/69_proxy_target_proper_score/69b/results/forecasts_snap.jsonl
```

`CJ69_TP` is the tensor-parallel size (default 1). Do not point this at a Gemini or Antigravity model; the script exits if the name contains `gemini`, `agy`, or `antigravity`.

## Lane A, API, cap $27, no agy

Set the price from a current price card before the probe. Example at $0.02 a call is $2 for 100 files and stays under the cap. If the price times 100 exceeds $27, the script stops after the 2-file probe.

```bash
export CJ69_API_MODEL="gpt-4.1-mini"    # any non-Gemini plan-lane model
export CJ69_API_BASE="https://api.openai.com/v1"
python3 experiments/69_proxy_target_proper_score/69b/scripts/score_native6.py \
  --backend openai \
  --model "$CJ69_API_MODEL" \
  --base-url "$CJ69_API_BASE" \
  --api-key-file "$HOME/keys/openai_api_brandos_personal_key.txt" \
  --usd-per-call 0.02 \
  --cap 27 \
  --packet-root "$CJ69_PACKET" \
  --out experiments/69_proxy_target_proper_score/69b/results/forecasts_api.jsonl
```

## Score the forecasts

```bash
python3 experiments/69_proxy_target_proper_score/69b/scripts/eval_69b.py \
  --forecasts experiments/69_proxy_target_proper_score/69b/results/forecasts_snap.jsonl \
  --out experiments/69_proxy_target_proper_score/69b/results/eval_69b.json
python3 experiments/69_proxy_target_proper_score/69c/scripts/eval_69c.py \
  --forecasts experiments/69_proxy_target_proper_score/69b/results/forecasts_snap.jsonl \
  --out experiments/69_proxy_target_proper_score/69c/results/eval_69c.json
```

A file whose rows say `"source": "dry_run"` is a pipeline check. It does not decide whether a judge beats the constant forecast.

## Dry-run, no packet and no key

```bash
python3 experiments/69_proxy_target_proper_score/69b/scripts/score_native6.py \
  --dry-run \
  --out experiments/69_proxy_target_proper_score/69b/results/forecasts_dry_run.jsonl
```
