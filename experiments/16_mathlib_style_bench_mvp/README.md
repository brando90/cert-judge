# Mathlib Style Bench MVP
**TLDR:** This experiment scaffolds a first pass at Mathlib Style Bench: score whether a judge prefers accepted mathlib-style Lean code over a worse but semantically similar version. It is intentionally offline-first: use the heuristic scorer for smoke tests, or pass externally produced LLM/human scores into the same metric pipeline.

Collaborator tag: @wrsturgeon ([GitHub](https://github.com/wrsturgeon)).

## Goal

The benchmark unit is a bad-code -> good-code Lean pair. The bad file should be plausible Lean 4 that proves the same or nearly the same fact but violates mathlib norms: verbose proof, avoidable induction, weak theorem reuse, awkward tactic script, poor naming, or brittle local rewriting. The good file should be the preferred mathlib-style rewrite.

The MVP answers one concrete question:

> Does a style judge assign a higher score to the good mathlib-style file than to the bad file?

## Layout

- `run_mathlib_style_bench.py`: offline runner that scores a pair manifest and writes metrics.
- `data/sample_pairs.jsonl`: seed manifest with handcrafted bad/good Lean pairs.
- `data/sample_pairs/bad/`: intentionally worse Lean files.
- `data/sample_pairs/good/`: corresponding mathlib-style Lean files.
- `prompts/mathlib_style_judge_prompt.txt`: initial prompt for producing external judge scores.
- `PROTOCOL.md`: metric and test-set-selection protocol.
- `tests/test_run_mathlib_style_bench.py`: unit tests for the runner and metric.

The upstream seed repo is `StanfordLeanClub/mathlib-style-bench`. At scaffold time it only contains a short README, so this folder keeps the concrete MVP inside `cert-judge` while the standalone benchmark can mature.

## Quick Start

Run the deterministic smoke baseline:

```bash
cd /Users/brandomiranda/cert-judge
python experiments/16_mathlib_style_bench_mvp/run_mathlib_style_bench.py \
  --pairs-file experiments/16_mathlib_style_bench_mvp/data/sample_pairs.jsonl \
  --out-dir experiments/16_mathlib_style_bench_mvp/results/smoke
```

Expected outputs:

- `pair_scores.csv`: one row per pair, variant, repeat, and judge.
- `pair_metrics.csv`: one row per pair with bad/good means, margin, order score, and pass flag.
- `summary.json`: aggregate MSB-MVP metrics.
- `REPORT.md`: readable summary.

Run tests:

```bash
python -m unittest experiments/16_mathlib_style_bench_mvp/tests/test_run_mathlib_style_bench.py
```

## External Judge Scores

The runner intentionally does not call provider APIs. To evaluate an LLM, produce a long-format CSV with this schema:

```csv
pair_id,variant,score,judge_id,repeat_idx,source
nat_zero_add,bad,0.35,my_judge,0,manual_or_cli
nat_zero_add,good,0.92,my_judge,0,manual_or_cli
```

Use `score` or `normalized_score` in `[0,1]`. If your judge emits raw points, use `raw_score,max_score` instead:

```csv
pair_id,variant,raw_score,max_score,judge_id,repeat_idx,source
nat_zero_add,bad,9,30,my_judge,0,manual_or_cli
nat_zero_add,good,28,30,my_judge,0,manual_or_cli
```

Then run:

```bash
python experiments/16_mathlib_style_bench_mvp/run_mathlib_style_bench.py \
  --pairs-file experiments/16_mathlib_style_bench_mvp/data/sample_pairs.jsonl \
  --scores-csv /path/to/external_scores.csv \
  --out-dir experiments/16_mathlib_style_bench_mvp/results/external_scores
```

External score rows must reference `pair_id` values from the manifest and use `variant` values `bad` or `good`; the runner rejects unknown IDs instead of silently dropping them.

## MVP Metric

The primary metric is `MSB-MVP`:

```text
MSB-MVP = 0.70 * style_order_score + 0.20 * margin_strength + 0.10 * P4_stability
```

- `style_order_score`: mean two-level monotonicity score. Good code has style-defect count `0`; bad code has style-defect count `1`. This reuses `cert_judge.hsj_scoring.compute_p2_or_p3_ordering_auc`.
- `margin_strength`: clipped mean positive score margin `(good_score - bad_score) / margin_target`.
- `P4_stability`: repeated-score reliability from `cert_judge.hsj_scoring.compute_p4_stability`.

The pair-level pass condition is `good_score_mean - bad_score_mean >= 0.05` by default. Keep the raw margin in reports; the threshold is only a first MVP convention.
With one score per `(pair_id, variant)`, P4 is vacuously `1.0` under the existing cert-judge definition; use repeated external judgments when reporting stability.

## Next Iterations

- Replace handcrafted pairs with accepted mathlib PR review examples.
- Add Lean compilation checks for both bad and good files against a pinned mathlib commit.
- Track source PR, reviewer, domain, tactic family, and style issue taxonomy in the manifest.
- Add human style labels and compare judge preference against expert preferences.
- Move stable data back to `StanfordLeanClub/mathlib-style-bench` when the protocol is less volatile.
