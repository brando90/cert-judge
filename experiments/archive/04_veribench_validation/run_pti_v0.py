#!/usr/bin/env python3
"""Deterministic, zero-spend PTI-v0 v4 experiment pipeline.

This command never imports an LLM client, reads credentials, or performs a
network request.  It freezes and audits inputs, constructs Lean-valid probes,
inventories legacy caches, quotes score requests, and computes PTI-v0 only from
an explicitly supplied long-form score file.
"""

from __future__ import annotations

import argparse
import ast
import csv
import fcntl
import hashlib
import itertools
import json
import math
import os
import platform
import random
import re
import statistics
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from statistics import NormalDist
from typing import Any

def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        if (parent / "py_src" / "cert_judge").is_dir() and (
            parent / "pyproject.toml"
        ).is_file():
            return parent
    raise RuntimeError(f"Could not locate cert-judge repository root from {here}")


REPO_ROOT = _repo_root()
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.probe_validation import (
    LeanCompiler,
    alpha_rename_bound_identifier,
    build_bug_ladder,
    build_missing_spec_ladder,
    classify_compile_error,
    sha256_text,
    summarize_compile_error,
)
from cert_judge.pti_v0 import (
    COMPUTED,
    METRIC_VERSION,
    NOT_COMPUTABLE,
    PropertyResult,
    aggregate_property_factors,
    average_ranks,
    compute_pti,
    kendall_tau_b,
    ladder_factor,
    pti_three_property,
    spearman_rho,
    stable_geometric_mean,
)

SCHEMA_VERSION = "PTI_v0_protocol_v4"
SCORE_SCHEMA_VERSION = "PTI_v0_scores_v1"
PIPELINE_VERSION = "PTI_v0_pipeline_v1"
FROZEN_DATE = "2026-08-21"
DEFAULT_RESULTS = Path(__file__).resolve().parent / "results_pti_v0_v4"
DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent / "pti_v0_v4"
DEFAULT_POOL = DEFAULT_CONFIG_DIR / "base_pool_manifest.json"
DEFAULT_CONFIG = DEFAULT_CONFIG_DIR / "frozen_config.json"
DEFAULT_PROBES = DEFAULT_RESULTS / "probe_validity_manifest.json"
DEFAULT_PANEL_DIR = DEFAULT_RESULTS / "panel_audit"
DEFAULT_CACHE = (
    REPO_ROOT
    / "experiments"
    / "archive" / "02_neurips_reviews"
    / "results"
    / "judge_cache.json"
)
DEFAULT_DETAIL_ROWS = (
    Path(__file__).resolve().parent / "results_exp16_final_robust" / "detail_rows.csv"
)
DEFAULT_LEAN_PROJECT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src"
DEFAULT_LAKE = (
    Path.home()
    / ".elan"
    / "toolchains"
    / "leanprover--lean4---v4.22.0"
    / "bin"
    / "lake"
)
DEFAULT_CANDIDATES = REPO_ROOT / "data" / "generated_agents"
DEFAULT_GOLD_ROOTS = (
    REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    REPO_ROOT / "data" / "veribench_dataset_newest" / "lean_src" / "veribench",
)
DEFAULT_DATA = Path(__file__).resolve().parent / "data"
_CANDIDATE_RE = re.compile(r"^(?P<item>.+)__(?P<agent>agent\d+)\.lean$")
_LEGACY_THEOREM_BLOCK_RE = re.compile(
    r"(?ms)^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b.*?"
    r"(?=^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b|\Z)"
)
_CRITERION_FALLBACK_PREFIXES = (
    "openai_error:",
    "anthropic_error:",
    "parse_error on:",
    "oauth_http_",
    "oauth_error:",
    "cli_failed:",
    "extracted from malformed json",
    "extracted from prose:",
    "extracted bare number:",
)
_LOCAL_LEAN_MODULES = (
    ("VeriBench", Path("veribench.lean")),
    ("VeriBench.Common", Path("veribench/Common.lean")),
    ("VeriBench.Prelude", Path("veribench/Prelude.lean")),
)
MODEL_PRICING_USD_PER_MILLION: dict[str, dict[str, Any]] = {
    "gpt-5.3-codex": {
        "input": 1.75,
        "cached_input": 0.175,
        "output": 14.00,
        "source": "https://platform.openai.com/pricing",
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "cached_input": 0.075,
        "output": 0.60,
        "source": "https://developers.openai.com/api/docs/models/gpt-4o-mini",
    },
}


JUDGES: tuple[dict[str, Any], ...] = (
    {
        "judge_id": "gpt-5.3-codex|P8_STRICT_B",
        "kind": "llm",
        "model": "gpt-5.3-codex",
        "prompt": "P8_STRICT_B",
        "role": "primary",
        "family": "gpt-5.3-codex",
    },
    {
        "judge_id": "gpt-5.3-codex|P4_CHECKLIST",
        "kind": "llm",
        "model": "gpt-5.3-codex",
        "prompt": "P4_CHECKLIST",
        "role": "primary",
        "family": "gpt-5.3-codex",
    },
    {
        "judge_id": "gpt-5.3-codex|P1_BASELINE",
        "kind": "llm",
        "model": "gpt-5.3-codex",
        "prompt": "P1_BASELINE",
        "role": "primary",
        "family": "gpt-5.3-codex",
    },
    {
        "judge_id": "gpt-5.3-codex|BAD_STRINGY",
        "kind": "llm_control",
        "model": "gpt-5.3-codex",
        "prompt": "BAD_STRINGY",
        "role": "control",
        "family": "string_similarity_control",
    },
    {
        "judge_id": "gpt-4o-mini|P8_STRICT_B",
        "kind": "llm",
        "model": "gpt-4o-mini",
        "prompt": "P8_STRICT_B",
        "role": "primary",
        "family": "gpt-4o-mini",
    },
    {
        "judge_id": "gpt-4o-mini|P4_CHECKLIST",
        "kind": "llm",
        "model": "gpt-4o-mini",
        "prompt": "P4_CHECKLIST",
        "role": "primary",
        "family": "gpt-4o-mini",
    },
    {
        "judge_id": "editdist_e1",
        "kind": "deterministic_control",
        "model": None,
        "prompt": None,
        "role": "control",
        "family": "edit_distance_control",
    },
    {
        "judge_id": "random_r1",
        "kind": "seeded_control",
        "model": None,
        "prompt": None,
        "role": "control",
        "family": "random_control",
    },
)


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


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _fingerprint(value: Any) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return sha256_text(canonical)


def _config_fingerprint(config: Mapping[str, Any]) -> str:
    """Fingerprint score semantics while retaining source hashes as provenance."""

    payload = json.loads(json.dumps(config))
    payload.get("implementation_provenance", {}).pop("pipeline_sha256", None)
    return _fingerprint(payload)


def _score_reference(text: str) -> str:
    matches = list(_LEGACY_THEOREM_BLOCK_RE.finditer(text))
    if not matches:
        return text
    block = text[matches[-1].start() : matches[-1].end()].strip()
    return block if block else text


@contextmanager
def _exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    locked = False
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another PTI process holds {path}") from exc
        locked = True
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.flush()
        yield
    finally:
        if locked:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
        if locked:
            path.unlink(missing_ok=True)


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


def frozen_config() -> dict[str, Any]:
    prompt_source = (
        REPO_ROOT
        / "experiments"
        / "archive" / "02_neurips_reviews"
        / "utils"
        / "sensitivity_sweep.py"
    )
    bad_prompt_source = (
        Path(__file__).resolve().parent / "exp16_multi_judge_human_sets.py"
    )
    score_schema = DEFAULT_CONFIG_DIR / "score_schema.json"
    test_vectors = REPO_ROOT / "tests" / "data" / "PTI_V0_TEST_VECTORS_v4.json"
    prompt_variants = _literal_assignments(prompt_source)["PROMPT_VARIANTS"]
    bad_prompt = _literal_assignments(bad_prompt_source)["BAD_STRINGY_PROMPT"]
    judges = []
    for source_judge in JUDGES:
        judge = dict(source_judge)
        if judge["prompt"] is not None:
            template = (
                bad_prompt
                if judge["prompt"] == "BAD_STRINGY"
                else prompt_variants[judge["prompt"]]
            )
            judge["prompt_sha256"] = sha256_text(template)
            judge["prompt_static_utf8_bytes"] = len(
                template.format(reference_impl="", generated_theorem="").encode("utf-8")
            )
        else:
            judge["prompt_sha256"] = None
            judge["prompt_static_utf8_bytes"] = 0
        if judge["kind"] in {"llm", "llm_control"}:
            judge["decoding"] = {
                "temperature": 1.0,
                "top_p": 1.0,
                "max_output_tokens": 256,
                "response_contract": "JSON object with normalized score and one-sentence reasoning",
            }
        elif judge["kind"] == "seeded_control":
            judge["decoding"] = {"seed": 42}
        else:
            judge["decoding"] = {"deterministic": True}
        judge["pricing_usd_per_million_tokens"] = (
            MODEL_PRICING_USD_PER_MILLION.get(judge["model"])
            if judge["model"] is not None
            else None
        )
        judges.append(judge)
    return {
        "schema_version": SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "frozen_date": FROZEN_DATE,
        "scope": "VERIBENCH observed generated-candidate pool",
        "claim_scope": {
            "route": "Route B",
            "language": "pre-specified falsifiable behavioral diagnostics",
            "assumptions": [
                "validated alpha transformations preserve candidate semantics",
                "validated cumulative bug and missing-spec levels worsen the intended artifact dimension",
                "large violations are behaviorally disqualifying only within the frozen benchmark/rubric context",
            ],
            "high_pti": "screen evidence, not proof of trustworthiness",
        },
        "pool_policy": {
            "candidate_pattern": "<item_id>__agent<id>.lean",
            "artifact_index": "f=(item_id,agent_id,generation_id=0)",
            "expected_agents": ["agent0", "agent1", "agent2"],
            "gold_resolution": "prefer legacy root; use newest root only when absent from legacy",
            "missing_expected_artifacts": "record and exclude structurally; never impute",
            "identical_candidate_content": (
                "retain distinct typed f rows, report hash groups, and use content-deduplicated sensitivity"
            ),
        },
        "panel_policy": {
            "policy": "keep72",
            "reason": "exclude three stale unsafeMultiply rows whose historical gold is not the intended safe gold",
            "duplicate_rule": "arithmetic mean within each human pass",
            "primary_view": "mean(strict,lenient)",
            "secondary_views": ["strict", "lenient"],
            "qwk": "omitted; half-score encoding was not frozen",
        },
        "probe_policy": {
            "ladder_degradation_levels": 4,
            "levels_include_original": True,
            "prepare_local_lean_modules": [
                module_name for module_name, _source in _LOCAL_LEAN_MODULES
            ],
            "environment_binding": (
                "platform/filesystem case behavior, lake manifest, and sorted "
                "available olean-module inventory"
            ),
            "candidate_and_gold_must_elaborate": True,
            "all_transformed_levels_must_elaborate": True,
            "reject_noop_or_duplicate": True,
            "constant_judge_score_ladder": "included with C=0",
        },
        "score_policy": {
            "score_range": [0.0, 1.0],
            "judge_repeats": 3,
            "repeat_aggregation": "median",
            "property_score_coverage_threshold": 1.0,
            "missing_scores": "NOT_COMPUTABLE and DEFER; never zero",
            "cache_schema_required": SCORE_SCHEMA_VERSION,
            "token_quote_rule": "one token per UTF-8 byte plus 128 request-overhead tokens",
            "output_token_upper_bound_per_call": 256,
            "reference_preprocessing": (
                "last theorem/lemma block using the frozen Exp16 regex; "
                "fall back to the full gold when no block exists"
            ),
        },
        "criterion_policy": {
            "score_coverage_threshold": 1.0,
            "llm_lineage": "exact legacy cache key and non-fallback entry required",
            "legacy_reasoning_scope": (
                "the legacy cache stores only first-repeat reasoning; non-fallback "
                "verification applies to that stored reasoning"
            ),
            "fallback_reason_prefixes": list(_CRITERION_FALLBACK_PREFIXES),
            "deterministic_controls": "recomputed from source and compared at stored six-decimal precision",
        },
        "control_policy": {
            "editdist_e1": {
                "formula": "1 - character Levenshtein distance / max character length",
                "empty_empty_similarity": 1.0,
                "repeat_policy": "repeat the deterministic score at every repeat_id",
                "legacy_source": "experiments/04_veribench_validation/exp16_multi_judge_human_sets.py",
            },
            "random_r1": {
                "seed": 42,
                "formula": "first 12 hex digits of sha256(judge_id || seed || reference[:200] || candidate[:200]) divided by 16^12-1",
                "repeat_policy": "repeat the deterministic score at every repeat_id",
                "legacy_source": "experiments/04_veribench_validation/exp16_multi_judge_human_sets.py",
            },
        },
        "statistics": {
            "property_bootstrap_unit": "base artifact f=(i,a,q)",
            "bridge_bootstrap_unit": "judge configuration",
            "bootstrap_method": "percentile",
            "bootstrap_iterations": 10000,
            "bootstrap_seed": 0,
            "undefined_bridge_replicates": "drop and report valid replicate count",
            "bridge_primary": "Spearman",
            "bridge_robustness": "Kendall tau-b",
            "bridge_primary_population": "primary judges only",
            "bridge_secondary_population": "all primary and control judges",
            "bridge_data_role": "validation analysis; no held-out generalization claim",
            "sesoi_rho": 0.5,
            "sesoi_decision_power": (
                "simulate the frozen rho>=SESOI and bootstrap-CI-low>0 rule"
            ),
            "screen_thresholds": "not frozen; no PASS-SCREEN claim permitted",
        },
        "alpha_policy": {
            "headline_transform": "alpha-renaming only",
            "optional_diagnostics": ["RENAME", "REORDER", "STYLE"],
            "paid_inference": "requires a separate exact quote and explicit approval",
        },
        "prompt_provenance": {
            "prompt_source": _repo_path(prompt_source),
            "prompt_source_sha256": _sha256_file(prompt_source),
            "bad_prompt_source": _repo_path(bad_prompt_source),
            "bad_prompt_source_sha256": _sha256_file(bad_prompt_source),
            "reference_preprocessing_source": _repo_path(bad_prompt_source),
            "reference_preprocessing_symbol": "_extract_last_theorem_block",
        },
        "implementation_provenance": {
            "pipeline_version": PIPELINE_VERSION,
            "metric_path": "py_src/cert_judge/pti_v0.py",
            "metric_sha256": _sha256_file(
                REPO_ROOT / "py_src" / "cert_judge" / "pti_v0.py"
            ),
            "transformer_path": "py_src/cert_judge/probe_validation.py",
            "transformer_sha256": _sha256_file(
                REPO_ROOT / "py_src" / "cert_judge" / "probe_validation.py"
            ),
            "pipeline_path": _repo_path(Path(__file__)),
            "pipeline_sha256": _sha256_file(Path(__file__)),
            "config_fingerprint_exclusions": [
                "implementation_provenance.pipeline_sha256"
            ],
            "refreeze_policy": (
                "any byte change to the metric, transformer, score schema, or test "
                "vectors requires deterministic config and downstream artifact "
                "regeneration; pipeline semantics are versioned separately"
            ),
            "score_schema_path": _repo_path(score_schema),
            "score_schema_sha256": _sha256_file(score_schema),
            "test_vectors_path": _repo_path(test_vectors),
            "test_vectors_sha256": _sha256_file(test_vectors),
        },
        "judges": judges,
    }


