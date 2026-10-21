#!/usr/bin/env python3
"""TLDR: Download the panel's weights at their pinned Hugging Face revisions into <dir>/<model key>/ (huggingface_hub), write
<dir>/<key>/REVISION, and check each finished snapshot (revision file, safetensors present, size within 10% of the
expected weights_gb). Needs internet and `huggingface_hub`; run on a node with internet (prepare.sh), never in a job.

Usage: fetch_models.py --dir ~/e58/models [--models qwen3_4b,qwen3_8b | all] [--list]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402


def snapshot_ok(d: Path, key: str) -> tuple[bool, str]:
    m = e58.MODELS[key]
    rf = d / "REVISION"
    if not rf.exists() or rf.read_text().strip() != m["revision"]:
        return False, "REVISION missing or different"
    size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / 1e9
    if not any(d.glob("*.safetensors")):
        return False, "no safetensors"
    if abs(size - m["weights_gb"]) > 0.10 * m["weights_gb"] + 1.0:
        return False, f"size {size:.1f} GB vs expected {m['weights_gb']} GB"
    return True, f"{size:.1f} GB"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--models", default="all")
    ap.add_argument("--list", action="store_true", help="print 'key gpus' lines (the tasks list) and exit")
    args = ap.parse_args()
    keys = e58.MODEL_ORDER if args.models == "all" else tuple(args.models.split(","))
    if args.list:
        for k in keys:
            print(k, e58.MODELS[k]["gpus"])
        return 0
    from huggingface_hub import snapshot_download
    bad = 0
    for k in keys:
        m = e58.MODELS[k]
        d = args.dir / k
        ok, why = snapshot_ok(d, k) if d.exists() else (False, "absent")
        if ok:
            print(f"{k}: present at {m['revision'][:12]} ({why})", flush=True)
            continue
        kw = {"allow_patterns": m.get("download_patterns", ["*.json", "*.safetensors", "*.txt", "tokenizer*", "*.jinja", "*.model"])}
        if m.get("download_ignore"):
            kw["ignore_patterns"] = m["download_ignore"]
        snapshot_download(m["repo"], revision=m["revision"], local_dir=str(d), **kw)
        (d / "REVISION").write_text(m["revision"] + "\n")
        ok, why = snapshot_ok(d, k)
        print(f"{k}: {'OK' if ok else 'CHECK FAILED'} {why}", flush=True)
        bad += 0 if ok else 1
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
