#!/usr/bin/env python3
"""Deterministic judge-level diagnostics from the committed fixed-index vectors (no inference).

For each family x label view, read `judge_trust_vector.csv` (columns judge_id, human_spearman,
C_f_mean, TI_variance_aware) and compute: the frozen n=8 Spearman association, its exact
permutation probability over all 8! orderings (two-sided, |rho| >= |observed|), the association of
the bug-monotonicity component C_f alone, the association after removing the two non-LLM controls
(edit distance, random; n=6), and the association among the four same-model prompts (n=4).
Ties get average ranks. Output: results/judge_level_diagnostics.csv and .json with input hashes.
"""
import csv, hashlib, itertools, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
B = ROOT / 'experiments/archive/04_veribench_validation'
INPUTS = {
    ('Codex', 'avg'): B / 'results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv',
    ('Codex', 'pass1'): B / 'results_exp28_varaware_codex_pass1_newindex/judge_trust_vector.csv',
    ('Codex', 'pass2'): B / 'results_exp28_varaware_codex_pass2_newindex/judge_trust_vector.csv',
    ('Claude Opus', 'avg'): B / 'results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv',
    ('Claude Opus', 'pass1'): B / 'results_exp28_varaware_opus_pass1_newindex/judge_trust_vector.csv',
    ('Claude Opus', 'pass2'): B / 'results_exp28_varaware_opus_pass2_newindex/judge_trust_vector.csv',
    ('Qwen3-Coder', 'avg'): B / 'results_exp28_varaware_qwen_avg/judge_trust_vector.csv',
    ('Qwen3-Coder', 'pass1'): B / 'results_exp28_varaware_qwen_pass1/judge_trust_vector.csv',
    ('Qwen3-Coder', 'pass2'): B / 'results_exp28_varaware_qwen_pass2/judge_trust_vector.csv',
}

def rank(v):
    idx = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]: j += 1
        for k in range(i, j + 1): r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r

def pearson(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return float('nan') if sa == 0 or sb == 0 else sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

def spearman(a, b): return pearson(rank(a), rank(b))

def perm_p(a, b):
    obs = spearman(a, b); ra = rank(a); rb = rank(b); cnt = tot = 0
    for p in itertools.permutations(range(len(b))):
        tot += 1
        if abs(pearson(ra, [rb[i] for i in p])) >= abs(obs) - 1e-12: cnt += 1
    return cnt / tot

def main():
    out = []; hashes = {}
    for (fam, view), path in INPUTS.items():
        data = path.read_bytes(); hashes[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
        rows = list(csv.DictReader(data.decode().splitlines()))
        ids = [r['judge_id'] for r in rows]
        y = [float(r['human_spearman']) for r in rows]
        ti = [float(r['TI_variance_aware']) for r in rows]
        cf = [float(r['C_f_mean']) for r in rows]
        keep6 = [i for i, j in enumerate(ids) if not j.startswith(('editdist', 'random'))]
        keep4 = [i for i in keep6 if 'gpt-4o-mini' not in ids[i]]
        sub = lambda v, k: [v[i] for i in k]
        out.append(dict(family=fam, view=view, n=len(ids), rho_ti=round(spearman(ti, y), 6),
                        perm_p_exact=round(perm_p(ti, y), 6), rho_cf=round(spearman(cf, y), 6),
                        n_no_controls=len(keep6), rho_no_controls=round(spearman(sub(ti, keep6), sub(y, keep6)), 6),
                        n_same_model=len(keep4), rho_same_model=round(spearman(sub(ti, keep4), sub(y, keep4)), 6),
                        judges_same_model='|'.join(sub(ids, keep4))))
    res = Path(__file__).resolve().parent / 'results'
    with open(res / 'judge_level_diagnostics.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    (res / 'judge_level_diagnostics.json').write_text(json.dumps({'rows': out, 'input_sha256': hashes}, indent=2))
    for r in out:
        print(f"{r['family']:<12} {r['view']:<6} rho={r['rho_ti']:.3f} p_exact={r['perm_p_exact']:.3f} rho_cf={r['rho_cf']:.3f} rho6={r['rho_no_controls']:.3f} rho4={r['rho_same_model']:.3f}")

if __name__ == '__main__':
    main()
