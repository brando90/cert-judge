#!/usr/bin/env python3
"""Freeze the exact historical 12-configuration pool and distinguish cache availability."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
E39 = REPO / "experiments" / "39_label_free_proxy_index_train_val_test_over_judge_families"
OUT = ROOT / "results"
RUN_ID = "cj-e47-v5-10-08-2026-a1"
POOL = (
    "opus55x|D0", "opus55x|H0", "opus55x|H2",
    "qwen36|D0", "qwen36|H0", "qwen36|H1", "qwen36|H2", "qwen36|R4",
    "t2_qwen|D0", "t2_qwen|H2", "t2_sonnet5|D0", "t2_sonnet5|H2",
)
CACHE = {"opus55x|H0", "opus55x|H2"}
FAMILY = {"opus55x": "Anthropic", "qwen36": "Alibaba", "t2_qwen": "Alibaba", "t2_sonnet5": "Anthropic"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    selectors = json.loads((E39 / "results/selectors.json").read_text())
    rows, errors = [], []
    for config in POOL:
        model, prompt = config.split("|", 1)
        path = E39 / "results/harvest" / f"{model}__{prompt}.json"
        if not path.exists():
            errors.append({"config": config, "error": "MISSING_E39_HARVEST"})
            continue
        h = json.loads(path.read_text())
        if h.get("config") != config:
            errors.append({"config": config, "error": "CONFIG_MISMATCH", "actual": h.get("config")})
        if h.get("family") != model:
            errors.append({"config": config, "error": "FAMILY_KEY_MISMATCH", "actual": h.get("family")})
        selector = h.get("selector")
        selected_override = selectors.get(model, {}).get("selector")
        if selected_override is not None and selected_override != selector:
            errors.append({"config": config, "error": "SELECTOR_OVERRIDE_MISMATCH"})
        rows.append({"config": config, "base_model": model, "provider_family": FAMILY[model],
                     "prompt": prompt, "selector": selector, "selector_source": h.get("selector_source"),
                     "harness": h.get("harness"), "kwargs": h.get("kwargs"), "scale": h.get("scale"),
                     "historical_harvest_sha256": sha(path), "historical_cells": h.get("n_cells"),
                     "historical_status_counts": h.get("status_counts"), "cached_v5_member": config in CACHE,
                     "e47_state": "CACHED_VERIFIED" if config in CACHE else "DECLARED_MISSING"})
    report = {"run_id": RUN_ID, "pool": rows, "declared_configurations": len(POOL),
              "cached_verified_configurations": len(CACHE), "missing_declared_configurations": len(POOL) - len(CACHE),
              "base_models": sorted({r["base_model"] for r in rows}),
              "provider_families": sorted({r["provider_family"] for r in rows}), "errors": errors,
              "rules": ["Historical selector and harness settings are copied from experiment-39 harvest receipts.",
                        "Cached v5 members are not a two-model ensemble or any rebuilt fold-specific judge.",
                        "All unavailable declared conditions remain in the later admission manifest; none is silently substituted."]}
    OUT.mkdir(exist_ok=True)
    (OUT / "historical_primary_pool_inventory.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if errors or len(rows) != len(POOL):
        raise SystemExit("historical-pool inventory failed")
    print(json.dumps({"declared": len(POOL), "cached": len(CACHE), "missing": len(POOL) - len(CACHE)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
