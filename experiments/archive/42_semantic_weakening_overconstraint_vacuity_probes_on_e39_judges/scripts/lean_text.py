#!/usr/bin/env python3
"""TLDR: Conservative text-level Lean 4 parsing for experiment 42's probe builder: column-zero theorem/lemma/def/abbrev
declarations (with same-line attributes and modifiers), their heads split into bracketed binder groups, the type and
the proof, the namespace a declaration lives in, top-level arrow premises, comment spans, and word-boundary renaming.
Everything here is text only; Lean elaboration decides every probe's validity (fail-closed). Zero model calls."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[4] / "py_src")]
from cert_judge.probe_validation import _TOP_LEVEL_BOUNDARY_RE, mask_lean_noncode  # noqa: E402

OPEN = {"(": ")", "{": "}", "[": "]", "⦃": "⦄"}
CLOSE = {v: k for k, v in OPEN.items()}
_MODIFIERS = r"(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)[ \t]+)*"
DECL_RE = re.compile(
    r"(?m)^(?P<prefix>(?:@\[[^\]\n]*\][ \t]*)*" + _MODIFIERS + r")"
    r"(?P<keyword>theorem|lemma|def|abbrev)\b[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_'.?!]*)"
)
NAMED_DECL_RE = re.compile(
    r"(?m)^(?:(?:@\[[^\]\n]*\][ \t]*)*" + _MODIFIERS + r")"
    r"(?P<keyword>theorem|lemma|def|abbrev|opaque|axiom|inductive|structure|class|instance)\b[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_'.?!]*)"
)
_IDENT_CHARS = r"A-Za-z0-9_'?!"
_BINDER_STOP = re.compile(r"(∀|∃!|∃|fun\b|λ|let\b|have\b|show\b|Σ|if\b|match\b|∑|∏)")
_ARROW = re.compile(r"→|->")
_IFF = re.compile(r"↔|<->")


@dataclass
class Decl:
    keyword: str
    name: str
    start: int                    # line start, including same-line attributes and modifiers
    kw_start: int                 # position of the keyword
    name_end: int
    end: int                      # next top-level boundary (raw span end)
    header_end: int | None        # position of the top-level `:=` (or match arm / `where`), None if not found
    assign: int | None            # position of the top-level `:=` if the header ends with one
    colon: int | None             # depth-0 `:` separating binders from the type
    binders: list[tuple[int, int]] = field(default_factory=list)
    binders_ok: bool = True       # every token before the colon sits inside a bracketed binder group
    namespace: tuple[str, ...] = ()

    @property
    def is_theorem(self) -> bool:
        return self.keyword in ("theorem", "lemma")


def namespace_at(masked: str, position: int) -> tuple[str, ...]:
    stack: list[tuple[str, str]] = []
    for m in re.finditer(r"(?m)^(namespace|section|noncomputable section|end)\b[ \t]*([^\s]*)", masked[:position]):
        kind, name = m.group(1), m.group(2)
        if kind == "namespace":
            stack.append(("namespace", name))
        elif kind in ("section", "noncomputable section"):
            stack.append(("section", name))
        elif stack:
            stack.pop()
    return tuple(name for kind, name in stack if kind == "namespace")


def _scan_header(masked: str, pos: int, end: int):
    """Scan a declaration head from just after its name. Returns (header_end, assign, colon, binders, ok)."""
    depth, colon, binders, ok, group_start, pending_let = 0, None, [], True, None, 0
    i = pos
    while i < end:
        ch = masked[i]
        if (depth == 0 and colon is not None and re.match(r"(let|have)\b", masked[i:i + 5])
                and not re.match(rf"[{_IDENT_CHARS}.]", masked[i - 1])):
            pending_let += 1                   # a `let x := v` / `have h := v` inside the type owns the next `:=`
        if depth == 0 and pending_let and masked.startswith(":=", i):
            pending_let -= 1
            i += 2
            continue
        if ch in OPEN:
            if depth == 0 and colon is None:
                group_start = i
            depth += 1
        elif ch in CLOSE:
            depth -= 1
            if depth == 0 and colon is None and group_start is not None:
                binders.append((group_start, i + 1))
                group_start = None
        elif depth == 0:
            if masked.startswith(":=", i):
                return i, i, colon, binders, ok
            if ch == ":" and colon is None:
                colon = i
            elif ch == "\n" and re.match(r"\n[ \t]*\|", masked[i:]):
                return i, None, colon, binders, ok
            elif (masked.startswith("where", i) and masked[i - 1].isspace()
                  and (i + 5 >= len(masked) or not re.match(rf"[{_IDENT_CHARS}]", masked[i + 5]))):
                return i, None, colon, binders, ok
            elif colon is None and not ch.isspace():
                ok = False
        i += 1
    return None, None, colon, binders, ok


def decls(text: str, masked: str | None = None) -> list[Decl]:
    masked = mask_lean_noncode(text) if masked is None else masked
    boundaries = [m.start() for m in _TOP_LEVEL_BOUNDARY_RE.finditer(masked)]
    out = []
    for m in DECL_RE.finditer(masked):
        start = m.start()
        end = next((b for b in boundaries if b > start), len(text))
        header_end, assign, colon, binders, ok = _scan_header(masked, m.end("name"), end)
        out.append(Decl(keyword=m.group("keyword"), name=m.group("name"), start=start, kw_start=m.start("keyword"),
                        name_end=m.end("name"), end=end, header_end=header_end, assign=assign, colon=colon,
                        binders=binders, binders_ok=ok, namespace=namespace_at(masked, start)))
    return out


def theorems(text: str) -> list[Decl]:
    return [d for d in decls(text) if d.is_theorem]


def find(decl_list: list[Decl], name: str) -> Decl | None:
    hits = [d for d in decl_list if d.name == name]
    return hits[0] if len(hits) == 1 else None


def qualified(decl: Decl) -> str:
    return ".".join(list(decl.namespace) + [decl.name])


def named_decls(text: str) -> list[tuple[str, str]]:
    """(keyword, fully qualified name) of every named column-zero declaration, for `#print` comparisons."""
    masked = mask_lean_noncode(text)
    out = []
    for m in NAMED_DECL_RE.finditer(masked):
        ns = namespace_at(masked, m.start())
        out.append((m.group("keyword"), ".".join(list(ns) + [m.group("name")])))
    return out


def trim_end(text: str, end: int) -> int:
    """Pull a span end back over trailing whitespace and a following declaration's doc comment / attribute lines."""
    masked = mask_lean_noncode(text)
    pos = end
    while True:
        stripped = text[:pos].rstrip()
        if stripped.endswith("-/"):
            open_pos = text.rfind("/--", 0, len(stripped))
            if open_pos >= 0 and masked[open_pos:pos].strip() == "" and "-/" not in text[open_pos:len(stripped) - 2]:
                pos = open_pos
                continue
            open_pos = text.rfind("/-", 0, len(stripped))
            if open_pos >= 0 and masked[open_pos:pos].strip() == "" and "-/" not in text[open_pos:len(stripped) - 2]:
                pos = open_pos
                continue
        line_start = text.rfind("\n", 0, len(stripped)) + 1
        line = text[line_start:len(stripped)]
        if re.fullmatch(r"[ \t]*@\[[^\n]*\][ \t]*", line) or (line.strip().startswith("--") and masked[line_start:len(stripped)].strip() == ""):
            pos = line_start
            continue
        return len(stripped)


