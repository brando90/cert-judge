# AGENT MISSION: Extend "Trusting the Formal Judge" — Reviewer Response Experiments

You are a research engineering agent working on a formal verification + LLM evaluation paper.
Your job is to implement, run, and record a set of targeted experiments that address peer 
reviewer critiques. The paper's core claim is: **a set of logical properties (identity, 
monotonicity) can certify whether an LLM judge is trustworthy for scoring Lean 4 theorems**.

The codebase uses:
- Python 3.10+
- Lean 4 (installed via elan, accessible via `lake` and `lean` CLI)
- Anthropic Python SDK (`anthropic`) for judge calls
- DSPy and/or Trace for agentic pipelines (check existing imports)
- VeriBench as the primary benchmark dataset

All experiment results must be saved to `results/` as JSON + CSV. 
All figures must be saved to `figures/` as PDF and PNG.
All new code goes in `experiments/` with one file per experiment.
After each experiment, write a `results/<experiment_name>/summary.md` 
with: what was tested, key numbers, and the 1-2 sentence takeaway for the paper.

---

## EXPERIMENT 1: Hard Identity Test (kills the "edit distance" critique)

**Goal**: Show the judge scores semantically equivalent but syntactically different theorems 
near-maximally, proving it reasons semantically rather than via string similarity.

**Steps**:
1. From VeriBench, sample 30 (theorem, reference_implementation) pairs.
2. For each theorem, produce 4 syntactic variants using this transformation pipeline:
   a. RENAME: Rename all variables (e.g., `n` → `k`, `h` → `hyp1`) using a Lean 4 
      AST-aware rename or simple regex with a validation step that re-checks Lean compiles.
   b. REORDER: Reorder hypothesis arguments where commutativity allows 
      (e.g., `theorem foo (a b : Nat) (h1 h2 : ...)` → swap `a b` order).
   c. STYLE: Replace `by exact` with `by { exact }`, expand `simp` calls to their 
      explicit lemma forms where possible, or add trivially true `have` intermediate steps.
   d. ALPHA: Full alpha-equivalence transformation — systematically rename ALL bound 
      variables to fresh names (`x0, x1, x2...`).
3. For each variant, call the LLM judge with `(original_theorem, variant, reference_impl)` 
   and record the score.
4. Also compute Levenshtein edit distance between original and each variant.
5. Plot: scatter of (edit_distance vs judge_score). If the judge is semantic, 
   high edit distance should NOT correlate with low scores.
6. Compute Pearson r between edit_distance and judge_score — expect near-zero or positive.
7. Separately compute Pearson r for the original identity test (identical inputs) as baseline.
8. Save all scores to `results/hard_identity/scores.csv`.
9. Generate a figure: 4-panel plot, one per transformation type, 
   x=edit_distance, y=judge_score, with a regression line.

**Pass criterion for the paper**: Mean judge score across all variants > 0.85, 
and Pearson(edit_distance, judge_score) < 0.3 (i.e., no meaningful negative correlation).

---

## EXPERIMENT 2: Hard Monotonicity Test — Semantic vs Syntactic Bugs

**Goal**: Show monotonicity holds for *subtle semantic bugs*, not just obvious syntactic ones,
further disproving the edit-distance hypothesis.

