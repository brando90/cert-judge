#!/usr/bin/env python3
"""Experiment 39: best-of-K judge selection bias on the 72-pair validation set.

Zero inference. Reads frozen labels and judge scores under ``experiments/archive/``
and writes CSV/JSON/figures under this experiment. No model clients, credentials
or network access. The frozen plan is ``../PROTOCOL.md``.

Analyses
  A  null best-of-K: block-permuted labels, largest agreement among K real configurations
  B  split-half selection: choose on 12 problems, evaluate on the other 12
  C  synthetic sweep: latent-quality model calibrated to the panel, K up to 64
  D  judge-level association adjusted for the choice among the reported index forms

Run (from anywhere):
  python3 experiments/39_best_of_k_judge_selection_bias_validation_set/analysis/best_of_k_selection_bias.py
Smoke run into a scratch directory:
  python3 .../best_of_k_selection_bias.py --draws 200 --out-dir /tmp/exp39_smoke
"""
from __future__ import annotations

import argparse
import csv
import functools
import hashlib
import itertools
import json
import platform
import statistics
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.special import ndtri


def find_root() -> Path:
    """Repository root, found by walking up (robust to moving this folder into the archive)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / 'pyproject.toml').is_file() and (parent / 'experiments').is_dir():
            return parent
    raise RuntimeError('repository root not found')


ROOT = find_root()
EXP = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'experiments' / 'archive'
VAL = ARCHIVE / '04_veribench_validation'
LABEL_FILES = {
    'pass1': VAL / 'data' / 'ethan_human_scores_20260425.tsv',
    'pass2': VAL / 'data' / 'ethan_human_scores_ORIGINAL.tsv',
    'avg': VAL / 'data' / 'ethan_human_scores_avg_two_passes_20260425.tsv',
}
VIEWS = ('avg', 'pass1', 'pass2')
MASTER_SEED = 20260926
K_GRID = (1, 2, 4, 8, 16, 32)
SYNTH_K_GRID = (1, 2, 4, 8, 16, 32, 64)
CONTROL_PREFIXES = ('random', 'editdist')
GATE_TOLERANCE = 1e-3

# Paper Table tab:codex_configs, averaged-label human agreement (three decimals).
PAPER_CODEX_AGREEMENT = {
    'gpt-5.3-codex|P1_BASELINE': 0.466,
    'gpt-5.3-codex|P4_CHECKLIST': 0.419,
    'gpt-5.3-codex|P8_STRICT_B': 0.365,
    'gpt-5.3-codex|BAD_STRINGY': 0.435,
    'gpt-4o-mini|P8_STRICT_B': -0.014,
    'gpt-4o-mini|P4_CHECKLIST': 0.092,
    'editdist_e1': 0.199,
    'random_r1': -0.001,
}
CODEX_PANEL_DIR = VAL / 'results_exp16_final_robust_r9_median'

# Analysis D sources: the eight-configuration family panels behind the paper's Table 2.
FAMILIES = {
    'Codex': {
        'exp16': VAL / 'results_exp16_final_robust_r9_median' / 'judge_rows.csv',
        'gm': VAL / 'results_exp22_geometric_trust_index' / 'median_mono_stab_40_60' / 'summary.json',
        'tivar': {v: VAL / f'results_exp28_varaware_codex_{v}_newindex' / 'judge_trust_vector.csv' for v in VIEWS},
    },
    'Claude Opus': {
        'exp16': VAL / 'results_exp16_opus47_r3_median' / 'judge_rows.csv',
        'gm': VAL / 'results_exp22_geometric_trust_index' / 'opus47_r3_median_mono_stab_40_60_avg' / 'summary.json',
        'tivar': {v: VAL / f'results_exp28_varaware_opus_{v}_newindex' / 'judge_trust_vector.csv' for v in VIEWS},
    },
    'Qwen3-Coder': {
        'exp16': ARCHIVE / '13_qwen_replication_exp16_exp19' / 'results' / 'exp16_qwen_r3_median' / 'judge_rows.csv',
        'gm': ARCHIVE / '13_qwen_replication_exp16_exp19' / 'results' / 'exp25_geometric_qwen_r3_median_mono_stab_40_60_avg' / 'summary.json',
        'tivar': {v: VAL / f'results_exp28_varaware_qwen_{v}' / 'judge_trust_vector.csv' for v in VIEWS},
    },
}
# Paper Table tab:tivar_cross_model_results (three decimals); experiment 38 exact two-sided p.
PAPER_TABLE2 = {
    ('Codex', 'avg'): {'v1': 0.762, 'v2': 0.476, 'gm': 0.857, 'tivar': 0.833},
    ('Claude Opus', 'avg'): {'v1': 0.429, 'v2': 0.143, 'gm': 0.714, 'tivar': 0.643},
    ('Qwen3-Coder', 'avg'): {'v1': 0.524, 'v2': 0.500, 'gm': 0.786, 'tivar': 0.905},
    ('Codex', 'pass1'): {'tivar': 0.905}, ('Codex', 'pass2'): {'tivar': 0.738},
    ('Claude Opus', 'pass1'): {'tivar': 0.810}, ('Claude Opus', 'pass2'): {'tivar': 0.595},
    ('Qwen3-Coder', 'pass1'): {'tivar': 0.476}, ('Qwen3-Coder', 'pass2'): {'tivar': 0.857},
}
EXP38_DIAGNOSTICS = ROOT / 'experiments' / '38_iclr_body_rewrite_to_trust_artifact_abstract' / 'analysis' / 'results' / 'judge_level_diagnostics.csv'
FORMS = ('v1', 'v2', 'gm', 'tivar')

INPUTS: dict[str, str] = {}


# ----------------------------------------------------------------------------- I/O

def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_text(path: Path, record: bool = True) -> str:
    data = path.read_bytes()
    if record:
        INPUTS[rel(path)] = hashlib.sha256(data).hexdigest()
    return data.decode('utf-8')


def read_csv(path: Path, delimiter: str = ',', record: bool = True) -> list[dict]:
    return list(csv.DictReader(read_text(path, record).splitlines(), delimiter=delimiter))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def r6(value):
    if isinstance(value, (float, np.floating)):
        return None if not np.isfinite(value) else round(float(value), 6)
    return value


def load_labels(path: Path) -> dict[tuple[str, str], float]:
    """Same semantics as exp16 ``_load_tsv_scores``: mean of duplicate rows per key."""
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in read_csv(path, delimiter='\t'):
        gold = (row.get('gold_file') or '').strip()
        cand = (row.get('candidate_file') or '').strip()
        score = (row.get('human_score_0_5') or '').strip()
        if gold and cand and score:
            groups[(gold, cand)].append(float(score))
    return {key: sum(v) / len(v) for key, v in groups.items()}


# ----------------------------------------------------------------------------- statistics

def spearman_last_axis(x, y) -> np.ndarray:
    """Tie-aware Spearman along the last axis, broadcasting leading axes; NaN if a side is constant."""
    rx = stats.rankdata(np.asarray(x, dtype=float), method='average', axis=-1)
    ry = stats.rankdata(np.asarray(y, dtype=float), method='average', axis=-1)
    rx = rx - rx.mean(axis=-1, keepdims=True)
    ry = ry - ry.mean(axis=-1, keepdims=True)
    num = (rx * ry).sum(axis=-1)
    den = np.sqrt((rx * rx).sum(axis=-1) * (ry * ry).sum(axis=-1))
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)


def standardized_ranks(x: np.ndarray) -> np.ndarray:
    """Centered average ranks scaled to unit norm along the last axis (dot product = Spearman)."""
    r = stats.rankdata(np.asarray(x, dtype=float), method='average', axis=-1)
    r = r - r.mean(axis=-1, keepdims=True)
    return r / np.sqrt((r * r).sum(axis=-1, keepdims=True))


def block_permutation(blocks: list[np.ndarray], rng: np.random.Generator) -> np.ndarray:
    """Index array ``idx`` so that ``labels[idx]`` permutes whole problems and shuffles within them."""
    order = rng.permutation(len(blocks))
    idx = np.empty(sum(len(b) for b in blocks), dtype=int)
    for target, source in zip(blocks, order):
        src = blocks[source]
        if len(src) != len(target):
            raise ValueError('block permutation needs equal block sizes')
        idx[target] = src[rng.permutation(len(src))]
    return idx


def icc_oneway(values: np.ndarray, groups: np.ndarray) -> float:
    """One-way ICC(1) for equal group sizes; ``groups`` holds a group index per item."""
    values = np.asarray(values, dtype=float)
    labels = np.unique(groups)
    k = int(np.sum(groups == labels[0]))
    if any(int(np.sum(groups == g)) != k for g in labels):
        raise ValueError('icc_oneway needs equal group sizes')
    means = np.array([values[groups == g].mean() for g in labels])
    grand = values.mean()
    msb = k * np.sum((means - grand) ** 2) / (len(labels) - 1)
    msw = sum(np.sum((values[groups == g] - m) ** 2) for g, m in zip(labels, means)) / (len(labels) * (k - 1))
    return float((msb - msw) / (msb + (k - 1) * msw))


def icc_oneway_batched(values: np.ndarray) -> np.ndarray:
    """ICC(1) for arrays shaped (..., groups, k)."""
    k = values.shape[-1]
    g = values.shape[-2]
    means = values.mean(axis=-1)
    grand = means.mean(axis=-1, keepdims=True)
    msb = k * np.sum((means - grand) ** 2, axis=-1) / (g - 1)
    msw = np.sum((values - means[..., None]) ** 2, axis=(-1, -2)) / (g * (k - 1))
    return (msb - msw) / (msb + (k - 1) * msw)


def nested_best(values: np.ndarray, k_grid) -> dict[int, np.ndarray]:
    """Index of the largest finite value among the first K columns, for each row and K.

    Undefined (NaN) values never win; a row with no finite value among the first K gets -1.
    """
    filled = np.where(np.isfinite(values), values, -np.inf)
    out = {}
    for k in k_grid:
        best = np.argmax(filled[:, :k], axis=1)
        none = ~np.isfinite(filled[np.arange(len(filled)), best])
        out[k] = np.where(none, -1, best)
    return out


def summarize(values: np.ndarray) -> dict:
    v = np.asarray(values, dtype=float)
    finite = v[np.isfinite(v)]
    n = len(finite)
    return {
        'n': n,
        'n_undefined': int(len(v) - n),
        'mean': float(finite.mean()) if n else float('nan'),
        'mc_se': float(finite.std(ddof=1) / np.sqrt(n)) if n > 1 else float('nan'),
        'p2_5': float(np.percentile(finite, 2.5)) if n else float('nan'),
        'median': float(np.median(finite)) if n else float('nan'),
        'p95': float(np.percentile(finite, 95)) if n else float('nan'),
        'p97_5': float(np.percentile(finite, 97.5)) if n else float('nan'),
    }


# ----------------------------------------------------------------------------- pool

def canonical_items(labels: dict[str, dict]) -> list[tuple[str, str]]:
    keys = set.intersection(*[set(v) for v in labels.values()])
    return sorted(keys)


def scan_configurations(item_keys: list[str]) -> list[dict]:
    """Every (source, judge_id) whose human_eval_union rows cover exactly the analyzed items."""
    wanted = set(item_keys)
    found = []
    for path in sorted(ARCHIVE.rglob('detail_rows.csv')):
        rows = read_csv(path, record=False)
        if not rows or 'row_type' not in rows[0]:
            continue
        by_judge: dict[str, dict[str, float]] = defaultdict(dict)
        repeats: dict[str, dict[str, list]] = defaultdict(dict)
        for row in rows:
            if row['row_type'] == 'human_eval_union':
                by_judge[row['judge_id']][row['item_key']] = float(row['score_mean'])
                repeats[row['judge_id']][row['item_key']] = json.loads(row['repeat_scores'])
        for judge_id, scores in sorted(by_judge.items()):
            if set(scores) != wanted:
                continue
            found.append({'source': path.parent, 'detail_path': path, 'judge_id': judge_id,
                          'scores': np.array([scores[k] for k in item_keys], dtype=float),
                          'repeats': [repeats[judge_id][k] for k in item_keys]})
    return found


# Historical runners aggregated repeats with one of these; with ``mean`` the float summation
# order can split mathematically equal means, which the recorded six-decimal scores keep tied.
HISTORICAL_AGGREGATORS = {
    'statistics.mean': lambda reps: statistics.mean(reps),
    'numpy.mean': lambda reps: float(np.mean(reps)),
    'numpy.median': lambda reps: float(np.median(reps)),
}
# The averaged-label file before commit 9e893c4 (used by results_exp16_multi_judge_human_sets).
OLD_AVG_LABELS = ('c73507a', 'experiments/04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv')


@functools.lru_cache(maxsize=1)
def old_avg_labels() -> dict | None:
    """Averaged labels before commit 9e893c4, read from git history; None if not in this clone."""
    try:
        text = subprocess.run(['git', 'show', f'{OLD_AVG_LABELS[0]}:{OLD_AVG_LABELS[1]}'], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in csv.DictReader(text.splitlines(), delimiter='\t'):
        if row.get('gold_file') and row.get('candidate_file') and row.get('human_score_0_5'):
            groups[(row['gold_file'].strip(), row['candidate_file'].strip())].append(float(row['human_score_0_5']))
    return {key: sum(v) / len(v) for key, v in groups.items()}


def explain_deviation(cfg: dict, labels_by_view: dict, items: list, frozen: dict) -> str:
    """Classify a gate deviation.

    'float_tie(<agg>)': the frozen values reproduce within 1e-6 when the aggregated score is recomputed
    from the repeat scores with a historical aggregator. 'older_avg_label_file[...]': the pass views
    reproduce and the averaged view reproduces with the pre-9e893c4 averaged-label file (recorded scores
    within the gate tolerance, or a historical aggregator within 1e-6). Anything else is 'unexplained'.
    """
    rebuilt = {name: np.array([agg(r) for r in cfg['repeats']]) for name, agg in HISTORICAL_AGGREGATORS.items()}
    for name, x in rebuilt.items():
        if all(abs(float(spearman_last_axis(x, labels_by_view[v])) - frozen[v]) <= 1e-6 for v in VIEWS):
            return f'float_tie({name})'
    old = old_avg_labels()
    if old is None:
        return 'unexplained(older avg file not in this clone)'
    old_vec = np.array([old[it] for it in items])
    for name, x, tol in [('recorded', cfg['scores'], GATE_TOLERANCE)] + [(n, x, 1e-6) for n, x in rebuilt.items()]:
        views_ok = all(abs(float(spearman_last_axis(x, labels_by_view[v])) - frozen[v]) <= tol for v in ('pass1', 'pass2'))
        if views_ok and abs(float(spearman_last_axis(x, old_vec)) - frozen['avg']) <= tol:
            return 'older_avg_label_file' if name == 'recorded' else f'older_avg_label_file+float_tie({name})'
    return 'unexplained'


def attach_frozen_rows(configs: list[dict]) -> None:
    cache: dict[Path, dict[str, dict]] = {}
    for cfg in configs:
        path = cfg['source'] / 'judge_rows.csv'
        if path not in cache:
            cache[path] = {r['judge_id']: r for r in read_csv(path, record=False)}
        row = cache[path].get(cfg['judge_id'])
        if row is None:
            raise RuntimeError(f'no judge_rows entry for {cfg["judge_id"]} in {rel(path)}')
        cfg['frozen'] = row


def build_pool(configs: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply the protocol's pool rule. Returns (kept representatives, manifest rows for all configs)."""
    kept: list[dict] = []
    seen: dict[tuple, dict] = {}
    manifest = []
    for cfg in sorted(configs, key=lambda c: (rel(c['source']), c['judge_id'])):
        status = 'kept'
        if cfg['judge_id'].startswith(CONTROL_PREFIXES):
            status = 'control_excluded'
        elif np.ptp(cfg['scores']) == 0:
            status = 'constant_excluded'
        else:
            key = tuple(np.round(cfg['scores'], 6))
            if key in seen:
                status = 'duplicate_of:' + seen[key]['config_id']
                seen[key]['aliases'].append(f'{rel(cfg["source"])}::{cfg["judge_id"]}')
            else:
                cfg['config_id'] = f'C{len(kept) + 1:03d}'
                cfg['aliases'] = []
                seen[key] = cfg
                kept.append(cfg)
        cfg['status'] = status
        manifest.append(cfg)
    return kept, manifest


