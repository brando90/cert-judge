# AGENT MISSION: Extend "Trusting the Formal Judge"
# Certification Experiments + W&B Tracking

You are a research engineering agent extending a formal verification + LLM evaluation paper.
Core claim: **logical properties (identity, monotonicity) can certify whether an LLM judge
is trustworthy for scoring Lean 4 theorems.**

Stack: Python 3.10+, Lean 4 (via elan/lake), Anthropic SDK, VeriBench benchmark, W&B.

**Directory layout:**
- New code → `experiments/` (one file per experiment)
- Results  → `results/<experiment_name>/summary.json` + `summary.md`
- Figures  → `figures/` as both `.pdf` and `.png`
- Do NOT modify existing paper code.

---

## STEP 0: W&B SETUP — run this block FIRST

```bash
export WANDB_API_KEY=$(cat ~/keys/brandos_wandb_key.txt)
export WANDB_PROJECT="trusting-formal-judge"
export WANDB_GROUP="certification-experiments"

pip show wandb > /dev/null 2>&1 || pip install wandb --break-system-packages
mkdir -p experiments/utils results figures
```

---

## STEP 1: Write `experiments/utils/push_per_run.py`

This is the most critical file. Every experiment MUST call it at the end.
It pushes: scalars, a results table row, and 4 bar charts to W&B.

