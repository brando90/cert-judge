# Experiment 62: Stage A, does a label-free score pick the judge that matches humans?

TLDR: zero model calls, CPU only. On the 90 cached open-weight judge units of experiments 59 and 60 (10 model families, single-call LLM, no tools), the label-free scores pick far better than random, and `F2_item` (agreement with the frontier-judge consensus) comes close to the oracle inside a model family. The frozen `C_ms_gold` pick falls short of the 0.75 bar. The bar is met only by the `F2_item` global pick, and only while Qwen3.6-27B is in the pool. Full tables: `results/RESULTS_stage_a.md`; raw numbers: `results/ANALYSIS.json`.

Note on the name: the design Doc calls this "E61"; `61_open_weight_judges_on_e43_gaming_candidates` already exists on main, so this folder is 62.

Question, bar and null (from the design Doc, fixed before the run): does a label-free score choose the judge unit with the best human rho? Success = picked unit human rho >= 0.75 with a 95% CI above 0, clearly beating 0.60 (best label-free single unit of experiment 60). Null = no better than 0.60: keep stacking open-weight judges.

Human rho of a unit = Spearman of its median item score with the 3-expert mean on the 45 val+test items (75 human-rated Claude 3.7 Sonnet items in all; per-unit CI about +/-0.3; no human ratings of frontier-judge outputs before 2026-11-06).

Headline (common pool, 87 units with all three scores):

| rule | global pick | its human rho | regret | within-family mean pick rho (oracle 0.656, random 0.25) | LOFO prompt transfer |
|---|---|---|---|---|---|
| C_ms_gold | qwen36 D0 | 0.727 | 0.130 | 0.533 | 0.492 |
| F2_item | qwen36 H1 | 0.857 [0.67, 0.93] | 0.000 | 0.614 | 0.387 |
| F1_probe | gpt_oss_20b H2 | 0.628 | 0.229 | 0.483 | 0.492 |

Reading: (1) every rule beats random inside a family (gain over random 0.23 to 0.36, family-bootstrap CIs above 0; permutation p <= 0.005). (2) `F2_item` has regret 0.04 inside a family (pick equals the best prompt in 6 of 10 families), but it uses frontier-judge outputs. (3) Dropping Qwen3.6 from the pool, the `F2_item` global pick is qwen3_32b D0 at 0.707, below 0.75; the pick that clears the bar depends on one strong family. (4) Choosing a prompt on other families and applying it to a new family gives 0.39 to 0.49, so a label-free prompt choice does not transfer well. (5) Seed retest (4 families): D0 picks of `C_ms_gold` move by 0.03 to 0.2 between seeds; the qwen3_8b pick is weak on both (-0.04 and 0.15). Limits: 10 families, 45 items per unit, picks are single units so their CIs are wide, and the old E59 units have no stored per-unit CI.

Run: `~/.venvs/e59/bin/python scripts/stage_a_selection.py` (numpy, scipy; reads `results/units_90.json`, `results/units_seed1_replicates.json`). `scripts/build_units.py` rebuilt the 26 new E60 units, the 9 hosted qwen36 units and the 36 seed-1 replicates from the E60 harvest tarballs (identical to the committed JSON); the other 54 units are copied from E59's `ANALYSIS.json` (`part1.unit_table`), whose harvests live on the cluster.