# ----------------------------------------------------------------------------- analyses A and B

def analysis_a(pool_scores, labels_by_view, blocks, rng, draws, k_grid) -> list[dict]:
    n_pool = pool_scores.shape[0]
    z_pool = standardized_ranks(pool_scores)                       # (N, n)
    rows = []
    for view in VIEWS:
        z_label = standardized_ranks(labels_by_view[view])         # (n,)
        perms = np.stack([block_permutation(blocks, rng) for _ in range(draws)])
        rho = z_label[perms] @ z_pool.T                            # (draws, N)
        order = np.argsort(rng.random((draws, n_pool)), axis=1)
        running = np.maximum.accumulate(np.take_along_axis(rho, order, axis=1), axis=1)
        for k in k_grid:
            s = summarize(running[:, k - 1])
            rows.append({'view': view, 'K': k, 'draws': draws, **{key: r6(v) for key, v in s.items()}})
    return rows


def analysis_b(pool_scores, cert, labels_by_view, blocks, rng, draws, k_grid) -> tuple[list[dict], dict]:
    n_pool = pool_scores.shape[0]
    n_problems = len(blocks)
    half = n_problems // 2
    rows = []
    raw = {}
    for view in VIEWS:
        y = labels_by_view[view]
        splits = np.stack([rng.permutation(n_problems) for _ in range(draws)])
        idx_s = np.stack([np.concatenate([blocks[p] for p in np.sort(s[:half])]) for s in splits])
        idx_h = np.stack([np.concatenate([blocks[p] for p in np.sort(s[half:])]) for s in splits])
        rho_s = spearman_last_axis(pool_scores[:, idx_s].transpose(1, 0, 2), y[idx_s][:, None, :])  # (draws, N)
        rho_h = spearman_last_axis(pool_scores[:, idx_h].transpose(1, 0, 2), y[idx_h][:, None, :])
        order = np.argsort(rng.random((draws, n_pool)), axis=1)
        rs = np.take_along_axis(rho_s, order, axis=1)
        rh = np.take_along_axis(rho_h, order, axis=1)
        cert_o = cert[order] + rng.random((draws, n_pool)) * 1e-12  # uniform tie-breaking
        best_label = nested_best(rs, k_grid)
        best_oracle = nested_best(rh, k_grid)
        best_prop = nested_best(cert_o, k_grid)
        view_raw = {}
        for k in k_grid:
            picks = {
                'label': best_label[k],
                'random': rng.integers(0, k, size=draws),
                'property': best_prop[k],
                'oracle': best_oracle[k],
            }
            for rule, pick in picks.items():
                ok = pick >= 0
                sel = np.full(draws, np.nan)
                held = np.full(draws, np.nan)
                sel[ok] = rs[np.arange(draws)[ok], pick[ok]]
                held[ok] = rh[np.arange(draws)[ok], pick[ok]]
                optimism = sel - held
                s_opt = summarize(optimism)
                rows.append({
                    'view': view, 'K': k, 'rule': rule, 'replicates': draws,
                    'mean_selection_rho': r6(np.nanmean(sel)), 'mean_heldout_rho': r6(np.nanmean(held)),
                    'mean_optimism': r6(s_opt['mean']), 'mc_se_optimism': r6(s_opt['mc_se']),
                    'optimism_p2_5': r6(s_opt['p2_5']), 'optimism_median': r6(s_opt['median']),
                    'optimism_p97_5': r6(s_opt['p97_5']), 'n_undefined': s_opt['n_undefined'],
                })
                view_raw[(k, rule)] = optimism
        raw[view] = view_raw
    return rows, raw


