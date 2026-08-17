#!/usr/bin/env python3
"""
Exp27: TI_2' scatter demo on real (already-collected) cert-judge data.

Reuses results already on disk from the ICLR-2027 / workshop submission runs
-- no judge inference, no LLM calls, no spend:
  - experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/
      detail_rows.csv   per-item, per-judge repeat scores (already computed)
      summary.json      per-judge audited human_spearman_r_* for cross-check
  - experiments/26_human_label_dataset_audit/results/aligned_panel_n75.tsv
      the audited 75-row human-label source of truth; 72 rows join the
      panel above (3 rows are `missing_gold`, per that audit -- they drop
      out of the join naturally, no special-casing needed here)

For each of a few representative judge configurations (spanning the range
TI_2' should discriminate -- a real judge with decent human agreement, a real
judge that passes the behavioral screen but barely correlates with humans,
and the random-judge anchor) this builds the item-level (human, judge) score
pairs, computes TI_2' via cert_judge.ti2prime_plot, renders the scatter, and
cross-checks the freshly computed Spearman correlation against exp06's
already-audited `human_spearman_r_avg` column (should match to float noise --
same formula, same data, independent recomputation).
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.ti2prime_plot import compute_ti2prime, plot_ti2prime_scatter  # noqa: E402

EXP06_DIR = REPO_ROOT / "experiments" / "06_cert_index_vs_human_judge_corr_and_low_var" / "full_run" / "mean"
AUDIT_TSV = REPO_ROOT / "experiments" / "26_human_label_dataset_audit" / "results" / "aligned_panel_n75.tsv"
AUDIT_MD = REPO_ROOT / "experiments" / "26_human_label_dataset_audit" / "results" / "AUDIT.md"
OUT_DIR = Path(__file__).resolve().parent / "results"

LABEL_VIEW = "avg"  # paper's headline label view (revision memo Sec 5: "headline = avg")

# One real judge with decent human agreement, one real judge that passes the
# behavioral screen (high cert_index) but barely correlates with humans -- the
# paper's own cautionary story (revision memo Sec 2.1-2.2) -- and the
# uniform-random anchor. Not all 9 judges: this is a demo of the plotting
# code, not a rerun of the full panel.
JUDGES = [
    "gpt-5.3-codex|P4_CHECKLIST",
    "claude-sonnet-4-20250514|P8_STRICT_B",
    "random_r1",
]


def _load_human_labels(path: Path) -> dict:
    """item_key ("{gold_file}::{candidate_file}") -> {pass1,pass2,avg} normalized to [0,1]."""
    labels = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            item_key = f"{row['gold_file']}::{row['candidate_file']}"
            labels[item_key] = {
                "pass1": float(row["pass1"]) / 5.0,
                "pass2": float(row["pass2"]) / 5.0,
                "avg": float(row["avg"]) / 5.0,
            }
    return labels


def _load_judge_detail(path: Path) -> dict:
    """judge_id -> {item_key: (score_mean, repeat_scores)}, human_eval_union rows only."""
    by_judge: dict = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["row_type"] != "human_eval_union":
                continue
            by_judge.setdefault(row["judge_id"], {})[row["item_key"]] = (
                float(row["score_mean"]),
                json.loads(row["repeat_scores"]),
            )
    return by_judge


def _load_audited_human_spearman(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        summary = json.load(f)
    return {r["judge_id"]: r[f"human_spearman_r_{LABEL_VIEW}"] for r in summary["judge_rows"]}


def _spearman_brown_ceiling(inter_pass_r: float) -> float:
    """
    Spearman-Brown prophecy formula for the reliability of a 2-pass average,
    then sqrt() for the attenuation ceiling on any correlation against that
    average (per certjudge-revision-memo.md, "Report correlations against the
    estimated ceiling, not against 1.0"). Assumes parallel forms; the two
    passes here are different rubric-strictness views rather than pure
    replications, and with a single rater the ceiling conflates rubric
    sensitivity with rater noise -- both point the same way, so this is a
    lower bound on what's achievable, not an exact value.
    """
    reliability = 2.0 * inter_pass_r / (1.0 + inter_pass_r)
    return math.sqrt(reliability)


def _load_interpass_reliability_numbers(audit_md_path: Path) -> dict:
    """
    Both numbers currently on record for pass1-vs-pass2 Spearman on the 72
    aligned items, read live from the audit rather than hardcoded -- AUDIT.md
    itself flags these as a MISMATCH (main.tex's stated 0.249 vs a newer
    recomputation at 0.280), unresolved as of this run. Report both rather
    than silently picking one.
    """
    text = audit_md_path.read_text(encoding="utf-8")
    m = re.search(
        r"\|\s*pass1 vs pass2 spearman\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|", text
    )
    if not m:
        raise ValueError(f"could not find the pass1-vs-pass2 spearman row in {audit_md_path}")
    return {"main_tex_cited": float(m.group(1)), "audit_recomputed": float(m.group(2))}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    human_labels = _load_human_labels(AUDIT_TSV)
    judge_detail = _load_judge_detail(EXP06_DIR / "detail_rows.csv")
    audited_rho = _load_audited_human_spearman(EXP06_DIR / "summary.json")

    interpass = _load_interpass_reliability_numbers(AUDIT_MD)
    ceiling_paper = _spearman_brown_ceiling(interpass["main_tex_cited"])
    ceiling_audit = _spearman_brown_ceiling(interpass["audit_recomputed"])
    print(
        f"Attenuation ceiling context: inter-pass Spearman = {interpass['main_tex_cited']} "
        f"(main.tex-cited) vs {interpass['audit_recomputed']} (AUDIT.md recompute) -- "
        f"AUDIT.md flags this pair as a MISMATCH, unresolved as of this run. "
        f"Spearman-Brown ceiling: {ceiling_paper:.3f} (paper-cited) / {ceiling_audit:.3f} "
        f"(recomputed). Reporting judge rho as a fraction of BOTH below, not picking one.\n"
    )

    report = []
    for judge_id in JUDGES:
        items = judge_detail[judge_id]
        item_keys = sorted(k for k in items if k in human_labels)
        assert len(item_keys) >= 50, f"suspiciously few joined items for {judge_id}: {len(item_keys)}"

        judge_scores = [items[k][0] for k in item_keys]
        human_scores = [human_labels[k][LABEL_VIEW] for k in item_keys]
        repeat_scores_by_item = {k: items[k][1] for k in item_keys}

        result = compute_ti2prime(judge_scores, human_scores, repeat_scores_by_item)

        safe_name = judge_id.replace("|", "_").replace("/", "_")
        out_path = OUT_DIR / f"ti2prime_scatter_{safe_name}"
        plot_ti2prime_scatter(
            judge_scores,
            human_scores,
            repeat_scores_by_item,
            judge_label=judge_id,
            x_label=f"Human score (avg of 2 rubric passes, {LABEL_VIEW} label view, /5 -> [0,1])",
            y_label="Judge score (repeat-mean, [0,1])",
            out=out_path,
        )

        rho_delta = abs(result.validity_raw - audited_rho[judge_id])
        frac_ceiling_paper = result.validity_raw / ceiling_paper if ceiling_paper > 0 else float("nan")
        frac_ceiling_audit = result.validity_raw / ceiling_audit if ceiling_audit > 0 else float("nan")
        report.append(
            {
                "judge_id": judge_id,
                "n_items": result.n_items,
                "corr_raw_spearman": result.validity_raw,
                "corr_clipped": result.validity,
                "stability_1_minus_std": result.stability,
                "ti2prime": result.vs_score,
                "audited_human_spearman_r_avg": audited_rho[judge_id],
                "cross_check_abs_diff": rho_delta,
                "fraction_of_attenuation_ceiling_paper_cited": frac_ceiling_paper,
                "fraction_of_attenuation_ceiling_audit_recomputed": frac_ceiling_audit,
                "figure_png": f"{out_path}.png",
            }
        )
        std_shown = 1.0 - result.stability
        print(
            f"{judge_id}: TI_2' = ({result.validity:.2f} * (1-{std_shown:.2f}))**0.5 = {result.vs_score:.3f}"
            f"  [cross-check |rho diff|={rho_delta:.6f}]"
            f"  [rho/ceiling: {frac_ceiling_paper*100:.0f}% (paper) / {frac_ceiling_audit*100:.0f}% (audit)]"
        )

    (OUT_DIR / "ti2prime_demo_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {len(report)} figures + summary to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
