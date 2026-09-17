#!/usr/bin/env python3
"""Render the saved exploratory diagnostics as tables and scientific figures."""
from pathlib import Path
from datetime import datetime
import csv
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def load(name):
    return json.loads((OUT / name).read_text())


def fmt(value):
    return "undefined" if value is None else f"{value:.3f}"


def main(snapshot=False):
    criterion = load("criterion.json")
    variants = load("proxy_variants.json")
    comparisons = load("associations.json")
    simulation = load("design_simulation.json")
    zero = load("zero_audit.json")
    holdout = load("family_holdout.json")
    manifest = load("run_manifest.json")
    publication = load("wandb_report.json") if (OUT / "wandb_report.json").exists() else None
    judges = [r["judge_id"] for r in manifest["judges"]]
    primary = {r["judge_id"] for r in manifest["judges"] if r["role"] == "primary"}
    plots = OUT / "plots"
    plots.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), layout="constrained")
    for ax, variant, title in zip(axes, ("frozen", "floor_0.001"), ("Frozen proxy", "Artifact-factor floor = 0.001")):
        for j in judges:
            x = variants[variant][j]
            y = criterion[j]["views"]["average"]["ti_2prime"]["spearman"]
            ax.scatter(x, y, c="#285F9A" if j in primary else "#C57835",
                       marker="o" if j in primary else "s", s=60)
            label = j.replace("claude-sonnet-5|", "Sonnet ").replace("gpt-5.6-terra|", "Terra ").replace("P4_CHECKLIST", "checklist").replace("P8_STRICT_B", "strict").replace("P1_BASELINE", "baseline").replace("BAD_STRINGY", "string control").replace("editdist_e1", "edit control").replace("random_r1", "random control")
            crowded = {"claude-sonnet-5|P4_CHECKLIST": .36,
                       "gpt-5.6-terra|P4_CHECKLIST": .48, "editdist_e1": .42}
            if variant == "frozen" and j in crowded:
                ax.annotate(label, (x, y), xytext=(.15, crowded[j]), textcoords="data",
                            fontsize=8, arrowprops={"arrowstyle": "-", "color": "#777777", "lw": .7})
            else:
                ax.annotate(label, (x, y), xytext=(5, 5 if "editdist" not in j else -12),
                            textcoords="offset points", fontsize=8)
        ax.set(xlabel="Proxy score", ylabel="Human agreement × repeat stability\n(geometric mean)",
               title=title, xlim=(-.04, 1.08), ylim=(-.03, .76))
        ax.grid(alpha=.15)
    fig.suptitle("Previously observed panel: 5 primary judges + 3 controls", fontsize=13)
    fig.savefig(plots / "proxy_vs_combined_trust.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.8, 4.3), layout="constrained")
    for rho in (.3, .5, .7):
        rows = [r for r in simulation["rows"] if r["intrafamily_correlation"] == 0 and r["population_pearson"] == rho]
        ax.plot([r["n_configurations"] for r in rows], [r["zero_exclusion_frequency"] for r in rows], marker="o", label=f"True Pearson correlation {rho}")
    ax.axhline(.8, color="#777777", ls="--", lw=1)
    ax.set(xlabel="Independent configurations (idealized)", ylabel="Fraction of 95% intervals excluding zero",
           ylim=(0, 1.04), title="Synthetic design sensitivity — 2,000 datasets per setting")
    ax.legend(fontsize=9)
    ax.grid(alpha=.15)
    fig.savefig(plots / "independent_panel_sensitivity.png", dpi=180)
    plt.close(fig)

    lines = ["# Proxy validation follow-up experiments", "",
        "**TLDR:** Adding repeat stability does not establish proxy validity on the current panel: the frozen index’s Spearman association is −0.354 across the five primary judges, and the 0.001-floor alternative is −0.600. The comparisons are exploratory, their problem-bootstrap intervals cross zero, and two primary judge families cannot support the requested train/validation/test design.", "",
        f"**Generated:** {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "**Status:** Experiments completed; independent review recorded in the experiment-root results.md.", "",
        "## What was executed", "",
        "The run reconstructs both saved proxy variants, recomputes the combined target from 1,728 criterion-associated scores, compares all declared aggregation variants, resamples shared problems, tests family-held-out calibration, and simulates sampling designs. It performs zero model calls and collects zero new human labels.", "",
        "| Setting | Value |", "|---|---|",
        f"| Human-labeled candidates / problems | {manifest['candidate_count']} / {manifest['problem_count']} |",
        "| Primary configurations / model families | 5 / 2 |",
        "| Controls | 3, reported separately |", "| Repeats per candidate and judge | 3 |",
        f"| Problem-bootstrap draws / seed | {manifest['draws']} / {manifest['seed']} |",
        "| Synthetic datasets per design | 2,000 |",
        "| Judge-score scale / human scale | [0,1] / [0,5], human scores divided by 5 once |",
        "| Primary variability convention | Mean within-candidate sample standard deviation, denominator K−1 |", "",
        "## Combined human-grounded target", "",
        "Trust Index 2-prime is the square root of nonnegative human agreement times one minus repeat variability. The signed agreement is retained, including when its contribution is clamped to zero. Pearson, Spearman, Kendall tau-b and absolute-agreement intraclass correlation are separate target definitions; their shared observations do not provide independent confirmations.", "",
        "| Judge | Role | Human Spearman | Repeat standard deviation | Combined trust |", "|---|---|---:|---:|---:|"]
    for j in judges:
        c = criterion[j]
        lines.append(f"| {j.replace('|', ' / ')} | {'primary' if j in primary else 'control'} | {fmt(c['views']['average']['agreement']['spearman'])} | {fmt(c['sample_sd'])} | {fmt(c['views']['average']['ti_2prime']['spearman'])} |")
    lines += ["", "The seeded random control repeats identically by construction; perfect repeatability does not make its answers accurate. The string-similarity control has the highest combined target on this panel, so control intent and the human criterion disagree. This does not independently prove either criterion correct.", "",
        "## Proxy comparisons", "",
        "These rows use the averaged rubric and Spearman-based combined target. The full machine-readable comparison includes all three rubric views, four target definitions, and Pearson, Spearman, Kendall, Lin concordance, and intraclass-correlation diagnostics between proxy and target.", "",
        "| Panel | Proxy | Pearson | Spearman | Kendall | 95% problem-bootstrap interval for Spearman |", "|---|---|---:|---:|---:|---|"]
    selected = [r for r in comparisons if r["view"] == "average" and r["inner_method"] == "spearman" and r["target"] == "ti_2prime" and r["proxy"] in ("frozen", "floor_0.001", "mean_then_gm", "stability_only")]
    for r in selected:
        ci = r["outer_spearman_problem_bootstrap"]
        lines.append(f"| {r['cohort']} | {r['proxy']} | {fmt(r['outer']['pearson'])} | {fmt(r['outer']['spearman'])} | {fmt(r['outer']['kendall_tau_b'])} | [{fmt(ci['ci_low'])}, {fmt(ci['ci_high'])}]; {ci['valid_draws']}/{manifest['draws']} defined |")
    lines += ["", "![Proxy versus combined trust](plots/proxy_vs_combined_trust.png)", "",
        "The floor improves ranking resolution, but it does not establish the intended ranking among primary judges. These exposed data cannot select a replacement and then validate it. The stability-only comparator also tests whether a shared repeatability term creates the apparent relationship.", "",
        "## What causes the zeros", "",
        f"{zero['aggregate_zero_judges']}/8 aggregate proxy scores are zero. Bug monotonicity is zero for {zero['zero_judges_by_property']['P_bm']}/8, correcting pull request 42’s 7/8 statement. Equality can independently collapse the aggregate; a zero raw score on a degraded ladder rung is not itself the zero rule. The rule acts on artifact-level property factors and their geometric aggregates.", "",
        "The committed zero audit includes every property’s factor-zero counts and a leave-one-problem-out aggregation check. Factors, strict and floored aggregates reproduce the frozen data within 1e-12 before new analyses run.", "",
        "## Generalization and calibration", "",
        "Only two primary judge-model families are available. Controls are excluded from the family-transfer analysis; generation slots are not documented generator-model families. A whole-family train/validation/test split is therefore not computable here.", "",
        "| Proxy | Prediction method | Mean squared error on held-out families | Spearman |", "|---|---|---:|---:|"]
    for r in holdout["rows"]:
        if r["target"] == "ti_2prime" and r["proxy"] in ("frozen", "floor_0.001"):
            lines.append(f"| {r['proxy']} | {r['mode']} | {r['mse']:.6f} | {fmt(r['outer']['spearman'])} |")
    lines += ["", "The nearly equal Sonnet proxy scores produce a steep calibration from only two training points; extrapolating to Terra gives extreme predictions and large errors. This is a recorded failure of the prespecified linear calibration, not missing data or a numerical exception. No clipping or replacement calibration was selected after seeing the result. Full fold slopes and predictions are saved. A reversing calibration tests a different claim from a positively oriented raw proxy; the training-mean baseline remains visible.", "",
        "## Sample-size experiment", "",
        "These are synthetic bivariate-normal scenarios, not a fitted forecast of unseen models or a measured human-label reliability. At true Pearson correlation 0.5, the independent-unit simulations give:", "",
        "| Independent units | Zero-exclusion frequency | Mean interval width | 95% interval coverage |", "|---:|---:|---:|---:|"]
    for r in simulation["rows"]:
        if r["intrafamily_correlation"] == 0 and r["population_pearson"] == .5:
            lines.append(f"| {r['n_configurations']} | {r['zero_exclusion_frequency']:.1%} | {r['mean_interval_width']:.3f} | {r['coverage_95']:.1%} |")
    lines += ["", "![Independent-panel sensitivity](plots/independent_panel_sensitivity.png)", "",
        "Twelve or twenty configurations are not a universal sufficiency rule. Related prompts further reduce effective independence: the separate clustered scenarios show that treating them as independent can under-cover the population correlation. Their specified intrafamily correlation of 0.7 is an assumption, not an estimate from two families.", "",
        "## Uncertainty and interpretation", "",
        "The problem bootstrap jointly resamples problems for every judge and recomputes proxy and criterion with the same weights. It preserves candidates within a problem and complete observed repeat vectors. Its intervals condition on the observed human labels, model calls and configurations; they do not measure uncertainty over new raters, future calls or new model families. Undefined correlations are counted. Pairwise ranking fractions are bootstrap frequencies, not posterior probabilities.", "",
        "The new analysis does not use the earlier automatic ceiling correction or independent-pair intervals for fitted cross-validation predictions. The same-person cross-rubric Spearman value 0.249 is not an intraclass-correlation estimate for the revised five-rater pool. Judge-level criterion reliability must be established at that level rather than borrowed from individual labels.", "",
        "## Reproduce and inspect", "", "```bash", "PYTHONPATH=py_src .venv/bin/python experiments/archive/30_proxy_trust_index_held_out_validity/expt_v2/run_diagnostics.py",
        ".venv/bin/python experiments/archive/30_proxy_trust_index_held_out_validity/expt_v2/render_report.py", "```", "",
        "The run manifest records source hashes, the seed, software versions and exact judge identifiers. No experiment-29 files were overwritten. All grids were specified in PROTOCOL.md before this follow-up run, after the historical data had already been inspected.", "",
        (f"Weights & Biases report: [open published report]({publication['report_url']})."
         if publication else "Weights & Biases report: pending publication after review."), "",
        "Method references: [intraclass-correlation definitions](https://pmc.ncbi.nlm.nih.gov/articles/PMC4913118/), [cross-validation dependence](https://www.jmlr.org/papers/v5/grandvalet04a.html), [small-sample rank inference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).", "",
        "**TLDR-end:** The combined target and zero-handling experiments do not establish proxy validity; retain the alternatives as exploratory and expand independent families only under a new locked design."]
    report = OUT / "report.md"
    report.write_text("\n".join(lines) + "\n")
    if snapshot:
        timestamped = OUT / f"results_summary_{datetime.now().strftime('%Y-%m-%d__%H-%M-%S')}.md"
        timestamped.write_text(report.read_text())
        print(timestamped)
    with (OUT / "associations.csv").open("w", newline="") as handle:
        fields = ["cohort", "view", "inner_method", "target", "proxy", "n_judges", "pearson", "spearman", "kendall_tau_b", "icc_a1", "lin_ccc"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for r in comparisons:
            writer.writerow({k: r[k] if k in r else r["outer"][k] for k in fields})
    print(report)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true", help="also save an immutable timestamped report")
    main(parser.parse_args().snapshot)
