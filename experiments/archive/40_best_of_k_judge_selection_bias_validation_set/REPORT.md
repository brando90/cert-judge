# Experiment 40 report: selection bias from choosing the best of K judges on the 72-pair validation set

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/40_best_of_k_judge_selection_bias_validation_set/REPORT.md>

**TLDR:** Reusing the 72-pair validation set to choose among judge configurations overstates the winner's human agreement by an amount comparable to the gaps between the judges being compared. Choosing the best of 8 configurations on 12 problems overstates its Spearman agreement on the other 12 by 0.15 on average; a simulation fitted to the panel puts the overstatement at about 0.10 for choosing on all 72 pairs. The judge-level associations survive a partial adjustment for choosing the index form in 4 of 9 family-label cells instead of 6 of 9.

All numbers come from frozen scores and labels. No model was called, and nothing under `paper_latex/` was edited. The plan was frozen before any analysis ran ([PROTOCOL.md](PROTOCOL.md), commit `7548c3a`); its three deviations were committed (`d5d6ea2`) before any selection result was inspected. A 200-draw smoke run had written outputs to scratch space; they were not read.

## Setup in one paragraph

The validation set is the paper's 72 candidate–gold pairs from 24 problems (3 candidates each), labeled twice by one annotator (pass1 stricter, pass2 more lenient; "averaged" is their mean). The pool is every judge configuration in the frozen archives scored on exactly those 72 pairs, deduplicated: **109 distinct configurations** (57 GPT-5.3-Codex variants, 22 GPT-4o-mini, 8 Claude Sonnet 4, 6 `cli-sol`, and 4 each of Claude 3.7 Sonnet, Claude Opus 4.7, Qwen3-Coder and Leanstral). The pool excludes the random and edit-distance controls (50 rows), 24 exact duplicates and 2 configurations with constant scores. A configuration's human agreement is the Spearman correlation between its recorded scores and the labels. On averaged labels, agreement ranges from −0.083 to 0.506 (median 0.315). The recomputed values reproduce the paper's Codex table at three decimals. Every other deviation from a frozen value is explained mechanically; see [Reproduction gate](#reproduction-gate).

## Findings

### A. When no configuration tracks the labels, the winner still looks good

Labels were permuted in whole-problem blocks, which keeps their clustering, over 4000 draws. The table gives the largest agreement among K randomly drawn real configurations:

| K | Averaged: mean (95th pct) | Pass1: mean (95th pct) | Pass2: mean (95th pct) |
|---|---|---|---|
| 1 | 0.000 (0.220) | 0.001 (0.214) | −0.001 (0.223) |
| 8 | **0.150** (0.317) | 0.152 (0.313) | 0.147 (0.313) |
| 32 | 0.216 (0.360) | 0.219 (0.363) | 0.214 (0.358) |
| 109 (all) | 0.263 (0.399) | 0.264 (0.398) | 0.258 (0.393) |

The Monte Carlo standard error of each mean is at most 0.0021. For comparison, the Codex panel's semantic prompts reach 0.365–0.466 on averaged labels. The observed best agreement (0.506) exceeds the 95th percentile of the null maximum over all 109 (0.399), and so do **31 of the 109 configurations**: a single-step max-T test at family-wise level 0.05. So the best judges' agreement is not a selection artifact, even though its size is overstated (B, C).

### B. Choosing on half the problems overstates the winner on the other half

Each of 4000 replicates draws a random split into 12 selection problems and 12 held-out problems (36 pairs each), plus a random K-subset of the pool. It then records the agreement of the configuration each rule picks. Results on averaged labels:

