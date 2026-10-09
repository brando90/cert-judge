import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("e47_build", ROOT / "build_probes_v5.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_frozen_depths_and_formula_source_are_pinned():
    assert MODULE.P.cut_points(5, 4) == [2, 3, 4, 5]
    assert MODULE.P.cut_points(5, 3) == [2, 4, 5]
    analysis = (MODULE.E39 / "analysis_lib.py").read_text(encoding="utf-8")
    assert '"GM_mono2": ("gm", ("ms_gold", "ms_cand"))' in analysis


def test_compilation_cache_environment_is_hash_bound(tmp_path):
    project = MODULE.LAKE_PROJECT_DEFAULT
    compiler = MODULE.Compiler(project, MODULE.LAKE_BIN_DEFAULT, tmp_path / "cache.jsonl", 1)
    assert (project / "lean-toolchain").read_text(encoding="utf-8").strip() == "leanprover/lean4:v4.22.0"
    assert MODULE.sha_file(project / "lean-toolchain") in compiler.environment
    assert MODULE.sha_file(project / "lake-manifest.json") in compiler.environment


def test_frozen_v5_inventory_excludes_anchor_and_keeps_declared_blanks():
    records, provenance = MODULE.source_records(MODULE.SOURCE_ROOT_DEFAULT)
    assert len(records) == 750
    assert sum(not row["blank"] for row in records) == 691
    assert sum(row["blank"] for row in records) == 59
    assert {row["group"] for row in records} == {
        *(f"G{i:02d}" for i in range(1, 14)), "G16", "G17"
    }
    assert provenance["source_commit_declared"] == "ccd86d467fd7577826c4b549df2c532bf43b1892"


def test_counts_keeps_criterion_rows_distinct_from_structural_validity():
    summary = MODULE.counts([
        {"kind": "crit", "valid": True},
        {"kind": "ms_cand", "valid": True},
        {"kind": "ms_cand", "valid": False},
    ])
    assert summary["crit"] == {"rows": 1, "valid": 1, "invalid": 0, "criterion_retained": 1}
    assert summary["ms_cand"] == {"rows": 2, "valid": 1, "invalid": 1, "criterion_retained": 0}
