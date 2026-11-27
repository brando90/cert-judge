#!/usr/bin/env python3
"""Proper-scoring behavioral proxies and decision-theoretic / proper-scoring meta-similarity metrics.

Reuses canonical item-level proper scoring functions from Experiment 68's `metrics.py`
and adds:
1. Label-free proper-scoring behavioral proxies computed directly from Lean-validated
   probe harvests (`E39`, `E42`, `E60`).
2. Decision-theoretic and proper-scoring meta-similarity metrics between a proxy P(j)
   and a target alignment/risk metric T(j): label-free tie-averaged Top-1 regret,
   expected subpool regret, leave-one-family-out (LOFO) regret, utility-weighted
   pairwise decision accuracy (UWA), train-calibrated Beat-CONST Meta-Brier/Meta-CE/AUROC,
   and continuous target-risk Meta-RMSE/Meta-ICC(A,1).
"""
from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy import optimize, stats

CJ_ROOT = Path(__file__).resolve().parents[3]
EXP68_SCRIPTS = CJ_ROOT / "experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts"
if str(EXP68_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EXP68_SCRIPTS))

import metrics as M  # noqa: E402

VALID_CELL_STATUSES = frozenset({"measured", "deterministic"})


def _cell_probe_id(cell: dict) -> str:
    """Resolve canonical probe_id from a harvest cell dict."""
    pid = cell.get("probe_id")
    if pid:
        return str(pid)
    cname = str(cell.get("cell", ""))
    if "__r" in cname:
        return cname.rsplit("__r", 1)[0]
    return f"{cell.get('kind')}__{cell.get('task')}__L{cell.get('level')}"


def _binary_brier(q_pos: float, y: int) -> float:
    return float((float(q_pos) - float(y)) ** 2)


def _binary_ce(q_pos: float, y: int, floor: float = 1e-12) -> float:
    p = max(floor, min(1.0 - floor, float(q_pos)))
    return float(-math.log(p) if y == 1 else -math.log(1.0 - p))


def _fullcov_prob(scores_01: Sequence[float], alpha: float = 0.5, thresh: float = 0.999) -> float:
    """Laplace-smoothed probability that the judge assigns full coverage (>= thresh)."""
    m = len(scores_01)
    hits = sum(1 for s in scores_01 if float(s) >= thresh)
    return float((hits + alpha) / (float(m) + 2.0 * alpha))


