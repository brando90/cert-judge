#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr

REPO_ROOT = Path(__file__).resolve().parents[2]
EXP02_DIR = REPO_ROOT / "experiments" / "02_neurips_reviews"
import sys
sys.path.insert(0, str(EXP02_DIR))

from utils.judge_caller import judge

VERIBENCH_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench"
GENERATED_AGENTS_DIR = REPO_ROOT / "data" / "generated_agents"
DATA_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "data"

PAIRWISE_PROMPT = """You are an expert in Lean 4 formal verification.
Your task is comparative semantic judging.

Given:
- REFERENCE IMPLEMENTATION (gold semantic target)
- TWO generated candidate theorem/specs (A and B)

Decide which candidate is semantically closer to the reference guarantees.
Focus on semantic correctness/completeness only; ignore formatting, names, proof style.

Scoring:
Return score in [0.0, 1.0] interpreted as probability A is better than B.
- 1.0 = A clearly better than B
- 0.5 = tie / indistinguishable
- 0.0 = B clearly better than A

Use checklist reasoning internally:
1) Core guarantee coverage vs reference
2) Missing or weakened guarantees
3) Vacuity / wrong-target theorem penalties

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}
"""


@dataclass
class PairRow:
    gold_file: str
    candidate_file: str
    item_id: str


def _load_tsv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")
    df["gold_file"] = df["gold_file"].astype(str)
    df["candidate_file"] = df["candidate_file"].astype(str)
    df["item_id"] = df["gold_file"] + "::" + df["candidate_file"]
    df["human_score_0_5"] = pd.to_numeric(df["human_score_0_5"], errors="coerce")
    return df.dropna(subset=["human_score_0_5"])


def _union_rows(pass_paths: List[Path]) -> pd.DataFrame:
    frames = [_load_tsv(p)[["gold_file", "candidate_file", "item_id"]] for p in pass_paths]
    return pd.concat(frames, ignore_index=True).drop_duplicates().reset_index(drop=True)


def _build_gold_index(root: Path) -> Dict[str, List[Path]]:
    idx: Dict[str, List[Path]] = {}
    for p in root.rglob("*.lean"):
        idx.setdefault(p.name, []).append(p)
    return idx


def _resolve_gold(gold_file: str, idx: Dict[str, List[Path]]) -> Path:
    matches = idx.get(gold_file, [])
    if not matches:
        # Handle known historical filename mismatches in the human label TSVs.
        aliases = []
        if gold_file == "0_unsafeMultiply_safe.lean":
            aliases.append("1_unsafeMultiply_safe.lean")
            aliases.append("1_unsafeMultiply.lean")
        if gold_file.endswith("_safe.lean"):
            aliases.append(gold_file.replace("_safe.lean", ".lean"))

        for alias in aliases:
            am = idx.get(alias, [])
            if am:
                matches = am
                break

    if not matches:
        raise FileNotFoundError(f"Missing gold: {gold_file}")
    matches = sorted(matches, key=lambda p: (len(p.parts), str(p)))
    return matches[0]


def _pair_blob(a_name: str, a_text: str, b_name: str, b_text: str) -> str:
    return (
        f"CANDIDATE A ({a_name}):\n```lean\n{a_text}\n```\n\n"
        f"CANDIDATE B ({b_name}):\n```lean\n{b_text}\n```\n"
    )