```python
#!/usr/bin/env python3
"""
Per-run W&B push for certification judge experiments.
Usage:
  python experiments/utils/push_per_run.py \
    --run_name hard_identity \
    --model claude-sonnet-4-5 \
    --results results/hard_identity/summary.json \
    --experiment exp1_hard_identity
"""
import argparse, json, os, re
import wandb

PROJECT = os.environ.get("WANDB_PROJECT", "trusting-formal-judge")
GROUP   = os.environ.get("WANDB_GROUP",   "certification-experiments")

# Certification thresholds — edit here if you want to tune them
IDENTITY_THRESHOLD  = 0.90   # identity_mean must exceed this
SPEARMAN_THRESHOLD  = -0.50  # mono_spearman_r must be below this (more negative = better)
WEAK_MONO_THRESHOLD = 80.0   # weak_monotonicity_pct must exceed this


def parse(path: str) -> dict:
    """Parse summary.json. Falls back to regex on plain text."""
    text = open(path).read()
    try:
        return json.loads(text)
    except Exception:
        pass
    patterns = {
        "identity_mean_score":     r"identity_mean[_score]*\s*[:\s]+([0-9.]+)",
        "identity_std":            r"identity_std\s*[:\s]+([0-9.]+)",
        "monotonicity_spearman_r": r"spearman_r\s*[:\s]+([-0-9.]+)",
        "weak_monotonicity_pct":   r"weak_mono[noticity_%]*\s*[:\s]+([0-9.]+)",
        "pearson_edit_vs_judge":   r"pearson[_edit_vs_judge]*\s*[:\s]+([-0-9.]+)",
        "n_theorems":              r"n_theorems\s*[:\s]+([0-9]+)",
        "certified":               r"certified\s*[:\s]+([01])",
    }
    out = {}
    for k, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        out[k] = float(m.group(1)) if m else 0.0
    return out


def compute_certified(identity_mean: float, spearman_r: float, weak_mono_pct: float) -> int:
    """Returns 1 if judge passes certification, 0 otherwise."""
    return int(
        identity_mean  > IDENTITY_THRESHOLD and
        spearman_r     < SPEARMAN_THRESHOLD and
        weak_mono_pct  > WEAK_MONO_THRESHOLD
    )


def push(run_name: str, model: str, results_path: str,
         experiment: str = "", notes: str = ""):

    m = parse(results_path)

    identity     = round(float(m.get("identity_mean_score", 0)), 4)
    identity_std = round(float(m.get("identity_std", 0)), 4)
    spearman     = round(float(m.get("monotonicity_spearman_r", 0)), 4)
    weak_mono    = round(float(m.get("weak_monotonicity_pct", 0)), 2)
    pearson_ed   = round(float(m.get("pearson_edit_vs_judge", 0)), 4)
    n_theorems   = int(float(m.get("n_theorems", 0)))

    # Override certified from parsed value OR recompute from thresholds
    certified = compute_certified(identity, spearman, weak_mono)

    # Combined score: identity × (weak_mono / 100)
    # Perfect judge = 1.0 on both → combined = 1.0
    combined  = round(identity * (weak_mono / 100.0), 4)
    cert_str  = "CERTIFIED" if certified else "NOT_CERTIFIED"

    # ── Terminal summary ──────────────────────────────────────────────────────
    print(f"\n{'='*62}")
    print(f"  Experiment  : {experiment}")
    print(f"  Run         : {run_name}  |  Model: {model}")
    print(f"  {'─'*56}")
    print(f"  identity_mean       : {identity:.4f} ± {identity_std:.4f}  "
          f"(threshold > {IDENTITY_THRESHOLD})")
    print(f"  mono_spearman_r     : {spearman:.4f}          "
          f"(threshold < {SPEARMAN_THRESHOLD})")
    print(f"  weak_mono_%         : {weak_mono:.1f}%            "
          f"(threshold > {WEAK_MONO_THRESHOLD}%)")
    print(f"  pearson(edit,judge) : {pearson_ed:.4f}          (want near 0)")
    print(f"  n_theorems          : {n_theorems}")
    print(f"  combined_score      : {combined:.4f}")
    print(f"  certification       : {'✅ ' if certified else '❌ '}{cert_str}")
    print(f"{'='*62}\n")

    # ── W&B run ───────────────────────────────────────────────────────────────
    run = wandb.init(
        project=PROJECT,
        group=GROUP,
        name=f"{experiment}__{run_name}__{model.replace('/', '_')}",
        tags=[experiment, run_name, model, GROUP, cert_str.lower()],
        notes=(
            f"**Experiment**: {experiment}\n"
            f"**Run**: {run_name} | **Model**: {model}\n\n"
            f"| Metric | Value | Pass? |\n"
            f"|--------|-------|-------|\n"
            f"| identity_mean | {identity:.4f} | {'✅' if identity > IDENTITY_THRESHOLD else '❌'} |\n"
            f"| mono_spearman_r | {spearman:.4f} | {'✅' if spearman < SPEARMAN_THRESHOLD else '❌'} |\n"
            f"| weak_mono_% | {weak_mono:.1f}% | {'✅' if weak_mono > WEAK_MONO_THRESHOLD else '❌'} |\n"
            f"| pearson(edit,judge) | {pearson_ed:.4f} | — |\n\n"
            f"**Result: {cert_str}**\n\n{notes}"
        ),
        config={
            "run_name":            run_name,
            "model":               model,
            "experiment":          experiment,
            "n_theorems":          n_theorems,
            "identity_threshold":  IDENTITY_THRESHOLD,
            "spearman_threshold":  SPEARMAN_THRESHOLD,
            "weak_mono_threshold": WEAK_MONO_THRESHOLD,
        }
    )

    # ── Scalars ───────────────────────────────────────────────────────────────
    wandb.log({
        "identity_mean":        identity,
        "identity_std":         identity_std,
        "mono_spearman_r":      spearman,
        "mono_spearman_abs":    abs(spearman),   # higher = better, easier to read in bar charts
        "weak_mono_pct":        weak_mono,
        "pearson_edit_judge":   pearson_ed,
        "pearson_edit_abs":     abs(pearson_ed), # want near 0
        "n_theorems":           n_theorems,
        "certified":            certified,
        "combined_score":       combined,
    })

    # ── Results table (one row per run — accumulates across all runs) ─────────
    tbl = wandb.Table(
        columns=["experiment", "run", "model",
                 "identity_mean", "identity_std",
                 "mono_spearman_r", "weak_mono_pct",
                 "pearson_edit_judge", "n_theorems",
                 "combined_score", "certified"],
        data=[[
            experiment, run_name, model,
            identity, identity_std,
            spearman, weak_mono,
            pearson_ed, n_theorems,
            combined, cert_str
        ]]
    )
    wandb.log({"run_results_table": tbl})

    # ── Bar charts (4 key metrics) ────────────────────────────────────────────
    label = f"{experiment}/{run_name}"

    t = wandb.Table(columns=["run", "identity_mean"], data=[[label, identity]])
    wandb.log({"identity_mean_bar": wandb.plot.bar(
        t, "run", "identity_mean",
        title=f"Identity Mean Score — {label}")})

    t = wandb.Table(columns=["run", "mono_spearman_abs"], data=[[label, abs(spearman)]])
    wandb.log({"mono_spearman_abs_bar": wandb.plot.bar(
        t, "run", "mono_spearman_abs",
        title=f"|Spearman r| Monotonicity (higher=better) — {label}")})

    t = wandb.Table(columns=["run", "weak_mono_pct"], data=[[label, weak_mono]])
    wandb.log({"weak_mono_pct_bar": wandb.plot.bar(
        t, "run", "weak_mono_pct",
        title=f"Weak Monotonicity % — {label}")})

    t = wandb.Table(columns=["run", "combined_score"], data=[[label, combined]])
    wandb.log({"combined_score_bar": wandb.plot.bar(
        t, "run", "combined_score",
        title=f"Combined Score (identity × weak_mono%) — {label}")})

    run.finish()
    print(f"  W&B run: {run.url}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run_name",   required=True,  help="Short name for this run")
    p.add_argument("--model",      required=True,  help="Model name e.g. claude-sonnet-4-5")
    p.add_argument("--results",    required=True,  help="Path to summary.json")
    p.add_argument("--experiment", default="",     help="Experiment tag e.g. exp1_hard_identity")
    p.add_argument("--notes",      default="",     help="Free-text notes for W&B run")
    a = p.parse_args()
    push(a.run_name, a.model, a.results, a.experiment, a.notes)
```

