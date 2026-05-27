#!/usr/bin/env python3
"""
Mathlib Style Bench MVP runner.

This script evaluates bad-code -> good-code Lean pairs where the intended
improvement is mathlib style rather than theorem semantics. It intentionally
does not call any LLM provider API. Use either the built-in heuristic scorer
for smoke tests or pass a CSV of externally produced judge scores.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
PY_SRC = REPO_ROOT / "py_src"
if str(PY_SRC) not in sys.path:
    sys.path.insert(0, str(PY_SRC))

from cert_judge.hsj_scoring import (  # noqa: E402
    compute_p2_or_p3_ordering_auc,
    compute_p4_stability,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_PAIRS_FILE = EXPERIMENT_DIR / "data" / "sample_pairs.jsonl"
DEFAULT_OUT_DIR = EXPERIMENT_DIR / "results" / "smoke"


@dataclass(frozen=True)
class StylePair:
    pair_id: str
    topic: str
    bad_path: Path
    good_path: Path
    split: str = "dev"
    style_issue: str = ""
    source: str = "mvp_handcrafted"


@dataclass(frozen=True)
class ScoreRecord:
    pair_id: str
    variant: str
    score: float
    judge_id: str
    repeat_idx: int
    source: str


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _read_jsonl(path: Path) -> Iterable[dict]:
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                yield json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc


def _resolve_manifest_path(value: str, manifest_dir: Path) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = manifest_dir / p
    return p.resolve()


def load_pairs(path: Path) -> List[StylePair]:
    manifest = path.expanduser().resolve()
    if not manifest.exists():
        raise FileNotFoundError(f"Pair manifest not found: {manifest}")

    pairs: List[StylePair] = []
    seen: set[str] = set()
    for row in _read_jsonl(manifest):
        pair_id = str(row["pair_id"])
        if pair_id in seen:
            raise ValueError(f"Duplicate pair_id in {manifest}: {pair_id}")
        seen.add(pair_id)
        pair = StylePair(
            pair_id=pair_id,
            topic=str(row.get("topic", "")),
            bad_path=_resolve_manifest_path(str(row["bad_path"]), manifest.parent),
            good_path=_resolve_manifest_path(str(row["good_path"]), manifest.parent),
            split=str(row.get("split", "dev")),
            style_issue=str(row.get("style_issue", "")),
            source=str(row.get("source", "mvp_handcrafted")),
        )
        missing = [p for p in (pair.bad_path, pair.good_path) if not p.exists()]
        if missing:
            raise FileNotFoundError(f"Missing Lean file(s) for {pair_id}: {missing}")
        pairs.append(pair)

    if not pairs:
        raise ValueError(f"No pairs found in {manifest}")
    return pairs


def heuristic_mathlib_style_score(code: str) -> float:
    """Small deterministic smoke-test baseline, not a reportable judge."""
    text = code.strip()
    lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("--")
    ]
    line_count = len(lines)

    score = 0.35
    if re.search(r"^\s*import\s+Mathlib\b", text, flags=re.MULTILINE):
        score += 0.05
    if re.search(r"\bsimpa\b", text):
        score += 0.22
    elif re.search(r"\bsimp\b", text):
        score += 0.16
    if re.search(r"\busing\b", text):
        score += 0.10
    if re.search(r"\b[A-Z][A-Za-z0-9_']*(?:\.[A-Za-z0-9_']+)+\b", text):
        score += 0.10
    if line_count <= 6:
        score += 0.16
    elif line_count <= 12:
        score += 0.08
    elif line_count > 30:
        score -= 0.12

    penalty_patterns = [
        (r"\bsorry\b|\badmit\b", 0.45),
        (r"\baxiom\b", 0.35),
        (r"\binduction\b", 0.10),
        (r"\bchange\b", 0.04),
        (r"\brepeat\b", 0.04),
    ]
    for pat, penalty in penalty_patterns:
        if re.search(pat, text):
            score -= penalty

    return _clip01(score)


def score_pairs_with_heuristic(
    pairs: Sequence[StylePair],
    repeats: int,
    judge_id: str,
) -> List[ScoreRecord]:
    records: List[ScoreRecord] = []
    for pair in pairs:
        for variant, path in (("bad", pair.bad_path), ("good", pair.good_path)):
            code = path.read_text(encoding="utf-8")
            score = heuristic_mathlib_style_score(code)
            for repeat_idx in range(repeats):
                records.append(
                    ScoreRecord(
                        pair_id=pair.pair_id,
                        variant=variant,
                        score=score,
                        judge_id=judge_id,
                        repeat_idx=repeat_idx,
                        source="heuristic_smoke",
                    )
                )
    return records


def _score_from_csv_row(row: dict, default_max_score: float) -> float:
    for key in ("score", "normalized_score"):
        value = row.get(key)
        if value not in (None, ""):
            return _clip01(float(value))

    raw = row.get("raw_score")
    if raw in (None, ""):
        raise ValueError("Score CSV row needs score, normalized_score, or raw_score")
    max_score = float(row.get("max_score") or default_max_score)
    if max_score <= 0:
        raise ValueError(f"max_score must be positive, got {max_score}")
    return _clip01(float(raw) / max_score)


def load_scores_csv(
    path: Path,
    default_judge_id: str,
    default_max_score: float,
) -> List[ScoreRecord]:
    score_path = path.expanduser().resolve()
    if not score_path.exists():
        raise FileNotFoundError(f"Scores CSV not found: {score_path}")

    records: List[ScoreRecord] = []
    with score_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"pair_id", "variant"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{score_path} is missing required columns: {sorted(missing)}")
        for row_idx, row in enumerate(reader, start=2):
            variant = str(row["variant"]).strip().lower()
            if variant not in {"bad", "good"}:
                raise ValueError(f"{score_path}:{row_idx} variant must be bad or good, got {variant!r}")
            records.append(
                ScoreRecord(
                    pair_id=str(row["pair_id"]).strip(),
                    variant=variant,
                    score=_score_from_csv_row(row, default_max_score),
                    judge_id=str(row.get("judge_id") or default_judge_id),
                    repeat_idx=int(row.get("repeat_idx") or 0),
                    source=str(row.get("source") or score_path.name),
                )
            )
    if not records:
        raise ValueError(f"No scores found in {score_path}")
    return records


def _mean(xs: Sequence[float]) -> float:
    return float(mean(xs)) if xs else float("nan")


def _portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _validate_score_records(
    pairs: Sequence[StylePair],
    records: Sequence[ScoreRecord],
    margin_target: float,
) -> None:
    if margin_target <= 0:
        raise ValueError("margin_target must be > 0")

    pair_ids = {pair.pair_id for pair in pairs}
    unknown_pair_ids = sorted({record.pair_id for record in records if record.pair_id not in pair_ids})
    if unknown_pair_ids:
        raise ValueError(f"Score records reference unknown pair_id(s): {unknown_pair_ids}")

    invalid_variants = sorted({record.variant for record in records if record.variant not in {"bad", "good"}})
    if invalid_variants:
        raise ValueError(f"Score records use invalid variant(s): {invalid_variants}")


def _pair_metric_row(
    pair: StylePair,
    bad_records: Sequence[ScoreRecord],
    good_records: Sequence[ScoreRecord],
    min_margin: float,
    margin_target: float,
) -> dict:
    bad_scores = [r.score for r in bad_records]
    good_scores = [r.score for r in good_records]
    bad_mean = _mean(bad_scores)
    good_mean = _mean(good_scores)
    margin = good_mean - bad_mean
    style_order_score = compute_p2_or_p3_ordering_auc([0, 1], [good_mean, bad_mean])

    return {
        "pair_id": pair.pair_id,
        "topic": pair.topic,
        "split": pair.split,
        "style_issue": pair.style_issue,
        "source": pair.source,
        "bad_path": _portable_path(pair.bad_path),
        "good_path": _portable_path(pair.good_path),
        "bad_score_mean": bad_mean,
        "good_score_mean": good_mean,
        "score_margin_good_minus_bad": margin,
        "style_order_score": style_order_score,
        "preference_tie_half": 1.0 if margin > 0 else 0.5 if margin == 0 else 0.0,
        "pass_at_min_margin": bool(margin >= min_margin),
        "margin_strength": _clip01(max(0.0, margin) / margin_target),
        "n_bad_scores": len(bad_scores),
        "n_good_scores": len(good_scores),
    }


def _summary_from_pair_rows(
    pairs: Sequence[StylePair],
    records: Sequence[ScoreRecord],
    pair_rows: Sequence[dict],
    skipped_pairs: Sequence[str],
    min_margin: float,
    margin_target: float,
    stability_tau: float,
    stability: float,
) -> dict:
    style_order = _mean([float(r["style_order_score"]) for r in pair_rows])
    margin_strength = _mean([float(r["margin_strength"]) for r in pair_rows])
    preference_tie_half = _mean([float(r["preference_tie_half"]) for r in pair_rows])
    win_at_margin = _mean([1.0 if r["pass_at_min_margin"] else 0.0 for r in pair_rows])
    mean_margin = _mean([float(r["score_margin_good_minus_bad"]) for r in pair_rows])
    mvp_score = 0.0 if not pair_rows else _clip01(
        0.70 * style_order + 0.20 * margin_strength + 0.10 * stability
    )

    return {
        "experiment": "16_mathlib_style_bench_mvp",
        "metric_version": "msb_mvp_v0",
        "n_manifest_pairs": len(pairs),
        "n_scored_pairs": len(pair_rows),
        "n_score_records": len(records),
        "skipped_pairs": list(skipped_pairs),
        "min_margin": min_margin,
        "margin_target": margin_target,
        "stability_tau": stability_tau,
        "style_order_score_mean": style_order,
        "preference_rate_tie_half": preference_tie_half,
        "win_rate_at_min_margin": win_at_margin,
        "mean_margin_good_minus_bad": mean_margin,
        "margin_strength_mean": margin_strength,
        "p4_stability": stability,
        "mathlib_style_bench_mvp_score": mvp_score,
    }


def aggregate_metrics(
    pairs: Sequence[StylePair],
    records: Sequence[ScoreRecord],
    min_margin: float,
    margin_target: float,
    stability_tau: float,
) -> Tuple[List[dict], dict]:
    _validate_score_records(pairs, records, margin_target)
    by_pair_variant: Dict[Tuple[str, str], List[ScoreRecord]] = defaultdict(list)
    for record in records:
        by_pair_variant[(record.pair_id, record.variant)].append(record)

    pair_rows: List[dict] = []
    repeat_scores_by_item: Dict[str, List[float]] = defaultdict(list)
    skipped_pairs: List[str] = []

    for record in records:
        repeat_scores_by_item[f"{record.pair_id}::{record.variant}"].append(record.score)

    for pair in pairs:
        bad_records = by_pair_variant.get((pair.pair_id, "bad"), [])
        good_records = by_pair_variant.get((pair.pair_id, "good"), [])
        if not bad_records or not good_records:
            skipped_pairs.append(pair.pair_id)
            continue

        pair_rows.append(
            _pair_metric_row(
                pair=pair,
                bad_records=bad_records,
                good_records=good_records,
                min_margin=min_margin,
                margin_target=margin_target,
            )
        )

    stability = compute_p4_stability(repeat_scores_by_item, tau=stability_tau)
    summary = _summary_from_pair_rows(
        pairs=pairs,
        records=records,
        pair_rows=pair_rows,
        skipped_pairs=skipped_pairs,
        min_margin=min_margin,
        margin_target=margin_target,
        stability_tau=stability_tau,
        stability=stability,
    )
    return pair_rows, summary


def write_score_records(path: Path, records: Sequence[ScoreRecord]) -> None:
    fieldnames = ["pair_id", "variant", "score", "judge_id", "repeat_idx", "source"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "pair_id": record.pair_id,
                    "variant": record.variant,
                    "score": f"{record.score:.10f}",
                    "judge_id": record.judge_id,
                    "repeat_idx": record.repeat_idx,
                    "source": record.source,
                }
            )


def write_dict_rows(path: Path, rows: Sequence[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _fmt_float(value: float) -> str:
    return "nan" if not math.isfinite(float(value)) else f"{float(value):.4f}"


def write_report(path: Path, pair_rows: Sequence[dict], summary: dict) -> None:
    lines: List[str] = []
    lines.append("# Mathlib Style Bench MVP Report")
    lines.append("**TLDR:** This report scores whether a style judge ranks the accepted mathlib-style Lean file above the intentionally worse Lean file for each pair.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- MSB-MVP score: `{_fmt_float(summary['mathlib_style_bench_mvp_score'])}`")
    lines.append(f"- Style order score: `{_fmt_float(summary['style_order_score_mean'])}`")
    lines.append(f"- Mean good-minus-bad margin: `{_fmt_float(summary['mean_margin_good_minus_bad'])}`")
    lines.append(f"- P4 stability: `{_fmt_float(summary['p4_stability'])}`")
    lines.append(f"- Scored pairs: `{summary['n_scored_pairs']}/{summary['n_manifest_pairs']}`")
    lines.append("")
    lines.append("## Pair Results")
    lines.append("")
    lines.append("| Pair | Topic | Bad | Good | Margin | Order | Pass |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    sorted_pair_rows = sorted(pair_rows, key=lambda row: float(row["score_margin_good_minus_bad"]))
    for row in sorted_pair_rows:
        lines.append(
            "| "
            f"`{row['pair_id']}` | {row['topic']} | "
            f"{float(row['bad_score_mean']):.3f} | {float(row['good_score_mean']):.3f} | "
            f"{float(row['score_margin_good_minus_bad']):+.3f} | "
            f"{float(row['style_order_score']):.1f} | "
            f"{'PASS' if row['pass_at_min_margin'] else 'FAIL'} |"
        )
    lines.append("")
    lines.append("## Metric")
    lines.append("")
    lines.append("`MSB-MVP = 0.70 * style_order_score + 0.20 * margin_strength + 0.10 * P4_stability`.")
    lines.append("The order term reuses `cert_judge.hsj_scoring.compute_p2_or_p3_ordering_auc` on a two-level style-defect ladder: good code has defect count 0, bad code has defect count 1.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Mathlib Style Bench MVP")
    parser.add_argument("--pairs-file", type=Path, default=DEFAULT_PAIRS_FILE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--scores-csv", type=Path, default=None,
                        help="Optional long-format CSV with pair_id,variant,score rows.")
    parser.add_argument("--scorer", choices=["heuristic"], default="heuristic",
                        help="Offline scorer used when --scores-csv is not provided.")
    parser.add_argument("--judge-id", default="heuristic_mathlib_style_v0")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-score", type=float, default=1.0,
                        help="Denominator for raw_score rows in --scores-csv.")
    parser.add_argument("--min-margin", type=float, default=0.05,
                        help="Minimum good-minus-bad score gap counted as a pair-level pass.")
    parser.add_argument("--margin-target", type=float, default=0.25,
                        help="Good-minus-bad margin that saturates margin_strength at 1.")
    parser.add_argument("--stability-tau", type=float, default=0.05,
                        help="Tau for cert_judge.hsj_scoring.compute_p4_stability.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats < 1:
        raise ValueError("--repeats must be >= 1")
    if args.margin_target <= 0:
        raise ValueError("--margin-target must be > 0")
    if args.stability_tau <= 0:
        raise ValueError("--stability-tau must be > 0")

    pairs = load_pairs(args.pairs_file)
    if args.scores_csv is not None:
        records = load_scores_csv(args.scores_csv, args.judge_id, args.max_score)
    elif args.scorer == "heuristic":
        records = score_pairs_with_heuristic(pairs, args.repeats, args.judge_id)
    else:
        raise ValueError(f"Unsupported scorer: {args.scorer}")

    pair_rows, summary = aggregate_metrics(
        pairs=pairs,
        records=records,
        min_margin=args.min_margin,
        margin_target=args.margin_target,
        stability_tau=args.stability_tau,
    )

    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_score_records(out_dir / "pair_scores.csv", records)
    write_dict_rows(out_dir / "pair_metrics.csv", pair_rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_report(out_dir / "REPORT.md", pair_rows, summary)

    print(f"Wrote Mathlib Style Bench MVP results to {out_dir}")
    print(f"MSB-MVP score: {_fmt_float(summary['mathlib_style_bench_mvp_score'])}")
    print(f"Style order score: {_fmt_float(summary['style_order_score_mean'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