def compute_e39_probe_proxies(
    cells: Sequence[dict],
    manifest_rows: Sequence[dict],
    coverage_min: float = 0.80,
    alpha: float = 0.5,
) -> dict[str, float | int | None]:
    """Compute label-free proper-scoring behavioral proxies from E39-style probes (`ident`, `blank`, `ms_gold`)."""
    valid_ident_tasks = {r["task"] for r in manifest_rows if r["kind"] == "ident" and r.get("valid")}
    valid_blank_tasks = {r["task"] for r in manifest_rows if r["kind"] == "blank" and r.get("valid")}
    ms_levels_by_task: dict[str, list[int]] = defaultdict(list)
    for r in manifest_rows:
        if r["kind"] == "ms_gold" and r.get("valid"):
            ms_levels_by_task[str(r["task"])].append(int(r["level"]))
    max_ms_level_by_task = {t: max(lvls) for t, lvls in ms_levels_by_task.items() if lvls}

    scores_by_key: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    for c in cells:
        if c.get("status") not in VALID_CELL_STATUSES or c.get("score") is None:
            continue
        kind = str(c.get("kind"))
        if kind not in ("ident", "blank", "ms_gold"):
            continue
        scores_by_key[(kind, str(c.get("task")), int(c.get("level", 0)))].append(float(c["score"]))

    # 1. Binary full-coverage Brier / CE / 6-class RPS on ident (y=1/5) vs blank + ms_gold max-leaf (y=0/0)
    ident_briers, ident_ces, ident_rps = [], [], []
    for t in sorted(valid_ident_tasks):
        sc = scores_by_key.get(("ident", t, 0), [])
        if sc:
            q1 = _fullcov_prob(sc, alpha=alpha)
            ident_briers.append(_binary_brier(q1, 1))
            ident_ces.append(_binary_ce(q1, 1))
            ident_rps.append(M.rps_item(M.binned_repeats_to_probs(sc, alpha=alpha), [5]))

    blank_briers, blank_ces, blank_rps = [], [], []
    for t in sorted(valid_blank_tasks):
        sc = scores_by_key.get(("blank", t, 0), [])
        if sc:
            q1 = _fullcov_prob(sc, alpha=alpha)
            blank_briers.append(_binary_brier(q1, 0))
            blank_ces.append(_binary_ce(q1, 0))
            blank_rps.append(M.rps_item(M.binned_repeats_to_probs(sc, alpha=alpha), [0]))

    leaf_briers, leaf_ces, leaf_rps = [], [], []
    for t, lmax in sorted(max_ms_level_by_task.items()):
        sc = scores_by_key.get(("ms_gold", t, lmax), [])
        if sc:
            q1 = _fullcov_prob(sc, alpha=alpha)
            leaf_briers.append(_binary_brier(q1, 0))
            leaf_ces.append(_binary_ce(q1, 0))
            leaf_rps.append(M.rps_item(M.binned_repeats_to_probs(sc, alpha=alpha), [0]))

    # 2. Curve RPS & step-margin over all valid ident + ms_gold ladder points
    curve_rps_vals = []
    step_margins = []
    n_declared_curve = len(valid_ident_tasks) + sum(len(v) for v in ms_levels_by_task.values())
    n_measured_curve = 0
    for t, lvls in sorted(ms_levels_by_task.items()):
        lmax = max(lvls)
        lvl_means: dict[int, float] = {}
        if t in valid_ident_tasks:
            sc0 = scores_by_key.get(("ident", t, 0), [])
            if sc0:
                n_measured_curve += 1
                lvl_means[0] = float(np.mean(sc0))
                curve_rps_vals.append(M.rps_item(M.binned_repeats_to_probs(sc0, alpha=alpha), [5]))
        for lvl in sorted(lvls):
            scl = scores_by_key.get(("ms_gold", t, lvl), [])
            if scl:
                n_measured_curve += 1
                lvl_means[lvl] = float(np.mean(scl))
                y_cat = int(round(5.0 * max(0.0, 1.0 - float(lvl) / float(lmax))))
                curve_rps_vals.append(M.rps_item(M.binned_repeats_to_probs(scl, alpha=alpha), [y_cat]))
        sorted_present = sorted(lvl_means)
        for a_l, b_l in zip(sorted_present[:-1], sorted_present[1:]):
            step_margins.append(lvl_means[a_l] - lvl_means[b_l])

    cov_ident = len(ident_briers) / float(max(1, len(valid_ident_tasks)))
    cov_blank = len(blank_briers) / float(max(1, len(valid_blank_tasks)))
    cov_leaf = len(leaf_briers) / float(max(1, len(max_ms_level_by_task)))
    cov_curve = n_measured_curve / float(max(1, n_declared_curve))

    out: dict[str, float | int | None] = {
        "e39_cov_ident": round(cov_ident, 4),
        "e39_cov_blank": round(cov_blank, 4),
        "e39_cov_leaf": round(cov_leaf, 4),
        "e39_cov_curve": round(cov_curve, 4),
        "P_e39_fullcov_brier": None,
        "P_e39_fullcov_ce": None,
        "P_e39_probe_rps": None,
        "P_e39_curve_rps": None,
        "P_e39_ms_margin": None,
    }
    if min(cov_ident, cov_blank, cov_leaf) + 1e-9 >= coverage_min:
        b_neg = 0.5 * (float(np.mean(blank_briers)) + float(np.mean(leaf_briers)))
        c_neg = 0.5 * (float(np.mean(blank_ces)) + float(np.mean(leaf_ces)))
        r_neg = 0.5 * (float(np.mean(blank_rps)) + float(np.mean(leaf_rps)))
        out["P_e39_fullcov_brier"] = 1.0 - 0.5 * (float(np.mean(ident_briers)) + b_neg)
        out["P_e39_fullcov_ce"] = -0.5 * (float(np.mean(ident_ces)) + c_neg)
        out["P_e39_probe_rps"] = 1.0 - 0.5 * (float(np.mean(ident_rps)) + r_neg)
    if cov_curve + 1e-9 >= coverage_min and curve_rps_vals and step_margins:
        out["P_e39_curve_rps"] = 1.0 - float(np.mean(curve_rps_vals))
        out["P_e39_ms_margin"] = float(np.mean(step_margins))
    return out


