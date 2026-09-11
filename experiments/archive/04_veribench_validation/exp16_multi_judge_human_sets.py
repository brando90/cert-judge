#!/usr/bin/env python3
"""
EXP16: Multi-judge trend with multiple human label sets (pass1/pass2/avg).

This extends EXP14 by evaluating the same set of judge scores against
three human targets:
  - pass1
  - pass2
  - avg(pass1, pass2)

Judge scoring is run once over the union of human-labeled rows, then reused
across all human targets to avoid duplicate API calls.
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

REPO_ROOT = Path(__file__).resolve().parents[3]
EXP02_DIR = REPO_ROOT / "experiments" / "02_neurips_reviews"
sys.path.insert(0, str(EXP02_DIR))

from utils.judge_caller import judge
from utils.metrics import levenshtein_normalized, spearman_r, weak_monotonicity_pct
from utils.sensitivity_sweep import PROMPT_VARIANTS
from utils.variant_generator import generate_variants
from utils.veribench_variance_utils import build_bug_ladder, extract_theorem_blocks


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent / "results_exp16_multi_judge_human_sets"
DEFAULT_VERIBENCH_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench"
DEFAULT_GENERATED_AGENTS_DIR = REPO_ROOT / "data" / "generated_agents"
_GLOBAL_CACHE_TAG = ""


@dataclass(frozen=True)
class JudgeSpec:
    judge_id: str
    kind: str  # llm | llm_bad | editdist | random
    model: str
    prompt_name: str


BAD_STRINGY_PROMPT = """You are a text similarity grader.
Compare generated theorem text to the reference implementation text.
Do NOT evaluate semantic correctness or theorem meaning.
Score ONLY based on superficial lexical/format overlap:
- high score if tokens/phrases look similar
- low score if wording/structure differs
Reference implementation:
{reference_impl}

Generated theorem:
{generated_theorem}

Return ONLY a JSON object:
{{"score": <float 0.0 to 1.0>, "reasoning": "<short reason>"}}
"""

BAD_FORMAT_BIAS_PROMPT = """You are a style-and-format grader.
Compare generated theorem text to the reference implementation text.
Do NOT reason about semantic correctness.
Score based on:
- visual formatting similarity
- line/indentation similarity
- naming/token overlap
- similar theorem statement shape
Reference implementation:
{reference_impl}

Generated theorem:
{generated_theorem}