| K | Labels rule: choosing half | Labels rule: held-out half | **Overstatement** | v1-index rule: held-out (overstatement) | Random: held-out (overstatement) | Best held-out in subset |
|---|---|---|---|---|---|---|
| 2 | 0.367 | 0.309 | +0.057 | 0.296 (−0.008) | 0.266 (−0.003) | 0.375 |
| 4 | 0.439 | 0.330 | +0.109 | 0.293 (−0.008) | 0.276 (−0.007) | 0.447 |
| 8 | 0.488 | 0.335 | **+0.153** | 0.258 (−0.004) | 0.278 (−0.007) | 0.492 |
| 16 | 0.523 | 0.326 | +0.197 | 0.234 (−0.006) | 0.273 (−0.005) | 0.528 |
| 32 | 0.552 | 0.316 | +0.236 | 0.229 (−0.004) | 0.275 (−0.005) | 0.557 |
| 109 | 0.593 | 0.296 | +0.297 | 0.305 (−0.006) | 0.272 (−0.006) | 0.599 |

- The Monte Carlo standard error of each mean overstatement is 0.004–0.005. Individual splits vary widely: at K = 8 the labels-rule overstatement has a 2.5–97.5% range of −0.334 to +0.689 across splits, because a half holds only 12 problems.
- **Per pass**, the labels-rule overstatement at K = 8 / 32 / 109 is +0.117 / +0.167 / +0.218 on pass1 and +0.194 / +0.286 / +0.368 on pass2. On the noisier pass2 labels, the label-chosen judge's held-out agreement at K = 8 (0.197) is no higher than a random pick's (0.201). At K = 109 it is lower (0.137 vs 0.196).
- **More candidates can make the choice worse, not just its estimate.** The label-chosen judge's held-out agreement peaks at K = 8 (0.335) and falls to 0.296 at K = 109 on averaged labels. With few labels per half, a large pool is increasingly won by configurations that were lucky on the chosen half.
- **Label-free selection is unbiased but not discriminating.** Choosing by the frozen v1 index (`cert_index`, computed from probes only) never overstates agreement (within ±0.01 at every K and label view). But its choices agree with held-out labels about as well as a random pick for 2 to 32 candidates (0.229–0.296 vs 0.266–0.278), and worse than the labels rule for K ≤ 32. The pre-registered rule 3 forbids a superiority claim either way.
- The random rule's overstatement is within three Monte Carlo standard errors of zero in every cell, as pre-registered rule 2 requires.

### C. At the full panel size the overstatement is smaller but still sizable

A latent-quality model reproduces the panel's label structure. Its parameters are fitted to the inter-pass Spearman (0.249), the averaged-label intraclass correlation (0.563) and the within-problem inter-pass correlation (0.110): r = 0.31, tau = 0.78, kappa = 0.50 (Deviation 2). The judges' problem-level intraclass correlation of 0.324 and median pairwise correlation of 0.315 come from the pool. The model was not fitted to B, but at 36 items it reproduces B's measured overstatement to within 0.02 (weak-heterogeneous setting, true agreements uniform on [0, 0.45]):

| K | Measured (B), 36 items | Model, 36 items | **Model, 72 items** | Model null with shared noise, 72 items | Measured null (A), 72 items |
|---|---|---|---|---|---|
| 2 | +0.057 | +0.063 | +0.041 | +0.062 | +0.059 |
| 8 | +0.153 | +0.170 | **+0.100** | +0.160 | +0.150 |
| 32 | +0.236 | +0.241 | +0.149 | +0.232 | +0.216 |
| 64 | — | +0.270 | +0.170 | +0.262 | — |

- Choosing on all 72 pairs roughly multiplies the overstatement by 0.59–0.63 (for K = 8 to 64) relative to choosing on 36. Scaling the measured 36-item values by the model's ratio gives about **0.09 at K = 8** and **0.15 at K = 32** for the paper's 72-pair setting.
- The model's shared-noise null tracks A's measured null within 0.02 at every K (0.160 vs 0.150 at K = 8). Independent judges would inflate more (0.193 at K = 8, 0.315 at K = 64).
- **Sensitivity.** The pre-registered item-level-noise model, whose clustering parameter sat at its grid boundary, gives similar values: +0.088 at K = 8 and +0.132 at K = 32 for 72 items. The held-out check statistic (problem-mean inter-pass correlation, 0.531 observed) is 0.328 in the fitted model and 0.49 in the pre-registered one; with 24 problems, the 0.20 gap is about 1.3 standard errors.

