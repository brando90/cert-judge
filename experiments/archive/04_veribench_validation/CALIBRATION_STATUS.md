# Five-Human Calibration Status

## Goal

We want judge-human correlations to be at least `0.7` for every main judge/model family when evaluated against all five human annotators.

The current target is:

- Human data: `experiments/human_labels/participant*.tsv`
- Main human target: five-rater item mean, unless noted otherwise
- Main threshold: item-level Spearman `>= 0.7`
- Candidate calibrated method: per-task isotonic calibration
- Desired model families: LeanStral, Codex, Claude, Qwen, plus any other judge families in the EXP16/EXP22 panels

Important: a high number is useful only if we can state what kind of evidence it is. The current per-task isotonic results are best described as a calibration upper bound, not held-out validation.

## Key Experiments

### EXP34: all-human task aggregation

Script:

```bash
python3 experiments/04_veribench_validation/exp34_all_human_task_aggregation.py
```

Outputs:

- `results_exp34_all_human_task_aggregation/`
- `results_exp34_all_human_task_aggregation_with_old_prompt/`

Purpose:

- Aggregate all available human labels by item and task.
- Re-correlate cached judge scores against the all-human aggregate.

Main result:

- Current human labels only: best all-human task Spearman was `0.510` for `labs-leanstral-2603|P1_BASELINE`.
- Including old-prompt labels: best all-human task Spearman was `0.460`.
- This did not recover the old `0.7+` result.

Takeaway:

- Simple all-human averaging is not enough.
- It makes the story more honest but weaker.

### EXP36: five-human super target

Script:

```bash
python3 experiments/04_veribench_validation/exp36_super_human_pass3.py
```

Outputs:

- `results_exp36_super_human_pass3/`
- `results_exp36_super_human_pass3_min5/`

Purpose:

- Build a five-human target from participant files.
- Evaluate raw judge correlations without strong calibration.

Takeaway:

- Raw item-level five-human agreement generally stays below `0.7`.
- This motivates calibration, but also shows the uncalibrated claim is not currently strong enough.

### EXP37: calibration and aggregation sweep

Script:

```bash
python3 experiments/04_veribench_validation/exp37_five_human_calibration_sweep.py
```

Outputs:

- `results_exp37_five_human_calibration_sweep/REPORT.md`
- `results_exp37_five_human_calibration_sweep/RECOMMENDED.md`
- `results_exp37_five_human_calibration_sweep/sweep_results.csv`

Purpose:

- Sweep human aggregation choices and calibration methods.
- Look for ways to get `>= 0.7` on the five-human target.

Important result:

- Many rows exceed `0.7`, but most are oracle-style because the calibration fits on the same items it evaluates.
- Holdout calibration did not reach `0.7`.

Useful `>= 0.7` examples from EXP37:

| Model family | Judge | Human target / method | Calibration | Item Spearman | n |
| --- | --- | --- | --- | ---: | ---: |
| Codex | `gpt-5.3-codex|BAD_STRINGY` | `human_median` | per-task isotonic oracle | `0.939` | 60 |
| Claude | `claude-opus-4-7|P1_BASELINE` | `human_zscore_mean` | per-task isotonic oracle | `0.843` | 60 |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | weighted target variant | per-task isotonic oracle | `0.864` | 60 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | `human_mean` | per-task isotonic oracle | `0.843` | 60 |

Takeaway:

- If we allow target variants and same-item per-task calibration, Codex, Claude, LeanStral, and GPT-4o-mini can clear `0.7`.
- Qwen does not have the required item-level calibrated row in this sweep.

### EXP38: five-human mean plus per-task isotonic

Script:

```bash
python3 experiments/04_veribench_validation/exp38_five_human_per_task_isotonic.py
```

Outputs:

- `results_exp38_five_human_per_task_isotonic/per_judge_metrics.csv`
- `results_exp38_five_human_per_task_isotonic/plots/`
- copied paper figures under `paper_latex/TMLR_2026/figures/exp38_five_human_per_task_isotonic/`

Purpose:

- Use the five-human mean target.
- Apply per-task isotonic calibration to cached judge scores.
- Generate paper-ready plots.

Best EXP38 results by model family:

| Model family | Best judge | Raw item rho | Calibrated item rho | Calibrated task rho | Above `0.7` item? |
| --- | --- | ---: | ---: | ---: | --- |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | `0.422` | `0.840` | `0.914` | Yes |
| Codex | `gpt-5.3-codex|BAD_STRINGY` | `-0.379` | `0.919` | `0.995` | Yes, but bad prompt |
| Codex | `gpt-5.3-codex|P14_HUMAN_ALIGN_V2` | `-0.080` | `0.722` | `0.804` | Yes |
| Codex | `gpt-5.3-codex|P3_CONCISE` | `-0.397` | `0.714` | `0.742` | Yes |
| Claude | `claude-opus-4-7|P4_CHECKLIST` | `-0.252` | `0.682` | `0.733` | No item, yes task |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | `0.263` | `0.843` | `0.916` | Yes |
| Random | `random_r1` | `0.181` | `0.934` | `1.000` | Yes, but invalidating caveat |
| Edit distance | `editdist_e1` | `-0.566` | `0.922` | `1.000` | Yes, but invalidating caveat |

