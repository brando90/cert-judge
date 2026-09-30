#!/usr/bin/env python3
"""TLDR: Deterministic, fail-closed probe constructors for experiment 39 on top of cert-judge's
`probe_validation` (declaration spans, alpha-renaming, bug ladders, Lean elaboration): cumulative
theorem-statement deletion ladders, a conservative theorem reorder, proof-to-sorry stripping and irrelevant
theorem spam. Every transformed artifact is validated by `lake env lean` before it can be scored."""
from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[3] / "py_src")]
from cert_judge.probe_validation import (  # noqa: E402
    _TOP_LEVEL_BOUNDARY_RE, _find_assignment, Declaration, LeanCompiler, alpha_rename_bound_identifier,
    build_bug_ladder, mask_lean_noncode, sha256_text,
)

THEOREM_KEYWORDS = {"theorem", "lemma"}
_ATTRIBUTE_LINE = re.compile(r"[ \t]*@\[[^\n]*\][ \t]*\n?")
SPAM_THEOREMS = (
    "theorem e39_extra_fact_1 : (2 : Nat) + 2 = 4 := by decide",
    "theorem e39_extra_fact_2 : ∀ n : Nat, n + 0 = n := fun n => rfl",
    "theorem e39_extra_fact_3 : (3 : Nat) * 3 = 9 := by decide",
)


@dataclass(frozen=True)
class Artifact:
    level: int
    code: str
    sha256: str
    note: str


# A theorem head at column zero, optionally preceded ON THE SAME LINE by attributes (`@[simp] theorem foo`) and a
# `private`/`protected` modifier. cert-judge's core `declarations()` matches the keyword only at line start and so
# misses same-line attributes, which 13 of the 25 annotation-era golds use (PR #48 review, 09-30-2026); the core
# finder is left untouched so the frozen PTI-v0 pipeline stays reproducible, and this one is used for every probe.
_THEOREM_HEAD_RE = re.compile(
    r"(?m)^(?P<prefix>(?:@\[[^\]\n]*\][ \t]*)*(?:(?:private|protected)[ \t]+)?)"
    r"(?P<keyword>theorem|lemma)\b[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)


def theorem_decls(text: str) -> list[Declaration]:
    """Theorem/lemma declarations at column zero, including `@[attr] theorem` and `private theorem` heads."""
    masked = mask_lean_noncode(text)
    boundaries = [m.start() for m in _TOP_LEVEL_BOUNDARY_RE.finditer(masked)]
    out = []
    for m in _THEOREM_HEAD_RE.finditer(masked):
        start = m.start()
        end = next((b for b in boundaries if b > start), len(text))
        out.append(Declaration(keyword=m.group("keyword"), name=m.group("name"), start=start, end=end,
                               assign=_find_assignment(masked, start, end)))
    return out


def _extend_start(text: str, masked: str, start: int) -> int:
    """Pull a declaration's start back over its own doc comment and attribute lines.

    `declarations()` starts a span at the keyword, so the doc comment and `@[...]` lines that belong to it
    would otherwise be orphaned by a deletion (a dangling doc comment does not elaborate)."""
    pos = start
    while True:
        line_start = text.rfind("\n", 0, pos) + 1
        prev = text[line_start:pos]
        if pos > 0 and prev.strip() == "" and line_start < pos:
            pos = line_start                       # a blank prefix on the keyword's own line
        # attribute line directly above
        prev_line_start = text.rfind("\n", 0, max(pos - 1, 0)) + 1
        prev_line = text[prev_line_start:pos]
        if _ATTRIBUTE_LINE.fullmatch(prev_line):
            pos = prev_line_start
            continue
        # doc comment directly above (masked region is whitespace, raw ends with -/)
        before = text[:pos].rstrip()
        if before.endswith("-/"):
            open_pos = text.rfind("/--", 0, len(before))
            if open_pos >= 0 and masked[open_pos:pos].strip() == "" and "-/" not in text[open_pos:len(before) - 2]:
                pos = open_pos
                continue
        return pos


def _trim_end(text: str, masked: str, end: int) -> int:
    """Pull a declaration's end back over trailing whitespace and the NEXT declaration's doc/attributes."""
    pos = end
    while True:
        stripped = text[:pos].rstrip()
        if stripped.endswith("-/"):
            open_pos = text.rfind("/--", 0, len(stripped))
            if open_pos >= 0 and masked[open_pos:pos].strip() == "" and "-/" not in text[open_pos:len(stripped) - 2]:
                pos = open_pos
                continue
        line_start = text.rfind("\n", 0, len(stripped)) + 1
        if _ATTRIBUTE_LINE.fullmatch(text[line_start:len(stripped)] + "\n"):
            pos = line_start
            continue
        return len(stripped) + (1 if pos > len(stripped) else 0)


def _own_span(text: str, masked: str, decl: Declaration) -> tuple[int, int]:
    return _extend_start(text, masked, decl.start), _trim_end(text, masked, decl.end)


def cut_points(n: int, max_levels: int) -> list[int]:
    """Cumulative deletion counts for `min(n, max_levels)` levels, the last level removing everything."""
    if n <= 0:
        return []
    levels = min(n, max_levels)
    return [math.ceil(k * n / levels) for k in range(1, levels + 1)]


def delete_theorems_ladder(text: str, max_levels: int, validate=None) -> list[Artifact]:
    """Cumulatively delete theorem/lemma declarations from the END of the file (dependencies point backwards).

    Returns level-0 (the original) plus every validated degraded level; stops at the first level that fails
    validation, so a returned ladder is always a valid prefix of the declared design."""
    original = text
    decls = theorem_decls(original)
    ladder = [Artifact(0, original, sha256_text(original), "original")]
    for level, count in enumerate(cut_points(len(decls), max_levels), start=1):
        masked = mask_lean_noncode(original)
        spans = [_own_span(original, masked, d) for d in decls[len(decls) - count:]]
        code = original
        for start, end in sorted(spans, reverse=True):
            code = code[:start] + code[end:]
        code = re.sub(r"\n{3,}", "\n\n", code)
        if sha256_text(code) in {a.sha256 for a in ladder}:
            break
        if validate is not None and not validate(code):
            break
        names = ", ".join(d.name for d in decls[len(decls) - count:])
        ladder.append(Artifact(level, code, sha256_text(code), f"removed last {count} theorem(s): {names}"))
    return ladder


def bug_ladder(text: str, validate=None, levels: int = 4) -> list[Artifact]:
    """cert-judge's cumulative implementation-bug ladder, longest constructible prefix up to `levels`."""
    for depth in range(levels, 0, -1):
        try:
            artifacts = build_bug_ladder(text, levels=depth, validate=validate)
        except ValueError:
            continue
        return [Artifact(a.level, a.code, a.sha256, a.step.target if a.step else "original") for a in artifacts]
    return [Artifact(0, text, sha256_text(text), "original")]


def alpha(text: str, validate=None) -> Artifact | None:
    try:
        transform = alpha_rename_bound_identifier(text)
    except ValueError:
        return None
    if validate is not None and not validate(transform.code):
        return None
    return Artifact(1, transform.code, transform.sha256,
                    f"{transform.declaration}: {transform.old_name} -> {transform.new_name} ({transform.occurrence_count} occurrences)")


def _mentions(masked: str, start: int, end: int, name: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_'.]){re.escape(name)}(?![A-Za-z0-9_'])", masked[start:end]) is not None