### D. Judge-level associations after adjusting for the choice among four reported index forms

For each family panel (8 configurations), the exact permutation distribution over all 40,320 orderings of the human-agreement vector is compared with the maximum Spearman over the four reported forms (v1, v2, `GM_{.4,.6}`, `TI_var`). The two-sided probabilities follow experiment 38's convention, which the paper quotes; the one-sided ones are as pre-registered:

| Family | Label view | `TI_var` Spearman | Two-sided p, unadjusted | **Two-sided p, adjusted** | One-sided p, unadjusted | One-sided p, adjusted |
|---|---|---|---|---|---|---|
| Codex | averaged | 0.833 | 0.015 | **0.037** | 0.008 | 0.019 |
| Codex | pass1 | 0.905 | 0.005 | **0.013** | 0.002 | 0.006 |
| Codex | pass2 | 0.738 | 0.046 | **0.096** | 0.023 | 0.048 |
| Claude Opus | averaged | 0.643 | 0.096 | **0.190** | 0.048 | 0.095 |
| Claude Opus | pass1 | 0.810 | 0.022 | **0.053** | 0.011 | 0.026 |
| Claude Opus | pass2 | 0.595 | 0.132 | **0.249** | 0.066 | 0.125 |
| Qwen3-Coder | averaged | 0.905 | 0.005 | **0.014** | 0.002 | 0.007 |
| Qwen3-Coder | pass1 | 0.476 | 0.243 | **0.450** | 0.122 | 0.225 |
| Qwen3-Coder | pass2 | 0.857 | 0.011 | **0.031** | 0.005 | 0.015 |

The adjustment multiplies every p-value by 1.9 to 3.2. Cells below 0.05 (two-sided) fall from 6 of 9 to 4 of 9, with Codex pass2 (0.096) and Opus pass1 (0.053) crossing. The adjustment is partial and still optimistic. It ignores the six-weight search, the local weight grid, any forms tried but not reported, and the fitting of the `GM` weights on pass1. The observed associations, unadjusted probabilities and all Table 2 entries reproduce the paper and experiment 38 exactly.

## Implications for the paper

1. The introduction's adaptive-overfitting sentence can carry a measured number. By the pre-registered decision rule 1, the null inflation at K = 8 is 0.150 ≥ 0.10, so the sentence gets a quantitative clause.
2. Section 5.1's "correlations on it are optimistic" can say by roughly how much: about 0.10 Spearman when choosing the best of eight on all 72 pairs, 0.15 on half of them.
3. Section 5.3's unadjusted p-values can be paired with the index-form adjustment, which is the honest companion to "the nine tests are unadjusted".
4. Section 6 gains a limitation the paper does not state yet. The label-free v1 index avoids the overstatement, but the judges it picks have about the held-out agreement of a random pick, so the screen reports failures; it does not rank acceptable judges. `TI_var` was not tested as a selection rule, because its normalization depends on a comparison panel.

## Drafted paper text

One sentence per line, validation-set vocabulary, and no "calibration" as a catchall. The paper owner decides placement. The appendix label `app:selection-bias` is new, and the figure file must be copied to `paper_latex/ICLR_2027_submission/figures/`.

Introduction, after "…risks adaptive overfitting~\citep{dwork2015reusableholdout}." (`01_introduction.tex`; 24 words, one claim):

```latex
On our validation set, the best of eight configurations chosen on half of the problems loses $0.15$ in Spearman agreement on the other half (Appendix~\ref{app:selection-bias}).
```

Section 5.1, after "…so correlations on it are optimistic." (`05_experiments.tex`):

```latex
In a simulation fitted to this panel's inter-pass agreement and clustering, the best of eight configurations chosen on all 72 pairs overstates its agreement by about $0.10$ (Appendix~\ref{app:selection-bias}).
```

Section 5.3, after "…and the nine tests are unadjusted." (`05_experiments.tex`):

```latex
Taking the maximum over the four reported index forms, a partial adjustment for choosing the form on these labels, raises the Codex averaged-label probability from $0.015$ to $0.037$ (Appendix~\ref{app:selection-bias}).
Four of the nine cells remain below $0.05$ after this adjustment, against six before.
```

