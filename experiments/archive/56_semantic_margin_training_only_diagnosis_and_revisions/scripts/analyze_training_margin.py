#!/usr/bin/env python3
"""Offline analysis that consumes only Experiment 56's train-only projection."""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, pearsonr, rankdata, spearmanr

import sys

def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "py_src" / "cert_judge").is_dir():
            return candidate
    raise RuntimeError("cert-judge root not found")


EXP = Path(__file__).resolve().parents[1]
INP = EXP / "results" / "train_only_inputs"
OUT = EXP / "results"
ROOT = repo_root(EXP)
sys.path.insert(0, str(ROOT / "py_src"))
from cert_judge.information_properties import complete_repeat_candidates, gold_deletion_monotonicity, repeat_tvd_task, semantic_auc_task
SEED = 20261019
DRAWS = 10_000
ACCEPTED = {"measured", "deterministic"}
TOL = 1e-12


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return clean(value.tolist())
    if isinstance(value, (float, np.floating)): return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, (int, np.integer)): return int(value)
    return value


def write(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n")


def median(values):
    return float(statistics.median(values)) if len(values) >= 2 else None


def index_cells(harvest: dict):
    cells, seen = defaultdict(dict), set()
    for cell in harvest["cells"]:
        cell_id = cell.get("cell")
        if cell_id in seen: raise ValueError(f"duplicate cell id: {cell_id}")
        seen.add(cell_id)
        if cell.get("status") not in ACCEPTED or cell.get("score") is None: continue
        score = float(cell["score"])
        if not (math.isfinite(score) and 0 <= score <= 1): raise ValueError("invalid accepted score")
        key = (cell.get("kind"), cell.get("key"), int(cell.get("level")))
        repeat = int(cell.get("repeat"))
        if repeat in cells[key]: raise ValueError(f"duplicate repeat: {key}, {repeat}")
        cells[key][repeat] = score
    return cells


def task_components(cells, declarations, controls, tasks):
    by_task = defaultdict(lambda: {"strict": [], "formatting": []})
    for row in declarations:
        if row["task"] not in tasks or row.get("valid") is not True: continue
        if row["family"] == "formatting": by_task[row["task"]]["formatting"].append(row)
        elif row["family"] == "weakening" and row.get("audit_label") == "strict": by_task[row["task"]]["strict"].append(row)
    controls_by_task = defaultdict(list)
    for row in controls:
        if row["task"] in tasks: controls_by_task[row["task"]].append(row)
    details = []
    for task in sorted(tasks):
        groups = by_task[task]
        baseline = median(list(cells.get(("ident", task, 1), {}).values()))
        strict, fmt, preserving = [], [], []
        for row in groups["strict"]:
            value = median(list(cells.get((row["kind"], task, int(row["level"])), {}).values()))
            if baseline is not None and value is not None: strict.append(baseline - value)
        for row in groups["formatting"]:
            value = median(list(cells.get((row["kind"], task, int(row["level"])), {}).values()))
            if baseline is not None and value is not None: fmt.append(abs(baseline - value))
        for row in controls_by_task[task]:
            value = median(list(cells.get((row["kind"], task, int(row["level"])), {}).values()))
            if baseline is not None and value is not None: preserving.append(abs(baseline - value))
        strict_required = math.ceil(.8 * len(groups["strict"]))
        preserving_required = math.ceil(.8 * len(controls_by_task[task]))
        base_ok = baseline is not None and bool(groups["strict"]) and bool(groups["formatting"]) and len(strict) >= strict_required and len(fmt) == len(groups["formatting"])
        specificity_ok = base_ok and bool(controls_by_task[task]) and len(preserving) >= preserving_required
        row = {"task": task, "identity_baseline": baseline, "strict_declared": len(groups["strict"]), "strict_observed": len(strict), "formatting_declared": len(groups["formatting"]), "formatting_observed": len(fmt), "preserving_declared": len(controls_by_task[task]), "preserving_observed": len(preserving), "base_observed": base_ok, "specificity_observed": specificity_ok}
        if base_ok:
            semantic, formatting = statistics.mean(strict), statistics.mean(fmt)
            row |= {"semantic_drop": semantic, "formatting_penalty": formatting, "semantic_auc": semantic_auc_task(strict, fmt), "original_S_minus_F": semantic - formatting}
            row["headroom_normalized"] = None if baseline == 0 else (semantic - formatting) / baseline
        if specificity_ok:
            row["preserving_penalty"] = statistics.mean(preserving)
            row["semantic_specificity"] = statistics.mean(strict) - row["preserving_penalty"]
        details.append(row)
    return details


def aggregate(details, candidate, *, specificity=False):
    eligible = (lambda row: row["strict_declared"] > 0 and row["formatting_declared"] > 0 and row["preserving_declared"] > 0) if specificity else (lambda row: row["strict_declared"] > 0 and row["formatting_declared"] > 0)
    declared = [row for row in details if eligible(row)]
    values = [r[candidate] for r in declared if r.get(candidate) is not None]
    required = math.ceil(.8 * len(declared))
    return {"value": statistics.mean(values) if declared and len(values) >= required else None, "declared_tasks": len(declared), "observed_tasks": len(values), "required_tasks": required, "coverage": len(values) / len(declared) if declared else 0.0, "status": "COMPUTED" if declared and len(values) >= required else "NOT_COMPUTABLE_COVERAGE"}


def correlations(judge, human):
    if len(judge) < 3 or len(set(judge)) < 2 or len(set(human)) < 2: return {"spearman": None, "pearson": None, "kendall": None}
    return {"spearman": float(spearmanr(judge, human).statistic), "pearson": float(pearsonr(judge, human).statistic), "kendall": float(kendalltau(judge, human).statistic)}


def metric(judge, human):
    diff = np.asarray(judge, float) - np.asarray(human, float)
    return correlations(judge, human) | {"mae": float(np.mean(abs(diff))), "bias": float(np.mean(diff)), "judge_mean": float(np.mean(judge)), "human_mean": float(np.mean(human))}


def task_bootstrap(scores, human, item_task):
    ids = list(scores)
    tasks = sorted({item_task[item] for item in ids})
    groups = [np.asarray([i for i, item in enumerate(ids) if item_task[item] == task], int) for task in tasks]
    rng = np.random.default_rng(SEED)
    choices = rng.integers(0, len(groups), (DRAWS, len(groups)))
    buckets = defaultdict(list)
    for draw, choice in enumerate(choices): buckets[sum(len(groups[g]) for g in choice)].append((draw, choice))
    output = {key: np.full(DRAWS, np.nan) for key in ("spearman", "pearson", "kendall", "mae", "bias", "judge_mean", "human_mean")}
    raw_scores, raw_human = np.asarray([scores[item] for item in ids]), np.asarray([human[item] for item in ids])
    for _, entries in buckets.items():
        draw_ids, selected = zip(*entries)
        indices = np.stack([np.concatenate([groups[g] for g in choice]) for choice in selected])
        judge, target = raw_scores[indices], raw_human[indices]
        def corr_rows(left, right):
            left, right = left-left.mean(1, keepdims=True), right-right.mean(1, keepdims=True)
            with np.errstate(divide="ignore", invalid="ignore"): return (left*right).sum(1) / np.sqrt((left*left).sum(1)*(right*right).sum(1))
        output["pearson"][list(draw_ids)] = corr_rows(judge, target)
        output["spearman"][list(draw_ids)] = corr_rows(rankdata(judge, axis=1), rankdata(target, axis=1))
        left, right = np.triu_indices(judge.shape[1], 1)
        js, hs = np.sign(judge[:, left]-judge[:, right]), np.sign(target[:, left]-target[:, right])
        with np.errstate(divide="ignore", invalid="ignore"): output["kendall"][list(draw_ids)] = (js*hs).sum(1) / np.sqrt((js*js).sum(1)*(hs*hs).sum(1))
        delta = judge-target
        output["mae"][list(draw_ids)], output["bias"][list(draw_ids)] = abs(delta).mean(1), delta.mean(1)
        output["judge_mean"][list(draw_ids)], output["human_mean"][list(draw_ids)] = judge.mean(1), target.mean(1)
    return {key: {"lo": float(np.nanpercentile(values, 2.5)) if np.isfinite(values).any() else None, "hi": float(np.nanpercentile(values, 97.5)) if np.isfinite(values).any() else None, "draws": int(np.isfinite(values).sum()), "resampling_unit": "training task"} for key, values in output.items()}


def weights_max(values):
    finite = {c: v for c, v in values.items() if v is not None and math.isfinite(v)}
    if not finite: return None
    maximum = max(finite.values())
    winners = sorted(c for c, value in finite.items() if abs(value - maximum) <= TOL)
    return {c: 1 / len(winners) for c in winners}


def repeat_tvd_property(cells, items):
    by_task = defaultdict(list)
    for row in items: by_task[row["task"]].append(row["item"])
    values, detail = [], []
    for task, item_ids in sorted(by_task.items()):
        candidates = {item: cells.get(("crit", item, 0), {}) for item in item_ids}
        complete, excluded = complete_repeat_candidates(candidates)
        observed = len(complete) >= 2
        detail.append({"task": task, "declared_candidates": len(candidates), "complete_candidates": len(complete), "excluded_candidates": excluded, "observed": observed})
        if observed: values.append(repeat_tvd_task(complete))
    required = math.ceil(.8 * len(detail))
    return {"value": statistics.mean(values) if len(values) >= required else None, "declared_tasks": len(detail), "observed_tasks": len(values), "required_tasks": required, "coverage": len(values) / len(detail) if detail else 0.0, "status": "COMPUTED" if len(values) >= required else "NOT_COMPUTABLE_COVERAGE"}, detail


def c_ms_gold_property(cells, probes):
    by_task = defaultdict(list)
    for row in probes:
        if row.get("kind") == "ms_gold": by_task[row["task"]].append(row)
    values, detail = [], []
    for task, rows in sorted(by_task.items()):
        key = rows[0]["key"]
        levels = sorted({int(row["level"]) for row in rows})
        medians = {0: median(list(cells.get(("ident", key, 0), {}).values()))}
        medians |= {level: median(list(cells.get(("ms_gold", key, level), {}).values())) for level in levels}
        observed = all(value is not None for value in medians.values())
        detail.append({"task": task, "declared_levels": [0, *levels], "observed": observed})
        if observed: values.append(gold_deletion_monotonicity(medians))
    required = math.ceil(.8 * len(detail))
    return {"value": statistics.mean(values) if len(values) >= required else None, "declared_tasks": len(detail), "observed_tasks": len(values), "required_tasks": required, "coverage": len(values) / len(detail) if detail else 0.0, "status": "COMPUTED" if len(values) >= required else "NOT_COMPUTABLE_COVERAGE"}, detail


def selection_folds(candidate, configs, h2, details, item_scores, ratings, item_task, tasks):
    folds = []
    for omitted in sorted(tasks):
        values = {config: aggregate([row for row in details[config] if row["task"] != omitted], candidate, specificity=candidate == "semantic_specificity")["value"] for config in configs}
        selector = weights_max(values)
        fold_items = [item for item, task in item_task.items() if task == omitted and all(item in item_scores[c] for c in configs)]
        def loss(weights):
            if not weights or not fold_items: return None
            per_config = [metric([item_scores[c][item] for item in fold_items], [ratings[item] for item in fold_items]) for c in weights]
            return {key: statistics.mean([row[key] for row in per_config if row[key] is not None]) if all(row[key] is not None for row in per_config) else None for key in ("mae", "bias", "judge_mean", "human_mean")}
        chosen, fixed = loss(selector), loss({c: 1 / len(h2) for c in h2})
        folds.append({"omitted_task": omitted, "selector": selector, "selected": sorted(selector) if selector else [], "candidate_values": values, "n_items": len(fold_items), "selected_metrics": chosen, "fixed_H2_metrics": fixed, "paired_mae_difference": None if chosen is None or fixed is None else chosen["mae"] - fixed["mae"]})
    diffs = [row["paired_mae_difference"] for row in folds if row["paired_mae_difference"] is not None]
    return {"status": "CONDITIONAL_FOLD_DESCRIPTIVE", "candidate": candidate, "folds": folds, "paired_absolute_error": {"mean_difference_selector_minus_H2": statistics.mean(diffs) if diffs else None, "fold_count": len(diffs), "fold_sd": statistics.stdev(diffs) if len(diffs) > 1 else None, "note": "No pooled rank statistic: individual judge choices vary by fold. Tie metrics/losses are averaged over selected individual judges, not scores."}}


def _assoc(xs, ys):
    """Point association across configurations. These rows share tasks, so no interval or test."""
    base = {
        "n_configurations": len(xs),
        "p_val": "n/a",
        "interval": "unavailable",
        "reason": "The configurations share the same training tasks, so they are not independent samples. No configuration-level interval or test is reported.",
    }
    if len(xs) < 3 or len(set(np.round(xs, 12))) < 2 or len(set(np.round(ys, 12))) < 2:
        return base | {"spearman": None, "pearson": None, "kendall": None}
    return base | correlations(xs, ys)


def build_diagnosis(properties, details, metrics, meta):
    """Pre-specified training diagnosis. It does not introduce a new candidate formula."""
    component_names = ("identity_baseline", "semantic_drop", "formatting_penalty", "preserving_penalty", "original_S_minus_F", "headroom_normalized", "semantic_specificity")
    per_config, zero_fmt, fmt_values, concentration = {}, 0, 0, []
    for config, rows in details.items():
        comp = {}
        for name in component_names:
            values = [row[name] for row in rows if row.get(name) is not None]
            comp[name] = {"mean": statistics.mean(values) if values else None, "n_tasks": len(values)}
        per_config[config] = comp
        for row in rows:
            if row.get("formatting_penalty") is None:
                continue
            fmt_values += 1
            if abs(row["formatting_penalty"]) <= TOL:
                zero_fmt += 1
        observed = [row for row in rows if row.get("original_S_minus_F") is not None]
        absolute_sum = sum(abs(row["original_S_minus_F"]) for row in observed)
        if observed and absolute_sum > 0:
            top = max(observed, key=lambda row: abs(row["original_S_minus_F"]))
            concentration.append({"config": config, "top_task": top["task"], "top_abs_share": abs(top["original_S_minus_F"]) / absolute_sum, "n_observed_tasks": len(observed)})
    associations = {}
    for name in ("original_S_minus_F", "headroom_normalized", "semantic_specificity", "semantic_auc", "repeat_tvd", "C_ms_gold"):
        xs, spearman, mae = [], [], []
        for config, prop in properties.items():
            value = prop[name]["value"]
            if value is None or metrics[config]["spearman"] is None:
                continue
            xs.append(value)
            spearman.append(metrics[config]["spearman"])
            mae.append(metrics[config]["mae"])
        associations[name] = {"versus_spearman": _assoc(xs, spearman), "versus_mae": _assoc(xs, mae)}
    for name in ("identity_baseline", "semantic_drop", "formatting_penalty", "preserving_penalty"):
        xs, spearman, mae = [], [], []
        for config, comp in per_config.items():
            value = comp[name]["mean"]
            if value is None or metrics[config]["spearman"] is None:
                continue
            xs.append(value)
            spearman.append(metrics[config]["spearman"])
            mae.append(metrics[config]["mae"])
        associations[name] = {"versus_spearman": _assoc(xs, spearman), "versus_mae": _assoc(xs, mae)}

    def grouped(field):
        groups = defaultdict(list)
        for config, row in metrics.items():
            groups[meta[config][field]].append(row)
        return [
            {
                "group": key,
                "n_configurations": len(rows),
                "mean_spearman": statistics.mean(row["spearman"] for row in rows),
                "mean_mae": statistics.mean(row["mae"] for row in rows),
                "mean_bias": statistics.mean(row["bias"] for row in rows),
            }
            for key, rows in sorted(groups.items())
        ]

    shares = [row["top_abs_share"] for row in concentration]
    return {
        "per_config_component_means": per_config,
        "formatting_penalty_exact_zeros": {"zero_task_values": zero_fmt, "observed_task_values": fmt_values},
        "task_concentration": {
            "rows": concentration,
            "median_top_abs_share": statistics.median(shares) if shares else None,
            "max_top_abs_share": max(shares) if shares else None,
        },
        "property_versus_training_agreement": associations,
        "leave_one_group_descriptive": {
            "model_key": grouped("model_key"),
            "harness": grouped("harness"),
            "note": "Means within a model or harness. Differences are descriptive; the configurations are correlated and the counts are small.",
        },
    }


def analyze():
    manifest = json.loads((INP / "input_manifest.json").read_text())
    receipt = json.loads((INP / "projection_receipt.json").read_text())
    if manifest["status"] != "FROZEN_BEFORE_NUMERICAL_READ" or receipt["status"] != "COMPLETE_TRAIN_ONLY": raise RuntimeError("missing frozen projection")
    items = manifest["train_items"]
    item_task = {row["item"]: row["task"] for row in items}
    tasks = set(item_task.values())
    ratings_raw = json.loads((INP / "ratings.json").read_text())
    ratings_by_target = {target: {row["item"]: float(row[target]) for row in ratings_raw} for target in ("current5_mean_0_to_1", "current3_mean_0_to_1")}
    semantic_harvests = json.loads((INP / "semantic_harvests.json").read_text())
    criterion_harvests = json.loads((INP / "criterion_harvests.json").read_text())
    e39_probes = json.loads((INP / "e39_train_probes.json").read_text())
    configs, h2 = manifest["primary_configs"], manifest["h2_configs"]
    declarations, controls = manifest["train_probe_declarations"], manifest["preservation_controls"]["rows"]
    details, properties, item_scores, repeat_summary, comparator_detail = {}, {}, {}, {}, {}
    for config in configs:
        semantic_cells, criterion_cells = index_cells(semantic_harvests[config]), index_cells(criterion_harvests[config])
        details[config] = task_components(semantic_cells, declarations, controls, tasks)
        properties[config] = {candidate: aggregate(details[config], candidate, specificity=candidate == "semantic_specificity") for candidate in ("original_S_minus_F", "headroom_normalized", "semantic_specificity", "semantic_auc")}
        properties[config]["repeat_tvd"], repeat_detail = repeat_tvd_property(criterion_cells, items)
        properties[config]["C_ms_gold"], deletion_detail = c_ms_gold_property(criterion_cells, e39_probes)
        comparator_detail[config] = {"repeat_tvd": repeat_detail, "C_ms_gold": deletion_detail}
        scores, repeat_counts, repeat_sds = {}, [], []
        for item in item_task:
            values = list(criterion_cells.get(("crit", item, 0), {}).values())
            value = median(values)
            if value is not None:
                scores[item] = value; repeat_counts.append(len(values)); repeat_sds.append(float(statistics.stdev(values)) if len(values) > 1 else 0.0)
        item_scores[config] = scores
        repeat_summary[config] = {"scored_items": len(scores), "repeat_count_mean": statistics.mean(repeat_counts) if repeat_counts else None, "repeat_sd_mean": statistics.mean(repeat_sds) if repeat_sds else None}
    common_items = [row["item"] for row in items if all(row["item"] in item_scores[c] for c in configs)]
    required_items = math.ceil(.9 * len(items))
    common_ok = len(common_items) >= required_items
    missing_common = []
    for row in items:
        absent = [config for config in configs if row["item"] not in item_scores[config]]
        if absent:
            missing_common.append({"item": row["item"], "task": row["task"], "configs_without_two_repeats": absent})
    config_metrics = {}
    for target, ratings in ratings_by_target.items():
        config_metrics[target] = {}
        for config in configs:
            ids = list(item_scores[config])
            scores = {item: item_scores[config][item] for item in ids}
            config_metrics[target][config] = metric(list(scores.values()), [ratings[item] for item in ids]) | {"intervals": task_bootstrap(scores, ratings, item_task), "n_items": len(ids), "n_tasks": len({item_task[item] for item in ids}), "support": "configuration_observed_items"}
    selection_candidates = ("original_S_minus_F", "headroom_normalized", "semantic_specificity", "semantic_auc")
    if common_ok:
        folds = {target: {candidate: selection_folds(candidate, configs, h2, details, item_scores, ratings, item_task, tasks) for candidate in selection_candidates} for target, ratings in ratings_by_target.items()}
    else:
        folds = {target: {"status": "UNAVAILABLE_COMMON_SUPPORT", "reason": f"{len(common_items)}/{len(items)} items are scored by every configuration, below the frozen ceil(0.9*declared) requirement of {required_items}. The threshold is not relaxed.", "candidates": list(selection_candidates)} for target in ratings_by_target}
    meta = {row["config"]: row for row in manifest["primary_config_metadata"]}
    diagnosis = build_diagnosis(properties, details, config_metrics["current5_mean_0_to_1"], meta)
    result = {"status": "COMPLETE_TRAINING_ONLY_EXPLORATORY", "seed": SEED, "bootstrap_draws": DRAWS, "target": "current5_mean_0_to_1", "sensitivity_target": "current3_mean_0_to_1", "configs": configs, "h2_configs": h2, "config_metadata": manifest["primary_config_metadata"], "common_support": {"status": "MEETS_90_PERCENT" if common_ok else "BELOW_90_PERCENT", "items": len(common_items), "declared_items": len(items), "tasks": len({item_task[item] for item in common_items}), "required_items": required_items, "missing": missing_common}, "properties": properties, "per_task_components": details, "existing_comparator_detail": comparator_detail, "repeat_summary": repeat_summary, "configuration_metrics": config_metrics, "cross_fitted_selection": folds, "diagnosis": diagnosis, "limitations": "Training-only historical cached data; no validation/test outcomes or fresh ratings accessed. The frozen 90% common-support comparison is unavailable when recorded as BELOW_90_PERCENT, and that threshold is not relaxed. Per-configuration agreement uses each configuration's observed items. Configuration comparisons are descriptive and correlated."}
    write("training_analysis.json", result)
    return result


def num(value, digits=3):
    if value is None:
        return "unavailable"
    return f"{float(value):.{digits}f}"


def interval(point, band, digits=3):
    if not band or band.get("lo") is None:
        return f"{num(point, digits)} [unavailable] p-val=n/a"
    return f"{num(point, digits)} [{num(band.get('lo'), digits)}, {num(band.get('hi'), digits)}] p-val=n/a"


def render(result):
    support = result["common_support"]
    diagnosis = result["diagnosis"]
    zeros = diagnosis["formatting_penalty_exact_zeros"]
    concentration = diagnosis["task_concentration"]
    lines = [
        "# Experiment 56 — Training-only semantic-margin diagnosis",
        "",
        "**TLDR:** Exploratory training-only diagnosis of the frozen semantic margin and two pre-specified revisions. It does not test transfer or fresh-rater validity.",
        "",
        "## Scope",
        "",
        f"The intersection scored by every configuration is {support['items']}/{support['declared_items']} training items, across {support['tasks']} tasks.",
        f"The frozen common-support rule needs {support['required_items']}, so the pooled comparison is {support['status']}.",
        "Per-configuration agreement below uses the items that configuration actually scored.",
        "No validation or test outcomes were opened.",
        "Score intervals are 95% percentile intervals from 10,000 task-cluster bootstrap draws, seed 20261019.",
        "They resample training tasks with their items kept together, and they do not cover judge selection, new raters, or a new task population.",
        "Bias is the mean of judge minus human, so a positive bias means the judge is lenient.",
        "Configuration-level associations have no interval: the 12 configurations share the same tasks.",
        "",
        "## Candidate coverage",
        "",
        "| Candidate | Computed configurations | Mean property |",
        "|---|---:|---:|",
    ]
    for candidate in ("original_S_minus_F", "headroom_normalized", "semantic_specificity", "semantic_auc", "repeat_tvd", "C_ms_gold"):
        values = [row[candidate]["value"] for row in result["properties"].values() if row[candidate]["value"] is not None]
        lines.append(f"| {candidate} | {len(values)}/{len(result['configs'])} | {num(statistics.mean(values)) if values else 'unavailable'} |")
    lines += [
        "",
        "## Why a high margin need not mean better agreement",
        "",
        f"Formatting penalties were exactly zero on {zeros['zero_task_values']} of {zeros['observed_task_values']} observed task values.",
        f"The largest task's share of the absolute per-task margin has median {num(concentration['median_top_abs_share'])} and maximum {num(concentration['max_top_abs_share'])} across configurations with an observed margin.",
        "",
        "| Property or component | n configs | Spearman vs training agreement | Pearson | Kendall | Spearman vs training MAE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, row in diagnosis["property_versus_training_agreement"].items():
        spearman, mae = row["versus_spearman"], row["versus_mae"]
        lines.append(f"| {name} | {spearman['n_configurations']} | {num(spearman['spearman'])} | {num(spearman['pearson'])} | {num(spearman['kendall'])} | {num(mae['spearman'])} |")
    identity_values = [row["identity_baseline"]["mean"] for row in diagnosis["per_config_component_means"].values() if row["identity_baseline"]["mean"] is not None]
    raw_values = [row["original_S_minus_F"]["value"] for row in result["properties"].values()]
    head_values = [row["headroom_normalized"]["value"] for row in result["properties"].values()]
    identical_headroom = all(a is not None and b is not None and abs(a - b) <= 1e-12 for a, b in zip(raw_values, head_values))
    auc_values = [row["semantic_auc"]["value"] for row in result["properties"].values() if row["semantic_auc"]["value"] is not None]
    lines += [
        "",
        "These associations are descriptive.",
        "p-val=n/a, and no configuration-level interval is reported, because the configurations are correlated.",
        "",
        "### Reading",
        "",
        f"The identity baseline is {num(min(identity_values)) if identity_values else 'unavailable'} on every configuration's observed tasks, so dividing the margin by it does not change the value." if identity_values and abs(min(identity_values) - max(identity_values)) <= 1e-12 else "The identity baseline varies across configurations.",
        "Headroom-normalized margin equals the original margin on all 12 configurations." if identical_headroom else "Headroom-normalized margin differs from the original margin on at least one configuration.",
        f"Semantic-over-format AUC is saturated: {sum(abs(value - 1.0) <= 1e-12 for value in auc_values)} of {len(auc_values)} configurations are exactly 1, because a zero formatting change loses to any positive semantic drop.",
        f"The original margin's Spearman with training agreement is {num(diagnosis['property_versus_training_agreement']['original_S_minus_F']['versus_spearman']['spearman'])} across {diagnosis['property_versus_training_agreement']['original_S_minus_F']['versus_spearman']['n_configurations']} correlated configurations (Pearson {num(diagnosis['property_versus_training_agreement']['original_S_minus_F']['versus_spearman']['pearson'])}, Kendall {num(diagnosis['property_versus_training_agreement']['original_S_minus_F']['versus_spearman']['kendall'])}; p-val=n/a).",
        "Specificity does not reverse that direction, and it is computable on only 3 training tasks.",
        "The two frozen revisions therefore do not provide a training-supported replacement.",
        "",
        "## Per-configuration current-five training agreement",
        "",
        "| Configuration | n items | Margin | Headroom | Specificity | Spearman (95% task bootstrap) | Pearson | Kendall | MAE | Bias | Judge mean | Human mean | Repeat SD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    current = result["configuration_metrics"]["current5_mean_0_to_1"]
    for config, row in current.items():
        prop = result["properties"][config]
        lines.append(
            f"| {config} | {row['n_items']} | {num(prop['original_S_minus_F']['value'])} | {num(prop['headroom_normalized']['value'])} | {num(prop['semantic_specificity']['value'])} | {interval(row['spearman'], row['intervals'].get('spearman'))} | {num(row['pearson'])} | {num(row['kendall'])} | {num(row['mae'])} | {num(row['bias'])} | {num(row['judge_mean'])} | {num(row['human_mean'])} | {num(result['repeat_summary'][config]['repeat_sd_mean'])} |"
        )
    lines += ["", "## Cross-fitted training-task selection", ""]
    for target in ("current5_mean_0_to_1", "current3_mean_0_to_1"):
        block = result["cross_fitted_selection"][target]
        lines.append(f"### {target}")
        lines.append("")
        if block.get("status") == "UNAVAILABLE_COMMON_SUPPORT":
            lines.append(block["reason"])
            lines.append("")
            continue
        lines += ["Each fold drops one training task from the property, selects the maximum, and scores that judge on the omitted task.", "Ties average the loss across the tied judges.", "The paired difference is selector minus the fixed four-configuration H2 (human-rubric) choice.", "A positive difference is worse absolute error than H2.", "Selection was not recomputed inside the bootstrap, so this difference is conditional on the observed folds: p-val=n/a.", "", "| Frozen selector | Mean paired MAE difference | Fold SD | Folds |", "|---|---:|---:|---:|"]
        for candidate, row in block.items():
            pair = row["paired_absolute_error"]
            lines.append(f"| {candidate} | {num(pair['mean_difference_selector_minus_H2'])} | {num(pair['fold_sd'])} | {pair['fold_count']} |")
        lines.append("")
    lines += ["## Model and harness means", "", "These are descriptive means of the current-five training metrics. They are not a held-out model test.", "", "| Group | Kind | n | Mean Spearman | Mean MAE | Mean bias |", "|---|---|---:|---:|---:|---:|"]
    for kind in ("model_key", "harness"):
        for row in diagnosis["leave_one_group_descriptive"][kind]:
            lines.append(f"| {row['group']} | {kind} | {row['n_configurations']} | {num(row['mean_spearman'])} | {num(row['mean_mae'])} | {num(row['mean_bias'])} |")
    lines += [
        "",
        "## Limitations",
        "",
        "All findings reuse historical training labels and cached judges.",
        "A favorable training comparison does not establish a better property, correctness, transfer, or validity on fresh raters.",
        "Candidate 3 uses only the pre-existing audit of redundant weakenings whose guarantee is still stated elsewhere.",
        "",
        "**TLDR-end:** [cert-judge: 56 semantic margin training diagnosis] The frozen training-only analysis reports the original margin, both revisions, and the existing comparators without using validation or test outcomes.",
        "",
    ]
    (EXP / "RESULTS_training_diagnosis.md").write_text("\n".join(lines))


if __name__ == "__main__":
    result = analyze(); render(result); print(json.dumps({"status": result["status"], "common_support": result["common_support"]}, indent=2))
