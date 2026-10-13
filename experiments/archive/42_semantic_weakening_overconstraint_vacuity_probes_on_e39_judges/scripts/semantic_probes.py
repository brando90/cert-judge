#!/usr/bin/env python3
"""TLDR: Experiment 42's probe constructors and fail-closed Lean checks. From one annotation-era reference it builds
vacuity (`True` statements; kept premises with a `True` conclusion), cumulative weakening (edits proposed per task in
`probe_edits/<task>.json`), over-constraint (an unsatisfiable hypothesis) and formatting-only probes, and validates
each: the probe must elaborate; for semantic probes a generated check file must prove, with no `sorryAx`, that every
changed reference statement implies its probe counterpart (the implementation functions named in the statement are
replaced by axioms of the same signature so a proof cannot compute through them), must prove any added
hypothesis unsatisfiable, and records whether the reverse implication is proved (proved-equivalent probes are
excluded); formatting probes must print exactly the same declarations. Zero model calls."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[4] / "py_src")]
import lean_text as L                                         # noqa: E402
from cert_judge.probe_validation import LeanCompiler, mask_lean_noncode, sha256_text  # noqa: E402

CHECK_PREFIX = "e42chk"
_POS_RE = re.compile(r"^(?P<path>[^\n:]*?\.lean):(?P<line>\d+):(?P<col>\d+): (?P<sev>error|warning|info)", re.M)
_AXIOMS_RE = re.compile(r"'(?P<name>[^']+)' depends on axioms: \[(?P<axioms>[^\]]*)\]", re.S)
_NO_AXIOMS_RE = re.compile(r"'(?P<name>[^']+)' does not depend on any axioms")
_SORRY_PROOF = {"sorry", "by sorry"}


@dataclass
class Check:
    ident: str                  # Lean name of the generated check theorem
    kind: str                   # forward | reverse | unsat
    theorem: str                # reference theorem it concerns
    after: str                  # probe declaration it is inserted after
    params: str                 # abstraction parameters `(e42fn_f : ...)`
    prop: str                   # the proposition checked
    proof: str                  # tactic block (without `by`)
    required: bool              # forward / unsat checks must pass; reverse checks are recorded only


@dataclass
class Probe:
    kind: str
    level: int
    code: str | None
    note: str
    valid: bool | None = None
    reason: str = ""
    checks: list[dict] = field(default_factory=list)
    reverse: str | None = None  # proved | unproved | not_applicable
    extra: dict = field(default_factory=dict)

    @property
    def sha256(self) -> str | None:
        return sha256_text(self.code) if self.code is not None else None


# ------------------------------------------------------------------------------------------------------------------
# Text helpers
# ------------------------------------------------------------------------------------------------------------------

def _proof_bounds(text: str, d: L.Decl) -> tuple[int, int] | None:
    """(start, end) of the proof: after `:=`, or the pattern-matching arms when the head has no `:=`."""
    if d.assign is not None:
        return d.assign + 2, L.trim_end(text, d.end)
    if d.header_end is not None:
        return d.header_end, L.trim_end(text, d.end)
    return None


def _proof_is_sorry(text: str, d: L.Decl) -> bool:
    bounds = _proof_bounds(text, d)
    return bounds is not None and " ".join(text[bounds[0]:bounds[1]].split()) in _SORRY_PROOF


def forall_text(binders: list[str], type_str: str) -> str:
    body = f"({type_str.strip()})"
    return f"(∀ {' '.join(b.strip() for b in binders)}, {body})" if binders else body


def _indent(block: str, spaces: int = 2) -> str:
    lines = block.strip("\n").splitlines()
    base = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    return "\n".join((" " * spaces + l[base:]) if l.strip() else "" for l in lines)


def uses_mathlib(text: str) -> bool:
    return any(m == "Mathlib" or m.startswith("Mathlib.") for m in L.imports(text))


def auto_tactic(text: str, unfold: list[str], intro: str = "intro H; intros") -> str:
    simp_set = f" [{', '.join(unfold)}]" if unfold else ""
    alts = [f"({intro}; trivial)", f"({intro}; simp_all{simp_set})", f"({intro}; omega)",
            f"({intro}; apply H <;> assumption)", f"({intro}; left; apply H <;> assumption)",
            f"({intro}; right; apply H <;> assumption)", f"({intro}; exact H ‹_›)"]
    if unfold:
        alts.append(f"({intro}; simp only{simp_set} at *; omega)")
    if uses_mathlib(text):
        alts += [f"({intro}; tauto)", f"({intro}; aesop)"]
    return "first\n  | " + "\n  | ".join(alts)


# ------------------------------------------------------------------------------------------------------------------
# Implementation abstraction: the check file sees every data-valued definition as an axiom
# ------------------------------------------------------------------------------------------------------------------

def _def_is_prop(text: str, d: L.Decl) -> bool:
    ty = L.type_text(text, d)
    return ty is not None and (ty == "Prop" or ty.endswith("→ Prop") or ty.endswith("-> Prop"))


def _axiomatizable(text: str, d: L.Decl) -> bool:
    ty = L.type_text(text, d)
    return (not d.is_theorem and d.binders_ok and ty is not None and not _def_is_prop(text, d)
            and not re.match(r"^(Type|Sort)\b", ty))


_COMMAND_RE = re.compile(r"(?m)^(example\b|#eval\b|#guard\b|#check\b|#reduce\b|#print\b|#guard_msgs\b)")


def _where_helpers(text: str, masked: str, d: L.Decl, end: int) -> list[tuple[str, str]] | None:
    """Helpers declared in the definition's `where` clause as (name, head); [] if none; None if one cannot be read."""
    body_start = d.header_end if d.header_end is not None else d.name_end
    m = re.search(r"(?m)^[ \t]*where[ \t]*$", masked[body_start:end])
    if not m:
        return []
    start = body_start + m.end()
    first = re.search(r"(?m)^([ \t]+)[A-Za-z_]", masked[start:end])
    if not first:
        return None
    indent = first.group(1)
    heads = list(re.finditer(rf"(?m)^{indent}(?P<name>[A-Za-z_][A-Za-z0-9_'?!]*)", masked[start:end]))
    out = []
    for i, h in enumerate(heads):
        h_end = start + (heads[i + 1].start() if i + 1 < len(heads) else end - start)
        header_end, _, colon, binders, ok = L._scan_header(masked, start + h.end("name"), h_end)
        if header_end is None or colon is None or not ok:
            return None
        out.append((h.group("name"), " ".join(text[start + h.end("name"):header_end].split())))
    return out


