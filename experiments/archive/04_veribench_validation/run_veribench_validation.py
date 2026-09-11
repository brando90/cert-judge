#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
LEAN_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src"
GOLD_ROOT = LEAN_ROOT / "veribench"
PY_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "py_src"
AGENT_ROOT = REPO_ROOT / "data" / "generated_agents"
LABELS_ROOT = REPO_ROOT / "experiments" / "ethan_hand_labels"

OUT_ROOT = REPO_ROOT / "experiments" / "04_veribench_validation" / "results"
STAGING_ROOT = OUT_ROOT / "veribench"

AGENT_MAP = {"0": "codex", "1": "claude", "2": "llama"}
SPLIT_LABELS = {
    "easy": LABELS_ROOT / "easy_set.csv",
    "cs": LABELS_ROOT / "cs_set.csv",
    "security": LABELS_ROOT / "security_6858.csv",
}
SPLIT_GOLD_DIR = {
    "easy": GOLD_ROOT / "easy_set",
    "cs": GOLD_ROOT / "cs_set",
    "security": GOLD_ROOT / "security_6858",
}
SPLIT_PY_DIR = {
    "easy": PY_ROOT / "easy_set",
    "cs": PY_ROOT / "cs_set",
    "security": PY_ROOT / "security_6858" / "safe",
}

PROMPT_TEMPLATE = """You are evaluating the quality of an AI-generated Lean 4 formalization.

## Original Python source:
{source}

## Gold-reference Lean formalization (human-written, trusted):
{gold}

## Agent-generated Lean formalization (to evaluate):
{agent}

Rate the agent's formalization on a 1–4 scale:
4 = Excellent: Faithfully captures full semantics, all properties/edge cases, non-trivial proof.
3 = Good: Core logic correct, substantive properties, may miss minor edge cases.
2 = Poor: Partial attempt, misses critical properties or has logical errors.
1 = Inadequate: Trivial, vacuous, or useless (theorem true, sorry, unrelated).

Respond with ONLY a JSON object:
{{"score": <1-4>, "reasoning": "<brief explanation>"}}
"""


@dataclass
class PairRow:
    split: str
    problem_id: str
    agent: str
    gold_file: str
    agent_file: str
    human_mean: float
    source_path: Path
    gold_path: Path
    agent_path: Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run VeriBench validation pipeline")
    p.add_argument("--out-dir", type=Path, default=OUT_ROOT)
    p.add_argument("--model", type=str, default="claude-sonnet-4-5")
    p.add_argument("--judge-repeats", type=int, default=3)
    p.add_argument("--skip-equiv", action="store_true")
    p.add_argument("--skip-judge", action="store_true")
    p.add_argument("--splits", nargs="*", default=["easy", "cs", "security"])
    p.add_argument("--limit", type=int, default=0, help="Limit rows for debugging")
    return p.parse_args()


def _read_tsvish_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_raw = next(reader)
        header = [h.strip().replace("\ufeff", "") for h in header_raw]
        for raw in reader:
            if not raw:
                continue
            rec = {}
            for i, key in enumerate(header):
                rec[key.lower()] = raw[i].strip() if i < len(raw) else ""
            rows.append(rec)
    return rows


def _agent_name_from_candidate(candidate: str) -> str:
    m = re.search(r"__agent(\d+)\.lean$", candidate)
    if not m:
        return "unknown"
    return AGENT_MAP.get(m.group(1), f"agent{m.group(1)}")


def _problem_id_from_gold(gold_ref: str) -> str:
    return Path(gold_ref).stem


def _resolve_gold(split: str, gold_file: str) -> Optional[Path]:
    base = SPLIT_GOLD_DIR[split]
    p = base / gold_file
    if p.exists():
        return p
    if split == "security":
        if gold_file == "0_unsafeMultiply_safe.lean":
            p0 = base / "1_unsafeMultiply.lean"
            if p0.exists():
                return p0
        unsuffixed = gold_file.replace("_safe.lean", ".lean")
        p2 = base / unsuffixed
        if p2.exists():
            return p2
    matches = list(base.rglob(gold_file))
    if matches:
        return matches[0]
    return None


