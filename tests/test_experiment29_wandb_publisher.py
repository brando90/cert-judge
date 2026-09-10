from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.filterwarnings(
    "ignore::pydantic.warnings.PydanticDeprecatedSince20"
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = (
    REPO_ROOT / "experiments" / "29_pti_v0_cli_bridge" / "expt_v5" / "push_to_wandb.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("pti_v0_wandb_publisher", PUBLISHER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _result_payload(path: Path):
    if path.name == "wandb_report.json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.name == "properties.json":
        properties = {
            name: {"value": 0.5, "coverage": 1.0}
            for name in ("P_eq", "P_bm", "P_ms", "P_eqalpha")
        }
        return {
            "judges": [
                {
                    "judge_id": "judge|one",
                    "role": "primary",
                    "family": "test",
                    "properties": properties,
                    "PTI_eq_bm_ms": {"value": 0.5},
                    "PTI_v0": {"value": 0.5},
                }
            ]
        }
    if path.name == "criterion.json":
        return {
            "records": [
                {
                    "judge_id": "judge|one",
                    "views": {"average": {"value": 0.4, "kendall_tau_b": 0.3}},
                }
            ]
        }
    if path.name == "bridge_pti_v0.json":
        analysis = {
            "spearman": -0.25,
            "kendall_tau_b": -0.2,
            "bootstrap": {
                "ci_low": -1.0,
                "ci_high": 0.4,
                "valid_replicates": 9999,
            },
        }
        return {
            "prebridge_commit": "a" * 40,
            "analyses": {
                "primaries": analysis,
                "pooled_with_controls": analysis,
            },
        }
    if path.name == "bridge_eq_bm_ms.json":
        return {"analyses": {"primaries": {"spearman": -0.25}}}
    if path.name == "sesoi_simulation.json":
        return {"rows": [{"rho_target": 0.5, "positive_decision_rate": 0.271}]}
    if path.name == "cli_auth_status.json":
        return {}
    raise AssertionError(f"unexpected result path: {path}")


def _stub_report_blocks(monkeypatch: pytest.MonkeyPatch, module) -> None:
    for name in (
        "Runset",
        "TableOfContents",
        "H1",
        "CalloutBlock",
        "HorizontalRule",
        "H2",
        "MarkdownBlock",
        "PanelGrid",
        "ScatterPlot",
        "SummaryMetric",
        "BarPlot",
        "MediaBrowser",
    ):
        monkeypatch.setattr(module.wr, name, lambda *args, **kwargs: object())


def test_report_only_updates_canonical_report_without_run_or_artifact_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    key_file = tmp_path / "wandb-key.txt"
    key_file.write_text("test-key", encoding="utf-8")
    report = SimpleNamespace(
        entity=module.ENTITY,
        project=module.PROJECT,
        url=module.DEFAULT_REPORT_URL,
        title=None,
        description=None,
        blocks=None,
    )
    original_created_at = "2026-08-28T07:33:11.230706+00:00"
    closeout_audit = {"noncanonical_duplicate_report_state": "pending"}
    (tmp_path / "wandb_report.json").write_text(
        json.dumps(
            {
                "created_at_utc": original_created_at,
                "release_closeout_audit": closeout_audit,
            }
        ),
        encoding="utf-8",
    )
    calls = {"from_url": [], "save": 0}

    class FakeReport:
        @staticmethod
        def from_url(url: str):
            calls["from_url"].append(url)
            return report

    report.save = lambda: calls.__setitem__("save", calls["save"] + 1)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "RESULTS", tmp_path)
    monkeypatch.setattr(module, "_read_json", _result_payload)
    monkeypatch.setattr(module.wandb, "login", lambda **kwargs: None)
    monkeypatch.setattr(
        module.wandb,
        "init",
        lambda **kwargs: pytest.fail("report-only mode called wandb.init"),
    )
    monkeypatch.setattr(
        module.wandb,
        "Artifact",
        lambda *args, **kwargs: pytest.fail("report-only mode created an artifact"),
    )
    monkeypatch.setattr(module.wr, "Report", FakeReport)
    _stub_report_blocks(monkeypatch, module)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(PUBLISHER), "--key-file", str(key_file)],
    )

    assert module.main() == 0
    assert calls == {"from_url": [module.DEFAULT_REPORT_URL], "save": 1}
    receipt = json.loads((tmp_path / "wandb_report.json").read_text())
    assert receipt["report_url"] == module.DEFAULT_REPORT_URL
    assert receipt["publication_mode"] == "report-only"
    assert receipt["judge_run_ids"] == [module._judge_run_id("judge|one")]
    assert receipt["created_at_utc"] == original_created_at
    assert receipt["release_closeout_audit"] == closeout_audit
    assert receipt["updated_at_utc"] > original_created_at


def test_mismatched_report_aborts_before_full_mode_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    key_file = tmp_path / "wandb-key.txt"
    key_file.write_text("test-key", encoding="utf-8")
    report = SimpleNamespace(entity="wrong-entity", project=module.PROJECT)
    side_effects = {"init": 0, "artifact": 0}

    class FakeReport:
        @staticmethod
        def from_url(url: str):
            return report

    def unexpected_init(**kwargs):
        side_effects["init"] += 1
        pytest.fail("invalid report target reached wandb.init")

    def unexpected_artifact(*args, **kwargs):
        side_effects["artifact"] += 1
        pytest.fail("invalid report target created an artifact")

    monkeypatch.setattr(module.wandb, "login", lambda **kwargs: None)
    monkeypatch.setattr(module.wandb, "init", unexpected_init)
    monkeypatch.setattr(module.wandb, "Artifact", unexpected_artifact)
    monkeypatch.setattr(module.wr, "Report", FakeReport)
    monkeypatch.setattr(
        module,
        "_read_json",
        lambda path: pytest.fail("invalid report target reached result loading"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(PUBLISHER),
            "--key-file",
            str(key_file),
            "--publish-runs-and-artifact",
        ],
    )

    with pytest.raises(ValueError, match="entity/project"):
        module.main()
    assert side_effects == {"init": 0, "artifact": 0}
