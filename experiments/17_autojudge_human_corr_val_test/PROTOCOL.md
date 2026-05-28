# Folder 17 - Autojudge Val/Test Protocol
**TLDR:** This protocol freezes a no-new-LLM prompt-selection experiment for Codex, Opus, and Leanstral judges. It aggregates five participant label files plus Ethan pass1/pass2, selects a judge prompt only on a fixed validation split, and reports the held-out test correlation without retuning.

This file freezes the protocol before any new result is interpreted. No new LLM calls are allowed. Any deviation observed during execution belongs in `REPORT.md`, not by silently editing the protocol after seeing the test result.

## Scientific question (locked)

Can a validation-only autojudge selection rule pick a Lean theorem judge whose held-out test scores correlate with the aggregate human target?

Operational criterion: for each judge family (Codex, Opus, Leanstral), select the eligible prompt with the highest validation Spearman correlation to the aggregate human target, then report that selected prompt's test Spearman correlation on the frozen held-out split.

## Locked parameters

- Human label sources: five top-level participant files in `experiments/human_labels/` plus `experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv` and `experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv`.
- Human aggregation: raw arithmetic mean over all nonblank labels per exact `gold_file::candidate_file` key.
- Ethan pass handling: pass1 and pass2 are separate label sources because the requested target is `5 + pass1 + pass2`.
- Candidate families:
  - Codex: `experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16`, model `gpt-5.3-codex`.
  - Opus: `experiments/04_veribench_validation/results_exp16_opus47_r3_median`, model `claude-opus-4-7`.
  - Leanstral: `experiments/04_veribench_validation/results_exp16_leanstral_r3_median`, model `labs-leanstral-2603`.
- Primary candidate allowlist: `kind=llm` only. Explicit `llm_bad`, edit-distance, random, and other-family controls are excluded from primary selection.
- Split unit: `gold_file`; all three candidate rows for a task stay together.
- Split rule: sort tasks by `SHA256("cert-judge-exp17-autojudge-val-test-v1\0" + gold_file)`, first 50% train/validation, remaining 50% test.
- Selection objective: maximize validation Spearman(`judge_score`, aggregate human mean) within each family.
- Tie break: lexicographic `judge_id`.
- Bootstrap intervals: 5000 resamples over candidate-pair rows; these are descriptive only.

## Scale verification (no further normalization)

Human labels are ordinal 0-5. Spearman correlation is invariant to linear rescaling, so the primary analysis uses raw means.

Saved judge `score_mean` values are already normalized to 0-1 in the reused Exp16-style `detail_rows.csv` files.

## Verified data schema

Human TSV files contain:

- `gold_file`
- `candidate_file`
- `human_score_0_5`

Judge `detail_rows.csv` files contain:

- `judge_id`
- `row_type`
- `item_key`
- `score_mean`

Judge `judge_rows.csv` files contain:

- `judge_id`
- `kind`
- `model`
- `prompt_name`

## Pre-conditions for run

- Run from `/Users/brandomiranda/cert-judge-autojudge-human-corr-val-test`.
- Do not load LLM provider keys.
- Do not make new LLM judge calls.
- Use the stdlib-only script so stale NumPy/SciPy/Pandas wheels cannot affect results.

## Estimated wall-clock

CPU-only and expected to finish in under one minute.

## Pass/fail / abort rules

- Abort if any locked human label file is missing.
- Abort if fewer than 12 exact scored pairs are common across all primary candidates.
- Report missing exact-score pairs instead of adding new judge calls.
- Do not change split seed, candidate allowlist, aggregation, or selection objective after seeing test results.

## Identity / contact crib (verified)

- Brando requested PR assignment/review from Ethan and Elyas.
- Ethan Hersch GitHub handle from the existing protocol: `@ehersch`.
- Elyas Obbad GitHub handle from `~/ultimate-utils/py_src/uutils/collaborators.py`: `@eobbad`.
