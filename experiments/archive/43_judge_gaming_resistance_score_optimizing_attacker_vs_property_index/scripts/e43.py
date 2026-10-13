#!/usr/bin/env python3
"""TLDR: Frozen constants, paths, the attacked judge configurations, the attacker and reference-ensemble
definitions, and read-only imports (VeriBench experiment 100's prompt renderer and parser, experiment 39's legacy
prompt renderer vendored byte-identically) for cert-judge experiment 43; zero model calls."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True           # never leave __pycache__ inside the read-only VeriBench clone

E = Path(__file__).resolve().parents[1]                       # experiment 43 root
REPO = E.parents[2]                                           # cert-judge root (experiment lives under experiments/archive/ since 10-13-2026)
SCRIPTS = E / "scripts"
PRIVATE = E / "private"                                       # git-ignored: prompts, packs, raw completions, cell state
RESULTS = E / "results"
SEED = 43
EXPERIMENT = "certjudge43-gaming"

VB_REPO = Path(os.environ.get("E43_VERIBENCH_REPO", "/lfs/skampere1/0/brando9/veribench_e43"))
X100 = VB_REPO / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test"
X103 = VB_REPO / "experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge"
# Experiment 43's own Lean mirror of experiment 39's grading project (see CKPT_gaming_resistance.md for the recipe).
LAKE_DIR = Path(os.environ.get("E43_LAKE_DIR", "/lfs/skampere1/0/brando9/cj_e43_lean_project"))
LAKE_BIN = Path(os.environ.get("E43_LAKE_BIN", str(Path.home() / ".elan/bin/lake")))
VALK = Path(os.environ.get("E43_VALK", "/lfs/skampere1/0/brando9/.local/share/valkyrie-host-bootstrap/tools/valkyrie/bin/valk"))
AGENT = "vb103_judge"                      # experiment 103's validated single-call transport (prompt bytes in, one call)
BENCHMARK = "certjudge43-gaming"           # hyphen-only (Valkyrie rejects underscores)
PORT = 9431                                # experiment 39 uses 8990-8998, experiment 103 8923-8962
CAP_USD = None                             # Valkyrie runs have no automatic spend cap (repository CLAUDE.md)
LEAN_TIMEOUT_S = 600

# ---------------------------------------------------------------------------------------------------------
# Attacked judges: one judge model (Claude Sonnet 5 at medium effort, an experiment 39 TRAIN model whose rows are
# open, and a model outside the reference ensemble) x the six prompts the README names. Prompt bytes and parsers are
# experiment 39's (VeriBench experiment 100's renderer for D0/H0/H2, the paper's legacy prompts for P1/P8/LEX).
# ---------------------------------------------------------------------------------------------------------
JUDGE_MODEL = {"key": "sonnet5m", "selector": "anthropic/claude-sonnet-5-medium", "kwargs": {"compute_effort": "medium"},
               "label": "Claude Sonnet 5 (medium), single call", "substitutes": []}
PROMPTS = {
    "LEX": {"rubric": "BAD_STRINGY", "family": "legacy", "scale": 1, "max_tokens": 16384},
    "D0": {"rubric": "D0_deployed_tc_v1", "family": "veribench", "scale": 10, "max_tokens": 16384},
    "H0": {"rubric": "H0_human_mirror", "family": "veribench", "scale": 5, "max_tokens": 32000},
    "H2": {"rubric": "H2_human_mirror_conventions_demos", "family": "veribench", "scale": 5, "max_tokens": 32000},
    "P1": {"rubric": "P1_BASELINE", "family": "legacy", "scale": 1, "max_tokens": 16384},
    "P8": {"rubric": "P8_STRICT_B", "family": "legacy", "scale": 1, "max_tokens": 16384},
}
JUDGES = {f"{JUDGE_MODEL['key']}|{p}": {"config": f"{JUDGE_MODEL['key']}|{p}", "prompt_key": p, **PROMPTS[p],
                                          "selector": JUDGE_MODEL["selector"], "kwargs": dict(JUDGE_MODEL["kwargs"])}
          for p in ("LEX", "D0", "H0", "H2", "P1", "P8")}
PILOT_JUDGES = ("sonnet5m|H2", "sonnet5m|LEX")

# Attacker: one pre-registered model through the same single-call transport. GPT-6 Luna (high) is outside both the
# attacked judge family and the reference ensemble; its pre-registered substitute is experiment 39's.
ATTACKER = {"key": "luna6h", "selector": "openai/gpt-6-luna-high", "kwargs": {"reasoning_effort": "high"},
            "substitutes": ["openai/gpt-5.6-luna-high"], "max_tokens": 32000, "label": "GPT-6 Luna (high), single call"}

# Reference, never shown to the attacker: VeriBench experiment 100's validated H2 ensemble (Claude Opus 5.5 at max
# effort + GPT-6 Sol at high effort), each repeated 3 times, plus the deterministic checks in reference_checks.py.
REFERENCE = {
    "rubric": "H2_human_mirror_conventions_demos", "scale": 5, "repeats": 3,
    "members": {
        "opus55x": {"selector": "anthropic/claude-opus-5-5-no-fallback", "kwargs": {"compute_effort": "max"}, "max_tokens": 32000},
        "sol6h": {"selector": "openai/gpt-6-sol-high", "kwargs": {"reasoning_effort": "high"}, "max_tokens": 32000},
    },
}
RESCORE_REPEATS = 3            # fresh attacked-judge scores of each cell's start and final candidate (post-loop)

K = 8                          # attack iterations per (judge, item) in the full run
PILOT = {"items": 3, "judges": PILOT_JUDGES, "iterations": 4}
GATES = {"lean_valid_edit_rate_min": 0.60, "judge_parse_rate_min": 0.95}
N_ITEMS = 15
COVERAGE_MAX = 0.6
CRITERION_SPLITS = ("val", "test")          # experiment 39's criterion tasks = experiment 75's val + test task split
BOOTSTRAP_REPS = 10000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(Path(path).read_bytes())


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=False) + "\n")
    tmp.replace(path)


def read_json(path: Path):
    return json.loads(Path(path).read_text())


def fs(name: str) -> str:
    return name.replace("|", "__")


_X100 = None


def x100_modules():
    """Experiment 100's frozen renderer and parser, imported read-only (never copied or edited)."""
    global _X100
    if _X100 is None:
        scripts = X100 / "scripts"
        if not scripts.is_dir():
            raise FileNotFoundError(f"experiment 100 scripts not found at {scripts}; set E43_VERIBENCH_REPO")
        sys.path[:0] = [str(scripts)]
        import common                                        # noqa: E402
        common.EXPT = X100
        common.ITEMS = X100 / "inputs/items.jsonl"
        import prompts                                       # noqa: E402
        _X100 = (common, prompts)
    return _X100


