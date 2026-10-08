#!/usr/bin/env python3
"""Offline experiment-46 analysis over the protocol's allowlisted measured caches.

This program has two explicit phases. ``select`` writes property rows and frozen
selector weights without reading human outcomes. ``evaluate`` verifies that seal,
then reads the published E45 rating artifact for utility and association reports.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import platform
import statistics
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import kendalltau, pearsonr, rankdata, spearmanr

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "py_src"))
from cert_judge.information_properties import (  # noqa: E402
    complete_repeat_candidates,
    deletion_tvd_task,
    repeat_tvd_task,
    semantic_acceptance_gaps,
    semantic_auc_task,
)

E46 = Path(__file__).resolve().parents[1]
OUT = E46 / "results"
E39 = ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E42 = ROOT / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges"
E44 = ROOT / "experiments/archive/44_cached_score_judge_selection_utility"
E45 = ROOT / "experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit"
SEED = 20261008
DRAWS = 10_000
ACCEPTED = {"measured", "deterministic"}
THRESHOLDS = (0.0, 0.01, 0.05, 0.10, 0.20)
METRICS = ("spearman", "pearson", "kendall", "mae", "bias", "judge_mean", "human_mean")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


U44 = load_module("e46_utility44", E44 / "scripts/analyze_selection_utility.py")
A39 = load_module("e46_analysis39", E39 / "scripts/analysis_lib.py")
# This import only defines E45's numerical helpers.  It does not call that
# script's load()/selection()/evaluation() entry points, which access labels
# outside this experiment's published ratings artifact.
sys.path.insert(0, str(E45 / "scripts"))
try:
    E45_NUMERICS = load_module("e46_e45_numerics", E45 / "scripts/analyze.py")
finally:
    sys.path.pop(0)


def read(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def write(name: str, value) -> Path:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True, allow_nan=False) + "\n")
    return path


def source_hashes() -> dict[str, str]:
    manifest = read(OUT / "input_manifest.json")
    return manifest["files"]


def assert_source_freeze() -> None:
    expected = source_hashes()
    observed = {path: sha256(ROOT / path) for path in expected}
    if observed != expected:
        changed = sorted(path for path in expected if expected[path] != observed.get(path))
        raise RuntimeError(f"frozen input changed: {changed}")


def median_or_none(values: list[float]) -> float | None:
    return statistics.median(values) if len(values) >= 2 else None


def accepted_cells(harvest: dict, *, invert: bool = False) -> tuple[dict[tuple[str, str, int], dict[int, float]], dict]:
    """Index accepted cells and fail closed on duplicate cell/repeat identifiers."""
    seen_cells: set[str] = set()
    grouped: dict[tuple[str, str, int], dict[int, float]] = defaultdict(dict)
    rejected = Counter()
    for cell in harvest["cells"]:
        cell_id = cell.get("cell")
        if cell_id in seen_cells:
            raise ValueError(f"duplicate cell id in {harvest['config']}: {cell_id}")
        seen_cells.add(cell_id)
        status = cell.get("status")
        score = cell.get("score")
        if status not in ACCEPTED or score is None:
            rejected[str(status)] += 1
            continue
        score = float(score)
        if not (math.isfinite(score) and 0.0 <= score <= 1.0):
            raise ValueError(f"out-of-range accepted score in {harvest['config']}: {score}")
        key = (str(cell["kind"]), str(cell.get("key") or cell.get("task")), int(cell["level"]))
        repeat = int(cell["repeat"])
        if repeat in grouped[key]:
            raise ValueError(f"duplicate repeat for {harvest['config']} {key} r{repeat}")
        grouped[key][repeat] = 1.0 - score if invert else score
    return grouped, {"accepted": sum(len(v) for v in grouped.values()), "rejected_by_status": dict(sorted(rejected.items()))}


def load_metadata(*, include_ratings: bool = True):
    panel = read(E39 / "results/panel.json")
    meta = {row["config"]: row for row in panel["units"] if row["kind"] == "llm"}
    # Metadata-only projection; no old human labels embedded in items.jsonl are used.
    items = []
    for line in (E44 / "inputs/items.jsonl").read_text().splitlines():
        raw = json.loads(line)
        items.append({key: raw[key] for key in ("item", "task", "split")})
    ratings = {}
    if include_ratings:
        ratings = {row["item"]: row for row in read(E45 / "results/individual_current_ratings.json")}
        if {row["item"] for row in items} != set(ratings):
            raise ValueError("E44 metadata and E45 published-ratings items differ")
    return meta, items, ratings


def split_task_map(items: list[dict]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for item in items:
        out[item["split"]].add(item["task"])
    return out


def semantic_declarations() -> tuple[dict[str, dict], dict[str, str]]:
    labels = {}
    for path in sorted((E42 / "probe_edits/audit").glob("*.json")):
        labels.update({probe_id: row["label"] for probe_id, row in read(path).get("labels", {}).items()})
    tasks: dict[str, dict] = defaultdict(lambda: {"strict": [], "formatting": []})
    for row in read(E42 / "results/semantic_probe_manifest.json")["rows"]:
        if row["valid"] is not True:
            continue
        if row["family"] == "weakening" and labels.get(row["probe_id"]) == "strict":
            tasks[row["task"]]["strict"].append(row)
        elif row["family"] == "formatting":
            tasks[row["task"]]["formatting"].append(row)
    eligible = {task: rows for task, rows in tasks.items() if rows["strict"] and rows["formatting"]}
    return eligible, labels


def semantic_for_split(cells, declarations: dict[str, dict], tasks: set[str]) -> tuple[dict, list[dict]]:
    declared = {task: rows for task, rows in declarations.items() if task in tasks}
    details, task_values, threshold_values = [], [], defaultdict(list)
    for task, rows in sorted(declared.items()):
        baseline = median_or_none(list(cells.get(("ident", task, 1), {}).values()))
        formats = []
        for row in rows["formatting"]:
            value = median_or_none(list(cells.get((row["kind"], task, int(row["level"])), {}).values()))
            if value is not None and baseline is not None:
                formats.append(abs(baseline - value))
        semantics = []
        for row in rows["strict"]:
            value = median_or_none(list(cells.get((row["kind"], task, int(row["level"])), {}).values()))
            if value is not None and baseline is not None:
                semantics.append(baseline - value)
        observed = baseline is not None and len(formats) == len(rows["formatting"]) and len(semantics) >= math.ceil(.8 * len(rows["strict"]))
        entry = {"task": task, "baseline": baseline, "strict_declared": len(rows["strict"]), "strict_observed": len(semantics),
                 "formatting_declared": len(rows["formatting"]), "formatting_observed": len(formats), "observed": observed}
        if observed:
            entry["value"] = semantic_auc_task(semantics, formats)
            entry["acceptance_gaps"] = semantic_acceptance_gaps(semantics, formats, THRESHOLDS)
            task_values.append(entry["value"])
            for threshold, value in entry["acceptance_gaps"].items():
                threshold_values[threshold].append(value)
        else:
            entry["reason"] = "missing_identity_or_all_formatting_or_80pct_strict"
        details.append(entry)
    required = math.ceil(.8 * len(declared))
    enough = len(task_values) >= required
    result = {"value": statistics.mean(task_values) if enough else None, "declared_tasks": len(declared), "observed_tasks": len(task_values),
              "required_tasks": required, "coverage": len(task_values) / len(declared) if declared else 0.0,
              "acceptance_gaps": {str(threshold): statistics.mean(values) if enough else None for threshold, values in threshold_values.items()},
              "status": "COMPUTED" if enough else "NOT_COMPUTABLE_COVERAGE"}
    return result, details


def prior_semantic_baseline(semantic_harvest: dict, tasks: set[str]) -> dict:
    """Exact E45 strict-minus-directional-formatting aggregate for one task split.

    Crucially, E45 declares *all* valid formatting probes, including those from
    tasks with no audit-strict weakening.  ``measure_rows`` separately preserves
    each family's 80% denominator and its declared missing entries.
    """
    declared_rows = [row for row in E45_NUMERICS.semantic_rows() if row["task"] in tasks]
    measured_rows = E45_NUMERICS.semantic(semantic_harvest, declared_rows)
    strict = E45_NUMERICS.measure_rows(
        [row for row in measured_rows if row["family"] == "weakening" and row["strictness"] == "strict"], "directional"
    )
    formatting = E45_NUMERICS.measure_rows(
        [row for row in measured_rows if row["family"] == "formatting"], "directional"
    )
    value = None if strict["value"] is None or formatting["value"] is None else max(0.0, strict["value"] - formatting["value"])
    return {"value": value, "strict_directional": strict["value"], "formatting_directional": formatting["value"],
            "strict": strict, "formatting": formatting, "definition": "E45 strict directional minus formatting directional, floored at zero",
            "implementation": "direct calls to E45 semantic_rows(), semantic(), and measure_rows()"}


def repeat_for_split(cells, items: list[dict], split: str) -> tuple[dict, list[dict]]:
    per_task: dict[str, list[dict]] = defaultdict(list)
    for row in items:
        if row["split"] == split:
            per_task[row["task"]].append(row)
    details, values = [], []
    for task, rows in sorted(per_task.items()):
        if len(rows) < 2:
            continue
        candidates = {row["item"]: cells.get(("crit", row["item"], 0), {}) for row in rows}
        complete_candidates, excluded_candidates = complete_repeat_candidates(candidates)
        observed = len(complete_candidates) >= 2
        entry = {"task": task, "candidate_count": len(rows), "complete_candidate_count": len(complete_candidates),
                 "excluded_candidate_count": len(excluded_candidates), "excluded_candidates": excluded_candidates,
                 "repeat_counts": {item: len(reps) for item, reps in candidates.items()}, "observed": observed}
        if observed:
            entry["value"] = repeat_tvd_task(complete_candidates)
            values.append(entry["value"])
        else:
            entry["reason"] = "requires_at_least_two_candidates_with_exactly_three_accepted_repeats"
        details.append(entry)
    required = math.ceil(.8 * len(details))
    return {"value": statistics.mean(values) if len(values) >= required else None, "declared_tasks": len(details), "observed_tasks": len(values),
            "required_tasks": required, "coverage": len(values) / len(details) if details else 0.0,
            "status": "COMPUTED" if len(values) >= required else "NOT_COMPUTABLE_COVERAGE"}, details


def deletion_for_split(cells, probes: dict[str, list[dict]], tasks: set[str]) -> tuple[dict, list[dict]]:
    by_task: dict[str, list[int]] = defaultdict(list)
    for row in probes.get("ms_gold", []):
        if row["task"] in tasks:
            by_task[row["task"]].append(int(row["level"]))
    details, values = [], []
    for task, levels in sorted(by_task.items()):
        all_levels = [0] + sorted(set(levels))
        repeats = {level: list(cells.get((("ident" if level == 0 else "ms_gold"), task, level), {}).values()) for level in all_levels}
        complete = all(len(scores) >= 2 for scores in repeats.values())
        entry = {"task": task, "declared_levels": all_levels, "repeat_counts": {str(level): len(scores) for level, scores in repeats.items()}, "observed": complete}
        if complete:
            entry.update(deletion_tvd_task(repeats))
            values.append(entry["value"])
        else:
            entry["reason"] = "requires_two_accepted_repeats_at_identity_and_every_deletion_level"
        details.append(entry)
    required = math.ceil(.8 * len(details))
    return {"value": statistics.mean(values) if len(values) >= required else None, "declared_tasks": len(details), "observed_tasks": len(values),
            "required_tasks": required, "coverage": len(values) / len(details) if details else 0.0,
            "mean_information": statistics.mean([entry["information"] for entry in details if entry["observed"]]) if values else None,
            "mean_orientation": statistics.mean([entry["orientation"] for entry in details if entry["observed"]]) if values else None,
            "status": "COMPUTED" if len(values) >= required else "NOT_COMPUTABLE_COVERAGE"}, details


def legacy_deletion(cells_harvest: dict, probes: dict[str, list[dict]], tasks: set[str]) -> dict:
    restricted = {kind: [row for row in rows if row.get("task") in tasks] for kind, rows in probes.items()}
    result = A39.components(A39.Scores(cells_harvest), restricted)["ms_gold"]
    return {"value": result["value"], "observed": result["n"], "declared": result["declared"], "coverage": result["coverage"],
            "status": "COMPUTED" if result["value"] is not None else "NOT_COMPUTABLE_COVERAGE", "source": "E39 analysis_lib.components"}


def calculate_properties(meta, items, *, invert: bool = False) -> tuple[dict, dict]:
    tasks_by_split = split_task_map(items)
    semantic_declared, _ = semantic_declarations()
    probes = A39.valid_probes(read(E39 / "results/probe_manifest.json"))
    semantic_harvest = {path.stem.replace("__", "|"): read(path) for path in sorted((E42 / "results/harvest").glob("*.json"))}
    rows, detail = {}, {}
    for config in sorted(meta):
        harvest = read(E39 / "results/harvest" / f"{config.replace('|', '__')}.json")
        cells, counts = accepted_cells(harvest, invert=invert)
        sem_cells = None
        sem_counts = {"available": False}
        if config in semantic_harvest:
            sem_cells, sem_counts = accepted_cells(semantic_harvest[config], invert=invert)
            sem_counts["available"] = True
        props, config_detail = {}, {}
        for split in ("train", "val", "test"):
            task_set = tasks_by_split[split]
            repeat, repeat_detail = repeat_for_split(cells, items, split)
            deletion, deletion_detail = deletion_for_split(cells, probes, task_set)
            legacy = legacy_deletion(harvest, probes, task_set) if not invert else None
            if sem_cells is None:
                semantic = {"value": None, "status": "NOT_COMPUTABLE_NO_SEMANTIC_HARVEST", "declared_tasks": len([t for t in semantic_declared if t in task_set]), "observed_tasks": 0}
                semantic_detail, baseline = [], {"value": None, "status": "NOT_COMPUTABLE_NO_SEMANTIC_HARVEST"}
            else:
                semantic, semantic_detail = semantic_for_split(sem_cells, semantic_declared, task_set)
                baseline = prior_semantic_baseline(semantic_harvest[config], task_set)
            props[split] = {"semantic_auc": semantic, "repeat_tvd": repeat, "deletion_tvd": deletion, "C_ms_gold": legacy, "prior_strict_minus_format": baseline}
            config_detail[split] = {"semantic": semantic_detail, "repeat": repeat_detail, "deletion": deletion_detail}
        rows[config] = {"config": config, "meta": meta[config], "properties": props, "cell_counts": counts, "semantic_cell_counts": sem_counts}
        detail[config] = config_detail
    return rows, detail


def maximum_weights(configs: list[str], values: dict[str, float | None]) -> dict[str, float] | None:
    finite = {config: value for config, value in values.items() if value is not None and math.isfinite(value)}
    if not finite:
        return None
    maximum = max(finite.values())
    winners = sorted(config for config, value in finite.items() if abs(value - maximum) <= 1e-12)
    return {config: 1.0 / len(winners) for config in winners}


def make_selectors(rows: dict, meta: dict, items: list[dict]) -> dict:
    pool = U44.pools(meta)
    primary, h2 = pool["primary_full_context"], pool["same_H2"]
    train = {name: {config: rows[config]["properties"]["train"][name]["value"] for config in primary}
             for name in ("semantic_auc", "repeat_tvd", "deletion_tvd", "C_ms_gold", "prior_strict_minus_format")}
    selectors = {f"property_{name}": maximum_weights(primary, values) for name, values in train.items() if name in ("semantic_auc", "repeat_tvd", "deletion_tvd")}
    selectors["max_train_C_ms_gold"] = maximum_weights(primary, train["C_ms_gold"])
    selectors["max_train_prior_strict_minus_format"] = maximum_weights(primary, train["prior_strict_minus_format"])
    selectors["random_primary12"] = {config: 1.0 / len(primary) for config in primary}
    selectors["fixed_H2"] = {config: 1.0 / len(h2) for config in h2}
    return {"status": "FROZEN_BEFORE_HUMAN_OUTCOMES", "protocol_sha256": sha256(E46 / "PROTOCOL.md"), "input_hashes": source_hashes(),
            "seed": SEED, "primary_pool": primary, "h2_pool": h2, "train_property_values": train, "weights": selectors,
            "declared_split_counts": {split: len([item for item in items if item["split"] == split]) for split in ("train", "val", "test")},
            "human_outcomes_read": False}


def select() -> int:
    assert_source_freeze()
    meta, items, _ = load_metadata(include_ratings=False)
    rows, detail = calculate_properties(meta, items)
    write("property_rows.json", {"status": "COMPLETE", "configs": rows})
    write("per_task_properties.json", detail)
    inverted, _ = calculate_properties(meta, items, invert=True)
    controls = {config: {split: {name: inverted[config]["properties"][split][name]["value"] for name in ("semantic_auc", "repeat_tvd", "deletion_tvd")}
                         for split in ("train", "val", "test")} for config in inverted}
    write("controls_score_inversion.json", {"description": "score -> 1-score; repeat information should be invariant while deletion orientation gates reversed ladders", "properties": controls,
                                               "fixtures": {"task_id_only_repeat_signal": 0.0, "candidate_id_only_repeat_signal": 0.5}})
    seal = make_selectors(rows, meta, items)
    selector_path = write("selectors.json", seal)
    write("selection_receipt.json", {"status": "COMPLETE", "selectors_sha256": sha256(selector_path), "human_outcomes_read": False, "source_hashes": source_hashes()})
    print(json.dumps({"configs": len(rows), "primary_pool": len(seal["primary_pool"]), "selector_path": str(selector_path.relative_to(ROOT))}, indent=2))
    return 0


def safe_corr(x, y) -> dict[str, float | None]:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return {"spearman": None, "pearson": None, "kendall": None}
    return {"spearman": float(spearmanr(x, y).statistic), "pearson": float(pearsonr(x, y).statistic), "kendall": float(kendalltau(x, y).statistic)}


def interval(point, values) -> dict:
    values = np.asarray(values, float)
    valid = values[np.isfinite(values)]
    lo, hi = (np.percentile(valid, [2.5, 97.5]).tolist() if len(valid) else (None, None))
    return {"value": point, "lo": lo, "hi": hi, "valid_draws": int(len(valid)), "undefined_draws": int(len(values) - len(valid)), "p_value": None}


def score_medians(meta: dict) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, list[float]]]]:
    medians, repeats = {}, {}
    for config in meta:
        cells, _ = accepted_cells(read(E39 / "results/harvest" / f"{config.replace('|', '__')}.json"))
        current = {key: values for (kind, key, level), values in cells.items() if kind == "crit" and level == 0}
        medians[config] = {key: statistics.median(list(values.values())) for key, values in current.items() if values}
        repeats[config] = {key: list(values.values()) for key, values in current.items()}
    return medians, repeats


def selector_metric(matrix, human, index, weights, configs) -> np.ndarray:
    selected = np.array([sum(weight * matrix[configs.index(config), index] for config, weight in weights.items())])
    # Expected selector utility: calculate each individual judge then weight metrics, never score-average judges.
    metrics = []
    for config, weight in weights.items():
        scores = matrix[configs.index(config), index]
        corr = safe_corr(scores, human[index])
        delta = scores - human[index]
        metrics.append((weight, [corr["spearman"], corr["pearson"], corr["kendall"], np.abs(delta).mean(), delta.mean(), scores.mean(), human[index].mean()]))
    if any(value is None for _, row in metrics for value in row[:3]):
        return np.full(len(METRICS), np.nan)
    return np.array([sum(weight * row[column] for weight, row in metrics) for column in range(len(METRICS))])


def _corr_rows(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Vectorized Pearson row correlations, with NaN for constant rows."""
    x_centered, y_centered = x - x.mean(axis=-1, keepdims=True), y - y.mean(axis=-1, keepdims=True)
    denominator = np.sqrt((x_centered * x_centered).sum(axis=-1) * (y_centered * y_centered).sum(axis=-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (x_centered * y_centered).sum(axis=-1) / denominator


def per_config_bootstrap_metrics(matrix: np.ndarray, human: np.ndarray, samples: np.ndarray) -> np.ndarray:
    """Vectorized [draw, configuration, metric] task-bootstrap calculations."""
    # matrix is [configuration, file], samples is [draw, file].
    scores = np.swapaxes(matrix[:, samples], 0, 1)  # draw, configuration, file
    outcome = human[samples]                         # draw, file
    draws, configs, _ = scores.shape
    pearson = _corr_rows(scores, outcome[:, None, :])
    score_ranks = rankdata(scores, axis=-1)
    human_ranks = rankdata(outcome, axis=-1)[:, None, :]
    spearman = _corr_rows(score_ranks, human_ranks)
    left, right = np.triu_indices(scores.shape[-1], 1)
    outcome_sign = np.sign(outcome[:, left] - outcome[:, right])
    outcome_tie_free = (outcome_sign * outcome_sign).sum(axis=-1)
    kendall = np.full((draws, configs), np.nan)
    for config in range(configs):
        score_sign = np.sign(scores[:, config, left] - scores[:, config, right])
        denominator = np.sqrt((score_sign * score_sign).sum(axis=-1) * outcome_tie_free)
        with np.errstate(invalid="ignore", divide="ignore"):
            kendall[:, config] = (score_sign * outcome_sign).sum(axis=-1) / denominator
    delta = scores - outcome[:, None, :]
    return np.stack((spearman, pearson, kendall, np.abs(delta).mean(axis=-1), delta.mean(axis=-1), scores.mean(axis=-1),
                     np.broadcast_to(outcome.mean(axis=-1)[:, None], (draws, configs))), axis=-1)


def task_cluster_bootstrap_metrics(matrix: np.ndarray, human: np.ndarray, group_draws: np.ndarray, groups: list[np.ndarray]) -> np.ndarray:
    """Vectorize task-cluster draws in same-length buckets.

    Task clusters can contain either two or three candidate files in the frozen
    cache, so a valid resample can have different file counts.  Bucketing those
    draws preserves cluster multiplicities while avoiding an invalid rectangular
    stack (and retains vectorized correlation work within each bucket).
    """
    buckets: dict[int, list[tuple[int, np.ndarray]]] = defaultdict(list)
    for draw, chosen_groups in enumerate(group_draws):
        indices = np.concatenate([groups[group] for group in chosen_groups])
        buckets[len(indices)].append((draw, indices))
    output = np.full((len(group_draws), matrix.shape[0], len(METRICS)), np.nan)
    for entries in buckets.values():
        draw_numbers, index_rows = zip(*entries)
        output[list(draw_numbers)] = per_config_bootstrap_metrics(matrix, human, np.stack(index_rows))
    return output


def expected_selector_metrics(per_config: np.ndarray, configs: list[str], weights: dict[str, float] | None) -> np.ndarray:
    if not weights:
        return np.full((per_config.shape[0], len(METRICS)), np.nan)
    positions = [configs.index(config) for config in weights]
    selected = per_config[:, positions, :]
    coefficients = np.asarray([weights[config] for config in weights])
    result = np.einsum("dcm,c->dm", selected, coefficients)
    # A selector's correlations are undefined if a positive-weight judge's
    # correlation is undefined; level metrics remain reported where defined.
    undefined_correlation = ~np.isfinite(selected[:, :, :3]).all(axis=1)
    result[:, :3][undefined_correlation] = np.nan
    return result


def evaluate_split(configs, split_rows, medians, repeats, ratings, selectors, draws: int, *, declared_files: int) -> dict:
    ids = [row["item"] for row in split_rows]
    matrix = np.array([[medians[config][item] for item in ids] for config in configs])
    targets = {name: np.array([ratings[item][name] for item in ids], float) for name in ("current5_mean_0_to_1", "current3_mean_0_to_1")}
    task_indices: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(split_rows):
        task_indices[row["task"]].append(index)
    groups = [np.asarray(task_indices[task], int) for task in sorted(task_indices)]
    rng = np.random.default_rng(SEED)
    samples = rng.integers(0, len(groups), size=(draws, len(groups)))
    output = {"status": "COMPUTED", "declared_files": declared_files, "common_files": len(ids), "common_tasks": len(groups), "item_ids": ids,
              "required_common_files": math.ceil(.9 * declared_files), "resampling_unit": "paired task clusters", "draws": draws, "seed": SEED,
              "selection_uncertainty_included": False, "targets": {}}
    all_indices = np.arange(len(ids))
    for target_name, human in targets.items():
        point_by_config = per_config_bootstrap_metrics(matrix, human, all_indices[None, :])[0]
        boot_by_config = task_cluster_bootstrap_metrics(matrix, human, samples, groups)
        points = {name: expected_selector_metrics(point_by_config[None, :, :], configs, weights)[0] for name, weights in selectors.items()}
        boot = {name: expected_selector_metrics(boot_by_config, configs, weights) for name, weights in selectors.items()}
        selector_rows = {name: {"weights": weights, "metrics": {metric: interval(points[name][col], boot[name][:, col]) for col, metric in enumerate(METRICS)}
                                 if weights else {metric: interval(None, np.full(draws, np.nan)) for metric in METRICS}}
                         for name, weights in selectors.items()}
        differences = {}
        for name in selectors:
            if name == "fixed_H2":
                continue
            differences[name] = {metric: interval(points[name][col] - points["fixed_H2"][col] if np.isfinite(points[name][col]) and np.isfinite(points["fixed_H2"][col]) else None,
                                                   boot[name][:, col] - boot["fixed_H2"][:, col]) for col, metric in enumerate(METRICS)}
        output["targets"][target_name] = {"selectors": selector_rows, "minus_fixed_H2": differences}
    output["repeat_counts"] = {config: {"available": sum(len(repeats[config].get(item, [])) for item in ids), "expected": 3 * len(ids),
                                         "per_item_count_histogram": dict(Counter(len(repeats[config].get(item, [])) for item in ids)),
                                         "mean_within_item_sample_sd": statistics.mean([statistics.stdev(repeats[config][item]) for item in ids if len(repeats[config].get(item, [])) >= 2])}
                               for config in configs}
    return output


def association(rows, configs, split_rows, medians, ratings, draws: int) -> dict:
    ids = [row["item"] for row in split_rows]
    matrix = np.array([[medians[config][item] for item in ids] for config in configs])
    y = np.array([ratings[item]["current5_mean_0_to_1"] for item in ids])
    tasks: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(split_rows): tasks[row["task"]].append(index)
    groups = [np.asarray(tasks[task], int) for task in sorted(tasks)]
    rng = np.random.default_rng(SEED)
    samples = rng.integers(0, len(groups), size=(draws, len(groups)))
    point_agreement = per_config_bootstrap_metrics(matrix, y, np.arange(len(ids))[None, :])[0, :, 0]
    boot_agreement = task_cluster_bootstrap_metrics(matrix, y, samples, groups)[:, :, 0]
    out = {}
    for property_name in ("semantic_auc", "repeat_tvd", "deletion_tvd"):
        values = np.array([rows[config]["properties"]["train"][property_name]["value"] for config in configs], float)
        eligible = np.isfinite(values)
        point = safe_corr(values[eligible], point_agreement[eligible]) if eligible.sum() >= 3 else {metric: None for metric in ("spearman", "pearson", "kendall")}
        boot = {metric: np.full(draws, np.nan) for metric in point}
        if eligible.sum() >= 3:
            fixed = np.broadcast_to(values[eligible], (draws, eligible.sum()))
            current = {"pearson": _corr_rows(fixed, boot_agreement[:, eligible]),
                       "spearman": _corr_rows(rankdata(fixed, axis=-1), rankdata(boot_agreement[:, eligible], axis=-1))}
            left, right = np.triu_indices(eligible.sum(), 1)
            fixed_sign = np.sign(fixed[:, left] - fixed[:, right])
            agreement_sign = np.sign(boot_agreement[:, eligible][:, left] - boot_agreement[:, eligible][:, right])
            denominator = np.sqrt((fixed_sign * fixed_sign).sum(axis=-1) * (agreement_sign * agreement_sign).sum(axis=-1))
            with np.errstate(invalid="ignore", divide="ignore"):
                current["kendall"] = (fixed_sign * agreement_sign).sum(axis=-1) / denominator
            for metric, values_boot in current.items():
                boot[metric] = values_boot
        out[property_name] = {"status": "COMPUTED" if eligible.sum() >= 3 else "NOT_COMPUTABLE_LT3_CONFIGS", "n_configs": int(eligible.sum()),
                              "configs": [config for config, keep in zip(configs, eligible) if keep], "metrics": {metric: interval(point[metric], boot[metric]) for metric in point},
                              "properties_fixed_across_task_bootstrap": True}
    return out


def render_report(evaluation: dict, associations: dict, properties: dict) -> None:
    test_split = evaluation["test"]
    test = test_split["targets"]["current5_mean_0_to_1"]
    lines = [
        "# Experiment 46 results: information-inspired properties on measured judge caches", "",
        "**Status:** COMPLETE — exploratory historical-cache analysis only; this is not prospective validation.", "",
        "**Paper summary:** [PAPER_SUMMARY.md](PAPER_SUMMARY.md) gives the short manuscript-facing interpretation.", "",
        "## Operational properties", "",
        "Semantic AUC compares signed score drops on audit-strict weakenings with absolute score changes on formatting probes.",
        "Repeat TVD is five-bin total variation between paired repeat scores and the product of their repeat marginals.",
        "Deletion TVD is level-score total variation normalized by the finite-level maximum and multiplied by a direction gate.", "",
        "## Measured property overview", "",
        "| Split | Property | Computed configurations / 56 | Observed range |",
        "| --- | --- | ---: | --- |",
    ]
    for split in ("train", "val", "test"):
        for name in ("semantic_auc", "repeat_tvd", "deletion_tvd"):
            values = [row["properties"][split][name]["value"] for row in properties.values()]
            finite = [value for value in values if value is not None]
            observed = f"{min(finite):.3f} to {max(finite):.3f}" if finite else "unavailable"
            lines.append(f"| {split} | {name} | {len(finite)} / 56 | {observed} |")
    lines += ["", "Deletion TVD is unavailable for all 56 configurations: experiment 39's `ms_gold` cache intentionally has one accepted repeat per level, below the frozen two-repeat requirement.",
              "", "## Primary 12-configuration pool — historical test split", "",
              f"The historical test comparison has {test_split['common_files']}/{test_split['declared_files']} common candidate files across {test_split['common_tasks']} tasks (requirement: {test_split['required_common_files']}); validation is {evaluation['val']['status']} with {evaluation['val']['common_files']}/{evaluation['val']['declared_files']} common files (requirement: {evaluation['val']['required_common_files']}).", "",
        "| Selector | Spearman (95% task-bootstrap interval) | Pearson | Kendall | Mean absolute error | Bias (judge − human) | Judge mean / human mean | Δ Spearman vs fixed H2 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, row in test["selectors"].items():
        metrics = row["metrics"]
        spearman = metrics["spearman"]
        delta = test["minus_fixed_H2"].get(name, {}).get("spearman", {})
        members = ", ".join(row["weights"] or {}) or "unavailable"
        lines.append(f"| {name} ({members}) | {spearman['value']:.3f} [{spearman['lo']:.3f}, {spearman['hi']:.3f}]" if spearman["value"] is not None else f"| {name} ({members}) | unavailable")
        if spearman["value"] is not None:
            lines[-1] += f" | {metrics['pearson']['value']:.3f} | {metrics['kendall']['value']:.3f} | {metrics['mae']['value']:.3f} | {metrics['bias']['value']:.3f} | {metrics['judge_mean']['value']:.3f} / {metrics['human_mean']['value']:.3f} | " + (f"{delta['value']:.3f} [{delta['lo']:.3f}, {delta['hi']:.3f}] |" if delta.get("value") is not None else "n/a |")
        else:
            lines[-1] += " | n/a | n/a | n/a | n/a | n/a | n/a |"
    lines += ["", "All intervals are 95% percentile intervals from 10,000 paired task-cluster draws, p-val=n/a. The repeat-count histogram and mean within-item sample standard deviation for every pool configuration are recorded in `results/selector_utility.json`.", "",
              "## Cross-configuration association", "",
              "These associations are across 12 correlated judge configurations, with the train property fixed and test human-agreement Spearman recomputed inside each task bootstrap draw.", "",
              "| Train property | Configurations | Association Spearman (95% interval) | Pearson | Kendall |",
              "| --- | ---: | --- | --- | --- |"]
    for name, row in associations.items():
        metric = row["metrics"]["spearman"]
        lines.append(f"| {name} | {row['n_configs']} | {metric['value']:.3f} [{metric['lo']:.3f}, {metric['hi']:.3f}] | {row['metrics']['pearson']['value']:.3f} | {row['metrics']['kendall']['value']:.3f} |" if metric["value"] is not None else f"| {name} | {row['n_configs']} | unavailable | n/a | n/a |")
    lines += ["", "## Limitations and next step", "",
              "The selection and association intervals condition on the fixed configuration pool, cached judge scores, selected weights, and current raters; they omit selector, model-population, and new-rater uncertainty.",
              "The historical train/validation/test labels name the original task splits, but every result here reuses historical data and is exploratory.",
              "Information is not sufficient for correctness: score inversion preserves repeat-distribution information, while the deletion direction gate rejects reversed ladders.",
              "The appropriate next step is prospective evaluation with the properties and selector frozen before collecting new ratings.", "",
              "## Artifacts", "",
              "Machine-readable property rows, task detail, frozen selectors, controls, utility, associations, and runtime receipt are under `results/`.", "",
              "**TLDR-end:** [cert-judge: e46 historical measured-cache information properties] The offline study reports all registered properties and fixed-pool utilities from existing measured caches, with no prospective claim.", "",
              "**Snapshot:** 56 measured configurations received property rows; the fixed 12-configuration pool was evaluated with 10,000 paired task-bootstrap draws."]
    (E46 / "RESULTS.md").write_text("\n".join(lines) + "\n")


def evaluate(draws: int) -> int:
    assert_source_freeze()
    selectors = read(OUT / "selectors.json")
    receipt = read(OUT / "selection_receipt.json")
    if receipt["selectors_sha256"] != sha256(OUT / "selectors.json") or selectors["human_outcomes_read"]:
        raise RuntimeError("selector seal is invalid")
    property_rows = read(OUT / "property_rows.json")["configs"]
    meta, items, ratings = load_metadata()
    medians, repeats = score_medians(meta)
    configs = selectors["primary_pool"]
    split_results = {}
    for split in ("val", "test"):
        declared = [row for row in items if row["split"] == split]
        common = [row for row in declared if all(row["item"] in medians[config] for config in configs)]
        if len(common) < math.ceil(.9 * len(declared)):
            split_results[split] = {"status": "UNAVAILABLE_SHARED_SUPPORT", "declared_files": len(declared), "common_files": len(common), "required_common_files": math.ceil(.9 * len(declared))}
        else:
            split_results[split] = evaluate_split(configs, common, medians, repeats, ratings, selectors["weights"], draws, declared_files=len(declared))
    test_rows = [row for row in items if row["split"] == "test" and all(row["item"] in medians[config] for config in configs)]
    associations = association(property_rows, configs, test_rows, medians, ratings, draws)
    evaluation = {"status": "COMPLETE", "draws": draws, "seed": SEED, "primary_pool": configs, "human_target_primary": "current5_mean_0_to_1", "human_target_sensitivity": "current3_mean_0_to_1",
                  "splits": split_results, "source_hashes": source_hashes(), "selectors_sha256": sha256(OUT / "selectors.json"),
                  "limitations": "Conditional on fixed selectors, cached scores, fixed configuration pool, and raters; descriptive intervals only."}
    write("selector_utility.json", evaluation)
    write("association.json", associations)
    render_report(split_results, associations, property_rows)
    write("analysis_receipt.json", {"status": "COMPLETE", "inference_calls": 0, "draws": draws, "seed": SEED, "source_hashes": source_hashes(),
                                      "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                                      "code_hashes": {"core": sha256(ROOT / "py_src/cert_judge/information_properties.py"), "analysis": sha256(Path(__file__)), "tests": sha256(ROOT / "tests/test_information_properties.py")}})
    print(json.dumps({"test_status": split_results["test"]["status"], "association_properties": list(associations), "draws": draws}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("select", "evaluate"))
    parser.add_argument("--draws", type=int, default=DRAWS)
    args = parser.parse_args()
    return select() if args.phase == "select" else evaluate(args.draws)


if __name__ == "__main__":
    raise SystemExit(main())
