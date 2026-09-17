#!/usr/bin/env python3
"""Smoke test the Qwen vLLM endpoint and the cert-judge dispatch path.

Verifies:
  1. vLLM /v1/models returns Qwen3.6-27B
  2. judge() returns a non-stub score for a real Lean theorem pair
  3. The score is bounded in [0, 1] and reasoning is non-empty.

Run after vLLM server is up. Exits non-zero on any failure.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

# unset PYTHONPATH leak before importing anything
for k in ("PYTHONPATH", "PYTHONHOME"):
    os.environ.pop(k, None)

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "experiments" / "archive" / "02_neurips_reviews"))

QWEN_BASE_URL = os.environ.setdefault("QWEN_BASE_URL", "http://127.0.0.1:8765/v1")
QWEN_API_KEY  = os.environ.setdefault("QWEN_API_KEY", "EMPTY")
MODEL = os.environ.get("QWEN_MODEL", "Qwen/Qwen3-Coder-30B-A3B-Instruct")


def step1_models_endpoint() -> None:
    url = QWEN_BASE_URL.rstrip("/") + "/models"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {QWEN_API_KEY}"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode("utf-8"))
    ids = [m.get("id") for m in payload.get("data", [])]
    print(f"[smoke 1/2] /v1/models ids = {ids}")
    assert any("qwen" in (i or "").lower() or "Qwen" in (i or "") for i in ids), \
        f"Expected a Qwen model in /v1/models, got {ids}"


def step2_judge_call() -> None:
    from utils.judge_caller import judge

    gen = "theorem add_comm_nat (k j : Nat) : k + j = j + k := by omega"
    ref = "theorem add_comm (n m : Nat) : n + m = m + n := by omega"

    # Force a fresh call with a smoke-only cache namespace.
    out = judge(
        generated_theorem=gen,
        reference_impl=ref,
        model=MODEL,
        n_repeats=1,
        cache_namespace=f"smoke13:{os.getpid()}",
    )
    print(f"[smoke 2/2] judge result: model={out.get('model')} score={out.get('score'):.3f}")
    print(f"           reasoning: {out.get('reasoning')[:120]}")
    assert 0.0 <= float(out["score"]) <= 1.0, f"score out of range: {out}"
    reasoning = (out.get("reasoning") or "").lower()
    bad_markers = ("openai_error", "anthropic_error", "parse_error", "oauth_error", "oauth_http_")
    assert not any(b in reasoning for b in bad_markers), \
        f"judge fell back to a stub: {out}"
    print("[smoke] OK — Qwen judge is genuinely answering.")


if __name__ == "__main__":
    try:
        step1_models_endpoint()
        step2_judge_call()
    except Exception as e:
        print(f"[smoke FAILED] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
