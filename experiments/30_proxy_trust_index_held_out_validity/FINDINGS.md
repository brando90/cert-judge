# Findings: PTI-v0 against human agreement on the experiment 29 panel

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

No criterion-validity claim can be made from this panel, in either direction.
The blocker is not the judges and not the label noise. It is that the headline
proxy has almost no variance across the panel, and the panel is too small for a
correlation to mean anything even if it did.

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
when any ladder rung contributes an exact zero, and again across properties
because the index is a geometric mean. `claude-sonnet-5|P4_CHECKLIST` shows the
cost most clearly. Three of its four properties are strong (0.67, 0.81, 0.90)
and it ends at 0.000 because `P_eq` hit exact zero, which ties it with
`random_r1`. Those are not equally trustworthy judges.

`P_bm` is zero for seven of eight judges, so bug monotonicity is where the
collapse originates.

## 2. The same run's epsilon-floored variant is not degenerate, and ranks the controls correctly

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
ties them with real judges at zero. This is a live argument for changing how
exact zeros are handled before the instrument is used to screen anything, and
it is a decision about the frozen spec, not something to settle here.

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

That happens because the controls are correctly placed at the bottom of both
axes, which manufactures positive association without the instrument having
discriminated among the five real judges at all. A validity correlation that
survives only while deliberately-broken baselines are in the panel is not
evidence that the instrument can rank real judges, and any reported coefficient
should say whether controls were included.

## 5. Human agreement is near zero for every judge here

The criterion values run from −0.001 to 0.425, and only two intervals exclude
zero: `gpt-5.6-terra|P1_BASELINE` at 0.338 (0.093 to 0.551) and
`BAD_STRINGY` at 0.425 (0.206 to 0.610).

`BAD_STRINGY` is the intentionally bad control, and it has the highest human
agreement on the panel. The submission already notes this; here it is starker,
because it now also outranks every real judge. It remains the strongest
argument for property certification over plain judge-human agreement, since
agreement alone would select the broken judge.

## What this changes

1. Decide the exact-zero policy before anything else. The headline index cannot
   be validated in its current form because it has no variance to validate.
2. Grow the judge panel. Twelve units is the floor this harness enforces and
   twenty gives a usable interval; both are reachable with configurations of
   models already in the panel and cost no human labels.
3. Report whether controls are in or out with every coefficient.
4. Only then spend the five-rater pool on the locked held-out test.
