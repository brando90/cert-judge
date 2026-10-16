#!/usr/bin/env python3
"""Frozen, offline semantic-effect-margin analysis for experiment 50.

The archived experiment-46 module is imported by path only for its verified
parsers and numerical helpers.  This module never invokes its select/evaluate
entry points and every write target is local to experiment 50.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
E50 = Path(__file__).resolve().parents[1]
OUT = E50 / "results"
E46 = ROOT / "experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation"
E45 = ROOT / "experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit"
SEED, DRAWS = 20261008, 10_000
METRICS = ("spearman", "pearson", "kendall", "mae", "bias", "judge_mean", "human_mean")
ACTIVE_PREFIX = "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/"
ARCHIVE_PREFIX = "experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E46A = load_module("e50_e46_helpers", E46 / "scripts/analyze_information_properties.py")


def read(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_manifest_path(name: str) -> Path:
    """Resolve pre-archive manifest names without rewriting frozen receipts."""
    candidate = ROOT / name
    if candidate.exists() or not name.startswith(ACTIVE_PREFIX):
        return candidate
    return ROOT / (ARCHIVE_PREFIX + name.removeprefix(ACTIVE_PREFIX))


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return clean(value.tolist())
    if isinstance(value, (np.floating, float)): return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, np.integer): return int(value)
    return value


def write(name: str, value) -> Path:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True, allow_nan=False) + "\n")
    return path


def manifest() -> dict:
    return read(OUT / "input_manifest.json")


def assert_freeze() -> None:
    expected = manifest()["files"]
    # The selector was computed with the initial local evaluator source frozen in
    # input_manifest.json.  A dated evaluator-only correction after selection is
    # recorded separately; it may not mutate the frozen data/protocol inputs.
    mutable_after_selection = {
        "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/analyze_semantic_margin.py",
        "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/freeze_inputs.py",
        "tests/test_semantic_margin.py",
    }
    changed = [name for name, digest in expected.items() if name not in mutable_after_selection and sha256(resolve_manifest_path(name)) != digest]
    if changed: raise RuntimeError(f"frozen input changed: {changed}")


def assert_evaluation_source_freeze() -> None:
    """Verify the separately committed post-selection evaluator correction."""
    receipt = read(OUT / "evaluation_source_manifest.json")
    if receipt["selection_receipt_sha256"] != sha256(OUT / "selection_receipt.json"):
        raise RuntimeError("selection receipt changed after selector freeze")
    changed = [name for name, digest in receipt["files"].items() if sha256(resolve_manifest_path(name)) != digest]
    if changed: raise RuntimeError(f"corrected evaluator source changed: {changed}")


def maximum_weights(configs: list[str], values: dict[str, float | None]):
    """Select only the explicitly supplied configs; ties use frozen 1e-12 tolerance."""
    finite = {c: values[c] for c in configs if values.get(c) is not None and math.isfinite(values[c])}
    if not finite: return None
    maximum = max(finite.values())
    winners = sorted(c for c, value in finite.items() if abs(value - maximum) <= 1e-12)
    return {c: 1.0 / len(winners) for c in winners}


def margin_for_split(cells, declarations: dict[str, dict], tasks: set[str]):
    declared = {task: rows for task, rows in declarations.items() if task in tasks}
    detail, values = [], []
    for task, rows in sorted(declared.items()):
        base_repeats = cells.get(("ident", task, 1), {})
        baseline = E46A.median_or_none(list(base_repeats.values()))
        probes = []
        strict, fmt = [], []
        for family, target in (("strict", strict), ("formatting", fmt)):
            for row in rows[family]:
                repeats = cells.get((row["kind"], task, int(row["level"])), {})
                median = E46A.median_or_none(list(repeats.values()))
                probe = {"probe_id": row.get("probe_id"), "kind": row["kind"], "level": int(row["level"]),
                         "family": family, "scores": [repeats[k] for k in sorted(repeats)],
                         "accepted_repeats": len(repeats), "median": median}
                if baseline is not None and median is not None:
                    probe["gap"] = baseline - median if family == "strict" else abs(baseline - median)
                    target.append(probe["gap"])
                probes.append(probe)
        observed = baseline is not None and len(fmt) == len(rows["formatting"]) and len(strict) >= math.ceil(.8 * len(rows["strict"]))
        entry = {"task": task, "identity_scores": [base_repeats[k] for k in sorted(base_repeats)], "identity_accepted_repeats": len(base_repeats),
                 "baseline": baseline, "strict_declared": len(rows["strict"]), "strict_observed": len(strict),
                 "formatting_declared": len(rows["formatting"]), "formatting_observed": len(fmt), "probes": probes, "observed": observed}
        if observed:
            entry.update({"semantic_drop": statistics.mean(strict), "formatting_change": statistics.mean(fmt),
                          "semantic_margin": statistics.mean(strict) - statistics.mean(fmt)})
            values.append(entry["semantic_margin"])
        else: entry["reason"] = "missing_identity_or_all_formatting_or_80pct_strict"
        detail.append(entry)
    required = math.ceil(.8 * len(declared))
    return ({"value": statistics.mean(values) if len(values) >= required and declared else None,
             "declared_tasks": len(declared), "observed_tasks": len(values), "required_tasks": required,
             "coverage": len(values) / len(declared) if declared else 0.0,
             "status": "COMPUTED" if len(values) >= required and declared else "NOT_COMPUTABLE_COVERAGE"}, detail)


def calculate_properties(meta, items):
    """Reuse E46 rows verbatim, adding the frozen signed-margin property and detail."""
    rows, detail = E46A.calculate_properties(meta, items)
    declarations, _ = E46A.semantic_declarations()
    tasks = E46A.split_task_map(items)
    e42 = E46A.E42
    harvests = {p.stem.replace("__", "|"): read(p) for p in sorted((e42 / "results/harvest").glob("*.json"))}
    for config in sorted(meta):
        sem = harvests.get(config)
        for split in ("train", "val", "test"):
            if sem is None:
                result, per_task = ({"value": None, "status": "NOT_COMPUTABLE_NO_SEMANTIC_HARVEST", "declared_tasks": 0, "observed_tasks": 0, "required_tasks": 0, "coverage": 0.0}, [])
            else:
                cells, _ = E46A.accepted_cells(sem)
                result, per_task = margin_for_split(cells, declarations, tasks[split])
            rows[config]["properties"][split]["semantic_margin"] = result
            detail[config][split]["semantic_margin"] = per_task
    return rows, detail


def make_selectors(rows, meta, items, detail):
    pools = E46A.U44.pools(meta)
    primary, h2 = pools["primary_full_context"], pools["same_H2"]
    properties = ("semantic_auc", "repeat_tvd", "deletion_tvd", "C_ms_gold", "prior_strict_minus_format", "semantic_margin")
    train = {name: {c: rows[c]["properties"]["train"][name]["value"] for c in primary} for name in properties}
    weights = {"property_semantic_auc": maximum_weights(primary, train["semantic_auc"]),
               "property_repeat_tvd": maximum_weights(primary, train["repeat_tvd"]),
               "property_deletion_tvd": maximum_weights(primary, train["deletion_tvd"]),
               "max_train_C_ms_gold": maximum_weights(primary, train["C_ms_gold"]),
               "max_train_prior_strict_minus_format": maximum_weights(primary, train["prior_strict_minus_format"]),
               "max_train_semantic_margin": maximum_weights(primary, train["semantic_margin"]),
               "random_primary12": {c: 1.0 / len(primary) for c in primary}, "fixed_H2": {c: 1.0 / len(h2) for c in h2}}
    train_tasks = sorted({x["task"] for x in items if x["split"] == "train" and x["task"] in {d["task"] for d in detail[primary[0]]["train"]["semantic_margin"]}})
    leave_task = {}
    for omitted in train_tasks:
        values = {}
        for config in primary:
            retained = [x["semantic_margin"] for x in detail[config]["train"]["semantic_margin"] if x["observed"] and x["task"] != omitted]
            declared = [x for x in detail[config]["train"]["semantic_margin"] if x["task"] != omitted]
            values[config] = statistics.mean(retained) if len(retained) >= math.ceil(.8 * len(declared)) and declared else None
        leave_task[omitted] = {"train_values": values, "weights": maximum_weights(primary, values)}
    model_ids = sorted({c.split("|", 1)[0] for c in primary})
    leave_model = {}
    for model in model_ids:
        remaining = [c for c in primary if not c.startswith(model + "|")]
        values = {c: train["semantic_margin"][c] for c in remaining}
        leave_model[model] = {"pool": remaining, "train_values": values, "weights": maximum_weights(remaining, values)}
    return {"status": "FROZEN_BEFORE_HUMAN_OUTCOMES", "protocol_sha256": sha256(E50 / "PROTOCOL.md"), "input_hashes": manifest()["files"],
            "seed": SEED, "primary_pool": primary, "h2_pool": h2, "train_property_values": train, "weights": weights,
            "leave_training_task": leave_task, "leave_model_harness": leave_model,
            "declared_split_counts": {s: sum(x["split"] == s for x in items) for s in ("train", "val", "test")}, "human_outcomes_read": False}


def select():
    assert_freeze()
    meta, items, _ = E46A.load_metadata(include_ratings=False)
    rows, detail = calculate_properties(meta, items)
    write("configuration_overview.json", {"status": "COMPLETE", "configs": rows})
    write("per_probe_task_components.json", detail)
    selectors = make_selectors(rows, meta, items, detail)
    path = write("selectors.json", selectors)
    write("selection_receipt.json", {"status": "COMPLETE", "selectors_sha256": sha256(path), "human_outcomes_read": False, "source_hashes": manifest()["files"]})
    print(json.dumps({"configs": len(rows), "primary_pool": len(selectors["primary_pool"]), "selectors": str(path.relative_to(ROOT))}, indent=2))


def metric_block(configs, matrix, human, groups, weights, draws):
    rng = np.random.default_rng(SEED)
    group_draws = rng.integers(0, len(groups), size=(draws, len(groups)))
    point_pc = E46A.per_config_bootstrap_metrics(matrix, human, np.arange(len(human))[None, :])[0]
    boot_pc = E46A.task_cluster_bootstrap_metrics(matrix, human, group_draws, groups)
    points = E46A.expected_selector_metrics(point_pc[None, :, :], configs, weights)[0]
    boots = E46A.expected_selector_metrics(boot_pc, configs, weights)
    return {metric: E46A.interval(points[i], boots[:, i]) for i, metric in enumerate(METRICS)}, point_pc, boot_pc


def evaluate_split(configs, split_rows, medians, repeats, ratings, selectors, draws, declared_files):
    ids = [r["item"] for r in split_rows]
    matrix = np.array([[medians[c][item] for item in ids] for c in configs])
    group_index = defaultdict(list)
    for i, row in enumerate(split_rows): group_index[row["task"]].append(i)
    groups = [np.asarray(group_index[t], int) for t in sorted(group_index)]
    targets, per_judge = {}, {}
    for target in ("current5_mean_0_to_1", "current3_mean_0_to_1"):
        human = np.array([ratings[item][target] for item in ids], float)
        _, point_pc, boot_pc = metric_block(configs, matrix, human, groups, selectors["fixed_H2"], draws)
        # Build all selector statistics with the identical seed/draws, then paired margin contrasts.
        selector_rows, boot_cache, point_cache = {}, {}, {}
        for name, weights in selectors.items():
            point = E46A.expected_selector_metrics(point_pc[None, :, :], configs, weights)[0]
            boot = E46A.expected_selector_metrics(boot_pc, configs, weights)
            selector_rows[name] = {"weights": weights, "metrics": {m: E46A.interval(point[i], boot[:, i]) for i, m in enumerate(METRICS)}}
            point_cache[name], boot_cache[name] = point, boot
        margin = "max_train_semantic_margin"
        contrasts = {name: {m: E46A.interval(point_cache[margin][i] - point_cache[name][i] if np.isfinite(point_cache[margin][i]) and np.isfinite(point_cache[name][i]) else None, boot_cache[margin][:, i] - boot_cache[name][:, i]) for i, m in enumerate(METRICS)} for name in selectors if name != margin}
        per_judge[target] = {c: {m: E46A.interval(point_pc[i, j], boot_pc[:, i, j]) for j, m in enumerate(METRICS)} for i, c in enumerate(configs)}
        targets[target] = {"selectors": selector_rows, "margin_minus_every_comparator": contrasts}
    return {"status": "COMPUTED", "declared_files": declared_files, "common_files": len(ids), "common_tasks": len(groups), "item_ids": ids,
            "required_common_files": math.ceil(.9 * declared_files), "resampling_unit": "paired task clusters", "draws": draws, "seed": SEED,
            "targets": targets, "per_judge": per_judge,
            "repeat_counts": {c: {"available": sum(len(repeats[c].get(i, [])) for i in ids), "expected": 3 * len(ids),
                                  "per_item_count_histogram": dict(Counter(len(repeats[c].get(i, [])) for i in ids)),
                                  "mean_within_item_sample_sd": statistics.mean([statistics.stdev(repeats[c][i]) for i in ids if len(repeats[c].get(i, [])) >= 2])} for c in configs}}


def association(rows, configs, split_rows, medians, ratings, draws):
    # Narrow extension of E46's association logic: semantic_margin is a fourth property.
    out = E46A.association(rows, configs, split_rows, medians, ratings, draws)
    ids = [x["item"] for x in split_rows]; matrix = np.array([[medians[c][i] for i in ids] for c in configs]); y = np.array([ratings[i]["current5_mean_0_to_1"] for i in ids])
    groups_by_task = defaultdict(list)
    for i, row in enumerate(split_rows): groups_by_task[row["task"]].append(i)
    groups = [np.asarray(groups_by_task[t], int) for t in sorted(groups_by_task)]
    rng = np.random.default_rng(SEED); draws_ix = rng.integers(0, len(groups), size=(draws, len(groups)))
    point = E46A.per_config_bootstrap_metrics(matrix, y, np.arange(len(ids))[None, :])[0, :, 0]
    boot_agree = E46A.task_cluster_bootstrap_metrics(matrix, y, draws_ix, groups)[:, :, 0]
    values = np.array([rows[c]["properties"]["train"]["semantic_margin"]["value"] for c in configs], float); keep = np.isfinite(values)
    pts = E46A.safe_corr(values[keep], point[keep]) if keep.sum() >= 3 else {m: None for m in ("spearman", "pearson", "kendall")}
    boot = {m: np.full(draws, np.nan) for m in pts}
    if keep.sum() >= 3:
        x = np.broadcast_to(values[keep], (draws, keep.sum())); yb = boot_agree[:, keep]
        boot["pearson"] = E46A._corr_rows(x, yb); boot["spearman"] = E46A._corr_rows(E46A.rankdata(x, axis=-1), E46A.rankdata(yb, axis=-1))
        left, right = np.triu_indices(keep.sum(), 1); sx, sy = np.sign(x[:, left] - x[:, right]), np.sign(yb[:, left] - yb[:, right])
        with np.errstate(invalid="ignore", divide="ignore"): boot["kendall"] = (sx * sy).sum(-1) / np.sqrt((sx * sx).sum(-1) * (sy * sy).sum(-1))
    out["semantic_margin"] = {"status": "COMPUTED" if keep.sum() >= 3 else "NOT_COMPUTABLE_LT3_CONFIGS", "n_configs": int(keep.sum()), "configs": [c for c, v in zip(configs, keep) if v], "metrics": {m: E46A.interval(pts[m], boot[m]) for m in pts}, "properties_fixed_across_task_bootstrap": True}
    return out


def robustness(rows, selectors, meta, items, medians, repeats, ratings, draws):
    configs = selectors["primary_pool"]
    common = [r for r in items if r["split"] == "test" and all(r["item"] in medians[c] for c in configs)]
    # Test-task deletion retains the primary fixed selectors and reports paired primary point difference.
    omit_test = {}
    for task in sorted({r["task"] for r in common}):
        remaining = [r for r in common if r["task"] != task]
        result = evaluate_split(configs, remaining, medians, repeats, ratings, selectors["weights"], draws, len(remaining))
        omit_test[task] = result["targets"]["current5_mean_0_to_1"]["margin_minus_every_comparator"]["fixed_H2"]["spearman"]
    model = {}
    for label, variant in selectors["leave_model_harness"].items():
        pool, weights = variant["pool"], variant["weights"]
        # Original full-pool common rows, intentionally not recomputed after removal.
        model[label] = {"pool": pool, "weights": weights,
                        "test": evaluate_split(pool, common, medians, repeats, ratings, {"max_train_semantic_margin": weights, "fixed_H2": {c: 1/len([x for x in selectors["h2_pool"] if x in pool]) for c in selectors["h2_pool"] if c in pool}}, draws, 30)["targets"]}
    return {"leave_training_task_selectors": selectors["leave_training_task"], "leave_test_task_primary_delta_spearman": omit_test,
            "leave_model_harness": model, "original_full_pool_common_test_files": [r["item"] for r in common]}


def evaluate(draws):
    assert_freeze(); assert_evaluation_source_freeze(); selectors = read(OUT / "selectors.json"); receipt = read(OUT / "selection_receipt.json")
    if receipt["selectors_sha256"] != sha256(OUT / "selectors.json") or selectors["human_outcomes_read"]: raise RuntimeError("selector seal is invalid")
    rows = read(OUT / "configuration_overview.json")["configs"]
    meta, items, ratings = E46A.load_metadata(include_ratings=True); medians, repeats = E46A.score_medians(meta); configs = selectors["primary_pool"]
    splits = {}
    for split in ("val", "test"):
        declared = [r for r in items if r["split"] == split]; common = [r for r in declared if all(r["item"] in medians[c] for c in configs)]
        splits[split] = evaluate_split(configs, common, medians, repeats, ratings, selectors["weights"], draws, len(declared)) if len(common) >= math.ceil(.9 * len(declared)) else {"status": "UNAVAILABLE_SHARED_SUPPORT", "declared_files": len(declared), "common_files": len(common), "required_common_files": math.ceil(.9 * len(declared))}
    test_rows = [r for r in items if r["split"] == "test" and all(r["item"] in medians[c] for c in configs)]
    evaluation = {"status": "COMPLETE", "draws": draws, "seed": SEED, "primary_pool": configs, "human_target_primary": "current5_mean_0_to_1", "human_target_sensitivity": "current3_mean_0_to_1", "splits": splits, "selectors_sha256": sha256(OUT / "selectors.json"), "source_hashes": manifest()["files"]}
    write("evaluation.json", evaluation); write("association.json", association(rows, configs, test_rows, medians, ratings, draws)); write("robustness.json", robustness(rows, selectors, meta, items, medians, repeats, ratings, draws))
    write("runtime.json", {"status": "COMPLETE", "inference_calls": 0, "draws": draws, "seed": SEED, "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}, "code_sha256": sha256(Path(__file__)), "source_hashes": manifest()["files"]})
    print(json.dumps({"val": splits["val"]["status"], "test": splits["test"]["status"], "draws": draws}, indent=2))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("phase", choices=("select", "evaluate")); parser.add_argument("--draws", type=int, default=DRAWS); args = parser.parse_args()
    return select() if args.phase == "select" else evaluate(args.draws)


if __name__ == "__main__": main()
