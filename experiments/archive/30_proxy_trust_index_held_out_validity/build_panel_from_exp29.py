#!/usr/bin/env python3
"""Build a validation panel from experiment 29's committed PTI-v0 outputs.

Joins the proxy and the criterion on ``judge_id``:

* ``results/properties/properties.json`` -> ``PTI_v0.value`` per judge (the
  label-free proxy ``PTI_p``);
* ``results/criterion/criterion.json`` -> the judge's agreement with the human
  panel under one label view (the criterion ``TI_m1``).

Reads committed artifacts only. No inference, no credentials, no writes outside
the chosen output path.

    python experiments/archive/30_proxy_trust_index_held_out_validity/build_panel_from_exp29.py \
        --view average --role primary --output panel_exp29_primary.json

Then feed the result to ``design_check.py --input``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXP29 = REPO_ROOT / "experiments" / "archive" / "29_proxy_validation" / "results"


def build(view: str, roles: set[str] | None) -> dict:
    criterion_path = EXP29 / "criterion" / "criterion.json"
    properties_path = EXP29 / "properties" / "properties.json"
    for path in (criterion_path, properties_path):
        if not path.exists():
            raise SystemExit(f"missing committed artifact: {path}")

    criterion = json.loads(criterion_path.read_text())
    properties = json.loads(properties_path.read_text())
    by_judge = {judge["judge_id"]: judge for judge in properties["judges"]}

    units: dict[str, dict] = {}
    dropped: list[str] = []
    for record in criterion["records"]:
        judge_id = record["judge_id"]
        if roles is not None and record.get("role") not in roles:
            continue
        proxy = by_judge.get(judge_id)
        if proxy is None:
            dropped.append(judge_id)
            continue
        views = record.get("views", {})
        if view not in views:
            raise SystemExit(
                f"view {view!r} not in {sorted(views)} for judge {judge_id}"
            )
        cell = views[view]
        units[judge_id] = {
            "pti": proxy["PTI_v0"]["value"],
            "ti": cell["value"],
            "group": record["family"],
            "role": record.get("role"),
            "pti_properties": proxy["PTI_v0"]["properties"],
            "ti_ci": [cell["bootstrap"]["ci_low"], cell["bootstrap"]["ci_high"]],
            "observed_count": cell.get("observed_count"),
        }

    if dropped:
        print(f"warning: no proxy row for {dropped}", file=sys.stderr)

    counts = [u["observed_count"] for u in units.values() if u["observed_count"]]
    return {
        "_source": "experiments/archive/29_proxy_validation/results",
        "_view": view,
        "_roles": sorted(roles) if roles else "all",
        "_metric_version": properties.get("metric_version"),
        "_protocol_version": criterion.get("protocol_version"),
        "_panel_manifest_fingerprint": criterion.get("panel_manifest_fingerprint"),
        "target_threshold": 0.70,
        "n_items_per_unit": max(counts) if counts else None,
        "units": units,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--view",
        default="average",
        help="label view to use as the criterion (average, strict, lenient)",
    )
    parser.add_argument(
        "--role",
        action="append",
        help="keep only judges with this role; repeatable. Default: keep all.",
    )
    parser.add_argument("--output", type=Path, help="write the panel JSON here")
    args = parser.parse_args(argv)

    panel = build(args.view, set(args.role) if args.role else None)
    text = json.dumps(panel, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        print(f"wrote {args.output} with {len(panel['units'])} units")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
