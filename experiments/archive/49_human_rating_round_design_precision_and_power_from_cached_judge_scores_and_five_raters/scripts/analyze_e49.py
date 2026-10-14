#!/usr/bin/env python3
"""TLDR: Experiment 49 analysis (zero inference): how the judge-human criterion's precision, its ranking of judge
configurations and the power of the pre-registered held-out test depend on rated tasks, raters per item and held-out
judge configurations, by resampling experiment 39's cached scores (56 LLM judge configurations x 75 items x 3 repeats)
and VeriBench experiment 100's five current raters. Implements PROTOCOL.md: gate G0 (seed 39 reproduction through
experiment 39's analysis_lib, NumPy parity), Q1 tasks x raters grid, Q2 power curves, Q3 equal-budget allocation,
Q4 labelled model-based extrapolation. No model calls, no credentials, no network.

Usage (from the repository root):  PYTHONPATH=py_src python3 experiments/49_.../scripts/analyze_e49.py [--quick]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = next(q for q in EXP.parents if (q / "py_src" / "cert_judge").is_dir())   # repo root, valid under experiments/ or experiments/archive/
RESULTS = EXP / "results"
REPORT = EXP / "RESULTS_rating_round_design.md"
E39_NAME = "39_label_free_proxy_index_train_val_test_over_judge_families"
ITEMS_REL = "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/items.jsonl"
ITEMS_SHA256 = "ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c"

SEED = 49                                  # every new resampling; G0 reproduces with experiment 39's seed 39
GATE_RHO = 0.45                            # experiment 39 PROTOCOL.md (pre-registered gate)
GATE_P = 0.05
TARGET_RELIABILITY = 0.90                  # agent-suggested design targets (PROTOCOL.md of this experiment)
TARGET_GATE_AGREEMENT = 0.90
TARGET_POWER = 0.80
T_GRID = (5, 8, 10, 15, 20, 25)
R_GRID = (1, 2, 3, 5)
Q1_DRAWS = 1000
K_GRID = (8, 12, 16, 24, 32, 48)
Q2_DRAWS = 1000
Q2_PERMS = 1000
RHO_GRID = (0.30, 0.45, 0.56, 0.70)
Q2B_DRAWS = 2000
M_GRID = (2, 3, 4, 6, 9)
N_EXTRAP = (90, 120, 150)
BOOT_DRAWS = 10000
RATERS = ("p1", "p2", "p3", "p4", "p5")
REGISTERED_RATERS = (0, 1, 2)              # participants 1-3 (experiment 39's target_expert)
LEGACY = {"P1", "P4", "P8", "LEX"}
FULLER = {"D0", "H0", "H1", "H2", "R4"}
MIN_UNITS = 8                              # analysis_lib.MIN_UNITS: a correlation over fewer configurations is not computed
MIN_COVERAGE = 0.90                        # analysis_lib.MIN_CRITERION_COVERAGE
TOL = 1e-9


# ------------------------------------------------------------------ plumbing
def e39_root() -> Path:
    for p in (REPO / "experiments" / E39_NAME, REPO / "experiments" / "archive" / E39_NAME):
        if (p / "results" / "units_test.json").exists():
            return p
    raise FileNotFoundError(f"experiment 39 receipts not found under experiments/ or experiments/archive/ in {REPO}")


def load_analysis_lib():
    scripts = str(e39_root() / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import analysis_lib  # noqa: E402
    return analysis_lib


def veribench_items_path() -> Path:
    return Path(os.environ.get("CJ_VERIBENCH_REPO", "/Users/brandomiranda/veribench")) / ITEMS_REL


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_head() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True, timeout=30)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=False, allow_nan=False) + "\n")


def clean(o):
    """JSON-safe: NaN -> None, numpy scalars -> Python."""
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    return o


# ------------------------------------------------------------------ statistics (NumPy, tie-aware)
def spearman_rows(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Tie-aware Spearman between every row of X and the vector y (Pearson of average ranks); NaN when undefined."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    if X.ndim == 1:
        X = X[None, :]
    if X.shape[1] < 3:
        return np.full(X.shape[0], np.nan)
    rx = rankdata(X, axis=1)
    ry = rankdata(y)
    rx = rx - rx.mean(axis=1, keepdims=True)
    ry = ry - ry.mean()
    num = rx @ ry
    den = np.sqrt((rx ** 2).sum(axis=1) * (ry ** 2).sum())
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = num / den
    rho[den <= 0] = np.nan
    return rho


def spearman_pairs(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Tie-aware Spearman between row i of X and row i of Y; NaN when undefined."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if X.shape[1] < 3:
        return np.full(X.shape[0], np.nan)
    rx = rankdata(X, axis=1)
    ry = rankdata(Y, axis=1)
    rx = rx - rx.mean(axis=1, keepdims=True)
    ry = ry - ry.mean(axis=1, keepdims=True)
    num = (rx * ry).sum(axis=1)
    den = np.sqrt((rx ** 2).sum(axis=1) * (ry ** 2).sum(axis=1))
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = num / den
    rho[den <= 0] = np.nan
    return rho


def perm_p_rows(X: np.ndarray, Y: np.ndarray, rng: np.random.Generator, perms: int) -> tuple[np.ndarray, np.ndarray]:
    """Observed row-wise Spearman and the one-sided permutation p-value (k + 1)/(perms + 1) for a positive association,
    permuting each row of Y independently; a permuted statistic that is undefined is not counted (as in analysis_lib)."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    rx = rankdata(X, axis=1)
    rx = rx - rx.mean(axis=1, keepdims=True)
    nx = np.sqrt((rx ** 2).sum(axis=1))
    ry = rankdata(Y, axis=1)
    ry_c = ry - ry.mean(axis=1, keepdims=True)
    ny = np.sqrt((ry_c ** 2).sum(axis=1))
    with np.errstate(divide="ignore", invalid="ignore"):
        obs = (rx * ry_c).sum(axis=1) / (nx * ny)
    obs[(nx <= 0) | (ny <= 0)] = np.nan
    count = np.zeros(X.shape[0], dtype=int)
    for _ in range(perms):
        yp = rng.permuted(ry, axis=1)
        yp = yp - yp.mean(axis=1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            stat = (rx * yp).sum(axis=1) / (nx * ny)
        count += np.where(np.isfinite(stat) & np.isfinite(obs), stat >= obs - 1e-12, False)
    p = (count + 1) / (perms + 1)
    p = np.where(np.isfinite(obs), p, np.nan)
    return obs, p


def perm_p_given(x, y, permuted_ys) -> float:
    """Permutation p for explicit permuted copies of y (used by the parity test against analysis_lib)."""
    x = np.asarray(x, dtype=float)
    obs = float(spearman_rows(x, np.asarray(y, dtype=float))[0])
    Y = np.asarray(permuted_ys, dtype=float)
    stats = spearman_pairs(np.tile(x, (Y.shape[0], 1)), Y)
    k = int(np.sum(np.isfinite(stats) & (stats >= obs - 1e-12)))
    return (k + 1) / (Y.shape[0] + 1)


def pct(a, q) -> float:
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    return float(np.percentile(a, q)) if a.size else float("nan")


def fisher_z(r: np.ndarray) -> np.ndarray:
    r = np.clip(np.asarray(r, dtype=float), -0.999999, 0.999999)
    return np.arctanh(r)


# ------------------------------------------------------------------ data
class Data:
    """Frozen inputs: 75 items (25 tasks), ratings (75 x 5, NaN = missing), 56 LLM configurations' per-item medians."""

    def __init__(self, A):
        self.A = A
        self.e39 = e39_root()
        self.items_path = veribench_items_path()
        self.hashes: dict[str, str] = {}
        sha = sha_file(self.items_path)
        if sha != ITEMS_SHA256:
            raise SystemExit(f"refusing items.jsonl with SHA-256 {sha} (expected {ITEMS_SHA256})")
        self.hashes[str(self.items_path)] = sha
        self.items = [json.loads(l) for l in self.items_path.read_text().splitlines() if l.strip()]
        self.n_items = len(self.items)
        self.item_index = {it["item"]: i for i, it in enumerate(self.items)}
        self.tasks = sorted({it["task"] for it in self.items})
        self.task_items = {t: [i for i, it in enumerate(self.items) if it["task"] == t] for t in self.tasks}
        self.split = np.array([it["split"] for it in self.items])
        self.ratings = np.array([[np.nan if it.get(r) is None else float(it[r]) for r in RATERS] for it in self.items])
        self.target_expert = np.array([float(it["target_expert"]) for it in self.items])
        self.heldout_tasks = sorted({it["task"] for it in self.items if it["split"] in ("val", "test")})
        # harvest -> per-item medians through experiment 39's Scores class (frozen code path)
        configs, rows, units_meta = [], [], []
        for path in sorted((self.e39 / "results" / "harvest").glob("*.json")):
            h = json.loads(path.read_text())
            self.hashes[str(path.relative_to(REPO))] = sha_file(path)
            if h.get("kind") != "llm":
                continue
            sc = A.Scores(h)
            configs.append(sc.config)
            rows.append([np.nan if sc.median("crit", it["item"], 0) is None else sc.median("crit", it["item"], 0) for it in self.items])
        self.configs = configs
        self.S = np.array(rows, dtype=float)
        self.n_configs = len(configs)
        self.model_key = [c.split("|")[0] for c in configs]
        self.prompt_key = [c.split("|")[1] for c in configs]
        units = {}
        for name in ("units_train_val.json", "units_test.json"):
            p = self.e39 / "results" / name
            self.hashes[str(p.relative_to(REPO))] = sha_file(p)
            for u in json.loads(p.read_text())["units"]:
                units[u["config"]] = u
        for name in ("probe_manifest.json", "TEST_RECEIPT.json"):
            p = self.e39 / "results" / name
            self.hashes[str(p.relative_to(REPO))] = sha_file(p)
        self.units = units
        missing = [c for c in configs if c not in units]
        if missing:
            raise SystemExit(f"configurations without a unit row: {missing}")
        self.cms = np.array([np.nan if units[c]["indices"].get("C_ms_gold") is None else float(units[c]["indices"]["C_ms_gold"]) for c in configs])
        self.unit_split = np.array([units[c]["split"] for c in configs])
        self.registered_heldout = np.array([np.nan if (units[c]["criteria"]["heldout"] or {}).get("spearman") is None
                                            else float(units[c]["criteria"]["heldout"]["spearman"]) for c in configs])
        self.test_mask = self.unit_split == "test"
        self.test_computable = self.test_mask & np.isfinite(self.cms)
        self.receipt = json.loads((self.e39 / "results" / "TEST_RECEIPT.json").read_text())

    def items_of_tasks(self, tasks) -> np.ndarray:
        return np.array([i for t in tasks for i in self.task_items[t]], dtype=int)


def rating_target(ratings_sub: np.ndarray, rater_idx) -> np.ndarray:
    """Mean of the drawn raters' available 0-5 ratings / 5 per item; NaN when no drawn rater rated the item."""
    sel = ratings_sub[:, list(rater_idx)]
    cnt = np.isfinite(sel).sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        t = np.nansum(sel, axis=1) / cnt / 5.0
    t = np.where(cnt > 0, t, np.nan)
    return t


def criterion_vector(S_sub: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Per-configuration tie-aware Spearman between per-item medians and the target over the items with a target;
    NaN (NOT_COMPUTABLE) when fewer than 90% of those items have a score, fewer than 3 pairs, or a constant vector."""
    keep = np.isfinite(target)
    S_sub = S_sub[:, keep]
    target = target[keep]
    n = S_sub.shape[1]
    out = np.full(S_sub.shape[0], np.nan)
    if n == 0:
        return out
    valid = np.isfinite(S_sub)
    cov = valid.sum(axis=1) / n
    ok = cov + 1e-9 >= MIN_COVERAGE
    groups: dict[bytes, list[int]] = {}
    for i in np.where(ok)[0]:
        groups.setdefault(valid[i].tobytes(), []).append(int(i))
    for rows in groups.values():
        mask = valid[rows[0]]
        if mask.sum() < 3:
            continue
        out[rows] = spearman_rows(S_sub[np.ix_(rows, np.where(mask)[0])], target[mask])
    return out


def draw_design(d, rng: np.random.Generator, T: int, R: int):
    """T tasks without replacement (all outputs of a task move together) and R raters without replacement."""
    tasks = [d.tasks[i] for i in rng.choice(len(d.tasks), size=T, replace=False)] if T < len(d.tasks) else list(d.tasks)
    raters = sorted(rng.choice(len(RATERS), size=R, replace=False).tolist()) if R < len(RATERS) else list(range(len(RATERS)))
    return tasks, raters, d.items_of_tasks(tasks)


def draw_cell(d, rng: np.random.Generator, T: int, R: int):
    """One Q1 draw -> (criterion vector, ratings used, n_items with a target, raters)."""
    tasks, raters, items = draw_design(d, rng, T, R)
    target = rating_target(d.ratings[items], raters)
    used = int(np.isfinite(d.ratings[items][:, raters]).sum())
    c = criterion_vector(d.S[:, items], target)
    return c, used, int(np.isfinite(target).sum()), raters


# ------------------------------------------------------------------ G0
def gate_g0(d: Data) -> dict:
    A = d.A
    out = {"written_utc": stamp(), "seed": 39, "checks": {}}
    # 1. every configuration's held-out criterion from the harvest matches the unit files
    held = [it for it in d.items if it["split"] in ("val", "test")]
    worst = 0.0
    per = {}
    for ci, c in enumerate(d.configs):
        xs, ys = [], []
        for it in held:
            m = d.S[ci, d.item_index[it["item"]]]
            if np.isfinite(m):
                xs.append(float(m))
                ys.append(float(it["target_expert"]))
        cov = len(xs) / len(held)
        rho = A.spearman(xs, ys) if cov + 1e-9 >= MIN_COVERAGE else None
        reg = d.units[c]["criteria"]["heldout"].get("spearman")
        diff = abs((rho if rho is not None else np.nan) - (reg if reg is not None else np.nan)) if (rho is not None or reg is not None) else 0.0
        if rho is None and reg is None:
            diff = 0.0
        per[c] = {"recomputed": rho, "registered": reg, "n_items": len(xs)}
        worst = max(worst, 0.0 if not math.isfinite(diff) else diff)
        if (rho is None) != (reg is None):
            worst = float("inf")
    out["checks"]["criterion_reproduction"] = {"n_configurations": len(d.configs), "max_abs_diff": worst, "pass": worst <= TOL, "per_configuration": per}
    # 2. registered test association through analysis_lib with seed 39
    test_units = [d.units[c] for c in d.configs if d.units[c]["split"] == "test"]
    assoc = A.association(test_units, "C_ms_gold", draws=BOOT_DRAWS, seed=39)
    rec = d.receipt["reported"]["C_ms_gold"]["test"]
    diffs = {"spearman": abs(assoc["spearman"] - rec["spearman"]), "ci_lo": abs(assoc["ci"]["lo"] - rec["ci"]["lo"]),
             "ci_hi": abs(assoc["ci"]["hi"] - rec["ci"]["hi"]), "permutation_p": abs(assoc["permutation_p"] - rec["permutation_p"]),
             "kendall": abs(assoc["kendall"] - rec["kendall"]), "pearson": abs(assoc["pearson"] - rec["pearson"])}
    out["checks"]["registered_association"] = {"recomputed": {k: assoc[k] for k in ("n_units", "spearman", "kendall", "pearson", "ci", "permutation_p")},
                                               "receipt": {k: rec[k] for k in ("n_units", "spearman", "kendall", "pearson", "ci", "permutation_p")},
                                               "max_abs_diff": max(diffs.values()), "pass": max(diffs.values()) <= TOL}
    # 3. NumPy parity on the full data: vectorized criterion (registered design) equals analysis_lib.spearman per configuration
    items = d.items_of_tasks(d.heldout_tasks)
    target = rating_target(d.ratings[items], REGISTERED_RATERS)
    # the registered target is the stored target_expert; where p3 is missing the stored value is the two-rater mean
    target_stored = d.target_expert[items]
    c_vec = criterion_vector(d.S[:, items], target_stored)
    worst3 = 0.0
    for ci, c in enumerate(d.configs):
        reg = per[c]["recomputed"]
        v = c_vec[ci]
        if reg is None and not np.isfinite(v):
            continue
        if (reg is None) != (not np.isfinite(v)):
            worst3 = float("inf")
            break
        worst3 = max(worst3, abs(v - reg))
    out["checks"]["numpy_parity_full_data"] = {"max_abs_diff": worst3, "pass": worst3 <= TOL,
                                              "target_expert_vs_mean_p1_p3": float(np.nanmax(np.abs(target - target_stored)))}
    out["pass"] = all(v["pass"] for v in out["checks"].values())
    return out


# ------------------------------------------------------------------ reference criterion and associations
def reference_vectors(d: Data) -> dict:
    A = d.A
    items_all = d.items_of_tasks(d.tasks)
    ref_target = rating_target(d.ratings[items_all], range(len(RATERS)))
    c_ref = criterion_vector(d.S[:, items_all], ref_target)
    items_reg = d.items_of_tasks(d.heldout_tasks)
    c_reg = criterion_vector(d.S[:, items_reg], d.target_expert[items_reg])

    def assoc(c: np.ndarray, seed: int) -> dict:
        m = d.test_computable & np.isfinite(c)
        x = d.cms[m].tolist()
        y = c[m].tolist()
        r = {"n_units": int(m.sum()), "units": [d.configs[i] for i in np.where(m)[0]]}
        if m.sum() >= MIN_UNITS:
            r.update(spearman=A.spearman(x, y), kendall=A.kendall(x, y), pearson=A.pearson(x, y),
                     ci=A.bootstrap_ci(x, y, A.spearman, BOOT_DRAWS, seed), permutation_p=A.permutation_p(x, y, A.spearman, BOOT_DRAWS, seed),
                     resampled_unit="judge configuration", draws=BOOT_DRAWS, seed=seed)
        return r

    rel = spearman_rows(c_reg[np.isfinite(c_reg) & np.isfinite(c_ref)], c_ref[np.isfinite(c_reg) & np.isfinite(c_ref)])[0]
    m = np.isfinite(c_reg) & np.isfinite(c_ref)
    agree = float(np.mean((c_reg[m] >= GATE_RHO) == (c_ref[m] >= GATE_RHO)))
    return {"reference": {"definition": "all 25 tasks (75 items), mean of all available current raters / 5", "criterion": dict(zip(d.configs, c_ref.tolist())),
                          "n_computable": int(np.isfinite(c_ref).sum()), "heldout_association": assoc(c_ref, SEED),
                          "pass_at_gate": int(np.nansum(c_ref >= GATE_RHO)), "ratings_used": int(np.isfinite(d.ratings).sum())},
            "registered": {"definition": "15 validation + test tasks (45 items), stored target_expert (raters 1-3 / 5)", "criterion": dict(zip(d.configs, c_reg.tolist())),
                           "n_computable": int(np.isfinite(c_reg).sum()), "heldout_association": assoc(c_reg, 39),
                           "ranking_reliability_vs_reference": float(rel), "gate_agreement_vs_reference": agree,
                           "ratings_used": int(np.isfinite(d.ratings[d.items_of_tasks(d.heldout_tasks)][:, list(REGISTERED_RATERS)]).sum())},
            "c_ref": c_ref, "c_reg": c_reg}


# ------------------------------------------------------------------ Q1
def q1_grid(d: Data, c_ref: np.ndarray, draws: int, rng: np.random.Generator) -> dict:
    h2 = np.array([p == "H2" for p in d.prompt_key])
    cells = []
    for T in T_GRID:
        for R in R_GRID:
            t0 = time.time()
            C = np.full((draws, d.n_configs), np.nan)
            used = np.zeros(draws)
            n_items = np.zeros(draws)
            rel = np.full(draws, np.nan)
            agree = np.full(draws, np.nan)
            held = np.full(draws, np.nan)
            for k in range(draws):
                c, u, ni, _ = draw_cell(d, rng, T, R)
                C[k] = c
                used[k] = u
                n_items[k] = ni
                m = np.isfinite(c) & np.isfinite(c_ref)
                if m.sum() >= MIN_UNITS:
                    rel[k] = spearman_rows(c[m], c_ref[m])[0]
                    agree[k] = np.mean((c[m] >= GATE_RHO) == (c_ref[m] >= GATE_RHO))
                mt = d.test_computable & np.isfinite(c)
                if mt.sum() >= MIN_UNITS:
                    held[k] = spearman_rows(d.cms[mt], c[mt])[0]
            with np.errstate(invalid="ignore"):
                sd = np.nanstd(C, axis=0, ddof=1) if draws > 1 else np.full(d.n_configs, np.nan)
            cells.append({"T": T, "R": R, "n_items_nominal": 3 * T, "n_items_mean": float(n_items.mean()), "ratings_nominal": 3 * T * R,
                          "ratings_used_mean": float(used.mean()), "draws": draws,
                          "precision_sd_mean_all": float(np.nanmean(sd)), "precision_sd_mean_h2": float(np.nanmean(sd[h2])),
                          "precision_sd_per_configuration": dict(zip(d.configs, sd.tolist())),
                          "not_computable_fraction": float(np.mean(~np.isfinite(C))),
                          "ranking_reliability_mean": float(np.nanmean(rel)), "ranking_reliability_p5": pct(rel, 5),
                          "ranking_reliability_median": float(np.nanmedian(rel)), "ranking_reliability_defined_draws": int(np.isfinite(rel).sum()),
                          "gate_agreement_mean": float(np.nanmean(agree)),
                          "heldout_association_mean": float(np.nanmean(held)), "heldout_association_p5": pct(held, 5),
                          "heldout_association_p95": pct(held, 95), "heldout_association_frac_ge_gate": float(np.nanmean(held >= GATE_RHO)),
                          "heldout_association_defined_draws": int(np.isfinite(held).sum()), "seconds": round(time.time() - t0, 2)})
    return {"written_utc": stamp(), "seed": SEED, "draws_per_cell": draws, "T_grid": list(T_GRID), "R_grid": list(R_GRID),
            "reference": "all 25 tasks, all available raters", "cells": cells}


# ------------------------------------------------------------------ Q2
def power_table(X: np.ndarray, Y: np.ndarray, rng: np.random.Generator, perms: int) -> dict:
    rho, p = perm_p_rows(X, Y, rng, perms)
    ok = np.isfinite(rho) & np.isfinite(p)
    passed = ok & (rho >= GATE_RHO) & (p < GATE_P)
    return {"draws": int(X.shape[0]), "permutations": perms, "undefined_draws": int((~ok).sum()),
            "power": float(passed.mean()), "frac_rho_ge_gate": float(np.mean(ok & (rho >= GATE_RHO))), "frac_p_lt_0_05": float(np.mean(ok & (p < GATE_P))),
            "rho_mean": float(np.nanmean(rho)) if ok.any() else float("nan"), "rho_sd": float(np.nanstd(rho, ddof=1)) if ok.sum() > 1 else float("nan"), "rho_p5": pct(rho, 5),
            "rho_p95": pct(rho, 95)}


def q2_power(d: Data, c_ref: np.ndarray, draws: int, draws_param: int, perms: int, rng: np.random.Generator) -> dict:
    base = np.isfinite(d.cms) & np.isfinite(c_ref)
    pools = {"all_configurations": base, "test_16": base & d.test_mask,
             "fuller_context": base & np.array([p in FULLER for p in d.prompt_key]), "legacy": base & np.array([p in LEGACY for p in d.prompt_key])}
    out = {"written_utc": stamp(), "seed": SEED, "gate": {"spearman": GATE_RHO, "p": GATE_P, "source": "experiment 39 PROTOCOL.md"}, "empirical": {}, "parametric": {}, "clustered": {}}
    for name, mask in pools.items():
        idx = np.where(mask)[0]
        x_pool, y_pool = d.cms[idx], c_ref[idx]
        pool = {"n_pool": int(len(idx)), "configurations": [d.configs[i] for i in idx],
                "pool_spearman": float(spearman_rows(x_pool, y_pool)[0]) if len(idx) >= MIN_UNITS else None, "by_K": {}}
        for K in K_GRID:
            pick = rng.integers(0, len(idx), size=(draws, K))
            pool["by_K"][str(K)] = power_table(x_pool[pick], y_pool[pick], rng, perms)
        out["empirical"][name] = pool
    for rho in RHO_GRID:
        row = {"by_K": {}}
        for K in K_GRID:
            z1 = rng.standard_normal((draws_param, K))
            z2 = rng.standard_normal((draws_param, K))
            y = rho * z1 + math.sqrt(1 - rho ** 2) * z2
            row["by_K"][str(K)] = power_table(z1, y, rng, perms)
        out["parametric"][f"{rho:.2f}"] = row
    # (c) model-clustered: M models with replacement, every computable configuration of each drawn model
    idx_all = np.where(base)[0]
    keys = sorted({d.model_key[i] for i in idx_all})
    by_model = {k: [i for i in idx_all if d.model_key[i] == k] for k in keys}
    for M in M_GRID:
        rhos, ps, Ks = [], [], []
        for _ in range(draws):
            drawn = [keys[j] for j in rng.integers(0, len(keys), size=M)]
            cfg = [i for k in drawn for i in by_model[k]]
            Ks.append(len(cfg))
            if len(cfg) < MIN_UNITS:
                rhos.append(np.nan)
                ps.append(np.nan)
                continue
            x = d.cms[cfg][None, :]
            y = c_ref[cfg][None, :]
            r, p = perm_p_rows(np.tile(x, (1, 1)), y, rng, perms)
            rhos.append(float(r[0]))
            ps.append(float(p[0]))
        rhos = np.array(rhos)
        ps = np.array(ps)
        ok = np.isfinite(rhos) & np.isfinite(ps)
        out["clustered"][str(M)] = {"draws": draws, "permutations": perms, "models_in_pool": keys, "K_mean": float(np.mean(Ks)), "K_min": int(min(Ks)), "K_max": int(max(Ks)),
                                    "draws_below_min_units": int(sum(1 for k in Ks if k < MIN_UNITS)), "undefined_draws": int((~ok).sum()),
                                    "power": float(np.mean(ok & (rhos >= GATE_RHO) & (ps < GATE_P))), "rho_mean": float(np.nanmean(rhos)), "rho_sd": float(np.nanstd(rhos, ddof=1)),
                                    "rho_p5": pct(rhos, 5), "rho_p95": pct(rhos, 95)}
    return out


# ------------------------------------------------------------------ Q3
def q3_allocation(q1: dict) -> dict:
    groups: dict[int, list[dict]] = {}
    for c in q1["cells"]:
        groups.setdefault(c["ratings_nominal"], []).append(c)
    rows = []
    for B in sorted(groups):
        cells = groups[B]
        if len(cells) < 2:
            continue
        best = max(cells, key=lambda c: (c["ranking_reliability_mean"] if math.isfinite(c["ranking_reliability_mean"]) else -9, c["T"]))
        rows.append({"ratings_nominal": B, "cells": [{"T": c["T"], "R": c["R"], "ratings_used_mean": c["ratings_used_mean"], "ranking_reliability_mean": c["ranking_reliability_mean"],
                                                        "gate_agreement_mean": c["gate_agreement_mean"], "precision_sd_mean_all": c["precision_sd_mean_all"]} for c in sorted(cells, key=lambda c: c["T"])],
                     "best": {"T": best["T"], "R": best["R"], "ranking_reliability_mean": best["ranking_reliability_mean"]}})
    more_tasks_wins = sum(1 for r in rows if r["best"]["T"] == max(c["T"] for c in r["cells"]))
    return {"written_utc": stamp(), "rule": "per nominal budget 3*T*R shared by more than one cell: the cell with the highest mean ranking reliability (ties: more tasks)",
            "budgets": rows, "n_budgets": len(rows), "n_budgets_won_by_more_tasks": more_tasks_wins}


# ------------------------------------------------------------------ Q4
def two_way_components(M: np.ndarray, tol: float = 1e-12, max_iter: int = 10000) -> dict:
    """Additive two-way model y_ij = mu + a_i + b_j + e_ij fitted by least squares on the observed cells (NaN = missing)
    through alternating least squares (exact at convergence, no dense design matrix); method-of-moments variance
    components and ICCs (Shrout-Fleiss consistency ICC(C,1) and agreement ICC(A,1))."""
    M = np.asarray(M, dtype=float)
    I, J = M.shape
    obs = np.isfinite(M)
    n_i = obs.sum(axis=1)
    n_j = obs.sum(axis=0)
    if (n_i == 0).any() or (n_j == 0).any():
        raise ValueError("every item and every rater needs at least one observation")
    N = int(obs.sum())
    Y = np.where(obs, M, 0.0)
    a = np.zeros(I)
    b = np.zeros(J)
    for _ in range(max_iter):
        a_new = (Y - obs * b[None, :]).sum(axis=1) / n_i
        b_new = (Y - obs * a_new[:, None]).sum(axis=0) / n_j
        delta = max(float(np.abs(a_new - a).max()), float(np.abs(b_new - b).max()))
        a, b = a_new, b_new
        if delta < tol:
            break
    resid = np.where(obs, M - a[:, None] - b[None, :], 0.0)
    dof = N - (I + J - 1)
    s2e = float((resid ** 2).sum() / dof)
    s2_item = max(0.0, float(np.var(a, ddof=1) - s2e * np.mean(1.0 / n_i)))
    s2_rater = max(0.0, float(np.var(b, ddof=1) - s2e * np.mean(1.0 / n_j)))
    iccc1 = s2_item / (s2_item + s2e) if s2_item + s2e > 0 else None
    icca1 = s2_item / (s2_item + s2_rater + s2e) if s2_item + s2_rater + s2e > 0 else None
    return {"n_items": I, "n_raters": J, "n_observations": N, "sigma2_item": s2_item, "sigma2_rater": s2_rater, "sigma2_error": s2e,
            "icc_c1": iccc1, "icc_a1": icca1,
            "icc_c_by_R": {str(R): (R * iccc1 / (1 + (R - 1) * iccc1)) if iccc1 is not None else None for R in R_GRID},
            "icc_a_by_R": {str(R): (s2_item / (s2_item + (s2_rater + s2e) / R)) if s2_item + s2_rater + s2e > 0 else None for R in R_GRID}}


def balanced_anova_icc(M: np.ndarray) -> dict:
    """Shrout-Fleiss two-way ICCs from a complete items x raters block (classic mean-square formulas)."""
    n, k = M.shape
    grand = M.mean()
    row_means = M.mean(axis=1)
    col_means = M.mean(axis=0)
    msr = k * np.sum((row_means - grand) ** 2) / (n - 1)
    msc = n * np.sum((col_means - grand) ** 2) / (k - 1)
    sse = np.sum((M - row_means[:, None] - col_means[None, :] + grand) ** 2)
    mse = sse / ((n - 1) * (k - 1))
    iccc1 = (msr - mse) / (msr + (k - 1) * mse)
    icca1 = (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)
    return {"n_items": n, "n_raters": k, "icc_c1": float(iccc1), "icc_a1": float(icca1), "ms_items": float(msr), "ms_raters": float(msc), "ms_error": float(mse)}


def q4_extrapolation(d: Data, rng: np.random.Generator, draws: int) -> dict:
    comp = two_way_components(d.ratings)
    complete = np.all(np.isfinite(d.ratings), axis=1)
    bal5 = balanced_anova_icc(d.ratings[complete])
    bal4 = balanced_anova_icc(d.ratings[:, [0, 1, 3, 4]])
    # (b) design effect from a 1,000-draw task bootstrap at 25 tasks with all available raters (see Deviations in results.md)
    items_all = d.items_of_tasks(d.tasks)
    ref_target = rating_target(d.ratings[items_all], range(len(RATERS)))
    C = np.full((draws, d.n_configs), np.nan)
    for k in range(draws):
        tasks = [d.tasks[i] for i in rng.integers(0, len(d.tasks), size=len(d.tasks))]
        items = d.items_of_tasks(tasks)
        C[k] = criterion_vector(d.S[:, items], rating_target(d.ratings[items], range(len(RATERS))))   # target recomputed on the drawn (possibly repeated) items
    with np.errstate(invalid="ignore"):
        sd_z = np.nanstd(fisher_z(C), axis=0, ddof=1)
        sd_r = np.nanstd(C, axis=0, ddof=1)
    N = d.n_items
    fisher_se = 1.0 / math.sqrt(N - 3)
    de = (sd_z / fisher_se) ** 2
    de_med = float(np.nanmedian(de))
    de_mean = float(np.nanmean(de))
    extrap = {}
    for n_new in (N,) + N_EXTRAP:
        sd_new = math.sqrt(de_med) / math.sqrt(n_new - 3)
        extrap[str(n_new)] = {"sd_fisher_z": sd_new, "half_width_95_at_rho": {f"{r:.1f}": float(math.tanh(math.atanh(r) + 1.96 * sd_new) - r) for r in (0.5, 0.8)},
                              "lower_half_width_95_at_rho": {f"{r:.1f}": float(r - math.tanh(math.atanh(r) - 1.96 * sd_new)) for r in (0.5, 0.8)}}
    return {"written_utc": stamp(), "seed": SEED, "label": "MODEL-BASED EXTRAPOLATION (PROTOCOL.md Q4): not a measurement beyond 75 items / 5 raters",
            "a_variance_components_all_observations": comp, "a_balanced_check_45_items_x_5_raters": bal5, "a_balanced_check_75_items_x_4_raters_no_p3": bal4,
            "b_design_effect": {"method": "task bootstrap at 25 tasks, all available raters, per-configuration SD of Fisher z across draws, divided by 1/sqrt(N-3), N=75",
                                "draws": draws, "fisher_se_independent_items": fisher_se, "design_effect_median": de_med, "design_effect_mean": de_mean,
                                "sd_rho_median_across_configurations": float(np.nanmedian(sd_r)), "sd_z_median": float(np.nanmedian(sd_z)),
                                "per_configuration": {c: {"sd_rho": float(sd_r[i]), "sd_z": float(sd_z[i]), "design_effect": float(de[i])} for i, c in enumerate(d.configs)},
                                "extrapolated": extrap},
            "c_attenuation_ceiling": {"rho_max_by_R_consistency": {R: (math.sqrt(v) if v is not None else None) for R, v in comp["icc_c_by_R"].items()},
                                      "rho_max_by_R_agreement": {R: (math.sqrt(v) if v is not None else None) for R, v in comp["icc_a_by_R"].items()},
                                      "note": "rho_max = sqrt(reliability of the R-rater target); the consistency version applies to rank correlations"}}


# ------------------------------------------------------------------ readings and report
def readings(q1: dict, q2: dict) -> dict:
    adequate = [c for c in q1["cells"] if math.isfinite(c["ranking_reliability_mean"]) and c["ranking_reliability_mean"] >= TARGET_RELIABILITY
                and math.isfinite(c["gate_agreement_mean"]) and c["gate_agreement_mean"] >= TARGET_GATE_AGREEMENT]
    best_cell = max(q1["cells"], key=lambda c: (c["ranking_reliability_mean"] if math.isfinite(c["ranking_reliability_mean"]) else -9))
    smallest = min(adequate, key=lambda c: (c["ratings_nominal"], c["T"])) if adequate else None

    def smallest_k(pool: dict):
        for K in K_GRID:
            if pool["by_K"][str(K)]["power"] >= TARGET_POWER:
                return K, pool["by_K"][str(K)]["power"]
        best = max(K_GRID, key=lambda K: pool["by_K"][str(K)]["power"])
        return None, pool["by_K"][str(best)]["power"]

    k_all, p_all = smallest_k(q2["empirical"]["all_configurations"])
    k_full, p_full = smallest_k(q2["empirical"]["fuller_context"])
    m_ok = [M for M in M_GRID if q2["clustered"][str(M)]["power"] >= TARGET_POWER]
    return {"targets": {"ranking_reliability": TARGET_RELIABILITY, "gate_agreement": TARGET_GATE_AGREEMENT, "power": TARGET_POWER, "source": "agent-suggested (PROTOCOL.md)"},
            "smallest_adequate_TR": None if smallest is None else {k: smallest[k] for k in ("T", "R", "ratings_nominal", "ratings_used_mean", "ranking_reliability_mean", "gate_agreement_mean")},
            "best_cell_if_unmet": {k: best_cell[k] for k in ("T", "R", "ranking_reliability_mean", "gate_agreement_mean")},
            "smallest_adequate_K_all_configurations": {"K": k_all, "power": p_all, "met": k_all is not None},
            "smallest_adequate_K_fuller_context": {"K": k_full, "power": p_full, "met": k_full is not None},
            "power_at_K16": {name: q2["empirical"][name]["by_K"]["16"]["power"] for name in q2["empirical"]},
            "smallest_adequate_M_clustered": {"M": (min(m_ok) if m_ok else None), "power": (q2["clustered"][str(min(m_ok))]["power"] if m_ok else max(q2["clustered"][str(M)]["power"] for M in M_GRID)), "met": bool(m_ok)}}


def fmt(v, nd=3):
    return "—" if v is None or (isinstance(v, float) and not math.isfinite(v)) else f"{v:.{nd}f}"


def write_report(d: Data, g0: dict, ref: dict, q1: dict, q2: dict, q3: dict, q4: dict, rd: dict, runtime_s: float, head: str | None) -> None:
    L = []
    rel = EXP.relative_to(REPO)
    L += [f"# Experiment 49 results: how many tasks, raters and held-out judges the cert-judge rating pool needs", "",
          f"**Doc link:** <https://github.com/brando90/cert-judge/blob/main/{rel}/RESULTS_rating_round_design.md>", ""]
    s = rd["smallest_adequate_TR"]
    ka = rd["smallest_adequate_K_all_configurations"]
    kf = rd["smallest_adequate_K_fuller_context"]
    mc = rd["smallest_adequate_M_clustered"]
    reg = ref["registered"]
    tr_txt = (f"{s['T']} tasks × {s['R']} raters ({s['ratings_nominal']} nominal ratings; mean ranking reliability {fmt(s['ranking_reliability_mean'])}, gate agreement {fmt(s['gate_agreement_mean'])})"
              if s else f"no grid cell reaches both targets (best: {rd['best_cell_if_unmet']['T']} tasks × {rd['best_cell_if_unmet']['R']} raters, reliability {fmt(rd['best_cell_if_unmet']['ranking_reliability_mean'])}, gate agreement {fmt(rd['best_cell_if_unmet']['gate_agreement_mean'])})")
    k_txt = f"K = {ka['K']} (power {fmt(ka['power'])})" if ka["met"] else f"unmet within K ≤ {max(K_GRID)} (best power {fmt(ka['power'])})"
    kf_txt = f"K = {kf['K']} (power {fmt(kf['power'])})" if kf["met"] else f"unmet within K ≤ {max(K_GRID)} (best power {fmt(kf['power'])})"
    m_txt = f"M = {mc['M']} judge models (power {fmt(mc['power'])})" if mc["met"] else f"unmet within M ≤ {max(M_GRID)} judge models (best power {fmt(mc['power'])})"
    L += ["**TLDR:** Measured by resampling experiment 39's cached scores (56 LLM judge configurations × 75 VeriBench items × 3 repeats) and VeriBench experiment 100's five current raters, "
          "with no new inference and no new labels. Against the agent-suggested targets (ranking reliability ≥ 0.90 and gate agreement ≥ 0.90 versus the 25-task five-rater reference; power ≥ 0.80 for "
          f"the pre-registered held-out test, Spearman ≥ 0.45 with one-sided permutation p-val < 0.05): the smallest adequate rating design is **{tr_txt}**; "
          f"the smallest adequate number of independently drawn held-out judge configurations from the all-configuration pool is **{k_txt}**; from the fuller-context pool **{kf_txt}**; "
          f"with judge models drawn as clusters, **{m_txt}**. The registered design (15 tasks, raters 1–3) has ranking reliability {fmt(reg['ranking_reliability_vs_reference'])} "
          f"and gate agreement {fmt(reg['gate_agreement_vs_reference'])} against the reference, and its held-out association is {fmt(reg['heldout_association'].get('spearman'))} "
          f"[{fmt((reg['heldout_association'].get('ci') or {}).get('lo'), 2)}, {fmt((reg['heldout_association'].get('ci') or {}).get('hi'), 2)}] p-val={fmt(reg['heldout_association'].get('permutation_p'), 4)} "
          f"(one-sided permutation over {reg['heldout_association'].get('n_units')} configurations). Nothing here changes experiment 39's verdict or set N's evaluation-only rule.", ""]
    L += [f"Generated {stamp()} by `scripts/analyze_e49.py` at worktree commit `{head}`; runtime {runtime_s:.0f} s; seed {SEED} (G0: 39). Inputs and hashes: `results/input_manifest.json`.", ""]
    # G0
    L += ["## Gate G0 — reproduction", "", f"- Criterion of every configuration from the harvest versus the unit files: max |Δ| = {g0['checks']['criterion_reproduction']['max_abs_diff']:.2e} over {g0['checks']['criterion_reproduction']['n_configurations']} configurations → {'PASS' if g0['checks']['criterion_reproduction']['pass'] else 'FAIL'}.",
          f"- Registered `C_ms_gold` test association through `analysis_lib.association` (seed 39): Spearman {fmt(g0['checks']['registered_association']['recomputed']['spearman'])} [{fmt(g0['checks']['registered_association']['recomputed']['ci']['lo'], 3)}, {fmt(g0['checks']['registered_association']['recomputed']['ci']['hi'], 3)}] p-val={fmt(g0['checks']['registered_association']['recomputed']['permutation_p'], 4)} on {g0['checks']['registered_association']['recomputed']['n_units']} units; max |Δ| versus `TEST_RECEIPT.json` = {g0['checks']['registered_association']['max_abs_diff']:.2e} → {'PASS' if g0['checks']['registered_association']['pass'] else 'FAIL'}.",
          f"- NumPy parity (vectorized tie-aware Spearman versus `analysis_lib.spearman` on the registered design, every configuration): max |Δ| = {g0['checks']['numpy_parity_full_data']['max_abs_diff']:.2e} → {'PASS' if g0['checks']['numpy_parity_full_data']['pass'] else 'FAIL'}.", f"- G0 overall: **{'PASS' if g0['pass'] else 'FAIL'}**.", ""]
    # reference
    ra = ref["reference"]["heldout_association"]
    L += ["## Reference criterion and the two fixed designs", "",
          "| Design | Items (tasks) | Raters | Ratings used | Computable configurations | Held-out association of `C_ms_gold` (n) | Kendall τ-b | Pearson | Ranking reliability vs reference | Gate agreement vs reference |", "|---|---|---|---|---|---|---|---|---|---|",
          f"| Reference | 75 (25) | all available (5; 4 where `p3` is missing) | {ref['reference']['ratings_used']} | {ref['reference']['n_computable']}/56 | {fmt(ra.get('spearman'))} [{fmt((ra.get('ci') or {}).get('lo'), 2)}, {fmt((ra.get('ci') or {}).get('hi'), 2)}] p-val={fmt(ra.get('permutation_p'), 4)} ({ra.get('n_units')}) | {fmt(ra.get('kendall'))} | {fmt(ra.get('pearson'))} | 1 (by definition) | 1 |",
          f"| Registered (experiment 39) | 45 (15) | 1–3 (stored `target_expert`) | {reg['ratings_used']} | {reg['n_computable']}/56 | {fmt(reg['heldout_association'].get('spearman'))} [{fmt((reg['heldout_association'].get('ci') or {}).get('lo'), 2)}, {fmt((reg['heldout_association'].get('ci') or {}).get('hi'), 2)}] p-val={fmt(reg['heldout_association'].get('permutation_p'), 4)} ({reg['heldout_association'].get('n_units')}) | {fmt(reg['heldout_association'].get('kendall'))} | {fmt(reg['heldout_association'].get('pearson'))} | {fmt(reg['ranking_reliability_vs_reference'])} | {fmt(reg['gate_agreement_vs_reference'])} |", "",
          "Intervals are 95% percentile bootstraps over judge configurations (10,000 draws); p-values are one-sided permutation tests of a positive association (10,000 permutations); the reference uses seed 49, the registered design seed 39.", ""]
    # Q1
    L += ["## Q1 — criterion precision and ranking reliability versus tasks and raters", "",
          f"{q1['draws_per_cell']} draws per cell (seed {SEED}); tasks drawn without replacement (all three outputs of a task together), raters drawn without replacement from the five current raters; a configuration's criterion needs ≥ 90% of the drawn items scored. Reliability and gate agreement are against the reference (25 tasks, all available raters); the held-out association is the Spearman between `C_ms_gold` and the draw's criterion over the computable test configurations.", "",
          "| Tasks T | Raters R | Items | Ratings used (mean) | Criterion SD (mean over 56) | Criterion SD (H2, 8) | Ranking reliability mean [5th pct] | Gate agreement | Held-out association mean [5th, 95th pct] | Draws ≥ 0.45 | Not computable |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in q1["cells"]:
        L.append(f"| {c['T']} | {c['R']} | {c['n_items_nominal']} | {c['ratings_used_mean']:.1f} | {fmt(c['precision_sd_mean_all'])} | {fmt(c['precision_sd_mean_h2'])} | {fmt(c['ranking_reliability_mean'])} [{fmt(c['ranking_reliability_p5'])}] | {fmt(c['gate_agreement_mean'])} | {fmt(c['heldout_association_mean'])} [{fmt(c['heldout_association_p5'], 2)}, {fmt(c['heldout_association_p95'], 2)}] | {fmt(c['heldout_association_frac_ge_gate'], 2)} | {fmt(c['not_computable_fraction'], 3)} |")
    L += ["", "The T = 25, R = 5 cell is the reference itself (no variation). p-val=n/a throughout this table (descriptive resampling).", ""]
    # Q2
    L += ["## Q2 — power of the held-out test versus the number of held-out judge configurations", "",
          f"Gate: Spearman ≥ {GATE_RHO} and one-sided permutation p-val < {GATE_P} (experiment 39's pre-registered rule). {Q2_DRAWS} draws per cell with {Q2_PERMS} permutations each (seed {SEED}); pairs (`C_ms_gold`, reference criterion) drawn with replacement, so configurations are treated as independent (optimistic; see the clustered variant).", "",
          "| Pool (n, pool Spearman) | " + " | ".join(f"K = {K}" for K in K_GRID) + " |", "|---|" + "---|" * len(K_GRID)]
    for name, pool in q2["empirical"].items():
        L.append(f"| {name} ({pool['n_pool']}, {fmt(pool['pool_spearman'])}) | " + " | ".join(f"{fmt(pool['by_K'][str(K)]['power'], 2)} (ρ̄ {fmt(pool['by_K'][str(K)]['rho_mean'], 2)}, sd {fmt(pool['by_K'][str(K)]['rho_sd'], 2)})" for K in K_GRID) + " |")
    L += ["", f"Parametric (bivariate normal pairs, {Q2B_DRAWS} draws per cell, same gate):", "", "| True ρ | " + " | ".join(f"K = {K}" for K in K_GRID) + " |", "|---|" + "---|" * len(K_GRID)]
    for rho, row in q2["parametric"].items():
        L.append(f"| {rho} | " + " | ".join(fmt(row["by_K"][str(K)]["power"], 2) for K in K_GRID) + " |")
    L += ["", "Model-clustered (M judge models drawn with replacement from the nine model keys; every computable configuration of a drawn model enters; draws with fewer than 8 configurations count as failures):", "",
          "| Models M | K mean [min, max] | Draws with K < 8 | Power | ρ̄ (sd) [5th, 95th pct] |", "|---|---|---|---|---|"]
    for M in M_GRID:
        r = q2["clustered"][str(M)]
        L.append(f"| {M} | {r['K_mean']:.1f} [{r['K_min']}, {r['K_max']}] | {r['draws_below_min_units']} | {fmt(r['power'], 2)} | {fmt(r['rho_mean'], 2)} ({fmt(r['rho_sd'], 2)}) [{fmt(r['rho_p5'], 2)}, {fmt(r['rho_p95'], 2)}] |")
    L += [""]
    # Q3
    L += ["## Q3 — allocation at equal rating budgets (from the Q1 grid)", "", f"Rule: {q3['rule']}.", "", "| Nominal ratings | Cells (T × R → reliability, gate agreement, criterion SD) | Best |", "|---|---|---|"]
    for r in q3["budgets"]:
        L.append(f"| {r['ratings_nominal']} | " + "; ".join(f"{c['T']}×{c['R']} → {fmt(c['ranking_reliability_mean'])}, {fmt(c['gate_agreement_mean'], 2)}, {fmt(c['precision_sd_mean_all'])}" for c in r["cells"]) + f" | {r['best']['T']} tasks × {r['best']['R']} raters |")
    L += ["", f"More tasks (fewer raters) wins {q3['n_budgets_won_by_more_tasks']} of {q3['n_budgets']} equal-budget comparisons.", ""]
    L = [ln.replace("× 1 raters", "× 1 rater") for ln in L]
    # Q4
    a = q4["a_variance_components_all_observations"]
    b = q4["b_design_effect"]
    L += ["## Q4 — model-based extrapolation (labelled; not a measurement beyond 75 items and 5 raters)", "",
          f"(a) Two-way additive model on all {a['n_observations']} ratings ({a['n_items']} items × {a['n_raters']} raters, missing allowed): σ²_item {fmt(a['sigma2_item'])}, σ²_rater {fmt(a['sigma2_rater'])}, σ²_error {fmt(a['sigma2_error'])} (0–5 scale); single-rater ICC(C,1) {fmt(a['icc_c1'])}, ICC(A,1) {fmt(a['icc_a1'])}. "
          f"Balanced checks: 45 items × 5 raters ICC(C,1) {fmt(q4['a_balanced_check_45_items_x_5_raters']['icc_c1'])}, ICC(A,1) {fmt(q4['a_balanced_check_45_items_x_5_raters']['icc_a1'])}; 75 items × 4 raters (without `p3`) ICC(C,1) {fmt(q4['a_balanced_check_75_items_x_4_raters_no_p3']['icc_c1'])}, ICC(A,1) {fmt(q4['a_balanced_check_75_items_x_4_raters_no_p3']['icc_a1'])}.", "",
          "| Raters R | ICC(C,R) of the R-rater mean | ρ_max = √ICC(C,R) | ICC(A,R) | ρ_max (agreement) |", "|---|---|---|---|---|"]
    for R in R_GRID:
        L.append(f"| {R} | {fmt(a['icc_c_by_R'][str(R)])} | {fmt(q4['c_attenuation_ceiling']['rho_max_by_R_consistency'][str(R)])} | {fmt(a['icc_a_by_R'][str(R)])} | {fmt(q4['c_attenuation_ceiling']['rho_max_by_R_agreement'][str(R)])} |")
    L += ["", f"(b) Design effect: {b['method']}; {b['draws']} draws. Median per-configuration SD of the criterion {fmt(b['sd_rho_median_across_configurations'])} (Fisher z SD {fmt(b['sd_z_median'])}) against the independent-items Fisher SE {fmt(b['fisher_se_independent_items'])}: design effect median {fmt(b['design_effect_median'], 2)}, mean {fmt(b['design_effect_mean'], 2)}.", "",
          "| Items N | Extrapolated SD (Fisher z) | 95% half-width above ρ = 0.5 | below ρ = 0.5 | above ρ = 0.8 | below ρ = 0.8 |", "|---|---|---|---|---|---|"]
    for n_new, e in b["extrapolated"].items():
        L.append(f"| {n_new} | {fmt(e['sd_fisher_z'])} | {fmt(e['half_width_95_at_rho']['0.5'])} | {fmt(e['lower_half_width_95_at_rho']['0.5'])} | {fmt(e['half_width_95_at_rho']['0.8'])} | {fmt(e['lower_half_width_95_at_rho']['0.8'])} |")
    L += ["", "(c) ρ_max is the attenuation ceiling for any proxy–criterion correlation implied by the R-rater target's reliability (model-based).", ""]
    # readings
    L += ["## Pre-declared readings", "", f"Targets (agent-suggested, PROTOCOL.md): ranking reliability ≥ {TARGET_RELIABILITY}, gate agreement ≥ {TARGET_GATE_AGREEMENT}, power ≥ {TARGET_POWER}.", "",
          f"- Smallest adequate (T, R): {tr_txt}.", f"- Smallest adequate K, all-configuration pool: {k_txt}.", f"- Smallest adequate K, fuller-context pool: {kf_txt}.",
          f"- Smallest adequate M, model-clustered: {m_txt}.", f"- Power at K = 16 by pool: " + ", ".join(f"{k} {fmt(v, 2)}" for k, v in rd["power_at_K16"].items()) + ".", "",
          f"**Headline triple:** (smallest adequate (T, R) = {('%d × %d' % (s['T'], s['R'])) if s else 'unmet'}; smallest adequate K for the all-configuration pool = {ka['K'] if ka['met'] else 'unmet'}; power at K = 16 for the fuller-context pool = {fmt(rd['power_at_K16']['fuller_context'], 2)}).", "",
          "**Reading the power numbers.** The all-configuration pool mixes the two prompt-rendering families: the legacy prompts (P1/P4/P8/LEX) have both low `C_ms_gold` and low agreement, so its pool Spearman "
          f"({fmt(q2['empirical']['all_configurations']['pool_spearman'], 2)}) and its power are carried by the between-family contrast. Within the fuller-context family (the configurations anyone would deploy) the pool Spearman is "
          f"{fmt(q2['empirical']['fuller_context']['pool_spearman'], 2)}, below the 0.45 gate, and no number of held-out configurations reaches 0.80 power; the parametric row at ρ = 0.30 shows why: as K grows the estimate concentrates below the gate and power falls. "
          "The all-configuration and model-clustered pools also contain the 38 train and validation configurations on which `C_ms_gold` was selected, so their pool Spearman is optimistic relative to the held-out 16 (0.56 registered, 0.60 against the reference). More ratings do not change this either (the held-out association column of Q1 is flat in T and R once the criterion is reliable). For the next pool the decisive lever is the size of the within-family effect (a better screen or a gate chosen for the deployable family), not more judges or more ratings; the model-clustered rows inherit the same between-family contrast.", "",
          "Nothing here changes experiment 39's verdict, the frozen screen, or set N's evaluation-only rule.", ""]
    L += [f"**TLDR-end:** [cert-judge: experiment 49 rating-round design from cached scores] Smallest adequate rating design {('%d tasks × %d raters' % (s['T'], s['R'])) if s else 'unmet in the grid'}; held-out test power reaches {TARGET_POWER} at K = {ka['K'] if ka['met'] else 'more than %d' % max(K_GRID)} independently drawn configurations of the mixed-family pool (power {fmt(ka['power'], 2)}), but the fuller-context pool gives only {fmt(rd['power_at_K16']['fuller_context'], 2)} at K = 16 and never reaches it, because its pool Spearman ({fmt(q2['empirical']['fuller_context']['pool_spearman'], 2)}) sits below the 0.45 gate.", ""]
    REPORT.write_text("\n".join(L))


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="smoke run with tiny draw counts (never for results)")
    args = ap.parse_args()
    t0 = time.time()
    draws_q1, draws_q2, draws_q2b, perms, draws_q4 = (Q1_DRAWS, Q2_DRAWS, Q2B_DRAWS, Q2_PERMS, 1000) if not args.quick else (20, 20, 20, 50, 20)
    A = load_analysis_lib()
    d = Data(A)
    head = git_head()
    RESULTS.mkdir(exist_ok=True)
    write_json(RESULTS / "input_manifest.json", {"written_utc": stamp(), "worktree_head": head, "experiment_39_root": str(d.e39.relative_to(REPO)),
                                                 "items_path": str(d.items_path), "items_sha256_expected": ITEMS_SHA256, "sha256": d.hashes,
                                                 "n_llm_configurations": d.n_configs, "configurations": d.configs, "n_items": d.n_items, "n_tasks": len(d.tasks),
                                                 "python": sys.version.split()[0], "numpy": np.__version__, "quick": args.quick})
    g0 = gate_g0(d)
    write_json(RESULTS / "g0_reproduction.json", clean(g0))
    if not g0["pass"]:
        print(json.dumps({"G0": "FAIL", "checks": {k: v["pass"] for k, v in g0["checks"].items()}}))
        return 1
    ref = reference_vectors(d)
    rng = np.random.default_rng(SEED)
    q1 = q1_grid(d, ref["c_ref"], draws_q1, rng)
    q1["registered_cell"] = {k: ref["registered"][k] for k in ("definition", "ranking_reliability_vs_reference", "gate_agreement_vs_reference", "ratings_used", "n_computable")}
    q1["registered_cell"]["heldout_association"] = ref["registered"]["heldout_association"]
    q1["reference_cell"] = {k: ref["reference"][k] for k in ("definition", "ratings_used", "n_computable", "pass_at_gate")}
    q1["reference_cell"]["heldout_association"] = ref["reference"]["heldout_association"]
    q1["criterion_reference"] = ref["reference"]["criterion"]
    q1["criterion_registered"] = ref["registered"]["criterion"]
    write_json(RESULTS / "q1_precision_grid.json", clean(q1))
    q2 = q2_power(d, ref["c_ref"], draws_q2, draws_q2b, perms, rng)
    write_json(RESULTS / "q2_power.json", clean(q2))
    q3 = q3_allocation(q1)
    write_json(RESULTS / "q3_allocation.json", clean(q3))
    q4 = q4_extrapolation(d, rng, draws_q4)
    write_json(RESULTS / "q4_extrapolation.json", clean(q4))
    rd = readings(q1, q2)
    runtime = time.time() - t0
    summary = {"written_utc": stamp(), "seed": SEED, "quick": args.quick, "runtime_seconds": round(runtime, 1), "g0_pass": g0["pass"], "readings": rd,
               "reference_heldout_association": ref["reference"]["heldout_association"], "registered_heldout_association": ref["registered"]["heldout_association"],
               "registered_vs_reference": {"ranking_reliability": ref["registered"]["ranking_reliability_vs_reference"], "gate_agreement": ref["registered"]["gate_agreement_vs_reference"]},
               "q4_single_rater_icc_c1": q4["a_variance_components_all_observations"]["icc_c1"], "q4_design_effect_median": q4["b_design_effect"]["design_effect_median"]}
    write_json(RESULTS / "summary.json", clean(summary))
    if not args.quick:
        write_report(d, g0, ref, q1, q2, q3, q4, rd, runtime, head)
    print(json.dumps(clean({"G0": "PASS", "readings": rd, "runtime_s": round(runtime, 1)}), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
