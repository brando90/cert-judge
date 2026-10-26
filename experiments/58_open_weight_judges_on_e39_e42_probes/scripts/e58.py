#!/usr/bin/env python3
"""TLDR: Frozen constants for cert-judge experiment 58: the open-weight judge panel (Hugging Face repo, pinned revision,
GPUs, context), experiment 39's nine prompt configurations reused unchanged, the vLLM generation rules, paths, and
read-only imports of experiments 39 and 42 (probe builders, renderers, parsers, analysis). Zero model calls."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

E = Path(__file__).resolve().parents[1]                       # experiment 58 root
REPO = E.parents[1]                                           # cert-judge root
E39_DIR = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E42_DIR = REPO / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges"
PRIVATE = E / "private"                                       # git-ignored: rebuilt probes, rendered prompts, raw outputs
RESULTS = E / "results"
EXPERIMENT = "certjudge58-open-weight-judges"
SEED = 58
EXPS = ("e39", "e42")                                         # the two probe sets this experiment re-scores

# The VeriBench clone read by the rebuild (never written). E39's e39.py reads E39_VERIBENCH_REPO at import time.
VB_REPO = Path(os.environ.get("E58_VERIBENCH_REPO", os.environ.get("E39_VERIBENCH_REPO", str(Path.home() / "veribench_e58"))))
os.environ["E39_VERIBENCH_REPO"] = str(VB_REPO)
os.environ["E42_VERIBENCH_REPO"] = str(VB_REPO)

# ---------------------------------------------------------------------------------------------------------------
# Open-weight judge panel. Every unit is one (model, prompt) configuration; every model gets all nine of experiment
# 39's prompt configurations. All units are fresh judges for experiment 39's frozen selection, so `split` is "test"
# for all of them (analysis_lib reads the field; nothing here is selected or tuned).
#   repo/revision: weights pinned at the revision read from the Hugging Face API on 10-20-2026.
#   source: "official" or "mirror" (the official repo is gated "manual"; the mirror carries the same weights ungated).
#   gpus: L40S 48 GB count (tensor parallel size). max_model_len: the context vLLM allocates (<= the model's own).
#   family + params_b: for the descriptive scale-within-family curves.
#   chat_kwargs: extra chat-template arguments (none: each model's default mode, thinking where it is the default).
# ---------------------------------------------------------------------------------------------------------------
MODELS = {
    "qwen3_4b": {"repo": "Qwen/Qwen3-4B", "revision": "1cfa9a7208912126459214e8b04321603b3df60c", "source": "official",
                 "family": "qwen3", "params_b": 4.0, "gpus": 1, "max_model_len": 40960, "weights_gb": 8.0, "thinking": True},
    "qwen3_8b": {"repo": "Qwen/Qwen3-8B", "revision": "b968826d9c46dd6066d109eabc6255188de91218", "source": "official",
                 "family": "qwen3", "params_b": 8.2, "gpus": 1, "max_model_len": 40960, "weights_gb": 16.4, "thinking": True},
    "qwen3_14b": {"repo": "Qwen/Qwen3-14B", "revision": "40c069824f4251a91eefaf281ebe4c544efd3e18", "source": "official",
                  "family": "qwen3", "params_b": 14.8, "gpus": 1, "max_model_len": 40960, "weights_gb": 29.5, "thinking": True},
    "qwen3_32b": {"repo": "Qwen/Qwen3-32B", "revision": "9216db5781bf21249d130ec9da846c4624c16137", "source": "official",
                  "family": "qwen3", "params_b": 32.8, "gpus": 2, "max_model_len": 40960, "weights_gb": 65.5, "thinking": True},
    # Bridge model: the same weights experiment 39 called hosted (selector alibaba/qwen3.6-27b) run locally in bf16.
    "qwen36_27b": {"repo": "Qwen/Qwen3.6-27B", "revision": "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", "source": "official",
                   "family": "qwen3.6", "params_b": 27.0, "gpus": 2, "max_model_len": 65536, "weights_gb": 55.6, "thinking": True,
                   "multimodal": True, "mm_limits": {"image": 0, "video": 0}, "bridge_e39_model": "qwen36"},
    "llama31_8b": {"repo": "unsloth/Llama-3.1-8B-Instruct", "revision": "4699cc75b550f9c6f3173fb80f4703b62d946aa5", "source": "mirror",
                   "official": "meta-llama/Llama-3.1-8B-Instruct", "family": "llama3", "params_b": 8.0, "gpus": 1,
                   "max_model_len": 65536, "weights_gb": 16.1, "thinking": False},
    "llama33_70b_awq": {"repo": "casperhansen/llama-3.3-70b-instruct-awq", "revision": "64d255621f40b42adaf6d1f32a47e1d4534c0f14",
                        "source": "mirror", "official": "meta-llama/Llama-3.3-70B-Instruct (AWQ int4 quantization of it)",
                        "family": "llama3", "params_b": 70.6, "gpus": 2, "max_model_len": 65536, "weights_gb": 39.8,
                        "thinking": False, "quantization": "awq"},
    "gemma3_4b": {"repo": "unsloth/gemma-3-4b-it", "revision": "bf46152c47f5dd20b896357cb51abc4c03b8ee8c", "source": "mirror",
                  "official": "google/gemma-3-4b-it", "family": "gemma3", "params_b": 4.3, "gpus": 1, "max_model_len": 65536,
                  "weights_gb": 8.6, "thinking": False, "multimodal": True, "mm_limits": {"image": 0}},
    "gemma3_12b": {"repo": "unsloth/gemma-3-12b-it", "revision": "9478e665381f42974aa06177b019352fb6291876", "source": "mirror",
                   "official": "google/gemma-3-12b-it", "family": "gemma3", "params_b": 12.2, "gpus": 1, "max_model_len": 65536,
                   "weights_gb": 24.4, "thinking": False, "multimodal": True, "mm_limits": {"image": 0}},
    "gemma3_27b": {"repo": "unsloth/gemma-3-27b-it", "revision": "7a5a3053dbd5d1d58e48159e87b9df2fc545a49a", "source": "mirror",
                   "official": "google/gemma-3-27b-it", "family": "gemma3", "params_b": 27.4, "gpus": 2, "max_model_len": 65536,
                   "weights_gb": 54.9, "thinking": False, "multimodal": True, "mm_limits": {"image": 0}},
    # OLMo 3 (not OLMo 2: 4k context is too short for these prompts). The Think pair is one release at both sizes.
    "olmo3_7b": {"repo": "allenai/Olmo-3-7B-Think", "revision": "d97e442d7cc678210054dbcc9b440894d62c89a4", "source": "official",
                 "family": "olmo3", "params_b": 7.3, "gpus": 1, "max_model_len": 65536, "weights_gb": 14.6, "thinking": True},
    "olmo3_32b": {"repo": "allenai/Olmo-3-32B-Think", "revision": "f2edda15216e738ef2bb73771e11890e152b2112", "source": "official",
                  "family": "olmo3", "params_b": 32.2, "gpus": 2, "max_model_len": 65536, "weights_gb": 64.5, "thinking": True},
    "gpt_oss_20b": {"repo": "openai/gpt-oss-20b", "revision": "6cee5e81ee83917806bbde320786a8fb61efebee", "source": "official",
                    "family": "gpt-oss", "params_b": 20.9, "gpus": 1, "max_model_len": 65536, "weights_gb": 13.8, "thinking": True,
                    "harmony": True, "download_patterns": ["*.json", "*.safetensors", "tokenizer*", "*.jinja"],
                    "download_ignore": ["original/*", "metal/*"]},
}
MODEL_ORDER = tuple(MODELS)

# Experiment 39's nine prompt configurations, imported unchanged (rubric, family, scale, max_tokens).
PROMPT_ORDER = ("D0", "R4", "H0", "H1", "H2", "P1", "P4", "P8", "LEX")

# Generation rules (PROTOCOL.md section 4).
GPU_MEMORY_UTILIZATION = 0.90
MIN_GENERATION_BUDGET = 1024      # a cell whose prompt leaves fewer new tokens than this is unmeasured_over_context
CHUNK = 256                       # cells per vLLM call; raw output is appended after each chunk (resumable)
HARNESS = "vllm_offline"


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


def read_jsonl(path: Path) -> list[dict]:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_jsonl_gz(path: Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    # mtime=0 keeps the archive bytes deterministic, so the package hash only moves when a prompt moves.
    with open(tmp, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as fh:
        for r in rows:
            fh.write((json.dumps(r, sort_keys=True) + "\n").encode("utf-8"))
    tmp.replace(path)


def prompt_sha(system: str, user: str) -> str:
    """Experiment 39's prompt hash: SHA-256 of system + blank line + user."""
    return sha((system + "\n\n" + user).encode())


