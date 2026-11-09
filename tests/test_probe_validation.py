import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.probe_validation import (
    CompileResult,
    LeanCompiler,
    alpha_rename_bound_identifier,
    build_bug_ladder,
    build_missing_spec_ladder,
    classify_compile_error,
    declarations,
    mask_lean_noncode,
    summarize_compile_error,
)


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (CompileResult(True, 0, ""), "ok"),
        (CompileResult(False, 124, "TIMEOUT after 1s"), "timeout"),
        (
            CompileResult(False, 1, "object file 'Std/Foo.olean' does not exist"),
            "unresolved_import",
        ),
        (CompileResult(False, 1, "unexpected token 'end'"), "parse"),
        (CompileResult(False, 1, "application type mismatch"), "type_or_elaboration"),
        (CompileResult(False, 1, "fail to show termination"), "termination"),
    ],
)
def test_compile_error_classification(result: CompileResult, expected: str) -> None:
    assert classify_compile_error(result) == expected


def test_lean_compiler_timeout_surfaces_as_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    lake = tmp_path / "lake"
    lake.write_text("", encoding="utf-8")

    def timeout(*_args: object, **_kwargs: object) -> None:
        raise subprocess.TimeoutExpired(cmd="lean", timeout=1)

    monkeypatch.setattr("cert_judge.probe_validation.subprocess.run", timeout)
    result = LeanCompiler(project, lake, timeout_seconds=1).compile("def value := 1\n")

    assert result.returncode == 124
    assert classify_compile_error(result) == "timeout"


def test_mask_lean_noncode_preserves_offsets_and_newlines() -> None:
    source = (
        'def visible := "def hidden" -- theorem nope\n'
        "/- outer /- inner -/ end -/\n"
        "def plusChar : Char := '+'\n"
        "#check visible\n"
    )
    masked = mask_lean_noncode(source)

    assert len(masked) == len(source)
    assert masked.count("\n") == source.count("\n")
    assert "hidden" not in masked
    assert "nope" not in masked
    assert "'+'" not in masked
    assert "#check visible" in masked


def test_declaration_span_stops_before_namespace_end() -> None:
    source = "namespace Demo\ndef f := 1\ntheorem ok : True := by trivial\nend Demo\n"
    found = declarations(source)

    assert [item.name for item in found] == ["f", "ok"]
    assert source[found[-1].start : found[-1].end].rstrip().endswith("trivial")
    assert "end Demo" not in source[found[-1].start : found[-1].end]


def test_declaration_span_stops_before_unselected_top_level_command() -> None:
    source = (
        "theorem removable : True := by trivial\n"
        "instance : Inhabited Nat := ⟨0⟩\n"
        "def program := default\n"
    )
    found = declarations(source)

    theorem = next(item for item in found if item.name == "removable")
    assert "instance" not in source[theorem.start : theorem.end]


def test_alpha_rename_changes_binder_and_all_header_uses_only() -> None:
    source = "theorem demo (x : Nat) : x = x := by\n  rfl\n"
    result = alpha_rename_bound_identifier(source)

    assert result.old_name == "x"
    assert result.new_name == "ptiAlpha0"
    assert result.occurrence_count == 3
    assert "(ptiAlpha0 : Nat) : ptiAlpha0 = ptiAlpha0" in result.code
    assert result.code.endswith("by\n  rfl\n")
    assert result.code != source


def test_alpha_rename_rejects_binder_used_in_proof() -> None:
    source = "theorem demo (x : Nat) : x = x := by\n  exact Eq.refl x\n"

    with pytest.raises(ValueError, match="no conservative alpha-renaming target"):
        alpha_rename_bound_identifier(source)


def test_alpha_rename_rejects_later_unparenthesized_shadowing_binder() -> None:
    source = "theorem demo (x : Nat) : (∀ x : Nat, x = x) ∧ x = x := by\n  sorry\n"

    with pytest.raises(ValueError, match="no conservative alpha-renaming target"):
        alpha_rename_bound_identifier(source)


