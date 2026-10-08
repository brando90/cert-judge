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
    assert "leanprover/lean4:v4.22.0" in compiler.environment