def legacy_module():
    """Experiment 39's legacy prompt renderer/parser, vendored byte-identically under scripts/vendor_e39/."""
    sys.path[:0] = [str(SCRIPTS / "vendor_e39" / "scripts")]
    import legacy                                            # noqa: E402
    return legacy


def load_items() -> list[dict]:
    rows = [json.loads(line) for line in (X100 / "inputs/items.jsonl").read_text().splitlines() if line.strip()]
    for row in rows:
        for key in ("candidate_path", "ref_ann_path", "py_ann_path", "ref_snap_path"):
            row[key + "_abs"] = str(X100 / row[key])
    return rows


def items_by_id() -> dict[str, dict]:
    return {r["item"]: r for r in load_items()}


def render_judge(config: str, item: dict, candidate_text: str) -> tuple[str, str] | tuple[None, float] | tuple[None, None]:
    """Frozen prompt bytes of one attacked-judge (or reference) cell.

    Returns (system, user) for a model call, (None, score) for the deployed D0 rubric's no-call rules, or
    (None, None) when D0's extractor refuses the source (unmeasured, never scored)."""
    rubric = JUDGES[config]["rubric"] if config in JUDGES else config
    family = "legacy" if rubric in ("BAD_STRINGY", "P1_BASELINE", "P4_CHECKLIST", "P8_STRICT_B") else "veribench"
    if family == "legacy":
        gold = Path(item["ref_ann_path_abs"]).read_text(encoding="utf-8", errors="replace")
        return legacy_module().render(rubric, gold, candidate_text)
    _, prompts_mod = x100_modules()
    try:
        return prompts_mod.render(rubric, item, candidate_text, item["candidate_file"])
    except prompts_mod.Unmeasured as exc:
        msg = str(exc)
        if msg.startswith("no_candidate_obligations"):
            return None, 0.0
        if msg.startswith("no_reference_obligations"):
            return None, 1.0
        return None, None


def parse_judge(rubric: str, text: str) -> float:
    """Normalized score in [0, 1]; raises ValueError on any ambiguity (experiment 39's parsers)."""
    if rubric in ("BAD_STRINGY", "P1_BASELINE", "P4_CHECKLIST", "P8_STRICT_B"):
        return float(legacy_module().parse(text)[1])
    _, prompts_mod = x100_modules()
    return float(prompts_mod.parse(rubric, text)[1])