Return ONLY a JSON object:
{{"score": <float 0.0 to 1.0>, "reasoning": "<short reason>"}}
"""

BAD_PROMPTS: Dict[str, str] = {
    "BAD_STRINGY": BAD_STRINGY_PROMPT,
    "BAD_FORMAT_BIAS": BAD_FORMAT_BIAS_PROMPT,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP16 multi-judge trend across pass1/pass2/avg human labels")
    p.add_argument("--pass1-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_20260425.tsv")
    p.add_argument("--pass2-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_ORIGINAL.tsv")
    p.add_argument("--avg-tsv", type=Path, default=DEFAULT_DATA_DIR / "ethan_human_scores_avg_two_passes_20260425.tsv")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--veribench-root", type=Path, default=DEFAULT_VERIBENCH_ROOT)
    p.add_argument("--generated-agents-dir", type=Path, default=DEFAULT_GENERATED_AGENTS_DIR)
    p.add_argument("--judge-repeats", type=int, default=3)
    p.add_argument(
        "--repeat-agg",
        choices=["mean", "median"],
        default="mean",
        help="Aggregate repeat scores with mean (default) or median for robustness.",
    )
    p.add_argument("--threshold", type=float, default=0.85)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--bootstrap-iters", type=int, default=5000)
    p.add_argument("--perm-iters", type=int, default=10000)
    p.add_argument(
        "--cache-tag",
        type=str,
        default="",
        help="Optional cache namespace suffix to force fresh judge calls (e.g., r9_median_v1).",
    )
    p.add_argument(
        "--plot-error-bars",
        choices=["on", "off"],
        default="on",
        help="Whether to draw per-judge CI bars in scatter plots.",
    )
    p.add_argument(
        "--judges",
        type=str,
        default=(
            "llm:gpt-5.3-codex:P8_STRICT_B,"
            "llm:gpt-5.3-codex:P4_CHECKLIST,"
            "llm:gpt-5.3-codex:P1_BASELINE,"
            "llm_bad:gpt-5.3-codex:BAD_STRINGY,"
            "llm:gpt-4o-mini:P8_STRICT_B,"
            "llm:gpt-4o-mini:P4_CHECKLIST,"
            "editdist:e1:na,"
            "random:r1:na"
        ),
    )
    return p.parse_args()


def _parse_judges(raw: str) -> List[JudgeSpec]:
    judges: List[JudgeSpec] = []
    for token in [t.strip() for t in raw.split(",") if t.strip()]:
        # Allow model identifiers that themselves contain ":" (e.g., Bedrock suffixes like "...-v1:0")
        if ":" not in token:
            raise ValueError(f"Bad judge spec: {token}")
        kind, rem = token.split(":", 1)
        if ":" not in rem:
            raise ValueError(f"Bad judge spec: {token}")
        model, prompt_name = rem.rsplit(":", 1)
        kind = kind.lower().strip()
        model = model.strip()
        prompt_name = prompt_name.strip()

        if kind == "llm":
            if prompt_name not in PROMPT_VARIANTS:
                raise ValueError(f"Unknown prompt name in judge spec: {prompt_name}")
            judge_id = f"{model}|{prompt_name}"
        elif kind == "llm_bad":
            if prompt_name.lower() == "na":
                prompt_name = "BAD_STRINGY"
            if prompt_name not in BAD_PROMPTS:
                raise ValueError(f"Unknown llm_bad prompt name: {prompt_name}. Choices: {sorted(BAD_PROMPTS)}")
            judge_id = f"{model}|{prompt_name}"
        elif kind in {"editdist", "random"}:
            suffix = "" if model in {"", "na"} else f"_{model}"
            judge_id = f"{kind}{suffix}"
            model = "na"
            prompt_name = "na"
        else:
            raise ValueError(f"Unknown judge kind: {kind}")

        judges.append(JudgeSpec(judge_id=judge_id, kind=kind, model=model, prompt_name=prompt_name))

    seen = set()
    uniq: List[JudgeSpec] = []
    for j in judges:
        if j.judge_id in seen:
            continue
        seen.add(j.judge_id)
        uniq.append(j)
    if len(uniq) < 2:
        raise ValueError("Provide at least 2 unique judges")
    return uniq


def _load_tsv_scores(path: Path) -> Dict[Tuple[str, str], float]:
    rows: Dict[Tuple[str, str], List[float]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            g = str(r.get("gold_file", "")).strip()
            c = str(r.get("candidate_file", "")).strip()
            s = str(r.get("human_score_0_5", "")).strip()
            if not g or not c or not s:
                continue
            rows.setdefault((g, c), []).append(float(s))
    return {k: float(sum(v) / len(v)) for k, v in rows.items()}


def _build_gold_index(veribench_root: Path) -> Dict[str, List[Path]]:
    idx: Dict[str, List[Path]] = {}
    for p in veribench_root.rglob("*.lean"):
        idx.setdefault(p.name, []).append(p)
    return idx


def _resolve_gold_path(gold_file: str, gold_idx: Dict[str, List[Path]]) -> Path:
    matches = gold_idx.get(gold_file, [])
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"Could not find gold file {gold_file}")
    # Prefer non-hidden and shorter paths if duplicated.
    matches = sorted(matches, key=lambda p: (len(p.parts), str(p)))
    return matches[0]


def _extract_last_theorem_block(text: str) -> str:
    spans = extract_theorem_blocks(text)
    if not spans:
        return text
    start, end = spans[-1]
    block = text[start:end].strip()
    return block if block else text


def _det_random_score(judge_id: str, gold: str, cand: str, seed: int) -> float:
    h = hashlib.sha256((judge_id + str(seed) + gold[:200] + cand[:200]).encode("utf-8")).hexdigest()
    x = int(h[:12], 16) / float(16**12 - 1)
    return float(x)


def _score_once(spec: JudgeSpec, gold: str, cand: str, repeats: int, seed: int) -> dict:
    if spec.kind == "llm":
        prompt = PROMPT_VARIANTS[spec.prompt_name]
        ns = f"exp16:{spec.judge_id}"
        if _GLOBAL_CACHE_TAG:
            ns = f"{ns}:{_GLOBAL_CACHE_TAG}"
        return judge(
            generated_theorem=cand,
            reference_impl=gold,
            model=spec.model,
            n_repeats=repeats,
            prompt_template=prompt,
            cache_namespace=ns,
        )
    if spec.kind == "llm_bad":
        ns = f"exp16_bad:{spec.judge_id}"
        if _GLOBAL_CACHE_TAG:
            ns = f"{ns}:{_GLOBAL_CACHE_TAG}"
        return judge(
            generated_theorem=cand,
            reference_impl=gold,
            model=spec.model,
            n_repeats=repeats,
            prompt_template=BAD_PROMPTS[spec.prompt_name],
            cache_namespace=ns,
        )
    if spec.kind == "editdist":
        score = 1.0 - levenshtein_normalized(gold, cand)
        score = max(0.0, min(1.0, float(score)))
        return {"mean": score, "std": 0.0, "scores": [score] * repeats, "cached": False, "reasoning": "edit-distance baseline"}
    if spec.kind == "random":
        score = _det_random_score(spec.judge_id, gold, cand, seed=seed)
        return {"mean": score, "std": 0.0, "scores": [score] * repeats, "cached": False, "reasoning": "deterministic random baseline"}
    raise ValueError(spec.kind)


def _aggregate_repeat_scores(result: dict, repeat_agg: str) -> Tuple[float, List[float]]:
    reps = [float(x) for x in result.get("scores", [])]
    if not reps:
        m = float(result.get("mean", float("nan")))
        reps = [m]
    arr = np.asarray(reps, dtype=float)
    if repeat_agg == "median":
        return (float(np.median(arr)), reps)
    return (float(np.mean(arr)), reps)


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
    mono_rank = max(0.0, min(1.0, (-bug_spearman_r + 1.0) / 2.0))
    weak = max(0.0, min(1.0, bug_weak_mono_pct / 100.0))
    flip_stability = max(0.0, min(1.0, 1.0 - flip_rate))
    ident = max(0.0, min(1.0, identity_mean))
    return float(0.30 * ident + 0.30 * mono_rank + 0.25 * weak + 0.15 * flip_stability)


def _compute_cert_index_v2(
    identity_mean: float,
    bug_spearman_r: float,
    bug_weak_mono_pct: float,
    flip_rate: float,
    anti_string_score: float,
    subtle_bug_sensitivity: float,
) -> float:
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


def _compute_trend(x: np.ndarray, y: np.ndarray, n_boot: int, n_perm: int, seed: int) -> dict:
    sp = float(_spearman_only(x, y))
    pe = float(_pearson_only(x, y))
    ke = float(_kendall_only(x, y))
    sp_ci = _bootstrap_ci_stat(x, y, _spearman_only, n_boot, seed + 11)
    pe_ci = _bootstrap_ci_stat(x, y, _pearson_only, n_boot, seed + 13)
    ke_ci = _bootstrap_ci_stat(x, y, _kendall_only, n_boot, seed + 17)
    sp_p = _perm_pvalue_corr(x, y, _spearman_only, n_perm, seed + 101)
    pe_p = _perm_pvalue_corr(x, y, _pearson_only, n_perm, seed + 103)
    ke_p = _perm_pvalue_corr(x, y, _kendall_only, n_perm, seed + 107)
    return {
        "spearman_r": sp,
        "spearman_ci_lo": float(sp_ci[0]),
        "spearman_ci_hi": float(sp_ci[1]),
        "spearman_perm_p": float(sp_p),
        "pearson_r": pe,
        "pearson_ci_lo": float(pe_ci[0]),
        "pearson_ci_hi": float(pe_ci[1]),
        "pearson_perm_p": float(pe_p),
        "kendall_tau": ke,
        "kendall_ci_lo": float(ke_ci[0]),
        "kendall_ci_hi": float(ke_ci[1]),
        "kendall_perm_p": float(ke_p),
    }


def _make_plots(judge_rows: List[dict], trend_by_set: Dict[str, dict], out_dir: Path, show_error_bars: bool = True) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)

    # Scatter for each label set.
    for label_set in ["pass1", "pass2", "avg"]:
        xs = [r["cert_index_v2"] for r in judge_rows]
        ys = [r[f"human_spearman_r_{label_set}"] for r in judge_rows]
        ylos = [r[f"human_spearman_ci_lo_{label_set}"] for r in judge_rows]
        yhis = [r[f"human_spearman_ci_hi_{label_set}"] for r in judge_rows]

        fig, ax = plt.subplots(figsize=(8.0, 5.6))
        ax.scatter(xs, ys, s=70)
        for i, r in enumerate(judge_rows):
            if show_error_bars:
                yerr_low = ys[i] - ylos[i] if math.isfinite(ylos[i]) else 0.0
                yerr_hi = yhis[i] - ys[i] if math.isfinite(yhis[i]) else 0.0
                ax.errorbar(xs[i], ys[i], yerr=[[yerr_low], [yerr_hi]], fmt="none", alpha=0.6)
            ax.annotate(r["judge_id"], (xs[i], ys[i]), xytext=(4, 4), textcoords="offset points", fontsize=8)
        if len(xs) >= 2:
            z = np.polyfit(xs, ys, 1)
            xline = np.linspace(min(xs), max(xs), 100)
            yline = z[0] * xline + z[1]
            ax.plot(xline, yline, "r--", linewidth=1.5)
        tr = trend_by_set[label_set]["trend_v2"]
        ax.set_xlabel("Certification Index (v2)")
        ax.set_ylabel(f"Human Correlation Spearman ({label_set})")
        ax.set_title(
            f"EXP16 ({label_set}): Cert v2 vs Human Corr\n"
            f"Spearman={tr['spearman_r']:.3f} (p_perm={tr['spearman_perm_p']:.4f})"
        )
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(out_dir / f"fig_cert_vs_human_scatter_{label_set}.png", dpi=180)
        plt.close(fig)


def main() -> int:
    args = parse_args()
    global _GLOBAL_CACHE_TAG
    _GLOBAL_CACHE_TAG = args.cache_tag.strip()
    random.seed(args.seed)
    np.random.seed(args.seed)

    judges = _parse_judges(args.judges)

    pass1 = _load_tsv_scores(args.pass1_tsv)
    pass2 = _load_tsv_scores(args.pass2_tsv)
    avg = _load_tsv_scores(args.avg_tsv)
    label_sets: Dict[str, Dict[Tuple[str, str], float]] = {"pass1": pass1, "pass2": pass2, "avg": avg}

    union_keys = sorted(set().union(*[set(v.keys()) for v in label_sets.values()]))
    if not union_keys:
        raise ValueError("No human labeled pairs found")

    gold_idx = _build_gold_index(args.veribench_root)
    text_rows: Dict[Tuple[str, str], dict] = {}
    skipped_pairs: List[dict] = []
    for g, c in union_keys:
        try:
            gold_path = _resolve_gold_path(g, gold_idx)
        except FileNotFoundError:
            skipped_pairs.append({"gold_file": g, "candidate_file": c, "reason": "missing_gold"})
            continue
        cand_path = args.generated_agents_dir / c
        if not cand_path.exists():
            skipped_pairs.append({"gold_file": g, "candidate_file": c, "reason": "missing_candidate"})
            continue
        text_rows[(g, c)] = {
            "gold_file": g,
            "candidate_file": c,
            "problem_id": Path(g).stem,
            "gold": _extract_last_theorem_block(gold_path.read_text(encoding="utf-8", errors="ignore")),
            "candidate": cand_path.read_text(encoding="utf-8", errors="ignore"),
        }

    unique_problems: Dict[str, dict] = {}
    for (g, _), row in text_rows.items():
        pkey = Path(g).stem
        if pkey not in unique_problems:
            unique_problems[pkey] = {"problem_id": pkey, "gold": row["gold"]}

    detail_rows: List[dict] = []
    judge_rows: List[dict] = []

    print("=" * 72)
    print("EXP16: Multi-Judge Trend across pass1/pass2/avg human labels")
    print(f"n_union_human_rows={len(text_rows)} n_unique_problems={len(unique_problems)} judges={len(judges)}")
    print(f"n_skipped_pairs={len(skipped_pairs)}")
    print("=" * 72)

    for spec in judges:
        print(f"[judge] {spec.judge_id}")

        score_map: Dict[Tuple[str, str], float] = {}

        identity_scores: List[float] = []
        identity_levs: List[float] = []
        identity_probe_scores: List[float] = []
        bug_levels_flat: List[int] = []
        bug_scores_flat: List[float] = []
        bug_ladders: List[List[float]] = []
        bug_lvl1_drops: List[float] = []
        flip_flags: List[bool] = []

        # Human row scoring once for union.
        for key, row in text_rows.items():
            result = _score_once(spec, row["gold"], row["candidate"], repeats=args.judge_repeats, seed=args.seed)
            mean_s, reps = _aggregate_repeat_scores(result, args.repeat_agg)
            score_map[key] = mean_s
            decs = [x >= args.threshold for x in reps]
            flip_flags.append(len(set(decs)) > 1)

            detail_rows.append(
                {
                    "judge_id": spec.judge_id,
                    "row_type": "human_eval_union",
                    "item_key": f"{row['gold_file']}::{row['candidate_file']}",
                    "score_mean": round(mean_s, 6),
                    "score_std": round(float(result.get("std", 0.0)), 6),
                    "repeat_scores": json.dumps([round(x, 6) for x in reps]),
                }
            )

        # Property probes on unique problems
        for pkey, prow in unique_problems.items():
            gold = prow["gold"]
            for v in generate_variants(gold):
                result = _score_once(spec, gold, v["code"], repeats=args.judge_repeats, seed=args.seed)
                mean_s, reps = _aggregate_repeat_scores(result, args.repeat_agg)
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
                    }
                )

            ladder_scores: List[float] = []
            ladder_codes: List[str] = []
            for level, cand in enumerate(build_bug_ladder(gold)):
                result = _score_once(spec, gold, cand, repeats=args.judge_repeats, seed=args.seed)
                mean_s, reps = _aggregate_repeat_scores(result, args.repeat_agg)
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
                    }
                )
            bug_ladders.append(ladder_scores)
            if len(ladder_scores) >= 2:
                bug_lvl1_drops.append(float(max(0.0, ladder_scores[0] - ladder_scores[1])))

        identity_mean = statistics.mean(identity_scores) if identity_scores else float("nan")
        identity_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0
        bug_spearman_r, bug_spearman_p = spearman_r(bug_levels_flat, bug_scores_flat)
        bug_weak_mono = weak_monotonicity_pct(bug_ladders)
        flip_rate = sum(1 for x in flip_flags if x) / max(1, len(flip_flags))

        lev_score_corr, _ = spearman_r(identity_levs, identity_probe_scores)
        anti_string_score = 1.0 - min(1.0, abs(float(lev_score_corr)) if math.isfinite(float(lev_score_corr)) else 1.0)
        subtle_raw = float(statistics.mean(bug_lvl1_drops)) if bug_lvl1_drops else 0.0
        subtle_bug_sensitivity = max(0.0, min(1.0, subtle_raw / 0.25))

        cert_index = _compute_cert_index(identity_mean, float(bug_spearman_r), float(bug_weak_mono), float(flip_rate))
        cert_index_v2 = _compute_cert_index_v2(
            identity_mean=identity_mean,
            bug_spearman_r=float(bug_spearman_r),
            bug_weak_mono_pct=float(bug_weak_mono),
            flip_rate=float(flip_rate),
            anti_string_score=float(anti_string_score),
            subtle_bug_sensitivity=float(subtle_bug_sensitivity),
        )

        row = {
            "judge_id": spec.judge_id,
            "kind": spec.kind,
            "model": spec.model,
            "prompt_name": spec.prompt_name,
            "n_union_rows": len(text_rows),
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

        # Human correlations for each label set
        for set_name, lbls in label_sets.items():
            hvals: List[float] = []
            jvals: List[float] = []
            for key, h in lbls.items():
                if key not in score_map:
                    continue
                hvals.append(float(h) / 5.0)
                jvals.append(float(score_map[key]))

            hs, hp = spearman_r(hvals, jvals)
            hci_lo, hci_hi = _bootstrap_ci_stat(hvals, jvals, _spearman_only, n_boot=args.bootstrap_iters, seed=args.seed)
            row[f"n_human_rows_{set_name}"] = len(hvals)
            row[f"human_spearman_r_{set_name}"] = float(hs)
            row[f"human_spearman_p_{set_name}"] = float(hp)
            row[f"human_spearman_ci_lo_{set_name}"] = float(hci_lo)
            row[f"human_spearman_ci_hi_{set_name}"] = float(hci_hi)
        judge_rows.append(row)

    # Trend per label set
    trend_by_set: Dict[str, dict] = {}
    x1_all = np.asarray([r["cert_index"] for r in judge_rows], dtype=float)
    x2_all = np.asarray([r["cert_index_v2"] for r in judge_rows], dtype=float)
    for set_name in ["pass1", "pass2", "avg"]:
        y_all = np.asarray([r[f"human_spearman_r_{set_name}"] for r in judge_rows], dtype=float)
        mask = np.isfinite(x1_all) & np.isfinite(x2_all) & np.isfinite(y_all)
        x1 = x1_all[mask]
        x2 = x2_all[mask]
        y = y_all[mask]
        if len(y) < 4:
            nan_trend = {
                "spearman_r": float("nan"),
                "spearman_ci_lo": float("nan"),
                "spearman_ci_hi": float("nan"),
                "spearman_perm_p": float("nan"),
                "pearson_r": float("nan"),
                "pearson_ci_lo": float("nan"),
                "pearson_ci_hi": float("nan"),
                "pearson_perm_p": float("nan"),
                "kendall_tau": float("nan"),
                "kendall_ci_lo": float("nan"),
                "kendall_ci_hi": float("nan"),
                "kendall_perm_p": float("nan"),
            }
            trend_by_set[set_name] = {
                "n_used_judges": int(len(y)),
                "trend_v1": dict(nan_trend),
                "trend_v2": dict(nan_trend),
            }
            continue
        trend_by_set[set_name] = {
            "n_used_judges": int(len(y)),
            "trend_v1": _compute_trend(x1, y, args.bootstrap_iters, args.perm_iters, args.seed + 200),
            "trend_v2": _compute_trend(x2, y, args.bootstrap_iters, args.perm_iters, args.seed + 300),
        }

    summary = {
        "experiment": "exp16_multi_judge_human_sets",
        "n_judges": len(judge_rows),
        "n_union_rows": len(text_rows),
        "n_skipped_pairs": len(skipped_pairs),
        "threshold": args.threshold,
        "judge_repeats": int(args.judge_repeats),
        "repeat_agg": args.repeat_agg,
        "cache_tag": _GLOBAL_CACHE_TAG,
        "judges": [j.judge_id for j in judges],
        "label_sets": {k: len(v) for k, v in label_sets.items()},
        "trend_by_set": trend_by_set,
        "skipped_pairs": skipped_pairs,
        "judge_rows": judge_rows,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (args.out_dir / "judge_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(judge_rows[0].keys()))
        w.writeheader()
        w.writerows(judge_rows)
    with (args.out_dir / "detail_rows.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(detail_rows[0].keys()))
        w.writeheader()
        w.writerows(detail_rows)
    if skipped_pairs:
        with (args.out_dir / "skipped_pairs.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["gold_file", "candidate_file", "reason"])
            w.writeheader()
            w.writerows(skipped_pairs)

    _make_plots(judge_rows, trend_by_set, args.out_dir, show_error_bars=(args.plot_error_bars == "on"))

    print("\nTrend summary by label set (v2 Spearman cert->human):")
    for set_name in ["pass1", "pass2", "avg"]:
        tr = trend_by_set[set_name]["trend_v2"]
        print(
            f"  {set_name}: r={tr['spearman_r']:.3f} "
            f"CI=[{tr['spearman_ci_lo']:.3f},{tr['spearman_ci_hi']:.3f}] "
            f"perm_p={tr['spearman_perm_p']:.4f}"
        )
    print(f"Wrote: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