def command_freeze_config(args: argparse.Namespace) -> int:
    config = frozen_config()
    config["config_fingerprint"] = _config_fingerprint(config)
    _write_json(args.out, config)
    judge_manifest = args.out.with_name("judge_manifest.csv")
    with judge_manifest.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "judge_id",
            "kind",
            "model",
            "prompt",
            "role",
            "family",
            "judge_repeats",
            "repeat_aggregation",
            "prompt_sha256",
            "input_price_usd_per_million",
            "cached_input_price_usd_per_million",
            "output_price_usd_per_million",
            "decoding_json",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for judge in config["judges"]:
            prices = judge["pricing_usd_per_million_tokens"] or {}
            writer.writerow(
                {
                    **{name: judge.get(name) for name in fieldnames},
                    "judge_repeats": config["score_policy"]["judge_repeats"],
                    "repeat_aggregation": config["score_policy"]["repeat_aggregation"],
                    "input_price_usd_per_million": prices.get("input"),
                    "cached_input_price_usd_per_million": prices.get("cached_input"),
                    "output_price_usd_per_million": prices.get("output"),
                    "decoding_json": json.dumps(judge["decoding"], sort_keys=True),
                }
            )
    print(f"wrote {args.out} and {judge_manifest}")
    return 0


def build_pool_manifest(
    candidate_dir: Path,
    gold_roots: Sequence[Path],
) -> dict[str, Any]:
    gold_indices: list[dict[str, Path]] = []
    for root in gold_roots:
        if not root.is_dir():
            raise ValueError(f"gold root does not exist: {root}")
        index: dict[str, Path] = {}
        for path in sorted(root.rglob("*.lean")):
            if path.name in index:
                raise ValueError(f"ambiguous basename {path.name!r} within {root}")
            index[path.name] = path
        gold_indices.append(index)

    rows: list[dict[str, Any]] = []
    observed: dict[str, set[str]] = defaultdict(set)
    for candidate in sorted(candidate_dir.glob("*.lean")):
        match = _CANDIDATE_RE.fullmatch(candidate.name)
        if match is None:
            raise ValueError(
                f"candidate filename violates frozen pattern: {candidate.name}"
            )
        item_id = match.group("item")
        agent_id = match.group("agent")
        observed[item_id].add(agent_id)
        gold_name = f"{item_id}.lean"
        matches = [
            (root_index, index[gold_name])
            for root_index, index in enumerate(gold_indices)
            if gold_name in index
        ]
        if not matches:
            raise ValueError(f"no gold basename match for {candidate.name}")
        selected_root_rank, selected = matches[0]
        rows.append(
            {
                "artifact_id": f"{item_id}|{agent_id}|q0",
                "item_id": item_id,
                "agent_id": agent_id,
                "generation_id": 0,
                "candidate_path": _repo_path(candidate),
                "candidate_sha256": _sha256_file(candidate),
                "candidate_utf8_bytes": len(candidate.read_bytes()),
                "gold_path": _repo_path(selected),
                "gold_sha256": _sha256_file(selected),
                "gold_utf8_bytes": len(selected.read_bytes()),
                "gold_resolution_root_rank": selected_root_rank,
                "gold_alternatives": [_repo_path(path) for _, path in matches[1:]],
            }
        )

    expected_agents = {"agent0", "agent1", "agent2"}
    missing = [
        {
            "artifact_id": f"{item_id}|{agent_id}|q0",
            "item_id": item_id,
            "agent_id": agent_id,
            "generation_id": 0,
            "reason": "missing_candidate_file",
        }
        for item_id in sorted(observed)
        for agent_id in sorted(expected_agents - observed[item_id])
    ]
    duplicate_hashes = {
        digest: sorted(
            row["artifact_id"] for row in rows if row["candidate_sha256"] == digest
        )
        for digest, count in Counter(row["candidate_sha256"] for row in rows).items()
        if count > 1
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "candidate_root": _repo_path(candidate_dir),
        "gold_roots_precedence": [_repo_path(root) for root in gold_roots],
        "observed_artifact_count": len(rows),
        "observed_item_count": len(observed),
        "nominal_grid_count": len(observed) * len(expected_agents),
        "missing_expected_count": len(missing),
        "missing_expected_artifacts": missing,
        "duplicate_candidate_content": duplicate_hashes,
        "manifest_fingerprint": _fingerprint(
            {
                "gold_roots_precedence": [_repo_path(root) for root in gold_roots],
                "artifacts": rows,
                "missing_expected_artifacts": missing,
            }
        ),
        "artifacts": rows,
    }


def command_freeze_pool(args: argparse.Namespace) -> int:
    manifest = build_pool_manifest(args.candidate_dir, args.gold_roots)
    _write_json(args.out, manifest)
    print(
        f"wrote {args.out}: artifacts={manifest['observed_artifact_count']} "
        f"items={manifest['observed_item_count']} missing={manifest['missing_expected_count']}"
    )
    return 0


def _compile_path_code(compiler: LeanCompiler, path: Path) -> dict[str, Any]:
    result = compiler.compile(path.read_text(encoding="utf-8", errors="strict"))
    return {
        "ok": result.ok,
        "returncode": result.returncode,
        "error_class": classify_compile_error(result),
        "error": None if result.ok else summarize_compile_error(result.output),
    }


def _available_olean_modules(project_root: Path) -> list[str]:
    roots: list[tuple[str, Path]] = [
        ("local", project_root / ".lake" / "build" / "lib" / "lean")
    ]
    packages = project_root / ".lake" / "packages"
    if packages.is_dir():
        roots.extend(
            (
                f"package:{package.name}",
                package / ".lake" / "build" / "lib" / "lean",
            )
            for package in sorted(packages.iterdir())
            if package.is_dir()
        )
    modules: list[str] = []
    for prefix, root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.olean")):
            module = ".".join(path.relative_to(root).with_suffix("").parts)
            modules.append(f"{prefix}:{module}")
    return sorted(set(modules))


def _filesystem_case_sensitive(root: Path) -> bool:
    """Measure case sensitivity on the filesystem that contains ``root``."""

    with tempfile.TemporaryDirectory(prefix=".pti-case-probe-", dir=root) as temp_dir:
        probe = Path(temp_dir) / "CaseSensitiveProbe"
        probe.write_text("probe\n", encoding="utf-8")
        return not (Path(temp_dir) / "casesensitiveprobe").exists()


def _prepare_lean_environment(compiler: LeanCompiler) -> dict[str, Any]:
    project = compiler.project_root
    lake_manifest = project / "lake-manifest.json"
    lakefile = project / "lakefile.toml"
    if not lake_manifest.is_file():
        raise ValueError(
            "resolved lake-manifest.json is required; run lake update before audit"
        )
    prepared: list[dict[str, Any]] = []
    for module_name, relative_source in _LOCAL_LEAN_MODULES:
        source = project / relative_source
        result = compiler.compile_module(module_name, source)
        error_class = classify_compile_error(result)
        record = {
            "module": module_name,
            "source_path": _repo_path(source),
            "source_sha256": _sha256_file(source),
            "ok": result.ok,
            "returncode": result.returncode,
            "error_class": error_class,
            "error": None if result.ok else summarize_compile_error(result.output),
        }
        prepared.append(record)
        if not result.ok:
            raise ValueError(
                f"failed to prepare local Lean module {module_name}: "
                f"{error_class}: {record['error']}"
            )
    modules = _available_olean_modules(project)
    return {
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "filesystem_case_sensitive": _filesystem_case_sensitive(project),
        "module_case_caveat": (
            "local sources and oleans use lowercase veribench paths while some "
            "imports use VeriBench; successful resolution is platform-dependent"
        ),
        "lakefile_path": _repo_path(lakefile),
        "lakefile_sha256": _sha256_file(lakefile),
        "lake_manifest_path": _repo_path(lake_manifest),
        "lake_manifest_sha256": _sha256_file(lake_manifest),
        "prepared_local_modules": prepared,
        "available_olean_module_count": len(modules),
        "available_olean_modules_sha256": sha256_text("\n".join(modules)),
        "available_olean_modules": modules,
    }


def _base_failure_reason(
    candidate_compile: Mapping[str, Any], gold_compile: Mapping[str, Any]
) -> str | None:
    failures: list[str] = []
    if not candidate_compile["ok"]:
        failures.append(f"candidate_{candidate_compile['error_class']}")
    if not gold_compile["ok"]:
        failures.append(f"gold_{gold_compile['error_class']}")
    return "+".join(failures) or None


def _step_record(step: Any) -> dict[str, Any] | None:
    if step is None:
        return None
    return {
        "kind": step.kind,
        "target": step.target,
        "before": step.before,
        "after": step.after,
        "start": step.start,
        "end": step.end,
    }


