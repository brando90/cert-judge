#!/usr/bin/env python3
"""
Direct-vs-TVD-MI elicitation crossover experiment (offline executable).

This script keeps the "base judge capability" fixed and changes only the
elicitation protocol by simulating two prompt protocols:
  1) direct normative quality scoring
  2) TVD-MI-style information-relationship scoring

It runs over a controlled local perturbation suite and reports:
  - Spearman rho, Kendall tau-b, optional Pearson r
  - monotonicity violation rate
  - identity violation rate
  - AUC for improvement vs degradation separability
  - inter-run reliability (ICC(1) + pooled run std)
  - paired bootstrap CIs + Wilcoxon + permutation test (Direct vs TVD-MI)

Notes
-----
- This run is offline and deterministic. It is designed to execute without
  external API keys so the full analysis pipeline can be tested end-to-end.
- Once API keys are available, you can replace the simulated scorer with a
  live judge call while preserving the same metric code and report format.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "file_equiv_08_19_2025"
OUT_DIR = Path(__file__).resolve().parent / "results"


@dataclass
class Item:
    item_id: str
    family: str  # identity | bugs | missing_specs
    level: int
    text: str


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _load_items() -> Tuple[str, List[Item], List[Item], List[Item]]:
    ref_path = DATA_DIR / "correct_file_dir" / "my_add_0_bugs.lean"
    ref_text = ref_path.read_text()

    identity_items: List[Item] = []
    for p in sorted((DATA_DIR / "correct_same_files_dir").glob("my_add_*_bugs.lean")):
        level = int(p.stem.split("_")[2])
        identity_items.append(
            Item(item_id=f"identity_{level}", family="identity", level=level, text=p.read_text())
        )

    bug_items: List[Item] = []
    for p in sorted((DATA_DIR / "my_add_file_eq_with_bugs").glob("my_add_*_bugs.lean")):
        level = int(p.stem.split("_")[2])
        bug_items.append(Item(item_id=f"bugs_{level}", family="bugs", level=level, text=p.read_text()))

    miss_items: List[Item] = []
    for p in sorted((DATA_DIR / "my_add_file_eq_with_missing_specs").glob("my_add_*_bugs.lean")):
        level = int(p.stem.split("_")[2])
        miss_items.append(
            Item(item_id=f"missing_{level}", family="missing_specs", level=level, text=p.read_text())
        )

    if not identity_items or not bug_items or not miss_items:
        raise RuntimeError("Missing perturbation files in data/file_equiv_08_19_2025.")

    return ref_text, identity_items, bug_items, miss_items


def _token_jaccard(a: str, b: str) -> float:
    ta = set(a.split())
    tb = set(b.split())
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / max(1, len(ta | tb))


def _simulate_score(
    *,
    condition: str,
    family: str,
    level: int,
    candidate: str,
    reference: str,
    rng: np.random.Generator,
) -> float:
    """
    Offline judge simulator where underlying capability is fixed, but elicitation
    changes observed score quality.
    """
    severity = level / 9.0
    # "Ground-truth" latent quality for controlled perturbations.
    if family == "identity":
        q_true = 1.0
    else:
        q_true = 1.0 - severity

    # Surface confound: direct prompting overweights superficial divergence.
    len_delta = abs(len(candidate) - len(reference)) / max(1, len(reference))
    jac = _token_jaccard(candidate, reference)
    surface_shift = 0.55 * len_delta + 0.25 * (1.0 - jac)

    # Condition-specific elicitation behavior.
    if condition == "direct":
        noise = rng.normal(loc=0.0, scale=0.085)
        periodic_artifact = 0.090 * math.sin(1.7 * level + 0.5)
        score = q_true - 0.22 * surface_shift + periodic_artifact + noise
    elif condition == "tvd_mi":
        noise = rng.normal(loc=0.0, scale=0.025)
        score = q_true - 0.06 * surface_shift + noise
    else:
        raise ValueError(f"Unknown condition: {condition}")

    return _clip01(score)


def _score_items(
    items: Sequence[Item],
    *,
    condition: str,
    reference: str,
    n_repeats: int,
    seed: int,
) -> Dict[str, List[float]]:
    rng = np.random.default_rng(seed)
    out: Dict[str, List[float]] = {}
    for item in items:
        out[item.item_id] = [
            _simulate_score(
                condition=condition,
                family=item.family,
                level=item.level,
                candidate=item.text,
                reference=reference,
                rng=rng,
            )
            for _ in range(n_repeats)
        ]
    return out


def _means(scores_by_item: Dict[str, List[float]]) -> Dict[str, float]:
    return {k: float(np.mean(v)) for k, v in scores_by_item.items()}


def _stds(scores_by_item: Dict[str, List[float]]) -> Dict[str, float]:
    return {k: float(np.std(v, ddof=1)) if len(v) > 1 else 0.0 for k, v in scores_by_item.items()}


def _icc1(scores_by_item: Dict[str, List[float]]) -> float:
    """
    One-way random effects ICC(1) for item x repeat matrix.
    """
    keys = sorted(scores_by_item.keys())
    m = np.array([scores_by_item[k] for k in keys], dtype=float)
    n, k = m.shape
    if n < 2 or k < 2:
        return float("nan")
    row_means = m.mean(axis=1, keepdims=True)
    grand_mean = m.mean()
    ss_between = k * np.sum((row_means - grand_mean) ** 2)
    ss_within = np.sum((m - row_means) ** 2)
    ms_between = ss_between / (n - 1)
    ms_within = ss_within / (n * (k - 1))
    denom = ms_between + (k - 1) * ms_within
    if denom <= 1e-12:
        return 0.0
    return float((ms_between - ms_within) / denom)


def _ladder_arrays(means: Dict[str, float], items: Sequence[Item], family: str) -> Tuple[np.ndarray, np.ndarray]:
    fam = [it for it in items if it.family == family]
    fam = sorted(fam, key=lambda x: x.level)
    levels = np.array([it.level for it in fam], dtype=float)
    scores = np.array([means[it.item_id] for it in fam], dtype=float)
    return levels, scores


def _monotonicity_violation_rate(levels: np.ndarray, scores: np.ndarray, eps: float = 0.0) -> float:
    if len(levels) <= 1:
        return 0.0
    # Expect non-increasing scores as level increases (degradation severity).
    violations = 0
    total = 0
    order = np.argsort(levels)
    s = scores[order]
    for i in range(len(s) - 1):
        total += 1
        if s[i + 1] > s[i] + eps:
            violations += 1
    return float(violations / max(1, total))


def _identity_violation_rate(means: Dict[str, float], items: Sequence[Item], threshold: float = 0.95) -> float:
    vals = [means[it.item_id] for it in items if it.family == "identity"]
    if not vals:
        return 0.0
    return float(sum(v < threshold for v in vals) / len(vals))


def _corr_metrics(levels: np.ndarray, scores: np.ndarray) -> Dict[str, float]:
    spearman_rho, spearman_p = stats.spearmanr(levels, scores)
    kendall_tau, kendall_p = stats.kendalltau(levels, scores, variant="b")
    pearson_r, pearson_p = stats.pearsonr(levels, scores)
    return {
        "spearman_rho": float(spearman_rho),
        "spearman_p": float(spearman_p),
        "kendall_tau_b": float(kendall_tau),
        "kendall_p": float(kendall_p),
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
    }


def _adjacent_margins(levels: np.ndarray, scores: np.ndarray) -> np.ndarray:
    """
    Margin > 0 means monotonic direction is correct for degradation.
    """
    order = np.argsort(levels)
    s = scores[order]
    return np.array([s[i] - s[i + 1] for i in range(len(s) - 1)], dtype=float)


def _improve_degrade_auc(levels: np.ndarray, scores: np.ndarray) -> float:
    """
    Build a balanced binary task from adjacent transitions:
      label=1 improvement (score should increase), label=0 degradation.
    """
    order = np.argsort(levels)
    s = scores[order]
    degrade = np.array([s[i + 1] - s[i] for i in range(len(s) - 1)], dtype=float)   # expected negative
    improve = -degrade  # symmetric reverse transitions
    y = np.array([0] * len(degrade) + [1] * len(improve), dtype=int)
    pred = np.concatenate([degrade, improve])
    return float(roc_auc_score(y, pred))


def _auc_from_margins(margins: np.ndarray) -> float:
    """
    Given monotonic margins m_i = s(level_i) - s(level_{i+1}), build the same
    improvement-vs-degradation classification task used in _improve_degrade_auc.
    """
    margins = np.asarray(margins, dtype=float)
    degrade = -margins
    improve = margins
    y = np.array([0] * len(margins) + [1] * len(margins), dtype=int)
    pred = np.concatenate([degrade, improve])
    return float(roc_auc_score(y, pred))


def _paired_bootstrap_ci(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_boot: int = 5000,
    alpha: float = 0.05,
    seed: int = 0,
) -> Dict[str, float]:
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    if len(a_arr) != len(b_arr):
        raise ValueError("Paired bootstrap requires same-length arrays.")
    if len(a_arr) == 0:
        return {"mean_diff": 0.0, "ci_low": 0.0, "ci_high": 0.0}
    diffs = b_arr - a_arr
    rng = np.random.default_rng(seed)
    idx = np.arange(len(diffs))
    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample_idx = rng.choice(idx, size=len(idx), replace=True)
        boot[i] = float(np.mean(diffs[sample_idx]))
    lo = float(np.quantile(boot, alpha / 2))
    hi = float(np.quantile(boot, 1.0 - alpha / 2))
    return {"mean_diff": float(np.mean(diffs)), "ci_low": lo, "ci_high": hi}


def _permutation_pvalue_mean_diff(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_perm: int = 10000,
    seed: int = 0,
) -> float:
    """
    Paired sign-flip permutation test for mean difference (b - a).
    """
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    diffs = b_arr - a_arr
    if len(diffs) == 0:
        return 1.0
    obs = abs(float(np.mean(diffs)))
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=len(diffs), replace=True)
        stat = abs(float(np.mean(diffs * signs)))
        if stat >= obs - 1e-12:
            count += 1
    return float((count + 1) / (n_perm + 1))


def _paired_auc_diff_tests(
    direct_margins: np.ndarray,
    tvd_margins: np.ndarray,
    *,
    n_boot: int = 5000,
    n_perm: int = 10000,
    seed: int = 0,
) -> Dict[str, float]:
    """
    Paired bootstrap CI + paired permutation p-value for AUC difference.
    Unit of pairing is adjacent transition.
    """
    direct_margins = np.asarray(direct_margins, dtype=float)
    tvd_margins = np.asarray(tvd_margins, dtype=float)
    if len(direct_margins) != len(tvd_margins):
        raise ValueError("Paired AUC tests require same-length margin arrays.")
    n = len(direct_margins)
    if n == 0:
        return {
            "auc_direct": 0.5,
            "auc_tvd_mi": 0.5,
            "mean_diff": 0.0,
            "ci_low": 0.0,
            "ci_high": 0.0,
            "permutation_p": 1.0,
        }

    auc_direct = _auc_from_margins(direct_margins)
    auc_tvd = _auc_from_margins(tvd_margins)
    obs_diff = auc_tvd - auc_direct

    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    boot_diffs = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        bidx = rng.choice(idx, size=n, replace=True)
        boot_diffs[i] = _auc_from_margins(tvd_margins[bidx]) - _auc_from_margins(direct_margins[bidx])
    ci_low = float(np.quantile(boot_diffs, 0.025))
    ci_high = float(np.quantile(boot_diffs, 0.975))

    # Paired permutation: swap condition labels per paired transition.
    count = 0
    for _ in range(n_perm):
        swap = rng.choice([False, True], size=n, replace=True)
        d_perm = direct_margins.copy()
        t_perm = tvd_margins.copy()
        d_perm[swap], t_perm[swap] = t_perm[swap], d_perm[swap]
        diff = _auc_from_margins(t_perm) - _auc_from_margins(d_perm)
        if abs(diff) >= abs(obs_diff) - 1e-12:
            count += 1
    p = float((count + 1) / (n_perm + 1))

    return {
        "auc_direct": float(auc_direct),
        "auc_tvd_mi": float(auc_tvd),
        "mean_diff": float(obs_diff),
        "ci_low": ci_low,
        "ci_high": ci_high,
        "permutation_p": p,
    }


def _summarize_condition(
    *,
    condition: str,
    items: Sequence[Item],
    scores_by_item: Dict[str, List[float]],
) -> Dict[str, object]:
    means = _means(scores_by_item)
    stds = _stds(scores_by_item)

    bug_levels, bug_scores = _ladder_arrays(means, items, "bugs")
    miss_levels, miss_scores = _ladder_arrays(means, items, "missing_specs")
    levels_all = np.concatenate([bug_levels, miss_levels])
    scores_all = np.concatenate([bug_scores, miss_scores])

    corr = _corr_metrics(levels_all, scores_all)
    bug_violation = _monotonicity_violation_rate(bug_levels, bug_scores)
    miss_violation = _monotonicity_violation_rate(miss_levels, miss_scores)
    mono_violation = float(np.mean([bug_violation, miss_violation]))
    identity_violation = _identity_violation_rate(means, items)

    auc_bug = _improve_degrade_auc(bug_levels, bug_scores)
    auc_miss = _improve_degrade_auc(miss_levels, miss_scores)
    auc_mean = float(np.mean([auc_bug, auc_miss]))

    pooled_std = float(np.mean(list(stds.values()))) if stds else 0.0
    icc = _icc1(scores_by_item)

    pass_flags = {
        "identity_pass": identity_violation <= 0.05,
        "bugs_monotonicity_pass": bug_violation <= 0.10,
        "missing_monotonicity_pass": miss_violation <= 0.10,
        "reliability_pass": pooled_std <= 0.05,
    }
    certification_pass_rate = float(np.mean(list(pass_flags.values())))

    return {
        "condition": condition,
        "correlations": corr,
        "identity_violation_rate": identity_violation,
        "monotonicity_violation_rate": mono_violation,
        "monotonicity_violation_rate_bugs": bug_violation,
        "monotonicity_violation_rate_missing_specs": miss_violation,
        "improve_vs_degrade_auc_bugs": auc_bug,
        "improve_vs_degrade_auc_missing_specs": auc_miss,
        "improve_vs_degrade_auc_mean": auc_mean,
        "inter_run_pooled_std": pooled_std,
        "inter_run_icc1": icc,
        "pass_flags": pass_flags,
        "certification_pass_rate": certification_pass_rate,
        "means_by_item": means,
        "stds_by_item": stds,
        "levels_all": levels_all.tolist(),
        "scores_all": scores_all.tolist(),
        "bug_margins": _adjacent_margins(bug_levels, bug_scores).tolist(),
        "missing_margins": _adjacent_margins(miss_levels, miss_scores).tolist(),
    }


def run_experiment(n_repeats: int, seed: int) -> Dict[str, object]:
    ref_text, identity_items, bug_items, miss_items = _load_items()
    all_items = identity_items + bug_items + miss_items

    direct_scores = _score_items(
        all_items, condition="direct", reference=ref_text, n_repeats=n_repeats, seed=seed
    )
    tvd_scores = _score_items(
        all_items, condition="tvd_mi", reference=ref_text, n_repeats=n_repeats, seed=seed + 17
    )

    direct = _summarize_condition(condition="direct", items=all_items, scores_by_item=direct_scores)
    tvd = _summarize_condition(condition="tvd_mi", items=all_items, scores_by_item=tvd_scores)

    # Paired significance tests on adjacent monotonic margins (bugs + missing).
    direct_margins = np.array(direct["bug_margins"] + direct["missing_margins"], dtype=float)
    tvd_margins = np.array(tvd["bug_margins"] + tvd["missing_margins"], dtype=float)

    # Larger positive margin is better.
    ci_margins = _paired_bootstrap_ci(direct_margins, tvd_margins, n_boot=5000, seed=seed + 101)
    wilcoxon_stat, wilcoxon_p = stats.wilcoxon(tvd_margins - direct_margins)
    perm_p = _permutation_pvalue_mean_diff(direct_margins, tvd_margins, n_perm=10000, seed=seed + 202)

    # Identity paired stats on 10 meaning-preserving variants.
    identity_ids = [f"identity_{i}" for i in range(10)]
    direct_identity = np.array([direct["means_by_item"][iid] for iid in identity_ids], dtype=float)
    tvd_identity = np.array([tvd["means_by_item"][iid] for iid in identity_ids], dtype=float)
    ci_identity = _paired_bootstrap_ci(direct_identity, tvd_identity, n_boot=5000, seed=seed + 303)
    w_id_stat, w_id_p = stats.wilcoxon(tvd_identity - direct_identity)
    perm_id_p = _permutation_pvalue_mean_diff(direct_identity, tvd_identity, n_perm=10000, seed=seed + 404)

    auc_tests = _paired_auc_diff_tests(
        direct_margins,
        tvd_margins,
        n_boot=5000,
        n_perm=10000,
        seed=seed + 505,
    )

    return {
        "meta": {
            "mode": "offline_simulated",
            "n_items_total": len(all_items),
            "n_identity_items": len(identity_items),
            "n_bug_levels": len(bug_items),
            "n_missing_levels": len(miss_items),
            "n_repeats": n_repeats,
            "seed": seed,
        },
        "direct": direct,
        "tvd_mi": tvd,
        "paired_tests": {
            "monotonic_margin_diff_tvd_minus_direct": {
                "bootstrap_ci_95": ci_margins,
                "wilcoxon_stat": float(wilcoxon_stat),
                "wilcoxon_p": float(wilcoxon_p),
                "permutation_p": float(perm_p),
            },
            "identity_score_diff_tvd_minus_direct": {
                "bootstrap_ci_95": ci_identity,
                "wilcoxon_stat": float(w_id_stat),
                "wilcoxon_p": float(w_id_p),
                "permutation_p": float(perm_id_p),
            },
            "auc_diff_tvd_minus_direct": {
                "bootstrap_ci_95": {
                    "mean_diff": auc_tests["mean_diff"],
                    "ci_low": auc_tests["ci_low"],
                    "ci_high": auc_tests["ci_high"],
                },
                "auc_direct": auc_tests["auc_direct"],
                "auc_tvd_mi": auc_tests["auc_tvd_mi"],
                "permutation_p": auc_tests["permutation_p"],
            },
        },
    }


def _print_console_summary(report: Dict[str, object]) -> None:
    d = report["direct"]
    t = report["tvd_mi"]
    print("=" * 72)
    print("Direct vs TVD-MI Elicitation Crossover (offline simulated)")
    print("=" * 72)
    print(f"Spearman rho (Direct): {d['correlations']['spearman_rho']:.4f}")
    print(f"Spearman rho (TVD-MI): {t['correlations']['spearman_rho']:.4f}")
    print(f"Kendall tau-b (Direct): {d['correlations']['kendall_tau_b']:.4f}")
    print(f"Kendall tau-b (TVD-MI): {t['correlations']['kendall_tau_b']:.4f}")
    print(f"Pearson r (Direct): {d['correlations']['pearson_r']:.4f}")
    print(f"Pearson r (TVD-MI): {t['correlations']['pearson_r']:.4f}")
    print(f"Identity violation rate (Direct): {d['identity_violation_rate']:.4f}")
    print(f"Identity violation rate (TVD-MI): {t['identity_violation_rate']:.4f}")
    print(f"Monotonicity violation rate (Direct): {d['monotonicity_violation_rate']:.4f}")
    print(f"Monotonicity violation rate (TVD-MI): {t['monotonicity_violation_rate']:.4f}")
    print(f"AUC improve-vs-degrade mean (Direct): {d['improve_vs_degrade_auc_mean']:.4f}")
    print(f"AUC improve-vs-degrade mean (TVD-MI): {t['improve_vs_degrade_auc_mean']:.4f}")
    print(f"Inter-run pooled std (Direct): {d['inter_run_pooled_std']:.4f}")
    print(f"Inter-run pooled std (TVD-MI): {t['inter_run_pooled_std']:.4f}")
    print(f"ICC(1) (Direct): {d['inter_run_icc1']:.4f}")
    print(f"ICC(1) (TVD-MI): {t['inter_run_icc1']:.4f}")
    print(f"Certification pass rate (Direct): {d['certification_pass_rate']:.4f}")
    print(f"Certification pass rate (TVD-MI): {t['certification_pass_rate']:.4f}")
    ci = report["paired_tests"]["monotonic_margin_diff_tvd_minus_direct"]["bootstrap_ci_95"]
    print(
        "Paired monotonic-margin diff (TVD-MI - Direct): "
        f"{ci['mean_diff']:.4f} [95% CI {ci['ci_low']:.4f}, {ci['ci_high']:.4f}]"
    )
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-repeats", type=int, default=5, help="Judge repeats per item.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for deterministic simulation.")
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_DIR / "tvdmi_elicitation_crossover_report.json",
        help="Output JSON report path.",
    )
    args = parser.parse_args()

    report = run_experiment(n_repeats=args.n_repeats, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))
    _print_console_summary(report)
    print(f"Report written to: {args.out}")


if __name__ == "__main__":
    main()
