#!/usr/bin/env python3
"""
EXP43: Frozen TIvar vs Held-Out 343-Label Human Correlation.

Addresses the top TMLR reviewer concern:
  "Run the held-out 343-label analysis now. Freeze TIvar exactly as-is,
   then report held-out correlations."

Protocol
--------
1. TIvar (v3) is taken frozen from EXP30 results — NOT refit.
2. Judge-level human Spearman is computed on the HELD-OUT participant1–5
   corpus (343 labels, 78 pairs, 60 overlap with EXP16 judge scores).
   These labels were never used in TIvar development.
3. Family-level Spearman(TIvar, held_out_human_spearman) is reported
   with 2000-replicate bootstrap CIs.
4. Results are compared to the calibration-panel numbers (pass1/pass2/avg)
   from judge_rows.csv.

Output tables
-------------
HELD_OUT_TABLE.md — family × {calib_spearman, heldout_spearman, bootstrap_ci}
HELD_OUT_PAPER_TABLE.md — TMLR-ready table (held-out only, with CIs)

Output figures
--------------
plots/scatter_heldout_{family}.png — TIvar vs held-out human Spearman
plots/scatter_calib_{family}.png   — TIvar vs calibration Spearman (for comparison)
"""
from __future__ import annotations

import csv
import math
import random
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_OUT_DIR = (
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp43_frozen_tivar_heldout"
)
DEFAULT_PAPER_FIG_DIR = (
    REPO_ROOT / "paper_latex" / "TMLR_2026" / "figures" / "exp43_heldout"
)

PARTICIPANT_FILES = {
    "participant1": "participant1_data_correct_prompt.tsv",
    "participant2": "participant2_data_pass_1.tsv",
    "participant3": "participant3_data_pass_1.tsv",
    "participant4": "participant4_data_pass_1.tsv",
    "participant5": "participant5_data_pass_1.tsv",
}

# Each panel: display name, frozen TIvar CSV, EXP16 detail_rows.csv, judge_rows.csv
PANELS = [
    {
        "name": "GPT-5.3-Codex",
        "family_key": "codex",
        "color": "#1f77b4",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_codex_avg.csv",
        "detail_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "detail_rows.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median" / "judge_rows.csv",
    },
    {
        "name": "Claude Opus 4.7",
        "family_key": "claude_opus",
        "color": "#9467bd",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_claude_opus_avg.csv",
        "detail_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median" / "detail_rows.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median" / "judge_rows.csv",
    },
    {
        "name": "Qwen3-Coder-30B",
        "family_key": "qwen",
        "color": "#d62728",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_qwen_avg.csv",
        "detail_rows_csv": REPO_ROOT / "experiments" / "13_qwen_replication_exp16_exp19" / "results" / "exp16_qwen_r3_median" / "detail_rows.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "13_qwen_replication_exp16_exp19" / "results" / "exp16_qwen_r3_median" / "judge_rows.csv",
    },
    {
        "name": "LeanStral",
        "family_key": "leanstral",
        "color": "#2ca02c",
        "tivar_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_tivar_v3_all_models" / "judge_trust_vector_leanstral_avg.csv",
        "detail_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median" / "detail_rows.csv",
        "judge_rows_csv": REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median" / "judge_rows.csv",
    },
]

N_BOOTSTRAP = 2000
BOOTSTRAP_SEED = 42

# ---------------------------------------------------------------------------
# Math utilities
# ---------------------------------------------------------------------------

def _mean(v: Sequence[float]) -> float:
    vs = [x for x in v if math.isfinite(x)]
    return math.fsum(vs) / len(vs) if vs else float("nan")


def _std(v: Sequence[float]) -> float:
    vs = [x for x in v if math.isfinite(x)]
    if len(vs) < 2:
        return 0.0
    m = _mean(vs)
    return math.sqrt(sum((x - m) ** 2 for x in vs) / (len(vs) - 1))


def _rankdata(v: Sequence[float]) -> List[float]:
    DIGITS = 12
    indexed = sorted(enumerate(v), key=lambda t: round(t[1], DIGITS))
    ranks = [0.0] * len(v)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and round(indexed[j][1], DIGITS) == round(indexed[i][1], DIGITS):
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg
        i = j
    return ranks


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx < 1e-12 or dy < 1e-12:
        return float("nan")
    return num / (dx * dy)


def _spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return float("nan")
    return _pearson(_rankdata([p[0] for p in pairs]), _rankdata([p[1] for p in pairs]))