def extend_start(text: str, start: int) -> int:
    """Pull a span start back over the doc comment and attribute lines directly above it (they belong to it)."""
    masked = mask_lean_noncode(text)
    pos = start
    while True:
        before = text[:pos].rstrip()
        if before.endswith("-/"):
            open_pos = text.rfind("/--", 0, len(before))
            if open_pos >= 0 and masked[open_pos:pos].strip() == "" and "-/" not in text[open_pos:len(before) - 2]:
                pos = text.rfind("\n", 0, open_pos) + 1 if text[text.rfind("\n", 0, open_pos) + 1:open_pos].strip() == "" else open_pos
                continue
        line_start = text.rfind("\n", 0, max(len(before), 0)) + 1
        if re.fullmatch(r"[ \t]*@\[[^\n]*\][ \t]*", text[line_start:len(before)]) and len(before) > 0:
            pos = line_start
            continue
        return pos


def support_theorems(text: str) -> set[str]:
    """Theorems used by a non-theorem declaration or command (e.g. an implementation's `decreasing_by` proof):
    implementation support, left unchanged by the specification probes."""
    masked = mask_lean_noncode(text)
    ths = theorems(text)
    outside = list(masked)
    for d in ths:
        for i in range(d.start, d.end):
            if outside[i] != "\n":
                outside[i] = " "
    outside_text = "".join(outside)
    return {d.name for d in ths if mentions(outside_text, d.name)}