---

## STEP 2: Write `experiments/utils/final_report.py`

Call this ONCE after all experiments are done.
Pulls all runs from W&B, deduplicates, prints terminal leaderboard,
and pushes a single shareable comparison report with 6 charts.

```python
#!/usr/bin/env python3
"""
Final W&B leaderboard report for certification judge experiments.
Run once after all experiments complete:
  python experiments/utils/final_report.py
"""
import wandb, os

PROJECT     = os.environ.get("WANDB_PROJECT", "trusting-formal-judge")
GROUP       = os.environ.get("WANDB_GROUP",   "certification-experiments")
REPORT_NAME = "FINAL--certification-leaderboard"

api      = wandb.Api()
all_runs = api.runs(
    f"{api.default_entity}/{PROJECT}",
    filters={"group": GROUP}
)

# Deduplicate: best combined_score per (experiment, run_name)
best = {}
for r in all_runs:
    if REPORT_NAME in r.name:
        continue
    exp     = r.config.get("experiment", "unknown")
    name    = r.config.get("run_name",   r.name)
    model   = r.config.get("model",      "unknown")
    key     = f"{exp}|{name}|{model}"
    score   = r.summary.get("combined_score", 0)
    if key not in best or score > best[key]["combined_score"]:
        best[key] = {
            "experiment":       exp,
            "run_name":         name,
            "model":            model,
            "identity_mean":    round(r.summary.get("identity_mean",       0), 4),
            "identity_std":     round(r.summary.get("identity_std",        0), 4),
            "mono_spearman_r":  round(r.summary.get("mono_spearman_r",     0), 4),
            "weak_mono_pct":    round(r.summary.get("weak_mono_pct",       0), 1),
            "pearson_edit":     round(r.summary.get("pearson_edit_judge",  0), 4),
            "n_theorems":       int(r.summary.get("n_theorems",            0)),
            "certified":        int(r.summary.get("certified",             0)),
            "combined_score":   round(r.summary.get("combined_score",      0), 4),
        }

rows = sorted(best.values(),
              key=lambda x: (x["certified"], x["identity_mean"]),
              reverse=True)

# ── Terminal leaderboard ──────────────────────────────────────────────────────
COL_W = [3, 20, 18, 22, 9, 9, 11, 11, 11, 9, 5]
HEADERS = ["#", "Experiment", "Run", "Model",
           "id_mean", "id_std", "spearman_r",
           "weak_mono%", "pearson_ed", "combined", "cert"]
sep = "+" + "+".join("-"*(w+2) for w in COL_W) + "+"
hdr = "| " + " | ".join(h.ljust(COL_W[i]) for i, h in enumerate(HEADERS)) + " |"
print(f"\n{'CERTIFICATION LEADERBOARD':^{sum(COL_W)+len(COL_W)*3}}")
print(f"{sep}\n{hdr}\n{sep}")
for i, d in enumerate(rows):
    cert_icon = "✅" if d["certified"] else "❌"
    cells = [
        str(i+1),
        d["experiment"][:COL_W[1]],
        d["run_name"][:COL_W[2]],
        d["model"][:COL_W[3]],
        f"{d['identity_mean']:.4f}",
        f"{d['identity_std']:.4f}",
        f"{d['mono_spearman_r']:.4f}",
        f"{d['weak_mono_pct']:.1f}%",
        f"{d['pearson_edit']:.4f}",
        f"{d['combined_score']:.4f}",
        cert_icon,
    ]
    print("| " + " | ".join(str(cells[j]).ljust(COL_W[j]) for j in range(len(COL_W))) + " |")
print(f"{sep}")

certified_rows = [d for d in rows if d["certified"]]
print(f"\n  {len(rows)} total runs | {len(certified_rows)} CERTIFIED | "
      f"{len(rows)-len(certified_rows)} NOT CERTIFIED\n")
if certified_rows:
    b = certified_rows[0]
    print(f"  Best certified: {b['experiment']} / {b['run_name']} ({b['model']})")
    print(f"    identity={b['identity_mean']:.4f}, spearman={b['mono_spearman_r']:.4f}, "
          f"weak_mono={b['weak_mono_pct']}%\n")

# ── W&B final report run ──────────────────────────────────────────────────────
run = wandb.init(
    project=PROJECT, group=GROUP, name=REPORT_NAME,
    tags=["summary", "final", GROUP],
    notes=(
        f"## Certification Leaderboard — Final Report\n\n"
        f"- **Total runs**: {len(rows)}\n"
        f"- **Certified**: {len(certified_rows)}\n"
        f"- **Not certified**: {len(rows)-len(certified_rows)}\n"
        f"- **Certification rate**: {len(certified_rows)/len(rows)*100:.1f}%\n\n"
        f"Best certified: "
        f"{certified_rows[0]['run_name'] if certified_rows else 'none'}\n\n"
        f"Certification criteria:\n"
        f"- identity_mean > 0.90\n"
        f"- mono_spearman_r < -0.50\n"
        f"- weak_mono_pct > 80%"
    )
)

# 1. Full leaderboard table
tbl = wandb.Table(
    columns=["rank","experiment","run","model",
             "identity_mean","identity_std","mono_spearman_r",
             "weak_mono_pct","pearson_edit","n_theorems",
             "combined_score","certified"],
    data=[[
        i+1, d["experiment"], d["run_name"], d["model"],
        d["identity_mean"], d["identity_std"], d["mono_spearman_r"],
        d["weak_mono_pct"], d["pearson_edit"], d["n_theorems"],
        d["combined_score"], "✅" if d["certified"] else "❌"
    ] for i, d in enumerate(rows)]
)
wandb.log({"leaderboard": tbl})

# 2. Identity mean bar — primary metric
t = wandb.Table(
    columns=["run", "identity_mean"],
    data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", d["identity_mean"]]
          for d in rows])
wandb.log({"identity_mean_comparison": wandb.plot.bar(
    t, "run", "identity_mean",
    title="Identity Mean Score by Run (higher = better)")})

# 3. |Spearman r| bar — monotonicity
t = wandb.Table(
    columns=["run", "mono_spearman_abs"],
    data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", abs(d["mono_spearman_r"])]
          for d in rows])
wandb.log({"mono_spearman_comparison": wandb.plot.bar(
    t, "run", "mono_spearman_abs",
    title="|Spearman r| Monotonicity by Run (higher = better)")})

# 4. Identity vs |Monotonicity| scatter — THE KEY CERTIFICATION PLOT
#    Certified models appear in top-right quadrant
t = wandb.Table(
    columns=["run", "identity_mean", "mono_spearman_abs"],
    data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}",
           d["identity_mean"], abs(d["mono_spearman_r"])]
          for d in rows])
wandb.log({"certification_scatter": wandb.plot.scatter(
    t, "identity_mean", "mono_spearman_abs",
    title="Identity vs |Monotonicity| — certified models cluster top-right")})

# 5. Pearson(edit, judge) bar — near 0 proves semantic reasoning
t = wandb.Table(
    columns=["run", "pearson_edit_judge"],
    data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", d["pearson_edit"]]
          for d in rows])
wandb.log({"pearson_edit_comparison": wandb.plot.bar(
    t, "run", "pearson_edit_judge",
    title="Pearson(edit_distance, judge_score) — near 0 = semantic judge")})

# 6. Combined score bar — summary metric
t = wandb.Table(
    columns=["run", "combined_score"],
    data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", d["combined_score"]]
          for d in rows])
wandb.log({"combined_score_comparison": wandb.plot.bar(
    t, "run", "combined_score",
    title="Combined Score (identity × weak_mono%) — higher = better")})

# 7. Summary scalars
wandb.log({
    "n_runs":                len(rows),
    "n_certified":           len(certified_rows),
    "certification_rate_%":  round(len(certified_rows)/len(rows)*100, 1) if rows else 0,
    "best_identity_mean":    rows[0]["identity_mean"] if rows else 0,
    "mean_identity_mean":    round(sum(d["identity_mean"] for d in rows)/len(rows), 4) if rows else 0,
    "mean_spearman_r":       round(sum(d["mono_spearman_r"] for d in rows)/len(rows), 4) if rows else 0,
    "mean_combined_score":   round(sum(d["combined_score"] for d in rows)/len(rows), 4) if rows else 0,
})

run.finish()
print(f"\n  W&B final report: {run.url}\n")
```

