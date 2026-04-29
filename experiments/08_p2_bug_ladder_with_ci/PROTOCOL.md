# Folder 08 — PROTOCOL (LOCKED before any expensive run)

This file freezes the protocol before analysis begins. It is written
PRIOR to seeing any results. Any deviation observed during execution
is documented in `REPORT.md` → "Open questions for Ethan", not by
editing this file.

## Scientific question (locked)

When a single LLM judge is asked the same `(candidate, gold)` query
multiple times under non-deterministic decoding, how stable is the
reported P2 monotonicity signal — i.e. does the apparent
"score ↓ as bug count ↑" trend survive once per-x sampling uncertainty
is shown as 95% confidence intervals on each bug-count file?

Operational form. For each k ∈ {0..9} on the
`data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/` ladder, draw
`num_samples=15` independent judge calls and aggregate per-x mean ±
95% CI (t-based primary; percentile bootstrap as ablation, re-using
the same raw matrix). Pass/fail is locked to per-file Spearman
ρ ≤ −0.7 (matches Folder 07's P2 threshold). A separate finding
fires if |per-call ρ − per-file ρ| > 0.1, indicating sampling-noise
dominance over the property signal.

This experiment is the measurement-rigor complement to Folder 07's
per-judge property sanity checks: it does not redefine P2, it makes
P2's reported trend statistically defensible by replacing the original
veribench Figure 6's single-LLM-call scatter with mean ± CI markers.

## Scope (locked)

Per-x 95% confidence-interval re-plot of the P2 bug-count vs LLM
judge file-equivalence-score property, on the
`my_add_file_eq_with_bugs` ladder, **single judge per run**.

Out of scope, by design:

- Multi-judge overlay → **Folder 08b** (follow-up).
- P3 spec ladder → reuse via filename regex change; do not fork.
  P3 expanded-panel rerun is **Folder 07c**.
- File-resampling (sample-set) slope CI → **Folder 08c** (follow-up).

## Locked metrics & thresholds

- **Per-x aggregation:** mean over `num_samples` judge calls.
- **Per-x CI (primary):** t-based two-sided 95% CI from `scipy.stats.t.ppf`.
- **Per-x CI (ablation):** percentile bootstrap, `bootstrap_iters=2000`.
- **Per-file correlation panel:** Spearman ρ, Kendall τ, Pearson r, R².
- **Per-call correlation panel:** same four metrics on the
  `(bug_count_repeated, score_per_call)` long-form view.
- **OLS slope:** fit on per-file means; reported in legend.
- **Pass/fail (locked, matches Folder 07 P2 threshold):**
  - per-file Spearman ρ ≤ −0.7 → judge passes P2 monotonicity.
  - |per-call ρ − per-file ρ| > 0.1 → flag sampling-noise dominance
    as a finding; does NOT fail the judge.

## Locked analysis params

- `num_samples = 15` (LLM calls per bug-count file).
- `max_workers = 16` (concurrent judge calls; raise on a fat host).
- `bootstrap_iters = 2000` (only when `--bootstrap` is set).
- `seed = 42`.
- `max_score = 30` (matches the prompt template's score range).
- Plot uses `ax.errorbar(yerr=2-row asymmetric)` so the t-CI and
  bootstrap-CI variants render the same code path.
- Both CI flavors run on the same raw `(num_samples, num_files)`
  matrix — the bootstrap ablation does NOT re-call the LLM.

## Verified data layout (Mode A)

Bug ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/`
- 10 files matching `^my_add_(\d+)_bugs\.lean$`, k ∈ {0..9}
- Gold reference = the k=0 file
  (matches Folder 00's `build_ladder` convention,
  `experiments/00_overall_cert_judge_metric_with_properties/main_overall_judge_score.py:181`)

Judge call entry point:
- `veribench.metrics.sim_file_eq_llm_judge.get_sim_score_file_eq_llm_result_in_json_str`
- Returns `{"score": int, "normalized_score": float in [0,1], ...}`
- The runner consumes `normalized_score` only.

Prompt template:
- `~/veribench/veribench_prompts/eval_prompts/file_equiv_prompts/simplest_prompt_varying_score_range.txt`
- Same template Folder 00 uses; do NOT swap without filing a follow-up.

Model dispatch:
- `TRACE_CUSTOMLLM_MODEL` is read at module import inside veribench.
- The wrapper `run_p2_bug_ladder_with_ci.sh` `source`s the chosen
  `.env_claude_*` BEFORE invoking Python.

## Scale verification (no further normalization)

- Judge `normalized_score` is already in [0,1] (raw `score / max_score`).
- Do NOT divide further or rescale in the runner or in any plot code.
- Smoke test will confirm; any deviation → `REPORT.md` "Open questions
  for Ethan".

## Pre-conditions for run

- `claude_dotenv_path` points at a readable `.env_claude_*` containing
  a valid `ANTHROPIC_API_KEY` and a `TRACE_CUSTOMLLM_MODEL`.
- `judge_prompt_temp_path` resolves to the locked prompt template
  above.
- The bug ladder dir contains exactly 10 files matching the regex.
- `~/uv_envs/veribench` (preferred) or `~/uv_envs/cert-judge`
  exists; the wrapper auto-activates the first available.

## Estimated wall-clock

- Smoke (3 samples × 10 files = 30 calls): a few minutes.
- Full primary (15 samples × 10 files = 150 calls, `max_workers=16`):
  ~5–15 minutes depending on Anthropic latency.
- Bootstrap ablation: seconds (no LLM calls; reuses raw matrix).
- Cross-model rerun (per model): same as full primary.
- Plot + summary write: < 1 second.

## Pass/fail / abort rules

- Smoke must produce a valid `summary.json` with `len(per_file) == 10`
  and `nan rate < 0.1` before the full run is launched.
- If, during the full run, the NaN rate exceeds 0.1, STOP and
  document the cause (rate limit, prompt parse failure, env
  mis-load) in `REPORT.md` before retrying.
- If the per-file Spearman ρ on the locked headline model is
  > −0.7, do NOT relax the threshold — report the failure as a
  finding and surface it in "Open questions for Ethan".
- No silent post-hoc parameter changes. Every variant tried goes
  in `REPORT.md`. Defensible best-effort decisions on ambiguities
  go in `REPORT.md` → "Open questions for Ethan."

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
- Anthropic key path: `~/keys/anthropic_bm_key_koyejolab.txt`
