# Experiment 49 — PROTOCOL (LOCKED before any number is computed)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters/PROTOCOL.md>

**TLDR:** Zero-inference design study for the planned cert-judge human rating pool (the judge-screening pool that VeriBench's set-N plan defers to "a separate pool on other tasks", option C of amendment C15). Using experiment 39's cached judge scores (56 LLM judge configurations × 75 VeriBench items × 3 repeats) and VeriBench experiment 100's five current raters, it measures by resampling how the judge–human criterion's precision, its ranking of judge configurations, and the power of the pre-registered held-out test (Spearman ≥ 0.45, one-sided permutation p-val < 0.05) depend on the number of rated tasks, raters per item and held-out judge configurations. The output is a measured sample-size table, not a verdict on any judge.

Written before any statistic below was computed (10-14-2026). Deviations are recorded in `results.md` under "Deviations", never by editing this file; amendments are numbered and appended at the end and apply prospectively.

## Scientific question (locked)

For a human rating pool that will serve as the criterion for screening judge configurations (new models and prompts), which numbers of rated tasks T (three agent outputs per task, as in experiment 100), raters per item R and held-out judge configurations K make (i) the criterion rank judge configurations reliably and (ii) the held-out test of a label-free screen adequately powered at the effect sizes experiment 39 observed? The existing arithmetic in the rating-pool lane (`experiments/ideas/cj_human_rating_pool_prospective_screen/scripts/e39_screen_baseline_readonly.py`, uncommitted on 10-14-2026) scales interval widths by √(15/T); this experiment replaces that assumption with resampled measurements.

**Central uncertainty (Trigger Rule 50).** Whether a pool of the size the team can rate (set N is 25 task folders with two ratings per file and about 60–110 rater-hours) can produce a criterion precise enough to tell good judge configurations from bad ones and to test a screen on held-out judges, or whether the decisive constraint is the number of held-out judge configurations rather than the number of ratings.

## Frozen inputs (hashed at first read; `results/input_manifest.json`)

| Input | Path | Use |
|---|---|---|
| Per-cell judge scores | experiment 39 `results/harvest/<config>.json` (56 LLM configurations; `crit` cells = 75 items × 3 repeats; controls excluded) | per-item median scores for every configuration |
| Unit files | experiment 39 `results/units_train_val.json`, `results/units_test.json` | `C_ms_gold` per configuration, split labels, registered criterion values (gate) |
| Probe manifest | experiment 39 `results/probe_manifest.json` | not used beyond the gate |
| Expert ratings | VeriBench experiment 100 `inputs/items.jsonl`, SHA-256 `ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c` (75 items, 25 tasks, raters `p1`–`p5` on 0–5; `p3` is missing on 30 items: 12 train, 6 validation, 12 test) | rating matrix and task structure |

Experiment 39's root is resolved at `experiments/39_…` first and `experiments/archive/39_…` second; the VeriBench checkout is `CJ_VERIBENCH_REPO` (default `/Users/brandomiranda/veribench`); the items file is accepted only if its SHA-256 matches. Experiment 39's `scripts/analysis_lib.py` is imported for the gate; the resampling loops may use NumPy only after a parity test shows identical Spearman values (to 1e-9) on the full data.

## Gate G0 — reproduction (must PASS before any new number is read)

1. Every LLM configuration's held-out criterion Spearman (45 items of the validation and test tasks, `target_expert` = mean of raters 1–3 ÷ 5, median of repeats) recomputed from the harvest matches the unit files to 1e-9.
2. The registered test association of `C_ms_gold` (16 units: Spearman 0.558…, interval [0.078…, 0.762…], permutation p-val 0.0127, seed 39) is reproduced to 1e-9 through `analysis_lib.association`.

## Fixed conventions

- A "rating target" for an item is the mean of the drawn raters' available 0–5 ratings ÷ 5; an item with no drawn rating is dropped from that draw. A configuration's criterion in a draw is the tie-aware Spearman between its per-item median score and the target over the drawn items, computed only when ≥ 90% of the drawn items have a score (experiment 39's rule), otherwise NOT_COMPUTABLE for that draw.
- Reference criterion = all 25 tasks (75 items) with the mean of all available current raters (the five-rater target of experiment 45). The registered design (15 validation + test tasks, raters 1–3) is reproduced as one labelled cell.
- Tasks are the resampling unit for items (all three outputs of a task move together). Seeds: 49 throughout (G0 uses 39). Thresholds: 0.45 and p-val < 0.05 are experiment 39's pre-registered gate; the design targets below (0.90 ranking reliability, 0.90 gate agreement, 0.80 power) are agent-suggested conventions and are labelled as such wherever they appear.

## Pre-registered analyses

**Q1 — Criterion precision and ranking reliability versus tasks and raters (empirical subsampling).** Grid: T ∈ {5, 8, 10, 15, 20, 25} tasks (sampled without replacement from the 25; T = 25 varies only the raters) × R ∈ {1, 2, 3, 5} raters (a subset of the five current raters drawn without replacement; R = 5 is the full set). 1,000 draws per cell. Per cell: (a) precision: the SD across draws of each configuration's criterion, averaged over the 56 configurations, and separately over the eight H2 configurations; (b) ranking reliability: Spearman between the draw's 56-configuration criterion vector and the reference vector, mean and 5th percentile over draws; (c) gate agreement: the fraction of configurations whose pass/fail at 0.45 agrees with the reference, mean over draws; (d) held-out association: Spearman between `C_ms_gold` and the draw's criterion over the 16 computable test units, mean, 5th and 95th percentile over draws; (e) the number of ratings used (items × R, minus missing).

**Q2 — Power of the held-out test versus the number of held-out judge configurations.** (a) Empirical: for K ∈ {8, 12, 16, 24, 32, 48}, draw K (`C_ms_gold`, reference criterion) pairs with replacement from each declared pool — all computable LLM configurations; the 16 test units; the fuller-context configurations (prompts D0/H0/H1/H2/R4, all splits); the legacy configurations (P1/P4/P8/LEX, all splits) — 1,000 draws, each with a 1,000-permutation one-sided p-value; power = fraction of draws with Spearman ≥ 0.45 and p-val < 0.05; also the mean Spearman and its SD across draws. (b) Parametric: bivariate normal pairs with true correlation ρ ∈ {0.30, 0.45, 0.56, 0.70}, same K grid, 2,000 draws, same gate; the Spearman of the sample. (c) Cluster-aware: draw M ∈ {2, 3, 4, 6, 9} judge models with replacement from the nine model keys (six single-call, three Terminus2) and take all their computable configurations; power as in (a). Configurations inside a model share its errors, so (a) is optimistic and (c) is the honest variant.

**Q3 — Allocation at equal rating budgets.** From the Q1 grid only: for each rating budget B achievable by more than one (T, R) cell (B ≈ 3T·R, exact count of available ratings reported), the cell with the highest mean ranking reliability, and the trade-off stated in words (more tasks with fewer raters versus fewer tasks with more raters).

**Q4 — Model-based extrapolation (labelled as such).** (a) Rater reliability: ICC(C,1)-style consistency of a single rater and the Spearman–Brown reliability of the mean of R raters from the 75 × 5 rating matrix (two-way random effects, method of moments, missing cells allowed). (b) Design effect: the ratio of Q1's empirical criterion SD at T = 25, R = 5 to the Fisher-transform standard error 1/√(N − 3) for N = 75 independent items; used to extrapolate the criterion SD to N ∈ {90, 120, 150} items. (c) The attenuation of any proxy–criterion correlation implied by (a): ρ_max = √(reliability of the R-rater target).

## Pre-declared readings (recorded before the numbers)

- Design recommendation = the smallest (T, R) cell with mean ranking reliability ≥ 0.90 and gate agreement ≥ 0.90, and, per pool, the smallest K (and M) with power ≥ 0.80 at the pooled effect size; if no cell in the grid reaches a target, the best achieved value is reported and the target is stated as unmet.
- The headline is the triple (smallest adequate (T, R); smallest adequate K for the all-configuration pool; power at K = 16 for the fuller-context pool), each with the measured values.
- Nothing here changes experiment 39's verdict, the frozen screen, or set N's evaluation-only rule.

## Execution

- `python3 scripts/analyze_e49.py` from the repository root writes `results/*.json` and `RESULTS_rating_round_design.md`; `python3 -m pytest scripts/test_e49.py` runs the offline tests. No model calls, no credentials, no network.
- Estimated wall-clock: under fifteen minutes on a laptop (NumPy for the permutation loops).

## Amendments

_None._
