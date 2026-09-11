#!/usr/bin/env python3
"""Per-run W&B push for certification judge experiments."""
import argparse, json, os, re
import wandb

PROJECT = os.environ.get("WANDB_PROJECT", "trusting-formal-judge")
GROUP   = os.environ.get("WANDB_GROUP",   "certification-experiments")

IDENTITY_THRESHOLD  = 0.90
SPEARMAN_THRESHOLD  = -0.50
WEAK_MONO_THRESHOLD = 80.0

def parse(path):
    text = open(path).read()
    try:
        return json.loads(text)
    except:
        pass
    patterns = {
        "identity_mean_score":     r"identity_mean[_score]*\s*[:\s]+([0-9.]+)",
        "identity_std":            r"identity_std\s*[:\s]+([0-9.]+)",
        "monotonicity_spearman_r": r"spearman_r\s*[:\s]+([-0-9.]+)",
        "weak_monotonicity_pct":   r"weak_mono[noticity_%]*\s*[:\s]+([0-9.]+)",
        "pearson_edit_vs_judge":   r"pearson[_edit_vs_judge]*\s*[:\s]+([-0-9.]+)",
        "n_theorems":              r"n_theorems\s*[:\s]+([0-9]+)",
        "certified":               r"certified\s*[:\s]+([01])",
    }
    out = {}
    for k, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        out[k] = float(m.group(1)) if m else 0.0
    return out

def compute_certified(identity_mean, spearman_r, weak_mono_pct):
    return int(
        identity_mean  > IDENTITY_THRESHOLD and
        spearman_r     < SPEARMAN_THRESHOLD and
        weak_mono_pct  > WEAK_MONO_THRESHOLD
    )

def push(run_name, model, results_path, experiment="", notes=""):
    m = parse(results_path)
    identity     = round(float(m.get("identity_mean_score", 0)), 4)
    identity_std = round(float(m.get("identity_std", 0)), 4)
    spearman     = round(float(m.get("monotonicity_spearman_r", 0)), 4)
    weak_mono    = round(float(m.get("weak_monotonicity_pct", 0)), 2)
    pearson_ed   = round(float(m.get("pearson_edit_vs_judge", 0)), 4)
    n_theorems   = int(float(m.get("n_theorems", 0)))
    certified    = compute_certified(identity, spearman, weak_mono)
    combined     = round(identity * (weak_mono / 100.0), 4)
    cert_str     = "CERTIFIED" if certified else "NOT_CERTIFIED"

    print(f"\n{'='*62}")
    print(f"  Experiment  : {experiment}")
    print(f"  Run         : {run_name}  |  Model: {model}")
    print(f"  {chr(9472)*56}")
    print(f"  identity_mean       : {identity:.4f} +/- {identity_std:.4f}  (threshold > {IDENTITY_THRESHOLD})")
    print(f"  mono_spearman_r     : {spearman:.4f}          (threshold < {SPEARMAN_THRESHOLD})")
    print(f"  weak_mono_%         : {weak_mono:.1f}%            (threshold > {WEAK_MONO_THRESHOLD}%)")
    print(f"  pearson(edit,judge) : {pearson_ed:.4f}          (want near 0)")
    print(f"  n_theorems          : {n_theorems}")
    print(f"  combined_score      : {combined:.4f}")
    print(f"  certification       : {'[PASS] ' if certified else '[FAIL] '}{cert_str}")
    print(f"{'='*62}\n")

    run = wandb.init(
        project=PROJECT,
        group=GROUP,
        name=f"{experiment}__{run_name}__{model.replace('/', '_')}",
        tags=[experiment, run_name, model, GROUP, cert_str.lower()],
        notes=(
            f"**Experiment**: {experiment}\n"
            f"**Run**: {run_name} | **Model**: {model}\n\n"
            f"| Metric | Value | Pass? |\n"
            f"|--------|-------|-------|\n"
            f"| identity_mean | {identity:.4f} | {'PASS' if identity > IDENTITY_THRESHOLD else 'FAIL'} |\n"
            f"| mono_spearman_r | {spearman:.4f} | {'PASS' if spearman < SPEARMAN_THRESHOLD else 'FAIL'} |\n"
            f"| weak_mono_% | {weak_mono:.1f}% | {'PASS' if weak_mono > WEAK_MONO_THRESHOLD else 'FAIL'} |\n"
            f"| pearson(edit,judge) | {pearson_ed:.4f} | --- |\n\n"
            f"**Result: {cert_str}**\n\n{notes}"
        ),
        config={
            "run_name":            run_name,
            "model":               model,
            "experiment":          experiment,
            "n_theorems":          n_theorems,
            "identity_threshold":  IDENTITY_THRESHOLD,
            "spearman_threshold":  SPEARMAN_THRESHOLD,
            "weak_mono_threshold": WEAK_MONO_THRESHOLD,
        }
    )

    wandb.log({
        "identity_mean":      identity,
        "identity_std":       identity_std,
        "mono_spearman_r":    spearman,
        "mono_spearman_abs":  abs(spearman),
        "weak_mono_pct":      weak_mono,
        "pearson_edit_judge": pearson_ed,
        "pearson_edit_abs":   abs(pearson_ed),
        "n_theorems":         n_theorems,
        "certified":          certified,
        "combined_score":     combined,
    })

    tbl = wandb.Table(
        columns=["experiment", "run_name", "model",
                 "identity_mean", "identity_std", "mono_spearman_r",
                 "weak_mono_pct", "pearson_edit", "n_theorems",
                 "combined_score", "certified"],
        data=[[experiment, run_name, model,
               identity, identity_std, spearman, weak_mono,
               pearson_ed, n_theorems, combined, cert_str]]
    )
    wandb.log({"run_results_table": tbl})

    label = f"{experiment}/{run_name}"
    for metric, val, title in [
        ("identity_mean",    identity,      f"Identity Mean Score -- {label}"),
        ("mono_spearman_abs", abs(spearman), f"|Spearman r| Monotonicity -- {label}"),
        ("weak_mono_pct",    weak_mono,     f"Weak Monotonicity % -- {label}"),
        ("combined_score",   combined,      f"Combined Score -- {label}"),
    ]:
        t = wandb.Table(columns=["run", metric], data=[[label, val]])
        wandb.log({f"{metric}_bar": wandb.plot.bar(t, "run", metric, title=title)})

    run.finish()
    print(f"  W&B run: {run.url}\n")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run_name",   required=True)
    p.add_argument("--model",      required=True)
    p.add_argument("--results",    required=True)
    p.add_argument("--experiment", default="")
    p.add_argument("--notes",      default="")
    a = p.parse_args()
    push(a.run_name, a.model, a.results, a.experiment, a.notes)