def _audit_artifact(
    artifact: Mapping[str, Any],
    compiler: LeanCompiler,
    *,
    levels: int,
    candidate_compile: Mapping[str, Any],
    gold_compile: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_path = REPO_ROOT / artifact["candidate_path"]
    code = candidate_path.read_text(encoding="utf-8", errors="strict")
    base_valid = candidate_compile["ok"] and gold_compile["ok"]
    base_failure_reason = _base_failure_reason(candidate_compile, gold_compile)
    row: dict[str, Any] = {
        "artifact_id": artifact["artifact_id"],
        "item_id": artifact["item_id"],
        "agent_id": artifact["agent_id"],
        "generation_id": artifact["generation_id"],
        "candidate_sha256": artifact["candidate_sha256"],
        "candidate_path": artifact["candidate_path"],
        "candidate_utf8_bytes": artifact["candidate_utf8_bytes"],
        "gold_sha256": artifact["gold_sha256"],
        "gold_path": artifact["gold_path"],
        "gold_utf8_bytes": artifact["gold_utf8_bytes"],
        "candidate_compile": candidate_compile,
        "gold_compile": gold_compile,
        "P_eq": {
            "structurally_valid": base_valid,
            "reason": base_failure_reason,
            "self_pair_sha256": artifact["candidate_sha256"] if base_valid else None,
        },
    }
    if not base_valid:
        for property_name in ("P_bm", "P_ms", "P_eqalpha"):
            row[property_name] = {
                "structurally_valid": False,
                "reason": base_failure_reason,
            }
        return row

    try:
        alpha = alpha_rename_bound_identifier(code)
    except ValueError as exc:
        row["P_eqalpha"] = {"structurally_valid": False, "reason": str(exc)}
    else:
        alpha_compile = compiler.compile(alpha.code)
        alpha_error_class = classify_compile_error(alpha_compile)
        if not alpha_compile.ok:
            row["P_eqalpha"] = {
                "structurally_valid": False,
                "reason": f"alpha_{alpha_error_class}",
                "compile": {
                    "ok": False,
                    "returncode": alpha_compile.returncode,
                    "error_class": alpha_error_class,
                    "error": summarize_compile_error(alpha_compile.output),
                },
            }
        else:
            row["P_eqalpha"] = {
                "structurally_valid": True,
                "reason": None,
                "original_sha256": artifact["candidate_sha256"],
                "alpha_sha256": alpha.sha256,
                "alpha_utf8_bytes": len(alpha.code.encode("utf-8")),
                "declaration": alpha.declaration,
                "old_name": alpha.old_name,
                "new_name": alpha.new_name,
                "occurrence_count": alpha.occurrence_count,
                "compile": {
                    "ok": True,
                    "returncode": alpha_compile.returncode,
                    "error_class": alpha_error_class,
                    "error": None,
                },
            }

    for property_name, builder in (
        ("P_bm", build_bug_ladder),
        ("P_ms", build_missing_spec_ladder),
    ):
        rejected_compile_classes: Counter[str] = Counter()

        def validates(
            candidate: str,
            rejected: Counter[str] = rejected_compile_classes,
        ) -> bool:
            result = compiler.compile(candidate)
            if not result.ok:
                rejected[classify_compile_error(result)] += 1
            return result.ok

        try:
            ladder = builder(code, levels=levels, validate=validates)
            row[property_name] = {
                "structurally_valid": True,
                "reason": None,
                "rejected_compile_classes": dict(
                    sorted(rejected_compile_classes.items())
                ),
                "levels": [
                    {
                        "level": artifact_level.level,
                        "sha256": artifact_level.sha256,
                        "utf8_bytes": len(artifact_level.code.encode("utf-8")),
                        "step": _step_record(artifact_level.step),
                        "compile": {"ok": True},
                    }
                    for artifact_level in ladder
                ],
            }
        except ValueError as exc:
            row[property_name] = {
                "structurally_valid": False,
                "reason": str(exc),
                "rejected_compile_classes": dict(
                    sorted(rejected_compile_classes.items())
                ),
            }
    return row


def _command_audit_probes_unlocked(args: argparse.Namespace) -> int:
    pool = _read_json(args.pool)
    compiler = LeanCompiler(
        args.lean_project, args.lake_bin, timeout_seconds=args.timeout
    )
    lean_environment = _prepare_lean_environment(compiler)
    rows: list[dict[str, Any]] = []
    artifacts = pool["artifacts"]
    unique_paths = sorted(
        {
            str(REPO_ROOT / artifact[path_field])
            for artifact in artifacts
            for path_field in ("candidate_path", "gold_path")
        }
    )
    compile_results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_compile_path_code, compiler, Path(path)): path
            for path in unique_paths
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            compile_results[futures[future]] = future.result()
            if completed % 100 == 0 or completed == len(futures):
                print(f"compiled originals {completed}/{len(futures)}", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                _audit_artifact,
                artifact,
                compiler,
                levels=args.levels,
                candidate_compile=compile_results[
                    str(REPO_ROOT / artifact["candidate_path"])
                ],
                gold_compile=compile_results[str(REPO_ROOT / artifact["gold_path"])],
            ): artifact
            for artifact in artifacts
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if completed % 25 == 0 or completed == len(futures):
                print(f"audited {completed}/{len(futures)}", flush=True)
    rows.sort(key=lambda row: row["artifact_id"])
    counts = {
        property_name: sum(row[property_name]["structurally_valid"] for row in rows)
        for property_name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
    }
    reason_counts = {
        property_name: dict(
            sorted(
                Counter(
                    row[property_name].get("reason") or "valid" for row in rows
                ).items()
            )
        )
        for property_name in counts
    }
    transformer_path = REPO_ROOT / "py_src" / "cert_judge" / "probe_validation.py"
    fingerprint_payload = {
        "pool_manifest_fingerprint": pool["manifest_fingerprint"],
        "lean_toolchain": "leanprover/lean4:v4.22.0",
        "ladder_degradation_levels": args.levels,
        "transformer_sha256": _sha256_file(transformer_path),
        "lean_environment": lean_environment,
        "artifacts": rows,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "pool_manifest_fingerprint": pool["manifest_fingerprint"],
        "lean_project": _repo_path(args.lean_project),
        "lake_bin": str(args.lake_bin.resolve()),
        "lean_toolchain": "leanprover/lean4:v4.22.0",
        "transformer_path": _repo_path(transformer_path),
        "transformer_sha256": fingerprint_payload["transformer_sha256"],
        "lean_environment": lean_environment,
        "ladder_degradation_levels": args.levels,
        "artifact_count": len(rows),
        "valid_probe_counts": counts,
        "invalid_probe_counts": {
            key: len(rows) - value for key, value in counts.items()
        },
        "reason_counts": reason_counts,
        "manifest_fingerprint": _fingerprint(fingerprint_payload),
        "artifacts": rows,
    }
    _write_json(args.out, manifest)
    print(f"wrote {args.out}: {counts}")
    return 0


def command_audit_probes(args: argparse.Namespace) -> int:
    with _exclusive_lock(args.out.with_suffix(args.out.suffix + ".lock")):
        return _command_audit_probes_unlocked(args)


