#!/usr/bin/env python3
"""TLDR: Lean guard for experiment 43 — split a Lean file into top-level commands, classify them as implementation,
specification, test or scaffold, build a Lean-valid attack start from a rated candidate with a fixed minimal repair
ladder, check that an attacker edit keeps every implementation command unchanged and elaborates (fail-closed, with
cert-judge's LeanCompiler on experiment 43's mirror project), and extract theorem statements. Zero model calls."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[3] / "py_src")]
import e43                                                    # noqa: E402
from cert_judge.probe_validation import (  # noqa: E402
    _SPEC_NAME_RE, CompileResult, LeanCompiler, classify_compile_error, mask_lean_noncode, summarize_compile_error,
)

# A top-level command starts at column zero with one of these tokens (cert-judge's boundary list plus `/--` doc
# comments, `import`, `mutual` and `#` commands); everything up to the next start belongs to it.
_START_RE = re.compile(
    r"(?m)^(?:@\[|private\b|protected\b|noncomputable\b|partial\b|unsafe\b|nonrec\b|"
    r"def\b|theorem\b|lemma\b|example\b|opaque\b|abbrev\b|axiom\b|instance\b|"
    r"inductive\b|structure\b|class\b|mutual\b|initialize\b|builtin_initialize\b|macro\b|macro_rules\b|syntax\b|"
    r"notation\b|infixl?\b|infixr\b|prefix\b|postfix\b|namespace\b|section\b|end\b|open\b|export\b|"
    r"set_option\b|attribute\b|variable\b|variables\b|universe\b|universes\b|include\b|omit\b|import\b|"
    r"deriving\b|#[a-z_]+\b)"
)
_HEAD_RE = re.compile(
    r"^(?P<attrs>(?:@\[[^\]\n]*\][ \t\n]*)*)(?P<mods>(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)[ \t]+)*)"
    r"(?P<keyword>def|theorem|lemma|example|opaque|abbrev|axiom|instance|inductive|structure|class|mutual|"
    r"namespace|section|end|open|export|set_option|attribute|variable|variables|universe|universes|import|"
    r"#[a-z_]+|[a-z_]+)\b(?P<rest>[^\n]*)"
)
_NAME_RE = re.compile(r"^[ \t]*(?P<name>[A-Za-z_][A-Za-z0-9_'.!?₀-₉]*)")
IMPLEMENTATION_KEYWORDS = {"def", "abbrev", "opaque", "instance", "inductive", "structure", "class", "axiom", "mutual"}
THEOREM_KEYWORDS = {"theorem", "lemma"}
TEST_COMMANDS = {"#eval", "#check", "#print", "#reduce", "#guard", "#guard_msgs", "#synth", "#assert", "#test"}
SPEC_NAMES = {"pre", "post", "precond", "postcond", "spec", "Pre", "Post"}
IMPORT_RE = re.compile(r"(?m)^import[ \t]+(\S+)[ \t]*$")
ERROR_RE = re.compile(r":(\d+):(\d+): error:")


@dataclass
class Command:
    start: int                 # byte offset of the command's own first line (after its doc comment)
    doc_start: int             # offset including a doc comment directly above it
    end: int
    keyword: str
    name: str
    kind: str = ""             # implementation | spec_def | theorem | test | scaffold | other
    text: str = ""


def strip_comments(text: str) -> str:
    """Remove Lean comments (line and nested block, including doc comments); keep strings, char literals and layout."""
    out: list[str] = []
    i, n, depth, in_str, esc = 0, len(text), 0, False, False
    while i < n:
        if depth:
            if text.startswith("/-", i):
                depth, i = depth + 1, i + 2
            elif text.startswith("-/", i):
                depth, i = depth - 1, i + 2
            else:
                if text[i] == "\n":
                    out.append("\n")
                i += 1
            continue
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if text.startswith("/-", i):
            depth, i = 1, i + 2
            continue
        if text.startswith("--", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "'" and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_'")):
            m = re.match(r"'(?:\\.|[^\\'\n])'", text[i:])
            if m:
                out.append(m.group(0))
                i += len(m.group(0))
                continue
        if ch == '"':
            in_str = True
        out.append(ch)
        i += 1
    return "".join(out)


def normalize_code(text: str) -> str:
    """Comment-free code with trailing whitespace and blank lines removed (indentation kept)."""
    lines = [line.rstrip() for line in strip_comments(text).split("\n")]
    return "\n".join(line for line in lines if line.strip())


def _doc_start(text: str, masked: str, pos: int) -> int:
    """Pull a command start back over comment blocks that sit directly above it (only whitespace in between)."""
    before = len(text[:pos].rstrip())
    if not text[:before].endswith("-/"):
        return pos
    best = pos
    open_pos = text.rfind("/-", 0, before - 2 + 1)
    while open_pos >= 0 and not masked[open_pos:before].strip():
        line_start = text.rfind("\n", 0, open_pos) + 1
        if not text[line_start:open_pos].strip():
            best = line_start
        open_pos = text.rfind("/-", 0, open_pos)
    return best


def commands(text: str) -> list[Command]:
    masked = mask_lean_noncode(text)
    starts = [m.start() for m in _START_RE.finditer(masked)]
    # attribute lines directly above a keyword line belong to it
    merged = []
    for s in starts:
        if merged and re.fullmatch(r"(?:@\[[^\]\n]*\][ \t]*\n)+", masked[merged[-1]:s]):
            continue
        merged.append(s)
    out = []
    for idx, s in enumerate(merged):
        e = merged[idx + 1] if idx + 1 < len(merged) else len(text)
        head = _HEAD_RE.match(masked[s:e])
        keyword = head.group("keyword") if head else "other"
        name = ""
        if head:
            nm = _NAME_RE.match(head.group("rest"))
            name = nm.group("name") if nm else ""
        cmd = Command(start=s, doc_start=s, end=e, keyword=keyword, name=name)
        out.append(cmd)
    # doc comments: a command's doc comment lies in the previous command's tail; move it
    for idx, cmd in enumerate(out):
        ds = _doc_start(text, masked, cmd.start)
        lower = out[idx - 1].start if idx else 0
        if ds < cmd.start and ds >= lower:
            cmd.doc_start = ds
            if idx:
                out[idx - 1].end = min(out[idx - 1].end, ds)
    for cmd in out:
        cmd.kind = classify(text, cmd)
        cmd.text = text[cmd.doc_start:cmd.end]
    return out


def _declared_type(text: str, cmd: Command) -> str:
    masked = mask_lean_noncode(text)
    body = masked[cmd.start:cmd.end]
    stop = body.find(":=")
    head = body if stop < 0 else body[:stop]
    head = head.split("\n|")[0]
    depth, colon = 0, -1
    for i, ch in enumerate(head):
        if ch in "([{⦃":
            depth += 1
        elif ch in ")]}⦄":
            depth -= 1
        elif ch == ":" and depth == 0 and not head.startswith(":=", i):
            colon = i
            break
    return " ".join(head[colon + 1:].split()) if colon >= 0 else ""


def classify(text: str, cmd: Command) -> str:
    kw = cmd.keyword
    if kw in THEOREM_KEYWORDS:
        return "theorem"
    if kw == "example" or kw in TEST_COMMANDS or kw.startswith("#"):
        return "test"
    if kw in IMPLEMENTATION_KEYWORDS:
        if kw in ("def", "abbrev", "opaque", "axiom"):
            short = cmd.name.split(".")[-1]
            dtype = _declared_type(text, cmd)
            if dtype.startswith("IO") or " IO " in f" {dtype} ":
                return "test"
            if short in SPEC_NAMES or _SPEC_NAME_RE.search(short) or re.search(r"(^|→\s*)Prop$", dtype):
                return "spec_def"
        return "implementation"
    if kw in ("namespace", "section", "end", "open", "export", "set_option", "attribute", "variable", "variables",
              "universe", "universes", "import"):
        return "scaffold"
    return "other"


def implementation(text: str) -> list[tuple[str, str, str]]:
    """Ordered (keyword, name, normalized code) of the implementation commands."""
    return [(c.keyword, c.name, normalize_code(text[c.start:c.end])) for c in commands(text) if c.kind == "implementation"]


def implementation_unchanged(start: str, edit: str) -> tuple[bool, str]:
    """Every implementation command of the start appears in the edit, byte-identical after comment and trailing-space
    normalization, exactly once under its name and in the same order; new commands may be added."""
    want = implementation(start)
    got = implementation(edit)
    got_by_name: dict[tuple[str, str], list[int]] = {}
    for i, (kw, name, _) in enumerate(got):
        got_by_name.setdefault((kw, name), []).append(i)
    last = -1
    for kw, name, code in want:
        idx = got_by_name.get((kw, name), [])
        if len(idx) != 1:
            return False, f"implementation command {kw} {name or '<anonymous>'} is {'missing' if not idx else 'duplicated'}"
        if got[idx[0]][2] != code:
            return False, f"implementation command {kw} {name or '<anonymous>'} was changed"
        if idx[0] < last:
            return False, f"implementation command {kw} {name} was reordered"
        last = idx[0]
    return True, ""


@dataclass
class Statement:
    name: str
    text: str                  # binders + type, whitespace-normalized, comments removed
    binders: str
    prop: str
    idents: set = field(default_factory=set)


def statements(text: str) -> list[Statement]:
    out = []
    masked = mask_lean_noncode(text)
    for c in commands(text):
        if c.kind != "theorem":
            continue
        body_masked = masked[c.start:c.end]
        stop = body_masked.find(":=")
        wher = re.search(r"\bwhere\b|\n\s*\|", body_masked)
        if stop < 0 or (wher and wher.start() < stop):
            stop = wher.start() if wher else len(body_masked)
        head = strip_comments(text[c.start:c.start + stop])
        head = re.sub(r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s+\S+", "", head.strip())
        norm = " ".join(head.split())
        depth, colon = 0, -1
        for i, ch in enumerate(norm):
            if ch in "([{⦃":
                depth += 1
            elif ch in ")]}⦄":
                depth -= 1
            elif ch == ":" and depth == 0 and not norm.startswith(":=", i):
                colon = i
                break
        binders, prop = (norm[:colon].strip(), norm[colon + 1:].strip()) if colon >= 0 else ("", norm)
        idents = set(re.findall(r"[A-Za-z_][A-Za-z0-9_'.!?]*", norm))
        out.append(Statement(name=c.name, text=norm, binders=binders, prop=prop, idents=idents))
    return out


# ---------------------------------------------------------------------------------------------------------
# Elaboration
# ---------------------------------------------------------------------------------------------------------
class Lean:
    def __init__(self, lake_dir: Path = e43.LAKE_DIR, lake_bin: Path = e43.LAKE_BIN, timeout: int = e43.LEAN_TIMEOUT_S):
        self.compiler = LeanCompiler(lake_dir, lake_bin, timeout_seconds=timeout)
        self.lake_dir = Path(lake_dir)

    def compile(self, code: str) -> CompileResult:
        return self.compiler.compile(code)

    def roots(self) -> list[Path]:
        toolchain = (self.lake_dir / "lean-toolchain").read_text().strip().replace("/", "--").replace(":", "---")
        roots = [Path.home() / ".elan/toolchains" / toolchain / "lib/lean", self.lake_dir / ".lake/build/lib/lean"]
        pkgs = self.lake_dir / ".lake/packages"
        if pkgs.is_dir():
            roots += [p / ".lake/build/lib/lean" for p in sorted(pkgs.iterdir())]
        return roots

    def module_available(self, module: str) -> bool:
        rel = module.replace(".", "/") + ".olean"
        return any((root / rel).is_file() for root in self.roots())


def first_error_line(output: str) -> int | None:
    lines = [int(m.group(1)) for m in ERROR_RE.finditer(output)]
    return min(lines) if lines else None


# ---------------------------------------------------------------------------------------------------------
# Repair ladder for attack starts (PROTOCOL.md section 3): the smallest stage whose output elaborates is the start.
# ---------------------------------------------------------------------------------------------------------
def s1_syntax(text: str) -> str:
    """Delete markdown fence lines; turn a doc comment that documents a `#` command into a plain comment."""
    text = "\n".join(line for line in text.split("\n") if not line.lstrip().startswith("```"))
    return re.sub(r"/--((?:(?!-/).)*?)-/(\s*\n)(?=#[a-z_]+)", lambda m: "/-" + m.group(1) + "-/" + m.group(2), text, flags=re.S)


def s2_imports(text: str, lean: Lean) -> str:
    """Delete imports of modules this toolchain does not provide; then make sure `import Mathlib` is present."""
    mods = IMPORT_RE.findall(text)
    bad = {m for m in mods if not lean.module_available(m)}
    if not bad:
        return text
    text = IMPORT_RE.sub(lambda m: "" if m.group(1) in bad else m.group(0), text)
    if "Mathlib" not in IMPORT_RE.findall(text):
        text = "import Mathlib\n" + text.lstrip("\n")
    return text


def s3_sorry(text: str) -> str:
    """Replace every theorem/lemma proof by `by sorry` (statements byte-identical)."""
    masked = mask_lean_noncode(text)
    cmds = [c for c in commands(text) if c.kind == "theorem"]
    code = text
    for c in sorted(cmds, key=lambda c: c.start, reverse=True):
        rel = masked[c.start:c.end].find(":=")
        if rel < 0:
            continue
        assign = c.start + rel
        tail_end = c.end
        # keep a doc comment that belongs to the next command (it was moved to that command already)
        code = code[:assign + 2] + " by sorry\n\n" + code[tail_end:]
    return code


def s4_prune(text: str, lean: Lean, max_steps: int = 60) -> tuple[str | None, list[str], str]:
    """Delete, one at a time, the non-implementation command holding the first Lean error (theorem, test, spec
    definition or `open`), until the file elaborates. Returns (code or None, deleted commands, last error)."""
    deleted: list[str] = []
    code = text
    for _ in range(max_steps):
        res = lean.compile(code)
        if res.ok:
            return code, deleted, ""
        line = first_error_line(res.output)
        if line is None:
            return None, deleted, summarize_compile_error(res.output)
        offset = sum(len(x) + 1 for x in code.split("\n")[:line - 1])
        holder = None
        for c in commands(code):
            if c.doc_start <= offset < max(c.end, c.doc_start + 1):
                holder = c
        if holder is None or not (holder.kind in ("theorem", "test", "spec_def") or holder.keyword == "open"):
            return None, deleted, f"error in {holder.kind + ' ' + holder.keyword + ' ' + holder.name if holder else 'no command'}: " \
                + summarize_compile_error(res.output, max_chars=300)
        deleted.append(f"{holder.keyword} {holder.name}".strip())
        code = code[:holder.doc_start] + code[holder.end:]
        code = re.sub(r"\n{3,}", "\n\n", code)
    return None, deleted, "prune step limit"


def build_start(original: str, lean: Lean) -> dict:
    """Apply the repair ladder; return the first stage that elaborates (or FAIL with the last error)."""
    stages = []
    code = original
    res = lean.compile(code)
    stages.append(("S0_original", res.ok))
    if res.ok:
        return {"stage": "S0_original", "code": code, "stages": stages, "pruned": []}
    for name, fn in (("S1_syntax", s1_syntax), ("S2_imports", lambda t: s2_imports(t, lean)), ("S3_proofs_sorry", s3_sorry)):
        new = fn(code)
        if new == code:
            stages.append((name, None))
            continue
        code = new
        res = lean.compile(code)
        stages.append((name, res.ok))
        if res.ok:
            return {"stage": name, "code": code, "stages": stages, "pruned": []}
    pruned_code, deleted, err = s4_prune(code, lean)
    stages.append(("S4_prune_failing_spec_and_tests", pruned_code is not None))
    if pruned_code is not None:
        return {"stage": "S4_prune_failing_spec_and_tests", "code": pruned_code, "stages": stages, "pruned": deleted}
    return {"stage": "FAIL", "code": None, "stages": stages, "pruned": deleted, "error": err,
            "error_class": classify_compile_error(lean.compile(code)) if not err.startswith("error in") else "implementation_error"}


# ---------------------------------------------------------------------------------------------------------
# Attacker output and the edit check
# ---------------------------------------------------------------------------------------------------------
FILE_BEGIN, FILE_END = "<lean_file>", "</lean_file>"


def extract_file(completion: str) -> str | None:
    """The Lean file the attacker returned: the last <lean_file>...</lean_file> block, else the last ```lean block."""
    if FILE_BEGIN in completion and FILE_END in completion:
        body = completion[completion.rindex(FILE_BEGIN) + len(FILE_BEGIN):]
        if FILE_END in body:
            body = body[:body.index(FILE_END)]
            body = body.strip("\n")
            fence = re.fullmatch(r"\s*```(?:lean4?|)\n(.*?)\n```\s*", body, flags=re.S)
            return (fence.group(1) if fence else body).rstrip() + "\n"
    blocks = re.findall(r"```(?:lean4?)\n(.*?)\n```", completion, flags=re.S)
    if blocks:
        return blocks[-1].rstrip() + "\n"
    return None


def relax_failing_proofs(code: str, output: str) -> tuple[str | None, list[str]]:
    """PROTOCOL.md Amendment 1: when every Lean error lies inside the proof of a theorem, lemma or example (after its
    `:=`), replace exactly those proofs by `by sorry` (statements byte-identical). Returns (relaxed code, names) or
    (None, []) when some error lies outside a proof."""
    lines = code.split("\n")
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)
    offsets = []
    for m in re.finditer(r":(\d+):(\d+): error:", output):
        ln, col = int(m.group(1)), int(m.group(2))
        if 1 <= ln <= len(lines):
            offsets.append(starts[ln - 1] + col)
    if not offsets:
        return None, []
    masked = mask_lean_noncode(code)
    targets: dict[int, Command] = {}
    for off in offsets:
        holder = None
        for c in commands(code):
            if c.start <= off < c.end:
                holder = c
        if holder is None or not (holder.kind == "theorem" or holder.keyword == "example"):
            return None, []
        rel = masked[holder.start:holder.end].find(":=")
        if rel < 0 or off < holder.start + rel:
            return None, []
        targets[holder.start] = holder
    out = code
    for s in sorted(targets, reverse=True):
        c = targets[s]
        assign = c.start + masked[c.start:c.end].find(":=")
        out = out[:assign + 2] + " by sorry\n\n" + out[c.end:]
    return out, [f"{c.keyword} {c.name}".strip() for c in targets.values()]


def check_edit(start: str, edit: str | None, lean: Lean | None, relax: bool = True) -> dict:
    """Fail-closed validity of one proposal: a file was returned, it differs from the start, implementation
    unchanged, and it elaborates (sorry allowed). With `relax` (Amendment 1), failing proofs are replaced by
    `by sorry` once and the file is re-elaborated; the relaxed file is then the proposal."""
    if edit is None or not edit.strip():
        return {"valid": False, "reason": "no_file", "detail": "no <lean_file> block in the completion"}
    if edit.strip() == start.strip():
        return {"valid": False, "reason": "no_change", "detail": "the returned file equals the current candidate"}
    ok, why = implementation_unchanged(start, edit)
    if not ok:
        return {"valid": False, "reason": "implementation_changed", "detail": why}
    if lean is None:
        return {"valid": True, "reason": "", "detail": "unvalidated (no Lean)"}
    res = lean.compile(edit)
    if not res.ok:
        failed = {"valid": False, "reason": "lean_error", "detail": summarize_compile_error(res.output, max_chars=600),
                  "error_class": classify_compile_error(res)}
        if not relax:
            return failed
        relaxed, names = relax_failing_proofs(edit, res.output)
        if relaxed is None:
            return failed
        if not implementation_unchanged(start, relaxed)[0]:
            return failed
        res2 = lean.compile(relaxed)
        if not res2.ok:
            failed["relax_attempted"] = names
            return failed
        return {"valid": True, "reason": "", "detail": "", "relaxed": True, "relaxed_proofs": names,
                "relaxed_code": relaxed, "original_error": failed["detail"]}
    return {"valid": True, "reason": "", "detail": ""}