def config_id(model_key: str, prompt_key: str) -> str:
    return f"{model_key}|{prompt_key}"


def fs(config: str) -> str:
    return config.replace("|", "__")


def prompts_path(exp: str, prompt_key: str) -> Path:
    return PRIVATE / "prompts" / exp / f"{prompt_key}.jsonl.gz"


# ---------------------------------------------------------------------------------------------------------------
# Read-only imports of experiments 39 and 42. Experiment 39's scripts directory goes first on sys.path, so `legacy`
# resolves to experiment 39's own (experiment 42 vendors the same file with only PROMPT_DIR changed).
# ---------------------------------------------------------------------------------------------------------------
def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def e39_modules():
    """(e39, probes, legacy) from experiment 39's scripts, imported, never copied or edited."""
    scripts = str(E39_DIR / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import e39                                                # noqa: E402
    import legacy                                             # noqa: E402
    import probes                                             # noqa: E402
    return e39, probes, legacy


def analysis_lib():
    e39_modules()
    import analysis_lib as A                                  # noqa: E402
    return A


def e42_modules():
    """(e42, semantic_probes, lean_text) from experiment 42's scripts; experiment 42's legacy.py is never imported."""
    e39_modules()
    scripts = str(E42_DIR / "scripts")
    if scripts not in sys.path:
        sys.path.append(scripts)
    e42 = _load("e42", E42_DIR / "scripts/e42.py")
    lean_text = _load("lean_text", E42_DIR / "scripts/lean_text.py")
    semantic = _load("semantic_probes", E42_DIR / "scripts/semantic_probes.py")
    return e42, semantic, lean_text


def units() -> list[dict]:
    """Every (model, prompt) unit of the panel in experiment 39's panel.json unit schema, plus the model fields."""
    e39, _, _ = e39_modules()
    out = []
    for model_key in MODEL_ORDER:
        m = MODELS[model_key]
        for prompt_key in PROMPT_ORDER:
            p = e39.PROMPTS[prompt_key]
            out.append({"config": config_id(model_key, prompt_key), "model_key": model_key, "prompt_key": prompt_key,
                        "family": model_key, "model_family": m["family"], "params_b": m["params_b"], "split": "test",
                        "kind": "llm", "label": f"{m['repo']}@{m['revision'][:12]} (local vLLM)", "harness": HARNESS,
                        "repo": m["repo"], "revision": m["revision"], "source": m["source"], "gpus": m["gpus"],
                        "max_model_len": m["max_model_len"], "rubric": p["rubric"], "prompt_family": p["family"],
                        "scale": p["scale"], "max_tokens": p["max_tokens"]})
    return out
