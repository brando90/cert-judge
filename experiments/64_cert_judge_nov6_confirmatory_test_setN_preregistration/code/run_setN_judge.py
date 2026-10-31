#!/usr/bin/env python3
"""E64: driver that points E58's judge_vllm.py at the set-N family prompt files, one (judge, family) unit at a time, with E58's context rules; no ratings read.
Reads only the rendered family files (setN_prompts/families/<P>.jsonl.gz from render_setN_families.py render), results/FAMILIES_MANIFEST.json and results/RUN_PLAN_setN_E58_2026-10-31.json.
Checks before any unit: each family file's sha256 equals the manifest's, each rendered row hashes (E39 rule, sha256(system+blank line+user)) to its own prompt_sha256 and to the manifest's.
Then calls E58's own run_config (judge_vllm.py, imported, never copied): E58's chat template, per-cell seed, model-default sampling, chunked resumable raw output, and the frozen over-context rule
(budget = min(prompt max_tokens, max_model_len - prompt tokens) < 1024 -> unmeasured_over_context, never truncated). Raw output goes to <run>/raw/setn/<model>/<P>.jsonl; harvest and scoring are not run here.
--dry-run tokenizes and counts only (tokenizer files, no GPU) and compares each unit's call and over-context counts with the run plan (exit 1 on any difference).
Needs this repo (E39, E58 scripts), the VeriBench clone E58 rebuilt from (E58_VERIBENCH_REPO, imported by E39 at load), and for a dry run python with transformers (e.g. ~/.venvs/l32/bin/python); a real run needs vllm and the weights.
  dry run, all 13 models x 9 families:  run_setN_judge.py --run ~/e64/run --prompts-dir setN_prompts --weights-root ~/tok --dry-run
  one unit smoke on GPU:                run_setN_judge.py --run ~/e64/smoke --prompts-dir setN_prompts --weights-root ~/e58/models --model qwen3_8b --prompts H2 --limit-cells 4"""
from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP64 = HERE.parent
E58_SCRIPTS = EXP64.parents[0] / "58_open_weight_judges_on_e39_e42_probes" / "scripts"
sys.path[:0] = [str(E58_SCRIPTS)]
import e58                                                    # noqa: E402
import judge_vllm as J                                        # noqa: E402

EXP = "setn"                                                  # raw/<EXP>/ namespace, separate from E58's e39/e42 raw outputs
MANIFEST = EXP64 / "results" / "FAMILIES_MANIFEST.json"
PLAN = EXP64 / "results" / "RUN_PLAN_setN_E58_2026-10-31.json"


def verify_families(fam_dir: Path, manifest: dict, prompts: tuple[str, ...]) -> None:
    """Stop if a family file or any rendered prompt differs from the frozen manifest (damaged or re-rendered files score nothing)."""
    for key in prompts:
        path = fam_dir / f"{key}.jsonl.gz"
        want = manifest["families"][key]
        if e58.sha_file(path) != want["file_sha256"]:
            raise SystemExit(f"STOP: {path} sha256 differs from FAMILIES_MANIFEST.json")
        rows = e58.read_jsonl(path)
        if len(rows) != manifest["n_files"] or len({r["cell"] for r in rows}) != len(rows):
            raise SystemExit(f"STOP: {key}: {len(rows)} rows, cells not {manifest['n_files']} distinct")
        for r in rows:
            frozen = want["prompt_sha256"][r["item"]]
            if r["status"] == "render":
                if e58.prompt_sha(r["system"], r["user"]) != r["prompt_sha256"] or r["prompt_sha256"] != frozen:
                    raise SystemExit(f"STOP: {key} {r['cell']}: prompt does not hash to the frozen prompt_sha256")
            elif frozen is not None:
                raise SystemExit(f"STOP: {key} {r['cell']}: status {r['status']} but the manifest has a prompt hash")


class DryLLM:
    """Stand-in for E58's LLM in a dry run: E58's run_config reads the model's default sampling params before its dry-run exit (its own --dry-run passes llm=None and stops there)."""
    @staticmethod
    def get_default_sampling_params():
        return types.SimpleNamespace(temperature=None, top_p=None, top_k=None, min_p=None, repetition_penalty=None)


