#!/usr/bin/env python3
"""TLDR: Freeze the judge panel and its train/val/test split over judge models into results/panel.json before any
score exists: units, families, selectors and substitutes, prompt fingerprints, cell kinds and repeat counts;
optionally check every selector against a saved gateway registry body. Zero model calls."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402
import legacy                                                 # noqa: E402


def prompt_fingerprints() -> dict[str, str]:
    out = {}
    try:
        _, prompts, _ = e39.x100_modules()
    except FileNotFoundError as exc:
        print(f"warning: {exc}; VeriBench prompt fingerprints unavailable")
        prompts = None
    for key, spec in e39.PROMPTS.items():
        if spec["family"] == "legacy":
            out[key] = legacy.fingerprint(spec["rubric"])
        elif prompts is not None:
            out[key] = prompts.rubric_fingerprint(spec["rubric"])
        else:
            out[key] = None
    return out


def check_registry(units: list[dict], registry_path: Path | None) -> dict:
    """Which pre-registered selector (or substitute) exists in the saved registry body, with its prices."""
    if registry_path is None:
        return {"checked": False}
    body = e39.read_json(registry_path)
    models = body.get("models", body)
    resolved = {}
    for unit in units:
        if unit["kind"] != "llm":
            continue
        chosen, source = None, None
        for selector in unit["selectors"]:
            if selector in models:
                chosen, source = selector, "pre-registered"
                break
        if chosen is None:
            for selector in unit["substitutes"]:
                if selector in models:
                    chosen, source = selector, "substitute"
                    break
        entry = models.get(chosen) or {}
        resolved[unit["model_key"]] = {"selector": chosen, "source": source,
                                       "costs_per_million_token": entry.get("costs_per_million_token"),
                                       "provider_name": entry.get("provider_name"),
                                       "fallback_models": (entry.get("provider_properties") or {}).get("fallback_models")}
    return {"checked": True, "registry_sha256": e39.sha_file(registry_path), "resolved": resolved}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", type=Path, default=None, help="saved gateway /registry body (private); optional")
    ap.add_argument("--out", type=Path, default=e39.RESULTS / "panel.json")
    args = ap.parse_args()
    units = e39.panel_units()
    counts = {}
    for unit in units:
        counts.setdefault(unit["split"], {"llm": 0, "control": 0})[unit["kind"]] += 1
    panel = {
        "written_utc": e39.stamp(), "experiment": e39.EXPERIMENT, "seed": e39.SEED,
        "e39_sha256": e39.sha_file(Path(e39.__file__)),
        "split_unit": "judge model (every prompt of a model shares its split); non-LLM controls are train-only",
        "criterion_items": {"splits": list(e39.CRITERION_SPLITS), "source": "experiment 75 task split (seed 20260903) via experiment 100 items.jsonl"},
        "units": units, "counts": counts,
        "models": e39.MODELS, "substitutes": e39.SUBSTITUTES, "prompts": e39.PROMPTS,
        "prompts_by_model": {k: list(v) for k, v in e39.PROMPTS_BY_MODEL.items()},
        "prompt_fingerprints": prompt_fingerprints(), "kinds": e39.KINDS, "cap_usd": e39.CAP_USD,
        "registry": check_registry(units, args.registry),
    }
    e39.write_json(args.out, panel)
    print(json.dumps({"units": len(units), "counts": counts, "out": str(args.out)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