def reorder(text: str, validate=None) -> Artifact | None:
    """Swap two adjacent theorem declarations, trying from the end of the file; the later one must not use
    the earlier one's name. Meaning-preserving by construction (Lean ignores declaration order between
    independent theorems); Lean validation still decides."""
    decls = theorem_decls(text)
    masked = mask_lean_noncode(text)
    for i in range(len(decls) - 1, 0, -1):
        first, second = decls[i - 1], decls[i]
        if first.name == second.name or _mentions(masked, second.start, second.end, first.name):
            continue
        a0, a1 = _own_span(text, masked, first)
        b0, b1 = _own_span(text, masked, second)
        if not (a0 < a1 <= b0 < b1):
            continue
        between = text[a1:b0]
        code = text[:a0] + text[b0:b1] + between + text[a0:a1] + text[b1:]
        if sha256_text(code) == sha256_text(text):
            continue
        if validate is not None and not validate(code):
            continue
        return Artifact(1, code, sha256_text(code), f"swapped {first.name} and {second.name}")
    return None


def strip_proofs(text: str, validate=None) -> Artifact | None:
    """Replace every theorem/lemma proof by `by sorry`, statements byte-identical."""
    decls = [d for d in theorem_decls(text) if d.assign is not None]
    if not decls:
        return None
    masked = mask_lean_noncode(text)
    code = text
    for d in sorted(decls, key=lambda d: d.start, reverse=True):
        proof_end = _trim_end(text, masked, d.end)
        code = code[:d.assign + 2] + " by sorry\n" + code[proof_end:]
    if sha256_text(code) == sha256_text(text):
        return None
    if validate is not None and not validate(code):
        return None
    return Artifact(1, code, sha256_text(code), f"{len(decls)} proof(s) replaced by sorry")


def spam(text: str, validate=None) -> Artifact | None:
    """Append three irrelevant, trivially true theorems with fresh names."""
    masked = mask_lean_noncode(text)
    if "e39_extra_fact" in masked:
        return None
    code = text.rstrip("\n") + "\n\n" + "\n".join(SPAM_THEOREMS) + "\n"
    if validate is not None and not validate(code):
        return None
    return Artifact(1, code, sha256_text(code), "appended 3 irrelevant true theorems")


def statement_texts(text: str) -> list[str]:
    """Theorem/lemma statements (keyword to `:=`), whitespace-normalized; used by the statements-equal check."""
    out = []
    for d in theorem_decls(text):
        stop = d.assign if d.assign is not None else d.end
        out.append(" ".join(text[d.start:stop].split()))
    return out


def theorem_names(text: str) -> list[str]:
    return [d.name for d in theorem_decls(text)]


def make_validator(lake_dir: Path | None, lake_bin: Path | None, timeout_seconds: int = 900):
    """A `code -> bool` Lean elaboration check, or None when Lean is unavailable (probes stay UNVALIDATED)."""
    if lake_dir is None or lake_bin is None:
        return None
    compiler = LeanCompiler(lake_dir, lake_bin, timeout_seconds=timeout_seconds)
    return compiler.validates
