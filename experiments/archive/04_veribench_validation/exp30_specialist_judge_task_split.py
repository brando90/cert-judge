#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
EXP02_DIR = REPO_ROOT / "experiments" / "02_neurips_reviews"
sys.path.insert(0, str(EXP02_DIR))

from utils.judge_caller import judge


DEFAULT_HUMAN_TSV = REPO_ROOT / "experiments" / "04_veribench_validation" / "data" / "ethan_human_scores_avg_two_passes_20260425.tsv"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp30_specialist_judge_task_split"
DEFAULT_VERIBENCH_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench"
DEFAULT_GENERATED_AGENTS_DIR = REPO_ROOT / "data" / "generated_agents"


BASE_PROMPT = """You are a specialist autorater for the VeriBench theorem-coverage task.

Goal:
Predict the expert human score on a 0-5 scale for how well a GENERATED THEOREM/SPEC
captures the semantic guarantees of a REFERENCE IMPLEMENTATION/SPEC.

The examples below are historical human ratings from the same benchmark. Use them to
calibrate both what matters semantically and how harshly to score.

Important:
- Match human semantic judgment, not text similarity.
- Ignore formatting, theorem order, comments, and variable names.
- Penalize missing core guarantees heavily.
- Penalize vacuous truth, impossible assumptions, weakened usefulness, or wrong target theorems heavily.
- If uncertain, choose the lower score.

Few-shot calibration examples:
{specialist_examples}

Now evaluate the target pair.

REFERENCE IMPLEMENTATION/SPEC:
{reference_impl}

GENERATED THEOREM/SPEC:
{generated_theorem}

Return JSON only:
{{"score": <float from 0.0 to 1.0>, "reasoning": "<one concise sentence>"}}"""


