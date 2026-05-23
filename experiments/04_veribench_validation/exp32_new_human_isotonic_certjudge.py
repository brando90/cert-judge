#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr

try:
    from sklearn.isotonic import IsotonicRegression
except Exception:  # pragma: no cover
    IsotonicRegression = None


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_SPLIT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp23_pass_split_for_brando" / "splits"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp32_new_human_isotonic_certjudge"
DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]

COMPONENTS = ["ident", "mono_rank", "weak_mono", "stability", "anti_string", "subtle_bug"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP32: new-label isotonic oracle and train-optimized CertJudge correlation")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument("--search-iters", type=int, default=200000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eps", type=float, default=1e-6)
    p.add_argument(
        "--include-old-prompt",
        action="store_true",
        help="Also include experiments/human_labels/old_prompt TSVs. Default excludes them.",
    )
    return p.parse_args()


def _clean_candidate_and_score(candidate: str, score: str) -> Tuple[str, str]:
    candidate = str(candidate).strip()
    score = "" if pd.isna(score) else str(score).strip()
    if not score and ".lean " in candidate:
        head, tail = candidate.rsplit(" ", 1)
        try:
            float(tail)
        except ValueError:
            return candidate, score
        return head.strip(), tail.strip()
    return candidate, score


def load_new_human_labels(human_dir: Path, include_old_prompt: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    files = sorted(human_dir.glob("*.tsv"))
    if include_old_prompt:
        files += sorted((human_dir / "old_prompt").glob("*.tsv"))
    if not files:
        raise FileNotFoundError(f"No TSV files found under {human_dir}")

    rows: List[dict] = []
    dropped: List[dict] = []
    for path in files:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line_no, row in enumerate(reader, start=2):
                gold = str(row.get("gold_file", "")).strip()
                cand, score_text = _clean_candidate_and_score(row.get("candidate_file", ""), row.get("human_score_0_5", ""))
                try:
                    score = float(score_text)
                except (TypeError, ValueError):
                    dropped.append(
                        {
                            "source_file": str(path.relative_to(REPO_ROOT)),
                            "line_no": line_no,
                            "gold_file": gold,
                            "candidate_file": cand,
                            "human_score_0_5": score_text,
                            "reason": "missing_or_invalid_score",
                        }
                    )
                    continue
                if not gold or not cand:
                    dropped.append(
                        {
                            "source_file": str(path.relative_to(REPO_ROOT)),
                            "line_no": line_no,
                            "gold_file": gold,
                            "candidate_file": cand,
                            "human_score_0_5": score_text,
                            "reason": "missing_file_key",
                        }
                    )
                    continue
                rows.append(
                    {
                        "source_file": str(path.relative_to(REPO_ROOT)),
                        "rater": path.stem,
                        "gold_file": gold,
                        "candidate_file": cand,
                        "item_key": f"{gold}::{cand}",
                        "human_score_0_5": score,
                        "human_score_0_1": score / 5.0,
                    }
                )
    labels = pd.DataFrame(rows)
    if labels.empty:
        raise ValueError("No usable human labels after cleaning")
    item_targets = (
        labels.groupby(["gold_file", "candidate_file", "item_key"], as_index=False)
        .agg(
            human_mean_0_5=("human_score_0_5", "mean"),
            human_mean_0_1=("human_score_0_1", "mean"),
            human_std_0_5=("human_score_0_5", "std"),
            n_labels=("human_score_0_5", "size"),
            n_raters=("rater", "nunique"),
        )
        .sort_values("item_key")
    )
    return labels, item_targets, pd.DataFrame(dropped)


def load_split_keys(split_dir: Path) -> Tuple[set[str], set[str]]:
    def read_pairs(name: str) -> set[str]:
        path = split_dir / f"{name}_pairs.tsv"
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path, sep="\t")
        return set(df["gold_file"].astype(str).str.strip() + "::" + df["candidate_file"].astype(str).str.strip())

    val = read_pairs("val")
    holdout = read_pairs("holdout")
    test = read_pairs("test")
    return val | holdout, test


