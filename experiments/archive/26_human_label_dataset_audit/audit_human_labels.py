#!/usr/bin/env python3
"""EXP21: Audit of the human-judgment label data that actually exists in this repo.

Purpose
-------
The paper (paper_latex/TMLR_2026/main.tex) repeatedly cites `n=75`, `pass1`, `pass2`,
and a held-out pool of `343 labels / 78 pairs`. This script recomputes every one of
those numbers *from the raw TSVs on disk* so the claims are auditable, and reports
where the on-disk data disagrees with the prose.

Design notes
------------
- Pure stdlib (no numpy / pandas / scipy). This repo's macOS python has none of them,
  and the statistics needed here (Pearson, Spearman, Kendall tau-b, quadratic-weighted
  kappa, MAE, MSE) are short enough to implement exactly.
- Read-only: touches nothing outside `results/` under this experiment directory.

Usage
-----
    python3 experiments/26_human_label_dataset_audit/audit_human_labels.py
    python3 experiments/26_human_label_dataset_audit/audit_human_labels.py --out-dir /tmp/x
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent

Pair = Tuple[str, str]  # (gold_file, candidate_file)


# --------------------------------------------------------------------------------------
# Files under audit
# --------------------------------------------------------------------------------------

# The "shared" human-label folder that experiments/19 documents as canonical.
SHARED_DIR = REPO_ROOT / "experiments" / "human_labels"
# The folder the actual paper pipeline (exp16/exp29/exp43) reads from.
PIPELINE_DIR = REPO_ROOT / "experiments" / "archive" / "04_veribench_validation" / "data"

FILES: Dict[str, Path] = {
    # --- shared folder (experiments/human_labels) ---
    "shared/participant1_correct_prompt": SHARED_DIR / "participant1_data_correct_prompt.tsv",
    "shared/participant2_pass_1": SHARED_DIR / "participant2_data_pass_1.tsv",
    "shared/participant3_pass_1": SHARED_DIR / "participant3_data_pass_1.tsv",
    "shared/participant4_pass_1": SHARED_DIR / "participant4_data_pass_1.tsv",
    "shared/participant5_pass_1": SHARED_DIR / "participant5_data_pass_1.tsv",
    "shared/expert_harsh_set": SHARED_DIR / "expert_harsh_set_data.tsv",
    "shared/lenient_set": SHARED_DIR / "lenient_set_data.tsv",
    "shared/old_prompt/participant1_pass_1": SHARED_DIR / "old_prompt" / "participant1_data_pass_1.tsv",
    "shared/old_prompt/participant1_pass_2": SHARED_DIR / "old_prompt" / "participant1_data_pass_2.tsv",
    # --- pipeline folder (04_veribench_validation/data) ---
    "pipeline/ethan_20260425  [= paper pass1]": PIPELINE_DIR / "ethan_human_scores_20260425.tsv",
    "pipeline/ethan_ORIGINAL  [= paper pass2]": PIPELINE_DIR / "ethan_human_scores_ORIGINAL.tsv",
    "pipeline/ethan_avg_two_passes [= paper avg]": PIPELINE_DIR / "ethan_human_scores_avg_two_passes_20260425.tsv",
    "pipeline/ethans_data_same_prompt": PIPELINE_DIR / "ethans_data_same_prompt.tsv",
    "pipeline/jolene_pass_1": PIPELINE_DIR / "jolene_data_pass_1.tsv",
    "pipeline/steven_pass_1": PIPELINE_DIR / "steven_data_pass_1.tsv",
    "pipeline/super_human_pass3_avg_five_raters": PIPELINE_DIR / "super_human_pass3_avg_five_raters.tsv",
}

# The three label views the paper calls pass1 / pass2 / avg.
PAPER_PASS1 = "pipeline/ethan_20260425  [= paper pass1]"
PAPER_PASS2 = "pipeline/ethan_ORIGINAL  [= paper pass2]"
PAPER_AVG = "pipeline/ethan_avg_two_passes [= paper avg]"

# The five-rater pool exp43 calls the held-out corpus.
HELDOUT_KEYS = [
    "shared/participant1_correct_prompt",
    "shared/participant2_pass_1",
    "shared/participant3_pass_1",
    "shared/participant4_pass_1",
    "shared/participant5_pass_1",
]

# Numbers asserted in paper_latex/TMLR_2026/main.tex, with the line where each appears.
PAPER_CLAIMS = {
    "aligned_panel_n": (75, "main.tex:316 'aligned panel of n=75 candidate--gold pairs'"),
    "n_problems": (24, "main.tex:316 'from 24 problems'"),
    "gens_per_problem": (3, "main.tex:316 '3 agent generations per problem'"),
    "interpass_spearman": (0.249, "main.tex:388,1043"),
    "interpass_pearson": (0.375, "main.tex:388,1043"),
    "interpass_kendall": (0.221, "main.tex:1043"),
    "interpass_qwk": (0.372, "main.tex:388,1043"),
    "interpass_mae": (0.778, "main.tex:1056"),
    "interpass_mse": (1.139, "main.tex:1057"),
    "heldout_labels": (343, "main.tex:438,531"),
    "heldout_pairs": (78, "main.tex:438,531"),
    "heldout_raters": (5, "main.tex:531"),
}


# --------------------------------------------------------------------------------------
# Statistics (pure stdlib, exact)
# --------------------------------------------------------------------------------------

def _ranks(xs: Sequence[float]) -> List[float]:
    """Average (fractional) ranks, ties shared -- matches scipy.stats.rankdata('average')."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return float("nan") if dx == 0 or dy == 0 else num / (dx * dy)


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return pearson(_ranks(xs), _ranks(ys))


