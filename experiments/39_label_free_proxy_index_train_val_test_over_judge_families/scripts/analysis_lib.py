#!/usr/bin/env python3
"""TLDR: Pure-Python analysis library for experiment 39 — tie-aware rank statistics with bootstrap and
permutation uncertainty, the human-agreement criterion per judge configuration, the ten label-free property
components, the paper's frozen indices (PTI-v0 as specified; TI_var with a frozen training-panel normalization)
and the pre-registered candidate index family with the train-then-val selection rule. No model calls."""
from __future__ import annotations

import math
import random
import statistics
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[3] / "py_src")]
from cert_judge import pti_v0 as PV                            # noqa: E402

HUMAN_CEILING_HELDOUT = 0.747          # mean leave-one-expert-out Spearman on the 45 held-out items (experiment 100)
MIN_CRITERION_COVERAGE = 0.90          # a configuration's criterion needs >= 90% of the held-out items scored
MIN_COMPONENT_COVERAGE = 0.80          # a component needs >= 80% of its structurally valid probes scored
MIN_UNITS = 8                          # a correlation over fewer configurations is not computed
COMPONENTS = ("ident", "blank", "ms_gold", "ms_cand", "bm_gold", "alpha", "reorder", "sorry", "spam", "stab")
COV7 = ("ms_gold", "ms_cand", "alpha", "sorry", "reorder", "stab", "spam")
CANDIDATES: dict[str, tuple[str, tuple[str, ...]]] = {
    "PTI_v0_frozen": ("frozen", ("ident", "bm_gold", "ms_gold", "alpha")),
    "TI_var_trainnorm": ("frozen", ("bm_gold", "stab")),
    "GM_cov5": ("gm", ("ms_gold", "ms_cand", "alpha", "sorry", "reorder")),
    "GM_cov6": ("gm", ("ms_gold", "ms_cand", "alpha", "sorry", "reorder", "stab")),
    "GM_cov7": ("gm", COV7),
    "GM_all10": ("gm", COMPONENTS),
    "AM_cov7": ("am", COV7),
    "MIN_cov7": ("min", COV7),
    "GM_mono2": ("gm", ("ms_gold", "ms_cand")),
    "GM_inv3": ("gm", ("alpha", "sorry", "reorder")),
    "GM_bm_ms_inv": ("gm", ("bm_gold", "ms_gold", "ms_cand", "alpha", "sorry", "reorder")),
}
for _c in COMPONENTS:
    CANDIDATES[f"C_{_c}"] = ("single", (_c,))


# ------------------------------------------------------------------ statistics
def spearman(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None and math.isfinite(a) and math.isfinite(b)]
    if len(pairs) < 3 or len({a for a, _ in pairs}) < 2 or len({b for _, b in pairs}) < 2:
        return None
    return PV.spearman_rho([a for a, _ in pairs], [b for _, b in pairs])


