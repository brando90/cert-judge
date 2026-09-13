#!/usr/bin/env python3
"""Plot saved average-rubric contrasts without recomputing the experiment."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "results"


def main():
    rows = json.loads((OUT / "audit.json").read_text())["views"]["average"]["differences"]
    labels, values, lows, highs = [], [], [], []
    for judge, row in rows.items():
        ci = row["conditional_95_interval"]
        labels.append(judge.replace("claude-sonnet-5|", "Sonnet 5 · ")
                      .replace("gpt-5.6-terra|", "Terra · ")
                      .replace("P4_CHECKLIST", "checklist").replace("P8_STRICT_B", "strict")
                      .replace("P1_BASELINE", "baseline"))
        values.append(row["string_minus_primary"])
        lows.append(ci["ci_low"])
        highs.append(ci["ci_high"])
    fig, ax = plt.subplots(figsize=(9, 4.8))
    y = np.arange(len(labels))
    for i, (value, low, high) in enumerate(zip(values, lows, highs)):
        if any(v is None for v in (value, low, high)):
            ax.text(0, i, "undefined", ha="center", va="center")
        else:
            ax.plot([low, high], [i, i], color="#3366A0", lw=2)
            ax.scatter(value, i, color="#3366A0", s=50, zorder=3)
    ax.axvline(0, color="#888888", ls="--", lw=1)
    ax.set(yticks=y, yticklabels=labels, xlim=(-.32, .22),
           xlabel="String control − primary judge: within-problem ordering accuracy",
           title="No resolved ordering advantage on the observed problems")
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(.5, .045, "Average human rubric · 22 informative problems · 2,000 shared problem draws\n"
             "95% percentile intervals; conditional on observed data, unadjusted for five comparisons",
             ha="center", fontsize=9, color="#444444")
    fig.subplots_adjust(left=.24, right=.98, top=.88, bottom=.24)
    plots = OUT / "plots"
    plots.mkdir(exist_ok=True)
    for suffix in ("png", "pdf"):
        fig.savefig(plots / f"within_problem_ordering.{suffix}", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
