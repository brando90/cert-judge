# Experiment 62: Stage A, does a label-free score pick the judge that matches humans?

TLDR: zero model calls, CPU only. On the 90 cached open-weight judge units of experiments 59 and 60 (10 model families, single-call LLM, no tools), the label-free scores pick far better than random, and `F2_item` (agreement with the frontier-judge consensus) comes close to the oracle inside a model family. The frozen `C_ms_gold` pick falls short of the 0.75 bar. The bar is met only by the `F2_item` global pick, and only while Qwen3.6-27B is in the pool. Full tables: `results/RESULTS_stage_a.md`; raw numbers: `results/ANALYSIS.json`.

Note on the name: the design Doc calls this "E61"; `61_open_weight_judges_on_e43_gaming_candidates` already exists on main, so this folder is 62.

Question, bar and null (from the design Doc, fixed before the run): does a label-free score choose the judge unit with the best human rho? Success = picked unit human rho >= 0.75 with a 95% CI above 0, clearly beating 0.60 (best label-free single unit of experiment 60). Null = no better than 0.60: keep stacking open-weight judges.

Human rho of a unit = Spearman of its median item score with the 3-expert mean on the 45 val+test items (75 human-rated Claude 3.7 Sonnet items in all; per-unit CI about +/-0.3; no human ratings of frontier-judge outputs before 2026-11-06).

Headline (every table uses the 87 units with all three label-free scores; regret = best unit's human rho minus the picked unit's; random-pick mean 0.244; oracle 0.857):

| rule | global pick | its human rho [95% CI] | regret | meets bar (0.75, CI above 0) | clearly above 0.60 (CI lower bound > 0.60) | leave-one-family-out: picks >= 0.75, mean regret | within-family mean pick rho (oracle 0.656, random 0.248) |
|---|---|---|---|---|---|---|---|
| F2_item (needs frontier-judge calls) | qwen36 H1 | 0.857 [0.67, 0.93] | 0.000 | yes, but fails when Qwen3.6 is dropped (0.707) | yes (0.67) | 9/10, 0.010 | 0.614 |
| C_ms_gold (frozen, self-contained) | qwen36 D0 | 0.727 [0.45, 0.90] | 0.130 | no (below 0.75) | no (CI includes 0.60) | 0/10, 0.127 | 0.533 |
| F1_probe (needs frontier-judge calls) | gpt_oss_20b H2 | 0.628 [0.25, 0.86] | 0.229 | no | no (CI includes 0.60) | 0/10, 0.213 | 0.474 |

Important: `F2_item`, and therefore the only row that meets the bar, depends on the frontier-judge consensus (its pooled agreement with human rho is 0.948 [0.91, 0.96]). It is label-free, but it needs frontier-judge calls on the 75 items, so it is not a free, self-contained open-weight selector. `F1_probe` also uses frontier-judge cells. The only selector that needs no frontier call is the frozen `C_ms_gold`, and its pick misses the bar (0.727); its pooled Spearman with human rho is 0.583 [0.36, 0.70].

Reading: (1) every rule beats random inside a family (gain over random 0.23 to 0.37, family-bootstrap CIs above 0; permutation p <= 0.006). (2) `F2_item` has regret 0.04 inside a family (pick equals the best prompt in 6 of 10 families). (3) The `F2_item` global pick clears the bar only while Qwen3.6 is in the pool; without it the pick is qwen3_32b D0 at 0.707. (4) Choosing a prompt on other families and applying it to a new family gives 0.35 to 0.49 (best prompt 0.66, random 0.25), so a label-free prompt choice transfers poorly; for `F2_item` the gain over random is [-0.03, 0.24]. (5) Seed retest (4 families): `C_ms_gold` D0 picks move by 0.03 to 0.2 between seeds; the qwen3_8b pick is weak on both (-0.04 and 0.15). Limits: 10 families, 45 items per unit, picks are single units so their CIs are wide, and the old E59 units have no stored per-unit CI (so the "clearly above 0.60" test is shown only where a CI was recomputed).

Run: `~/.venvs/e59/bin/python scripts/stage_a_selection.py` (numpy, scipy; reads `results/units_90.json`, `results/units_seed1_replicates.json`). `scripts/build_units.py` rebuilt the 26 new E60 units, the 9 hosted qwen36 units and the 36 seed-1 replicates from the E60 harvest tarballs (identical to the committed JSON); the other 54 units are copied from E59's `ANALYSIS.json` (`part1.unit_table`), whose harvests live on the cluster.