---

## STEP 3: Write Shared Utilities in `experiments/utils/`

### `lean_runner.py`
```python
# Write Lean 4 theorem string to a temp .lean file,
# run `lean --make` via subprocess with timeout=30s,
# return (compiled: bool, error_msg: str).
# Cache results by sha256(theorem_string) in results/lean_cache.json.
# If lean binary not found: return (None, "lean_not_available") — flag but don't crash.
```

### `judge_caller.py`
```python
# Call the LLM judge.
# Inputs: generated_theorem (str), reference_implementation (str), model (str)
# Returns: {"score": float, "reasoning": str, "mean": float, "std": float}
# - Run each pair 3x, return mean ± std (needed for error bars in figures)
# - Cache ALL calls by (model, sha256(theorem), sha256(ref)) in results/judge_cache.json
# - Retry with exponential backoff, 3 attempts max
#
# Judge prompt (do NOT modify between experiments — consistency is critical):
# -----------------------------------------------------------------------
# You are an expert in Lean 4 formal verification.
# Score how well the GENERATED THEOREM captures the correctness properties
# of the REFERENCE IMPLEMENTATION. Score from 0.0 to 1.0.
#
# - 1.0: Semantically equivalent to what the reference guarantees
# - 0.7-0.9: Captures most properties, misses minor ones
# - 0.4-0.6: Captures some properties, has meaningful gaps
# - 0.1-0.3: Technically valid Lean but misses core properties
# - 0.0: Trivially true (e.g., `True`) or incorrect
#
# REFERENCE IMPLEMENTATION:
# {reference_impl}
#
# GENERATED THEOREM:
# {generated_theorem}
#
# Respond ONLY with valid JSON, no markdown:
# {"score": <float 0.0-1.0>, "reasoning": "<one sentence max>"}
# -----------------------------------------------------------------------
```