def kendall_tau_b(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    conc = disc = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = xs[i] - xs[j]
            dy = ys[i] - ys[j]
            p = dx * dy
            if p > 0:
                conc += 1
            elif p < 0:
                disc += 1
            else:
                if dx == 0:
                    tx += 1
                if dy == 0:
                    ty += 1
    n0 = n * (n - 1) / 2
    den = math.sqrt((n0 - tx) * (n0 - ty))
    return float("nan") if den == 0 else (conc - disc) / den


def quadratic_weighted_kappa(xs: Sequence[float], ys: Sequence[float]) -> float:
    """QWK over the integer rating grid spanned by both vectors (halves rounded to nearest int)."""
    a = [int(round(v)) for v in xs]
    b = [int(round(v)) for v in ys]
    lo, hi = min(min(a), min(b)), max(max(a), max(b))
    k = hi - lo + 1
    n = len(a)
    obs = [[0.0] * k for _ in range(k)]
    for i, j in zip(a, b):
        obs[i - lo][j - lo] += 1
    ha = Counter(a)
    hb = Counter(b)
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = ((i - j) ** 2) / ((k - 1) ** 2) if k > 1 else 0.0
            exp = ha[i + lo] * hb[j + lo] / n
            num += w * obs[i][j]
            den += w * exp
    return float("nan") if den == 0 else 1.0 - num / den


def mae(xs: Sequence[float], ys: Sequence[float]) -> float:
    return sum(abs(x - y) for x, y in zip(xs, ys)) / len(xs)


def mse(xs: Sequence[float], ys: Sequence[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(xs, ys)) / len(xs)


# --------------------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------------------

AGENT_RE = re.compile(r"__(agent\d+)\.lean$")


class LabelFile:
    def __init__(self, key: str, path: Path):
        self.key = key
        self.path = path
        self.exists = path.exists()
        self.rows: List[Tuple[Pair, float]] = []
        self.bad_rows: List[List[str]] = []
        self.sha256 = ""
        if not self.exists:
            return
        self.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                gold = (row.get("gold_file") or "").strip()
                cand = (row.get("candidate_file") or "").strip()
                raw = (row.get("human_score_0_5") or "").strip()
                if not gold or not cand:
                    continue
                try:
                    self.rows.append(((gold, cand), float(raw)))
                except ValueError:
                    self.bad_rows.append([gold, cand, raw])

    # ---- derived views -------------------------------------------------------------

    @property
    def n_rows(self) -> int:
        return len(self.rows)

    @property
    def pairs(self) -> List[Pair]:
        return [p for p, _ in self.rows]

    @property
    def pair_set(self) -> set:
        return set(self.pairs)

    @property
    def duplicate_pairs(self) -> Dict[Pair, List[float]]:
        by_pair: Dict[Pair, List[float]] = defaultdict(list)
        for p, s in self.rows:
            by_pair[p].append(s)
        return {p: v for p, v in by_pair.items() if len(v) > 1}

    def deduped(self) -> Dict[Pair, float]:
        """Mean-collapse duplicate (gold, candidate) rows -- this is what the plots do."""
        by_pair: Dict[Pair, List[float]] = defaultdict(list)
        for p, s in self.rows:
            by_pair[p].append(s)
        return {p: sum(v) / len(v) for p, v in by_pair.items()}

    @property
    def problems(self) -> set:
        return {g for g, _ in self.pairs}

    @property
    def agents(self) -> Counter:
        c: Counter = Counter()
        for _, cand in self.pairs:
            m = AGENT_RE.search(cand)
            c[m.group(1) if m else "OTHER"] += 1
        return c

    @property
    def score_hist(self) -> Counter:
        return Counter(s for _, s in self.rows)


# --------------------------------------------------------------------------------------
# Report helpers
# --------------------------------------------------------------------------------------

def fmt(x: float, nd: int = 3) -> str:
    return "n/a" if isinstance(x, float) and math.isnan(x) else f"{x:.{nd}f}"


def check(actual, expected, tol: float = 0.0005) -> str:
    if isinstance(expected, int) and isinstance(actual, int):
        return "MATCH" if actual == expected else "**MISMATCH**"
    if isinstance(actual, float) and math.isnan(actual):
        return "n/a"
    return "MATCH" if abs(actual - expected) <= tol else "**MISMATCH**"


def aligned(a: Dict[Pair, float], b: Dict[Pair, float]) -> Tuple[List[float], List[float], List[Pair]]:
    keys = sorted(set(a) & set(b))
    return [a[k] for k in keys], [b[k] for k in keys], keys


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="EXP21 human-label dataset audit")
    ap.add_argument("--out-dir", type=Path, default=EXP_DIR / "results")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    loaded = {k: LabelFile(k, p) for k, p in FILES.items()}
    missing = [k for k, f in loaded.items() if not f.exists]

    L: List[str] = []
    W = L.append
    W("# EXP21 results: what human-judgment data actually exists\n")
    W("Auto-generated by `audit_human_labels.py`. Every number below is recomputed from the")
    W("raw TSVs on disk; nothing is copied from the paper except the *claimed* values in the")
    W("verification tables.\n")
    if missing:
        W(f"> **Missing files:** {', '.join(missing)}\n")

    # ---------------- 1. Inventory ----------------
    W("## 1. File inventory\n")
    W("| key | rows | unique pairs | dup pairs | problems | agents | score range | sha256[:12] |")
    W("| --- | ---: | ---: | ---: | ---: | --- | --- | --- |")
    for k, f in loaded.items():
        if not f.exists:
            W(f"| `{k}` | MISSING | | | | | | |")
            continue
        ag = ", ".join(f"{a}:{n}" for a, n in sorted(f.agents.items()))
        scores = [s for _, s in f.rows]
        rng = f"{min(scores):g}-{max(scores):g}" if scores else "-"
        W(
            f"| `{k}` | {f.n_rows} | {len(f.pair_set)} | {len(f.duplicate_pairs)} | "
            f"{len(f.problems)} | {ag} | {rng} | `{f.sha256}` |"
        )
    W("")

    # ---------------- 2. Which files are the same data ----------------
    W("## 2. Content-identity classes\n")
    W("Files whose *(gold, candidate) -> score* maps are exactly equal (so the two paths are")
    W("the same dataset under two names):\n")
    keys = [k for k, f in loaded.items() if f.exists]
    seen: set = set()
    classes: List[List[str]] = []
    for i, ka in enumerate(keys):
        if ka in seen:
            continue
        cls = [ka]
        for kb in keys[i + 1 :]:
            if kb in seen:
                continue
            if loaded[ka].deduped() == loaded[kb].deduped():
                cls.append(kb)
                seen.add(kb)
        seen.add(ka)
        classes.append(cls)
    dup_classes = [c for c in classes if len(c) > 1]
    if dup_classes:
        for c in dup_classes:
            W(f"- **identical:** " + " == ".join(f"`{x}`" for x in c))
    else:
        W("- (no two files carry identical score maps)")
    W("")
    W("Pairwise agreement on overlapping pairs (Spearman / n overlap), all files:\n")
    W("| A | B | n overlap | identical scores? | Spearman | MAE |")
    W("| --- | --- | ---: | --- | ---: | ---: |")
    for i, ka in enumerate(keys):
        for kb in keys[i + 1 :]:
            xa, xb, ks = aligned(loaded[ka].deduped(), loaded[kb].deduped())
            if len(ks) < 3:
                continue
            same = "yes" if all(a == b for a, b in zip(xa, xb)) else "no"
            W(f"| `{ka}` | `{kb}` | {len(ks)} | {same} | {fmt(spearman(xa, xb))} | {fmt(mae(xa, xb))} |")
    W("")

    # ---------------- 3. The n=75 panel ----------------
    W("## 3. The `n=75` calibration panel (paper pass1 / pass2 / avg)\n")
    p1, p2, av = loaded[PAPER_PASS1], loaded[PAPER_PASS2], loaded[PAPER_AVG]
    d1, d2, da = p1.deduped(), p2.deduped(), av.deduped()
    panel = sorted(set(d1) & set(d2))
    W(f"- `pass1` file: `{p1.path.relative_to(REPO_ROOT)}` -- {p1.n_rows} rows, {len(d1)} unique pairs")
    W(f"- `pass2` file: `{p2.path.relative_to(REPO_ROOT)}` -- {p2.n_rows} rows, {len(d2)} unique pairs")
    W(f"- `avg`   file: `{av.path.relative_to(REPO_ROOT)}` -- {av.n_rows} rows, {len(da)} unique pairs")
    W(f"- **aligned panel (pairs present in both passes): n = {len(panel)}**")
    if p2.duplicate_pairs:
        W(f"- `pass2` contains {len(p2.duplicate_pairs)} duplicated pair(s) "
          f"({sum(len(v) for v in p2.duplicate_pairs.values())} rows) that collapse by averaging:")
        for pr, vals in sorted(p2.duplicate_pairs.items()):
            W(f"  - `{pr[0]}` / `{pr[1]}` -> {vals} -> {sum(vals)/len(vals):g}")
    W("")

    # is avg really the mean of the two passes?
    ok_avg = sum(1 for k in panel if abs(da.get(k, float("nan")) - (d1[k] + d2[k]) / 2) < 1e-6)
    W(f"- `avg` file reproduces `mean(pass1, pass2)` on **{ok_avg}/{len(panel)}** aligned pairs.")
    W("")

    # structure: problems x agents
    W("### Panel structure (problems x generations)\n")
    prob_counts = Counter(g for g, _ in panel)
    dist = Counter(prob_counts.values())
    W(f"- distinct problems (gold files) in the panel: **{len(prob_counts)}**")
    W(f"- candidates per problem: " + ", ".join(f"{c} problem(s) with {n} candidate(s)" for n, c in sorted(dist.items())))
    W(f"- agent-id breakdown across the panel: " +
      ", ".join(f"{a}:{n}" for a, n in sorted(Counter(AGENT_RE.search(c).group(1) if AGENT_RE.search(c) else "OTHER" for _, c in panel).items())))
    odd = sorted(p for p, c in prob_counts.items() if c != 3)
    if odd:
        W(f"- problems **not** contributing exactly 3 candidates: " + ", ".join(f"`{p}` ({prob_counts[p]})" for p in odd))
    W("")

    W("### Verification against the paper's structural claims\n")
    W("| paper claim | value in paper | value on disk | status | source |")
    W("| --- | ---: | ---: | --- | --- |")
    for name, key in [("aligned panel n", "aligned_panel_n"), ("distinct problems", "n_problems"),
                      ("generations per problem", "gens_per_problem")]:
        exp_v, src = PAPER_CLAIMS[key]
        act = {"aligned_panel_n": len(panel), "n_problems": len(prob_counts),
               "gens_per_problem": (sorted(dist)[0] if len(dist) == 1 else -1)}[key]
        shown = act if act != -1 else f"mixed {dict(sorted(dist.items()))}"
        W(f"| {name} | {exp_v} | {shown} | {check(act, exp_v)} | {src} |")
    W("")
    W(f"> Arithmetic check: {len(prob_counts)} problems x 3 generations = {len(prob_counts)*3}, "
      f"panel is {len(panel)}.")
    W("")

    # ---------------- 4. Inter-pass agreement ----------------
    W("## 4. Inter-pass (pass1 vs pass2) agreement on the aligned panel\n")
    x1 = [d1[k] for k in panel]
    x2 = [d2[k] for k in panel]
    stats = {
        "interpass_spearman": spearman(x1, x2),
        "interpass_pearson": pearson(x1, x2),
        "interpass_kendall": kendall_tau_b(x1, x2),
        "interpass_qwk": quadratic_weighted_kappa(x1, x2),
        "interpass_mae": mae(x1, x2),
        "interpass_mse": mse(x1, x2),
    }
    W("| statistic | paper value | recomputed | status | source |")
    W("| --- | ---: | ---: | --- | --- |")
    for key, val in stats.items():
        exp_v, src = PAPER_CLAIMS[key]
        W(f"| {key.replace('interpass_', 'pass1 vs pass2 ')} | {exp_v} | {fmt(val)} | {check(val, exp_v, 0.002)} | {src} |")
    W("")
    W("Score distributions on the aligned panel (0-5 rubric):\n")
    W("| score | pass1 count | pass2 count |")
    W("| ---: | ---: | ---: |")
    all_scores = sorted(set(x1) | set(x2))
    c1, c2 = Counter(x1), Counter(x2)
    for s in all_scores:
        W(f"| {s:g} | {c1.get(s, 0)} | {c2.get(s, 0)} |")
    W(f"| **mean** | **{fmt(sum(x1)/len(x1), 2)}** | **{fmt(sum(x2)/len(x2), 2)}** |")
    W("")

    # ---------------- 5. Held-out five-rater pool ----------------
    W("## 5. The held-out five-rater pool (paper: 343 labels / 78 pairs)\n")
    pool_rows = 0
    pool_pairs: set = set()
    per_rater = []
    for k in HELDOUT_KEYS:
        f = loaded[k]
        pool_rows += f.n_rows
        pool_pairs |= f.pair_set
        per_rater.append((k, f.n_rows, len(f.pair_set), len(f.problems)))
    W("| rater file | rows | unique pairs | problems |")
    W("| --- | ---: | ---: | ---: |")
    for k, nr, npair, nprob in per_rater:
        W(f"| `{k}` | {nr} | {npair} | {nprob} |")
    W(f"| **union** | **{pool_rows}** | **{len(pool_pairs)}** | **{len({g for g, _ in pool_pairs})}** |")
    W("")
    W("| paper claim | value in paper | value on disk | status | source |")
    W("| --- | ---: | ---: | --- | --- |")
    for name, key, act in [("held-out labels", "heldout_labels", pool_rows),
                           ("held-out distinct pairs", "heldout_pairs", len(pool_pairs)),
                           ("held-out raters", "heldout_raters", len(HELDOUT_KEYS))]:
        exp_v, src = PAPER_CLAIMS[key]
        W(f"| {name} | {exp_v} | {act} | {check(act, exp_v)} | {src} |")
    W("")
    # overlap of pool with the calibration panel
    W(f"- Pairs shared between the five-rater pool and the `n={len(panel)}` calibration panel: "
      f"**{len(pool_pairs & set(panel))}**")
    W(f"- Pairs in the pool that are **not** in the calibration panel: **{len(pool_pairs - set(panel))}**")
    W(f"- Pairs in the calibration panel that are **not** in the pool: **{len(set(panel) - pool_pairs)}**")
    W("")
    W("Pairwise inter-rater Spearman across the five raters (on their shared pairs):\n")
    W("| rater A | rater B | n | Spearman | Pearson | MAE |")
    W("| --- | --- | ---: | ---: | ---: | ---: |")
    for i, ka in enumerate(HELDOUT_KEYS):
        for kb in HELDOUT_KEYS[i + 1 :]:
            xa, xb, ks = aligned(loaded[ka].deduped(), loaded[kb].deduped())
            W(f"| `{ka.split('/')[-1]}` | `{kb.split('/')[-1]}` | {len(ks)} | "
              f"{fmt(spearman(xa, xb))} | {fmt(pearson(xa, xb))} | {fmt(mae(xa, xb))} |")
    W("")

    # ---------------- 6. Stacked "set" files ----------------
    W("## 6. What `expert_harsh_set_data.tsv` / `lenient_set_data.tsv` are\n")
    for setkey in ["shared/expert_harsh_set", "shared/lenient_set"]:
        f = loaded[setkey]
        if not f.exists:
            continue
        by_pair: Dict[Pair, List[float]] = defaultdict(list)
        for p, s in f.rows:
            by_pair[p].append(s)
        mult = Counter(len(v) for v in by_pair.values())
        W(f"### `{f.path.relative_to(REPO_ROOT)}`\n")
        W(f"- {f.n_rows} rows over {len(by_pair)} distinct pairs -> **stacked (long-format) file, not one rating per pair**")
        W(f"- rows-per-pair histogram: " + ", ".join(f"{k} row(s): {v} pair(s)" for k, v in sorted(mult.items())))
        # which single-rater files are contained in it, as multisets
        stack = Counter((p, s) for p, s in f.rows)
        contained = []
        for k2 in keys:
            if k2 == setkey:
                continue
            g = loaded[k2]
            if not g.rows:
                continue
            gc = Counter((p, s) for p, s in g.rows)
            if all(stack[kk] >= vv for kk, vv in gc.items()):
                contained.append((k2, g.n_rows))
        if contained:
            W(f"- fully contained single-rater files (every (pair, score) row present): ")
            for k2, nr in contained:
                W(f"  - `{k2}` ({nr} rows)")
            W(f"  - sum of contained rows = {sum(nr for _, nr in contained)} vs file rows = {f.n_rows}")
        else:
            W("- no single-rater file is fully contained as an exact row multiset")
        W("")

    # ---------------- 7. Machine-readable summary ----------------
    summary = {
        "aligned_panel_n": len(panel),
        "panel_problems": len(prob_counts),
        "panel_candidates_per_problem": dict(sorted(dist.items())),
        "pass1_file": str(p1.path.relative_to(REPO_ROOT)),
        "pass2_file": str(p2.path.relative_to(REPO_ROOT)),
        "avg_file": str(av.path.relative_to(REPO_ROOT)),
        "avg_reproduces_mean_on": f"{ok_avg}/{len(panel)}",
        "interpass": {k: (None if math.isnan(v) else round(v, 6)) for k, v in stats.items()},
        "pass1_mean": round(sum(x1) / len(x1), 6),
        "pass2_mean": round(sum(x2) / len(x2), 6),
        "heldout_pool": {
            "raters": len(HELDOUT_KEYS),
            "labels": pool_rows,
            "distinct_pairs": len(pool_pairs),
            "distinct_problems": len({g for g, _ in pool_pairs}),
            "overlap_with_panel": len(pool_pairs & set(panel)),
        },
        "files": {
            k: {
                "path": str(f.path.relative_to(REPO_ROOT)) if f.exists else None,
                "rows": f.n_rows,
                "unique_pairs": len(f.pair_set),
                "problems": len(f.problems),
                "sha256_12": f.sha256,
            }
            for k, f in loaded.items()
        },
    }

    (args.out_dir / "AUDIT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (args.out_dir / "audit_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Also emit the canonical panel as a single tidy TSV so downstream work has one source.
    with (args.out_dir / "aligned_panel_n75.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["gold_file", "candidate_file", "problem", "agent", "pass1", "pass2", "avg"])
        for g, c in panel:
            m = AGENT_RE.search(c)
            w.writerow([g, c, g[:-5], m.group(1) if m else "", f"{d1[(g,c)]:g}",
                        f"{d2[(g,c)]:g}", f"{(d1[(g,c)]+d2[(g,c)])/2:g}"])

    print(f"wrote {args.out_dir/'AUDIT.md'}")
    print(f"wrote {args.out_dir/'audit_summary.json'}")
    print(f"wrote {args.out_dir/'aligned_panel_n75.tsv'}  ({len(panel)} rows)")
    print(json.dumps({k: summary[k] for k in
                      ["aligned_panel_n", "panel_problems", "panel_candidates_per_problem",
                       "interpass", "heldout_pool"]}, indent=2))


if __name__ == "__main__":
    main()
