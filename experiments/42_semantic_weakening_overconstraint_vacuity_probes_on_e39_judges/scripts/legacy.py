#!/usr/bin/env python3
"""TLDR: (Vendored unchanged from experiment 39's scripts/legacy.py except PROMPT_DIR, which reads experiment 39's prompts/.) Render and parse the cert-judge paper's legacy judge prompts (P1_BASELINE, P4_CHECKLIST, P8_STRICT_B and
the deliberately lexical BAD_STRINGY) exactly as experiment 16 fed them: the reference is the gold's LAST
theorem/lemma block and the candidate is the whole candidate file; the verdict is a JSON score in [0, 1]."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[2] / "39_label_free_proxy_index_train_val_test_over_judge_families/prompts"   # experiment 39's ported prompts, read-only
LEGACY_RUBRICS = ("P1_BASELINE", "P4_CHECKLIST", "P8_STRICT_B", "BAD_STRINGY")
# The transport requires a non-empty system prompt (experiment 103's task-file markers). The paper sent the
# template as a single message; this one-line system prompt adds no grading instruction.
SYSTEM = "Follow the instructions in the message exactly and answer with only the requested JSON object."
# Verbatim from experiments/archive/02_neurips_reviews/utils/veribench_variance_utils.py:extract_theorem_blocks
_THEOREM_BLOCK = re.compile(
    r"(?ms)^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b.*?(?=^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b|\Z)"
)


def template(rubric: str) -> str:
    if rubric not in LEGACY_RUBRICS:
        raise KeyError(rubric)
    return (PROMPT_DIR / f"{rubric}.txt").read_text(encoding="utf-8")


def last_theorem_block(text: str) -> str:
    """Experiment 16's `_extract_last_theorem_block`: the final theorem/lemma block, else the whole text."""
    spans = [(m.start(), m.end()) for m in _THEOREM_BLOCK.finditer(text)]
    if not spans:
        return text
    start, end = spans[-1]
    block = text[start:end].strip()
    return block if block else text


def render(rubric: str, gold_text: str, candidate_text: str) -> tuple[str, str]:
    user = template(rubric).format(reference_impl=last_theorem_block(gold_text), generated_theorem=candidate_text)
    return SYSTEM, user


def _top_level_objects(text: str) -> list[dict]:
    out, start, depth, in_str, esc = [], None, 0, False, False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            start = i if depth == 0 else start
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(text[start:i + 1])
                    if isinstance(obj, dict):
                        out.append(obj)
                except json.JSONDecodeError:
                    pass
                start = None
    return out


def parse(text: str) -> tuple[float, float, dict]:
    """Return (raw score, normalized score, verdict object); raise ValueError on any ambiguity."""
    found = []
    for obj in _top_level_objects(text):
        value = obj.get("score")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if math.isfinite(value) and 0.0 <= value <= 1.0:
            found.append((float(value), obj))
    if not found:
        raise ValueError("no valid 'score' in [0, 1] in response")
    if len({v for v, _ in found}) != 1:
        raise ValueError("conflicting verdicts in response")
    raw, obj = found[0]
    return raw, raw, obj


def fingerprint(rubric: str) -> str:
    import hashlib
    return hashlib.sha256((SYSTEM + template(rubric)).encode()).hexdigest()