def _resolve_source(split: str, gold_file: str) -> Optional[Path]:
    base = SPLIT_PY_DIR[split]
    py_file = gold_file.replace(".lean", ".py")
    if split == "security" and py_file == "0_unsafeMultiply_safe.py":
        py_file = "1_unsafeMultiply_safe.py"
    p = base / py_file
    if p.exists():
        return p
    if split == "security":
        unsuffixed = py_file.replace("_safe.py", ".py")
        p2 = base / py_file
        if p2.exists():
            return p2
        p3 = (PY_ROOT / "security_6858" / "safe" / py_file)
        if p3.exists():
            return p3
        p4 = (PY_ROOT / "security_6858" / "vulnerabilities" / unsuffixed)
        if p4.exists():
            return p4
    matches = list(base.rglob(py_file))
    if matches:
        return matches[0]
    return None


def load_pairs(splits: List[str]) -> List[PairRow]:
    rows: List[PairRow] = []
    for split in splits:
        label_path = SPLIT_LABELS[split]
        raw = _read_tsvish_csv(label_path)
        grouped: Dict[Tuple[str, str], List[float]] = {}
        for r in raw:
            gold = r.get("gold ref") or r.get("gold")
            cand = r.get("agent item") or r.get("candidate")
            score_s = r.get("score")
            if not gold or not cand or not score_s:
                continue
            try:
                score = float(score_s)
            except ValueError:
                continue
            grouped.setdefault((gold, cand), []).append(score)

        for (gold_file, agent_file), scores in sorted(grouped.items()):
            gold_path = _resolve_gold(split, gold_file)
            source_path = _resolve_source(split, gold_file)
            agent_path = AGENT_ROOT / agent_file
            if split == "security" and not agent_path.exists() and agent_file.startswith("0_unsafeMultiply_safe__agent"):
                agent_path = AGENT_ROOT / agent_file.replace("0_unsafeMultiply_safe__", "1_unsafeMultiply_safe__")
            if not gold_path or not source_path or not agent_path.exists():
                continue
            rows.append(
                PairRow(
                    split=split,
                    problem_id=_problem_id_from_gold(gold_file),
                    agent=_agent_name_from_candidate(agent_file),
                    gold_file=gold_file,
                    agent_file=agent_file,
                    human_mean=float(sum(scores) / len(scores)),
                    source_path=source_path,
                    gold_path=gold_path,
                    agent_path=agent_path,
                )
            )
    return rows


