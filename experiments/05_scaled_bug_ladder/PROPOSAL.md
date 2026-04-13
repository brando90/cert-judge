# Experiment 05: Scaled Bug Ladder (P2 at Scale)

## Motivation

The current P2 (monotonicity to bugs) result is based on **one manually-created bug ladder** for the `my_add` example (10 cumulative bugs in `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/`). The Exp2 experiment in `02_reviewer_response_neurips_math_ai_2026/` uses regex-based degradation on 20 VeriBench files, but those degradations are syntactic heuristics (e.g., replace `∧` with `∨`), not true semantic bug insertions.

This experiment **scales up** the manual approach:
- Automatically generate **semantic** bug ladders for **all** VeriBench files (150 files)
- Use Claude as the **bug inserter** (understands Lean 4 semantics)
- Use Claude as the **judge** (replacing gpt-4o-mini)
- Produce a robust, large-N P2 monotonicity measurement

## Design

### Bug Ladder Generation (Claude as Bug Inserter)

For each VeriBench `.lean` file (the gold reference):
1. **Level 0**: Original file (gold, no bugs)
2. **Level 1**: 1 semantic bug inserted
3. **Level 2**: 2 cumulative semantic bugs
4. **Level 3**: 3 cumulative semantic bugs
5. **Level 4**: 4 cumulative semantic bugs

**Why 5 levels (0-4), not 10?**
- Many VeriBench files are 100-250 lines with 2-5 theorems/properties
- 10 bugs would oversaturate small files (nowhere to put distinct bugs)
- 5 levels is enough to measure monotonicity (matches our grading scale granularity)
- The manual `my_add` example had 9 bugs in a 173-line file; most VeriBench files are comparable or smaller

**Bug types** (Claude is instructed to choose from these categories):
- **Property definition errors**: Wrong mathematical property (e.g., `n + 0 = n` -> `n + 1 = n`)
- **Postcondition weakening**: Remove a conjunct from a postcondition, or replace `∧` with `∨`
- **Implementation logic errors**: Break the imperative implementation (e.g., off-by-one, no-op loop)
- **Equivalence specification errors**: Break the equivalence theorem (e.g., `f a b = g a b` -> `f a b = f a b`)
- **Precondition strengthening/weakening**: Change precondition to make it trivially true or overly restrictive

Each bug must be **semantic** (changes the meaning), not just syntactic. The file must remain valid Lean 4 syntax (parseable, though proofs can be `sorry`).

### Bug Insertion Prompt

Claude receives:
1. The current file (with N-1 bugs already inserted)
2. A list of bugs already inserted (so it doesn't repeat)
3. Instructions to insert exactly ONE new semantic bug
4. The categories of bugs to choose from
5. Return: the modified file + a description of the bug inserted

### Judging (Claude as Judge)

For each file and each bug level:
- Score the buggy version against the original (gold) using the standard judge prompt
- Use `claude-sonnet-4-20250514` as the judge model (via Anthropic API)
- 3 repeats per pair (for P4 stability measurement too)
- Total calls: 150 files x 4 buggy levels x 3 repeats = **1,800 judge calls**
  (plus 150 x 3 = 450 identity calls for Level 0 = **2,250 total**)

### Metrics

- **P2 per-file**: Spearman rho between bug level [0,1,2,3,4] and judge score for each file
- **P2 aggregate**: Spearman rho across all (file, level) pairs
- **Weak monotonicity %**: Fraction of adjacent level pairs where score[level] >= score[level+1]
- **AUC**: Pairwise ordering accuracy (from `compute_p2_or_p3_ordering_auc()`)
- **P1 identity**: Level 0 scores (should be ~1.0)
- **P4 stability**: Variance across the 3 repeats per pair
- **Per-split breakdown**: Results split by VeriBench category (easy, cs, humaneval, real_code, security)

### Output

```
experiments/05_scaled_bug_ladder/
  results/
    bug_ladders/          # Generated .lean files: {filename}_level{0-4}.lean
    bug_descriptions.json # What bug was inserted at each level for each file
    judge_scores.json     # All judge scores (cached)
    summary.json          # Aggregate P2, P1, P4 metrics
    per_file_results.csv  # Per-file Spearman, weak_mono, mean scores
    per_split_results.csv # Per-split aggregate metrics
  figures/
    monotonicity_ladder_all.png    # All-file overlay + bold mean
    monotonicity_by_split.png      # One subplot per VeriBench split
    per_file_spearman_hist.png     # Histogram of per-file Spearman rho
  PROPOSAL.md            # This file
  run_bug_ladder.py      # Main experiment script
  run.sh                 # Shell wrapper
```

## Comparison to Existing Experiments

| Aspect | Exp02 (current) | This Experiment |
|---|---|---|
| Bug insertion | Regex heuristics | LLM-generated semantic bugs |
| Files | 20 sampled | All 150 VeriBench |
| Bug levels | 5 (regex-based) | 5 (LLM cumulative) |
| Judge model | gpt-4o-mini | claude-sonnet-4-20250514 |
| Judge calls | 300 | ~2,250 |
| Per-split analysis | No | Yes |
| Bug descriptions | Implicit (regex) | Explicit (logged) |

## Cost Estimate

- Bug generation: 150 files x 4 bugs x ~500 tokens = ~300K tokens (~$0.90 input + $2.40 output at Sonnet pricing)
- Judging: 2,250 calls x ~1K tokens = ~2.25M tokens (~$6.75 input + $18 output)
- **Total: ~$28 at Sonnet pricing** (rough estimate)

## How to Run

```bash
cd experiments/05_scaled_bug_ladder
bash run.sh
# or directly:
python run_bug_ladder.py --model claude-sonnet-4-20250514 --n_repeats 3
```

Requires `ANTHROPIC_API_KEY` set in environment or in `~/keys/`.
