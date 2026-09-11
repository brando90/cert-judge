#!/usr/bin/env python3
"""Zero-spend design check for the ``PTI_p -> TI_m`` criterion-validity claim.

This CLI has no inference client and cannot load credentials.  It reads numbers
you already have and answers three questions, in the order that matters:

1.  **Ceiling.**  Given how much your raters agree with each other, what is the
    largest judge-human correlation anyone could observe?  If your acceptance
    threshold sits above that ceiling, no judge can reach it and the fix is
    more raters, not a better judge.

2.  **Resolving power.**  Given your panel size and items per unit, can the
    design tell a strong proxy from a useless one?  A correlation over a small
    panel whose criterion is noisily estimated is compatible with almost any
    true value, in either direction.

3.  **Criterion validity.**  Only if 1 and 2 permit it: does ``PTI_p`` actually
    predict ``TI_m``, across all four correlation definitions, under splits
    that hold out whole agent or judge families.

Run the design check on the submission's own published parameters::

    python experiments/30_pti_ti_criterion_validity/design_check.py --demo

Run the full validation on a panel of your own::

    python experiments/30_pti_ti_criterion_validity/design_check.py \
        --input panel.json --output report.json

Input schema
------------

.. code-block:: json

    {
      "target_threshold": 0.70,
      "n_items_per_unit": 75,
      "single_rater_reliability": 0.249,
      "n_raters": 5,
      "ratings": [[4, 3, 4], [1, 2, 1]],
      "units": {
        "codex-prompt1": {"pti": 0.71, "ti": 0.62, "group": "codex"},
        "opus-prompt1":  {"pti": 0.55, "ti": 0.48, "group": "opus"}
      }
    }

``ratings`` is a fully crossed items x raters matrix and is preferred over
``single_rater_reliability``/``n_raters`` when available, because it estimates
reliability by ICC rather than extrapolating.  ``group`` drives the held-out
splits; units without one fall back to their own name, which makes every split
a leave-one-unit-out fold.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.ti_validation import (  # noqa: E402
    MIN_TRUSTWORTHY_PANEL,
    VALIDATION_VERSION,
    CeilingReport,
    ValidationReport,
    ceiling_report,
    fisher_ci,
    leave_one_group_out,
    min_units_for_ci_width,
    pooled_leave_one_group_out,
    resolving_power,
    validate_pti,
    validate_pti_across_splits,
)

# Published design parameters of the CertJudge submission.  Every value here
# appears in the paper; none is inferred or simulated.
PAPER = {
    "inter_pass_spearman": 0.249,  # Appendix G.2, pass1 vs pass2, n = 75
    "n_items": 75,  # Section 5.1, aligned candidate-gold pairs
    "n_judges": 8,  # Appendix G.3, judge configurations per family
    "n_judges_expanded": 13,  # Appendix Figure 8, expanded panel
    "best_judge_human_avg": 0.480,  # Table 9
    "best_judge_human_pass1": 0.559,  # Table 9
    "new_pool_raters": 5,  # Section 6.1, held-out annotation pool
    "new_pool_pairs": 78,  # Section 6.1
}

RULE = "-" * 72


def _render(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _render(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _render(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_render(v) for v in value]
    return value


def _fmt(value: float | None, places: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{places}f}"


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------


def print_ceiling(report: CeilingReport) -> None:
    print(RULE)
    print("1. CEILING  what the labels allow, before any judge is run")
    print(RULE)
    print(f"  raters in pool                 {report.n_raters}")
    print(f"  single-rater reliability       {_fmt(report.single_rater_reliability)}")
    print(f"  reliability of averaged label  {_fmt(report.averaged_reliability)}")
    print(f"  ceiling, single rater          {_fmt(report.ceiling_single)}")
    print(f"  ceiling, averaged label        {_fmt(report.ceiling_averaged)}")
    if report.target_threshold is not None:
        print(f"  acceptance threshold           {_fmt(report.target_threshold, 2)}")
        if report.threshold_reachable:
            print("  verdict                        REACHABLE with this rater pool")
        else:
            print("  verdict                        ABOVE THE CEILING, unreachable")
            if report.raters_needed_for_threshold:
                print(
                    "  raters needed                  "
                    f"{report.raters_needed_for_threshold}"
                )


def print_power(
    n_units: int, n_items: int, *, spread: float | None = None
) -> None:
    print()
    print(RULE)
    print("2. RESOLVING POWER  can this design detect anything")
    print(RULE)
    print(f"  units on the panel             {n_units}")
    print(f"  items per unit                 {n_items}")
    for rho in (0.70, 0.50):
        interval = fisher_ci(rho, n_units)
        if interval is None:
            continue
        low, high = interval
        flag = "  <- includes zero" if low <= 0.0 <= high else ""
        print(
            f"  95% interval if rho = {rho:.2f}     "
            f"[{low:+.3f}, {high:+.3f}]  width {high - low:.3f}{flag}"
        )
    needed = min_units_for_ci_width(0.70, 0.5)
    if needed:
        print(f"  units for a 0.50-wide interval {needed}")
    if n_units < MIN_TRUSTWORTHY_PANEL:
        print(
            f"  verdict                        UNDERPOWERED "
            f"(floor is {MIN_TRUSTWORTHY_PANEL} units)"
        )
    else:
        print("  verdict                        panel size adequate")


def print_validation(report: ValidationReport) -> None:
    print()
    print(RULE)
    print(f"3. CRITERION VALIDITY  [{report.split_name}]")
    print(RULE)
    print(f"  units                          {len(report.units)}")
    print(f"  status                         {report.status}")
    overshoot = False
    for name, estimate in report.correlations.items():
        interval = (
            ""
            if estimate.ci_low is None
            else f"  [{estimate.ci_low:+.3f}, {estimate.ci_high:+.3f}]"
        )
        corrected = report.disattenuated.get(name)
        extra = "" if corrected is None else f"   disattenuated {corrected:+.3f}"
        if corrected is not None and corrected > 1.0:
            extra += " *"
            overshoot = True
        print(f"  {name:<22} {_fmt(estimate.value):>7}{interval}{extra}")
    if overshoot:
        print(
            "  * disattenuated above 1.0 is not a valid correlation: it means the "
            "reliability\n    estimate is too low for this panel. Report the raw "
            "value and fix the estimate."
        )
    print(f"  pairwise rank accuracy         {_fmt(report.pairwise_rank_accuracy)}")
    print(f"  top-k overlap                  {_fmt(report.top_k_overlap)}")
    print(f"  mean rank displacement         {_fmt(report.mean_rank_displacement)}")
    for note in report.power.notes:
        print(f"  ! {note}")


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------


def run_demo() -> dict[str, Any]:
    """Design check on the submission's published parameters."""
    print()
    print("PTI -> TI design check")
    print(f"metric version: {VALIDATION_VERSION}")
    print(
        "inputs: published parameters of the CertJudge submission "
        "(no simulated data)"
    )
    print()

    current = ceiling_report(
        single_rater_reliability=PAPER["inter_pass_spearman"],
        n_raters=1,
        target_threshold=0.70,
    )
    print("CURRENT LABELS  one annotator, two rubric passes")
    print_ceiling(current)

    print()
    print("NEW POOL  five independent reviewers")
    planned = ceiling_report(
        single_rater_reliability=PAPER["inter_pass_spearman"],
        n_raters=PAPER["new_pool_raters"],
        target_threshold=0.70,
    )
    print_ceiling(planned)

    print()
    print(
        f"  observed best judge            "
        f"{PAPER['best_judge_human_avg']:.3f} (avg) / "
        f"{PAPER['best_judge_human_pass1']:.3f} (pass1)"
    )
    print("  those judges already sit at the single-pass ceiling")

    print_power(PAPER["n_judges"], PAPER["n_items"])

    criterion_band = [0.45 + 0.109 * i / 7 for i in range(PAPER["n_judges"])]
    power = resolving_power(criterion_band, n_items_per_unit=PAPER["n_items"])
    print(f"  criterion spread               {_fmt(power.criterion_spread)}")
    print(f"  standard error per unit        {_fmt(power.criterion_se)}")
    print(f"  spread / error                 {_fmt(power.resolving_ratio, 2)}")
    print("  (spread and error are the same size: the ranking is mostly noise)")

    print()
    print(RULE)
    print("WHAT TO CHANGE")
    print(RULE)
    print(f"  raters    1 -> {planned.raters_needed_for_threshold}+ lifts the ceiling past 0.70")
    print(
        f"  units     {PAPER['n_judges']} -> {min_units_for_ci_width(0.70, 0.5)}"
        " narrows the interval to 0.50 wide"
    )
    print(f"  items     {PAPER['n_items']} -> 300 halves the per-unit error")
    print()

    return {
        "mode": "demo",
        "metric_version": VALIDATION_VERSION,
        "paper_parameters": PAPER,
        "ceiling_current": _render(current),
        "ceiling_new_pool": _render(planned),
        "power": _render(power),
    }


