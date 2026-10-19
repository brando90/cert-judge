#!/usr/bin/env python3
"""TLDR: Structural probe-support counts for CLEVER, FVAPPS, and miniCodeProps. Zero model calls.
Reads shallow clones in /tmp/cj54_benchmarks. See PROTOCOL.md for the 80 percent rule.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/tmp/cj54_benchmarks")
OUT = Path(__file__).resolve().parents[1] / "results"


def sha(repo: Path) -> str | None:
    if not (repo / ".git").exists():
        return None
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def toolchain(repo: Path) -> str | None:
    hits = [p for p in repo.rglob("lean-toolchain") if ".git" not in p.parts]
    return hits[0].read_text(encoding="utf-8").strip() if hits else None


def share(n: int, k: int) -> dict:
    return {"n": k, "of": n, "share": (k / n) if n else None, "supports": None if n == 0 else k / n >= 0.80}


def clever() -> dict:
    files = sorted((ROOT / "clever/src/lean4/human_eval").glob("*.lean"))
    spec = bug = alpha = sorry = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "def problem_spec" in text or "\ntheorem " in text:
            spec += 1
        if "def problem_spec" in text and "(" in text.split("def problem_spec", 1)[1].split(":=", 1)[0]:
            alpha += 1
        if "-- start_def implementation\n" in text:
            body = text.split("-- start_def implementation\n", 1)[1].split("-- end_def implementation", 1)[0].strip()
            if body == "sorry" or body.startswith("sorry"):
                sorry += 1
            else:
                bug += 1
    n = len(files)
    return {
        "benchmark": "CLEVER",
        "commit": sha(ROOT / "clever"),
        "toolchain": toolchain(ROOT / "clever"),
        "unit": "human_eval/*.lean",
        "lean_files": n,
        "implementation_sorry": sorry,
        "specification_removal": share(n, spec),
        "bug_ladder": share(n, bug),
        "alpha": share(n, alpha),
        "elaboration": "NOT_INSTALLED",
        "note": "Pinned toolchain leanprover/lean4:v4.27.0 is not installed on this machine (installed: v4.18.0, v4.22.0, v4.24.0).",
    }


def fvapps() -> dict:
    return {
        "benchmark": "FVAPPS",
        "commit": sha(ROOT / "fvapps"),
        "toolchain": toolchain(ROOT / "fvapps"),
        "unit": "GitHub checkout; the task set is the Hugging Face dataset quinn-dougherty/fvapps, which was not downloaded",
        "lean_files": 0,
        "scaffolding_lean_files": len(list((ROOT / "fvapps").rglob("*.lean"))),
        "specification_removal": share(0, 0),
        "bug_ladder": share(0, 0),
        "alpha": share(0, 0),
        "elaboration": "NOT_MEASURED",
        "note": "The checkout contains scaffolding Lean files only. Task support is not measured.",
    }


def mini() -> dict:
    rows = [json.loads(line) for line in (ROOT / "minicodeprops/data/minicodeprops_bench_ps.jsonl").read_text().splitlines() if line.strip()]
    n = len(rows)
    spec = sum(1 for row in rows if row["prop_defn"].lstrip().startswith("theorem"))
    alpha = sum(1 for row in rows if "(" in row["prop_defn"].split(":=", 1)[0])
    return {
        "benchmark": "miniCodeProps",
        "commit": sha(ROOT / "minicodeprops"),
        "toolchain": toolchain(ROOT / "minicodeprops/MiniCodePropsLeanSrc"),
        "unit": "data/minicodeprops_bench_ps.jsonl property theorems; programs are 7 shared LeanSrc files",
        "lean_files": n,
        "specification_removal": share(n, spec),
        "bug_ladder": share(n, 0),
        "alpha": share(n, alpha),
        "elaboration": "NOT_INSTALLED",
        "note": "Pinned toolchain leanprover/lean4:v4.9.0 is not installed. No per-task implementation, so a bug ladder has no file of its own.",
    }


def main() -> None:
    rows = [clever(), fvapps(), mini()]
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"written_utc": datetime.now(timezone.utc).isoformat(), "threshold": 0.80, "rows": rows}
    (OUT / "structural_counts.json").write_text(json.dumps(payload, indent=1) + "\n")
    for row in rows:
        print(row["benchmark"], row["specification_removal"], row["bug_ladder"], row["alpha"])


if __name__ == "__main__":
    main()