_DOC_ORPHAN_NEXT = re.compile(r"(?:[ \t]*(?:--[^\n]*)?\n)*[ \t]*(?:@\[|private\b|protected\b|noncomputable\b|partial\b|unsafe\b|"
                              r"def\b|theorem\b|lemma\b|abbrev\b|axiom\b|opaque\b|structure\b|inductive\b|class\b|"
                              r"instance\b|example\b|macro\b|syntax\b|notation\b)")


def drop_orphan_docstrings(text: str) -> str:
    """Remove `/-- ... -/` doc comments that no longer precede a declaration (their test was dropped)."""
    edits = []
    for a, b, kind in L.comment_spans(text):
        if kind == "doc" and not _DOC_ORPHAN_NEXT.match(text, b):
            edits.append((a, b, ""))
    return _replace_spans(text, edits)


def check_base(text: str) -> tuple[str, list[str], list[str]]:
    """The probe as the check file sees it: every data-valued definition with a written type becomes an `axiom` with
    the same signature (so no proof can compute through the implementation: implications hold for ANY
    implementation), every theorem proof becomes `sorry`, and unit tests (`example`, `#eval`, `#guard`, ...) are
    dropped. Prop-valued definitions (the specification predicates) keep their bodies. Returns (text, axiomatized
    names, data-valued definitions left concrete because their type is not written)."""
    masked = mask_lean_noncode(text)
    boundaries = [m.start() for m in L._TOP_LEVEL_BOUNDARY_RE.finditer(masked)]
    edits, axiomatized, concrete = [], [], []
    for d in L.decls(text, masked):
        end = L.trim_end(text, d.end)
        if d.is_theorem:
            bounds = _proof_bounds(text, d)
            if bounds is not None:
                edits.append((bounds[0], bounds[1], (" sorry" if d.assign is not None else " := sorry")))
            if "@[" in text[d.start:d.kw_start]:     # a sorry-proved @[simp] lemma must not feed automation
                edits.append(_strip_attrs(text, d))
        elif _axiomatizable(text, d):
            helpers = _where_helpers(text, masked, d, end)
            if helpers is None:
                concrete.append(d.name)
                continue
            modifiers = " ".join(m for m in re.sub(r"@\[[^\]\n]*\]", " ", text[d.start:d.kw_start]).split()
                                 if m in ("private", "protected"))
            head = text[d.name_end:d.header_end].rstrip()
            lines = [(modifiers + " " if modifiers else "") + f"axiom {d.name}{head}"]
            lines += [f"axiom {d.name}.{name}{hhead}" for name, hhead in helpers]
            edits.append((d.start, end, "\n".join(lines)))
            axiomatized.extend([d.name] + [f"{d.name}.{name}" for name, _ in helpers])
        elif not d.is_theorem and not _def_is_prop(text, d) and L.type_text(text, d) is None:
            concrete.append(d.name)
    for m in _COMMAND_RE.finditer(masked):
        end = next((b for b in boundaries if b > m.start()), len(text))
        edits.append((L.extend_start(text, m.start()), L.trim_end(text, end), ""))
    return drop_orphan_docstrings(_replace_spans(text, edits)), axiomatized, concrete


