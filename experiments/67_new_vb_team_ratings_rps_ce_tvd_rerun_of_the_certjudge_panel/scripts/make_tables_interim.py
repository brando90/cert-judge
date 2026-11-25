"""Markdown tables for the interim judge-scored run (results/interim_11-24-2026/). Stdlib only."""
import csv, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "results" / "interim_11-24-2026"
rd = lambda f: list(csv.DictReader(open(D / f)))
f = lambda x, n=3: "" if x in ("", None) else f"{float(x):.{n}f}"
iv = lambda r, k, n=3: f"{f(r[k],n)} [{f(r[k+'_lo'],n)}, {f(r[k+'_hi'],n)}]"
SN = {"old (H_vb)": "old (59 files, 20 tasks)", "new (interim)": "new (100 files, 25 tasks)", "pooled old+new": "pooled (159 files, 45 tasks)"}
out = []
b1 = rd("judged_B1_per_set_and_pooled.csv")
out += ["### B1a. Proper scores per set: judge vs the constant forecaster (lower is better; 95% task-bootstrap)", "",
        "| Judge | Set | RPS | const RPS | RPS minus const | CE | const CE | TVD | const TVD |", "|---|---|---|---|---|---|---|---|---|"]
for r in b1:
    out.append(f"| {r['family']} | {SN[r['set']]} | {iv(r,'RPS')} | {f(r['constRPS'])} | {iv(r,'dRPS_vs_const')} | {iv(r,'CE')} | {f(r['constCE'])} | {iv(r,'TVD')} | {f(r['constTVD'])} |")
out += ["", "### B1b. Secondary: correlations", "", "| Judge | Set | Spearman | Pearson | Spearman width | RPS width |", "|---|---|---|---|---|---|"]
for r in b1:
    out.append(f"| {r['family']} | {SN[r['set']]} | {iv(r,'Spearman',2)} | {iv(r,'Pearson',2)} | {f(r['Spearman_width'],2)} | {f(r['RPS_width'],3)} |")
b3 = rd("judged_B3_calibrated.csv")
out += ["", "### B3. Calibrated forecasters, leave-one-task-out (difference, negative = first is better; 95% task-bootstrap)", "",
        "| Judge | Set | Comparison | dRPS | dCE | dTVD |", "|---|---|---|---|---|---|"]
for r in b3:
    if r["comparison"] == "levels": continue
    out.append(f"| {r['family']} | {r['set'].split(' (')[0]} | {r['comparison']} | {iv(r,'dRPS',4)} | {iv(r,'dCE',3)} | {iv(r,'dTVD',3)} |")
out += ["", "Levels (RPS / CE / TVD):", "", "| Judge | Set | CONST | CE-fit | Pearson-fit |", "|---|---|---|---|---|"]
for r in b3:
    if r["comparison"] != "levels": continue
    t = lambda p: f"{f(r[p+'_RPS'],4)} / {f(r[p+'_CE'],3)} / {f(r[p+'_TVD'],3)}"
    out.append(f"| {r['family']} | {r['set'].split(' (')[0]} | {t('CONST')} | {t('CE-fit')} | {t('Pearson-fit')} |")
b4 = rd("judged_B4_learning_curves.csv")
out += ["", "### B4. Learning curves over random k tasks (median over draws)", "", "| Judge | Set | k tasks | Spearman median | Spearman width | dRPS median | dRPS width |", "|---|---|---|---|---|---|---|"]
for r in b4:
    out.append(f"| {r['family']} | {r['set']} | {r['k_tasks']} | {f(r['spearman_median'],2)} | {f(r['spearman_width'],2)} | {f(r['dRPS_median'],3)} | {f(r['dRPS_width'],3)} |")
(D / "tables_interim.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