def kendall(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3 or len({a for a, _ in pairs}) < 2 or len({b for _, b in pairs}) < 2:
        return None
    return PV.kendall_tau_b([a for a, _ in pairs], [b for _, b in pairs])


def pearson(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    n = len(pairs)
    if n < 3:
        return None
    mx = sum(a for a, _ in pairs) / n
    my = sum(b for _, b in pairs) / n
    sxx = sum((a - mx) ** 2 for a, _ in pairs)
    syy = sum((b - my) ** 2 for _, b in pairs)
    if sxx == 0 or syy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in pairs) / math.sqrt(sxx * syy)


def bootstrap_ci(x, y, fn=spearman, draws: int = 10000, seed: int = 39, clusters=None, level: float = 0.95):
    """Percentile interval over resampled units, or over resampled clusters (tasks) when given."""
    rng = random.Random(seed)
    n = len(x)
    if n < 3:
        return {"lo": None, "hi": None, "valid_draws": 0}
    groups = None
    if clusters is not None:
        groups = {}
        for i, c in enumerate(clusters):
            groups.setdefault(c, []).append(i)
        keys = sorted(groups)
    values = []
    for _ in range(draws):
        if groups is None:
            idx = [rng.randrange(n) for _ in range(n)]
        else:
            idx = [i for k in (rng.choice(keys) for _ in keys) for i in groups[k]]
        v = fn([x[i] for i in idx], [y[i] for i in idx])
        if v is not None:
            values.append(v)
    if not values:
        return {"lo": None, "hi": None, "valid_draws": 0}
    values.sort()
    a = (1 - level) / 2
    return {"lo": values[int(a * (len(values) - 1))], "hi": values[int((1 - a) * (len(values) - 1))], "valid_draws": len(values)}


def permutation_p(x, y, fn=spearman, draws: int = 10000, seed: int = 39):
    """One-sided p-value for a positive association: P(stat >= observed) under label permutation, (k+1)/(n+1)."""
    observed = fn(x, y)
    if observed is None:
        return None
    rng = random.Random(seed)
    ys = list(y)
    k = 0
    for _ in range(draws):
        rng.shuffle(ys)
        v = fn(x, ys)
        if v is not None and v >= observed - 1e-12:
            k += 1
    return (k + 1) / (draws + 1)


def geometric_mean(values):
    vals = [float(v) for v in values]
    if not vals or any(v is None for v in vals):
        return None
    if any(v <= 0.0 for v in vals):
        return 0.0
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def sd_pop(values):
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


# ------------------------------------------------------------------ harvest access
class Scores:
    """Scores of one configuration indexed by (kind, key, level) -> list over repeats (measured + deterministic)."""

    def __init__(self, harvest: dict):
        self.config = harvest["config"]
        self.split = harvest["split"]
        self.family = harvest["family"]
        self.kind = harvest["kind"]
        self.harness = harvest.get("harness", "vb103_judge" if harvest["kind"] == "llm" else "none")
        self.cells: dict[tuple, list[float]] = {}
        self.status_counts = harvest.get("status_counts", {})
        for c in harvest["cells"]:
            if c["status"] in ("measured", "deterministic") and c.get("score") is not None:
                self.cells.setdefault((c["kind"], c["key"], c["level"]), []).append(float(c["score"]))

    def repeats(self, kind: str, key: str, level: int = 0) -> list[float]:
        return self.cells.get((kind, key, level), [])

    def median(self, kind: str, key: str, level: int = 0):
        reps = self.repeats(kind, key, level)
        return statistics.median(reps) if reps else None


def valid_probes(manifest: dict, allow_unvalidated: bool = False) -> dict[str, list[dict]]:
    """Structurally valid probe rows by kind (the denominators of every coverage figure)."""
    out: dict[str, list[dict]] = {}
    for r in manifest["rows"]:
        if r["valid"] is True or (r["valid"] is None and allow_unvalidated):
            out.setdefault(r["kind"], []).append(r)
    return out


# ------------------------------------------------------------------ criterion
def criterion(sc: Scores, items: list[dict], splits: tuple[str, ...], draws: int = 10000, seed: int = 39) -> dict:
    rows = [it for it in items if it["split"] in splits]
    xs, ys, tasks = [], [], []
    for it in rows:
        m = sc.median("crit", it["item"], 0)
        if m is not None:
            xs.append(m)
            ys.append(float(it["target_expert"]))
            tasks.append(it["task"])
    coverage = len(xs) / len(rows) if rows else 0.0
    out = {"splits": list(splits), "n_declared": len(rows), "n_items": len(xs), "coverage": round(coverage, 4),
           "spearman": None, "kendall": None, "pearson": None, "ci": None, "status": "NOT_COMPUTABLE"}
    if coverage + 1e-9 >= MIN_CRITERION_COVERAGE:
        out.update(spearman=spearman(xs, ys), kendall=kendall(xs, ys), pearson=pearson(xs, ys),
                   ci=bootstrap_ci(xs, ys, spearman, draws, seed, clusters=tasks), status="COMPUTED")
    return out


# ------------------------------------------------------------------ components
def ladder_quality(levels: list[int], medians: list[float]):
    """PTI-v0's per-ladder quality C = (1 - rho)/2 with tie-aware Spearman; a constant ladder is C = 0."""
    if len(medians) < 2:
        return None
    if all(v == medians[0] for v in medians[1:]):
        return 0.0
    rho = PV.spearman_rho([float(v) for v in levels], medians)
    return None if rho is None else PV.ladder_quality_from_rho(rho)


def ladder_medians(sc: Scores, kind: str, key: str, base_kind: str, valid_levels: list[int]):
    """Level-0 median from the base cell (ident for gold ladders, crit for candidate ladders) plus each valid level."""
    base = sc.median(base_kind, key, 0)
    if base is None:
        return None, None
    levels, meds = [0], [base]
    for level in sorted(valid_levels):
        m = sc.median(kind, key, level)
        if m is None:
            return None, None                       # a partially scored ladder is not a ladder
        levels.append(level)
        meds.append(m)
    return levels, meds


def components(sc: Scores, probes: dict[str, list[dict]]) -> dict:
    """The ten label-free components with their probe counts; None when coverage is below the threshold."""
    out = {}

    def finish(name, values, declared):
        n = len(values)
        cov = n / declared if declared else 0.0
        out[name] = {"value": (sum(values) / n) if n and cov + 1e-9 >= MIN_COMPONENT_COVERAGE else None,
                     "n": n, "declared": declared, "coverage": round(cov, 4)}

    ident_rows = probes.get("ident", [])
    vals = [sc.median("ident", r["key"], 0) for r in ident_rows]
    finish("ident", [v for v in vals if v is not None], len(ident_rows))
    blank_rows = probes.get("blank", [])
    vals = [sc.median("blank", r["key"], 0) for r in blank_rows]
    finish("blank", [1.0 - v for v in vals if v is not None], len(blank_rows))

    for name, kind, base in (("ms_gold", "ms_gold", "ident"), ("ms_cand", "ms_cand", "crit"), ("bm_gold", "bm_gold", "ident")):
        by_key: dict[str, list[int]] = {}
        for r in probes.get(kind, []):
            by_key.setdefault(r["key"], []).append(r["level"])
        qualities = []
        for key, levels in by_key.items():
            lv, meds = ladder_medians(sc, kind, key, base, levels)
            if lv is None:
                continue
            q = ladder_quality(lv, meds)
            if q is not None:
                qualities.append(q)
        finish(name, qualities, len(by_key))

    for name in ("alpha", "reorder", "sorry"):
        vals = []
        rows = probes.get(name, [])
        for r in rows:
            base, probe = sc.median("crit", r["key"], 0), sc.median(name, r["key"], r["level"])
            if base is not None and probe is not None:
                vals.append(1.0 - abs(base - probe))
        finish(name, vals, len(rows))
    vals, rows = [], probes.get("spam", [])
    for r in rows:
        base, probe = sc.median("crit", r["key"], 0), sc.median("spam", r["key"], r["level"])
        if base is not None and probe is not None:
            vals.append(1.0 - max(0.0, probe - base))
    finish("spam", vals, len(rows))

    repeated = [reps for (kind, key, level), reps in sc.cells.items() if kind in ("crit", "ident", "bm_gold") and len(reps) >= 2]
    declared = sum(1 for r in probes.get("crit", []) + probes.get("ident", []) + probes.get("bm_gold", []))
    instab = [min(1.0, 2.0 * sd_pop(reps)) for reps in repeated]
    finish("stab", [1.0 - v for v in instab], declared)
    return out


# ------------------------------------------------------------------ frozen paper indices
def pti_v0_frozen(sc: Scores, probes: dict[str, list[dict]]) -> dict:
    """PTI-v0 exactly as docs/spec/PTI_V0.md: strict coverage, exact-zero geometric means, K=1 ladders -> mu = C."""
    props = {}
    ident_rows = probes.get("ident", [])
    eq = [sc.median("ident", r["key"], 0) for r in ident_rows]
    props["P_eq"] = PV.aggregate_property_factors([v for v in eq if v is not None], required_count=len(ident_rows) or None) \
        if ident_rows else PV.PropertyResult(PV.NOT_COMPUTABLE, None, 0.0, 0, 0, 0, 0, 0)
    for prop, kind in (("P_bm", "bm_gold"), ("P_ms", "ms_gold")):
        by_key: dict[str, list[int]] = {}
        for r in probes.get(kind, []):
            by_key.setdefault(r["key"], []).append(r["level"])
        ladders = []
        for key, levels in by_key.items():
            rows = [sc.repeats("ident", key, 0)] + [sc.repeats(kind, key, lv) for lv in sorted(levels)]
            if any(not row for row in rows):
                continue
            k = min(len(row) for row in rows)
            rows = [row[:k] for row in rows] if k > 1 and all(len(row) >= k for row in rows) else [[statistics.median(row)] for row in rows]
            try:
                ladders.append(PV.ladder_factor(rows))
            except (ValueError, AssertionError):
                continue
        props[prop] = PV.aggregate_ladder_property(ladders, required_count=len(by_key) or None) if by_key else \
            PV.PropertyResult(PV.NOT_COMPUTABLE, None, 0.0, 0, 0, 0, 0, 0)
    orig, alph = [], []
    for r in probes.get("alpha", []):
        base, probe = sc.median("crit", r["key"], 0), sc.median("alpha", r["key"], r["level"])
        if base is not None and probe is not None:
            orig.append(base)
            alph.append(probe)
    n_alpha = len(probes.get("alpha", []))
    if n_alpha and len(orig) == n_alpha:
        props["P_eqalpha"] = PV.PropertyResult(PV.COMPUTED, PV.alpha_invariance_property(orig, alph), 1.0, n_alpha, n_alpha, 0,
                                               sum(1 for o, a in zip(orig, alph) if 1.0 - abs(o - a) == 0.0), 0)
    else:
        props["P_eqalpha"] = PV.PropertyResult(PV.NOT_COMPUTABLE, None, (len(orig) / n_alpha) if n_alpha else 0.0, n_alpha, len(orig), n_alpha - len(orig), 0, 0)
    result = PV.compute_pti(props)
    return {"value": result.value, "status": result.status, "properties": {k: {"value": v.value, "status": v.status, "coverage": v.coverage,
            "observed": v.observed_count, "required": v.required_count, "zero_count": v.zero_count,
            "constant_ladders": v.constant_ladder_count} for k, v in props.items()},
            "missing_properties": list(result.missing_properties)}


def ti_var_raw(sc: Scores, probes: dict[str, list[dict]]) -> dict | None:
    """The three bug-ladder quantities behind the paper's TI_var: C_f (mean per-ladder quality), V_c (variance of the
    per-ladder qualities) and V_s (mean within-level variance across repeated calls)."""
    by_key: dict[str, list[int]] = {}
    for r in probes.get("bm_gold", []):
        by_key.setdefault(r["key"], []).append(r["level"])
    qualities, within = [], []
    for key, levels in by_key.items():
        lv, meds = ladder_medians(sc, "bm_gold", key, "ident", levels)
        if lv is None:
            continue
        q = ladder_quality(lv, meds)
        if q is None:
            continue
        qualities.append(q)
        for level in lv:
            reps = sc.repeats("ident" if level == 0 else "bm_gold", key, level)
            if len(reps) >= 2:
                within.append(sd_pop(reps) ** 2)
    if not by_key or len(qualities) / len(by_key) + 1e-9 < MIN_COMPONENT_COVERAGE or not within:
        return None
    return {"C_f": sum(qualities) / len(qualities), "V_c": sd_pop(qualities) ** 2, "V_s": sum(within) / len(within), "n_ladders": len(qualities)}


def ti_var(raw: dict, norm: dict) -> float:
    """exp(mean(log C_f, log(1 - Vc~), log(1 - Vs~))) with min-max normalization frozen from the training panel and
    the implementation's 1e-6 floor (paper eq. tivar)."""
    def minmax(v, lo, hi):
        return 0.0 if hi <= lo else min(1.0, max(0.0, (v - lo) / (hi - lo)))
    terms = [max(raw["C_f"], 1e-6), max(1.0 - minmax(raw["V_c"], *norm["V_c"]), 1e-6), max(1.0 - minmax(raw["V_s"], *norm["V_s"]), 1e-6)]
    return math.exp(sum(math.log(t) for t in terms) / 3.0)


def candidate_value(name: str, comps: dict, frozen: dict):
    kind, parts = CANDIDATES[name]
    if kind == "frozen":
        return frozen.get(name)
    values = [comps[p]["value"] for p in parts]
    if any(v is None for v in values):
        return None
    if kind == "gm":
        return geometric_mean(values)
    if kind == "am":
        return sum(values) / len(values)
    if kind == "min":
        return min(values)
    if kind == "single":
        return values[0]
    raise KeyError(kind)


def association(units: list[dict], index_name: str, criterion_key: str = "heldout", draws: int = 10000, seed: int = 39,
                with_uncertainty: bool = True) -> dict:
    """Spearman (primary), Kendall and Pearson between an index and the criterion over judge configurations."""
    pairs = [(u["indices"].get(index_name), (u["criteria"].get(criterion_key) or {}).get("spearman"), u["config"]) for u in units]
    pairs = [(a, b, c) for a, b, c in pairs if a is not None and b is not None]
    x, y = [a for a, _, _ in pairs], [b for _, b, _ in pairs]
    out = {"index": index_name, "criterion": criterion_key, "n_units": len(pairs), "units": [c for _, _, c in pairs],
           "spearman": None, "kendall": None, "pearson": None, "ci": None, "permutation_p": None}
    if len(pairs) < MIN_UNITS:
        return out
    out.update(spearman=spearman(x, y), kendall=kendall(x, y), pearson=pearson(x, y))
    if with_uncertainty:
        out.update(ci=bootstrap_ci(x, y, spearman, draws, seed), permutation_p=permutation_p(x, y, spearman, draws, seed))
    return out


def rank_candidates(units: list[dict], names, criterion_key: str = "heldout") -> list[dict]:
    rows = []
    for name in names:
        a = association(units, name, criterion_key, with_uncertainty=False)
        rows.append({"index": name, "n_components": len(CANDIDATES[name][1]), **{k: a[k] for k in ("n_units", "spearman", "kendall", "pearson")}})
    rows.sort(key=lambda r: (-(r["spearman"] if r["spearman"] is not None else -9.0), r["n_components"], r["index"]))
    return rows