### `variant_generator.py`
```python
# Produce 4 syntactic variants of a Lean 4 theorem string.
# Each variant is semantically equivalent but syntactically different.
#
# RENAME  — rename all variables (n→k, h→hyp1, xs→items, etc.)
# REORDER — swap order of hypotheses in the theorem signature
# STYLE   — change proof style: `exact` ↔ `{ exact }`, expand `simp`
# ALPHA   — full alpha rename: all bound variables → x0, x1, x2...
#
# After generating each variant:
#   1. Call lean_runner.py to validate it compiles
#   2. If it doesn't compile, try a simpler substitution
#   3. Always return the variant (with compiled flag) — never block on Lean
```

### `metrics.py`
```python
# pearson_r(xs, ys)         → (r: float, p: float)
# spearman_r(xs, ys)        → (r: float, p: float)
# weak_monotonicity_pct(ladders: list[list[float]]) → float
#   ladders is a list of score sequences (one per theorem).
#   A ladder passes if scores are non-increasing (allow ties).
#   Returns % of ladders that pass.
# levenshtein_normalized(a, b) → float (0=identical, 1=totally different)
# bleu_score(reference, hypothesis) → float
# jaccard_tokens(a, b)      → float
```

---

## EXPERIMENTS

All experiments share this summary.json schema.
Fields not relevant to a given experiment should be set to 0.

