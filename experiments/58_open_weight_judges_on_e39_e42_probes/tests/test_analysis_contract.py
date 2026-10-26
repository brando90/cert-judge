"""Regression checks against the frozen protocol; no model calls or private prompts."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze58 as Z
import e58
import analysis_inputs as I


def write_harvest(run, exp="e39", model="qwen3_4b", prompt="D0"):
    h = I.missing_harvest(exp, model, prompt)
    h.pop("harvest_status")
    path = run / "harvest" / exp / f"{e58.fs(h['config'])}.json"
    e58.write_json(path, h)
    return path, h


def test_empty_run_keeps_all_declared_units(tmp_path):
    A = e58.analysis_lib()
    manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
    units, _ = Z.build_units(A, tmp_path, Z.load_items(), manifest, draws=2)
    assert len(units) == 117
    assert all(u["harvest_status"] == "missing" for u in units)
    assert all(u["criteria"]["heldout"]["spearman"] is None for u in units)
    assert all(u["indices"]["C_ms_gold"] is None for u in units)
    assert Z.secondary_block(A, units, 2)["pti_v0_status_counts"] == {"NOT_COMPUTABLE": 117}


def test_no_computable_pairs_is_not_a_failed_scientific_gate():
    result = Z.gate_block(e58.analysis_lib(), [], 2)
    assert result["plain_status"] == "NOT_COMPUTABLE"
    assert result["model_clustered_status"] == "NOT_COMPUTABLE"
    assert result["plain_PASS"] is None


def test_deletion_covariate_uses_deletions_not_implementation_bugs():
    A = e58.analysis_lib()
    # Bug scores are constant; deletion scores strictly decrease. The two
    # instruments must remain distinguishable even when their keys coincide.
    cells = []
    for kind, level, value in [("ident", 0, 1.0), ("ms_gold", 1, .5),
                               ("ms_gold", 2, 0.0), ("bm_gold", 1, 1.0), ("bm_gold", 2, 1.0)]:
        cells.extend(dict(kind=kind, key="task", level=level, status="measured", score=value) for _ in range(2))
    h = dict(config="synthetic|D0", split="test", family="synthetic", kind="llm", cells=cells)
    probes = {kind: [dict(key="task", level=i) for i in (1, 2)] for kind in ("ms_gold", "bm_gold")}
    result = Z.tvd_mi(A.Scores(h), h, probes)
    assert result["deletion_tvd_value"] == pytest.approx(1.0)
    assert result["deletion_tvd_information"] == pytest.approx(1.0)


def test_missing_deletion_repeats_stay_unavailable():
    A = e58.analysis_lib()
    cells = [dict(kind=k, key="task", level=i, status="measured", score=v)
             for k, i, v in [("ident", 0, 1.0), ("ident", 0, 1.0), ("ms_gold", 1, .5), ("ms_gold", 2, 0.0)]]
    h = dict(config="synthetic|D0", split="test", family="synthetic", kind="llm", cells=cells)
    result = Z.tvd_mi(A.Scores(h), h, {"ms_gold": [dict(key="task", level=i) for i in (1, 2)]})
    assert result["n_declared_ladders"] == 1
    assert result["n_ladders"] == 0
    assert result["deletion_tvd_value"] is None


def test_empty_e42_run_keeps_not_computable_panel(tmp_path):
    result = Z.e42_block(tmp_path, e58.analysis_lib(), [], 2)
    assert result["n_units"] == 117
    assert result["verdicts"] == {"PASS": 0, "FAIL": 0, "NOT_COMPUTABLE": 117}


def test_partial_harvest_keeps_present_and_missing_units(tmp_path):
    write_harvest(tmp_path)
    panel = I.load_panel(tmp_path, "e39")
    assert len(panel) == 117
    assert sum(h["harvest_status"] == "present" for h in panel) == 1
    assert sum(h["n_cells"] for h in panel) == 117 * 521


def test_panel_preserves_legacy_filename_order_for_seeded_statistics(tmp_path):
    for model in ("qwen3_4b", "gemma3_27b", "gpt_oss_20b"):
        for prompt in ("D0", "R4", "LEX"):
            write_harvest(tmp_path, model=model, prompt=prompt)
    observed = [h["config"] for h in I.load_panel(tmp_path, "e39") if h["harvest_status"] == "present"]
    legacy = [e58.read_json(p)["config"] for p in sorted((tmp_path / "harvest/e39").glob("*.json"))]
    assert observed == legacy


@pytest.mark.parametrize("defect", ["duplicate", "identity", "hash", "counts", "nonfinite", "range"])
def test_bad_harvest_is_rejected(tmp_path, defect):
    path, h = write_harvest(tmp_path)
    if defect == "duplicate":
        h["cells"][-1] = h["cells"][0].copy()
    elif defect == "identity":
        h["config"] = "qwen3_8b|D0"
    elif defect == "hash":
        h["cells"][0]["prompt_sha256"] = "0" * 64
    elif defect == "counts":
        h["status_counts"] = {}
    else:
        h["cells"][0].update(status="measured", score=float("nan") if defect == "nonfinite" else 1.01)
    e58.write_json(path, h)
    with pytest.raises(ValueError):
        I.load_panel(tmp_path, "e39")


def test_outside_panel_is_rejected(tmp_path):
    path, _ = write_harvest(tmp_path)
    path.rename(path.with_name("other__D0.json"))
    with pytest.raises(ValueError, match="outside the frozen panel"):
        I.load_panel(tmp_path, "e39")


def test_collection_requires_manifest_unless_explicit_dry_run(tmp_path):
    with pytest.raises(ValueError, match="MANIFEST"):
        I.verify_collection(tmp_path)
    assert I.verify_collection(tmp_path, dry_run=True)["status"] == "UNVERIFIED_DRY_RUN"
    with pytest.raises(ValueError, match="does not exist"):
        I.verify_collection(tmp_path / "typo", dry_run=True)


def test_collection_verifies_hashes_and_harvest_coverage(tmp_path):
    path, _ = write_harvest(tmp_path)
    manifest = tmp_path / "MANIFEST.sha256"
    manifest.write_text(f"{e58.sha_file(path)}  ./{path.relative_to(tmp_path)}\n")
    assert I.verify_collection(tmp_path)["status"] == "VERIFIED"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        I.verify_collection(tmp_path, dry_run=True)
    manifest.write_text("")
    with pytest.raises(ValueError, match="not all covered"):
        I.verify_collection(tmp_path)


def test_failure_flag_uses_strictly_more_than_twenty_percent(monkeypatch, tmp_path):
    def fake_panel(run, exp):
        return [dict(family=m, n_cells=100, harvest_status="present",
                     status_counts={"parse_error": 10, "incomplete": 11 if m == e58.MODEL_ORDER[0] else 10})
                for m in e58.MODEL_ORDER]
    monkeypatch.setattr(I, "load_panel", fake_panel)
    counts = I.failure_counts(tmp_path)
    assert counts["flagged_models"] == [e58.MODEL_ORDER[0]]
    assert counts["models"][e58.MODEL_ORDER[0]]["failure_fraction"] == .21
    assert counts["models"][e58.MODEL_ORDER[1]]["failure_fraction"] == .20


def test_failure_sensitivity_excludes_whole_flagged_model(monkeypatch, tmp_path):
    units = [dict(model_key=m, config=f"{m}|D0") for m in ("bad", "good")]
    monkeypatch.setattr(Z, "failure_counts", lambda run: {"flagged_models": ["bad"]})
    monkeypatch.setattr(Z, "gate_block", lambda A, rows, draws: [u["model_key"] for u in rows])
    assert Z.failure_sensitivity(None, tmp_path, units, 2)["without_flagged_models"] == ["good"]


def test_later_experiment_settings_cannot_masquerade_as_e58(tmp_path):
    path, h = write_harvest(tmp_path, model="qwen3_32b")
    h["engine"] = dict(quantization="fp8", max_model_len=32768, tensor_parallel_size=1)
    e58.write_json(path, h)
    audit = I.runtime_contract(tmp_path)
    fields = {r["field"] for r in audit["mismatches"]}
    assert {"engine.quantization", "engine.max_model_len", "engine.tensor_parallel_size"} <= fields
    assert audit["n_present_harvests"] == 1


def test_cli_rejects_non_frozen_draws_without_dry_run(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["analyze58.py", "--run", str(tmp_path), "--draws", "20"])
    with pytest.raises(SystemExit) as exc:
        Z.main()
    assert exc.value.code == 2


def test_changed_frozen_probe_manifest_stops_analysis(tmp_path, monkeypatch):
    original = e58.sha_file
    monkeypatch.setattr(e58, "sha_file", lambda path: "changed" if path.name == "probe_manifest.json" else original(path))
    monkeypatch.setattr(sys, "argv", ["analyze58.py", "--run", str(tmp_path), "--dry-run"])
    with pytest.raises(SystemExit, match="probe_manifest.json"):
        Z.main()


def test_recorded_frozen_runtime_is_admitted(tmp_path):
    path, h = write_harvest(tmp_path)
    m = e58.MODELS["qwen3_4b"]
    p = e58.e39_modules()[0].PROMPTS["D0"]
    h.update(selector=f"{m['repo']}@{m['revision']}", rubric=p["rubric"], scale=p["scale"],
             engine=dict(tensor_parallel_size=m["gpus"], max_model_len=m["max_model_len"],
                         gpu_memory_utilization=.90, quantization=None),
             kwargs=dict(min_generation_budget=1024, max_tokens_rule=f"min({p['max_tokens']}, max_model_len - prompt tokens)",
                         seed_rule="int(sha256('58|<config>|<cell>')[:8], 16)", skip_special_tokens=True))
    e58.write_json(path, h)
    assert I.runtime_contract(tmp_path)["status"] == "MATCH"
