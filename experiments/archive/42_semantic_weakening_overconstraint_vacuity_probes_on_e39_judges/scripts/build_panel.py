#!/usr/bin/env python3
"""TLDR: Write results/panel.json for experiment 42: experiment 39's 56 LLM judge configurations and 4 deterministic
controls exactly as its frozen scripts/e39.py defines them (its split labels are kept for the index analysis), plus
the prompt fingerprints. Zero model calls."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e42                                                    # noqa: E402
import legacy                                                 # noqa: E402


def main() -> int:
    units = e42.panel_units()
    _, prompts_mod, _ = e42.x100_modules()
    fingerprints = {}
    for key, prompt in e42.PROMPTS.items():
        if prompt["family"] == "legacy":
            fingerprints[key] = legacy.fingerprint(prompt["rubric"])
        else:
            fingerprints[key] = prompts_mod.rubric_fingerprint(prompt["rubric"])
    counts = {}
    for u in units:
        counts.setdefault(u["split"], {"llm": 0, "control": 0})[u["kind"]] += 1
    out = {"written_utc": e42.stamp(), "experiment": e42.EXPERIMENT, "source": "experiment 39 scripts/e39.py (read-only import)",
           "e39_py_sha256": e42.sha_file(e42.E39_DIR / "scripts/e39.py"), "n_units": len(units),
           "n_llm": sum(u["kind"] == "llm" for u in units), "counts_by_e39_split": counts,
           "prompt_fingerprints": fingerprints, "units": units}
    e42.write_json(e42.RESULTS / "panel.json", out)
    print(json.dumps({k: out[k] for k in ("n_units", "n_llm", "counts_by_e39_split")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