Takeaway:

- EXP38 gets several non-LeanStral families over `0.7`.
- Claude misses `0.7` on item-level five-human mean but clears task-level.
- The method also makes random and edit-distance look excellent, so it is not a clean validity claim.

### EXP39: AutoMetrics-inspired AutoTI

Scripts:

```bash
python3 experiments/04_veribench_validation/exp39_autometrics_autoti.py
python3 experiments/04_veribench_validation/exp39_autometrics_autoti.py --target median --out-dir experiments/04_veribench_validation/results_exp39_autometrics_autoti_median
python3 experiments/04_veribench_validation/exp39_autometrics_autoti.py --target zscore_mean --out-dir experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean
```

Outputs:

- `results_exp39_autometrics_autoti/`
- `results_exp39_autometrics_autoti_median/`
- `results_exp39_autometrics_autoti_zscore_mean/`

Purpose:

- Inspired by AutoMetrics, treat prompt-level judge scores as a small metric bank.
- Learn a ridge composition per model family.
- Compare same-item upper bound with leave-one-task-out generalization.

Main result on five-human mean:

| Model family | Same-item AutoTI item rho | Same-item AutoTI task rho | Leave-one-task-out item rho | Leave-one-task-out task rho |
| --- | ---: | ---: | ---: | ---: |
| Codex | `0.625` | `0.746` | `0.285` | `0.306` |
| Claude | `0.429` | `0.567` | `0.224` | `0.289` |
| LeanStral | `0.462` | `0.668` | `0.322` | `0.494` |
| GPT-4o-mini | `0.518` | `0.750` | `0.335` | `0.585` |

Target variants did not rescue LeanStral above `0.7` for EXP39:

- Median target: LeanStral same-item `0.396` item, `0.681` task.
- Z-score target: LeanStral same-item `0.477` item, `0.670` task.

Takeaway:

- AutoTI is more principled than per-task isotonic, but it does not currently achieve the `>= 0.7` item-level goal across model families.
- Held-out learned calibration is much weaker than same-item/oracle calibration.

### EXP42: Proper global calibration transfer (definitive held-out result)

Script:

```bash
python3 experiments/04_veribench_validation/exp42_proper_transfer_calibration.py
```

Outputs:

- `results_exp42_proper_transfer/PAPER_TABLE.md`
- `results_exp42_proper_transfer/PER_REVIEWER_TABLE.md`
- `results_exp42_proper_transfer/MULTISEED_TABLE.md`
- `results_exp42_proper_transfer/sweep_results.csv`

Purpose:

- Fit global isotonic calibration on train tasks ONLY.
- Apply calibration to test tasks with ZERO test-label leakage.
- Report per-reviewer (participant1–5) as well as aggregate breakdown.
- Multi-seed robustness: 10 random 70/30 splits.

Primary table (seed=42, global isotonic, zscore_mean, best prompt selected on train):

| Model | Raw item ρ | Train item ρ | **Test item ρ** |
| --- | ---: | ---: | ---: |
| LeanStral | 0.426 | 0.566 | -0.084 |
| GPT-4o-mini | 0.266 | 0.419 | 0.295 |
| GPT-5.3 Codex | -0.052 | 0.119 | -0.460 |
| Claude Opus 4.7 | 0.203 | -0.001 | -0.108 |

Multi-seed result (mean ± std across 10 seeds, best prompt per seed):

| Model | Mean test ρ | Std |
| --- | ---: | ---: |
| LeanStral | 0.457 | ±0.218 |
| GPT-4o-mini | 0.439 | ±0.173 |
| GPT-5.3 Codex | 0.119 | ±0.275 |
| Claude Opus 4.7 | 0.291 | ±0.273 |

Takeaway:

- **No model family achieves ≥0.70 test item ρ under zero-leakage global calibration.**
- Multi-seed mean test ρ ranges from 0.12 (Codex) to 0.46 (LeanStral) with std ±0.2–0.3.
- High variance across seeds (LeanStral min=0.026, max=0.822) confirms the result is
  task-split-dependent and fundamentally limited by only 8 test tasks.
- This is the honest lower bound; EXP38/EXP41 per-task oracle is the upper bound.
- The 0.70+ numbers from EXP40/EXP41 PAPER_TABLE are all per-task oracle (same items),
  NOT held-out evidence.

## Qwen Status

Current Qwen artifacts found:

- `results_exp28_varaware_qwen_avg/`
- `results_exp28_varaware_qwen_pass1/`
- `results_exp28_varaware_qwen_pass2/`
- `results_exp30_tivar_v3_all_models/judge_trust_vector_qwen_*.csv`
- `results_exp33_tivar_protocol_new_human_stress/`

What we have:

- Qwen trust-vector summaries.
- Qwen legacy judge-level correlations.
- Qwen new-human stress summaries.

What we do not currently have:

- Qwen EXP16-style `detail_rows.csv` with item-level `human_eval_union` scores.
- Therefore, Qwen cannot be included in EXP38 per-task isotonic calibration as-is.

