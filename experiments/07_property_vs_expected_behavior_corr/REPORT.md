# Folder 07 — REPORT

Per-judge P1/P2/P4 property sanity checks across the expanded 9-judge
panel, computed on Folder 06 detail_rows.csv (Mode A; no new LLM-budget
spend).

## Headline numbers

Run: `full_run/median/`, `2026-04-28 23:35` PT.
Input: `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv`.

Locked thresholds (PROTOCOL.md): P1 ≥ 0.9 on STYLE/RENAME/REORDER,
P2 ≤ −0.7 (median per-problem ρ), P4 ≥ 0.9 (median per-item α).

| Judge | P1 (S/R/Re) | P2 ρ_med | P4 α_med | All pass |
|---|---|---|---|---|
| `claude-sonnet-4-20250514\|P8_STRICT_B`   | 0.996/0.988/0.996 | −0.894 | 1.000 | **PASS** |
| `claude-sonnet-4-20250514\|P4_CHECKLIST`  | 0.996/1.000/1.000 | −0.894 | 1.000 | **PASS** |
| `claude-sonnet-4-20250514\|P1_BASELINE`   | 1.000/1.000/1.000 | −0.894 | 1.000 | **PASS** |
| `claude-sonnet-4-20250514\|BAD_STRINGY`   | 0.950/0.926/0.948 | −0.894 | 1.000 | **PASS** |
| `gpt-5.3-codex\|P8_STRICT_B`              | 0.999/1.000/0.998 | −0.894 | 1.000 | **PASS** |
| `gpt-5.3-codex\|P4_CHECKLIST`             | 0.999/1.000/1.000 | −0.866 | 1.000 | **PASS** |
| `gpt-5.3-codex\|P1_BASELINE`              | 1.000/1.000/1.000 | −0.866 | 1.000 | **PASS** |
| `editdist_e1`                              | 0.974/0.920/0.893 | **−0.600** | 1.000 | **FAIL (P2)** |
| `random_r1`                                | **0.414/0.451/0.479** | **+0.100** | 1.000 | **FAIL (P1, P2)** |

**7 of 9 judges pass all three sanity checks.** The two failures are
exactly the baselines that should fail:

- `editdist_e1`: P1 nearly passes (edit-distance is permissive on
  cosmetic perturbations) but bug-ladder ρ = −0.600 fails the −0.7
  threshold. This is the canonical "edit-distance is too coarse"
  finding.
- `random_r1`: P1 fails at all variants (mean ~0.45, far below 0.9).
  Bug-ladder ρ ≈ 0 (deterministic-random has no bug-monotonicity
  signal).

## P1 ALPHA (isolated, not gated)

ALPHA-renaming is the halting-problem-style perturbation called out
in PROTOCOL.md:

| Judge                                       | ALPHA mean (n=24) |
|---------------------------------------------|-------------------|
| `claude-sonnet-4-20250514\|P8_STRICT_B`     | 0.708             |
| `claude-sonnet-4-20250514\|P4_CHECKLIST`    | 0.046             |
| `claude-sonnet-4-20250514\|P1_BASELINE`     | 0.004             |
| `claude-sonnet-4-20250514\|BAD_STRINGY`     | 0.881             |
| `gpt-5.3-codex\|P8_STRICT_B`                | 0.179             |
| `gpt-5.3-codex\|P4_CHECKLIST`               | 0.000             |
| `gpt-5.3-codex\|P1_BASELINE`                | 0.000             |
| `editdist_e1`                               | 0.953             |
| `random_r1`                                 | 0.476             |

Numbers from `full_run/median/per_judge_property_table.csv` (column `p1_alpha_mean`).

**Diagnostic, not a pass/fail.** ALPHA renames every single-letter
variable to `x0,x1,x2,...` (`utils/variant_generator.py:85`). Strictly
in Lean, alpha-renaming bound variables produces α-equivalent terms,
so a "semantic" judge could legitimately call ALPHA = 1.0; a "strict
string-match with rationale" judge could legitimately call it 0.0.
The PROTOCOL isolates ALPHA precisely because there is no algorithmic
oracle for which equivalence class the human rubric implies — this is
the "halting-problem argument" referenced in the protocol.

What the numbers show:
- The "strict" Claude / Codex baseline & checklist prompts call ALPHA
  ≈ 0 (treat name changes as a difference). This matches a literal
  name-binding interpretation.
