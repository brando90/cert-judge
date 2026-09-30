#!/usr/bin/env python3
"""TLDR: Frozen constants, paths, the judge panel with its pre-registered train/val/test split over judge
models, and read-only imports of VeriBench's frozen prompt renderer (experiment 100) and Valkyrie judge
transport (experiment 103) for cert-judge experiment 39; zero model calls."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parents[1]                       # experiment 39 root
REPO = E.parents[1]                                           # cert-judge root
PRIVATE = E / "private"                                       # git-ignored: prompts, packs, raw verdicts
RESULTS = E / "results"
PROMPT_DIR = E / "prompts"
SEED = 39
EXPERIMENT = "certjudge39-proxy-index"

# The VeriBench clone this experiment reads (never writes). On SNAP the worker clones its own copy; locally
# the environment variable points at any checkout.
VB_REPO = Path(os.environ.get("E39_VERIBENCH_REPO", "/lfs/skampere1/0/brando9/veribench_e39"))
X100 = VB_REPO / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test"
X103 = VB_REPO / "experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge"
X75 = VB_REPO / "experiments/75_J1_validating_formal_spec_judge_train_val_test"
# Lean 4.22 + Mathlib project used for fail-closed probe elaboration (experiment 105 used the same one).
LAKE_DIR = Path(os.environ.get("E39_LAKE_DIR", "/lfs/skampere1/0/brando9/vb90_grading/lean_project"))
LAKE_BIN = Path(os.environ.get("E39_LAKE_BIN", str(Path.home() / ".elan/bin/lake")))
VALK = Path(os.environ.get("E39_VALK", "/lfs/skampere1/0/brando9/.local/share/valkyrie-host-bootstrap/tools/valkyrie/bin/valk"))
AGENT = "vb103_judge"                       # experiment 103's validated judge transport agent (prompt bytes in, one call)
BENCHMARK = "certjudge39-proxy-index"
CAP_USD = None                              # no automatic spend cap on Valkyrie runs (PROTOCOL.md Amendment 1)
GATEWAY_SECRET = "fellows/brandoModelGatewayApiKey"   # secret NAME resolved by Valkyrie server-side; never read on the host
# Agent-judge harness: a Terminus2 bundle already in the account, tried in this order at the smoke gate. It is the
# only agent harness VeriBench has run through Valkyrie (experiments 95, 97); the native Claude Code / Codex bundles
# of experiment 90 are unadmitted and are not used.
AGENT_HARNESS_CANDIDATES = ("brando_terminus_gateway", "terminus2", "brando_terminus_astra_smoke")

# ---------------------------------------------------------------------------------------------------------
# Judge panel. A unit is one configuration = judge (model, harness) x prompt. The split is over judge models
# and harnesses, fixed here before any score exists (PROTOCOL.md). Efforts copy experiment 100's configs where
# they exist. `harness` "vb103_judge" = one gateway call carrying the frozen prompt bytes (single-call judge);
# "terminus2" = the model inside the Terminus2 agent harness, given the same prompt bytes as its task and asked
# to write the verdict file (agent judge).
# ---------------------------------------------------------------------------------------------------------
MODELS = {
    # key: (selector candidates best first, effort kwargs, split, label, harness)
    "sol6h": {"selectors": ["openai/gpt-6-sol-high"], "kwargs": {"reasoning_effort": "high"},
              "split": "train", "label": "GPT-6 Sol (high), single call", "max_tokens": 32000, "harness": "vb103_judge"},
    "sonnet5m": {"selectors": ["anthropic/claude-sonnet-5-medium"], "kwargs": {"compute_effort": "medium"},
                 "split": "train", "label": "Claude Sonnet 5 (medium), single call", "max_tokens": 32000, "harness": "vb103_judge"},
    "luna6h": {"selectors": ["openai/gpt-6-luna-high", "openai/gpt-5.6-luna-high"], "kwargs": {"reasoning_effort": "high"},
               "split": "val", "label": "GPT-6 Luna (high), single call", "max_tokens": 32000, "harness": "vb103_judge"},
    "gem31h": {"selectors": ["google/gemini-3.1-pro-preview-high", "google/gemini-3.1-pro-preview"],
               "kwargs": {"reasoning_effort": "high"}, "split": "val", "label": "Gemini 3.1 Pro (high), single call",
               "max_tokens": 32000, "harness": "vb103_judge"},
    "opus55x": {"selectors": ["anthropic/claude-opus-5-5-no-fallback"], "kwargs": {"compute_effort": "max"},
                "split": "test", "label": "Claude Opus 5.5 (max), single call", "max_tokens": 32000, "harness": "vb103_judge"},
    "qwen36": {"selectors": ["alibaba/qwen3.6-27b-thinking", "alibaba/qwen3.6-27b"], "kwargs": {},
               "split": "test", "label": "Qwen3.6-27B (thinking), single call", "max_tokens": 32000, "harness": "vb103_judge"},
    # Agent judges: the same rubric text delivered as a Terminus2 task; the agent reads it in its sandbox and writes the
    # verdict file. One in val (cheap), two in test (a held-out harness on a train model, and a held-out harness on a
    # held-out model).
    "t2_luna": {"selectors": ["openai/gpt-6-luna-high", "openai/gpt-5.6-luna-high"], "kwargs": {"reasoning_effort": "high"},
                "split": "val", "label": "Terminus2 agent + GPT-6 Luna (high)", "max_tokens": 32000, "harness": "terminus2"},
    "t2_sonnet5": {"selectors": ["anthropic/claude-sonnet-5-medium"], "kwargs": {},
                   "split": "test", "label": "Terminus2 agent + Claude Sonnet 5 (medium)", "max_tokens": 32000, "harness": "terminus2"},
    "t2_qwen": {"selectors": ["alibaba/qwen3.6-27b-thinking", "alibaba/qwen3.6-27b"], "kwargs": {},
                "split": "test", "label": "Terminus2 agent + Qwen3.6-27B (thinking)", "max_tokens": 32000, "harness": "terminus2"},
}
# Pre-registered substitutes if a selector is absent from the live registry at admission time (recorded, never
# chosen after seeing scores). A substitute keeps the split of the model it replaces.
SUBSTITUTES = {"luna6h": ["openai/gpt-5.6-luna-high"], "gem31h": ["openai/gpt-5.6-luna-high"],
               "qwen36": ["openai/gpt-5.6-luna-high", "anthropic/claude-opus-5-no-fallback"],
               "t2_luna": ["openai/gpt-5.6-luna-high"], "t2_qwen": ["openai/gpt-5.6-luna-high"]}

# Prompt families. VeriBench prompts render through experiment 100's frozen `prompts.render`; the paper's
# legacy prompts render through `legacy.render` (reference = the gold's last theorem block, as in the paper).
PROMPTS = {
    "D0": {"rubric": "D0_deployed_tc_v1", "family": "veribench", "scale": 10, "max_tokens": 16384,
           "doc": "deployed VBV1/VBV2 scoreboard judge rubric tc_coverage_v1 (experiment 95)"},
    "R4": {"rubric": "R4_exp75_human_precondition", "family": "veribench", "scale": 5, "max_tokens": 32000,
           "doc": "experiment 75's best earlier prompt (human 0-5 checklist plus precondition clause)"},
    "H0": {"rubric": "H0_human_mirror", "family": "veribench", "scale": 5, "max_tokens": 32000,
           "doc": "the raters' instructions, verbatim"},
    "H1": {"rubric": "H1_human_mirror_rater_conventions", "family": "veribench", "scale": 5, "max_tokens": 32000,
           "doc": "H0 plus four training-derived rater conventions"},
    "H2": {"rubric": "H2_human_mirror_conventions_demos", "family": "veribench", "scale": 5, "max_tokens": 32000,
           "doc": "H1 plus four leave-task-out rated examples (experiment 100's validated judge prompt)"},
    "P1": {"rubric": "P1_BASELINE", "family": "legacy", "scale": 1, "max_tokens": 16384,
           "doc": "cert-judge paper P1_BASELINE prompt, verbatim"},
    "P4": {"rubric": "P4_CHECKLIST", "family": "legacy", "scale": 1, "max_tokens": 16384,
           "doc": "cert-judge paper P4_CHECKLIST prompt, verbatim"},
    "P8": {"rubric": "P8_STRICT_B", "family": "legacy", "scale": 1, "max_tokens": 16384,
           "doc": "cert-judge paper P8_STRICT_B prompt, verbatim"},
    "LEX": {"rubric": "BAD_STRINGY", "family": "legacy", "scale": 1, "max_tokens": 16384,
            "doc": "cert-judge paper BAD_STRINGY deliberately lexical judge, verbatim (a designed-bad control that is still an LLM configuration)"},
}
PROMPT_ORDER = ("D0", "R4", "H0", "H1", "H2", "P1", "P4", "P8", "LEX")
# The flagship is judged on a five-prompt subset spanning the expected quality range; agent judges on the two
# VeriBench extremes (the validated H2 prompt and the deployed D0 rubric) (cost, PROTOCOL.md).
PROMPTS_BY_MODEL = {key: PROMPT_ORDER for key in MODELS}
PROMPTS_BY_MODEL["opus55x"] = ("H2", "H0", "D0", "P4", "LEX")
for _key, _model in MODELS.items():
    if _model["harness"] == "terminus2":
        PROMPTS_BY_MODEL[_key] = ("H2", "D0")

# Non-LLM controls: deterministic, zero calls, train split only (PROTOCOL.md section 3).
CONTROLS = {
    "ctl|editdist": "normalized character-Levenshtein similarity between candidate and gold (paper control editdist_e1)",
    "ctl|random": "seed-42 SHA-256 pseudo-random score of the pair (paper control random_r1)",
    "ctl|count_ratio": "min(1, candidate theorem-statement count / gold theorem-statement count) (experiment 100's dumb baseline)",
    "ctl|name_jaccard": "Jaccard overlap of theorem names between candidate and gold",
}

# Cell kinds, their repeat counts and the maximum ladder depth. Level 0 of every ladder is shared with an
# existing cell (crit for candidate ladders, ident for gold ladders) and is never re-judged.
KINDS = {
    "crit": {"repeats": 3, "doc": "the 75 rated candidates against their gold (criterion items; level 0 of ms_cand)"},
    "ident": {"repeats": 3, "doc": "the gold as its own candidate (identity; level 0 of ms_gold and bm_gold)"},
    "blank": {"repeats": 1, "doc": "empty candidate (vacuity)"},
    "ms_gold": {"repeats": 1, "levels": 4, "doc": "cumulative theorem-statement deletion from the gold, up to 4 levels"},
    "ms_cand": {"repeats": 1, "levels": 3, "doc": "cumulative theorem-statement deletion from a candidate, up to 3 levels"},
    "bm_gold": {"repeats": 3, "levels": 4, "doc": "cumulative implementation bug mutations of the gold (cert-judge build_bug_ladder), 4 levels"},
    "alpha": {"repeats": 1, "doc": "conservative alpha-renaming of one theorem binder in the candidate"},
    "reorder": {"repeats": 1, "doc": "the candidate's last two theorem declarations swapped"},
    "sorry": {"repeats": 1, "doc": "every theorem/lemma proof of the candidate replaced by sorry"},
    "spam": {"repeats": 1, "doc": "three irrelevant true theorems appended to the candidate"},
}

# Which VeriBench task split gives the criterion items (experiment 75's task split, seed 20260903).
CRITERION_SPLITS = ("val", "test")


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


def panel_units() -> list[dict]:
    """Every unit of the panel with its family and split; controls are train-only, zero-call units."""
    units = []
    for model_key, model in MODELS.items():
        for prompt_key in PROMPTS_BY_MODEL[model_key]:
            prompt = PROMPTS[prompt_key]
            units.append({"config": config_id(model_key, prompt_key), "model_key": model_key, "prompt_key": prompt_key,
                          "family": model_key, "split": model["split"], "kind": "llm", "label": model["label"],
                          "harness": model["harness"], "pack_flavor": "agent" if model["harness"] != "vb103_judge" else "transport",
                          "selectors": list(model["selectors"]), "substitutes": list(SUBSTITUTES.get(model_key, [])),
                          "kwargs": dict(model["kwargs"]), "rubric": prompt["rubric"], "prompt_family": prompt["family"],
                          "scale": prompt["scale"], "max_tokens": min(model["max_tokens"], prompt["max_tokens"])})
    for name, doc in CONTROLS.items():
        units.append({"config": name, "model_key": "ctl", "prompt_key": name.split("|", 1)[1], "family": "control",
                      "split": "train", "kind": "control", "label": doc, "harness": "none", "pack_flavor": "none",
                      "selectors": [], "substitutes": [], "kwargs": {}, "rubric": name, "prompt_family": "control",
                      "scale": 1, "max_tokens": 0})
    return units


def x100_modules():
    """Experiment 100's frozen renderer, parser and item loader, imported (never copied or edited)."""
    scripts = X100 / "scripts"
    if not scripts.is_dir():
        raise FileNotFoundError(f"experiment 100 scripts not found at {scripts}; set E39_VERIBENCH_REPO")
    sys.path[:0] = [str(scripts)]
    import common                                            # noqa: E402
    common.EXPT = X100
    common.ITEMS = X100 / "inputs/items.jsonl"
    import prompts                                           # noqa: E402
    import build_inputs                                      # noqa: E402
    return common, prompts, build_inputs


def x103_judge_pack():
    """Experiment 103's task-file format (`emit`) and its agent's own parser."""
    sys.path[:0] = [str(X103 / "scripts")]
    import judge_pack                                        # noqa: E402
    sys.path[:0] = [str(X103 / "scripts/valkyrie_judge_agent")]
    import judge_call                                        # noqa: E402
    return judge_pack, judge_call


def load_items() -> list[dict]:
    """Experiment 100's 75 items (annotation-era inputs, expert targets, experiment 75's task split)."""
    rows = [json.loads(line) for line in (X100 / "inputs/items.jsonl").read_text().splitlines() if line.strip()]
    for row in rows:
        for key in ("candidate_path", "ref_ann_path", "py_ann_path", "ref_snap_path"):
            row[key + "_abs"] = str(X100 / row[key])
    return rows


def cert_judge_modules():
    sys.path[:0] = [str(REPO / "py_src")]
    from cert_judge import probe_validation, pti_v0          # noqa: E402
    return probe_validation, pti_v0
