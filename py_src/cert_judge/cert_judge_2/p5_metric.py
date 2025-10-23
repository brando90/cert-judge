"""
P5: TVD‑MI (Information‑Relationship Robustness) metric.

Implements the P5 property as described in scoring_judges.md:
- Build TVD lower bound via Youden's J from a categorical critic.
- Compute item‑level macro AUC from critic scores.
- Optionally quantify tamper robustness via the maximal AUC drop.
- Combine facets with weights that sum to 1.

This module depends only on numpy and the helper utilities in
cert_judge.tvd_mi_tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from .tvd_mi_tools import (
    CriticLabel,
    TVDMIReport,
    tvd_mi_from_critic,
    per_item_auc_macro,
)


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass
class P5Inputs:
    # Ground truth for pairs: True if two outputs share the same source
    y_true_same_source: Sequence[bool]
    # Categorical critic outputs per pair
    y_pred_labels: Sequence[CriticLabel]
    # Optional: item IDs per pair to compute item‑level macro AUC
    item_ids: Optional[Sequence[Union[str, int]]] = None
    # Optional: critic confidence/scores per pair for AUC; if None, derive
    # from labels via a simple mapping.
    pair_scores: Optional[Sequence[float]] = None
    # Optional: tamper transforms -> new scores per pair; used to compute
    # AUC drop under tampering. If None/empty, we skip tamper penalty.
    tamper_scores: Optional[Mapping[str, Sequence[float]]] = None
    # Weights for combining facets; must be non‑negative. They will be
    # normalized to sum to 1 internally.
    beta1_j: float = 1/3
    beta2_auc: float = 1/3
    beta3_tamper: float = 1/3


@dataclass
class P5Report:
    # Sub‑metrics
    youdens_j: float          # in [-1, 1]
    J_tilde: float            # (J+1)/2 in [0,1]
    macro_auc: float          # in [0,1]
    tamper_auc_drop: float    # max drop ≥ 0
    tamper_component: float   # 1 - drop in [0,1]
    # Final P5 and supporting report
    p5: float
    tvdmi_report: TVDMIReport
    per_item_aucs: List[Tuple[Union[str, int], float]]
    tamper_details: Mapping[str, Tuple[float, float, float]]  # name -> (auc_before, auc_after, delta)


def _default_label_score(label: CriticLabel) -> float:
    # Natural ordering: Significant > Little > None
    if label == "Significant Gain":
        return 1.0
    if label == "Little Gain":
        return 0.5
    return 0.0


def compute_p5(inputs: P5Inputs) -> P5Report:
    # 1) TVD‑MI via Youden's J
    tvd_rep = tvd_mi_from_critic(inputs.y_true_same_source, inputs.y_pred_labels)
    J = float(tvd_rep.youdens_j)
    J_tilde = _clip01((J + 1.0) / 2.0)

    # 2) Item‑level macro AUC
    if inputs.item_ids is not None:
        # Determine scores for AUC: use provided or map from labels
        if inputs.pair_scores is None:
            scores = np.array([_default_label_score(lbl) for lbl in inputs.y_pred_labels], dtype=float)
        else:
            scores = np.asarray(inputs.pair_scores, dtype=float)

        # Positive for AUC = same‑source pairs (class 1), negative = different (class 0)
        y = np.asarray(inputs.y_true_same_source, dtype=bool)
        per_class = np.where(y, 1, 0)
        macro_auc, per_item = per_item_auc_macro(inputs.item_ids, scores, per_class)
    else:
        macro_auc, per_item = 0.5, []

    macro_auc = _clip01(float(macro_auc))

    # 3) Tamper robustness: compute AUC drop per transform and take maximum drop
    tamper_details: dict[str, Tuple[float, float, float]] = {}
    tamper_drop = 0.0
    if inputs.tamper_scores:
        # Baseline AUC on the same scores used above
        if inputs.item_ids is None:
            # If we cannot compute item‑level AUC, fall back to pooled binary AUC over pairs
            # Approximate pooled AUC from per_item_auc_macro by putting all pairs under one pseudo item
            pseudo_ids = [0] * len(list(inputs.y_true_same_source))
            if inputs.pair_scores is None:
                base_scores = np.array([_default_label_score(lbl) for lbl in inputs.y_pred_labels], dtype=float)
            else:
                base_scores = np.asarray(inputs.pair_scores, dtype=float)
            y = np.asarray(inputs.y_true_same_source, dtype=bool)
            per_class = np.where(y, 1, 0)
            base_auc, _ = per_item_auc_macro(pseudo_ids, base_scores, per_class)
        else:
            base_auc = macro_auc

        for name, sc in inputs.tamper_scores.items():
            sc = np.asarray(sc, dtype=float)
            if inputs.item_ids is None:
                pseudo_ids = [0] * len(sc)
                y = np.asarray(inputs.y_true_same_source, dtype=bool)
                per_class = np.where(y, 1, 0)
                auc_after, _ = per_item_auc_macro(pseudo_ids, sc, per_class)
            else:
                auc_after, _ = per_item_auc_macro(inputs.item_ids, sc, per_class)  # type: ignore[arg-type]
            delta = float(auc_after - base_auc)
            tamper_details[str(name)] = (float(base_auc), float(auc_after), float(delta))
            tamper_drop = max(tamper_drop, max(0.0, -delta))  # maximal drop

    tamper_component = _clip01(1.0 - tamper_drop)

    # 4) Combine facets
    b1 = max(0.0, float(inputs.beta1_j))
    b2 = max(0.0, float(inputs.beta2_auc))
    b3 = max(0.0, float(inputs.beta3_tamper))
    s = b1 + b2 + b3
    if s <= 0:
        b1 = b2 = b3 = 1/3
        s = 1.0
    b1, b2, b3 = b1 / s, b2 / s, b3 / s

    p5 = _clip01(b1 * J_tilde + b2 * macro_auc + b3 * tamper_component)

    return P5Report(
        youdens_j=J,
        J_tilde=J_tilde,
        macro_auc=macro_auc,
        tamper_auc_drop=tamper_drop,
        tamper_component=tamper_component,
        p5=p5,
        tvdmi_report=tvd_rep,
        per_item_aucs=per_item,
        tamper_details=tamper_details,
    )