- The "lenient" `BAD_STRINGY` and edit-distance baselines call ALPHA
  ≈ 0.9–0.95 (low edit distance, so high score). This matches the
  paper's argument that lexical-only judges over-credit superficial
  similarity.
- Claude P8_STRICT_B sits in the middle (0.71) — partial alpha
  reasoning.

This is consistent with the "lexical vs semantic" axis on which v2 of
the certification index discriminates judges (anti-string-bias).

## P2 details (pooled per-judge over all 24 problems × 5 levels)

| Judge | Pooled ρ | 95% CI | perm-p | Weak-mono % | n_problems |
|---|---|---|---|---|---|
| `claude-sonnet-4-20250514\|P8_STRICT_B`  | −0.826 | (see CSV) | <5e-5 |  96.9% | 24 |
| `claude-sonnet-4-20250514\|P4_CHECKLIST` | −0.840 | (see CSV) | <5e-5 | 100.0% | 24 |
| `claude-sonnet-4-20250514\|P1_BASELINE`  | −0.850 | (see CSV) | <5e-5 | 100.0% | 24 |
| `claude-sonnet-4-20250514\|BAD_STRINGY`  | −0.834 | (see CSV) | <5e-5 |  94.8% | 24 |
| `gpt-5.3-codex\|P8_STRICT_B`             | −0.762 | (see CSV) | <5e-5 |  95.8% | 24 |
| `gpt-5.3-codex\|P4_CHECKLIST`            | −0.791 | (see CSV) | <5e-5 | 100.0% | 24 |
| `gpt-5.3-codex\|P1_BASELINE`             | −0.799 | (see CSV) | <5e-5 | 100.0% | 24 |
| `editdist_e1`                            | −0.594 | (see CSV) | <5e-5 |  50.0% | 24 |
| `random_r1`                              | +0.003 | (see CSV) | ~1    |  53.1% | 24 |

Numbers from `full_run/median/per_judge_property_table.csv` (cols
`p2_pooled_spearman` etc.).

## Mean-aggregation ablation

`full_run/mean/REPORT_AUTO.md` produces the same pass/fail set as the
median primary; per-judge P1 and P2 numbers move by ≤ 0.005. The
threshold-crossing pattern is identical (7/9 pass; editdist and random
fail).

## Open questions for Ethan

1. **P4 Cronbach's α saturates at 1.000 because n_repeats=3 with
   nearly-constant repeats per item.** Three repeats of the same prompt
   on the same problem rarely produce variance, so the
   1 − var/(p(1−p)) form floors at 1. The n_repeats=9 follow-up
   (Folder 06b → Folder 07b) will give a more nuanced α distribution.
   Locked threshold (≥0.9) still distinguishes good from bad if any
   judge does have variance, but on this n_repeats=3 data it's
   uninformative. **Suggest**: keep the α field (it's not misleading,
   just saturated) and add a "n_repeats=9 P4 follow-up" to the manuscript
   error-bar / variance section.
2. **`BAD_STRINGY` passes the P1/P2/P4 trio.** This is expected and
   documented in §6 of the paper: lexical-only "bad" judges can pass
   property sanity checks individually but should fail on the
   anti-string-bias metric used in cert v2. Confirmed here — its v2
   index in Folder 06 (0.825) is well below the four "good" Claude
   judges (0.873–0.892). The property panel on its own is necessary
   but not sufficient; the v2 panel completes the gate.
3. **P3 (spec ablation) remains out of scope** per Folder 07 PROTOCOL §
   "Scope". Filed as **Folder 07c** (spec-ablation rerun on the
   expanded panel against `data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs/`).
4. **P5–P9** (TVD-MI, mutual evaluation, human/prover correlations)
   are tracked under Folder 04 / Folder 05 and are not part of this
   sanity-check folder. Listed for completeness only.

## Files

- `PROTOCOL.md` — locked thresholds (frozen pre-run)
- `run_07.sh` — wrapper (median/mean)
- `run_property_analysis.py` — analysis script (reads detail_rows.csv)
- `full_run/median/{summary.json, REPORT_AUTO.md, per_judge_property_table.csv, per_judge_per_problem_p2.csv, per_item_alpha.csv}`
- `full_run/mean/{...}`