def _float(row: dict, key: str, default: float = float("nan")) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def load_judges(result_dirs: Iterable[Path]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    meta_by_judge: Dict[str, dict] = {}
    score_rows: List[dict] = []
    seen_scores: set[Tuple[str, str]] = set()
    for result_dir in result_dirs:
        judge_rows_path = result_dir / "judge_rows.csv"
        detail_rows_path = result_dir / "detail_rows.csv"
        if not judge_rows_path.exists() or not detail_rows_path.exists():
            continue
        with judge_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                judge_id = row["judge_id"]
                if judge_id not in meta_by_judge:
                    ident = np.clip(_float(row, "identity_mean"), 0.0, 1.0)
                    mono_rank = np.clip((1.0 - _float(row, "bug_spearman_r")) / 2.0, 0.0, 1.0)
                    weak = np.clip(_float(row, "bug_weak_mono_pct") / 100.0, 0.0, 1.0)
                    stability = np.clip(1.0 - _float(row, "flip_rate"), 0.0, 1.0)
                    anti = np.clip(_float(row, "anti_string_score", 0.0), 0.0, 1.0)
                    subtle = np.clip(_float(row, "subtle_bug_sensitivity", 0.0), 0.0, 1.0)
                    meta_by_judge[judge_id] = {
                        "judge_id": judge_id,
                        "kind": row.get("kind", ""),
                        "model": row.get("model", ""),
                        "prompt_name": row.get("prompt_name", ""),
                        "source_dir": str(result_dir.relative_to(REPO_ROOT)),
                        "cert_index": _float(row, "cert_index"),
                        "cert_index_v2": _float(row, "cert_index_v2"),
                        "ident": ident,
                        "mono_rank": mono_rank,
                        "weak_mono": weak,
                        "stability": stability,
                        "anti_string": anti,
                        "subtle_bug": subtle,
                    }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                judge_id = row["judge_id"]
                item_key = row["item_key"]
                dedup_key = (judge_id, item_key)
                if judge_id not in meta_by_judge or dedup_key in seen_scores:
                    continue
                seen_scores.add(dedup_key)
                score_rows.append(
                    {
                        "judge_id": judge_id,
                        "item_key": item_key,
                        "score_mean": _float(row, "score_mean"),
                    }
                )
    if not meta_by_judge:
        raise ValueError("No EXP16-style judge metadata loaded")
    return pd.DataFrame(meta_by_judge.values()).sort_values("judge_id"), pd.DataFrame(score_rows)


def safe_metrics(y_pred: Sequence[float], y_true: Sequence[float]) -> dict:
    yp = np.asarray(y_pred, dtype=float)
    yt = np.asarray(y_true, dtype=float)
    mask = np.isfinite(yp) & np.isfinite(yt)
    yp = yp[mask]
    yt = yt[mask]
    if len(yp) < 3 or len(np.unique(yp)) < 2 or len(np.unique(yt)) < 2:
        return {
            "n": int(len(yp)),
            "pearson_r": float("nan"),
            "spearman_rho": float("nan"),
            "kendall_tau": float("nan"),
            "mae_0_1": float("nan"),
            "rmse_0_1": float("nan"),
        }
    return {
        "n": int(len(yp)),
        "pearson_r": float(pearsonr(yp, yt).statistic),
        "spearman_rho": float(spearmanr(yp, yt).statistic),
        "kendall_tau": float(kendalltau(yp, yt).statistic),
        "mae_0_1": float(np.mean(np.abs(yp - yt))),
        "rmse_0_1": float(np.sqrt(np.mean((yp - yt) ** 2))),
    }


def isotonic_fit_predict(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    if IsotonicRegression is None:
        raise RuntimeError("sklearn IsotonicRegression is unavailable")
    model = IsotonicRegression(y_min=0.0, y_max=1.0, increasing=True, out_of_bounds="clip")
    model.fit(x, y)
    return model.predict(x)


def geometric_index(meta: pd.DataFrame, weights: np.ndarray, eps: float) -> np.ndarray:
    comp = meta[COMPONENTS].to_numpy(dtype=float)
    comp = np.clip(comp, eps, 1.0)
    return np.exp(np.log(comp) @ weights)


def fit_train_weights(meta: pd.DataFrame, y_train: np.ndarray, iters: int, seed: int, eps: float) -> Tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    best_w = np.ones(len(COMPONENTS), dtype=float) / len(COMPONENTS)
    best_r = float("-inf")
    priors = [
        np.ones(len(COMPONENTS), dtype=float),
        np.array([1, 1, 1, 1, 0, 0], dtype=float),
        np.array([0, 1, 1, 1, 0, 0], dtype=float),
        np.array([0, 1, 0, 1, 0, 0], dtype=float),
        np.eye(len(COMPONENTS), dtype=float)[0],
        np.eye(len(COMPONENTS), dtype=float)[1],
        np.eye(len(COMPONENTS), dtype=float)[2],
        np.eye(len(COMPONENTS), dtype=float)[3],
        np.eye(len(COMPONENTS), dtype=float)[4],
        np.eye(len(COMPONENTS), dtype=float)[5],
    ]
    candidates: List[np.ndarray] = []
    for w in priors:
        if np.sum(w) > 0:
            candidates.append(w / np.sum(w))
    for _ in range(iters):
        candidates.append(rng.dirichlet(np.ones(len(COMPONENTS), dtype=float)))

    mask = np.isfinite(y_train)
    for w in candidates:
        x = geometric_index(meta, w, eps)
        if np.sum(mask) < 3 or len(np.unique(x[mask])) < 2:
            continue
        r = float(spearmanr(x[mask], y_train[mask]).statistic)
        if math.isfinite(r) and r > best_r:
            best_r = r
            best_w = w.copy()
    return best_w, best_r


def judge_alignment_rows(scores: pd.DataFrame, targets: pd.DataFrame, split_keys: set[str], split_name: str) -> pd.DataFrame:
    target_cols = ["item_key", "human_mean_0_1"]
    rows = scores[scores["item_key"].isin(split_keys)].merge(targets[target_cols], on="item_key", how="inner")
    out: List[dict] = []
    for judge_id, group in rows.groupby("judge_id"):
        metrics = safe_metrics(group["score_mean"], group["human_mean_0_1"])
        out.append(
            {
                "judge_id": judge_id,
                f"n_items_{split_name}": metrics["n"],
                f"human_spearman_{split_name}": metrics["spearman_rho"],
                f"human_pearson_{split_name}": metrics["pearson_r"],
                f"human_kendall_{split_name}": metrics["kendall_tau"],
            }
        )
    return pd.DataFrame(out)


def run_test_isotonic(scores: pd.DataFrame, targets: pd.DataFrame, test_keys: set[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows = scores[scores["item_key"].isin(test_keys)].merge(targets[["item_key", "human_mean_0_1"]], on="item_key", how="inner")
    metric_rows: List[dict] = []
    pred_rows: List[pd.DataFrame] = []
    for judge_id, group in rows.groupby("judge_id"):
        group = group.dropna(subset=["score_mean", "human_mean_0_1"]).copy()
        if len(group) < 3 or len(group["score_mean"].unique()) < 2:
            continue
        y_iso = isotonic_fit_predict(group["score_mean"].to_numpy(dtype=float), group["human_mean_0_1"].to_numpy(dtype=float))
        raw = safe_metrics(group["score_mean"], group["human_mean_0_1"])
        iso = safe_metrics(y_iso, group["human_mean_0_1"])
        metric_rows.append(
            {
                "judge_id": judge_id,
                "n_test_items": int(len(group)),
                **{f"raw_{k}": v for k, v in raw.items() if k != "n"},
                **{f"test_isotonic_oracle_{k}": v for k, v in iso.items() if k != "n"},
            }
        )
        pred = group[["judge_id", "item_key", "score_mean", "human_mean_0_1"]].copy()
        pred["test_isotonic_oracle_pred"] = y_iso
        pred_rows.append(pred)
    return pd.DataFrame(metric_rows), pd.concat(pred_rows, ignore_index=True) if pred_rows else pd.DataFrame()


def write_report(out_dir: Path, summary: dict, top_iso: pd.DataFrame, train_table: pd.DataFrame) -> None:
    lines = [
        "# EXP32 New Human Labels: Isotonic Oracle and CertJudge Train Fit",
        "**TLDR:** This run aggregates the new human-label TSVs, fits an isotonic oracle on the test split, and searches train-side CertJudge weights for high judge-level correlation.",
        "",
        "## Data",
        f"- Human files used: {summary['data']['n_human_files_used']}",
        f"- Usable labels: {summary['data']['n_usable_labels']}",
        f"- Distinct labeled items: {summary['data']['n_distinct_items']}",
        f"- Items overlapping judge scores: {summary['data']['n_items_with_judge_scores']}",
        f"- Train items: {summary['data']['n_train_items_overlap']}",
        f"- Test items: {summary['data']['n_test_items_overlap']}",
        f"- Dropped labels: {summary['data']['n_dropped_labels']}",
        "",
        "## Test-Set Isotonic Oracle",
        "This intentionally fits the monotone mapping on test labels, so it is an upper-bound diagnostic, not deployment-valid calibration.",
    ]
    if not top_iso.empty:
        for _, row in top_iso.head(5).iterrows():
            lines.append(
                f"- `{row['judge_id']}`: isotonic Spearman={row['test_isotonic_oracle_spearman_rho']:.3f}, "
                f"Pearson={row['test_isotonic_oracle_pearson_r']:.3f}, MAE={row['test_isotonic_oracle_mae_0_1']:.3f} (n={int(row['n_test_items'])})"
            )
    lines += [
        "",
        "## Train-Optimized CertJudge",
        f"- Best train Spearman: {summary['train_certjudge']['best_train_spearman']:.3f}",
        f"- Same weights on test Spearman: {summary['train_certjudge']['test_spearman_same_weights']:.3f}",
        f"- Best weights: {summary['train_certjudge']['weights']}",
        "",
        "## Outputs",
        "- `new_human_labels_cleaned.csv`",
        "- `new_human_item_targets.csv`",
        "- `test_isotonic_oracle_per_judge.csv`",
        "- `test_isotonic_oracle_predictions.csv`",
        "- `train_certjudge_weight_search.csv`",
        "- `summary.json`",
    ]
    out_dir.joinpath("README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    labels, targets, dropped = load_new_human_labels(args.human_dir, args.include_old_prompt)
    train_keys, test_keys = load_split_keys(args.split_dir)
    meta, scores = load_judges(args.result_dirs)

    score_keys = set(scores["item_key"])
    target_keys = set(targets["item_key"])
    train_overlap = train_keys & target_keys & score_keys
    test_overlap = test_keys & target_keys & score_keys

    labels.to_csv(args.out_dir / "new_human_labels_cleaned.csv", index=False)
    targets.to_csv(args.out_dir / "new_human_item_targets.csv", index=False)
    dropped.to_csv(args.out_dir / "dropped_human_label_rows.csv", index=False)

    iso_rows, iso_preds = run_test_isotonic(scores, targets, test_overlap)
    iso_rows = iso_rows.merge(meta[["judge_id", "model", "prompt_name", "kind", "source_dir"]], on="judge_id", how="left")
    iso_rows = iso_rows.sort_values(
        ["test_isotonic_oracle_spearman_rho", "test_isotonic_oracle_pearson_r", "test_isotonic_oracle_mae_0_1"],
        ascending=[False, False, True],
    )
    iso_rows.to_csv(args.out_dir / "test_isotonic_oracle_per_judge.csv", index=False)
    iso_preds.to_csv(args.out_dir / "test_isotonic_oracle_predictions.csv", index=False)

    train_align = judge_alignment_rows(scores, targets, train_overlap, "train")
    test_align = judge_alignment_rows(scores, targets, test_overlap, "test")
    align = meta.merge(train_align, on="judge_id", how="left").merge(test_align, on="judge_id", how="left")

    y_train = align["human_spearman_train"].to_numpy(dtype=float)
    best_w, best_train = fit_train_weights(align, y_train, args.search_iters, args.seed, args.eps)
    align["certjudge_train_optimized"] = geometric_index(align, best_w, args.eps)
    train_mask = np.isfinite(align["human_spearman_train"].to_numpy(dtype=float))
    test_mask = np.isfinite(align["human_spearman_test"].to_numpy(dtype=float))
    train_r = float(spearmanr(align.loc[train_mask, "certjudge_train_optimized"], align.loc[train_mask, "human_spearman_train"]).statistic)
    test_r = float(spearmanr(align.loc[test_mask, "certjudge_train_optimized"], align.loc[test_mask, "human_spearman_test"]).statistic)
    baseline_rows = []
    for col in ["cert_index", "cert_index_v2"]:
        baseline_rows.append(
            {
                "index_name": col,
                "train_spearman": float(spearmanr(align.loc[train_mask, col], align.loc[train_mask, "human_spearman_train"]).statistic),
                "test_spearman": float(spearmanr(align.loc[test_mask, col], align.loc[test_mask, "human_spearman_test"]).statistic),
            }
        )
    baseline_rows.append({"index_name": "certjudge_train_optimized", "train_spearman": train_r, "test_spearman": test_r})
    baseline_df = pd.DataFrame(baseline_rows)
    align.sort_values("certjudge_train_optimized", ascending=False).to_csv(args.out_dir / "train_certjudge_weight_search.csv", index=False)
    baseline_df.to_csv(args.out_dir / "certjudge_index_correlations.csv", index=False)

    top_iso = iso_rows.head(10)
    summary = {
        "experiment": "exp32_new_human_isotonic_certjudge",
        "inputs": {
            "human_dir": str(args.human_dir),
            "include_old_prompt": bool(args.include_old_prompt),
            "split_dir": str(args.split_dir),
            "result_dirs": [str(p) for p in args.result_dirs],
        },
        "data": {
            "n_human_files_used": int(labels["source_file"].nunique()),
            "n_usable_labels": int(len(labels)),
            "n_dropped_labels": int(len(dropped)),
            "n_distinct_items": int(len(targets)),
            "n_distinct_tasks": int(targets["gold_file"].nunique()),
            "n_items_with_judge_scores": int(len(target_keys & score_keys)),
            "n_train_items_overlap": int(len(train_overlap)),
            "n_test_items_overlap": int(len(test_overlap)),
            "n_judges": int(len(meta)),
        },
        "test_isotonic_oracle": {
            "note": "IsotonicRegression is fit and evaluated on the test split; this is an oracle/upper-bound mapping, not a leakage-free deployment estimate.",
            "top_judge_by_isotonic_spearman": top_iso.iloc[0].to_dict() if not top_iso.empty else None,
        },
        "train_certjudge": {
            "note": "Weights are optimized on train judge-level human Spearman, then also evaluated on test for a leakage check.",
            "search_iters": int(args.search_iters),
            "seed": int(args.seed),
            "components": COMPONENTS,
            "weights": {name: float(best_w[i]) for i, name in enumerate(COMPONENTS)},
            "best_train_spearman": float(best_train),
            "recomputed_train_spearman": train_r,
            "test_spearman_same_weights": test_r,
            "baseline_indices": baseline_df.to_dict(orient="records"),
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(args.out_dir, summary, top_iso, align)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