def compute_e42_probe_proxies(
    cells: Sequence[dict],
    manifest_rows: Sequence[dict],
    coverage_min: float = 0.80,
    alpha: float = 0.5,
    strict_probe_ids: set[str] | None = None,
) -> dict[str, float | int | None]:
    """Compute label-free proper-scoring behavioral proxies on Lean-verified E42 semantic probes."""
    fam_probes: dict[str, list[str]] = defaultdict(list)
    for r in manifest_rows:
        if r.get("valid"):
            fam_probes[str(r["family"])].append(str(r["probe_id"]))

    scores_by_pid: dict[str, list[float]] = defaultdict(list)
    for c in cells:
        if c.get("status") not in VALID_CELL_STATUSES or c.get("score") is None:
            continue
        scores_by_pid[_cell_probe_id(c)].append(float(c["score"]))

    families = ("identity", "formatting", "vacuity", "weakening", "overconstraint")
    pos_fams = ("identity", "formatting")
    neg_fams = ("vacuity", "weakening", "overconstraint")

    cov_by_fam: dict[str, float] = {}
    strict_cov_by_fam: dict[str, float] = {}
    fullcov_brier_by_fam: dict[str, float] = {}
    fullcov_ce_by_fam: dict[str, float] = {}
    score_brier_by_fam: dict[str, float] = {}
    rps_by_fam: dict[str, float] = {}
    strict_brier_by_fam: dict[str, float] = {}

    for fam in families:
        pids = fam_probes.get(fam, [])
        strict_pids = [
            pid for pid in pids
            if strict_probe_ids is not None and (fam not in ("weakening", "overconstraint") or pid in strict_probe_ids)
        ]
        y_bin = 1 if fam in pos_fams else 0
        y_cat = 5 if fam in pos_fams else 0
        fb, fc, sb, rp, sb_strict = [], [], [], [], []
        for pid in pids:
            sc = scores_by_pid.get(pid, [])
            if not sc:
                continue
            q1 = _fullcov_prob(sc, alpha=alpha)
            s_mean = float(np.mean(sc))
            b_val = _binary_brier(q1, y_bin)
            fb.append(b_val)
            fc.append(_binary_ce(q1, y_bin))
            sb.append(_binary_brier(s_mean, y_bin))
            rp.append(M.rps_item(M.binned_repeats_to_probs(sc, alpha=alpha), [y_cat]))
            if strict_probe_ids is not None and (fam not in ("weakening", "overconstraint") or pid in strict_probe_ids):
                sb_strict.append(b_val)
        cov = len(fb) / float(max(1, len(pids)))
        cov_by_fam[fam] = cov
        if strict_probe_ids is not None:
            strict_cov_by_fam[fam] = len(sb_strict) / float(max(1, len(strict_pids)))
        if fb:
            fullcov_brier_by_fam[fam] = float(np.mean(fb))
            fullcov_ce_by_fam[fam] = float(np.mean(fc))
            score_brier_by_fam[fam] = float(np.mean(sb))
            rps_by_fam[fam] = float(np.mean(rp))
        if sb_strict:
            strict_brier_by_fam[fam] = float(np.mean(sb_strict))

    out: dict[str, float | int | None] = {
        "e42_min_fam_cov": round(min(cov_by_fam.values()), 4),
        "P_e42_fullcov_brier": None,
        "P_e42_strict_brier": None,
        "P_e42_fullcov_ce": None,
        "P_e42_score_brier": None,
        "P_e42_probe_rps": None,
        "e42_brier_ident": fullcov_brier_by_fam.get("identity"),
        "e42_brier_fmt": fullcov_brier_by_fam.get("formatting"),
        "e42_brier_vac": fullcov_brier_by_fam.get("vacuity"),
        "e42_brier_weak": fullcov_brier_by_fam.get("weakening"),
        "e42_brier_overc": fullcov_brier_by_fam.get("overconstraint"),
    }
    if min(cov_by_fam.values()) + 1e-9 >= coverage_min:
        fb_pos = float(np.mean([fullcov_brier_by_fam[f] for f in pos_fams]))
        fb_neg = float(np.mean([fullcov_brier_by_fam[f] for f in neg_fams]))
        fc_pos = float(np.mean([fullcov_ce_by_fam[f] for f in pos_fams]))
        fc_neg = float(np.mean([fullcov_ce_by_fam[f] for f in neg_fams]))
        sb_pos = float(np.mean([score_brier_by_fam[f] for f in pos_fams]))
        sb_neg = float(np.mean([score_brier_by_fam[f] for f in neg_fams]))
        rp_pos = float(np.mean([rps_by_fam[f] for f in pos_fams]))
        rp_neg = float(np.mean([rps_by_fam[f] for f in neg_fams]))
        out["P_e42_fullcov_brier"] = 1.0 - 0.5 * (fb_pos + fb_neg)
        out["P_e42_fullcov_ce"] = -0.5 * (fc_pos + fc_neg)
        out["P_e42_score_brier"] = 1.0 - 0.5 * (sb_pos + sb_neg)
        out["P_e42_probe_rps"] = 1.0 - 0.5 * (rp_pos + rp_neg)
        if strict_probe_ids is not None and min(strict_cov_by_fam.values()) + 1e-9 >= coverage_min and all(f in strict_brier_by_fam for f in families):
            st_pos = float(np.mean([strict_brier_by_fam[f] for f in pos_fams]))
            st_neg = float(np.mean([strict_brier_by_fam[f] for f in neg_fams]))
            out["P_e42_strict_brier"] = 1.0 - 0.5 * (st_pos + st_neg)
    return out


