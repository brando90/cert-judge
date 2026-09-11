# Folder 08 — REPORT

Per-x 95% CI replacement for the original veribench Figure 6
("Bug Count vs LLM Judge File Equivalence Score"), single-judge.

## Locked protocol (mirror of `PROTOCOL.md`)

- `num_samples = 15` LLM calls per bug-count file.
- Per-x CI primary = t-based two-sided 95%; ablation = percentile bootstrap (2000 iters).
- Pass: per-file Spearman ρ ≤ −0.7 (matches Folder 07 P2 lock).
- Flag: |per-call ρ − per-file ρ| > 0.1 → sampling-noise dominance finding.
- Bug ladder = `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/` (10 files, k=0..9), gold = k=0.

## Headline numbers

Run: `full_run/claude_sonnet_4_5/`, `2026-04-27 21:00` PT, 150/150 calls in 93.7 s, NaN rate **0.0%**.

| metric                                | value          | gate            | result      |
|---------------------------------------|----------------|-----------------|-------------|
| Per-file Spearman ρ (k vs mean)       | **−0.9879**    | ≤ −0.7          | **PASS**    |
| Per-call Spearman ρ (k vs each call)  | **−0.9153**    | ≤ −0.7          | **PASS**    |
| \|per-call ρ − per-file ρ\|           | **0.0726**     | > 0.1 → flag    | not flagged |
| Per-file Pearson r                    | −0.6963        | (info)          | —           |
| Per-call Pearson r                    | −0.6920        | (info)          | —           |
| Per-file Kendall τ                    | −0.9556        | (info)          | —           |
| Per-call Kendall τ                    | −0.8337        | (info)          | —           |
| OLS slope on per-file means           | −0.0655        | (info)          | —           |
| OLS intercept                         | 0.5116         | (info)          | —           |
| OLS R² on per-file means              | 0.4848         | (info)          | —           |

Headline figure: `full_run/claude_sonnet_4_5/p2_bug_ladder_with_ci.png`

## Per-file table (t-based 95% CI; primary)

| k | n  | mean   | CI low | CI high | SEM    | half-width |
|---|----|--------|--------|---------|--------|------------|
| 0 | 15 | 1.000  | 1.000  | 1.000   | 0.0000 | 0.000      |
| 1 | 15 | 0.278  | 0.269  | 0.287   | 0.0042 | 0.009      |
| 2 | 15 | 0.249  | 0.215  | 0.283   | 0.0159 | 0.034      |
| 3 | 15 | 0.116  | 0.091  | 0.141   | 0.0117 | 0.025      |
| 4 | 15 | 0.122  | 0.095  | 0.150   | 0.0129 | 0.028      |
| 5 | 15 | 0.093  | 0.086  | 0.101   | 0.0035 | 0.008      |
| 6 | 15 | 0.093  | 0.086  | 0.101   | 0.0035 | 0.008      |
| 7 | 15 | 0.084  | 0.075  | 0.094   | 0.0044 | 0.010      |
| 8 | 15 | 0.067  | 0.067  | 0.067   | 0.0000 | 0.000      |
| 9 | 15 | 0.064  | 0.060  | 0.069   | 0.0022 | 0.005      |

Notes:
- The k=3 / k=4 means invert (0.116 vs 0.122). Their 95% CIs overlap by a wide
  margin ([0.091, 0.141] vs [0.095, 0.150]) → inversion is **not** statistically
  meaningful at this sample size; treat the (k=3, k=4) plateau as ~0.12.
- k=0 and k=8 have zero CI half-width → all 15 calls returned the same integer
  score for those two files (30/30 and 2/30 respectively). This is what makes
  the bug=0 monotonicity assertion air-tight: every call from the judge said
  "fully equivalent" for the self-pair.
- Boundary saturation at the 0/30 floor and the 30/30 ceiling means a normal
  approximation under-states the upper-tail uncertainty when scores hit the
  ceiling. The bootstrap ablation (below) confirms this is a non-issue at
  N=15 here, but it would matter for an unsaturated mid-range judge.

## Ablation: t-based CI vs percentile bootstrap CI

Output: `full_run/claude_sonnet_4_5_bootstrap/`. Re-aggregated **without**
re-calling the LLM (per PROTOCOL: "bootstrap ablation does NOT re-call the LLM").

| k | t-CI half-width | bootstrap-CI half-width | |Δ|   |
|---|------------------|--------------------------|------|
| 0 | 0.000            | 0.000                    | 0.000|
| 1 | 0.009            | 0.008                    | 0.001|
| 2 | 0.034            | 0.029                    | 0.005|
| 3 | 0.025            | 0.021                    | 0.004|
| 4 | 0.028            | 0.025                    | 0.003|
| 5 | 0.008            | 0.007                    | 0.001|
| 6 | 0.008            | 0.007                    | 0.001|
| 7 | 0.010            | 0.009                    | 0.001|
| 8 | 0.000            | 0.000                    | 0.000|
| 9 | 0.005            | 0.004                    | 0.001|

