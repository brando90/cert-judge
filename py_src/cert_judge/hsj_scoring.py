"""
Hybrid Spec‑Judging Score (HSJ‑Score) implementation for cert-judge.

Provides:
- Property metrics P1–P4 for judge certification
- Judge Trust Index (JTI)
- Isotonic calibration (sklearn if available; PAV fallback)
- Hybrid score fusion combining supervised (judge) and unsupervised (MI) signals

All functions return floats in [0,1] unless stated otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _safe_mean(xs: Sequence[float]) -> float:
    xs_list = list(xs)
    if not xs_list:
        return 0.0
    return sum(xs_list) / len(xs_list)


def _pairwise_ordering_auc(xs: Sequence[float], ys: Sequence[float]) -> float:
    """
    Pairwise ordering AUC: probability that when x_i < x_j we have y_i > y_j.
    Ties in y get 0.5 credit. Returns AUC in [0,1].
    """
    x = list(xs)
    y = list(ys)
    n = len(x)
    if n <= 1:
        return 0.5

    correct = 0.0
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            if x[i] == x[j]:
                continue
            total += 1
            if x[i] < x[j]:
                if y[i] > y[j]:
                    correct += 1.0
                elif y[i] == y[j]:
                    correct += 0.5
            else:  # x[i] > x[j]
                if y[j] > y[i]:
                    correct += 1.0
                elif y[i] == y[j]:
                    correct += 0.5
    if total == 0:
        return 0.5
    return correct / float(total)


# --- Properties P1–P4 ---------------------------------------------------------

def compute_p1_identity(identity_scores_norm: Sequence[float]) -> float:
    """
    P1 — Identity/Consistency.
    Returns the median normalized score on identity pairs (gold vs gold).
    """
    s = sorted(_clip01(v) for v in identity_scores_norm)
    if not s:
        return 0.0
    m = len(s)
    if m % 2 == 1:
        return float(s[m // 2])
    return float(0.5 * (s[m // 2 - 1] + s[m // 2]))


def compute_p2_or_p3_ordering_auc(
    counts: Sequence[Union[int, float]],
    scores_norm: Sequence[float],
) -> float:
    """
    P2/P3 — Monotonicity via pairwise AUC.
    - counts: increasing x (e.g., #bugs or #missing specs)
    - scores_norm: normalized scores in [0,1]
    Maps AUC → [0,1] via P = 2*(AUC - 0.5).
    """
    auc = _pairwise_ordering_auc(counts, scores_norm)
    return _clip01(2.0 * (auc - 0.5))


def compute_p4_stability(
    repeat_scores_by_item: Dict[Union[str, int], Sequence[float]],
    tau: float = 0.05,
) -> float:
    """
    P4 — Low variance (stability/robustness).
    P4 = clip(1 - pooled_within_item_variance / tau^2, 0, 1).
    """
    if tau <= 0:
        raise ValueError("tau must be positive")

    variances: List[float] = []
    for scores in repeat_scores_by_item.values():
        s = list(scores)
        if len(s) <= 1:
            continue
        mu = _safe_mean(s)
        var = _safe_mean([(v - mu) ** 2 for v in s])
        variances.append(var)
    if not variances:
        return 1.0
    pooled_var = _safe_mean(variances)
    return _clip01(1.0 - pooled_var / (tau * tau))


def compute_jti(
    p1: float,
    p2: float,
    p3: float,
    p4: float,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Judge Trust Index (JTI) = w1*p1 + w2*p2 + w3*p3 + w4*p4."""
    if weights is None:
        weights = {"p1": 0.25, "p2": 0.25, "p3": 0.25, "p4": 0.25}
    total_w = sum(max(0.0, float(v)) for v in weights.values())
    if total_w <= 0:
        weights = {"p1": 0.25, "p2": 0.25, "p3": 0.25, "p4": 0.25}
        total_w = 1.0
    w1 = weights.get("p1", 0.0) / total_w
    w2 = weights.get("p2", 0.0) / total_w
    w3 = weights.get("p3", 0.0) / total_w
    w4 = weights.get("p4", 0.0) / total_w
    return _clip01(w1 * _clip01(p1) + w2 * _clip01(p2) + w3 * _clip01(p3) + w4 * _clip01(p4))


# --- Isotonic Regression (sklearn or PAV fallback) ---------------------------

class IsotonicCalibrator:
    """
    Monotone (non-decreasing) calibrator using isotonic regression.
    Prefers scikit-learn when available; otherwise a PAV step-function fallback.
    """

    def __init__(self) -> None:
        self._x_: Optional[List[float]] = None
        self._y_: Optional[List[float]] = None
        self._use_sklearn: bool = False
        self._sk_model = None

    def fit(self, x: Sequence[float], y: Sequence[float]) -> "IsotonicCalibrator":
        xs = [float(v) for v in x]
        ys = [float(v) for v in y]
        if not xs:
            self._x_ = [0.0, 1.0]
            self._y_ = [0.0, 1.0]
            self._use_sklearn = False
            self._sk_model = None
            return self
        ys = [_clip01(v) for v in ys]
        try:
            from sklearn.isotonic import IsotonicRegression  # type: ignore

            model = IsotonicRegression(y_min=0.0, y_max=1.0, increasing=True, out_of_bounds="clip")
            model.fit(xs, ys)
            ux = sorted(set(xs))
            uy = [float(model.predict([v])[0]) for v in ux]
            self._x_, self._y_ = ux, uy
            self._use_sklearn = True
            self._sk_model = model
            return self
        except Exception:
            pass

        # PAV fallback (piecewise-constant)
        pairs = sorted(zip(xs, ys), key=lambda t: t[0])
        grouped_x: List[float] = []
        grouped_y: List[float] = []
        grouped_w: List[int] = []
        i = 0
        while i < len(pairs):
            x_i = pairs[i][0]
            ys_i: List[float] = [pairs[i][1]]
            j = i + 1
            while j < len(pairs) and pairs[j][0] == x_i:
                ys_i.append(pairs[j][1])
                j += 1
            grouped_x.append(x_i)
            grouped_y.append(_safe_mean(ys_i))
            grouped_w.append(len(ys_i))
            i = j

        sum_y: List[float] = []
        weight: List[float] = []
        mean: List[float] = []
        for k in range(len(grouped_x)):
            sum_y.append(grouped_y[k] * grouped_w[k])
            weight.append(float(grouped_w[k]))
            mean.append(sum_y[-1] / weight[-1])
            while len(mean) >= 2 and mean[-2] > mean[-1]:
                sum_y[-2] += sum_y[-1]
                weight[-2] += weight[-1]
                mean[-2] = sum_y[-2] / weight[-2]
                sum_y.pop(); weight.pop(); mean.pop()

        x_grid: List[float] = []
        y_grid: List[float] = []
        idx = 0
        for m in mean:
            x_grid.append(grouped_x[idx])
            y_grid.append(_clip01(m))
            idx += 1
        if x_grid and (x_grid[-1] < grouped_x[-1]):
            x_grid.append(grouped_x[-1])
            y_grid.append(y_grid[-1])
        self._x_, self._y_ = x_grid, y_grid
        self._use_sklearn = False
        self._sk_model = None
        return self

    def predict_one(self, x: float) -> float:
        if self._x_ is None or self._y_ is None:
            return _clip01(x)
        if x <= self._x_[0]:
            return _clip01(self._y_[0])
        if x >= self._x_[-1]:
            return _clip01(self._y_[-1])
        lo, hi = 0, len(self._x_) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self._x_[mid] <= x:
                lo = mid + 1
            else:
                hi = mid - 1
        idx = max(0, hi)
        return _clip01(self._y_[idx])

    def __call__(self, x: float) -> float:
        return self.predict_one(x)


@dataclass
class HSJInputs:
    judge_raw_norm: Sequence[Optional[float]]
    mi_raw: Sequence[Optional[float]]
    fJ: Callable[[float], float]
    fI: Callable[[float], float]
    jti: float
    lambda_gt: float = 1.0
    gamma: float = 1.5
    jti_red: float = 0.70  # guardrail: if jti < jti_red, drop supervised leg


def compute_alpha(lambda_gt: float, jti: float, gamma: float = 1.5, jti_red: float = 0.0) -> float:
    if _clip01(jti) < jti_red:
        return 0.0
    return _clip01(max(0.0, lambda_gt) * ( _clip01(jti) ** float(gamma)))


def compute_hsj_scores(
    judge_raw_norm: Sequence[Optional[float]],
    mi_raw: Sequence[Optional[float]],
    fJ: Callable[[float], float],
    fI: Callable[[float], float],
    jti: float,
    lambda_gt: float = 1.0,
    gamma: float = 1.5,
    jti_red: float = 0.0,
) -> List[float]:
    """
    Compute Hybrid Spec‑Judging scores for candidates:
      Q = (1-α)*S_unsup + α*(JTI*S_sup_raw)
      where α = clip(lambda_gt * JTI^gamma), optionally zeroed if JTI < jti_red.
    """
    n = max(len(judge_raw_norm), len(mi_raw))
    jr = list(judge_raw_norm)
    mr = list(mi_raw)
    if len(jr) != n:
        jr += [None] * (n - len(jr))
    if len(mr) != n:
        mr += [None] * (n - len(mr))

    alpha = compute_alpha(lambda_gt=lambda_gt, jti=jti, gamma=gamma, jti_red=jti_red)
    out: List[float] = []
    for jv, mv in zip(jr, mr):
        s_unsup = 0.0 if mv is None else _clip01(fI(float(mv)))
        s_sup_raw = 0.0 if jv is None else _clip01(fJ(_clip01(float(jv))))
        s_sup = _clip01(jti) * s_sup_raw
        q = (1.0 - alpha) * s_unsup + alpha * s_sup
        out.append(_clip01(q))
    return out


def fit_isotonic_calibrator(
    x: Sequence[float],
    y: Sequence[float],
    y_is_rungs: bool = False,
    rung_max: Optional[int] = None,
) -> IsotonicCalibrator:
    ys = list(y)
    if y_is_rungs:
        if rung_max is None:
            rung_max = max(int(v) for v in ys) if ys else 1
        scale = float(max(1, rung_max))
        ys = [float(v) / scale for v in ys]
    return IsotonicCalibrator().fit(x, ys)


if __name__ == "__main__":
    # Quick self-test
    p1 = compute_p1_identity([1.0, 0.99, 1.0])
    p2 = compute_p2_or_p3_ordering_auc([0, 1, 2], [0.9, 0.6, 0.2])
    p3 = compute_p2_or_p3_ordering_auc([0, 1, 2], [0.88, 0.7, 0.4])
    p4 = compute_p4_stability({"a": [0.9, 0.91, 0.89]}, tau=0.05)
    jti = compute_jti(p1, p2, p3, p4)
    fJ = fit_isotonic_calibrator([0.2, 0.5, 0.8], [0.0, 0.5, 1.0])
    fI = fit_isotonic_calibrator([0.1, 0.6, 0.95], [0.0, 0.5, 1.0])
    final = compute_hsj_scores([0.35, 0.55, 0.9], [0.25, 0.5, 0.99], fJ, fI, jti, lambda_gt=0.7, gamma=1.5, jti_red=0.70)
    print({"p1": p1, "p2": p2, "p3": p3, "p4": p4, "jti": jti, "final": final})