Section 6, "What the screen covers" (`06_limitations.tex`):

```latex
Choosing configurations by the label-free v1 index does not overstate their agreement, but its choices agree with held-out labels about as well as random choices ($0.23$--$0.30$ versus $0.27$--$0.28$ among two to 32 candidates; Appendix~\ref{app:selection-bias}).
This index therefore does not replace labels for ranking acceptable judges.
We did not test $\mathrm{TI}_{\mathrm{var}}$ as a selection rule because its normalization depends on a comparison panel.
```

Appendix subsection (for `990_appendix_additional_results.tex`):

```latex
\subsection{Selection bias from reusing the validation set}\label{app:selection-bias}
We measure how much choosing among judge configurations on the 72 validation pairs overstates the winner's agreement, using only recorded scores.
The pool contains the 109 distinct configurations we scored on exactly these pairs, excluding random and edit-distance controls.
When labels are permuted in whole-problem blocks, the best of eight configurations still reaches a mean Spearman agreement of $0.150$ (95th percentile $0.317$), and the best of all 109 reaches $0.263$ (Figure~\ref{fig:selection-bias}a).
The observed agreement of 31 configurations exceeds $0.399$, the 95th percentile of the maximum over all 109, so the strongest agreements are not selection artifacts.
Chosen on 12 problems, the best of eight overstates its agreement on the other 12 problems by $0.153$ on averaged labels, $0.117$ on pass1, and $0.194$ on pass2 (Figure~\ref{fig:selection-bias}b--c).
Beyond eight candidates, choosing among more configurations lowers the held-out agreement of the choice, from $0.335$ to $0.296$ at 109.
A latent-quality simulation fitted to the panel's inter-pass agreement and clustering reproduces the half-panel overstatement within $0.02$ and places it at about $0.10$ for eight candidates chosen on all 72 pairs.
Choosing by the label-free v1 index never overstates agreement by more than $0.01$, but its held-out agreement is close to that of a random choice.
At the judge level, taking the maximum over the four reported index forms multiplies the exact two-sided permutation probabilities by $1.9$ to $3.2$; four of nine family--label cells remain below $0.05$, against six unadjusted.

\begin{figure}[h]
\centering
\includegraphics[width=\linewidth]{figures/best_of_k_selection_bias.pdf}
\caption{Choosing among configurations on the validation labels overstates the winner's agreement.
(a) Largest agreement among $K$ configurations with block-permuted labels.
(b) Agreement of the configuration chosen on 12 problems, on those problems and on the other 12.
(c) Chosen-minus-held-out agreement, measured on half panels and simulated for half and full panels; means over 4000 draws.}
\label{fig:selection-bias}
\end{figure}
```

### Drop-in check (scratch builds, 09-26-2026)

Two scratch copies of `paper_latex/ICLR_2027_submission/` at `b4e3db0` were built with Tectonic 0.17.0 (no `latexmk` in this container): one unmodified and one with the five blocks above inserted at the stated anchors and the figure copied into `figures/`. The paper directory itself was not touched.

| Build | Pages | Errors / undefined references | Main text ends | Free lines left on page 9 |
|---|---|---|---|---|
| Unmodified | 19 (same as the committed `main.pdf`) | 0 / 0 | page 9, line 468 | 17 |
| With the drafted text | 21 | 0 / 0 | page 9, line 476 | 9 |

The new appendix renders as C.5 after "Local weight sensitivity", and the introduction sentence lands on page 2. No new overfull or underfull boxes appeared; the modified build has one fewer underfull box.

## Reproduction gate

The protocol's gate stopped the first run. Ten kept configurations deviated from their frozen agreement by more than 1e-3 (maximum 0.0079), while the paper's eight Codex values matched at three decimals. The classification ([`results/reproduction_gate.json`](results/reproduction_gate.json), per row in [`results/pool_manifest.csv`](results/pool_manifest.csv)) covers all 183 scanned configurations with non-constant scores:

