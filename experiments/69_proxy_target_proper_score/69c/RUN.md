# How to run experiment 69C

69C reads a 69B forecast file. It does not call a model. Run it after `69b/RUN.md` has written a measured `forecasts_*.jsonl`.

```bash
python3 experiments/69_proxy_target_proper_score/69c/scripts/eval_69c.py \
  --forecasts experiments/69_proxy_target_proper_score/69b/results/forecasts_snap.jsonl \
  --out experiments/69_proxy_target_proper_score/69c/results/eval_69c.json
```

The sealed 10/5/10 task split is in `PREREG.md`. Formulation ④ selects on the train tasks. Formulation ③ selects on the validation tasks. The printed JSON has `dry_run: true` when the forecasts are the point-mass dry-run.
