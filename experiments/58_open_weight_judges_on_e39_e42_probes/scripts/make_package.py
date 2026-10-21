#!/usr/bin/env python3
"""TLDR: Build experiment 58's upload package: a repo-shaped tgz (py_src, experiments 39 and 42 scripts and committed cells,
experiment 58 with its rebuilt prompts and a minimal VeriBench subset for the parsers) plus its sha256, then unpack it into a
temp dir and run the CPU checks there (prompt hash verification, import of the driver's modules). No model calls.

Usage: E58_VERIBENCH_REPO=<veribench clone> make_package.py --out <dir> [--no-check]"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402

X100 = "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test"
GATEWAY = "experiments/95_full_vb_860ish_agent_gpt6_luna_llm_judge_gpt6_sol/tc_gateway"


def vendor_veribench() -> Path:
    """The minimal VeriBench subset experiment 39's imports need (E100 scripts + items, the tc_gateway canonical rubric)."""
    dst = e58.PRIVATE / "veribench_min"
    if dst.exists():
        shutil.rmtree(dst)
    for rel, pats in ((f"{X100}/scripts", ["*.py"]), (f"{X100}/inputs", ["items.jsonl"]), (f"{GATEWAY}/canonical", ["*.py"])):
        (dst / rel).mkdir(parents=True)
        for pat in pats:
            for f in sorted((e58.VB_REPO / rel).glob(pat)):
                shutil.copy2(f, dst / rel / f.name)
    return dst


def package_members() -> list[Path]:
    e39, e42 = e58.E39_DIR, e58.E42_DIR
    keep = [e58.REPO / "py_src", e39 / "scripts", e39 / "results/cells", e39 / "results/probe_manifest.json", e39 / "results/SELECTION.json",
            e39 / "results/panel.json", e39 / "results/harvest", e39 / "prompts", e42 / "scripts", e42 / "probe_edits", e42 / "results/cells",
            e42 / "results/semantic_probe_manifest.json", e58.E]
    files: list[Path] = []
    for p in keep:
        if p.is_dir():
            files += [f for f in sorted(p.rglob("*")) if f.is_file() and "__pycache__" not in f.parts and ".pytest_cache" not in f.parts]
        elif p.exists():
            files.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    vendor_veribench()
    files = package_members()
    tgz = args.out / "e58_pkg.tgz"
    with tarfile.open(tgz, "w:gz") as tar:
        for f in files:
            ti = tar.gettarinfo(str(f), arcname=str(f.relative_to(e58.REPO)))
            ti.mtime, ti.uid, ti.gid, ti.uname, ti.gname = 0, 0, 0, "", ""
            with open(f, "rb") as fh:
                tar.addfile(ti, fh)
    digest = e58.sha_file(tgz)
    (args.out / "e58_pkg.tgz.sha256").write_text(f"{digest}  e58_pkg.tgz\n")
    print(f"{tgz} {tgz.stat().st_size / 1e6:.1f} MB sha256 {digest} ({len(files)} files)")
    if not args.no_check:
        with tempfile.TemporaryDirectory() as td:
            with tarfile.open(tgz) as tar:
                tar.extractall(td)
            code = Path(td) / "experiments" / e58.E.name
            env = {"E58_VERIBENCH_REPO": str(code / "private/veribench_min"), "PATH": "/usr/bin:/bin"}
            for cmd in (["scripts/verify_prompts.py"], ["-c", "import sys; sys.path.insert(0,'scripts'); import e58, harvest_lib, judge_vllm, fetch_models;"
                                                        " e39,_,_ = e58.e39_modules(); import harvest_lib as H; H._x100_prompts();"
                                                        " assert len(e58.units()) == 117; print('imports ok')"]):
                r = subprocess.run([sys.executable, *cmd], cwd=code, env=env, capture_output=True, text=True)
                print(r.stdout.strip(), r.stderr.strip()[-400:])
                if r.returncode:
                    return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
