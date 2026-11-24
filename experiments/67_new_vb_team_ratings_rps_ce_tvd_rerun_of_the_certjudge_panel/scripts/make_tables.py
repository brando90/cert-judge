"""Experiment 67: build the markdown tables of RESULTS.md from results/*.csv and results/*.json (no new computation of metrics)."""
import csv, json
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[1] / "results"
A1 = list(csv.DictReader(open(R / "old_A1_raw_per_judge.csv"))); A2 = list(csv.DictReader(open(R / "old_A2_calibrated_loto.csv")))
f = lambda r, k: float(r[k])
out = []
out.append("### T1. Old set, per judge series, against the corrected VeriBench labels (H_vb: 59 artifacts, 20 tasks, 4.5 ratings each). Lower is better for RPS, CE, TVD. Intervals: task-bootstrap 95%.\n")
out.append("| family | judge series | RPS [95%] | CE | TVD | Spearman [95%] | Pearson |\n|---|---|---|---|---|---|---|")
for r in A1:
    if r["target"] != "H_vb": continue
    out.append(f"| {r['family']} | {r['judge']} | {f(r,'RPS'):.3f} [{f(r,'RPS_lo'):.3f}, {f(r,'RPS_hi'):.3f}] | {f(r,'CE'):.2f} | {f(r,'TVD'):.3f} | {f(r,'Spearman'):+.2f} [{f(r,'Spearman_lo'):+.2f}, {f(r,'Spearman_hi'):+.2f}] | {f(r,'Pearson'):+.2f} |")
out.append("\n### T2. Calibrated forecasts, leave-one-task-out, mean over the 8 series of each family (H_vb). Negative difference = first is better.\n")
out.append("| family | CONST RPS | CE-fit RPS | Pearson-fit RPS | CE-fit minus CONST: series better / significantly better (RPS) | CE-fit minus Pearson-fit: series better (RPS / CE / TVD) |\n|---|---|---|---|---|---|")
for fam in ["Codex", "Claude Opus", "Qwen3-Coder", "ALL 24"]:
    sel = lambda c: [r for r in A2 if r["comparison"] == c and (fam.startswith("ALL") or r["family"] == fam)]
    lv = {k: np.mean([f(r, "dRPS") for r in sel("heldout level " + k)]) for k in ("CONST", "CE-fit", "Pearson-fit")}
    c1 = sel("CE-fit minus CONST"); c2 = sel("CE-fit minus Pearson-fit")
    out.append(f"| {fam} | {lv['CONST']:.4f} | {lv['CE-fit']:.4f} | {lv['Pearson-fit']:.4f} | {sum(f(r,'dRPS')<0 for r in c1)}/{len(c1)} / {sum(f(r,'dRPS_hi')<0 for r in c1)} | {sum(f(r,'dRPS')<0 for r in c2)} / {sum(f(r,'dCE')<0 for r in c2)} / {sum(f(r,'dTVD')<0 for r in c2)} of {len(c2)} |")
ce_ = [r for r in A2 if r["comparison"] == "heldout level CONST"]
out.append("\n### T3. Human side: old and new\n")
A3 = list(csv.DictReader(open(R / "old_A3_ceiling.csv")))[0]
N = json.load(open(R / "new_summary.json")); a = N["agree"]
out.append("| | old (corrected labels) | new (returned so far) |\n|---|---|---|")
out.append(f"| artifacts / tasks | {A3['n_items']} / {A3['n_tasks']} | 100 / 25 |")
out.append(f"| ratings per artifact | {float(A3['ratings_per_item']):.1f} | 2.5 (two raters complete: 2.0 on each of the 100) |")
out.append(f"| split-half Spearman, Spearman-Brown corrected | {float(A3['spearman_brown']):.2f} | {a['spearman_brown_2raters']:.2f} (from two raters, so a mean of 2) |")
out.append(f"| ceiling on judge-human correlation (sqrt) | {float(A3['ceiling_judge_human']):.2f} | {a['ceiling_judge_mean_of_2']:.2f} |")
out.append(f"| two raters: Spearman [95%], exact, within 1, weighted kappa | n/a | {a['spearman']:.2f} [{a['spearman_lo']:.2f}, {a['spearman_hi']:.2f}], {a['exact']:.2f}, {a['within1']:.2f}, {a['qwk']:.2f} |")
S = json.load(open(R / "old_summary.json")); d = S["Codex"]["vb_rating_dist"]
out.append(f"| share of ratings at 5 / at 4 or 5 | {d[5]:.2f} / {d[4]+d[5]:.2f} | {a['share_5']:.2f} / {a['share_4_5']:.2f} |")
out.append("\n### T4. Task-bootstrap interval width of the judge-free edit-distance baseline's Spearman (so it can be compared across old, new and pooled without any judge scores on the new files)\n")
out.append("| set | tasks | artifacts | Spearman [95%] | width |\n|---|---|---|---|---|")
for k, v in N["pooled_editdist"].items():
    out.append(f"| {k} | {v['n_tasks']} | {v['n_artifacts']} | {v['spearman']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}] | {v['width']:.2f} |")
out.append("\n### T5. Learning curve, headline judge series on old H_vb (random k of 20 tasks, 500 draws, 2.5 to 97.5 percentile of Spearman); last row is the task-bootstrap of all tasks\n")
out.append("| series | k=4 | k=8 | k=12 | k=16 | all 20 (bootstrap) |\n|---|---|---|---|---|---|")
C = list(csv.DictReader(open(R / "old_A4_learning_curve.csv")))
for fam in ["Codex", "Claude Opus", "Qwen3-Coder"]:
    rows = [r for r in C if r["family"] == fam]
    cells = [f"{f(r,'median'):+.2f} (width {f(r,'width'):.2f})" for r in rows if int(r["k_tasks"]) < 20] + [f"{f(rows[-1],'median'):+.2f} (width {f(rows[-1],'width'):.2f})"]
    out.append(f"| {fam} P8_STRICT_B | " + " | ".join(cells) + " |")
out.append("\n### T6. Learning curve of the edit-distance baseline, pooled with within-set ranks (random k of 45 tasks)\n")
out.append("| k tasks | 10 | 20 | 30 | 40 |\n|---|---|---|---|---|")
pc = N["pooled_curve_within"]
out.append("| median (width) | " + " | ".join(f"{x['median']:+.2f} ({x['width']:.2f})" for x in pc[:4]) + " |")
A5 = list(csv.DictReader(open(R / "old_A5_TI_vs_alignment.csv")))
out.append("\n### T7. Does the Trust Index track alignment? Spearman of TI_var with each alignment over the 8 judge series of a family (H_vb); interval = task-bootstrap, p = exact permutation\n")
out.append("| family | alignment | rho [95%] | p |\n|---|---|---|---|")
for r in A5:
    out.append(f"| {r['family']} | {r['alignment']} | {float(r['rho_TI'].strip('[]')) :+.2f} [{f(r,'lo'):+.2f}, {f(r,'hi'):+.2f}] | {f(r,'perm_p'):.3f} |")
(R / "tables.md").write_text("\n".join(out) + "\n"); print("\n".join(out))
