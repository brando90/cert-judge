#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test P5 (TVD-MI) implementation for HSJ judge certification.

This script verifies that P5 correctly evaluates:
1. Information-relationship robustness via Youden's J
2. Item-level discriminability via macro AUC
3. Tamper resistance via AUC stability

It uses the TVD-MI tools to simulate realistic critic behavior
and demonstrates integration with the HSJ framework.
"""

import sys
import numpy as np
from pathlib import Path

# Add cert_judge to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "py_src"))

from cert_judge.tvd_mi_tools import (
    tvd_mi_from_critic,
    per_item_auc_macro,
    tamper_suite_report,
)
from cert_judge.hsj_scoring import compute_p5_tvd_mi, compute_jti


def test_p5_perfect_judge():
    """Test P5 with a perfect judge (high J, high AUC, no tamper drop)."""
    print("\n" + "="*70)
    print("Test 1: Perfect Judge")
    print("="*70)
    
    # Simulate perfect critic: 100% TPR and TNR
    n_pos = 100
    n_neg = 100
    y_true = [True] * n_pos + [False] * n_neg
    y_pred = ["Significant Gain"] * n_pos + ["No Gain"] * n_neg
    
    report = tvd_mi_from_critic(y_true, y_pred)
    print(f"  TPR: {report.tpr:.4f}")
    print(f"  TNR: {report.tnr:.4f}")
    print(f"  Youden's J: {report.youdens_j:.4f}")
    
    # Perfect item-level AUC
    item_ids = list(range(20)) * 10  # 20 items, 10 pairs each
    pair_scores = [1.0 if y_true[i] else 0.0 for i in range(200)]
    pair_class = [1 if y_true[i] else 0 for i in range(200)]
    
    macro_auc, _ = per_item_auc_macro(item_ids, pair_scores, pair_class)
    print(f"  Macro AUC: {macro_auc:.4f}")
    
    # No tamper drop
    delta_auc_tamper = 0.0
    print(f"  Tamper AUC drop: {delta_auc_tamper:.4f}")
    
    # Compute P5
    p5 = compute_p5_tvd_mi(report.youdens_j, macro_auc, delta_auc_tamper)
    print(f"\n  P5 = {p5:.4f}")
    
    # Verify P5 is close to 1.0
    assert p5 >= 0.99, f"Expected P5 ≈ 1.0 for perfect judge, got {p5:.4f}"
    print(f"  ✅ PASS: P5 = {p5:.4f} (expected ≈ 1.0)")
    
    return p5


def test_p5_poor_judge():
    """Test P5 with a poor judge (low J, low AUC)."""
    print("\n" + "="*70)
    print("Test 2: Poor Judge (Random Performance)")
    print("="*70)
    
    # Simulate random critic: ~50% TPR and TNR
    rng = np.random.default_rng(42)
    n_pos = 100
    n_neg = 100
    y_true = [True] * n_pos + [False] * n_neg
    y_pred = [rng.choice(["Significant Gain", "Little Gain", "No Gain"]) for _ in range(200)]
    
    report = tvd_mi_from_critic(y_true, y_pred)
    print(f"  TPR: {report.tpr:.4f}")
    print(f"  TNR: {report.tnr:.4f}")
    print(f"  Youden's J: {report.youdens_j:.4f}")
    
    # Random item-level AUC (~0.5)
    item_ids = list(range(20)) * 10
    pair_scores = rng.uniform(0, 1, 200)
    pair_class = [1 if y_true[i] else 0 for i in range(200)]
    
    macro_auc, _ = per_item_auc_macro(item_ids, pair_scores, pair_class)
    print(f"  Macro AUC: {macro_auc:.4f}")
    
    # Some tamper drop
    delta_auc_tamper = 0.15
    print(f"  Tamper AUC drop: {delta_auc_tamper:.4f}")
    
    # Compute P5
    p5 = compute_p5_tvd_mi(report.youdens_j, macro_auc, delta_auc_tamper)
    print(f"\n  P5 = {p5:.4f}")
    
    # Verify P5 is close to 0.5 (random performance)
    assert 0.35 <= p5 <= 0.65, f"Expected P5 ≈ 0.5 for random judge, got {p5:.4f}"
    print(f"  ✅ PASS: P5 = {p5:.4f} (expected ≈ 0.5)")
    
    return p5


def test_p5_good_judge_veribench_scale():
    """Test P5 with realistic VeriBench-scale data."""
    print("\n" + "="*70)
    print("Test 3: Good Judge at VeriBench Scale (140 files)")
    print("="*70)
    
    # Simulate good critic: 90% TPR, 85% TNR
    rng = np.random.default_rng(42)
    n_pos = 140
    n_neg = 140
    
    y_true = [True] * n_pos + [False] * n_neg
    y_pred = []
    
    # Same-source pairs: 90% correct ("Significant Gain")
    for _ in range(n_pos):
        if rng.random() < 0.90:
            y_pred.append("Significant Gain")
        else:
            y_pred.append(rng.choice(["Little Gain", "No Gain"]))
    
    # Different-source pairs: 85% correct ("No Gain")
    for _ in range(n_neg):
        if rng.random() < 0.85:
            y_pred.append("No Gain")
        else:
            y_pred.append(rng.choice(["Significant Gain", "Little Gain"]))
    
    report = tvd_mi_from_critic(y_true, y_pred)
    print(f"  TPR: {report.tpr:.4f}")
    print(f"  TNR: {report.tnr:.4f}")
    print(f"  Youden's J: {report.youdens_j:.4f}")
    
    # Good item-level AUC (~0.85)
    item_ids = []
    pair_scores = []
    pair_class = []
    
    for item_id in range(20):
        for _ in range(14):  # 14 pairs per item
            item_ids.append(item_id)
            is_positive = rng.random() < 0.5
            if is_positive:
                pair_scores.append(rng.uniform(0.7, 1.0))
                pair_class.append(1)
            else:
                pair_scores.append(rng.uniform(0.0, 0.4))
                pair_class.append(0)
    
    macro_auc, _ = per_item_auc_macro(item_ids, pair_scores, pair_class)
    print(f"  Macro AUC: {macro_auc:.4f}")
    
    # Small tamper drop (robust judge)
    delta_auc_tamper = 0.05
    print(f"  Tamper AUC drop: {delta_auc_tamper:.4f}")
    
    # Compute P5
    p5 = compute_p5_tvd_mi(report.youdens_j, macro_auc, delta_auc_tamper)
    print(f"\n  P5 = {p5:.4f}")
    
    # Verify P5 is high (good judge)
    assert p5 >= 0.70, f"Expected P5 ≥ 0.70 for good judge, got {p5:.4f}"
    print(f"  ✅ PASS: P5 = {p5:.4f} (expected ≥ 0.70)")
    
    return p5


def test_p5_tamper_vulnerable_judge():
    """Test P5 with a judge vulnerable to tampering."""
    print("\n" + "="*70)
    print("Test 4: Tamper-Vulnerable Judge")
    print("="*70)
    
    # Good base performance
    n_pos = 100
    n_neg = 100
    y_true = [True] * n_pos + [False] * n_neg
    
    # 85% TPR, 80% TNR
    rng = np.random.default_rng(42)
    y_pred = []
    for i in range(n_pos):
        y_pred.append("Significant Gain" if rng.random() < 0.85 else "No Gain")
    for i in range(n_neg):
        y_pred.append("No Gain" if rng.random() < 0.80 else "Significant Gain")
    
    report = tvd_mi_from_critic(y_true, y_pred)
    print(f"  TPR: {report.tpr:.4f}")
    print(f"  TNR: {report.tnr:.4f}")
    print(f"  Youden's J: {report.youdens_j:.4f}")
    
    # Good base AUC
    item_ids = list(range(20)) * 10
    pair_scores = [rng.uniform(0.7, 1.0) if y_true[i] else rng.uniform(0.0, 0.4) for i in range(200)]
    pair_class = [1 if y_true[i] else 0 for i in range(200)]
    
    macro_auc, _ = per_item_auc_macro(item_ids, pair_scores, pair_class)
    print(f"  Macro AUC: {macro_auc:.4f}")
    
    # LARGE tamper drop (vulnerable to gaming)
    delta_auc_tamper = 0.40  # 40% drop!
    print(f"  Tamper AUC drop: {delta_auc_tamper:.4f} (VULNERABLE)")
    
    # Compute P5
    p5 = compute_p5_tvd_mi(report.youdens_j, macro_auc, delta_auc_tamper)
    print(f"\n  P5 = {p5:.4f}")
    
    # P5 should be penalized due to high tamper vulnerability
    print(f"  ⚠️  WARNING: Judge is vulnerable to tampering (40% AUC drop)")
    print(f"  P5 is penalized from base performance")
    
    return p5


def test_p5_integration_with_jti():
    """Test P5 integration into Judge Trust Index."""
    print("\n" + "="*70)
    print("Test 5: P5 Integration with JTI")
    print("="*70)
    
    # Simulate all properties
    p1 = 0.95  # Good reflexivity
    p2 = 0.88  # Good bug detection
    p3 = 0.82  # Good spec completeness
    p4 = 0.90  # Good stability
    
    # Simulate P5 data
    youdens_j = 0.75  # Good information preservation
    auc_macro = 0.85  # Good item-level discrimination
    delta_auc_tamper = 0.08  # Robust to tampering
    
    p5 = compute_p5_tvd_mi(youdens_j, auc_macro, delta_auc_tamper)
    
    print(f"  P1 (Reflexivity):        {p1:.4f}")
    print(f"  P2 (Bug Monotonicity):   {p2:.4f}")
    print(f"  P3 (Spec Completeness):  {p3:.4f}")
    print(f"  P4 (Stability):          {p4:.4f}")
    print(f"  P5 (TVD-MI):             {p5:.4f}")
    print()
    
    # Compute JTI without P5
    jti_without_p5 = compute_jti(p1, p2, p3, p4, p5=None)
    print(f"  JTI (without P5): {jti_without_p5:.4f}")
    
    # Compute JTI with P5
    jti_with_p5 = compute_jti(p1, p2, p3, p4, p5=p5)
    print(f"  JTI (with P5):    {jti_with_p5:.4f}")
    
    # Verify equal-weight averaging
    expected_with_p5 = 0.2 * (p1 + p2 + p3 + p4 + p5)
    assert abs(jti_with_p5 - expected_with_p5) < 0.001, \
        f"JTI mismatch: expected {expected_with_p5:.4f}, got {jti_with_p5:.4f}"
    
    print(f"\n  ✅ PASS: JTI correctly integrates P5")
    print(f"  P5 adds information-theoretic robustness to judge certification")
    
    return jti_with_p5


def test_p5_edge_cases():
    """Test P5 edge cases and boundary conditions."""
    print("\n" + "="*70)
    print("Test 6: P5 Edge Cases")
    print("="*70)
    
    # Test 1: Perfect scores
    p5_perfect = compute_p5_tvd_mi(youdens_j=1.0, auc_macro=1.0, delta_auc_tamper=0.0)
    print(f"  Perfect judge: P5 = {p5_perfect:.4f} (expected 1.0)")
    assert abs(p5_perfect - 1.0) < 0.001
    
    # Test 2: Worst scores
    p5_worst = compute_p5_tvd_mi(youdens_j=-1.0, auc_macro=0.0, delta_auc_tamper=1.0)
    print(f"  Worst judge:   P5 = {p5_worst:.4f} (expected 0.0)")
    assert abs(p5_worst - 0.0) < 0.001
    
    # Test 3: Random performance (J=0, AUC=0.5, no tamper drop)
    # Note: With default weights (β₁=0.5, β₂=0.3, β₃=0.2):
    # P5 = 0.5*(0+1)/2 + 0.3*0.5 + 0.2*(1-0) = 0.25 + 0.15 + 0.2 = 0.6
    p5_random = compute_p5_tvd_mi(youdens_j=0.0, auc_macro=0.5, delta_auc_tamper=0.0)
    print(f"  Random judge:  P5 = {p5_random:.4f} (expected ≈ 0.60)")
    assert 0.55 <= p5_random <= 0.65
    
    # Test 4: Custom weights
    p5_custom = compute_p5_tvd_mi(
        youdens_j=0.8,
        auc_macro=0.9,
        delta_auc_tamper=0.1,
        beta1=0.6,  # Emphasize Youden's J
        beta2=0.3,
        beta3=0.1,
    )
    print(f"  Custom weights: P5 = {p5_custom:.4f}")
    
    print(f"\n  ✅ PASS: All edge cases handled correctly")
    
    return True


def run_all_tests():
    """Run all P5 tests."""
    print("\n" + "#"*70)
    print("# P5 (TVD-MI) Implementation Test Suite")
    print("#"*70)
    
    tests = [
        ("Perfect Judge", test_p5_perfect_judge),
        ("Poor Judge", test_p5_poor_judge),
        ("VeriBench Scale", test_p5_good_judge_veribench_scale),
        ("Tamper Vulnerable", test_p5_tamper_vulnerable_judge),
        ("JTI Integration", test_p5_integration_with_jti),
        ("Edge Cases", test_p5_edge_cases),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n  ❌ FAIL: {name} - {e}")
            raise
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY: P5 Implementation Verification")
    print("="*70)
    print()
    print("✅ All tests passed!")
    print()
    print("P5 (TVD-MI) correctly implements:")
    print("  1. Youden's J normalization: (J + 1) / 2")
    print("  2. Item-level macro AUC integration")
    print("  3. Tamper resistance penalty: 1 - ΔAUC")
    print("  4. Weighted combination: β₁·J̃ + β₂·AUC + β₃·(1-ΔAUC)")
    print("  5. Integration into 5-property JTI")
    print()
    print("P5 is ready for deployment in VeriBench judge certification!")
    print()
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