```json
{
  "identity_mean_score":     0.0,
  "identity_std":            0.0,
  "monotonicity_spearman_r": 0.0,
  "weak_monotonicity_pct":   0.0,
  "pearson_edit_vs_judge":   0.0,
  "n_theorems":              0,
  "certified":               0,
  "lean_available":          true,
  "notes":                   ""
}
```

**After EVERY experiment, push to W&B immediately:**
```bash
python experiments/utils/push_per_run.py \
  --run_name <run_name> \
  --model <model> \
  --results results/<experiment_name>/summary.json \
  --experiment <exp_tag>
```

---

### EXPERIMENT 5 (run FIRST — smoke test + validates infrastructure)
**Edit Distance Control: prove judge ≠ string matching**

1. Take 10 theorem pairs from VeriBench as a smoke test.
2. For each pair generate all 4 syntactic variants (via variant_generator.py).
3. For each (original, variant): compute levenshtein_normalized, bleu, jaccard, AND judge_score.
4. Key result: variants with HIGH edit distance still get HIGH judge scores.
5. Compute Pearson r between levenshtein and judge_score → expect near 0 or positive.
6. Figure: side-by-side bars of mean(levenshtein) vs mean(judge_score) per variant type.
   Save as `figures/fig_string_vs_semantic.pdf` + `.png`.
7. Write `results/edit_distance_control/summary.json`. Set certified=0 (not a full cert test).
8. Push: `--run_name edit_distance_control --experiment exp5_edit_distance_control`

**Pass:** mean judge_score on variants > 0.80 AND Pearson(levenshtein, judge) < 0.30

---

### EXPERIMENT 1: Hard Identity Test
**Show judge is semantic, not edit-distance-based**

