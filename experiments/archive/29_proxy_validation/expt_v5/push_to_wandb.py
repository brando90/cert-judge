#!/usr/bin/env python3
"""Log PTI-v0 v5 artifacts and publish the permanent W&B Report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import wandb
import wandb_workspaces.reports.v2 as wr

ENTITY = "brando-su"
PROJECT = "cert-judge-pti-v0"
REPO_ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = EXPERIMENT_ROOT / "results"
DEFAULT_KEY_FILE = Path("/Users/brandomiranda/keys/brandos_wandb_key.txt")
DEFAULT_REPORT_URL = (
    "https://wandb.ai/brando-su/cert-judge-pti-v0/reports/"
    "Experiment-29-%E2%80%94-PTI-v0-v5-outer-bridge--VmlldzoxNzgyMzE2MA=="
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _judge_run_id(judge_id: str) -> str:
    return "pti29v5" + hashlib.sha256(judge_id.encode("utf-8")).hexdigest()[:12]


def _runset(run_ids: list[str], name: str) -> wr.Runset:
    filters = " or ".join(f'ID == "{run_id}"' for run_id in run_ids)
    return wr.Runset(entity=ENTITY, project=PROJECT, name=name, filters=filters)


def _markdown_property_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Judge | Role | P_eq | P_bm | P_ms | P_eqalpha | PTI_v0 | TI_m1 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['judge_id']}` | {row['role']} | {row['P_eq']:.4f} | "
            f"{row['P_bm']:.4f} | {row['P_ms']:.4f} | "
            f"{row['P_eqalpha']:.4f} | {row['pti_v0']:.4f} | "
            f"{row['ti_m1']:.4f} |"
        )
    return "\n".join(lines)


def main() -> int:
    global ENTITY, PROJECT
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--entity", default=ENTITY)
    parser.add_argument("--project", default=PROJECT)
    parser.add_argument(
        "--report-url",
        default=DEFAULT_REPORT_URL,
        help="Existing report to update in place; defaults to the canonical report.",
    )
    publication_mode = parser.add_mutually_exclusive_group()
    publication_mode.add_argument(
        "--report-only",
        dest="report_only",
        action="store_true",
        help="Update only the report (the safe default).",
    )
    publication_mode.add_argument(
        "--publish-runs-and-artifact",
        dest="report_only",
        action="store_false",
        help="Explicitly log run summaries and a new artifact version before publishing.",
    )
    parser.set_defaults(report_only=True)
    args = parser.parse_args()
    ENTITY = args.entity
    PROJECT = args.project

    key = args.key_file.read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError(f"empty W&B key file: {args.key_file}")
    os.environ["WANDB_SILENT"] = "true"
    os.environ.setdefault("WANDB_DIR", "/tmp/cert-judge-pti-v0-wandb")
    Path(os.environ["WANDB_DIR"]).mkdir(parents=True, exist_ok=True)
    wandb.login(key=key, relogin=True)

    report = None
    if args.report_url:
        report = wr.Report.from_url(args.report_url)
        if report.entity != ENTITY or report.project != PROJECT:
            raise ValueError(
                "existing report does not belong to the requested W&B entity/project"
            )

    properties = _read_json(RESULTS / "properties" / "properties.json")
    criterion = _read_json(RESULTS / "criterion" / "criterion.json")
    bridge = _read_json(RESULTS / "bridge" / "bridge_pti_v0.json")
    bridge_three = _read_json(RESULTS / "bridge" / "bridge_eq_bm_ms.json")
    sesoi = _read_json(RESULTS / "sesoi" / "sesoi_simulation.json")
    auth = _read_json(RESULTS / "cli_auth_status.json")
    criterion_by_id = {row["judge_id"]: row for row in criterion["records"]}

    rows: list[dict[str, Any]] = []
    judge_run_ids: list[str] = []
    judge_run_urls: list[str] = []
    for property_row in properties["judges"]:
        judge_id = property_row["judge_id"]
        criterion_view = criterion_by_id[judge_id]["views"]["average"]
        row = {
            "judge_id": judge_id,
            "role": property_row["role"],
            "family": property_row["family"],
            "P_eq": property_row["properties"]["P_eq"]["value"],
            "P_bm": property_row["properties"]["P_bm"]["value"],
            "P_ms": property_row["properties"]["P_ms"]["value"],
            "P_eqalpha": property_row["properties"]["P_eqalpha"]["value"],
            "pti_eq_bm_ms": property_row["PTI_eq_bm_ms"]["value"],
            "pti_v0": property_row["PTI_v0"]["value"],
            "ti_m1": criterion_view["value"],
            "ti_m1_kendall_tau_b": criterion_view["kendall_tau_b"],
            "coverage": min(
                value["coverage"] for value in property_row["properties"].values()
            ),
        }
        rows.append(row)
        run_id = _judge_run_id(judge_id)
        judge_run_ids.append(run_id)
        judge_run_urls.append(f"https://wandb.ai/{ENTITY}/{PROJECT}/runs/{run_id}")
        if args.report_only:
            continue
        with wandb.init(
            entity=ENTITY,
            project=PROJECT,
            id=run_id,
            name=judge_id.replace("|", " · "),
            group="experiment-29-v5",
            job_type="judge-result",
            resume="allow",
            mode="online",
            save_code=False,
            config={
                "experiment": 29,
                "protocol_version": "PTI_v0_cli_protocol_v5",
                "metric_version": "PTI_v0",
                "judge_id": judge_id,
                "role": property_row["role"],
                "family": property_row["family"],
                "pre_result_commit": "395efdc00584cad32f6e9a525a8dbd9b201ff2a7",
                "prebridge_commit": bridge["prebridge_commit"],
                "provider_api_spend_usd": 0.0,
                "model_provenance_note": (
                    "Claude runs requested/scored with claude-sonnet-5 and disclose "
                    "auxiliary claude-haiku-4-5 telemetry; Codex runs disclose "
                    "gpt-5.6-terra as the explicit CLI argument because Codex JSONL "
                    "has no served-model field. Exact v4 models were NOT_RUN."
                ),
            },
        ) as run:
            run.log(
                {key: value for key, value in row.items() if isinstance(value, float)}
            )
            run.summary["provider_api_spend_usd"] = 0.0
            run.summary["cells_complete"] = 4728
            run.summary["cells_expected"] = 4728

    summary_run_id = "pti29v5summary"
    summary_run_url = f"https://wandb.ai/{ENTITY}/{PROJECT}/runs/{summary_run_id}"
    primary = bridge["analyses"]["primaries"]
    pooled = bridge["analyses"]["pooled_with_controls"]
    metrics = {
        "bridge_primary_spearman": primary["spearman"],
        "bridge_primary_kendall_tau_b": primary["kendall_tau_b"],
        "bridge_primary_ci_low": primary["bootstrap"]["ci_low"],
        "bridge_primary_ci_high": primary["bootstrap"]["ci_high"],
        "bridge_primary_valid_bootstrap": primary["bootstrap"]["valid_replicates"],
        "bridge_pooled_spearman": pooled["spearman"],
        "bridge_pooled_ci_low": pooled["bootstrap"]["ci_low"],
        "bridge_pooled_ci_high": pooled["bootstrap"]["ci_high"],
        "bridge_three_property_spearman": bridge_three["analyses"]["primaries"][
            "spearman"
        ],
        "complete_cli_tasks": 774,
        "complete_score_cells": 4728,
        "score_records": 14184,
        "provider_api_spend_usd": 0.0,
        "sesoi_positive_decision_power_at_rho_0_5": next(
            row["positive_decision_rate"]
            for row in sesoi["rows"]
            if row["rho_target"] == 0.5
        ),
    }
    if not args.report_only:
        with wandb.init(
            entity=ENTITY,
            project=PROJECT,
            id=summary_run_id,
            name="Experiment 29 · PTI-v0 v5 summary",
            group="experiment-29-v5",
            job_type="experiment-summary",
            resume="allow",
            mode="online",
            save_code=False,
            config={
                "experiment": 29,
                "protocol_version": "PTI_v0_cli_protocol_v5",
                "metric_version": "PTI_v0",
                "config_fingerprint": (
                    "735bd5951d4e6f8e9bf5f0d5e374028e1e46d92077b64584a7f89ff30981be9e"
                ),
                "prebridge_commit": bridge["prebridge_commit"],
                "bootstrap_iterations": 10000,
                "sesoi_spearman": 0.5,
                "provider_api_spend_usd": 0.0,
                "exact_v4_status": "NOT_RUN",
                "actual_scoring_models": ["gpt-5.6-terra", "claude-sonnet-5"],
                "claude_auxiliary_telemetry": ["claude-haiku-4-5"],
                "subscription_auth": auth,
            },
        ) as summary_run:
            summary_run.log(metrics)
            table_columns = list(rows[0])
            summary_run.log(
                {
                    "judge_results": wandb.Table(
                        columns=table_columns,
                        data=[
                            [row[column] for column in table_columns] for row in rows
                        ],
                    ),
                    "outer_bridge_primaries": wandb.Image(
                        str(RESULTS / "figures" / "outer_bridge_primaries.png")
                    ),
                    "outer_bridge_pooled_secondary": wandb.Image(
                        str(RESULTS / "figures" / "outer_bridge_pooled_secondary.png")
                    ),
                    "sesoi_simulation": wandb.Table(
                        columns=list(sesoi["rows"][0]),
                        data=[list(row.values()) for row in sesoi["rows"]],
                    ),
                }
            )
            artifact = wandb.Artifact(
                "experiment-29-pti-v0-v5-results",
                type="experiment-results",
                description=(
                    "Complete machine-readable PTI-v0 v5 property, criterion, bridge, "
                    "SESOI, score, and figure-source artifacts."
                ),
                metadata={
                    "prebridge_commit": bridge["prebridge_commit"],
                    "exact_v4_status": "NOT_RUN",
                    "provider_api_spend_usd": 0.0,
                },
            )
            artifact_paths = [
                RESULTS / "scores.json",
                RESULTS / "properties" / "properties.json",
                RESULTS / "properties" / "property_table.csv",
                RESULTS / "criterion" / "criterion.json",
                RESULTS / "criterion" / "criterion.csv",
                RESULTS / "bridge" / "bridge_pti_v0.json",
                RESULTS / "bridge" / "bridge_eq_bm_ms.json",
                RESULTS / "sesoi" / "sesoi_simulation.json",
                RESULTS / "sesoi" / "sesoi_simulation.csv",
                RESULTS / "figures" / "outer_bridge_source_data.csv",
                RESULTS / "figures" / "outer_bridge_source_data.json",
                EXPERIMENT_ROOT / "frozen_config.json",
                EXPERIMENT_ROOT / "PROTOCOL.md",
                EXPERIMENT_ROOT / "RESULTS_QA.md",
            ]
            for path in artifact_paths:
                artifact.add_file(
                    str(path), name=str(path.relative_to(EXPERIMENT_ROOT))
                )
            summary_run.log_artifact(artifact)

    runset = _runset(judge_run_ids, "Eight frozen judge configurations")
    summary_runset = _runset([summary_run_id], "Experiment summary")
    report_title = "Experiment 29 — PTI-v0 v5 outer bridge"
    report_description = (
        "Complete subscription-CLI PTI-v0 v5 run: 774 tasks, 4,728 cells, "
        "five primary judges, three controls, and a pre-specified judge-level "
        "validation bridge without a held-out generalization claim."
    )
    report_blocks = [
        wr.TableOfContents(),
        wr.H1(text="Experiment 29 — PTI-v0 v5 outer bridge"),
        wr.CalloutBlock(
            text=(
                "**TL;DR** — The run completed 774/774 CLI tasks and 4,728/4,728 "
                "cells at **$0 provider-API spend**. Four of five primary PTIs are "
                "exactly zero under the frozen zero-first geometric mean. The "
                f"primaries-only bridge is **Spearman {primary['spearman']:.3f}** "
                f"(95% judge-bootstrap CI [{primary['bootstrap']['ci_low']:.3f}, "
                f"{primary['bootstrap']['ci_high']:.3f}], n=5): below the 0.5 "
                "SESOI and inconclusive about zero. Passing PTI is not proof of "
                "trustworthiness."
            )
        ),
        wr.HorizontalRule(),
        wr.H2(text="Completion and provenance"),
        wr.MarkdownBlock(
            text=(
                "| Field | Value |\n|---|---|\n"
                "| Accepted CLI tasks | 774 / 774 |\n"
                "| Complete score cells | 4,728 / 4,728 |\n"
                "| Score records | 14,184 |\n"
                "| Property/criterion coverage | 100% |\n"
                "| Provider API spend | $0 |\n"
                "| Exact v4 models | NOT RUN |\n"
                "| Actual scoring models | `gpt-5.6-terra`; requested/scoring "
                "`claude-sonnet-5` |\n"
                "| Codex model telemetry | `gpt-5.6-terra` requested by explicit "
                "CLI argument; no served-model field |\n"
                "| Claude auxiliary telemetry | `claude-haiku-4-5` on all 258 "
                "accepted Claude CLI tasks |\n"
                f"| Pre-bridge commit | `{bridge['prebridge_commit']}` |"
            )
        ),
        wr.H2(text="Property and human-criterion table"),
        wr.MarkdownBlock(text=_markdown_property_table(rows)),
        wr.H2(text="Pre-specified judge-level validation bridge"),
        wr.MarkdownBlock(
            text=(
                f"Primary Spearman: **{primary['spearman']:.6f}**; Kendall tau-b: "
                f"**{primary['kendall_tau_b']:.6f}**; 95% bootstrap CI "
                f"**[{primary['bootstrap']['ci_low']:.6f}, "
                f"{primary['bootstrap']['ci_high']:.6f}]** with "
                f"{primary['bootstrap']['valid_replicates']:,}/10,000 valid "
                "replicates. The interval includes zero and its upper endpoint is "
                "below the frozen rho=0.5 SESOI.\n\n"
                f"Pooled controls (secondary): Spearman **{pooled['spearman']:.6f}**, "
                f"95% CI **[{pooled['bootstrap']['ci_low']:.6f}, "
                f"{pooled['bootstrap']['ci_high']:.6f}]**, n=8. The three-property "
                "sensitivity has the same rank association because it retains the "
                "same tie pattern. Both family-leave-one-out analyses are "
                "`NOT_COMPUTABLE` at this panel size."
            )
        ),
        wr.PanelGrid(
            runsets=[runset],
            panels=[
                wr.ScatterPlot(
                    title="PTI-v0 vs TI_m1 (judge-level; all roles)",
                    x=wr.SummaryMetric("pti_v0"),
                    y=wr.SummaryMetric("ti_m1"),
                    regression=False,
                ),
                wr.BarPlot(
                    title="PTI-v0 by frozen judge configuration",
                    metrics=[wr.SummaryMetric("pti_v0")],
                    orientation="h",
                ),
                wr.BarPlot(
                    title="TI_m1 by frozen judge configuration",
                    metrics=[wr.SummaryMetric("ti_m1")],
                    orientation="h",
                ),
            ],
        ),
        wr.PanelGrid(
            runsets=[summary_runset],
            panels=[
                wr.MediaBrowser(
                    title="Audited outer bridge figures",
                    media_keys=[
                        "outer_bridge_primaries",
                        "outer_bridge_pooled_secondary",
                    ],
                    mode="gallery",
                )
            ],
        ),
        wr.H2(text="SESOI simulation and interpretation"),
        wr.MarkdownBlock(
            text=(
                "At the frozen true Spearman SESOI of 0.5, the full positive decision "
                "rule (point estimate >=0.5 and lower bootstrap bound >0) fires in "
                f"**{metrics['sesoi_positive_decision_power_at_rho_0_5']:.1%}** of "
                "10,000 simulations. The five-judge design is therefore low-power; "
                "the observed result is below-SESOI and statistically inconclusive, "
                "not evidence of a positive bridge. No deployment threshold or "
                "human-validations-saved claim was frozen."
            )
        ),
        wr.H2(text="Limitations and audit status"),
        wr.MarkdownBlock(
            text=(
                "- Exact v4 model IDs were inaccessible through the approved "
                "ChatGPT-backed CLI; these are versioned v5 results.\n"
                "- Unrelated cases share a deterministic batch context, though no "
                "batch contains two cells for the same typed artifact.\n"
                "- Every accepted Claude transcript records a small auxiliary Haiku helper "
                "alongside Sonnet. The scoring output is attributed to Sonnet, but "
                "Sonnet-only execution is not claimed.\n"
                "- Three-stage Mega-QA independently reproduced all frozen numbers; "
                "the current report includes its provenance corrections.\n"
                "- The PTI axis and TI_m1 axis are not a shared calibrated level "
                "scale; no identity line or level MAE is used."
            )
        ),
        wr.H2(text="Reproduction"),
        wr.MarkdownBlock(
            text=(
                "```bash\n"
                "python experiments/archive/29_proxy_validation/run_pti_v0_cli.py status\n"
                "python experiments/archive/04_veribench_validation/run_pti_v0.py "
                "compute-bridge --variant PTI_v0 --prebridge-commit "
                f"{bridge['prebridge_commit']} --bootstrap-iters 10000 --seed 0 --no-api\n"
                "python experiments/archive/29_proxy_validation/generate_bridge_figure.py\n"
                "```"
            )
        ),
    ]
    if report is not None:
        report.title = report_title
        report.description = report_description
        report.blocks = report_blocks
    else:
        report = wr.Report(
            entity=ENTITY,
            project=PROJECT,
            title=report_title,
            description=report_description,
            blocks=report_blocks,
        )
    report.save()
    updated_at = datetime.now(timezone.utc).isoformat()
    output = RESULTS / "wandb_report.json"
    previous_receipt = _read_json(output) if output.exists() else {}
    payload = {
        "created_at_utc": previous_receipt.get("created_at_utc", updated_at),
        "entity": ENTITY,
        "project": PROJECT,
        "report_url": report.url,
        "summary_run_id": summary_run_id,
        "summary_run_url": summary_run_url,
        "judge_run_ids": judge_run_ids,
        "judge_run_urls": judge_run_urls,
        "publication_mode": "report-only" if args.report_only else "full",
        "updated_at_utc": updated_at,
    }
    if "release_closeout_audit" in previous_receipt:
        payload["release_closeout_audit"] = previous_receipt["release_closeout_audit"]
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Report URL: {report.url}")
    print(f"wrote {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