@dataclass(frozen=True)
class LabeledPair:
    gold_file: str
    candidate_file: str
    human_score_0_5: float
    reference_text: str
    candidate_text: str

    @property
    def task_id(self) -> str:
        return Path(self.gold_file).stem

    @property
    def item_key(self) -> str:
        return f"{self.gold_file}::{self.candidate_file}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP30: benchmark-specialized judge with task-split ICL examples")
    p.add_argument("--human-tsv", type=Path, default=DEFAULT_HUMAN_TSV)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--veribench-root", type=Path, default=DEFAULT_VERIBENCH_ROOT)
    p.add_argument("--generated-agents-dir", type=Path, default=DEFAULT_GENERATED_AGENTS_DIR)
    p.add_argument("--model", type=str, default="gpt-5.3-codex")
    p.add_argument("--judge-repeats", type=int, default=3)
    p.add_argument("--n-shots", type=int, default=12)
    p.add_argument("--train-frac", type=float, default=0.6)
    p.add_argument("--val-frac", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cache-tag", type=str, default="exp30_specialist_v1")
    p.add_argument("--limit-test-items", type=int, default=0)
    p.add_argument(
        "--selection-strategy",
        choices=["stratified_score", "random"],
        default="stratified_score",
    )
    return p.parse_args()


def load_human_rows(path: Path) -> Dict[Tuple[str, str], float]:
    rows: Dict[Tuple[str, str], List[float]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gold = str(row.get("gold_file", "")).strip()
            cand = str(row.get("candidate_file", "")).strip()
            raw = str(row.get("human_score_0_5", "")).strip()
            if not gold or not cand or not raw:
                continue
            try:
                score = float(raw)
            except ValueError:
                continue
            rows.setdefault((gold, cand), []).append(score)
    return {k: float(sum(v) / len(v)) for k, v in rows.items()}


def build_gold_index(veribench_root: Path) -> Dict[str, List[Path]]:
    idx: Dict[str, List[Path]] = {}
    for path in veribench_root.rglob("*.lean"):
        idx.setdefault(path.name, []).append(path)
    return idx


def resolve_gold_path(gold_file: str, gold_idx: Dict[str, List[Path]]) -> Path:
    matches = gold_idx.get(gold_file, [])
    if not matches:
        raise FileNotFoundError(gold_file)
    return sorted(matches, key=lambda p: (len(p.parts), str(p)))[0]


def load_pairs(args: argparse.Namespace) -> List[LabeledPair]:
    human = load_human_rows(args.human_tsv)
    gold_idx = build_gold_index(args.veribench_root)
    out: List[LabeledPair] = []
    for (gold_file, candidate_file), score in sorted(human.items()):
        gold_path = resolve_gold_path(gold_file, gold_idx)
        cand_path = args.generated_agents_dir / candidate_file
        if not cand_path.exists():
            continue
        out.append(
            LabeledPair(
                gold_file=gold_file,
                candidate_file=candidate_file,
                human_score_0_5=score,
                reference_text=gold_path.read_text(encoding="utf-8", errors="ignore"),
                candidate_text=cand_path.read_text(encoding="utf-8", errors="ignore"),
            )
        )
    if not out:
        raise ValueError("No labeled pairs loaded")
    return out


def split_tasks(task_ids: Sequence[str], train_frac: float, val_frac: float, seed: int) -> Dict[str, List[str]]:
    unique = sorted(set(task_ids))
    rng = random.Random(seed)
    rng.shuffle(unique)
    n = len(unique)
    n_train = max(1, int(round(n * train_frac)))
    n_val = max(1, int(round(n * val_frac)))
    if n_train + n_val >= n:
        n_train = max(1, n - 2)
        n_val = 1
    train = unique[:n_train]
    val = unique[n_train:n_train + n_val]
    test = unique[n_train + n_val:]
    if not test:
        test = [val.pop()]
    return {"train": train, "val": val, "test": test}


def select_shots(rows: Sequence[LabeledPair], n_shots: int, strategy: str, seed: int) -> List[LabeledPair]:
    rng = random.Random(seed)
    pool = list(rows)
    if len(pool) <= n_shots:
        return sorted(pool, key=lambda r: (r.human_score_0_5, r.item_key))

    if strategy == "random":
        rng.shuffle(pool)
        return sorted(pool[:n_shots], key=lambda r: (r.human_score_0_5, r.item_key))

    # Stratify across the 0-5 rating scale so the prompt sees both weak and strong examples.
    by_bucket: Dict[int, List[LabeledPair]] = {}
    for row in pool:
        bucket = int(round(row.human_score_0_5))
        by_bucket.setdefault(bucket, []).append(row)
    for vals in by_bucket.values():
        rng.shuffle(vals)
    buckets = sorted(by_bucket)
    selected: List[LabeledPair] = []
    while len(selected) < n_shots and any(by_bucket.values()):
        for bucket in buckets:
            if by_bucket[bucket]:
                selected.append(by_bucket[bucket].pop())
                if len(selected) >= n_shots:
                    break
    return sorted(selected, key=lambda r: (r.human_score_0_5, r.item_key))


def build_specialist_examples(rows: Sequence[LabeledPair]) -> str:
    blocks: List[str] = []
    for i, row in enumerate(rows, start=1):
        blocks.append(
            f"""Example {i}
REFERENCE IMPLEMENTATION/SPEC:
{row.reference_text}

GENERATED THEOREM/SPEC:
{row.candidate_text}

HUMAN SCORE (0-5): {row.human_score_0_5:.1f}
HUMAN SCORE (0-1 normalized): {row.human_score_0_5 / 5.0:.3f}"""
        )
    return "\n\n".join(blocks)


def safe_corr(x: Sequence[float], y: Sequence[float]) -> Dict[str, float]:
    if len(x) < 2:
        return {
            "pearson_r": float("nan"),
            "pearson_p": float("nan"),
            "spearman_r": float("nan"),
            "spearman_p": float("nan"),
            "kendall_tau": float("nan"),
            "kendall_p": float("nan"),
        }
    pr, pp = pearsonr(x, y)
    sr, sp = spearmanr(x, y)
    kt = kendalltau(x, y)
    return {
        "pearson_r": float(pr),
        "pearson_p": float(pp),
        "spearman_r": float(sr),
        "spearman_p": float(sp),
        "kendall_tau": float(kt.statistic),
        "kendall_p": float(kt.pvalue),
    }


def score_row(row: LabeledPair, args: argparse.Namespace, specialist_examples: str, split_name: str) -> Tuple[float, dict]:
    prompt = BASE_PROMPT.format(
        specialist_examples=specialist_examples,
        reference_impl="{reference_impl}",
        generated_theorem="{generated_theorem}",
    )
    cache_namespace = f"{args.cache_tag}:{split_name}:shots{args.n_shots}:{args.selection_strategy}"
    result = judge(
        generated_theorem=row.candidate_text,
        reference_impl=row.reference_text,
        model=args.model,
        n_repeats=args.judge_repeats,
        prompt_template=prompt,
        cache_namespace=cache_namespace,
    )
    reps = [float(x) for x in result.get("scores", [])]
    if not reps:
        reps = [float(result.get("mean", 0.5))]
    return float(np.mean(reps)), result


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_pairs(args)
    split = split_tasks([r.task_id for r in rows], args.train_frac, args.val_frac, args.seed)

    by_split: Dict[str, List[LabeledPair]] = {
        name: [r for r in rows if r.task_id in tasks] for name, tasks in split.items()
    }
    shots = select_shots(by_split["train"], args.n_shots, args.selection_strategy, args.seed)
    specialist_examples = build_specialist_examples(shots)

    detail_rows: List[dict] = []
    summary: Dict[str, dict] = {
        "experiment": "exp30_specialist_judge_task_split",
        "model": args.model,
        "human_tsv": str(args.human_tsv),
        "n_rows_total": len(rows),
        "n_tasks_total": len({r.task_id for r in rows}),
        "split": split,
        "n_shots": args.n_shots,
        "selection_strategy": args.selection_strategy,
        "judge_repeats": args.judge_repeats,
        "shots": [
            {
                "item_key": r.item_key,
                "task_id": r.task_id,
                "human_score_0_5": r.human_score_0_5,
            }
            for r in shots
        ],
        "results": {},
    }

    for split_name in ["val", "test"]:
        eval_rows = list(by_split[split_name])
        if args.limit_test_items > 0 and split_name == "test":
            eval_rows = eval_rows[: args.limit_test_items]
        human_vals: List[float] = []
        judge_vals: List[float] = []
        for row in eval_rows:
            score, raw = score_row(row, args, specialist_examples, split_name)
            judge_vals.append(score)
            human_vals.append(row.human_score_0_5 / 5.0)
            detail_rows.append(
                {
                    "split": split_name,
                    "gold_file": row.gold_file,
                    "candidate_file": row.candidate_file,
                    "task_id": row.task_id,
                    "human_score_0_5": row.human_score_0_5,
                    "human_score_norm": row.human_score_0_5 / 5.0,
                    "judge_score": score,
                    "judge_mean_raw": float(raw.get("mean", score)),
                    "judge_std_raw": float(raw.get("std", 0.0)),
                    "repeat_scores": json.dumps(raw.get("scores", [])),
                    "cached": bool(raw.get("cached", False)),
                    "reasoning": str(raw.get("reasoning", "")),
                }
            )
        corr = safe_corr(judge_vals, human_vals)
        mae = float(np.mean([abs(a - b) for a, b in zip(judge_vals, human_vals)])) if judge_vals else float("nan")
        summary["results"][split_name] = {
            "n_rows": len(eval_rows),
            "n_tasks": len({r.task_id for r in eval_rows}),
            "mae": mae,
            **corr,
        }

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if detail_rows:
        with (args.out_dir / "detail_rows.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(detail_rows[0].keys()))
            w.writeheader()
            w.writerows(detail_rows)
    (args.out_dir / "specialist_examples.txt").write_text(specialist_examples, encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
