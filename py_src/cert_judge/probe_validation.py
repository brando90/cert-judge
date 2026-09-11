"""Deterministic construction and Lean validation for PTI-v0 probes.

The transformations here are deliberately conservative.  They never add a
comment merely to manufacture a distinct file, and callers must elaborate all
included artifacts with the pinned project toolchain before scoring them.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

_DECLARATION_RE = re.compile(
    r"(?m)^(?P<keyword>def|theorem|lemma|example|opaque|abbrev|axiom|#eval|#check)\b"
    r"(?:\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*))?"
)
_TOP_LEVEL_BOUNDARY_RE = re.compile(
    r"(?m)^(?:@\[|private\b|protected\b|noncomputable\b|partial\b|unsafe\b|"
    r"def\b|theorem\b|lemma\b|example\b|opaque\b|abbrev\b|axiom\b|"
    r"inductive\b|structure\b|class\b|instance\b|mutual\b|initialize\b|"
    r"builtin_initialize\b|macro\b|syntax\b|notation\b|infixl?\b|infixr\b|"
    r"prefix\b|postfix\b|namespace\b|section\b|end\b|open\b|export\b|"
    r"set_option\b|attribute\b|variable\b|variables\b|universe\b|universes\b|"
    r"include\b|omit\b|#eval\b|#check\b|#print\b|#reduce\b|#synth\b|"
    r"#guard\b|#assert\b)"
)
_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_']*\b")
_SPEC_NAME_RE = re.compile(
    r"(?:^|_)(?:precondition|postcondition|specification|spec|tests?|checks?|"
    r"run(?:Tests?|Checks?))(?=$|_|[A-Z0-9])|"
    r"(?:Precondition|Postcondition|Specification|Spec|Tests?|Checks?|"
    r"Run(?:Tests?|Checks?))(?=$|_|[A-Z0-9])"
)
_TEMP_PROBE_PREFIX_RE = re.compile(
    r"^(?:.*[/\\])?pti_probe_[^:/\\]+\.lean(?=:\d+:\d+:)"
)


@dataclass(frozen=True)
class Declaration:
    keyword: str
    name: str
    start: int
    end: int
    assign: int | None


@dataclass(frozen=True)
class TransformStep:
    kind: str
    target: str
    before: str
    after: str
    start: int
    end: int


@dataclass(frozen=True)
class ProbeArtifact:
    level: int
    code: str
    sha256: str
    step: TransformStep | None


@dataclass(frozen=True)
class AlphaTransform:
    code: str
    sha256: str
    declaration: str
    old_name: str
    new_name: str
    occurrence_count: int


@dataclass(frozen=True)
class CompileResult:
    ok: bool
    returncode: int
    output: str


def classify_compile_error(result: CompileResult) -> str:
    """Classify a failed Lean invocation without hiding environment failures."""

    if result.ok:
        return "ok"
    output = result.output.lower()
    if result.returncode == 124 or output.startswith("timeout after"):
        return "timeout"
    if (
        ("object file" in output and "does not exist" in output)
        or "unknown module prefix" in output
        or "invalid import" in output
    ):
        return "unresolved_import"
    if any(
        marker in output
        for marker in (
            "unexpected token",
            "unexpected end of input",
            "invalid syntax",
            "parser error",
        )
    ):
        return "parse"
    if "termination" in output or "decreasing argument" in output:
        return "termination"
    if any(
        marker in output
        for marker in (
            "application type mismatch",
            "type mismatch",
            "failed to synthesize",
            "unknown identifier",
            "declaration has metavariables",
        )
    ):
        return "type_or_elaboration"
    return "elaboration"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mask_lean_noncode(text: str) -> str:
    """Mask strings and nested comments while preserving offsets/newlines."""

    chars = list(text)
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(chars):
        if block_depth:
            if text.startswith("/-", i):
                chars[i : i + 2] = "  "
                block_depth += 1
                i += 2
            elif text.startswith("-/", i):
                chars[i : i + 2] = "  "
                block_depth -= 1
                i += 2
            else:
                if chars[i] != "\n":
                    chars[i] = " "
                i += 1
            continue
        if in_string:
            if chars[i] != "\n":
                chars[i] = " "
            if escaped:
                escaped = False
            elif text[i] == "\\":
                escaped = True
            elif text[i] == '"':
                in_string = False
            i += 1
            continue
        if text.startswith("/-", i):
            chars[i : i + 2] = "  "
            block_depth = 1
            i += 2
        elif text.startswith("--", i):
            while i < len(chars) and chars[i] != "\n":
                chars[i] = " "
                i += 1
        elif text[i] == '"':
            chars[i] = " "
            in_string = True
            i += 1
        elif text[i] == "'" and (
            i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_'")
        ):
            end = i + 1
            escaped_character = False
            while end < len(text) and text[end] != "\n":
                if text[end] == "'" and not escaped_character:
                    end += 1
                    break
                if text[end] == "\\" and not escaped_character:
                    escaped_character = True
                else:
                    escaped_character = False
                end += 1
            if end <= len(text) and end > i + 1 and text[end - 1] == "'":
                for position in range(i, end):
                    if chars[position] != "\n":
                        chars[position] = " "
                i = end
            else:
                i += 1
        else:
            i += 1
    return "".join(chars)


def _find_assignment(masked: str, start: int, end: int) -> int | None:
    position = masked.find(":=", start, end)
    return None if position < 0 else position


def declarations(text: str) -> tuple[Declaration, ...]:
    """Return conservative column-zero Lean declaration spans."""

    masked = mask_lean_noncode(text)
    matches = list(_DECLARATION_RE.finditer(masked))
    boundaries = [match.start() for match in _TOP_LEVEL_BOUNDARY_RE.finditer(masked)]
    result: list[Declaration] = []
    for match in matches:
        end = next(
            (position for position in boundaries if position > match.start()), len(text)
        )
        result.append(
            Declaration(
                keyword=match.group("keyword"),
                name=match.group("name") or match.group("keyword"),
                start=match.start(),
                end=end,
                assign=_find_assignment(masked, match.start(), end),
            )
        )
    return tuple(result)


def _identifier_spans(
    text: str, start: int, end: int, name: str
) -> list[tuple[int, int]]:
    pattern = re.compile(rf"(?<![A-Za-z0-9_']){re.escape(name)}(?![A-Za-z0-9_'])")
    return [(m.start(), m.end()) for m in pattern.finditer(text, start, end)]


def _fresh_alpha_name(masked: str) -> str:
    identifiers = set(_IDENTIFIER_RE.findall(masked))
    index = 0
    while f"ptiAlpha{index}" in identifiers:
        index += 1
    return f"ptiAlpha{index}"


def alpha_rename_bound_identifier(text: str) -> AlphaTransform:
    """Rename one explicit theorem binder and all of its bound occurrences.

    To make the semantic guarantee auditable without implementing the entire
    Lean elaborator, the selected binder must have at least one use in the
    declaration header and no occurrence in the proof.  All occurrences from
    its binder declaration through ``:=`` are renamed, and the fresh name must
    not occur anywhere in the file.  Files without such a conservative target
    are rejected rather than changed by a no-op/comment fallback.
    """

    masked = mask_lean_noncode(text)
    fresh_name = _fresh_alpha_name(masked)
    for declaration in declarations(text):
        if (
            declaration.keyword not in {"theorem", "lemma"}
            or declaration.assign is None
        ):
            continue
        header = masked[declaration.start : declaration.assign]
        binder_pattern = re.compile(r"[({]\s*([^:(){}]+?)\s*:")
        binder_declarations: dict[str, list[int]] = {}
        for group in binder_pattern.finditer(header):
            group_start = declaration.start + group.start(1)
            for name_match in _IDENTIFIER_RE.finditer(group.group(1)):
                name = name_match.group(0)
                if name == "_":
                    continue
                binder_declarations.setdefault(name, []).append(
                    group_start + name_match.start()
                )
        for old_name, positions in binder_declarations.items():
            if len(positions) != 1:
                continue
            binder_start = positions[0]
            relative_binder_start = binder_start - declaration.start
            later_header = header[relative_binder_start + len(old_name) :]
            if re.search(
                rf"(?:∀|fun|let)\s+{re.escape(old_name)}(?![A-Za-z0-9_'])",
                later_header,
            ):
                continue
            header_spans = _identifier_spans(
                masked, binder_start, declaration.assign, old_name
            )
            proof_spans = _identifier_spans(
                masked, declaration.assign + 2, declaration.end, old_name
            )
            if len(header_spans) < 2 or proof_spans:
                continue
            transformed = text
            for start, end in reversed(header_spans):
                transformed = transformed[:start] + fresh_name + transformed[end:]
            if transformed == text or ":=:=" in transformed:
                continue
            return AlphaTransform(
                code=transformed,
                sha256=sha256_text(transformed),
                declaration=declaration.name,
                old_name=old_name,
                new_name=fresh_name,
                occurrence_count=len(header_spans),
            )
    raise ValueError(
        "no conservative alpha-renaming target with a bound header occurrence"
    )


_BUG_MUTATIONS: tuple[tuple[str, str, str], ...] = (
    (r"==", "!=", "boolean equality reversed"),
    (r"!=", "==", "boolean inequality reversed"),
    (r"&&", "||", "boolean conjunction weakened to disjunction"),
    (r"\|\|", "&&", "boolean disjunction strengthened to conjunction"),
    (r"≤", "<", "non-strict upper comparison made strict"),
    (r"≥", ">", "non-strict lower comparison made strict"),
    (r"(?<![<:])<(?![=>])", "≤", "strict upper comparison made non-strict"),
    (r"(?<![-=:])>(?![=])", "≥", "strict lower comparison made non-strict"),
    (r"(?<![+:])\+(?![+=])", "-", "addition replaced by subtraction"),
    (r"(?<![-:])-(?![->=])", "+", "subtraction replaced by addition"),
    (r"(?<![*/])\*(?![*/=])", "+", "multiplication replaced by addition"),
)


def _executable_declarations(text: str) -> tuple[Declaration, ...]:
    return tuple(
        declaration
        for declaration in declarations(text)
        if declaration.keyword in {"def", "opaque", "abbrev"}
        and declaration.assign is not None
        and not _SPEC_NAME_RE.search(declaration.name)
    )


def _bug_candidates(
    text: str, used_positions: set[int]
) -> Iterable[tuple[str, TransformStep]]:
    masked = mask_lean_noncode(text)
    for declaration in _executable_declarations(text):
        assert declaration.assign is not None
        body_start = declaration.assign + 2
        for pattern, replacement, description in _BUG_MUTATIONS:
            for match in re.compile(pattern).finditer(
                masked, body_start, declaration.end
            ):
                if match.start() in used_positions:
                    continue
                before = text[match.start() : match.end()]
                after = replacement
                candidate = text[: match.start()] + after + text[match.end() :]
                step = TransformStep(
                    kind="bug_mutation",
                    target=f"{declaration.name}: {description}",
                    before=before,
                    after=after,
                    start=match.start(),
                    end=match.end(),
                )
                yield candidate, step


def build_bug_ladder(
    text: str,
    *,
    levels: int = 4,
    validate: Callable[[str], bool] | None = None,
) -> tuple[ProbeArtifact, ...]:
    """Build a cumulative, byte-distinct, type-preserving mutation ladder."""

    if levels < 1:
        raise ValueError("levels must be positive")
    artifacts = [ProbeArtifact(0, text, sha256_text(text), None)]
    current = text
    used_positions: set[int] = set()
    for level in range(1, levels + 1):
        accepted: tuple[str, TransformStep] | None = None
        for candidate, step in _bug_candidates(current, used_positions):
            if sha256_text(candidate) in {artifact.sha256 for artifact in artifacts}:
                continue
            if validate is None or validate(candidate):
                accepted = candidate, step
                break
        if accepted is None:
            raise ValueError(
                f"could not construct compile-valid cumulative bug level {level}"
            )
        current, step = accepted
        used_positions.add(step.start)
        artifacts.append(ProbeArtifact(level, current, sha256_text(current), step))
    return tuple(artifacts)


def _is_spec_declaration(declaration: Declaration) -> bool:
    return declaration.keyword in {
        "theorem",
        "lemma",
        "example",
        "axiom",
        "#eval",
        "#check",
    } or bool(_SPEC_NAME_RE.search(declaration.name))


def _remove_span(text: str, start: int, end: int) -> str:
    replacement = "\n" * max(1, text[start:end].count("\n"))
    return text[:start] + replacement + text[end:]


def build_missing_spec_ladder(
    text: str,
    *,
    levels: int = 4,
    validate: Callable[[str], bool] | None = None,
) -> tuple[ProbeArtifact, ...]:
    """Remove specification/test declarations cumulatively in dependency order."""

    if levels < 1:
        raise ValueError("levels must be positive")
    artifacts = [ProbeArtifact(0, text, sha256_text(text), None)]
    current = text
    for level in range(1, levels + 1):
        accepted: tuple[str, TransformStep] | None = None
        candidates = [d for d in declarations(current) if _is_spec_declaration(d)]
        for declaration in reversed(candidates):
            candidate = _remove_span(current, declaration.start, declaration.end)
            if sha256_text(candidate) in {artifact.sha256 for artifact in artifacts}:
                continue
            if validate is None or validate(candidate):
                step = TransformStep(
                    kind="missing_spec_removal",
                    target=f"{declaration.keyword} {declaration.name}",
                    before=current[declaration.start : declaration.end],
                    after="",
                    start=declaration.start,
                    end=declaration.end,
                )
                accepted = candidate, step
                break
        if accepted is None:
            raise ValueError(
                f"could not construct compile-valid cumulative spec level {level}"
            )
        current, step = accepted
        artifacts.append(ProbeArtifact(level, current, sha256_text(current), step))
    return tuple(artifacts)


class LeanCompiler:
    """Elaborate transient Lean source with a pinned Lake project."""

    def __init__(
        self, project_root: Path, lake_bin: Path, *, timeout_seconds: int = 60
    ):
        self.project_root = Path(project_root).resolve()
        self.lake_bin = Path(lake_bin).resolve()
        self.timeout_seconds = timeout_seconds
        if not self.project_root.is_dir():
            raise ValueError(f"Lean project root does not exist: {self.project_root}")
        if not self.lake_bin.is_file():
            raise ValueError(f"Lake binary does not exist: {self.lake_bin}")

    def compile(self, code: str) -> CompileResult:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".lean",
            prefix="pti_probe_",
            encoding="utf-8",
            delete=False,
        ) as handle:
            handle.write(code)
            path = Path(handle.name)
        try:
            process = subprocess.run(
                [str(self.lake_bin), "env", "lean", str(path)],
                cwd=self.project_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=self.timeout_seconds,
                check=False,
            )
            return CompileResult(
                process.returncode == 0, process.returncode, process.stdout
            )
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            return CompileResult(
                False, 124, f"TIMEOUT after {self.timeout_seconds}s\n{output}"
            )
        finally:
            path.unlink(missing_ok=True)

    def validates(self, code: str) -> bool:
        return self.compile(code).ok

    def compile_module(self, module_name: str, source_path: Path) -> CompileResult:
        """Compile a local project module into Lake's build tree."""

        source = Path(source_path).resolve()
        try:
            source.relative_to(self.project_root)
        except ValueError as exc:
            raise ValueError("module source must be inside the Lean project") from exc
        if not source.is_file():
            raise ValueError(f"module source does not exist: {source}")
        module_parts = module_name.split(".")
        output_base = self.project_root / ".lake" / "build" / "lib" / "lean"
        output = output_base.joinpath(*module_parts).with_suffix(".olean")
        interface = output.with_suffix(".ilean")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            process = subprocess.run(
                [
                    str(self.lake_bin),
                    "env",
                    "lean",
                    "-o",
                    str(output),
                    "-i",
                    str(interface),
                    str(source),
                ],
                cwd=self.project_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=self.timeout_seconds,
                check=False,
            )
            return CompileResult(
                process.returncode == 0, process.returncode, process.stdout
            )
        except subprocess.TimeoutExpired as exc:
            captured = exc.stdout or ""
            if isinstance(captured, bytes):
                captured = captured.decode("utf-8", errors="replace")
            return CompileResult(
                False, 124, f"TIMEOUT after {self.timeout_seconds}s\n{captured}"
            )


def summarize_compile_error(output: str, *, max_chars: int = 500) -> str:
    errors = [
        _TEMP_PROBE_PREFIX_RE.sub("<pti_probe>.lean", line.strip())
        for line in output.splitlines()
        if "error:" in line
    ]
    summary = " | ".join(errors) if errors else output.strip().split("\n", 1)[0]
    return summary[:max_chars]


__all__ = [
    "AlphaTransform",
    "CompileResult",
    "Declaration",
    "LeanCompiler",
    "ProbeArtifact",
    "TransformStep",
    "alpha_rename_bound_identifier",
    "build_bug_ladder",
    "build_missing_spec_ladder",
    "classify_compile_error",
    "declarations",
    "mask_lean_noncode",
    "sha256_text",
    "summarize_compile_error",
]
