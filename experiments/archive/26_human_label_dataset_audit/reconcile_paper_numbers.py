#!/usr/bin/env python3
"""EXP21b: Reconcile the paper's pass1-vs-pass2 numbers with the raw TSVs.

`audit_human_labels.py` recomputes the inter-pass agreement under one convention
(average the duplicated rows) and gets numbers close to but not equal to the paper's.
This script sweeps every plausible convention for handling
  (a) the 3 duplicated `4_json_decoder` rows in `ethan_human_scores_ORIGINAL.tsv`, and
  (b) the row subset (all 75 pairs vs dropping the duplicated problem -> 72),
and reports which combination reproduces the paper's published statistics.

It also prints the problem-level composition of every rater file so it is obvious
which problems each annotator actually saw.

Pure stdlib. Read-only outside `results/`.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import audit_human_labels as A  # same directory

REPO_ROOT = A.REPO_ROOT
EXP_DIR = A.EXP_DIR

# Published values in paper_latex/TMLR_2026/main.tex (lines 388, 1043, 1056, 1057).
PAPER = {
    "spearman": 0.249,
    "pearson": 0.375,
    "kendall": 0.221,
    "qwk": 0.372,
    "mae": 0.778,
    "mse": 1.139,
}


def variants(rows: List[Tuple[A.Pair, float]]) -> Dict[str, Dict[A.Pair, float]]:
    """Different ways to collapse duplicate (gold, candidate) rows into one score."""
    by_pair: Dict[A.Pair, List[float]] = defaultdict(list)
    for p, s in rows:
        by_pair[p].append(s)
    return {
        "mean_of_dupes": {p: sum(v) / len(v) for p, v in by_pair.items()},
        "first_of_dupes": {p: v[0] for p, v in by_pair.items()},
        "last_of_dupes": {p: v[-1] for p, v in by_pair.items()},
        "min_of_dupes": {p: min(v) for p, v in by_pair.items()},
        "max_of_dupes": {p: max(v) for p, v in by_pair.items()},
    }


def qwk_variants(xs: Sequence[float], ys: Sequence[float]) -> Dict[str, float]:
    """QWK is sensitive to how half-point scores are mapped onto the integer grid."""
    out = {}
    out["qwk_round"] = A.quadratic_weighted_kappa(xs, ys)
    out["qwk_floor"] = A.quadratic_weighted_kappa([math.floor(v) for v in xs], [math.floor(v) for v in ys])
    out["qwk_ceil"] = A.quadratic_weighted_kappa([math.ceil(v) for v in xs], [math.ceil(v) for v in ys])
    # half-point grid: double everything so 1.5 -> 3 on an integer 0..10 scale
    out["qwk_half_grid"] = A.quadratic_weighted_kappa([v * 2 for v in xs], [v * 2 for v in ys])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP21b reconcile paper inter-pass numbers")
    ap.add_argument("--out-dir", type=Path, default=EXP_DIR / "results")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    p1 = A.LabelFile("pass1", A.FILES[A.PAPER_PASS1])
    p2 = A.LabelFile("pass2", A.FILES[A.PAPER_PASS2])
    av = A.LabelFile("avg", A.FILES[A.PAPER_AVG])

    d1 = p1.deduped()
    dup_problems = {g for g, _ in p2.duplicate_pairs}

    L: List[str] = []
    W = L.append
    W("# EXP21b: reconciling the paper's inter-pass statistics\n")
    W("Paper values (`paper_latex/TMLR_2026/main.tex` lines 388 / 1043 / 1056 / 1057):\n")
    W("| stat | paper |")
    W("| --- | ---: |")
    for k, v in PAPER.items():
        W(f"| {k} | {v} |")
    W("")
    W(f"The only ambiguity in the raw data is `{p2.path.name}`, which has "
      f"{p2.n_rows} rows for {len(p2.pair_set)} pairs: the problem "
      f"`{sorted(dup_problems)[0]}` appears twice (all 3 of its candidates).\n")

    # ---------------- sweep ----------------
    W("## Convention sweep\n")
    W("Each row is one way of collapsing those duplicate rows, crossed with the row subset.")
    W("`|delta|` is the max absolute deviation from the paper across the 6 statistics.\n")
    W("| dupe rule | subset | n | Spearman | Pearson | Kendall | QWK | MAE | MSE | max abs delta |")
    W("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")

    best = None
    records = []
    for rule, d2 in variants(p2.rows).items():
        for subset in ("all_pairs", f"drop_{sorted(dup_problems)[0][:-5]}"):
            keys = sorted(set(d1) & set(d2))
            if subset.startswith("drop_"):
                keys = [k for k in keys if k[0] not in dup_problems]
            xs = [d1[k] for k in keys]
            ys = [d2[k] for k in keys]
            got = {
                "spearman": A.spearman(xs, ys),
                "pearson": A.pearson(xs, ys),
                "kendall": A.kendall_tau_b(xs, ys),
                "qwk": A.quadratic_weighted_kappa(xs, ys),
                "mae": A.mae(xs, ys),
                "mse": A.mse(xs, ys),
            }
            delta = max(abs(got[k] - PAPER[k]) for k in PAPER)
            records.append({"dupe_rule": rule, "subset": subset, "n": len(keys),
                            **{k: round(v, 6) for k, v in got.items()},
                            "max_abs_delta": round(delta, 6)})
            W(f"| `{rule}` | `{subset}` | {len(keys)} | " +
              " | ".join(A.fmt(got[k]) for k in ["spearman", "pearson", "kendall", "qwk", "mae", "mse"]) +
              f" | {delta:.3f} |")
            if best is None or delta < best["max_abs_delta"]:
                best = records[-1]
    W("")
    W(f"**Closest convention:** `{best['dupe_rule']}` / `{best['subset']}` (n={best['n']}), "
      f"max abs deviation `{best['max_abs_delta']:.3f}`.\n")
    if best["max_abs_delta"] > 0.005:
        W("> No convention reproduces the published numbers exactly. The published inter-pass")
        W("> statistics therefore came from a **snapshot of the label files that no longer matches**")
        W("> what is on disk (or from an intermediate cleaned frame that was not checked in).")
        W("> The qualitative claim (\"agreement between passes is moderate\") survives under every")
        W("> convention; the exact decimals do not.\n")

    # QWK sub-sweep, since QWK is the most convention-sensitive
    W("## QWK grid sensitivity (mean-of-dupes, all 75 pairs)\n")
    d2m = variants(p2.rows)["mean_of_dupes"]
    keys = sorted(set(d1) & set(d2m))
    xs = [d1[k] for k in keys]
    ys = [d2m[k] for k in keys]
    W("| QWK variant | value | paper 0.372 |")
    W("| --- | ---: | --- |")
    for k, v in qwk_variants(xs, ys).items():
        W(f"| `{k}` | {A.fmt(v)} | {A.check(v, PAPER['qwk'], 0.002)} |")
    W("")

    # ---------------- avg file provenance ----------------
    W("## Is the `avg` file really mean(pass1, pass2)?\n")
    da = av.deduped()
    bad = [(k, da[k], d1[k], d2m[k]) for k in keys if abs(da.get(k, float("nan")) - (d1[k] + d2m[k]) / 2) > 1e-6]
    W(f"- reproduces on **{len(keys)-len(bad)}/{len(keys)}** pairs")
    if bad:
        W("- exceptions:\n")
        W("| pair | avg file | pass1 | pass2 (mean-of-dupes) | mean(pass1,pass2) |")
        W("| --- | ---: | ---: | ---: | ---: |")
        for (g, c), a_, x_, y_ in bad:
            W(f"| `{g}` / `{c}` | {a_:g} | {x_:g} | {y_:g} | {(x_+y_)/2:g} |")
    W("")

    # ---------------- problem-level composition ----------------
    W("## Problem-level composition of every rater file\n")
    W("Which gold problems each file actually contains (`.lean` suffix stripped).")
    W("This is what makes the overlap counts in `AUDIT.md` non-obvious.\n")
    loaded = {k: A.LabelFile(k, p) for k, p in A.FILES.items()}
    all_problems = sorted({g for f in loaded.values() for g, _ in f.pairs})
    cols = [
        ("pass1", A.PAPER_PASS1),
        ("pass2", A.PAPER_PASS2),
        ("p1_correct_prompt", "shared/participant1_correct_prompt"),
        ("p2", "shared/participant2_pass_1"),
        ("p3", "shared/participant3_pass_1"),
        ("p4", "shared/participant4_pass_1"),
        ("p5", "shared/participant5_pass_1"),
    ]
    W("| problem | " + " | ".join(n for n, _ in cols) + " |")
    W("| --- | " + " | ".join("---:" for _ in cols) + " |")
    for prob in all_problems:
        cells = []
        for _, key in cols:
            n = sum(1 for g, _ in loaded[key].pair_set if g == prob)
            cells.append(str(n) if n else "-")
        W(f"| `{prob[:-5]}` | " + " | ".join(cells) + " |")
    W(f"| **total problems** | " +
      " | ".join(str(len(loaded[key].problems)) for _, key in cols) + " |")
    W("")
    W(f"- distinct problems across **all** human-label files: **{len(all_problems)}**")
    panel_probs = {g for g, _ in (set(d1) & set(d2m))}
    W(f"- distinct problems in the `n=75` calibration panel: **{len(panel_probs)}**")
    pool_probs = {g for k in A.HELDOUT_KEYS for g, _ in loaded[k].pair_set}
    W(f"- distinct problems in the 5-rater held-out pool: **{len(pool_probs)}**")
    W(f"- in pool but not panel: " + (", ".join(f"`{p[:-5]}`" for p in sorted(pool_probs - panel_probs)) or "(none)"))
    W(f"- in panel but not pool: " + (", ".join(f"`{p[:-5]}`" for p in sorted(panel_probs - pool_probs)) or "(none)"))
    W("")

    (args.out_dir / "RECONCILIATION.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with (args.out_dir / "interpass_convention_sweep.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    print(f"wrote {args.out_dir/'RECONCILIATION.md'}")
    print(f"wrote {args.out_dir/'interpass_convention_sweep.csv'}")
    print(json.dumps({"closest": best}, indent=2))


if __name__ == "__main__":
    main()