**Steps**:
1. From VeriBench, sample 20 (theorem, reference_impl) pairs with passing Lean proofs.
2. For each, create a 5-level degradation ladder:
   - Level 0: Original correct theorem (baseline)
   - Level 1: SUBTLE semantic bug — weaken one precondition 
     (e.g., `n > 0` → `n ≥ 0`, or `List.length l = n` → `List.length l ≤ n`)
   - Level 2: MODERATE semantic bug — remove one postcondition clause entirely
   - Level 3: SIGNIFICANT bug — swap `∧` for `∨` in a key conjunction
   - Level 4: SEVERE bug — replace theorem body with a trivially true but useless statement
     (e.g., `True`)
   
   For each level, VERIFY the modified theorem either:
   - Still compiles in Lean (so the judge can't just use Lean feedback), OR
   - Fails to compile — track this separately as it tests a different capability
   
3. Call the judge on each (degraded_theorem, reference_impl) pair and record scores.
4. Test WEAK monotonicity: for each theorem, check that scores are non-increasing 
   from level 0 → 4 (allow ties). Compute % of theorems satisfying weak monotonicity.
5. Compute Spearman rank correlation between degradation_level and judge_score (expect negative).
6. Also compute edit distance at each level — show semantic severity doesn't correlate 
   with edit distance (a Level 1 subtle bug may have edit_distance=3 but score drop of 0.3).
7. Plot: line chart per theorem (light gray) + mean line (bold), x=degradation_level, 
   y=judge_score. Add a secondary axis showing mean edit distance.
8. Save to `results/hard_monotonicity/`.

**Pass criterion**: ≥ 80% of theorems show weak monotonicity, 
Spearman r ≤ -0.6 between level and score.

---

## EXPERIMENT 3: Multi-Model Certification Ablation

**Goal**: Show the certification protocol is model-agnostic — some models pass, 
some fail — proving the protocol is a meaningful filter, not a rubber stamp.

**Steps**:
1. Select a representative subset of 20 theorem pairs from the identity test 
   and 20 from the monotonicity test (40 total certification tests).
2. Run ALL of the following models as judges on these 40 tests:
   - `claude-opus-4-5` (or latest available via Anthropic SDK)
   - `claude-haiku-4-5` (smaller, cheaper — hypothesize it may fail)
   - `claude-sonnet-4-5` (mid-tier)
   - If OpenAI key available: `gpt-4o` and `gpt-4o-mini`
   - If together.ai or ollama available locally: `llama-3-70b-instruct`
   Use IDENTICAL prompts for all models — do not tune per model.
3. For each model compute:
   - Identity score: mean score on identical-input pairs (expect near 1.0 for good models)
   - Monotonicity Spearman r on degradation ladder (expect strongly negative for good models)
   - CERTIFICATION PASS/FAIL: passes if identity_mean > 0.90 AND spearman_r < -0.5
4. Create a summary table:
   | Model | Identity Score | Monotonicity r | CERTIFIED? |
   |-------|---------------|----------------|------------|
5. This is the key table for the paper — it shows the protocol discriminates.
6. Save to `results/multi_model/`.

**Important**: If a model FAILS certification, that's a GOOD result for the paper. 
It shows the protocol has teeth.

---

## EXPERIMENT 4: Out-of-Domain Generalization Test

**Goal**: Show certification properties hold beyond VeriBench, 
addressing the "finite perturbations on one benchmark" critique.

**Steps**:
1. Source 15 theorem pairs from a DIFFERENT domain than VeriBench. Options:
   a. Mathlib4 — pull theorems about number theory (`Nat.Prime`, `GCD`, etc.)
   b. Lean 4 standard library theorems about `List`, `Array`, or `Option`
   c. Simple algorithm correctness theorems you write manually 
      (e.g., `sum_correct`, `reverse_involutive`)
   Script to fetch from Mathlib: search for theorems tagged `@[simp]` in `Mathlib.Data.Nat`
2. Run the full certification suite (identity + monotonicity) on these 15 pairs 
   using the primary certified judge (Claude Sonnet/Opus).
3. Report: does the judge maintain certification properties on out-of-domain theorems?
4. Save to `results/out_of_domain/`.

---

## EXPERIMENT 5: Semantic Equivalence Baseline (edit distance control)

**Goal**: Provide the quantitative proof that judge ≠ edit distance.

**Steps**:
1. Take all pairs from Experiment 1 (hard identity variants).
2. Implement three string-similarity baselines:
   - Levenshtein edit distance (normalized 0–1)
   - BLEU score (treating theorem text as a sentence)
   - Jaccard similarity on token sets
3. For each pair, record: (string_similarity_score, llm_judge_score)
4. Show that string similarity FAILS identity: syntactic variants have low string 
   similarity but the LLM judge correctly gives high scores.
5. Compute and report: on hard identity variants, 
   mean string_sim vs mean judge_score — expect large gap.
6. Save to `results/edit_distance_control/`.

---

## SHARED INFRASTRUCTURE TO BUILD

Before running experiments, implement these shared utilities in `experiments/utils/`:

### `lean_runner.py`
```python
# Utility to:
# 1. Write a Lean 4 theorem string to a temp .lean file
# 2. Run `lean --make` on it
# 3. Return (compiled: bool, error_msg: str)
# Use subprocess with timeout=30s
# Cache results by hash of theorem string to avoid re-running
```

### `judge_caller.py`
```python
# Utility to call the LLM judge with:
# - generated_theorem: str (Lean 4 code)  
# - reference_implementation: str (ground truth code)
# - model: str (model name)
# Returns: score (float 0-1), reasoning (str)
# Implement retry logic with exponential backoff
# Log all calls to results/judge_call_log.jsonl for auditability
# The judge prompt should be:
# """
# You are an expert in Lean 4 formal verification. 
# Score how well the GENERATED THEOREM captures the correctness properties
# of the REFERENCE IMPLEMENTATION on a scale from 0.0 to 1.0.
# 
# Scoring criteria:
# - 1.0: Theorem is semantically equivalent to what reference impl guarantees
# - 0.7-0.9: Theorem captures most properties but misses minor ones  
# - 0.4-0.6: Theorem captures some properties but has meaningful gaps
# - 0.1-0.3: Theorem is technically valid but misses core properties
# - 0.0: Theorem is trivially true or wrong
#
# REFERENCE IMPLEMENTATION:
# {reference_impl}
#
# GENERATED THEOREM:
# {generated_theorem}
#
# Respond with JSON only: {"score": <float>, "reasoning": "<one sentence>"}
# """
```

### `variant_generator.py`
```python
# Generates syntactic variants of Lean 4 theorems
# Implements the 4 transformation types from Experiment 1
# Each transformation validates the output still parses 
# (runs lean_runner.py to check compilation)
```

### `metrics.py`
```python
# Computes: pearson_r, spearman_r, weak_monotonicity_pct,
# levenshtein_normalized, bleu, jaccard
# All functions take lists of floats and return (stat, p_value)
```

---

## FIGURE REQUIREMENTS

All figures must be publication-ready (matplotlib, seaborn or plotly):
- Font size ≥ 12pt
- Axes fully labeled with units
- Error bars where applicable (run judge 3x per pair, report mean ± std)
- Color-blind friendly palette (use seaborn `colorblind` palette)
- Save as both `.pdf` (for paper) and `.png` (for README)

Required figures:
1. `fig_hard_identity.pdf` — scatter of edit_distance vs judge_score (Exp 1)
2. `fig_monotonicity_ladder.pdf` — score degradation curves (Exp 2)
3. `fig_model_certification_table.pdf` — heatmap of model × property (Exp 3)
4. `fig_string_vs_semantic.pdf` — bar chart of string_sim vs judge_score on variants (Exp 5)

---

## EXECUTION ORDER

Run in this order (each depends on infrastructure from previous):
1. Build `experiments/utils/` infrastructure first, test with 2–3 examples
2. Experiment 5 (easiest, validates infrastructure)
3. Experiment 1 (hard identity)
4. Experiment 2 (hard monotonicity)
5. Experiment 3 (multi-model — most API calls, run last)
6. Experiment 4 (out-of-domain — run in parallel with 3)

After ALL experiments complete, generate `results/PAPER_NUMBERS.md` 
containing every number that should go into the paper, formatted as:
"In the hard identity test, mean judge score across syntactic variants was X.XX (±Y.YY), 
while mean normalized edit distance was Z.ZZ, with Pearson r = W.WW (p < 0.05)."

---

## CONSTRAINTS

- Budget: minimize API calls. Cache all judge responses by (model, theorem_hash, reference_hash).
- If Lean 4 is not available in the environment, mock the compilation check but flag results clearly.
- All randomness must use `random.seed(42)` for reproducibility.
- Every experiment must run end-to-end in under 2 hours on a single machine.
- Do not modify existing paper code — only add to `experiments/`.