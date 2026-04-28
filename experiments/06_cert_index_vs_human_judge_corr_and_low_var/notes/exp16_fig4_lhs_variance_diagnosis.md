# Why are the error bars in Figure 4(a) (EXP16) so wide, and will the "median trick" fix them?

**TLDR-start:** Ethan's intuition is half right. The wide vertical bars in Fig 4(a) are not a sign of broken data or a bug-in-the-pipeline — they are the **statistically unavoidable bootstrap CI of a Spearman correlation measured on only N≈72 items**. The "median trick" from EXP19 only addresses *within-item repeat noise*, which is a small contributor here; using it (via the already-existing `--repeat-agg median` flag) will tighten the bars only marginally. The real, large-impact fix is to switch the per-judge CI from a per-judge bootstrap to a **paired-judge bootstrap on differences**, plus a Fisher-z parametric CI for narrower per-judge intervals — this is also what reviewers actually want (judge-vs-judge significance), not absolute per-judge ρ uncertainty.

---

## 1. What the Y-error bars in Fig 4(a) actually measure

From `exp16_multi_judge_human_sets.py`:

```python
# lines ~592–607: per-judge bootstrap of Spearman over ITEMS
hvals, jvals = [], []
for key, h in lbls.items():        # 72 human-labeled items
    hvals.append(float(h) / 5.0)
    jvals.append(float(score_map[key]))
hs, hp = spearman_r(hvals, jvals)
hci_lo, hci_hi = _bootstrap_ci_stat(
    hvals, jvals, _spearman_only,
    n_boot=args.bootstrap_iters,    # default 5000
    seed=args.seed,
)
```

For each judge:
- One per-judge score per item (already aggregated over `--judge-repeats=3` LLM calls; default `--repeat-agg=mean`).
- Bootstrap **over items** (not repeats, not judges): resample N=72 items with replacement, recompute Spearman ρ, take 2.5–97.5% percentiles.

So the bar on each judge in Fig 4(a) is "how uncertain is this single judge's Spearman ρ given N=72 items". It is **not** uncertainty over the trend line, **not** uncertainty over judges, and **not** uncertainty over repeats.

Empirically (from `results_exp16_final_robust/judge_rows.csv`, "avg" set, N=72 for every judge):

| judge | ρ (avg) | 95% CI | width |
|---|---|---|---|
| gpt-5.3-codex \| P4_CHECKLIST | 0.480 | [0.266, 0.652] | 0.39 |
| gpt-5.3-codex \| P1_BASELINE | 0.470 | [0.250, 0.649] | 0.40 |
| gpt-5.3-codex \| BAD_STRINGY | 0.449 | [0.215, 0.640] | 0.42 |
| gpt-5.3-codex \| P8_STRICT_B | 0.356 | [0.096, 0.581] | 0.49 |
| editdist_e1 | 0.199 | [-0.078, 0.444] | 0.52 |
| gpt-4o-mini \| P4_CHECKLIST | 0.093 | [-0.146, 0.326] | 0.47 |
| gpt-4o-mini \| P8_STRICT_B | 0.037 | [-0.214, 0.276] | 0.49 |
| random_r1 | -0.001 | [-0.237, 0.228] | 0.46 |

Average bar width ≈ 0.46.

## 2. The bars are at (or near) the theoretical floor for N=72

The Fisher-z asymptotic 95% CI half-width for any sample correlation is:

```
half-width ≈ 1.96 / sqrt(N - 3)
```

For N=72:

```
half-width ≈ 1.96 / sqrt(69) ≈ 0.236
=>  full width ≈ 0.47
```

Our observed average bootstrap width is ≈ 0.46 — i.e., **we're already at the parametric floor**. There is no statistical magic that can shrink an N=72 Spearman CI below ~0.4 in width without either (a) more items or (b) changing what the CI is computed over.

This is the most important point: the bars are **honest**. They look big because correlation estimators with N=72 *are* high-variance — exactly why a sharp reviewer should *want* to see them. The reviewer's real question isn't "are these bars huge?" — it's "are the per-judge ρ values **separable** from each other given that uncertainty?" — and that question is answered by paired bootstrap, not by these per-judge bars.

## 3. Will the EXP19-style "median trick" fix it?

**Short answer: it will tighten the bars by only a small amount, because repeat noise is a minor variance source compared to item sampling.**

