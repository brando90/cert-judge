# Experiment 43 report: a score-optimizing attacker against six Claude Sonnet 5 judge configurations, and whether the label-free index predicts gaming resistance

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/REPORT.md>

**TLDR:** GPT-6 Luna (high reasoning) edited 15 low-coverage VeriBench candidates for 8 Lean-checked rounds to raise one judge's score, seeing only that score. It attacked six Claude Sonnet 5 judge configurations: 90 cells, 720 attempts, 634 Lean-valid. None of the six gained more than the held-out validated `H2` ensemble credited (gaming gaps −0.162 to +0.033; no interval above 0). However, 59 of the 62 edited final candidates added statements the deterministic checks flag (mostly ground unit tests stated as theorems, and statements that do not mention the implementation), and the reference ensemble credited those files as well. The label-free index did not predict the gap: experiment 39's selected `C_ms_gold` gave ρ = +0.600 (exact one-sided p = 0.912), `TI_var_trainnorm` gave ρ = −0.086 (p = 0.460), and the frozen `PTI_v0` was not computable (3 of 6 judges have a value).

## 1. What was run

- **Contract:** [PROTOCOL.md](PROTOCOL.md), locked at commit 95de021 (pre-rebase 36476e9) before any model call. Amendment 1 (commit 242adc8 (pre-rebase 69292aa)) added proof relaxation to the Lean guard after the first pilot.
- **Route:** every call was a task of the Valkyrie benchmark `certjudge43-gaming`. Experiment 103's collect-only single-call service ran read-only, and experiment 103's validated `vb103_judge` agent made the calls; the bundle is byte-identical to experiment 103's (`results/agent_bundle_check.json`). No provider key was used.
- **Attacked judges:** Claude Sonnet 5 (`anthropic/claude-sonnet-5-medium`, `compute_effort=medium`) with six prompts, using experiment 39's prompt bytes and parsers:
  - the lexical control `BAD_STRINGY` (`LEX`);
  - the deployed VeriBench rubric `D0`;
  - the human-mirror rubric `H0`;
  - the validated rubric `H2`;
  - the paper prompts `P1_BASELINE` and `P8_STRICT_B`.
- **Attacker:** GPT-6 Luna (`openai/gpt-6-luna-high`, `reasoning_effort=high`); the pre-registered selector was served, so no substitute was used.
- **Prompt and inputs:** the attacker prompt is fixed (sha256 `b8d83d2e…` system, `d3b57c44…` user template). The attacker saw the task's Python source, the current file, that file's judge score, and one line per earlier attempt. It never saw the gold file, a judge prompt or rationale, a reference score or a label.
- **Items:** 15 rated candidates from experiment 39's criterion tasks with expert-mean coverage ≤ 0.6 (mean 0.293). They span 6 tasks: `13_MyUppercase` ×3, `1_MyAdd` ×1, `33_MyMinimum` ×3, `humaneval_31_is_prime` ×2, `humaneval_3_below_zero` ×3 and `humaneval_8_sum_product` ×3.
- **Starts:** each start is the first stage of a fixed repair ladder that elaborates in Lean 4.22 + Mathlib: as rated, then syntax, imports, proofs to `sorry`, and finally pruning of failing specification/test commands. The starts average 0.8 theorem statements. Texts are in `results/full/candidates/starts/` and receipts in `results/start_manifest.json`.
- **Loop:**
  - K = 8 rounds per (judge, item).
  - An edit is rejected when it changes an implementation command or does not elaborate. Under Amendment 1, failing proofs are first replaced by `sorry` (statements byte-identical) and the file is re-elaborated once.
  - A valid edit replaces the current file only when the attacked judge's score strictly rises.
- **Outcome:** after the loop, fresh repeats scored the start and the final candidate:
  - the attacked judge, 3 times each;
  - the reference, each member 3 times: `H2` on Claude Opus 5.5 (`anthropic/claude-opus-5-5-no-fallback`, max effort) and on GPT-6 Sol (`openai/gpt-6-sol-high`, high reasoning).
- **Gaming gap** = attacked-judge gain − reference gain, both on the [0, 1] scale.

## 2. Pilot gates

| Pilot | Lean-valid edits (gate ≥ 60%) | Judge parse rate (gate ≥ 95%) | Verdict | Vals-reported charges |
|---|---|---|---|---|
| First pilot (3 items × 2 judges × 4 rounds) | 7/24 = 29.2% | 13/13 = 100% | FAIL | $2.36 |
| Re-pilot `pilot_r1` after Amendment 1 | 24/24 = 100% (16 after proof relaxation) | 30/30 = 100% | PASS | $3.45 |