| Explanation | Configurations | Evidence |
|---|---|---|
| Within 1e-3 | 165 | Direct recomputation |
| Floating-point ties in mean-aggregated runs | 10 (all kept) | Frozen values reproduce within 1e-6 when the mean is recomputed from `repeat_scores` with `statistics.mean` (2) or `numpy.mean` (8). Different repeat multisets with equal decimal means differ in the last bit and were ranked apart; the recorded six-decimal scores keep them tied. |
| Averaged-label file before commit `9e893c4` | 7 | `results_exp16_multi_judge_human_sets`: pass views match; the averaged view reproduces with the file at `c73507a` (7 of 72 averaged labels differ). None is in the pool. |
| Both causes | 1 | Same run, with the float-tie mean |
| Unexplained | 0 | |

We kept the pre-registered input (the recorded scores), which treats mathematically equal means as ties (Deviation 1).

## Limitations of this analysis

- **One annotator, one domain.** All selection effects are measured against labels that disagree between passes (inter-pass Spearman 0.249). The overstatement depends on that noise level, as the pass-level differences show. With more reliable labels it would be smaller.
- **The pool is historical, not a design.** Its 109 configurations over-represent Codex prompt variants and share caches. K-subsets are random draws from it, not the sequence of choices the authors actually made, so the numbers are what a practitioner choosing among these recorded configurations would face.
- **Half panels.** Held-out estimates need held-out problems, so B chooses on 36 pairs; the 72-pair values come from the fitted simulation (C), whose label model misses the problem-mean inter-pass correlation (0.328 vs 0.531 observed).
- **The v1 index stands in for the property screen.** It is the only label-free per-configuration statistic available for all 109 configurations. `TI_var` needs a comparison panel for its normalization and was not evaluated as a selection rule.
- **Adjustment D is partial**, as stated above.

## Reproduce

```bash
uv venv ~/uv_envs/cert-judge-analysis && uv pip install --python ~/uv_envs/cert-judge-analysis/bin/python numpy==2.2.6 scipy==1.17.1 matplotlib==3.11.1 pytest
~/uv_envs/cert-judge-analysis/bin/python experiments/archive/40_best_of_k_judge_selection_bias_validation_set/analysis/best_of_k_selection_bias.py   # about 2.5 minutes
~/uv_envs/cert-judge-analysis/bin/python experiments/archive/40_best_of_k_judge_selection_bias_validation_set/analysis/make_figure.py
~/uv_envs/cert-judge-analysis/bin/python -m pytest tests/test_best_of_k_selection_bias.py
```

Seeds are fixed (master seed 20260926), so the outputs are byte-identical across runs except for `runtime_seconds` in `results/summary.json`. The gate reads the old averaged-label file from git history. In a clone without commit `c73507a` it reports the 8 non-pool configurations as unexplained and stops, by design.

## Files

| File | Content |
|---|---|
| `results/pool_manifest.csv` | All 185 scanned configurations: status, source, `cert_index`, recomputed and frozen agreement, gate explanation, duplicate aliases |
| `results/reproduction_gate.json` | Gate summary |
| `results/A_null_best_of_k.csv` | Analysis A by label view and K |
| `results/B_split_half_selection.csv` | Analysis B by label view, K and rule |
| `results/C_calibration.json`, `results/C_synthetic_best_of_k.csv` | Analysis C parameters and results by label model, setting, panel size and K |
| `results/D_judge_level_adjusted.csv` | Analysis D, nine family-label cells |
| `results/summary.json` | Seeds, versions, gates, fitted parameters and SHA-256 hashes of 96 inputs |
| `figures/best_of_k_selection_bias.{pdf,png}` | The three-panel figure |

**TLDR-end:** [cj: exp40 selection bias] Choosing the best of 8 judge configurations on the paper's validation labels overstates its human agreement by about 0.15 on half the panel and about 0.10 on all 72 pairs; adjusting for the index-form choice multiplies the judge-level p-values by 1.9 to 3.2, and label-free selection avoids the overstatement without picking better judges.
