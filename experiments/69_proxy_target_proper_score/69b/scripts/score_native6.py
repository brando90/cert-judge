#!/usr/bin/env python3
"""Native 6-class scoring for experiment 69B. Dry-run by default. No agy. Cap $27.

SNAP (local GPU, $0):
  python3 score_native6.py --backend vllm --model Qwen/Qwen3-8B --packet-root /path/to/main_rating_task --out forecasts.jsonl

API (plan lane, cap $27, model must not be Gemini or agy):
  python3 score_native6.py --backend openai --model "$CJ69_API_MODEL" \\
    --base-url "$CJ69_API_BASE" --api-key-file ~/keys/openai_api_brandos_personal_key.txt \\
    --usd-per-call 0.02 --packet-root /path/to/main_rating_task --out forecasts.jsonl

This VM: python3 score_native6.py --dry-run --out /tmp/69b_dry.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    RUBRIC, SPEND_CAP_USD, build_user, digit_probs_from_top, items_from_ratings,
    point_mass, read_capped, reject_model, sha256_text, within_cap,
)


def pack_prompts(items: list[dict], packet: Path | None) -> list[dict]:
    out = []
    for item in items:
        if packet is None:
            user, truncated = f"ITEM {item['item_id']} (packet missing)", False
        else:
            gold, gcut = read_capped(packet, item["gold_file"])
            cand, ccut = read_capped(packet, item["candidate_file"])
            user, truncated = build_user(gold, cand), gcut or ccut
        out.append({**item, "system": RUBRIC, "user": user, "truncated": truncated,
                    "prompt_sha256": sha256_text(RUBRIC + user)})
    return out


def openai_one(base: str, key: str, model: str, system: str, user: str) -> tuple[list[tuple[str, float]], dict]:
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "max_tokens": 1,
        "logprobs": True,
        "top_logprobs": 10,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode())
    choice = payload["choices"][0]
    top = choice.get("logprobs", {}).get("content", [{}])[0].get("top_logprobs", [])
    pairs = [(row["token"], float(row["logprob"])) for row in top]
    return pairs, payload.get("usage") or {}


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", choices=("vllm", "openai"), default="openai")
    ap.add_argument("--model", default="")
    ap.add_argument("--packet-root", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default=os.environ.get("CJ69_API_BASE", "https://api.openai.com/v1"))
    ap.add_argument("--api-key-file", default="")
    ap.add_argument("--usd-per-call", type=float, default=0.0)
    ap.add_argument("--cap", type=float, default=SPEND_CAP_USD)
    ap.add_argument("--probe", type=int, default=2)
    args = ap.parse_args()
    items = items_from_ratings()
    if len(items) != 100:
        raise SystemExit(f"expected 100 items, found {len(items)}")
    packet = Path(args.packet_root) if args.packet_root else None
    if packet is not None and not (packet / items[0]["gold_file"]).is_file():
        raise SystemExit(f"packet missing {items[0]['gold_file']}")
    prompts = pack_prompts(items, packet)
    model = args.model or ("dry-run" if args.dry_run else "")
    if not args.dry_run:
        if not model:
            raise SystemExit("set --model or CJ69_API_MODEL")
        reject_model(model)
    rows = []
    if args.dry_run:
        for rec in prompts:
            rows.append({
                "judge": "dry_run_point5", "model": "dry-run", "source": "dry_run",
                "item_id": rec["item_id"], "task": rec["task"], "split": rec["split"],
                "probs": point_mass(5), "digit_mass": 1.0, "cost_usd": 0.0,
                "prompt_sha256": rec["prompt_sha256"], "truncated": rec["truncated"],
            })
        write_rows(Path(args.out), rows)
        print(json.dumps({"status": "DRY_RUN", "n": len(rows), "cost_usd": 0}))
        return
    if args.backend == "vllm":
        from vllm import LLM, SamplingParams
        llm = LLM(model, tensor_parallel_size=int(os.environ.get("CJ69_TP", "1")), dtype="bfloat16",
                  max_model_len=16384, gpu_memory_utilization=0.9)
        tok = llm.get_tokenizer()
        chat = []
        for rec in prompts:
            msgs = [{"role": "system", "content": rec["system"]}, {"role": "user", "content": rec["user"]}]
            try:
                chat.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
            except TypeError:
                chat.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))
        outs = llm.generate(chat, SamplingParams(max_tokens=1, temperature=0.0, logprobs=20))
        for rec, out in zip(prompts, outs):
            lp = out.outputs[0].logprobs[0]
            pairs = [(tok.convert_ids_to_tokens(tid), obj.logprob) for tid, obj in lp.items()]
            probs, mass = digit_probs_from_top(pairs)
            rows.append({
                "judge": "snap_qwen3_8b", "model": model, "source": "vllm",
                "item_id": rec["item_id"], "task": rec["task"], "split": rec["split"],
                "probs": None if probs is None else [float(x) for x in probs],
                "digit_mass": mass, "cost_usd": 0.0, "status": "measured" if probs is not None else "unmeasured_no_logprobs",
                "prompt_sha256": rec["prompt_sha256"], "truncated": rec["truncated"],
            })
        write_rows(Path(args.out), rows)
        print(json.dumps({"status": "VLLM", "n": len(rows), "cost_usd": 0, "measured": sum(r["probs"] is not None for r in rows)}))
        return
    key = Path(args.api_key_file).read_text().strip()
    if args.usd_per_call <= 0:
        raise SystemExit("API scoring needs --usd-per-call from the probe price so the $27 cap can be enforced")
    spent = 0.0
    order = prompts[: args.probe] + prompts[args.probe:]
    for i, rec in enumerate(order):
        if not within_cap(spent, args.usd_per_call, args.cap):
            print(json.dumps({"status": "STOPPED_CAP", "spent": spent, "n_written": len(rows)}))
            break
        pairs, _usage = openai_one(args.base_url, key, model, rec["system"], rec["user"])
        probs, mass = digit_probs_from_top(pairs)
        spent += args.usd_per_call
        rows.append({
            "judge": "api_frontier", "model": model, "source": "api",
            "item_id": rec["item_id"], "task": rec["task"], "split": rec["split"],
            "probs": None if probs is None else [float(x) for x in probs],
            "digit_mass": mass, "cost_usd": args.usd_per_call,
            "status": "measured" if probs is not None else "unmeasured_no_logprobs",
            "prompt_sha256": rec["prompt_sha256"], "truncated": rec["truncated"],
        })
        if i + 1 == args.probe and not within_cap(spent, args.usd_per_call * (len(prompts) - args.probe), args.cap):
            print(json.dumps({"status": "STOPPED_AFTER_PROBE", "spent": spent, "projected": args.usd_per_call * len(prompts)}))
            break
    write_rows(Path(args.out), rows)
    print(json.dumps({"status": "API", "n": len(rows), "cost_usd": spent, "cap": args.cap}))


if __name__ == "__main__":
    main()
