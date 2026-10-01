# Experiment 42 report: do judges catch vacuous, weakened or over-constrained formal specifications?

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/REPORT.md>

**TLDR:** All 56 LLM judge configurations of experiment 39 scored 194 Lean-validated probes built from the VeriBench references (3 repeats, 32,592 Valkyrie calls, 99.35% measured, $656.15 Vals-reported). Nearly every configuration lowers its score when theorem statements become `True` (vacuity directional accuracy 0.996 on average). Weakening separates judges: only 15 of 56 configurations pass the locked screen (directional accuracy ≥ 0.8 on vacuity, weakening and over-constraint; formatting gap ≤ 0.05). The judge model matters more than the prompt among the VeriBench rubrics: Claude Sonnet 5 and Qwen3.6-27B catch about 9 in 10 weakenings, GPT-6 Sol and Luna about 4 in 10. The paper's legacy prompts, which show only the reference's last theorem, catch about 6 in 100. Against experiment 39's expert criterion (judge–human agreement on 45 held-out items), weakening directional accuracy has Spearman 0.73 [0.55, 0.86] over its 38 train and val units and 0.72 [0.31, 0.92] over its 18 test units (post hoc). Adding the semantic component to experiment 39's selected index does not improve it on train and val (0.78 → 0.72, Δ −0.06 [−0.16, 0.04]); the test-split gain is inconclusive (0.56 → 0.67, Δ +0.11 [−0.13, 0.39]).

## What was run

- **Probes** (`results/semantic_probe_manifest.json`; PROTOCOL.md locked at 685b9d0 before any call): from the 25 annotation-era VeriBench references, 24 of which elaborate in Lean 4.22 + Mathlib.
  - identity anchors: 24
  - vacuity (all theorem statements → `True`; or premises kept, conclusion `True`): 38
  - cumulative weakening L1–L3 (drop a conjunct, relax `=` to `≤`/`≥`, add a disjunctive escape): 57
  - over-constraint (an unsatisfiable hypothesis on the main theorem, L1, then on every eligible theorem, L2): 37
  - formatting-only (comments removed; theorem heads joined onto one line): 38

  Every semantic probe came with Lean proofs, free of `sorryAx`, that each changed reference statement implies its probe counterpart. In the check file every implementation definition is an axiom, so these hold for any implementation. Each added hypothesis is proved unsatisfiable, and proved-equivalent edits are excluded (0 of 57 weakening levels were). Formatting probes `#print` identical declarations.