def test_bug_ladder_is_cumulative_unique_and_does_not_mutate_comments() -> None:
    source = (
        "def arithmetic (a b : Nat) : Nat :=\n"
        "  ((a + b) * (a + 1)) + ((b + 2) * (b + 3))\n"
        "-- a + b in this comment must remain unchanged\n"
    )
    ladder = build_bug_ladder(source, levels=4)

    assert [artifact.level for artifact in ladder] == [0, 1, 2, 3, 4]
    assert len({artifact.sha256 for artifact in ladder}) == 5
    assert [artifact.code.count(" - ") for artifact in ladder] == [0, 1, 2, 3, 4]
    assert all("-- a + b in this comment" in artifact.code for artifact in ladder)


def test_bug_ladder_fails_closed_when_levels_cannot_be_built() -> None:
    with pytest.raises(ValueError, match="could not construct"):
        build_bug_ladder("def constant : Nat := 1\n", levels=1)


def test_missing_spec_ladder_removes_reverse_dependencies_and_preserves_end() -> None:
    source = (
        "namespace Demo\n"
        "def program (x : Nat) := x + 1\n"
        "theorem precondition : True := by trivial\n"
        "lemma postcondition : True := by trivial\n"
        "def runTests : Bool := true\n"
        "#eval runTests\n"
        "end Demo\n"
    )
    ladder = build_missing_spec_ladder(source, levels=4)

    assert [artifact.step.target for artifact in ladder[1:]] == [
        "#eval runTests",
        "def runTests",
        "lemma postcondition",
        "theorem precondition",
    ]
    assert len({artifact.sha256 for artifact in ladder}) == 5
    assert all("def program" in artifact.code for artifact in ladder)
    assert all("end Demo" in artifact.code for artifact in ladder)
    assert "runTests" not in ladder[2].code


def test_missing_spec_ladder_removes_multiple_eval_commands() -> None:
    source = "def program := 1\n#eval program\n#eval program + 1\n"
    ladder = build_missing_spec_ladder(source, levels=2)

    assert "#eval" not in ladder[-1].code


def test_spec_name_detection_does_not_match_incidental_substrings() -> None:
    source = (
        "def respect (x : Nat) := x + 1\n"
        "def inspectValue (x : Nat) := respect x\n"
        "def runAlgorithm (x : Nat) := inspectValue x\n"
        "def runTests := inspectValue 1 == 2\n"
    )
    ladder = build_missing_spec_ladder(source, levels=1)

    assert "def respect" in ladder[-1].code
    assert "def inspectValue" in ladder[-1].code
    assert "def runAlgorithm" in ladder[-1].code
    assert "def runTests" not in ladder[-1].code


def test_lean_compiler_accepts_valid_code_and_rejects_invalid_code() -> None:
    project_root = REPO_ROOT / "data" / "veribench_dataset" / "lean_src"
    lake_bin = (
        Path.home()
        / ".elan"
        / "toolchains"
        / "leanprover--lean4---v4.22.0"
        / "bin"
        / "lake"
    )
    mathlib_build = project_root / ".lake" / "packages" / "mathlib" / ".lake" / "build"
    if not project_root.is_dir() or not lake_bin.is_file() or not mathlib_build.is_dir():
        pytest.skip(
            "needs the pinned Lean 4.22 toolchain and a built Mathlib in "
            "data/veribench_dataset/lean_src/.lake (the Mac/Lean environment)"
        )

    compiler = LeanCompiler(project_root, lake_bin)
    assert compiler.compile("def ptiProbe (x : Nat) : Nat := x + 1\n").ok
    assert not compiler.compile("def ptiProbe : Nat := missingName\n").ok


def test_compile_error_summary_removes_random_temporary_filename() -> None:
    first = "/tmp/pti_probe_abcd1234.lean:2:7: error: unknown identifier 'x'\n"
    second = (
        "/var/folders/random/pti_probe_wxyz9876.lean:2:7: "
        "error: unknown identifier 'x'\n"
    )

    assert summarize_compile_error(first) == summarize_compile_error(second)
    assert summarize_compile_error(first) == (
        "<pti_probe>.lean:2:7: error: unknown identifier 'x'"
    )