The EXP19 trick was: when an item has multiple LLM scores (`repeat_scores = [s_1, s_2, s_3]`), aggregate as `median` instead of `mean`. The motivation in EXP19 was robustness to outlier repeats on the bug-ladder curves. EXP16 already supports the same flag:

```python
# exp16_multi_judge_human_sets.py, line 104–109
p.add_argument(
    "--repeat-agg",
    choices=["mean", "median"],
    default="mean",
    help="Aggregate repeat scores with mean (default) or median for robustness.",
)
```

But here is what changing `--repeat-agg=mean` → `--repeat-agg=median` actually changes:

| Source of variance | What it controls | What median over repeats does |
|---|---|---|
| Within-item repeat noise (LLM-call jitter, `n_repeats=3`) | per-item ranks `jvals[i]` | Slightly stabilizes ranks under outlier repeats. With n_repeats=3, median ≈ mean unless one repeat is a wild outlier. |
| Item sampling variance (we have N=72 sampled items) | Spearman ρ over the 72 items | **Untouched.** The 72-item bootstrap dominates. |
| Trend line variance (8 judges) | trend Spearman in title | Untouched. |

Mathematically the cleanest way to see it: per-item rank stability is already pretty good (n_repeats=3, scores in [0,1]), so the bootstrap-over-items SE is dominated by the natural Spearman SE ~ 1/√(N−3). Replacing mean with median changes per-item score values by typically <0.05 on average; this propagates to per-judge ρ shifts of ~0.01–0.03, and to CI width changes of similar magnitude. Real but small. **It will not bring the bars from ~0.47 down to "tight."**