# ------------------------------------------------------------------------------------------------------------------
# Check files
# ------------------------------------------------------------------------------------------------------------------

def _check_block(chk: Check) -> str:
    return (f"\n\n-- {CHECK_PREFIX}-begin {chk.ident}\n"
            f"theorem {chk.ident} {chk.params} :\n    {chk.prop} := by\n{_indent(chk.proof)}\n"
            f"-- {CHECK_PREFIX}-end {chk.ident}\n#print axioms {chk.ident}\n")


def assemble(probe_text: str, checks: list[Check], copies: dict[str, str]) -> str:
    """Insert original-definition copies after their definitions and check theorems after their anchor declarations
    (so every block elaborates in the anchor's namespace, section and local-instance context)."""
    inserts: dict[int, list[str]] = {}
    ds = L.decls(probe_text)
    for name, block in copies.items():
        d = L.find(ds, name)
        if d is None:
            raise ValueError(f"definition {name} not found in the probe")
        inserts.setdefault(L.trim_end(probe_text, d.end), []).append("\n\n" + block.strip("\n") + "\n")
    for chk in checks:
        d = L.find(ds, chk.after)
        if d is None:
            raise ValueError(f"anchor {chk.after} not found in the probe")
        inserts.setdefault(L.trim_end(probe_text, d.end), []).append(_check_block(chk))
    out, prev = [], 0
    for pos in sorted(inserts):
        out.append(probe_text[prev:pos])
        out.extend(inserts[pos])
        prev = pos
    out.append(probe_text[prev:])
    return "".join(out)


def parse_output(check_text: str, output: str, checks: list[Check]) -> dict[str, dict]:
    """Per check: status proved / failed (an error inside its block, or `sorryAx`, or no axiom line)."""
    lines = check_text.splitlines()
    ranges = {}
    for idx, line in enumerate(lines, start=1):
        m = re.match(rf"-- {CHECK_PREFIX}-(begin|end) (\S+)", line)
        if m:
            ranges.setdefault(m.group(2), [0, 0])[0 if m.group(1) == "begin" else 1] = idx
    errors = [(int(m.group("line")), output[m.start():output.find("\n", m.start())][:300])
              for m in _POS_RE.finditer(output) if m.group("sev") == "error"]
    axioms = {m.group("name").split(".")[-1]: [a.strip() for a in m.group("axioms").split(",") if a.strip()]
              for m in _AXIOMS_RE.finditer(output)}
    axioms.update({m.group("name").split(".")[-1]: [] for m in _NO_AXIOMS_RE.finditer(output)})
    result = {}
    for chk in checks:
        lo, hi = ranges.get(chk.ident, [0, 0])
        errs = [e for line, e in errors if lo <= line <= hi + 1]
        ax = axioms.get(chk.ident)
        ok = not errs and ax is not None and "sorryAx" not in ax
        result[chk.ident] = {"status": "proved" if ok else "failed", "axioms": ax, "errors": errs[:3]}
    in_blocks = set()
    for lo, hi in ranges.values():
        in_blocks.update(range(lo, hi + 2))
    result["__outside_errors__"] = [e for line, e in errors if line not in in_blocks][:5]
    return result


