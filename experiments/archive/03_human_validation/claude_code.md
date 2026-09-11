# Experiment 03 — Human-Judge Agreement Study

## Goal
Measure agreement between the LLM judge and human expert annotators on Lean 4 theorem quality.
This directly addresses Reviewer ivJs's "no human validation" concern and Reviewer 36Hd's
"missing details" concern by establishing a human ground truth for judge alignment.

---

## Research Question
> Does the LLM judge score align with expert human assessment of Lean 4 theorem quality?

Target metrics:
- ICC(2,1) between human raters: > 0.70 (good inter-rater reliability)
- Pearson/Spearman between human mean and LLM judge: > 0.70
- AUC-ROC for binary "acceptable/not-acceptable" classification: > 0.80

---

## Experimental Design

### Stimulus set: 30 theorem-quality pairs
- **Source**: 10 VeriBench theorems × 3 degradation levels (L0, L2, L4)
  - L0: original correct theorem
  - L2: moderate bug (remove ∧ clause)
  - L4: severe bug (replace with True)
- **Total**: 30 Lean 4 snippets to rate

### Annotators
- **Option A (ideal)**: 3 Lean 4 experts (grad students or postdocs with formal verification experience)
- **Option B (practical)**: 3 CS annotators with programming experience + brief Lean 4 tutorial
- Each rates all 30 snippets independently, in randomized order

### Rating task
For each Lean 4 theorem snippet, rate:
1. **Correctness** (1–5): Is the theorem mathematically correct?
2. **Specificity** (1–5): Does the theorem say something non-trivial (not trivially True/trivially provable)?
3. **Overall quality** (1–10): Would you accept this theorem as a useful specification?

Show annotators:
- The Lean 4 snippet (statement only, no proof)
- A 2-sentence description of what the theorem claims
- A reference to what the theorem *should* say (the L0 original)

---

## Implementation Plan

### File structure
```
experiments/03_human_validation/
├── claude_code.md              # this file
├── data/
│   stimulus_set.json           # 30 theorem snippets with metadata
│   annotation_template.csv     # blank template for annotators
│   annotations/
│       annotator_1.csv
│       annotator_2.csv
│       annotator_3.csv
├── exp3_human_validation.py    # main experiment script
├── utils/
│   icc_analysis.py             # ICC(2,1) via pingouin
│   correlation_analysis.py     # Pearson/Spearman human vs judge
│   plot_agreement.py           # Bland-Altman, scatter, heatmap
└── results/
    human_validation/
        summary.json
        icc_results.json
        correlation_results.json
        figures/
```

### Step 1 — Generate stimulus set (`generate_stimuli.py`)
```python
import json, random
from pathlib import Path
random.seed(42)

# Load 10 VeriBench theorems (same as Exp2)
# For each: generate L0 (original), L2 (moderate bug), L4 (severe bug)
# Save as stimulus_set.json with fields:
# {
#   "id": "thm_001_L0",
#   "theorem_id": "thm_001",
#   "level": 0,
#   "lean_code": "...",
#   "description": "States that for all natural numbers n, n + 0 = n",
#   "reference_statement": "...",   # L0 version shown to annotators
#   "llm_judge_score": 0.942        # pre-computed
# }

VERIBENCH = Path.home() / "veribench/veribench_dataset/lean_src/veribench"
files = sorted(VERIBENCH.glob("*.lean"))[:10]
```

### Step 2 — Run LLM judge on all stimuli
Use existing `judge_caller.py` to score all 30 snippets with 3 calls each.
Cache in `results/judge_cache.json`.

### Step 3 — Collect human annotations
Provide `data/annotation_template.csv` to each annotator:
```
id,correctness_1_5,specificity_1_5,overall_1_10,notes
thm_001_L0,,,,
thm_001_L2,,,,
...
```
Annotators fill this in independently. Randomize row order per annotator.

### Step 4 — Analysis (`exp3_human_validation.py`)