def stub_vllm_for_dry_run() -> None:
    """E58's run_config also imports vllm names before that exit; a dry run (tokenizer only, no GPU) gets inert stand-ins when vllm is not installed."""
    try:
        import vllm                                           # noqa: F401
        return
    except ImportError:
        pass
    top, inputs = types.ModuleType("vllm"), types.ModuleType("vllm.inputs")
    top.SamplingParams, inputs.TokensPrompt = object, dict
    top.inputs = inputs
    sys.modules.update({"vllm": top, "vllm.inputs": inputs})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", type=Path, required=True, help="run directory; raw output under <run>/raw/setn/")
    ap.add_argument("--prompts-dir", type=Path, required=True, help="render output dir holding families/<P>.jsonl.gz")
    ap.add_argument("--weights-root", type=Path, required=True, help="directory with one folder per E58 model key (weights, or tokenizer files for --dry-run)")
    ap.add_argument("--model", default="all", help="comma list of E58 model keys, default all 13")
    ap.add_argument("--prompts", default="all", help="comma list of families (D0 R4 H0 H1 H2 P1 P4 P8 LEX), default all nine")
    ap.add_argument("--limit-cells", type=int, default=None, help="smoke only: this many cells per unit, spread over prompt length")
    ap.add_argument("--dry-run", action="store_true", help="tokenize and count only; compare with the run plan")
    a = ap.parse_args()
    models = e58.MODEL_ORDER if a.model == "all" else tuple(a.model.split(","))
    prompts = e58.PROMPT_ORDER if a.prompts == "all" else tuple(a.prompts.split(","))
    bad = [k for k in models if k not in e58.MODELS] + [k for k in prompts if k not in e58.PROMPT_ORDER]
    if bad:
        raise SystemExit(f"unknown model or family: {bad}")
    manifest, plan = e58.read_json(MANIFEST), e58.read_json(PLAN)
    fam_dir = a.prompts_dir / "families"
    verify_families(fam_dir, manifest, prompts)
    print(json.dumps({"verified_families": list(prompts), "n_files": manifest["n_files"]}), flush=True)
    # E58's loader reads e58.prompts_path(exp, key); point it at the set-N family files.
    e58.prompts_path = lambda exp, key: fam_dir / f"{key}.jsonl.gz"
    J.e58.prompts_path = e58.prompts_path
    if a.dry_run:
        stub_vllm_for_dry_run()
    mismatches, ledger = [], a.run / "ledger.jsonl"
    for model_key in models:
        weights = a.weights_root / model_key
        if a.dry_run:
            from transformers import AutoTokenizer
            llm, tokenizer = DryLLM(), AutoTokenizer.from_pretrained(str(weights))
        else:
            llm = J.make_llm(model_key, weights)
            tokenizer = llm.get_tokenizer()
        for key in prompts:
            res = J.run_config(llm, tokenizer, model_key, EXP, key, a.run, a.limit_cells, a.dry_run)
            if a.dry_run:
                want = plan["models"][model_key]["configs"][key]
                if (res["to_generate"], res["over_context"]) != (want["calls"], want["over_context"]):
                    mismatches.append({"unit": f"{model_key}|{key}", "got": [res["to_generate"], res["over_context"]],
                                       "plan": [want["calls"], want["over_context"]]})
            else:
                ledger.parent.mkdir(parents=True, exist_ok=True)
                raw = J.H.raw_path(a.run, EXP, model_key, key)
                with open(ledger, "a") as fh:
                    fh.write(json.dumps({"unit": f"{model_key}|{key}", "utc": e58.stamp(), "raw_sha256": e58.sha_file(raw),
                                         "limit_cells": a.limit_cells}) + "\n")
        if not a.dry_run:
            del llm                                           # free the GPUs before the next model
    if a.dry_run:
        print(json.dumps({"dry_run_units": len(models) * len(prompts), "plan_mismatches": mismatches}))
        return 1 if mismatches else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
