#!/usr/bin/env python3
"""TLDR: Experiment 39's analysis driver — per-configuration criterion (agreement with the expert ratings on
the 45 held-out items), label-free components and indices; the pre-registered selection (rank candidates on the
TRAIN judge models, keep the top three, pick by VAL) with the test-model rows sealed under private/; the one-shot
TEST unlock bound to the committed FINALISTS.json; and the Markdown report. No model calls.

Usage:  analyze.py units            # criterion + components + indices for every harvested configuration
        analyze.py select           # train -> val selection; writes results/FINALISTS.json, results/SELECTION.json
        analyze.py test --finalists-commit <sha>   # one-shot test on the sealed test-model rows
        analyze.py report           # results/RESULTS_proxy_index_train_val_test.md from whatever exists
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import analysis_lib as A                                      # noqa: E402
import e39                                                    # noqa: E402

UNITS_OPEN = e39.RESULTS / "units_train_val.json"
UNITS_SEALED = e39.PRIVATE / "units_test_sealed.json"
FINALISTS = e39.RESULTS / "FINALISTS.json"
SELECTION = e39.RESULTS / "SELECTION.json"
TEST_RECEIPT = e39.RESULTS / "TEST_RECEIPT.json"
GATE_TEST_SPEARMAN = 0.45
GATE_PERMUTATION_P = 0.05
MATCH_TOLERANCE = 0.30                 # "the two correlations match": |train - test| within this band


def load_units(allow_unvalidated: bool = False) -> tuple[list[dict], dict]:
    manifest = e39.read_json(e39.RESULTS / "probe_manifest.json")
    probes = A.valid_probes(manifest, allow_unvalidated)
    items = e39.load_items()
    units = []
    for path in sorted((e39.RESULTS / "harvest").glob("*.json")):
        sc = A.Scores(e39.read_json(path))
        crit = {"heldout": A.criterion(sc, items, e39.CRITERION_SPLITS), "test_items": A.criterion(sc, items, ("test",)),
                "val_items": A.criterion(sc, items, ("val",)), "train_items": A.criterion(sc, items, ("train",)),
                "all_items": A.criterion(sc, items, ("train", "val", "test"))}
        comps = A.components(sc, probes)
        frozen_pti = A.pti_v0_frozen(sc, probes)
        units.append({"config": sc.config, "family": sc.family, "split": sc.split, "kind": sc.kind, "status_counts": sc.status_counts,
                      "criteria": crit, "components": comps, "pti_v0": frozen_pti, "ti_var_raw": A.ti_var_raw(sc, probes),
                      "indices": {"PTI_v0_frozen": frozen_pti["value"]}})
    # TI_var normalization is frozen from the TRAIN LLM units only, then applied to every unit.
    train_raw = [u["ti_var_raw"] for u in units if u["split"] == "train" and u["kind"] == "llm" and u["ti_var_raw"]]
    norm = None
    if len(train_raw) >= 2:
        norm = {"V_c": (min(r["V_c"] for r in train_raw), max(r["V_c"] for r in train_raw)),
                "V_s": (min(r["V_s"] for r in train_raw), max(r["V_s"] for r in train_raw)), "n_train_units": len(train_raw)}
    for u in units:
        u["indices"]["TI_var_trainnorm"] = A.ti_var(u["ti_var_raw"], norm) if (norm and u["ti_var_raw"]) else None
        for name in A.CANDIDATES:
            if A.CANDIDATES[name][0] != "frozen":
                u["indices"][name] = A.candidate_value(name, u["components"], u["indices"])
    return units, {"ti_var_norm": norm, "n_valid_probes": {k: len(v) for k, v in probes.items()}}


def split_half_reliability(units: list[dict]) -> dict:
    """How reproducible is the criterion RANKING of configurations? Spearman across units between the criterion on
    the validation items and on the test items; an attenuation bound for any proxy."""
    llm = [u for u in units if u["kind"] == "llm"]
    x = [(u["criteria"]["val_items"] or {}).get("spearman") for u in llm]
    y = [(u["criteria"]["test_items"] or {}).get("spearman") for u in llm]
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    return {"n_units": len(pairs), "spearman_val_items_vs_test_items": A.spearman([a for a, _ in pairs], [b for _, b in pairs]) if len(pairs) >= A.MIN_UNITS else None,
            "human_ceiling_heldout_items": A.HUMAN_CEILING_HELDOUT}


def cmd_units(args) -> int:
    units, meta = load_units(args.allow_unvalidated)
    open_units = [u for u in units if u["split"] in ("train", "val")]
    sealed = [u for u in units if u["split"] == "test"]
    e39.write_json(UNITS_OPEN, {"written_utc": e39.stamp(), "meta": meta, "n_units": len(open_units), "units": open_units,
                                "reliability_all_llm_units": split_half_reliability(units)})
    e39.write_json(UNITS_SEALED, {"written_utc": e39.stamp(), "meta": meta, "n_units": len(sealed), "units": sealed})
    print(json.dumps({"open_units": len(open_units), "sealed_test_units": len(sealed), "ti_var_norm": meta["ti_var_norm"],
                      "criterion_heldout": {u["config"]: (u["criteria"]["heldout"] or {}).get("spearman") for u in open_units}}, indent=1))
    return 0


def cmd_select(args) -> int:
    blob = e39.read_json(UNITS_OPEN)
    units = blob["units"]
    train = [u for u in units if u["split"] == "train" and u["kind"] == "llm"]
    train_ctl = [u for u in units if u["split"] == "train"]
    val = [u for u in units if u["split"] == "val" and u["kind"] == "llm"]
    names = list(A.CANDIDATES)
    train_rank = A.rank_candidates(train, names)
    train_rank_ctl = A.rank_candidates(train_ctl, names)
    val_rows = {r["index"]: r for r in A.rank_candidates(val, names)}
    finalists = [r for r in train_rank if r["spearman"] is not None][:3]
    for f in finalists:
        f["val"] = {k: val_rows[f["index"]][k] for k in ("n_units", "spearman", "kendall", "pearson")}
    chosen = sorted([f for f in finalists if f["val"]["spearman"] is not None],
                    key=lambda f: (-f["val"]["spearman"], f["n_components"], f["index"]))
    selected = chosen[0]["index"] if chosen else None
    receipt = {"written_utc": e39.stamp(), "rule": ("rank every pre-registered candidate by Spearman with the held-out criterion over "
               "the TRAIN judge models (LLM configurations only; ties -> fewer components -> name); keep the top three; select the "
               "finalist with the highest VAL Spearman (same tie-break). Frozen before any test-model row was read."),
               "n_train_units": len(train), "n_train_units_with_controls": len(train_ctl), "n_val_units": len(val),
               "candidates": {k: {"aggregation": v[0], "components": list(v[1])} for k, v in A.CANDIDATES.items()},
               "train_ranking": train_rank, "train_ranking_with_controls": train_rank_ctl,
               "val_all_candidates": [val_rows[n] for n in names], "finalists": finalists, "selected": selected,
               "always_reported": ["PTI_v0_frozen", "TI_var_trainnorm"], "ti_var_norm": blob["meta"]["ti_var_norm"]}
    e39.write_json(FINALISTS, {"written_utc": receipt["written_utc"], "finalists": [f["index"] for f in finalists], "selected": selected,
                               "always_reported": receipt["always_reported"], "ti_var_norm": blob["meta"]["ti_var_norm"],
                               "units_open_sha256": e39.sha_file(UNITS_OPEN)})
    e39.write_json(SELECTION, receipt)
    print(json.dumps({"selected": selected, "finalists": [(f["index"], f["spearman"], f["val"]["spearman"]) for f in finalists],
                      "train_top5": [(r["index"], r["spearman"]) for r in train_rank[:5]]}, indent=1))
    return 0


def finalists_commit() -> str | None:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(FINALISTS)], cwd=str(e39.E), capture_output=True, text=True, timeout=60)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def cmd_test(args) -> int:
    if not FINALISTS.exists():
        raise SystemExit("results/FINALISTS.json missing: run `analyze.py select` and commit it first")
    fin = e39.read_json(FINALISTS)
    committed = finalists_commit()
    if not args.allow_uncommitted and (committed is None or committed != args.finalists_commit):
        raise SystemExit(f"FINALISTS.json is not committed at {args.finalists_commit!r} (git says {committed!r}); refusing to unlock the test split")
    if e39.sha_file(UNITS_OPEN) != fin["units_open_sha256"]:
        raise SystemExit("units_train_val.json changed after selection; refusing to unlock the test split")
    sealed = e39.read_json(UNITS_SEALED)["units"]
    test = [u for u in sealed if u["kind"] == "llm"]
    open_units = e39.read_json(UNITS_OPEN)["units"]
    train = [u for u in open_units if u["split"] == "train" and u["kind"] == "llm"]
    val = [u for u in open_units if u["split"] == "val" and u["kind"] == "llm"]
    reported = [fin["selected"]] + [n for n in fin["always_reported"] if n != fin["selected"]] if fin["selected"] else list(fin["always_reported"])
    results = {}
    for name in reported:
        results[name] = {"test": A.association(test, name), "val": A.association(val, name, with_uncertainty=False),
                         "train": A.association(train, name, with_uncertainty=False)}
    secondary = {name: A.association(test, name, with_uncertainty=False) for name in A.CANDIDATES if name not in reported}
    sel = results.get(fin["selected"]) if fin["selected"] else None
    gate = None
    if sel and sel["test"]["spearman"] is not None:
        rho, p = sel["test"]["spearman"], sel["test"]["permutation_p"]
        gap = None if sel["train"]["spearman"] is None else abs(sel["train"]["spearman"] - rho)
        gate = {"index": fin["selected"], "test_spearman": rho, "gate_spearman": GATE_TEST_SPEARMAN, "permutation_p": p,
                "gate_p": GATE_PERMUTATION_P, "train_test_gap": gap, "match_tolerance": MATCH_TOLERANCE,
                "PASS": bool(rho >= GATE_TEST_SPEARMAN and p is not None and p < GATE_PERMUTATION_P),
                "correlations_match": None if gap is None else bool(gap <= MATCH_TOLERANCE)}
    receipt = {"written_utc": e39.stamp(), "finalists_commit": args.finalists_commit, "finalists_sha256": e39.sha_file(FINALISTS),
               "n_test_units": len(test), "test_units": [u["config"] for u in test], "reported": results, "secondary_test_only": secondary,
               "gate": gate, "sealed_units_sha256": e39.sha_file(UNITS_SEALED)}
    e39.write_json(TEST_RECEIPT, receipt)
    e39.write_json(e39.RESULTS / "units_test.json", {"written_utc": e39.stamp(), "units": sealed, "unlocked_by": receipt["finalists_commit"]})
    print(json.dumps({"gate": gate, "reported": {k: {s: v[s]["spearman"] for s in ("train", "val", "test")} for k, v in results.items()}}, indent=1))
    return 0


def fmt(v, nd=3):
    return "—" if v is None else f"{v:.{nd}f}"


def cmd_report(args) -> int:
    lines = ["# Experiment 39 results: label-free proxy index, train/val/test over judge models", "",
             f"**Doc link:** <https://github.com/brando90/cert-judge/blob/main/{e39.E.relative_to(e39.REPO)}/results/RESULTS_proxy_index_train_val_test.md>", "",
             f"Generated {e39.stamp()} by `scripts/analyze.py report`. Numbers are Spearman unless stated; n is the count behind each one.", ""]
    if not UNITS_OPEN.exists():
        lines += ["_No units analysed yet._"]
    else:
        blob = e39.read_json(UNITS_OPEN)
        units = list(blob["units"])
        if (e39.RESULTS / "units_test.json").exists():
            units += e39.read_json(e39.RESULTS / "units_test.json")["units"]
        rel = blob.get("reliability_all_llm_units", {})
        lines += ["## Criterion: agreement with the expert coverage ratings", "",
                  f"Human ceiling on the 45 held-out items: {A.HUMAN_CEILING_HELDOUT}. Criterion ranking reproducibility (val items vs test items, "
                  f"over {rel.get('n_units')} LLM configurations): {fmt(rel.get('spearman_val_items_vs_test_items'))}.", "",
                  "| Configuration | Split | Held-out ρ [95% CI] (n) | Test-item ρ (n) | All-item ρ (n) | Stability | PTI-v0 frozen | TI_var (train-norm) |", "|---|---|---|---|---|---|---|---|"]
        for u in sorted(units, key=lambda u: (u["split"], u["config"])):
            h, t, a = u["criteria"]["heldout"], u["criteria"]["test_items"], u["criteria"]["all_items"]
            ci = h.get("ci") or {}
            lines.append(f"| `{u['config']}` | {u['split']} | {fmt(h['spearman'])} [{fmt(ci.get('lo'), 2)}, {fmt(ci.get('hi'), 2)}] ({h['n_items']}) | "
                         f"{fmt(t['spearman'])} ({t['n_items']}) | {fmt(a['spearman'])} ({a['n_items']}) | {fmt(u['components']['stab']['value'])} | "
                         f"{fmt(u['indices'].get('PTI_v0_frozen'))} ({u['pti_v0']['status']}) | {fmt(u['indices'].get('TI_var_trainnorm'))} |")
        lines += ["", "## Components (label-free)", "", "| Configuration | " + " | ".join(A.COMPONENTS) + " |", "|---|" + "---|" * len(A.COMPONENTS)]
        for u in sorted(units, key=lambda u: (u["split"], u["config"])):
            lines.append(f"| `{u['config']}` | " + " | ".join(f"{fmt(u['components'][c]['value'], 2)} ({u['components'][c]['n']}/{u['components'][c]['declared']})" for c in A.COMPONENTS) + " |")
    if SELECTION.exists():
        sel = e39.read_json(SELECTION)
        lines += ["", "## Selection on the train judge models, checked on the val judge models", "",
                  f"Selected: **{sel['selected']}**. Rule: {sel['rule']}", "",
                  "| Candidate | Components | Train ρ (n) | Train ρ with controls (n) | Val ρ (n) |", "|---|---|---|---|---|"]
        ctl = {r["index"]: r for r in sel["train_ranking_with_controls"]}
        val = {r["index"]: r for r in sel["val_all_candidates"]}
        for r in sel["train_ranking"]:
            lines.append(f"| {r['index']} | {r['n_components']} | {fmt(r['spearman'])} ({r['n_units']}) | {fmt(ctl[r['index']]['spearman'])} ({ctl[r['index']]['n_units']}) | "
                         f"{fmt(val[r['index']]['spearman'])} ({val[r['index']]['n_units']}) |")
    if TEST_RECEIPT.exists():
        rec = e39.read_json(TEST_RECEIPT)
        lines += ["", "## One-shot test on the held-out judge models", "", f"Test units ({rec['n_test_units']}): " + ", ".join(f"`{c}`" for c in rec["test_units"]), "",
                  "| Index | Train ρ (n) | Val ρ (n) | Test ρ [95% CI] (n) | Test τ-b | Test Pearson | Permutation p |", "|---|---|---|---|---|---|---|"]
        for name, r in rec["reported"].items():
            t = r["test"]
            ci = t.get("ci") or {}
            lines.append(f"| **{name}** | {fmt(r['train']['spearman'])} ({r['train']['n_units']}) | {fmt(r['val']['spearman'])} ({r['val']['n_units']}) | "
                         f"{fmt(t['spearman'])} [{fmt(ci.get('lo'), 2)}, {fmt(ci.get('hi'), 2)}] ({t['n_units']}) | {fmt(t['kendall'])} | {fmt(t['pearson'])} | {fmt(t['permutation_p'], 4)} |")
        g = rec.get("gate")
        if g:
            lines += ["", f"**Pre-registered gate for `{g['index']}`:** test Spearman {fmt(g['test_spearman'])} (gate ≥ {g['gate_spearman']}), permutation p "
                      f"{fmt(g['permutation_p'], 4)} (gate < {g['gate_p']}) → **{'PASS' if g['PASS'] else 'FAIL'}**; train−test gap {fmt(g['train_test_gap'])} "
                      f"(match tolerance {g['match_tolerance']}) → correlations {'match' if g['correlations_match'] else 'do not match'}."]
        lines += ["", "Secondary (test only, not pre-registered): " + ", ".join(f"{k} {fmt(v['spearman'])} (n={v['n_units']})" for k, v in rec["secondary_test_only"].items())]
    out = e39.RESULTS / "RESULTS_proxy_index_train_val_test.md"
    out.write_text("\n".join(lines) + "\n")
    print(str(out))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("units"); u.add_argument("--allow-unvalidated", action="store_true")
    sub.add_parser("select")
    t = sub.add_parser("test"); t.add_argument("--finalists-commit", default=""); t.add_argument("--allow-uncommitted", action="store_true", help="unit tests and dry runs only")
    sub.add_parser("report")
    args = ap.parse_args()
    return {"units": cmd_units, "select": cmd_select, "test": cmd_test, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
