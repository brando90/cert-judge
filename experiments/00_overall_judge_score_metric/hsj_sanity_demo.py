from __future__ import annotations

import os
import sys


def ensure_path():
    # Add cert-judge/py_src to PYTHONPATH for local runs
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    py_src = os.path.join(repo_root, "py_src")
    if py_src not in sys.path:
        sys.path.insert(0, py_src)


def main() -> None:
    ensure_path()
    from cert_judge.hsj_scoring import (
        compute_p1_identity,
        compute_p2_or_p3_ordering_auc,
        compute_p4_stability,
        compute_jti,
        fit_isotonic_calibrator,
        compute_hsj_scores,
    )

    # 1) Cert metrics
    p1 = compute_p1_identity([1.0, 0.99, 1.0, 0.98])
    p2 = compute_p2_or_p3_ordering_auc([0, 1, 2, 3], [0.92, 0.7, 0.5, 0.2])
    p3 = compute_p2_or_p3_ordering_auc([0, 1, 2, 3], [0.90, 0.75, 0.6, 0.4])
    p4 = compute_p4_stability({"ex": [0.9, 0.91, 0.89]}, tau=0.05)
    jti = compute_jti(p1, p2, p3, p4)
    print({"p1": round(p1,3), "p2": round(p2,3), "p3": round(p3,3), "p4": round(p4,3), "jti": round(jti,3)})

    # 2) Calibrate
    fJ = fit_isotonic_calibrator([0.2, 0.5, 0.8], [0.0, 0.5, 1.0])
    fI = fit_isotonic_calibrator([0.1, 0.6, 0.95], [0.0, 0.6, 1.0])

    # 3) Scores
    final = compute_hsj_scores([0.35, 0.55, 0.9], [0.25, 0.5, 0.99], fJ, fI, jti, lambda_gt=0.7, gamma=1.5, jti_red=0.70)
    print({"final": [round(v, 4) for v in final]})


if __name__ == "__main__":
    main()

