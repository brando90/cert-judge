#!/usr/bin/env python3
"""Shared helpers for judge variance experiments over VeriBench."""
from __future__ import annotations

import csv
import random
import re
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from utils.judge_caller import judge


def infer_split(path: Path) -> str:
    parts = list(path.parts)
    if "easy_set" in parts:
        return "easy"
    if "cs_set" in parts:
        return "cs"
    if "humaneval_set" in parts:
        return "humaneval"
    if "real_code" in parts or "realcode_set" in parts:
        return "real_code"
    if "security_6858" in parts or "security_set" in parts:
        return "security"
    if "security_python" in parts:
        return "security_python"
    return "other"


def collect_veribench_files(veribench_root: Path, max_files: int, seed: int) -> List[Path]:
    if not veribench_root.exists():
        return []

    skip_names = {"Common.lean", "Prelude.lean", "veribench.lean", "sandbox.lean", "tmp.lean", "55.lean"}
    files = [
        p for p in veribench_root.rglob("*.lean")
        if p.is_file() and p.name not in skip_names
    ]
    files = sorted(files)

    if max_files > 0 and len(files) > max_files:
        rng = random.Random(seed)
        rng.shuffle(files)
        files = sorted(files[:max_files])
    return files


def extract_theorem_blocks(text: str) -> List[Tuple[int, int]]:
    pat = re.compile(
        r"(?ms)^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b.*?(?=^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b|\Z)"
    )
    return [(m.start(), m.end()) for m in pat.finditer(text)]


def _remove_last_theorem_block(text: str) -> Tuple[str, bool]:
    spans = extract_theorem_blocks(text)
    if not spans:
        return text, False
    start, end = spans[-1]
    return text[:start] + "\n" + text[end:], True


def build_bug_ladder(code: str) -> List[str]:
    """5-level semantic bug ladder (0=clean, 4=maximally broken)."""
    ladder = [code]

    level1 = ladder[-1]
    changed = False
    for pat, repl in [
        (r"(?<!:)(?<!=)=(?!=)", "≤"),
        (r"\b>\b", "≥"),
        (r"\bAnd\b", "Or"),
        (r"∧", "∨"),
    ]:
        level1, n = re.subn(pat, repl, level1, count=1)
        changed = n > 0
        if changed:
            break
    if not changed:
        level1 += "\n-- bug_level_1"
    ladder.append(level1)

    level2 = ladder[-1]
    level2, changed = _remove_last_theorem_block(level2)
    if not changed:
        level2, n = re.subn(r"\bTrue\b", "False", level2, count=1)
        changed = n > 0
    if not changed:
        level2 += "\n-- bug_level_2"
    ladder.append(level2)

    level3 = ladder[-1]
    level3, n = re.subn(r"(?<!:)(?<!=)=(?!=)", "<", level3, count=1)
    changed = n > 0
    if not changed:
        level3, n = re.subn(r"∧", "∨", level3, count=1)
        changed = n > 0
    if not changed:
        level3 += "\n-- bug_level_3"
    ladder.append(level3)

    level4 = ladder[-1]
    theorem_sig = re.compile(r"(?ms)(^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b[^:]*:\s*)(.*?)(\s*:=)")

    def _to_true(match: re.Match[str]) -> str:
        return f"{match.group(1)}True{match.group(3)}"

    level4, n = theorem_sig.subn(_to_true, level4)
    if n > 0:
        level4 = re.sub(r"(?ms):=.*$", ":= trivial", level4)
    else:
        level4 += "\n-- bug_level_4\nexample : True := trivial\n"
    ladder.append(level4)

    return ladder


def local_prompt_judge(generated_theorem: str, reference_impl: str) -> dict:
    import difflib
    from utils.metrics import bleu_score, jaccard_tokens

    if generated_theorem == reference_impl:
        return {
            "score": 1.0,
            "mean": 1.0,
            "std": 0.0,
            "scores": [1.0],
            "reasoning": "Exact string match.",
            "model": "local_prompt_judge",
            "cached": False,
        }

    ratio = difflib.SequenceMatcher(None, reference_impl, generated_theorem).ratio()
    lev_like = 1.0 - ratio
    jacc = jaccard_tokens(reference_impl, generated_theorem)
    bleu = bleu_score(reference_impl, generated_theorem)
    textual_sim = max(0.0, min(1.0, 0.45 * (1.0 - lev_like) + 0.35 * jacc + 0.20 * bleu))

    trivial_hits = 0
    trivial_hits += generated_theorem.count(": True")
    trivial_hits += generated_theorem.count(":= trivial")
    trivial_hits += generated_theorem.count("True.intro")
    trivial_penalty = min(0.45, 0.08 * trivial_hits)

    score = textual_sim - trivial_penalty
    score = max(0.0, min(1.0, score))

    return {
        "score": score,
        "mean": score,
        "std": 0.0,
        "scores": [score],
        "reasoning": (
            f"local judge: sim={textual_sim:.3f}, trivial_penalty={trivial_penalty:.3f}"
        ),
        "model": "local_prompt_judge",
        "cached": False,
    }


def score_pair(
    generated_theorem: str,
    reference_impl: str,
    model: str,
    n_repeats: int,
    prompt_template: str,
    cache_namespace: str,
    judge_mode: str,
) -> dict:
    if judge_mode == "local":
        return local_prompt_judge(generated_theorem=generated_theorem, reference_impl=reference_impl)
    return judge(
        generated_theorem=generated_theorem,
        reference_impl=reference_impl,
        model=model,
        n_repeats=n_repeats,
        prompt_template=prompt_template,
        cache_namespace=cache_namespace,
    )


def write_csv(path: Path, rows: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