def _clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def run(args: argparse.Namespace) -> None:
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    pass1_path = DATA_DIR / "ethan_human_scores_20260425.tsv"
    pass2_path = DATA_DIR / "ethan_human_scores_ORIGINAL.tsv"
    avg_path = DATA_DIR / "ethan_human_scores_avg_two_passes_20260425.tsv"

    union_df = _union_rows([pass1_path, pass2_path, avg_path])

    # Keep tasks with >=2 candidates; expected is 3 each
    grouped = union_df.groupby("gold_file")

    gold_idx = _build_gold_index(VERIBENCH_ROOT)

    pairwise_rows: List[dict] = []
    item_rows: List[dict] = []

    for gold_file, gdf in grouped:
        cands = sorted(gdf["candidate_file"].unique().tolist())
        if len(cands) < 2:
            continue

        gold_path = _resolve_gold(gold_file, gold_idx)
        gold_text = gold_path.read_text(encoding="utf-8")

        cand_text = {}
        for c in cands:
            p = GENERATED_AGENTS_DIR / c
            if not p.exists():
                continue
            cand_text[c] = p.read_text(encoding="utf-8")
        cands = [c for c in cands if c in cand_text]
        if len(cands) < 2:
            continue

        # Build symmetric pairwise probabilities p(i > j)
        pmat: Dict[Tuple[str, str], float] = {}

        for i in range(len(cands)):
            for j in range(i + 1, len(cands)):
                a = cands[i]
                b = cands[j]

                blob_ab = _pair_blob(a, cand_text[a], b, cand_text[b])
                rab = judge(
                    generated_theorem=blob_ab,
                    reference_impl=gold_text,
                    model=args.model,
                    n_repeats=args.repeats,
                    prompt_template=PAIRWISE_PROMPT,
                    cache_namespace=args.cache_namespace,
                )
                p_ab = _clip01(float(rab["score"]))

                blob_ba = _pair_blob(b, cand_text[b], a, cand_text[a])
                rba = judge(
                    generated_theorem=blob_ba,
                    reference_impl=gold_text,
                    model=args.model,
                    n_repeats=args.repeats,
                    prompt_template=PAIRWISE_PROMPT,
                    cache_namespace=args.cache_namespace,
                )
                p_ba = _clip01(float(rba["score"]))

                # Symmetrize
                p = _clip01(0.5 * (p_ab + (1.0 - p_ba)))
                pmat[(a, b)] = p
                pmat[(b, a)] = 1.0 - p

                pairwise_rows.append({
                    "gold_file": gold_file,
                    "cand_a": a,
                    "cand_b": b,
                    "p_a_better_b_ab": p_ab,
                    "p_a_better_b_from_reverse": 1.0 - p_ba,
                    "p_a_better_b_sym": p,
                    "reasoning_ab": rab.get("reasoning", ""),
                    "reasoning_ba": rba.get("reasoning", ""),
                })

        # Per-candidate strength = average pairwise win probability
        for a in cands:
            others = [b for b in cands if b != a]
            if not others:
                continue
            s = float(np.mean([pmat[(a, b)] for b in others]))
            item_id = f"{gold_file}::{a}"
            item_rows.append({
                "item_id": item_id,
                "gold_file": gold_file,
                "candidate_file": a,
                "judge_model": args.model,
                "judge_prompt_name": "P4_CHECKLIST_PAIRWISE_BT_V1",
                "score": s,
            })

    pairwise_df = pd.DataFrame(pairwise_rows)
    item_df = pd.DataFrame(item_rows)

    pairwise_path = out_dir / "pairwise_rows.csv"
    scores_path = out_dir / "pairwise_item_scores.csv"
    pairwise_df.to_csv(pairwise_path, index=False)
    item_df.to_csv(scores_path, index=False)

    # Correlations vs Ethan passes
    pass_map = {
        "pass1_20260425": _load_tsv(pass1_path),
        "pass2_original": _load_tsv(pass2_path),
        "avg_two_passes_20260425": _load_tsv(avg_path),
    }

    corr_rows = []
    for name, hdf in pass_map.items():
        m = item_df.merge(hdf[["item_id", "human_score_0_5"]], on="item_id", how="inner")
        x = m["score"].to_numpy()
        y = m["human_score_0_5"].to_numpy()
        if len(m) < 3:
            continue
        pr = pearsonr(x, y)
        sr = spearmanr(x, y)
        kr = kendalltau(x, y)
        corr_rows.append({
            "pass": name,
            "n_overlap": len(m),
            "pearson_r": pr.statistic,
            "pearson_p": pr.pvalue,
            "spearman_rho": sr.statistic,
            "spearman_p": sr.pvalue,
            "kendall_tau": kr.statistic,
            "kendall_p": kr.pvalue,
        })

    corr_df = pd.DataFrame(corr_rows)
    corr_path = out_dir / "corr_all_metrics_all_passes.csv"
    corr_df.to_csv(corr_path, index=False)

    summary = {
        "scores_path": str(scores_path),
        "pairwise_path": str(pairwise_path),
        "corr_path": str(corr_path),
        "n_item_scores": int(len(item_df)),
        "n_pair_rows": int(len(pairwise_df)),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(corr_df.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    print("\nWrote:")
    print(scores_path)
    print(pairwise_path)
    print(corr_path)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gpt-5.3-codex")
    p.add_argument("--repeats", type=int, default=9)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_p4_pairwise_bt_v1",
    )
    p.add_argument("--cache-namespace", default="exp16_p4_pairwise_bt_v1")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