# ----------------------------------------------------------------------------- analysis C

def cut_points(observed: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Normal thresholds reproducing the empirical marginal of ``observed`` for a N(0,1) latent."""
    levels, counts = np.unique(observed, return_counts=True)
    cdf = np.cumsum(counts)[:-1] / counts.sum()
    return ndtri(cdf), levels


def discretize(latent: np.ndarray, cuts: np.ndarray, levels: np.ndarray) -> np.ndarray:
    return levels[np.searchsorted(cuts, latent)]


def simulate_labels(q, r, e1, e2, cuts1, cuts2):
    y1 = discretize(np.sqrt(r) * q + np.sqrt(1 - r) * e1, *cuts1)
    y2 = discretize(np.sqrt(r) * q + np.sqrt(1 - r) * e2, *cuts2)
    return y1, y2, (y1 + y2) / 2.0


def label_statistics(y1: np.ndarray, y2: np.ndarray) -> dict:
    """Label-structure statistics for arrays shaped (problems, 3)."""
    avg = (y1 + y2) / 2.0
    d1 = y1 - y1.mean(axis=-1, keepdims=True)
    d2 = y2 - y2.mean(axis=-1, keepdims=True)
    return {
        'interpass_spearman': float(spearman_last_axis(y1.ravel(), y2.ravel())),
        'icc_avg': float(icc_oneway_batched(avg)),
        'within_problem_interpass_pearson': float(np.corrcoef(d1.ravel(), d2.ravel())[0, 1]),
        'problem_mean_interpass_pearson': float(np.corrcoef(y1.mean(axis=-1), y2.mean(axis=-1))[0, 1]),
    }


FIT_TARGETS = ('interpass_spearman', 'icc_avg', 'within_problem_interpass_pearson')


def calibrate(labels_by_view, groups, pool_scores, rng, big_problems=20_000) -> dict:
    """Calibrate the synthetic label and judge models to the panel (see PROTOCOL.md, analysis C).

    ``prereg``: the pre-registered model (item-level label noise, kappa = 0): r from the inter-pass
    Spearman, then tau from the averaged-label ICC. ``extended`` (Deviation 2): label noise with a
    problem-level share kappa; (r, tau, kappa) fitted jointly to the two pre-registered targets plus
    the within-problem inter-pass correlation, coarse grid then a local fine grid.
    """
    if not np.all(np.diff(groups) >= 0):
        raise ValueError('items must be sorted by problem')
    n_problems = len(np.unique(groups))
    cuts1 = cut_points(labels_by_view['pass1'])
    cuts2 = cut_points(labels_by_view['pass2'])
    observed = label_statistics(labels_by_view['pass1'].reshape(n_problems, 3), labels_by_view['pass2'].reshape(n_problems, 3))

    a = rng.standard_normal((big_problems, 1))
    e = rng.standard_normal((big_problems, 3))
    b1, b2 = rng.standard_normal((big_problems, 1)), rng.standard_normal((big_problems, 1))
    h1, h2 = rng.standard_normal((big_problems, 3)), rng.standard_normal((big_problems, 3))

    def stats_at(r, tau, kappa):
        q = np.sqrt(tau) * a + np.sqrt(1 - tau) * e
        n1 = np.sqrt(kappa) * b1 + np.sqrt(1 - kappa) * h1
        n2 = np.sqrt(kappa) * b2 + np.sqrt(1 - kappa) * h2
        y1, y2, _ = simulate_labels(q, r, n1, n2, cuts1, cuts2)
        return label_statistics(y1, y2)

    # Pre-registered sequential fit (kappa = 0).
    r_grid = np.round(np.arange(0.0, 0.951, 0.005), 3)
    interpass = np.array([stats_at(r, 0.0, 0.0)['interpass_spearman'] for r in r_grid])
    r_pre = float(r_grid[np.argmin(np.abs(interpass - observed['interpass_spearman']))])
    tau_grid = np.round(np.arange(0.0, 0.951, 0.01), 3)
    icc_pre = np.array([stats_at(r_pre, t, 0.0)['icc_avg'] for t in tau_grid])
    tau_pre = float(tau_grid[np.argmin(np.abs(icc_pre - observed['icc_avg']))])
    prereg = {'r': r_pre, 'tau': tau_pre, 'kappa': 0.0, 'simulated': stats_at(r_pre, tau_pre, 0.0),
              'tau_at_grid_boundary': bool(tau_pre >= tau_grid[-1])}

    # Extended joint fit.
    def loss(s):
        return sum((s[t] - observed[t]) ** 2 for t in FIT_TARGETS)

    coarse = np.round(np.arange(0.05, 0.951, 0.05), 3)
    best = min(((loss(stats_at(r, t, k)), r, t, k) for r in coarse for t in coarse for k in np.concatenate([[0.0], coarse])),
               key=lambda z: z[0])
    fine = lambda c: np.round(np.clip(np.arange(c - 0.05, c + 0.0501, 0.01), 0.0, 0.99), 3)
    best = min(((loss(stats_at(r, t, k)), r, t, k) for r in fine(best[1]) for t in fine(best[2]) for k in fine(best[3])),
               key=lambda z: z[0])
    _, r_ext, tau_ext, kappa_ext = best
    extended = {'r': float(r_ext), 'tau': float(tau_ext), 'kappa': float(kappa_ext),
                'simulated': stats_at(r_ext, tau_ext, kappa_ext), 'fit_loss': float(best[0])}

    # Judge-side parameters from the real pool.
    icc_judges = icc_oneway_batched(pool_scores.reshape(pool_scores.shape[0], n_problems, -1))
    pair = spearman_last_axis(pool_scores[:, None, :], pool_scores[None, :, :])
    off = pair[~np.eye(len(pool_scores), dtype=bool)]

    # Fresh-data agreement (population Spearman with the averaged label) as a function of beta.
    # It depends on r and the label marginals only: clustering changes sampling variance, not the population value.
    big = 3 * big_problems
    q = rng.standard_normal(big)
    f1, f2, noise = rng.standard_normal(big), rng.standard_normal(big), rng.standard_normal(big)
    beta_grid = np.round(np.arange(0.0, 0.991, 0.01), 3)
    for model in (prereg, extended):
        avg_big = simulate_labels(q, model['r'], f1, f2, cuts1, cuts2)[2]
        fresh = np.array([float(spearman_last_axis(bb * q + np.sqrt(1 - bb * bb) * noise, avg_big)) for bb in beta_grid])
        model['beta_grid'] = beta_grid.tolist()
        model['fresh_agreement'] = [round(float(v), 6) for v in np.maximum.accumulate(fresh)]
        model['fresh_agreement_at_beta_0_99'] = float(fresh[-1])

    return {
        'observed': observed, 'fit_targets': list(FIT_TARGETS),
        'label_models': {'prereg': prereg, 'extended': extended},
        'tau_s_median_judge_icc': float(np.median(icc_judges)),
        'judge_icc_min': float(icc_judges.min()), 'judge_icc_max': float(icc_judges.max()),
        'c_pool_median_pairwise_spearman': float(np.median(off)),
        'cuts_pass1': [cuts1[0].tolist(), cuts1[1].tolist()], 'cuts_pass2': [cuts2[0].tolist(), cuts2[1].tolist()],
        'n_big_problems': big_problems,
    }


def beta_for(fresh_target: np.ndarray, model: dict) -> np.ndarray:
    fresh = np.asarray(model['fresh_agreement'])
    beta = np.asarray(model['beta_grid'])
    if np.any(fresh_target > fresh[-1]):
        raise ValueError('target agreement exceeds what the calibrated labels allow')
    return np.interp(fresh_target, fresh, beta)


def clustered_noise(rng, shape_lead, n_problems, tau_s):
    """Unit-variance noise with problem intraclass correlation tau_s; shape (*lead, P, 3)."""
    prob = rng.standard_normal((*shape_lead, n_problems, 1))
    item = rng.standard_normal((*shape_lead, n_problems, 3))
    return np.sqrt(tau_s) * prob + np.sqrt(1 - tau_s) * item


def analysis_c(calib, rng, draws, n_problems_list=(24, 12), k_grid=SYNTH_K_GRID, chunk=500) -> list[dict]:
    cuts1 = (np.array(calib['cuts_pass1'][0]), np.array(calib['cuts_pass1'][1]))
    cuts2 = (np.array(calib['cuts_pass2'][0]), np.array(calib['cuts_pass2'][1]))
    tau_s, c_pool = calib['tau_s_median_judge_icc'], calib['c_pool_median_pairwise_spearman']
    k_max = max(k_grid)
    settings = {
        'null-indep': {'fresh': 'zero', 'c': 0.0},
        'null-shared': {'fresh': 'zero', 'c': c_pool},
        'weak-equal': {'fresh': 'equal', 'c': 0.0},
        'weak-hetero': {'fresh': 'uniform', 'c': 0.0},
    }
    rows = []
    for label_model in ('extended', 'prereg'):
        model = calib['label_models'][label_model]
        r, tau, kappa = model['r'], model['tau'], model['kappa']
        for name, spec in settings.items():
            for n_problems in n_problems_list:
                panel_w = {k: [] for k in k_grid}
                fresh_w = {k: [] for k in k_grid}
                done = 0
                while done < draws:
                    m = min(chunk, draws - done)
                    a = rng.standard_normal((m, n_problems, 1))
                    e = rng.standard_normal((m, n_problems, 3))
                    q = np.sqrt(tau) * a + np.sqrt(1 - tau) * e                       # (m, P, 3)
                    n1 = clustered_noise(rng, (m,), n_problems, kappa)                 # rater noise, pass 1
                    n2 = clustered_noise(rng, (m,), n_problems, kappa)                 # rater noise, pass 2
                    _, _, avg = simulate_labels(q, r, n1, n2, cuts1, cuts2)
                    if spec['fresh'] == 'zero':
                        fresh = np.zeros((m, k_max))
                    elif spec['fresh'] == 'equal':
                        fresh = np.full((m, k_max), 0.30)
                    else:
                        fresh = rng.uniform(0.0, 0.45, size=(m, k_max))
                    beta = beta_for(fresh, model)                                      # (m, K)
                    shared = clustered_noise(rng, (m, 1), n_problems, tau_s)           # (m, 1, P, 3)
                    own = clustered_noise(rng, (m, k_max), n_problems, tau_s)          # (m, K, P, 3)
                    noise = np.sqrt(spec['c']) * shared + np.sqrt(1 - spec['c']) * own
                    b = beta[:, :, None, None]
                    s = b * q[:, None] + np.sqrt(1 - b * b) * noise
                    rho = spearman_last_axis(s.reshape(m, k_max, -1), avg.reshape(m, 1, -1))  # (m, K)
                    best = nested_best(rho, k_grid)
                    for k in k_grid:
                        w = best[k]
                        panel_w[k].append(rho[np.arange(m), w])
                        fresh_w[k].append(fresh[np.arange(m), w])
                    done += m
                for k in k_grid:
                    panel = np.concatenate(panel_w[k])
                    fr = np.concatenate(fresh_w[k])
                    s_inf = summarize(panel - fr)
                    rows.append({'label_model': label_model, 'setting': name, 'n_problems': n_problems,
                                 'n_items': 3 * n_problems, 'K': k, 'replicates': draws,
                                 'mean_winner_panel_rho': r6(panel.mean()), 'mean_winner_fresh_rho': r6(fr.mean()),
                                 'mean_inflation': r6(s_inf['mean']), 'mc_se_inflation': r6(s_inf['mc_se']),
                                 'inflation_p2_5': r6(s_inf['p2_5']), 'inflation_p97_5': r6(s_inf['p97_5'])})
    return rows


# ----------------------------------------------------------------------------- analysis D

def load_family(name: str, spec: dict) -> dict:
    exp16 = {r['judge_id']: r for r in read_csv(spec['exp16'])}
    gm_rows = {r['judge_id']: r for r in json.loads(read_text(spec['gm']))['rows']}
    tivar = {v: {r['judge_id']: r for r in read_csv(p)} for v, p in spec['tivar'].items()}
    ids = [r for r in tivar['avg']]
    for v in VIEWS:
        if sorted(tivar[v]) != sorted(ids):
            raise RuntimeError(f'{name}: TI_var judge sets differ across views')
        for j in ids:
            if abs(float(tivar[v][j]['TI_variance_aware']) - float(tivar['avg'][j]['TI_variance_aware'])) > 1e-12:
                raise RuntimeError(f'{name}: TI_var differs across label views for {j}')
    if sorted(exp16) != sorted(ids) or sorted(gm_rows) != sorted(ids):
        raise RuntimeError(f'{name}: judge sets differ across sources')
    forms = {
        'v1': np.array([float(exp16[j]['cert_index']) for j in ids]),
        'v2': np.array([float(exp16[j]['cert_index_v2']) for j in ids]),
        'gm': np.array([float(gm_rows[j]['geo_trust_index']) for j in ids]),
        'tivar': np.array([float(tivar['avg'][j]['TI_variance_aware']) for j in ids]),
    }
    targets = {}
    for v in VIEWS:
        y16 = np.array([float(exp16[j][f'human_spearman_r_{v}']) for j in ids])
        y28 = np.array([float(tivar[v][j]['human_spearman']) for j in ids])
        if not np.allclose(y16, y28, atol=1e-9):
            raise RuntimeError(f'{name} {v}: exp16 and exp28 human agreement differ')
        targets[v] = y16
    return {'ids': ids, 'forms': forms, 'targets': targets}


def exact_permutation_table(forms: dict, target: np.ndarray) -> dict:
    n = len(target)
    zf = {f: standardized_ranks(x) for f, x in forms.items()}
    zt = standardized_ranks(target)
    perms = np.array(list(itertools.permutations(range(n))), dtype=np.int16)   # (n!, n)
    zt_perm = zt[perms]                                                         # (n!, n)
    stat = {f: zt_perm @ z for f, z in zf.items()}                              # permuted Spearman per form
    obs = {f: float(zf[f] @ zt) for f in forms}
    eps = 1e-12
    mx = np.max(np.stack([stat[f] for f in forms]), axis=0)
    mx_abs = np.max(np.stack([np.abs(stat[f]) for f in forms]), axis=0)
    best_form = max(obs, key=lambda f: obs[f])
    return {
        'n_permutations': len(perms), 'observed': obs,
        'p_tivar_one_sided': float(np.mean(stat['tivar'] >= obs['tivar'] - eps)),
        'p_tivar_two_sided': float(np.mean(np.abs(stat['tivar']) >= abs(obs['tivar']) - eps)),
        'p_tivar_adjusted_one_sided': float(np.mean(mx >= obs['tivar'] - eps)),
        'p_tivar_adjusted_two_sided': float(np.mean(mx_abs >= abs(obs['tivar']) - eps)),
        'best_form': best_form,
        'p_best_adjusted_one_sided': float(np.mean(mx >= obs[best_form] - eps)),
    }


def analysis_d() -> tuple[list[dict], dict]:
    exp38 = {(r['family'], r['view']): r for r in read_csv(EXP38_DIAGNOSTICS)}
    rows, gate = [], {'table2_mismatches': [], 'exp38_mismatches': []}
    for name, spec in FAMILIES.items():
        fam = load_family(name, spec)
        for view in VIEWS:
            res = exact_permutation_table(fam['forms'], fam['targets'][view])
            for form, expected in PAPER_TABLE2.get((name, view), {}).items():
                if round(res['observed'][form], 3) != expected:
                    gate['table2_mismatches'].append([name, view, form, res['observed'][form], expected])
            ref = exp38[(name, view)]
            if abs(res['p_tivar_two_sided'] - float(ref['perm_p_exact'])) > 1e-6 or abs(res['observed']['tivar'] - float(ref['rho_ti'])) > 1e-6:
                gate['exp38_mismatches'].append([name, view, res['p_tivar_two_sided'], float(ref['perm_p_exact'])])
            rows.append({'family': name, 'view': view, 'n_configurations': len(fam['ids']),
                         **{f'rho_{f}': r6(res['observed'][f]) for f in FORMS},
                         'p_tivar_one_sided': r6(res['p_tivar_one_sided']),
                         'p_tivar_adjusted_one_sided': r6(res['p_tivar_adjusted_one_sided']),
                         'p_tivar_two_sided': r6(res['p_tivar_two_sided']),
                         'p_tivar_adjusted_two_sided': r6(res['p_tivar_adjusted_two_sided']),
                         'best_observed_form': res['best_form'],
                         'p_best_form_adjusted_one_sided': r6(res['p_best_adjusted_one_sided']),
                         'n_permutations': res['n_permutations']})
    gate['passed'] = not gate['table2_mismatches'] and not gate['exp38_mismatches']
    return rows, gate


# ----------------------------------------------------------------------------- main

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--draws', type=int, default=4000, help='Monte Carlo draws per cell (protocol: 4000)')
    parser.add_argument('--out-dir', type=Path, default=EXP, help='writes results/ and figures/ under this directory')
    parser.add_argument('--pool-only', action='store_true', help='build the pool and run the reproduction gate only')
    args = parser.parse_args(argv)
    started = time.time()
    out_results = args.out_dir / 'results'
    out_figures = args.out_dir / 'figures'
    out_results.mkdir(parents=True, exist_ok=True)
    out_figures.mkdir(parents=True, exist_ok=True)

    seeds = np.random.SeedSequence(MASTER_SEED).spawn(4)
    rng_a, rng_b, rng_c, _rng_d = (np.random.default_rng(s) for s in seeds)

    # Labels and items.
    labels_raw = {view: load_labels(path) for view, path in LABEL_FILES.items()}
    items_all = canonical_items(labels_raw)
    # The analyzed items are the label keys that the judges actually scored (missing gold excluded).
    scored = scan_scored_keys()
    items = [it for it in items_all if f'{it[0]}::{it[1]}' in scored]
    item_keys = [f'{g}::{c}' for g, c in items]
    problems = [Path(g).stem for g, _ in items]
    uniq = sorted(set(problems))
    groups = np.array([uniq.index(p) for p in problems])
    sizes = np.bincount(groups)
    if len(items) != 72 or len(uniq) != 24 or set(sizes) != {3}:
        raise SystemExit(f'item structure gate failed: {len(items)} items, {len(uniq)} problems, sizes {sorted(set(sizes))}')
    blocks = [np.where(groups == g)[0] for g in range(len(uniq))]
    labels_by_view = {v: np.array([labels_raw[v][it] for it in items], dtype=float) for v in VIEWS}

    # Pool and reproduction gate.
    configs = scan_configurations(item_keys)
    attach_frozen_rows(configs)
    pool, manifest = build_pool(configs)
    for cfg in manifest:
        INPUTS[rel(cfg['detail_path'])] = hashlib.sha256(cfg['detail_path'].read_bytes()).hexdigest()
        jr = cfg['source'] / 'judge_rows.csv'
        INPUTS[rel(jr)] = hashlib.sha256(jr.read_bytes()).hexdigest()
    manifest_rows = []
    for cfg in manifest:
        frozen = {v: float(cfg['frozen'][f'human_spearman_r_{v}']) for v in VIEWS}
        if cfg['status'] == 'constant_excluded':
            cfg['rho'] = {v: float('nan') for v in VIEWS}
            cfg['deviation'], cfg['explanation'] = float('nan'), 'not_checked(constant scores)'
        else:
            cfg['rho'] = {v: float(spearman_last_axis(cfg['scores'], labels_by_view[v])) for v in VIEWS}
            cfg['deviation'] = max(abs(cfg['rho'][v] - frozen[v]) for v in VIEWS)
            cfg['explanation'] = ('within_tolerance' if cfg['deviation'] <= GATE_TOLERANCE
                                  else explain_deviation(cfg, labels_by_view, items, frozen))
        manifest_rows.append({
            'config_id': cfg.get('config_id', ''), 'status': cfg['status'], 'source': rel(cfg['source']),
            'judge_id': cfg['judge_id'], 'cert_index': r6(float(cfg['frozen']['cert_index'])),
            **{f'rho_{v}': r6(cfg['rho'][v]) for v in VIEWS}, **{f'frozen_rho_{v}': r6(frozen[v]) for v in VIEWS},
            'max_abs_deviation': r6(cfg['deviation']), 'gate_explanation': cfg['explanation'],
            'aliases': ';'.join(cfg.get('aliases', [])),
        })
    paper_checks = []
    for cfg in manifest:
        if cfg['source'].resolve() == CODEX_PANEL_DIR.resolve() and cfg['judge_id'] in PAPER_CODEX_AGREEMENT:
            paper_checks.append({'judge_id': cfg['judge_id'], 'recomputed': round(cfg['rho']['avg'], 3),
                                 'paper': PAPER_CODEX_AGREEMENT[cfg['judge_id']]})
    checked = [c for c in manifest if np.isfinite(c['deviation'])]
    kept_over = [c for c in pool if c['deviation'] > GATE_TOLERANCE]

    def tally(cfgs):
        counts: dict[str, int] = defaultdict(int)
        for c in cfgs:
            counts[c['explanation']] += 1
        return dict(sorted(counts.items()))

    gate = {
        'scope': 'protocol: kept configurations; all scanned configurations are also checked and reported',
        'tolerance': GATE_TOLERANCE,
        'n_configurations_scanned': len(manifest), 'n_checked': len(checked), 'n_kept': len(pool),
        'kept_max_abs_deviation': max(c['deviation'] for c in pool),
        'kept_n_over_tolerance': len(kept_over), 'kept_explanations': tally(pool),
        'all_max_abs_deviation': max(c['deviation'] for c in checked),
        'all_n_over_tolerance': int(sum(c['deviation'] > GATE_TOLERANCE for c in checked)),
        'all_explanations': tally(checked),
        'paper_codex_checks': paper_checks,
        'paper_codex_all_match': len(paper_checks) == len(PAPER_CODEX_AGREEMENT) and all(c['recomputed'] == c['paper'] for c in paper_checks),
        'amendment': 'PROTOCOL.md Deviation 1: a kept configuration over tolerance passes only when its frozen values '
                     'reproduce within 1e-6 from repeat scores (float_tie); any unexplained deviation fails the gate',
    }
    gate['passed'] = (gate['paper_codex_all_match']
                      and all(c['explanation'].startswith('float_tie') for c in kept_over)
                      and not any(c['explanation'].startswith('unexplained') for c in checked))
    write_csv(out_results / 'pool_manifest.csv', manifest_rows)
    (out_results / 'reproduction_gate.json').write_text(json.dumps(gate, indent=2) + '\n')
    status_counts = defaultdict(int)
    for cfg in manifest:
        status_counts[cfg['status'].split(':')[0]] += 1
    print(f'pool: {len(pool)} kept of {len(manifest)} scanned {dict(status_counts)}; gate passed={gate["passed"]} '
          f'kept max_dev={gate["kept_max_abs_deviation"]:.2e} explanations={gate["all_explanations"]}')
    if not gate['passed']:
        print(json.dumps(gate, indent=2))
        raise SystemExit('reproduction gate failed; stopping per protocol')
    if args.pool_only:
        return 0

    pool_scores = np.stack([cfg['scores'] for cfg in pool])
    cert = np.array([float(cfg['frozen']['cert_index']) for cfg in pool])
    n_pool = len(pool)
    k_grid = tuple(k for k in K_GRID if k < n_pool) + (n_pool,)

    t0 = time.time()
    rows_a = analysis_a(pool_scores, labels_by_view, blocks, rng_a, args.draws, k_grid)
    write_csv(out_results / 'A_null_best_of_k.csv', rows_a)
    print(f'A done in {time.time() - t0:.1f}s')

    t0 = time.time()
    rows_b, _raw_b = analysis_b(pool_scores, cert, labels_by_view, blocks, rng_b, args.draws, k_grid)
    write_csv(out_results / 'B_split_half_selection.csv', rows_b)
    broken =[r for r in rows_b if r['rule'] == 'random' and abs(r['mean_optimism']) > 3 * r['mc_se_optimism']]
    print(f'B done in {time.time() - t0:.1f}s; random-rule checks outside 3 SE: {len(broken)}')
    if broken:
        raise SystemExit('random-rule optimism is not centered at zero; split machinery treated as broken (protocol rule 2)')

    t0 = time.time()
    calib = calibrate(labels_by_view, groups, pool_scores, rng_c)
    (out_results / 'C_calibration.json').write_text(json.dumps(calib, indent=2) + '\n')
    rows_c = analysis_c(calib, rng_c, args.draws)
    write_csv(out_results / 'C_synthetic_best_of_k.csv', rows_c)
    models = calib['label_models']
    print(f'C done in {time.time() - t0:.1f}s; extended r={models["extended"]["r"]} tau={models["extended"]["tau"]} '
          f'kappa={models["extended"]["kappa"]}; prereg r={models["prereg"]["r"]} tau={models["prereg"]["tau"]}; '
          f'tau_s={calib["tau_s_median_judge_icc"]:.3f} c={calib["c_pool_median_pairwise_spearman"]:.3f}')

    t0 = time.time()
    rows_d, gate_d = analysis_d()
    write_csv(out_results / 'D_judge_level_adjusted.csv', rows_d)
    print(f'D done in {time.time() - t0:.1f}s; gate passed={gate_d["passed"]}')
    if not gate_d['passed']:
        print(json.dumps(gate_d, indent=2))
        raise SystemExit('analysis D reproduction gate failed; stopping per protocol')

    summary = {
        'experiment': '39_best_of_k_judge_selection_bias_validation_set',
        'protocol': 'PROTOCOL.md (frozen 09-26-2026 16:56 PDT, commit 7548c3a)',
        'master_seed': MASTER_SEED, 'draws_per_cell': args.draws,
        'n_items': len(items), 'n_problems': len(uniq), 'pool_size': n_pool, 'k_grid_real': list(k_grid),
        'k_grid_synthetic': list(SYNTH_K_GRID),
        'reproduction_gate': gate, 'judge_level_gate': gate_d,
        'calibration': {**{k: v for k, v in calib.items() if k != 'label_models'},
                        'label_models': {name: {k: v for k, v in model.items() if k not in ('beta_grid', 'fresh_agreement')}
                                         for name, model in calib['label_models'].items()}},
        'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': __import__('scipy').__version__},
        'inputs_sha256': dict(sorted(INPUTS.items())), 'runtime_seconds': round(time.time() - started, 1),
    }
    (out_results / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(f'all analyses done in {time.time() - started:.1f}s')
    return 0


def scan_scored_keys() -> set[str]:
    """Item keys scored in the Codex panel (the paper's analyzed pairs)."""
    rows = read_csv(CODEX_PANEL_DIR / 'detail_rows.csv', record=False)
    return {r['item_key'] for r in rows if r['row_type'] == 'human_eval_union'}


if __name__ == '__main__':
    raise SystemExit(main())
