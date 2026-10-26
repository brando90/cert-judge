"""Frozen-panel input accounting for E58 analysis, with no model calls."""
from __future__ import annotations

from collections import Counter
import functools
import math
from pathlib import Path
import re

import e58


@functools.lru_cache(maxsize=None)
def declared_cells(exp: str, prompt: str) -> list[dict]:
    root, model = (e58.E39_DIR, "gem31h") if exp == "e39" else (e58.E42_DIR, "qwen36")
    return e58.read_json(root / f"results/cells/{model}__{prompt}.json")["cells"]


def missing_harvest(exp: str, model: str, prompt: str) -> dict:
    """Retain the declared unit without inventing observed or deterministic scores."""
    config = e58.config_id(model, prompt)
    cells = [{**{k: c[k] for k in ("cell", "kind", "key", "task", "item", "level", "repeat")},
              "config": config, "prompt_sha256": c.get("prompt_sha256"),
              "status": "unmeasured_infra", "reason": "missing harvest"}
             for c in declared_cells(exp, prompt)]
    info = e58.MODELS[model]
    return {"config": config, "family": model, "model_family": info["family"], "params_b": info["params_b"],
            "split": "test", "kind": "llm", "probe_set": exp, "harness": e58.HARNESS,
            "n_cells": len(cells), "status_counts": {"unmeasured_infra": len(cells)}, "cells": cells,
            "harvest_status": "missing"}


def load_panel(run: Path, exp: str) -> list[dict]:
    """Read exactly the frozen model/prompt grid; reject ambiguous or malformed input."""
    directory = run / "harvest" / exp
    expected = {f"{e58.fs(e58.config_id(m, p))}.json" for m in e58.MODEL_ORDER for p in e58.PROMPT_ORDER}
    unexpected = sorted(p.name for p in directory.glob("*.json") if p.name not in expected)
    if unexpected:
        raise ValueError(f"{exp}: harvests outside the frozen panel: {unexpected}")
    panel = []
    for model in e58.MODEL_ORDER:
        for prompt in e58.PROMPT_ORDER:
            config = e58.config_id(model, prompt)
            path = directory / f"{e58.fs(config)}.json"
            if not path.exists():
                panel.append(missing_harvest(exp, model, prompt))
                continue
            h = e58.read_json(path)
            if h.get("config") != config or h.get("family") != model or h.get("probe_set") != exp or h.get("split") != "test":
                raise ValueError(f"{path}: harvest identity does not match the frozen unit")
            declared = {c["cell"]: c for c in declared_cells(exp, prompt)}
            cells = h["cells"]
            if len(cells) != len(declared) or {c["cell"] for c in cells} != set(declared):
                raise ValueError(f"{path}: missing, duplicate or unexpected cells")
            for c in cells:
                d = declared[c["cell"]]
                if any(c.get(k) != d.get(k) for k in ("kind", "key", "task", "item", "level", "repeat", "prompt_sha256")):
                    raise ValueError(f"{path}: cell identity/hash mismatch: {c['cell']}")
                score = c.get("score")
                if c["status"] in ("measured", "deterministic") and (
                        not isinstance(score, (int, float)) or isinstance(score, bool) or not math.isfinite(score) or not 0 <= score <= 1):
                    raise ValueError(f"{path}: invalid normalized score: {c['cell']}")
            counts = dict(Counter(c["status"] for c in cells))
            if h.get("n_cells") != len(cells) or h.get("status_counts") != counts:
                raise ValueError(f"{path}: cell/status counts do not match the harvest")
            h.update(harvest_status="present", model_family=e58.MODELS[model]["family"], params_b=e58.MODELS[model]["params_b"])
            panel.append(h)
    # Preserve the original sorted-glob order of observed units. Association
    # bootstraps/permutations use a fixed seed, so reordering changes the draws.
    return sorted(panel, key=lambda h: e58.fs(h["config"]))