def _load_tsv_pass(path: Path) -> tuple[dict[tuple[str, str], float], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (row["gold_file"].strip(), row["candidate_file"].strip())
            grouped[key].append(float(row["human_score_0_5"]))
    values = {key: statistics.fmean(scores) for key, scores in grouped.items()}
    return values, {
        "path": _repo_path(path),
        "sha256": _sha256_file(path),
        "raw_rows": sum(len(scores) for scores in grouped.values()),
        "unique_rows": len(grouped),
        "duplicate_groups": {
            f"{key[0]}::{key[1]}": scores
            for key, scores in grouped.items()
            if len(scores) > 1
        },
    }


def command_audit_panel(args: argparse.Namespace) -> int:
    strict, strict_meta = _load_tsv_pass(args.strict)
    lenient, lenient_meta = _load_tsv_pass(args.lenient)
    checked, checked_meta = _load_tsv_pass(args.checked_average)
    common = sorted(set(strict) & set(lenient))
    unsafe = [key for key in common if key[0] == "0_unsafeMultiply_safe.lean"]
    if args.policy != "keep72":
        raise ValueError("only the evidence-supported keep72 policy is implemented")
    included = [key for key in common if key not in unsafe]
    all_rows = [
        {
            "gold_file": key[0],
            "candidate_file": key[1],
            "strict_score_0_5": strict[key],
            "lenient_score_0_5": lenient[key],
            "average_score_0_5": (strict[key] + lenient[key]) / 2.0,
            "checked_average_score_0_5": checked.get(key),
            "checked_average_matches": (
                checked.get(key) is not None
                and abs(checked[key] - (strict[key] + lenient[key]) / 2.0) <= 1e-12
            ),
        }
        for key in common
    ]
    rows = [
        row
        for row in all_rows
        if (row["gold_file"], row["candidate_file"]) in set(included)
    ]
    all_mismatches = [row for row in all_rows if not row["checked_average_matches"]]
    mismatches = [row for row in rows if not row["checked_average_matches"]]
    historical_dir = (
        Path(__file__).resolve().parent
        / "results"
        / "veribench"
        / "security"
        / "0_unsafeMultiply_safe"
    )
    vulnerable_gold = (
        REPO_ROOT
        / "data"
        / "veribench_dataset"
        / "lean_src"
        / "veribench"
        / "security_6858"
        / "1_unsafeMultiply.lean"
    )
    safe_gold = vulnerable_gold.parent / "safe" / "1_unsafeMultiply_safe.lean"
    agent_mapping = {
        "agent0": historical_dir / "agent_codex.lean",
        "agent1": historical_dir / "agent_claude.lean",
        "agent2": historical_dir / "agent_llama.lean",
    }
    provenance = {
        "historical_gold": {
            "path": _repo_path(historical_dir / "gold.lean"),
            "sha256": _sha256_file(historical_dir / "gold.lean"),
        },
        "current_vulnerable_gold": {
            "path": _repo_path(vulnerable_gold),
            "sha256": _sha256_file(vulnerable_gold),
        },
        "intended_safe_gold": {
            "path": _repo_path(safe_gold),
            "sha256": _sha256_file(safe_gold),
        },
        "historical_gold_matches_vulnerable": (
            _sha256_file(historical_dir / "gold.lean") == _sha256_file(vulnerable_gold)
        ),
        "historical_gold_matches_intended_safe": (
            _sha256_file(historical_dir / "gold.lean") == _sha256_file(safe_gold)
        ),
        "candidate_generation_mapping": [
            {
                "agent_id": agent_id,
                "historical_path": _repo_path(historical_path),
                "historical_sha256": _sha256_file(historical_path),
                "current_path": _repo_path(
                    DEFAULT_CANDIDATES / f"1_unsafeMultiply_safe__{agent_id}.lean"
                ),
                "current_sha256": _sha256_file(
                    DEFAULT_CANDIDATES / f"1_unsafeMultiply_safe__{agent_id}.lean"
                ),
                "content_matches": (
                    _sha256_file(historical_path)
                    == _sha256_file(
                        DEFAULT_CANDIDATES / f"1_unsafeMultiply_safe__{agent_id}.lean"
                    )
                ),
            }
            for agent_id, historical_path in agent_mapping.items()
        ],
        "conclusion": "candidate generations map, but gold provenance fails; keep72 is required",
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "policy": args.policy,
        "source_files": {
            "strict": strict_meta,
            "lenient": lenient_meta,
            "checked_average": checked_meta,
        },
        "common_before_policy": len(common),
        "excluded_count": len(unsafe),
        "included_count": len(rows),
        "excluded_rows": [
            {
                "gold_file": key[0],
                "candidate_file": key[1],
                "strict_score_0_5": strict[key],
                "lenient_score_0_5": lenient[key],
                "reason": "stale key points to vulnerable gold; safe-gold provenance failed",
            }
            for key in unsafe
        ],
        "unsafe_multiply_provenance": provenance,
        "checked_average_mismatch_before_policy_count": len(all_mismatches),
        "checked_average_mismatches_before_policy": all_mismatches,
        "checked_average_mismatch_count": len(mismatches),
        "checked_average_mismatches": mismatches,
        "manifest_fingerprint": _fingerprint(
            {
                "policy": args.policy,
                "source_sha256": {
                    "strict": strict_meta["sha256"],
                    "lenient": lenient_meta["sha256"],
                    "checked_average": checked_meta["sha256"],
                },
                "excluded": unsafe,
                "unsafe_multiply_provenance": provenance,
                "rows": rows,
            }
        ),
        "rows": rows,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.out_dir / "panel_manifest.json", manifest)
    with (args.out_dir / "canonical_panel_72.tsv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"wrote {args.out_dir}: included={len(rows)} excluded={len(unsafe)} "
        f"checked_average_mismatches={len(mismatches)}"
    )
    return 0


def _request_points(probes: Mapping[str, Any]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for row in probes["artifacts"]:
        gold_source = (REPO_ROOT / row["gold_path"]).read_text(encoding="utf-8")
        if sha256_text(gold_source) != row["gold_sha256"]:
            raise ValueError(f"gold hash drift for {row['artifact_id']}")
        reference = _score_reference(gold_source)
        common = {
            "artifact_id": row["artifact_id"],
            "gold_source_sha256": row["gold_sha256"],
            "reference_preprocessing": "last_theorem_or_lemma_block_v1",
            "reference_sha256": sha256_text(reference),
            "reference_utf8_bytes": len(reference.encode("utf-8")),
        }
        if row["P_eq"]["structurally_valid"]:
            points.append(
                {
                    **common,
                    "probe_type": "eq",
                    "level": 0,
                    "variant": "self",
                    "candidate_sha256": row["candidate_sha256"],
                    "candidate_utf8_bytes": row["candidate_utf8_bytes"],
                    "reference_preprocessing": "self_pair",
                    "reference_sha256": row["candidate_sha256"],
                    "reference_utf8_bytes": row["candidate_utf8_bytes"],
                }
            )
        for property_name, probe_type in (("P_bm", "bm"), ("P_ms", "ms")):
            if row[property_name]["structurally_valid"]:
                for level in row[property_name]["levels"]:
                    points.append(
                        {
                            **common,
                            "probe_type": probe_type,
                            "level": level["level"],
                            "variant": f"L{level['level']}",
                            "candidate_sha256": level["sha256"],
                            "candidate_utf8_bytes": level["utf8_bytes"],
                        }
                    )
        if row["P_eqalpha"]["structurally_valid"]:
            points.extend(
                [
                    {
                        **common,
                        "probe_type": "eqalpha",
                        "level": 0,
                        "variant": "original",
                        "candidate_sha256": row["P_eqalpha"]["original_sha256"],
                        "candidate_utf8_bytes": row["candidate_utf8_bytes"],
                    },
                    {
                        **common,
                        "probe_type": "eqalpha",
                        "level": 0,
                        "variant": "alpha",
                        "candidate_sha256": row["P_eqalpha"]["alpha_sha256"],
                        "candidate_utf8_bytes": row["P_eqalpha"]["alpha_utf8_bytes"],
                    },
                ]
            )
    return points


def command_build_requests(args: argparse.Namespace) -> int:
    probes = _read_json(args.probe_manifest)
    config = _read_json(args.config)
    points = _request_points(probes)
    requests: list[dict[str, Any]] = []
    for judge in config["judges"]:
        for point in points:
            request = {
                **point,
                "judge_id": judge["judge_id"],
                "judge_kind": judge["kind"],
                "model": judge["model"],
                "prompt": judge["prompt"],
                "prompt_sha256": judge["prompt_sha256"],
                "role": judge["role"],
                "repeat_count": config["score_policy"]["judge_repeats"],
            }
            if request["model"] is not None:
                request["input_token_upper_bound_per_call"] = (
                    int(judge["prompt_static_utf8_bytes"])
                    + int(request["candidate_utf8_bytes"])
                    + int(request["reference_utf8_bytes"])
                    + 128
                )
                request["output_token_upper_bound_per_call"] = int(
                    config["score_policy"]["output_token_upper_bound_per_call"]
                )
                request["pricing_usd_per_million_tokens"] = judge[
                    "pricing_usd_per_million_tokens"
                ]
            else:
                request["input_token_upper_bound_per_call"] = 0
                request["output_token_upper_bound_per_call"] = 0
                request["pricing_usd_per_million_tokens"] = None
            cell_identity = {
                "score_schema_version": SCORE_SCHEMA_VERSION,
                "judge_id": request["judge_id"],
                "candidate_sha256": request["candidate_sha256"],
                "reference_sha256": request["reference_sha256"],
                "repeat_count": request["repeat_count"],
                "prompt_provenance": config["prompt_provenance"],
            }
            request["score_cell_id"] = sha256_text(
                json.dumps(cell_identity, sort_keys=True, separators=(",", ":"))
            )
            requests.append(request)
    counts = Counter(point["probe_type"] for point in points)
    unique_cells = {request["score_cell_id"]: request for request in requests}
    manifest = {
        "schema_version": "PTI_v0_score_requests_v1",
        "metric_version": METRIC_VERSION,
        "probe_manifest_fingerprint": probes["manifest_fingerprint"],
        "point_count_per_judge": len(points),
        "point_counts_by_probe": dict(sorted(counts.items())),
        "judge_count": len(config["judges"]),
        "conceptual_request_cell_count": len(requests),
        "unique_score_cell_count": len(unique_cells),
        "paid_call_count_before_cache": sum(
            request["repeat_count"]
            for request in unique_cells.values()
            if request["judge_kind"] in {"llm", "llm_control"}
        ),
        "config_fingerprint": config.get("config_fingerprint"),
        "manifest_fingerprint": _fingerprint(
            {
                "probe_manifest_fingerprint": probes["manifest_fingerprint"],
                "config_fingerprint": config.get("config_fingerprint"),
                "requests": requests,
            }
        ),
        "requests": requests,
    }
    _write_json(args.out, manifest)
    print(
        f"wrote {args.out}: points/judge={len(points)} cells={len(requests)} "
        f"unique={len(unique_cells)} paid_calls={manifest['paid_call_count_before_cache']}"
    )
    return 0


def _replay_probe_level(code: str, level: Mapping[str, Any]) -> str:
    step = level.get("step")
    if step is None:
        if int(level["level"]) != 0:
            raise ValueError("only probe level zero may omit a transformation step")
        transformed = code
    else:
        start = int(step["start"])
        end = int(step["end"])
        before = str(step["before"])
        if code[start:end] != before:
            raise ValueError(
                f"probe replay span mismatch at level {level['level']}: "
                f"expected {before!r}, found {code[start:end]!r}"
            )
        if step["kind"] == "bug_mutation":
            replacement = str(step["after"])
        elif step["kind"] == "missing_spec_removal":
            replacement = "\n" * max(1, before.count("\n"))
        else:
            raise ValueError(f"unsupported recorded probe step {step['kind']!r}")
        transformed = code[:start] + replacement + code[end:]
    if sha256_text(transformed) != level["sha256"]:
        raise ValueError(
            f"probe replay hash mismatch at level {level['level']}: "
            f"expected {level['sha256']}"
        )
    return transformed


def _probe_content_pairs(
    probes: Mapping[str, Any],
) -> dict[tuple[str, str, int, str], tuple[str, str]]:
    pairs: dict[tuple[str, str, int, str], tuple[str, str]] = {}
    for row in probes["artifacts"]:
        artifact_id = str(row["artifact_id"])
        candidate = (REPO_ROOT / row["candidate_path"]).read_text(encoding="utf-8")
        gold_source = (REPO_ROOT / row["gold_path"]).read_text(encoding="utf-8")
        if sha256_text(candidate) != row["candidate_sha256"]:
            raise ValueError(f"candidate hash drift for {artifact_id}")
        if sha256_text(gold_source) != row["gold_sha256"]:
            raise ValueError(f"gold hash drift for {artifact_id}")
        reference = _score_reference(gold_source)
        if row["P_eq"]["structurally_valid"]:
            pairs[(artifact_id, "eq", 0, "self")] = (candidate, candidate)
        for property_name, probe_type in (("P_bm", "bm"), ("P_ms", "ms")):
            probe = row[property_name]
            if not probe["structurally_valid"]:
                continue
            current = candidate
            for level in probe["levels"]:
                current = _replay_probe_level(current, level)
                level_number = int(level["level"])
                pairs[(artifact_id, probe_type, level_number, f"L{level_number}")] = (
                    current,
                    reference,
                )
        if row["P_eqalpha"]["structurally_valid"]:
            alpha = alpha_rename_bound_identifier(candidate).code
            if sha256_text(alpha) != row["P_eqalpha"]["alpha_sha256"]:
                raise ValueError(f"alpha hash drift for {artifact_id}")
            pairs[(artifact_id, "eqalpha", 0, "original")] = (
                candidate,
                reference,
            )
            pairs[(artifact_id, "eqalpha", 0, "alpha")] = (alpha, reference)
    return pairs


def _edit_similarity(reference: str, candidate: str) -> float:
    if not reference and not candidate:
        return 1.0
    try:
        from rapidfuzz.distance import Levenshtein

        distance = int(Levenshtein.distance(reference, candidate))
    except ImportError:
        previous = list(range(len(candidate) + 1))
        for row_index, reference_character in enumerate(reference, start=1):
            current = [row_index]
            for column_index, candidate_character in enumerate(candidate, start=1):
                current.append(
                    min(
                        previous[column_index] + 1,
                        current[column_index - 1] + 1,
                        previous[column_index - 1]
                        + (reference_character != candidate_character),
                    )
                )
            previous = current
        distance = previous[-1]
    return max(0.0, min(1.0, 1.0 - distance / max(len(reference), len(candidate))))


def _deterministic_random_score(
    judge_id: str, reference: str, candidate: str, *, seed: int
) -> float:
    digest = sha256_text(judge_id + str(seed) + reference[:200] + candidate[:200])
    return int(digest[:12], 16) / float(16**12 - 1)


def command_materialize_local_controls(args: argparse.Namespace) -> int:
    probes = _read_json(args.probe_manifest)
    requests = _read_json(args.requests)
    config = _read_json(args.config)
    if requests["probe_manifest_fingerprint"] != probes["manifest_fingerprint"]:
        raise ValueError("request/probe manifest fingerprint mismatch")
    if requests.get("config_fingerprint") != config.get("config_fingerprint"):
        raise ValueError("request/config fingerprint mismatch")
    pairs = _probe_content_pairs(probes)
    judges = {judge["judge_id"]: judge for judge in config["judges"]}
    local_kinds = {"deterministic_control", "seeded_control"}
    unique_requests = {
        request["score_cell_id"]: request
        for request in requests["requests"]
        if request["judge_kind"] in local_kinds
    }
    records: list[dict[str, Any]] = []
    cells_by_judge: Counter[str] = Counter()
    for cell_id, request in sorted(unique_requests.items()):
        key = (
            str(request["artifact_id"]),
            str(request["probe_type"]),
            int(request["level"]),
            str(request["variant"]),
        )
        candidate, reference = pairs[key]
        if sha256_text(candidate) != request["candidate_sha256"]:
            raise ValueError(f"candidate request hash mismatch for {cell_id}")
        if sha256_text(reference) != request["reference_sha256"]:
            raise ValueError(f"reference request hash mismatch for {cell_id}")
        judge = judges[request["judge_id"]]
        if judge["kind"] == "deterministic_control":
            value = _edit_similarity(reference, candidate)
        elif judge["kind"] == "seeded_control":
            value = _deterministic_random_score(
                judge["judge_id"],
                reference,
                candidate,
                seed=int(judge["decoding"]["seed"]),
            )
        else:
            raise ValueError(f"unsupported local control kind {judge['kind']!r}")
        cells_by_judge[judge["judge_id"]] += 1
        records.extend(
            {
                "score_cell_id": cell_id,
                "repeat_id": repeat_id,
                "normalized_score": value,
            }
            for repeat_id in range(int(request["repeat_count"]))
        )
    payload = {
        "schema_version": SCORE_SCHEMA_VERSION,
        "metric_version": METRIC_VERSION,
        "request_manifest_fingerprint": requests["manifest_fingerprint"],
        "source": "deterministic local controls; no inference or network access",
        "control_policy": config["control_policy"],
        "complete_cells_by_judge": dict(sorted(cells_by_judge.items())),
        "record_count": len(records),
        "records": records,
    }
    _write_json(args.out, payload)
    print(
        f"wrote {args.out}: cells={len(unique_requests)} records={len(records)} "
        f"judges={len(cells_by_judge)}"
    )
    return 0


def _cache_key_parts(
    key: str,
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    parts = key.split("|")
    if len(parts) == 3:
        return None, parts[0], None, parts[-2], parts[-1]
    if len(parts) >= 5:
        return "|".join(parts[:-4]), parts[-4], parts[-3], parts[-2], parts[-1]
    return None, None, None, None, None


def _fallback_reason_class(reasoning: Any) -> str | None:
    if not isinstance(reasoning, str):
        return "missing_reasoning"
    normalized = reasoning.strip().lower()
    for prefix in _CRITERION_FALLBACK_PREFIXES:
        if normalized.startswith(prefix):
            return prefix.rstrip(":")
    return None


def command_inventory_cache(args: argparse.Namespace) -> int:
    requests = _read_json(args.requests)
    cache = _read_json(args.cache)
    if not isinstance(cache, dict):
        raise TypeError("legacy cache must contain a JSON object")
    repeat_histogram: Counter[str] = Counter()
    malformed = 0
    lookup: set[tuple[str, str, str]] = set()
    detailed_lookup: dict[
        tuple[str, str, str], list[tuple[str | None, str | None, Mapping[str, Any]]]
    ] = defaultdict(list)
    for key, value in cache.items():
        namespace, model, prompt_hash, candidate_hash, reference_hash = (
            _cache_key_parts(key)
        )
        if model and candidate_hash and reference_hash:
            lookup.add((model, candidate_hash, reference_hash))
            if isinstance(value, Mapping):
                detailed_lookup[(model, candidate_hash, reference_hash)].append(
                    (namespace, prompt_hash, value)
                )
        scores = value.get("scores") if isinstance(value, dict) else None
        if isinstance(scores, list):
            repeat_histogram[str(len(scores))] += 1
        else:
            repeat_histogram["missing"] += 1
            malformed += 1
    potential: set[str] = set()
    prompt_matched: set[str] = set()
    repeat_matched: set[str] = set()
    fallback_matched: set[str] = set()
    for request in requests["requests"]:
        if request["model"] is None:
            continue
        key = (
            request["model"],
            request["candidate_sha256"],
            request["reference_sha256"],
        )
        if key in lookup:
            potential.add(request["score_cell_id"])
        for _namespace, prompt_hash, entry in detailed_lookup.get(key, []):
            if prompt_hash != request.get("prompt_sha256"):
                continue
            prompt_matched.add(request["score_cell_id"])
            scores = entry.get("scores")
            if isinstance(scores, list) and len(scores) == request["repeat_count"]:
                repeat_matched.add(request["score_cell_id"])
            if _fallback_reason_class(entry.get("reasoning")) is not None:
                fallback_matched.add(request["score_cell_id"])
    report = {
        "schema_version": "PTI_v0_cache_inventory_v1",
        "metric_version": METRIC_VERSION,
        "cache_path": _repo_path(args.cache),
        "cache_sha256": _sha256_file(args.cache),
        "legacy_entry_count": len(cache),
        "repeat_count_histogram": dict(sorted(repeat_histogram.items())),
        "malformed_entry_count": malformed,
        "potential_content_model_matches": len(potential),
        "prompt_content_model_matches": len(prompt_matched),
        "prompt_content_model_repeat_matches": len(repeat_matched),
        "fallback_matched_request_cells": len(fallback_matched),
        "admissible_request_cells": 0,
        "admissible_paid_calls": 0,
        "reason_no_admissible_entries": (
            "legacy entries lack the PTI score schema, scorer/decoding version, and "
            "success contract; exact prompt/content/repeat matches are inventoried "
            "but remain inadmissible, and some legacy entries are error fallbacks"
        ),
        "request_manifest_fingerprint": requests["manifest_fingerprint"],
    }
    _write_json(args.out, report)
    print(
        f"wrote {args.out}: legacy={len(cache)} potential={len(potential)} admissible=0"
    )
    return 0


def command_quote_spend(args: argparse.Namespace) -> int:
    requests = _read_json(args.requests)
    cache = _read_json(args.cache_inventory)
    requested_transforms = {transform.upper() for transform in args.transforms}
    available_transforms = {
        request["variant"].upper() for request in requests["requests"]
    }
    select_all = "ALL" in requested_transforms
    unavailable_transforms = sorted(
        (requested_transforms - {"ALL"}) - available_transforms
    )
    selected = {
        request["score_cell_id"]: request
        for request in requests["requests"]
        if (select_all or request["variant"].upper() in requested_transforms)
        and request["judge_kind"] in {"llm", "llm_control"}
    }
    grouped: dict[str, dict[str, Any]] = {}
    for request in selected.values():
        model = request["model"]
        assert model is not None
        record = grouped.setdefault(
            model,
            {
                "request_cells": 0,
                "repeats_per_cell": request["repeat_count"],
                "missing_calls": 0,
                "input_token_upper_bound": 0,
                "output_token_upper_bound": 0,
                "pricing_usd_per_million_tokens": request[
                    "pricing_usd_per_million_tokens"
                ],
            },
        )
        record["request_cells"] += 1
        record["missing_calls"] += request["repeat_count"]
        record["input_token_upper_bound"] += (
            request["input_token_upper_bound_per_call"] * request["repeat_count"]
        )
        record["output_token_upper_bound"] += (
            request["output_token_upper_bound_per_call"] * request["repeat_count"]
        )
    for record in grouped.values():
        prices = record["pricing_usd_per_million_tokens"]
        record["upper_bound_cost_usd"] = (
            record["input_token_upper_bound"] * prices["input"]
            + record["output_token_upper_bound"] * prices["output"]
        ) / 1_000_000
    total_cost = sum(record["upper_bound_cost_usd"] for record in grouped.values())
    cost_status = (
        "NOT_QUOTABLE_UNVALIDATED_TRANSFORM"
        if unavailable_transforms
        else "QUOTED_CONSERVATIVE_UPPER_BOUND"
    )
    report = {
        "schema_version": "PTI_v0_spend_quote_v1",
        "metric_version": METRIC_VERSION,
        "quote_date": FROZEN_DATE,
        "transforms": sorted(requested_transforms),
        "unavailable_transforms": unavailable_transforms,
        "cache_admissible_paid_calls": cache["admissible_paid_calls"],
        "models": grouped,
        "total_missing_calls": sum(
            record["missing_calls"] for record in grouped.values()
        ),
        "token_bound": (
            "input <= UTF-8 bytes of rendered prompt + 128 protocol tokens; "
            "output <= 256 tokens; all input billed uncached"
        ),
        "cost_status": cost_status,
        "upper_bound_cost_usd": None if unavailable_transforms else total_cost,
        "approval_status": "NOT_REQUESTED",
        "execution_command": None,
        "no_api_guarantee": "this CLI contains no inference client or credential loading code",
    }
    _write_json(args.out, report)
    print(
        f"wrote {args.out}: missing_calls={report['total_missing_calls']} "
        f"upper_bound_cost_usd={report['upper_bound_cost_usd']} status={cost_status}"
    )
    return 0


def _property_status(required_count: int) -> dict[str, Any]:
    return asdict(
        PropertyResult(
            status=NOT_COMPUTABLE,
            value=None,
            coverage=0.0,
            required_count=required_count,
            observed_count=0,
            missing_count=required_count,
            zero_count=0,
        )
    )


def _score_use_key(request: Mapping[str, Any]) -> tuple[str, str, str, int, str]:
    return (
        str(request["judge_id"]),
        str(request["artifact_id"]),
        str(request["probe_type"]),
        int(request["level"]),
        str(request["variant"]),
    )


def _load_score_cells(
    score_path: Path,
    requests: Mapping[str, Any],
) -> tuple[dict[str, list[float]], dict[str, Any]]:
    payload = _read_json(score_path)
    if payload.get("schema_version") != SCORE_SCHEMA_VERSION:
        raise ValueError(f"scores must use schema_version={SCORE_SCHEMA_VERSION}")
    if payload.get("metric_version") != METRIC_VERSION:
        raise ValueError(f"scores must use metric_version={METRIC_VERSION}")
    if payload.get("request_manifest_fingerprint") != requests["manifest_fingerprint"]:
        raise ValueError("score/request manifest fingerprint mismatch")
    expected: dict[str, int] = {}
    for request in requests["requests"]:
        cell_id = request["score_cell_id"]
        repeat_count = int(request["repeat_count"])
        if cell_id in expected and expected[cell_id] != repeat_count:
            raise ValueError(f"inconsistent repeat count for score cell {cell_id}")
        expected[cell_id] = repeat_count
    observed: dict[str, dict[int, float]] = defaultdict(dict)
    for record in payload.get("records", []):
        cell_id = str(record.get("score_cell_id", ""))
        if cell_id not in expected:
            raise ValueError(f"unexpected score_cell_id {cell_id!r}")
        repeat_id = int(record["repeat_id"])
        if repeat_id < 0 or repeat_id >= expected[cell_id]:
            raise ValueError(f"repeat_id out of range for {cell_id}: {repeat_id}")
        if repeat_id in observed[cell_id]:
            raise ValueError(f"duplicate score record for {cell_id} repeat {repeat_id}")
        value = float(record["normalized_score"])
        if not math.isfinite(value) or value < 0.0 or value > 1.0:
            raise ValueError(
                f"normalized score must be finite and in [0,1], got {value}"
            )
        observed[cell_id][repeat_id] = value
    complete = {
        cell_id: [repeats[index] for index in range(expected[cell_id])]
        for cell_id, repeats in observed.items()
        if set(repeats) == set(range(expected[cell_id]))
    }
    return complete, {
        "score_path": _repo_path(score_path),
        "score_sha256": _sha256_file(score_path),
        "expected_unique_cells": len(expected),
        "cells_with_any_record": len(observed),
        "complete_cells": len(complete),
        "incomplete_cells": len(observed) - len(complete),
        "missing_cells": len(expected) - len(complete),
    }


def _aggregate_or_empty(
    factors: Mapping[str, float],
    *,
    required_count: int,
    min_coverage: float,
    constant_ladder_count: int = 0,
) -> PropertyResult:
    if required_count == 0:
        return PropertyResult(
            status=NOT_COMPUTABLE,
            value=None,
            coverage=0.0,
            required_count=0,
            observed_count=0,
            missing_count=0,
            zero_count=0,
            constant_ladder_count=0,
        )
    return aggregate_property_factors(
        list(factors.values()),
        required_count=required_count,
        min_coverage=min_coverage,
        constant_ladder_count=constant_ladder_count,
    )


def _bootstrap_property_maps(
    factor_maps: Mapping[str, Mapping[str, float]],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    clusters = sorted(
        {artifact_id for factors in factor_maps.values() for artifact_id in factors}
    )
    if not clusters:
        return {}
    generator = random.Random(seed)
    samples: dict[str, list[float]] = {name: [] for name in factor_maps}
    samples["PTI_eq_bm_ms"] = []
    samples["PTI_v0"] = []
    for _ in range(iterations):
        selected = [clusters[generator.randrange(len(clusters))] for _ in clusters]
        property_values: dict[str, float] = {}
        for property_name, factors in factor_maps.items():
            values = [
                factors[artifact_id]
                for artifact_id in selected
                if artifact_id in factors
            ]
            if values:
                property_values[property_name] = stable_geometric_mean(values)
                samples[property_name].append(property_values[property_name])
        if all(name in property_values for name in ("P_eq", "P_bm", "P_ms")):
            samples["PTI_eq_bm_ms"].append(
                pti_three_property(
                    property_values["P_eq"],
                    property_values["P_bm"],
                    property_values["P_ms"],
                )
            )
        if all(
            name in property_values for name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
        ):
            samples["PTI_v0"].append(
                stable_geometric_mean(
                    [
                        property_values["P_eq"],
                        property_values["P_bm"],
                        property_values["P_ms"],
                        property_values["P_eqalpha"],
                    ]
                )
            )
    return {
        name: {
            "ci_low": _percentile(values, 0.025) if values else None,
            "ci_high": _percentile(values, 0.975) if values else None,
            "valid_replicates": len(values),
            "requested_replicates": iterations,
            "seed": seed,
        }
        for name, values in samples.items()
    }


def command_compute_properties(args: argparse.Namespace) -> int:
    probes = _read_json(args.probe_manifest)
    requests = _read_json(args.requests)
    config = _read_json(args.config)
    counts = probes["valid_probe_counts"]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.scores is None:
        properties = {
            name: _property_status(counts[name])
            for name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
        }
        report = {
            "schema_version": "PTI_v0_properties_v1",
            "metric_version": METRIC_VERSION,
            "run_mode": "cache_only_zero_spend",
            "status": NOT_COMPUTABLE,
            "screen": "DEFER",
            "reason": "no admissible PTI_v0_scores_v1 records exist",
            "properties": properties,
            "PTI_eq_bm_ms": {"status": NOT_COMPUTABLE, "value": None},
            "PTI_v0": {"status": NOT_COMPUTABLE, "value": None},
            "bridge_allowed": False,
            "probe_manifest_fingerprint": probes["manifest_fingerprint"],
            "request_manifest_fingerprint": requests["manifest_fingerprint"],
            "config_fingerprint": config.get("config_fingerprint"),
        }
        _write_json(args.out_dir / "properties_status.json", report)
        print(
            f"wrote {args.out_dir / 'properties_status.json'}: NOT_COMPUTABLE / DEFER"
        )
        return 0

    complete_cells, score_inventory = _load_score_cells(args.scores, requests)
    use_index = {_score_use_key(request): request for request in requests["requests"]}
    structural_rows = {row["artifact_id"]: row for row in probes["artifacts"]}
    min_coverage = float(config["score_policy"]["property_score_coverage_threshold"])
    judge_records: list[dict[str, Any]] = []
    ladder_rows: list[dict[str, Any]] = []
    table_rows: list[dict[str, Any]] = []

    def score_repeats(
        judge_id: str,
        artifact_id: str,
        probe_type: str,
        level: int,
        variant: str,
    ) -> list[float] | None:
        request = use_index[(judge_id, artifact_id, probe_type, level, variant)]
        return complete_cells.get(request["score_cell_id"])

    for judge_index, judge in enumerate(config["judges"]):
        judge_id = judge["judge_id"]
        factors: dict[str, dict[str, float]] = {
            name: {} for name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
        }
        constant_counts = {"P_bm": 0, "P_ms": 0}
        for artifact_id, structural in structural_rows.items():
            if structural["P_eq"]["structurally_valid"]:
                repeats = score_repeats(judge_id, artifact_id, "eq", 0, "self")
                if repeats is not None:
                    factors["P_eq"][artifact_id] = float(statistics.median(repeats))
            for property_name, probe_type in (("P_bm", "bm"), ("P_ms", "ms")):
                probe = structural[property_name]
                if not probe["structurally_valid"]:
                    continue
                score_rows: list[list[float]] = []
                for level in probe["levels"]:
                    repeats = score_repeats(
                        judge_id,
                        artifact_id,
                        probe_type,
                        int(level["level"]),
                        f"L{level['level']}",
                    )
                    if repeats is None:
                        score_rows = []
                        break
                    score_rows.append(repeats)
                if not score_rows:
                    continue
                result = ladder_factor(score_rows)
                factors[property_name][artifact_id] = result.factor
                constant_counts[property_name] += int(result.constant_ladder)
                ladder_rows.append(
                    {
                        "judge_id": judge_id,
                        "artifact_id": artifact_id,
                        "probe_type": probe_type,
                        **asdict(result),
                    }
                )
            if structural["P_eqalpha"]["structurally_valid"]:
                original = score_repeats(
                    judge_id, artifact_id, "eqalpha", 0, "original"
                )
                alpha = score_repeats(judge_id, artifact_id, "eqalpha", 0, "alpha")
                if original is not None and alpha is not None:
                    factors["P_eqalpha"][artifact_id] = 1.0 - abs(
                        float(statistics.median(original))
                        - float(statistics.median(alpha))
                    )

        property_results = {
            name: _aggregate_or_empty(
                factors[name],
                required_count=int(counts[name]),
                min_coverage=min_coverage,
                constant_ladder_count=constant_counts.get(name, 0),
            )
            for name in factors
        }
        three_ready = all(
            property_results[name].status == COMPUTED
            for name in ("P_eq", "P_bm", "P_ms")
        )
        three = (
            pti_three_property(
                property_results["P_eq"].value,  # type: ignore[arg-type]
                property_results["P_bm"].value,  # type: ignore[arg-type]
                property_results["P_ms"].value,  # type: ignore[arg-type]
            )
            if three_ready
            else None
        )
        four = compute_pti(property_results)
        bootstrap = _bootstrap_property_maps(
            factors,
            iterations=args.bootstrap_iters,
            seed=args.seed + judge_index,
        )
        epsilon_properties = {
            name: stable_geometric_mean([max(1e-3, value) for value in values.values()])
            if values
            else None
            for name, values in factors.items()
        }
        epsilon_four = (
            stable_geometric_mean([epsilon_properties[name] for name in factors])
            if all(epsilon_properties[name] is not None for name in factors)
            else None
        )
        content_deduplicated_properties: dict[str, float | None] = {}
        for name, values in factors.items():
            seen_hashes: set[str] = set()
            deduplicated_values: list[float] = []
            for artifact_id in sorted(values):
                candidate_hash = structural_rows[artifact_id]["candidate_sha256"]
                if candidate_hash in seen_hashes:
                    continue
                seen_hashes.add(candidate_hash)
                deduplicated_values.append(values[artifact_id])
            content_deduplicated_properties[name] = (
                stable_geometric_mean(deduplicated_values)
                if deduplicated_values
                else None
            )
        content_deduplicated_four = (
            stable_geometric_mean(
                [content_deduplicated_properties[name] for name in factors]  # type: ignore[list-item]
            )
            if all(
                content_deduplicated_properties[name] is not None for name in factors
            )
            else None
        )
        record = {
            "judge_id": judge_id,
            "role": judge["role"],
            "family": judge["family"],
            "properties": {
                name: asdict(result) for name, result in property_results.items()
            },
            "zero_factor_artifacts": {
                name: sorted(
                    artifact_id for artifact_id, value in values.items() if value == 0.0
                )
                for name, values in factors.items()
            },
            "PTI_eq_bm_ms": {
                "status": COMPUTED if three is not None else NOT_COMPUTABLE,
                "value": three,
                "bootstrap": bootstrap.get("PTI_eq_bm_ms"),
            },
            "PTI_v0": {**asdict(four), "bootstrap": bootstrap.get("PTI_v0")},
            "property_bootstrap": {
                name: bootstrap.get(name)
                for name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
            },
            "epsilon_1e3_sensitivity": {
                "properties": epsilon_properties,
                "PTI_v0": epsilon_four,
                "headline": False,
            },
            "content_deduplicated_sensitivity": {
                "properties": content_deduplicated_properties,
                "PTI_v0": content_deduplicated_four,
                "headline": False,
            },
        }
        judge_records.append(record)
        table_rows.append(
            {
                "judge_id": judge_id,
                "role": judge["role"],
                "family": judge["family"],
                **{name: property_results[name].value for name in property_results},
                **{
                    f"{name}_status": property_results[name].status
                    for name in property_results
                },
                **{
                    f"{name}_coverage": property_results[name].coverage
                    for name in property_results
                },
                "PTI_eq_bm_ms": three,
                "PTI_v0": four.value,
                "PTI_v0_status": four.status,
            }
        )
    primary_count = sum(record["role"] == "primary" for record in judge_records)
    failures_by_property = {
        name: sum(
            record["properties"][name]["status"] != COMPUTED
            for record in judge_records
            if record["role"] == "primary"
        )
        for name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
    }
    hard_gate = any(
        count > primary_count / 2 for count in failures_by_property.values()
    )
    report = {
        "schema_version": "PTI_v0_properties_v1",
        "metric_version": METRIC_VERSION,
        "run_mode": "supplied_scores",
        "score_inventory": score_inventory,
        "probe_manifest_fingerprint": probes["manifest_fingerprint"],
        "request_manifest_fingerprint": requests["manifest_fingerprint"],
        "config_fingerprint": config.get("config_fingerprint"),
        "coverage_threshold": min_coverage,
        "bootstrap": {
            "iterations": args.bootstrap_iters,
            "seed": args.seed,
            "unit": "base artifact f",
        },
        "hard_gate": {
            "bridge_allowed": not hard_gate,
            "not_computable_primary_judges_by_property": failures_by_property,
            "primary_judge_count": primary_count,
        },
        "judges": judge_records,
    }
    _write_json(args.out_dir / "properties.json", report)
    with (args.out_dir / "property_table.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(table_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(table_rows)
    if ladder_rows:
        serialized_rows = [
            {
                **row,
                "levels": json.dumps(row["levels"]),
                "medians": json.dumps(row["medians"]),
            }
            for row in ladder_rows
        ]
        with (args.out_dir / "ladder_diagnostics.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(
                handle, fieldnames=list(serialized_rows[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(serialized_rows)
    print(
        f"wrote {args.out_dir}: judges={len(judge_records)} bridge_allowed={not hard_gate}"
    )
    return 0


def _percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    if probability < 0.0 or probability > 1.0:
        raise ValueError("percentile probability must be in [0,1]")
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _bootstrap_paired_spearman(
    x: Sequence[float],
    y: Sequence[float],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("bootstrap requires at least two paired observations")
    generator = random.Random(seed)
    values: list[float] = []
    for _ in range(iterations):
        indices = [generator.randrange(len(x)) for _ in range(len(x))]
        rho = spearman_rho(
            [x[index] for index in indices], [y[index] for index in indices]
        )
        if rho is not None:
            values.append(rho)
    return {
        "ci_low": _percentile(values, 0.025) if values else None,
        "ci_high": _percentile(values, 0.975) if values else None,
        "requested_replicates": iterations,
        "valid_replicates": len(values),
        "undefined_replicates": iterations - len(values),
        "seed": seed,
        "method": "paired cluster percentile bootstrap",
    }


def _criterion_sources(
    panel_rows: Sequence[Mapping[str, Any]],
    *,
    candidate_dir: Path,
    gold_root: Path,
) -> dict[str, dict[str, str]]:
    gold_index: dict[str, list[Path]] = defaultdict(list)
    for path in gold_root.rglob("*.lean"):
        gold_index[path.name].append(path)
    sources: dict[str, dict[str, str]] = {}
    for row in panel_rows:
        gold_file = str(row["gold_file"])
        candidate_file = str(row["candidate_file"])
        matches = gold_index.get(gold_file, [])
        if not matches:
            raise ValueError(f"criterion gold source is missing: {gold_file}")
        gold_path = min(matches, key=lambda path: (len(path.parts), str(path)))
        candidate_path = candidate_dir / candidate_file
        if not candidate_path.is_file():
            raise ValueError(f"criterion candidate source is missing: {candidate_file}")
        gold = gold_path.read_text(encoding="utf-8", errors="strict")
        candidate = candidate_path.read_text(encoding="utf-8", errors="strict")
        key = f"{gold_file}::{candidate_file}"
        sources[key] = {
            "candidate": candidate,
            "reference": _score_reference(gold),
        }
    return sources


def _criterion_cache_key(
    judge: Mapping[str, Any], candidate: str, reference: str
) -> str:
    namespace_prefix = "exp16_bad" if judge["kind"] == "llm_control" else "exp16"
    namespace = f"{namespace_prefix}:{judge['judge_id']}"
    return "|".join(
        (
            namespace,
            str(judge["model"]),
            str(judge["prompt_sha256"]),
            sha256_text(candidate),
            sha256_text(reference),
        )
    )


def _rounded_scores_match(left: Sequence[float], right: Sequence[Any]) -> bool:
    if len(left) != len(right):
        return False
    return all(
        math.isfinite(float(value)) and round(float(value), 6) == round(stored, 6)
        for stored, value in zip(left, right)
    )


def _criterion_lineage(
    judge: Mapping[str, Any],
    source: Mapping[str, str],
    repeats: Sequence[float],
    cache: Mapping[str, Any],
) -> dict[str, Any]:
    kind = judge.get("kind")
    candidate = source["candidate"]
    reference = source["reference"]
    if kind == "deterministic_control":
        expected = _edit_similarity(reference, candidate)
        return {
            "status": "verified"
            if _rounded_scores_match(repeats, [expected] * len(repeats))
            else "local_control_mismatch",
            "source": "recomputed_edit_distance",
        }
    if kind == "seeded_control":
        expected = _deterministic_random_score(
            str(judge["judge_id"]),
            reference,
            candidate,
            seed=int(judge["decoding"]["seed"]),
        )
        return {
            "status": "verified"
            if _rounded_scores_match(repeats, [expected] * len(repeats))
            else "local_control_mismatch",
            "source": "recomputed_seeded_random",
        }
    if kind not in {"llm", "llm_control"}:
        return {"status": "unsupported_lineage_kind", "source": str(kind)}
    cache_key = _criterion_cache_key(judge, candidate, reference)
    key_hash = sha256_text(cache_key)
    entry = cache.get(cache_key)
    if not isinstance(entry, Mapping):
        return {
            "status": "missing_cache_entry",
            "cache_key_sha256": key_hash,
        }
    fallback = _fallback_reason_class(entry.get("reasoning"))
    if fallback is not None:
        return {
            "status": "fallback_entry",
            "fallback_class": fallback,
            "cache_key_sha256": key_hash,
        }
    cached_scores = entry.get("scores")
    if (
        not isinstance(cached_scores, list)
        or not _rounded_scores_match(repeats, cached_scores)
        or entry.get("model") != judge.get("model")
    ):
        return {
            "status": "cache_entry_mismatch",
            "cache_key_sha256": key_hash,
        }
    return {
        "status": "verified",
        "source": "legacy_cache_exact_key_nonfallback",
        "cache_key_sha256": key_hash,
    }


def command_compute_criterion(args: argparse.Namespace) -> int:
    panel = _read_json(args.panel_manifest)
    config = _read_json(args.config)
    expected = {
        f"{row['gold_file']}::{row['candidate_file']}": row for row in panel["rows"]
    }
    judge_meta = {judge["judge_id"]: judge for judge in config["judges"]}
    candidate_dir = Path(getattr(args, "candidate_dir", DEFAULT_CANDIDATES))
    gold_root = Path(getattr(args, "gold_root", DEFAULT_GOLD_ROOTS[0]))
    cache_path = Path(getattr(args, "legacy_cache", DEFAULT_CACHE))
    cache = _read_json(cache_path)
    if not isinstance(cache, Mapping):
        raise TypeError("criterion legacy cache must contain a JSON object")
    sources = _criterion_sources(
        panel["rows"], candidate_dir=candidate_dir, gold_root=gold_root
    )
    judge_scores: dict[str, dict[str, float]] = defaultdict(dict)
    lineage_counts: dict[str, Counter[str]] = defaultdict(Counter)
    lineage_failures: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with args.detail_rows.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if (
                row.get("row_type") != "human_eval_union"
                or row.get("item_key") not in expected
            ):
                continue
            repeats = json.loads(row["repeat_scores"])
            if not isinstance(repeats, list) or not repeats:
                raise ValueError(
                    f"invalid repeat_scores for {row.get('judge_id')} {row.get('item_key')}"
                )
            expected_repeats = int(config["score_policy"]["judge_repeats"])
            if len(repeats) != expected_repeats:
                raise ValueError(
                    f"criterion repeat-count mismatch for {row.get('judge_id')} "
                    f"{row.get('item_key')}: expected {expected_repeats}, got {len(repeats)}"
                )
            checked = [float(value) for value in repeats]
            if any(
                not math.isfinite(value) or value < 0.0 or value > 1.0
                for value in checked
            ):
                raise ValueError("criterion judge scores must be finite and in [0,1]")
            key = row["item_key"]
            judge_id = row["judge_id"]
            if judge_id not in judge_meta:
                raise ValueError(f"unknown criterion judge_id: {judge_id}")
            lineage = _criterion_lineage(
                judge_meta[judge_id], sources[key], checked, cache
            )
            lineage_counts[judge_id][lineage["status"]] += 1
            if lineage["status"] != "verified":
                lineage_failures[judge_id].append({"item_key": key, **lineage})
                continue
            if key in judge_scores[judge_id]:
                raise ValueError(f"duplicate criterion score: {judge_id} {key}")
            judge_scores[judge_id][key] = float(statistics.median(checked))

    records: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    criterion_coverage_threshold = float(
        config.get("criterion_policy", {}).get("score_coverage_threshold", 1.0)
    )
    view_fields = {
        "average": "average_score_0_5",
        "strict": "strict_score_0_5",
        "lenient": "lenient_score_0_5",
    }
    for judge_id in sorted(judge_meta):
        scores = judge_scores.get(judge_id, {})
        ordered_keys = sorted(expected)
        observed_keys = [key for key in ordered_keys if key in scores]
        coverage = len(observed_keys) / len(ordered_keys)
        excluded_rows = lineage_failures.get(judge_id, [])
        failure_counts = Counter(row["status"] for row in excluded_rows)
        lineage = {
            "verified_count": lineage_counts[judge_id]["verified"],
            "excluded_count": len(excluded_rows),
            "fallback_count": failure_counts["fallback_entry"],
            "failure_counts": dict(sorted(failure_counts.items())),
            "excluded_rows": excluded_rows,
        }
        views: dict[str, Any] = {}
        for view_index, (view, human_field) in enumerate(view_fields.items()):
            if coverage < criterion_coverage_threshold:
                view_result = {
                    "status": NOT_COMPUTABLE,
                    "value": None,
                    "kendall_tau_b": None,
                    "coverage": coverage,
                    "required_count": len(ordered_keys),
                    "observed_count": len(observed_keys),
                }
            else:
                judge_values = [scores[key] for key in ordered_keys]
                human_values = [
                    float(expected[key][human_field]) for key in ordered_keys
                ]
                rho = spearman_rho(judge_values, human_values)
                tau = kendall_tau_b(judge_values, human_values)
                if rho is None:
                    view_result = {
                        "status": NOT_COMPUTABLE,
                        "value": None,
                        "kendall_tau_b": tau,
                        "coverage": coverage,
                        "required_count": len(ordered_keys),
                        "observed_count": len(observed_keys),
                        "reason": "constant judge or human criterion vector",
                    }
                else:
                    derived_seed = args.seed + int(
                        sha256_text(f"{judge_id}|{view}|criterion")[:8], 16
                    )
                    view_result = {
                        "status": COMPUTED,
                        "value": rho,
                        "kendall_tau_b": tau,
                        "coverage": coverage,
                        "required_count": len(ordered_keys),
                        "observed_count": len(observed_keys),
                        "bootstrap": _bootstrap_paired_spearman(
                            judge_values,
                            human_values,
                            iterations=args.bootstrap_iters,
                            seed=derived_seed,
                        ),
                    }
            views[view] = view_result
            csv_rows.append(
                {
                    "judge_id": judge_id,
                    "role": judge_meta[judge_id]["role"],
                    "family": judge_meta[judge_id]["family"],
                    "view": view,
                    "status": view_result["status"],
                    "TI_m1_spearman": view_result["value"],
                    "kendall_tau_b": view_result["kendall_tau_b"],
                    "coverage": view_result["coverage"],
                    "required_count": view_result["required_count"],
                    "observed_count": view_result["observed_count"],
                    "lineage_excluded_count": lineage["excluded_count"],
                    "lineage_fallback_count": lineage["fallback_count"],
                    "ci_low": view_result.get("bootstrap", {}).get("ci_low"),
                    "ci_high": view_result.get("bootstrap", {}).get("ci_high"),
                    "valid_bootstrap_replicates": view_result.get("bootstrap", {}).get(
                        "valid_replicates"
                    ),
                }
            )
        records.append(
            {
                "judge_id": judge_id,
                "role": judge_meta[judge_id]["role"],
                "family": judge_meta[judge_id]["family"],
                "lineage": lineage,
                "views": views,
            }
        )
    result = {
        "schema_version": "TI_m1_criterion_v2",
        "criterion": "TI_m1",
        "primary_view": "average",
        "panel_manifest_fingerprint": panel["manifest_fingerprint"],
        "detail_rows_path": _repo_path(args.detail_rows),
        "detail_rows_sha256": _sha256_file(args.detail_rows),
        "legacy_cache_path": _repo_path(cache_path),
        "legacy_cache_sha256": _sha256_file(cache_path),
        "candidate_root": _repo_path(candidate_dir),
        "gold_root": _repo_path(gold_root),
        "lineage_policy": config.get("criterion_policy"),
        "criterion_coverage_threshold": criterion_coverage_threshold,
        "repeat_aggregation": "median",
        "config_fingerprint": config.get("config_fingerprint"),
        "bootstrap_iterations": args.bootstrap_iters,
        "records": records,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.out_dir / "criterion.json", result)
    with (args.out_dir / "criterion.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(csv_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"wrote {args.out_dir}: judges={len(records)} panel={len(expected)}")
    return 0


def _bridge_decisions_by_proxy_order(
    target: Sequence[float],
    *,
    sesoi: float,
    bootstrap_iterations: int,
    seed: int,
) -> dict[tuple[int, ...], dict[str, bool]]:
    if len(target) > 7:
        raise ValueError("exact proxy-order decision cache supports at most 7 judges")
    decisions: dict[tuple[int, ...], dict[str, bool]] = {}
    for order in itertools.permutations(range(len(target))):
        proxy = [0.0] * len(order)
        for rank, index in enumerate(order):
            proxy[index] = float(rank)
        rho = spearman_rho(proxy, target)
        bootstrap = _bootstrap_paired_spearman(
            proxy,
            target,
            iterations=bootstrap_iterations,
            seed=seed,
        )
        ci_low = bootstrap["ci_low"]
        point_pass = rho is not None and rho >= sesoi
        ci_pass = ci_low is not None and ci_low > 0.0
        decisions[order] = {
            "point_at_or_above_sesoi": point_pass,
            "ci_excludes_zero": ci_pass,
            "positive": point_pass and ci_pass,
        }
    return decisions


def command_simulate_sesoi(args: argparse.Namespace) -> int:
    criterion = _read_json(args.criterion)
    target = [
        record["views"]["average"]["value"]
        for record in criterion["records"]
        if record["role"] == "primary"
        and record["views"]["average"]["status"] == COMPUTED
    ]
    if len(target) < 3 or max(target) == min(target):
        raise ValueError(
            "SESOI simulation requires at least three nonconstant primary TI_m1 values"
        )
    target_ranks = average_ranks(target)
    normal = NormalDist()
    target_latent = [
        normal.inv_cdf((rank - 0.5) / len(target_ranks)) for rank in target_ranks
    ]
    target_mean = statistics.fmean(target)
    oracle_benefit = max(target) - target_mean
    if oracle_benefit <= 0.0:
        raise ValueError("empirical criterion has no positive oracle top-1 benefit")
    generator = random.Random(args.seed)
    sesoi = float(getattr(args, "sesoi", 0.5))
    decision_bootstrap_iters = int(getattr(args, "decision_bootstrap_iters", 10000))
    decision_by_order = _bridge_decisions_by_proxy_order(
        target,
        sesoi=sesoi,
        bootstrap_iterations=decision_bootstrap_iters,
        seed=args.seed,
    )
    rows: list[dict[str, Any]] = []
    for rho_target in args.rhos:
        latent_correlation = 2.0 * math.sin(math.pi * rho_target / 6.0)
        false_pass_rates: list[float] = []
        retentions: list[float] = []
        realized_rhos: list[float] = []
        point_passes = 0
        ci_passes = 0
        positive_decisions = 0
        for _ in range(args.draws):
            proxy = [
                latent_correlation * value
                + math.sqrt(1.0 - latent_correlation**2) * generator.gauss(0.0, 1.0)
                for value in target_latent
            ]
            proxy_median = statistics.median(proxy)
            target_median = statistics.median(target)
            passed = [
                index for index, value in enumerate(proxy) if value >= proxy_median
            ]
            low_and_passed = sum(target[index] < target_median for index in passed)
            false_pass_rates.append(low_and_passed / len(passed))
            selected = max(range(len(proxy)), key=lambda index: (proxy[index], -index))
            retentions.append((target[selected] - target_mean) / oracle_benefit)
            realized = spearman_rho(proxy, target)
            if realized is not None:
                realized_rhos.append(realized)
            order = tuple(
                sorted(range(len(proxy)), key=lambda index: (proxy[index], index))
            )
            decision = decision_by_order[order]
            point_passes += int(decision["point_at_or_above_sesoi"])
            ci_passes += int(decision["ci_excludes_zero"])
            positive_decisions += int(decision["positive"])
        rows.append(
            {
                "rho_target": rho_target,
                "latent_pearson_correlation": latent_correlation,
                "mean_realized_spearman": statistics.fmean(realized_rhos),
                "empirical_false_pass_rate": statistics.fmean(false_pass_rates),
                "gaussian_reference_pairwise_misordering_rate": (
                    0.5 - math.asin(latent_correlation) / math.pi
                ),
                "empirical_top1_benefit_retention": statistics.fmean(retentions),
                "point_at_or_above_sesoi_rate": point_passes / args.draws,
                "ci_excludes_zero_rate": ci_passes / args.draws,
                "positive_decision_rate": positive_decisions / args.draws,
                "draws": args.draws,
                "judge_count": len(target),
            }
        )
    report = {
        "schema_version": "PTI_v0_sesoi_simulation_v1",
        "status": "DERIVED",
        "seed": args.seed,
        "draws_per_rho": args.draws,
        "sesoi_rho": sesoi,
        "decision_bootstrap_iterations": decision_bootstrap_iters,
        "decision_bootstrap_seed": args.seed,
        "target_population": "primary judges with computed average-view TI_m1",
        "target_values": target,
        "dgp": (
            "fixed empirical TI_m1 average ranks mapped to normal scores; "
            "Gaussian-copula proxy with latent correlation 2*sin(pi*rho_s/6); "
            "independent draws by rho"
        ),
        "screen_gate": "proxy at or above its sample median; low TI below the empirical TI median",
        "bridge_decision_rule": "positive iff Spearman >= SESOI and 95% bootstrap CI low > 0",
        "retention": "(selected TI - mean TI)/(max TI - mean TI); values are not clipped",
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _write_json(args.out, report)
    with args.out.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.out}: rhos={len(rows)} draws={args.draws}")
    return 0


def _verify_prebridge_commit(commit: str, properties_path: Path) -> None:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError("--prebridge-commit must be a full 40-character Git SHA")
    relative = _repo_path(properties_path)
    if relative.startswith("/"):
        raise ValueError("properties file must be inside the repository")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError("pre-bridge commit is not an ancestor of HEAD")
    committed = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if committed.returncode != 0:
        # A directory rename changes the path, not the pre-result authority.
        # Resolve a unique same-named, identical Git blob in the original tree;
        # never substitute a later commit or accept changed property contents.
        blob = subprocess.run(
            ["git", "hash-object", "--no-filters", "--", str(properties_path)],
            cwd=REPO_ROOT, capture_output=True, check=True,
        ).stdout.strip()
        tree = subprocess.run(
            ["git", "ls-tree", "-r", "-z", commit],
            cwd=REPO_ROOT, capture_output=True, check=True,
        )
        matches = []
        for entry in tree.stdout.split(b"\0"):
            metadata, separator, name = entry.partition(b"\t")
            if separator and metadata.split()[1:] == [b"blob", blob]:
                if Path(os.fsdecode(name)).name == properties_path.name:
                    matches.append(os.fsdecode(name))
        if len(matches) != 1:
            raise ValueError(
                "properties file is absent or ambiguous in the pre-bridge commit"
            )
        committed = subprocess.run(
            ["git", "show", f"{commit}:{matches[0]}"],
            cwd=REPO_ROOT, capture_output=True, check=True,
        )
    if hashlib.sha256(committed.stdout).hexdigest() != _sha256_file(properties_path):
        raise ValueError(
            "current properties file differs from the pre-bridge committed blob"
        )


def _bridge_association(
    rows: Sequence[Mapping[str, Any]],
    *,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    x = [float(row["pti"]) for row in rows]
    y = [float(row["ti_m1"]) for row in rows]
    if len(rows) < 3:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "bridge requires at least three judges",
            "judge_count": len(rows),
        }
    rho = spearman_rho(x, y)
    if rho is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "constant PTI or TI_m1 vector",
            "judge_count": len(rows),
        }
    bootstrap = _bootstrap_paired_spearman(x, y, iterations=iterations, seed=seed)
    ci_low = bootstrap["ci_low"]
    ci_high = bootstrap["ci_high"]
    supported = ci_low is not None and ci_low > 0.0
    decision_relevant = rho >= 0.5
    if supported and decision_relevant:
        decision = "POSITIVE_SUPPORTED_AND_DECISION_RELEVANT"
    elif ci_high is not None and ci_high < 0.0:
        decision = "NEGATIVE_ASSOCIATION"
    elif ci_high is not None and ci_high < 0.5:
        decision = "SUPPORTED_OR_INCONCLUSIVE_BUT_BELOW_SESOI"
    else:
        decision = "INCONCLUSIVE"
    return {
        "status": COMPUTED,
        "judge_count": len(rows),
        "spearman": rho,
        "kendall_tau_b": kendall_tau_b(x, y),
        "bootstrap": bootstrap,
        "sesoi_rho": 0.5,
        "supported_ci_excludes_zero": supported,
        "point_estimate_meets_sesoi": decision_relevant,
        "decision": decision,
        "judge_ids": [row["judge_id"] for row in rows],
    }


def command_compute_bridge(args: argparse.Namespace) -> int:
    properties = _read_json(args.properties)
    criterion = _read_json(args.criterion)
    if not properties.get("judges"):
        report = {
            "schema_version": "PTI_v0_bridge_v1",
            "metric_version": METRIC_VERSION,
            "status": NOT_COMPUTABLE,
            "reason": properties.get("reason", "no computed property records"),
            "variant": args.variant,
            "bridge_statistic_computed": False,
        }
        _write_json(args.out, report)
        print(f"wrote {args.out}: NOT_COMPUTABLE (no bridge statistic)")
        return 0
    if not properties.get("hard_gate", {}).get("bridge_allowed", False):
        report = {
            "schema_version": "PTI_v0_bridge_v1",
            "metric_version": METRIC_VERSION,
            "status": NOT_COMPUTABLE,
            "reason": "property hard gate forbids bridge computation",
            "variant": args.variant,
            "bridge_statistic_computed": False,
            "hard_gate": properties.get("hard_gate"),
        }
        _write_json(args.out, report)
        print(f"wrote {args.out}: NOT_COMPUTABLE (property hard gate)")
        return 0
    if not args.prebridge_commit:
        raise ValueError("computed bridge requires --prebridge-commit")
    _verify_prebridge_commit(args.prebridge_commit, args.properties)

    pti_field = "PTI_v0" if args.variant == "PTI_v0" else "PTI_eq_bm_ms"
    criterion_by_judge = {record["judge_id"]: record for record in criterion["records"]}
    rows: list[dict[str, Any]] = []
    for property_record in properties["judges"]:
        judge_id = property_record["judge_id"]
        pti_record = property_record[pti_field]
        criterion_record = (
            criterion_by_judge.get(judge_id, {}).get("views", {}).get("average", {})
        )
        if (
            pti_record.get("status") != COMPUTED
            or criterion_record.get("status") != COMPUTED
        ):
            continue
        rows.append(
            {
                "judge_id": judge_id,
                "role": property_record["role"],
                "family": property_record["family"],
                "pti": pti_record["value"],
                "ti_m1": criterion_record["value"],
            }
        )
    primary_rows = [row for row in rows if row["role"] == "primary"]
    analyses = {
        "primaries": _bridge_association(
            primary_rows,
            iterations=args.bootstrap_iters,
            seed=args.seed,
        ),
        "pooled_with_controls": _bridge_association(
            rows,
            iterations=args.bootstrap_iters,
            seed=args.seed + 1,
        ),
    }
    families = sorted({row["family"] for row in primary_rows})
    leave_one_family_out = {}
    for family_index, family in enumerate(families):
        subset = [row for row in primary_rows if row["family"] != family]
        leave_one_family_out[family] = _bridge_association(
            subset,
            iterations=args.bootstrap_iters,
            seed=args.seed + 100 + family_index,
        )
    exploratory: dict[str, Any] = {}
    for property_name in ("P_eq", "P_bm", "P_ms", "P_eqalpha"):
        property_rows = []
        for record in properties["judges"]:
            criterion_record = (
                criterion_by_judge.get(record["judge_id"], {})
                .get("views", {})
                .get("average", {})
            )
            property_result = record["properties"][property_name]
            if (
                record["role"] == "primary"
                and property_result["status"] == COMPUTED
                and criterion_record.get("status") == COMPUTED
            ):
                property_rows.append(
                    {
                        "judge_id": record["judge_id"],
                        "pti": property_result["value"],
                        "ti_m1": criterion_record["value"],
                    }
                )
        exploratory[property_name] = _bridge_association(
            property_rows,
            iterations=args.bootstrap_iters,
            seed=args.seed + 200 + len(exploratory),
        )
    report = {
        "schema_version": "PTI_v0_bridge_v1",
        "metric_version": METRIC_VERSION,
        "status": analyses["primaries"]["status"],
        "variant": args.variant,
        "prebridge_commit": args.prebridge_commit,
        "properties_sha256": _sha256_file(args.properties),
        "criterion_sha256": _sha256_file(args.criterion),
        "axes_are_not_level_calibrated": True,
        "identity_line": False,
        "level_mae": None,
        "source_rows": rows,
        "analyses": analyses,
        "leave_one_family_out": leave_one_family_out,
        "exploratory_per_property": exploratory,
    }
    _write_json(args.out, report)
    print(
        f"wrote {args.out}: primary_status={report['status']} judges={len(primary_rows)}"
    )
    return 0


def _add_no_api(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--no-api",
        action="store_true",
        default=True,
        help="Compatibility flag; this program has no API/inference implementation.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze_config_parser = subparsers.add_parser("freeze-config")
    freeze_config_parser.add_argument("--out", type=Path, default=DEFAULT_CONFIG)
    _add_no_api(freeze_config_parser)
    freeze_config_parser.set_defaults(func=command_freeze_config)

    freeze_pool_parser = subparsers.add_parser("freeze-pool")
    freeze_pool_parser.add_argument(
        "--candidate-dir", type=Path, default=DEFAULT_CANDIDATES
    )
    freeze_pool_parser.add_argument(
        "--gold-roots", nargs="+", type=Path, default=list(DEFAULT_GOLD_ROOTS)
    )
    freeze_pool_parser.add_argument("--out", type=Path, default=DEFAULT_POOL)
    _add_no_api(freeze_pool_parser)
    freeze_pool_parser.set_defaults(func=command_freeze_pool)

    audit_probes_parser = subparsers.add_parser("audit-probes")
    audit_probes_parser.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    audit_probes_parser.add_argument(
        "--lean-project", type=Path, default=DEFAULT_LEAN_PROJECT
    )
    audit_probes_parser.add_argument("--lake-bin", type=Path, default=DEFAULT_LAKE)
    audit_probes_parser.add_argument("--levels", type=int, default=4)
    audit_probes_parser.add_argument("--workers", type=int, default=8)
    audit_probes_parser.add_argument("--timeout", type=int, default=60)
    audit_probes_parser.add_argument("--out", type=Path, default=DEFAULT_PROBES)
    _add_no_api(audit_probes_parser)
    audit_probes_parser.set_defaults(func=command_audit_probes)

    audit_panel_parser = subparsers.add_parser("audit-panel")
    audit_panel_parser.add_argument(
        "--strict", type=Path, default=DEFAULT_DATA / "ethan_human_scores_20260425.tsv"
    )
    audit_panel_parser.add_argument(
        "--lenient", type=Path, default=DEFAULT_DATA / "ethan_human_scores_ORIGINAL.tsv"
    )
    audit_panel_parser.add_argument(
        "--checked-average",
        type=Path,
        default=DEFAULT_DATA / "ethan_human_scores_avg_two_passes_20260425.tsv",
    )
    audit_panel_parser.add_argument("--policy", choices=["keep72"], default="keep72")
    audit_panel_parser.add_argument("--out-dir", type=Path, default=DEFAULT_PANEL_DIR)
    _add_no_api(audit_panel_parser)
    audit_panel_parser.set_defaults(func=command_audit_panel)

    build_requests_parser = subparsers.add_parser("build-requests")
    build_requests_parser.add_argument(
        "--probe-manifest", type=Path, default=DEFAULT_PROBES
    )
    build_requests_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    build_requests_parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS / "score_requests.json"
    )
    _add_no_api(build_requests_parser)
    build_requests_parser.set_defaults(func=command_build_requests)

    local_controls_parser = subparsers.add_parser("materialize-local-controls")
    local_controls_parser.add_argument(
        "--probe-manifest", type=Path, default=DEFAULT_PROBES
    )
    local_controls_parser.add_argument(
        "--requests", type=Path, default=DEFAULT_RESULTS / "score_requests.json"
    )
    local_controls_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    local_controls_parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS / "local_control_scores.json"
    )
    _add_no_api(local_controls_parser)
    local_controls_parser.set_defaults(func=command_materialize_local_controls)

    inventory_parser = subparsers.add_parser("inventory-cache")
    inventory_parser.add_argument(
        "--requests", type=Path, default=DEFAULT_RESULTS / "score_requests.json"
    )
    inventory_parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    inventory_parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS / "cache_inventory.json"
    )
    _add_no_api(inventory_parser)
    inventory_parser.set_defaults(func=command_inventory_cache)

    quote_parser = subparsers.add_parser("quote-spend")
    quote_parser.add_argument(
        "--requests", type=Path, default=DEFAULT_RESULTS / "score_requests.json"
    )
    quote_parser.add_argument(
        "--cache-inventory", type=Path, default=DEFAULT_RESULTS / "cache_inventory.json"
    )
    quote_parser.add_argument("--transforms", nargs="+", default=["ALPHA"])
    quote_parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS / "spend_alpha_only.json"
    )
    quote_parser.add_argument("--dry-run", action="store_true", default=True)
    _add_no_api(quote_parser)
    quote_parser.set_defaults(func=command_quote_spend)

    properties_parser = subparsers.add_parser("compute-properties")
    properties_parser.add_argument(
        "--probe-manifest", type=Path, default=DEFAULT_PROBES
    )
    properties_parser.add_argument(
        "--requests", type=Path, default=DEFAULT_RESULTS / "score_requests.json"
    )
    properties_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    properties_parser.add_argument("--scores", type=Path)
    properties_parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_RESULTS / "properties"
    )
    properties_parser.add_argument("--bootstrap-iters", type=int, default=10000)
    properties_parser.add_argument("--seed", type=int, default=0)
    properties_parser.add_argument("--cache-only", action="store_true", default=True)
    _add_no_api(properties_parser)
    properties_parser.set_defaults(func=command_compute_properties)

    criterion_parser = subparsers.add_parser("compute-criterion")
    criterion_parser.add_argument(
        "--panel-manifest",
        type=Path,
        default=DEFAULT_PANEL_DIR / "panel_manifest.json",
    )
    criterion_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    criterion_parser.add_argument(
        "--detail-rows", type=Path, default=DEFAULT_DETAIL_ROWS
    )
    criterion_parser.add_argument("--legacy-cache", type=Path, default=DEFAULT_CACHE)
    criterion_parser.add_argument(
        "--candidate-dir", type=Path, default=DEFAULT_CANDIDATES
    )
    criterion_parser.add_argument(
        "--gold-root", type=Path, default=DEFAULT_GOLD_ROOTS[0]
    )
    criterion_parser.add_argument("--bootstrap-iters", type=int, default=10000)
    criterion_parser.add_argument("--seed", type=int, default=0)
    criterion_parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_RESULTS / "criterion"
    )
    _add_no_api(criterion_parser)
    criterion_parser.set_defaults(func=command_compute_criterion)

    sesoi_parser = subparsers.add_parser("simulate-sesoi")
    sesoi_parser.add_argument(
        "--criterion",
        type=Path,
        default=DEFAULT_RESULTS / "criterion" / "criterion.json",
    )
    sesoi_parser.add_argument(
        "--rhos",
        nargs="+",
        type=float,
        default=[round(index / 10, 1) for index in range(1, 10)],
    )
    sesoi_parser.add_argument("--draws", type=int, default=10000)
    sesoi_parser.add_argument("--seed", type=int, default=0)
    sesoi_parser.add_argument("--sesoi", type=float, default=0.5)
    sesoi_parser.add_argument("--decision-bootstrap-iters", type=int, default=10000)
    sesoi_parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS / "sesoi_simulation.json"
    )
    _add_no_api(sesoi_parser)
    sesoi_parser.set_defaults(func=command_simulate_sesoi)

    bridge_parser = subparsers.add_parser("compute-bridge")
    bridge_parser.add_argument(
        "--properties",
        type=Path,
        default=DEFAULT_RESULTS / "properties" / "properties_status.json",
    )
    bridge_parser.add_argument(
        "--criterion",
        type=Path,
        default=DEFAULT_RESULTS / "criterion" / "criterion.json",
    )
    bridge_parser.add_argument(
        "--variant",
        choices=["PTI_v0", "PTI_eq_bm_ms"],
        default="PTI_v0",
    )
    bridge_parser.add_argument("--prebridge-commit")
    bridge_parser.add_argument("--bootstrap-iters", type=int, default=10000)
    bridge_parser.add_argument("--seed", type=int, default=0)
    bridge_parser.add_argument(
        "--out", type=Path, default=DEFAULT_RESULTS / "bridge" / "bridge.json"
    )
    _add_no_api(bridge_parser)
    bridge_parser.set_defaults(func=command_compute_bridge)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