1. Sample 30 (theorem, reference_impl) pairs from VeriBench.
2. For each, generate all 4 syntactic variants via variant_generator.py.
3. Call judge on (original, variant, reference_impl). Run 3x per pair, record mean ± std.
4. Compute Pearson r between levenshtein_distance and judge_score → expect < 0.30.
5. Compute mean judge_score across all 120 variant pairs → expect > 0.85.
6. Figure: 4-panel scatter (one per variant type), x=levenshtein, y=judge_score,
   regression line + R² annotation.
   Save as `figures/fig_hard_identity.pdf` + `.png`.
7. Write `results/hard_identity/summary.json`. Set certified based on thresholds.
8. Push: `--run_name hard_identity --experiment exp1_hard_identity`

**Pass:** identity_mean > 0.85 AND Pearson(edit, score) < 0.30

---

### EXPERIMENT 2: Hard Monotonicity — Semantic Bug Ladder
**Show monotonicity holds for subtle semantic bugs**

1. Sample 20 theorem pairs with passing Lean proofs from VeriBench.
2. Build 5-level degradation ladder per theorem:
   - Level 0: Original correct theorem
   - Level 1: SUBTLE — weaken precondition (e.g., `n > 0` → `n ≥ 0`)
   - Level 2: MODERATE — remove one postcondition clause
   - Level 3: SIGNIFICANT — swap `∧` for `∨` in key conjunction
   - Level 4: SEVERE — replace body with `True`
   For each level: run lean_runner.py, record compiled (bool).
3. Call judge on each level. Run 3x, record mean.
4. Compute Spearman r between degradation_level and judge_score → expect ≤ -0.60.
5. Compute weak_monotonicity_pct across all 20 theorem ladders → expect ≥ 80%.
6. Critical check: Level 1 has tiny levenshtein distance but meaningful score drop.
   Record and report the mean(levenshtein at level 1) vs mean(score drop at level 1).
7. Figure: line chart — light gray line per theorem, bold mean line.
   Secondary axis: mean levenshtein distance per level.
   Save as `figures/fig_monotonicity_ladder.pdf` + `.png`.
8. Write `results/hard_monotonicity/summary.json`.
9. Push: `--run_name hard_monotonicity --experiment exp2_hard_monotonicity`

**Pass:** weak_mono_pct ≥ 80% AND Spearman r ≤ -0.60

---

### EXPERIMENT 3: Multi-Model Certification Ablation
**Show the protocol is a meaningful filter — some models fail**

1. Take 20 pairs from Exp 1 + 20 from Exp 2 = 40 certification test pairs.
2. Run EACH of these models as the judge using IDENTICAL prompts (no per-model tuning):
   - claude-opus-4-5      (expect: PASS)
   - claude-sonnet-4-5    (expect: PASS)
   - claude-haiku-4-5     (expect: possibly FAIL — smaller, cheaper)
   - gpt-4o               (if OPENAI_API_KEY set, else skip)
   - gpt-4o-mini          (if OPENAI_API_KEY set, else skip)
3. For each model compute identity_mean, mono_spearman_r, weak_mono_pct, certified.
4. Save each model to its own summary.json in `results/multi_model/<model>/summary.json`.
5. Push each model as a SEPARATE W&B run:
   ```bash
   python experiments/utils/push_per_run.py \
     --run_name <model_name> \
     --model <model_name> \
     --results results/multi_model/<model_name>/summary.json \
     --experiment exp3_multi_model
   ```
6. Figure: heatmap — rows=models, cols=[identity_mean, |spearman_r|, weak_mono%, certified].
   Green = pass threshold, red = fail. Save as `figures/fig_model_certification_table.pdf`.

**Goal:** At least one model FAILS certification (proves protocol has teeth).
If ALL models pass, lower thresholds slightly and re-evaluate — the point is discrimination.

---

### EXPERIMENT 4: Out-of-Domain Generalization
**Show certification holds beyond VeriBench**

