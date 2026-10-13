#!/usr/bin/env python3
"""Gate G0: reproduce the paper's nine judge-level Spearman values (3 families x
averaged/pass1/pass2) from the committed judge_trust_vector.csv files, to 3 decimals.

Zero model calls. Reads only already-committed, frozen CSVs.
"""
import csv
import json
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parents[1]
CJ_ROOT = EXP_DIR.parents[2]  # under experiments/archive/ since 10-13-2026
B = CJ_ROOT / "experiments/archive/04_veribench_validation"

INPUTS = {
    ("Codex", "avg"): B / "results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv",
    ("Codex", "pass1"): B / "results_exp28_varaware_codex_pass1_newindex/judge_trust_vector.csv",
    ("Codex", "pass2"): B / "results_exp28_varaware_codex_pass2_newindex/judge_trust_vector.csv",
    ("Claude Opus", "avg"): B / "results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv",
    ("Claude Opus", "pass1"): B / "results_exp28_varaware_opus_pass1_newindex/judge_trust_vector.csv",
    ("Claude Opus", "pass2"): B / "results_exp28_varaware_opus_pass2_newindex/judge_trust_vector.csv",
    ("Qwen3-Coder", "avg"): B / "results_exp28_varaware_qwen_avg/judge_trust_vector.csv",
    ("Qwen3-Coder", "pass1"): B / "results_exp28_varaware_qwen_pass1/judge_trust_vector.csv",
    ("Qwen3-Coder", "pass2"): B / "results_exp28_varaware_qwen_pass2/judge_trust_vector.csv",
}

# Paper's quoted headline numbers (README.md TLDR): Codex Spearman 0.833 on averaged labels,
# 0.905 and 0.738 on the two passes.
PAPER_QUOTED = {
    ("Codex", "avg"): 0.833,
    ("Codex", "pass1"): 0.905,
    ("Codex", "pass2"): 0.738,
}


def rank(v):
    idx = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    sa = sum((x - ma) ** 2 for x in a) ** 0.5
    sb = sum((y - mb) ** 2 for y in b) ** 0.5
    if sa == 0 or sb == 0:
        return float("nan")
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def spearman(a, b):
    return pearson(rank(a), rank(b))


def main():
    out = []
    for (fam, view), path in INPUTS.items():
        rows = list(csv.DictReader(path.read_text().splitlines()))
        y = [float(r["human_spearman"]) for r in rows]
        ti = [float(r["TI_variance_aware"]) for r in rows]
        rho = spearman(ti, y)
        row = {"family": fam, "view": view, "n_judges": len(rows), "rho_ti_vs_human": round(rho, 6)}
        if (fam, view) in PAPER_QUOTED:
            want = PAPER_QUOTED[(fam, view)]
            row["paper_quoted"] = want
            row["matches_3dp"] = round(rho, 3) == round(want, 3)
        out.append(row)

    all_g0_pass = all(r.get("matches_3dp", True) for r in out)
    result = {"gate": "G0", "rows": out, "all_quoted_values_reproduced_to_3dp": all_g0_pass}
    (EXP_DIR / "results" / "G0_reproduction.json").write_text(json.dumps(result, indent=2) + "\n")
    for r in out:
        extra = f" (paper quoted {r['paper_quoted']}, match={r['matches_3dp']})" if "paper_quoted" in r else ""
        print(f"{r['family']:<12} {r['view']:<6} rho={r['rho_ti_vs_human']:.6f}{extra}")
    print("G0 PASS" if all_g0_pass else "G0 FAIL")


if __name__ == "__main__":
    main()