def bootstrap_ci(
    xs: List[float], ys: List[float], n: int = N_BOOTSTRAP, seed: int = BOOTSTRAP_SEED, alpha: float = 0.05
) -> Tuple[float, float]:
    """Bootstrap percentile CI for Spearman rho between xs and ys."""
    rng = random.Random(seed)
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3:
        return float("nan"), float("nan")
    rhos = []
    for _ in range(n):
        sample = [rng.choice(pairs) for _ in range(len(pairs))]
        sx = [p[0] for p in sample]
        sy = [p[1] for p in sample]
        rhos.append(_spearman(sx, sy))
    rhos_fin = sorted(r for r in rhos if math.isfinite(r))
    if len(rhos_fin) < 10:
        return float("nan"), float("nan")
    lo_idx = int(alpha / 2 * len(rhos_fin))
    hi_idx = int((1 - alpha / 2) * len(rhos_fin))
    return rhos_fin[lo_idx], rhos_fin[min(hi_idx, len(rhos_fin) - 1)]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_participant_labels(human_dir: Path) -> Tuple[Dict[str, float], Dict[str, Dict[str, float]]]:
    """
    Returns:
      mean_target: {item_key: mean score (normalized 0-1)}
      per_rater:   {rater: {item_key: score}}
    """
    by_item: Dict[str, Dict[str, float]] = defaultdict(dict)
    raters: List[str] = []
    for rater, fname in sorted(PARTICIPANT_FILES.items()):
        path = human_dir / fname
        if not path.exists():
            continue
        raters.append(rater)
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gold = str(row.get("gold_file", "")).strip()
                cand = str(row.get("candidate_file", "")).strip()
                score_text = str(row.get("human_score_0_5", "")).strip()
                if not score_text and ".lean " in cand:
                    head, tail = cand.rsplit(" ", 1)
                    try:
                        float(tail)
                        cand, score_text = head.strip(), tail.strip()
                    except ValueError:
                        pass
                try:
                    score = float(score_text) / 5.0
                except (TypeError, ValueError):
                    continue
                if not gold or not cand:
                    continue
                by_item[f"{gold}::{cand}"][rater] = score

    mean_target: Dict[str, float] = {}
    per_rater: Dict[str, Dict[str, float]] = {r: {} for r in raters}
    for ik, rmap in by_item.items():
        vals = [rmap[r] for r in raters if r in rmap]
        if vals:
            mean_target[ik] = _mean(vals)
        for r in raters:
            if r in rmap:
                per_rater[r][ik] = rmap[r]

    total_labels = sum(len(v) for v in per_rater.values())
    print(f"  Participant labels: {len(mean_target)} items, {total_labels} total labels, {len(raters)} raters")
    return mean_target, per_rater


def load_tivar(tivar_csv: Path) -> Dict[str, float]:
    """Load frozen TIvar v3 scores per judge_id."""
    out: Dict[str, float] = {}
    with tivar_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            jid = row["judge_id"]
            val = row.get("ti_var_v3", "")
            try:
                out[jid] = float(val)
            except ValueError:
                pass
    return out


def load_judge_item_scores(detail_rows_csv: Path) -> Dict[str, Dict[str, float]]:
    """Load per-judge item scores from detail_rows.csv (human_eval_union rows)."""
    out: Dict[str, Dict[str, float]] = defaultdict(dict)
    with detail_rows_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("row_type") != "human_eval_union":
                continue
            jid = row["judge_id"]
            ik = row["item_key"]
            if ik in out[jid]:
                continue
            try:
                out[jid][ik] = float(row.get("score_mean") or "nan")
            except ValueError:
                pass
    return dict(out)


def load_calib_human_spearman(judge_rows_csv: Path) -> Dict[str, Dict[str, float]]:
    """Load calibration-panel human Spearman (pass1, pass2, avg) from judge_rows.csv."""
    out: Dict[str, Dict[str, float]] = {}
    with judge_rows_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            jid = row["judge_id"]
            out[jid] = {
                "pass1": _safe_float(row.get("human_spearman_r_pass1", "")),
                "pass2": _safe_float(row.get("human_spearman_r_pass2", "")),
                "avg": _safe_float(row.get("human_spearman_r_avg", "")),
            }
    return out


def _safe_float(s: str) -> float:
    try:
        return float(s)
    except (ValueError, TypeError):
        return float("nan")


# ---------------------------------------------------------------------------
# Per-judge held-out human Spearman
# ---------------------------------------------------------------------------

