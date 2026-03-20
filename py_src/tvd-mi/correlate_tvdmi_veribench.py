"""
Correlation analysis between TVD-MI scores and VeriBench oracle metrics.

This module implements the correlation analysis described in the user's requirements:
1. Agent-level correlation: Spearman ρ between TVD-MI abilities (θ_i) and VeriBench oracle metrics (g_i)
2. Pairwise ROC AUC: How well TVD-MI ranking matches VeriBench ranking
3. Item-level correlation: Spearman ρ between TVD-MI difficulties (b_j) and VeriBench oracle difficulties
4. Cell-level correlation: Point-biserial correlation between s_{ij} and correctness y_{ij}

Usage:
    python -m veribench.tvd_mi.correlate_tvdmi_veribench \
        --tvdmi-matrix results/tvd_mi_individual_examples/tvd_mi_score_matrix.json \
        --veribench-results path/to/veribench/results.json \
        --output results/correlation_analysis.json
"""

import json
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from sklearn.metrics import roc_auc_score, roc_curve
import warnings

warnings.filterwarnings("ignore")


def load_tvdmi_matrix(matrix_path: str) -> Dict[str, Any]:
    """Load TVD-MI score matrix from JSON file."""
    with open(matrix_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def compute_agent_abilities_from_matrix(score_matrix: np.ndarray) -> np.ndarray:
    """
    Compute agent abilities (θ_i) from TVD-MI score matrix.
    
    Uses row means: θ_i = mean_j(s_{ij})
    """
    return np.mean(score_matrix, axis=1)


def compute_item_difficulties_from_matrix(score_matrix: np.ndarray) -> np.ndarray:
    """
    Compute item difficulties (b_j) from TVD-MI score matrix.
    
    Uses negative column means: b_j = -mean_i(s_{ij})
    """
    return -np.mean(score_matrix, axis=0)


def agent_level_correlation(
    tvdmi_abilities: np.ndarray,
    veribench_abilities: np.ndarray,
    agent_names: List[str],
) -> Dict[str, Any]:
    """
    Compute agent-level correlation between TVD-MI abilities and VeriBench oracle metrics.
    
    Args:
        tvdmi_abilities: TVD-MI derived agent abilities (θ_i)
        veribench_abilities: VeriBench oracle metrics (g_i) per agent
        agent_names: List of agent names
        
    Returns:
        Dictionary with correlation metrics (Spearman ρ, Kendall τ, Pearson r)
    """
    if len(tvdmi_abilities) != len(veribench_abilities):
        raise ValueError(
            f"Mismatch in number of agents: TVD-MI has {len(tvdmi_abilities)}, "
            f"VeriBench has {len(veribench_abilities)}"
        )
    
    # Compute correlations
    spearman_rho, spearman_p = stats.spearmanr(tvdmi_abilities, veribench_abilities)
    kendall_tau, kendall_p = stats.kendalltau(tvdmi_abilities, veribench_abilities)
    pearson_r, pearson_p = stats.pearsonr(tvdmi_abilities, veribench_abilities)
    
    return {
        "spearman_rho": float(spearman_rho),
        "spearman_p_value": float(spearman_p),
        "kendall_tau": float(kendall_tau),
        "kendall_p_value": float(kendall_p),
        "pearson_r": float(pearson_r),
        "pearson_p_value": float(pearson_p),
        "num_agents": len(tvdmi_abilities),
        "agent_data": [
            {
                "agent": agent_names[i],
                "tvdmi_ability": float(tvdmi_abilities[i]),
                "veribench_ability": float(veribench_abilities[i]),
            }
            for i in range(len(agent_names))
        ],
    }


def pairwise_roc_auc(
    tvdmi_abilities: np.ndarray,
    veribench_abilities: np.ndarray,
    agent_names: List[str],
) -> Dict[str, Any]:
    """
    Compute pairwise ROC AUC for agent ordering.
    
    For each pair of agents (i, k), define:
    - y_{ik} = 1 if g_i > g_k (oracle says i is better than k), else 0
    - z_{ik} = θ_i - θ_k (TVD-MI score difference)
    
    Then compute ROC AUC treating (z_{ik}, y_{ik}) as binary classifier.
    
    Args:
        tvdmi_abilities: TVD-MI derived agent abilities (θ_i)
        veribench_abilities: VeriBench oracle metrics (g_i) per agent
        agent_names: List of agent names
        
    Returns:
        Dictionary with ROC AUC and related metrics
    """
    num_agents = len(tvdmi_abilities)
    
    # Build pairwise comparisons
    labels = []  # y_{ik}
    scores = []  # z_{ik} = θ_i - θ_k
    pairs = []
    
    for i in range(num_agents):
        for k in range(num_agents):
            if i != k:
                # Label: 1 if agent i is better than agent k according to oracle
                if veribench_abilities[i] > veribench_abilities[k]:
                    labels.append(1)
                elif veribench_abilities[i] < veribench_abilities[k]:
                    labels.append(0)
                else:
                    # Skip ties
                    continue
                
                # Score: TVD-MI ability difference
                scores.append(tvdmi_abilities[i] - tvdmi_abilities[k])
                pairs.append((agent_names[i], agent_names[k]))
    
    if len(labels) == 0:
        return {
            "roc_auc": None,
            "error": "No valid pairs found (all agents have same oracle score)",
        }
    
    labels = np.array(labels)
    scores = np.array(scores)
    
    # Compute ROC AUC
    try:
        roc_auc = roc_auc_score(labels, scores)
        fpr, tpr, thresholds = roc_curve(labels, scores)
    except ValueError as e:
        return {
            "roc_auc": None,
            "error": str(e),
        }
    
    # Compute ranking accuracy (fraction of pairs correctly ordered)
    correct_pairs = np.sum((scores > 0) == (labels == 1))
    ranking_accuracy = correct_pairs / len(labels)
    
    return {
        "roc_auc": float(roc_auc),
        "ranking_accuracy": float(ranking_accuracy),
        "num_pairs": len(labels),
        "num_correct": int(correct_pairs),
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": thresholds.tolist(),
    }


def item_level_correlation(
    tvdmi_difficulties: np.ndarray,
    veribench_difficulties: np.ndarray,
    item_ids: List[str],
) -> Dict[str, Any]:
    """
    Compute item-level correlation between TVD-MI difficulties and VeriBench oracle difficulties.
    
    Args:
        tvdmi_difficulties: TVD-MI derived item difficulties (b_j)
        veribench_difficulties: VeriBench oracle difficulties (d_j) per item
        item_ids: List of item/task IDs
        
    Returns:
        Dictionary with correlation metrics
    """
    if len(tvdmi_difficulties) != len(veribench_difficulties):
        raise ValueError(
            f"Mismatch in number of items: TVD-MI has {len(tvdmi_difficulties)}, "
            f"VeriBench has {len(veribench_difficulties)}"
        )
    
    # Compute correlations
    spearman_rho, spearman_p = stats.spearmanr(tvdmi_difficulties, veribench_difficulties)
    kendall_tau, kendall_p = stats.kendalltau(tvdmi_difficulties, veribench_difficulties)
    pearson_r, pearson_p = stats.pearsonr(tvdmi_difficulties, veribench_difficulties)
    
    return {
        "spearman_rho": float(spearman_rho),
        "spearman_p_value": float(spearman_p),
        "kendall_tau": float(kendall_tau),
        "kendall_p_value": float(kendall_p),
        "pearson_r": float(pearson_r),
        "pearson_p_value": float(pearson_p),
        "num_items": len(tvdmi_difficulties),
        "item_data": [
            {
                "item_id": item_ids[i],
                "tvdmi_difficulty": float(tvdmi_difficulties[i]),
                "veribench_difficulty": float(veribench_difficulties[i]),
            }
            for i in range(len(item_ids))
        ],
    }


def cell_level_correlation(
    score_matrix: np.ndarray,
    correctness_matrix: np.ndarray,
    agent_names: List[str],
    item_ids: List[str],
) -> Dict[str, Any]:
    """
    Compute cell-level correlation between TVD-MI scores and correctness.
    
    Args:
        score_matrix: TVD-MI score matrix S where S[i,j] is score for agent i on item j
        correctness_matrix: Binary correctness matrix Y where Y[i,j] = 1 if agent i passed item j
        agent_names: List of agent names
        item_ids: List of item/task IDs
        
    Returns:
        Dictionary with point-biserial correlation and logistic regression results
    """
    if score_matrix.shape != correctness_matrix.shape:
        raise ValueError(
            f"Shape mismatch: score_matrix {score_matrix.shape} vs "
            f"correctness_matrix {correctness_matrix.shape}"
        )
    
    # Flatten matrices for correlation
    scores_flat = score_matrix.flatten()
    correctness_flat = correctness_matrix.flatten()
    
    # Point-biserial correlation (equivalent to Pearson for binary variable)
    point_biserial_r, point_biserial_p = stats.pointbiserialr(correctness_flat, scores_flat)
    
    # Simple logistic regression: Pr(y=1 | s) = σ(α + β*s)
    from sklearn.linear_model import LogisticRegression
    
    X = scores_flat.reshape(-1, 1)
    y = correctness_flat
    
    # Fit logistic regression
    lr = LogisticRegression()
    lr.fit(X, y)
    
    beta = lr.coef_[0][0]  # Coefficient on score
    alpha = lr.intercept_[0]  # Intercept
    
    # Predictions
    y_pred = lr.predict_proba(X)[:, 1]
    
    return {
        "point_biserial_r": float(point_biserial_r),
        "point_biserial_p_value": float(point_biserial_p),
        "logistic_regression": {
            "alpha": float(alpha),
            "beta": float(beta),
            "beta_positive": beta > 0,
            "beta_significant": point_biserial_p < 0.05,
        },
        "num_cells": len(scores_flat),
        "num_correct": int(np.sum(correctness_flat)),
        "num_incorrect": int(len(correctness_flat) - np.sum(correctness_flat)),
    }


def load_veribench_results(results_path: str) -> Dict[str, Any]:
    """
    Load VeriBench evaluation results.
    
    Expected format (flexible):
    {
        "agent_metrics": {
            "agent_name": {
                "unit_test_accuracy": float,
                "theorem_accuracy": float,
                "compilation_success_rate": float,
                ...
            }
        },
        "item_metrics": {
            "item_id": {
                "difficulty": float,  # 1 - fraction of agents passing
                ...
            }
        },
        "correctness_matrix": [[...], ...],  # Optional: agent x item binary matrix
        ...
    }
    """
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def extract_veribench_agent_abilities(
    veribench_data: Dict[str, Any], metric_name: str = "unit_test_accuracy"
) -> Tuple[np.ndarray, List[str]]:
    """
    Extract agent abilities from VeriBench results.
    
    Args:
        veribench_data: Loaded VeriBench results
        metric_name: Name of metric to use (e.g., "unit_test_accuracy", "theorem_accuracy")
        
    Returns:
        Tuple of (abilities array, agent_names list)
    """
    agent_metrics = veribench_data.get("agent_metrics", {})
    
    if not agent_metrics:
        raise ValueError("No 'agent_metrics' found in VeriBench results")
    
    agent_names = []
    abilities = []
    
    for agent_name, metrics in agent_metrics.items():
        if metric_name in metrics:
            agent_names.append(agent_name)
            abilities.append(metrics[metric_name])
    
    if len(abilities) == 0:
        raise ValueError(f"Metric '{metric_name}' not found in any agent metrics")
    
    return np.array(abilities), agent_names


def extract_veribench_item_difficulties(
    veribench_data: Dict[str, Any], item_ids: List[str]
) -> np.ndarray:
    """
    Extract item difficulties from VeriBench results.
    
    If explicit difficulties are not available, compute from correctness matrix:
    d_j = 1 - (1/K) * sum_i y_{ij}
    
    Args:
        veribench_data: Loaded VeriBench results
        item_ids: List of item IDs to match
        
    Returns:
        Array of item difficulties
    """
    item_metrics = veribench_data.get("item_metrics", {})
    
    # Try to get explicit difficulties
    if item_metrics:
        difficulties = []
        for item_id in item_ids:
            if item_id in item_metrics and "difficulty" in item_metrics[item_id]:
                difficulties.append(item_metrics[item_id]["difficulty"])
            else:
                difficulties.append(None)
        
        if all(d is not None for d in difficulties):
            return np.array(difficulties)
    
    # Fall back to computing from correctness matrix
    correctness_matrix = veribench_data.get("correctness_matrix")
    if correctness_matrix is not None:
        correctness_matrix = np.array(correctness_matrix)
        # d_j = 1 - fraction of agents passing item j
        difficulties = 1 - np.mean(correctness_matrix, axis=0)
        return difficulties
    
    raise ValueError(
        "Cannot extract item difficulties: need either 'item_metrics' with 'difficulty' "
        "or 'correctness_matrix' in VeriBench results"
    )


def extract_veribench_correctness_matrix(
    veribench_data: Dict[str, Any], agent_names: List[str], item_ids: List[str]
) -> Optional[np.ndarray]:
    """
    Extract correctness matrix from VeriBench results.
    
    Args:
        veribench_data: Loaded VeriBench results
        agent_names: List of agent names (to match order)
        item_ids: List of item IDs (to match order)
        
    Returns:
        Binary correctness matrix (agents x items) or None if not available
    """
    correctness_matrix = veribench_data.get("correctness_matrix")
    if correctness_matrix is not None:
        return np.array(correctness_matrix)
    return None


def run_correlation_analysis(
    tvdmi_matrix_path: str,
    veribench_results_path: str,
    output_path: str,
    veribench_metric: str = "unit_test_accuracy",
):
    """
    Run full correlation analysis between TVD-MI and VeriBench.
    
    Args:
        tvdmi_matrix_path: Path to TVD-MI score matrix JSON
        veribench_results_path: Path to VeriBench results JSON
        output_path: Path to save correlation results
        veribench_metric: Which VeriBench metric to use for agent abilities
    """
    print("Loading TVD-MI score matrix...")
    tvdmi_data = load_tvdmi_matrix(tvdmi_matrix_path)
    
    score_matrix = np.array(tvdmi_data["score_matrix"])
    agent_names = tvdmi_data["agent_names"]
    item_ids = tvdmi_data["item_ids"]
    
    print(f"  Loaded matrix: {score_matrix.shape} (agents x items)")
    print(f"  Agents: {len(agent_names)}")
    print(f"  Items: {len(item_ids)}")
    
    # Compute TVD-MI abilities and difficulties
    tvdmi_abilities = compute_agent_abilities_from_matrix(score_matrix)
    tvdmi_difficulties = compute_item_difficulties_from_matrix(score_matrix)
    
    print("\nLoading VeriBench results...")
    veribench_data = load_veribench_results(veribench_results_path)
    
    # Extract VeriBench metrics
    print(f"  Extracting agent abilities using metric: {veribench_metric}")
    veribench_abilities, veribench_agent_names = extract_veribench_agent_abilities(
        veribench_data, metric_name=veribench_metric
    )
    
    print(f"  Extracting item difficulties...")
    veribench_difficulties = extract_veribench_item_difficulties(veribench_data, item_ids)
    
    # Align agent names (handle mismatches)
    print("\nAligning agent names...")
    agent_name_mapping = {}
    for i, tvdmi_name in enumerate(agent_names):
        # Try exact match first
        if tvdmi_name in veribench_agent_names:
            agent_name_mapping[i] = veribench_agent_names.index(tvdmi_name)
        else:
            # Try to find closest match
            matches = [j for j, name in enumerate(veribench_agent_names) if tvdmi_name in name or name in tvdmi_name]
            if matches:
                agent_name_mapping[i] = matches[0]
            else:
                print(f"  Warning: No match found for agent '{tvdmi_name}'")
                agent_name_mapping[i] = None
    
    # Reorder VeriBench abilities to match TVD-MI order
    aligned_veribench_abilities = []
    for i in range(len(agent_names)):
        if agent_name_mapping[i] is not None:
            aligned_veribench_abilities.append(veribench_abilities[agent_name_mapping[i]])
        else:
            aligned_veribench_abilities.append(np.nan)
    
    aligned_veribench_abilities = np.array(aligned_veribench_abilities)
    
    # Remove agents with missing data
    valid_mask = ~np.isnan(aligned_veribench_abilities)
    if not np.all(valid_mask):
        print(f"  Warning: {np.sum(~valid_mask)} agents have missing VeriBench data, excluding them")
        tvdmi_abilities = tvdmi_abilities[valid_mask]
        aligned_veribench_abilities = aligned_veribench_abilities[valid_mask]
        agent_names_aligned = [agent_names[i] for i in range(len(agent_names)) if valid_mask[i]]
    else:
        agent_names_aligned = agent_names
    
    print("\nComputing correlations...")
    
    # 1. Agent-level correlation
    print("  1. Agent-level correlation...")
    agent_corr = agent_level_correlation(
        tvdmi_abilities, aligned_veribench_abilities, agent_names_aligned
    )
    print(f"     Spearman ρ = {agent_corr['spearman_rho']:.4f} (p={agent_corr['spearman_p_value']:.4f})")
    
    # 2. Pairwise ROC AUC
    print("  2. Pairwise ROC AUC...")
    roc_results = pairwise_roc_auc(
        tvdmi_abilities, aligned_veribench_abilities, agent_names_aligned
    )
    if roc_results.get("roc_auc") is not None:
        print(f"     ROC AUC = {roc_results['roc_auc']:.4f}")
        print(f"     Ranking Accuracy = {roc_results['ranking_accuracy']:.4f}")
    else:
        print(f"     Error: {roc_results.get('error', 'Unknown error')}")
    
    # 3. Item-level correlation
    print("  3. Item-level correlation...")
    item_corr = item_level_correlation(
        tvdmi_difficulties, veribench_difficulties, item_ids
    )
    print(f"     Spearman ρ = {item_corr['spearman_rho']:.4f} (p={item_corr['spearman_p_value']:.4f})")
    
    # 4. Cell-level correlation (if correctness matrix available)
    print("  4. Cell-level correlation...")
    correctness_matrix = extract_veribench_correctness_matrix(
        veribench_data, agent_names, item_ids
    )
    if correctness_matrix is not None:
        # Align correctness matrix with valid agents
        if not np.all(valid_mask):
            correctness_matrix = correctness_matrix[valid_mask, :]
        
        cell_corr = cell_level_correlation(
            score_matrix[valid_mask, :] if not np.all(valid_mask) else score_matrix,
            correctness_matrix,
            agent_names_aligned,
            item_ids,
        )
        print(f"     Point-biserial r = {cell_corr['point_biserial_r']:.4f} (p={cell_corr['point_biserial_p_value']:.4f})")
        print(f"     Logistic β = {cell_corr['logistic_regression']['beta']:.4f}")
    else:
        print("     Skipping: No correctness matrix available")
        cell_corr = None
    
    # Compile results
    results = {
        "tvdmi_matrix_path": tvdmi_matrix_path,
        "veribench_results_path": veribench_results_path,
        "veribench_metric_used": veribench_metric,
        "agent_level_correlation": agent_corr,
        "pairwise_roc_auc": roc_results,
        "item_level_correlation": item_corr,
        "cell_level_correlation": cell_corr,
        "summary": {
            "agent_spearman_rho": agent_corr["spearman_rho"],
            "agent_spearman_p": agent_corr["spearman_p_value"],
            "pairwise_roc_auc": roc_results.get("roc_auc"),
            "item_spearman_rho": item_corr["spearman_rho"],
            "item_spearman_p": item_corr["spearman_p_value"],
            "cell_point_biserial_r": cell_corr["point_biserial_r"] if cell_corr else None,
        },
    }
    
    # Save results
    print(f"\nSaving results to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print("Done!")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Correlate TVD-MI scores with VeriBench oracle metrics"
    )
    parser.add_argument(
        "--tvdmi-matrix",
        required=True,
        help="Path to TVD-MI score matrix JSON file",
    )
    parser.add_argument(
        "--veribench-results",
        required=True,
        help="Path to VeriBench evaluation results JSON file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to save correlation analysis results",
    )
    parser.add_argument(
        "--metric",
        default="unit_test_accuracy",
        help="VeriBench metric to use for agent abilities (default: unit_test_accuracy)",
    )
    
    args = parser.parse_args()
    
    run_correlation_analysis(
        tvdmi_matrix_path=args.tvdmi_matrix,
        veribench_results_path=args.veribench_results,
        output_path=args.output,
        veribench_metric=args.metric,
    )


if __name__ == "__main__":
    import os
    
    main()