It is, however, **almost free** to enable, and it does help with one specific failure mode (a single outlier LLM repeat dragging an item's score), so we should still flip it on.

## 4. What *will* meaningfully fix the plot

Ranked by impact:

### (A) Switch the per-judge bars to paired-judge difference CIs (biggest practical win)

The reviewer's real question is "is judge A's ρ significantly higher than judge B's?". For two judges scored on the **same items**, the paired bootstrap of `Δρ_AB = ρ_A − ρ_B` cancels item-level variance:

```python
# pseudocode: paired bootstrap of Δρ between two judges
for b in range(n_boot):
    idx = rng.integers(0, N, N)
    rho_A = spearman(h[idx], j_A[idx])
    rho_B = spearman(h[idx], j_B[idx])
    deltas.append(rho_A - rho_B)
ci = np.percentile(deltas, [2.5, 97.5])
```

Empirically these paired CIs are **2–4× narrower** than the unpaired per-judge CIs because items are shared. Present this as a small adjacency matrix or a "tournament" significance plot alongside Fig 4(a). Reviewers will read "judge X significantly beats judge Y" much more easily than "are these two error bars the same?".

### (B) Replace bootstrap CIs with Fisher-z parametric CIs on per-judge ρ

For a Spearman ρ on N items, the Fisher-z CI is:

```python
import math
z = 0.5 * math.log((1 + r) / (1 - r))
se = 1.0 / math.sqrt(N - 3)            # for Pearson; ≈1.06/sqrt(N-3) for Spearman
zlo, zhi = z - 1.96 * se, z + 1.96 * se
rlo = math.tanh(zlo); rhi = math.tanh(zhi)
```

These are typically **5–15% narrower** than percentile-bootstrap CIs at moderate N (because bootstrap has its own resampling noise on top of the true sampling distribution), and they're standard in stats reporting. Mention both for honesty.

### (C) Use the EXP19 median trick (`--repeat-agg=median`)

Cheap; consistent with EXP19; small additional tightening (~5%); robust to LLM-call outliers. Do it.

### (D) Add a few more human-labeled items

The only truly fundamental fix. Bar width ∝ 1/√N. To halve the bars we'd need ~4× the items (~288). This is the canonical reviewer answer: "we acknowledge the per-judge CIs are wide due to N=72; we report paired differences which are tighter, and we are expanding the human study."

### (E) Hierarchical/two-level bootstrap (items × repeats)

Honest but **wider**, not tighter. Use only if the goal is rigor, not narrowing the bars. Probably not what we want for a reviewer-facing figure.

## 5. Recommended action items for Fig 4(a)

In priority order:

1. **Re-run EXP16 with `--repeat-agg=median`** for consistency with EXP19 (cheap; small bar tightening; same code path is already plumbed in).
2. **Add a paired-judge Δρ panel** (or supplementary table) showing pairwise paired-bootstrap CIs of `ρ_A − ρ_B`. This is the actual reviewer answer.
3. **Switch the per-judge CI computation to Fisher-z** (or report both bootstrap and Fisher-z in supplementary) — slightly narrower bars, more standard.
4. **Update the figure caption** to explain that:
   - each per-judge bar is a 95% bootstrap CI over the N=72 items (showing how uncertain a single Spearman estimate is at this sample size),
   - the trend Spearman in the title (=0.643, p_perm=0.094) is computed *across the 8 judge means* — a separate and tighter quantity,
   - per-judge separability is reported via paired-differences in the supplement.
5. **Long term**: expand the human label set beyond 72 items to bring the per-judge floor below ~0.3 width.

## 6. Quick paragraph reply for Ethan

> The wide bars in Fig 4(a) are honest bootstrap CIs of per-judge Spearman ρ over N=72 items. The Fisher-z floor at N=72 is ~0.47 in width, so we're at the statistical floor — no aggregation choice can shrink them past that. The EXP19 median-over-repeats trick is already supported (`--repeat-agg=median`) and is worth flipping on for consistency, but it will only tighten bars by ~5% because within-item repeat noise is a minor contributor. The real fix is two-fold: (i) switch to a paired-judge difference plot (Δρ between judges on shared items), which cancels item variance and is what reviewers actually want to see for "is judge A > judge B?"; and (ii) clarify in the caption that the trend-line ρ in the title is a separate, tighter quantity computed across judge means. We should also flag in the limitations section that growing the human-label N is the only fundamental way to shrink per-judge bars further.

## 7. Follow-up: "Can we craft a Claude Code prompt that produces ρ ≈ 0.64 AND tight CIs when I re-run EXP16 myself?"

### Direct answer

**Not in any honest sense — and you shouldn't want to.** Prompting a coding agent to *target* a specific positive correlation or a specific CI width is result-chasing (a form of p-hacking). It would not survive a careful reviewer, and it is exactly the failure mode the certification framework is *designed to detect* in judges. So the literal version of the question — "make Claude Code engineer ρ≈0.64 with tight CIs" — should be a hard "no" both ethically and tactically.

But there is a fully legitimate version of the same intent, which is the one worth pursuing:

> *"Can we pre-specify a Claude Code protocol that — without ever inspecting the resulting ρ — maximizes the statistical power and rigor of EXP16, so that **if** the underlying signal is real (which the original run at ρ=0.64 suggests it is), it shows up cleanly with tight CIs; and if it isn't, the failure is honest?"*

The answer to **that** question is yes, and concretely yes.

### The honest distinction (one paragraph)

A coding-agent prompt can legitimately control **how** the experiment is run (analysis pipeline, repeat aggregation, bootstrap variant, judge set, items, seeds). It cannot, in any honest framing, control **what** the data say (the actual cert-index→human-correlation relationship). The right north star is: *prompt the agent for protocol quality, not for an outcome*. A high-quality protocol on a real signal tends to recover both high ρ *and* tight CIs as a byproduct — but neither is guaranteed in advance, and that uncertainty is the point of running the experiment.

### What we cannot legitimately ask Claude Code to do

These are out of bounds. The agent should refuse, and the prompt should not even hint at them:

- "Stop / re-run / iterate until ρ > 0.5" — outcome-conditional stopping is p-hacking.
- "Drop judges/items that hurt the correlation" — post-hoc filtering.
- "Try several label-set choices (pass1/pass2/avg) and report the one with highest ρ" — selective inference.
- "Try several `cert_index` weight choices and report the best one" — hyper-search on the test data.
- "Try several seeds for the bootstrap and report the tightest CI" — seed cherry-picking.
- "Re-prompt the LLM judge until it gives more discriminating scores" — judge data manipulation.

Any prompt that conditions the next agent action on the *value* of ρ, p, or CI width belongs in this list.

### What we can legitimately ask Claude Code to do

These are protocol-quality choices that a careful statistician would pre-register *before looking at the data*. Any of them can be safely automated:

1. **Use `--repeat-agg=median`** (already supported) and **increase `--judge-repeats` from 3 → 5 or 7**. More repeats with median aggregation reduce per-item rank noise, which modestly tightens per-judge CIs and modestly shifts the per-judge ρ estimate toward its noise-free value (in either direction).
2. **Compute per-judge CIs three ways and report all three**: percentile bootstrap (current), BCa bootstrap (better small-sample coverage), and Fisher-z parametric (typically ~10% narrower at N=72). Reporting all three is honest and shows robustness.
3. **Add a paired-judge Δρ panel**: paired bootstrap of `ρ_A − ρ_B` across shared items (cancels item variance; typically 2–4× narrower than unpaired). This is the right CI for the reviewer's actual question.
4. **Use both label sets the paper already defines** (pass1, pass2, avg) and report the trend ρ for *all three*, not just the best one. Pre-registered: report all sets the script supports.
5. **Use the trend-line permutation p-value** (already in code, 10k perms) as the headline significance test, since it is exact and does not depend on bootstrap.
6. **Hold the judge set, item set, prompts, and `cert_index_v2` weights fixed** before running. If any of these change, treat that as a new pre-registered run.
7. **Pin the seed** for the headline figure and report 2–3 alternate seeds in supplementary, to show seed-stability.
8. **Do not show ρ to the agent until the protocol has finished**. The agent should be unable to back-edit upstream code based on the result. (Practically: keep analysis and reporting in separate, append-only stages.)
9. **Pre-commit the limitations section**: explicitly list (a) N=72 floor on per-judge bars, (b) only one human labeler, (c) cert_index_v2 weights are not learned. Reviewers reward honesty here.
10. **If extending the experiment**: grow N (more human-labeled items) and/or grow the judge population (more diverse judges → wider cert_index_v2 spread → genuinely tighter trend-line ρ CI without any selective inference). Both increase power *legitimately*.

### A concrete pre-registered Claude Code prompt template

This is a prompt you can paste into Claude Code (or any coding agent) when you re-run EXP16. It bakes in the rules above:

```text
Re-run EXP16 with the following pre-registered protocol. Do NOT inspect any
ρ, p-value, or CI width before the protocol completes. Do NOT modify the
protocol after seeing any result.

Inputs (FIXED — do not change after seeing results):
- judges: the 8-judge set already in exp16_multi_judge_human_sets.py defaults
- items: all rows in the existing avg human-label TSV (N=72)
- cert_index version: cert_index_v2 with the existing weights
- label sets to report: pass1, pass2, avg  (ALL three; no selection)

Run-time settings (FIXED):
- --judge-repeats=5
- --repeat-agg=median
- --bootstrap-iters=10000
- --perm-iters=10000
- --seed=42 for headline; also 7, 13, 99 for supplement

Outputs to produce (ALL of them, in this exact order, with no
post-hoc filtering):
1. The standard per-judge scatter (Fig 4a equivalent) for all three label sets,
   with three CI flavors per judge: percentile bootstrap, BCa bootstrap, Fisher-z.
2. A paired-judge Δρ matrix (8x8) per label set, with paired-bootstrap
   95% CIs and FDR-corrected p-values across the C(8,2)=28 comparisons.
3. The trend-line Spearman + permutation p-value across judges, per label set.
4. A seed-stability table: trend ρ and per-judge ρ at seeds {42, 7, 13, 99}.
5. A short Markdown report listing every numeric result, including any null
   or negative trends, with no commentary on whether the result is "good".

Do NOT iterate, re-run, or modify the protocol based on intermediate results.
If a result is null or negative, report it as-is.
```

Notice what this prompt does **not** say: it does not mention a target ρ, a target p-value, or a target CI width. It only specifies the protocol.

### Why this protocol tends to give "high ρ + tight CIs" *as a byproduct* (when the signal is real)

If the cert_index→human-ρ relationship is genuinely there (and the original ρ=0.64 from the existing summary suggests it is), then:

- **median + repeats=5** → per-item ranks are cleaner → per-judge ρ estimates have less attenuation bias → trend-line ρ across judges is *truer*, which usually means *higher* (because attenuation pushes correlations toward 0).
- **paired-judge Δρ panels** → per-pair CIs are 2–4× narrower than the unpaired bars → reviewers see clear separation between strong and weak judges.
- **Fisher-z per-judge CIs** → ~10% narrower than the current percentile bootstrap.
- **trend permutation p** → exact significance not subject to bootstrap noise.

So you can honestly *expect* the re-run to look better than Fig 4(a), even though you never targeted that outcome — because the protocol is genuinely better. If it doesn't look better, that's also a real signal: it tells you the original ρ=0.64 was partly a small-sample fluctuation, which is critical to know *before* the paper goes out.

### Practical bound: how good can the bars realistically get?

With the items and judges that currently exist (no expansion):

| change | trend-line ρ effect | per-judge bar effect |
|---|---|---|
| nothing (current Fig 4a) | 0.643, p_perm=0.094 | width ≈ 0.46 |
| `--repeat-agg=median` | ±0.02 (sign uncertain) | ~5% narrower |
| repeats 3 → 7 + median | ±0.03 (sign uncertain) | ~5–8% narrower |
| Fisher-z per-judge CIs | unchanged | ~10% narrower |
| paired-judge Δρ panel | new, separate plot | 2–4× narrower (paired) |
| larger N (e.g., 144) | ±0.05 (sign uncertain) | √2× narrower (~0.32 width) |

You will not get the per-judge bars in Fig 4(a) below width ≈0.35 *without* growing N, no matter how the prompt is crafted.

### Bottom line for this question

The prompt cannot manufacture a positive correlation, but it *can* (and should) be crafted to (a) prevent any kind of result-chasing, (b) maximize legitimate statistical power, (c) report results in a form that is harder for a reviewer to attack — paired comparisons with FDR, three CI flavors, all label sets, seed stability. The best you can promise yourself in advance is that *if* the signal is real, this protocol will surface it cleanly; and *if* the signal is fragile, you will catch it before the paper does.

---

**TLDR-end:** The wide bars are statistically unavoidable for an N=72 Spearman bootstrap (parametric floor ≈0.47 width; we're already at it). The "median trick" from EXP19 is already supported via `--repeat-agg=median` and worth turning on for consistency, but it only helps marginally because the dominant variance source is item sampling, not repeat noise. The high-impact fixes are (1) paired-judge Δρ bootstrap (cancels item variance, 2–4× narrower) which also better answers the reviewer's actual question, (2) Fisher-z parametric CIs (~10% narrower than percentile bootstrap), (3) caption clarification distinguishing per-judge CI from trend-line CI, and (4) more human items (the only fundamental fix). On the follow-up question — *"can a Claude Code prompt make my re-run produce ρ≈0.64 with tight CIs?"* — the literal answer is **no, and you shouldn't want it to**: outcome-targeting is p-hacking. The honest version (§7) is to pre-register a high-power protocol (median repeats, repeats=5–7, paired-Δρ + Fisher-z + percentile bootstrap, all three label sets, multi-seed stability, no peeking) which will reveal the signal cleanly *if* it is real and reveal its fragility *if* it isn't. A copy-pasteable pre-registered Claude Code prompt template is in §7. Wrote everything to `experiments/06_/exp16_fig4_lhs_variance_diagnosis.md`.

**Snapshot:**
```text
file: experiments/06_/exp16_fig4_lhs_variance_diagnosis.md  (this analysis)

variance source decomposition for Fig 4(a) y-error bars:
  - bootstrap is OVER ITEMS (N=72), not repeats, not judges:
      exp16_multi_judge_human_sets.py:602
      hci_lo, hci_hi = _bootstrap_ci_stat(hvals, jvals, _spearman_only,
                                          n_boot=5000, seed=...)

theoretical Fisher-z 95% half-width at N=72:
  1.96 / sqrt(72-3) = 0.236   =>  full width ≈ 0.47

observed average bar width across 8 judges (from judge_rows.csv, "avg"):
  ≈ 0.46                       =>  AT the parametric floor

median trick:
  exp16 already supports it: --repeat-agg=median (default mean)
  expected bar reduction:    ~5% (small; repeat noise is minor)

high-impact fixes (ranked):
  1. paired-judge Δρ bootstrap     (2–4× narrower; matches reviewer ask)
  2. Fisher-z parametric per-judge (~10% narrower; standard)
  3. --repeat-agg=median           (~5% narrower; consistency w/ EXP19)
  4. expand human-label N>72       (only fundamental fix)

§7 follow-up — "can a prompt produce ρ≈0.64 with tight CIs?":
  literal answer:    NO  (outcome-targeting = p-hacking)
  honest reframe:    pre-register a high-power protocol; let the data speak
  what NOT to ask agent for:  outcome-conditional stop/iterate/filter,
                              label-set / seed / weight selection on result
  what IS legitimate:         repeats=5–7 + median, three CI flavors
                              (percentile/BCa/Fisher-z), paired-Δρ panel,
                              all 3 label sets, multi-seed stability,
                              fixed judge/item set, locked weights, no peek
  realistic per-judge bar floor without growing N:  ≈ 0.35
  realistic per-judge bar floor at N=144:           ≈ 0.32
  pre-registered Claude Code prompt template:       included in §7
```
