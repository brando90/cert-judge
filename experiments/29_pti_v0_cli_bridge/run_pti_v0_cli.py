#!/usr/bin/env python3
"""CLI-only PTI-v0 scoring protocol.

This runner deliberately has no provider SDK, HTTP client, API-key loader, or
credential path.  It invokes only the locally authenticated ``codex exec`` and
``clauded`` subscription CLIs, validates every structured batch response, and
writes resumable per-batch artifacts before materializing the provider-neutral
``PTI_v0_scores_v1`` payload consumed by experiment 04's canonical metric code.
"""

from __future__ import annotations

import argparse
import ast
import csv
import fcntl
import hashlib
import importlib.util
import json
import math
import os
import re
import statistics
import subprocess
import tempfile
import threading
import time
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EXPERIMENT_DIR / "results"
RAW_BATCH_DIR = RESULTS_DIR / "raw_batches"
FROZEN_CONFIG_PATH = EXPERIMENT_DIR / "frozen_config.json"
BATCH_SCHEMA_PATH = EXPERIMENT_DIR / "batch_score_schema.json"
V4_RUNNER_PATH = REPO_ROOT / "experiments" / "04_veribench_validation" / "run_pti_v0.py"
V4_CONFIG_PATH = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "pti_v0_v4"
    / "frozen_config.json"
)
V4_REQUESTS_PATH = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "results_pti_v0_v4"
    / "score_requests.json"
)
V4_PROBES_PATH = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "results_pti_v0_v4"
    / "probe_validity_manifest.json"
)
V4_PANEL_PATH = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "results_pti_v0_v4"
    / "panel_audit"
    / "panel_manifest.json"
)
V4_POOL_PATH = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "pti_v0_v4"
    / "base_pool_manifest.json"
)
PROMPT_SOURCE = (
    REPO_ROOT
    / "experiments"
    / "02_reviewer_response_neurips_math_ai_2026"
    / "utils"
    / "sensitivity_sweep.py"
)
BAD_PROMPT_SOURCE = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "exp16_multi_judge_human_sets.py"
)

PROTOCOL_VERSION = "PTI_v0_cli_protocol_v5"
REQUEST_SCHEMA_VERSION = "PTI_v0_cli_score_requests_v1"
SCORE_SCHEMA_VERSION = "PTI_v0_scores_v1"
BATCH_SCHEMA_VERSION = "PTI_v0_cli_batch_result_v1"
METRIC_VERSION = "PTI_v0"
FROZEN_DATE = "2026-08-25"
REPEAT_COUNT = 3
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 0
MAX_CASES_PER_BATCH = 16
MAX_PROMPT_UTF8_BYTES = 180_000
DEFAULT_TIMEOUT_SECONDS = 900
DEFAULT_RETRIES = 3

JUDGES: tuple[dict[str, Any], ...] = (
    {
        "judge_id": "gpt-5.6-terra|P8_STRICT_B",
        "kind": "llm",
        "backend": "codex",
        "model": "gpt-5.6-terra",
        "prompt": "P8_STRICT_B",
        "role": "primary",
        "family": "gpt-5.6-terra",
        "effort": "low",
    },
    {
        "judge_id": "gpt-5.6-terra|P4_CHECKLIST",
        "kind": "llm",
        "backend": "codex",
        "model": "gpt-5.6-terra",
        "prompt": "P4_CHECKLIST",
        "role": "primary",
        "family": "gpt-5.6-terra",
        "effort": "low",
    },
    {
        "judge_id": "gpt-5.6-terra|P1_BASELINE",
        "kind": "llm",
        "backend": "codex",
        "model": "gpt-5.6-terra",
        "prompt": "P1_BASELINE",
        "role": "primary",
        "family": "gpt-5.6-terra",
        "effort": "low",
    },
    {
        "judge_id": "claude-sonnet-5|P8_STRICT_B",
        "kind": "llm",
        "backend": "clauded",
        "model": "claude-sonnet-5",
        "prompt": "P8_STRICT_B",
        "role": "primary",
        "family": "claude-sonnet-5",
        "effort": "low",
    },
    {
        "judge_id": "claude-sonnet-5|P4_CHECKLIST",
        "kind": "llm",
        "backend": "clauded",
        "model": "claude-sonnet-5",
        "prompt": "P4_CHECKLIST",
        "role": "primary",
        "family": "claude-sonnet-5",
        "effort": "low",
    },
    {
        "judge_id": "gpt-5.6-terra|BAD_STRINGY",
        "kind": "llm_control",
        "backend": "codex",
        "model": "gpt-5.6-terra",
        "prompt": "BAD_STRINGY",
        "role": "control",
        "family": "string_similarity_control",
        "effort": "low",
    },
    {
        "judge_id": "editdist_e1",
        "kind": "deterministic_control",
        "backend": "local",
        "model": None,
        "prompt": None,
        "role": "control",
        "family": "edit_distance_control",
        "effort": None,
    },
    {
        "judge_id": "random_r1",
        "kind": "seeded_control",
        "backend": "local",
        "model": None,
        "prompt": None,
        "role": "control",
        "family": "random_control",
        "effort": None,
    },
)

BATCH_WRAPPER = """You are processing a fixed batch of independent Lean-judge requests.
Evaluate every CASE independently. Do not compare cases, normalize scores across cases,
or let one case change another case's score. The embedded single-case instructions are
authoritative for scoring. Their single-object output instruction is superseded only by
the batch-level output contract below.

Return exactly one JSON object with this shape:
{{"scores":[{{"id":"<CASE_ID>","score":<float from 0.0 to 1.0>,"reasoning":"<one sentence>"}}]}}

Requirements:
- Return exactly one entry for every CASE_ID and no extra entries.
- Preserve each CASE_ID byte-for-byte.
- Scores must be finite numbers in [0.0, 1.0].
- No markdown or text outside the JSON object.

{cases}
"""