def compute_heldout_human_spearman(
    judge_item_scores: Dict[str, Dict[str, float]],
    participant_mean: Dict[str, float],
) -> Dict[str, float]:
    """
    For each judge: Spearman correlation between judge item scores and
    participant mean on the overlapping items.
    """
    out: Dict[str, float] = {}
    for jid, scores in judge_item_scores.items():
        common = sorted(set(scores) & set(participant_mean))
        if len(common) < 5:
            continue
        xs = [scores[k] for k in common]
        ys = [participant_mean[k] for k in common]
        out[jid] = _spearman(xs, ys)
    return out


# ---------------------------------------------------------------------------
# Short label for scatter plot points
# ---------------------------------------------------------------------------

def short_label(judge_id: str) -> str:
    if judge_id == "editdist_e1":
        return "edit"
    if judge_id == "random_r1":
        return "rand"
    if "|BAD_STRINGY" in judge_id:
        return "BAD"
    if "|P1_BASELINE" in judge_id:
        return "P1"
    if "|P4_CHECKLIST" in judge_id:
        return "P4"
    if "|P8_STRICT_B" in judge_id:
        return "P8"
    if "gpt-4o-mini|" in judge_id:
        suffix = judge_id.split("|", 1)[1]
        return f"4o-{suffix[:4]}"
    return judge_id.split("|")[-1][:10]


# ---------------------------------------------------------------------------
# Scatter plot
# ---------------------------------------------------------------------------

