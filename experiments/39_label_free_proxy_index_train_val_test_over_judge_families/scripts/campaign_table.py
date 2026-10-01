#!/usr/bin/env python3
"""TLDR: Rewrite the live judge-campaign table in results.md from the merged receipts under results/harvest/ (measured /
missing counts, recovered cells, Vals-reported charges and the selector per configuration) plus the smoke and recovery
totals from private/judge, between the `campaign-table` markers; zero model calls. Run after every merge."""
from __future__ import annotations

import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402

BEGIN, END = "<!-- campaign-table:begin -->", "<!-- campaign-table:end -->"


def main() -> int:
    panel = {u["config"]: u for u in e39.read_json(e39.RESULTS / "panel.json")["units"] if u["kind"] == "llm"}
    merged = {}
    for path in sorted(glob.glob(str(e39.RESULTS / "harvest" / "*.json"))):
        blob = json.loads(Path(path).read_text())
        if blob.get("kind") == "llm":
            merged[blob["config"]] = blob
    smoke_total = 0.0
    for path in glob.glob(str(e39.PRIVATE / "judge" / "harvests" / "*_smoke.json")):
        smoke_total += json.loads(Path(path).read_text()).get("charges_usd") or 0.0
    rows = ["| Configuration | Split | Selector | Cells | Measured | Deterministic | Missing (class) | Recovered | Charges (USD) |",
            "|---|---|---|---:|---:|---:|---|---:|---:|"]
    totals = {"measured": 0, "cells": 0, "charges": 0.0}
    for config in sorted(panel, key=lambda c: ({"train": 0, "val": 1, "test": 2}[panel[c]["split"]], c)):
        unit = panel[config]
        blob = merged.get(config)
        if not blob:
            rows.append(f"| `{config}` | {unit['split']} | — | — | — | — | not merged yet | — | — |")
            continue
        counts = blob["status_counts"]
        missing = {k: v for k, v in counts.items() if k not in ("measured", "deterministic")}
        rows.append(f"| `{config}` | {blob['split']} | `{blob['selector']}` | {blob['n_cells']} | {counts.get('measured', 0)} | "
                    f"{counts.get('deterministic', 0)} | {', '.join(f'{k} {v}' for k, v in sorted(missing.items())) or '0'} | "
                    f"{blob.get('recovered_cells', 0)} | {blob['charges_usd']:.2f} |")
        totals["measured"] += counts.get("measured", 0)
        totals["cells"] += blob["n_cells"]
        totals["charges"] += blob["charges_usd"]
    stamp = datetime.now(timezone.utc).strftime("%m-%d-%Y %H:%M UTC")
    table = "\n".join([BEGIN, f"_Merged configurations as of {stamp}: {len(merged)}/{len(panel)}; measured cells {totals['measured']:,} of "
                       f"{totals['cells']:,} merged cells; Vals-reported charges ${totals['charges']:,.2f} on merged main + recovery runs, "
                       f"plus ${smoke_total:,.2f} on the 56 smoke cells._", ""] + rows + [END])
    path = e39.E / "results.md"
    text = path.read_text()
    if BEGIN in text and END in text:
        text = text[:text.index(BEGIN)] + table + text[text.index(END) + len(END):]
    else:
        anchor = "## Deviations and open questions for Brando"
        text = text.replace(anchor, "## Judge campaign (live, per configuration)\n\n" + table + "\n\n" + anchor)
    path.write_text(text)
    print(json.dumps({"merged": len(merged), "measured": totals["measured"], "cells": totals["cells"],
                      "charges_usd": round(totals["charges"], 2), "smoke_usd": round(smoke_total, 2)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
