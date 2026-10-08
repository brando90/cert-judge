# Five-current-rater cached comparison and behavioral design

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit/README.md>

**Status:** Complete, archived 10-07-2026. No new inference and no manuscript changes.

Read [the results](RESULTS_five_rater_comparison.md) for the verified answer, [the prospective plan](PROSPECTIVE_PLAN.md) for stronger weakening and gaming tests, and [proposed methods wording](PROPOSED_METHODS.md) for a proportionate reuse disclosure. The frozen [protocol](PROTOCOL.md), [selection receipt](results/SELECTION.json), and [supplement scope](SUPPLEMENT.md) distinguish planned selection from descriptive completion analyses.

## Reproduction

The original computations ran on skampere2 with Python 3.12.3, NumPy 1.26.4 and SciPy 1.11.4. Use that environment or an equivalent environment managed by `uv`; no model client or credential is needed. The pinned VeriBench source revision is `3169b2fd15e3d42338f09b2e5999ef66faac6019`. The verifier fails on changed input hashes. Choose an isolated checkout before regenerating outputs. From its repository root:

```bash
CJ45_EXP=experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit
CJ45_VB=/path/to/pinned/veribench
python3 "$CJ45_EXP/scripts/verify.py" --veribench "$CJ45_VB"
python3 -c "import sys; sys.path.insert(0, '$CJ45_EXP/scripts'); import test_analysis as t; [f() for n,f in vars(t).items() if n.startswith('test_')]"
```

For full offline reproduction, run `inventory.py --veribench "$CJ45_VB"`, `analyze.py select --veribench "$CJ45_VB"`, then `analyze.py evaluate --veribench "$CJ45_VB"`, `behavioral.py --veribench "$CJ45_VB"`, `legacy.py --veribench "$CJ45_VB"`, and `supplement.py --veribench "$CJ45_VB"` in that order, using the same script directory and interpreter. Each statistical script defaults to 10,000 draws and seed 45. `build_followup_manifest.py` only enumerates a proposal; it cannot call a model. `report.py` renders the report from those files. Rerun the verifier after generation. `run_cached.sh` and `run_legacy.sh` retain the original host-specific launch commands as execution provenance; the commands above are portable.

## Artifacts and interpretation

- [Individual current ratings](results/individual_current_ratings.json), [coverage](results/coverage_by_item.json), [reference provenance](results/reference_provenance.json), [inventory](results/inventory.json) and [input hashes](results/input_files.json).
- [Utility views](results/comparisons/), [modern proxy associations](results/proxy_associations.json), [individual-rater agreement](results/rater_agreement.json), [historical-score views](results/legacy/), [semantic audit](results/semantic_audit.json), [gaming audit](results/gaming_audit.json).
- [Verification receipt](results/verification.json), [analysis receipt](results/analysis_receipt.json), [supplement receipt](results/supplement_receipt.json), [historical receipt](results/legacy_receipt.json).
- [Proposed follow-up manifest](results/followup_manifest.json): no admissions, unquoted cost, zero calls made.

Existing source caches and the frozen protocol are unchanged. Their original path strings are provenance, not instructions to recreate retired roots. The archive-aware verifier resolves the protocol’s old logical hash key to its present location. Runtime receipts and recovery history remain at `research_notes/recovery_10-07-2026/` in the repository root; the current [checkpoint](../../../CKPT_codex-cj-five-rater-recovery.md) links the final state. No unstarted follow-up keeps this completed analysis active.