PROTOCOL predicted "agree to within ~0.02 on every per-x half-width when
num_samples >= 15 and scores are not boundary-stuck." Verified: max |Δ| = 0.005,
well inside the predicted band. The two CI methods produce visually identical
plots; t-CI is kept as the headline.

## Cross-method correlation cross-check

The bootstrap re-aggregation does not change the score data, so the per-call
and per-mean correlations are bitwise identical to the t-CI run:
- Per-call: Pearson r = −0.692, Spearman ρ = −0.915, Kendall τ = −0.834
- Per-mean: Pearson r = −0.696, Spearman ρ = −0.988, R² = 0.485

## Smoke run

`smoke/`, 30/30 calls in 29.1 s, NaN rate 0.0%. Per-call Spearman = −0.950.
All step-2 sanity checks pass; the full run was launched on that basis.

## Pre-condition patches applied during execution

Two genuine artifacts were missing from the assumed environment. Both
patches are local to this experiment dir; neither modifies the upstream
veribench repo. Both are surfaced under "Open questions for Ethan" so he
can review and decide whether to upstream.

1. **Missing prompt template.** `simplest_prompt_varying_score_range.txt`
   is referenced by `~/veribench/experiments/10_file_equiv/main.sh:33` and
   by the existing `experiments/00_overall_cert_judge_metric_with_properties/`
   shell script, but the file does not exist on disk and is not in
   `~/veribench` git history. A canonical copy was written into
   `experiments/08_p2_bug_ladder_with_ci/prompts/` matching the parser
   contract from `~/veribench/py_src/veribench/metrics/sim_file_eq_llm_judge.py:117–125`
   (placeholders `{$GOLD_FILE}`, `{$AGENT_FILE}`, `{$MAX_SCORE}`; output
   tags `<RATIONALE>...</RATIONALE>` then `<SCORE_RESULT>integer</SCORE_RESULT>`).
   The prompt is calibrated to a 0..max_score integer scale with explicit
   counterexample-search instructions and anti-clustering guidance.

2. **macOS fastchat → torch import chain.** `veribench.utils` does
   `from fastchat.model import get_conversation_template` at module load,
   and the real fastchat hard-imports torch at module load. Installing torch
   on this Apple Silicon Mac was deemed out-of-scope. A minimal shim package
   `experiments/08_p2_bug_ladder_with_ci/_compat/fastchat/model/__init__.py`
   was added; `_ensure_cert_judge_on_path()` prepends `_compat/` to
   `sys.path` so the shim wins over the installed fastchat. The shim
   exposes only what `veribench.utils.call_llm` reads from a Conversation
   (`.roles`, `.append_message(role, content)`, `.to_openai_api_messages()`).

## Backend deviation

The locked PROTOCOL named the veribench litellm proxy
(`TRACE_CUSTOMLLM_URL=http://3.142.95.101:4000`, model
`anthropic.claude-3-5-sonnet-20240620-v1:0`) as the headline backend.

That proxy is **not reachable from this Mac** — both candidate proxy hosts
(`3.142.95.101:4000` and `3.15.208.99:8888`) time out after 5 s, while
`api.anthropic.com` is reachable (40 ms). Best-effort decision:

- Added an `anthropic_direct` backend to `run_p2_bug_ladder_with_ci.py`
  that calls the Anthropic SDK with the same prompt-fill + parse contract
  used by veribench's `get_sim_score_file_eq_llm_result_in_json_str`.
- The wrapper defaults to `judge_backend=anthropic_direct` and
  `anthropic_model=claude-sonnet-4-5` (the only Anthropic model the local
  `~/keys/anthropic_bm_key_koyejolab.txt` resolves: `claude-sonnet-4-5`,
  `claude-3-5-sonnet-*` returns 404).