1. Source 15 theorem pairs from OUTSIDE VeriBench. Priority:
   a. Mathlib4 theorems (Nat.Prime, GCD, List properties) — fetch via lake/mathlib
   b. Lean 4 stdlib theorems about List, Array, Option
   c. If neither available: write 15 simple theorems manually
      (sum_correct, reverse_involutive, filter_length_le, etc.)
2. Run full certification suite: hard identity variants + monotonicity ladder.
3. Report: does the certified judge (from Exp 1+2) maintain properties out-of-domain?
4. Write `results/out_of_domain/summary.json`.
5. Push: `--run_name out_of_domain_mathlib --experiment exp4_out_of_domain`

---

## EXECUTION ORDER

```
Step 0  — W&B setup + mkdir
Step 1  — Write push_per_run.py  ← most critical, verify it works with a dry run first
Step 2  — Write final_report.py
Step 3  — Write shared utils (lean_runner, judge_caller, variant_generator, metrics)
          Test on 2-3 examples before running any full experiment.

Exp 5   — Edit distance control (smoke test, ~10 pairs, validates the whole pipeline)
Exp 1   — Hard identity (~30 pairs × 4 variants × 3 judge calls = ~360 calls)
Exp 2   — Hard monotonicity (~20 pairs × 5 levels × 3 calls = ~300 calls)
Exp 4   — Out of domain (run in parallel with Exp 2 if possible)
Exp 3   — Multi-model (most API calls, run last)

Final   — python experiments/utils/final_report.py
        — Write results/PAPER_NUMBERS.md (see template below)
```

---

## PAPER NUMBERS TEMPLATE

After all experiments, write `results/PAPER_NUMBERS.md` with every number
formatted for direct copy-paste into the paper or rebuttal:

```
EXP 1 — Hard Identity:
"Mean judge score across syntactic variants was X.XX (±Y.YY), while mean
normalized edit distance was Z.ZZ. Pearson r between edit distance and
judge score was W.WW (p=P.PP), confirming the judge reasons semantically."

EXP 2 — Hard Monotonicity:
"Weak monotonicity held for X% of theorems. Spearman r between
degradation level and judge score was -Y.YY (p=P.PP). Notably,
Level 1 (subtle precondition weakening) had mean edit distance of Z.ZZ
but mean score drop of W.WW, demonstrating sensitivity to semantic changes
that string similarity cannot detect."

EXP 3 — Multi-Model:
"Of N models evaluated, M passed certification (identity_mean > 0.90,
Spearman r < -0.50, weak_mono_pct > 80%). [Model X] failed with
identity_mean=A.AA and Spearman r=B.BB, demonstrating the protocol
is a discriminative filter and not a rubber stamp."

EXP 4 — Out-of-Domain:
"On 15 Mathlib4 theorems outside VeriBench, the certified judge achieved
identity_mean=X.XX and Spearman r=-Y.YY, confirming generalization
beyond the training distribution."

EXP 5 — Edit Distance Control:
"String similarity metrics (levenshtein, BLEU, Jaccard) scored our
syntactic variants at mean=X.XX, while the LLM judge scored the same
pairs at mean=Y.YY, a gap of Z.ZZ. This directly demonstrates that
the judge evaluates semantic content rather than surface form."
```

---

## CONSTRAINTS

- `random.seed(42)` everywhere for reproducibility
- Cache ALL judge calls: `results/judge_cache.json` keyed by (model, sha256(theorem), sha256(ref))
- Run each judge call 3x, report mean ± std (required for error bars in figures)
- If Lean 4 unavailable: set `lean_available: false` in summary.json and flag in W&B notes
- Budget: ~600 judge API calls total. The cache prevents re-spending on re-runs.
- Every experiment must complete in under 2 hours on a single machine
- All figures: font ≥ 12pt, axes labeled with units, colorblind-safe palette
  (`seaborn.set_palette("colorblind")`), saved as both `.pdf` and `.png`