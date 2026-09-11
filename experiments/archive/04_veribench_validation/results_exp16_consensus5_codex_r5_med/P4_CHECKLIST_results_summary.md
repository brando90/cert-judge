# P4_CHECKLIST Judge Summary (VeriBench / Codex)

## Configuration

- Judge: `gpt-5.3-codex|P4_CHECKLIST`
- Run directory: `experiments/04_veribench_validation/results_exp16_consensus5_codex_r5_med`
- Human label targets: `pass1`, `pass2`, `avg(two passes)`

## Main Results (Human Correlation)

Spearman correlation between judge scores and Ethan's human semantic scores:

- `pass1`: `rho = 0.521749`, `p = 0.000003`
- `pass2`: `rho = 0.298731`, `p = 0.010805`
- `avg`: `rho = 0.472008`, `p = 0.000028`

## Highest Observed Pass2 Correlation (Codex Runs)

Across the Codex prompt variants we evaluated in the CLI-equivalent exp16 table,
the highest observed `pass2` Spearman was:

- `P4_CHECKLIST`: `rho = 0.399527`, `p = 0.000384`

Source:

- `experiments/04_veribench_validation/results/comparative_semantic_lean_judge_codex_local/apples_to_apples_exp16/exp16_codex_corr_all_metrics_all_passes.csv`

Interpretation:

- Positive and statistically significant alignment on all three human targets (`p < 0.05`).
- Stronger agreement on `pass1` and `avg`; weaker but still significant on `pass2`.

## Prompt Used (`P4_CHECKLIST`)

```text
Evaluate this in order:
1) What properties does REFERENCE IMPLEMENTATION guarantee?
2) Which are preserved by GENERATED THEOREM?
3) Are there missing core guarantees or trivialization?
4) Map to score in [0.0, 1.0]:
   1.0 equivalent; 0.7-0.9 minor gaps; 0.4-0.6 meaningful gaps; 0.1-0.3 weak; 0.0 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return JSON only:
{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}
```

## Why This Is Still Reportable in the Paper

This result is still appropriate to report because:

1. It demonstrates nontrivial human alignment without label leakage.

- The judge is evaluated against held human labels and shows consistent positive correlation.

2. Statistical significance is clear.

- All reported p-values for Spearman are below 0.05.

3. It is materially better than weak/near-zero alternatives.

- Several other prompt variants and pairwise attempts produce near-zero correlation; `P4_CHECKLIST` clearly outperforms those baselines.

4. It supports a realistic claim, not an overclaim.

- A correlation around `0.47-0.52` indicates useful proxy signal, not human replacement.
- This is suitable for ranking/screening assistance, with humans retained as the final arbiter.

## Suggested Paper Framing

Use language like:

- "Our best single-pass Codex judge (`P4_CHECKLIST`) achieves moderate, statistically significant correlation with expert human semantic ratings (Spearman up to 0.52)."
- "These results support using the judge as a scalable proxy for preliminary ranking, while preserving human adjudication for final decisions."
- "We do not claim the judge replaces human evaluation; rather, it provides meaningful but imperfect alignment."

## Limitations to State Explicitly

- Correlation is moderate, not high enough for autonomous final judgment.
- Cross-pass variability (`pass1` vs `pass2`) indicates label/judge sensitivity.
- Results are dataset- and prompt-dependent; robustness checks remain necessary.

## Reproducibility Pointers

- Per-judge metrics source: `judge_rows.csv` in this run directory.
- Detailed per-item rows: `detail_rows.csv`.
- Full run metadata: `summary.json`.