# ------------------------------------------------------------------------------------------------------------------
# Constructors
# ------------------------------------------------------------------------------------------------------------------

def _replace_spans(text: str, edits: list[tuple[int, int, str]]) -> str:
    for a, b, new in sorted(edits, key=lambda e: e[0], reverse=True):
        text = text[:a] + new + text[b:]
    return text


def _strip_attrs(text: str, d: L.Decl) -> tuple[int, int, str]:
    prefix = text[d.start:d.kw_start]
    return d.start, d.kw_start, re.sub(r"@\[[^\]\n]*\][ \t]*", "", prefix)


def vac_true(text: str) -> str | None:
    edits = []
    support = L.support_theorems(text)
    for d in L.theorems(text):
        if d.name in support:
            continue
        bounds = _proof_bounds(text, d)
        if bounds is None:
            return None
        proof = text[bounds[0]:bounds[1]] if _proof_is_sorry(text, d) and d.assign is not None else " trivial"
        edits.append((d.name_end, bounds[1], " : True :=" + (proof if proof.startswith(" ") else " " + proof)))
        edits.append(_strip_attrs(text, d))
    return _replace_spans(text, edits) if edits else None


def vac_hyp(text: str) -> str | None:
    edits, kept_any = [], False
    support = L.support_theorems(text)
    for d in L.theorems(text):
        if d.name in support:
            continue
        bounds = _proof_bounds(text, d)
        ty = L.type_text(text, d)
        if bounds is None or ty is None or not d.binders_ok:
            return None
        premises, _ = L.split_premises(ty)
        kept_any = kept_any or bool(d.binders) or bool(premises)
        new_type = " → ".join(premises + ["True"])
        head = text[d.name_end:d.colon]
        proof = text[bounds[0]:bounds[1]] if _proof_is_sorry(text, d) and d.assign is not None else " by intros; trivial"
        edits.append((d.name_end, bounds[1], head.rstrip() + " :\n    " + new_type + " :=" + (proof if proof.startswith(" ") else " " + proof)))
        edits.append(_strip_attrs(text, d))
    return _replace_spans(text, edits) if edits and kept_any else None


_NAT = re.compile(r"^(Nat|ℕ)$")
_LEN = re.compile(r"^(List|Array|String)\b")


def _unsat_hyp(text: str, d: L.Decl) -> tuple[str, str] | None:
    """An unsatisfiable hypothesis over one explicit binder variable: Nat `v < 0`, List/String `v.length < 0`,
    Array `v.size < 0`, Int `v < v`. Prefers Nat variables (the README's example), then sized containers, then Int."""
    choices = []
    for b in L.binder_texts(text, d):
        if not b.startswith("(") or ":" not in b or ":=" in b:
            continue
        names, ty = b[1:-1].split(":", 1)
        ty = ty.strip()
        for v in names.split():
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", v):
                continue
            if _NAT.match(ty):
                choices.append((0, v, f"{v} < 0"))
            elif _LEN.match(ty):
                choices.append((1, v, f"{v}.{'size' if ty.startswith('Array') else 'length'} < 0"))
            elif ty in ("Int", "ℤ"):
                choices.append((2, v, f"{v} < {v}"))
    if not choices:
        return None
    _, v, hyp = sorted(choices, key=lambda c: c[0])[0]
    return v, hyp


def _fresh(text: str, base: str) -> str:
    name, k = base, 1
    while L.mentions(text, name):
        k += 1
        name = f"{base}{k}"
    return name


