#!/usr/bin/env python3
"""
Experiment 9: Judge Stability (P4)

Measure how stable judge scores are across:
  1) repeated calls (within-prompt repeatability),
  2) prompt variants (cross-prompt agreement),
  3) non-semantic surface variants (invariance).

Outputs:
  - results/stability/summary.json
  - results/stability/detail_rows.csv
  - results/stability/repeat_rows.csv
  - results/stability/per_item_prompt_dispersion.csv
  - results/stability/prompt_pairwise.csv
  - results/stability/invariance_rows.csv
  - figures/stability/*.png
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import sys
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

EXP_DIR = Path(__file__).parent
REPO_ROOT = EXP_DIR.parents[2]
sys.path.insert(0, str(EXP_DIR))

from utils.judge_caller import judge
from utils.metrics import spearman_r
from utils.sensitivity_sweep import PROMPT_VARIANTS, cohen_kappa, score_to_label
from utils.variant_generator import generate_variants


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P4 stability evaluation for the Lean judge.")
    parser.add_argument("--model", type=str, default="gpt-5.3-codex")
    parser.add_argument("--judge-mode", type=str, default="api", choices=["api", "local"])
    parser.add_argument("--n-repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-files", type=int, default=0, help="0 means all Lean files under veribench-root.")
    parser.add_argument(
        "--prompt-names",
        type=str,
        default="",
        help="Comma-separated prompt names from PROMPT_VARIANTS. Empty => all prompts.",
    )
    parser.add_argument(
        "--veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    )
    parser.add_argument(
        "--append-veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset_newest" / "lean_src" / "veribench",
        help="Optional second root for appending extra tasks not present in --veribench-root.",
    )
    parser.add_argument(
        "--append-max-files",
        type=int,
        default=0,
        help="How many append-only files to include from --append-veribench-root (0 disables append).",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=EXP_DIR / "results" / "stability",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=EXP_DIR / "figures" / "stability",
    )
    return parser.parse_args()


def _extract_theorem_lemma_names(text: str) -> set[str]:
    import re

    names = set()
    for m in re.finditer(r"(?m)^\s*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)", text):
        names.add(m.group(1))
    return names


def _local_prompt_judge(generated_theorem: str, reference_impl: str) -> dict:
    import difflib

    if generated_theorem == reference_impl:
        return {
            "score": 1.0,
            "mean": 1.0,
            "std": 0.0,
            "scores": [1.0],
            "reasoning": "Exact string match.",
            "model": "local_prompt_judge",
            "cached": False,
        }

    ratio = difflib.SequenceMatcher(None, reference_impl, generated_theorem).ratio()
    lev_like = 1.0 - ratio

    ref_toks = set(reference_impl.split())
    gen_toks = set(generated_theorem.split())
    if ref_toks or gen_toks:
        jacc = len(ref_toks & gen_toks) / max(1, len(ref_toks | gen_toks))
    else:
        jacc = 1.0

    ref_names = _extract_theorem_lemma_names(reference_impl)
    gen_names = _extract_theorem_lemma_names(generated_theorem)
    coverage = (len(ref_names & gen_names) / max(1, len(ref_names))) if ref_names else 1.0

    theorem_penalty = 0.0
    if len(gen_names) < max(1, len(ref_names) // 2):
        theorem_penalty += 0.20
    if len(gen_names) == 0:
        theorem_penalty += 0.20

    trivial_hits = 0
    trivial_hits += generated_theorem.count(": True")
    trivial_hits += generated_theorem.count(":= trivial")
    trivial_hits += generated_theorem.count("True.intro")
    trivial_penalty = min(0.45, 0.08 * trivial_hits)

    score = 0.62 * (1.0 - lev_like) + 0.38 * coverage
    score = score * 0.85 + 0.15 * jacc
    score = score - theorem_penalty - trivial_penalty
    score = max(0.0, min(1.0, score))

    return {
        "score": score,
        "mean": score,
        "std": 0.0,
        "scores": [score],
        "reasoning": (
            f"local judge: sim={1.0-lev_like:.3f}, jacc={jacc:.3f}, coverage={coverage:.3f}, "
            f"theorem_penalty={theorem_penalty:.3f}, trivial_penalty={trivial_penalty:.3f}"
        ),
        "model": "local_prompt_judge",
        "cached": False,
    }


def _score_pair(
    generated_theorem: str,
    reference_impl: str,
    model: str,
    n_repeats: int,
    prompt_template: str,
    cache_namespace: str,
    judge_mode: str,
) -> dict:
    if judge_mode == "local":
        return _local_prompt_judge(generated_theorem, reference_impl)
    return judge(
        generated_theorem=generated_theorem,
        reference_impl=reference_impl,
        model=model,
        n_repeats=n_repeats,
        prompt_template=prompt_template,
        cache_namespace=cache_namespace,
    )


def _infer_split(path: Path) -> str:
    parts = list(path.parts)
    if "easy_set" in parts:
        return "easy"
    if "cs_set" in parts:
        return "cs"
    if "humaneval_set" in parts:
        return "humaneval"
    if "real_code" in parts or "realcode_set" in parts:
        return "real_code"
    if "security_6858" in parts:
        return "security_6858"
    if "security_set" in parts:
        return "security_6858"
    if "security_python" in parts:
        return "security_python"
    return "other"


def collect_veribench_files(
    veribench_root: Path,
    max_files: int,
    seed: int,
    append_veribench_root: Path | None = None,
    append_max_files: int = 0,
) -> List[Path]:
    if not veribench_root.exists():
        return []

    skip_names = {"Common.lean", "Prelude.lean", "veribench.lean", "sandbox.lean", "tmp.lean", "55.lean"}
    base_files = [
        p for p in veribench_root.rglob("*.lean") if p.is_file() and p.name not in skip_names
    ]
    base_files = sorted(base_files)
    merged_files = list(base_files)

    if append_veribench_root and append_max_files > 0 and append_veribench_root.exists():
        base_rel = {str(p.relative_to(veribench_root)) for p in base_files}
        append_candidates = [
            p
            for p in append_veribench_root.rglob("*.lean")
            if p.is_file()
            and p.name not in skip_names
            and str(p.relative_to(append_veribench_root)) not in base_rel
        ]
        append_candidates = sorted(append_candidates)
        if append_candidates:
            rng = random.Random(seed)
            rng.shuffle(append_candidates)
            append_take = sorted(append_candidates[:append_max_files])
            merged_files.extend(append_take)

    if max_files > 0 and len(merged_files) > max_files:
        rng = random.Random(seed)
        rng.shuffle(merged_files)
        merged_files = sorted(merged_files[:max_files])
    return merged_files


def _relative_display_path(p: Path, primary_root: Path, append_root: Path | None) -> str:
    try:
        return str(p.relative_to(primary_root))
    except ValueError:
        if append_root is not None:
            try:
                return str(p.relative_to(append_root))
            except ValueError:
                pass
    return str(p)


def _write_csv(path: Path, rows: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _cronbach_alpha(rows_by_item: Dict[str, Dict[str, float]], prompt_names: List[str]) -> float:
    # alpha = (k/(k-1)) * (1 - sum(var_i) / var_total)
    # where each "item" is a file+variant, each "rater" is a prompt.
    if len(prompt_names) < 2 or len(rows_by_item) < 2:
        return 0.0

    matrix: List[List[float]] = []
    for item_id in sorted(rows_by_item.keys()):
        row = rows_by_item[item_id]
        if all(p in row for p in prompt_names):
            matrix.append([float(row[p]) for p in prompt_names])

    if len(matrix) < 2:
        return 0.0

    k = len(prompt_names)
    col_vars = []
    for j in range(k):
        col = [r[j] for r in matrix]
        if len(col) < 2:
            return 0.0
        col_vars.append(statistics.variance(col))

    totals = [sum(r) for r in matrix]
    if len(totals) < 2:
        return 0.0
    total_var = statistics.variance(totals)
    if total_var <= 1e-12:
        return 1.0
    alpha = (k / (k - 1.0)) * (1.0 - (sum(col_vars) / total_var))
    return float(alpha)


def _make_figures(
    figures_dir: Path,
    detail_rows: List[dict],
    prompt_names: List[str],
    prompt_pairwise: List[dict],
    per_item_prompt_dispersion: List[dict],
    invariance_rows: List[dict],
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception as e:
        print(f"WARNING: figure generation skipped (matplotlib unavailable): {e}")
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1) Boxplot of score means by prompt.
    grouped: Dict[str, List[float]] = {p: [] for p in prompt_names}
    for r in detail_rows:
        grouped[str(r["prompt_name"])].append(float(r["score_mean"]))
    arr = [grouped[p] for p in prompt_names]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.boxplot(arr, tick_labels=prompt_names, showfliers=False)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("Score Mean")
    ax.set_title("Score Distribution by Prompt Variant")
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / "prompt_score_distribution_boxplot.png", dpi=180)
    plt.close(fig)

    # 2) Repeatability histogram (std across repeats).
    repeat_stds = [float(r["score_std"]) for r in detail_rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(repeat_stds, bins=20)
    ax.set_xlabel("Within-item std across repeats")
    ax.set_ylabel("Count")
    ax.set_title("Repeatability (Per Prompt, Per Item)")
    fig.tight_layout()
    fig.savefig(figures_dir / "repeatability_std_histogram.png", dpi=180)
    plt.close(fig)

    # 3) Prompt pairwise Spearman heatmap.
    idx = {name: i for i, name in enumerate(prompt_names)}
    n = len(prompt_names)
    spearman = np.zeros((n, n), dtype=float)
    np.fill_diagonal(spearman, 1.0)
    for row in prompt_pairwise:
        i = idx[row["a"]]
        j = idx[row["b"]]
        spearman[i, j] = spearman[j, i] = float(row["spearman_r"])

    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(spearman, vmin=-1.0, vmax=1.0, cmap="coolwarm")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(prompt_names, rotation=90, fontsize=8)
    ax.set_yticklabels(prompt_names, fontsize=8)
    ax.set_title("Prompt Pairwise Spearman Correlation")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(figures_dir / "prompt_pairwise_spearman_heatmap.png", dpi=180)
    plt.close(fig)

    # 4) Invariance gap by variant type.
    var_to_vals: Dict[str, List[float]] = {}
    for r in invariance_rows:
        vt = str(r["variant_type"])
        if vt == "ORIGINAL":
            continue
        var_to_vals.setdefault(vt, []).append(float(r["abs_gap_vs_original"]))
    labels = sorted(var_to_vals.keys())
    if labels:
        means = [statistics.mean(var_to_vals[k]) for k in labels]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(labels, means)
        ax.set_ylim(0.0, 1.0)
        ax.set_ylabel("Mean Absolute Gap vs ORIGINAL")
        ax.set_title("Semantic Invariance Gap by Variant Type")
        fig.tight_layout()
        fig.savefig(figures_dir / "semantic_invariance_gap_by_variant.png", dpi=180)
        plt.close(fig)


def _select_prompts(prompt_names_arg: str) -> List[str]:
    available = list(PROMPT_VARIANTS.keys())
    if not prompt_names_arg.strip():
        return available
    wanted = [p.strip() for p in prompt_names_arg.split(",") if p.strip()]
    bad = [p for p in wanted if p not in PROMPT_VARIANTS]
    if bad:
        raise ValueError(f"Unknown prompt names: {bad}. Available: {available}")
    return wanted


def main() -> int:
    args = parse_args()
    prompt_names = _select_prompts(args.prompt_names)

    files = collect_veribench_files(
        veribench_root=args.veribench_root,
        max_files=args.max_files,
        seed=args.seed,
        append_veribench_root=args.append_veribench_root,
        append_max_files=args.append_max_files,
    )
    if not files:
        print(f"ERROR: no .lean files found under {args.veribench_root}")
        return 1

    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("EXP 9: Judge Stability (P4)")
    print(
        f"model={args.model} judge_mode={args.judge_mode} repeats={args.n_repeats} "
        f"files={len(files)} prompts={len(prompt_names)}"
    )
    print(f"veribench_root={args.veribench_root}")
    print(f"append_veribench_root={args.append_veribench_root} append_max_files={args.append_max_files}")
    print(f"prompts={prompt_names}")
    print("=" * 72)

    detail_rows: List[dict] = []
    repeat_rows: List[dict] = []

    # key=(split|file|variant_type) -> prompt -> score_mean
    score_by_item_prompt: Dict[str, Dict[str, float]] = {}
    labels_by_item_prompt: Dict[str, Dict[str, str]] = {}

    for i, fpath in enumerate(files, start=1):
        code = fpath.read_text(encoding="utf-8", errors="ignore")
        rel = _relative_display_path(
            fpath,
            primary_root=args.veribench_root,
            append_root=args.append_veribench_root if args.append_max_files > 0 else None,
        )
        split = _infer_split(fpath)
        print(f"[{i}/{len(files)}] {rel}")

        candidates = [{"variant_type": "ORIGINAL", "code": code}] + generate_variants(code)
        for cand in candidates:
            variant_type = str(cand["variant_type"])
            cand_code = str(cand["code"])
            item_key = f"{split}|{rel}|{variant_type}"
            score_by_item_prompt.setdefault(item_key, {})
            labels_by_item_prompt.setdefault(item_key, {})

            for prompt_name in prompt_names:
                prompt_template = PROMPT_VARIANTS[prompt_name]
                result = _score_pair(
                    generated_theorem=cand_code,
                    reference_impl=code,
                    model=args.model,
                    n_repeats=args.n_repeats,
                    prompt_template=prompt_template,
                    cache_namespace=(
                        f"exp9_stability:{args.judge_mode}:r{args.n_repeats}:{prompt_name}:{variant_type}"
                    ),
                    judge_mode=args.judge_mode,
                )

                mean_score = float(result["mean"])
                std_score = float(result["std"])
                label = score_to_label(mean_score)
                score_by_item_prompt[item_key][prompt_name] = mean_score
                labels_by_item_prompt[item_key][prompt_name] = label

                detail_rows.append(
                    {
                        "split": split,
                        "file": str(rel),
                        "variant_type": variant_type,
                        "prompt_name": prompt_name,
                        "score_mean": round(mean_score, 6),
                        "score_std": round(std_score, 6),
                        "label": label,
                        "cached": bool(result.get("cached", False)),
                    }
                )

                scores = [float(s) for s in result.get("scores", [])]
                for ridx, rscore in enumerate(scores):
                    repeat_rows.append(
                        {
                            "split": split,
                            "file": str(rel),
                            "variant_type": variant_type,
                            "prompt_name": prompt_name,
                            "repeat_idx": ridx,
                            "repeat_score": round(rscore, 6),
                        }
                    )

    # Per-item dispersion across prompts.
    per_item_prompt_dispersion: List[dict] = []
    flip_flags: List[int] = []
    for item_key in sorted(score_by_item_prompt.keys()):
        vals = [score_by_item_prompt[item_key][p] for p in prompt_names if p in score_by_item_prompt[item_key]]
        labs = [labels_by_item_prompt[item_key][p] for p in prompt_names if p in labels_by_item_prompt[item_key]]
        if not vals:
            continue
        item_std = statistics.stdev(vals) if len(vals) > 1 else 0.0
        flip = len(set(labs)) > 1
        flip_flags.append(1 if flip else 0)
        split, rel, variant_type = item_key.split("|", 2)
        per_item_prompt_dispersion.append(
            {
                "split": split,
                "file": rel,
                "variant_type": variant_type,
                "score_std_across_prompts": round(float(item_std), 6),
                "score_min_across_prompts": round(float(min(vals)), 6),
                "score_max_across_prompts": round(float(max(vals)), 6),
                "n_unique_labels": int(len(set(labs))),
                "label_flip": bool(flip),
            }
        )

    # Prompt pairwise metrics.
    prompt_pairwise: List[dict] = []
    label_order = ["fail", "weak", "partial", "mostly", "equivalent"]
    item_ids = sorted(score_by_item_prompt.keys())
    for a, b in combinations(prompt_names, 2):
        xs: List[float] = []
        ys: List[float] = []
        xl: List[str] = []
        yl: List[str] = []
        for item_id in item_ids:
            row_s = score_by_item_prompt[item_id]
            row_l = labels_by_item_prompt[item_id]
            if a in row_s and b in row_s:
                xs.append(float(row_s[a]))
                ys.append(float(row_s[b]))
                xl.append(str(row_l[a]))
                yl.append(str(row_l[b]))
        if not xs:
            continue
        rho, pval = spearman_r(xs, ys)
        kappa = cohen_kappa(xl, yl, label_order)
        mad = sum(abs(x - y) for x, y in zip(xs, ys)) / max(1, len(xs))
        prompt_pairwise.append(
            {
                "a": a,
                "b": b,
                "n_items": len(xs),
                "spearman_r": round(float(rho), 6),
                "spearman_p": round(float(pval), 6),
                "cohen_kappa": round(float(kappa), 6),
                "mean_abs_diff": round(float(mad), 6),
            }
        )

    # Invariance rows: compare each variant against ORIGINAL for same file+prompt.
    # Build lookup: (split,file,prompt,variant) -> score
    lookup: Dict[Tuple[str, str, str, str], float] = {}
    for r in detail_rows:
        key = (str(r["split"]), str(r["file"]), str(r["prompt_name"]), str(r["variant_type"]))
        lookup[key] = float(r["score_mean"])

    invariance_rows: List[dict] = []
    unique_files = sorted({(str(r["split"]), str(r["file"])) for r in detail_rows})
    for split, rel in unique_files:
        for prompt_name in prompt_names:
            base_key = (split, rel, prompt_name, "ORIGINAL")
            if base_key not in lookup:
                continue
            base = lookup[base_key]
            for vt in ["RENAME", "REORDER", "STYLE", "ALPHA"]:
                key = (split, rel, prompt_name, vt)
                if key not in lookup:
                    continue
                gap = abs(lookup[key] - base)
                invariance_rows.append(
                    {
                        "split": split,
                        "file": rel,
                        "prompt_name": prompt_name,
                        "variant_type": vt,
                        "score_original": round(base, 6),
                        "score_variant": round(float(lookup[key]), 6),
                        "abs_gap_vs_original": round(float(gap), 6),
                    }
                )

    # Aggregate prompt-level repeatability.
    prompt_repeatability_rows: List[dict] = []
    for p in prompt_names:
        vals = [float(r["score_std"]) for r in detail_rows if str(r["prompt_name"]) == p]
        if not vals:
            continue
        prompt_repeatability_rows.append(
            {
                "prompt_name": p,
                "n_cells": len(vals),
                "mean_repeat_std": round(float(statistics.mean(vals)), 6),
                "median_repeat_std": round(float(statistics.median(vals)), 6),
                "p90_repeat_std": round(float(sorted(vals)[int(0.9 * (len(vals) - 1))]), 6),
            }
        )

    # Aggregate invariance by variant.
    invariance_by_variant: Dict[str, dict] = {}
    for vt in ["RENAME", "REORDER", "STYLE", "ALPHA"]:
        vals = [float(r["abs_gap_vs_original"]) for r in invariance_rows if str(r["variant_type"]) == vt]
        if vals:
            invariance_by_variant[vt] = {
                "n": len(vals),
                "mean_abs_gap": round(float(statistics.mean(vals)), 6),
                "median_abs_gap": round(float(statistics.median(vals)), 6),
            }

    mean_item_std = statistics.mean(
        [float(r["score_std_across_prompts"]) for r in per_item_prompt_dispersion]
    ) if per_item_prompt_dispersion else 0.0
    flip_rate = (sum(flip_flags) / max(1, len(flip_flags))) if flip_flags else 0.0
    min_pairwise_spearman = min((float(r["spearman_r"]) for r in prompt_pairwise), default=0.0)
    min_pairwise_kappa = min((float(r["cohen_kappa"]) for r in prompt_pairwise), default=0.0)
    cronbach = _cronbach_alpha(score_by_item_prompt, prompt_names)
    mean_repeat_std = statistics.mean([float(r["score_std"]) for r in detail_rows]) if detail_rows else 0.0

    summary = {
        "experiment": "exp9_stability",
        "model": args.model,
        "judge_mode": args.judge_mode,
        "n_repeats": args.n_repeats,
        "n_files": len(files),
        "append_max_files": args.append_max_files,
        "n_prompts": len(prompt_names),
        "prompt_names": prompt_names,
        "n_cells": len(detail_rows),
        "n_repeat_rows": len(repeat_rows),
        "n_item_variants": len(score_by_item_prompt),
        "stability": {
            "mean_repeat_std": round(float(mean_repeat_std), 6),
            "mean_score_std_across_prompts": round(float(mean_item_std), 6),
            "flip_rate": round(float(flip_rate), 6),
            "min_pairwise_spearman": round(float(min_pairwise_spearman), 6),
            "min_pairwise_kappa": round(float(min_pairwise_kappa), 6),
            "cronbach_alpha": round(float(cronbach), 6),
        },
        "invariance_by_variant": invariance_by_variant,
        "notes": "Use one judge_mode per run for fair comparisons.",
    }

    _write_csv(args.results_dir / "detail_rows.csv", detail_rows)
    _write_csv(args.results_dir / "repeat_rows.csv", repeat_rows)
    _write_csv(args.results_dir / "per_item_prompt_dispersion.csv", per_item_prompt_dispersion)
    _write_csv(args.results_dir / "prompt_pairwise.csv", prompt_pairwise)
    _write_csv(args.results_dir / "invariance_rows.csv", invariance_rows)
    _write_csv(args.results_dir / "prompt_repeatability.csv", prompt_repeatability_rows)
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _make_figures(
        figures_dir=args.figures_dir,
        detail_rows=detail_rows,
        prompt_names=prompt_names,
        prompt_pairwise=prompt_pairwise,
        per_item_prompt_dispersion=per_item_prompt_dispersion,
        invariance_rows=invariance_rows,
    )

    print("\nSummary")
    print(f"  mean_repeat_std={mean_repeat_std:.4f}")
    print(f"  mean_score_std_across_prompts={mean_item_std:.4f}")
    print(f"  flip_rate={flip_rate:.4f}")
    print(f"  min_pairwise_spearman={min_pairwise_spearman:.4f}")
    print(f"  min_pairwise_kappa={min_pairwise_kappa:.4f}")
    print(f"  cronbach_alpha={cronbach:.4f}")
    print(f"  wrote results: {args.results_dir}")
    print(f"  wrote figures: {args.figures_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