def top1_regret_label_free(
    rows: Sequence[dict],
    proxy_key: str,
    target_key: str,
    lower_is_better: bool = True,
    tie_tol: float = 1e-12,
) -> dict[str, object]:
    """Select max-proxy units with strictly label-free tie-averaging and compute regret vs oracle."""
    elig = [r for r in rows if r["proxies"].get(proxy_key) is not None and r["targets"].get(target_key) is not None]
    if not elig:
        return {"n_units": 0}
    p_vals = np.array([float(r["proxies"][proxy_key]) for r in elig], dtype=float)
    t_vals = np.array([float(r["targets"][target_key]) for r in elig], dtype=float)
    max_p = float(np.max(p_vals))
    tied_mask = np.abs(p_vals - max_p) <= tie_tol
    tied_rows = [elig[i] for i in range(len(elig)) if tied_mask[i]]
    sel_target = float(np.mean(t_vals[tied_mask]))
    if lower_is_better:
        ora_idx = int(np.argmin(t_vals))
        ora_target = float(t_vals[ora_idx])
        regret = sel_target - ora_target
    else:
        ora_idx = int(np.argmax(t_vals))
        ora_target = float(t_vals[ora_idx])
        regret = ora_target - sel_target
    return {
        "n_units": len(elig),
        "proxy": proxy_key,
        "target": target_key,
        "n_tied": len(tied_rows),
        "selected_configs": [r["config"] for r in tied_rows],
        "selected_proxy_val": max_p,
        "selected_target": sel_target,
        "oracle_config": elig[ora_idx]["config"],
        "oracle_target": ora_target,
        "regret": regret,
        "pool_mean_target": float(np.mean(t_vals)),
    }