Relevant Qwen numbers:

| Source | Result |
| --- | --- |
| `results_exp28_varaware_qwen_avg/judge_trust_vector.csv` | best legacy human Spearman around `0.370` |
| `results_exp30_tivar_v3_all_models/tivar_cross_model_summary.csv` | Qwen pass2 family-level TI/human correlation `0.905`, avg `0.667` |
| `results_exp33_tivar_protocol_new_human_stress/expanded_new_human_tivar_summary.csv` | Qwen new-human avg item correlation around `-0.310`, avg task around `-0.143` |

Takeaway:

- Qwen does not currently satisfy the five-human `>= 0.7` claim.
- The high Qwen pass2 number is a legacy family-level TI correlation, not the same as item-level five-human calibrated judge-score correlation.
- To test Qwen fairly, generate Qwen `detail_rows.csv` on the same five-human item panel, then rerun EXP38 with the Qwen result directory included.

## Current Answer To The Goal

Strict five-human mean plus EXP38 per-task isotonic:

| Model family | Gets item rho `>= 0.7`? | Notes |
| --- | --- | --- |
| LeanStral | Yes | `0.840` |
| Codex | Yes | `0.714` to `0.919`, depending on prompt |
| Claude | No | best item `0.682`; task `0.733` |
| GPT-4o-mini | Yes | `0.843` |
| Qwen | Not established | missing item-level calibrated data |

Any five-human target variant plus EXP37 per-task isotonic:

| Model family | Gets item rho `>= 0.7`? | Notes |
| --- | --- | --- |
| LeanStral | Yes | `0.864` best, but target variant is weighted |
| Codex | Yes | `0.939` best, but best prompt is `BAD_STRINGY` |
| Claude | Yes | `0.843` with `zscore_mean` |
| GPT-4o-mini | Yes | `0.843` |
| Qwen | No / missing | no comparable row |

Held-out / more defensible learned calibration:

| Method | Gets all model families above `0.7`? |
| --- | --- |
| EXP39 AutoTI leave-one-task-out | No |
| EXP37 holdout calibration | No |

## Paper Framing

Recommended wording:

> We additionally study a low-data calibration upper bound inspired by adaptive metric induction. Using five human annotators, within-task isotonic calibration can raise item-level judge-human Spearman above `0.7` for several model families. However, this calibration is fit on the same task items and can also inflate random or edit-distance baselines, so we report it as calibration capacity rather than held-out evidence of judge validity.

Avoid saying:

> All judges are validated above `0.7` on all human data.

Better claim:

> Several judge families can be calibrated above `0.7` against the five-human target under same-item within-task isotonic calibration; held-out calibration remains below this threshold and Qwen requires item-level cached scores before it can be evaluated under the same protocol.

## Next Steps For Agents

1. Generate Qwen item-level judge score caches.
   - Need EXP16-style outputs with both `judge_rows.csv` and `detail_rows.csv`.
   - The `detail_rows.csv` must contain `row_type == human_eval_union` rows.
   - Include the same item keys as the five-human participant TSVs.

2. Rerun EXP38 with Qwen included.
   - Add the Qwen result directory to `--result-dirs`.
   - Check `per_judge_metrics.csv` for Qwen calibrated item and task Spearman.

3. Improve Claude item-level mean result.
   - Current strict five-human mean best is `0.682`, close to `0.7`.
   - Try median or z-score target if the paper can justify annotator normalization.
   - Try task-level reporting if the claim is task agreement rather than item agreement.

4. Keep random/edit-distance baselines in every calibration table.
   - If random/edit-distance also exceed `0.7`, label the method as an oracle upper bound.
   - Do not use this alone as evidence that a judge is semantically valid.

5. Separate three claims in writing.
   - Raw judge-human alignment: conservative, currently below `0.7` for many judges.
   - Same-item calibration capacity: can exceed `0.7` for several families.
   - Held-out validity: not yet above `0.7` across all families.

## Quick Commands

Run five-human per-task isotonic:

```bash
python3 experiments/04_veribench_validation/exp38_five_human_per_task_isotonic.py
```

Run aggregation/calibration sweep:

```bash
python3 experiments/04_veribench_validation/exp37_five_human_calibration_sweep.py
```

Run AutoMetrics-inspired learned AutoTI:

```bash
python3 experiments/04_veribench_validation/exp39_autometrics_autoti.py
```

Inspect best calibrated EXP38 rows:

```bash
python3 - <<'PY'
import csv
p = "experiments/04_veribench_validation/results_exp38_five_human_per_task_isotonic/per_judge_metrics.csv"
rows = list(csv.DictReader(open(p)))
by = {}
for r in rows:
    model = r["model"] or r["judge_id"].split("|")[0]
    rho = float(r["per_task_iso_item_spearman_r"])
    if model not in by or rho > float(by[model]["per_task_iso_item_spearman_r"]):
        by[model] = r
for model, r in sorted(by.items()):
    print(model, r["judge_id"], r["per_task_iso_item_spearman_r"], r["per_task_iso_task_spearman_r"])
PY
```
