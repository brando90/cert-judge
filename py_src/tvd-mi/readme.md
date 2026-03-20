# TVD-MI Judge

## Quick Start

```bash
# From py_src directory:
python veribench/tvd-mi/tvd-mi-judge.py --lean-dir ../veribench_dataset/lean_src --output ../results --examples 10

# From project root:
python py_src/veribench/tvd-mi/tvd-mi-judge.py --lean-dir veribench_dataset/lean_src --output results --examples 10
```

## ⚠️ IMPORTANT: Multiple Agents Required

TVD-MI requires **multiple agent versions of the same task**. If you only have 1 agent, all scores will be 0.0.

### File Naming Pattern

Your files must follow this pattern:
```
<task_id>__<agent_name>.lean
```

**Examples:**
- `humaneval_0__baseline.lean` (task: humaneval_0, agent: baseline)
- `humaneval_0__trace_debug.lean` (task: humaneval_0, agent: trace_debug)
- `humaneval_1__baseline.lean` (task: humaneval_1, agent: baseline)
- `humaneval_1__trace_debug.lean` (task: humaneval_1, agent: trace_debug)

### How to Get Multiple Agents

See `HOW_TO_GET_MULTIPLE_AGENTS.md` in the project root for detailed instructions on:
- Renaming files to create multiple agents
- Creating agent data JSON manually
- Combining outputs from different experiments
- Generating multiple agent versions

## Usage

```bash
python veribench/tvd-mi/tvd-mi-judge.py \
  --lean-dir <path_to_lean_files> \
  --output <output_dir> \
  --examples <num>
```

### Arguments:
- `--lean-dir`: Directory containing Lean files with pattern `<task_id>__<agent_name>.lean`
- `--output`: Directory to save results
- `--examples`: Number of examples to process
- `--workers`: Number of parallel workers (default: 5)
- `--verbosity`: Output verbosity level 0-2 (default: 0)
- `--no-recursive`: Don't recursively search subdirectories (default: searches recursively)

## Output

The script will:
1. Build agent-data JSON from Lean files
2. Run TVD-MI analysis on all examples
3. Save individual task results to `output/tvd_mi_individual_examples/`
4. Aggregate results and save to `output/tvd_mi_aggregated.json`
5. Save score matrix for correlation analysis to `output/tvd_mi_individual_examples/tvd_mi_score_matrix.json`

## Correlation Analysis

After running TVD-MI, use the correlation script to compare with VeriBench oracle metrics:

```bash
python py_src/veribench/tvd-mi/correlate_tvdmi_veribench.py \
    --tvdmi-matrix results/tvd_mi_individual_examples/tvd_mi_score_matrix.json \
    --veribench-results path/to/veribench/results.json \
    --output results/correlation_analysis.json \
    --metric unit_test_accuracy
```

## Proxy vs Oracle (Item-Level)

If you have a **pairwise item matrix** (e.g., information-relatedness across tasks),
you can collapse each row into a proxy score and correlate against oracle scores:

```bash
python py_src/veribench/tvd-mi/proxy_vs_oracle.py \
  --pairwise-matrix path/to/pairwise_matrix.json \
  --oracle-scores path/to/oracle_scores.json \
  --output results/proxy_vs_oracle.json \
  --null-shuffles 500
```

Expected formats:
- Pairwise matrix JSON with `pairwise_matrix` or `matrix` (square), and optional `item_ids`.
- Oracle scores as `{\"item_id\": score, ...}` or `{\"item_ids\": [...], \"scores\": [...]}`.
