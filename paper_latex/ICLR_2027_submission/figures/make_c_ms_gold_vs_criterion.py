#!/usr/bin/env python3
"""TLDR: Draw the paper's main-result figure (gold deletion-monotonicity component C_ms_gold against each judge
configuration's agreement with the expert ratings, one panel per judge split) from experiment 39's committed unit files;
no model calls, no new numbers. Run from anywhere: python3 make_c_ms_gold_vs_criterion.py"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E39 = REPO / "experiments/archive/39_label_free_proxy_index_train_val_test_over_judge_families/results"
OUT = HERE / "c_ms_gold_vs_criterion_train_val_test.pdf"

LEGACY = {"P1", "P4", "P8", "LEX"}                     # the paper's earlier prompts: the judge sees the gold's last theorem block only
FULLER = {"D0", "R4", "H0", "H1", "H2"}               # VeriBench rubrics: complete reference, Python source and full candidate


def load(name: str) -> list[dict]:
    return json.loads((E39 / name).read_text())["units"]


def group(unit: dict) -> str:
    prompt = unit["config"].split("|")[1]
    if unit["kind"] != "llm":
        return "control"
    if unit["harness"] != "vb103_judge":
        return "agent"
    return "legacy" if prompt in LEGACY else "fuller"


STYLE = {
    "fuller": dict(marker="o", color="#1f5fa8", label="fuller-context prompt (D0, R4, H0--H2)"),
    "legacy": dict(marker="s", color="#c8102e", label="legacy prompt (P1, P4, P8, LEX)"),
    "agent": dict(marker="^", color="#2a9d4a", label="Terminus2 agent judge"),
    "control": dict(marker="x", color="#777777", label="deterministic control (train only, not used for selection)"),
}


def main() -> None:
    units = load("units_train_val.json") + load("units_test.json")
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), sharey=True)
    for ax, split, title in zip(axes, ("train", "val", "test"), ("Train judges", "Validation judges", "Test judges (held out)")):
        rows = [u for u in units if u["split"] == split]
        n_llm = 0
        for g, st in STYLE.items():
            xs, ys = [], []
            for u in rows:
                if group(u) != g:
                    continue
                x = u["indices"].get("C_ms_gold")
                y = (u["criteria"].get("heldout") or {}).get("spearman")
                if x is None or y is None:
                    continue
                xs.append(x)
                ys.append(y)
                if g != "control":
                    n_llm += 1
            if xs:
                ax.scatter(xs, ys, s=34, alpha=0.9, zorder=3, **st)
        ax.set_title(f"{title}\n$n={n_llm}$ configurations with both values", fontsize=9)
        ax.set_xlabel(r"$C_{\mathrm{ms,gold}}$ (gold deletion monotonicity)", fontsize=9)
        ax.axhline(0.0, color="#bbbbbb", lw=0.6, zorder=1)
        ax.set_xlim(-0.03, 1.03)
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel("Agreement with expert ratings\n(Spearman, 45 held-out items)", fontsize=9)
    seen: dict[str, object] = {}
    for ax in axes:                                              # the agent judges appear only on the validation and test panels
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    order = [STYLE[g]["label"] for g in ("fuller", "legacy", "agent", "control") if STYLE[g]["label"] in seen]
    fig.legend([seen[l] for l in order], order, loc="lower center", ncol=2, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.08))
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
