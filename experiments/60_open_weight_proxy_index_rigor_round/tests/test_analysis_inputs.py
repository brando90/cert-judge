"""Input-boundary regressions for E60's cached-data analysis; no model calls."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load_dirs(dirs, rename=None):
    # register59 changes E58's module-level panel on import. Exercise the real
    # loader in a child process so collecting these tests cannot change E58 tests.
    code = """
import json, sys
sys.path.insert(0, sys.argv[1])
import analyze60
args = json.loads(sys.argv[2])
try:
    result = {"harvests": analyze60.load_dirs(args["dirs"], rename=args["rename"])}
except ValueError as exc:
    result = {"error": str(exc)}
print(json.dumps(result))
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(SCRIPTS), json.dumps({"dirs": [str(p) for p in dirs], "rename": rename})],
        check=True, capture_output=True, text=True,
    )
    payload = json.loads(result.stdout)
    if "error" in payload:
        raise ValueError(payload["error"])
    return payload["harvests"]


def harvest(run, name, config):
    path = run / "harvest" / "e39" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"config": config, "family": config.split("|")[0], "cells": []}
    path.write_text(json.dumps(data))
    return path, data


@pytest.mark.parametrize("kind", ["missing", "file", "empty", "empty_harvest", "nested_seed"])
def test_explicit_run_must_contain_harvests(tmp_path, kind):
    run = tmp_path / "run"
    if kind == "file":
        run.write_text("not a directory")
    elif kind == "empty":
        run.mkdir()
    elif kind == "empty_harvest":
        (run / "harvest" / "e39").mkdir(parents=True)
    elif kind == "nested_seed":
        harvest(run / "seed0", "qwen3_4b__D0", "qwen3_4b|D0")
    with pytest.raises(ValueError, match="directory|No harvest JSON"):
        load_dirs([run])


def test_missing_second_run_is_not_silently_ignored(tmp_path):
    harvest(tmp_path / "valid", "qwen3_4b__D0", "qwen3_4b|D0")
    with pytest.raises(ValueError, match="missing"):
        load_dirs([tmp_path / "valid", tmp_path / "missing"])


def test_optional_absent_runs_still_allowed():
    assert load_dirs([]) == {}


def test_valid_runs_preserve_filename_order_and_seed_renaming(tmp_path):
    first, original = harvest(tmp_path / "seed1", "z", "qwen3_4b|R4")
    harvest(tmp_path / "seed1", "a", "qwen3_4b|D0")
    _, other = harvest(tmp_path / "old", "b", "llama31_8b|D0")
    plain = load_dirs([tmp_path / "seed1", tmp_path / "old"])
    assert list(plain) == ["qwen3_4b|D0", "qwen3_4b|R4", "llama31_8b|D0"]
    assert plain[original["config"]] == original
    assert plain[other["config"]] == other
    renamed = load_dirs([tmp_path / "seed1"], rename="@s1")
    assert list(renamed) == ["qwen3_4b@s1|D0", "qwen3_4b@s1|R4"]
    assert renamed["qwen3_4b@s1|R4"]["family"] == "qwen3_4b@s1"
    assert json.loads(first.read_text()) == original
