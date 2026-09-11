#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
LEAN_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench"
AGENT_ROOT = REPO_ROOT / "data" / "generated_agents"
OUT_ROOT = REPO_ROOT / "experiments" / "04_veribench_validation" / "results"

PROMPT_NAME = "veribench_comparative_semantic_v1"

PROMPT_TEMPLATE = """You are grading semantic theorem/specification quality in Lean 4.

Goal:
Match expert human ratings of semantic correctness and completeness. Do not grade text similarity, proof style, theorem names, variable names, formatting, comments, or theorem order.

You must compare the GENERATED THEOREM/SPEC against the semantic guarantees implied by the REFERENCE IMPLEMENTATION/SPEC.

Use comparative prompting as the core judging mode:
1. Identify the key semantic guarantees required by the reference.
2. Identify what the generated theorem/spec actually guarantees.
3. Compare them side by side.
4. Penalize the most important semantic mismatch.
5. Assign a calibrated score from 0.0 to 1.0.

Important:
- A theorem that compiles or has a proof is not necessarily good.
- Reward exact semantic coverage of the reference behavior.
- Penalize missing postconditions or missing guarantees heavily.
- Penalize weakened assumptions/preconditions heavily if they make the theorem less useful.
- Penalize strengthened or impossible preconditions that make the theorem vacuous.
- Penalize vacuous truth heavily, including impossible assumptions or hypotheses that avoid the real case.
- Penalize wrong target theorems heavily, even if the theorem is provable.
- Penalize theorems that prove only type-correctness, existence, or trivial facts when the reference requires functional correctness.
- Penalize missing edge cases, such as empty structures, zero cases, failure cases, boundary conditions, or omitted branches.
- Penalize missing one direction of an iff/equivalence if the reference requires both directions.
- Penalize existential claims when the reference requires a universal or exact functional guarantee.
- If uncertain between two score bands, choose the lower band.

Do NOT perform a rigid checklist decomposition. Do NOT merely count syntactic overlap.
Use holistic side-by-side semantic comparison.

Rubric:
1.0 = semantically equivalent guarantees
0.8-0.9 = almost complete; only minor omission or harmless difference
0.6-0.7 = mostly right; one meaningful missing guarantee or moderate weakening
0.3-0.5 = partial; substantial semantic gaps
0.1-0.2 = weak match; only loosely related to the intended guarantee
0.0 = trivial, vacuous, incorrect, or semantically misaligned

REFERENCE IMPLEMENTATION/SPEC:
{reference_impl}

GENERATED THEOREM/SPEC:
{generated_theorem}

Return JSON only, with no markdown:
{{"score": <float from 0.0 to 1.0>, "reasoning": "<one concise sentence identifying the main semantic match or mismatch>"}}
"""

REPAIR_PROMPT = (
    "Return ONLY valid JSON with keys score (float in [0,1]) and reasoning (short string). "
    "No markdown, no prose before/after JSON."
)

TASK_IDS = [
    "0_bisect_right",
    "0_unsafeCopy_safe",
    "13_MyUppercase",
    "18_MyFibonacci",
    "1_MyAdd",
    "1_bisect_left",
    "2_heappush",
    "33_MyMinimum",
    "3_heappop",
    "43_replace_spaces",
    "4_json_decoder",
    "4_unsafeCounter_safe",
    "5_unsafeFormatString_safe",
    "9_pathTraversal_safe",
    "binary_search",
    "bubble_sort",
    "humaneval_13__gcd",
    "humaneval_31_is_prime",
    "humaneval_3_below_zero",
    "humaneval_47_median",
    "humaneval_8_sum_product",
    "insertion_sort",
    "merge_sort",
    "selection_sort",
]


@dataclass
class Candidate:
    item_id: str
    task_id: str
    generated_id: str
    source_model: str
    reference_path: Path
    generated_path: Path


def _get_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    key_paths = [
        Path(os.path.expanduser("~/keys/openai_bm_key_koyejolab.txt")),
        Path(os.path.expanduser("~/keys/openai_api_brandos_personal_key.txt")),
    ]
    for p in key_paths:
        try:
            k = p.read_text(encoding="utf-8").strip()
            if k:
                return k
        except Exception:
            continue
    raise RuntimeError("OPENAI_API_KEY not found")