def plot_scatter(
    rows: List[dict],
    title: str,
    xlabel: str,
    ylabel: str,
    rho: float,
    ci: Tuple[float, float],
    out_path: Path,
    color: str,
) -> None:
    fig, ax = plt.subplots(figsize=(5, 4.5))
    xs = [r["tivar"] for r in rows]
    ys = [r["human_spearman"] for r in rows]
    labels = [r["label"] for r in rows]

    ax.scatter(xs, ys, color=color, alpha=0.8, s=60, zorder=3)
    for x, y, lbl in zip(xs, ys, labels):
        ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(4, 3),
                    fontsize=7, alpha=0.8)

    # Trend line
    if len(xs) >= 2:
        m_x, m_y = sum(xs) / len(xs), sum(ys) / len(ys)
        den = sum((xi - m_x) ** 2 for xi in xs)
        if den > 1e-12:
            slope = sum((xi - m_x) * (yi - m_y) for xi, yi in zip(xs, ys)) / den
            intercept = m_y - slope * m_x
            x_line = [min(xs) - 0.02, max(xs) + 0.02]
            y_line = [slope * xi + intercept for xi in x_line]
            ax.plot(x_line, y_line, "--", color=color, alpha=0.4, linewidth=1)

    ci_str = f"[{ci[0]:.2f}, {ci[1]:.2f}]" if all(math.isfinite(c) for c in ci) else "—"
    ax.set_title(f"{title}\nρ = {rho:.3f}  95% CI {ci_str}", fontsize=10)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.axhline(0, color="gray", linewidth=0.5, alpha=0.4)
    ax.axvline(0, color="gray", linewidth=0.5, alpha=0.4)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="EXP43: Frozen TIvar vs held-out 343-label human Spearman")
    parser.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--paper-fig-dir", type=Path, default=DEFAULT_PAPER_FIG_DIR)
    parser.add_argument("--n-bootstrap", type=int, default=N_BOOTSTRAP)
    args = parser.parse_args()

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    print("Loading held-out participant labels...")
    participant_mean, participant_per_rater = load_participant_labels(args.human_dir)

    # Total label count
    total_labels = sum(
        sum(1 for v in rmap.values() if math.isfinite(v))
        for rmap in participant_per_rater.values()
    )
    n_pairs = len(participant_mean)
    print(f"  {n_pairs} pairs, ~{total_labels} labels")

    results: List[dict] = []

    for panel in PANELS:
        name = panel["name"]
        fkey = panel["family_key"]
        color = panel["color"]
        print(f"\nProcessing {name}...")

        if not panel["tivar_csv"].exists():
            print(f"  SKIP: TIvar CSV not found: {panel['tivar_csv']}")
            continue
        if not panel["detail_rows_csv"].exists():
            print(f"  SKIP: detail_rows.csv not found: {panel['detail_rows_csv']}")
            continue

        tivar = load_tivar(panel["tivar_csv"])
        judge_item_scores = load_judge_item_scores(panel["detail_rows_csv"])
        calib_spearman = load_calib_human_spearman(panel["judge_rows_csv"])
        heldout_spearman = compute_heldout_human_spearman(judge_item_scores, participant_mean)

        # Common judges: must have TIvar, held-out spearman, and calibration spearman
        common_judges = sorted(
            set(tivar) & set(heldout_spearman) & set(calib_spearman)
        )
        print(f"  {len(common_judges)} judges with all data: {common_judges}")

        if len(common_judges) < 3:
            print(f"  SKIP: too few judges")
            continue

        tivar_vals = [tivar[j] for j in common_judges]
        heldout_vals = [heldout_spearman[j] for j in common_judges]
        calib_avg_vals = [calib_spearman[j]["avg"] for j in common_judges]
        calib_pass1_vals = [calib_spearman[j]["pass1"] for j in common_judges]
        calib_pass2_vals = [calib_spearman[j]["pass2"] for j in common_judges]

        # Family-level Spearman: TIvar vs held-out
        rho_heldout = _spearman(tivar_vals, heldout_vals)
        ci_heldout = bootstrap_ci(tivar_vals, heldout_vals, n=args.n_bootstrap)

        # Family-level Spearman: TIvar vs calibration (for comparison)
        rho_calib_avg = _spearman(tivar_vals, calib_avg_vals)
        rho_calib_pass1 = _spearman(tivar_vals, calib_pass1_vals)
        rho_calib_pass2 = _spearman(tivar_vals, calib_pass2_vals)
        ci_calib_avg = bootstrap_ci(tivar_vals, calib_avg_vals, n=args.n_bootstrap)

        print(f"  TIvar vs held-out human Spearman: ρ = {rho_heldout:.3f}  95% CI [{ci_heldout[0]:.3f}, {ci_heldout[1]:.3f}]")
        print(f"  TIvar vs calib avg human Spearman: ρ = {rho_calib_avg:.3f}")
        print(f"  Held-out human Spearman per judge:")
        for j, tv, hv, cv in zip(common_judges, tivar_vals, heldout_vals, calib_avg_vals):
            print(f"    {j:50s}  TIvar={tv:.3f}  held-out={hv:.3f}  calib_avg={cv:.3f}")

        # Scatter: held-out
        scatter_rows = [
            {"tivar": tivar[j], "human_spearman": heldout_spearman[j], "label": short_label(j)}
            for j in common_judges
        ]
        plot_scatter(
            rows=scatter_rows,
            title=name,
            xlabel="TIvar (frozen, from EXP30)",
            ylabel="Human Spearman — held-out (participant 1–5)",
            rho=rho_heldout,
            ci=ci_heldout,
            out_path=plots_dir / f"scatter_heldout_{fkey}.png",
            color=color,
        )

        # Scatter: calibration avg (for comparison figure)
        scatter_rows_calib = [
            {"tivar": tivar[j], "human_spearman": calib_spearman[j]["avg"], "label": short_label(j)}
            for j in common_judges
        ]
        plot_scatter(
            rows=scatter_rows_calib,
            title=name,
            xlabel="TIvar (frozen, from EXP30)",
            ylabel="Human Spearman — calibration panel (avg)",
            rho=rho_calib_avg,
            ci=ci_calib_avg,
            out_path=plots_dir / f"scatter_calib_{fkey}.png",
            color=color,
        )

        results.append({
            "family": name,
            "family_key": fkey,
            "n_judges": len(common_judges),
            "n_heldout_items": min(
                len(set(judge_item_scores[j]) & set(participant_mean)) for j in common_judges
            ),
            "rho_heldout": rho_heldout,
            "ci_lo_heldout": ci_heldout[0],
            "ci_hi_heldout": ci_heldout[1],
            "rho_calib_avg": rho_calib_avg,
            "rho_calib_pass1": rho_calib_pass1,
            "rho_calib_pass2": rho_calib_pass2,
            "ci_lo_calib": ci_calib_avg[0],
            "ci_hi_calib": ci_calib_avg[1],
            "judges": ",".join(common_judges),
        })

    # Write CSV
    if results:
        with (out_dir / "heldout_summary.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)
        print("\nWrote heldout_summary.csv")

    # ---------------------------------------------------------------------------
    # Write tables
    # ---------------------------------------------------------------------------

    def _fmt(v: float, d: int = 3) -> str:
        return "—" if not math.isfinite(v) else f"{v:.{d}f}"

    def _flag(v: float, thresh: float = 0.70) -> str:
        return " **✓**" if math.isfinite(v) and v >= thresh else ""

    # --- HELD_OUT_TABLE.md ---
    lines = [
        "# EXP43 Frozen TIvar vs Held-Out Human Correlation",
        "",
        f"Held-out corpus: participant1–5 labels ({n_pairs} pairs, ~{total_labels} labels).  ",
        "TIvar (v3) taken frozen from EXP30 — never refit on participant data.  ",
        f"Bootstrap: {args.n_bootstrap} replicates, percentile 95% CI.",
        "",
        "---",
        "",
        "## Table 1 — Held-Out: TIvar vs Participant Human Spearman",
        "",
        "Metric: family-level Spearman(TIvar, judge-level human Spearman) on held-out corpus.",
        "",
        "| Family | n judges | n items | Held-out ρ | 95% CI | Calib avg ρ | Calib pass1 ρ | Calib pass2 ρ |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for r in results:
        ci_str = f"[{_fmt(r['ci_lo_heldout'])}, {_fmt(r['ci_hi_heldout'])}]"
        lines.append(
            f"| {r['family']} "
            f"| {r['n_judges']} "
            f"| {r['n_heldout_items']} "
            f"| {_fmt(r['rho_heldout'])}{_flag(r['rho_heldout'])} "
            f"| {ci_str} "
            f"| {_fmt(r['rho_calib_avg'])}{_flag(r['rho_calib_avg'])} "
            f"| {_fmt(r['rho_calib_pass1'])}{_flag(r['rho_calib_pass1'])} "
            f"| {_fmt(r['rho_calib_pass2'])}{_flag(r['rho_calib_pass2'])} |"
        )
    lines += [
        "",
        "**✓** = ρ ≥ 0.70.",
        "",
        "---",
        "",
        "## Interpretation",
        "",
        "- **Held-out ρ** is the primary TMLR claim: TIvar predicts which judge",
        "  configurations are more human-aligned, evaluated on labels collected",
        "  independently from the calibration panel.",
        "- **Calib ρ** (pass1/pass2/avg) is the within-panel validation result",
        "  already reported in the paper (Table in Section 4).",
        "- Agreement between held-out ρ and calib ρ demonstrates that the",
        "  TIvar ranking is not overfit to the calibration labels.",
        "- n judges ≈ 8 per family; CIs are wide by design — we report them",
        "  explicitly rather than suppressing the uncertainty.",
    ]
    (out_dir / "HELD_OUT_TABLE.md").write_text("\n".join(lines) + "\n")
    print("Wrote HELD_OUT_TABLE.md")

    # --- HELD_OUT_PAPER_TABLE.md (TMLR-ready) ---
    paper_lines = [
        "# EXP43 TMLR Paper Table: Frozen TIvar Held-Out Validation",
        "",
        r"Human target: mean of participant1–5 (343 labels, 60 overlapping items per judge).  ",
        r"TIvar frozen from EXP30; labels never seen during TIvar development.  ",
        "",
        "| Judge family | n | Held-out ρ (95% CI) | Calib ρ (avg) |",
        "| --- | ---: | --- | ---: |",
    ]
    for r in results:
        ci_lo, ci_hi = r["ci_lo_heldout"], r["ci_hi_heldout"]
        ci_str = (f"{_fmt(r['rho_heldout'])}{_flag(r['rho_heldout'])} "
                  f"[{_fmt(ci_lo)}, {_fmt(ci_hi)}]")
        paper_lines.append(
            f"| {r['family']} | {r['n_judges']} | {ci_str} | {_fmt(r['rho_calib_avg'])}{_flag(r['rho_calib_avg'])} |"
        )
    paper_lines += [
        "",
        "**✓** = ρ ≥ 0.70.",
        "",
        "**Held-out ρ**: Spearman between frozen TIvar and judge-level human Spearman",
        "on the held-out participant corpus. Calibration panel labels were never used.",
    ]
    (out_dir / "HELD_OUT_PAPER_TABLE.md").write_text("\n".join(paper_lines) + "\n")
    print("Wrote HELD_OUT_PAPER_TABLE.md")

    # Copy to paper figures
    paper_fig_dir: Path = args.paper_fig_dir
    paper_fig_dir.mkdir(parents=True, exist_ok=True)
    for f in plots_dir.glob("*.png"):
        shutil.copy2(f, paper_fig_dir / f.name)
    for fname in ["HELD_OUT_TABLE.md", "HELD_OUT_PAPER_TABLE.md", "heldout_summary.csv"]:
        src = out_dir / fname
        if src.exists():
            shutil.copy2(src, paper_fig_dir / fname)
    print(f"Copied outputs to {paper_fig_dir}")
    print("\nDone.")


if __name__ == "__main__":
    main()