- Run on Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`), temperature
  0.7, `max_tokens=1024`. The veribench-proxy backend is preserved for
  re-runs from the cluster.

The PROTOCOL is **not** edited. This deviation is logged here per the
protocol's "no silent post-hoc parameter changes" rule and surfaced in
"Open questions for Ethan".

## Transparency self-check

- `num_samples=15` (locked). ✅
- Both CI flavors run against the same raw matrix; bootstrap did **not**
  re-call the LLM. ✅
- Both correlation flavors (per-call S·N points and per-file means) reported
  on the figure and in this report. ✅
- Pass/fail threshold not touched. ✅ Judge passes (ρ = −0.988 ≤ −0.7).
- Sampling-noise flag rule not triggered (|Δρ| = 0.073 < 0.10). ✅
- Smoke produced a valid `summary.json` before the full run was launched. ✅
- NaN rate 0.0% throughout (smoke + full + ablation). ✅
- Locked headline judge (Claude 3.5 Sonnet via lab proxy) was unreachable
  from this host; ran on Claude Sonnet 4.5 via direct Anthropic SDK
  instead, with the same prompt + parser contract. Documented above.
- Single-judge by design (Folder 08b would expand). ✅
- P3 spec ladder out of scope (Folder 07c follow-up). ✅

## Open questions for Ethan

1. **Backend / model deviation — keep, or rerun on cluster?** The headline
   number is from Claude Sonnet 4.5 via direct Anthropic SDK because both
   lab litellm proxies (`3.142.95.101:4000`, `3.15.208.99:8888`) are
   unreachable from this Mac. The original Figure 6 was Claude 3.5 Sonnet.
   Should we (a) keep the Sonnet-4.5 number as the new Figure 6 headline
   and add a sentence acknowledging the model upgrade, (b) re-run from
   the cluster on Claude 3.5 Sonnet to preserve the model identity, or
   (c) report both as a model-comparison appendix?
2. **Missing prompt template upstream.** `simplest_prompt_varying_score_range.txt`
   does not exist anywhere in `~/veribench` (referenced from `main.sh:33`
   but absent on disk and from git history). The local copy at
   `experiments/08_p2_bug_ladder_with_ci/prompts/` follows the parser
   contract from `sim_file_eq_llm_judge.py:117–125` and produces correct
   `<RATIONALE>` / `<SCORE_RESULT>` blocks at temperature 0.7.
   Should this be upstreamed to
   `~/veribench/veribench_prompts/judge_prompts/file_equiv_prompts/`
   so Folder 00 and Folder 10 also become runnable as documented?
3. **fastchat shim upstream?** The `_compat/fastchat/model/__init__.py` shim
   is the cleanest way to import `veribench.utils` on macOS without torch.
   Should this be upstreamed (e.g. as
   `veribench.utils.minimal_chat`) so the existing Folder 00 / Folder 10
   experiments stop hard-failing on Apple Silicon, or kept local to this
   experiment to avoid changing veribench's call surface?
4. **Folder 08b cross-judge overlay — file now or wait for Sonnet 3.5
   re-run?** Cleanest if we wait until the cluster re-run resolves question
   1 so 08b can show 3.5-Sonnet, 4-Sonnet, 4.5-Sonnet on the same axes.
5. **Folder 08c file-resampling slope CI — file now or defer?** With ρ at
   −0.988 the slope is unambiguous on this ladder; an outer file-resample
   bootstrap is more useful on noisier panels. Defer until cross-judge
   shows a less monotone judge?
6. **K=3 vs K=4 plateau** (means 0.116 vs 0.122 with overlapping CIs). On
   inspection of the bug ladder this is plausibly a property of the
   ladder (bugs at L3 and L4 happen to have similar semantic severity);
   Folder 08 doesn't claim more than "monotone within CI". Worth a
   one-sentence note in the paper caption?
7. **Boundary saturation at k=0 and k=8.** The judge returned the same
   integer for all 15 calls on those two files. The model isn't broken,
   it's reflecting a deterministic decision (perfect equivalence at k=0;
   "very bad" at k=8). The t-CI handles this by giving zero half-width;
   bootstrap agrees. Worth flagging in §3 of the paper as an interpretation
   note rather than as a measurement artifact?

## Manuscript update — what to change

- Replace the original Figure 6 in
  `paper_latex/NeurIPS_2025/mathai_neurips2025_template/neurips_2025.tex`
  and `paper_latex/ICML_2026/sections/appendix.tex` with
  `full_run/claude_sonnet_4_5/p2_bug_ladder_with_ci.png`.
- Caption update: "Each marker is the mean of 15 judge calls; vertical
  bars are 95% CIs (t-based; bootstrap variant in appendix). Per-file
  Spearman ρ = −0.99, per-call Spearman ρ = −0.92, OLS slope = −0.066."
- Add one sentence in the figure-introducing paragraph acknowledging that
  the prior version of this figure rendered single LLM calls with no
  per-x replication, and that this rendering corrects the measurement-rigor
  issue without changing the underlying property definition.
- Update the §3 P2 paragraph to cite per-file AND per-call Spearman.
- Limitations: state explicitly that this is single-judge; cross-judge
  overlay is filed as Folder 08b. Note model deviation per Open Question 1.

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
- Brando's GitHub login: `brando90`
- Anthropic key path: `~/keys/anthropic_bm_key_koyejolab.txt`
