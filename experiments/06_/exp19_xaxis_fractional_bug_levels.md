# Why does the EXP19 monotonicity plot show "0.5", "1.5", "2.5", "3.5" on the x-axis?

**TLDR-start:** The fractional ticks (0.5, 1.5, 2.5, 3.5) are *not* data points and they do *not* mean half-bugs were ever introduced — they are matplotlib's default minor-tick labels for a numeric axis whose data only lives at integers 0,1,2,3,4. The bug ladder is still fully discrete (L0…L4); only the *axis labels* are misleading. The fix is one line: force integer ticks.

---

## Short answer

> "0.5" on the x-axis is a **matplotlib auto-tick**, not a real bug level. There is no L0.5 in the experiment. The judge was only ever evaluated at five discrete levels: L0 (clean), L1, L2, L3, L4 (most degraded).

When matplotlib plots numeric data on an x-range of `[0, 4]` and you don't tell it otherwise, its default tick locator (`AutoLocator`) picks pretty round numbers and lands on a 0.5 spacing. Because the line is drawn between integer data points (linear interpolation between markers is purely cosmetic), the axis happily shows "0.5", "1.5", "2.5", "3.5" *as if* fractional levels existed. They don't.

## Evidence that the data is purely discrete

The plotting code in `experiments/04_veribench_validation/exp19_replot_low_variance.py` only ever appends integer levels to the x-list:

```python
# exp19_replot_low_variance.py, lines ~132–145
for lvl in [0, 1, 2, 3, 4]:
    v = []
    for _, ladder in by_problem.items():
        if lvl in ladder:
            v.append(ladder[lvl])
    arr = np.asarray(v, dtype=float)
    if len(arr) == 0:
        continue
    m = float(np.mean(arr))
    cil, cih = _bootstrap_ci(arr, args.bootstrap_iters, args.seed + i * 100 + lvl)
    xs.append(lvl)        # <-- lvl is always an int in {0,1,2,3,4}
    ys.append(m)
```

The level itself is parsed from the `item_key` (lines ~100–109) as an integer that must literally start with `L`:

```python
lvl_txt = parts[1].upper().strip()
if not lvl_txt.startswith("L"):
    continue
try:
    lvl = int(lvl_txt[1:])     # parses "L0".."L4" → 0..4
except Exception:
    continue
```

And the corresponding CSV (`results_exp19_low_variance_replot/bug_curve_main_points.csv`) confirms it — every `bug_level` value is an integer:

```csv
judge_id,bug_level,mean_score,ci_lo,ci_hi,n_problems
gpt-5.3-codex|P8_STRICT_B,0,1.0,1.0,1.0,24
gpt-5.3-codex|P8_STRICT_B,1,0.2708333333333333,...,24
gpt-5.3-codex|P8_STRICT_B,2,0.0,0.0,0.0,24
gpt-5.3-codex|P8_STRICT_B,3,0.0,0.0,0.0,24
gpt-5.3-codex|P8_STRICT_B,4,...
```

No 0.5, no 1.5, no 2.5, no 3.5. Only {0,1,2,3,4}.

## Why matplotlib chose 0.5 spacing

The plotting block sets:

```python
ax.plot(xs, ys, marker="o", linewidth=2.0, ...)
ax.fill_between(xs, lo, hi, alpha=0.16, ...)
ax.set_xlabel("Bug level (L0 clean → L4 most degraded)")
# ... no ax.set_xticks(...) anywhere
```

Because `set_xticks` is never called, matplotlib's `AutoLocator` is in charge. For a data range `[0, 4]` it picks ~9 ticks at 0.5 spacing (its idea of "nice" round numbers). The line that connects the markers is linearly interpolated, so visually you see a continuous curve passing over those fractional ticks, which is what makes the axis read like a continuous variable.

Bottom line: the **axis** was treated as continuous; the **data** is not.

## Recommended fix (one-line change)

Force integer ticks (and integer-only labels) so the axis matches the discrete experimental design. Add this immediately before `ax.set_xlabel(...)` in `exp19_replot_low_variance.py`:

```python
ax.set_xticks([0, 1, 2, 3, 4])
ax.set_xticklabels(["L0", "L1", "L2", "L3", "L4"])
```

Or, if you'd rather keep numeric labels:

```python
from matplotlib.ticker import MaxNLocator
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_xlim(-0.1, 4.1)
```

Either change makes the axis honestly represent the five discrete levels and removes the "what is 0.5?" ambiguity for readers of the paper.

## Optional, stronger fix: plot as a categorical axis

If you want to make it categorically clear that nothing lives between the levels, plot against string categories so matplotlib never draws a continuous axis at all:

```python
labels = ["L0", "L1", "L2", "L3", "L4"]
ax.plot(labels[:len(xs)], ys, marker="o", linewidth=2.0, ...)
ax.fill_between(labels[:len(xs)], lo, hi, alpha=0.16, ...)
```

The connecting line still helps the eye follow monotonicity, but the axis itself is unambiguously discrete.

## What to tell readers (paper-side caveat)

If the figure ships as-is in the paper, a one-line caption clarification is enough:

> *Bug levels are integer-valued (L0–L4); the connecting line is for visual guidance only, and intermediate x-axis values do not correspond to evaluated configurations.*

But the cleaner option is to just regenerate the figure with `set_xticks([0,1,2,3,4])` so no caption disclaimer is needed.

---

**TLDR-end:** Nothing was actually run at L0.5/L1.5/L2.5/L3.5 — those are just matplotlib's default tick labels because the script never calls `set_xticks`. The data and the underlying CSV are strictly integer-valued (L0–L4). Fix it by adding `ax.set_xticks([0,1,2,3,4])` (optionally with `["L0",…,"L4"]` labels) right before `ax.set_xlabel(...)` in `experiments/04_veribench_validation/exp19_replot_low_variance.py`, and the misleading fractional ticks will disappear.

**Snapshot:**
```text
file: experiments/06_/exp19_xaxis_fractional_bug_levels.md  (this file)

evidence the data is integer-only:
  exp19_replot_low_variance.py:132   for lvl in [0, 1, 2, 3, 4]:
  exp19_replot_low_variance.py:144       xs.append(lvl)
  exp19_replot_low_variance.py:106       lvl = int(lvl_txt[1:])

bug_curve_main_points.csv (head):
  judge_id,bug_level,mean_score,ci_lo,ci_hi,n_problems
  gpt-5.3-codex|P8_STRICT_B,0,1.0,1.0,1.0,24
  gpt-5.3-codex|P8_STRICT_B,1,0.270...,0.145...,0.420...,24
  gpt-5.3-codex|P8_STRICT_B,2,0.0,0.0,0.0,24
  gpt-5.3-codex|P8_STRICT_B,3,0.0,0.0,0.0,24

one-line fix to apply in exp19_replot_low_variance.py (~line 159):
  ax.set_xticks([0, 1, 2, 3, 4])
  ax.set_xticklabels(["L0", "L1", "L2", "L3", "L4"])
  ax.set_xlabel("Bug level (L0 clean → L4 most degraded)")
```