```python
import pandas as pd
import numpy as np
import pingouin as pg
from scipy import stats
import wandb

# Load annotations
ann1 = pd.read_csv("data/annotations/annotator_1.csv")
ann2 = pd.read_csv("data/annotations/annotator_2.csv")
ann3 = pd.read_csv("data/annotations/annotator_3.csv")

# Load LLM judge scores
stimuli = json.load(open("data/stimulus_set.json"))
judge_scores = {s["id"]: s["llm_judge_score"] for s in stimuli}

# --- Inter-rater reliability (ICC) ---
# Stack ratings into long format for pingouin
ratings = pd.DataFrame({
    "id": ann1["id"],
    "rater_1": ann1["overall_1_10"],
    "rater_2": ann2["overall_1_10"],
    "rater_3": ann3["overall_1_10"],
})
# Convert to long format
long = ratings.melt(id_vars="id", var_name="rater", value_name="score")
icc = pg.intraclass_corr(data=long, targets="id", raters="rater", ratings="score")
icc_21 = icc[icc["Type"] == "ICC2"]["ICC"].values[0]
icc_21_ci = icc[icc["Type"] == "ICC2"][["CI95%"]].values[0][0]
print(f"ICC(2,1) = {icc_21:.3f}, 95% CI = {icc_21_ci}")

# --- Human mean vs LLM judge correlation ---
human_mean = ratings[["rater_1","rater_2","rater_3"]].mean(axis=1) / 10  # normalise to [0,1]
llm_scores = ratings["id"].map(judge_scores)

r_pearson, p_pearson = stats.pearsonr(human_mean, llm_scores)
r_spearman, p_spearman = stats.spearmanr(human_mean, llm_scores)
r_kendall, p_kendall = stats.kendalltau(human_mean, llm_scores)
r2 = r_pearson**2

# --- Per-level analysis ---
# Test: do humans and LLM both agree L0 > L2 > L4?
for level in [0, 2, 4]:
    ids = [s["id"] for s in stimuli if s["level"] == level]
    h = human_mean[ratings["id"].isin(ids)].mean()
    j = llm_scores[ratings["id"].isin(ids)].mean()
    print(f"L{level}: human_mean={h:.3f}, judge_mean={j:.3f}")

# --- Log to W&B ---
run = wandb.init(
    project="trusting-formal-judge",
    name="human_validation",
    group="certification-experiments",
    tags=["exp3_human", "human-validation", "icc"],
    config={"n_stimuli": 30, "n_annotators": 3, "n_levels": 3},
)
wandb.log({
    "icc_21": icc_21,
    "icc_21_ci_lo": icc_21_ci[0],
    "icc_21_ci_hi": icc_21_ci[1],
    "pearson_human_judge": r_pearson,
    "spearman_human_judge": r_spearman,
    "kendall_human_judge": r_kendall,
    "r2_human_judge": r2,
    "p_pearson": p_pearson,
    "p_spearman": p_spearman,
    "n_stimuli": 30,
    "n_annotators": 3,
})

# Log scatter table: human_mean vs llm_judge_score
scatter_table = wandb.Table(
    columns=["stimulus_id", "level", "human_mean", "llm_judge_score"],
    data=[[
        ratings["id"].iloc[i],
        stimuli_level_map[ratings["id"].iloc[i]],
        human_mean.iloc[i],
        llm_scores.iloc[i],
    ] for i in range(len(ratings))]
)
wandb.log({"human_vs_judge_scatter": scatter_table})
wandb.finish()

# Save results
results = {
    "icc_21": icc_21,
    "pearson_human_judge": r_pearson,
    "spearman_human_judge": r_spearman,
    "kendall_human_judge": r_kendall,
    "r2_human_judge": r2,
    "certified": (
        icc_21 > 0.70
        and abs(r_spearman) > 0.70
    ),
}
json.dump(results, open("results/human_validation/summary.json", "w"), indent=2)
print(json.dumps(results, indent=2))
```

### Step 5 — Figures (`utils/plot_agreement.py`)
1. **Scatter plot**: human_mean vs llm_judge_score, coloured by level, regression line, r² annotation
2. **Bland-Altman plot**: agreement between human mean and LLM judge
3. **Per-level box plot**: human ratings vs LLM scores side-by-side for L0/L2/L4
4. **ICC forest plot**: per-metric ICC(2,1) with 95% CI

---

## Expected Results

| Metric | Expected | Pass threshold |
|---|---|---|
| ICC(2,1) human-human | > 0.70 | > 0.70 |
| Pearson human vs judge | > 0.70 | > 0.70 |
| Spearman human vs judge | > 0.70 | > 0.70 |
| R² human vs judge | > 0.50 | > 0.50 |

If the LLM judge passes all thresholds → **human-validated certification**.

---

## How to Run

```bash
source $HOME/uv_envs/cert-judge/bin/activate
export WANDB_API_KEY=$(cat ~/keys/brandos_wandb_key.txt)
export OPENAI_API_KEY=$(cat ~/keys/openai_api_brandos_personal_key.txt)

cd experiments/03_human_validation
python generate_stimuli.py          # creates data/stimulus_set.json + annotation template
# --- collect annotations from 3 humans manually ---
python exp3_human_validation.py     # analysis + W&B logging
python utils/plot_agreement.py      # figures
```

---

## Dependencies
```
pingouin>=0.5.4    # ICC(2,1)
scipy>=1.11        # Pearson, Spearman, Kendall
pandas>=2.0        # annotation loading
wandb>=0.18        # experiment tracking
plotly>=5.20       # interactive figures
kaleido>=0.2       # static PNG export
```

---

## Notes
- Stimulus level L1 (subtle: weaken precondition) is omitted from human study — too subtle
  for non-experts to reliably rate without domain knowledge
- If real Lean experts are unavailable, use CS PhD students who have taken a types/logic course
- Randomize stimulus order per annotator to avoid order effects
- Show annotators the L0 reference alongside each stimulus so they have context
- This experiment does NOT require running new LLM judge calls if you use cached scores from Exp2

---

## Reviewer Response Text (draft)

> "To address the concern about human validation, we conducted a human-judge agreement study (Experiment 3)
> in which [N] annotators with formal methods backgrounds independently rated 30 Lean 4 theorem snippets
> spanning three quality levels. We measured ICC(2,1) for inter-rater reliability and Pearson/Spearman
> correlation between human mean ratings and LLM judge scores. The LLM judge achieves ICC(2,1) = [X],
> Spearman ρ = [Y] (p<0.001), confirming alignment with expert human judgment."
