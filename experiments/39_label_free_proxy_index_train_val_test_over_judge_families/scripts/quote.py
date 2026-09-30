#!/usr/bin/env python3
"""TLDR: Exact call count and cost quote for experiment 39 from the rendered cells: a worst-case admission
bound per configuration (experiment 100's reservation formula: every output token billed at max_tokens) and an
expected cost from per-call means measured in experiment 100's receipts, recorded for Brando (no automatic cap: PROTOCOL.md Amendment 1).
Zero model calls; prices come from a saved registry body or the pre-filled fallback table."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402

# USD per million tokens (input, output), Vals gateway registry as read on 09-28-2026 by experiment 103, and
# experiment 100's configs. Overridden by --registry when a saved registry body is available.
FALLBACK_PRICES = {
    "sol6h": (4.0, 20.0), "sonnet5m": (3.0, 15.0), "luna6h": (0.1, 0.5), "gem31h": (2.0, 12.0),
    "opus55x": (15.0, 75.0), "qwen36": (0.6, 3.6),
    "t2_luna": (0.1, 0.5), "t2_sonnet5": (3.0, 15.0), "t2_qwen": (0.6, 3.6),
}  # Sonnet 5 and Opus 5.5 prices are not committed anywhere; these two are assumptions (their expected cost uses measured means)
# Mean cost per COMPLETE call measured in experiment 100's receipts (same prompts, same models):
# p5_test_H2_sol_high $0.0118 (n=126); ab_R4_sonnet5 $0.0154 (n=135); p5_test_H2_opus55_max $0.1064 (n=126),
# p3_i3_H2_opus55_max $0.1307 (n=116), ab_H0_opus $0.1658 (n=135); ab_D0_sol $0.0088 (n=126).
MEASURED_PER_CALL = {"sol6h": 0.012, "sonnet5m": 0.016, "opus55x": 0.13}
# Output tokens (answer plus reasoning) assumed for models without a measured mean, from the same receipts:
# Sol ~500, Opus ~4,000. Conservative middle value.
ASSUMED_OUTPUT_TOKENS = 1500
# Agent judges (Terminus2): the task is re-sent on every turn; assume 4 turns of the full prompt plus the harness's own
# system prompt, and 2,000 output tokens in total. No measured mean exists for a Terminus2 judge.
AGENT_TURNS = 4
AGENT_OUTPUT_TOKENS = 2000
AGENT_OVERHEAD_TOKENS = 3000          # Terminus2 system prompt and tool chatter per turn


def prices(panel: dict, registry: Path | None) -> dict[str, tuple[float, float]]:
    out = dict(FALLBACK_PRICES)
    resolved = (panel.get("registry") or {}).get("resolved") or {}
    if registry is not None:
        body = e39.read_json(registry)
        models = body.get("models", body)
        for key, info in resolved.items():
            entry = models.get(info.get("selector") or "")
            cost = (entry or {}).get("costs_per_million_token")
            if cost:
                out[key] = (float(cost["input"]), float(cost["output"]))
    else:
        for key, info in resolved.items():
            cost = info.get("costs_per_million_token")
            if cost:
                out[key] = (float(cost["input"]), float(cost["output"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=e39.RESULTS / "panel.json")
    ap.add_argument("--registry", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=e39.RESULTS / "QUOTE.json")
    args = ap.parse_args()
    panel = e39.read_json(args.panel)
    price = prices(panel, args.registry)
    rows, total_calls, total_worst, total_expected = [], 0, 0.0, 0.0
    for unit in panel["units"]:
        if unit["kind"] != "llm":
            continue
        path = e39.RESULTS / "cells" / (unit["config"].replace("|", "__") + ".json")
        if not path.exists():
            rows.append({"config": unit["config"], "missing": True})
            continue
        blob = e39.read_json(path)
        in_rate, out_rate = price[unit["model_key"]]
        calls = blob["n_calls"]
        bytes_total = blob["prompt_bytes_total"]
        worst = ((bytes_total + 1024 * calls) * in_rate * 1.25 + calls * unit["max_tokens"] * out_rate) / 1e6
        if unit["pack_flavor"] == "agent":
            per_turn = bytes_total / 3.5 + calls * AGENT_OVERHEAD_TOKENS
            expected = (AGENT_TURNS * per_turn * in_rate + calls * AGENT_OUTPUT_TOKENS * out_rate) / 1e6
            basis = f"agent judge: {AGENT_TURNS} turns x (bytes/3.5 + {AGENT_OVERHEAD_TOKENS}) input tokens + {AGENT_OUTPUT_TOKENS} output tokens per cell (assumption, no measured mean)"
        elif unit["model_key"] in MEASURED_PER_CALL:
            expected = calls * MEASURED_PER_CALL[unit["model_key"]]
            basis = "measured per-call mean (experiment 100 receipts)"
        else:
            expected = ((bytes_total / 3.5) * in_rate + calls * ASSUMED_OUTPUT_TOKENS * out_rate) / 1e6
            basis = f"bytes/3.5 input tokens + {ASSUMED_OUTPUT_TOKENS} output tokens per call"
        rows.append({"config": unit["config"], "split": unit["split"], "calls": calls, "deterministic": blob["n_deterministic"],
                     "unmeasured": blob["n_unmeasured"], "prompt_bytes": bytes_total, "usd_per_million": [in_rate, out_rate],
                     "worst_case_usd": round(worst, 2), "expected_usd": round(expected, 2), "expected_basis": basis})
        total_calls += calls
        total_worst += worst
        total_expected += expected
    by_split, by_model = {}, {}
    for r in rows:
        if r.get("missing"):
            continue
        for bucket, key in ((by_split, r["split"]), (by_model, r["config"].split("|")[0])):
            b = bucket.setdefault(key, {"calls": 0, "expected_usd": 0.0, "worst_case_usd": 0.0})
            b["calls"] += r["calls"]
            b["expected_usd"] = round(b["expected_usd"] + r["expected_usd"], 2)
            b["worst_case_usd"] = round(b["worst_case_usd"] + r["worst_case_usd"], 2)
    quote = {"written_utc": e39.stamp(), "cap_usd": e39.CAP_USD, "total_calls": total_calls,
             "expected_usd": round(total_expected, 2), "worst_case_usd": round(total_worst, 2),
             "prices_usd_per_million": price,
             "by_split": by_split, "by_model": by_model, "rows": rows,
             "note": ("worst case bills max_tokens output on every call (experiment 100's reservation rule); "
                      "the expected figure is the planning estimate; Vals-reported charges are the record")}
    e39.write_json(args.out, quote)
    print(json.dumps({k: quote[k] for k in ("total_calls", "expected_usd", "worst_case_usd", "by_split", "by_model")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
