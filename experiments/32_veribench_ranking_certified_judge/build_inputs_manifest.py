#!/usr/bin/env python3
"""Build inputs_manifest.json for Experiment 32 (no inference, no credentials).

Candidates: the four Claude-3.7 agent runs pinned in ~/veribench/CONTRIBUTING.md
(lines 180-183). Golds: frozen precedence policy from
experiments/archive/04_veribench_validation/run_pti_v0.py (legacy root first,
newest root only when absent from legacy), matched by basename within the
candidate's split directory first, then anywhere under the root.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = Path(__file__).resolve().parent
VB = Path.home() / "veribench/research_archive/experiments/11_dspy_or_trace_agent_gens_for_evals/latest_runs"
AGENTS = {
    "baseline": VB / "trace/2025_m09_d23_t21h_47m_14s/allen_run_baseline_on_veribench",
    "dspy_react": VB / "dspy_3-7-sonnet/2025_m09_d23_t21h_47m_14s/allen_run_dspy_on_veribench",
    "trace_plus": VB / "trace/2025_m09_d23_t21h_47m_14s/allen_run_trace_self_debug_on_veribench",
    "trace_plusplus": VB / "trace/2025_m09_d24_t18h_57m_03s/allen_run_trace_self_debug_and_self_improve_on_veribench",
}
AGENT_TABLE_NAMES = {
    "baseline": "Baseline",
    "dspy_react": "DSPy ReAct",
    "trace_plus": "Trace+",
    "trace_plusplus": "Trace++",
}
GOLD_ROOTS = (
    REPO_ROOT / "data/veribench_dataset/lean_src/veribench",
    REPO_ROOT / "data/veribench_dataset_newest/lean_src/veribench",
)
SPLITS = ["easy_set", "cs_set", "real_code", "humaneval_set", "security_6858", "security_python"]
# Frozen Exp16 regex (run_pti_v0.py::_LEGACY_THEOREM_BLOCK_RE / utils.veribench_variance_utils.extract_theorem_blocks)
THEOREM_BLOCK_RE = re.compile(
    r"(?ms)^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b.*?"
    r"(?=^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b|\Z)"
)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def last_theorem_block(text: str) -> tuple[str, bool]:
    spans = [(m.start(), m.end()) for m in THEOREM_BLOCK_RE.finditer(text)]
    if not spans:
        return text, False
    s, e = spans[-1]
    block = text[s:e].strip()
    return (block, True) if block else (text, False)


def resolve_gold(split: str, name: str) -> tuple[Path, str]:
    for root in GOLD_ROOTS:
        direct = root / split / name
        if direct.exists():
            return direct, f"{root.relative_to(REPO_ROOT)} (split dir)"
        hits = sorted(root.rglob(name))
        if len(hits) == 1:
            return hits[0], f"{root.relative_to(REPO_ROOT)} (rglob)"
        if len(hits) > 1:
            raise RuntimeError(f"ambiguous gold for {split}/{name}: {hits}")
    raise FileNotFoundError(f"no gold for {split}/{name}")


def main() -> None:
    rows = []
    golds = {}
    for agent, adir in AGENTS.items():
        if not adir.is_dir():
            raise FileNotFoundError(adir)
        for split in SPLITS:
            sdir = adir / split
            for cand in sorted(sdir.glob("*.lean")):
                item = f"{split}/{cand.stem}"
                if item not in golds:
                    gpath, how = resolve_gold(split, cand.name)
                    gtext = gpath.read_text(encoding="utf-8", errors="ignore")
                    block, found = last_theorem_block(gtext)
                    golds[item] = {
                        "item": item,
                        "split": split,
                        "gold_path": str(gpath),
                        "gold_sha256": sha256_file(gpath),
                        "gold_resolution": how,
                        "reference_has_theorem_block": found,
                        "reference_chars": len(block),
                    }
                rows.append({
                    "item": item,
                    "agent": agent,
                    "agent_table_name": AGENT_TABLE_NAMES[agent],
                    "split": split,
                    "candidate_path": str(cand),
                    "candidate_sha256": sha256_file(cand),
                    "candidate_chars": len(cand.read_text(encoding="utf-8", errors="ignore")),
                })
    items = sorted(golds)
    manifest = {
        "schema_version": "exp32_inputs_manifest_v1",
        "candidate_source": "~/veribench/CONTRIBUTING.md lines 180-183 (Claude 3.7 Sonnet agent runs, latest_runs)",
        "agent_dirs": {a: str(p) for a, p in AGENTS.items()},
        "gold_roots_precedence": [str(r.relative_to(REPO_ROOT)) for r in GOLD_ROOTS],
        "gold_resolution_policy": "prefer legacy root; use newest root only when absent from legacy (frozen PTI-v0 policy)",
        "reference_preprocessing": "last theorem/lemma block of the gold using the frozen Exp16 regex; full gold when no block exists (exp16_multi_judge_human_sets.py:476)",
        "candidate_preprocessing": "full candidate file text (exp16_multi_judge_human_sets.py:477)",
        "splits": SPLITS,
        "n_items": len(items),
        "n_agents": len(AGENTS),
        "n_candidate_rows": len(rows),
        "items": [golds[i] for i in items],
        "candidates": rows,
    }
    out = EXP_DIR / "inputs_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    per_split = {s: sum(1 for i in items if i.startswith(s + "/")) for s in SPLITS}
    print(f"wrote {out}: items={len(items)} rows={len(rows)} per_split={per_split}")
    print("golds without theorem block:", [g["item"] for g in golds.values() if not g["reference_has_theorem_block"]])
    print("gold resolution modes:", sorted({g["gold_resolution"] for g in golds.values()}))


if __name__ == "__main__":
    main()
