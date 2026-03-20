"""
Generate oracle scores by comparing agent Lean outputs to gold references.

Uses an LLM judge that sees (Python source, agent Lean, gold Lean) and returns
a score from 0 to 10.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import openai
import urllib.error
import urllib.request


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _load_config_fallback() -> Dict[str, Optional[str]]:
    config_path = PROJECT_ROOT / "config.py"
    if not config_path.exists():
        return {}
    spec = importlib.util.spec_from_file_location("veribench_config", config_path)
    if spec is None or spec.loader is None:
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        "TRACE_CUSTOMLLM_URL": getattr(module, "TRACE_CUSTOMLLM_URL", None),
        "TRACE_CUSTOMLLM_API_KEY": getattr(module, "TRACE_CUSTOMLLM_API_KEY", None),
        "TRACE_CUSTOMLLM_MODEL": getattr(module, "TRACE_CUSTOMLLM_MODEL", None),
    }


def _resolve_llm_config(model_override: Optional[str]) -> Tuple[str, str, str]:
    base_url = os.environ.get("TRACE_CUSTOMLLM_URL")
    api_key = os.environ.get("TRACE_CUSTOMLLM_API_KEY")
    model = model_override or os.environ.get("TRACE_CUSTOMLLM_MODEL")

    if not base_url or not api_key or not model:
        fallback = _load_config_fallback()
        base_url = base_url or fallback.get("TRACE_CUSTOMLLM_URL")
        api_key = api_key or fallback.get("TRACE_CUSTOMLLM_API_KEY")
        model = model or fallback.get("TRACE_CUSTOMLLM_MODEL")

    if not base_url or not api_key or not model:
        raise ValueError(
            "Missing TRACE_CUSTOMLLM_URL / TRACE_CUSTOMLLM_API_KEY / TRACE_CUSTOMLLM_MODEL."
        )

    return base_url, api_key, model


def _normalize_anthropic_model(model: str) -> str:
    if model.startswith("anthropic."):
        model = model[len("anthropic.") :]
    if model.endswith("-v1:0"):
        model = model[: -len("-v1:0")]
    return model


def call_llm(
    message: str,
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    timeout_secs: float = 120.0,
    max_retries: int = 3,
    retry_sleep_secs: float = 5.0,
) -> str:
    base_url, api_key, model = _resolve_llm_config(model_name)
    use_anthropic = "api.anthropic.com" in base_url
    if use_anthropic and not base_url.endswith("/v1/messages"):
        base_url = base_url.rstrip("/") + "/v1/messages"
    if use_anthropic:
        model = _normalize_anthropic_model(model)

    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            if use_anthropic:
                req_body = json.dumps(
                    {
                        "model": model,
                        "max_tokens": 512,
                        "temperature": temperature,
                        "messages": [{"role": "user", "content": message}],
                    }
                ).encode("utf-8")
                req = urllib.request.Request(
                    base_url,
                    data=req_body,
                    method="POST",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=timeout_secs) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                content = payload.get("content", [])
                if content and isinstance(content, list):
                    return content[0].get("text", "")
                return ""

            client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=timeout_secs)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                temperature=temperature,
            )
            return response.choices[0].message.content
        except (openai.APITimeoutError, openai.APIError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(retry_sleep_secs)
            else:
                raise
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8")
            except Exception:
                body = ""
            raise RuntimeError(f"HTTP Error {exc.code}: {exc.reason} {body}".strip()) from exc
    raise last_error if last_error else RuntimeError("LLM call failed.")


def load_item_ids_from_matrix(matrix_path: Path) -> List[str]:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    for key in ("item_ids", "items", "task_ids", "example_ids"):
        if key in data:
            return [str(x) for x in data[key]]
    raise ValueError("No item_ids found in matrix JSON.")


def load_item_ids_from_file(path: Path) -> List[str]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("Item ID file is empty.")
    if raw.startswith("["):
        data = json.loads(raw)
        return [str(x) for x in data]
    return [line.strip() for line in raw.splitlines() if line.strip()]


def build_oracle_prompt(py_code: str, cand_lean: str, gold_lean: str) -> str:
    return (
        "You are a judge for Python->Lean translations.\n"
        "Given the Python spec and two Lean 4 artifacts (candidate and gold),\n"
        "score how equivalent the candidate is to the gold for the given Python task.\n"
        "Return a single integer from 0 to 10 (higher is better). Do not include any extra text.\n\n"
        "Python:\n"
        f"{py_code}\n\n"
        "Candidate Lean:\n"
        f"{cand_lean}\n\n"
        "Gold Lean:\n"
        f"{gold_lean}\n"
    )


def parse_score(text: str) -> Optional[int]:
    match = re.search(r"\b(10|[0-9])\b", text.strip())
    if match:
        return int(match.group(1))
    return None


def find_by_stem(root: Path, stem: str, suffix: str) -> Optional[Path]:
    for path in root.rglob(f"{stem}{suffix}"):
        return path
    return None


def find_candidate(agent_dir: Path, item_id: str, agent_name: str) -> Optional[Path]:
    direct = agent_dir / f"{item_id}__{agent_name}.lean"
    if direct.exists():
        return direct
    # Fallback: search recursively in case of nested paths
    for path in agent_dir.rglob(f"{item_id}__{agent_name}.lean"):
        return path
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate oracle scores with an LLM judge.")
    parser.add_argument(
        "--matrix",
        help="Path to tvd_mi_score_matrix.json (optional if --item-ids is provided)",
    )
    parser.add_argument(
        "--item-ids",
        help="Path to a JSON list or newline-separated list of item IDs",
    )
    parser.add_argument("--py-dir", required=True, help="Directory with Python sources")
    parser.add_argument("--gold-lean-dir", required=True, help="Directory with gold Lean files")
    parser.add_argument("--agent-lean-dir", required=True, help="Directory with agent Lean files")
    parser.add_argument("--agent-name", default="agent0", help="Agent name to score (default: agent0)")
    parser.add_argument("--output", required=True, help="Path to write oracle_scores.json")
    parser.add_argument("--model", default=None, help="Override model name")
    parser.add_argument("--timeout-secs", type=float, default=120.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--retry-sleep-secs", type=float, default=5.0)

    args = parser.parse_args()

    matrix_path = Path(args.matrix).expanduser().resolve() if args.matrix else None
    py_dir = Path(args.py_dir).expanduser().resolve()
    gold_dir = Path(args.gold_lean_dir).expanduser().resolve()
    agent_dir = Path(args.agent_lean_dir).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if args.item_ids:
        item_ids = load_item_ids_from_file(Path(args.item_ids).expanduser().resolve())
    elif matrix_path:
        item_ids = load_item_ids_from_matrix(matrix_path)
    else:
        raise ValueError("Provide either --matrix or --item-ids.")
    scores: List[Optional[int]] = []
    missing: List[str] = []

    for item_id in item_ids:
        py_path = find_by_stem(py_dir, item_id, ".py")
        gold_path = find_by_stem(gold_dir, item_id, ".lean")
        cand_path = find_candidate(agent_dir, item_id, args.agent_name)

        if not py_path or not gold_path or not cand_path:
            missing.append(item_id)
            scores.append(None)
            continue

        py_code = py_path.read_text(encoding="utf-8")
        gold_lean = gold_path.read_text(encoding="utf-8")
        cand_lean = cand_path.read_text(encoding="utf-8")

        prompt = build_oracle_prompt(py_code, cand_lean, gold_lean)
        response = call_llm(
            prompt,
            model_name=args.model,
            temperature=0.0,
            timeout_secs=args.timeout_secs,
            max_retries=args.max_retries,
            retry_sleep_secs=args.retry_sleep_secs,
        )
        score = parse_score(response)
        scores.append(score)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "item_ids": item_ids,
        "scores": scores,
        "agent_name": args.agent_name,
        "missing_items": missing,
    }
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote oracle scores to {output_path}")


if __name__ == "__main__":
    main()