_PRINT_LOCK = threading.Lock()
_EXPLICIT_LLM_KEY_NAMES = {
    "ANTHROPIC_API_KEY",
    "CLAUDE_API_KEY",
    "CODEX_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _json_bytes(value)
    temporary = path.with_suffix(
        path.suffix + f".tmp.{os.getpid()}.{threading.get_ident()}"
    )
    temporary.write_bytes(payload)
    temporary.replace(path)


def _write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(
        path.suffix + f".tmp.{os.getpid()}.{threading.get_ident()}"
    )
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _child_env(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return a CLI child environment with every LLM API credential removed."""

    values = os.environ if source is None else source
    return {
        key: value
        for key, value in values.items()
        if key not in _EXPLICIT_LLM_KEY_NAMES and not key.upper().endswith("_API_KEY")
    }


def _record_cli_auth_status(path: Path) -> dict[str, Any]:
    child_env = _child_env()
    if any(
        key in _EXPLICIT_LLM_KEY_NAMES or key.upper().endswith("_API_KEY")
        for key in child_env
    ):
        raise RuntimeError("LLM API-key variable survived child-environment scrub")
    codex = subprocess.run(
        ["codex", "login", "status"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=child_env,
    )
    codex_text = f"{codex.stdout}\n{codex.stderr}".strip()
    if codex.returncode != 0 or "chatgpt" not in codex_text.lower():
        raise RuntimeError("Codex is not authenticated through ChatGPT subscription")
    claude = subprocess.run(
        ["claude", "auth", "status", "--json"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=child_env,
    )
    if claude.returncode != 0:
        raise RuntimeError("Claude CLI auth status failed")
    claude_status = json.loads(claude.stdout)
    if (
        not claude_status.get("loggedIn")
        or claude_status.get("authMethod") != "claude.ai"
    ):
        raise RuntimeError("Claude is not authenticated through claude.ai subscription")
    report = {
        "schema_version": "PTI_v0_cli_auth_status_v1",
        "checked_at": datetime.now(UTC).isoformat(),
        "child_environment_key_scrub": "all *_API_KEY plus explicit provider names",
        "codex": {"logged_in": True, "auth_method": "ChatGPT"},
        "claude": {
            "logged_in": True,
            "auth_method": claude_status.get("authMethod"),
            "api_provider": claude_status.get("apiProvider"),
            "subscription_type": claude_status.get("subscriptionType"),
        },
        "provider_api_spend_usd": 0.0,
    }
    _write_json_atomic(path, report)
    return report


@contextmanager
def _exclusive_score_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another score process holds {path}") from exc
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.flush()
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    path.unlink(missing_ok=True)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fingerprint(value: Any) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return _sha256_text(canonical)


def _verify_embedded_fingerprint(value: Mapping[str, Any], field: str) -> None:
    payload = json.loads(json.dumps(value))
    observed = str(payload.pop(field, ""))
    expected = _fingerprint(payload)
    if observed != expected:
        raise ValueError(f"{field} integrity check failed")


def _repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _literal_assignments(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: dict[str, Any] = {}
    for node in tree.body:
        target: ast.expr | None = None
        value: ast.expr | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        if isinstance(target, ast.Name) and value is not None:
            try:
                values[target.id] = ast.literal_eval(value)
            except (ValueError, TypeError):
                continue
    return values


@lru_cache(maxsize=1)
def _load_v4_runner():
    spec = importlib.util.spec_from_file_location(
        "cert_judge_pti_v0_v4", V4_RUNNER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {V4_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prompt_templates() -> dict[str, str]:
    variants = _literal_assignments(PROMPT_SOURCE)["PROMPT_VARIANTS"]
    bad = _literal_assignments(BAD_PROMPT_SOURCE)["BAD_STRINGY_PROMPT"]
    return {
        "P8_STRICT_B": variants["P8_STRICT_B"],
        "P4_CHECKLIST": variants["P4_CHECKLIST"],
        "P1_BASELINE": variants["P1_BASELINE"],
        "BAD_STRINGY": bad,
    }


def frozen_config() -> dict[str, Any]:
    templates = _prompt_templates()
    v4_config = _read_json(V4_CONFIG_PATH)
    judges: list[dict[str, Any]] = []
    for source in JUDGES:
        judge = dict(source)
        prompt_name = judge["prompt"]
        judge["prompt_sha256"] = (
            _sha256_text(templates[prompt_name]) if prompt_name is not None else None
        )
        judge["repeat_count"] = REPEAT_COUNT
        judge["response_contract"] = (
            "validated structured batch JSON" if judge["backend"] != "local" else None
        )
        judges.append(judge)
    config: dict[str, Any] = {
        "schema_version": PROTOCOL_VERSION,
        "metric_version": METRIC_VERSION,
        "frozen_date": FROZEN_DATE,
        "supersedes_execution_only": "PTI_v0_protocol_v4",
        "v4_status": (
            "NOT_RUN: exact gpt-5.3-codex and gpt-4o-mini model IDs are rejected "
            "by the approved ChatGPT-backed Codex CLI"
        ),
        "scientific_question": (
            "Does the unchanged PTI_v0 proxy rank current CLI-accessible judge "
            "configurations like paired human TI_m1?"
        ),
        "metric_contract": {
            "properties": ["P_eq", "P_bm", "P_ms", "P_eqalpha"],
            "repeat_aggregation": "median",
            "repeat_count": REPEAT_COUNT,
            "coverage_threshold": 1.0,
            "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "sesoi_spearman": 0.5,
            "source": _repo_path(V4_CONFIG_PATH),
            "source_sha256": _sha256_file(V4_CONFIG_PATH),
        },
        "execution_contract": {
            "allowed_backends": ["codex exec", "clauded", "local deterministic"],
            "provider_sdk_or_http": "forbidden and absent",
            "billing": "subscription CLI; provider API spend USD = 0",
            "child_environment": (
                "all variables ending in _API_KEY plus explicit provider key names are "
                "removed before either CLI process starts"
            ),
            "independence": (
                "each batch repeat is a new ephemeral CLI process; fixed cases within a "
                "batch are instructed to be scored independently"
            ),
            "batch_assignment": (
                "per judge, sorted artifact round-robin into the lowest artifact-disjoint "
                "batch satisfying fixed case/byte caps; fixed across repeats"
            ),
            "max_cases_per_batch": MAX_CASES_PER_BATCH,
            "max_prompt_utf8_bytes": MAX_PROMPT_UTF8_BYTES,
            "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
            "max_retries": DEFAULT_RETRIES,
            "sampling": (
                "CLI default decoding; subscription CLIs expose no stable provider-"
                "temperature flag in this protocol"
            ),
            "batch_wrapper_sha256": _sha256_text(BATCH_WRAPPER),
            "batch_schema_sha256": _sha256_file(BATCH_SCHEMA_PATH),
        },
        "panel_policy": v4_config["panel_policy"],
        "probe_policy": v4_config["probe_policy"],
        "score_policy": v4_config["score_policy"],
        "criterion_policy": {
            "score_coverage_threshold": 1.0,
            "score_source": "same PTI_v0 CLI score manifest as the property run",
            "repeat_aggregation": "median of exactly three independent batch processes",
            "human_primary_view": "average",
            "human_secondary_views": ["strict", "lenient"],
            "bootstrap": "paired-artifact percentile with undefined replicates counted",
        },
        "statistics": v4_config["statistics"],
        "control_policy": v4_config["control_policy"],
        "judges": judges,
        "source_provenance": {
            "v4_probe_manifest": _repo_path(V4_PROBES_PATH),
            "v4_probe_manifest_sha256": _sha256_file(V4_PROBES_PATH),
            "v4_panel_manifest": _repo_path(V4_PANEL_PATH),
            "v4_panel_manifest_sha256": _sha256_file(V4_PANEL_PATH),
            "prompt_source": _repo_path(PROMPT_SOURCE),
            "prompt_source_sha256": _sha256_file(PROMPT_SOURCE),
            "bad_prompt_source": _repo_path(BAD_PROMPT_SOURCE),
            "bad_prompt_source_sha256": _sha256_file(BAD_PROMPT_SOURCE),
            "runner": _repo_path(Path(__file__)),
            "runner_sha256": _sha256_file(Path(__file__)),
        },
    }
    config["config_fingerprint"] = _fingerprint(config)
    return config


def _verify_frozen_config(path: Path = FROZEN_CONFIG_PATH) -> dict[str, Any]:
    observed = _read_json(path)
    expected = frozen_config()
    if observed != expected:
        raise ValueError(
            f"frozen config drift: regenerate and commit {path} before inference"
        )
    return observed


def command_freeze(args: argparse.Namespace) -> int:
    config = frozen_config()
    _write_json_atomic(args.out, config)
    print(f"wrote {args.out}: {config['config_fingerprint']}")
    return 0


def _point_fields(request: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "artifact_id",
        "candidate_sha256",
        "candidate_utf8_bytes",
        "gold_source_sha256",
        "level",
        "probe_type",
        "reference_preprocessing",
        "reference_sha256",
        "reference_utf8_bytes",
        "variant",
    )
    return {key: request[key] for key in keys}


def _property_points() -> list[dict[str, Any]]:
    source = _read_json(V4_REQUESTS_PATH)
    first_judge = source["requests"][0]["judge_id"]
    return [
        _point_fields(request)
        for request in source["requests"]
        if request["judge_id"] == first_judge
    ]


def _criterion_points() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    v4 = _load_v4_runner()
    panel = _read_json(V4_PANEL_PATH)
    pool = _read_json(V4_POOL_PATH)
    by_candidate_name = {
        Path(row["candidate_path"]).name: row for row in pool["artifacts"]
    }
    points: list[dict[str, Any]] = []
    criterion_rows: list[dict[str, Any]] = []
    for row in panel["rows"]:
        candidate_name = row["candidate_file"]
        source = by_candidate_name.get(candidate_name)
        if source is None:
            raise ValueError(f"panel candidate absent from pool: {candidate_name}")
        candidate_path = REPO_ROOT / source["candidate_path"]
        gold_path = REPO_ROOT / source["gold_path"]
        candidate = candidate_path.read_text(encoding="utf-8")
        gold_source = gold_path.read_text(encoding="utf-8")
        reference = v4._score_reference(gold_source)
        if _sha256_text(candidate) != source["candidate_sha256"]:
            raise ValueError(f"candidate hash drift: {candidate_name}")
        point = {
            "artifact_id": source["artifact_id"],
            "candidate_sha256": _sha256_text(candidate),
            "candidate_utf8_bytes": len(candidate.encode("utf-8")),
            "gold_source_sha256": _sha256_text(gold_source),
            "level": 0,
            "probe_type": "criterion",
            "reference_preprocessing": "last_theorem_or_lemma_block_v1",
            "reference_sha256": _sha256_text(reference),
            "reference_utf8_bytes": len(reference.encode("utf-8")),
            "variant": "human_panel",
        }
        points.append(point)
        criterion_rows.append(
            {
                "artifact_id": source["artifact_id"],
                "candidate_file": candidate_name,
                "gold_file": row["gold_file"],
                "strict_score_0_5": float(row["strict_score_0_5"]),
                "lenient_score_0_5": float(row["lenient_score_0_5"]),
                "average_score_0_5": float(row["average_score_0_5"]),
            }
        )
    return points, criterion_rows


def _score_cell_id(
    point: Mapping[str, Any], judge: Mapping[str, Any], config: Mapping[str, Any]
) -> str:
    identity = {
        "score_schema_version": SCORE_SCHEMA_VERSION,
        "execution_protocol": PROTOCOL_VERSION,
        "judge_id": judge["judge_id"],
        "model": judge["model"],
        "prompt_sha256": judge["prompt_sha256"],
        "batch_wrapper_sha256": config["execution_contract"]["batch_wrapper_sha256"],
        "candidate_sha256": point["candidate_sha256"],
        "reference_sha256": point["reference_sha256"],
        "repeat_count": REPEAT_COUNT,
    }
    return _fingerprint(identity)


def _request_from_point(
    point: Mapping[str, Any], judge: Mapping[str, Any], config: Mapping[str, Any]
) -> dict[str, Any]:
    request = {
        **point,
        "judge_id": judge["judge_id"],
        "judge_kind": judge["kind"],
        "backend": judge["backend"],
        "model": judge["model"],
        "prompt": judge["prompt"],
        "prompt_sha256": judge["prompt_sha256"],
        "role": judge["role"],
        "family": judge["family"],
        "effort": judge["effort"],
        "repeat_count": REPEAT_COUNT,
    }
    request["score_cell_id"] = _score_cell_id(point, judge, config)
    return request


def _content_pairs() -> dict[tuple[str, str, int, str], tuple[str, str]]:
    v4 = _load_v4_runner()
    pairs = dict(v4._probe_content_pairs(_read_json(V4_PROBES_PATH)))
    criterion_points, _rows = _criterion_points()
    pool = _read_json(V4_POOL_PATH)
    by_artifact = {row["artifact_id"]: row for row in pool["artifacts"]}
    for point in criterion_points:
        source = by_artifact[point["artifact_id"]]
        candidate = (REPO_ROOT / source["candidate_path"]).read_text(encoding="utf-8")
        gold = (REPO_ROOT / source["gold_path"]).read_text(encoding="utf-8")
        reference = v4._score_reference(gold)
        pairs[(point["artifact_id"], "criterion", 0, "human_panel")] = (
            candidate,
            reference,
        )
    return pairs


def _request_pair(
    request: Mapping[str, Any],
    pairs: Mapping[tuple[str, str, int, str], tuple[str, str]],
) -> tuple[str, str]:
    key = (
        str(request["artifact_id"]),
        str(request["probe_type"]),
        int(request["level"]),
        str(request["variant"]),
    )
    candidate, reference = pairs[key]
    if _sha256_text(candidate) != request["candidate_sha256"]:
        raise ValueError(f"candidate hash mismatch for {request['score_cell_id']}")
    if _sha256_text(reference) != request["reference_sha256"]:
        raise ValueError(f"reference hash mismatch for {request['score_cell_id']}")
    return candidate, reference


def _render_case(
    request: Mapping[str, Any], templates: Mapping[str, str], pairs: Mapping[Any, Any]
) -> str:
    candidate, reference = _request_pair(request, pairs)
    prompt_name = str(request["prompt"])
    single = templates[prompt_name].format(
        reference_impl=reference,
        generated_theorem=candidate,
    )
    return (
        f"CASE_ID: {request['score_cell_id']}\n"
        "BEGIN_SINGLE_CASE_PROMPT\n"
        f"{single}\n"
        "END_SINGLE_CASE_PROMPT"
    )


def _render_batch(
    batch: Mapping[str, Any],
    unique_requests: Mapping[str, Mapping[str, Any]],
    templates: Mapping[str, str],
    pairs: Mapping[Any, Any],
) -> str:
    cases = "\n\n".join(
        _render_case(unique_requests[cell_id], templates, pairs)
        for cell_id in batch["score_cell_ids"]
    )
    prompt = BATCH_WRAPPER.format(cases=cases)
    if _sha256_text(prompt) != batch["rendered_prompt_sha256"]:
        raise ValueError(f"batch prompt hash drift for {batch['batch_id']}")
    return prompt


def _pack_batches(
    unique_requests: Mapping[str, Mapping[str, Any]],
    templates: Mapping[str, str],
    pairs: Mapping[Any, Any],
) -> list[dict[str, Any]]:
    by_judge: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for cell_id, request in unique_requests.items():
        if request["backend"] != "local":
            by_judge[str(request["judge_id"])][str(request["artifact_id"])].append(
                cell_id
            )
    batches: list[dict[str, Any]] = []
    for judge_id in sorted(by_judge):
        slots: list[dict[str, Any]] = []
        for artifact_id in sorted(by_judge[judge_id]):
            for cell_id in sorted(by_judge[judge_id][artifact_id]):
                placed = False
                for slot in slots:
                    if artifact_id in slot["artifact_ids"]:
                        continue
                    proposed = [*slot["cell_ids"], cell_id]
                    if len(proposed) > MAX_CASES_PER_BATCH:
                        continue
                    cases = "\n\n".join(
                        _render_case(unique_requests[value], templates, pairs)
                        for value in proposed
                    )
                    if (
                        len(BATCH_WRAPPER.format(cases=cases).encode("utf-8"))
                        > MAX_PROMPT_UTF8_BYTES
                    ):
                        continue
                    slot["cell_ids"].append(cell_id)
                    slot["artifact_ids"].add(artifact_id)
                    placed = True
                    break
                if not placed:
                    slots.append({"cell_ids": [cell_id], "artifact_ids": {artifact_id}})
        for slot in slots:
            batches.append(
                _make_batch(
                    judge_id, slot["cell_ids"], unique_requests, templates, pairs
                )
            )
    return batches


def _make_batch(
    judge_id: str,
    cell_ids: Sequence[str],
    unique_requests: Mapping[str, Mapping[str, Any]],
    templates: Mapping[str, str],
    pairs: Mapping[Any, Any],
) -> dict[str, Any]:
    first = unique_requests[cell_ids[0]]
    cases = "\n\n".join(
        _render_case(unique_requests[value], templates, pairs) for value in cell_ids
    )
    prompt = BATCH_WRAPPER.format(cases=cases)
    prompt_bytes = len(prompt.encode("utf-8"))
    artifact_ids = [
        str(unique_requests[cell_id]["artifact_id"]) for cell_id in cell_ids
    ]
    if len(cell_ids) > MAX_CASES_PER_BATCH:
        raise ValueError(f"batch {judge_id} exceeds fixed case cap")
    if prompt_bytes > MAX_PROMPT_UTF8_BYTES:
        raise ValueError(f"batch {judge_id} exceeds fixed prompt-byte cap")
    if len(artifact_ids) != len(set(artifact_ids)):
        raise ValueError(f"batch {judge_id} contains repeated artifact IDs")
    identity = {
        "protocol": PROTOCOL_VERSION,
        "judge_id": judge_id,
        "backend": first["backend"],
        "model": first["model"],
        "effort": first["effort"],
        "score_cell_ids": list(cell_ids),
        "rendered_prompt_sha256": _sha256_text(prompt),
    }
    return {
        "batch_id": _fingerprint(identity),
        "judge_id": judge_id,
        "backend": first["backend"],
        "model": first["model"],
        "effort": first["effort"],
        "prompt": first["prompt"],
        "score_cell_ids": list(cell_ids),
        "artifact_ids": artifact_ids,
        "case_count": len(cell_ids),
        "rendered_prompt_utf8_bytes": prompt_bytes,
        "rendered_prompt_sha256": _sha256_text(prompt),
        "repeat_count": REPEAT_COUNT,
    }


def command_build(args: argparse.Namespace) -> int:
    config = _verify_frozen_config(args.config)
    property_points = _property_points()
    criterion_points, criterion_rows = _criterion_points()
    all_points = [*property_points, *criterion_points]
    requests = [
        _request_from_point(point, judge, config)
        for judge in config["judges"]
        for point in all_points
    ]
    unique_requests: dict[str, dict[str, Any]] = {}
    for request in requests:
        cell_id = request["score_cell_id"]
        if cell_id in unique_requests:
            left = unique_requests[cell_id]
            for field in ("candidate_sha256", "reference_sha256", "judge_id"):
                if left[field] != request[field]:
                    raise ValueError(f"score-cell collision on {cell_id}")
        else:
            unique_requests[cell_id] = request
    manifest: dict[str, Any] = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "config_fingerprint": config["config_fingerprint"],
        "source_probe_manifest_sha256": _sha256_file(V4_PROBES_PATH),
        "source_panel_manifest_sha256": _sha256_file(V4_PANEL_PATH),
        "property_point_count_per_judge": len(property_points),
        "criterion_point_count_per_judge": len(criterion_points),
        "judge_count": len(config["judges"]),
        "conceptual_request_cell_count": len(requests),
        "unique_score_cell_count": len(unique_requests),
        "requests": requests,
    }
    manifest["manifest_fingerprint"] = _fingerprint(manifest)
    _write_json_atomic(args.out_dir / "score_requests.json", manifest)

    score_cells_by_judge_and_artifact: dict[tuple[str, str], str] = {}
    for request in requests:
        if request["probe_type"] == "criterion":
            score_cells_by_judge_and_artifact[
                (request["judge_id"], request["artifact_id"])
            ] = request["score_cell_id"]
    criterion_manifest = {
        "schema_version": "PTI_v0_cli_criterion_manifest_v1",
        "metric_version": METRIC_VERSION,
        "panel_manifest_sha256": _sha256_file(V4_PANEL_PATH),
        "panel_row_count": len(criterion_rows),
        "rows": [
            {
                **row,
                "score_cell_ids": {
                    judge["judge_id"]: score_cells_by_judge_and_artifact[
                        (judge["judge_id"], row["artifact_id"])
                    ]
                    for judge in config["judges"]
                },
            }
            for row in criterion_rows
        ],
    }
    criterion_manifest["manifest_fingerprint"] = _fingerprint(criterion_manifest)
    _write_json_atomic(args.out_dir / "criterion_manifest.json", criterion_manifest)

    templates = _prompt_templates()
    pairs = _content_pairs()
    batches = _pack_batches(unique_requests, templates, pairs)
    batch_manifest: dict[str, Any] = {
        "schema_version": "PTI_v0_cli_batch_manifest_v1",
        "metric_version": METRIC_VERSION,
        "request_manifest_fingerprint": manifest["manifest_fingerprint"],
        "assignment": (
            "per judge, sorted artifact round-robin into the lowest artifact-disjoint "
            "batch satisfying fixed case/byte caps; fixed across repeats"
        ),
        "max_cases_per_batch": MAX_CASES_PER_BATCH,
        "max_prompt_utf8_bytes": MAX_PROMPT_UTF8_BYTES,
        "batch_count": len(batches),
        "cli_invocation_count": len(batches) * REPEAT_COUNT,
        "batches_by_judge": dict(Counter(batch["judge_id"] for batch in batches)),
        "batches": batches,
    }
    batch_manifest["manifest_fingerprint"] = _fingerprint(batch_manifest)
    _write_json_atomic(args.out_dir / "batch_manifest.json", batch_manifest)
    print(
        f"wrote manifests: conceptual={len(requests)} unique={len(unique_requests)} "
        f"batches={len(batches)} cli_invocations={len(batches) * REPEAT_COUNT}"
    )
    return 0


def _unique_requests(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for request in manifest["requests"]:
        unique.setdefault(request["score_cell_id"], request)
    return unique


def _validate_batch_scores(
    value: Any, expected_ids: Sequence[str]
) -> list[dict[str, Any]]:
    if not isinstance(value, dict) or not isinstance(value.get("scores"), list):
        raise TypeError("batch output must be an object containing a scores list")
    scores = value["scores"]
    observed: dict[str, dict[str, Any]] = {}
    for record in scores:
        if not isinstance(record, dict):
            raise TypeError("every batch score must be an object")
        cell_id = str(record.get("id", ""))
        if cell_id in observed:
            raise ValueError(f"duplicate batch score id {cell_id}")
        raw_score = record["score"]
        if isinstance(raw_score, bool) or not isinstance(raw_score, (int, float)):
            raise TypeError(f"score for {cell_id} must be a JSON number")
        score = float(raw_score)
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError(f"invalid score for {cell_id}: {score}")
        reasoning = str(record.get("reasoning", "")).strip()
        if not reasoning:
            raise ValueError(f"missing reasoning for {cell_id}")
        observed[cell_id] = {"id": cell_id, "score": score, "reasoning": reasoning}
    if set(observed) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(observed))
        extra = sorted(set(observed) - set(expected_ids))
        raise ValueError(f"batch id mismatch: missing={missing[:3]} extra={extra[:3]}")
    return [observed[cell_id] for cell_id in expected_ids]


def _parse_json_text(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return json.loads(stripped)


def _run_codex(
    batch: Mapping[str, Any], prompt: str, *, timeout: int
) -> tuple[Any, dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="pti-v0-codex-") as temporary:
        root = Path(temporary)
        output_path = root / "last.json"
        argv = [
            "codex",
            "exec",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "-C",
            str(root),
            "-s",
            "read-only",
            "--ephemeral",
            "--json",
            "--color",
            "never",
            "-m",
            str(batch["model"]),
            "-c",
            f'model_reasoning_effort="{batch["effort"]}"',
            "--output-schema",
            str(BATCH_SCHEMA_PATH),
            "-o",
            str(output_path),
            "-",
        ]
        completed = subprocess.run(
            argv,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=_child_env(),
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"codex rc={completed.returncode}: {(completed.stderr or completed.stdout)[-500:]}"
            )
        if not output_path.exists():
            raise RuntimeError("codex did not write --output-last-message")
        parsed = _parse_json_text(output_path.read_text(encoding="utf-8"))
        event_types: Counter[str] = Counter()
        item_types: Counter[str] = Counter()
        allowed_items = {"agent_message", "reasoning"}
        for line in completed.stdout.splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError("codex --json emitted non-JSON output") from exc
            event_types[str(event.get("type", "unknown"))] += 1
            item = event.get("item")
            if isinstance(item, dict):
                item_type = str(item.get("type", "unknown"))
                item_types[item_type] += 1
                if item_type not in allowed_items:
                    raise RuntimeError(
                        f"codex attempted forbidden tool use: {item_type}"
                    )
        usage: dict[str, Any] = {}
        combined = f"{completed.stdout}\n{completed.stderr}"
        match = re.search(r"tokens used\s*\n?\s*([0-9,]+)", combined)
        if match:
            usage["tokens_used"] = int(match.group(1).replace(",", ""))
        model_match = re.search(r"(?m)^model:\s*(\S+)\s*$", combined)
        effort_match = re.search(r"(?m)^reasoning effort:\s*(\S+)\s*$", combined)
        if model_match and model_match.group(1) != batch["model"]:
            raise RuntimeError(
                f"codex model mismatch: requested={batch['model']} "
                f"observed={model_match.group(1)}"
            )
        if effort_match and effort_match.group(1) != batch["effort"]:
            raise RuntimeError(
                f"codex effort mismatch: requested={batch['effort']} "
                f"observed={effort_match.group(1)}"
            )
        usage["requested_model"] = batch["model"]
        usage["observed_model"] = model_match.group(1) if model_match else None
        usage["observed_effort"] = effort_match.group(1) if effort_match else None
        usage["event_types"] = dict(sorted(event_types.items()))
        usage["item_types"] = dict(sorted(item_types.items()))
        usage["forbidden_tool_item_count"] = 0
        usage["model_provenance"] = (
            "explicit -m argument; successful CLI invocation; Codex JSONL does not "
            "currently expose a model field"
            if model_match is None
            else "CLI header"
        )
        return parsed, usage, completed.stdout, completed.stderr


def _run_clauded(
    batch: Mapping[str, Any], prompt: str, *, timeout: int
) -> tuple[Any, dict[str, Any], str, str]:
    inline_schema = dict(_read_json(BATCH_SCHEMA_PATH))
    inline_schema.pop("$schema", None)
    schema_text = json.dumps(inline_schema, separators=(",", ":"))
    argv = [
        "claude",
        "--safe-mode",
        "--model",
        str(batch["model"]),
        "--effort",
        str(batch["effort"]),
        "--no-session-persistence",
        "--tools",
        "",
        "--disable-slash-commands",
        "--output-format",
        "json",
        "--json-schema",
        schema_text,
        "--max-budget-usd",
        "2.0",
        "-p",
        prompt,
    ]
    completed = subprocess.run(
        argv,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env=_child_env(),
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"clauded rc={completed.returncode}: {(completed.stderr or completed.stdout)[-500:]}"
        )
    outer = json.loads(completed.stdout)
    if outer.get("is_error"):
        raise RuntimeError(f"clauded error: {outer.get('result')}")
    parsed = outer.get("structured_output")
    if parsed is None:
        parsed = _parse_json_text(str(outer["result"]))
    model_usage = outer.get("modelUsage", {})
    canonical_models = {
        str(value.get("canonicalModel"))
        for value in model_usage.values()
        if isinstance(value, dict)
    }
    if batch["model"] not in canonical_models and batch["model"] not in model_usage:
        raise RuntimeError(
            f"clauded model mismatch: requested={batch['model']} observed={sorted(canonical_models)}"
        )
    usage = {
        "requested_model": batch["model"],
        "canonical_models": sorted(canonical_models),
        "usage": outer.get("usage", {}),
        "model_usage": model_usage,
        "service_tier": outer.get("usage", {}).get("service_tier"),
    }
    return parsed, usage, completed.stdout, completed.stderr


def _raw_batch_path(batch_id: str, repeat_id: int, raw_dir: Path) -> Path:
    return raw_dir / f"{batch_id}__r{repeat_id}.json"


def _validate_raw_result(
    payload: Mapping[str, Any],
    batch: Mapping[str, Any],
    repeat_id: int,
    path: Path | None = None,
) -> None:
    if payload.get("schema_version") != BATCH_SCHEMA_VERSION:
        raise ValueError("raw batch schema mismatch")
    if payload.get("batch_id") != batch["batch_id"]:
        raise ValueError("raw batch id mismatch")
    if int(payload.get("repeat_id", -1)) != repeat_id:
        raise ValueError("raw batch repeat mismatch")
    expected_fields = {
        "protocol_version": PROTOCOL_VERSION,
        "judge_id": batch["judge_id"],
        "backend": batch["backend"],
        "requested_model": batch["model"],
        "effort": batch["effort"],
    }
    for field, expected in expected_fields.items():
        if payload.get(field) != expected:
            raise ValueError(f"raw batch {field} mismatch")
    if payload.get("rendered_prompt_sha256") != batch["rendered_prompt_sha256"]:
        raise ValueError("raw batch prompt hash mismatch")
    if float(payload.get("provider_api_spend_usd", -1.0)) != 0.0:
        raise ValueError("raw batch provider-spend invariant failed")
    if path is not None:
        stdout_path = path.with_suffix(".stdout.txt")
        stderr_path = path.with_suffix(".stderr.txt")
        if not stdout_path.exists() or not stderr_path.exists():
            raise ValueError("raw batch transcript is missing")
        if _sha256_file(stdout_path) != payload.get("cli_stdout_sha256"):
            raise ValueError("raw batch stdout transcript hash mismatch")
        if _sha256_file(stderr_path) != payload.get("cli_stderr_sha256"):
            raise ValueError("raw batch stderr transcript hash mismatch")
    _validate_batch_scores({"scores": payload.get("scores")}, batch["score_cell_ids"])


def _execute_one(
    batch: Mapping[str, Any],
    repeat_id: int,
    unique_requests: Mapping[str, Mapping[str, Any]],
    templates: Mapping[str, str],
    pairs: Mapping[Any, Any],
    raw_dir: Path,
    timeout: int,
    retries: int,
) -> tuple[str, bool, str]:
    path = _raw_batch_path(batch["batch_id"], repeat_id, raw_dir)
    if path.exists():
        try:
            _validate_raw_result(_read_json(path), batch, repeat_id, path)
            return batch["batch_id"], True, "cached"
        except Exception:  # noqa: BLE001 - corrupt resume artifacts are quarantined
            quarantine = path.with_suffix(path.suffix + f".invalid.{time.time_ns()}")
            path.rename(quarantine)
    prompt = _render_batch(batch, unique_requests, templates, pairs)
    errors: list[str] = []
    for attempt in range(1, retries + 1):
        started = time.monotonic()
        try:
            if batch["backend"] == "codex":
                parsed, usage, stdout, stderr = _run_codex(
                    batch, prompt, timeout=timeout
                )
            elif batch["backend"] == "clauded":
                parsed, usage, stdout, stderr = _run_clauded(
                    batch, prompt, timeout=timeout
                )
            else:
                raise ValueError(f"unsupported backend {batch['backend']}")
            scores = _validate_batch_scores(parsed, batch["score_cell_ids"])
            payload = {
                "schema_version": BATCH_SCHEMA_VERSION,
                "metric_version": METRIC_VERSION,
                "protocol_version": PROTOCOL_VERSION,
                "batch_id": batch["batch_id"],
                "repeat_id": repeat_id,
                "judge_id": batch["judge_id"],
                "backend": batch["backend"],
                "requested_model": batch["model"],
                "effort": batch["effort"],
                "rendered_prompt_sha256": batch["rendered_prompt_sha256"],
                "case_count": batch["case_count"],
                "scores": scores,
                "usage": usage,
                "attempt": attempt,
                "elapsed_seconds": time.monotonic() - started,
                "completed_at": datetime.now(UTC).isoformat(),
                "cli_stdout_sha256": _sha256_text(stdout),
                "cli_stderr_sha256": _sha256_text(stderr),
                "provider_api_spend_usd": 0.0,
            }
            _write_text_atomic(path.with_suffix(".stdout.txt"), stdout)
            _write_text_atomic(path.with_suffix(".stderr.txt"), stderr)
            _write_json_atomic(path, payload)
            _validate_raw_result(payload, batch, repeat_id, path)
            return batch["batch_id"], False, "ok"
        except Exception as exc:  # noqa: BLE001 - CLI/process/parse failures share retry policy
            errors.append(f"attempt {attempt}: {type(exc).__name__}: {str(exc)[:500]}")
            if attempt < retries:
                time.sleep(min(45.0, 5.0 * (3 ** (attempt - 1))))
    failure_path = path.with_suffix(path.suffix + f".failure.{time.time_ns()}.json")
    _write_json_atomic(
        failure_path,
        {
            "schema_version": "PTI_v0_cli_batch_failure_v1",
            "batch_id": batch["batch_id"],
            "repeat_id": repeat_id,
            "judge_id": batch["judge_id"],
            "errors": errors,
            "completed_at": datetime.now(UTC).isoformat(),
        },
    )
    return batch["batch_id"], False, errors[-1]


def _materialize_scores(
    requests: Mapping[str, Any],
    batches: Mapping[str, Any],
    raw_dir: Path,
    out: Path,
) -> tuple[int, int]:
    unique = _unique_requests(requests)
    pairs = _content_pairs()
    v4 = _load_v4_runner()
    records: list[dict[str, Any]] = []
    observed_repeats: dict[str, set[int]] = defaultdict(set)
    batch_by_id = {batch["batch_id"]: batch for batch in batches["batches"]}
    for batch_id in sorted(batch_by_id):
        batch = batch_by_id[batch_id]
        for repeat_id in range(REPEAT_COUNT):
            path = _raw_batch_path(batch_id, repeat_id, raw_dir)
            if not path.exists():
                continue
            payload = _read_json(path)
            _validate_raw_result(payload, batch, repeat_id, path)
            for score in payload["scores"]:
                records.append(
                    {
                        "score_cell_id": score["id"],
                        "repeat_id": repeat_id,
                        "normalized_score": score["score"],
                        "reasoning": score["reasoning"],
                        "judge_id": batch["judge_id"],
                        "model": batch["model"],
                        "backend": batch["backend"],
                        "batch_id": batch_id,
                    }
                )
                observed_repeats[score["id"]].add(repeat_id)
    for cell_id, request in sorted(unique.items()):
        if request["backend"] != "local":
            continue
        candidate, reference = _request_pair(request, pairs)
        if request["judge_kind"] == "deterministic_control":
            value = v4._edit_similarity(reference, candidate)
        elif request["judge_kind"] == "seeded_control":
            value = v4._deterministic_random_score(
                request["judge_id"], reference, candidate, seed=42
            )
        else:
            raise ValueError(f"unknown local kind {request['judge_kind']}")
        for repeat_id in range(REPEAT_COUNT):
            records.append(
                {
                    "score_cell_id": cell_id,
                    "repeat_id": repeat_id,
                    "normalized_score": value,
                    "reasoning": "deterministic local control",
                    "judge_id": request["judge_id"],
                    "model": None,
                    "backend": "local",
                    "batch_id": None,
                }
            )
            observed_repeats[cell_id].add(repeat_id)
    complete_cells = {
        cell_id
        for cell_id, repeat_ids in observed_repeats.items()
        if repeat_ids == set(range(REPEAT_COUNT))
    }
    payload = {
        "schema_version": SCORE_SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "request_manifest_fingerprint": requests["manifest_fingerprint"],
        "batch_manifest_fingerprint": batches["manifest_fingerprint"],
        "source": "approved subscription CLIs plus deterministic local controls",
        "provider_api_spend_usd": 0.0,
        "expected_unique_cells": len(unique),
        "complete_unique_cells": len(complete_cells),
        "record_count": len(records),
        "records": sorted(
            records, key=lambda row: (row["score_cell_id"], row["repeat_id"])
        ),
    }
    _write_json_atomic(out, payload)
    return len(complete_cells), len(unique)


def command_score(args: argparse.Namespace) -> int:
    lock_path = args.raw_dir.parent / ".score.lock"
    with _exclusive_score_lock(lock_path):
        return _command_score_locked(args)


def _command_score_locked(args: argparse.Namespace) -> int:
    config = _verify_frozen_config(args.config)
    requests = _read_json(args.requests)
    batches = _read_json(args.batches)
    _verify_embedded_fingerprint(requests, "manifest_fingerprint")
    _verify_embedded_fingerprint(batches, "manifest_fingerprint")
    if requests.get("config_fingerprint") != config["config_fingerprint"]:
        raise ValueError("request/config fingerprint mismatch")
    if batches["request_manifest_fingerprint"] != requests["manifest_fingerprint"]:
        raise ValueError("batch/request manifest mismatch")
    _record_cli_auth_status(args.raw_dir.parent / "cli_auth_status.json")
    unique = _unique_requests(requests)
    templates = _prompt_templates()
    pairs = _content_pairs()
    selected = list(batches["batches"])
    if args.judge:
        allowed = set(args.judge)
        selected = [batch for batch in selected if batch["judge_id"] in allowed]
    tasks = [
        (batch, repeat_id) for batch in selected for repeat_id in range(REPEAT_COUNT)
    ]
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    total = len(tasks)
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                _execute_one,
                batch,
                repeat_id,
                unique,
                templates,
                pairs,
                args.raw_dir,
                args.timeout,
                args.retries,
            ): (batch, repeat_id)
            for batch, repeat_id in tasks
        }
        for index, future in enumerate(as_completed(futures), start=1):
            batch, repeat_id = futures[future]
            try:
                _batch_id, cached, status = future.result()
            except Exception as exc:  # noqa: BLE001 - surface worker failures in run status
                cached = False
                status = f"worker exception: {type(exc).__name__}: {exc}"
            if status not in {"ok", "cached"}:
                failures.append(f"{batch['batch_id']} r{repeat_id}: {status}")
            with _PRINT_LOCK:
                print(
                    f"[{index}/{total}] {batch['judge_id']} batch={batch['batch_id'][:10]} "
                    f"r={repeat_id} status={'cached' if cached else status}",
                    flush=True,
                )
    complete, expected = _materialize_scores(requests, batches, args.raw_dir, args.out)
    print(
        f"materialized {args.out}: complete_cells={complete}/{expected} "
        f"failures={len(failures)}"
    )
    if failures:
        for failure in failures[:20]:
            print(f"FAIL: {failure}")
        return 2
    if args.max_tasks is None and complete != expected:
        return 3
    return 0


def _criterion_view(
    judge_scores: Mapping[str, Sequence[float]],
    rows: Sequence[Mapping[str, Any]],
    label_field: str,
    *,
    judge_id: str,
    view_name: str,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    expected_ids = [str(row["artifact_id"]) for row in rows]
    available = [
        artifact_id for artifact_id in expected_ids if artifact_id in judge_scores
    ]
    if len(available) != len(expected_ids):
        return {
            "status": "NOT_COMPUTABLE",
            "value": None,
            "kendall_tau_b": None,
            "coverage": len(available) / len(expected_ids),
            "required_count": len(expected_ids),
            "observed_count": len(available),
            "missing_count": len(expected_ids) - len(available),
        }
    medians = [
        statistics.median(judge_scores[artifact_id]) for artifact_id in expected_ids
    ]
    labels = [float(row[label_field]) for row in rows]
    v4 = _load_v4_runner()
    rho = v4.spearman_rho(medians, labels)
    tau = v4.kendall_tau_b(medians, labels)
    if rho is None:
        return {
            "status": "NOT_COMPUTABLE",
            "value": None,
            "kendall_tau_b": tau,
            "coverage": 1.0,
            "required_count": len(rows),
            "observed_count": len(rows),
            "missing_count": 0,
            "reason": "constant score or label vector",
        }
    derived_seed = seed + int(_sha256_text(f"{judge_id}|{view_name}|criterion")[:8], 16)
    bootstrap = v4._bootstrap_paired_spearman(
        medians,
        labels,
        iterations=iterations,
        seed=derived_seed,
    )
    return {
        "status": "COMPUTED",
        "value": rho,
        "kendall_tau_b": tau,
        "coverage": 1.0,
        "required_count": len(rows),
        "observed_count": len(rows),
        "missing_count": 0,
        "repeat_aggregation": "median",
        "bootstrap": bootstrap,
    }


def command_compute_criterion(args: argparse.Namespace) -> int:
    config = _verify_frozen_config(args.config)
    requests = _read_json(args.requests)
    batches = _read_json(args.batches)
    criterion = _read_json(args.criterion_manifest)
    scores = _read_json(args.scores)
    _verify_embedded_fingerprint(requests, "manifest_fingerprint")
    _verify_embedded_fingerprint(batches, "manifest_fingerprint")
    _verify_embedded_fingerprint(criterion, "manifest_fingerprint")
    if requests.get("config_fingerprint") != config["config_fingerprint"]:
        raise ValueError("request/config fingerprint mismatch")
    if batches.get("request_manifest_fingerprint") != requests["manifest_fingerprint"]:
        raise ValueError("batch/request manifest mismatch")
    if scores["request_manifest_fingerprint"] != requests["manifest_fingerprint"]:
        raise ValueError("score/request manifest mismatch")
    if scores.get("batch_manifest_fingerprint") != batches["manifest_fingerprint"]:
        raise ValueError("score/batch manifest mismatch")
    if float(scores.get("provider_api_spend_usd", -1.0)) != 0.0:
        raise ValueError("score provider-spend invariant failed")
    if (
        criterion.get("panel_manifest_sha256")
        != config["source_provenance"]["v4_panel_manifest_sha256"]
    ):
        raise ValueError("criterion/config panel provenance mismatch")
    score_repeats: dict[str, dict[int, float]] = defaultdict(dict)
    for record in scores["records"]:
        cell_id = str(record["score_cell_id"])
        repeat_id = int(record["repeat_id"])
        if repeat_id in score_repeats[cell_id]:
            raise ValueError(f"duplicate score repeat {cell_id} r{repeat_id}")
        score_repeats[cell_id][repeat_id] = float(record["normalized_score"])
    records: list[dict[str, Any]] = []
    for judge in config["judges"]:
        by_artifact: dict[str, list[float]] = {}
        for row in criterion["rows"]:
            cell_id = row["score_cell_ids"][judge["judge_id"]]
            repeats = score_repeats.get(cell_id, {})
            if set(repeats) == set(range(REPEAT_COUNT)):
                by_artifact[row["artifact_id"]] = [
                    repeats[index] for index in range(REPEAT_COUNT)
                ]
        views = {
            name: _criterion_view(
                by_artifact,
                criterion["rows"],
                field,
                judge_id=judge["judge_id"],
                view_name=name,
                iterations=args.bootstrap_iters,
                seed=args.seed,
            )
            for name, field in (
                ("average", "average_score_0_5"),
                ("strict", "strict_score_0_5"),
                ("lenient", "lenient_score_0_5"),
            )
        }
        records.append(
            {
                "judge_id": judge["judge_id"],
                "role": judge["role"],
                "family": judge["family"],
                "model": judge["model"],
                "views": views,
            }
        )
    report = {
        "schema_version": "PTI_v0_criterion_v1",
        "metric_version": METRIC_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "panel_manifest_fingerprint": criterion["manifest_fingerprint"],
        "score_sha256": _sha256_file(args.scores),
        "human_panel_count": len(criterion["rows"]),
        "primary_view": "average",
        "records": records,
    }
    _write_json_atomic(args.out, report)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "judge_id",
            "role",
            "family",
            "model",
            "view",
            "status",
            "ti_m1",
            "coverage",
            "kendall_tau_b",
            "ci_low",
            "ci_high",
            "valid_replicates",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for record in records:
            for view_name, view in record["views"].items():
                bootstrap = view.get("bootstrap", {})
                writer.writerow(
                    {
                        "judge_id": record["judge_id"],
                        "role": record["role"],
                        "family": record["family"],
                        "model": record["model"],
                        "view": view_name,
                        "status": view["status"],
                        "ti_m1": view.get("value"),
                        "coverage": view.get("coverage"),
                        "kendall_tau_b": view.get("kendall_tau_b"),
                        "ci_low": bootstrap.get("ci_low"),
                        "ci_high": bootstrap.get("ci_high"),
                        "valid_replicates": bootstrap.get("valid_replicates"),
                    }
                )
    print(f"wrote {args.out} and {args.csv}: judges={len(records)}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    requests = _read_json(args.requests)
    batches = _read_json(args.batches)
    unique = _unique_requests(requests)
    expected_tasks = len(batches["batches"]) * REPEAT_COUNT
    complete_tasks = 0
    by_judge: Counter[str] = Counter()
    invalid = 0
    for batch in batches["batches"]:
        for repeat_id in range(REPEAT_COUNT):
            path = _raw_batch_path(batch["batch_id"], repeat_id, args.raw_dir)
            if not path.exists():
                continue
            try:
                _validate_raw_result(_read_json(path), batch, repeat_id, path)
                complete_tasks += 1
                by_judge[batch["judge_id"]] += 1
            except Exception:  # noqa: BLE001 - status reports invalid artifacts, never trusts them
                invalid += 1
    local_cells = sum(request["backend"] == "local" for request in unique.values())
    report = {
        "expected_cli_tasks": expected_tasks,
        "complete_cli_tasks": complete_tasks,
        "remaining_cli_tasks": expected_tasks - complete_tasks,
        "invalid_raw_tasks": invalid,
        "complete_tasks_by_judge": dict(sorted(by_judge.items())),
        "unique_score_cells": len(unique),
        "local_control_cells": local_cells,
        "provider_api_spend_usd": 0.0,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("--out", type=Path, default=FROZEN_CONFIG_PATH)
    freeze_parser.set_defaults(func=command_freeze)

    build = subparsers.add_parser("build")
    build.add_argument("--config", type=Path, default=FROZEN_CONFIG_PATH)
    build.add_argument("--out-dir", type=Path, default=RESULTS_DIR)
    build.set_defaults(func=command_build)

    score = subparsers.add_parser("score")
    score.add_argument("--config", type=Path, default=FROZEN_CONFIG_PATH)
    score.add_argument(
        "--requests", type=Path, default=RESULTS_DIR / "score_requests.json"
    )
    score.add_argument(
        "--batches", type=Path, default=RESULTS_DIR / "batch_manifest.json"
    )
    score.add_argument("--raw-dir", type=Path, default=RAW_BATCH_DIR)
    score.add_argument("--out", type=Path, default=RESULTS_DIR / "scores.json")
    score.add_argument("--workers", type=int, default=2)
    score.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    score.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    score.add_argument("--judge", action="append")
    score.add_argument("--max-tasks", type=int)
    score.set_defaults(func=command_score)

    criterion = subparsers.add_parser("compute-criterion")
    criterion.add_argument("--config", type=Path, default=FROZEN_CONFIG_PATH)
    criterion.add_argument(
        "--requests", type=Path, default=RESULTS_DIR / "score_requests.json"
    )
    criterion.add_argument(
        "--batches", type=Path, default=RESULTS_DIR / "batch_manifest.json"
    )
    criterion.add_argument(
        "--criterion-manifest",
        type=Path,
        default=RESULTS_DIR / "criterion_manifest.json",
    )
    criterion.add_argument("--scores", type=Path, default=RESULTS_DIR / "scores.json")
    criterion.add_argument(
        "--out", type=Path, default=RESULTS_DIR / "criterion" / "criterion.json"
    )
    criterion.add_argument(
        "--csv", type=Path, default=RESULTS_DIR / "criterion" / "criterion.csv"
    )
    criterion.add_argument("--bootstrap-iters", type=int, default=BOOTSTRAP_ITERATIONS)
    criterion.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    criterion.set_defaults(func=command_compute_criterion)

    status = subparsers.add_parser("status")
    status.add_argument(
        "--requests", type=Path, default=RESULTS_DIR / "score_requests.json"
    )
    status.add_argument(
        "--batches", type=Path, default=RESULTS_DIR / "batch_manifest.json"
    )
    status.add_argument("--raw-dir", type=Path, default=RAW_BATCH_DIR)
    status.set_defaults(func=command_status)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "workers", 1) < 1:
        raise ValueError("--workers must be at least one")
    if getattr(args, "retries", 1) < 1:
        raise ValueError("--retries must be at least one")
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