- **Judges:** experiment 39's 56 LLM configurations (6 models × the VeriBench rubrics D0, R4, H0, H1, H2 and the paper's legacy prompts P1, P4, P8 and the lexical LEX; Opus on a 5-prompt subset; Terminus2 agent judges on H2 and D0) plus its 4 deterministic controls. Selectors: openai/gpt-6-sol-high, anthropic/claude-sonnet-5-medium, openai/gpt-6-luna-high, google/gemini-3.1-pro-preview, anthropic/claude-opus-5-5-no-fallback, alibaba/qwen3.6-27b (`results/RECONCILIATION.json`).
- **Execution:** Valkyrie only (vb103_judge single-call transport byte-identical to experiment 103's validated bundle; Terminus2 `brando_terminus_gateway` for agent judges). 56/56 smoke cells measured. The main pass plus one `recovery_1` pass gave 32,592 of 32,592 cells reconciled: 32,381 measured, 209 parse errors, 2 model errors.

## Results (locked rule)

Directional accuracy is the share of a family's probes scored strictly below the same task's identity score (ties are misses). Values are point estimates with task-clustered 95% bootstrap intervals; the full 60-row table is `results/RESULTS_semantic_screen.md`.

| Configuration | Vacuity | Weakening | Over-constraint | Formatting gap | τ (weakening level) | Verdict |
|---|---|---|---|---|---|---|
| Claude Sonnet 5, H2 | 1.00 | 0.95 [0.89, 1.00] | 0.97 [0.92, 1.00] | 0.00 | −0.82 | PASS |
| Qwen3.6-27B, H2 | 1.00 | 0.93 [0.86, 0.98] | 0.94 [0.86, 1.00] | 0.00 | −0.71 | PASS |
| Terminus2 + Sonnet 5, H2 | 1.00 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 | −0.83 | PASS |
| Terminus2 + Qwen3.6, H2 | 1.00 | 0.96 [0.91, 1.00] | 0.97 [0.92, 1.00] | 0.00 | −0.80 | PASS |
| Claude Opus 5.5, H2 | 1.00 | 0.77 [0.68, 0.86] | 1.00 | 0.00 | −0.83 | FAIL |
| Gemini 3.1 Pro, H2 | 1.00 | 0.61 [0.46, 0.75] | 0.95 [0.86, 1.00] | 0.00 | −0.71 | FAIL |
| GPT-6 Luna, H2 | 1.00 | 0.44 [0.26, 0.61] | 0.59 [0.47, 0.71] | 0.00 | −0.49 | FAIL |
| GPT-6 Sol, H2 | 1.00 | 0.39 [0.21, 0.58] | 0.49 [0.32, 0.65] | 0.00 | −0.43 | FAIL |
| Claude Sonnet 5, P4 (paper legacy) | 1.00 | 0.07 [0.00, 0.19] | 0.59 [0.51, 0.69] | 0.09 | −0.05 | FAIL |
| control: edit distance | 1.00 | 1.00 | 1.00 | 0.044 | −1.00 | PASS |

By prompt (mean over the models that ran it):

| Prompt | Configurations | Vacuity | Weakening | Over-constraint | Formatting false alarm | Passing |
|---|---|---|---|---|---|---|
| D0 | 9 | 1.00 | 0.67 | 0.98 | 0.03 | 3 |
| R4 | 5 | 1.00 | 0.66 | 0.76 | 0.00 | 2 |
| H0 | 6 | 1.00 | 0.73 | 0.82 | 0.00 | 4 |
| H1 | 5 | 1.00 | 0.67 | 0.76 | 0.00 | 2 |
| H2 | 9 | 1.00 | 0.73 | 0.83 | 0.00 | 4 |
| P1 | 5 | 1.00 | 0.07 | 0.54 | 0.06 | 0 |
| P4 | 6 | 1.00 | 0.06 | 0.57 | 0.06 | 0 |
| P8 | 5 | 1.00 | 0.06 | 0.51 | 0.04 | 0 |
| LEX (designed-bad lexical) | 6 | 0.96 | 0.23 | 0.50 | 0.34 | 0 |

The **15 passing LLM configurations** are: Claude Sonnet 5 (D0, H0, H1, H2, R4), Qwen3.6-27B (D0, H0, H1, H2, R4), Claude Opus 5.5 (D0, H0), Gemini 3.1 Pro (H0), Terminus2 + Sonnet 5 (H2) and Terminus2 + Qwen3.6 (H2). Among failing configurations, the failed criterion is weakening in 41, over-constraint in 32 and the formatting gap in 10 (several fail more than one).

## Reading

1. **Vacuity is not the hard case.** Replacing theorem statements with `True` lowers the score on every vacuity probe for 53 of 56 configurations; the three exceptions are the designed-bad lexical prompt on Gemini 3.1 Pro (0.87), Sonnet 5 (0.92) and Opus 5.5 (0.97).
2. **Weakening is.** On the VeriBench rubrics, mean weakening accuracy by model:

   | Model | Mean weakening accuracy (VeriBench rubrics) |
   |---|---|
   | Claude Sonnet 5 | 0.95 |
   | Qwen3.6-27B | 0.91 |
   | Terminus2 + Sonnet 5 | 0.89 |
   | Claude Opus 5.5 | 0.87 |
   | Terminus2 + Qwen | 0.86 |
   | Gemini 3.1 Pro | 0.68 |
   | Terminus2 + Luna | 0.46 |
   | GPT-6 Luna | 0.42 |
   | GPT-6 Sol | 0.38 |

   The τ with weakening level is negative for every VeriBench-rubric configuration (−0.38 to −0.92), so judges that notice weaken their scores further with each level.
3. **The paper's legacy prompts cannot see most weakenings.** P1/P4/P8 show the judge only the reference's last theorem block (as in the paper), so a weakened `Post` or property definition elsewhere in the file is invisible. Their weakening accuracy is 0.04–0.14. Experiment 39 recorded this limitation before any call.
4. **Much of the weakening miss rate is about redundancy, not blindness.** Lean proves each changed statement weaker, but the file-level audit found that 31 of 57 weakening probes leave the file's overall guarantee unchanged, because the references restate the same property in a separate theorem. On the 25 strict probes, GPT-6 Sol (H2) reaches 0.84 and Luna 0.92, against 0.39 and 0.44 on all probes. So those models mostly withhold a penalty when the property is still stated elsewhere. Both readings are reported, and the locked verdict uses all Lean-valid probes.
5. **The screen is necessary, not sufficient.** The edit-distance control passes it: any change detector lowers its score for every edit, and formatting edits are small (gap 0.044). Amendment 1, added before any main verdict, reports the formatting false-alarm rate and discrimination (mean semantic accuracy minus false alarms). Edit distance has discrimination 0.00. The passing LLM configurations have 0.93–1.00 with zero false alarms, and the legacy and lexical prompts 0.08–0.55.

## Association with experiment 39's criterion

Criterion: experiment 39's `criteria.heldout.spearman` per configuration (agreement with the three-expert coverage ratings on 45 held-out VeriBench items), read from its committed files on `main` at 99e3496 (selection seal 86ae479, test unlock f5a3f4a). The test view exists because `results/TEST_RECEIPT.json` was committed before this analysis; it is post hoc. Spearman across configurations, with a bootstrap over units (95%) and a one-sided permutation p (10,000, seed 42). Full tables: `results/RESULTS_semantic_screen.md`, `results/index_association.json`.

| Component (per configuration) | Train + val (38 LLM units) | Test, post hoc (18 LLM units) |
|---|---|---|
| Directional accuracy, vacuity | 0.30 [0.13, 0.50], p 0.03 | 0.35 [0.26, 0.65], p 0.11 |
| Directional accuracy, weakening | **0.73 [0.55, 0.86], p < 0.001** | **0.72 [0.31, 0.92], p 0.001** |
| Directional accuracy, over-constraint | 0.41 [0.11, 0.68], p 0.006 | 0.57 [0.06, 0.80], p 0.008 |
| 1 − formatting gap | 0.73 [0.57, 0.82], p < 0.001 | 0.47 [0.14, 0.75], p 0.02 |
| −τ (weakening level) | 0.83 [0.70, 0.90], p < 0.001 | 0.45 [−0.11, 0.74], p 0.03 |
| S = GM(three accuracies, 1 − gap) | 0.72 [0.55, 0.83], p < 0.001 | 0.65 [0.21, 0.87], p 0.003 |

Does S add to a label-free index? I compared the geometric mean of each index with S against the index alone (paired bootstrap of the Spearman difference over units):

| Index | Split | Index alone | GM(index, S) | Δ [95% CI] |
|---|---|---|---|---|
| `C_ms_gold` (experiment 39's selected index) | train + val (n 38) | 0.78 | 0.72 | −0.06 [−0.16, 0.04] |
| `C_ms_gold` | test, post hoc (n 16) | 0.56 | 0.67 | +0.11 [−0.13, 0.39] |
| `TI_var_trainnorm` (paper) | train + val (n 38) | −0.09 | 0.06 | +0.15 [0.05, 0.26] |
| `TI_var_trainnorm` | test, post hoc (n 18) | −0.33 | 0.34 | +0.67 [0.16, 1.16] |
| `PTI_v0_frozen` (paper) | train + val (n 33) | 0.26 | 0.26 | 0.00 |

Reading:

- The semantic components predict judge–human agreement about as well as experiment 39's selected index does. Weakening accuracy (0.73 / 0.72) and S (0.72 / 0.65) sit beside `C_ms_gold` (0.78 train + val, 0.56 test). Unlike `C_ms_gold`, they were not selected on this criterion.
- Combined with the selected index, S adds nothing on train and val. Its test gain has an interval that spans zero.
- The paper's indices behave differently.
  - **`TI_var`:** the gains come mostly from the exact-zero rule of the geometric mean. A non-positive base value gives 0, so the combination largely re-ranks configurations by S.
  - **`PTI_v0`:** it is zero or missing for many configurations, so the combination is unchanged.
- **Caution:** configurations share judge models (six models, several prompts each), so the units are not independent. The bootstrap over units understates uncertainty. Some of the association may be general model capability: the same models (Sonnet 5, Qwen3.6) both agree with experts and catch weakenings.

## Drafted paper sentences (text only; `paper_latex/` was not edited)

**§5 (experiments).** "To test whether judges notice formal specifications that look right but guarantee less, we built 194 Lean-validated probes from the 25 VeriBench references: vacuous statements, cumulative weakenings with a Lean proof that the reference implies each weakened statement, unsatisfiable added hypotheses, and formatting-only edits. All 56 judge configurations of the proxy-index study scored them through Valkyrie with three repeats each. Vacuity was caught almost universally (mean directional accuracy 0.996), but weakening separated judges: under the VeriBench rubrics, Claude Sonnet 5 and Qwen3.6-27B scored a weakened specification below the reference in about nine of ten cases, GPT-6 Sol and Luna in about four of ten, and the paper's legacy prompts, which show the judge only the reference's last theorem, in about six of one hundred. Fifteen of 56 configurations passed a pre-registered screen (directional accuracy at least 0.8 on vacuity, weakening and over-constraint, formatting gap at most 0.05)."

**§5, index paragraph.** "These semantic components were not used to select any index, yet weakening directional accuracy is associated with judge–human agreement across configurations (Spearman 0.73 over 38 train and validation configurations; 0.72 over the 18 held-out configurations, computed after the test split was unsealed). Combining them with the selected label-free index did not increase its agreement on the train and validation configurations (Δ = −0.06, 95% CI [−0.16, 0.04])."

**§6 (limitations).** "The semantic screen is necessary but not sufficient: a character edit-distance baseline passes it because every edit lowers its score, so we also report a formatting false-alarm rate, on which that baseline fails. About half of our weakening probes weaken one theorem while another theorem of the same reference restates the dropped property, and judges that withhold a penalty in that case look worse on the primary metric than on strictly weaker files. Two references contain mutually inconsistent sorry-proved theorems (MyFibonacci's increasing property at n = 1, and gcd's maximality at a = b = 0), and all probes derive from 24 references."

## Open questions for Brando

- The primary weakening metric counts file-level-redundant weakenings (a theorem gets weaker but another theorem restates what was dropped). Should the paper quote the strict-only numbers instead? Both are in the table.
- The legacy prompts' near-zero weakening accuracy follows from their last-theorem rendering, which the paper inherited. Worth stating explicitly in §5 where those prompts are used.
- The `18_MyFibonacci` and `humaneval_13__gcd` references contain mutually inconsistent `sorry`-proved theorems (found by the file-level audit). VeriBench may want to fix them.

## Deviations

- Amendment 1 (secondary metrics only; before any main verdict): formatting false-alarm rate and discrimination.
- File-level audit labels (sensitivity) were added before any call. The proposed one-off exclusion of one weakening level was reverted in favour of the uniform audit.
- Every weakening edit was proposed by Claude Code subagents (claude-opus-5-5, subscription) and admitted only through the Lean checks. Every model call was made through Valkyrie.
- Worker model: claude-opus-5-5 (effort high) throughout; no model switch.

**TLDR-end:** [cj: e42-semantic-probes] Fifteen of 56 judge configurations pass the semantic screen. Vacuity is caught almost universally, but weakening separates judges: Sonnet 5 and Qwen catch about 9 in 10 under VeriBench rubrics, GPT-6 Sol and Luna about 4 in 10, and the paper's legacy prompts about 6 in 100. Weakening accuracy also tracks experiment 39's expert criterion (Spearman 0.73 train + val, 0.72 test post hoc), but adds nothing to experiment 39's selected index on train + val.