def _copy_text(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def stage_files(rows: List[PairRow], out_dir: Path) -> None:
    root = out_dir / "veribench"
    for row in rows:
        d = root / row.split / row.problem_id
        _copy_text(row.source_path, d / "source.py")
        _copy_text(row.gold_path, d / "gold.lean")
        _copy_text(row.agent_path, d / f"agent_{row.agent}.lean")


def ensure_veribench_stubs() -> None:
    vb_root = LEAN_ROOT / "VeriBench"
    vb_root.mkdir(parents=True, exist_ok=True)
    main = LEAN_ROOT / "VeriBench.lean"
    common = vb_root / "Common.lean"
    prelude = vb_root / "Prelude.lean"

    if not main.exists():
        main.write_text(
            """namespace VeriBench

inductive Result (α : Type) where
  | ok : α → Result α
  | err : String → Result α

structure TestCase (α β : Type) where
  input : α
  expected : Result β

def checkTests (_ : List (TestCase α β)) (_f : α → Result β) : IO Unit := pure ()

def assertEq {α : Type} [BEq α] [ToString α] (actual expected : α) : IO Unit :=
  if actual == expected then pure () else throw <| IO.userError s!"assertEq failed: {actual} != {expected}"

def assertPanics {α : Type} (_ : α) : IO Unit := pure ()

end VeriBench
""",
            encoding="utf-8",
        )

    if not common.exists():
        common.write_text("import VeriBench\n", encoding="utf-8")
    if not prelude.exists():
        prelude.write_text("import VeriBench\n", encoding="utf-8")


def _split_imports_and_body(text: str) -> Tuple[List[str], str]:
    imports: List[str] = []
    body_lines: List[str] = []
    for line in text.splitlines():
        if line.strip().startswith("import "):
            imports.append(line.strip())
        elif line.strip().startswith("#eval"):
            continue
        else:
            body_lines.append(line)
    return imports, "\n".join(body_lines) + "\n"


def _find_theorem_decl(text: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    ns_stack: List[str] = []
    lines = text.splitlines()

    for line in lines:
        s = line.strip()
        if s.startswith("namespace "):
            ns = s[len("namespace ") :].strip().split()[0]
            ns_stack.append(ns)
            continue
        if s.startswith("end"):
            if ns_stack:
                ns_stack.pop()
            continue
        if s.startswith("theorem "):
            m = re.match(r"theorem\s+([A-Za-z0-9_'.]+)", s)
            if not m:
                continue
            nm = m.group(1)
            fq = ".".join(ns_stack + [nm]) if ns_stack else nm
            out.append((nm, fq))
    return out


def _extract_theorem_prop(text: str, theorem_name: str) -> Optional[str]:
    m = re.search(rf"theorem\s+{re.escape(theorem_name)}\b", text)
    if not m:
        return None
    i = m.end()
    depth = 0
    found_assign = False
    buff: List[str] = []
    while i < len(text):
        ch = text[i]
        nxt = text[i : i + 2]
        if nxt == ":=" and depth == 0:
            found_assign = True
            break
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
        buff.append(ch)
        i += 1
    if not found_assign:
        return None
    sig = "".join(buff).strip()

    binders: List[str] = []
    j = 0
    while j < len(sig):
        while j < len(sig) and sig[j].isspace():
            j += 1
        if j >= len(sig):
            break
        if sig[j] in "({[":
            open_ch = sig[j]
            close_ch = {"(": ")", "{": "}", "[": "]"}[open_ch]
            d = 0
            k = j
            while k < len(sig):
                if sig[k] == open_ch:
                    d += 1
                elif sig[k] == close_ch:
                    d -= 1
                    if d == 0:
                        break
                k += 1
            if k >= len(sig):
                return None
            binders.append(sig[j : k + 1].strip())
            j = k + 1
            continue
        if sig[j] == ":":
            body = sig[j + 1 :].strip()
            if not body:
                return None
            if not binders:
                return body
            prefix = " ".join(f"∀ {b}," for b in binders)
            return f"{prefix} {body}"
        j += 1
    return None


def _pick_main_theorem(text: str) -> Optional[Tuple[str, str]]:
    candidates = _find_theorem_decl(text)
    if not candidates:
        return None
    priority = [
        r"correctness_thm",
        r"_correct$",
        r"correct",
        r"equivalence",
        r"safe",
        r"post",
    ]
    for pat in priority:
        for nm, fq in candidates:
            if re.search(pat, nm):
                return nm, fq
    return candidates[0]


def _mk_equiv_content(gold_text: str, agent_text: str, direction: str) -> Tuple[str, Optional[str], Optional[str]]:
    gold_imports, gold_body = _split_imports_and_body(gold_text)
    agent_imports, agent_body = _split_imports_and_body(agent_text)

    imports = sorted(set(gold_imports + agent_imports + ["import VeriBench", "import Mathlib"]))

    picked_gold = _pick_main_theorem(gold_body)
    picked_agent = _pick_main_theorem(agent_body)
    if not picked_gold or not picked_agent:
        return "\n".join(imports) + "\n\nnamespace GoldWrap\n" + gold_body + "\nend GoldWrap\n\nnamespace AgentWrap\n" + agent_body + "\nend AgentWrap\n\n-- No theorem candidates found\n", None, None

    gold_nm, gold_fq = picked_gold
    agent_nm, agent_fq = picked_agent

    gold_prop = _extract_theorem_prop(gold_body, gold_nm)
    agent_prop = _extract_theorem_prop(agent_body, agent_nm)

    if not gold_prop or not agent_prop:
        return "\n".join(imports) + "\n\nnamespace GoldWrap\n" + gold_body + "\nend GoldWrap\n\nnamespace AgentWrap\n" + agent_body + "\nend AgentWrap\n\n-- Could not parse theorem signatures\n", None, None

    if direction == "iff":
        proof = """
theorem equiv_agent_gold : AgentMain ↔ GoldMain := by
  constructor
  · intro h
    simpa [AgentMain, GoldMain] using h
  · intro h
    simpa [AgentMain, GoldMain] using h
"""
    elif direction == "forward_only":
        proof = """
theorem equiv_agent_gold_forward : AgentMain → GoldMain := by
  intro h
  simpa [AgentMain, GoldMain] using h
"""
    else:
        proof = """
theorem equiv_agent_gold_reverse : GoldMain → AgentMain := by
  intro h
  simpa [AgentMain, GoldMain] using h
"""

    content = (
        "\n".join(imports)
        + "\n\nnamespace GoldWrap\n"
        + gold_body
        + "\nend GoldWrap\n\nnamespace AgentWrap\n"
        + agent_body
        + "\nend AgentWrap\n\n"
        + f"abbrev GoldMain : Prop := ({gold_prop})\n"
        + f"abbrev AgentMain : Prop := ({agent_prop})\n"
        + proof
    )
    return content, f"GoldWrap.{gold_fq}", f"AgentWrap.{agent_fq}"


def _run_lean_check(file_path: Path) -> Tuple[bool, str]:
    file_abs = file_path.resolve()
    cmd = ["zsh", "-lc", f"cd {LEAN_ROOT} && source $HOME/.elan/env && lake env lean {file_abs}"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return False, "lean_check_timeout"
    ok = proc.returncode == 0
    err = (proc.stderr or proc.stdout or "").strip()
    if len(err) > 4000:
        err = err[-4000:]
    return ok, err


def _categorize_error(err: str) -> str:
    e = err.lower()
    if "type mismatch" in e:
        return "type_mismatch"
    if "unknown constant" in e or "unknown identifier" in e or "unknown package" in e:
        return "missing_definition"
    if "sorry" in e or "admit" in e:
        return "sorry_remaining"
    if "application type mismatch" in e:
        return "type_mismatch"
    return "unrelated_structure"


def run_equivalence(rows: List[PairRow], out_dir: Path) -> pd.DataFrame:
    records: List[Dict[str, object]] = []
    root = out_dir / "veribench"

    for row in rows:
        d = root / row.split / row.problem_id
        gold_text = (d / "gold.lean").read_text(encoding="utf-8")
        agent_text = (d / f"agent_{row.agent}.lean").read_text(encoding="utf-8")

        best_direction = "none"
        best_error = ""

        attempts = ["iff", "forward_only", "reverse_only"]
        for direction in attempts:
            content, gold_main, agent_main = _mk_equiv_content(gold_text, agent_text, direction)
            eq_file = d / f"equiv_{row.agent}.lean"
            eq_file.write_text(content, encoding="utf-8")

            ok, err = _run_lean_check(eq_file)
            if ok:
                best_direction = direction
                best_error = ""
                break
            if not best_error:
                best_error = err

        records.append(
            {
                "split": row.split,
                "problem_id": row.problem_id,
                "agent": row.agent,
                "proof_compiles": best_direction != "none",
                "direction": best_direction,
                "lean_error": best_error,
                "error_category": _categorize_error(best_error) if best_error else "",
            }
        )

    df = pd.DataFrame(records).sort_values(["split", "problem_id", "agent"])
    df.to_csv(out_dir / "equivalence_results.csv", index=False)
    return df


def _extract_json_obj(text: str) -> Optional[Dict[str, object]]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _call_judge_once(prompt: str, model: str) -> Tuple[Optional[int], str]:
    if model.startswith("claude"):
        import anthropic

        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            return None, "Missing ANTHROPIC_API_KEY"
        client = anthropic.Anthropic(api_key=key)
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text if resp.content else ""
        except Exception as e:
            return None, f"judge_api_error: {e}"
    else:
        from openai import OpenAI

        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            return None, "Missing OPENAI_API_KEY"
        client = OpenAI(api_key=key)
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.choices[0].message.content or ""
        except Exception as e:
            return None, f"judge_api_error: {e}"

    obj = _extract_json_obj(text or "")
    if not obj:
        return None, "judge_parse_error"

    score_raw = obj.get("score")
    try:
        score = int(score_raw)
    except Exception:
        return None, f"judge_bad_score: {score_raw}"
    if score < 1 or score > 4:
        return None, f"judge_score_out_of_range: {score}"
    reasoning = str(obj.get("reasoning", "")).strip()
    return score, reasoning


def run_judge(rows: List[PairRow], out_dir: Path, model: str, repeats: int) -> pd.DataFrame:
    records: List[Dict[str, object]] = []
    root = out_dir / "veribench"

    for row in rows:
        d = root / row.split / row.problem_id
        source = (d / "source.py").read_text(encoding="utf-8")
        gold = (d / "gold.lean").read_text(encoding="utf-8")
        agent = (d / f"agent_{row.agent}.lean").read_text(encoding="utf-8")

        prompt = PROMPT_TEMPLATE.format(source=source, gold=gold, agent=agent)
        votes: List[int] = []
        reasonings: List[str] = []
        errors: List[str] = []
        for _ in range(repeats):
            score, why = _call_judge_once(prompt, model=model)
            if score is None:
                errors.append(why)
            else:
                votes.append(score)
                reasonings.append(why)

        if votes:
            counts = Counter(votes)
            modal_score = sorted(counts.items(), key=lambda kv: (-kv[1], -kv[0]))[0][0]
            modal_reasoning = ""
            for s, r in zip(votes, reasonings):
                if s == modal_score and r:
                    modal_reasoning = r
                    break
        else:
            modal_score = None
            modal_reasoning = "; ".join(errors)[:500]

        records.append(
            {
                "split": row.split,
                "problem_id": row.problem_id,
                "agent": row.agent,
                "judge_score": modal_score,
                "judge_reasoning": modal_reasoning,
                "judge_votes": json.dumps(votes),
            }
        )

    df = pd.DataFrame(records).sort_values(["split", "problem_id", "agent"])
    df.to_csv(out_dir / "judge_results.csv", index=False)
    return df


def write_human(rows: List[PairRow], out_dir: Path) -> pd.DataFrame:
    records = [
        {
            "split": r.split,
            "problem_id": r.problem_id,
            "agent": r.agent,
            "human_mean": r.human_mean,
            "gold_file": r.gold_file,
            "agent_file": r.agent_file,
        }
        for r in rows
    ]
    df = pd.DataFrame(records).sort_values(["split", "problem_id", "agent"])
    df.to_csv(out_dir / "human_judgments.csv", index=False)
    return df


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_pairs(args.splits)
    if args.limit > 0:
        rows = rows[: args.limit]
    if not rows:
        raise RuntimeError("No rows were loaded; check split/file mappings")

    stage_files(rows, out_dir)
    ensure_veribench_stubs()

    human_df = write_human(rows, out_dir)
    print(f"Wrote human_judgments.csv with n={len(human_df)}")

    if not args.skip_equiv:
        eq_df = run_equivalence(rows, out_dir)
        print(f"Wrote equivalence_results.csv with n={len(eq_df)}")

    if not args.skip_judge:
        judge_df = run_judge(rows, out_dir, model=args.model, repeats=args.judge_repeats)
        print(f"Wrote judge_results.csv with n={len(judge_df)}")


if __name__ == "__main__":
    main()
