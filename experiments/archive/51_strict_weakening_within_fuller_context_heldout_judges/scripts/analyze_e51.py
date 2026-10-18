#!/usr/bin/env python3
"""TLDR: Experiment 51 — join experiment 42's cached strict-weakening accuracy to experiment 39's
held-out criterion, fuller-context test judges only. Zero inference. Run from the repository root:

    python3 experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/scripts/analyze_e51.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
E51 = HERE.parent
REPO = next(q for q in E51.parents if (q / "py_src" / "cert_judge").is_dir())
E39 = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E42 = REPO / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges"
sys.path.insert(0, str(E39 / "scripts"))
import analysis_lib as A  # noqa: E402

FULLER = {"D0", "H0", "H1", "H2", "R4"}
SEED = 51
DRAWS = 10000
GATE = 0.45
GATE_P = 0.05
TOL = 1e-9
RESULTS = E51 / "results"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1) + "\n")


def prompt_of(config: str) -> str:
    return config.split("|", 1)[1]


def model_of(config: str) -> str:
    return config.split("|", 1)[0]


def fmt(v, digits=3):
    if v is None:
        return "unavailable"
    return f"{v:.{digits}f}"


def reading(spearman, p, n) -> str:
    """Locked readings in PROTOCOL.md. REVERSED wins over a non-significant p-value."""
    if spearman is None or n < A.MIN_UNITS:
        return "NOT_COMPUTABLE"
    if spearman <= 0:
        return "REVERSED"
    if spearman >= GATE and p is not None and p < GATE_P:
        return "PASS"
    return "FAIL"


def associate(pairs: list[dict], seed: int = SEED) -> dict:
    x = [p["x"] for p in pairs]
    y = [p["y"] for p in pairs]
    out = {
        "n": len(pairs),
        "configs": [p["config"] for p in pairs],
        "spearman": None,
        "pearson": None,
        "kendall": None,
        "ci": None,
        "permutation_p": None,
        "reading": "NOT_COMPUTABLE",
    }
    if len(pairs) < A.MIN_UNITS:
        return out
    spearman = A.spearman(x, y)
    out.update(
        spearman=spearman,
        pearson=A.pearson(x, y),
        kendall=A.kendall(x, y),
        ci=A.bootstrap_ci(x, y, A.spearman, DRAWS, seed),
        permutation_p=A.permutation_p(x, y, A.spearman, DRAWS, seed),
    )
    out["reading"] = reading(out["spearman"], out["permutation_p"], out["n"])
    xs = [p["x"] for p in pairs]
    out["n_x_at_one"] = sum(1 for v in xs if abs(v - 1.0) <= 1e-12)
    out["x_min"] = min(xs) if xs else None
    out["x_max"] = max(xs) if xs else None
    return out


def within_model_p(pairs: list[dict], seed: int = SEED) -> dict:
    """One-sided permutation of the criterion inside each judge-model key. p-val uses (k+1)/(n+1)."""
    if len(pairs) < A.MIN_UNITS:
        return {"permutation_p": None, "draws": DRAWS, "test": "within-model criterion permutation"}
    x = [p["x"] for p in pairs]
    y = [p["y"] for p in pairs]
    observed = A.spearman(x, y)
    if observed is None:
        return {"permutation_p": None, "draws": DRAWS, "observed": None}
    by_model: dict[str, list[int]] = {}
    for i, p in enumerate(pairs):
        by_model.setdefault(p["model"], []).append(i)
    rng = random.Random(seed)
    k = 0
    finite = 0
    for _ in range(DRAWS):
        y_work = list(y)
        for idxs in by_model.values():
            vals = [y[i] for i in idxs]
            rng.shuffle(vals)
            for i, v in zip(idxs, vals):
                y_work[i] = v
        stat = A.spearman(x, y_work)
        if stat is not None:
            finite += 1
            if stat >= observed - 1e-12:
                k += 1
    return {
        "permutation_p": (k + 1) / (DRAWS + 1),
        "draws": DRAWS,
        "finite_draws": finite,
        "observed": observed,
        "models": {m: len(ix) for m, ix in sorted(by_model.items())},
        "test": "one-sided permutation of the criterion within judge model",
    }


def model_cluster_ci(pairs: list[dict], seed: int = SEED) -> dict:
    """Resample judge-model keys with replacement; keep every configuration of a drawn model."""
    if len(pairs) < 3:
        return {"lo": None, "hi": None, "valid_draws": 0, "p_val": "n/a"}
    by_model: dict[str, list[dict]] = {}
    for p in pairs:
        by_model.setdefault(p["model"], []).append(p)
    keys = sorted(by_model)
    rng = random.Random(seed)
    values = []
    for _ in range(DRAWS):
        chosen = [keys[rng.randrange(len(keys))] for _ in keys]
        x, y = [], []
        for m in chosen:
            for row in by_model[m]:
                x.append(row["x"])
                y.append(row["y"])
        stat = A.spearman(x, y)
        if stat is not None:
            values.append(stat)
    values.sort()
    if not values:
        return {"lo": None, "hi": None, "valid_draws": 0, "p_val": "n/a"}
    a = 0.025
    return {
        "lo": values[int(a * (len(values) - 1))],
        "hi": values[int((1 - a) * (len(values) - 1))],
        "valid_draws": len(values),
        "p_val": "n/a",
        "n_models": len(keys),
    }


def g0() -> dict:
    units = read_json(E39 / "results/units_test.json")["units"]
    receipt = read_json(E39 / "results/TEST_RECEIPT.json")["reported"]["C_ms_gold"]["test"]
    got = A.association(units, "C_ms_gold", "heldout", DRAWS, 39)
    checks = {
        "n_units": (got["n_units"], receipt["n_units"]),
        "spearman": (got["spearman"], receipt["spearman"]),
        "kendall": (got["kendall"], receipt["kendall"]),
        "pearson": (got["pearson"], receipt["pearson"]),
        "ci_lo": (got["ci"]["lo"], receipt["ci"]["lo"]),
        "ci_hi": (got["ci"]["hi"], receipt["ci"]["hi"]),
        "permutation_p": (got["permutation_p"], receipt["permutation_p"]),
    }
    ok = all(abs(float(a) - float(b)) <= TOL for a, b in checks.values())
    return {"pass": ok, "checks": {k: {"got": a, "receipt": b} for k, (a, b) in checks.items()}}


def screen_index(screen_units: list[dict]) -> dict[str, dict]:
    return {u["config"]: u for u in screen_units}


def strict_value(unit: dict):
    block = ((unit.get("metrics") or {}).get("file_level_strict_only") or {}).get("weakening") or {}
    return block.get("value"), block.get("n"), block.get("n_tasks")


def primary_weakening(unit: dict):
    block = (unit.get("metrics") or {}).get("weakening") or {}
    return block.get("value")


def rows_for_split(e39_units: list[dict], screen: dict[str, dict], split: str) -> tuple[list[dict], dict]:
    kept, dropped = [], {"not_fuller": 0, "wrong_split": 0, "control": 0, "missing_screen": 0,
                         "missing_strict": 0, "criterion_not_computed": 0, "split_mismatch": 0}
    for u in e39_units:
        config = u["config"]
        if u.get("kind") == "control" or config.startswith("ctl|"):
            dropped["control"] += 1
            continue
        if u.get("split") != split:
            dropped["wrong_split"] += 1
            continue
        if prompt_of(config) not in FULLER:
            dropped["not_fuller"] += 1
            continue
        s = screen.get(config)
        if s is None:
            dropped["missing_screen"] += 1
            continue
        if s.get("split") != split:
            dropped["split_mismatch"] += 1
            continue
        value, n_probes, n_tasks = strict_value(s)
        crit = (u.get("criteria") or {}).get("heldout") or {}
        if crit.get("status") != "COMPUTED" or crit.get("spearman") is None:
            dropped["criterion_not_computed"] += 1
            continue
        if value is None:
            dropped["missing_strict"] += 1
            continue
        kept.append({
            "config": config,
            "model": model_of(config),
            "prompt": prompt_of(config),
            "x": float(value),
            "y": float(crit["spearman"]),
            "strict_n": n_probes,
            "strict_n_tasks": n_tasks,
            "primary_weakening": primary_weakening(s),
            "c_ms_gold": (u.get("indices") or {}).get("C_ms_gold"),
        })
    return kept, dropped


def comparator(pairs: list[dict], key: str) -> dict:
    sub = [dict(p, x=p[key]) for p in pairs if p.get(key) is not None]
    out = associate(sub)
    out["dropped_missing"] = len(pairs) - len(sub)
    out["name"] = key
    return out


def render(payload: dict) -> str:
    primary = payload["primary"]
    ci = primary.get("ci") or {}
    sens = payload["within_model"]
    cluster = payload["model_cluster_ci"]
    lines = [
        "# Strict weakening inside fuller-context held-out judges",
        "",
        "**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/RESULTS_strict_within_family.md>",
        "",
        "**TLDR:** "
        f"On the fuller-context held-out judges ({primary['n']} configurations), strict weakening accuracy versus the existing human-agreement criterion is "
        f"Spearman {fmt(primary['spearman'])} [{fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}] "
        f"p-val={fmt(primary['permutation_p'], 4)} "
        f"(one-sided configuration permutation, {DRAWS} draws, seed {SEED}). "
        f"Reading: **{primary['reading']}** against experiment 39's gate (Spearman ≥ {GATE}, p-val < {GATE_P}). "
        f"Pearson {fmt(primary['pearson'])}, Kendall {fmt(primary['kendall'])}. "
        "No new judge calls and no new ratings.",
        "",
        "## Question",
        "",
        "Does file-level strict weakening accuracy rank the judges one would deploy, on configurations that were not used to choose experiment 39's deletion screen?",
        "",
        "## Reproduction",
        "",
        f"Experiment 39's registered `C_ms_gold` test association reproduced: **{'PASS' if payload['g0']['pass'] else 'FAIL'}** (absolute tolerance {TOL}).",
        "",
        "## Primary result",
        "",
        "Population: experiment 39 test-split configurations with prompts D0, H0, H1, H2 or R4, joined to experiment 42's stored `file_level_strict_only.weakening` value and to `criteria.heldout` (status COMPUTED). The interval resamples configurations, which share judge models, so it is narrower than a model-cluster interval.",
        "",
        "| Statistic | Value |",
        "|---|---|",
        f"| Configurations | {primary['n']} |",
        f"| Spearman [95% configuration bootstrap] | {fmt(primary['spearman'])} [{fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}] |",
        f"| Pearson | {fmt(primary['pearson'])} |",
        f"| Kendall tau-b | {fmt(primary['kendall'])} |",
        f"| One-sided permutation p-val | {fmt(primary['permutation_p'], 4)} |",
        f"| Reading | {primary['reading']} |",
        f"| Strict-accuracy values exactly 1 | {primary.get('n_x_at_one')} of {primary['n']} (min {fmt(primary.get('x_min'))}, max {fmt(primary.get('x_max'))}) |",
        f"| Finite configuration-bootstrap draws | {ci.get('valid_draws')} of {DRAWS} |",
        "",
        "The configuration interval's upper end is above zero, so this is not a demonstration that the population correlation is negative. "
        "The reading REVERSED is the locked point-estimate rule (Spearman ≤ 0). "
        "The one-sided p-value tests a positive association. "
        f"{primary.get('n_x_at_one')} of {primary['n']} held-out fuller-context judges score exactly 1 on strict weakening, so the score has almost no room to rank them.",
        "",
        "Within-model sensitivity (not part of the gate): "
        f"p-val={fmt(sens.get('permutation_p'), 4)} by permuting the criterion inside each judge model "
        f"({sens.get('models')}). "
        + (
            "The association is not resolved within judge models."
            if sens.get("permutation_p") is None or sens.get("permutation_p") >= GATE_P
            else "The within-model permutation also falls below 0.05."
        ),
        "",
        "Model-cluster interval (resample judge-model keys, 10,000 draws, seed 51; p-val=n/a): "
        f"{fmt(cluster.get('lo'))} to {fmt(cluster.get('hi'))} "
        f"({cluster.get('valid_draws')} finite draws, {cluster.get('n_models')} models).",
        "",
        "## Same configurations, other cached scores",
        "",
        "These rows use the primary configuration list. They are comparators, not a second gate.",
        "",
        "| Score | n | Spearman [95% configuration bootstrap] | Pearson | Kendall | p-val | Reading |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for name, block in (("strict weakening (headline)", primary), ("primary weakening, all probes", payload["primary_weakening"]), ("C_ms_gold", payload["c_ms_gold"])):
        bci = block.get("ci") or {}
        lines.append(
            f"| {name} | {block['n']} | {fmt(block['spearman'])} [{fmt(bci.get('lo'))}, {fmt(bci.get('hi'))}] | "
            f"{fmt(block['pearson'])} | {fmt(block['kendall'])} | {fmt(block['permutation_p'], 4)} | {block['reading']} |"
        )
    lines += [
        "",
        "## Descriptive splits (not the verdict)",
        "",
        "| Split | n | At 1 | Min score | Spearman [95% configuration bootstrap] | p-val | Reading |",
        "|---|---:|---:|---:|---|---:|---|",
    ]
    for split, block in payload["descriptive"].items():
        bci = block.get("ci") or {}
        lines.append(
            f"| {split} | {block['n']} | {block.get('n_x_at_one')} | {fmt(block.get('x_min'))} | "
            f"{fmt(block['spearman'])} [{fmt(bci.get('lo'))}, {fmt(bci.get('hi'))}] | "
            f"{fmt(block['permutation_p'], 4)} | {block['reading']} |"
        )
    lines.append("")
    lines.append("Train and validation were locked as descriptive. The validation split meets the numerical gate and the test split does not; the validation split does not replace the test.")
    lines += [
        "",
        "## What was excluded",
        "",
        "```",
        json.dumps(payload["dropped_test"], indent=1),
        "```",
        "",
        "## Scope",
        "",
        "This is a cached association on the judges and ratings experiment 39 already used. It does not change that experiment's registered pass, and it is not a test on new items or new raters. A pass would still need a prospective check. A failure means these probes do not supply a within-family screen.",
        "",
        f"**TLDR-end:** [cert-judge: strict weakening within fuller-context judges] {primary['reading']}: Spearman {fmt(primary['spearman'])} [{fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}] p-val={fmt(primary['permutation_p'], 4)} on {primary['n']} held-out fuller-context configurations.",
        "",
    ]
    return "\n".join(lines)


def ledger(payload: dict) -> str:
    primary = payload["primary"]
    ci = primary.get("ci") or {}
    return "\n".join([
        "# Strict weakening within fuller-context judges",
        "",
        "**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/results.md>",
        "",
        f"**Status:** DONE ({payload['written_utc']})",
        "",
        f"**Last updated:** 10-18-2026",
        "",
        "| Phase | State | Result |",
        "|---|---|---|",
        f"| Protocol locked | DONE | Gate Spearman ≥ {GATE} and one-sided p-val < {GATE_P}; fuller-context test judges |",
        f"| Reproduction of the registered deletion-score test | {'PASS' if payload['g0']['pass'] else 'FAIL'} | tolerance {TOL} |",
        f"| Primary association | DONE | {primary['reading']}: Spearman {fmt(primary['spearman'])} [{fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}] p-val={fmt(primary['permutation_p'], 4)} on {primary['n']} configurations |",
        "",
        "Report: [RESULTS_strict_within_family.md](RESULTS_strict_within_family.md). Inputs: `results/input_manifest.json`. Pairs: `results/primary_pairs.json`.",
        "",
        "No model calls. No set-N sheets.",
        "",
        f"**TLDR-end:** [cert-judge: strict weakening within fuller-context judges] {primary['reading']} on {primary['n']} held-out fuller-context configurations, Spearman {fmt(primary['spearman'])} [{fmt(ci.get('lo'))}, {fmt(ci.get('hi'))}] p-val={fmt(primary['permutation_p'], 4)}.",
        "",
    ])


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    inputs = {
        "units_test": E39 / "results/units_test.json",
        "units_train_val": E39 / "results/units_train_val.json",
        "test_receipt": E39 / "results/TEST_RECEIPT.json",
        "semantic_screen": E42 / "results/semantic_screen.json",
        "protocol": E51 / "PROTOCOL.md",
    }
    manifest = {name: {"path": str(path.relative_to(REPO)), "sha256": sha256(path)} for name, path in inputs.items()}
    write_json(RESULTS / "input_manifest.json", {"written_utc": datetime.now(timezone.utc).isoformat(), "inputs": manifest})

    gate = g0()
    write_json(RESULTS / "g0_reproduction.json", gate)
    if not gate["pass"]:
        print("G0 FAIL; no verdict written")
        return 1

    screen = screen_index(read_json(inputs["semantic_screen"])["units"])
    train_val = read_json(inputs["units_train_val"])["units"]
    by_split = {
        "test": read_json(inputs["units_test"])["units"],
        "val": [u for u in train_val if u.get("split") == "val"],
        "train": [u for u in train_val if u.get("split") == "train"],
    }
    test_rows, dropped = rows_for_split(by_split["test"], screen, "test")
    primary = associate(test_rows)
    payload = {
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "g0": gate,
        "dropped_test": dropped,
        "primary": primary,
        "within_model": within_model_p(test_rows),
        "model_cluster_ci": model_cluster_ci(test_rows),
        "primary_weakening": comparator(test_rows, "primary_weakening"),
        "c_ms_gold": comparator(test_rows, "c_ms_gold"),
        "descriptive": {},
    }
    for split in ("train", "val"):
        rows, _drop = rows_for_split(by_split[split], screen, split)
        payload["descriptive"][split] = associate(rows)
    write_json(RESULTS / "primary_pairs.json", test_rows)
    write_json(RESULTS / "association.json", payload)
    report = render(payload)
    (E51 / "RESULTS_strict_within_family.md").write_text(report)
    (E51 / "results.md").write_text(ledger(payload))
    print(payload["primary"]["reading"], payload["primary"]["spearman"], payload["primary"]["permutation_p"], payload["primary"]["n"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