def run_panel(payload: dict[str, Any], *, resamples: int) -> dict[str, Any]:
    """Full criterion-validity check on a supplied panel."""
    units = payload.get("units") or {}
    if not units:
        raise SystemExit("input has no 'units' block; nothing to validate")

    pti = {name: spec["pti"] for name, spec in units.items() if "pti" in spec}
    ti = {name: spec.get("ti") for name, spec in units.items()}
    groups = {name: spec.get("group", name) for name, spec in units.items()}
    n_items = payload.get("n_items_per_unit")
    threshold = payload.get("target_threshold", 0.70)

    ceiling: CeilingReport | None = None
    if payload.get("ratings"):
        ceiling = ceiling_report(payload["ratings"], target_threshold=threshold)
    elif payload.get("single_rater_reliability") is not None:
        ceiling = ceiling_report(
            single_rater_reliability=payload["single_rater_reliability"],
            n_raters=payload.get("n_raters", 1),
            target_threshold=threshold,
        )

    print()
    print("PTI -> TI criterion validity")
    print(f"metric version: {VALIDATION_VERSION}")
    print()
    if ceiling is not None:
        print_ceiling(ceiling)
    else:
        print("1. CEILING  skipped: no rater agreement supplied")

    print_power(len(pti), n_items or 0)

    overall = validate_pti(
        pti,
        ti,
        split_name="all-units",
        n_items_per_unit=n_items,
        ceiling=ceiling,
        resamples=resamples,
    )
    print_validation(overall)

    split_payload: dict[str, Any] = {}
    distinct = {groups[name] for name in pti}
    if len(distinct) >= 2:
        splits = leave_one_group_out(sorted(pti), groups)
        results = validate_pti_across_splits(
            pti,
            ti,
            splits,
            n_items_per_unit=n_items,
            ceiling=ceiling,
            resamples=resamples,
        )
        print()
        print(RULE)
        print("HELD-OUT GROUPS  the split that matches the claim")
        print(RULE)
        weak_folds = 0
        for split_name, portions in results.items():
            train = portions.get("train")
            test = portions.get("test")
            train_value = _fmt(train.headline.value) if train and train.headline else "n/a"
            test_value = _fmt(test.headline.value) if test and test.headline else "n/a"
            test_status = test.status if test else "NO_TEST"
            if test_status != "COMPUTED":
                weak_folds += 1
            print(
                f"  {split_name:<28} train rho {train_value:>7}   "
                f"held-out rho {test_value:>7}   {test_status}"
            )
        print(
            "  train is a pipeline sanity check only; a negative value there "
            "means a bug"
        )
        if weak_folds:
            print(
                f"  {weak_folds} of {len(results)} held-out folds are too small to "
                "read on their own;\n  the pooled estimate below is the one to "
                "quote."
            )

        pooled = pooled_leave_one_group_out(
            pti,
            ti,
            groups,
            n_items_per_unit=n_items,
            resamples=resamples,
        )
        print()
        print(RULE)
        print("POOLED HELD-OUT  one estimate over every cross-validated prediction")
        print(RULE)
        print(f"  folds                          {pooled.n_folds}")
        print(f"  units predicted out of group   {len(pooled.units)}")
        if pooled.skipped_units:
            print(f"  skipped (degenerate fold)      {len(pooled.skipped_units)}")
        print(f"  status                         {pooled.status}")
        for name, estimate in pooled.correlations.items():
            interval = (
                ""
                if estimate.ci_low is None
                else f"  [{estimate.ci_low:+.3f}, {estimate.ci_high:+.3f}]"
            )
            print(f"  {name:<22} {_fmt(estimate.value):>7}{interval}")
        print(
            f"  pairwise rank accuracy         "
            f"{_fmt(pooled.pairwise_rank_accuracy)}"
        )
        print(
            "  every prediction comes from a calibration that never saw that "
            "unit's group"
        )
        split_payload = {
            name: {portion: _render(rep) for portion, rep in portions.items()}
            for name, portions in results.items()
        }
        split_payload["_pooled"] = _render(pooled)
    else:
        print()
        print("HELD-OUT GROUPS  skipped: fewer than two distinct groups")

    print()
    return {
        "mode": "panel",
        "metric_version": VALIDATION_VERSION,
        "ceiling": _render(ceiling) if ceiling else None,
        "overall": _render(overall),
        "held_out_groups": split_payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Zero-spend design and criterion-validity check for PTI -> TI_m. "
            "Performs no inference and loads no credentials."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--demo",
        action="store_true",
        help="run the design check on the submission's published parameters",
    )
    source.add_argument(
        "--input", type=Path, help="JSON panel file (see module docstring)"
    )
    parser.add_argument("--output", type=Path, help="write the JSON report here")
    parser.add_argument(
        "--resamples",
        type=int,
        default=10_000,
        help="bootstrap resamples for confidence intervals (default: 10000)",
    )
    args = parser.parse_args(argv)

    if args.demo:
        report = run_demo()
    else:
        report = run_panel(
            json.loads(args.input.read_text()), resamples=args.resamples
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
