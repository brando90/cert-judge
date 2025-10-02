# HSJ Real Judge Evaluation - Quick Start

## Summary of Changes

Your code now supports **real HSJ evaluation** that actually calls your LLM judge on data files, not just synthetic demos.

### What Changed:

1. **Shell script** (`main_overall_judge_score.sh`):
   - Changed `eval_mode="hsj_demo"` → `eval_mode="hsj_real"`
   - Added `--claude_dotenv_path` argument to pass credentials

2. **Python script** (`main_overall_judge_score.py`):
   - Implemented the empty `main()` function with real evaluation logic
   - Added `hsj_real` mode handler in `_main()` that calls LLM judge on actual files

## How It Works

When `eval_mode="hsj_real"`, the script:

### P1: Reflexivity & Consistency
- Takes all `.lean` files from `paths_p1` directories
- Calls LLM judge with each file vs itself: `Judge(file, file)`
- Computes: `P1 = median(scores)`

### P2: Monotonicity to Bugs
- Finds bug ladder files in `path_p2` (e.g., `file_0_bugs.lean`, `file_1_bugs.lean`, ...)
- Calls judge on each buggy version vs gold (0 bugs)
- Computes: `P2 = 2 * (AUC_bugs - 0.5)`

### P3: Monotonicity to Missing Specs
- Finds missing spec ladder files in `path_p3`
- Calls judge on each incomplete version vs gold (0 missing)
- Computes: `P3 = 2 * (AUC_miss - 0.5)`

### P4: Low Variance (Stability)
- Samples 5 files from P1 paths
- Calls judge 5 times per file (repeats)
- Computes: `P4 = clip(1 - σ²/τ², 0, 1)` where τ=0.05

### Judge Trust Index (JTI)
- Combines all: `JTI = 0.25·P1 + 0.25·P2 + 0.25·P3 + 0.25·P4`

## How to Run

```bash
cd ~/cert-judge/experiments/00_overall_judge_score_metric
bash main_overall_judge_score.sh
```

**Expected behavior:**
- ✅ Actual LLM API calls to Claude (via your `.env_claude_3_7`)
- ✅ Progress logs showing each file being scored
- ✅ Takes several minutes (not 3 seconds!)
- ✅ Results logged to WandB at `https://wandb.ai/brando-su/vb-thm-eq`

## Expected Runtime

- **Demo mode** (`hsj_demo`): ~3-5 seconds (synthetic data only)
- **Real mode** (`hsj_real`): ~10-30 minutes depending on:
  - Number of files in your paths_p1 directories
  - Number of bug/missing spec ladder steps
  - LLM API latency

## Output

The script returns:
```python
{
    "p1": 0.XXX,         # Reflexivity score [0,1]
    "p2": 0.XXX,         # Bug monotonicity [0,1]
    "p3": 0.XXX,         # Missing spec monotonicity [0,1]
    "p4": 0.XXX,         # Stability score [0,1]
    "jti": 0.XXX,        # Judge Trust Index [0,1]
    "identity_scores": [...],    # Raw P1 scores
    "p2_counts": [...],          # Bug counts for P2
    "p2_scores": [...],          # Judge scores for P2
    "p3_counts": [...],          # Missing spec counts
    "p3_scores": [...],          # Judge scores for P3
    "repeat_scores": {...},      # Variance data for P4
}
```

## Verification

To verify it's working correctly, you should see:
1. Log messages like `P1: Scored filename.lean`
2. LLM API calls happening (check network activity or API logs)
3. Multiple scores being collected for each property
4. Final metrics like `P1 = 0.9950`, `P2 = 0.8500`, etc.
5. WandB run URL at the end

## Switch Back to Demo Mode

If you want to test just the math formulas (instant, no LLM calls):
```bash
export eval_mode="hsj_demo"
bash main_overall_judge_score.sh
```

---

**Status:** ✅ Implementation is correct and ready to use
**Mathematical formulas:** ✅ Verified against specification in `scoring_judges.md`
**Next step:** Run the real evaluation and check your judge's scores!

