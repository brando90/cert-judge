#!/usr/bin/env python3
"""
Final W&B leaderboard report for certification judge experiments.
Run once after all experiments complete:
  python utils/final_report.py
"""
import wandb, os

PROJECT     = os.environ.get("WANDB_PROJECT", "trusting-formal-judge")
GROUP       = os.environ.get("WANDB_GROUP",   "certification-experiments")
REPORT_NAME = "FINAL--certification-leaderboard"


def main():
    api      = wandb.Api()
    all_runs = api.runs(
        f"{api.default_entity}/{PROJECT}",
        filters={"group": GROUP}
    )

    # Deduplicate: best combined_score per (experiment, run_name, model)
    best = {}
    for r in all_runs:
        if REPORT_NAME in r.name:
            continue
        exp   = r.config.get("experiment", "unknown")
        name  = r.config.get("run_name",   r.name)
        model = r.config.get("model",      "unknown")
        key   = f"{exp}|{name}|{model}"
        score = r.summary.get("combined_score", 0)
        if key not in best or score > best[key]["combined_score"]:
            best[key] = {
                "experiment":       exp,
                "run_name":         name,
                "model":            model,
                "identity_mean":    round(r.summary.get("identity_mean",       0), 4),
                "identity_std":     round(r.summary.get("identity_std",        0), 4),
                "mono_spearman_r":  round(r.summary.get("mono_spearman_r",     0), 4),
                "weak_mono_pct":    round(r.summary.get("weak_mono_pct",       0), 1),
                "pearson_edit":     round(r.summary.get("pearson_edit_judge",  0), 4),
                "n_theorems":       int(r.summary.get("n_theorems",            0)),
                "certified":        int(r.summary.get("certified",             0)),
                "combined_score":   round(r.summary.get("combined_score",      0), 4),
            }

    rows = sorted(best.values(),
                  key=lambda x: (x["certified"], x["identity_mean"]),
                  reverse=True)

    if not rows:
        print("No runs found in W&B. Have you run any experiments?")
        return

    # Terminal leaderboard
    COL_W = [3, 20, 18, 22, 9, 9, 11, 11, 11, 9, 5]
    HEADERS = ["#", "Experiment", "Run", "Model",
               "id_mean", "id_std", "spearman_r",
               "weak_mono%", "pearson_ed", "combined", "cert"]
    sep = "+" + "+".join("-"*(w+2) for w in COL_W) + "+"
    hdr = "| " + " | ".join(h.ljust(COL_W[i]) for i, h in enumerate(HEADERS)) + " |"
    print(f"\n{'CERTIFICATION LEADERBOARD':^{sum(COL_W)+len(COL_W)*3}}")
    print(f"{sep}\n{hdr}\n{sep}")
    for i, d in enumerate(rows):
        cert_icon = "[CERTIFIED]" if d["certified"] else "[NOT_CERT]"
        cells = [
            str(i+1),
            d["experiment"][:COL_W[1]],
            d["run_name"][:COL_W[2]],
            d["model"][:COL_W[3]],
            f"{d['identity_mean']:.4f}",
            f"{d['identity_std']:.4f}",
            f"{d['mono_spearman_r']:.4f}",
            f"{d['weak_mono_pct']:.1f}%",
            f"{d['pearson_edit']:.4f}",
            f"{d['combined_score']:.4f}",
            cert_icon[:COL_W[10]],
        ]
        print("| " + " | ".join(str(cells[j]).ljust(COL_W[j]) for j in range(len(COL_W))) + " |")
    print(f"{sep}")

    certified_rows = [d for d in rows if d["certified"]]
    print(f"\n  {len(rows)} total runs | {len(certified_rows)} CERTIFIED | "
          f"{len(rows)-len(certified_rows)} NOT CERTIFIED\n")
    if certified_rows:
        b = certified_rows[0]
        print(f"  Best certified: {b['experiment']} / {b['run_name']} ({b['model']})")
        print(f"    identity={b['identity_mean']:.4f}, spearman={b['mono_spearman_r']:.4f}, "
              f"weak_mono={b['weak_mono_pct']}%\n")

    # W&B final report run
    run = wandb.init(
        project=PROJECT, group=GROUP, name=REPORT_NAME,
        tags=["summary", "final", GROUP],
        notes=(
            f"## Certification Leaderboard -- Final Report\n\n"
            f"- **Total runs**: {len(rows)}\n"
            f"- **Certified**: {len(certified_rows)}\n"
            f"- **Not certified**: {len(rows)-len(certified_rows)}\n"
            f"- **Certification rate**: {len(certified_rows)/len(rows)*100:.1f}%\n\n"
            f"Best certified: "
            f"{certified_rows[0]['run_name'] if certified_rows else 'none'}\n\n"
            f"Certification criteria:\n"
            f"- identity_mean > 0.90\n"
            f"- mono_spearman_r < -0.50\n"
            f"- weak_mono_pct > 80%"
        )
    )

    # 1. Full leaderboard table
    tbl = wandb.Table(
        columns=["rank","experiment","run","model",
                 "identity_mean","identity_std","mono_spearman_r",
                 "weak_mono_pct","pearson_edit","n_theorems",
                 "combined_score","certified"],
        data=[[
            i+1, d["experiment"], d["run_name"], d["model"],
            d["identity_mean"], d["identity_std"], d["mono_spearman_r"],
            d["weak_mono_pct"], d["pearson_edit"], d["n_theorems"],
            d["combined_score"], "CERTIFIED" if d["certified"] else "NOT_CERTIFIED"
        ] for i, d in enumerate(rows)]
    )
    wandb.log({"leaderboard": tbl})

    # 2. Identity mean bar
    t = wandb.Table(
        columns=["run", "identity_mean"],
        data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", d["identity_mean"]]
              for d in rows])
    wandb.log({"identity_mean_comparison": wandb.plot.bar(
        t, "run", "identity_mean",
        title="Identity Mean Score by Run (higher = better)")})

    # 3. |Spearman r| bar
    t = wandb.Table(
        columns=["run", "mono_spearman_abs"],
        data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", abs(d["mono_spearman_r"])]
              for d in rows])
    wandb.log({"mono_spearman_comparison": wandb.plot.bar(
        t, "run", "mono_spearman_abs",
        title="|Spearman r| Monotonicity by Run (higher = better)")})

    # 4. Identity vs |Monotonicity| scatter
    t = wandb.Table(
        columns=["run", "identity_mean", "mono_spearman_abs"],
        data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}",
               d["identity_mean"], abs(d["mono_spearman_r"])]
              for d in rows])
    wandb.log({"certification_scatter": wandb.plot.scatter(
        t, "identity_mean", "mono_spearman_abs",
        title="Identity vs |Monotonicity| -- certified models cluster top-right")})

    # 5. Pearson(edit, judge) bar
    t = wandb.Table(
        columns=["run", "pearson_edit_judge"],
        data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", d["pearson_edit"]]
              for d in rows])
    wandb.log({"pearson_edit_comparison": wandb.plot.bar(
        t, "run", "pearson_edit_judge",
        title="Pearson(edit_distance, judge_score) -- near 0 = semantic judge")})

    # 6. Combined score bar
    t = wandb.Table(
        columns=["run", "combined_score"],
        data=[[f"{d['experiment']}/{d['run_name']}/{d['model']}", d["combined_score"]]
              for d in rows])
    wandb.log({"combined_score_comparison": wandb.plot.bar(
        t, "run", "combined_score",
        title="Combined Score (identity x weak_mono%) -- higher = better")})

    # 7. Summary scalars
    wandb.log({
        "n_runs":                len(rows),
        "n_certified":           len(certified_rows),
        "certification_rate_%":  round(len(certified_rows)/len(rows)*100, 1) if rows else 0,
        "best_identity_mean":    rows[0]["identity_mean"] if rows else 0,
        "mean_identity_mean":    round(sum(d["identity_mean"] for d in rows)/len(rows), 4) if rows else 0,
        "mean_spearman_r":       round(sum(d["mono_spearman_r"] for d in rows)/len(rows), 4) if rows else 0,
        "mean_combined_score":   round(sum(d["combined_score"] for d in rows)/len(rows), 4) if rows else 0,
    })

    run.finish()
    print(f"\n  W&B final report: {run.url}\n")


if __name__ == "__main__":
    main()
