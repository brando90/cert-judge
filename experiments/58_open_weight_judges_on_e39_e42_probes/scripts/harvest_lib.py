#!/usr/bin/env python3
"""TLDR: Turn experiment 58's raw local-judge outputs into experiment 39's harvest schema: strip the reasoning trace
(`<think>` blocks; gpt-oss harmony analysis channel), parse the final answer with experiment 39's own parsers
(experiment 100 `prompts.parse` for VeriBench rubrics, `legacy.parse` for the paper's prompts), merge the deterministic
and unmeasured cells, and write <run>/harvest/<exp>/<model>__<prompt>.json, which analysis_lib.Scores reads unchanged.

Usage: harvest_lib.py --run <run dir> [--exps e39,e42] [--models all] [--prompts all]"""
from __future__ import annotations

import argparse
import functools
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402

HARMONY_FINAL = "<|channel|>final<|message|>"
HARMONY_TAILS = ("<|return|>", "<|end|>", "<|call|>")
# Statuses written by the driver for cells it did not send to the model.
NOT_CALLED = ("unmeasured_over_context", "unmeasured_infra")


def final_text(text: str, harmony: bool = False) -> tuple[str, str]:
    """(final answer, how it was found). The reasoning trace never reaches the parser: the hosted judges of experiment
    39 returned only their final message, so the local judges are parsed on theirs."""
    if harmony:
        if HARMONY_FINAL not in text:
            return "", "no_final_channel"
        out = text.rsplit(HARMONY_FINAL, 1)[1]
        for tail in HARMONY_TAILS:
            out = out.split(tail, 1)[0]
        return out.strip(), "harmony_final"
    if "</think>" in text:
        return text.rsplit("</think>", 1)[1].strip(), "after_think"
    if "<think>" in text:
        return "", "unclosed_think"
    return text.strip(), "plain"


@functools.lru_cache(maxsize=None)
def _x100_prompts():
    e39, _, _ = e58.e39_modules()
    return e39.x100_modules()[1]


def parse(prompt_key: str, text: str):
    """Experiment 39's parse_verdict: (raw score, normalized score, verdict object); ValueError on any ambiguity."""
    e39, _, legacy = e58.e39_modules()
    unit = e39.PROMPTS[prompt_key]
    if unit["family"] == "legacy":
        return legacy.parse(text)
    return _x100_prompts().parse(unit["rubric"], text)


def judge_cell(prompt_key: str, raw: dict, harmony: bool) -> dict:
    """One raw driver row -> the verdict fields of a harvest cell."""
    if raw["status"] in NOT_CALLED:
        return {"status": raw["status"], "reason": raw.get("reason")}
    final, how = final_text(raw["text"], harmony)
    out = {"finish_reason": raw.get("finish_reason"), "n_prompt_tokens": raw.get("n_prompt_tokens"),
           "n_output_tokens": raw.get("n_output_tokens"), "budget": raw.get("budget"), "final_from": how,
           "verdict_sha256": e58.sha(raw["text"].encode())}
    try:
        if not final:
            raise ValueError(f"no final answer ({how})")
        raw_score, norm, verdict = parse(prompt_key, final)
        out.update(status="measured", score_raw=raw_score, score=norm,
                   rationale=str(verdict.get("rationale") or verdict.get("reasoning") or verdict.get("reason") or "")[:300])
    except ValueError as exc:
        # A generation that ran out of budget before a parseable verdict is "incomplete" (experiment 39's status for a
        # call that did not finish); any other unparseable answer is a parse_error. Neither is retried.
        status = "incomplete" if raw.get("finish_reason") == "length" else "parse_error"
        out.update(status=status, error=str(exc)[:200])
    return out


def build_harvest(exp: str, model_key: str, prompt_key: str, prompt_rows: list[dict], raw_rows: list[dict],
                  meta: dict | None = None) -> dict:
    """Experiment 39's merged harvest blob for one configuration (results/harvest/<config>.json schema)."""
    e39, _, _ = e58.e39_modules()
    model, prompt = e58.MODELS[model_key], e39.PROMPTS[prompt_key]
    config = e58.config_id(model_key, prompt_key)
    raw_by_cell = {r["cell"]: r for r in raw_rows}
    cells = []
    for p in prompt_rows:
        cell = {k: p[k] for k in ("cell", "kind", "key", "task", "item", "level", "repeat")}
        cell.update(config=config, prompt_sha256=p.get("prompt_sha256"))
        if p["status"] == "deterministic":
            cell.update(status="deterministic", score=p["score"], score_raw=p["score"] * prompt["scale"], reason=p["reason"])
        elif p["status"] != "render":                         # unmeasured_extraction / unmeasured_rebuild_mismatch
            cell.update(status=p["status"], reason=p.get("reason"))
        elif p["cell"] not in raw_by_cell:
            cell.update(status="unmeasured_infra", reason="no driver output for this cell")
        else:
            cell.update(judge_cell(prompt_key, raw_by_cell[p["cell"]], bool(model.get("harmony"))))
        cells.append(cell)
    cells.sort(key=lambda c: c["cell"])
    counts: dict[str, int] = {}
    for c in cells:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    meta = meta or {}
    return {"written_utc": e58.stamp(), "experiment": e58.EXPERIMENT, "probe_set": exp, "config": config,
            "family": model_key, "model_family": model["family"], "params_b": model["params_b"], "split": "test",
            "kind": "llm", "harness": e58.HARNESS, "rubric": prompt["rubric"], "scale": prompt["scale"],
            "selector": f"{model['repo']}@{model['revision']}", "selector_source": f"e58.MODELS['{model_key}'] ({model['source']})",
            "kwargs": meta.get("sampling", {}), "engine": meta.get("engine", {}), "run_ids": meta.get("run_ids", {}),
            "n_cells": len(cells), "status_counts": counts, "recovered_cells": 0, "charges_usd": 0.0, "cells": cells}


def raw_path(run: Path, exp: str, model_key: str, prompt_key: str) -> Path:
    return Path(run) / "raw" / exp / model_key / f"{prompt_key}.jsonl"


def harvest_path(run: Path, exp: str, model_key: str, prompt_key: str) -> Path:
    return Path(run) / "harvest" / exp / f"{e58.fs(e58.config_id(model_key, prompt_key))}.json"


def harvest_one(run: Path, exp: str, model_key: str, prompt_key: str) -> dict | None:
    rp = raw_path(run, exp, model_key, prompt_key)
    if not rp.exists():
        return None
    meta_path = rp.with_suffix(".meta.json")
    meta = e58.read_json(meta_path) if meta_path.exists() else {}
    blob = build_harvest(exp, model_key, prompt_key, e58.read_jsonl(e58.prompts_path(exp, prompt_key)), e58.read_jsonl(rp), meta)
    e58.write_json(harvest_path(run, exp, model_key, prompt_key), blob)
    return blob


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--exps", default="e39,e42")
    ap.add_argument("--models", default="all")
    ap.add_argument("--prompts", default="all")
    args = ap.parse_args()
    models = e58.MODEL_ORDER if args.models == "all" else args.models.split(",")
    prompts = e58.PROMPT_ORDER if args.prompts == "all" else args.prompts.split(",")
    for exp in args.exps.split(","):
        for m in models:
            for p in prompts:
                blob = harvest_one(args.run, exp, m, p)
                if blob:
                    print(json.dumps({"exp": exp, "config": blob["config"], "status_counts": blob["status_counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
