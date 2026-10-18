#!/usr/bin/env python3
"""TLDR: Pin the 51 new judge configurations and the rater rubric for the cert-judge rating pool.
No model calls. Does not pin the 125 candidate files; those bytes are not in this checkout.

    python3 experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/pin_judges_and_rubric.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = next(q for q in HERE.parents if (q / "py_src" / "cert_judge").is_dir())
VB = Path("/Users/brandomiranda/veribench")
RUBRIC = VB / "py_src/veribench_prompts/human_judgements_prompt.md"
RUBRIC_SHA = "b29e9cafdab10463d29b6ffdbb4700b46ead0e6023278b9b7b69d9ef0ab350af"
PANEL = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/panel.json"
PROMPTS = ("D0", "R4", "H0", "H1", "H2")
FAMILIES = (
    ("fable51", "anthropic/claude-fable-5-1-no-fallback", {"compute_effort": "high"}),
    ("astra", "openai/gpt-6-astra-high", {}),
    ("argon", "google/gemini-4-argon", {"reasoning_effort": "high"}),
    ("grok47", "grok/grok-4.7-high", {}),
    ("kimik3", "kimi/kimi-k3-high", {}),
    ("qwen38", "alibaba/qwen3.8-max", {}),
    ("deepseek", "deepseek/deepseek-v4-pro-0813-high", {}),
    ("glm53", "zai/glm-5.3-high", {}),
    ("mimo", "xiaomi/mimo-v2.6-pro", {}),
)
AGENT_FAMILIES = ("fable51", "astra", "kimik3")
AGENT_PROMPTS = ("H2", "D0")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rubric = sha256(RUBRIC)
    if rubric != RUBRIC_SHA:
        raise SystemExit(f"rubric hash {rubric} != {RUBRIC_SHA}")
    panel = json.loads(PANEL.read_text())
    fingerprints = {k: panel["prompt_fingerprints"][k] for k in PROMPTS}
    units = []
    for key, selector, kwargs in FAMILIES:
        for prompt in PROMPTS:
            units.append({"config": f"{key}|{prompt}", "family": key, "selector": selector,
                          "prompt": prompt, "harness": "vb103_judge", "kwargs": kwargs,
                          "prompt_fingerprint": fingerprints[prompt]})
    for key, selector, kwargs in FAMILIES:
        if key not in AGENT_FAMILIES:
            continue
        for prompt in AGENT_PROMPTS:
            units.append({"config": f"t2_{key}|{prompt}", "family": key, "selector": selector,
                          "prompt": prompt, "harness": "terminus2", "kwargs": {**kwargs, "max_turns": 20, "reasoning_effort": "high"},
                          "prompt_fingerprint": fingerprints[prompt]})
    if len(units) != 51:
        raise SystemExit(f"expected 51 units, got {len(units)}")
    payload = {
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "status": "JUDGES AND RUBRIC PINNED. Candidate files are not pinned. Do not send packets.",
        "no_model_calls": True,
        "source": "PROPOSAL_10-14-2026.md section 3.2, selectors as written there",
        "rubric": {"path": str(RUBRIC), "sha256": rubric},
        "prompt_fingerprints": fingerprints,
        "prompt_fingerprint_source": str(PANEL.relative_to(REPO)),
        "panel_sha256": sha256(PANEL),
        "n_units": len(units),
        "n_single_call": 45,
        "n_agent": 6,
        "publication_caveat": "Gemini 4 Argon units are in the pin. Experiment 106 keeps that model's per-configuration statistics private unless Vals permits publication; the public outer association then uses the other 46 units.",
        "units": units,
        "not_pinned": ["SHA-256 of the 125 experiment-109 candidate files (25 wave-1 tasks x Fable 5.1, GPT-6 Astra, Kimi K3, GLM-5.3, Mistral Medium 3.5). No Lean outputs from experiment 109 are in the local VeriBench checkout, and the IC summaries do not store per-file hashes."],
    }
    (HERE / "JUDGE_PIN_10-18-2026.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"n": len(units), "rubric": rubric[:16], "prompts": list(fingerprints)}, indent=1))


if __name__ == "__main__":
    main()