def expected_subpool_regret(
    rows: Sequence[dict],
    proxy_key: str,
    target_key: str,
    pool_size: int,
    const_threshold: float | None = None,
    draws: int = 2000,
    seed: int = 69,
    lower_is_better: bool = True,
    tie_tol: float = 1e-12,
) -> dict[str, object]:
    """Expected Top-1 selection regret and Beat-CONST rate across random subpools of fixed size."""
    elig = [r for r in rows if r["proxies"].get(proxy_key) is not None and r["targets"].get(target_key) is not None]
    n = len(elig)
    if n < pool_size or pool_size < 2:
        return {"n_units": n, "pool_size": pool_size, "computed": False}
    p_vals = np.array([float(r["proxies"][proxy_key]) for r in elig], dtype=float)
    t_vals = np.array([float(r["targets"][target_key]) for r in elig], dtype=float)
    rng = np.random.default_rng(seed)
    regrets = np.empty(draws, dtype=float)
    sel_targets = np.empty(draws, dtype=float)
    beat_const = np.zeros(draws, dtype=float)
    for d in range(draws):
        idx = rng.choice(n, size=pool_size, replace=False)
        ps = p_vals[idx]
        ts = t_vals[idx]
        max_p = float(np.max(ps))
        sel_t = float(np.mean(ts[np.abs(ps - max_p) <= tie_tol]))
        sel_targets[d] = sel_t
        if lower_is_better:
            regrets[d] = sel_t - float(np.min(ts))
            if const_threshold is not None and sel_t < const_threshold:
                beat_const[d] = 1.0
        else:
            regrets[d] = float(np.max(ts)) - sel_t
            if const_threshold is not None and sel_t > const_threshold:
                beat_const[d] = 1.0
    return {
        "n_units": n,
        "pool_size": pool_size,
        "draws": draws,
        "computed": True,
        "mean_regret": float(np.mean(regrets)),
        "regret_p025": float(np.percentile(regrets, 2.5)),
        "regret_p975": float(np.percentile(regrets, 97.5)),
        "mean_selected_target": float(np.mean(sel_targets)),
        "beat_const_rate": float(np.mean(beat_const)) if const_threshold is not None else None,
        "_per_draw_regrets": regrets,
    }


def lofo_regret(
    rows: Sequence[dict],
    proxy_key: str,
    target_key: str,
    family_key: str = "family",
    lower_is_better: bool = True,
    tie_tol: float = 1e-12,
) -> dict[str, object]:
    """Leave-one-family-out and within-family selection regret (label-free tie-averaging)."""
    elig = [r for r in rows if r["proxies"].get(proxy_key) is not None and r["targets"].get(target_key) is not None]
    fams = sorted({str(r[family_key]) for r in elig})
    if len(fams) < 2:
        return {"n_families": len(fams), "computed": False}
    within_regs, lofo_regs = [], []
    for fam in fams:
        in_f = [r for r in elig if str(r[family_key]) == fam]
        out_f = [r for r in elig if str(r[family_key]) != fam]
        if len(in_f) >= 2:
            within_regs.append(float(top1_regret_label_free(in_f, proxy_key, target_key, lower_is_better, tie_tol)["regret"]))
        if len(out_f) >= 2:
            lofo_regs.append(float(top1_regret_label_free(out_f, proxy_key, target_key, lower_is_better, tie_tol)["regret"]))
    return {
        "n_families": len(fams),
        "computed": True,
        "within_family_mean_regret": float(np.mean(within_regs)) if within_regs else None,
        "n_within_families": len(within_regs),
        "lofo_mean_regret": float(np.mean(lofo_regs)) if lofo_regs else None,
    }