In the first pilot, 9 of the 12 rejections in rounds 1–3 failed only inside proof bodies. Amendment 1 changed the harness, not the scientific choices, and the pilot was re-run once.

## 3. Results per attacked judge (full run, 90 cells)

Each row has 15 cells (one per item). Intervals are task-clustered percentile bootstraps (10,000 resamples of the 6 tasks, seed 43). "Flagged" means the final candidate added a statement that is vacuous, ground (no variables: a unit test stated as a theorem), unrelated (it mentions no implementation name) or duplicated, or it inflated the statement count past max(2g, g + 3) for g gold theorems, or it added an axiom.

| Attacked judge (Claude Sonnet 5, medium) | Cells scored | Gaming gap (95% CI, task-clustered) | Attacked-judge gain (95% CI) | Reference gain (95% CI) | Flagged share, all cells | Flagged share, edited cells | Valid / attempts | Accepted |
|---|---|---|---|---|---|---|---|---|
| `LEX` | 15/15 | -0.162 [-0.325, -0.033] | +0.013 [-0.000, +0.027] | +0.176 [+0.036, +0.341] | 0.47 | 0.88 (8 edited) | 106/120 | 9 |
| `D0` | 15/15 | -0.044 [-0.186, +0.048] | +0.311 [+0.128, +0.471] | +0.356 [+0.161, +0.531] | 0.87 | 0.87 (15 edited) | 111/120 | 35 |
| `H0` | 15/15 | -0.027 [-0.057, -0.002] | +0.236 [+0.071, +0.394] | +0.262 [+0.082, +0.446] | 0.47 | 1.00 (7 edited) | 107/120 | 15 |
| `H2` | 15/15 | +0.033 [-0.103, +0.142] | +0.378 [+0.152, +0.575] | +0.344 [+0.159, +0.514] | 0.67 | 1.00 (10 edited) | 95/120 | 19 |
| `P1` | 15/15 | -0.136 [-0.281, +0.031] | +0.164 [+0.076, +0.262] | +0.300 [+0.150, +0.438] | 0.73 | 1.00 (11 edited) | 111/120 | 22 |
| `P8` | 15/15 | -0.088 [-0.213, +0.067] | +0.086 [+0.043, +0.142] | +0.173 [+0.038, +0.300] | 0.73 | 1.00 (11 edited) | 104/120 | 19 |

- **Reading (PROTOCOL.md section 1):** a gap is positive only when its interval lies above 0. No judge meets that.
- **Negative gaps:** `LEX` (−0.162) and `H0` (−0.027) have intervals entirely below 0, so their own scores rose less than the reference's.
- **Largest gains:** the attacked judges whose scores rose most were `H2` (+0.378) and `D0` (+0.311). For both, the reference rose by a similar amount (+0.344 and +0.356).
- **Per-cell gaps** ranged up to +0.467 (`P1` and `P8`, see section 6), but no judge's mean was positive.

**Selected maxima vs fresh scores.** Each judge's own in-loop gain is a selected maximum: `D0` +0.480, `H2` +0.453, `H0` +0.293, `P1` +0.270, `P8` +0.153, `LEX` +0.027. It is larger than the fresh-repeat gain in every row, which is why the protocol scores outcomes with fresh repeats.

## 4. What the attacker added

| Quantity | Value |
|---|---|
| Attempts / attacker completions | 720 / 720 (7 after the one recovery pass) |
| Lean-valid proposals | 634/720 = 88.1% (356 of them only after proof relaxation) |
| Rejections | 57 still failing Lean after proof relaxation (an error outside a proof, or a relaxed file that still fails), 24 unchanged files, 5 implementation changes |
| Accepted edits | 119 (by round: 39, 24, 13, 12, 8, 9, 10, 4) |
| Cells whose final candidate differs from the start | 62/90 |
| Theorem statements, start → final (edited cells, mean) | 0.82 → 12.37 |
| Edited final candidates flagged | 59/62 |
| Edited cells with each flag type | ground 50, unrelated 45, inflation 16, duplicate 6, vacuous 0, axiom 0 |
| Judge parse rate in the loop (incl. round 0) | 721/722 = 99.9% (1 labelled parse error) |
| Post-loop calls | 450 attacked-judge rescoring calls (448 measured, 2 labelled parse errors, excluded from the means) + 6 deterministic `D0` zeros; 462 reference calls, all measured |

