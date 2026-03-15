#!/usr/bin/env python3
"""
Statistical metrics for certification judge experiments.
"""
from typing import List, Tuple
import statistics


def pearson_r(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    """
    Compute Pearson correlation coefficient and p-value.
    Returns (r, p).
    """
    from scipy.stats import pearsonr
    if len(xs) < 2 or len(xs) != len(ys):
        return (0.0, 1.0)
    try:
        r, p = pearsonr(xs, ys)
        return (float(r), float(p))
    except Exception:
        return (0.0, 1.0)


def spearman_r(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    """
    Compute Spearman rank correlation coefficient and p-value.
    Returns (r, p).
    """
    from scipy.stats import spearmanr
    if len(xs) < 2 or len(xs) != len(ys):
        return (0.0, 1.0)
    try:
        r, p = spearmanr(xs, ys)
        return (float(r), float(p))
    except Exception:
        return (0.0, 1.0)


def weak_monotonicity_pct(ladders: List[List[float]]) -> float:
    """
    Compute percentage of ladders (score sequences) that are non-increasing
    (allowing ties). A ladder passes if every consecutive pair satisfies
    scores[i] >= scores[i+1].

    Args:
        ladders: list of score sequences, one per theorem.
                 Each sequence goes from best (level 0) to worst (level N).

    Returns:
        float: percentage of ladders that are non-increasing (0-100).
    """
    if not ladders:
        return 0.0

    passed = 0
    for ladder in ladders:
        if len(ladder) <= 1:
            passed += 1
            continue
        non_increasing = all(ladder[i] >= ladder[i+1] for i in range(len(ladder)-1))
        if non_increasing:
            passed += 1

    return 100.0 * passed / len(ladders)


def levenshtein_normalized(a: str, b: str) -> float:
    """
    Normalized Levenshtein distance in [0, 1].
    0 = identical, 1 = maximally different.
    """
    try:
        import Levenshtein
        if not a and not b:
            return 0.0
        dist = Levenshtein.distance(a, b)
        max_len = max(len(a), len(b))
        if max_len == 0:
            return 0.0
        return dist / max_len
    except ImportError:
        # Fallback: simple character-level diff
        if a == b:
            return 0.0
        max_len = max(len(a), len(b))
        if max_len == 0:
            return 0.0
        # Simple edit distance via DP
        m, n = len(a), len(b)
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            new_dp = [i] + [0] * n
            for j in range(1, n + 1):
                if a[i-1] == b[j-1]:
                    new_dp[j] = dp[j-1]
                else:
                    new_dp[j] = 1 + min(dp[j], new_dp[j-1], dp[j-1])
            dp = new_dp
        return dp[n] / max_len


def jaccard_tokens(a: str, b: str) -> float:
    """
    Jaccard similarity over token sets.
    Returns similarity in [0, 1] (1 = identical).
    Note: returns similarity, not distance.
    """
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a and not tokens_b:
        return 1.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(intersection) / len(union)


def bleu_score(reference: str, hypothesis: str) -> float:
    """
    Simple BLEU-1 score between reference and hypothesis strings.
    """
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        ref_tokens = reference.split()
        hyp_tokens = hypothesis.split()
        if not ref_tokens or not hyp_tokens:
            return 0.0
        smoother = SmoothingFunction().method1
        return float(sentence_bleu([ref_tokens], hyp_tokens,
                                   weights=(1.0, 0, 0, 0),
                                   smoothing_function=smoother))
    except Exception:
        # Fallback: unigram overlap
        ref_tokens = set(reference.split())
        hyp_tokens = hypothesis.split()
        if not hyp_tokens:
            return 0.0
        matches = sum(1 for t in hyp_tokens if t in ref_tokens)
        return matches / len(hyp_tokens)


if __name__ == "__main__":
    # Quick tests
    a = "theorem foo (n m : Nat) : n + m = m + n := Nat.add_comm n m"
    b = "theorem bar (k j : Nat) : k + j = j + k := Nat.add_comm k j"

    print(f"pearson_r: {pearson_r([1,2,3,4], [1.1,1.9,3.2,4.1])}")
    print(f"spearman_r: {spearman_r([1,2,3,4], [1.1,1.9,3.2,4.1])}")
    print(f"weak_mono: {weak_monotonicity_pct([[0.9, 0.8, 0.6, 0.4], [0.9, 0.9, 0.7, 0.5]])}")
    print(f"levenshtein: {levenshtein_normalized(a, b):.3f}")
    print(f"jaccard: {jaccard_tokens(a, b):.3f}")
    print(f"bleu: {bleu_score(a, b):.3f}")
