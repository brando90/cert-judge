"""
Proxy vs oracle correlation analysis for pairwise information matrices.

This script expects a pairwise matrix over items/examples. It collapses each row
into a proxy score (row-average) and correlates against oracle scores.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import stats
from sklearn.metrics import r2_score


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_matrix(data: Dict[str, Any]) -> Tuple[np.ndarray, str]:
    if "pairwise_matrix" in data:
        return np.array(data["pairwise_matrix"], dtype=float), "pairwise_matrix"
    if "matrix" in data:
        return np.array(data["matrix"], dtype=float), "matrix"
    if "score_matrix" in data:
        return np.array(data["score_matrix"], dtype=float), "score_matrix"
    raise ValueError("No matrix found in file.")


def _load_item_ids(data: Dict[str, Any], fallback_len: int) -> List[str]:
    for key in ("item_ids", "items", "task_ids", "example_ids"):
        if key in data:
            return [str(x) for x in data[key]]
    return [f"item_{i}" for i in range(fallback_len)]


def _load_item_ids_from_file(path: Path) -> List[str]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("Item ID file is empty.")
    if raw.startswith("["):
        data = json.loads(raw)
        return [str(x) for x in data]
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _load_oracle_scores(path: str, item_ids: List[str]) -> Tuple[np.ndarray, List[str]]:
    data = _load_json(path)

    if isinstance(data, dict) and "scores" in data:
        scores = data["scores"]
        ids = data.get("item_ids", item_ids)
        if len(scores) != len(ids):
            raise ValueError("Oracle scores length does not match item_ids length.")
        return np.array(scores, dtype=float), [str(x) for x in ids]

    if isinstance(data, dict):
        # Assume mapping item_id -> score
        scores = []
        ids = []
        for item_id in item_ids:
            if item_id in data:
                ids.append(item_id)
                scores.append(data[item_id])
        if not scores:
            raise ValueError("Oracle score mapping did not match any item_ids.")
        return np.array(scores, dtype=float), ids

    if isinstance(data, list):
        if len(data) != len(item_ids):
            raise ValueError(
                "Oracle scores list length does not match item_ids length."
            )
        return np.array(data, dtype=float), item_ids

    raise ValueError("Unsupported oracle score format.")


def compute_proxy_scores(
    matrix: np.ndarray, exclude_diagonal: bool = True
) -> np.ndarray:
    if matrix.shape[0] == matrix.shape[1]:
        if exclude_diagonal:
            masked = matrix.astype(float).copy()
            np.fill_diagonal(masked, np.nan)
            return np.nanmean(masked, axis=1)
        return np.mean(matrix, axis=1)

    # Treat rectangular matrices as agent×item; return item-level averages.
    return np.mean(matrix, axis=0)


def align_scores(
    item_ids: List[str],
    proxy_scores: np.ndarray,
    oracle_scores: np.ndarray,
    oracle_item_ids: List[str],
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    oracle_map = {
        item_id: score for item_id, score in zip(oracle_item_ids, oracle_scores)
    }
    aligned_proxy = []
    aligned_oracle = []
    aligned_ids = []

    for item_id, proxy in zip(item_ids, proxy_scores):
        if item_id in oracle_map:
            aligned_ids.append(item_id)
            aligned_proxy.append(proxy)
            aligned_oracle.append(oracle_map[item_id])

    if not aligned_ids:
        raise ValueError(
            "No overlapping item IDs between proxy matrix and oracle scores."
        )

    return np.array(aligned_proxy), np.array(aligned_oracle), aligned_ids


def compute_correlations(proxy: np.ndarray, oracle: np.ndarray) -> Dict[str, float]:
    if len(proxy) < 2:
        raise ValueError("Need at least 2 items to compute correlations.")
    spearman_rho, spearman_p = stats.spearmanr(proxy, oracle)
    kendall_tau, kendall_p = stats.kendalltau(proxy, oracle)
    pearson_r, pearson_p = stats.pearsonr(proxy, oracle)

    return {
        "spearman_rho": float(spearman_rho),
        "spearman_p_value": float(spearman_p),
        "kendall_tau": float(kendall_tau),
        "kendall_p_value": float(kendall_p),
        "pearson_r": float(pearson_r),
        "pearson_p_value": float(pearson_p),
    }


def compute_r2(proxy: np.ndarray, oracle: np.ndarray, direction: str) -> float:
    if len(proxy) < 2:
        raise ValueError("Need at least 2 items to compute R².")
    if np.allclose(proxy, proxy[0]) or np.allclose(oracle, oracle[0]):
        return float("nan")
    if direction == "proxy_on_oracle":
        y_true = proxy
        y_pred = np.polyval(np.polyfit(oracle, proxy, 1), oracle)
    else:
        y_true = oracle
        y_pred = np.polyval(np.polyfit(proxy, oracle, 1), proxy)
    return float(r2_score(y_true, y_pred))


def compute_nulls(
    proxy: np.ndarray, oracle: np.ndarray, shuffles: int
) -> Dict[str, Any]:
    rng = np.random.default_rng(0)
    spearman_vals = []
    pearson_vals = []

    for _ in range(shuffles):
        shuffled = rng.permutation(oracle)
        spearman_vals.append(stats.spearmanr(proxy, shuffled)[0])
        pearson_vals.append(stats.pearsonr(proxy, shuffled)[0])

    return {
        "spearman_rho": {
            "mean": float(np.mean(spearman_vals)),
            "std": float(np.std(spearman_vals)),
            "min": float(np.min(spearman_vals)),
            "max": float(np.max(spearman_vals)),
        },
        "pearson_r": {
            "mean": float(np.mean(pearson_vals)),
            "std": float(np.std(pearson_vals)),
            "min": float(np.min(pearson_vals)),
            "max": float(np.max(pearson_vals)),
        },
    }


def compute_self_consistency(
    proxy_a: np.ndarray, proxy_b: np.ndarray
) -> Dict[str, float]:
    if len(proxy_a) != len(proxy_b):
        raise ValueError("Proxy score vectors must be the same length.")

    spearman_rho, spearman_p = stats.spearmanr(proxy_a, proxy_b)
    kendall_tau, kendall_p = stats.kendalltau(proxy_a, proxy_b)
    pearson_r, pearson_p = stats.pearsonr(proxy_a, proxy_b)

    return {
        "spearman_rho": float(spearman_rho),
        "spearman_p_value": float(spearman_p),
        "kendall_tau": float(kendall_tau),
        "kendall_p_value": float(kendall_p),
        "pearson_r": float(pearson_r),
        "pearson_p_value": float(pearson_p),
    }


def summarize_matrix(matrix: np.ndarray) -> Dict[str, Any]:
    zero_mask = np.isclose(matrix, 0)
    off_diag = matrix.copy().astype(float)
    off_diag_zero_fraction = None
    if matrix.shape[0] == matrix.shape[1]:
        np.fill_diagonal(off_diag, np.nan)
        off_diag_mask = ~np.isnan(off_diag)
        if np.any(off_diag_mask):
            off_diag_zero_fraction = float(
                np.mean(np.isclose(off_diag[off_diag_mask], 0))
            )
        else:
            off_diag_zero_fraction = 0.0

    return {
        "shape": [int(matrix.shape[0]), int(matrix.shape[1])],
        "zero_fraction": float(np.mean(zero_mask)),
        "off_diagonal_zero_fraction": off_diag_zero_fraction,
        "min": float(np.min(matrix)),
        "max": float(np.max(matrix)),
        "mean": float(np.mean(matrix)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Correlate proxy row-averaged scores against oracle scores."
    )
    parser.add_argument(
        "--pairwise-matrix", required=True, help="Path to pairwise matrix JSON"
    )
    parser.add_argument(
        "--oracle-scores", required=True, help="Path to oracle scores JSON"
    )
    parser.add_argument("--output", required=True, help="Path to save analysis JSON")
    parser.add_argument(
        "--include-diagonal",
        action="store_true",
        help="Include diagonal entries when averaging rows (default: exclude)",
    )
    parser.add_argument(
        "--r2-direction",
        choices=["proxy_on_oracle", "oracle_on_proxy"],
        default="proxy_on_oracle",
        help="Direction of linear fit for R^2 (default: proxy_on_oracle)",
    )
    parser.add_argument(
        "--null-shuffles",
        type=int,
        default=0,
        help="Number of shuffle-based null trials (default: 0)",
    )
    parser.add_argument(
        "--pairwise-matrix-b",
        help="Optional second matrix for self-consistency check",
    )
    parser.add_argument(
        "--item-ids",
        help="Optional JSON list or newline-separated list of item IDs to override matrix IDs.",
    )
    parser.add_argument(
        "--plot-path",
        help="Optional path to save a proxy-vs-oracle scatter plot (png).",
    )
    parser.add_argument(
        "--plot-title",
        default=None,
        help="Optional plot title override.",
    )
    parser.add_argument(
        "--normalize-oracle",
        action="store_true",
        help="Normalize oracle scores to [0,1] by dividing by 10.",
    )

    args = parser.parse_args()

    matrix_data = _load_json(args.pairwise_matrix)
    matrix, matrix_key = _find_matrix(matrix_data)
    if args.item_ids:
        item_ids = _load_item_ids_from_file(Path(args.item_ids).expanduser().resolve())
    else:
        item_ids = _load_item_ids(
            matrix_data,
            matrix.shape[0] if matrix.shape[0] == matrix.shape[1] else matrix.shape[1],
        )

    proxy_scores = compute_proxy_scores(
        matrix, exclude_diagonal=not args.include_diagonal
    )

    oracle_scores, oracle_item_ids = _load_oracle_scores(args.oracle_scores, item_ids)
    if args.normalize_oracle:
        oracle_scores = oracle_scores / 10.0
    aligned_proxy, aligned_oracle, aligned_ids = align_scores(
        item_ids, proxy_scores, oracle_scores, oracle_item_ids
    )
    mask = np.isfinite(aligned_proxy) & np.isfinite(aligned_oracle)
    if not np.all(mask):
        aligned_proxy = aligned_proxy[mask]
        aligned_oracle = aligned_oracle[mask]
        aligned_ids = [item for item, keep in zip(aligned_ids, mask) if keep]
    if len(aligned_ids) < 2:
        raise ValueError("Need at least 2 overlapping items to compute correlations.")

    correlations = compute_correlations(aligned_proxy, aligned_oracle)
    r2_value = compute_r2(aligned_proxy, aligned_oracle, args.r2_direction)

    results: Dict[str, Any] = {
        "pairwise_matrix_path": args.pairwise_matrix,
        "oracle_scores_path": args.oracle_scores,
        "matrix_key": matrix_key,
        "matrix_is_square": matrix.shape[0] == matrix.shape[1],
        "matrix_summary": summarize_matrix(matrix),
        "num_items": len(aligned_ids),
        "exclude_diagonal": not args.include_diagonal,
        "correlations": correlations,
        "r2": {
            "direction": args.r2_direction,
            "value": r2_value,
        },
        "aligned_items": aligned_ids,
        "proxy_scores": aligned_proxy.tolist(),
        "oracle_scores": aligned_oracle.tolist(),
    }

    if args.null_shuffles > 0:
        results["null_controls"] = compute_nulls(
            aligned_proxy, aligned_oracle, args.null_shuffles
        )

    if args.pairwise_matrix_b:
        matrix_b_data = _load_json(args.pairwise_matrix_b)
        matrix_b, _ = _find_matrix(matrix_b_data)
        item_ids_b = _load_item_ids(matrix_b_data, matrix_b.shape[0])
        proxy_b = compute_proxy_scores(
            matrix_b, exclude_diagonal=not args.include_diagonal
        )

        aligned_proxy_b, _, aligned_ids_b = align_scores(
            item_ids_b, proxy_b, aligned_oracle, aligned_ids
        )
        aligned_proxy_a, _, _ = align_scores(
            aligned_ids, aligned_proxy, aligned_oracle, aligned_ids
        )
        results["self_consistency"] = {
            "matrix_b_path": args.pairwise_matrix_b,
            "num_items": len(aligned_ids_b),
            "correlations": compute_self_consistency(aligned_proxy_a, aligned_proxy_b),
        }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    if args.plot_path:
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError("matplotlib is required for --plot-path") from exc

        plot_path = Path(args.plot_path)
        plot_path.parent.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(aligned_oracle, aligned_proxy, color="#1f77b4", alpha=0.85)

        if len(aligned_oracle) >= 2:
            coef = np.polyfit(aligned_oracle, aligned_proxy, 1)
            xs = np.linspace(min(aligned_oracle), max(aligned_oracle), 100)
            ys = np.polyval(coef, xs)
            ax.plot(xs, ys, color="#d62728", linewidth=1.5)

        ax.set_xlabel("Oracle score")
        ax.set_ylabel("Proxy score")

        title = args.plot_title or "Proxy vs Oracle"
        ax.set_title(title)

        text = (
            f"Spearman ρ={correlations['spearman_rho']:.3f}, Kendall τ={correlations['kendall_tau']:.3f}\n"
            f"Pearson r={correlations['pearson_r']:.3f}, R²={r2_value:.3f}\n"
            f"n={len(aligned_ids)}"
        )
        ax.text(
            0.02,
            0.98,
            text,
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            bbox=dict(
                boxstyle="round", facecolor="white", alpha=0.8, edgecolor="#cccccc"
            ),
        )
        ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)

        fig.tight_layout()
        fig.savefig(plot_path, dpi=200)
        plt.close(fig)
        print(f"Saved plot to {plot_path}")

    print(f"Saved proxy vs oracle analysis to {output_path}")


if __name__ == "__main__":
    main()
