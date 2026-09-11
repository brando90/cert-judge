# Findings: PTI-v0 against human agreement on the experiment 29 panel

**TLDR:** The frozen proxy has seven tied zero scores in this previously observed panel; flooring improves resolution but does not establish validity among the five primary judges. Corrections below distinguish observed rankings from generalization claims; the combined agreement-and-stability follow-up is in [results.md](results.md).

Run of the harness in this folder against the committed v5 outputs of
[`29_proxy_validation`](../29_proxy_validation/).
Reads committed artifacts only; no inference, no new labels.

Reproduce:

```bash
D=experiments/30_proxy_trust_index_held_out_validity
python $D/build_panel_from_exp29.py --view average --output $D/panels/panel_exp29_all.json
python $D/design_check.py --input $D/panels/panel_exp29_all.json
```

## Bottom line

The panel does not establish validity on new judge or generator families.
It has limited proxy ranking resolution and only two primary judge-model
families. Its observed correlations remain descriptive evidence about this
particular panel; they are not a general impossibility or validity result.

## 1. The headline index is degenerate: 7 of 8 judges score exactly zero

| judge | role | `PTI_v0` | P_eq | P_bm | P_ms | P_eqalpha | human agreement (avg) |
|---|---|---|---|---|---|---|---|
| `gpt-5.6-terra\|P8_STRICT_B` | primary | 0.000 | 0.00 | 0.00 | 0.00 | 0.00 | 0.011 |
| `gpt-5.6-terra\|P4_CHECKLIST` | primary | 0.000 | 0.00 | 0.00 | 0.00 | 0.88 | 0.211 |
| `gpt-5.6-terra\|P1_BASELINE` | primary | 0.000 | 0.00 | 0.00 | 0.00 | 0.94 | 0.338 |
| `claude-sonnet-5\|P8_STRICT_B` | primary | **0.811** | 0.92 | 0.65 | 0.78 | 0.94 | 0.089 |
| `claude-sonnet-5\|P4_CHECKLIST` | primary | 0.000 | 0.00 | 0.67 | 0.81 | 0.90 | 0.210 |
| `gpt-5.6-terra\|BAD_STRINGY` | control | 0.000 | 1.00 | 0.00 | 0.85 | 0.94 | 0.425 |
| `editdist_e1` | control | 0.000 | 1.00 | 0.00 | 0.00 | 1.00 | 0.199 |
| `random_r1` | control | 0.000 | 0.42 | 0.00 | 0.00 | 1.00 | −0.001 |

Two distinct proxy values across eight judges. A rank correlation still returns
a number, but it is decided entirely by where the one untied judge falls, so it
is not evidence about the proxy. The harness reports this as a degenerate
predictor and marks the run `UNDERPOWERED` regardless of the coefficient.

The mechanism is the exact-zero rule compounding twice: once inside a property
when any artifact-level property factor is exactly zero, and again across properties
because the index is a geometric mean. `claude-sonnet-5|P4_CHECKLIST` shows the
cost most clearly. Three of its four properties are strong (0.67, 0.81, 0.90)
and it ends at 0.000 because `P_eq` hit exact zero, which ties it with
`random_r1`. The zero aggregate hides differences in their other property scores; it does not by itself establish their relative human-grounded trustworthiness.

`P_bm` is zero for six of eight judges; both Sonnet configurations are positive.
Equality independently collapses the checklist configuration, so bug
monotonicity is not the sole source of aggregate zeros.

## 2. The epsilon-floored variant separates previously tied scores

`epsilon_1e3_sensitivity` is already computed in `properties.json`. Flooring
zeros at 1e-3 instead of collapsing them gives eight distinct values:

| judge | role | `PTI_v0` | epsilon-floored | human agreement |
|---|---|---|---|---|
| `claude-sonnet-5\|P4_CHECKLIST` | primary | 0.000 | **0.813** | 0.210 |
| `claude-sonnet-5\|P8_STRICT_B` | primary | 0.811 | 0.811 | 0.089 |
| `gpt-5.6-terra\|BAD_STRINGY` | control | 0.000 | 0.489 | 0.425 |
| `gpt-5.6-terra\|P8_STRICT_B` | primary | 0.000 | 0.443 | 0.011 |
| `gpt-5.6-terra\|P4_CHECKLIST` | primary | 0.000 | 0.204 | 0.211 |
| `gpt-5.6-terra\|P1_BASELINE` | primary | 0.000 | 0.118 | 0.338 |
| `editdist_e1` | control | 0.000 | 0.036 | 0.199 |
| `random_r1` | control | 0.000 | 0.029 | −0.001 |

The epsilon variant puts the random and edit-distance controls at the bottom,
which is the behaviour a screening instrument should have. The headline index
ties them with real judges at zero. This motivates a sensitivity analysis of zero handling; it does not validate
changing the frozen specification. The exploratory alternatives are evaluated
in the follow-up without overwriting the original index.

## 3. Either way the panel is too small to support a claim

| proxy | units | Pearson | Spearman | Kendall | Lin's CCC | status |
|---|---|---|---|---|---|---|
| `PTI_v0` | 8 | −0.260 | −0.247 | −0.214 | −0.198 | degenerate, underpowered |
| `PTI_v0` | 5 primary | −0.368 | −0.354 | −0.316 | −0.228 | degenerate, underpowered |
| epsilon-floored | 8 | 0.001 | 0.262 | 0.214 | 0.001 | underpowered |
| epsilon-floored | 5 primary | −0.484 | −0.600 | −0.400 | −0.166 | underpowered |

Every interval spans zero, most of them span nearly the whole range, and the
epsilon row at eight units carries a 95% interval 1.36 wide.

## 4. The positive row depends on the controls

The only non-negative Spearman in the table is the epsilon variant over all
eight units. Drop the three controls and it inverts to −0.600.

The controls do not all sit at the bottom of both axes: the string-similarity
control has the highest human agreement. Their inclusion changes the panel
composition and reverses the sign; this does not establish validity among the
five primary configurations. A validity correlation that
survives only while deliberately-broken baselines are in the panel is not
evidence that the instrument can rank real judges, and any reported coefficient
should say whether controls were included.

## 5. Human agreement varies and the string-similarity control ranks highest

The criterion values run from −0.001 to 0.425, and only two intervals exclude
zero: `gpt-5.6-terra|P1_BASELINE` at 0.338 (0.093 to 0.551) and
`BAD_STRINGY` at 0.425 (0.206 to 0.610).

`BAD_STRINGY` is the intentionally bad control, and it has the highest human
agreement on the panel. The submission already notes this; here it is starker,
because it now also outranks every real judge. This exposes disagreement between the intended control classification and
the human criterion. It does not independently validate the property index;
control design and criterion interpretation require further investigation.

## What this changes

- [p 10/10] The requested target includes repeat stability, so evaluate that target from the saved repeated scores before attributing all disagreement to the proxy.
- [p 9/10] Ties limit resolution on this panel, so compare declared zero-handling alternatives without selecting and validating on the same observed data.
- [p 8/10] Generalization depends on independent families, so estimate the sampling design rather than treating 12 or 20 related configurations as universally sufficient.
- [p 8/10] Controls change the association, so report primary-only results alongside all-configurations diagnostics.

Here p denotes predicted priority. The follow-up runs these diagnostics in
`expt_v2/`; any new human-label pool requires a separately locked evaluation
plan. The earlier percentile intervals condition on configuration pairs and
are not uncertainty over new families. A small sample and heavy ties do not
make every coefficient meaningless; they constrain what it can establish.