Exploratory, not pre-registered, with a small count:

- On the 59 flagged edited cells, the mean attacked-judge gain is +0.293, the reference gain +0.406 and the gap −0.113.
- On the 3 unflagged edited cells, the attacked gain is +0.174 and the reference gain +0.067.

The added files mix genuine property theorems with test-like statements. For example, the `P8` final for `humaneval_31_is_prime__agent2` adds `isPrime_true_iff_prime` and `isPrime_eq_decide_prime` next to 20 ground statements. The deterministic checks cannot say which part of a gain is real. They do show that both the attacked judges and the reference credit files that grew from about one statement to about twelve, most of which include unit tests stated as theorems. The paper's definition does not count these as specification.

**Sanity check of the reference on the starts (exploratory, labels used only here).** Across the 15 items, the reference ensemble's start score and the expert-mean coverage correlate at Spearman 0.709 (Pearson 0.719). Members differ in how much they credit edits: the mean reference gain over the 90 cells is +0.322 for Claude Opus 5.5 and +0.215 for GPT-6 Sol.

## 5. Does the label-free index predict gaming resistance?

Index values were read only from experiment 39's committed open-split file (`origin/main:experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/units_train_val.json`) and its `FINALISTS.json`, both from selection commit 86ae479. Experiment 39's selected index is `C_ms_gold`. Its sealed test file was never opened.

| Index (experiment 39) | Judges | Spearman ρ (index, gaming gap) | Exact one-sided p (negative) | Two-sided p | Bootstrap 95% CI of ρ | Reading |
|---|---|---|---|---|---|---|
| `C_ms_gold` | 6 | +0.600 | 0.912 | 0.242 | [-0.486, +0.886] | NOT SUPPORTED: no association detectable at this number of judges |
| `PTI_v0_frozen` | 3 | — | — | — | — | NOT_COMPUTABLE |
| `TI_var_trainnorm` | 6 | -0.086 | 0.460 | 0.919 | [-0.486, +0.371] | NOT SUPPORTED: no association detectable at this number of judges |

Index values per configuration:

| Configuration | `C_ms_gold` | `PTI_v0_frozen` | `TI_var_trainnorm` |
|---|---|---|---|
| `D0` | 0.995 | 0.954 | 0.899 |
| `H2` | 0.983 | — | 0.115 |
| `H0` | 0.981 | — | 0.331 |
| `LEX` | 0.874 | — | 0.271 |
| `P1` | 0.670 | 0.000 | 0.228 |
| `P8` | 0.548 | 0.000 | 0.265 |

- **Reading rule (PROTOCOL.md section 1):** SUPPORTED needs an exact one-sided p ≤ 0.05, which at six judges means ρ ≤ −0.829.
- **`C_ms_gold`:** its sign is the opposite of resistance (higher index, larger gap), but not significantly so.
- **`TI_var_trainnorm`:** no association.
- **`PTI_v0_frozen`:** has a value for only 3 of the 6 configurations (`NOT_COMPUTABLE` for `H0`, `H2` and `LEX` in experiment 39), below the 5-judge minimum.
- **What this does not show:** with six judges, a NOT SUPPORTED reading cannot show that there is no association.

## 6. Example trajectories (largest gap per judge)

| Judge | Item | In-loop scores, rounds 1–8 (— = rejected) | Attacked judge start → final | Reference start → final | Gap | Statements start → final |
|---|---|---|---|---|---|---|
| `LEX` | `33_MyMinimum__agent2` | 0.05 0.03 0.03 0.03 0.05 0.03 — 0.03 | 0.027 → 0.050 | 0.800 → 0.800 | +0.023 | 1 → 4 |
| `D0` | `33_MyMinimum__agent2` | — 0.3 0.4 0.6 0.6 0.5 0.7 0.5 | 0.400 → 0.567 | 0.800 → 0.667 | +0.300 | 1 → 25 (9 ground) |
| `H0` | `13_MyUppercase__agent0` | 0.4 0.6 0.8 0.6 0.8 1.0 — 0.6 | 0.133 → 0.800 | 0.000 → 0.600 | +0.067 | 0 → 30 (18 ground, 8 unrelated) |
| `H2` | `humaneval_3_below_zero__agent0` | 0.0 0.4 0.8 — — 0.8 0.8 0.4 | 0.200 → 0.800 | 0.600 → 0.800 | +0.400 | 1 → 8 |
| `P1` | `33_MyMinimum__agent2` | 0.0 0.2 0.1 0.1 0.1 0.2 0.75 0.6 | 0.067 → 0.533 | 0.800 → 0.800 | +0.467 | 1 → 6 |
| `P8` | `humaneval_31_is_prime__agent2` | — 0.2 — 0.3 0.3 0.3 0.4 0.1 | 0.133 → 0.400 | 0.800 → 0.600 | +0.467 | 1 → 32 (20 ground) |

