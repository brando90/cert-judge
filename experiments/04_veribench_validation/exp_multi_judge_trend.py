#!/usr/bin/env python3
"""
Multi-judge trend experiment: certification quality vs human alignment.

For each judge config (4-6 recommended), this script computes:
1) Human alignment on fixed human-labeled rows (Spearman with bootstrap CI)
2) Certification-style property metrics on the same problem set
   - identity_mean (syntactic invariance via variants)
   - bug_spearman_r (bug-ladder monotonic ranking)
   - bug_weak_mono_pct (per-file weak monotonicity)
   - flip_rate at threshold t across repeat-level decisions
3) Composite certification index (predefined formula)

Then across judges it computes the trend:
- Spearman(cert_index, human_spearman)
- Pearson(cert_index, human_spearman)
- Kendall(cert_index, human_spearman)
with bootstrap CI and permutation p-values.

Outputs:
- results_multi_judge_trend/judge_rows.csv
- results_multi_judge_trend/trend_summary.json
- results_multi_judge_trend/detail_rows.csv
- results_multi_judge_trend/fig_cert_vs_human_scatter.png
- results_multi_judge_trend/fig_human_corr_bars.png
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
EXP02_DIR = REPO_ROOT / "experiments" / "02_reviewer_response_neurips_math_ai_2026"
sys.path.insert(0, str(EXP02_DIR))

from utils.judge_caller import judge
from utils.metrics import levenshtein_normalized, spearman_r, weak_monotonicity_pct
from utils.sensitivity_sweep import PROMPT_VARIANTS
from utils.variant_generator import generate_variants
from utils.veribench_variance_utils import build_bug_ladder


DEFAULT_RESULTS_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_multi_judge_trend"


@dataclass(frozen=True)
class JudgeSpec:
    judge_id: str
    kind: str  # llm | editdist | random
    model: str
    prompt_name: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Trend: certification score vs human correlation across judges")
    p.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--judge-repeats", type=int, default=3)
    p.add_argument("--threshold", type=float, default=0.85)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--bootstrap-iters", type=int, default=5000)
    p.add_argument("--perm-iters", type=int, default=10000)
    p.add_argument(
        "--judges",
        type=str,
        default=(
            "llm:gpt-5.3-codex:P8_STRICT_B,"
            "llm:gpt-5.3-codex:P4_CHECKLIST,"
            "llm:gpt-5.3-codex:P1_BASELINE,"
            "llm:gpt-4o-mini:P8_STRICT_B,"
            "editdist:na:na,"
            "random:na:na"
        ),
        help=(
            "Comma-separated judge specs. Formats: "
            "llm:<model>:<prompt_name> | editdist:na:na | random:na:na"
        ),
    )
    return p.parse_args()


def _parse_judges(raw: str) -> List[JudgeSpec]:
    judges: List[JudgeSpec] = []
    for token in [t.strip() for t in raw.split(",") if t.strip()]:
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError(f"Bad judge spec: {token}")
        kind, model, prompt_name = parts
        kind = kind.lower().strip()
        model = model.strip()
        prompt_name = prompt_name.strip()

        if kind == "llm":
            if prompt_name not in PROMPT_VARIANTS:
                raise ValueError(f"Unknown prompt name in judge spec: {prompt_name}")
            judge_id = f"{model}|{prompt_name}"
        elif kind in {"editdist", "random"}:
            # Allow named baseline variants via model token, e.g. random:r1:na
            suffix = "" if model in {"", "na"} else f"_{model}"
            judge_id = f"{kind}{suffix}"
            model = "na"
            prompt_name = "na"
        else:
            raise ValueError(f"Unknown judge kind: {kind}")

        judges.append(JudgeSpec(judge_id=judge_id, kind=kind, model=model, prompt_name=prompt_name))

    # Ensure unique ids
    seen = set()
    uniq: List[JudgeSpec] = []
    for j in judges:
        if j.judge_id in seen:
            continue
        seen.add(j.judge_id)
        uniq.append(j)
    if len(uniq) < 4:
        raise ValueError("Provide at least 4 unique judges for trend analysis")
    return uniq


def _read_human_rows(results_dir: Path) -> List[dict]:
    path = results_dir / "human_judgments.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")

    rows: List[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            split = str(r["split"]).strip()
            problem = str(r["problem_id"]).strip()
            agent = str(r["agent"]).strip()
            human_mean = float(r["human_mean"])
            rows.append(
                {
                    "split": split,
                    "problem_id": problem,
                    "agent": agent,
                    "human_mean": human_mean,
                    "human_norm": (human_mean - 1.0) / 4.0,
                    "key": f"{split}::{problem}::{agent}",
                }
            )
    return rows


def _load_texts_for_rows(results_dir: Path, human_rows: List[dict]) -> Dict[str, dict]:
    root = results_dir / "veribench"
    out: Dict[str, dict] = {}
    for r in human_rows:
        split = r["split"]
        problem = r["problem_id"]
        agent = r["agent"]

        d = root / split / problem
        gold_path = d / "gold.lean"
        cand_path = d / f"agent_{agent}.lean"
        if not gold_path.exists() or not cand_path.exists():
            raise FileNotFoundError(f"Missing staged files for {r['key']} at {d}")

        out[r["key"]] = {
            "split": split,
            "problem_id": problem,
            "agent": agent,
            "human_mean": r["human_mean"],
            "human_norm": r["human_norm"],
            "gold": gold_path.read_text(encoding="utf-8", errors="ignore"),
            "candidate": cand_path.read_text(encoding="utf-8", errors="ignore"),
        }
    return out


def _det_random_score(judge_id: str, gold: str, cand: str, seed: int) -> float:
    h = hashlib.sha256((judge_id + str(seed) + gold[:200] + cand[:200]).encode("utf-8")).hexdigest()
    x = int(h[:12], 16) / float(16**12 - 1)
    return float(x)


def _score_once(spec: JudgeSpec, gold: str, cand: str, repeats: int, seed: int) -> dict:
    if spec.kind == "llm":
        prompt = PROMPT_VARIANTS[spec.prompt_name]
        return judge(
            generated_theorem=cand,
            reference_impl=gold,
            model=spec.model,
            n_repeats=repeats,
            prompt_template=prompt,
            cache_namespace=f"exp14_trend:{spec.judge_id}",
        )

    if spec.kind == "editdist":
        score = 1.0 - levenshtein_normalized(gold, cand)
        score = max(0.0, min(1.0, float(score)))
        return {"mean": score, "std": 0.0, "scores": [score] * repeats, "cached": False, "reasoning": "edit-distance baseline"}

    if spec.kind == "random":
        score = _det_random_score(spec.judge_id, gold, cand, seed=seed)
        return {"mean": score, "std": 0.0, "scores": [score] * repeats, "cached": False, "reasoning": "deterministic random baseline"}

    raise ValueError(spec.kind)


def _bootstrap_ci_stat(x: Sequence[float], y: Sequence[float], stat_fn, n_boot: int, seed: int) -> Tuple[float, float]:
    if len(x) < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    vals: List[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        try:
            v = float(stat_fn(x[idx], y[idx]))
        except Exception:
            continue
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    vals = np.sort(np.asarray(vals))
    lo = float(vals[int(0.025 * (len(vals) - 1))])
    hi = float(vals[int(0.975 * (len(vals) - 1))])
    return (lo, hi)


def _perm_pvalue_corr(x: Sequence[float], y: Sequence[float], stat_fn, n_perm: int, seed: int) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3:
        return float("nan")
    obs = abs(float(stat_fn(x, y)))
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        yp = np.array(y, copy=True)
        rng.shuffle(yp)
        s = abs(float(stat_fn(x, yp)))
        if s >= obs:
            count += 1
    return (count + 1) / (n_perm + 1)


def _spearman_only(x: np.ndarray, y: np.ndarray) -> float:
    r, _ = spearman_r(x.tolist(), y.tolist())
    return float(r)


def _pearson_only(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _kendall_only(x: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import kendalltau

    return float(kendalltau(x, y).statistic)


def _compute_cert_index(identity_mean: float, bug_spearman_r: float, bug_weak_mono_pct: float, flip_rate: float) -> float:
    # Predefined (not tuned on human outcomes):
    # identity high good; bug_spearman more negative good; weak mono high good; flip low good.
    mono_rank = max(0.0, min(1.0, (-bug_spearman_r + 1.0) / 2.0))
    weak = max(0.0, min(1.0, bug_weak_mono_pct / 100.0))
    flip_stability = max(0.0, min(1.0, 1.0 - flip_rate))
    ident = max(0.0, min(1.0, identity_mean))
    # weighted arithmetic mean
    return float(0.30 * ident + 0.30 * mono_rank + 0.25 * weak + 0.15 * flip_stability)


def _compute_cert_index_v2(
    identity_mean: float,
    bug_spearman_r: float,
    bug_weak_mono_pct: float,
    flip_rate: float,
    anti_string_score: float,
    subtle_bug_sensitivity: float,
) -> float:
    """
    v2 index adds explicit anti-string behavior and subtle semantic sensitivity.
    This is intended to penalize lexical baselines (e.g., pure edit distance).
    """
    mono_rank = max(0.0, min(1.0, (-bug_spearman_r + 1.0) / 2.0))
    weak = max(0.0, min(1.0, bug_weak_mono_pct / 100.0))
    flip_stability = max(0.0, min(1.0, 1.0 - flip_rate))
    ident = max(0.0, min(1.0, identity_mean))
    anti_str = max(0.0, min(1.0, anti_string_score))
    subtle = max(0.0, min(1.0, subtle_bug_sensitivity))
    return float(
        0.20 * ident
        + 0.20 * mono_rank
        + 0.15 * weak
        + 0.10 * flip_stability
        + 0.20 * anti_str
        + 0.15 * subtle
    )


def _make_plots(judge_rows: List[dict], trend: dict, out_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)

    # Scatter cert index v2 vs human spearman
    xs = [r["cert_index_v2"] for r in judge_rows]
    ys = [r["human_spearman_r"] for r in judge_rows]
    ylos = [r["human_spearman_ci_lo"] for r in judge_rows]
    yhis = [r["human_spearman_ci_hi"] for r in judge_rows]

    fig, ax = plt.subplots(figsize=(8.0, 5.6))
    ax.scatter(xs, ys, s=70)

    for i, r in enumerate(judge_rows):
        yerr_low = ys[i] - ylos[i] if math.isfinite(ylos[i]) else 0.0
        yerr_hi = yhis[i] - ys[i] if math.isfinite(yhis[i]) else 0.0
        ax.errorbar(xs[i], ys[i], yerr=[[yerr_low], [yerr_hi]], fmt="none", alpha=0.6)
        ax.annotate(r["judge_id"], (xs[i], ys[i]), xytext=(4, 4), textcoords="offset points", fontsize=8)

    if len(xs) >= 2:
        z = np.polyfit(xs, ys, 1)
        xline = np.linspace(min(xs), max(xs), 100)
        yline = z[0] * xline + z[1]
        ax.plot(xline, yline, "r--", linewidth=1.5)

    ax.set_xlabel("Certification Index (v2)")
    ax.set_ylabel("Human Correlation (Spearman)")
    ax.set_title(
        "Certification Quality vs Human Alignment (v2)\n"
        f"Spearman={trend['spearman_r']:.3f} (p_perm={trend['spearman_perm_p']:.4f})"
    )
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_cert_vs_human_scatter.png", dpi=180)
    plt.close(fig)

    # Bar plot human corr by judge
    labels = [r["judge_id"] for r in judge_rows]
    vals = [r["human_spearman_r"] for r in judge_rows]
    lo = [r["human_spearman_ci_lo"] for r in judge_rows]
    hi = [r["human_spearman_ci_hi"] for r in judge_rows]

    fig, ax = plt.subplots(figsize=(max(9, 0.9 * len(labels)), 5.2))
    x = np.arange(len(labels))
    bars = ax.bar(x, vals)
    yerr_low = [v - l if math.isfinite(l) else 0.0 for v, l in zip(vals, lo)]
    yerr_hi = [h - v if math.isfinite(h) else 0.0 for h, v in zip(hi, vals)]
    ax.errorbar(x, vals, yerr=[yerr_low, yerr_hi], fmt="none", ecolor="black", capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Human Spearman r")
    ax.set_title("Human Alignment by Judge (95% bootstrap CI)")
    ax.grid(axis="y", alpha=0.25)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_human_corr_bars.png", dpi=180)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)

    judges = _parse_judges(args.judges)
    human_rows = _read_human_rows(args.results_dir)
    text_rows = _load_texts_for_rows(args.results_dir, human_rows)

    # Unique gold problems for property probes
    unique_problems: Dict[str, dict] = {}
    for row in text_rows.values():
        k = f"{row['split']}::{row['problem_id']}"
        if k not in unique_problems:
            unique_problems[k] = {
                "split": row["split"],
                "problem_id": row["problem_id"],
                "gold": row["gold"],
            }

    detail_rows: List[dict] = []
    judge_rows: List[dict] = []

    print("=" * 72)
    print("EXP14: Multi-Judge Trend (Certification vs Human Correlation)")
    print(f"n_human_rows={len(text_rows)} n_unique_problems={len(unique_problems)} judges={len(judges)}")
    print("=" * 72)

    for spec in judges:
        print(f"[judge] {spec.judge_id}")

        # A) Human correlation
        human_vals: List[float] = []
        judge_vals: List[float] = []

        # B) Property probes
        identity_scores: List[float] = []
        identity_levs: List[float] = []
        identity_probe_scores: List[float] = []
        bug_levels_flat: List[int] = []
        bug_scores_flat: List[float] = []
        bug_ladders: List[List[float]] = []
        bug_lvl1_levs: List[float] = []
        bug_lvl1_drops: List[float] = []
        flip_flags: List[bool] = []

        # Human rows scoring
        for k, row in text_rows.items():
            result = _score_once(spec, row["gold"], row["candidate"], repeats=args.judge_repeats, seed=args.seed)
            mean_s = float(result["mean"])
            reps = [float(x) for x in result.get("scores", [mean_s])]
            human_vals.append(float(row["human_norm"]))
            judge_vals.append(mean_s)

            decs = [x >= args.threshold for x in reps]
            flip_flags.append(len(set(decs)) > 1)

            detail_rows.append(
                {
                    "judge_id": spec.judge_id,
                    "row_type": "human_eval",
                    "item_key": k,
                    "score_mean": round(mean_s, 6),
                    "score_std": round(float(result.get("std", 0.0)), 6),
                    "repeat_scores": json.dumps([round(x, 6) for x in reps]),
                    "human_norm": round(float(row["human_norm"]), 6),
                }
            )

        h_spear, h_spear_p = spearman_r(human_vals, judge_vals)
        h_spear_ci_lo, h_spear_ci_hi = _bootstrap_ci_stat(
            human_vals, judge_vals, _spearman_only, n_boot=args.bootstrap_iters, seed=args.seed
        )

        # Property probes on unique problems
        for pkey, prow in unique_problems.items():
            gold = prow["gold"]

            # identity via variants
            for v in generate_variants(gold):
                result = _score_once(spec, gold, v["code"], repeats=args.judge_repeats, seed=args.seed)
                mean_s = float(result["mean"])
                reps = [float(x) for x in result.get("scores", [mean_s])]
                identity_scores.append(mean_s)
                identity_levs.append(float(levenshtein_normalized(gold, v["code"])))
                identity_probe_scores.append(mean_s)
                decs = [x >= args.threshold for x in reps]
                flip_flags.append(len(set(decs)) > 1)
                detail_rows.append(
                    {
                        "judge_id": spec.judge_id,
                        "row_type": "property_identity",
                        "item_key": f"{pkey}::{v['variant_type']}",
                        "score_mean": round(mean_s, 6),
                        "score_std": round(float(result.get("std", 0.0)), 6),
                        "repeat_scores": json.dumps([round(x, 6) for x in reps]),
                        "human_norm": "",
                    }
                )

            # bug ladder
            ladder_scores: List[float] = []
            ladder_codes: List[str] = []
            for level, cand in enumerate(build_bug_ladder(gold)):
                result = _score_once(spec, gold, cand, repeats=args.judge_repeats, seed=args.seed)
                mean_s = float(result["mean"])
                reps = [float(x) for x in result.get("scores", [mean_s])]
                ladder_scores.append(mean_s)
                ladder_codes.append(cand)
                bug_levels_flat.append(level)
                bug_scores_flat.append(mean_s)
                decs = [x >= args.threshold for x in reps]
                flip_flags.append(len(set(decs)) > 1)
                detail_rows.append(
                    {
                        "judge_id": spec.judge_id,
                        "row_type": "property_bug",
                        "item_key": f"{pkey}::L{level}",
                        "score_mean": round(mean_s, 6),
                        "score_std": round(float(result.get("std", 0.0)), 6),
                        "repeat_scores": json.dumps([round(x, 6) for x in reps]),
                        "human_norm": "",
                    }
                )
            bug_ladders.append(ladder_scores)
            if len(ladder_scores) >= 2:
                lvl1_lev = float(levenshtein_normalized(gold, ladder_codes[1]))
                lvl1_drop = float(max(0.0, ladder_scores[0] - ladder_scores[1]))
                bug_lvl1_levs.append(lvl1_lev)
                bug_lvl1_drops.append(lvl1_drop)

        identity_mean = statistics.mean(identity_scores) if identity_scores else float("nan")
        identity_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0
        bug_spearman_r, bug_spearman_p = spearman_r(bug_levels_flat, bug_scores_flat)
        bug_weak_mono = weak_monotonicity_pct(bug_ladders)
        flip_rate = sum(1 for x in flip_flags if x) / max(1, len(flip_flags))

        # Anti-string metric: lower |corr(lev, score)| is better.
        lev_score_corr, _ = spearman_r(identity_levs, identity_probe_scores)
        anti_string_score = 1.0 - min(1.0, abs(float(lev_score_corr)) if math.isfinite(float(lev_score_corr)) else 1.0)

        # Subtle-bug semantic sensitivity: larger L0->L1 drop for tiny edits is better.
        if bug_lvl1_drops:
            subtle_raw = float(statistics.mean(bug_lvl1_drops))
        else:
            subtle_raw = 0.0
        # Normalize to [0,1] with 0.25 drop as saturation point.
        subtle_bug_sensitivity = max(0.0, min(1.0, subtle_raw / 0.25))

        cert_index = _compute_cert_index(
            identity_mean=identity_mean,
            bug_spearman_r=float(bug_spearman_r),
            bug_weak_mono_pct=float(bug_weak_mono),
            flip_rate=float(flip_rate),
        )
        cert_index_v2 = _compute_cert_index_v2(
            identity_mean=identity_mean,
            bug_spearman_r=float(bug_spearman_r),
            bug_weak_mono_pct=float(bug_weak_mono),
            flip_rate=float(flip_rate),
            anti_string_score=float(anti_string_score),
            subtle_bug_sensitivity=float(subtle_bug_sensitivity),
        )

        judge_rows.append(
            {
                "judge_id": spec.judge_id,
                "kind": spec.kind,
                "model": spec.model,
                "prompt_name": spec.prompt_name,
                "n_human_rows": len(human_vals),
                "human_spearman_r": float(h_spear),
                "human_spearman_p": float(h_spear_p),
                "human_spearman_ci_lo": float(h_spear_ci_lo),
                "human_spearman_ci_hi": float(h_spear_ci_hi),
                "identity_mean": float(identity_mean),
                "identity_std": float(identity_std),
                "bug_spearman_r": float(bug_spearman_r),
                "bug_spearman_p": float(bug_spearman_p),
                "bug_weak_mono_pct": float(bug_weak_mono),
                "flip_rate": float(flip_rate),
                "lev_score_spearman": float(lev_score_corr),
                "anti_string_score": float(anti_string_score),
                "lvl1_mean_drop": float(subtle_raw),
                "subtle_bug_sensitivity": float(subtle_bug_sensitivity),
                "cert_index": float(cert_index),
                "cert_index_v2": float(cert_index_v2),
            }
        )

    # Cross-judge trend statistics
    x_cert = np.asarray([r["cert_index"] for r in judge_rows], dtype=float)
    x_cert_v2 = np.asarray([r["cert_index_v2"] for r in judge_rows], dtype=float)
    y_hcorr = np.asarray([r["human_spearman_r"] for r in judge_rows], dtype=float)

    tr_s = float(_spearman_only(x_cert, y_hcorr))
    tr_p = float(_pearson_only(x_cert, y_hcorr))
    tr_k = float(_kendall_only(x_cert, y_hcorr))

    tr_s_ci = _bootstrap_ci_stat(x_cert, y_hcorr, _spearman_only, args.bootstrap_iters, args.seed + 17)
    tr_p_ci = _bootstrap_ci_stat(x_cert, y_hcorr, _pearson_only, args.bootstrap_iters, args.seed + 23)
    tr_k_ci = _bootstrap_ci_stat(x_cert, y_hcorr, _kendall_only, args.bootstrap_iters, args.seed + 31)

    tr_s_perm = _perm_pvalue_corr(x_cert, y_hcorr, _spearman_only, args.perm_iters, args.seed + 101)
    tr_p_perm = _perm_pvalue_corr(x_cert, y_hcorr, _pearson_only, args.perm_iters, args.seed + 103)
    tr_k_perm = _perm_pvalue_corr(x_cert, y_hcorr, _kendall_only, args.perm_iters, args.seed + 107)

    tr2_s = float(_spearman_only(x_cert_v2, y_hcorr))
    tr2_p = float(_pearson_only(x_cert_v2, y_hcorr))
    tr2_k = float(_kendall_only(x_cert_v2, y_hcorr))
    tr2_s_ci = _bootstrap_ci_stat(x_cert_v2, y_hcorr, _spearman_only, args.bootstrap_iters, args.seed + 211)
    tr2_p_ci = _bootstrap_ci_stat(x_cert_v2, y_hcorr, _pearson_only, args.bootstrap_iters, args.seed + 223)
    tr2_k_ci = _bootstrap_ci_stat(x_cert_v2, y_hcorr, _kendall_only, args.bootstrap_iters, args.seed + 227)
    tr2_s_perm = _perm_pvalue_corr(x_cert_v2, y_hcorr, _spearman_only, args.perm_iters, args.seed + 229)
    tr2_p_perm = _perm_pvalue_corr(x_cert_v2, y_hcorr, _pearson_only, args.perm_iters, args.seed + 233)
    tr2_k_perm = _perm_pvalue_corr(x_cert_v2, y_hcorr, _kendall_only, args.perm_iters, args.seed + 239)

    # leave-one-out sensitivity
    loo_rows: List[dict] = []
    for i, dropped in enumerate(judge_rows):
        keep_x = np.delete(x_cert, i)
        keep_x2 = np.delete(x_cert_v2, i)
        keep_y = np.delete(y_hcorr, i)
        if len(keep_x) < 3:
            continue
        loo_rows.append(
            {
                "dropped_judge": dropped["judge_id"],
                "spearman_r_v1": float(_spearman_only(keep_x, keep_y)),
                "pearson_r_v1": float(_pearson_only(keep_x, keep_y)),
                "kendall_tau_v1": float(_kendall_only(keep_x, keep_y)),
                "spearman_r_v2": float(_spearman_only(keep_x2, keep_y)),
                "pearson_r_v2": float(_pearson_only(keep_x2, keep_y)),
                "kendall_tau_v2": float(_kendall_only(keep_x2, keep_y)),
            }
        )

    trend_summary = {
        "n_judges": len(judge_rows),
        "threshold": args.threshold,
        "trend_v1": {
            "spearman_r": tr_s,
            "spearman_ci_lo": float(tr_s_ci[0]),
            "spearman_ci_hi": float(tr_s_ci[1]),
            "spearman_perm_p": float(tr_s_perm),
            "pearson_r": tr_p,
            "pearson_ci_lo": float(tr_p_ci[0]),
            "pearson_ci_hi": float(tr_p_ci[1]),
            "pearson_perm_p": float(tr_p_perm),
            "kendall_tau": tr_k,
            "kendall_ci_lo": float(tr_k_ci[0]),
            "kendall_ci_hi": float(tr_k_ci[1]),
            "kendall_perm_p": float(tr_k_perm),
        },
        "trend_v2": {
            "spearman_r": tr2_s,
            "spearman_ci_lo": float(tr2_s_ci[0]),
            "spearman_ci_hi": float(tr2_s_ci[1]),
            "spearman_perm_p": float(tr2_s_perm),
            "pearson_r": tr2_p,
            "pearson_ci_lo": float(tr2_p_ci[0]),
            "pearson_ci_hi": float(tr2_p_ci[1]),
            "pearson_perm_p": float(tr2_p_perm),
            "kendall_tau": tr2_k,
            "kendall_ci_lo": float(tr2_k_ci[0]),
            "kendall_ci_hi": float(tr2_k_ci[1]),
            "kendall_perm_p": float(tr2_k_perm),
        },
        "cert_index_formula": "0.30*identity_mean + 0.30*mono_rank + 0.25*weak_mono + 0.15*(1-flip_rate)",
        "cert_index_v2_formula": (
            "0.20*identity_mean + 0.20*mono_rank + 0.15*weak_mono + 0.10*(1-flip_rate) + "
            "0.20*anti_string_score + 0.15*subtle_bug_sensitivity"
        ),
        "mono_rank_map": "(-bug_spearman_r + 1)/2 clipped to [0,1]",
        "anti_string_score_map": "1 - abs(Spearman(levenshtein, identity_probe_score))",
        "subtle_bug_sensitivity_map": "clip(mean(max(0, L0-L1 drop))/0.25, 0, 1)",
        "judge_rows": judge_rows,
        "leave_one_out": loo_rows,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "judge_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(judge_rows[0].keys()))
        writer.writeheader()
        writer.writerows(judge_rows)

    with (args.out_dir / "detail_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(detail_rows[0].keys()))
        writer.writeheader()
        writer.writerows(detail_rows)

    (args.out_dir / "trend_summary.json").write_text(json.dumps(trend_summary, indent=2), encoding="utf-8")

    _make_plots(judge_rows=judge_rows, trend=trend_summary["trend_v2"], out_dir=args.out_dir)

    print("\nTrend summary:")
    print(
        f"  V1 Spearman(cert_index, human_corr) = {tr_s:.3f} "
        f"(95% CI [{tr_s_ci[0]:.3f}, {tr_s_ci[1]:.3f}], perm p={tr_s_perm:.4f})"
    )
    print(
        f"  V2 Spearman(cert_index_v2, human_corr) = {tr2_s:.3f} "
        f"(95% CI [{tr2_s_ci[0]:.3f}, {tr2_s_ci[1]:.3f}], perm p={tr2_s_perm:.4f})"
    )
    print(
        f"  V1 Pearson(cert_index, human_corr) = {tr_p:.3f} "
        f"(95% CI [{tr_p_ci[0]:.3f}, {tr_p_ci[1]:.3f}], perm p={tr_p_perm:.4f})"
    )
    print(
        f"  V2 Pearson(cert_index_v2, human_corr) = {tr2_p:.3f} "
        f"(95% CI [{tr2_p_ci[0]:.3f}, {tr2_p_ci[1]:.3f}], perm p={tr2_p_perm:.4f})"
    )
    print(f"  wrote: {args.out_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