def utility_weighted_pairwise_accuracy(
    proxies: Sequence[float],
    targets: Sequence[float],
    lower_is_better: bool = True,
    tie_tol: float = 1e-12,
) -> float:
    """Fraction of total pairwise |T_i - T_j| target utility captured by ordering pairs by proxy."""
    p = np.asarray(proxies, dtype=float)
    t = np.asarray(targets, dtype=float)
    n = len(p)
    if n < 2:
        return float("nan")
    iu, ju = np.triu_indices(n, k=1)
    dt = t[iu] - t[ju]
    w = np.abs(dt)
    mask = w > 1e-15
    if not np.any(mask):
        return float("nan")
    w = w[mask]
    dt = dt[mask]
    dp = p[iu][mask] - p[ju][mask]
    is_tie = np.abs(dp) <= tie_tol
    want_i_better = (dt < 0.0) if lower_is_better else (dt > 0.0)
    picked_i = dp > 0.0
    credit = np.where(is_tie, 0.5 * w, np.where(want_i_better == picked_i, w, 0.0))
    return float(np.sum(credit) / np.sum(w))


def _roc_auc(y_true: Sequence[int], y_score: Sequence[float]) -> float:
    yt = np.asarray(y_true, dtype=int)
    ys = np.asarray(y_score, dtype=float)
    pos = ys[yt == 1]
    neg = ys[yt == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = 0.0
    for p_v in pos:
        wins += float(np.sum(p_v > neg) + 0.5 * np.sum(p_v == neg))
    return wins / float(len(pos) * len(neg))


def meta_binary_proper_eval(
    train_x: Sequence[float],
    train_y: Sequence[int],
    test_x: Sequence[float],
    test_y: Sequence[int],
    l2: float = 1e-2,
) -> dict[str, float | int]:
    """Fit 1D logistic calibrator on train judge families and score held-out test families via Brier/CE/AUROC."""
    tx = np.asarray(train_x, dtype=float)
    ty = np.asarray(train_y, dtype=float)
    ex = np.asarray(test_x, dtype=float)
    ey = np.asarray(test_y, dtype=float)
    n_tr, n_te = len(tx), len(ex)
    if n_tr < 3 or n_te < 2:
        return {"n_train": n_tr, "n_test": n_te}

    # Standardize using train statistics only
    mu = float(np.mean(tx))
    sd = float(np.std(tx))
    sd = sd if sd > 1e-9 else 1.0
    tx_z = (tx - mu) / sd
    ex_z = (ex - mu) / sd

    # Laplace-smoothed train base rate forecast
    base_rate = float((np.sum(ty) + 0.5) / (float(n_tr) + 1.0))
    base_rate = max(1e-4, min(1.0 - 1e-4, base_rate))

    if np.ptp(ty) == 0.0 or np.ptp(tx_z) < 1e-12:
        q_te = np.full(n_te, base_rate, dtype=float)
    else:
        def obj(w: np.ndarray) -> float:
            z = np.clip(w[0] + w[1] * tx_z, -30.0, 30.0)
            p = 1.0 / (1.0 + np.exp(-z))
            p = np.clip(p, 1e-12, 1.0 - 1e-12)
            nll = -float(np.mean(ty * np.log(p) + (1.0 - ty) * np.log(1.0 - p)))
            return nll + 0.5 * l2 * float(w[1] ** 2)

        opt = optimize.minimize(obj, np.array([math.log(base_rate / (1.0 - base_rate)), 0.0]), method="L-BFGS-B")
        z_te = np.clip(opt.x[0] + opt.x[1] * ex_z, -30.0, 30.0)
        q_te = np.clip(1.0 / (1.0 + np.exp(-z_te)), 1e-6, 1.0 - 1e-6)

    q_base = np.full(n_te, base_rate, dtype=float)
    brier = float(np.mean((q_te - ey) ** 2))
    base_brier = float(np.mean((q_base - ey) ** 2))
    ce = float(-np.mean(ey * np.log(q_te) + (1.0 - ey) * np.log(1.0 - q_te)))
    base_ce = float(-np.mean(ey * np.log(q_base) + (1.0 - ey) * np.log(1.0 - q_base)))
    return {
        "n_train": n_tr,
        "n_test": n_te,
        "test_pos_count": int(np.sum(ey)),
        "train_base_rate": base_rate,
        "meta_brier": brier,
        "base_rate_brier": base_brier,
        "meta_brier_skill": (1.0 - brier / base_brier) if base_brier > 0.0 else float("nan"),
        "meta_ce": ce,
        "base_rate_ce": base_ce,
        "auroc": _roc_auc(ey.astype(int), ex),
        "raw_proxy_auroc": _roc_auc(ey.astype(int), ex),
        "calibrated_auroc": _roc_auc(ey.astype(int), q_te),
    }


def meta_continuous_risk_eval(
    train_x: Sequence[float],
    train_y: Sequence[float],
    test_x: Sequence[float],
    test_y: Sequence[float],
    l2: float = 1e-2,
    clip_bounds: tuple[float, float] = (0.0, 1.0),
) -> dict[str, float | int]:
    """Fit 1D ridge linear calibrator P -> target_risk on train judge families, evaluate MAE/RMSE/R2/ICC(A,1) on test."""
    tx = np.asarray(train_x, dtype=float)
    ty = np.asarray(train_y, dtype=float)
    ex = np.asarray(test_x, dtype=float)
    ey = np.asarray(test_y, dtype=float)
    if len(tx) < 3 or len(ex) < 3:
        return {"n_train": len(tx), "n_test": len(ex)}
    mu_x = float(np.mean(tx))
    sd_x = float(np.std(tx))
    sd_x = sd_x if sd_x > 1e-9 else 1.0
    tx_z = (tx - mu_x) / sd_x
    ex_z = (ex - mu_x) / sd_x

    mu_y = float(np.mean(ty))
    denom = float(np.sum(tx_z ** 2)) + l2 * float(len(tx))
    slope = float(np.dot(tx_z, ty - mu_y) / denom) if denom > 0.0 else 0.0
    y_hat = np.clip(mu_y + slope * ex_z, clip_bounds[0], clip_bounds[1])
    const_hat = np.full(len(ey), mu_y, dtype=float)

    rmse = float(np.sqrt(np.mean((y_hat - ey) ** 2)))
    const_rmse = float(np.sqrt(np.mean((const_hat - ey) ** 2)))
    mae = float(np.mean(np.abs(y_hat - ey)))
    icc_a, icc_c = M.icc_two_way_both(y_hat, ey)
    return {
        "n_train": len(tx),
        "n_test": len(ex),
        "meta_mae": mae,
        "meta_rmse": rmse,
        "const_rmse": const_rmse,
        "meta_r2": (1.0 - (rmse ** 2) / (const_rmse ** 2)) if const_rmse > 0.0 else float("nan"),
        "meta_icc_a1": icc_a,
        "meta_icc_c1": icc_c,
        "meta_bias": float(np.mean(y_hat - ey)),
    }


def evaluate_proxy_against_target(
    rows: Sequence[dict],
    proxy_key: str,
    target_key: str,
    const_threshold: float | None = None,
    lower_is_better: bool = True,
    train_val_splits: tuple[str, ...] = ("train", "val"),
    test_split: str = "test",
    draws: int = 2000,
    seed: int = 69,
) -> dict[str, object]:
    """Full decision-theoretic, proper-scoring, and rank evaluation of one proxy against one target."""
    elig = [r for r in rows if r["proxies"].get(proxy_key) is not None and r["targets"].get(target_key) is not None]
    if len(elig) < 5:
        return {"proxy": proxy_key, "target": target_key, "n_units": len(elig), "computable": False}

    px = np.array([float(r["proxies"][proxy_key]) for r in elig], dtype=float)
    ty = np.array([float(r["targets"][target_key]) for r in elig], dtype=float)
    fams = [str(r["family"]) for r in elig]
    y_oriented = (-ty) if lower_is_better else ty

    top1 = top1_regret_label_free(elig, proxy_key, target_key, lower_is_better=lower_is_better)
    sub5 = expected_subpool_regret(
        elig, proxy_key, target_key, pool_size=min(5, len(elig)), const_threshold=const_threshold,
        draws=draws, seed=seed, lower_is_better=lower_is_better,
    )
    sub10 = expected_subpool_regret(
        elig, proxy_key, target_key, pool_size=min(10, len(elig)), const_threshold=const_threshold,
        draws=draws, seed=seed + 1, lower_is_better=lower_is_better,
    )
    lofo = lofo_regret(elig, proxy_key, target_key, lower_is_better=lower_is_better)
    uwa = utility_weighted_pairwise_accuracy(px, ty, lower_is_better=lower_is_better)

    # Bootstrap CI for UWA over configs and families
    rng = np.random.default_rng(seed)
    n = len(elig)
    uwa_boot = []
    for _ in range(draws):
        ii = rng.integers(0, n, size=n)
        v = utility_weighted_pairwise_accuracy(px[ii], ty[ii], lower_is_better=lower_is_better)
        if math.isfinite(v):
            uwa_boot.append(v)
    uwa_ci = [float(np.percentile(uwa_boot, 2.5)), float(np.percentile(uwa_boot, 97.5))] if uwa_boot else None

    rank_meta = M.meta_association(px, y_oriented, families=fams, draws=max(draws, 5000), seed=seed, boot_draws=draws)

    # Strip raw per-draw arrays from JSON output
    sub5_clean = {k: v for k, v in sub5.items() if k != "_per_draw_regrets"}
    sub10_clean = {k: v for k, v in sub10.items() if k != "_per_draw_regrets"}

    out: dict[str, object] = {
        "proxy": proxy_key,
        "target": target_key,
        "n_units": len(elig),
        "computable": True,
        "top1": top1,
        "subpool_5": sub5_clean,
        "subpool_10": sub10_clean,
        "lofo": lofo,
        "uwa": uwa,
        "uwa_ci": uwa_ci,
        "rank_meta": rank_meta,
    }

    # Train/val -> test held-out proper-scoring meta-prediction if splits are present (LLMs only in train)
    tr_rows = [r for r in elig if r.get("split") in train_val_splits and r.get("kind", "llm") == "llm"]
    te_rows = [r for r in elig if r.get("split") == test_split]
    if const_threshold is not None and len(tr_rows) >= 5 and len(te_rows) >= 3:
        tr_px = [float(r["proxies"][proxy_key]) for r in tr_rows]
        te_px = [float(r["proxies"][proxy_key]) for r in te_rows]
        tr_ty = [float(r["targets"][target_key]) for r in tr_rows]
        te_ty = [float(r["targets"][target_key]) for r in te_rows]
        tr_bin = [1 if (v < const_threshold if lower_is_better else v > const_threshold) else 0 for v in tr_ty]
        te_bin = [1 if (v < const_threshold if lower_is_better else v > const_threshold) else 0 for v in te_ty]
        out["beat_const_meta_pred"] = meta_binary_proper_eval(tr_px, tr_bin, te_px, te_bin)
        out["risk_meta_pred"] = meta_continuous_risk_eval(tr_px, tr_ty, te_px, te_ty)

    return out