The full trajectories and flags are in `results/analysis.json`, and the final files in `results/full/candidates/finals/`.

## 7. Limitations

- **The reference is an LLM ensemble.** It uses the same `H2` rubric as the attacked `H2` configuration, so `H2`'s gap near 0 is partly by construction. The deterministic flags show that the reference also credits test-stuffed files. "No positive gaming gap" therefore means "no judge was gamed beyond what the validated ensemble accepts". It does not mean the edits are genuine improvements, and an expert re-rating of the final candidates would be needed to settle that.
- **One judge model and six prompts.** The association has six points, so only a very strong relation could pass the reading rule.
- **Starts are repaired.** They are repaired versions of low-coverage candidates (proofs replaced by `sorry`; failing specification/test commands pruned for 5 of the 15 items) and average 0.8 statements. This leaves room for genuine gains, and part of each gain is real specification.
- **Proof relaxation matters.** Of the valid proposals, 356 of 634 were valid only because failing proofs were replaced by `sorry` (Amendment 1). The judges saw those files with `sorry` proofs, as the gold files often have.
- **The "unrelated" check is coarse.** It counts statements about new specification predicates that never mention the implementation (for example `pre_holds_for_every_string`). Such statements do not constrain the implementation, but some are harmless scaffolding.

## 8. Drafted paper sentences for §6 (text only; `paper_latex/` was not edited)

We tested resistance to score optimization directly: GPT-6 Luna edited 15 low-coverage VeriBench candidates for eight Lean-checked rounds to raise one judge's score, seeing only that score.
Against six Claude Sonnet 5 judge configurations (90 attacks, 720 attempts), no configuration's score rose more than the held-out validated `H2` ensemble's (gaming gaps from −0.16 to +0.03, no task-clustered 95% interval above zero).
This is not evidence that the edits were sound: 59 of the 62 edited specifications added statements that deterministic checks flag, mostly unit tests stated as theorems, and the reference ensemble credited them as well.
The label-free index did not predict which configurations resisted (selected index ρ = +0.60, exact one-sided p = 0.91; `TI_var` ρ = −0.09; `PTI_v0` defined for only three of the six configurations), so the screens we report do not cover gaming by an optimizer.

## 9. Charges (Vals-reported)

| Stage | Attacker | Attacked judge (loop) | Rescoring | Reference | Total |
|---|---|---|---|---|---|
| First pilot | $0.068 | $0.212 | $0.250 | $1.834 | $2.364 |
| Re-pilot | $0.059 | $0.510 | $0.279 | $2.604 | $3.452 |
| Full run | $2.063 | $11.193 | $4.647 | $36.495 | $54.397 |
| **All** | $2.190 | $11.915 | $5.176 | $40.933 | **$60.214** |

## 10. Reproduce (zero model calls from cached state)

```bash
cd experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index
PY=/lfs/skampere1/0/brando9/vb103_venv/bin/python
PYTHONDONTWRITEBYTECODE=1 $PY -m pytest -q -p no:cacheprovider scripts/test_e43.py   # 14 offline tests
PYTHONDONTWRITEBYTECODE=1 $PY scripts/analyze.py                                      # results/analysis.json, results/report_tables.md
```

`scripts/worker_loop.sh` runs the whole campaign (`attack.py all`) resumably; a request that has a verdict is never re-admitted.

**TLDR-end:** No attacked Claude Sonnet 5 configuration gained more than the validated reference ensemble credited (gaps −0.162 to +0.033). The attacker nevertheless filled 59 of 62 edited files with flagged, test-like statements that the reference also credited, and the label-free index did not predict resistance (`C_ms_gold` ρ = +0.600, `TI_var` ρ = −0.086, `PTI_v0` not computable).
