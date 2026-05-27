#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = REPO_ROOT / "experiments" / "04_veribench_validation"
DEFAULT_SUMMARY = EXP_DIR / "results_exp16_final_robust_r9_median" / "summary.json"
DEFAULT_DETAIL = EXP_DIR / "results_exp16_final_robust_r9_median" / "detail_rows.csv"
DEFAULT_SPLIT_DIR = EXP_DIR / "results_exp23_pass_split_for_brando" / "splits"
DEFAULT_OUT_DIR = EXP_DIR / "results_exp23_calibrated_val_test"
DEFAULT_HUMAN_LABEL_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_TRUST_VECTOR = EXP_DIR / "results_exp28_varaware_codex_avg" / "judge_trust_vector.csv"
DEFAULT_HELDOUT_OUT_DIR = EXP_DIR / "results_exp23_heldout_human_labels"

COMP_ORDER = ["ident", "mono", "weak", "stab", "anti", "subtle"]
HELDOUT_AGGREGATIONS = ["raw_mean", "raw_median", "rater_zmean"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Exp23: calibrate cert-index weights on a validation split, or run the "
            "frozen held-out human-label test from experiments/human_labels."
        )
    )
    p.add_argument(
        "--mode",
        choices=["legacy-split", "heldout-human-labels"],
        default="legacy-split",
        help="legacy-split preserves the original val/test split workflow; heldout-human-labels uses the fresh participant pool.",
    )
    p.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--detail-csv", type=Path, default=DEFAULT_DETAIL)
    p.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], default="avg")
    p.add_argument("--search-iters", type=int, default=200000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eps", type=float, default=1e-6)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)

    p.add_argument("--human-label-dir", type=Path, default=DEFAULT_HUMAN_LABEL_DIR)
    p.add_argument(
        "--human-label-glob",
        default="participant*.tsv",
        help="Top-level TSV glob for the held-out independent pool. Defaults to participant*.tsv and excludes old_prompt/.",
    )
    p.add_argument("--trust-vector-csv", type=Path, default=DEFAULT_TRUST_VECTOR)
    p.add_argument("--trust-column", default="TI_variance_aware")
    p.add_argument("--heldout-out-dir", type=Path, default=DEFAULT_HELDOUT_OUT_DIR)
    p.add_argument(
        "--candidate-alias-sensitivity",
        action="store_true",
        help="Also report a non-primary sensitivity that matches missing gold::candidate rows by unique candidate filename.",
    )
    return p.parse_args()


def _finite_pairs(x: Sequence[float], y: Sequence[float]) -> Tuple[List[float], List[float]]:
    out_x: List[float] = []
    out_y: List[float] = []
    for a, b in zip(x, y):
        if math.isfinite(a) and math.isfinite(b):
            out_x.append(float(a))
            out_y.append(float(b))
    return out_x, out_y


def rankdata_average(values: Sequence[float]) -> List[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        i = j
    return ranks


def pearson_corr(x: Sequence[float], y: Sequence[float]) -> float:
    xs, ys = _finite_pairs(x, y)
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    dx = [v - mx for v in xs]
    dy = [v - my for v in ys]
    sx = math.sqrt(sum(v * v for v in dx))
    sy = math.sqrt(sum(v * v for v in dy))
    if sx <= 0.0 or sy <= 0.0:
        return float("nan")
    return sum(a * b for a, b in zip(dx, dy)) / (sx * sy)


def spearman_corr(x: Sequence[float], y: Sequence[float]) -> float:
    xs, ys = _finite_pairs(x, y)
    if len(xs) < 2:
        return float("nan")
    return pearson_corr(rankdata_average(xs), rankdata_average(ys))


def exact_permutation_p_spearman(x: Sequence[float], y: Sequence[float]) -> float | None:
    xs, ys = _finite_pairs(x, y)
    n = len(xs)
    if n < 3 or n > 9:
        return None
    observed = spearman_corr(xs, ys)
    if not math.isfinite(observed):
        return None
    total = 0
    extreme = 0
    for perm in itertools.permutations(ys):
        total += 1
        rho = spearman_corr(xs, perm)
        if math.isfinite(rho) and abs(rho) >= abs(observed) - 1e-12:
            extreme += 1
    return extreme / total


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def load_human_scores(path: Path) -> Dict[str, float]:
    out: Dict[str, float] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            k = f"{row['gold_file']}::{row['candidate_file']}"
            out[k] = float(row["human_score_0_5"])
    return out


def load_judge_scores(detail_csv: Path) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    with detail_csv.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("row_type") != "human_eval_union":
                continue
            out.setdefault(row["judge_id"], {})[row["item_key"]] = float(row["score_mean"])
    return out


def components_from_summary(summary_json: Path) -> Tuple[List[str], List[List[float]]]:
    obj = json.loads(summary_json.read_text(encoding="utf-8"))
    rows = obj["judge_rows"]
    judge_ids = [r["judge_id"] for r in rows]

    def clip(v: float) -> float:
        return min(1.0, max(0.0, float(v)))

    ident = [clip(r["identity_mean"]) for r in rows]
    mono = [clip((-float(r["bug_spearman_r"]) + 1.0) / 2.0) for r in rows]
    weak = [clip(float(r["bug_weak_mono_pct"]) / 100.0) for r in rows]
    stab = [clip(1.0 - float(r["flip_rate"])) for r in rows]
    anti = [clip(float(r.get("anti_string_score", 0.0))) for r in rows]
    subtle = [clip(float(r.get("subtle_bug_sensitivity", 0.0))) for r in rows]
    return judge_ids, [ident, mono, weak, stab, anti, subtle]


def human_corr_per_judge(
    judge_ids: List[str],
    judge_scores: Mapping[str, Mapping[str, float]],
    human_scores: Mapping[str, float],
) -> List[float]:
    ys: List[float] = []
    keys = set(human_scores.keys())
    for j in judge_ids:
        js = judge_scores.get(j, {})
        overlap = sorted(keys.intersection(js.keys()))
        if len(overlap) < 3:
            ys.append(float("nan"))
            continue
        x = [js[k] for k in overlap]
        y = [human_scores[k] for k in overlap]
        ys.append(spearman_corr(x, y))
    return ys


def geo_index(comp: Sequence[Sequence[float]], w: Sequence[float], eps: float) -> List[float]:
    out: List[float] = []
    n_judges = len(comp[0]) if comp else 0
    for j in range(n_judges):
        log_sum = 0.0
        for i, weight in enumerate(w):
            log_sum += weight * math.log(max(eps, min(1.0, comp[i][j])))
        out.append(math.exp(log_sum))
    return out


def _dirichlet_unit(k: int, rng: random.Random) -> List[float]:
    vals = [rng.gammavariate(1.0, 1.0) for _ in range(k)]
    total = sum(vals)
    return [v / total for v in vals]


def fit_weights_random_search(
    comp: Sequence[Sequence[float]],
    y: Sequence[float],
    iters: int,
    seed: int,
    eps: float,
) -> Tuple[List[float], float]:
    rng = random.Random(seed)
    best_w = [1.0 / len(comp)] * len(comp)
    best_r = float("-inf")

    candidates = [
        [1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0.4, 0, 0.6, 0, 0],
        [0.25, 0.25, 0.2, 0.15, 0.1, 0.05],
    ]

    for w in candidates:
        total = sum(w)
        ww = [v / total for v in w]
        r = spearman_corr(geo_index(comp, ww, eps), y)
        if math.isfinite(r) and r > best_r:
            best_r = r
            best_w = ww

    for _ in range(iters):
        w = _dirichlet_unit(len(comp), rng)
        r = spearman_corr(geo_index(comp, w, eps), y)
        if math.isfinite(r) and r > best_r:
            best_r = r
            best_w = w

    return best_w, best_r


def _subset_components(comp: Sequence[Sequence[float]], mask: Sequence[bool]) -> List[List[float]]:
    return [[v for v, keep in zip(component, mask) if keep] for component in comp]


def run_legacy_split(args: argparse.Namespace) -> int:
    args.out_dir.mkdir(parents=True, exist_ok=True)

    val_tsv = args.split_dir / f"val_{args.label_set}.tsv"
    test_tsv = args.split_dir / f"test_{args.label_set}.tsv"

    human_val = load_human_scores(val_tsv)
    human_test = load_human_scores(test_tsv)
    judge_scores = load_judge_scores(args.detail_csv)
    judge_ids, comp = components_from_summary(args.summary_json)

    y_val = human_corr_per_judge(judge_ids, judge_scores, human_val)
    y_test = human_corr_per_judge(judge_ids, judge_scores, human_test)

    valid = [math.isfinite(v) for v in y_val]
    if sum(valid) < 4:
        raise ValueError("Not enough judges with finite val correlation to calibrate")

    comp_valid = _subset_components(comp, valid)
    y_val_valid = [v for v in y_val if math.isfinite(v)]
    best_w, best_val_r = fit_weights_random_search(comp_valid, y_val_valid, args.search_iters, args.seed, args.eps)

    x_all = geo_index(comp, best_w, args.eps)
    val_r = spearman_corr([x for x, keep in zip(x_all, valid) if keep], [y for y in y_val if math.isfinite(y)])

    valid_test = [math.isfinite(v) for v in y_test]
    test_r = spearman_corr(
        [x for x, keep in zip(x_all, valid_test) if keep],
        [y for y in y_test if math.isfinite(y)],
    )

    out = {
        "experiment": "exp23_calibrated_val_report_test",
        "label_set": args.label_set,
        "inputs": {
            "summary_json": str(args.summary_json),
            "detail_csv": str(args.detail_csv),
            "split_dir": str(args.split_dir),
            "val_tsv": str(val_tsv),
            "test_tsv": str(test_tsv),
        },
        "search": {
            "iters": args.search_iters,
            "seed": args.seed,
            "eps": args.eps,
            "best_val_r_from_search": best_val_r,
        },
        "weights": {k: float(best_w[i]) for i, k in enumerate(COMP_ORDER)},
        "results": {
            "val_corr_spearman": val_r,
            "test_corr_spearman": test_r,
            "n_judges_val": int(sum(valid)),
            "n_judges_test": int(sum(valid_test)),
        },
        "per_judge": [
            {
                "judge_id": j,
                "cert_index_calibrated": float(x_all[i]),
                "human_corr_val": float(y_val[i]) if math.isfinite(y_val[i]) else None,
                "human_corr_test": float(y_test[i]) if math.isfinite(y_test[i]) else None,
            }
            for i, j in enumerate(judge_ids)
        ],
        "formula": "TI = exp(sum_i w_i * log(max(eps, v_i)))",
        "components_order": COMP_ORDER,
    }

    out_path = args.out_dir / f"summary_{args.label_set}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


def load_heldout_labels(label_dir: Path, glob_pat: str) -> List[dict]:
    rows: List[dict] = []
    for path in sorted(label_dir.glob(glob_pat)):
        if not path.is_file():
            continue
        rater_id = path.stem
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row_i, row in enumerate(reader, start=2):
                score_s = (row.get("human_score_0_5") or "").strip()
                if not score_s:
                    continue
                rows.append(
                    {
                        "rater_id": rater_id,
                        "source_file": repo_path(path),
                        "source_line": row_i,
                        "gold_file": row["gold_file"],
                        "candidate_file": row["candidate_file"],
                        "item_key": f"{row['gold_file']}::{row['candidate_file']}",
                        "score": float(score_s),
                    }
                )
    return rows


def aggregate_heldout_labels(rows: Sequence[dict]) -> Tuple[Dict[str, Dict[str, float]], List[dict], dict]:
    by_key: Dict[str, List[dict]] = defaultdict(list)
    by_rater: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        by_key[row["item_key"]].append(row)
        by_rater[row["rater_id"]].append(float(row["score"]))

    rater_stats: Dict[str, Tuple[float, float]] = {}
    for rater, vals in by_rater.items():
        mu = sum(vals) / len(vals)
        sigma = statistics.pstdev(vals)
        rater_stats[rater] = (mu, sigma if sigma > 1e-12 else 1.0)

    aggregations = {name: {} for name in HELDOUT_AGGREGATIONS}
    pair_rows: List[dict] = []
    for key, key_rows in sorted(by_key.items()):
        scores = [float(r["score"]) for r in key_rows]
        zscores = [
            (float(r["score"]) - rater_stats[r["rater_id"]][0]) / rater_stats[r["rater_id"]][1]
            for r in key_rows
        ]
        raw_mean = sum(scores) / len(scores)
        raw_median = statistics.median(scores)
        rater_zmean = sum(zscores) / len(zscores)
        aggregations["raw_mean"][key] = raw_mean
        aggregations["raw_median"][key] = raw_median
        aggregations["rater_zmean"][key] = rater_zmean
        gold_file, candidate_file = key.split("::", 1)
        pair_rows.append(
            {
                "item_key": key,
                "gold_file": gold_file,
                "candidate_file": candidate_file,
                "n_ratings": len(scores),
                "raw_mean": raw_mean,
                "raw_median": raw_median,
                "rater_zmean": rater_zmean,
                "ratings_json": json.dumps(
                    [
                        {
                            "rater_id": r["rater_id"],
                            "score": r["score"],
                            "source_file": r["source_file"],
                            "source_line": r["source_line"],
                        }
                        for r in key_rows
                    ],
                    sort_keys=True,
                ),
            }
        )

    meta = {
        "n_label_files": len({r["source_file"] for r in rows}),
        "n_nonblank_labels": len(rows),
        "n_unique_pairs": len(by_key),
        "ratings_per_pair_distribution": dict(sorted(Counter(len(v) for v in by_key.values()).items())),
        "labels_per_rater": dict(sorted((r, len(v)) for r, v in by_rater.items())),
        "rater_stats": {
            r: {"mean": mu, "population_std": sigma}
            for r, (mu, sigma) in sorted(rater_stats.items())
        },
    }
    return aggregations, pair_rows, meta


def load_trust_vector(path: Path, trust_column: str) -> List[Tuple[str, float]]:
    out: List[Tuple[str, float]] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append((row["judge_id"], float(row[trust_column])))
    return out


def _candidate_file(item_key: str) -> str:
    return item_key.split("::", 1)[1]


def score_for_key(
    judge_scores: Mapping[str, float],
    item_key: str,
    candidate_alias: Mapping[str, str] | None,
) -> Tuple[float | None, str]:
    if item_key in judge_scores:
        return judge_scores[item_key], "exact"
    if candidate_alias is None:
        return None, "missing"
    alias_key = candidate_alias.get(_candidate_file(item_key))
    if alias_key is None:
        return None, "missing"
    return judge_scores[alias_key], "candidate_alias"


def build_candidate_alias_map(scored_keys: Iterable[str]) -> Dict[str, str]:
    candidates: Dict[str, List[str]] = defaultdict(list)
    for key in scored_keys:
        candidates[_candidate_file(key)].append(key)
    return {cand: keys[0] for cand, keys in candidates.items() if len(keys) == 1}


def evaluate_heldout_aggregation(
    aggregation: Mapping[str, float],
    trust_vector: Sequence[Tuple[str, float]],
    judge_scores: Mapping[str, Mapping[str, float]],
    *,
    use_candidate_alias: bool,
) -> Tuple[dict, List[dict]]:
    per_judge: List[dict] = []
    trust_vals: List[float] = []
    human_vals: List[float] = []
    for judge_id, trust_score in trust_vector:
        scores_for_judge = judge_scores.get(judge_id, {})
        alias = build_candidate_alias_map(scores_for_judge.keys()) if use_candidate_alias else None
        judge_x: List[float] = []
        human_y: List[float] = []
        exact = 0
        candidate_alias = 0
        for item_key, human_score in sorted(aggregation.items()):
            judge_score, match_mode = score_for_key(scores_for_judge, item_key, alias)
            if judge_score is None:
                continue
            judge_x.append(judge_score)
            human_y.append(human_score)
            if match_mode == "exact":
                exact += 1
            elif match_mode == "candidate_alias":
                candidate_alias += 1
        human_corr = spearman_corr(judge_x, human_y)
        row = {
            "judge_id": judge_id,
            "trust_score": trust_score,
            "heldout_human_spearman": human_corr,
            "n_pairs_scored": len(judge_x),
            "n_pairs_exact": exact,
            "n_pairs_candidate_alias": candidate_alias,
        }
        per_judge.append(row)
        if math.isfinite(human_corr):
            trust_vals.append(trust_score)
            human_vals.append(human_corr)

    rho = spearman_corr(trust_vals, human_vals)
    pearson = pearson_corr(trust_vals, human_vals)
    result = {
        "spearman_TI_vs_heldout_human": rho,
        "spearman_exact_permutation_p_two_sided": exact_permutation_p_spearman(trust_vals, human_vals),
        "pearson_TI_vs_heldout_human": pearson,
        "n_judges": len(trust_vals),
        "n_pairs_scored_min": min((r["n_pairs_scored"] for r in per_judge), default=0),
        "n_pairs_scored_max": max((r["n_pairs_scored"] for r in per_judge), default=0),
        "n_pairs_exact_min": min((r["n_pairs_exact"] for r in per_judge), default=0),
        "n_pairs_candidate_alias_max": max((r["n_pairs_candidate_alias"] for r in per_judge), default=0),
        "match_mode": "exact_plus_candidate_alias" if use_candidate_alias else "exact_gold_candidate",
    }
    return result, per_judge


def write_csv(path: Path, rows: Sequence[Mapping[str, object]], fieldnames: Sequence[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_missing_pairs_csv(
    path: Path,
    human_keys: Iterable[str],
    judge_scores: Mapping[str, Mapping[str, float]],
) -> dict:
    scored_union = set()
    for scores in judge_scores.values():
        scored_union.update(scores.keys())
    candidate_alias = build_candidate_alias_map(scored_union)

    rows: List[dict] = []
    for key in sorted(set(human_keys) - scored_union):
        cand = _candidate_file(key)
        alias_key = candidate_alias.get(cand)
        rows.append(
            {
                "item_key": key,
                "gold_file": key.split("::", 1)[0],
                "candidate_file": cand,
                "reason": "no_exact_frozen_judge_score",
                "candidate_alias_key": alias_key or "",
            }
        )
    write_csv(path, rows, ["item_key", "gold_file", "candidate_file", "reason", "candidate_alias_key"])
    return {
        "n_missing_exact_pairs": len(rows),
        "n_missing_with_unique_candidate_alias": sum(1 for r in rows if r["candidate_alias_key"]),
        "n_missing_without_candidate_alias": sum(1 for r in rows if not r["candidate_alias_key"]),
    }


def write_heldout_report(path: Path, summary: Mapping[str, object]) -> None:
    primary = summary["primary_result"]
    sensitivity = summary.get("candidate_file_alias_sensitivity")
    label_pool = summary["label_pool"]
    caveat = summary["methodological_caveats"][0]
    lines = [
        "# Exp23 Held-Out Human-Label Test Report",
        "**TLDR:** Frozen \\(\\mathrm{TI}_{\\mathrm{var}}\\) has a held-out judge-level Spearman correlation of "
        f"{primary['spearman_TI_vs_heldout_human']:.3f} against the fresh independent human-label pool. "
        f"The primary exact-key analysis uses {primary['n_pairs_scored_min']} scored pairs because the frozen judge-score CSV does not cover all "
        f"{label_pool['n_unique_pairs']} labeled pairs.",
        "",
        "## Primary Result",
        "",
        "| Metric | Value |",
        "|:---|---:|",
        f"| Label files | {label_pool['n_label_files']} |",
        f"| Nonblank labels | {label_pool['n_nonblank_labels']} |",
        f"| Unique labeled pairs | {label_pool['n_unique_pairs']} |",
        f"| Exact scored pairs per judge | {primary['n_pairs_scored_min']} |",
        f"| Judges | {primary['n_judges']} |",
        f"| Spearman(TI_var, held-out human Spearman) | {primary['spearman_TI_vs_heldout_human']:.3f} |",
        f"| Exact permutation p-value | {primary['spearman_exact_permutation_p_two_sided']:.4f} |",
        f"| Pearson(TI_var, held-out human Spearman) | {primary['pearson_TI_vs_heldout_human']:.3f} |",
        "",
        "## Sensitivity",
        "",
        "| Aggregation | Match mode | Spearman | p-value | Scored pairs |",
        "|:---|:---|---:|---:|---:|",
    ]
    for name, result in summary["results_by_aggregation"].items():
        lines.append(
            f"| {name} | {result['match_mode']} | {result['spearman_TI_vs_heldout_human']:.3f} | "
            f"{result['spearman_exact_permutation_p_two_sided']:.4f} | {result['n_pairs_scored_min']} |"
        )
    if sensitivity:
        lines.append(
            f"| raw_mean | {sensitivity['match_mode']} | {sensitivity['spearman_TI_vs_heldout_human']:.3f} | "
            f"{sensitivity['spearman_exact_permutation_p_two_sided']:.4f} | {sensitivity['n_pairs_scored_min']} |"
        )
    lines.extend(
        [
            "",
            "## Methodological Caveat",
            "",
            caveat,
            "",
            "## Review Request",
            "",
            "@ehersch please check the exact-match caveat and whether the paper should quote only the primary 60-pair result or also mention the candidate-file alias sensitivity.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_heldout_human_labels(args: argparse.Namespace) -> int:
    out_dir = args.heldout_out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    label_rows = load_heldout_labels(args.human_label_dir, args.human_label_glob)
    if not label_rows:
        raise ValueError(f"No held-out labels found in {args.human_label_dir} with glob {args.human_label_glob}")
    aggregations, pair_rows, label_meta = aggregate_heldout_labels(label_rows)
    trust_vector = load_trust_vector(args.trust_vector_csv, args.trust_column)
    judge_scores = load_judge_scores(args.detail_csv)

    pair_labels_csv = out_dir / "pair_label_aggregates.csv"
    write_csv(
        pair_labels_csv,
        pair_rows,
        ["item_key", "gold_file", "candidate_file", "n_ratings", "raw_mean", "raw_median", "rater_zmean", "ratings_json"],
    )

    missing_pairs_csv = out_dir / "missing_frozen_judge_pairs.csv"
    missing_meta = write_missing_pairs_csv(missing_pairs_csv, aggregations["raw_mean"].keys(), judge_scores)

    results_by_aggregation: Dict[str, dict] = {}
    per_judge_by_aggregation: Dict[str, List[dict]] = {}
    for name, aggregation in aggregations.items():
        result, per_judge = evaluate_heldout_aggregation(
            aggregation,
            trust_vector,
            judge_scores,
            use_candidate_alias=False,
        )
        results_by_aggregation[name] = result
        per_judge_by_aggregation[name] = per_judge

    primary_result = results_by_aggregation["raw_mean"]
    primary_per_judge_csv = out_dir / "per_judge_primary_raw_mean_exact.csv"
    write_csv(
        primary_per_judge_csv,
        per_judge_by_aggregation["raw_mean"],
        [
            "judge_id",
            "trust_score",
            "heldout_human_spearman",
            "n_pairs_scored",
            "n_pairs_exact",
            "n_pairs_candidate_alias",
        ],
    )

    candidate_file_alias_sensitivity = None
    candidate_file_alias_per_judge_csv = None
    if args.candidate_alias_sensitivity:
        candidate_file_alias_sensitivity, per_judge_alias = evaluate_heldout_aggregation(
            aggregations["raw_mean"],
            trust_vector,
            judge_scores,
            use_candidate_alias=True,
        )
        candidate_file_alias_per_judge_csv = out_dir / "per_judge_raw_mean_candidate_alias_sensitivity.csv"
        write_csv(
            candidate_file_alias_per_judge_csv,
            per_judge_alias,
            [
                "judge_id",
                "trust_score",
                "heldout_human_spearman",
                "n_pairs_scored",
                "n_pairs_exact",
                "n_pairs_candidate_alias",
            ],
        )

    summary = {
        "experiment": "exp23_heldout_human_labels",
        "protocol": "PROTOCOL_test.md",
        "inputs": {
            "human_label_dir": repo_path(args.human_label_dir),
            "human_label_glob": args.human_label_glob,
            "detail_csv": repo_path(args.detail_csv),
            "trust_vector_csv": repo_path(args.trust_vector_csv),
            "trust_column": args.trust_column,
        },
        "frozen_index": {
            "name": "TI_var",
            "source": repo_path(args.trust_vector_csv),
            "selection_rule": "Use existing Exp28 variance-aware trust vector; do not tune weights or thresholds on held-out labels.",
        },
        "label_pool": label_meta,
        "missing_frozen_judge_scores": missing_meta,
        "primary_aggregation": "raw_mean",
        "primary_result": primary_result,
        "results_by_aggregation": results_by_aggregation,
        "candidate_file_alias_sensitivity": candidate_file_alias_sensitivity,
        "methodological_caveats": [
            (
                "The fresh independent label pool contains 343 nonblank labels over 78 unique pairs, "
                "but the frozen Exp16 judge-score detail file has exact gold::candidate scores for only 60 "
                "of those pairs. The primary result therefore uses the 60 exact-key pairs and does not spend "
                "new LLM budget to score the remaining pairs. A candidate-file alias sensitivity can recover "
                "renumbered real-code pairs, but it is not the primary result because it changes the gold-file key."
            ),
            (
                "The held-out test reuses the same eight frozen judge configurations and TI_var scores from the "
                "validation-stage judge panel. It is held out over human raters and part of the item pool, not over "
                "judge family."
            ),
        ],
        "outputs": {
            "summary_json": repo_path(out_dir / "summary.json"),
            "report_md": repo_path(out_dir / "report.md"),
            "pair_label_aggregates_csv": repo_path(pair_labels_csv),
            "missing_pairs_csv": repo_path(missing_pairs_csv),
            "per_judge_primary_csv": repo_path(primary_per_judge_csv),
            "per_judge_candidate_alias_sensitivity_csv": repo_path(candidate_file_alias_per_judge_csv)
            if candidate_file_alias_per_judge_csv
            else None,
        },
    }

    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_heldout_report(out_dir / "report.md", summary)
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    if args.mode == "heldout-human-labels":
        return run_heldout_human_labels(args)
    return run_legacy_split(args)


if __name__ == "__main__":
    raise SystemExit(main())
