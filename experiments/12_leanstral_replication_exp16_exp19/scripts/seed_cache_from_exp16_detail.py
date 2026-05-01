#!/usr/bin/env python3
"""Rebuild an Exp16 judge cache from completed detail rows.

Exp12 had successful Leanstral/GPT judge outputs in the canonical Exp04 result
directory, but some racing runs died before writing their own Exp12 summaries.
This script turns those completed repeat scores back into the cache entries that
`exp16_multi_judge_human_sets.py` expects for a specified cache tag.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import statistics
import sys
from pathlib import Path
from typing import Dict, Tuple


REPO = Path(__file__).resolve().parents[3]
EXP16_PATH = REPO / "experiments/04_veribench_validation/exp16_multi_judge_human_sets.py"


def _load_exp16_module():
    spec = importlib.util.spec_from_file_location("exp16_multi_judge_human_sets", EXP16_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {EXP16_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_item_text_map(exp16) -> Dict[Tuple[str, str], Tuple[str, str]]:
    pass1 = exp16._load_tsv_scores(exp16.DEFAULT_DATA_DIR / "ethan_human_scores_20260425.tsv")
    pass2 = exp16._load_tsv_scores(exp16.DEFAULT_DATA_DIR / "ethan_human_scores_ORIGINAL.tsv")
    avg = exp16._load_tsv_scores(exp16.DEFAULT_DATA_DIR / "ethan_human_scores_avg_two_passes_20260425.tsv")
    union_keys = sorted(set(pass1) | set(pass2) | set(avg))

    gold_idx = exp16._build_gold_index(exp16.DEFAULT_VERIBENCH_ROOT)
    text_rows = {}
    for gold_file, candidate_file in union_keys:
        try:
            gold_path = exp16._resolve_gold_path(gold_file, gold_idx)
        except FileNotFoundError:
            continue
        cand_path = exp16.DEFAULT_GENERATED_AGENTS_DIR / candidate_file
        if not cand_path.exists():
            continue
        gold = exp16._extract_last_theorem_block(gold_path.read_text(encoding="utf-8", errors="ignore"))
        cand = cand_path.read_text(encoding="utf-8", errors="ignore")
        text_rows[(gold_file, candidate_file)] = {
            "problem_id": Path(gold_file).stem,
            "gold": gold,
            "candidate": cand,
        }

    item_text: Dict[Tuple[str, str], Tuple[str, str]] = {}
    unique_problems = {}
    for (gold_file, candidate_file), row in text_rows.items():
        item_text[("human_eval_union", f"{gold_file}::{candidate_file}")] = (row["gold"], row["candidate"])
        unique_problems.setdefault(row["problem_id"], row["gold"])

    for problem_id, gold in unique_problems.items():
        for variant in exp16.generate_variants(gold):
            item_text[("property_identity", f"{problem_id}::{variant['variant_type']}")] = (
                gold,
                variant["code"],
            )
        for level, candidate in enumerate(exp16.build_bug_ladder(gold)):
            item_text[("property_bug", f"{problem_id}::L{level}")] = (gold, candidate)

    return item_text


def _cache_key(exp16, judge_id: str, cache_tag: str, generated: str, reference: str) -> str | None:
    if "|" not in judge_id:
        return None
    model, prompt_name = judge_id.split("|", 1)
    if prompt_name in exp16.PROMPT_VARIANTS:
        namespace = f"exp16:{judge_id}:{cache_tag}"
        prompt_template = exp16.PROMPT_VARIANTS[prompt_name]
    elif prompt_name in exp16.BAD_PROMPTS:
        namespace = f"exp16_bad:{judge_id}:{cache_tag}"
        prompt_template = exp16.BAD_PROMPTS[prompt_name]
    else:
        return None
    return (
        f"{namespace}|{model}|{_sha256(prompt_template)}|"
        f"{_sha256(generated)}|{_sha256(reference)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--detail-rows",
        type=Path,
        default=REPO / "experiments/04_veribench_validation/results_exp16_leanstral_r3_median/detail_rows.csv",
    )
    parser.add_argument("--cache-tag", default="leanstral_full_r3_median")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    exp16 = _load_exp16_module()
    item_text = _build_item_text_map(exp16)

    cache = {}
    missed = []
    with args.detail_rows.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["row_type"], row["item_key"])
            if key not in item_text:
                missed.append(key)
                continue
            reference, generated = item_text[key]
            cache_key = _cache_key(exp16, row["judge_id"], args.cache_tag, generated, reference)
            if cache_key is None:
                continue
            scores = [float(x) for x in json.loads(row["repeat_scores"])]
            mean = float(statistics.mean(scores))
            std = float(statistics.stdev(scores)) if len(scores) > 1 else 0.0
            model = row["judge_id"].split("|", 1)[0]
            cache[cache_key] = {
                "score": mean,
                "mean": mean,
                "std": std,
                "scores": scores,
                "reasoning": "reconstructed from completed exp16 detail_rows.csv",
                "model": model,
            }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print(f"wrote {len(cache)} cache entries to {args.out}")
    if missed:
        print(f"warning: skipped {len(missed)} rows with missing source text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
