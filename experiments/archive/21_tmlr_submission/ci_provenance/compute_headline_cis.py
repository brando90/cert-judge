#!/usr/bin/env python3
"""Deterministic provenance for the headline TI_var-vs-human uncertainty numbers.

Recomputes, from the exp28 trust-vector artifacts, the three judge-level Spearman
correlations quoted in the paper abstract (0.833/0.905/0.738) together with their
10k-resample bootstrap 95% CIs and 10k permutation p-values (seed 42) that the
TMLR resubmission (paper_latex/TMLR_2026) quotes as [0.24,1.00]/[0.41,1.00]/[0.11,1.00]
and p = 0.017/0.005/0.045.

Run:  python3 compute_headline_cis.py   (writes headline_cis.json next to itself)

History: first computed 2026-07-29 in-session for the TMLR submission; Mega-QA stage 3
(2026-08-01) independently reproduced the CIs exactly and the perm p within Monte-Carlo
noise; this script freezes the exact procedure + RNG stream as a machine-readable artifact.
"""
import csv, json, random
from pathlib import Path

from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parents[3]
EXP28 = REPO / "experiments/04_veribench_validation"
PANELS = [("avg", "results_exp28_varaware_codex_avg_newindex"),
          ("pass1", "results_exp28_varaware_codex_pass1"),
          ("pass2", "results_exp28_varaware_codex_pass2_newindex")]
N_BOOT = N_PERM = 10_000
SEED = 42

out = {"seed": SEED, "n_boot": N_BOOT, "n_perm": N_PERM, "panels": {}}
for label, d in PANELS:
    summ = json.load(open(EXP28 / d / "summary.json"))
    csv_path = Path(summ["outputs"]["judge_trust_vector_csv"])
    if not csv_path.is_absolute():
        csv_path = REPO / csv_path  # artifact stores repo-relative paths
    rows = list(csv.DictReader(open(csv_path)))
    tik = next(k for k in rows[0] if "ti" in k.lower() or "trust" in k.lower())
    hk = next(k for k in rows[0] if "human" in k.lower())
    x = [float(r[tik]) for r in rows]
    y = [float(r[hk]) for r in rows]
    point = spearmanr(x, y).statistic

    rng = random.Random(SEED)
    boots = []
    while len(boots) < N_BOOT:
        idx = [rng.randrange(len(x)) for _ in range(len(x))]
        if len({x[i] for i in idx}) < 2 or len({y[i] for i in idx}) < 2:
            continue
        s = spearmanr([x[i] for i in idx], [y[i] for i in idx]).statistic
        if s == s:
            boots.append(s)
    boots.sort()

    perm, xs = 0, x[:]
    for _ in range(N_PERM):
        rng.shuffle(xs)
        if abs(spearmanr(xs, y).statistic) >= abs(point) - 1e-12:
            perm += 1

    out["panels"][label] = {
        "n_judges": len(x), "ti_column": tik, "artifact_dir": d,
        "rho": round(point, 4),
        "ci95": [round(boots[int(0.025 * len(boots))], 3), round(boots[int(0.975 * len(boots))], 3)],
        "perm_p": round((perm + 1) / (N_PERM + 1), 4),
    }

path = Path(__file__).with_name("headline_cis.json")
path.write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
