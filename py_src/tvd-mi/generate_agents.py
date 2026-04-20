"""
Generate multiple Lean translations (agents) per Python task for TVD-MI.

This script reads Python files, calls an LLM to translate each file into Lean 4
in the VeriBench style, and writes multiple agent outputs per task.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import logging
import sys

# Ensure py_src is on sys.path for direct script execution.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "py_src"))

import importlib.util
import urllib.error
import urllib.request
import openai


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("veribench.generate_agents")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def _load_config_fallback() -> Dict[str, str]:
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


def call_llm(
    message: str,
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    timeout_secs: float = 120.0,
    max_retries: int = 3,
    retry_sleep_secs: float = 5.0,
) -> str:
    base_url = os.environ.get("TRACE_CUSTOMLLM_URL")
    api_key = os.environ.get("TRACE_CUSTOMLLM_API_KEY")
    model = model_name or os.environ.get("TRACE_CUSTOMLLM_MODEL")

    # Standard OpenAI fallback.
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not base_url or not api_key or not model:
        fallback = _load_config_fallback()
        base_url = base_url or fallback.get("TRACE_CUSTOMLLM_URL")
        api_key = api_key or fallback.get("TRACE_CUSTOMLLM_API_KEY")
        model = model or fallback.get("TRACE_CUSTOMLLM_MODEL")

    # If no custom endpoint is configured but we have OpenAI creds/model, use default OpenAI API.
    if not base_url and api_key and model:
        base_url = "https://api.openai.com/v1"

    if not base_url or not api_key or not model:
        raise ValueError(
            "Missing model credentials. Set TRACE_CUSTOMLLM_* or OPENAI_API_KEY + --model."
        )

    use_anthropic = "api.anthropic.com" in base_url
    if use_anthropic and not base_url.endswith("/v1/messages"):
        base_url = base_url.rstrip("/") + "/v1/messages"
    if use_anthropic and model:
        if model.startswith("anthropic."):
            model = model[len("anthropic.") :]
        if model.endswith("-v1:0"):
            model = model[: -len("-v1:0")]
    logger.info(f"LLM endpoint: {base_url} | model: {model}")

    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            if use_anthropic:
                req_body = json.dumps(
                    {
                        "model": model,
                        "max_tokens": 4096,
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
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8")
            except Exception:
                body = ""
            raise RuntimeError(
                f"HTTP Error {exc.code}: {exc.reason} {body}".strip()
            ) from exc
        except (openai.APITimeoutError, openai.APIError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(retry_sleep_secs)
            else:
                raise
    raise last_error if last_error else RuntimeError("LLM call failed.")

logger = configure_logging()


def list_python_files(py_dir: Path) -> List[Path]:
    return sorted(p for p in py_dir.rglob("*.py") if p.is_file())

def load_fewshot_examples(
    gold_examples_dir_py: str, gold_examples_dir_lean: str
) -> List[str]:
    """Load few-shot Python/Lean pairs without requiring DSPy."""
    py_dir = Path(gold_examples_dir_py).expanduser().resolve()
    lean_dir = Path(gold_examples_dir_lean).expanduser().resolve()

    if not py_dir.exists():
        raise FileNotFoundError(f"Few-shot Python dir not found: {py_dir}")
    if not lean_dir.exists():
        raise FileNotFoundError(f"Few-shot Lean dir not found: {lean_dir}")

    examples: List[str] = []
    for py_path in sorted(py_dir.glob("*.py")):
        lean_path = lean_dir / py_path.with_suffix(".lean").name
        if not lean_path.exists():
            continue
        py_code = py_path.read_text(encoding="utf-8").strip()
        lean_code = lean_path.read_text(encoding="utf-8").strip()
        examples.append(
            "Python:\n"
            "```python\n"
            f"{py_code}\n"
            "```\n\n"
            "Lean4:\n"
            "```lean\n"
            f"{lean_code}\n"
            "```"
        )
    return examples


def task_id_from_path(py_path: Path, py_root: Path, include_subdir: bool) -> str:
    if include_subdir:
        rel = py_path.relative_to(py_root).with_suffix("")
        return "__".join(rel.parts)
    return py_path.stem


def ensure_unique_task_ids(task_ids: Sequence[str]) -> None:
    seen: Dict[str, int] = {}
    duplicates = []
    for task_id in task_ids:
        seen[task_id] = seen.get(task_id, 0) + 1
    for task_id, count in seen.items():
        if count > 1:
            duplicates.append(task_id)
    if duplicates:
        dup_preview = ", ".join(sorted(duplicates)[:5])
        raise ValueError(
            "Duplicate task_ids detected. Use --include-subdir-in-task-id to disambiguate. "
            f"Examples: {dup_preview}"
        )


def build_prompt(python_code: str, fewshot_examples: Optional[List[str]] = None) -> str:
    fewshot_block = ""
    if fewshot_examples:
        fewshot_block = "\n\n".join(
            f"Example {idx + 1}:\n{ex}" for idx, ex in enumerate(fewshot_examples)
        )

    prompt = (
        "You are translating a Python function/specification into a Lean 4 verification artifact "
        "in the VeriBench format. Follow the style of the examples, including: Implementation, tests, "
        "pre/post conditions, and a correctness theorem. Use `sorry` for proofs. "
        "Return only Lean 4 code with no markdown or commentary."
    )

    if fewshot_block:
        prompt += "\n\n" + fewshot_block

    prompt += (
        "\n\nPython:\n"
        f"{python_code.strip()}\n\n"
        "Lean 4:\n"
    )

    return prompt


def parse_agent_names(
    agent_names: Optional[str],
    num_agents: int,
    agent_prefix: str,
) -> List[str]:
    if agent_names:
        names = [name.strip() for name in agent_names.split(",") if name.strip()]
        if not names:
            raise ValueError("--agent-names is empty after parsing.")
        return names

    return [f"{agent_prefix}{i}" for i in range(num_agents)]


def parse_temperatures(
    temperatures: Optional[str],
    num_agents: int,
    default_temperature: float,
) -> List[float]:
    if temperatures is None:
        return [default_temperature] * num_agents

    temps = [t.strip() for t in temperatures.split(",") if t.strip()]
    if len(temps) != num_agents:
        raise ValueError(
            f"Expected {num_agents} temperatures, got {len(temps)}."
        )
    return [float(t) for t in temps]


def read_python_file(py_path: Path) -> str:
    return py_path.read_text(encoding="utf-8")


def write_output(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        logger.info(f"Skipping existing file: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_manifest(output_dir: Path, manifest: List[Dict[str, object]]) -> None:
    manifest_path = output_dir / "generation_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Saved manifest: {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate multiple Lean translations per Python task for TVD-MI."
    )
    parser.add_argument("--py-dir", required=True, help="Directory with Python tasks")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write generated Lean files",
    )
    parser.add_argument(
        "--num-agents",
        type=int,
        default=3,
        help="Number of agents to generate when --agent-names not provided",
    )
    parser.add_argument(
        "--agent-names",
        help="Comma-separated agent names (overrides --num-agents)",
    )
    parser.add_argument(
        "--agent-prefix",
        default="agent",
        help="Prefix for auto-generated agent names (default: agent)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Default sampling temperature",
    )
    parser.add_argument(
        "--temperatures",
        help="Comma-separated temperatures, one per agent",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name override (uses TRACE_CUSTOMLLM_MODEL by default)",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=None,
        help="Limit number of Python files processed",
    )
    parser.add_argument(
        "--include-subdir-in-task-id",
        action="store_true",
        help="Use relative path (with '__') to avoid task_id collisions",
    )
    parser.add_argument(
        "--fewshot-k",
        type=int,
        default=0,
        help="Include up to K few-shot examples in the prompt",
    )
    parser.add_argument(
        "--fewshot-py-dir",
        default="veribench_dataset/gold_examples/py_src",
        help="Few-shot Python examples directory",
    )
    parser.add_argument(
        "--fewshot-lean-dir",
        default="veribench_dataset/gold_examples/lean_src",
        help="Few-shot Lean examples directory",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing Lean files",
    )
    parser.add_argument(
        "--sleep-secs",
        type=float,
        default=0.0,
        help="Sleep between LLM calls",
    )
    parser.add_argument(
        "--save-prompts",
        action="store_true",
        help="Store prompts and responses in the manifest (large files)",
    )
    parser.add_argument(
        "--timeout-secs",
        type=float,
        default=120.0,
        help="Request timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Max retries per LLM call (default: 3)",
    )
    parser.add_argument(
        "--retry-sleep-secs",
        type=float,
        default=5.0,
        help="Sleep between retry attempts (default: 5s)",
    )

    args = parser.parse_args()

    py_root = Path(args.py_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    python_files = list_python_files(py_root)
    if args.max_examples is not None:
        python_files = python_files[: args.max_examples]

    if not python_files:
        raise ValueError(f"No Python files found under {py_root}")

    agent_names = parse_agent_names(args.agent_names, args.num_agents, args.agent_prefix)
    temperatures = parse_temperatures(
        args.temperatures, len(agent_names), args.temperature
    )

    task_ids = [
        task_id_from_path(p, py_root, args.include_subdir_in_task_id)
        for p in python_files
    ]
    ensure_unique_task_ids(task_ids)

    fewshot_examples: Optional[List[str]] = None
    if args.fewshot_k > 0:
        fewshot_examples = load_fewshot_examples(
            gold_examples_dir_py=args.fewshot_py_dir,
            gold_examples_dir_lean=args.fewshot_lean_dir,
        )[: args.fewshot_k]

    manifest: List[Dict[str, object]] = []

    for py_path, task_id in zip(python_files, task_ids):
        python_code = read_python_file(py_path)
        prompt = build_prompt(python_code, fewshot_examples=fewshot_examples)
        model_used = args.model or os.environ.get("TRACE_CUSTOMLLM_MODEL")

        for agent_name, temperature in zip(agent_names, temperatures):
            output_name = f"{task_id}__{agent_name}.lean"
            output_path = output_dir / output_name

            if output_path.exists() and not args.overwrite:
                logger.info(f"Skipping existing output: {output_path}")
                manifest.append(
                    {
                        "task_id": task_id,
                        "agent": agent_name,
                        "python_path": str(py_path),
                        "output_path": str(output_path),
                        "skipped": True,
                    }
                )
                continue

            logger.info(f"Generating {output_name}")
            try:
                if args.model:
                    response = call_llm(
                        prompt,
                        model_name=args.model,
                        temperature=temperature,
                        timeout_secs=args.timeout_secs,
                        max_retries=args.max_retries,
                        retry_sleep_secs=args.retry_sleep_secs,
                    )
                else:
                    response = call_llm(
                        prompt,
                        temperature=temperature,
                        timeout_secs=args.timeout_secs,
                        max_retries=args.max_retries,
                        retry_sleep_secs=args.retry_sleep_secs,
                    )
                write_output(output_path, response.strip() + "\n", overwrite=True)

                entry: Dict[str, object] = {
                    "task_id": task_id,
                    "agent": agent_name,
                    "python_path": str(py_path),
                    "output_path": str(output_path),
                    "temperature": temperature,
                    "model": model_used,
                    "skipped": False,
                    "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                }
                if args.save_prompts:
                    entry["prompt"] = prompt
                    entry["response"] = response
                manifest.append(entry)

            except Exception as exc:
                logger.error(f"Failed to generate {output_name}: {exc}")
                manifest.append(
                    {
                        "task_id": task_id,
                        "agent": agent_name,
                        "python_path": str(py_path),
                        "output_path": str(output_path),
                        "skipped": False,
                        "error": str(exc),
                    }
                )

            if args.sleep_secs > 0:
                time.sleep(args.sleep_secs)

    save_manifest(output_dir, manifest)


if __name__ == "__main__":
    main()
