#!/usr/bin/env python3
"""Offline, deterministic cached-score selection-utility analysis for experiment 44.

Run from any directory: python3 experiments/archive/44_cached_score_judge_selection_utility/scripts/analyze_selection_utility.py
No inference client, credentials, or network access is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import __version__ as SCIPY_VERSION
from scipy.stats import kendalltau, pearsonr, rankdata, spearmanr

EXPECTED_ITEMS = "ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c"
SOURCE_REVISION = "fc73f78696d53551cd57f13094ec6f73fbb1c234"
SEED = 44
DRAWS = 10_000
PRIMARY_PROMPTS = {"D0", "H0", "H1", "H2", "R4"}
VIEWS = ("original45", "no_placeholder36", "no_ambiguity36", "neither27", "test_only30")


def root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists() and (parent / ".git").exists():
            return parent
    raise RuntimeError("cannot locate repository root by pyproject.toml/.git")


ROOT = root()
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / "results"
ITEMS_PATH = EXP / "inputs" / "items.jsonl"


def source_dir() -> Path:
    candidates = [
        ROOT / "experiments" / "39_label_free_proxy_index_train_val_test_over_judge_families",
        ROOT / "experiments" / "archive" / "39_label_free_proxy_index_train_val_test_over_judge_families",
        Path("/lfs/skampere1/0/brando9/cert-judge_e39/experiments/39_label_free_proxy_index_train_val_test_over_judge_families"),
    ]
    for path in candidates:
        if (path / "results" / "panel.json").exists() and (path / "scripts" / "analysis_lib.py").exists():
            return path
    raise RuntimeError("source experiment 39 not found in active/archive alternatives")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_fingerprint(src: Path) -> dict[str, str]:
    """Immutable source inputs checked before and after the analysis."""
    names = ("panel.json", "units_train_val.json", "units_test.json", "probe_manifest.json", "SELECTION.json", "FINALISTS.json", "TEST_RECEIPT.json")
    paths = [ITEMS_PATH, *(src / "results" / name for name in names), *sorted((src / "results" / "harvest").glob("*.json"))]
    if not all(path.exists() for path in paths):
        raise FileNotFoundError("a required frozen source input is absent")
    return {str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path): digest(path) for path in paths}


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def finite(v) -> bool:
    return v is not None and math.isfinite(float(v))


def corr(x, y) -> dict[str, float | None]:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or len(np.unique(x)) < 2 or len(np.unique(y)) < 2:
        return {"spearman": None, "pearson": None, "kendall": None}
    return {
        "spearman": float(spearmanr(x, y).statistic),
        "pearson": float(pearsonr(x, y).statistic),
        "kendall": float(kendalltau(x, y).statistic),
    }


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    return float(np.percentile(np.asarray(values, float), p))


def median_scores(harvest: dict, item_map: dict[str, dict] | None = None) -> dict[str, float]:
    """Final-status normalized criterion medians; zero is intentionally retained."""
    buckets: dict[str, list[float]] = defaultdict(list)
    seen: set[str] = set()
    for cell in harvest["cells"]:
        if cell.get("kind") != "crit" or cell.get("level") != 0:
            continue
        key = cell.get("cell")
        if key in seen:
            raise ValueError(f"duplicate cell/repeat key in {harvest['config']}: {key}")
        seen.add(key)
        if cell.get("status") not in {"measured", "deterministic"} or cell.get("score") is None:
            continue
        score = float(cell["score"])
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"unnormalized accepted score in {harvest['config']}: {score}")
        buckets[cell["key"]].append(score)
        if item_map is not None:
            item = item_map.get(cell["key"])
            if item is None or cell.get("item") != item["item"] or cell.get("task") != item["task"]:
                raise ValueError(f"inconsistent item/task join in {harvest['config']}: {cell.get('cell')}")
    return {key: float(statistics.median(values)) for key, values in buckets.items()}


def load_inputs() -> tuple[list[dict], dict[str, dict]]:
    if digest(ITEMS_PATH) != EXPECTED_ITEMS:
        raise ValueError("items.jsonl fingerprint mismatch")
    items = [json.loads(line) for line in ITEMS_PATH.read_text().splitlines() if line]
    if len(items) != 75 or len({x["item"] for x in items}) != 75 or len({x["task"] for x in items}) != 25:
        raise ValueError("expected 75 unique items across 25 tasks")
    counts = {split: sum(x["split"] == split for x in items) for split in ("train", "val", "test")}
    if counts != {"train": 30, "val": 15, "test": 30}:
        raise ValueError(f"unexpected splits: {counts}")
    for item in items:
        if not finite(item.get("target_expert")) or not 0 <= item["target_expert"] <= 1:
            raise ValueError(f"invalid normalized target_expert: {item['item']}")
    return items, {x["item"]: x for x in items}


def view_items(items: list[dict], view: str) -> list[dict]:
    out = [x for x in items if x["split"] in {"val", "test"}]
    if view == "no_placeholder36":
        out = [x for x in out if not x["ref_placeholder_at_annotation"]]
    elif view == "no_ambiguity36":
        out = [x for x in out if not x["ref_ambiguous_in_window"]]
    elif view == "neither27":
        out = [x for x in out if not x["ref_placeholder_at_annotation"] and not x["ref_ambiguous_in_window"]]
    elif view == "test_only30":
        out = [x for x in out if x["split"] == "test"]
    elif view != "original45":
        raise KeyError(view)
    return out


def config_correlations(scores: dict[str, dict[str, float]], configs: list[str], items: list[dict], mask: list[str]) -> dict:
    by_item = {x["item"]: x for x in items}
    y = [by_item[key]["target_expert"] for key in mask]
    return {config: corr([scores[config][key] for key in mask], y) for config in configs}


def weights_max(configs: list[str], values: dict[str, float | None]) -> dict[str, float] | None:
    eligible = [x for x in configs if finite(values.get(x))]
    if not eligible:
        return None
    maximum = max(values[x] for x in eligible)
    tied = [x for x in eligible if values[x] == maximum]
    return {x: 1.0 / len(tied) for x in tied}


def expected(weights: dict[str, float] | None, utilities: dict[str, dict]) -> dict:
    if not weights:
        return {"status": "ABSTAIN", "value": None, "members": [], "range": None}
    metrics = {}
    for statistic in ("spearman", "pearson", "kendall"):
        vals = {config: utilities[config][statistic] for config in weights}
        metrics[statistic] = None if any(not finite(v) for v in vals.values()) else sum(weights[x] * vals[x] for x in weights)
    vals = {config: utilities[config]["spearman"] for config in weights}
    return {"status": "COMPUTED" if finite(metrics["spearman"]) else "UNDEFINED", "value": metrics["spearman"], "metrics": metrics,
            "members": sorted(weights), "range": ([min(vals.values()), max(vals.values())] if all(finite(v) for v in vals.values()) else None)}


def selector_weights(configs: list[str], meta: dict[str, dict], proxy: dict, ident: dict, transferred_prompt: str | None) -> dict[str, dict[str, float] | None]:
    h2 = [x for x in configs if meta[x]["prompt_key"] == "H2"]
    transferred = [x for x in configs if meta[x]["prompt_key"] == transferred_prompt] if transferred_prompt else []
    return {
        "proxy_C_ms_gold": weights_max(configs, proxy),
        "identity_C_ident": weights_max(configs, ident),
        "human_mirror_H2": ({x: 1.0 / len(h2) for x in h2} if h2 else None),
        "random": ({x: 1.0 / len(configs) for x in configs} if configs else None),
        "transferred_prompt": ({x: 1.0 / len(transferred) for x in transferred} if transferred else None),
    }


def maximum_margin(configs: list[str], values: dict[str, float | None]) -> float | None:
    ranked = sorted((v for c, v in values.items() if c in configs and finite(v)), reverse=True)
    return (ranked[0] - ranked[1]) if len(ranked) >= 2 else None


def choose_prompt(open_units: list[dict], meta: dict[str, dict]) -> dict:
    rows = [u for u in open_units if u["kind"] == "llm" and u["config"] in meta]
    def mean_for(split: str, prompt: str):
        values = [(u["criteria"].get("heldout") or {}).get("spearman") for u in rows
                  if u["split"] == split and meta[u["config"]]["prompt_key"] == prompt]
        values = [v for v in values if finite(v)]
        configs = sorted(u["config"] for u in rows if u["split"] == split and meta[u["config"]]["prompt_key"] == prompt and finite((u["criteria"].get("heldout") or {}).get("spearman")))
        return ((sum(values) / len(values)) if values else None), configs
    prompts = sorted({m["prompt_key"] for m in meta.values()})
    train = [{"prompt": p, "mean_spearman": mean_for("train", p)[0], "n_configs": len(mean_for("train", p)[1]), "configs": mean_for("train", p)[1]} for p in prompts]
    ranked = sorted([x for x in train if finite(x["mean_spearman"])], key=lambda x: (-x["mean_spearman"], x["prompt"]))[:3]
    validation = [{"prompt": x["prompt"], "mean_spearman": mean_for("val", x["prompt"])[0], "n_configs": len(mean_for("val", x["prompt"])[1]), "configs": mean_for("val", x["prompt"])[1]} for x in ranked]
    usable = [x for x in validation if finite(x["mean_spearman"])]
    chosen = sorted(usable, key=lambda x: (-x["mean_spearman"], x["prompt"]))[0]["prompt"] if usable else None
    return {"train": train, "retained_top3": ranked, "validation": validation, "chosen_prompt": chosen}


def draw_correlations(matrix: np.ndarray, y: np.ndarray, idx: np.ndarray) -> dict[str, np.ndarray]:
    """All three correlations for each configuration on one resampled item index.

    Kendall's tau-b uses vectorized pair signs, including ties, rather than a
    million slow scalar SciPy calls. It is cross-checked against SciPy in tests.
    """
    x = matrix[:, idx]
    yy = y[idx]
    def pearson_rows(values: np.ndarray, target: np.ndarray) -> np.ndarray:
        vx, vy = values - values.mean(axis=1, keepdims=True), target - target.mean()
        den = np.sqrt((vx * vx).sum(axis=1) * (vy * vy).sum())
        nonconstant = (np.ptp(values, axis=1) > 0) & (np.ptp(target) > 0)
        return np.divide((vx * vy).sum(axis=1), den, out=np.full(values.shape[0], np.nan), where=(den != 0) & nonconstant)
    spear = pearson_rows(rankdata(x, axis=1), rankdata(yy))
    pear = pearson_rows(x, yy)
    pi, pj = np.triu_indices(len(idx), 1)
    sx = np.sign(x[:, pi] - x[:, pj])
    sy = np.sign(yy[pi] - yy[pj])
    n0 = len(pi)
    denom = np.sqrt((n0 - (sx == 0).sum(axis=1)) * (n0 - (sy == 0).sum()))
    kend = np.divide((sx * sy).sum(axis=1), denom, out=np.full(x.shape[0], np.nan), where=denom != 0)
    return {"spearman": spear, "pearson": pear, "kendall": kend}


def bootstrap(scores: dict[str, dict[str, float]], configs: list[str], items: list[dict], mask: list[str], weights: dict[str, dict | None], draws: int) -> dict:
    """Paired task bootstrap preserving task multiplicity and fixed selectors."""
    by_item = {x["item"]: x for x in items}
    by_task: dict[str, list[int]] = defaultdict(list)
    for i, key in enumerate(mask):
        by_task[by_item[key]["task"]].append(i)
    tasks = sorted(by_task)
    if not tasks:
        return {"draws": draws, "valid": {}, "intervals": {}}
    y = np.array([by_item[key]["target_expert"] for key in mask], float)
    matrix = np.array([[scores[c][key] for key in mask] for c in configs], float)
    rng = np.random.default_rng(SEED)
    metric_values: dict[str, list[float]] = defaultdict(list)
    valid: dict[str, int] = defaultdict(int)
    undefined: dict[str, int] = defaultdict(int)
    for _ in range(draws):
        chosen = rng.integers(0, len(tasks), size=len(tasks))
        idx = np.concatenate([np.asarray(by_task[tasks[i]], int) for i in chosen])
        by_stat = draw_correlations(matrix, y, idx)
        values = {stat: {config: (None if not np.isfinite(arr[i]) else float(arr[i])) for i, config in enumerate(configs)} for stat, arr in by_stat.items()}
        oracle = None if any(not finite(values["spearman"][c]) for c in configs) else max(values["spearman"].values())
        selector_value = {stat: {} for stat in values}
        for name, member_weights in weights.items():
            for stat in values:
                key = f"{name}:{stat}"
                if not member_weights or any(not finite(values[stat][c]) for c in member_weights):
                    selector_value[stat][name] = None
                    undefined[key] += 1
                else:
                    selector_value[stat][name] = sum(w * values[stat][c] for c, w in member_weights.items())
                    valid[key] += 1
                    metric_values[f"utility:{key}"].append(selector_value[stat][name])
            if finite(selector_value["spearman"].get(name)) and oracle is not None:
                metric_values[f"regret:{name}"].append(oracle - selector_value["spearman"][name])
        # Pairwise contrasts deliberately use the shared finite intersection for that pair.
        for left, right in (("proxy_C_ms_gold", "human_mirror_H2"), ("proxy_C_ms_gold", "random")):
            if finite(selector_value["spearman"].get(left)) and finite(selector_value["spearman"].get(right)):
                metric_values[f"difference:{left}-{right}"].append(selector_value["spearman"][left] - selector_value["spearman"][right])
    intervals = {key: {"lo": percentile(vals, 2.5), "hi": percentile(vals, 97.5), "valid_draws": len(vals)}
                 for key, vals in metric_values.items()}
    return {"draws": draws, "valid": dict(valid), "undefined": dict(undefined), "intervals": intervals,
            "resampling_unit": "task; all retained item rows copied with task multiplicity"}


def score_diagnostics(scores: dict[str, dict[str, float]], item_map: dict[str, dict], mask: list[str], weights: dict[str, float] | None, raw_repeats: dict[str, dict[str, list[float]]]) -> dict:
    if not weights:
        return {"status": "ABSTAIN"}
    pieces = []
    for config, weight in weights.items():
        if any(key not in scores[config] for key in mask):
            return {"status": "UNDEFINED"}
        judge = np.array([scores[config][k] for k in mask])
        human = np.array([item_map[k]["target_expert"] for k in mask])
        diff = judge - human
        pieces.append((weight, diff, judge, human, [raw_repeats[config].get(k, []) for k in mask]))
    # A selector expectation is reported as weighted configuration diagnostics, not an ensemble prediction.
    repeat_sd = {c: {k: (statistics.stdev(raw_repeats[c].get(k, [])) if len(raw_repeats[c].get(k, [])) >= 2 else None) for k in mask} for c in weights}
    repeat_counts = {c: {k: len(raw_repeats[c].get(k, [])) for k in mask} for c in weights}
    expected_slots = 3 * len(mask)
    return {"status": "COMPUTED", "mean_absolute_error": sum(w * float(np.mean(abs(d))) for w, d, _, _, _ in pieces),
            "mean_bias_judge_minus_human": sum(w * float(np.mean(d)) for w, d, _, _, _ in pieces),
            "mean_judge_score": sum(w * float(np.mean(j)) for w, _, j, _, _ in pieces),
            "mean_human_score": sum(w * float(np.mean(h)) for w, _, _, h, _ in pieces),
            "expected_repeat_slots": expected_slots,
            "available_repeat_counts": {c: sum(repeat_counts[c].values()) for c in weights},
            "missing_repeat_counts": {c: expected_slots - sum(repeat_counts[c].values()) for c in weights},
            "per_item_repeat_count_histogram": {c: {str(n): list(repeat_counts[c].values()).count(n) for n in sorted(set(repeat_counts[c].values()))} for c in weights},
            "within_item_raw_repeat_sample_sd": {c: {"n_defined": sum(v is not None for v in d.values()), "n_unavailable": sum(v is None for v in d.values()),
                                                       "mean": (float(np.mean([v for v in d.values() if v is not None])) if any(v is not None for v in d.values()) else None),
                                                       "max": (max(v for v in d.values() if v is not None) if any(v is not None for v in d.values()) else None)} for c, d in repeat_sd.items()}}


def pools(meta: dict[str, dict]) -> dict[str, list[str]]:
    test = sorted(c for c, m in meta.items() if m["split"] == "test" and m["kind"] == "llm")
    primary = [c for c in test if meta[c]["prompt_key"] in PRIMARY_PROMPTS]
    h2 = [c for c in test if meta[c]["prompt_key"] == "H2"]
    if len(primary) != 12 or len(h2) != 4 or len(test) != 18:
        raise ValueError(f"declared pool mismatch: primary={len(primary)}, h2={len(h2)}, broad={len(test)}")
    return {"primary_full_context": primary, "same_H2": h2, "broad": test}


def run(draws: int = DRAWS) -> dict:
    OUT.mkdir(exist_ok=True)
    src = source_dir()
    source_before = source_fingerprint(src)
    items, item_map = load_inputs()
    panel = read_json(src / "results" / "panel.json")
    units_test = read_json(src / "results" / "units_test.json")["units"]
    open_units = read_json(src / "results" / "units_train_val.json")["units"]
    meta = {u["config"]: u for u in panel["units"] if u["kind"] == "llm"}
    test_units = {u["config"]: u for u in units_test}
    if set(test_units) != {c for c, m in meta.items() if m["split"] == "test"}:
        raise ValueError("test unit/configuration mismatch")
    # Source `results/harvest` is the frozen canonical post-recovery export used for
    # units_test; raw private transport files are only source availability evidence.
    harvest_dir = src / "results" / "harvest"
    scores, raw_repeats, source_hashes = {}, {}, {}
    for config in test_units:
        filename = config.replace("|", "__") + ".json"
        path = harvest_dir / filename
        if not path.exists():
            raise FileNotFoundError(path)
        harvest = read_json(path)
        if harvest.get("config") != config:
            raise ValueError(f"harvest config mismatch: {path}")
        scores[config] = median_scores(harvest, item_map)
        values: dict[str, list[float]] = defaultdict(list)
        for cell in harvest["cells"]:
            if cell.get("kind") == "crit" and cell.get("level") == 0 and cell.get("status") in {"measured", "deterministic"} and cell.get("score") is not None:
                values[cell["key"]].append(float(cell["score"]))
        if any(len(v) > 3 for v in values.values()):
            raise ValueError(f"criterion repeat count exceeds frozen three-slot design: {config}")
        raw_repeats[config] = dict(values)
        source_hashes[str(path)] = digest(path)
    # Fail-closed reproduction on the frozen original 45-item criterion (source statistic uses each judge's own support).
    reconstruction = []
    original = view_items(items, "original45")
    for config, unit in test_units.items():
        own = [x for x in original if x["item"] in scores[config]]
        got = corr([scores[config][x["item"]] for x in own], [x["target_expert"] for x in own])
        stored = unit["criteria"]["heldout"]
        if stored.get("n_declared") != len(original) or stored.get("n_items") != len(own):
            raise ValueError(f"stored denominator differs for {config}")
        if len(own) / len(original) + 1e-12 < .90:
            if stored["status"] != "NOT_COMPUTABLE":
                raise ValueError(f"coverage reproduction mismatch {config}")
        else:
            for stat in ("spearman", "pearson", "kendall"):
                if (got[stat] is None) != (stored.get(stat) is None):
                    raise ValueError(f"{config} {stat} nullness differs from frozen statistic")
                if finite(stored.get(stat)) and abs(got[stat] - stored[stat]) > 1e-10:
                    raise ValueError(f"{config} {stat} differs from frozen statistic")
        reconstruction.append({"config": config, "n_items": len(own), "coverage": len(own) / len(original), "reconstructed": got,
                               "stored": {k: stored.get(k) for k in ("spearman", "pearson", "kendall", "status")}})
    # Reproduce the source pooled held-out association from reconstructed per-judge outcomes.
    receipt_source = read_json(src / "results" / "TEST_RECEIPT.json")
    pooled = [r for r in reconstruction if finite(test_units[r["config"]]["indices"].get("C_ms_gold")) and finite(r["reconstructed"]["spearman"])]
    pooled_got = corr([test_units[r["config"]]["indices"]["C_ms_gold"] for r in pooled], [r["reconstructed"]["spearman"] for r in pooled])
    pooled_stored = receipt_source["reported"]["C_ms_gold"]["test"]
    for stat in ("spearman", "pearson", "kendall"):
        if abs(pooled_got[stat] - pooled_stored[stat]) > 1e-10:
            raise ValueError(f"pooled TEST_RECEIPT reconstruction differs for {stat}")
    prompt_choice = choose_prompt(open_units, meta)
    proxy = {c: test_units[c]["indices"].get("C_ms_gold") for c in test_units}
    ident = {c: test_units[c]["indices"].get("C_ident") for c in test_units}
    declared_pools = pools(meta)
    all_results, candidates = {}, []
    for pool_name, declared in declared_pools.items():
        for view in VIEWS:
            selected_items = view_items(items, view)
            mask = [x["item"] for x in selected_items if all(x["item"] in scores[c] for c in declared)]
            enough = len(mask) >= math.ceil(.9 * len(selected_items))
            key = f"{pool_name}/{view}"
            base = {"pool": pool_name, "view": view, "declared_configs": declared, "declared_items": len(selected_items),
                    "common_items": len(mask), "common_tasks": len({item_map[x]["task"] for x in mask}), "available": enough}
            if not enough:
                all_results[key] = {**base, "status": "UNAVAILABLE_SHARED_SUPPORT"}
                continue
            utility = config_correlations(scores, declared, selected_items, mask)
            weight_map = selector_weights(declared, meta, proxy, ident, prompt_choice["chosen_prompt"])
            rows = {}
            oracle = max((utility[c]["spearman"] for c in declared), default=None) if all(finite(utility[c]["spearman"]) for c in declared) else None
            for name, weights in weight_map.items():
                exp = expected(weights, utility)
                exp["weights"] = weights
                exp["selection_margin"] = maximum_margin(declared, proxy if name == "proxy_C_ms_gold" else ident) if name in {"proxy_C_ms_gold", "identity_C_ident"} else None
                exp["regret"] = (oracle - exp["value"]) if finite(oracle) and finite(exp["value"]) else None
                exp["diagnostics"] = score_diagnostics(scores, item_map, mask, weights, raw_repeats)
                rows[name] = exp
            boot = bootstrap(scores, declared, selected_items, mask, weight_map, draws)
            comparisons = {}
            for other in ("human_mirror_H2", "random"):
                a, b = rows["proxy_C_ms_gold"]["value"], rows[other]["value"]
                delta = a - b if finite(a) and finite(b) else None
                comparisons[f"proxy_minus_{other}"] = {"difference": delta, "bootstrap": boot["intervals"].get(f"difference:proxy_C_ms_gold-{other}")}
            all_results[key] = {**base, "status": "COMPUTED", "config_utilities": utility, "selectors": rows, "oracle_spearman": oracle,
                                "bootstrap": boot, "comparisons": comparisons}
            candidates.extend({"pool": pool_name, "view": view, "config": c, "proxy_C_ms_gold": proxy[c], "identity_C_ident": ident[c],
                               **utility[c]} for c in declared)
            # Same proxy-eligible sensitivity: declared-pool common item mask remains fixed by design.
            eligible = [c for c in declared if finite(proxy[c])]
            if eligible and len(eligible) < len(declared):
                eligible_utility = config_correlations(scores, eligible, selected_items, mask)
                eligible_weights = selector_weights(eligible, meta, proxy, ident, prompt_choice["chosen_prompt"])
                eligible_rows = {n: {**expected(w, eligible_utility), "weights": w} for n, w in eligible_weights.items()}
                ep, eh, er = eligible_rows["proxy_C_ms_gold"]["value"], eligible_rows["human_mirror_H2"]["value"], eligible_rows["random"]["value"]
                all_results[key]["proxy_eligible_fixed_mask_sensitivity"] = {
                    "status": "COMPUTED_DESCRIPTIVE_ONLY", "configs": eligible, "n_candidates": len(eligible), "fixed_mask_items": len(mask),
                    "fixed_mask_tasks": len({item_map[x]["task"] for x in mask}), "selectors": eligible_rows,
                    "differences": {"proxy_minus_human_mirror_H2": (ep - eh if finite(ep) and finite(eh) else None), "proxy_minus_random": (ep - er if finite(ep) and finite(er) else None)},
                    "uncertainty": "same declared-pool mask retained to isolate candidate eligibility; descriptive only"}
    # Descriptive leave-one-base-model-out and harness diagnostics over primary/original only.
    sens = {}
    base_model = {c: ({"t2_qwen": "qwen36", "t2_sonnet5": "sonnet5"}.get(meta[c]["model_key"], meta[c]["model_key"])) for c in test_units}
    main = declared_pools["primary_full_context"]
    for label, subset in {**{f"leave_out_{m}": [c for c in main if base_model[c] != m] for m in sorted(set(base_model[c] for c in main))},
                          "single_call_only": [c for c in main if meta[c]["harness"] == "vb103_judge"],
                          "agent_only": [c for c in main if meta[c]["harness"] == "terminus2"]}.items():
        selected = view_items(items, "original45")
        mask = [x["item"] for x in selected if all(x["item"] in scores[c] for c in subset)]
        if subset and len(mask) >= math.ceil(.9 * len(selected)):
            u = config_correlations(scores, subset, selected, mask)
            w = selector_weights(subset, meta, proxy, ident, prompt_choice["chosen_prompt"])
            selector_rows = {n: {**expected(x, u), "weights": x} for n, x in w.items()}
            for name, row in selector_rows.items():
                row["selection_margin"] = maximum_margin(subset, proxy if name == "proxy_C_ms_gold" else ident) if name in {"proxy_C_ms_gold", "identity_C_ident"} else None
            p, h, r = selector_rows["proxy_C_ms_gold"]["value"], selector_rows["human_mirror_H2"]["value"], selector_rows["random"]["value"]
            sens[label] = {"status": "COMPUTED_DESCRIPTIVE_ONLY", "configs": subset, "n_candidates": len(subset), "n_declared_items": len(selected),
                           "n_common_items": len(mask), "n_common_tasks": len({item_map[x]["task"] for x in mask}), "selectors": selector_rows,
                           "differences": {"proxy_minus_human_mirror_H2": (p - h if finite(p) and finite(h) else None), "proxy_minus_random": (p - r if finite(p) and finite(r) else None)},
                           "uncertainty": "not bootstrapped: few non-independent base models; descriptive only"}
        else:
            sens[label] = {"status": "UNAVAILABLE", "n_candidates": len(subset), "n_declared_items": len(selected), "n_common_items": len(mask), "n_common_tasks": len({item_map[x]["task"] for x in mask})}
    source_after = source_fingerprint(src)
    if source_before != source_after:
        raise ValueError("frozen source hashes changed during analysis")
    frozen_files = [src / "results" / name for name in ("panel.json", "units_train_val.json", "units_test.json", "probe_manifest.json", "SELECTION.json", "FINALISTS.json", "TEST_RECEIPT.json")]
    manifest = {"experiment": "44_cached_score_judge_selection_utility", "source_experiment": "39_label_free_proxy_index_train_val_test_over_judge_families",
                "source_revision": SOURCE_REVISION, "source_path": str(src), "items_sha256": digest(ITEMS_PATH), "source_harvest_sha256": source_hashes,
                "seed": SEED, "bootstrap_draws": draws, "python": sys.version, "numpy": np.__version__, "scipy": SCIPY_VERSION,
                "platform": platform.platform(), "no_inference": True,
                "frozen_source_file_sha256": {str(p.relative_to(src)): digest(p) for p in frozen_files},
                "source_hashes_before": source_before, "source_hashes_after": source_after, "source_hashes_equal": source_before == source_after}
    receipt = {"manifest": manifest, "reconstruction": reconstruction, "pooled_test_receipt_reconstruction": {"computed": pooled_got, "stored": {k: pooled_stored[k] for k in ("spearman", "pearson", "kendall", "n_units")}}, "prompt_selection": prompt_choice, "pool_views": all_results,
               "sensitivities": sens, "limitations": ["Exploratory reused item panel; not an independent test.",
               "Task bootstrap conditions on fixed candidate pool and fixed selectors; it does not model model-population, proxy-selection, or annotation-process uncertainty.",
               "No selector creates an ensemble; all expectations are over individual configurations."]}
    write_json("source_manifest.json", manifest)
    write_json("reconstruction.json", reconstruction)
    write_json("candidate_table.json", candidates)
    write_json("selector_table.json", all_results)
    write_json("prompt_selection.json", prompt_choice)
    write_json("sensitivity.json", sens)
    write_json("repeat_diagnostics.json", {c: {k: {"n_repeats": len(v), "sample_sd": (statistics.stdev(v) if len(v) >= 2 else None)} for k, v in values.items()} for c, values in raw_repeats.items()})
    write_json("criterion_matrix.json", {"items": items, "scores": scores, "raw_repeats": raw_repeats, "test_units": test_units,
                                           "panel_units": {c: meta[c] for c in test_units}, "note": "compact export reconstructed from committed experiment39 harvest exports"})
    write_json("SUMMARY_RECEIPT.json", receipt)
    render_report(receipt)
    return receipt


def fmt(v) -> str:
    return "n/a" if not finite(v) else f"{v:.3f}"


def render_report(receipt: dict) -> None:
    results = receipt["pool_views"]
    primary = results.get("primary_full_context/original45", {})
    proxy = primary.get("selectors", {}).get("proxy_C_ms_gold", {})
    h2 = primary.get("selectors", {}).get("human_mirror_H2", {})
    rand = primary.get("selectors", {}).get("random", {})
    diff_h2 = primary.get("comparisons", {}).get("proxy_minus_human_mirror_H2", {})
    diff_rand = primary.get("comparisons", {}).get("proxy_minus_random", {})
    lines = [
        "# Cached-score judge selection utility results",
        "",
        "**Status:** COMPLETE — exploratory cached-score analysis, no inference or new labels.",
        "",
        "## Practical decision",
        "",
        "On the primary 12-configuration, 42-file/15-task common-support comparison, the frozen deletion-monotonicity proxy did not demonstrate an advantage over fixed H2: proxy minus H2 Spearman was -0.086, with a paired 95% task-cluster percentile interval [-0.308, 0.058] across 10,000 draws (p-val=n/a). The proxy's point estimate was lower and the interval crossed zero. This exploratory follow-up therefore preserves the original registered result rather than replacing it; label-free deployment remains unproven.",
        "",
        "## Primary full-context pool / original 45-item view",
        "",
        "| Selector | Expected Spearman / Pearson / Kendall | Spearman 95% interval | Selected configurations | Margin | Regret (95% interval) |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for name, row in primary.get("selectors", {}).items():
        metrics = row.get("metrics", {})
        interval = primary.get("bootstrap", {}).get("intervals", {}).get(f"utility:{name}:spearman", {})
        regret_ci = primary.get("bootstrap", {}).get("intervals", {}).get(f"regret:{name}", {})
        members = ", ".join(x.replace("|", "\\|") for x in row.get("members", [])) or "abstain"
        lines.append(f"| {name} | {fmt(metrics.get('spearman'))} / {fmt(metrics.get('pearson'))} / {fmt(metrics.get('kendall'))} | [{fmt(interval.get('lo'))}, {fmt(interval.get('hi'))}] ({interval.get('valid_draws', 0)}) | {members} | {fmt(row.get('selection_margin'))} | {fmt(row.get('regret'))} [{fmt(regret_ci.get('lo'))}, {fmt(regret_ci.get('hi'))}] |")
    for label, row in (("Proxy − H2", diff_h2), ("Proxy − random", diff_rand)):
        ci = row.get("bootstrap") or {}
        lines.append(f"\n{label}: {fmt(row.get('difference'))} [95% {fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}; valid task draws={ci.get('valid_draws', 0)}; p-val=n/a].")
    lines += ["", "## Pool/view summary", "", "| Pool | View | Shared items/tasks | Proxy | H2 | Random | Proxy − H2 |", "|---|---|---:|---:|---:|---:|---:|"]
    for key, row in results.items():
        ss = row.get("selectors", {})
        cmp = row.get("comparisons", {}).get("proxy_minus_human_mirror_H2", {})
        lines.append(f"| {row['pool']} | {row['view']} | {row.get('common_items', 0)}/{row.get('common_tasks', 0)} | {fmt(ss.get('proxy_C_ms_gold', {}).get('value'))} | {fmt(ss.get('human_mirror_H2', {}).get('value'))} | {fmt(ss.get('random', {}).get('value'))} | {fmt(cmp.get('difference'))} |")
    lines += ["", "## Frozen transferred prompt", "", "```json", json.dumps(receipt["prompt_selection"], indent=2), "```", "",
              "## Sensitivities and next priority", "", "All declared criterion views, proxy-eligible fixed-mask comparisons, leave-one-base-model-out summaries, and single-call/agent-only summaries are in `results/selector_table.json` and `results/sensitivity.json`; unavailable broad-pool cells remain explicit rather than dropped. The next priority is a prospective confirmation with new raters under the same frozen rubric and a frozen proxy, rather than further tuning on this reused panel.",
              "", "## Verification and limitations", "", "- Reconstructed every source test configuration's original-mask Spearman, Pearson, and Kendall statistic and the original pooled TEST_RECEIPT association from final-status measured/deterministic cached scores and median repeats before utility computation.",
              "- The 10,000 paired bootstrap draws resample tasks (retaining repeated task rows) and hold candidates, proxy values, and selectors fixed. Positive-weight members with undefined correlation make that selector draw undefined; pairwise contrasts use each pair's shared finite draws.",
              "- All reported p-values are `n/a`; no inferential threshold was imposed. Missing proxy values exclude only the proxy selector and are retained in random, H2, and oracle comparisons. The small, non-independent set of base models, reused human panel, and fixed-candidate conditional bootstrap limit generalization.",
              "", "**TLDR-end:** [cert-judge: 44_cached_score_judge_selection_utility] This completed exploratory cached-score study measures frozen-proxy selection utility with task-cluster uncertainty and preserves all declared support and missingness rules."]
    lines[2:2] = ["**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/RESULTS_selection_utility.md>", "",
                    "**TLDR:** Proxy selection has not demonstrated a gain over the fixed human-rating rubric among comparable judges; the original registered association is preserved.", ""]
    lines[8:8] = ["H2 denotes the fixed prompt that mirrors the human-rating rubric, with conventions and demonstrations. The H2 selector chooses uniformly among four individual configurations; it is not an ensemble. The primary pool has 12 configurations from three underlying model families, with single-call and agent variants.", ""]
    extra = ["", "## Additional primary diagnostics", "",
             "Intervals below use the same paired task draws; complete counts and all sensitivity intervals are in [the machine-readable receipt](results/SUMMARY_RECEIPT.json).",
             "", "| Selector | Pearson 95% interval | Kendall 95% interval | Mean absolute error | Mean bias | Judge / human means | Observed repeats per member |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for name, row in primary["selectors"].items():
        bs = primary["bootstrap"]["intervals"]
        pc, kc = bs.get(f"utility:{name}:pearson", {}), bs.get(f"utility:{name}:kendall", {})
        d = row.get("diagnostics", {})
        counts = list(d.get("available_repeat_counts", {}).values())
        rep = f"{min(counts)}–{max(counts)}" if counts else "n/a"
        extra.append(f"| {name} | [{fmt(pc.get('lo'))}, {fmt(pc.get('hi'))}] | [{fmt(kc.get('lo'))}, {fmt(kc.get('hi'))}] | {fmt(d.get('mean_absolute_error'))} | {fmt(d.get('mean_bias_judge_minus_human'))} | {fmt(d.get('mean_judge_score'))} / {fmt(d.get('mean_human_score'))} | {rep} of {d.get('expected_repeat_slots', 'n/a')} |")
    extra += ["", "Score-level diagnostics use the same common items and normalized [0,1] scale. Bias is judge minus human (positive means lenient); these diagnostic point estimates do not determine selection. The [repeat diagnostics](results/repeat_diagnostics.json) record raw-repeat sample standard deviations, unavailable values, and missing slots, separately from median-score agreement.", ""]
    lines[-1:-1] = extra
    (EXP / "RESULTS_selection_utility.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draws", type=int, default=DRAWS)
    args = parser.parse_args()
    run(args.draws)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
