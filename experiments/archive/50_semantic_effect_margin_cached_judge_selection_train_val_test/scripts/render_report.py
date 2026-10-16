#!/usr/bin/env python3
"""Render the committed experiment-50 Markdown report from numerical tables."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
E = Path(__file__).resolve().parents[1]
R = E / "results"
def read(n): return json.loads((R / n).read_text())
def cell(c): return "undefined" if c["value"] is None else f"{c['value']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}]"
def main():
    ev, assoc, base = read("evaluation.json"), read("association.json"), read("baseline_reproduction.json")
    test, val = ev["splits"]["test"], ev["splits"]["val"]
    primary = test["targets"]["current5_mean_0_to_1"]
    margin = primary["selectors"]["max_train_semantic_margin"]["metrics"]
    h2 = primary["selectors"]["fixed_H2"]["metrics"]
    delta = primary["margin_minus_every_comparator"]["fixed_H2"]["spearman"]
    lines = ["# Semantic effect margin: cached judge selection", "", "**Doc link:** https://github.com/brando90/cert-judge/tree/codex/cj-e50-semantic-margin/experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test", "", "## Result", "", f"On the historical VeriBench version 1 test split, maximum training semantic margin selected `t2_sonnet5|D0` and had expected Spearman {cell(margin['spearman'])}, versus fixed H2 {cell(h2['spearman'])}; the paired margin-minus-H2 difference is {cell(delta)} (p-val=n/a).", "The interval spans zero, so this exploratory cached analysis supplies no positive selection evidence; validation is unavailable under the frozen common-support rule (13/15 files, 14 required).", "", "## Frozen scope and provenance", "", "The selector was frozen before outcome loading: `selection_receipt.json` records `human_outcomes_read=false` and SHA-256 `5cce7bd559bfae1ddd3fb531ef268aeb0cafaf5f5fc5b79b31b24254523bd858`.", "The post-selection evaluator correction only fixed return-value unpacking and added deterministic adapter fixtures; `evaluation_source_manifest.json` hashes the correction, selection bytes, and imported experiment-45 inventory dependency.", "Inputs are archived experiment-46/39/42/44/45 cached artifacts; there were zero new judge calls, no new human data, and no manuscript/reference changes.", "", "## Common support", "", f"| Split | Status | Common / declared files | Requirement | Tasks |", "| --- | --- | ---: | ---: | ---: |", f"| validation | {val['status']} | {val['common_files']} / {val['declared_files']} | {val['required_common_files']} | n/a |", f"| test | {test['status']} | {test['common_files']} / {test['declared_files']} | {test['required_common_files']} | {test['common_tasks']} |", "", "## Test utility: current-five target", "", "| Selector | Spearman [95% task bootstrap] | Pearson | Kendall tau-b | MAE | Bias | Judge mean | Human mean |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, row in primary["selectors"].items():
        m = row["metrics"]
        lines.append(f"| {name} | {cell(m['spearman'])} | {cell(m['pearson'])} | {cell(m['kendall'])} | {cell(m['mae'])} | {cell(m['bias'])} | {cell(m['judge_mean'])} | {cell(m['human_mean'])} |")
    lines += ["", "## Margin contrasts: current-five test target", "", "| Comparator | Delta Spearman (margin minus comparator) [95% interval] |", "| --- | --- |"]
    for name, metrics in primary["margin_minus_every_comparator"].items(): lines.append(f"| {name} | {cell(metrics['spearman'])} |")
    sensitivity = test["targets"]["current3_mean_0_to_1"]
    lines += ["", "## Test utility: current-three sensitivity", "", "| Selector | Spearman [95% task bootstrap] | Pearson | Kendall tau-b | MAE | Bias | Judge mean | Human mean |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, row in sensitivity["selectors"].items():
        m = row["metrics"]
        lines.append(f"| {name} | {cell(m['spearman'])} | {cell(m['pearson'])} | {cell(m['kendall'])} | {cell(m['mae'])} | {cell(m['bias'])} | {cell(m['judge_mean'])} | {cell(m['human_mean'])} |")
    lines += ["", "| Current-three comparator | Delta Spearman (margin minus comparator) [95% interval] |", "| --- | --- |"]
    for name, metrics in sensitivity["margin_minus_every_comparator"].items(): lines.append(f"| {name} | {cell(metrics['spearman'])} |")
    lines += ["", "Per-judge results, repeat-count histograms, every seven-metric contrast, and all leave-one-out tables are committed in `results/evaluation.json` and `results/robustness.json`.", "", "## Cross-configuration association", "", "| Training property | Configurations | Spearman [95% task bootstrap] | Pearson | Kendall tau-b |", "| --- | ---: | --- | --- | --- |"]
    for name, row in assoc.items():
        m = row["metrics"]; lines.append(f"| {name} | {row['n_configs']} | {cell(m['spearman'])} | {cell(m['pearson'])} | {cell(m['kendall'])} |")
    lines += ["", "## Robustness and limitations", "", "`results/robustness.json` retains every leave-training-task selector, every leave-test-task paired estimate, and each four-way model/harness exclusion evaluated on the original full-pool common test rows.", "Deletion total-variation distance remains unavailable because the frozen gold-deletion cache has one accepted repeat per level, below the required two.", "A high semantic margin is a response-effect property, not proof of correctness: the deterministic fixture includes a high-margin scorer with reversed human ordering.", "All intervals are 95% percentile intervals from 10,000 paired task-cluster draws at seed 20261008, p-val=n/a; they condition on cached scores, selectors, the fixed pool, and current raters and omit selector, model-population, and new-rater uncertainty.", f"Archived-baseline reproduction: {base['status']} over {base['checked_cells']} comparable cells at absolute tolerance {base['tolerance']:g}.", "", "## Artifacts", "", "Numerical tables: `results/configuration_overview.json`, `per_probe_task_components.json`, `selectors.json`, `evaluation.json`, `association.json`, `robustness.json`, `baseline_reproduction.json`, and `runtime.json`.", "", "**TLDR-end:** [cert-judge: 50_semantic_effect_margin_cached_judge_selection_train_val_test] The frozen semantic-margin selector does not show a positive historical cached-selection advantage over fixed H2 on the 29-file test support; all numerical artifacts and conditional uncertainty are committed.", "", "**Snapshot:**", "```text", f"margin selector: t2_sonnet5|D0", f"test support: {test['common_files']}/{test['declared_files']} files, {test['common_tasks']} tasks", f"margin Spearman: {margin['spearman']['value']:.3f}", f"fixed H2 Spearman: {h2['spearman']['value']:.3f}", f"paired delta: {delta['value']:.3f} [{delta['lo']:.3f}, {delta['hi']:.3f}]", f"validation: {val['status']} ({val['common_files']}/{val['declared_files']})", "```"]
    (E / "RESULTS_semantic_margin.md").write_text("\n".join(lines) + "\n")
if __name__ == "__main__": main()
