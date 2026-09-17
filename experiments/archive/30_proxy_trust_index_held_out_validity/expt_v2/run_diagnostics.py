#!/usr/bin/env python3
"""Exploratory proxy diagnostics from frozen local data; no inference clients."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "py_src"))
from cert_judge.pti_v0 import ladder_factor
from cert_judge.ti_validation import (
    CORRELATION_FUNCTIONS, fisher_ci, icc, pairwise_rank_accuracy, top_k_overlap,
)

HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/29_proxy_validation/results"
PROBES = ROOT / "experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json"
PROPERTIES = ("P_eq", "P_bm", "P_ms", "P_eqalpha")
FLOORS = (1e-6, 1e-4, 1e-3, 1e-2)
INNER_METHODS = ("pearson", "spearman", "kendall_tau_b", "icc_a1")


def read(path):
    return json.loads(path.read_text())


def clean(value):
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True, allow_nan=False) + "\n")


def score_index(records):
    """Keep judge identity in the key and reject incomplete/duplicate cells."""
    cells = {}
    for r in records:
        key = (r["judge_id"], r["score_cell_id"])
        repeats = cells.setdefault(key, {})
        repeat = r["repeat_id"]
        score = float(r["normalized_score"])
        if type(repeat) is not int or repeat not in (0, 1, 2) or repeat in repeats:
            raise ValueError(f"invalid or duplicate repeat for {key}")
        if not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError(f"score outside [0,1] for {key}")
        repeats[repeat] = score
    if any(set(r) != {0, 1, 2} for r in cells.values()):
        raise ValueError("incomplete score cell")
    return {key: [r[i] for i in range(3)] for key, r in cells.items()}


def reconstruct_factors(judges, requests, cells, probes):
    index = {(r["judge_id"], r["artifact_id"], r["probe_type"], r["level"], r["variant"]): r
             for r in requests["requests"]}
    if len(index) != len(requests["requests"]):
        raise ValueError("duplicate conceptual score request")
    result = {p: {} for p in PROPERTIES}
    for structural in probes["artifacts"]:
        artifact = structural["artifact_id"]
        for prop in PROPERTIES:
            probe = structural[prop]
            if not probe["structurally_valid"]:
                continue
            values = []
            for judge in judges:
                def scores(kind, level, variant):
                    request = index[(judge, artifact, kind, level, variant)]
                    return cells[(judge, request["score_cell_id"])]
                if prop == "P_eq":
                    factor = float(np.median(scores("eq", 0, "self")))
                elif prop == "P_eqalpha":
                    factor = 1 - abs(float(np.median(scores("eqalpha", 0, "original")))
                                     - float(np.median(scores("eqalpha", 0, "alpha"))))
                else:
                    kind = "bm" if prop == "P_bm" else "ms"
                    rows = [scores(kind, int(level["level"]), f"L{level['level']}")
                            for level in probe["levels"]]
                    factor = ladder_factor(rows).factor
                values.append(factor)
            result[prop][artifact] = values
    for prop in PROPERTIES:
        if len(result[prop]) != probes["valid_probe_counts"][prop]:
            raise ValueError(f"incomplete structural coverage: {prop}")
    return result


def geometric(values, axis=-1):
    values = np.asarray(values, dtype=float)
    return np.where(np.any(values == 0, axis=axis), 0.0,
                    np.exp(np.log(np.maximum(values, 1e-300)).mean(axis=axis)))


def aggregate(factors, problem_weights=None):
    """Shared problem weights preserve covariance between judges/properties."""
    names = ("frozen",) + tuple(f"floor_{eps:g}" for eps in FLOORS) + ("mean_then_gm",)
    components = {name: [] for name in names}
    for prop in PROPERTIES:
        artifacts = sorted(factors[prop])
        values = np.array([factors[prop][a] for a in artifacts])  # artifact x judge
        weights = np.array([problem_weights[a.split("|")[0]] for a in artifacts]).T if problem_weights is not None else np.ones((1, len(artifacts)))
        denominator = weights.sum(axis=1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            for name, eps in zip(names[:-1], (0.0,) + FLOORS):
                logs = np.log(np.maximum(values, max(eps, 1e-300)))
                gm = np.exp((weights @ logs) / denominator)
                if eps == 0:
                    gm = np.where((weights @ (values == 0)) > 0, 0.0, gm)
                components[name].append(gm)
            components["mean_then_gm"].append((weights @ values) / denominator)
    variants = {name: geometric(np.stack(parts, axis=-1)) for name, parts in components.items()}
    variants.update({prop: components["frozen"][i] for i, prop in enumerate(PROPERTIES)})
    return variants


def correlations(x, y):
    x, y = list(x), list(y)
    values = {name: fn(x, y) for name, fn in CORRELATION_FUNCTIONS.items()}
    agreement = icc(list(zip(x, y)))
    values.update(icc_a1=agreement.icc_2_1, icc_c1=agreement.icc_3_1)
    return values


def row_pearson(x, y):
    x, y = np.asarray(x), np.asarray(y)
    xc, yc = x - x.mean(axis=-1, keepdims=True), y - y.mean(axis=-1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (xc * yc).sum(axis=-1) / np.sqrt((xc * xc).sum(axis=-1) * (yc * yc).sum(axis=-1))


def row_spearman(x, y):
    return row_pearson(rankdata(x, axis=-1), rankdata(y, axis=-1))


def interval(values):
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    return {"ci_low": float(np.quantile(finite, .025)) if len(finite) else None,
            "ci_high": float(np.quantile(finite, .975)) if len(finite) else None,
            "valid_draws": len(finite), "undefined_draws": len(values) - len(finite)}


def load_inputs():
    paths = [SOURCE / p for p in ("scores.json", "score_requests.json", "criterion_manifest.json",
                                  "properties/properties.json", "criterion/criterion.json")] + [PROBES]
    scores, requests, manifest, properties, old_criterion, probes = map(read, paths)
    if scores["request_manifest_fingerprint"] != requests["manifest_fingerprint"]:
        raise ValueError("score/request identity mismatch")
    if properties["probe_manifest_fingerprint"] != probes["manifest_fingerprint"]:
        raise ValueError("property/probe identity mismatch")
    if properties["config_fingerprint"] != requests["config_fingerprint"]:
        raise ValueError("property/request configuration mismatch")
    if old_criterion["score_sha256"] != hashlib.sha256(paths[0].read_bytes()).hexdigest():
        raise ValueError("criterion/score content mismatch")
    metadata = {r["judge_id"]: r for r in properties["judges"]}
    judges = sorted(metadata)
    cells = score_index(scores["records"])
    if set(cells) != {(r["judge_id"], r["score_cell_id"]) for r in requests["requests"]}:
        raise ValueError("score cells and requested judge/cell keys differ")
    for r in requests["requests"]:
        if (r["judge_id"], r["score_cell_id"]) not in cells:
            raise ValueError("request lacks complete score cell")
    rows = manifest["rows"]
    if len({r["artifact_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate criterion artifact")
    if any(r["artifact_id"].split("|")[0] != r["gold_file"].removesuffix(".lean") for r in rows):
        raise ValueError("criterion problem and artifact identifiers disagree")
    repeats = np.array([[cells[(j, r["score_cell_ids"][j])] for r in rows] for j in judges])
    labels = {v: np.array([r[f"{v}_score_0_5"] / 5 for r in rows]) for v in ("average", "strict", "lenient")}
    if any(not np.all(np.isfinite(y) & (y >= 0) & (y <= 1)) for y in labels.values()):
        raise ValueError("human scores outside [0,5]")
    factors = reconstruct_factors(judges, requests, cells, probes)
    variants = aggregate(factors)
    for i, j in enumerate(judges):
        for prop in PROPERTIES:
            np.testing.assert_allclose(variants[prop][0, i], metadata[j]["properties"][prop]["value"], atol=1e-12, rtol=0)
        for variant, frozen in [("frozen", metadata[j]["PTI_v0"]["value"]),
                                ("floor_0.001", metadata[j]["epsilon_1e3_sensitivity"]["PTI_v0"])]:
            np.testing.assert_allclose(variants[variant][0, i], frozen, atol=1e-12, rtol=0)
    medians = np.median(repeats, axis=2)
    for r in old_criterion["records"]:
        for view, y in labels.items():
            actual = CORRELATION_FUNCTIONS["spearman"](medians[judges.index(r["judge_id"])], y)
            np.testing.assert_allclose(actual, r["views"][view]["value"], atol=1e-12, rtol=0)
    return paths, judges, metadata, rows, repeats, labels, factors, variants


def criterion_report(judges, rows, repeats, labels):
    result = {}
    for i, judge in enumerate(judges):
        median = np.median(repeats[i], axis=1)
        sd = float(np.std(repeats[i], axis=1, ddof=1).mean())
        scaled = float((2 * np.std(repeats[i], axis=1, ddof=0)).mean())
        views = {}
        for view, y in labels.items():
            corr = correlations(median, y)
            joint = lambda noise: {m: math.sqrt(max(0., corr[m]) * max(0., 1 - noise))
                                  if corr[m] is not None else None for m in INNER_METHODS}
            views[view] = {"agreement": corr, "ti_2prime": joint(sd), "ti_scaled_population_sd": joint(scaled)}
        result[judge] = {"n_candidates": len(rows), "sample_sd": sd, "stability": 1 - sd,
                         "twice_population_sd": scaled, "views": views}
    return result


def bootstrap(rows, repeats, labels, factors, draws, seed):
    rng = np.random.default_rng(seed)
    human_problems = sorted({r["gold_file"].removesuffix(".lean") for r in rows})
    all_problems = sorted({a.split("|")[0] for f in factors.values() for a in f})
    other = sorted(set(all_problems) - set(human_problems))
    weights = {p: np.zeros(draws) for p in set(all_problems) | set(human_problems)}
    problem_to_rows = {p: [i for i, r in enumerate(rows) if r["gold_file"] == p + ".lean"] for p in human_problems}
    targets = np.empty((draws, repeats.shape[0], 2))
    stability = np.empty((draws, repeats.shape[0]))
    for b in range(draws):
        sampled = rng.choice(human_problems, len(human_problems), replace=True)
        indices = [i for p in sampled for i in problem_to_rows[p]]
        for p, count in Counter(sampled).items():
            weights[p][b] = count
        if other:
            for p, count in Counter(rng.choice(other, len(other), replace=True)).items():
                weights[p][b] = count
        rr = repeats[:, indices, :]
        y = labels["average"][indices]
        rho = row_spearman(np.median(rr, axis=2), y)
        stable = 1 - np.std(rr, axis=2, ddof=1).mean(axis=1)
        targets[b, :, 0], targets[b, :, 1] = rho, np.sqrt(np.maximum(rho, 0) * stable)
        stability[b] = stable
    proxies = aggregate(factors, weights)
    proxies["stability_only"] = stability
    return targets, proxies


def associations(judges, metadata, criteria, variants, boot_targets, boot_proxies):
    result = []
    for cohort in ("primary", "all"):
        use = [i for i, j in enumerate(judges) if cohort == "all" or metadata[j]["role"] == "primary"]
        for view in ("average", "strict", "lenient"):
            for method in INNER_METHODS:
                for target in ("agreement", "ti_2prime"):
                    y = [criteria[judges[i]]["views"][view][target][method] for i in use]
                    for variant, values in variants.items():
                        x = values[0, use]
                        record = {"cohort": cohort, "n_judges": len(use), "view": view,
                                  "inner_method": method, "target": target, "proxy": variant,
                                  "outer": correlations(x, y), "top_1_overlap": top_k_overlap(x, y, 1),
                                  "pairwise_accuracy": pairwise_rank_accuracy(x, y)}
                        if view == "average" and method == "spearman":
                            t = 0 if target == "agreement" else 1
                            rho = row_spearman(boot_proxies[variant][:, use], boot_targets[:, use, t])
                            record["outer_spearman_problem_bootstrap"] = interval(rho)
                        result.append(record)
    return result


def family_predictions(x, y, groups, mode):
    """A complete prediction procedure: constant fits retain the training mean."""
    predicted = np.empty(len(x))
    folds = []
    for held in sorted(set(groups)):
        test = np.array([g == held for g in groups])
        train = ~test
        if train.sum() < 2:
            raise ValueError("fewer than two training configurations")
        tx, ty = x[train], y[train]
        denominator = float(((tx - tx.mean()) ** 2).sum())
        raw_slope = float(((tx - tx.mean()) * (ty - ty.mean())).sum() / denominator) if denominator else None
        slope = 0.0 if mode == "training_mean" or raw_slope is None else raw_slope
        if mode == "nonnegative":
            slope = max(0.0, slope)
        intercept = float(ty.mean() - slope * tx.mean())
        predicted[test] = slope * x[test] + intercept
        folds.append({"held_family": held, "train_count": int(train.sum()), "test_count": int(test.sum()),
                      "raw_slope": raw_slope, "used_slope": slope, "intercept": intercept,
                      "constant_training_fallback": denominator == 0})
    return predicted, folds


def holdout(judges, metadata, criteria, variants):
    use = [i for i, j in enumerate(judges) if metadata[j]["role"] == "primary"]
    groups = [metadata[judges[i]]["family"] for i in use]
    rows = []
    for target in ("agreement", "ti_2prime"):
        y = np.array([criteria[judges[i]]["views"]["average"][target]["spearman"] for i in use])
        for variant in ("frozen", "floor_0.001", "mean_then_gm", "stability_only"):
            x = variants[variant][0, use]
            for mode in ("raw", "training_mean", "nonnegative", "unrestricted"):
                prediction, folds = (x, []) if mode == "raw" else family_predictions(x, y, groups, mode)
                rows.append({"target": target, "proxy": variant, "mode": mode,
                             "judges": [judges[i] for i in use], "actual": y, "predicted": prediction,
                             "mse": float(((prediction - y) ** 2).mean()), "outer": correlations(prediction, y), "folds": folds})
    return {"status": "EXPLORATORY_TWO_FAMILIES", "independent_primary_families": sorted(set(groups)),
            "three_way_split_status": "NOT_COMPUTABLE: fewer than three primary families",
            "generator_family_transfer": "NOT_COMPUTABLE: generation slots lack model-family provenance",
            "uncertainty": "No independent-pair bootstrap of fitted out-of-family predictions", "rows": rows}


def simulations(draws, seed):
    rng = np.random.default_rng(seed)
    rows = []
    designs = [(n, n, 1, rho, 0.) for n in (5, 8, 12, 20, 32, 48) for rho in (0., .3, .5, .7)]
    designs += [(f * p, f, p, .5, .7) for f in (2, 4, 8, 12) for p in (2, 4)]
    for n, families, prompts, rho, dependence in designs:
        def draw():
            family = rng.normal(size=(draws, families, 1))
            errors = rng.normal(size=(draws, families, prompts))
            return (np.sqrt(dependence) * family + np.sqrt(1 - dependence) * errors).reshape(draws, n)
        x = draw()
        y = rho * x + np.sqrt(1 - rho ** 2) * draw()
        observed = row_pearson(x, y)
        z = np.arctanh(np.clip(observed, -1 + 1e-15, 1 - 1e-15))
        half = 1.959963984540054 / np.sqrt(n - 3)
        low, high = np.tanh(z - half), np.tanh(z + half)
        rows.append({"n_configurations": n, "n_families": families, "prompts_per_family": prompts,
                     "population_pearson": rho, "intrafamily_correlation": dependence,
                     "coverage_95": float(((low <= rho) & (high >= rho)).mean()),
                     "zero_exclusion_frequency": float(((low > 0) | (high < 0)).mean()),
                     "mean_interval_width": float((high - low).mean())})
    return {"status": "SYNTHETIC_SENSITIVITY_NOT_EMPIRICAL_POWER", "datasets_per_setting": draws, "rows": rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "results")
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260911)
    args = parser.parse_args(argv)
    if args.draws < 2:
        parser.error("--draws must be at least 2")
    paths, judges, metadata, rows, repeats, labels, factors, variants = load_inputs()
    criteria = criterion_report(judges, rows, repeats, labels)
    variants["stability_only"] = np.array([[criteria[j]["stability"] for j in judges]])
    write(args.out / "criterion.json", criteria)
    write(args.out / "factors.json", factors)
    write(args.out / "proxy_variants.json", {name: dict(zip(judges, values[0])) for name, values in variants.items()})
    zero_counts = {p: {j: sum(v[i] == 0 for v in factors[p].values()) for i, j in enumerate(judges)} for p in PROPERTIES}
    leave_one_problem = {}
    problems = sorted({a.split("|")[0] for f in factors.values() for a in f})
    for omitted in problems:
        reduced = {p: {a: v for a, v in f.items() if a.split("|")[0] != omitted} for p, f in factors.items()}
        leave_one_problem[omitted] = aggregate(reduced)["frozen"][0]
    write(args.out / "zero_audit.json", {"judges": judges, "per_artifact_zero_counts": zero_counts,
          "zero_judges_by_property": {p: int((variants[p] == 0).sum()) for p in PROPERTIES},
          "aggregate_zero_judges": int((variants["frozen"] == 0).sum()),
          "leave_one_problem_out_frozen": leave_one_problem})
    print("Phase 1: reconstructed frozen outputs and computed combined criteria.", flush=True)
    targets, proxies = bootstrap(rows, repeats, labels, factors, args.draws, args.seed)
    comparisons = associations(judges, metadata, criteria, variants, targets, proxies)
    write(args.out / "associations.json", comparisons)
    primary = [i for i, j in enumerate(judges) if metadata[j]["role"] == "primary"]
    pairwise = []
    for a, b in combinations(primary, 2):
        difference = targets[:, a, 1] - targets[:, b, 1]
        pairwise.append({"judge_a": judges[a], "judge_b": judges[b], "difference_interval": interval(difference),
                         "bootstrap_ordering_fraction_a_gt_b": float(np.mean(difference > 0)),
                         "bootstrap_tie_fraction": float(np.mean(difference == 0))})
    write(args.out / "ranking_uncertainty.json", {"scope": "Shared-problem bootstrap; fixed observed calls/labels/configurations",
          "primary_judges": [judges[i] for i in primary], "pairwise": pairwise,
          "criterion_covariance": np.cov(targets[:, primary, 1], rowvar=False)})
    print("Phase 2: completed shared-problem uncertainty and proxy comparisons.", flush=True)
    write(args.out / "family_holdout.json", holdout(judges, metadata, criteria, variants))
    write(args.out / "design_simulation.json", simulations(args.draws, args.seed + 1))
    paths += [Path(__file__), HERE / "PROTOCOL.md", ROOT / "py_src/cert_judge/ti_validation.py", ROOT / "py_src/cert_judge/pti_v0.py"]
    write(args.out / "run_manifest.json", {"status": "COMPLETED_EXPLORATORY", "draws": args.draws, "seed": args.seed,
          "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
          "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
          "numpy": np.__version__, "scipy": scipy.__version__, "python": sys.version,
          "judges": [{k: metadata[j][k] for k in ("judge_id", "family", "role")} for j in judges],
          "candidate_count": len(rows), "problem_count": len({r['gold_file'] for r in rows}),
          "primary_family_count": len({metadata[j]['family'] for j in judges if metadata[j]['role'] == 'primary'}),
          "model_calls": 0, "new_human_labels": 0})
    print(f"Phase 3: family diagnostics and synthetic design study complete: {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