def head_text(text: str, d: Decl) -> str:
    """Binders and type of a declaration (from just after its name to the end of its header), whitespace-normalized."""
    stop = d.header_end if d.header_end is not None else d.end
    return " ".join(text[d.name_end:stop].split())


def binder_texts(text: str, d: Decl) -> list[str]:
    return [text[a:b] for a, b in d.binders]


def type_text(text: str, d: Decl) -> str | None:
    if d.colon is None or d.header_end is None:
        return None
    return text[d.colon + 1:d.header_end].strip()


def proof_span(text: str, d: Decl) -> tuple[int, int] | None:
    if d.assign is None:
        return None
    return d.assign + 2, trim_end(text, d.end)


def split_premises(type_str: str) -> tuple[list[str], str]:
    """Split a type at its depth-0 arrows into (premises, conclusion). Stops at the first depth-0 binder keyword
    (its scope runs to the end); a depth-0 `↔` (looser than `→`) makes the whole type one conclusion."""
    masked = mask_lean_noncode(type_str)
    depth, cuts = 0, []
    i = 0
    while i < len(masked):
        ch = masked[i]
        if ch in OPEN or ch == "⟨":
            depth += 1
        elif ch in CLOSE or ch == "⟩":
            depth -= 1
        elif depth == 0:
            if _IFF.match(masked, i):
                return [], type_str.strip()
            if _BINDER_STOP.match(masked, i) and (i == 0 or not re.match(rf"[{_IDENT_CHARS}]", masked[i - 1])):
                break
            m = _ARROW.match(masked, i)
            if m:
                cuts.append((i, m.end()))
                i = m.end()
                continue
        i += 1
    if not cuts:
        return [], type_str.strip()
    pieces, prev = [], 0
    for a, b in cuts:
        pieces.append(type_str[prev:a].strip())
        prev = b
    return pieces, type_str[prev:].strip()


def comment_spans(text: str) -> list[tuple[int, int, str]]:
    """(start, end, kind) for every comment: kind in line / block / doc (`/--`) / moddoc (`/-!`). Strings and char
    literals are skipped exactly as `mask_lean_noncode` does."""
    spans, i, n = [], 0, len(text)
    while i < n:
        if text.startswith("/-", i):
            kind = "doc" if text.startswith("/--", i) and not text.startswith("/--/", i) else "moddoc" if text.startswith("/-!", i) else "block"
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/-", j):
                    depth += 1
                    j += 2
                elif text.startswith("-/", j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            spans.append((i, j, kind))
            i = j
        elif text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            spans.append((i, j, "line"))
            i = j
        elif text[i] == '"':
            j, escaped = i + 1, False
            while j < n:
                if escaped:
                    escaped = False
                elif text[j] == "\\":
                    escaped = True
                elif text[j] == '"':
                    break
                j += 1
            i = j + 1
        elif text[i] == "'" and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_'")):
            end, esc = i + 1, False
            while end < n and text[end] != "\n":
                if text[end] == "'" and not esc:
                    end += 1
                    break
                esc = text[end] == "\\" and not esc
                end += 1
            i = end if end > i + 1 and text[end - 1] == "'" else i + 1
        else:
            i += 1
    return spans


def rename(text: str, mapping: dict[str, str]) -> str:
    """Word-boundary identifier renaming (Lean identifiers may contain ' ? !; a dotted prefix is not renamed)."""
    if not mapping:
        return text
    pattern = re.compile(rf"(?<![{_IDENT_CHARS}.])(" + "|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True))
                         + rf")(?![{_IDENT_CHARS}])")
    return pattern.sub(lambda m: mapping[m.group(1)], text)


def mentions(text: str, name: str) -> bool:
    return re.search(rf"(?<![{_IDENT_CHARS}.]){re.escape(name)}(?![{_IDENT_CHARS}])", text) is not None


def imports(text: str) -> list[str]:
    return re.findall(r"(?m)^import\s+(\S+)", text)
