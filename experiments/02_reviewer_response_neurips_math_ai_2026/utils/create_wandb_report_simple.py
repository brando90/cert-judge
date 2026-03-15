#!/usr/bin/env python3
"""
Create a clean executive-summary W&B Report (VeriBench E3 style).
One leaderboard table + 2 key charts. Fast to scan.

Usage:
    python utils/create_wandb_report_simple.py
"""
import wandb_workspaces.reports.v2 as wr

ENTITY  = "brando-su"
PROJECT = "trusting-formal-judge"

# All experiment run IDs
RUN_IDS = {
    "exp1":        "5vkx8ltc",
    "exp2":        "y8khbzo2",
    "exp4":        "yibfdiz7",
    "exp3_mini":   "e29grtu5",
    "exp3_4o":     "dhs45cu1",
}
exp_run_ids = list(RUN_IDS.values())

def runset(*run_ids, name="Runs"):
    f = " or ".join(f'ID == "{rid}"' for rid in run_ids)
    return wr.Runset(entity=ENTITY, project=PROJECT, name=name, filters=f)

report = wr.Report(
    entity=ENTITY,
    project=PROJECT,
    title="Certifying LLM Judges — Leaderboard",
    description=(
        "5 experiments certifying LLM judges for Lean 4 theorem scoring. "
        "Metric: combined_score = identity_mean × (weak_mono% / 100) — perfect judge = 1.00. "
        "Best: Exp4 out-of-domain (gpt-4o-mini) — combined_score = 1.000, CERTIFIED ✅."
    ),
    blocks=[
        wr.H1(text="Certifying LLM Judges — Leaderboard"),
        wr.P(text=(
            "**5 experiments** certifying LLM judges via Identity + Monotonicity properties on Lean 4 theorems. "
            "Judge model: **gpt-4o-mini**. "
            "Certified = identity_mean > 0.90 **and** Spearman ρ < −0.50 **and** weak_mono > 80%."
        )),
        wr.HorizontalRule(),

        wr.H2(text="Results (sorted by combined score)"),
        wr.MarkdownBlock(text=(
            "| Experiment | Setup | Identity Mean | Spearman ρ | Weak Mono% | Combined Score | Certified |\n"
            "|---|---|---|---|---|---|---|\n"
            "| **Exp4** Out-of-Domain | 15 OOD theorems | **1.000** | −0.707 | **100%** | **1.000** | ✅ |\n"
            "| **Exp2** Monotonicity (in-domain) | 20 VeriBench × 5 levels | 0.942 | **−0.862** | **80%** | 0.754 | partial |\n"
            "| **Exp1** Hard Identity | 30 VeriBench × 4 variants | **0.920** | — | — | — | ✅ property |\n"
            "| **Exp3** gpt-4o | 20 VeriBench pairs | 0.959 | −0.867 | 70% | 0.671 | ❌ |\n"
            "| **Exp3** gpt-4o-mini | 20 VeriBench pairs | 0.917 | −0.888 | 70% | 0.642 | ❌ |\n"
        )),
        wr.HorizontalRule(),

        wr.H2(text="Charts"),
        wr.PanelGrid(
            runsets=[runset(*exp_run_ids, name="All Experiments")],
            panels=[
                wr.BarPlot(
                    title="Combined Score (identity × weak_mono/100) — higher is better",
                    metrics=[wr.SummaryMetric("combined_score")],
                    orientation="h",
                ),
                wr.BarPlot(
                    title="Weak Monotonicity % — threshold: 80%",
                    metrics=[wr.SummaryMetric("weak_mono_pct")],
                    orientation="h",
                ),
                wr.BarPlot(
                    title="Identity Mean — threshold: 0.90",
                    metrics=[wr.SummaryMetric("identity_mean")],
                    orientation="h",
                ),
                wr.ScatterPlot(
                    title="Identity Mean vs |Spearman ρ| — certified = top-right",
                    x=wr.SummaryMetric("identity_mean"),
                    y=wr.SummaryMetric("mono_spearman_abs"),
                    regression=False,
                ),
            ],
        ),
        wr.HorizontalRule(),

        wr.H2(text="Key Finding"),
        wr.CalloutBlock(text=(
            "The judge detects **semantic changes invisible to edit distance**: "
            "L1 degradation (Levenshtein = 0.002) drops score by **0.143**. "
            "Pearson r(edit_distance, judge_score) = **−0.054** (p=0.56) — "
            "no surface-similarity bias. Spearman ρ = **−0.862** (p<0.001) on the bug ladder. "
            "Cohen's d L0→L1 = **1.20** (large effect). "
            "The protocol is **discriminative** — same models that CERTIFY on simpler OOD theorems "
            "**FAIL** on VeriBench-complexity theorems."
        )),
        wr.HorizontalRule(),

        wr.P(text=(
            f"Full detailed report: "
            f"[Certifying LLM Judges — Full Report](https://wandb.ai/{ENTITY}/{PROJECT}/reports/"
            f"Certifying-LLM-Judges:-Full-Experimental-Report-(NeurIPS-Math-AI-2026)--VmlldzoxNjIwOTA0Mw==) · "
            f"[All runs](https://wandb.ai/{ENTITY}/{PROJECT})"
        )),
    ],
)

print("Saving simple W&B report...")
report.save()
print(f"\n{'='*62}")
print(f"  Simple Report URL: {report.url}")
print(f"  All reports: https://wandb.ai/{ENTITY}/{PROJECT}/reportlist")
print(f"{'='*62}\n")