def _extract_json_obj(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _coerce_score_reason(obj: dict[str, Any]) -> tuple[float, str] | None:
    if "score" not in obj or "reasoning" not in obj:
        return None
    try:
        score = float(obj["score"])
    except Exception:
        return None
    score = max(0.0, min(1.0, score))
    reasoning = str(obj["reasoning"]).strip()
    if not reasoning:
        reasoning = "No reasoning provided."
    return score, reasoning


def _resolve_reference(task_id: str) -> Path:
    hits = list(LEAN_ROOT.rglob(f"{task_id}.lean"))
    if not hits:
        raise FileNotFoundError(f"Missing reference for {task_id}")
    if len(hits) > 1:
        hits.sort(key=lambda p: len(str(p)))
    return hits[0]


def build_candidates() -> list[Candidate]:
    items: list[Candidate] = []
    agent_map = {"0": "codex", "1": "claude", "2": "llama"}
    for task_id in TASK_IDS:
        ref_path = _resolve_reference(task_id)
        for agent_idx in [0, 1, 2]:
            generated_id = f"{task_id}__agent{agent_idx}.lean"
            generated_path = AGENT_ROOT / generated_id
            if not generated_path.exists():
                continue
            item_id = f"{task_id}.lean::{generated_id}"
            items.append(
                Candidate(
                    item_id=item_id,
                    task_id=task_id,
                    generated_id=generated_id,
                    source_model=agent_map[str(agent_idx)],
                    reference_path=ref_path,
                    generated_path=generated_path,
                )
            )
    return items


def _judge_once(client: Any, model: str, prompt: str) -> str:
    resp = client.responses.create(
        model=model,
        temperature=0,
        reasoning={"effort": "high"},
        input=[
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
        ],
    )
    return resp.output_text


def run(args: argparse.Namespace) -> None:
    from openai import OpenAI

    now = datetime.now(timezone.utc)
    run_stamp = now.strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir / f"comparative_semantic_lean_judge_{run_stamp}"
    raw_dir = out_dir / "raw_responses"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    candidates = build_candidates()
    if args.limit > 0:
        candidates = candidates[: args.limit]

    if args.smoke:
        candidates = candidates[:3]

    client = OpenAI(api_key=_get_openai_key())

    rows: list[dict[str, Any]] = []
    for idx, cand in enumerate(candidates, start=1):
        ref_text = cand.reference_path.read_text(encoding="utf-8")
        gen_text = cand.generated_path.read_text(encoding="utf-8")
        prompt = PROMPT_TEMPLATE.format(reference_impl=ref_text, generated_theorem=gen_text)

        raw_text = _judge_once(client, args.judge_model, prompt)
        parsed = _extract_json_obj(raw_text)
        parsed_ok = False
        score = 0.0
        reasoning = "Unparseable response"

        if parsed is not None:
            coerced = _coerce_score_reason(parsed)
            if coerced is not None:
                score, reasoning = coerced
                parsed_ok = True

        if not parsed_ok:
            repair_prompt = f"{REPAIR_PROMPT}\n\nOriginal response:\n{raw_text}"
            repair_text = _judge_once(client, args.judge_model, repair_prompt)
            repair_parsed = _extract_json_obj(repair_text)
            if repair_parsed is not None:
                coerced = _coerce_score_reason(repair_parsed)
                if coerced is not None:
                    score, reasoning = coerced
                    parsed_ok = True
                    raw_text = repair_text

        raw_path = raw_dir / f"{idx:04d}_{cand.generated_id.replace('.lean','')}.txt"
        raw_path.write_text(raw_text, encoding="utf-8")

        rows.append(
            {
                "item_id": cand.item_id,
                "task_id": cand.task_id,
                "generated_id": cand.generated_id,
                "source_model": cand.source_model,
                "judge_model": args.judge_model,
                "judge_prompt_name": PROMPT_NAME,
                "score": score,
                "reasoning": reasoning,
                "parse_ok": parsed_ok,
                "raw_response_path": str(raw_path),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    csv_path = out_dir / "comparative_semantic_lean_judge_scores.csv"
    fieldnames = [
        "item_id",
        "task_id",
        "generated_id",
        "source_model",
        "judge_model",
        "judge_prompt_name",
        "score",
        "reasoning",
        "parse_ok",
        "raw_response_path",
        "timestamp",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    parse_ok_n = sum(1 for r in rows if r["parse_ok"])
    scores = [float(r["score"]) for r in rows]
    summary = {
        "output_csv": str(csv_path),
        "num_examples": len(rows),
        "parse_success_rate": (parse_ok_n / len(rows)) if rows else 0.0,
        "score_min": min(scores) if scores else None,
        "score_mean": (sum(scores) / len(scores)) if scores else None,
        "score_max": max(scores) if scores else None,
        "failures": [r["item_id"] for r in rows if not r["parse_ok"]],
        "judge_model": args.judge_model,
        "judge_prompt_name": PROMPT_NAME,
        "smoke": args.smoke,
    }
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--judge-model", default="gpt-5.3-codex")
    p.add_argument("--out-dir", type=Path, default=OUT_ROOT)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    run(parse_args())
