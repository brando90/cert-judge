#!/usr/bin/env python3
"""TLDR: Frozen constants and paths for cert-judge experiment 42 (semantic weakening, over-constraint, vacuity and
formatting probes scored by experiment 39's judges). The judge panel (models, prompts, prompt-by-model table,
controls, selectors, substitutes) is imported read-only from experiment 39's `scripts/e39.py` in this clone so the
configurations are byte-identical; everything this experiment writes lives under its own folder. Zero model calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parents[1]                       # experiment 42 root
REPO = E.parents[2]                                           # cert-judge root (experiment lives under experiments/archive/ since 10-13-2026)
PRIVATE = E / "private"                                       # git-ignored: probe files, prompts, packs, raw verdicts
RESULTS = E / "results"
EXPERIMENT = "certjudge42-semantic-probes"
SEED = 42

# Experiment 39's folder in THIS clone (read-only import of its frozen panel and prompt files; never written).
E39_DIR = REPO / "experiments/archive/39_label_free_proxy_index_train_val_test_over_judge_families"
E39_PROMPT_DIR = E39_DIR / "prompts"

# VeriBench clone read by this experiment (never written). e39.py reads E39_VERIBENCH_REPO at import time, so it is
# pointed at this experiment's own clone before the import.
VB_REPO = Path(os.environ.get("E42_VERIBENCH_REPO", "/lfs/skampere1/0/brando9/veribench_e42"))
os.environ["E39_VERIBENCH_REPO"] = str(VB_REPO)
LAKE_DIR = Path(os.environ.get("E42_LAKE_DIR", "/lfs/skampere1/0/brando9/vb90_grading/lean_project"))
LAKE_BIN = Path(os.environ.get("E42_LAKE_BIN", str(Path.home() / ".elan/bin/lake")))
os.environ.setdefault("E39_LAKE_DIR", str(LAKE_DIR))
os.environ.setdefault("E39_LAKE_BIN", str(LAKE_BIN))


def _load_e39():
    spec = importlib.util.spec_from_file_location("e39_frozen", E39_DIR / "scripts/e39.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["e39_frozen"] = module
    spec.loader.exec_module(module)
    return module


E39 = _load_e39()
X100, X103 = E39.X100, E39.X103
VALK = Path(os.environ.get("E42_VALK", str(E39.VALK)))
AGENT = E39.AGENT                                             # experiment 103's validated single-call transport agent
GATEWAY_SECRET = E39.GATEWAY_SECRET
AGENT_HARNESS_CANDIDATES = E39.AGENT_HARNESS_CANDIDATES
MODELS, SUBSTITUTES = E39.MODELS, E39.SUBSTITUTES
PROMPTS, PROMPT_ORDER, PROMPTS_BY_MODEL = E39.PROMPTS, E39.PROMPT_ORDER, E39.PROMPTS_BY_MODEL
CONTROLS = E39.CONTROLS
CAP_USD = None                                                # no automatic spend cap on Valkyrie runs (repository CLAUDE.md)
BENCHMARK_PREFIX = "certjudge42"                              # one served benchmark per judge key: certjudge42-<key, hyphens>
BASE_PORT = 9460                                              # 9460-9468 (experiment 39: 8990-8998; 43: 9431; 103: 8923-8962)

# Probe families and cell kinds (PROTOCOL.md). Every kind is judged with 3 repeats; `ident` (the reference as its own
# candidate) is the anchor every directional comparison is made against.
REPEATS = 3
KINDS = {
    "ident": {"family": "identity", "levels": 1, "doc": "the annotation-era reference as its own candidate (anchor)"},
    "vac_true": {"family": "vacuity", "levels": 1, "doc": "every theorem statement replaced by `True`"},
    "vac_hyp": {"family": "vacuity", "levels": 1,
                "doc": "every theorem keeps its binders and premises; its conclusion becomes `True`"},
    "weak": {"family": "weakening", "levels": 3,
             "doc": "cumulative semantic weakening (drop a conjunct, relax = to <= / >=, add a disjunctive escape), "
                    "each level with a Lean proof that the reference implies it"},
    "overc": {"family": "overconstraint", "levels": 2,
              "doc": "an unsatisfiable hypothesis added to the main theorem (L1) and to every eligible theorem (L2), "
                     "with a Lean proof that the hypothesis is unsatisfiable"},
    "fmt_comments": {"family": "formatting", "levels": 1,
                     "doc": "non-doc comments removed and blank lines normalized (same elaborated declarations)"},
    "fmt_layout": {"family": "formatting", "levels": 1,
                   "doc": "multi-line theorem heads joined onto one line (same elaborated declarations)"},
}
FAMILIES = ("vacuity", "weakening", "overconstraint", "formatting")
# Decision rule (PROTOCOL.md): a judge passes the semantic screen iff its directional accuracy is >= 0.8 on each of
# vacuity, weakening and over-constraint AND its formatting gap is <= 0.05.
PASS_DIRECTIONAL = 0.8
PASS_FORMATTING_GAP = 0.05
BOOTSTRAP_DRAWS = 10000


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


def config_id(model_key: str, prompt_key: str) -> str:
    return f"{model_key}|{prompt_key}"


def benchmark_of(model_key: str) -> str:
    """Valkyrie accepts hyphen-only benchmark names (experiment 39's finding), so a key's underscore is folded."""
    return f"{BENCHMARK_PREFIX}-{model_key.replace('_', '-')}"


def port_of(model_key: str) -> int:
    return BASE_PORT + list(MODELS).index(model_key)


def panel_units() -> list[dict]:
    """Experiment 39's 56 LLM units and 4 controls, unchanged (its own split labels kept for the index analysis)."""
    return E39.panel_units()


def x100_modules():
    return E39.x100_modules()


def x103_judge_pack():
    return E39.x103_judge_pack()


def load_items() -> list[dict]:
    return E39.load_items()


def references() -> dict[str, dict]:
    """task -> {path, text, base item}: the 25 annotation-era references (experiment 100 `inputs/references/annotation`)."""
    out = {}
    for item in sorted(load_items(), key=lambda r: r["item"]):
        if item["task"] in out:
            continue
        path = Path(item["ref_ann_path_abs"])
        out[item["task"]] = {"path": str(path), "text": path.read_text(encoding="utf-8", errors="replace"), "base_item": item}
    return out