_MAIN_NAME = re.compile(r"correct|spec|post|main|satisf", re.I)


def overc_targets(text: str) -> list[L.Decl]:
    """Theorems with an eligible binder that no other declaration uses by name (an added hypothesis would change the
    arity seen by a proof that applies the theorem)."""
    ds = L.decls(text)
    masked = mask_lean_noncode(text)
    def used_elsewhere(d: L.Decl) -> bool:
        return any(o.start != d.start and L.mentions(masked[o.start:o.end], d.name) for o in ds)
    return [d for d in L.theorems(text) if d.binders_ok and d.colon is not None and d.binders and _unsat_hyp(text, d)
            and not used_elsewhere(d)]


def main_theorem(text: str) -> L.Decl | None:
    eligible = overc_targets(text)
    if not eligible:
        return None
    named = [d for d in eligible if _MAIN_NAME.search(d.name)]
    return named[-1] if named else eligible[-1]


def overc(text: str, level: int, exclude: frozenset[str] = frozenset()) -> tuple[str, list[dict]] | None:
    """L1: the main theorem gets one unsatisfiable hypothesis; L2: every eligible theorem not in `exclude` does
    (skipped when that equals L1). `exclude` holds theorems whose own proof stops elaborating with the hypothesis."""
    eligible = [d for d in overc_targets(text) if d.name not in exclude]
    main = main_theorem(text)
    if main is None:
        return None
    targets = [main] if level == 1 else eligible
    if level == 2 and (len(eligible) < 2 or main.name in exclude):
        return None
    hname = _fresh(text, "hrange")
    edits, added = [], []
    for d in targets:
        var, hyp = _unsat_hyp(text, d)
        last = d.binders[-1][1]
        edits.append((last, last, f" ({hname} : {hyp})"))
        added.append({"theorem": d.name, "variable": var, "hypothesis": f"({hname} : {hyp})"})
    return _replace_spans(text, edits), added


def theorems_with_errors(code: str, output: str) -> set[str]:
    """Names of the theorems whose span contains an error line of `output` (a compile of `code`)."""
    starts = [0] + [i + 1 for i, ch in enumerate(code) if ch == "\n"]
    lines = {int(m.group("line")) for m in _POS_RE.finditer(output) if m.group("sev") == "error"}
    out = set()
    for d in L.theorems(code):
        lo = sum(1 for s in starts if s <= d.start)
        hi = sum(1 for s in starts if s <= d.end)
        if any(lo <= ln <= hi for ln in lines):
            out.add(d.name)
    return out


def fmt_comments(text: str) -> str | None:
    spans = [(a, b) for a, b, kind in L.comment_spans(text) if kind in ("line", "block", "moddoc")]
    if not spans:
        return None
    out = text
    for a, b in sorted(spans, reverse=True):
        line_start = out.rfind("\n", 0, a) + 1
        line_end = out.find("\n", b)
        line_end = len(out) if line_end < 0 else line_end
        if out[line_start:a].strip() == "" and out[b:line_end].strip() == "":
            out = out[:line_start] + out[line_end + 1:]
        else:
            out = out[:a] + out[b:]
    out = "\n".join(l.rstrip() for l in out.splitlines())
    out = re.sub(r"\n{3,}", "\n\n", out).strip("\n") + "\n"
    return out if out != text else None


def fmt_layout(text: str) -> str | None:
    edits = []
    comments = L.comment_spans(text)
    for d in L.theorems(text):
        if d.assign is None:
            continue
        head = text[d.kw_start:d.assign]
        if ("\n" not in head.strip() or '"' in head or any(d.kw_start <= a < d.assign for a, _, _ in comments)
                or re.search(r"(?<![A-Za-z0-9_'.])(let|have|match|do|by|fun)(?![A-Za-z0-9_'])", head)):
            continue
        edits.append((d.kw_start, d.assign, " ".join(head.split()) + " "))
    return _replace_spans(text, edits) if edits else None


# ------------------------------------------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------------------------------------------

