#!/usr/bin/env python3
"""
Run human-vs-judge correlation analysis using Ethan's hand labels.

What it does:
1) Normalizes inconsistent CSV schemas in experiments/ethan_hand_labels
2) Joins each label row to gold/candidate Lean files
3) Computes judge scores for all joinable rows
4) Reports Pearson/Spearman/Kendall/R^2 overall and per category
5) Computes ICC(2,1) and ICC(2,k) when multiple raters are present
6) Generates plots and CSV/JSON outputs
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
JUDGE_UTILS_DIR = REPO_ROOT / "experiments" / "02_neurips_reviews"
sys.path.insert(0, str(JUDGE_UTILS_DIR))


@dataclass
class LabelRow:
    split: str
    gold_ref: str
    candidate_file: str
    human_score: float
    rater_id: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Human vs judge correlation with Ethan labels")
    p.add_argument("--labels-dir", type=Path, default=REPO_ROOT / "experiments" / "ethan_hand_labels")
    p.add_argument("--generated-dir", type=Path, default=REPO_ROOT / "data" / "generated_agents")
    p.add_argument("--gold-root", type=Path, default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench")
    p.add_argument("--out-dir", type=Path, default=REPO_ROOT / "experiments" / "03_human_validation" / "results" / "ethan_human_vs_judge")
    p.add_argument("--model", type=str, default="gpt-4o-mini")
    p.add_argument("--n-repeats", type=int, default=3)
    p.add_argument("--max-rows", type=int, default=0, help="0 means use all joinable rows")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cache-namespace", type=str, default="ethan_human_vs_judge_v1")
    p.add_argument("--bootstrap-iters", type=int, default=2000)
    return p.parse_args()


def _clean(s: Optional[str]) -> str:
    return (s or "").strip().strip("\ufeff")


def _parse_score(s: str) -> Optional[float]:
    s = _clean(s)
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def _pick(row: Dict[str, str], *keys: str) -> str:
    # robust against tabs/spaces in header names
    normalized = {k.strip().lower().replace("\t", ""): v for k, v in row.items()}
    for key in keys:
        k = key.strip().lower().replace("\t", "")
        if k in normalized:
            v = _clean(normalized[k])
            if v:
                return v
    return ""


def _load_labels(labels_dir: Path) -> List[LabelRow]:
    import csv

    rows: List[LabelRow] = []
    for csv_path in sorted(labels_dir.glob("*.csv")):
        split = csv_path.stem
        with csv_path.open(newline="") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                gold_ref = _pick(raw, "gold ref", "gold")
                candidate = _pick(raw, "agent item", "candidate")
                score_str = _pick(raw, "score", "human_score")
                score = _parse_score(score_str)
                # Optional multi-rater support if columns exist
                rater_id = _pick(raw, "rater_id", "rater", "annotator") or "ethan"
                if not gold_ref or not candidate or score is None:
                    continue
                rows.append(LabelRow(split=split, gold_ref=gold_ref, candidate_file=candidate, human_score=score, rater_id=rater_id))
    return rows


def _resolve_gold(gold_root: Path, split: str, gold_ref: str) -> Optional[Path]:
    base = gold_root / split
    p = base / gold_ref
    if p.exists():
        return p
    # security split can nest under safe/
    for q in base.rglob(gold_ref):
        return q
    return None


def _agent_id_from_candidate(candidate_file: str) -> str:
    m = re.search(r"__agent(\d+)\.lean$", candidate_file)
    if m:
        return f"agent{m.group(1)}"
    return "unknown"


def _bootstrap_ci(xs: Sequence[float], ys: Sequence[float], metric: str, n_boot: int = 2000) -> Tuple[float, float]:
    import random
    from scipy.stats import pearsonr, spearmanr, kendalltau

    n = len(xs)
    if n < 3:
        return (float("nan"), float("nan"))

    vals: List[float] = []
    for _ in range(n_boot):
        idxs = [random.randrange(n) for _ in range(n)]
        bx = [xs[i] for i in idxs]
        by = [ys[i] for i in idxs]
        try:
            if metric == "pearson":
                v = float(pearsonr(bx, by).statistic)
            elif metric == "spearman":
                v = float(spearmanr(bx, by).statistic)
            elif metric == "kendall":
                v = float(kendalltau(bx, by).statistic)
            else:
                raise ValueError(metric)
            if math.isfinite(v):
                vals.append(v)
        except Exception:
            continue

    if not vals:
        return (float("nan"), float("nan"))
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return (float(lo), float(hi))


def _corr_stats(xs: Sequence[float], ys: Sequence[float], n_boot: int = 2000) -> Dict[str, float]:
    from scipy.stats import pearsonr, spearmanr, kendalltau

    if len(xs) < 3 or len(xs) != len(ys):
        return {
            "n": len(xs),
            "pearson_r": float("nan"),
            "pearson_p": float("nan"),
            "spearman_r": float("nan"),
            "spearman_p": float("nan"),
            "kendall_tau": float("nan"),
            "kendall_p": float("nan"),
            "r2": float("nan"),
            "pearson_ci_lo": float("nan"),
            "pearson_ci_hi": float("nan"),
            "spearman_ci_lo": float("nan"),
            "spearman_ci_hi": float("nan"),
            "kendall_ci_lo": float("nan"),
            "kendall_ci_hi": float("nan"),
        }

    pr = pearsonr(xs, ys)
    sr = spearmanr(xs, ys)
    kt = kendalltau(xs, ys)

    pr_lo, pr_hi = _bootstrap_ci(xs, ys, "pearson", n_boot)
    sr_lo, sr_hi = _bootstrap_ci(xs, ys, "spearman", n_boot)
    kt_lo, kt_hi = _bootstrap_ci(xs, ys, "kendall", n_boot)

    return {
        "n": len(xs),
        "pearson_r": float(pr.statistic),
        "pearson_p": float(pr.pvalue),
        "spearman_r": float(sr.statistic),
        "spearman_p": float(sr.pvalue),
        "kendall_tau": float(kt.statistic),
        "kendall_p": float(kt.pvalue),
        "r2": float(pr.statistic ** 2),
        "pearson_ci_lo": pr_lo,
        "pearson_ci_hi": pr_hi,
        "spearman_ci_lo": sr_lo,
        "spearman_ci_hi": sr_hi,
        "kendall_ci_lo": kt_lo,
        "kendall_ci_hi": kt_hi,
    }


def _compute_icc2(df) -> Dict[str, object]:
    """
    Compute ICC(2,1) and ICC(2,k) for absolute agreement on a two-way random-effects model.
    Requires columns: item_id, rater_id, human_score.
    """
    import pandas as pd
    import numpy as np

    needed = {"item_id", "rater_id", "human_score"}
    if not needed.issubset(df.columns):
        return {"available": False, "reason": "missing_columns"}

    wide = df.pivot_table(index="item_id", columns="rater_id", values="human_score", aggfunc="mean")
    wide = wide.dropna(axis=0, how="any")

    n, k = wide.shape
    if n < 3 or k < 2:
        return {
            "available": False,
            "reason": "need_at_least_3_items_and_2_raters",
            "n_items_complete": int(n),
            "n_raters": int(k),
        }

    x = wide.to_numpy(dtype=float)
    grand = np.mean(x)
    row_means = np.mean(x, axis=1)
    col_means = np.mean(x, axis=0)

    ss_rows = k * np.sum((row_means - grand) ** 2)
    ss_cols = n * np.sum((col_means - grand) ** 2)
    ss_total = np.sum((x - grand) ** 2)
    ss_err = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_cols = ss_cols / (k - 1)
    ms_err = ss_err / ((n - 1) * (k - 1))

    denom_21 = ms_rows + (k - 1) * ms_err + (k * (ms_cols - ms_err) / n)
    if abs(denom_21) < 1e-12:
        return {"available": False, "reason": "degenerate_variance", "n_items_complete": int(n), "n_raters": int(k)}

    icc21 = (ms_rows - ms_err) / denom_21

    denom_2k = ms_rows + (ms_cols - ms_err) / n
    if abs(denom_2k) < 1e-12:
        return {"available": False, "reason": "degenerate_variance", "n_items_complete": int(n), "n_raters": int(k)}

    icc2k = (ms_rows - ms_err) / denom_2k

    return {
        "available": True,
        "n_items_complete": int(n),
        "n_raters": int(k),
        "icc2_1": float(icc21),
        "icc2_k": float(icc2k),
    }


def _save_plots(df, out_dir: Path, split_metrics: Dict[str, Dict[str, float]], agent_metrics: Dict[str, Dict[str, float]]) -> None:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Overall scatter
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.scatter(df["human_score"], df["judge_score"], alpha=0.75)
    if len(df) > 1:
        z = np.polyfit(df["human_score"], df["judge_score"], 1)
        x = np.linspace(df["human_score"].min(), df["human_score"].max(), 100)
        ax.plot(x, z[0] * x + z[1], "r--", lw=1.5)
    ax.set_title("Human vs Judge (Overall)")
    ax.set_xlabel("Human score")
    ax.set_ylabel("Judge score")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_overall_scatter.png", dpi=180)
    plt.close(fig)

    # 2) Per-split scatter small multiples
    splits = sorted(df["split"].unique())
    cols = 3
    rows = int(math.ceil(len(splits) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 4.5 * rows))
    axes = np.array(axes).reshape(rows, cols)
    for i, split in enumerate(splits):
        r, c = divmod(i, cols)
        ax = axes[r, c]
        sdf = df[df["split"] == split]
        ax.scatter(sdf["human_score"], sdf["judge_score"], alpha=0.75)
        if len(sdf) > 1:
            z = np.polyfit(sdf["human_score"], sdf["judge_score"], 1)
            x = np.linspace(sdf["human_score"].min(), sdf["human_score"].max(), 100)
            ax.plot(x, z[0] * x + z[1], "r--", lw=1.25)
        stats = split_metrics.get(split, {})
        ax.set_title(f"{split} (n={len(sdf)}, r={stats.get('pearson_r', float('nan')):.2f})")
        ax.set_xlabel("Human")
        ax.set_ylabel("Judge")
        ax.grid(True, alpha=0.25)
    for j in range(len(splits), rows * cols):
        r, c = divmod(j, cols)
        axes[r, c].axis("off")
    fig.suptitle("Human vs Judge by Split", y=1.01)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_per_split_scatter.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # 3) Correlation bars by split
    split_names = sorted(split_metrics.keys())
    metrics = ["pearson_r", "spearman_r", "kendall_tau", "r2"]
    x = np.arange(len(split_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(11, 5.5))
    for i, m in enumerate(metrics):
        vals = [split_metrics[s].get(m, float("nan")) for s in split_names]
        ax.bar(x + (i - 1.5) * width, vals, width=width, label=m)
    ax.set_xticks(x)
    ax.set_xticklabels(split_names, rotation=20)
    ax.set_title("Correlation Metrics by Split")
    ax.set_ylabel("Value")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "fig_per_split_correlations.png", dpi=180)
    plt.close(fig)

    # 4) Correlation bars by agent category
    agent_names = sorted(agent_metrics.keys())
    if agent_names:
        x = np.arange(len(agent_names))
        fig, ax = plt.subplots(figsize=(9, 5.5))
        for i, m in enumerate(metrics):
            vals = [agent_metrics[a].get(m, float("nan")) for a in agent_names]
            ax.bar(x + (i - 1.5) * width, vals, width=width, label=m)
        ax.set_xticks(x)
        ax.set_xticklabels(agent_names)
        ax.set_title("Correlation Metrics by Agent Category")
        ax.set_ylabel("Value")
        ax.grid(True, axis="y", alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "fig_per_agent_correlations.png", dpi=180)
        plt.close(fig)


def main() -> int:
    import random
    import pandas as pd
    from utils.judge_caller import judge

    args = parse_args()
    random.seed(args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Human vs Judge Correlation (Ethan Labels)")
    print(f"labels_dir={args.labels_dir}")
    print(f"generated_dir={args.generated_dir}")
    print(f"gold_root={args.gold_root}")
    print(f"model={args.model} repeats={args.n_repeats}")
    print("=" * 72)

    label_rows = _load_labels(args.labels_dir)
    if not label_rows:
        print("ERROR: no label rows loaded")
        return 1

    normalized_records: List[Dict[str, object]] = []
    joinable_records: List[Dict[str, object]] = []

    for r in label_rows:
        candidate_path = args.generated_dir / r.candidate_file
        gold_path = _resolve_gold(args.gold_root, r.split, r.gold_ref)
        agent_id = _agent_id_from_candidate(r.candidate_file)

        rec = {
            "split": r.split,
            "gold_ref": r.gold_ref,
            "candidate_file": r.candidate_file,
            "human_score": float(r.human_score),
            "rater_id": r.rater_id,
            "agent_id": agent_id,
            "candidate_path": str(candidate_path),
            "gold_path": str(gold_path) if gold_path else "",
            "candidate_exists": bool(candidate_path.exists()),
            "gold_exists": bool(gold_path is not None),
            "joinable": bool(candidate_path.exists() and gold_path is not None),
        }
        normalized_records.append(rec)
        if rec["joinable"]:
            joinable_records.append(rec)

    if args.max_rows and args.max_rows > 0:
        joinable_records = joinable_records[: args.max_rows]

    print(f"Loaded label rows: {len(label_rows)}")
    print(f"Joinable rows: {len(joinable_records)}")

    if not joinable_records:
        print("ERROR: no joinable rows")
        pd.DataFrame(normalized_records).to_csv(args.out_dir / "normalized_rows.csv", index=False)
        return 1

    scored_rows: List[Dict[str, object]] = []
    for i, rec in enumerate(joinable_records, start=1):
        gold_path = Path(str(rec["gold_path"]))
        candidate_path = Path(str(rec["candidate_path"]))
        gold_text = gold_path.read_text()
        candidate_text = candidate_path.read_text()

        result = judge(
            generated_theorem=candidate_text,
            reference_impl=gold_text,
            model=args.model,
            n_repeats=args.n_repeats,
            cache_namespace=args.cache_namespace,
        )

        row = dict(rec)
        row.update(
            {
                "judge_score": float(result["mean"]),
                "judge_std": float(result["std"]),
                "judge_scores": json.dumps(result.get("scores", [])),
                "cached": bool(result.get("cached", False)),
                "judge_reasoning": str(result.get("reasoning", "")),
                "item_id": f"{rec['split']}::{rec['gold_ref']}::{rec['candidate_file']}",
            }
        )
        scored_rows.append(row)
        print(f"[{i}/{len(joinable_records)}] {rec['split']} | {rec['candidate_file']} | human={rec['human_score']} judge={row['judge_score']:.3f} cached={row['cached']}")

    # Save row-level data
    import pandas as pd
    norm_df = pd.DataFrame(normalized_records)
    scored_df = pd.DataFrame(scored_rows)
    norm_df.to_csv(args.out_dir / "normalized_rows.csv", index=False)
    scored_df.to_csv(args.out_dir / "scored_rows.csv", index=False)

    # Correlations overall and per category
    overall = _corr_stats(scored_df["human_score"].tolist(), scored_df["judge_score"].tolist(), args.bootstrap_iters)

    per_split: Dict[str, Dict[str, float]] = {}
    for split, sdf in scored_df.groupby("split"):
        per_split[split] = _corr_stats(sdf["human_score"].tolist(), sdf["judge_score"].tolist(), args.bootstrap_iters)

    per_agent: Dict[str, Dict[str, float]] = {}
    for agent, sdf in scored_df.groupby("agent_id"):
        per_agent[agent] = _corr_stats(sdf["human_score"].tolist(), sdf["judge_score"].tolist(), args.bootstrap_iters)

    icc = _compute_icc2(scored_df[["item_id", "rater_id", "human_score"]])

    summary = {
        "experiment": "ethan_human_vs_judge",
        "model": args.model,
        "n_repeats": args.n_repeats,
        "n_label_rows": len(label_rows),
        "n_joinable_rows": len(joinable_records),
        "n_scored_rows": len(scored_rows),
        "overall": overall,
        "per_split": per_split,
        "per_agent_category": per_agent,
        "icc": icc,
        "missing_candidates": sorted(
            {r["candidate_file"] for r in normalized_records if not r["candidate_exists"]}
        ),
        "missing_gold_refs": sorted(
            {f"{r['split']}/{r['gold_ref']}" for r in normalized_records if not r["gold_exists"]}
        ),
    }

    with (args.out_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    # Human-readable category tables
    split_rows = []
    for k, v in sorted(per_split.items()):
        split_rows.append({"category": k, **v})
    pd.DataFrame(split_rows).to_csv(args.out_dir / "per_split_correlations.csv", index=False)

    agent_rows = []
    for k, v in sorted(per_agent.items()):
        agent_rows.append({"category": k, **v})
    pd.DataFrame(agent_rows).to_csv(args.out_dir / "per_agent_correlations.csv", index=False)

    _save_plots(scored_df, args.out_dir, per_split, per_agent)

    print("\n=== Overall Correlations ===")
    print(f"n={overall['n']}")
    print(f"Pearson r={overall['pearson_r']:.4f} p={overall['pearson_p']:.4g} CI=[{overall['pearson_ci_lo']:.4f},{overall['pearson_ci_hi']:.4f}]")
    print(f"Spearman r={overall['spearman_r']:.4f} p={overall['spearman_p']:.4g} CI=[{overall['spearman_ci_lo']:.4f},{overall['spearman_ci_hi']:.4f}]")
    print(f"Kendall tau={overall['kendall_tau']:.4f} p={overall['kendall_p']:.4g} CI=[{overall['kendall_ci_lo']:.4f},{overall['kendall_ci_hi']:.4f}]")
    print(f"R^2={overall['r2']:.4f}")

    print("\n=== Per Split ===")
    for split, stats in sorted(per_split.items()):
        print(f"{split:16s} n={stats['n']:>3d} | pearson={stats['pearson_r']:.3f} | spearman={stats['spearman_r']:.3f} | kendall={stats['kendall_tau']:.3f} | r2={stats['r2']:.3f}")

    print("\n=== Per Agent Category ===")
    for agent, stats in sorted(per_agent.items()):
        print(f"{agent:16s} n={stats['n']:>3d} | pearson={stats['pearson_r']:.3f} | spearman={stats['spearman_r']:.3f} | kendall={stats['kendall_tau']:.3f} | r2={stats['r2']:.3f}")

    print("\n=== ICC ===")
    if icc.get("available"):
        print(f"ICC(2,1)={icc['icc2_1']:.4f} | ICC(2,k)={icc['icc2_k']:.4f} | n_items={icc['n_items_complete']} | n_raters={icc['n_raters']}")
    else:
        print(f"Not available: {icc.get('reason')}")

    print(f"\nWrote outputs to: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
