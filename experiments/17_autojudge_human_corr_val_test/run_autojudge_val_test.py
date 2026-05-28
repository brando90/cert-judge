#!/usr/bin/env python3
"""Autojudge validation/test selection over frozen human-label artifacts.

This script intentionally uses only the Python standard library. The local
macOS environment has had stale x86 NumPy wheels, and this experiment only
needs CSV parsing plus rank correlations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
EXP04_DIR = REPO_ROOT / "experiments" / "04_veribench_validation"
EXP17_DIR = REPO_ROOT / "experiments" / "17_autojudge_human_corr_val_test"
DEFAULT_OUT_DIR = EXP17_DIR / "results"

SPLIT_SALT = "cert-judge-exp17-autojudge-val-test-v1"
PRIMARY_KIND_ALLOWLIST = {"llm"}

HUMAN_LABEL_SOURCES = [
    ("participant1", REPO_ROOT / "experiments" / "human_labels" / "participant1_data_correct_prompt.tsv"),
    ("participant2", REPO_ROOT / "experiments" / "human_labels" / "participant2_data_pass_1.tsv"),
    ("participant3", REPO_ROOT / "experiments" / "human_labels" / "participant3_data_pass_1.tsv"),
    ("participant4", REPO_ROOT / "experiments" / "human_labels" / "participant4_data_pass_1.tsv"),
    ("participant5", REPO_ROOT / "experiments" / "human_labels" / "participant5_data_pass_1.tsv"),
    ("ethan_pass1", EXP04_DIR / "data" / "ethan_human_scores_20260425.tsv"),
    ("ethan_pass2", EXP04_DIR / "data" / "ethan_human_scores_ORIGINAL.tsv"),
]

FAMILY_SPECS = {
    "Codex": {
        "model": "gpt-5.3-codex",
        "result_dir": EXP04_DIR / "results_exp22_expanded_judges_stable" / "exp16",
    },
    "Opus": {
        "model": "claude-opus-4-7",
        "result_dir": EXP04_DIR / "results_exp16_opus47_r3_median",
    },
    "Leanstral": {
        "model": "labs-leanstral-2603",
        "result_dir": EXP04_DIR / "results_exp16_leanstral_r3_median",
    },
}
FAMILY_ORDER = ["Codex", "Opus", "Leanstral"]


@dataclass(frozen=True)
class Candidate:
    family: str
    judge_id: str
    kind: str
    model: str
    prompt_name: str
    result_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select one autojudge per family on a frozen validation split and report held-out test correlation."
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--train-frac", type=float, default=0.5)
    parser.add_argument("--split-salt", default=SPLIT_SALT)
    parser.add_argument("--bootstrap-iters", type=int, default=5000)
    parser.add_argument(
        "--include-bad-controls",
        action="store_true",
        help="Non-primary sensitivity: include llm_bad judges in the selectable pool.",
    )
    return parser.parse_args()


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def item_key(gold_file: str, candidate_file: str) -> str:
    return f"{gold_file}::{candidate_file}"


def split_item_key(key: str) -> tuple[str, str]:
    return tuple(key.split("::", 1))  # type: ignore[return-value]


def read_human_rows() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    source_counts: dict[str, int] = {}
    missing_sources: list[str] = []
    for source_id, path in HUMAN_LABEL_SOURCES:
        if not path.exists():
            missing_sources.append(repo_path(path))
            continue
        count = 0
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line_no, row in enumerate(reader, start=2):
                score_s = (row.get("human_score_0_5") or "").strip()
                gold_file = (row.get("gold_file") or "").strip()
                candidate_file = (row.get("candidate_file") or "").strip()
                if not score_s or not gold_file or not candidate_file:
                    continue
                rows.append(
                    {
                        "source_id": source_id,
                        "source_file": repo_path(path),
                        "source_line": line_no,
                        "gold_file": gold_file,
                        "candidate_file": candidate_file,
                        "item_key": item_key(gold_file, candidate_file),
                        "score": float(score_s),
                    }
                )
                count += 1
        source_counts[source_id] = count

    meta = {
        "source_counts": source_counts,
        "missing_sources": missing_sources,
        "n_sources_found": len(source_counts),
        "n_nonblank_labels": len(rows),
    }
    return rows, meta


def aggregate_human_rows(rows: Sequence[Mapping[str, object]]) -> tuple[dict[str, float], list[dict], dict]:
    by_key: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        by_key[str(row["item_key"])].append(row)

    agg: dict[str, float] = {}
    out_rows: list[dict] = []
    for key, key_rows in sorted(by_key.items()):
        scores = [float(r["score"]) for r in key_rows]
        agg[key] = sum(scores) / len(scores)
        gold_file, candidate_file = split_item_key(key)
        out_rows.append(
            {
                "item_key": key,
                "gold_file": gold_file,
                "candidate_file": candidate_file,
                "human_mean_0_5": agg[key],
                "human_median_0_5": statistics.median(scores),
                "n_ratings": len(scores),
                "source_ids": ";".join(sorted(str(r["source_id"]) for r in key_rows)),
                "ratings_json": json.dumps(
                    [
                        {
                            "source_id": r["source_id"],
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
        "n_unique_pairs": len(by_key),
        "ratings_per_pair_distribution": dict(sorted(Counter(len(v) for v in by_key.values()).items())),
    }
    return agg, out_rows, meta


def read_candidates(include_bad_controls: bool) -> list[Candidate]:
    allowed_kinds = set(PRIMARY_KIND_ALLOWLIST)
    if include_bad_controls:
        allowed_kinds.add("llm_bad")

    candidates: list[Candidate] = []
    for family, spec in FAMILY_SPECS.items():
        result_dir = Path(spec["result_dir"])
        judge_rows = result_dir / "judge_rows.csv"
        if not judge_rows.exists():
            raise FileNotFoundError(f"Missing judge rows for {family}: {judge_rows}")
        with judge_rows.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("model") != spec["model"]:
                    continue
                if row.get("kind") not in allowed_kinds:
                    continue
                candidates.append(
                    Candidate(
                        family=family,
                        judge_id=row["judge_id"],
                        kind=row.get("kind", ""),
                        model=row.get("model", ""),
                        prompt_name=row.get("prompt_name", ""),
                        result_dir=result_dir,
                    )
                )
    if not candidates:
        raise ValueError("No selectable candidates found")
    return candidates


def read_score_maps(candidates: Sequence[Candidate]) -> dict[str, dict[str, float]]:
    score_maps: dict[str, dict[str, float]] = {}
    detail_cache: dict[Path, list[dict]] = {}

    for candidate in candidates:
        detail_rows = candidate.result_dir / "detail_rows.csv"
        if detail_rows not in detail_cache:
            if not detail_rows.exists():
                raise FileNotFoundError(f"Missing detail rows: {detail_rows}")
            with detail_rows.open("r", newline="", encoding="utf-8") as f:
                detail_cache[detail_rows] = list(csv.DictReader(f))
        scores: dict[str, float] = {}
        for row in detail_cache[detail_rows]:
            if row.get("judge_id") != candidate.judge_id:
                continue
            if row.get("row_type") != "human_eval_union":
                continue
            scores[row["item_key"]] = float(row["score_mean"])
        score_maps[candidate.judge_id] = scores
    return score_maps


def rankdata_average(values: Sequence[float]) -> list[float]:
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


def pearson_corr(xs: Sequence[float], ys: Sequence[float]) -> float:
    pairs = [(float(x), float(y)) for x, y in zip(xs, ys) if math.isfinite(float(x)) and math.isfinite(float(y))]
    if len(pairs) < 2:
        return float("nan")
    x_vals = [p[0] for p in pairs]
    y_vals = [p[1] for p in pairs]
    mx = sum(x_vals) / len(x_vals)
    my = sum(y_vals) / len(y_vals)
    dx = [x - mx for x in x_vals]
    dy = [y - my for y in y_vals]
    sx = math.sqrt(sum(x * x for x in dx))
    sy = math.sqrt(sum(y * y for y in dy))
    if sx <= 0.0 or sy <= 0.0:
        return float("nan")
    return sum(x * y for x, y in zip(dx, dy)) / (sx * sy)


def spearman_corr(xs: Sequence[float], ys: Sequence[float]) -> float:
    pairs = [(float(x), float(y)) for x, y in zip(xs, ys) if math.isfinite(float(x)) and math.isfinite(float(y))]
    if len(pairs) < 2:
        return float("nan")
    x_vals = [p[0] for p in pairs]
    y_vals = [p[1] for p in pairs]
    return pearson_corr(rankdata_average(x_vals), rankdata_average(y_vals))


def stable_seed(*parts: object) -> int:
    blob = "\0".join(str(p) for p in parts)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def bootstrap_ci_spearman(xs: Sequence[float], ys: Sequence[float], iters: int, seed: int) -> tuple[float, float]:
    if len(xs) < 3 or iters <= 0:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    vals: list[float] = []
    n = len(xs)
    for _ in range(iters):
        idx = [rng.randrange(n) for _ in range(n)]
        rho = spearman_corr([xs[i] for i in idx], [ys[i] for i in idx])
        if math.isfinite(rho):
            vals.append(rho)
    if not vals:
        return float("nan"), float("nan")
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return lo, hi


def hash_split_tasks(tasks: Sequence[str], train_frac: float, salt: str) -> tuple[list[str], list[str], list[dict]]:
    if not 0.1 <= train_frac <= 0.9:
        raise ValueError("--train-frac must be between 0.1 and 0.9")
    ranked = []
    for task in sorted(tasks):
        digest = hashlib.sha256(f"{salt}\0{task}".encode("utf-8")).hexdigest()
        ranked.append((digest, task))
    ranked.sort()
    n_train = round(len(ranked) * train_frac)
    n_train = min(max(1, n_train), len(ranked) - 1)
    train_tasks = sorted(task for _, task in ranked[:n_train])
    test_tasks = sorted(task for _, task in ranked[n_train:])
    split_rows = [
        {
            "gold_file": task,
            "split": "train" if task in train_tasks else "test",
            "sha256_rank": i + 1,
            "sha256": digest,
        }
        for i, (digest, task) in enumerate(ranked)
    ]
    return train_tasks, test_tasks, split_rows


def rows_for_split(keys: Iterable[str], split_tasks: set[str]) -> list[str]:
    return sorted(k for k in keys if split_item_key(k)[0] in split_tasks)


def evaluate_candidate(
    candidate: Candidate,
    score_map: Mapping[str, float],
    human_scores: Mapping[str, float],
    keys: Sequence[str],
    split_name: str,
    bootstrap_iters: int,
) -> dict:
    judge_vals = [float(score_map[k]) for k in keys]
    human_vals = [float(human_scores[k]) for k in keys]
    rho = spearman_corr(judge_vals, human_vals)
    pearson = pearson_corr(judge_vals, human_vals)
    ci_lo, ci_hi = bootstrap_ci_spearman(
        judge_vals,
        human_vals,
        bootstrap_iters,
        stable_seed(candidate.judge_id, split_name, "bootstrap"),
    )
    return {
        "family": candidate.family,
        "judge_id": candidate.judge_id,
        "kind": candidate.kind,
        "model": candidate.model,
        "prompt_name": candidate.prompt_name,
        "split": split_name,
        "n_pairs": len(keys),
        "spearman_r": rho,
        "spearman_ci_lo": ci_lo,
        "spearman_ci_hi": ci_hi,
        "pearson_r": pearson,
        "result_dir": repo_path(candidate.result_dir),
    }


def write_csv(path: Path, rows: Sequence[Mapping[str, object]], fieldnames: Sequence[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: object, digits: int = 3) -> str:
    try:
        x = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(x):
        return "NA"
    return f"{x:.{digits}f}"


def format_prompt_counts(counts: Mapping[str, int]) -> str:
    parts = []
    for family in FAMILY_ORDER:
        count = counts.get(family, 0)
        noun = "eligible prompt" if count == 1 else "eligible prompts"
        parts.append(f"{family} has {count} {noun}")
    return "; ".join(parts)


def write_report(out_dir: Path, summary: Mapping[str, object], selected_rows: Sequence[Mapping[str, object]]) -> None:
    label_meta = summary["label_pool"]  # type: ignore[index]
    split = summary["split"]  # type: ignore[index]
    caveats = summary["caveats"]  # type: ignore[index]
    source_url = "https://arxiv.org/abs/2512.17267"
    selected_by_family = {str(row["family"]): row for row in selected_rows}
    tldr_parts = []
    for family in FAMILY_ORDER:
        row = selected_by_family[family]
        tldr_parts.append(
            f"{family} `{row['selected_prompt']}` test Spearman {fmt_float(row['test_spearman'])}"
        )
    lines = [
        "# Autojudge Human Correlation Val/Test Report",
        "**TLDR:** A validation-only prompt-selection procedure selects "
        + ", ".join(tldr_parts)
        + " under the frozen split. Codex does not generalize on this split; Opus and Leanstral are weakly positive with bootstrap intervals crossing zero.",
        "",
        "## Result",
        "",
        "| Family | Selected judge | Train Spearman | Test Spearman | Test 95% boot CI | n train | n test |",
        "|:---|:---|---:|---:|:---|---:|---:|",
    ]
    for family in FAMILY_ORDER:
        row = selected_by_family[family]
        lines.append(
            f"| {row['family']} | `{row['selected_judge_id']}` | "
            f"{fmt_float(row['train_spearman'])} | {fmt_float(row['test_spearman'])} | "
            f"[{fmt_float(row['test_ci_lo'])}, {fmt_float(row['test_ci_hi'])}] | "
            f"{row['n_train']} | {row['n_test']} |"
        )

    lines.extend(
        [
            "",
            "## Protocol",
            "",
            f"- Human target: raw mean over five participant files plus Ethan pass1 and Ethan pass2, with Ethan's two passes intentionally counted as two label sources.",
            f"- Split: fixed SHA256 task split with salt `{split['salt']}`; all candidates for a `gold_file` stay in the same split.",
            f"- Train split: {split['n_train_tasks']} tasks / {split['n_train_pairs']} candidate pairs.",
            f"- Test split: {split['n_test_tasks']} tasks / {split['n_test_pairs']} candidate pairs.",
            "- Selection rule: within each family, choose the eligible prompt with the highest train Spearman against the aggregate human target; break exact ties by lexicographic `judge_id`.",
            "- Eligible primary candidates: saved `kind=llm` judges for the target family only. Explicit `llm_bad`, edit-distance, random, and other-family controls are excluded from primary selection.",
            f"- AutoMetrics relation: this is an AutoMetrics-style low-data selector over an existing metric/prompt bank, not a full reimplementation with new generated criteria or regression composition. AutoMetrics is the motivating paper: [{source_url}]({source_url}).",
            "",
            "## Exact Commands",
            "",
            "```bash",
            "cd /Users/brandomiranda/cert-judge-autojudge-human-corr-val-test",
            "python experiments/17_autojudge_human_corr_val_test/run_autojudge_val_test.py \\",
            "  --out-dir experiments/17_autojudge_human_corr_val_test/results",
            "```",
            "",
            "## Label And Coverage",
            "",
            f"- Label sources found: {label_meta['n_sources_found']} files.",
            f"- Nonblank ratings loaded: {label_meta['n_nonblank_labels']}.",
            f"- Unique labeled pairs before score coverage filtering: {label_meta['n_unique_pairs']}.",
            f"- Exact pairs scored by every primary candidate: {summary['coverage']['n_common_scored_pairs']}.",
            f"- Human-labeled pairs excluded for missing saved judge scores: {summary['coverage']['n_human_pairs_without_common_scores']}.",
            "",
            "## Caveats",
            "",
        ]
    )
    for caveat in caveats:
        lines.append(f"- {caveat}")

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `results/selection_table.csv`: selected family-level train/test table.",
            "- `results/all_candidate_correlations.csv`: every eligible prompt correlation before selection.",
            "- `results/frozen_split.csv`: task-level train/test assignment.",
            "- `results/pair_label_aggregates.csv`: seven-source human label aggregate.",
            "- `results/missing_pairs.csv`: human-labeled pairs excluded from primary exact-score analysis.",
            "- `results/summary.json`: machine-readable run metadata and selected rows.",
            "",
            "## Paper Patch Decision",
            "",
            "No paper text was patched in this PR. The result is a new prompt-selection diagnostic over the existing saved judge panel, not a held-out test of the paper's variance-aware trust index. Current paper drafts already separate validation-set evidence from held-out generalization, and this result is too caveated for a clean main-text claim without reviewer discussion.",
            "",
        ]
    )
    (EXP17_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    human_rows, human_source_meta = read_human_rows()
    if human_source_meta["missing_sources"]:
        raise FileNotFoundError(f"Missing human label sources: {human_source_meta['missing_sources']}")
    human_scores, pair_rows, human_agg_meta = aggregate_human_rows(human_rows)

    candidates = read_candidates(args.include_bad_controls)
    score_maps = read_score_maps(candidates)

    common_keys = set(human_scores.keys())
    for candidate in candidates:
        common_keys &= set(score_maps[candidate.judge_id].keys())
    if len(common_keys) < 12:
        raise ValueError(f"Only {len(common_keys)} common scored pairs; aborting")

    tasks = sorted({split_item_key(k)[0] for k in common_keys})
    train_tasks, test_tasks, split_rows = hash_split_tasks(tasks, args.train_frac, args.split_salt)
    train_keys = rows_for_split(common_keys, set(train_tasks))
    test_keys = rows_for_split(common_keys, set(test_tasks))

    candidate_rows: list[dict] = []
    for candidate in candidates:
        train_eval = evaluate_candidate(
            candidate, score_maps[candidate.judge_id], human_scores, train_keys, "train", args.bootstrap_iters
        )
        test_eval = evaluate_candidate(
            candidate, score_maps[candidate.judge_id], human_scores, test_keys, "test", args.bootstrap_iters
        )
        row = {
            "family": candidate.family,
            "judge_id": candidate.judge_id,
            "kind": candidate.kind,
            "model": candidate.model,
            "prompt_name": candidate.prompt_name,
            "train_spearman": train_eval["spearman_r"],
            "train_ci_lo": train_eval["spearman_ci_lo"],
            "train_ci_hi": train_eval["spearman_ci_hi"],
            "train_pearson": train_eval["pearson_r"],
            "n_train": train_eval["n_pairs"],
            "test_spearman": test_eval["spearman_r"],
            "test_ci_lo": test_eval["spearman_ci_lo"],
            "test_ci_hi": test_eval["spearman_ci_hi"],
            "test_pearson": test_eval["pearson_r"],
            "n_test": test_eval["n_pairs"],
            "result_dir": train_eval["result_dir"],
        }
        candidate_rows.append(row)

    selected_rows: list[dict] = []
    for family in FAMILY_ORDER:
        rows = [r for r in candidate_rows if r["family"] == family]
        if not rows:
            raise ValueError(f"No candidate rows for {family}")
        selected = sorted(
            rows,
            key=lambda r: (
                -float(r["train_spearman"]) if math.isfinite(float(r["train_spearman"])) else float("inf"),
                str(r["judge_id"]),
            ),
        )[0]
        selected_rows.append(
            {
                "family": family,
                "selected_judge_id": selected["judge_id"],
                "selected_prompt": selected["prompt_name"],
                "train_spearman": selected["train_spearman"],
                "train_ci_lo": selected["train_ci_lo"],
                "train_ci_hi": selected["train_ci_hi"],
                "train_pearson": selected["train_pearson"],
                "n_train": selected["n_train"],
                "test_spearman": selected["test_spearman"],
                "test_ci_lo": selected["test_ci_lo"],
                "test_ci_hi": selected["test_ci_hi"],
                "test_pearson": selected["test_pearson"],
                "n_test": selected["n_test"],
                "result_dir": selected["result_dir"],
            }
        )
    candidate_counts_by_family = {family: sum(1 for r in candidate_rows if r["family"] == family) for family in FAMILY_ORDER}

    scored_common = set(common_keys)
    missing_rows = []
    for key in sorted(set(human_scores) - scored_common):
        gold_file, candidate_file = split_item_key(key)
        missing_rows.append(
            {
                "item_key": key,
                "gold_file": gold_file,
                "candidate_file": candidate_file,
                "reason": "not_scored_by_every_primary_candidate_family",
                "human_mean_0_5": human_scores[key],
                "n_ratings": next(r["n_ratings"] for r in pair_rows if r["item_key"] == key),
            }
        )
    caveats = [
        f"The primary analysis uses exact gold_file::candidate_file matches only; {len(missing_rows)} aggregated human-labeled pairs lack saved scores from every primary family and are excluded rather than newly judged.",
        "The split is held out by problem, but rows within a problem share the same gold file; bootstrap intervals over pair rows therefore understate uncertainty if task-level dependence dominates.",
        "This is prompt selection over saved judge outputs, not a full AutoMetrics implementation with newly generated evaluator criteria or regression-composed metrics.",
        f"The candidate pool is not identical across families: {format_prompt_counts(candidate_counts_by_family)}.",
        "The human target is an aggregate of ordinal 0-5 labels; Spearman uses rank information and does not model rater-specific reliability.",
    ]

    for row in split_rows:
        row["n_pairs"] = sum(1 for key in common_keys if split_item_key(key)[0] == row["gold_file"])

    write_csv(
        out_dir / "pair_label_aggregates.csv",
        pair_rows,
        ["item_key", "gold_file", "candidate_file", "human_mean_0_5", "human_median_0_5", "n_ratings", "source_ids", "ratings_json"],
    )
    write_csv(out_dir / "frozen_split.csv", split_rows, ["gold_file", "split", "sha256_rank", "sha256", "n_pairs"])
    write_csv(
        out_dir / "all_candidate_correlations.csv",
        sorted(candidate_rows, key=lambda r: (r["family"], -float(r["train_spearman"]), r["judge_id"])),
    )
    write_csv(out_dir / "selection_table.csv", selected_rows)
    write_csv(out_dir / "missing_pairs.csv", missing_rows)

    summary = {
        "experiment": "17_autojudge_human_corr_val_test",
        "mode": "primary_llm_prompt_selection",
        "no_new_llm_calls": True,
        "human_sources": [{"source_id": sid, "path": repo_path(path)} for sid, path in HUMAN_LABEL_SOURCES],
        "family_specs": {
            family: {"model": spec["model"], "result_dir": repo_path(Path(spec["result_dir"]))}
            for family, spec in FAMILY_SPECS.items()
        },
        "label_pool": {**human_source_meta, **human_agg_meta},
        "split": {
            "salt": args.split_salt,
            "train_frac": args.train_frac,
            "n_tasks": len(tasks),
            "n_train_tasks": len(train_tasks),
            "n_test_tasks": len(test_tasks),
            "n_train_pairs": len(train_keys),
            "n_test_pairs": len(test_keys),
            "train_gold_files": train_tasks,
            "test_gold_files": test_tasks,
        },
        "coverage": {
            "n_common_scored_pairs": len(common_keys),
            "n_human_pairs_without_common_scores": len(missing_rows),
        },
        "selection_rule": {
            "objective": "maximize train Spearman(judge_score, human_mean_0_5) within family",
            "tie_break": "lexicographic judge_id",
            "primary_kind_allowlist": sorted(PRIMARY_KIND_ALLOWLIST),
            "include_bad_controls": bool(args.include_bad_controls),
            "candidate_counts_by_family": candidate_counts_by_family,
        },
        "bootstrap": {
            "iters": args.bootstrap_iters,
            "unit": "candidate pair rows",
        },
        "selected_rows": selected_rows,
        "outputs": {
            "pair_label_aggregates_csv": repo_path(out_dir / "pair_label_aggregates.csv"),
            "frozen_split_csv": repo_path(out_dir / "frozen_split.csv"),
            "all_candidate_correlations_csv": repo_path(out_dir / "all_candidate_correlations.csv"),
            "selection_table_csv": repo_path(out_dir / "selection_table.csv"),
            "missing_pairs_csv": repo_path(out_dir / "missing_pairs.csv"),
            "summary_json": repo_path(out_dir / "summary.json"),
            "report_md": repo_path(EXP17_DIR / "REPORT.md"),
        },
        "caveats": caveats,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_report(out_dir, summary, selected_rows)

    print(json.dumps({"selected_rows": selected_rows, "summary_json": repo_path(out_dir / "summary.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