class Validator:
    def __init__(self, lake_dir: Path, lake_bin: Path, timeout: int = 900):
        self.compiler = LeanCompiler(lake_dir, lake_bin, timeout_seconds=timeout)

    def compile(self, code: str):
        return self.compiler.compile(code)


def closure_of(text: str, edited_defs: set[str]) -> set[str]:
    """Edited definitions plus every definition whose body mentions one of them (transitively)."""
    masked = mask_lean_noncode(text)
    ds = [d for d in L.decls(text, masked) if not d.is_theorem]
    closure = set(edited_defs)
    changed = True
    while changed:
        changed = False
        for d in ds:
            if d.name not in closure and any(L.mentions(masked[d.name_end:d.end], n) for n in closure):
                closure.add(d.name)
                changed = True
    return closure


def _explicit_args(binder: str) -> list[str]:
    if not binder.startswith("(") or ":" not in binder:
        return []
    return [n for n in binder[1:-1].split(":", 1)[0].split() if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'?!]*", n)]


def build_checks(ref: str, probe: str, *, tag: str, proofs: dict[str, str] | None = None,
                 closure: set[str] = frozenset(), unsat: list[dict] | None = None,
                 edited_defs: set[str] = frozenset()) -> tuple[list[Check], dict[str, str], list[str]]:
    """Forward (reference => probe) and reverse checks for every theorem whose statement changed or that mentions
    an edited definition, plus unsatisfiability checks for added hypotheses. The statements are taken from the real
    files; they are checked inside `check_base(probe)`, where the implementation is axiomatized."""
    proofs = proofs or {}
    ref_th = {d.name: d for d in L.theorems(ref)}
    probe_th = {d.name: d for d in L.theorems(probe)}
    renames = {n: f"{n}_e42o" for n in closure}
    unfold = sorted(set(closure) | set(renames.values()))
    checks, notes = [], []
    for name, rd in ref_th.items():
        pd = probe_th.get(name)
        if pd is None:
            notes.append(f"{name}: missing from the probe")
            continue
        r_head, p_head = L.head_text(ref, rd), L.head_text(probe, pd)
        if r_head == p_head and not any(L.mentions(r_head, n) for n in closure):
            continue
        r_ty, p_ty = L.type_text(ref, rd), L.type_text(probe, pd)
        idx = len(checks)
        if r_ty is None or p_ty is None or not rd.binders_ok or not pd.binders_ok:
            notes.append(f"{name}: head not parseable")
            checks.append(Check(f"{CHECK_PREFIX}_{tag}_fwd_{idx}", "forward", name, name, "", "False", "exact absurd", True))
            continue
        r_prop = L.rename(forall_text(L.binder_texts(ref, rd), r_ty), renames)
        p_prop = forall_text(L.binder_texts(probe, pd), p_ty)
        checks.append(Check(f"{CHECK_PREFIX}_{tag}_fwd_{idx}", "forward", name, name, "", f"{r_prop} →\n    {p_prop}",
                            proofs.get(name) or auto_tactic(ref, unfold), True))
        checks.append(Check(f"{CHECK_PREFIX}_{tag}_rev_{idx}", "reverse", name, name, "", f"{p_prop} →\n    {r_prop}",
                            auto_tactic(ref, unfold), False))
    # Definition-level checks: every edited Prop-valued definition D must satisfy ∀ binders, D_orig args → D args
    # (the weakening is checked even when no theorem mentions D).
    probe_ds = {d.name: d for d in L.decls(probe) if not d.is_theorem}
    for name in sorted(edited_defs):
        pd = probe_ds.get(name)
        if pd is None or not pd.binders_ok:
            notes.append(f"{name}: definition head not parseable")
            checks.append(Check(f"{CHECK_PREFIX}_{tag}_dfwd_{len(checks)}", "forward", name, name, "", "False", "exact absurd", True))
            continue
        binders = L.binder_texts(probe, pd)
        args = " ".join(a for b in binders for a in _explicit_args(b))
        before = sorted(n for n in closure if n in probe_ds and probe_ds[n].start <= pd.start)
        local_unfold = before + [renames[n] for n in before]
        app_new, app_old = f"{name} {args}".strip(), f"{renames[name]} {args}".strip()
        idx = len(checks)
        checks.append(Check(f"{CHECK_PREFIX}_{tag}_dfwd_{idx}", "forward", name, name, "",
                            forall_text(binders, f"{app_old} → {app_new}"),
                            proofs.get(name) or auto_tactic(ref, local_unfold, intro="intros; rename_i H"), True))
        checks.append(Check(f"{CHECK_PREFIX}_{tag}_drev_{idx}", "reverse", name, name, "",
                            forall_text(binders, f"{app_new} → {app_old}"), auto_tactic(ref, local_unfold, intro="intros; rename_i H"), False))
    for u in unsat or []:
        rd = ref_th.get(u["theorem"])
        binders = L.binder_texts(ref, rd) if rd else []
        hyp = u["hypothesis"][1:-1].split(":", 1)[1].strip()
        checks.append(Check(f"{CHECK_PREFIX}_{tag}_unsat_{len(checks)}", "unsat", u["theorem"], u["theorem"], "",
                            forall_text(binders, f"¬ ({hyp})"),
                            "intros\nfirst\n  | omega\n  | simp_all\n  | exact absurd ‹_› (Nat.lt_irrefl _)", True))
    copies = {}
    if closure:
        ref_ds = L.decls(ref)
        for n in closure:
            d = L.find(ref_ds, n)
            if d is None:
                raise ValueError(f"edited definition {n} not found in the reference")
            copies[n] = L.rename(ref[d.kw_start:L.trim_end(ref, d.end)], renames)
    return checks, copies, notes


def run_checks(validator: Validator, probe: str, checks: list[Check], copies: dict[str, str]) -> tuple[dict, str, str, list[str]]:
    base, axiomatized, _ = check_base(probe)
    check_text = assemble(base, checks, copies)
    result = validator.compile(check_text)
    return parse_output(check_text, result.output, checks), check_text, result.output, axiomatized


def judge_semantic(p: Probe, validator: Validator, ref: str, **kw) -> Probe:
    """Fail-closed validity for a vacuity / weakening / over-constraint probe."""
    if p.code is None:
        p.valid, p.reason = False, p.reason or "not constructible"
        return p
    compiled = validator.compile(p.code)
    if not compiled.ok:
        p.valid, p.reason = False, "probe does not elaborate: " + _first_error(compiled.output)
        return p
    checks, copies, notes = build_checks(ref, p.code, tag=f"{p.kind}{p.level}", **kw)
    if not any(c.kind == "forward" for c in checks):
        p.valid, p.reason = False, "no reference statement changed" + (f" ({'; '.join(notes)})" if notes else "")
        return p
    try:
        parsed, check_text, output, axiomatized = run_checks(validator, p.code, checks, copies)
    except ValueError as exc:
        p.valid, p.reason = False, f"check scaffolding: {exc}"
        return p
    p.extra["check_sha256"] = sha256_text(check_text)
    p.extra["axiomatized"] = axiomatized
    p.extra["concrete_untyped_defs"] = check_base(p.code)[2]
    p.extra["_check_text"], p.extra["_check_output"] = check_text, output
    for c in checks:
        r = parsed[c.ident]
        p.checks.append({"ident": c.ident, "kind": c.kind, "theorem": c.theorem, "status": r["status"], "axioms": r["axioms"], "errors": r["errors"] if r["status"] != "proved" else []})
    outside = parsed["__outside_errors__"]
    failed = [c for c in p.checks if c["kind"] in ("forward", "unsat") and c["status"] != "proved"]
    rev = [c for c in p.checks if c["kind"] == "reverse"]
    p.reverse = "proved" if rev and all(c["status"] == "proved" for c in rev) else "unproved"
    if outside:
        p.valid, p.reason = False, "check file errors outside the check blocks: " + outside[0]
    elif failed:
        p.valid, p.reason = False, f"{failed[0]['kind']} check failed for {failed[0]['theorem']}: " + (failed[0]["errors"][0] if failed[0]["errors"] else f"axioms {failed[0]['axioms']}")
    elif p.reverse == "proved":
        p.valid, p.reason = False, "proved equivalent to the reference (every reverse implication proved)"
    else:
        p.valid, p.reason = True, ""
    return p


def print_block(ref: str) -> str:
    names = [n for _, n in L.named_decls(ref)]
    return "\n\n" + "\n".join(f"#print {n}" for n in names) + "\n"


def normalized_messages(output: str) -> list[str]:
    return [re.sub(r"^[^\n:]*?\.lean:\d+:\d+: ", "", line) for line in output.splitlines()]


def judge_formatting(p: Probe, validator: Validator, ref: str, ref_messages: list[str] | None) -> Probe:
    if p.code is None:
        p.valid, p.reason = False, "no formatting change applies"
        return p
    compiled = validator.compile(p.code)
    if not compiled.ok:
        p.valid, p.reason = False, "probe does not elaborate: " + _first_error(compiled.output)
        return p
    ours = validator.compile(p.code + print_block(ref))
    same = ref_messages is not None and normalized_messages(ours.output) == ref_messages
    p.checks.append({"kind": "same_declarations", "status": "proved" if same else "failed",
                     "n_messages": len(normalized_messages(ours.output))})
    p.reverse = "not_applicable"
    p.valid, p.reason = (True, "") if same else (False, "elaborated declarations differ from the reference (#print comparison)")
    return p


def _first_error(output: str) -> str:
    for line in output.splitlines():
        if "error:" in line:
            return re.sub(r"^[^\n:]*?\.lean:", "<probe>.lean:", line.strip())[:300]
    return output.strip().split("\n", 1)[0][:300] if output.strip() else "non-zero exit"


# ------------------------------------------------------------------------------------------------------------------
# Weakening edits (proposed per task, validated here)
# ------------------------------------------------------------------------------------------------------------------

def apply_edits(ref: str, edits: list[dict]) -> tuple[str | None, str, set[str], set[str]]:
    """Apply `{decl, old, new}` edits in order, each `old` exactly once inside the named declaration. Only theorem
    statements/proofs and Prop-valued definitions may be edited. Returns (text, error, edited defs, edited theorems)."""
    text, edited_defs, edited_th = ref, set(), set()
    for e in edits:
        ds = L.decls(text)
        d = L.find(ds, e["decl"])
        if d is None:
            return None, f"declaration {e['decl']} not found (or not unique)", edited_defs, edited_th
        if not d.is_theorem and not _def_is_prop(ref, L.find(L.decls(ref), e["decl"]) or d):
            return None, f"{e['decl']} is not a theorem or a Prop-valued definition", edited_defs, edited_th
        span_end = L.trim_end(text, d.end)
        segment = text[d.kw_start:span_end]
        if segment.count(e["old"]) != 1:
            return None, f"edit target occurs {segment.count(e['old'])} times in {e['decl']}", edited_defs, edited_th
        text = text[:d.kw_start] + segment.replace(e["old"], e["new"], 1) + text[span_end:]
        (edited_th if d.is_theorem else edited_defs).add(e["decl"])
    return text, "", edited_defs, edited_th


def weak_levels(ref: str, spec: dict) -> list[tuple[Probe, dict]]:
    """Cumulative levels from a `probe_edits/<task>.json` spec: level k applies the edits of levels 1..k."""
    out, edits = [], []
    for lv in spec.get("levels", []):
        edits = edits + lv["edits"]
        text, err, edited_defs, _ = apply_edits(ref, edits)
        p = Probe("weak", lv["level"], text, f"{lv.get('op', '')}: {lv.get('description', '')}".strip(": "))
        if text is None:
            p.valid, p.reason = False, "edit not applicable: " + err
        elif sorted(L.named_decls(text)) != sorted(L.named_decls(ref)):
            p.code, p.valid, p.reason = None, False, "edits must not add, remove or rename declarations"
        elif text == ref:
            p.code, p.valid, p.reason = None, False, "no-op edit"
        out.append((p, {"closure": closure_of(ref, edited_defs) if text else set(), "proofs": lv.get("proofs", {}),
                        "edited_defs": set(edited_defs) if text else set()}))
    return out
