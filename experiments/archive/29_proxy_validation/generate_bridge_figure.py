#!/usr/bin/env python3
"""Generate the judge-level PTI-v0 bridge figures and source-data artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[3]
DODGE_STEP = 0.026
EXPERIMENT_ROOT = Path(__file__).resolve().parent
DEFAULT_PROPERTIES = EXPERIMENT_ROOT / "results" / "properties" / "properties.json"
DEFAULT_CRITERION = EXPERIMENT_ROOT / "results" / "criterion" / "criterion.json"
DEFAULT_BRIDGE = EXPERIMENT_ROOT / "results" / "bridge" / "bridge_pti_v0.json"
DEFAULT_OUT_DIR = EXPERIMENT_ROOT / "results" / "figures"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_rows(
    properties: dict[str, Any],
    criterion: dict[str, Any],
    bridge: dict[str, Any],
) -> list[dict[str, Any]]:
    property_by_id = {row["judge_id"]: row for row in properties["judges"]}
    criterion_by_id = {row["judge_id"]: row for row in criterion["records"]}
    rows: list[dict[str, Any]] = []
    for source in bridge["source_rows"]:
        judge_id = source["judge_id"]
        property_row = property_by_id[judge_id]
        criterion_view = criterion_by_id[judge_id]["views"]["average"]
        pti = property_row["PTI_v0"]
        pti_bootstrap = pti["bootstrap"]
        criterion_bootstrap = criterion_view["bootstrap"]
        if source["pti"] != pti["value"]:
            raise ValueError(f"bridge/property PTI mismatch for {judge_id}")
        if source["ti_m1"] != criterion_view["value"]:
            raise ValueError(f"bridge/criterion TI_m1 mismatch for {judge_id}")
        rows.append(
            {
                "judge_id": judge_id,
                "role": source["role"],
                "family": source["family"],
                "pti_v0": pti["value"],
                "pti_ci_low": pti_bootstrap["ci_low"],
                "pti_ci_high": pti_bootstrap["ci_high"],
                "ti_m1": criterion_view["value"],
                "ti_m1_ci_low": criterion_bootstrap["ci_low"],
                "ti_m1_ci_high": criterion_bootstrap["ci_high"],
                "kendall_tau_b_item_level": criterion_view["kendall_tau_b"],
                "property_coverage_min": min(
                    value["coverage"] for value in property_row["properties"].values()
                ),
            }
        )
    return rows


def _short_label(judge_id: str) -> str:
    labels = {
        "gpt-5.6-terra|P8_STRICT_B": "Terra–P8",
        "gpt-5.6-terra|P4_CHECKLIST": "Terra–P4",
        "gpt-5.6-terra|P1_BASELINE": "Terra–P1",
        "claude-sonnet-5|P8_STRICT_B": "Sonnet–P8",
        "claude-sonnet-5|P4_CHECKLIST": "Sonnet–P4",
        "gpt-5.6-terra|BAD_STRINGY": "String control",
        "editdist_e1": "Edit distance",
        "random_r1": "Random",
    }
    return labels[judge_id]


def _style(row: dict[str, Any]) -> tuple[str, str, str]:
    if row["role"] == "control":
        return "#666666", "X", "white"
    if row["family"] == "gpt-5.6-terra":
        return "#1464A5", "o", "#1464A5"
    return "#D97904", "s", "#D97904"


def _annotation_offset(judge_id: str, pooled: bool) -> tuple[float, float, str]:
    primary = {
        "gpt-5.6-terra|P8_STRICT_B": (0.025, -0.055, "left"),
        "gpt-5.6-terra|P4_CHECKLIST": (0.025, 0.085, "left"),
        "gpt-5.6-terra|P1_BASELINE": (0.025, 0.035, "left"),
        "claude-sonnet-5|P8_STRICT_B": (-0.025, -0.065, "right"),
        "claude-sonnet-5|P4_CHECKLIST": (0.025, -0.080, "left"),
    }
    controls = {
        "gpt-5.6-terra|BAD_STRINGY": (0.025, 0.050, "left"),
        "editdist_e1": (0.025, -0.145, "left"),
        "random_r1": (0.025, -0.130, "left"),
    }
    if pooled and judge_id in controls:
        return controls[judge_id]
    return primary.get(judge_id, (0.02, 0.02, "left"))


def _draw(
    rows: list[dict[str, Any]],
    analysis: dict[str, Any],
    *,
    pooled: bool,
    output_stem: Path,
) -> None:
    selected = rows if pooled else [row for row in rows if row["role"] == "primary"]
    # Judges whose PTI values are byte-identical (e.g. several exact zeros) would
    # otherwise be drawn on top of each other and their vertical intervals would
    # be unattributable.  Their markers and vertical intervals are offset
    # horizontally by multiples of DODGE_STEP; the plotted PTI interval, the
    # annotation coordinates, and the source data keep the exact abscissa.
    groups: dict[float, list[int]] = {}
    for index, row in enumerate(selected):
        groups.setdefault(round(float(row["pti_v0"]), 9), []).append(index)
    offsets: dict[int, float] = {}
    for members in groups.values():
        for position, index in enumerate(members):
            offsets[index] = (
                (position - (len(members) - 1) / 2.0) * DODGE_STEP
                if len(members) > 1
                else 0.0
            )
    left_margin = min(offsets.values()) if offsets else 0.0
    fig, ax = plt.subplots(figsize=(7.1, 5.0), constrained_layout=True)
    for index, row in enumerate(selected):
        color, marker, face = _style(row)
        x = float(row["pti_v0"])
        y = float(row["ti_m1"])
        x_draw = x + offsets[index]
        if float(row["pti_ci_high"]) > float(row["pti_ci_low"]):
            ax.errorbar(
                x,
                y,
                xerr=[[x - float(row["pti_ci_low"])], [float(row["pti_ci_high"]) - x]],
                fmt="none",
                ecolor=color,
                elinewidth=1.1,
                capsize=2.5,
                alpha=0.92,
                zorder=2,
            )
        ax.errorbar(
            x_draw,
            y,
            yerr=[
                [y - float(row["ti_m1_ci_low"])],
                [float(row["ti_m1_ci_high"]) - y],
            ],
            fmt=marker,
            markersize=7.5,
            markeredgewidth=1.5,
            markeredgecolor=color,
            markerfacecolor=face,
            color=color,
            ecolor=color,
            elinewidth=1.1,
            capsize=2.5,
            alpha=0.92,
            zorder=3,
        )
        dx, dy, alignment = _annotation_offset(row["judge_id"], pooled)
        group = groups[round(x, 9)]
        arrow = None
        if len(group) > 1:
            # Labels of a dodged cluster are stacked to the right of the whole
            # cluster and tied to their marker by a thin leader line.
            cluster_right = max(offsets[member] for member in group)
            dx = (cluster_right - offsets[index]) + 0.03
            alignment = "left"
            arrow = {"arrowstyle": "-", "color": "#9A9A9A", "linewidth": 0.6, "shrinkA": 0, "shrinkB": 4}
        ax.annotate(
            _short_label(row["judge_id"]),
            (x_draw, y),
            xytext=(x_draw + dx, y + dy),
            textcoords="data",
            ha=alignment,
            va="center",
            fontsize=8.3,
            color="#222222",
            arrowprops=arrow,
            zorder=4,
        )

    ax.axhline(0.0, color="#B8B8B8", linewidth=0.8, linestyle=":", zorder=0)
    ax.axvline(0.0, color="#B8B8B8", linewidth=0.8, linestyle=":", zorder=0)
    ax.set_xlim(min(-0.02, left_margin - 0.03), 1.0)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylim(-1.0, 1.0)
    if any(value != 0.0 for value in offsets.values()):
        ax.text(
            0.01,
            0.015,
            "Judges with identical PTI values are offset horizontally by multiples of "
            f"{DODGE_STEP} for legibility;\ntheir exact abscissa is the dotted vertical line.",
            transform=ax.transAxes,
            fontsize=7.2,
            color="#444444",
            va="bottom",
            ha="left",
        )
    ax.set_xlabel(r"Judge-level $\mathrm{PTI}_{\mathrm{v0}}$  [0, 1]")
    ax.set_ylabel(r"Human criterion $\mathrm{TI}_{m_1}$ (Spearman)  [-1, 1]")
    population = "Primaries + controls (secondary)" if pooled else "Primary judges"
    valid = analysis["bootstrap"]["valid_replicates"]
    requested = analysis["bootstrap"]["requested_replicates"]
    ax.set_title(
        "PTI-v0 outer bridge (judge is the unit)\n"
        f"{population}: "
        rf"$\rho_s={analysis['spearman']:.3f}$, "
        f"95% bootstrap CI [{analysis['bootstrap']['ci_low']:.3f}, "
        f"{analysis['bootstrap']['ci_high']:.3f}], "
        f"n={analysis['judge_count']}; valid={valid:,}/{requested:,}",
        loc="left",
        fontsize=11,
        pad=10,
    )
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#1464A5",
            markeredgecolor="#1464A5",
            label="Terra primary",
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            color="none",
            markerfacecolor="#D97904",
            markeredgecolor="#D97904",
            label="Sonnet primary",
        ),
    ]
    if pooled:
        handles.append(
            Line2D(
                [0],
                [0],
                marker="X",
                color="none",
                markerfacecolor="white",
                markeredgecolor="#666666",
                label="Control",
            )
        )
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=8.5)
    ax.grid(True, color="#E6E6E6", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.savefig(
        output_stem.with_suffix(".pdf"),
        bbox_inches="tight",
        metadata={"CreationDate": None, "ModDate": None},
    )
    fig.savefig(output_stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--properties", type=Path, default=DEFAULT_PROPERTIES)
    parser.add_argument("--criterion", type=Path, default=DEFAULT_CRITERION)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    properties = _read_json(args.properties)
    criterion = _read_json(args.criterion)
    bridge = _read_json(args.bridge)
    if bridge["variant"] != "PTI_v0" or bridge["status"] != "COMPUTED":
        raise ValueError("headline figure requires a computed PTI_v0 bridge")
    if bridge["identity_line"] is not False or bridge["level_mae"] is not None:
        raise ValueError("bridge artifact violates the frozen scale-semantics contract")
    if bridge["properties_sha256"] != _sha256(args.properties):
        raise ValueError("bridge is not bound to the supplied property artifact")
    if bridge["criterion_sha256"] != _sha256(args.criterion):
        raise ValueError("bridge is not bound to the supplied criterion artifact")

    rows = _build_rows(properties, criterion, bridge)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "outer_bridge_source_data.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "schema_version": "PTI_v0_outer_bridge_figure_v1",
        "metric_version": "PTI_v0",
        "prebridge_commit": bridge["prebridge_commit"],
        "properties_sha256": bridge["properties_sha256"],
        "criterion_sha256": bridge["criterion_sha256"],
        "source_rows": rows,
        "analyses": bridge["analyses"],
        "figure_contract": {
            "unit": "judge configuration",
            "identity_line": False,
            "level_mae": None,
            "primary_population": "primaries",
            "pooled_population": "primaries and controls; secondary",
            "uncertainty": "95% artifact-cluster PTI and paired-cluster TI_m1 intervals",
        },
        "generator": str(Path(__file__).resolve().relative_to(REPO_ROOT)),
    }
    (args.out_dir / "outer_bridge_source_data.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    _draw(
        rows,
        bridge["analyses"]["primaries"],
        pooled=False,
        output_stem=args.out_dir / "outer_bridge_primaries",
    )
    _draw(
        rows,
        bridge["analyses"]["pooled_with_controls"],
        pooled=True,
        output_stem=args.out_dir / "outer_bridge_pooled_secondary",
    )
    print(f"wrote source data and bridge figures under {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
