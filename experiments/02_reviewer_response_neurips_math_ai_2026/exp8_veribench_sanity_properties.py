#!/usr/bin/env python3
"""
Experiment 8: VeriBench-wide judge sanity properties.

Scales the paper's three sanity-check figures from a single my_add example to all
available VeriBench Lean artifacts:
  1) Identity (syntactic variants vs reference)
  2) Monotonicity to semantic bugs (generated bug ladder)
  3) Monotonicity to missing specs (generated ablation ladder)

Outputs:
  - results/veribench_sanity_properties/summary.json
  - results/veribench_sanity_properties/identity_rows.csv
  - results/veribench_sanity_properties/bug_ladder_rows.csv
  - results/veribench_sanity_properties/missing_ladder_rows.csv
  - figures/identity_property.png
  - figures/monotonicity_bugs.png
  - figures/monotonicity_missing_specs.png
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import statistics
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

EXP_DIR = Path(__file__).parent
REPO_ROOT = EXP_DIR.parents[1]
sys.path.insert(0, str(EXP_DIR))

from utils.judge_caller import judge
from utils.metrics import pearson_r, spearman_r, weak_monotonicity_pct
from utils.variant_generator import generate_variants


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scale identity + monotonicity sanity checks across VeriBench")
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--n-repeats", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-files", type=int, default=0, help="0 means all VeriBench Lean files")
    parser.add_argument(
        "--veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=EXP_DIR / "results" / "veribench_sanity_properties",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=EXP_DIR / "figures",
    )
    parser.add_argument(
        "--paper-fig-dir",
        type=Path,
        default=REPO_ROOT / "paper_latex" / "NeurIPS_2025" / "figures",
    )
    parser.add_argument(
        "--skip-paper-copy",
        action="store_true",
        help="If set, do not copy generated PNGs into paper figures directory",
    )
    return parser.parse_args()


def _infer_split(path: Path) -> str:
    parts = list(path.parts)
    if "easy_set" in parts:
        return "easy"
    if "cs_set" in parts:
        return "cs"
    if "humaneval_set" in parts:
        return "humaneval"
    if "real_code" in parts:
        return "real_code"
    if "security_6858" in parts:
        return "security_6858"
    if "security_python" in parts:
        return "security_python"
    return "other"


def collect_veribench_files(veribench_root: Path, max_files: int, seed: int) -> List[Path]:
    if not veribench_root.exists():
        return []

    skip_names = {"Common.lean", "Prelude.lean", "veribench.lean", "sandbox.lean", "tmp.lean", "55.lean"}
    all_files = [
        p for p in veribench_root.rglob("*.lean")
        if p.is_file() and p.name not in skip_names
    ]
    all_files = sorted(all_files)

    if max_files > 0 and len(all_files) > max_files:
        rng = random.Random(seed)
        rng.shuffle(all_files)
        all_files = sorted(all_files[:max_files])

    return all_files


def _replace_first(pattern: str, repl: str, text: str, flags: int = 0) -> Tuple[str, bool]:
    out, n = re.subn(pattern, repl, text, count=1, flags=flags)
    return out, n > 0


def _extract_theorem_blocks(text: str) -> List[Tuple[int, int]]:
    # Heuristic theorem/lemma block extraction.
    pat = re.compile(
        r"(?ms)^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b.*?(?=^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b|\Z)"
    )
    return [(m.start(), m.end()) for m in pat.finditer(text)]


def _remove_last_theorem_block(text: str) -> Tuple[str, bool]:
    spans = _extract_theorem_blocks(text)
    if not spans:
        return text, False
    start, end = spans[-1]
    return text[:start] + "\n" + text[end:], True


def build_bug_ladder(code: str) -> List[str]:
    """5-level semantic bug ladder (0=clean, 4=maximally broken)."""
    ladder = [code]

    level1 = ladder[-1]
    changed = False
    for pat, repl in [
        (r"(?<!:)(?<!=)=(?!=)", "≤"),
        (r"\b>\b", "≥"),
        (r"\bAnd\b", "Or"),
        (r"∧", "∨"),
    ]:
        level1, changed = _replace_first(pat, repl, level1)
        if changed:
            break
    if not changed:
        level1 += "\n-- bug_level_1"
    ladder.append(level1)

    level2 = ladder[-1]
    level2, changed = _remove_last_theorem_block(level2)
    if not changed:
        level2, changed = _replace_first(r"\bTrue\b", "False", level2)
    if not changed:
        level2 += "\n-- bug_level_2"
    ladder.append(level2)

    level3 = ladder[-1]
    level3, changed = _replace_first(r"(?<!:)(?<!=)=(?!=)", "<", level3)
    if not changed:
        level3, changed = _replace_first(r"∧", "∨", level3)
    if not changed:
        level3 += "\n-- bug_level_3"
    ladder.append(level3)

    # Level 4: force theorem claims to True and proofs to trivial where possible.
    level4 = ladder[-1]
    theorem_sig = re.compile(r"(?ms)(^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b[^:]*:\s*)(.*?)(\s*:=)")

    def _to_true(match: re.Match[str]) -> str:
        return f"{match.group(1)}True{match.group(3)}"

    level4, n = theorem_sig.subn(_to_true, level4)
    if n > 0:
        level4 = re.sub(r"(?ms):=.*$", ":= trivial", level4)
    else:
        level4 += "\n-- bug_level_4\nexample : True := trivial\n"
    ladder.append(level4)

    return ladder


def _remove_fraction_of_theorems(text: str, frac: float) -> Tuple[str, bool]:
    spans = _extract_theorem_blocks(text)
    if not spans:
        return text, False

    n_remove = max(1, int(round(frac * len(spans)))) if frac > 0 else 0
    n_remove = min(n_remove, len(spans))
    if n_remove <= 0:
        return text, False

    # Remove from the end to keep early core definitions intact.
    keep_until = len(spans) - n_remove
    keep_spans = spans[:keep_until]

    if not keep_spans:
        # Remove all theorem blocks.
        start = spans[0][0]
        return text[:start], True

    pieces = []
    cursor = 0
    keep_idx = set(range(keep_until))
    for i, (s, e) in enumerate(spans):
        if i in keep_idx:
            pieces.append(text[cursor:e])
        else:
            pieces.append(text[cursor:s])
        cursor = e
    pieces.append(text[cursor:])
    return "".join(pieces), True


def build_missing_specs_ladder(code: str) -> List[str]:
    """5-level spec-ablation ladder (0=no removal, 4=aggressive removal)."""
    ladder = [code]
    for frac in [0.25, 0.50, 0.75, 1.0]:
        prev = ladder[-1]
        cur, changed = _remove_fraction_of_theorems(prev, frac)
        if not changed:
            # Fallback for files without theorem blocks: progressively truncate tail lines.
            lines = prev.splitlines()
            keep = max(1, int(len(lines) * (1.0 - frac)))
            cur = "\n".join(lines[:keep]) + f"\n-- missing_specs_level_{int(frac*100)}"
        ladder.append(cur)
    return ladder


def _write_csv(path: Path, rows: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _make_identity_figure(rows: Sequence[dict], out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    if not rows:
        return

    variants = [r["variant_type"] for r in rows]
    scores = np.array([float(r["judge_mean"]) for r in rows], dtype=float)
    xs = np.arange(len(rows))

    palette = {
        "RENAME": "#1f77b4",
        "REORDER": "#ff7f0e",
        "STYLE": "#2ca02c",
        "ALPHA": "#d62728",
    }
    colors = [palette.get(v, "#7f7f7f") for v in variants]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(xs, scores, s=12, alpha=0.7, c=colors)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.axhline(float(np.mean(scores)), color="#444444", linestyle=":", linewidth=1)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Variant Pair Index")
    ax.set_ylabel("Judge Score")
    ax.set_title(f"Identity over VeriBench variants (n={len(rows)}, mean={np.mean(scores):.3f})")

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", label=k, markerfacecolor=v, markersize=6)
        for k, v in palette.items()
    ]
    ax.legend(handles=handles, fontsize=9, ncol=4, loc="lower left")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def _make_ladder_figure(
    ladders: Sequence[Sequence[float]],
    spearman_rho: float,
    weak_mono: float,
    title: str,
    out_png: Path,
) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    if not ladders:
        return

    arr = np.array(ladders, dtype=float)
    levels = np.arange(arr.shape[1])
    mean_scores = arr.mean(axis=0)

    fig, ax = plt.subplots(figsize=(6.2, 4.5))
    for row in arr:
        ax.plot(levels, row, color="lightgray", linewidth=0.8, alpha=0.6)
    ax.plot(levels, mean_scores, color="#1f77b4", linewidth=2.5, marker="o", label="Mean")

    ax.set_xticks(levels)
    ax.set_xticklabels([f"L{i}" for i in levels])
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Degradation Level")
    ax.set_ylabel("Judge Score")
    ax.set_title(f"{title}\nSpearman={spearman_rho:.3f}, Weak Mono={weak_mono:.1f}%")
    ax.legend(fontsize=9)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def _copy_if_needed(src: Path, dst_dir: Path, skip: bool) -> None:
    if skip:
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    dst.write_bytes(src.read_bytes())


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)

    files = collect_veribench_files(args.veribench_root, args.max_files, args.seed)
    if not files:
        print(f"ERROR: no .lean files found under {args.veribench_root}")
        return 1

    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("EXP 8: VeriBench-wide Identity + Monotonicity Sanity Properties")
    print(f"model={args.model} repeats={args.n_repeats} files={len(files)}")
    print(f"veribench_root={args.veribench_root}")
    print("=" * 72)

    identity_rows: List[dict] = []
    bug_rows: List[dict] = []
    missing_rows: List[dict] = []

    bug_ladders: List[List[float]] = []
    missing_ladders: List[List[float]] = []

    flat_bug_levels: List[int] = []
    flat_bug_scores: List[float] = []
    flat_missing_levels: List[int] = []
    flat_missing_scores: List[float] = []

    for i, fpath in enumerate(files, start=1):
        code = fpath.read_text(encoding="utf-8", errors="ignore")
        rel = fpath.relative_to(args.veribench_root)
        split = _infer_split(fpath)
        print(f"[{i}/{len(files)}] {rel}")

        variants = generate_variants(code)
        for v in variants:
            result = judge(
                generated_theorem=v["code"],
                reference_impl=code,
                model=args.model,
                n_repeats=args.n_repeats,
                cache_namespace="exp8_identity",
            )
            identity_rows.append(
                {
                    "split": split,
                    "file": str(rel),
                    "variant_type": v["variant_type"],
                    "judge_mean": round(float(result["mean"]), 6),
                    "judge_std": round(float(result["std"]), 6),
                    "cached": bool(result.get("cached", False)),
                }
            )

        bug_codes = build_bug_ladder(code)
        bug_scores: List[float] = []
        for level, cand in enumerate(bug_codes):
            result = judge(
                generated_theorem=cand,
                reference_impl=code,
                model=args.model,
                n_repeats=args.n_repeats,
                cache_namespace="exp8_bug_ladder",
            )
            s = float(result["mean"])
            bug_scores.append(s)
            flat_bug_levels.append(level)
            flat_bug_scores.append(s)
            bug_rows.append(
                {
                    "split": split,
                    "file": str(rel),
                    "level": level,
                    "judge_mean": round(s, 6),
                    "judge_std": round(float(result["std"]), 6),
                    "cached": bool(result.get("cached", False)),
                }
            )
        bug_ladders.append(bug_scores)

        missing_codes = build_missing_specs_ladder(code)
        missing_scores: List[float] = []
        for level, cand in enumerate(missing_codes):
            result = judge(
                generated_theorem=cand,
                reference_impl=code,
                model=args.model,
                n_repeats=args.n_repeats,
                cache_namespace="exp8_missing_ladder",
            )
            s = float(result["mean"])
            missing_scores.append(s)
            flat_missing_levels.append(level)
            flat_missing_scores.append(s)
            missing_rows.append(
                {
                    "split": split,
                    "file": str(rel),
                    "level": level,
                    "judge_mean": round(s, 6),
                    "judge_std": round(float(result["std"]), 6),
                    "cached": bool(result.get("cached", False)),
                }
            )
        missing_ladders.append(missing_scores)

    # Aggregate metrics
    identity_scores = [float(r["judge_mean"]) for r in identity_rows]
    id_mean = statistics.mean(identity_scores) if identity_scores else 0.0
    id_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0

    bug_spear, bug_spear_p = spearman_r(flat_bug_levels, flat_bug_scores)
    bug_pear, bug_pear_p = pearson_r(flat_bug_levels, flat_bug_scores)
    bug_weak = weak_monotonicity_pct(bug_ladders)

    miss_spear, miss_spear_p = spearman_r(flat_missing_levels, flat_missing_scores)
    miss_pear, miss_pear_p = pearson_r(flat_missing_levels, flat_missing_scores)
    miss_weak = weak_monotonicity_pct(missing_ladders)

    summary = {
        "experiment": "exp8_veribench_sanity_properties",
        "model": args.model,
        "n_repeats": args.n_repeats,
        "n_files": len(files),
        "identity": {
            "n_pairs": len(identity_rows),
            "mean": round(id_mean, 6),
            "std": round(id_std, 6),
        },
        "monotonicity_bugs": {
            "n_points": len(flat_bug_scores),
            "spearman_r": round(float(bug_spear), 6),
            "spearman_p": round(float(bug_spear_p), 6),
            "pearson_r": round(float(bug_pear), 6),
            "pearson_p": round(float(bug_pear_p), 6),
            "weak_monotonicity_pct": round(float(bug_weak), 6),
        },
        "monotonicity_missing_specs": {
            "n_points": len(flat_missing_scores),
            "spearman_r": round(float(miss_spear), 6),
            "spearman_p": round(float(miss_spear_p), 6),
            "pearson_r": round(float(miss_pear), 6),
            "pearson_p": round(float(miss_pear_p), 6),
            "weak_monotonicity_pct": round(float(miss_weak), 6),
        },
    }

    # Write tables
    _write_csv(args.results_dir / "identity_rows.csv", identity_rows)
    _write_csv(args.results_dir / "bug_ladder_rows.csv", bug_rows)
    _write_csv(args.results_dir / "missing_ladder_rows.csv", missing_rows)
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Write paper-compatible figure names
    fig_identity = args.figures_dir / "identity_property.png"
    fig_bugs = args.figures_dir / "monotonicity_bugs.png"
    fig_missing = args.figures_dir / "monotonicity_missing_specs.png"

    _make_identity_figure(identity_rows, fig_identity)
    _make_ladder_figure(bug_ladders, bug_spear, bug_weak, "Monotonicity vs Bugs (VeriBench-wide)", fig_bugs)
    _make_ladder_figure(
        missing_ladders,
        miss_spear,
        miss_weak,
        "Monotonicity vs Missing Specs (VeriBench-wide)",
        fig_missing,
    )

    _copy_if_needed(fig_identity, args.paper_fig_dir, args.skip_paper_copy)
    _copy_if_needed(fig_bugs, args.paper_fig_dir, args.skip_paper_copy)
    _copy_if_needed(fig_missing, args.paper_fig_dir, args.skip_paper_copy)

    print("\nSummary")
    print(f"  identity mean/std: {id_mean:.4f} / {id_std:.4f}")
    print(f"  bugs:    Spearman={bug_spear:.4f}, Pearson={bug_pear:.4f}, weak_mono={bug_weak:.1f}%")
    print(f"  missing: Spearman={miss_spear:.4f}, Pearson={miss_pear:.4f}, weak_mono={miss_weak:.1f}%")
    print(f"  wrote results: {args.results_dir}")
    print(f"  wrote figures: {args.figures_dir}")
    if not args.skip_paper_copy:
        print(f"  copied paper figures to: {args.paper_fig_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
