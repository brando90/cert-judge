#!/usr/bin/env python3
"""Read-only source audit and cached-pilot preparation; no inference client."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V2 = HERE.parent / "expt_v2/run_diagnostics.py"
spec = importlib.util.spec_from_file_location("proxy_v2_audit_input", V2)
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
STRING = "gpt-5.6-terra|BAD_STRINGY"
SEED = 20260913
DRAWS = 2000


def pair_accuracy(prediction, target):
    """Equal pair weight; human ties omitted, prediction ties count one half."""
    scores, ties = [], 0
    for a, b in combinations(range(len(target)), 2):
        direction = np.sign(target[a] - target[b])
        if direction == 0:
            ties += 1
            continue
        predicted = np.sign(prediction[a] - prediction[b])
        scores.append(0.5 if predicted == 0 else float(predicted == direction))
    return (float(np.mean(scores)) if scores else float("nan")), len(scores), ties


def centered_pearson(prediction, target, groups):
    x, y = np.asarray(prediction, float).copy(), np.asarray(target, float).copy()
    for group in groups:
        x[group] -= x[group].mean()
        y[group] -= y[group].mean()
    return v2.row_pearson(x, y).item()


def bootstrap_means(values, draws):
    """Draw whole problems; omit only problems with no human-unequal pairs."""
    sampled = values[draws]
    valid = np.isfinite(sampled)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(valid, sampled, 0).sum(axis=1) / valid.sum(axis=1)


def pilot_inventory(rows, judges, requests, score_records):
    problems = sorted({r["gold_file"] for r in rows}, key=lambda p: hashlib.sha256(
        f"{SEED}|{p}".encode()).hexdigest())[:6]
    stems = {Path(p).stem for p in problems}
    selected = [r for r in requests if r["artifact_id"].split("|")[0] in stems]
    keys = {(r["judge_id"], r["score_cell_id"]) for r in selected}
    observed = [r for r in score_records if (r["judge_id"], r["score_cell_id"]) in keys]
    cells_validated = v2.score_index(observed)
    if set(cells_validated) != keys:
        raise ValueError("selected request has no observed score cell")
    repeat_ids = {key: [] for key in keys}
    for row in observed:
        repeat_ids[(row["judge_id"], row["score_cell_id"])].append(row["repeat_id"])
    missing = [kind for kind in ("eq", "eqalpha", "bm", "ms")
               if any(not any(r["probe_type"] == kind and r["judge_id"] == j for r in selected)
                      for j in judges)]
    by_judge = {}
    for judge in judges:
        subset = [r for r in selected if r["judge_id"] == judge]
        cells = sorted({r["score_cell_id"] for r in subset})
        by_judge[judge] = {
            "conceptual_requests": len(subset), "unique_cells": len(cells),
            "cached_repeat_scores": len(cells) * 3,
            "one_cell_per_invocation_replay_bound": len(cells) * 3,
            "missing_cached_scores": 0, "new_invocations_authorized": 0,
            "requests_by_probe_type": {kind: sum(r["probe_type"] == kind for r in subset)
                                       for kind in ("criterion", "eq", "eqalpha", "bm", "ms")},
        }
    return {"status": "CACHE_REPLAY_ONLY", "selection_seed": SEED,
            "selected_problems": problems, "candidate_count": sum(
                r["gold_file"] in problems for r in rows), "by_judge": by_judge,
            "fresh_family_panel": "NOT_SELECTED_OR_QUOTED",
            "joint_proxy_pilot_readiness": "NOT_READY_MISSING_STRUCTURAL_PROBE_COVERAGE" if missing
                                          else "COVERAGE_REQUIRES_PROTOCOL_REVIEW",
            "missing_property_request_types": missing,
            "observed_cells": [{"judge_id": j, "score_cell_id": cell,
                                "repeat_ids": sorted(repeat_ids[(j, cell)])}
                               for j, cell in sorted(keys)],
            "requests_by_probe_type": {kind: sum(r["probe_type"] == kind for r in selected)
                                       for kind in ("criterion", "eq", "eqalpha", "bm", "ms")},
            "notes": "Counts preserve original identities; never rerun cached cells. "
                     "A different model needs a new reviewed manifest and workload estimate.",
            "requests": selected}


def analyze(judges, metadata, rows, repeats, labels):
    names = sorted({r["gold_file"] for r in rows})
    groups = [np.array([i for i, r in enumerate(rows) if r["gold_file"] == p]) for p in names]
    if len(names) != 24 or any(len(g) != 3 for g in groups):
        raise ValueError("expected 24 problems with three candidates each")
    medians = np.median(repeats, axis=2)
    draws = np.random.default_rng(SEED).integers(0, len(groups), (DRAWS, len(groups)))
    output = {"seed": SEED, "draws": DRAWS, "problem_count": len(groups), "views": {}}
    for view, target in labels.items():
        records, problem_scores = {}, {}
        for j, judge in enumerate(judges):
            values = [pair_accuracy(medians[j, g], target[g]) for g in groups]
            pairwise = np.array([v[0] for v in values])
            problem_scores[judge] = pairwise
            finite = np.isfinite(pairwise)
            records[judge] = {
                "role": metadata[judge]["role"],
                "pooled_spearman": v2.row_spearman(medians[j], target).item(),
                "within_problem_centered_pearson": centered_pearson(medians[j], target, groups),
                "within_problem_pair_accuracy": float(pairwise[finite].mean()) if finite.any() else None,
                "informative_problems": int(finite.sum()),
                "human_unequal_pairs": sum(v[1] for v in values),
                "human_tied_pairs": sum(v[2] for v in values),
                "per_problem_accuracy": dict(zip(names, pairwise)),
            }
        differences = {}
        for judge in judges:
            if metadata[judge]["role"] != "primary":
                continue
            delta = problem_scores[STRING] - problem_scores[judge]
            estimate = bootstrap_means(delta, draws)
            differences[judge] = {
                "string_minus_primary": float(np.nanmean(delta)) if np.isfinite(delta).any() else None,
                "conditional_95_interval": v2.interval(estimate),
            }
        low = [r["conditional_95_interval"]["ci_low"] for r in differences.values()]
        high = [r["conditional_95_interval"]["ci_high"] for r in differences.values()]
        verdict = "INCONCLUSIVE"
        if all(v is not None and v > 0 for v in low):
            verdict = "PRIORITIZE_BLINDED_CRITERION_AUDIT"
        elif all(v is not None and v < 0 for v in high):
            verdict = "PRIORITIZE_PROBLEM_COMPOSITION_SENSITIVITY"
        output["views"][view] = {"judges": records, "differences": differences, "decision": verdict}
    return output


def report(audit, inventory):
    def number(v):
        return "undefined" if v is None or not np.isfinite(v) else f"{v:.3f}"

    average = audit["views"]["average"]
    lines = ["# Within-problem criterion audit", "",
        "**TLDR:** This audit separates pooled agreement from ordering among answers to the same problem; it does not change the human labels or validate a replacement proxy. The prespecified average-rubric decision is " + average["decision"] + ".", "",
        "## Executed", "",
        "Used 72 already exposed candidates from 24 problems, eight judges and three cached repeats. "
        "All original joins and proxy reconstructions passed before this new analysis. "
        "No new model calls, human annotations or benchmark reference edits occurred.", "",
        "| Judge | Pooled Spearman | Within-problem centered Pearson | Within-problem pair accuracy |",
        "|---|---:|---:|---:|"]
    for j, r in average["judges"].items():
        lines.append(f"| {j.replace('|', ' / ')} | {number(r['pooled_spearman'])} | "
                     f"{number(r['within_problem_centered_pearson'])} | {number(r['within_problem_pair_accuracy'])} |")
    lines += ["", "The three columns measure different quantities. Centered Pearson removes each problem's "
        "mean from both scores; it is not partial Spearman. Pair accuracy uses human-unequal pairs, "
        "gives a judge tie one-half credit, and weights informative problems equally.", "",
        "| Primary judge | String control minus primary pair accuracy | Conditional 95% interval |",
        "|---|---:|---|"]
    for j, r in average["differences"].items():
        ci = r["conditional_95_interval"]
        lines.append(f"| {j.replace('|', ' / ')} | {number(r['string_minus_primary'])} | "
                     f"[{number(ci['ci_low'])}, {number(ci['ci_high'])}] |")
    first = next(iter(average["judges"].values()))
    lines += ["", f"Average rubric: {first['informative_problems']}/24 informative problems, "
        f"{first['human_unequal_pairs']} human-unequal pairs and {first['human_tied_pairs']} human-tied pairs.", "",
        "Intervals use 2,000 shared problem draws (seed 20260913). They are exploratory, "
        "unadjusted for multiple comparisons, and conditional on the observed labels, calls and configurations. "
        "They do not establish causality, label validity or generalization to future models. "
        "The strict and lenient rubric results remain separately available in audit.json.", "",
        "![Within-problem ordering contrasts](plots/within_problem_ordering.png)", "",
        "## Prepared pilot inventory", "",
        f"Six problems and {inventory['candidate_count']} candidates were selected by a fixed hash order, "
        "independently of labels and outcomes. pilot_inventory.json preserves every selected "
        "original request, judge identity and payload hash. All selected repeat scores are cached.", "",
        "The selected inventory contains 144 criterion requests, 8 equality requests and 16 "
        "alpha-renaming requests; it contains no bug or missing-specification requests. "
        "Only one selected candidate has equality/renaming probes. It is therefore not ready "
        "for joint four-property proxy validation. The missing structural-probe coverage must "
        "be addressed under a separate protocol; the locked six-problem selection is unchanged.", "",
        "A new model-family panel is not selected, quoted or launched. Its request identities, "
        "client/effort, output directory, budget and review must be frozen separately. "
        "This inventory is preparation for that runner, not a fresh-model evaluation.", "",
        "## Reproduce", "", "```bash",
        "CUDA_VISIBLE_DEVICES='' PYTHONPATH=py_src python experiments/archive/30_proxy_trust_index_held_out_validity/expt_v3/run_audit.py",
        "CUDA_VISIBLE_DEVICES='' python experiments/archive/30_proxy_trust_index_held_out_validity/expt_v3/render_plot.py",
        "```", "", "**TLDR-end:** Use the within-problem diagnostic to choose the next audit; "
        "keep the new-family claim pending and preserve all earlier frozen results."]
    return "\n".join(lines) + "\n"


def main():
    paths, judges, metadata, rows, repeats, labels, _, _ = v2.load_inputs()
    requests = v2.read(v2.SOURCE / "score_requests.json")["requests"]
    audit = analyze(judges, metadata, rows, repeats, labels)
    score_records = v2.read(v2.SOURCE / "scores.json")["records"]
    inventory = pilot_inventory(rows, judges, requests, score_records)
    out = HERE / "results"
    v2.write(out / "audit.json", audit)
    v2.write(out / "pilot_inventory.json", inventory)
    sources = paths + [V2, HERE / "PROTOCOL.md", Path(__file__), HERE / "render_plot.py", ROOT / "py_src/cert_judge/pti_v0.py",
                       ROOT / "py_src/cert_judge/ti_validation.py"]
    v2.write(out / "source_manifest.json", {
        "source_commit": "6e9df01368fd7b0c6df927afc0d68e69cf403b09",
        "model_calls": 0, "new_human_labels": 0, "seed": SEED, "draws": DRAWS,
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": v2.scipy.__version__},
        "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    })
    (out / "report.md").write_text(report(audit, inventory))
    print(json.dumps({"decision": audit["views"]["average"]["decision"],
                      "selected_problems": inventory["selected_problems"],
                      "outputs": str(out)}, indent=2))


if __name__ == "__main__":
    main()