def verify_collection(run: Path, dry_run: bool = False) -> dict:
    """Protocol section 9: conclusions require a collected, hash-listed run.

    An explicitly labelled dry run can inspect uncollected partial inputs. If a
    manifest exists, even a dry run must honor it rather than ignore corruption.
    """
    if not run.is_dir():
        raise ValueError(f"run directory does not exist: {run}")
    manifest = run / "MANIFEST.sha256"
    if not manifest.is_file():
        if not dry_run:
            raise ValueError("MANIFEST.sha256 is missing; collect the run or use --dry-run for provisional diagnostics")
        return {"status": "UNVERIFIED_DRY_RUN", "manifest_sha256": None, "n_files": 0}
    files = set()
    for line in manifest.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
        if not match:
            raise ValueError("malformed MANIFEST.sha256 line")
        digest, name = match.groups()
        path = (run / name).resolve()
        if not path.is_relative_to(run.resolve()) or path in files:
            raise ValueError(f"unsafe or duplicate manifest path: {name}")
        if not path.is_file() or e58.sha_file(path) != digest:
            raise ValueError(f"collection hash mismatch: {name}")
        files.add(path)
    harvests = {p.resolve() for p in (run / "harvest").glob("*/*.json")}
    if not harvests <= files:
        raise ValueError("harvest files are not all covered by MANIFEST.sha256")
    return {"status": "VERIFIED", "manifest_sha256": e58.sha_file(manifest), "n_files": len(files)}


def runtime_contract(run: Path) -> dict:
    """Distinguish E58 inputs from later experiments that reuse its harvest schema.

    Inspect recorded settings; this does not attest actual weights or replay the
    generation. Unknown/mismatched settings are diagnostic-only, not silently
    admitted as the frozen E58 condition.
    """
    prompts = e58.e39_modules()[0].PROMPTS
    mismatches = []
    present = 0
    for exp in e58.EXPS:
        for h in load_panel(run, exp):
            if h["harvest_status"] == "missing":
                continue
            present += 1
            model = e58.MODELS[h["family"]]
            prompt = prompts[h["config"].split("|")[1]]
            expected = {"selector": f"{model['repo']}@{model['revision']}", "harness": e58.HARNESS,
                        "rubric": prompt["rubric"], "scale": prompt["scale"],
                        "engine.tensor_parallel_size": model["gpus"], "engine.max_model_len": model["max_model_len"],
                        "engine.gpu_memory_utilization": e58.GPU_MEMORY_UTILIZATION,
                        "engine.quantization": model.get("quantization"),
                        "kwargs.min_generation_budget": e58.MIN_GENERATION_BUDGET,
                        "kwargs.max_tokens_rule": f"min({prompt['max_tokens']}, max_model_len - prompt tokens)",
                        "kwargs.seed_rule": "int(sha256('58|<config>|<cell>')[:8], 16)",
                        "kwargs.skip_special_tokens": not model.get("harmony", False)}
            for key, wanted in expected.items():
                actual = h
                for part in key.split("."):
                    actual = actual.get(part, "<missing>") if isinstance(actual, dict) else "<missing>"
                if actual != wanted:
                    mismatches.append({"probe_set": exp, "config": h["config"], "field": key, "expected": wanted, "observed": actual})
    return {"n_present_harvests": present, "n_expected_harvests": 2 * len(e58.MODEL_ORDER) * len(e58.PROMPT_ORDER),
            "status": "MISMATCH" if mismatches else "MATCH" if present else "NO_HARVESTS",
            "mismatches": mismatches}


def failure_counts(run: Path) -> dict:
    """Section 10: incomplete + parse_error / all declared cells, across both probe sets."""
    rows = {m: {"n_declared_cells": 0, "n_failed_cells": 0, "n_present_harvests": 0, "by_probe_set": {}} for m in e58.MODEL_ORDER}
    for exp in e58.EXPS:
        for h in load_panel(run, exp):
            row = rows[h["family"]]
            count = row["by_probe_set"].setdefault(exp, {"n_declared_cells": 0, "n_failed_cells": 0})
            failed = sum(h["status_counts"].get(s, 0) for s in ("incomplete", "parse_error"))
            for r in (row, count):
                r["n_declared_cells"] += h["n_cells"]
                r["n_failed_cells"] += failed
            row["n_present_harvests"] += h["harvest_status"] == "present"
    for row in rows.values():
        row["failure_fraction"] = row["n_failed_cells"] / row["n_declared_cells"]
        row["flagged"] = row["failure_fraction"] > .20
    return {"threshold": .20, "comparison": ">", "denominator": "all declared E39 + E42 cells per model",
            "flagged_models": [m for m, r in rows.items() if r["flagged"]], "models": rows}
