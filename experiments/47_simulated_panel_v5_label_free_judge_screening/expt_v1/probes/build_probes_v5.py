#!/usr/bin/env python3
"""Build the frozen E39 subset for E47 and compile it with Lean.

This worker deliberately imports the frozen E39 transformation module instead of
copying its algorithms.  All mutable files are beneath E47's ignored private
worker directory; the committed manifests contain only logical paths and hashes.
No inference client is imported or called.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPT = HERE.parent
REPO = HERE.parents[3]
E39 = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts"
SOURCE_ROOT_DEFAULT = Path("/dfs/scratch0/brando9/cert-judge-e47-v5-sandbox/experiments/47_simulated_panel_v5_label_free_judge_screening/expt_v1")
LAKE_PROJECT_DEFAULT = Path("/lfs/skampere1/0/brando9/vb90_grading/lean_project")
LAKE_BIN_DEFAULT = Path.home() / ".elan/bin/lake"
PRIVATE = EXPT / "private/probes_worker"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def json_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def logical_path(path: Path) -> str:
    """Never publish an absolute source or private path."""
    return path.name


def load_frozen_probes():
    sys.path.insert(0, str(E39))
    spec = importlib.util.spec_from_file_location("e47_frozen_e39_probes", E39 / "probes.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen E39 probes.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


P = load_frozen_probes()


class Compiler:
    """Hash-resumable, two-worker-safe `lake env lean` executor."""

    def __init__(self, project: Path, lake: Path, cache_path: Path, timeout: int):
        self.project, self.lake, self.cache_path, self.timeout = project, lake, cache_path, timeout
        self.lock = threading.Lock()
        self.cache: dict[str, dict] = {}
        if cache_path.exists():
            for line in cache_path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                if row.get("environment") == self.environment:
                    self.cache[row["sha256"]] = row

    @property
    def environment(self) -> str:
        return f"{self.project}:{sha_file(self.project / 'lean-toolchain')}:{sha_file(self.project / 'lake-manifest.json')}:{sha_file(self.lake)}"

    def compile(self, code: str) -> dict:
        digest = P.sha256_text(code)
        with self.lock:
            cached = self.cache.get(digest)
        if cached is not None:
            return {**cached, "reused": True}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", prefix="e47_probe_", encoding="utf-8", delete=False) as out:
            out.write(code)
            source = Path(out.name)
        try:
            proc = subprocess.run([str(self.lake), "env", "lean", str(source)], cwd=self.project,
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=self.timeout, check=False)
            output, rc = proc.stdout, proc.returncode
        except subprocess.TimeoutExpired as exc:
            output, rc = "TIMEOUT after %ss\n%s" % (self.timeout, exc.stdout or ""), 124
        finally:
            source.unlink(missing_ok=True)
        result = {"sha256": digest, "ok": rc == 0, "returncode": rc, "output_sha256": sha_bytes(output.encode()),
                  "output": output[-12000:], "environment": self.environment, "finished_utc": utc(), "reused": False}
        with self.lock:
            # A concurrently completed same digest is equivalent; preserve the first receipt.
            prior = self.cache.get(digest)
            if prior is not None:
                return {**prior, "reused": True}
            self.cache[digest] = result
            with self.cache_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, sort_keys=True) + "\n")
        return result


def compile_reason(receipt: dict) -> str:
    if receipt["ok"]:
        return "ok"
    output = receipt.get("output", "").lower()
    if receipt["returncode"] == 124:
        return "timeout"
    if "unknown module prefix" in output or "invalid import" in output or "object file" in output:
        return "unresolved_import"
    if "unexpected token" in output or "parser error" in output or "invalid syntax" in output:
        return "parse"
    if "type mismatch" in output or "failed to synthesize" in output or "unknown identifier" in output:
        return "type_or_elaboration"
    return "elaboration"


def candidate_source(record: dict, root: Path) -> Path | None:
    group, harbor = record["group"], record["harbor"]
    if group in {f"G{i:02d}" for i in range(1, 14)}:
        return root / "inputs/veribench_v5/inputs/candidates" / group / f"{harbor}.lean"
    if group == "G16":
        return root / "private/late_candidates/G16" / f"{harbor}.lean"
    if group == "G17":
        # The frozen source field names the exact selected replacement/recovery output.
        source_file = record["source"].get("file", "")
        if "/outputs/" not in source_file:
            return None
        relative = source_file.split("/outputs/", 1)[1]
        return root / "private/late_candidates" / relative
    return None


def copy_bound(path: Path, destination: Path, expected: str | None) -> tuple[str | None, str]:
    if not path.is_file():
        return None, "missing_source"
    digest = sha_file(path)
    if expected is not None and digest != expected:
        return digest, "hash_mismatch"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or sha_file(destination) != digest:
        shutil.copyfile(path, destination)
    return digest, "verified"


def source_records(root: Path) -> tuple[list[dict], dict]:
    base = root / "inputs/veribench_v5"
    main = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    late = json.loads((base / "late/manifest_G16_G17.json").read_text(encoding="utf-8"))
    rows = [r for r in main["items"] if r["group"] != "G00"] + list(late["items"])
    if len(rows) != 750 or sum(not r["blank"] for r in rows) != 691:
        raise RuntimeError("frozen source counts are not 750 declared / 691 nonblank")
    if set(r["group"] for r in rows) != {*(f"G{i:02d}" for i in range(1, 14)), "G16", "G17"}:
        raise RuntimeError("fresh group set differs from G01-G13,G16,G17")
    return rows, {"main_manifest_sha256": sha_file(base / "manifest.json"),
                  "late_manifest_sha256": sha_file(base / "late/manifest_G16_G17.json"),
                  "source_commit_declared": "ccd86d467fd7577826c4b549df2c532bf43b1892"}


def make_row(kind: str, key: str, task: str, item: str | None, level: int, source_sha: str | None, **extra) -> dict:
    return {"probe_id": f"{kind}__{key}__L{level}", "kind": kind, "key": key, "task": task,
            "item": item, "level": level, "source_sha256": source_sha, **extra}


def build_one(task: str, reference: dict, candidates: list[dict], compiler: Compiler) -> tuple[list[dict], list[dict]]:
    """Use frozen E39 constructors; return public rows plus private code artifacts."""
    rows, artifacts = [], []
    ref_code = reference["code"]
    ref_sha = reference["actual_sha256"]
    ref_receipt = compiler.compile(ref_code)
    rows.append(make_row("ident", task, task, None, 0, ref_sha, sha256=ref_sha, valid=ref_receipt["ok"],
                         compile=receipt_public(ref_receipt), note="gold as candidate", reason=compile_reason(ref_receipt)))
    rows.append(make_row("blank", task, task, None, 0, ref_sha, sha256=P.sha256_text(""), valid=True,
                         compile={"status": "not_applicable"}, note="empty candidate", reason="structural blank control"))
    gold_declared = len(P.cut_points(len(P.theorem_decls(ref_code)), 4))
    if ref_receipt["ok"]:
        ladder = P.delete_theorems_ladder(ref_code, 4, lambda text: compiler.compile(text)["ok"])
        for art in ladder[1:]:
            receipt = compiler.compile(art.code)
            artifacts.append(private_artifact("ms_gold", task, art.level, art.code))
            rows.append(make_row("ms_gold", task, task, None, art.level, ref_sha, sha256=art.sha256, valid=receipt["ok"],
                                 compile=receipt_public(receipt), note=art.note, reason=compile_reason(receipt)))
        for level in range(len(ladder), gold_declared + 1):
            rows.append(make_row("ms_gold", task, task, None, level, ref_sha, sha256=None, valid=False,
                                 compile={"status": "not_constructed"}, note="", reason="level did not elaborate or was a no-op"))
        bugs = P.bug_ladder(ref_code, lambda text: compiler.compile(text)["ok"], 4)
        for art in bugs[1:]:
            receipt = compiler.compile(art.code)
            artifacts.append(private_artifact("bm_gold", task, art.level, art.code))
            rows.append(make_row("bm_gold", task, task, None, art.level, ref_sha, sha256=art.sha256, valid=receipt["ok"],
                                 compile=receipt_public(receipt), note=art.note, reason=compile_reason(receipt)))
        for level in range(len(bugs), 5):
            rows.append(make_row("bm_gold", task, task, None, level, ref_sha, sha256=None, valid=False,
                                 compile={"status": "not_constructed"}, note="", reason="no compile-valid cumulative mutation"))
    else:
        for kind, max_level in (("ms_gold", max(gold_declared, 1)), ("bm_gold", 4)):
            for level in range(1, max_level + 1):
                rows.append(make_row(kind, task, task, None, level, ref_sha, sha256=None, valid=False,
                                     compile={"status": "not_attempted"}, note="", reason="reference does not elaborate"))
    for candidate in candidates:
        item = candidate["item"]
        if candidate["blank"]:
            rows.append(make_row("crit", item, task, item, 0, candidate.get("actual_sha256"), sha256=candidate.get("actual_sha256"),
                                 valid=True, compile={"status": "not_applicable"}, note="declared blank candidate retained", reason="declared_blank"))
            rows.append(make_row("ms_cand", item, task, item, 1, candidate.get("actual_sha256"), sha256=None, valid=False,
                                 compile={"status": "not_attempted"}, note="", reason="declared_blank"))
            continue
        if candidate["source_status"] != "verified":
            rows.append(make_row("crit", item, task, item, 0, candidate.get("actual_sha256"), sha256=candidate.get("actual_sha256"),
                                 valid=True, compile={"status": "source_unavailable"}, note="criterion row retained", reason=candidate["source_status"]))
            rows.append(make_row("ms_cand", item, task, item, 1, candidate.get("actual_sha256"), sha256=None, valid=False,
                                 compile={"status": "not_attempted"}, note="", reason=candidate["source_status"]))
            continue
        code, digest = candidate["code"], candidate["actual_sha256"]
        cand_receipt = compiler.compile(code)
        # Frozen criterion rows stay declared even if their Lean source fails.
        rows.append(make_row("crit", item, task, item, 0, digest, sha256=digest, valid=True,
                             candidate_compile=receipt_public(cand_receipt), note="rated candidate", reason="criterion_row_retained"))
        if not cand_receipt["ok"]:
            rows.append(make_row("ms_cand", item, task, item, 1, digest, sha256=None, valid=False,
                                 compile={"status": "not_constructed", "source_compile": receipt_public(cand_receipt)}, note="",
                                 reason="candidate does not elaborate"))
            continue
        declared = len(P.cut_points(len(P.theorem_decls(code)), 3))
        ladder = P.delete_theorems_ladder(code, 3, lambda text: compiler.compile(text)["ok"])
        for art in ladder[1:]:
            receipt = compiler.compile(art.code)
            artifacts.append(private_artifact("ms_cand", item, art.level, art.code))
            rows.append(make_row("ms_cand", item, task, item, art.level, digest, sha256=art.sha256, valid=receipt["ok"],
                                 compile=receipt_public(receipt), note=art.note, reason=compile_reason(receipt)))
        for level in range(len(ladder), declared + 1):
            rows.append(make_row("ms_cand", item, task, item, level, digest, sha256=None, valid=False,
                                 compile={"status": "not_constructed"}, note="", reason="level did not elaborate or was a no-op"))
        if declared == 0:
            rows.append(make_row("ms_cand", item, task, item, 1, digest, sha256=None, valid=False,
                                 compile={"status": "not_attempted"}, note="", reason="no theorem/lemma declarations"))
    return rows, artifacts


def private_artifact(kind: str, key: str, level: int, code: str) -> dict:
    path = PRIVATE / "artifacts" / kind / f"{key}__L{level}.lean"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return {"kind": kind, "key": key, "level": level, "sha256": sha_file(path), "private_relpath": str(path.relative_to(EXPT))}


def receipt_public(receipt: dict) -> dict:
    return {k: receipt[k] for k in ("ok", "returncode", "output_sha256", "finished_utc", "reused") if k in receipt} | {"class": compile_reason(receipt)}


def counts(rows: list[dict]) -> dict:
    result: dict[str, dict[str, int]] = {}
    for row in rows:
        group = result.setdefault(row["kind"], {"rows": 0, "valid": 0, "invalid": 0, "criterion_retained": 0})
        group["rows"] += 1
        if row.get("valid") is True:
            group["valid"] += 1
        elif row.get("valid") is False:
            group["invalid"] += 1
        if row["kind"] == "crit":
            group["criterion_retained"] += 1
    return result


def write_ack(input_hash: str) -> None:
    json_write(HERE / "runtime/worker_ack.json", {
        "run_id": "cj-e47-probes-10-08-2026-a1", "written_utc": utc(), "input_manifest_sha256": input_hash,
        "executor": {"model": "gpt-5.6-terra", "reasoning_effort": "high", "permissions": "full access; no approvals"},
        "host": socket.gethostname(), "cwd": str(Path.cwd()), "session": "codex-cj-e47-v5-probes",
        "process_id": os.getpid(), "first_useful_action": "verified frozen input manifest counts and Lean v4.22 project provenance"
    })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", type=Path, default=SOURCE_ROOT_DEFAULT)
    ap.add_argument("--lake-project", type=Path, default=LAKE_PROJECT_DEFAULT)
    ap.add_argument("--lake-bin", type=Path, default=LAKE_BIN_DEFAULT)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    if args.jobs != 2:
        raise SystemExit("frozen worker launch uses exactly two compile workers")
    if not (args.lake_project / "lean-toolchain").is_file() or not args.lake_bin.is_file():
        raise SystemExit("pinned Lean project or lake binary unavailable")
    records, provenance = source_records(args.source_root)
    write_ack(provenance["main_manifest_sha256"])
    input_dir = PRIVATE / "input_bytes"
    references: dict[str, dict] = {}
    candidate_rows: list[dict] = []
    for record in records:
        task, harbor = record["task"], record["harbor"]
        ref_source = args.source_root / "inputs/veribench_v5/inputs/tasks" / harbor / record["ref_name"]
        digest, status = copy_bound(ref_source, input_dir / "references" / f"{harbor}.lean", record["ref_sha256"])
        if status != "verified":
            raise RuntimeError(f"reference {task} is {status}; no artifact admitted")
        prior = references.get(task)
        if prior is None:
            copied = input_dir / "references" / f"{harbor}.lean"
            references[task] = {"task": task, "harbor": harbor, "expected_sha256": record["ref_sha256"], "actual_sha256": digest,
                                "source_status": status, "code": copied.read_text(encoding="utf-8", errors="replace")}
        elif prior["actual_sha256"] != digest:
            raise RuntimeError(f"reference hash disagreement within task {task}")
        source = candidate_source(record, args.source_root)
        expected = record["cand_sha256"]
        if record["blank"]:
            candidate_rows.append({**record, "source_status": "declared_blank", "actual_sha256": None})
            continue
        destination = input_dir / "candidates" / record["group"] / f"{harbor}.lean"
        actual, status = copy_bound(source, destination, expected) if source is not None else (None, "missing_source")
        item = {**record, "source_status": status, "actual_sha256": actual}
        if status == "verified":
            item["code"] = destination.read_text(encoding="utf-8", errors="replace")
        candidate_rows.append(item)
    if len(references) != 50:
        raise RuntimeError(f"expected 50 unique reference tasks, got {len(references)}")
    source_manifest = {"written_utc": utc(), "provenance": provenance, "declared": {"rows": len(records), "nonblank": sum(not r["blank"] for r in records), "blank": sum(r["blank"] for r in records), "unique_tasks": len(references)},
                       "references": [{k: v for k, v in r.items() if k != "code"} for r in sorted(references.values(), key=lambda r: r["task"])],
                       "candidates": [{k: v for k, v in r.items() if k not in {"code", "source"}} for r in candidate_rows]}
    json_write(HERE / "source_manifest.json", source_manifest)
    compiler = Compiler(args.lake_project, args.lake_bin, PRIVATE / "compile_cache.jsonl", args.timeout)
    by_task: dict[str, list[dict]] = {}
    for row in candidate_rows:
        by_task.setdefault(row["task"], []).append(row)
    with ThreadPoolExecutor(max_workers=2) as pool:
        built = list(pool.map(lambda task: build_one(task, references[task], sorted(by_task[task], key=lambda r: r["item"]), compiler), sorted(references)))
    rows = [row for item_rows, _ in built for row in item_rows]
    artifacts = [artifact for _, item_artifacts in built for artifact in item_artifacts]
    probe_manifest = {"written_utc": utc(), "run_id": "cj-e47-probes-10-08-2026-a1", "frozen_transform": {"path": "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts/probes.py", "sha256": sha_file(E39 / "probes.py"), "kinds": {"ident": 0, "blank": 0, "ms_gold": 4, "ms_cand": 3, "bm_gold": 4}},
                      "rows": rows, "counts": counts(rows), "private_artifacts": artifacts}
    json_write(HERE / "probe_manifest.json", probe_manifest)
    cache_rows = [json.loads(x) for x in (PRIVATE / "compile_cache.jsonl").read_text(encoding="utf-8").splitlines()]
    summary = {"written_utc": utc(), "toolchain": {"lake": "~/.elan/bin/lake", "lake_sha256": sha_file(args.lake_bin), "lake_version": subprocess.check_output([str(args.lake_bin), "--version"], text=True).strip(), "project": "vb90_grading/lean_project", "lean_toolchain": (args.lake_project / "lean-toolchain").read_text().strip(), "lean_toolchain_sha256": sha_file(args.lake_project / "lean-toolchain"), "lake_manifest_sha256": sha_file(args.lake_project / "lake-manifest.json")},
               "unique_compilations": len(cache_rows), "ok": sum(r["ok"] for r in cache_rows), "failed": sum(not r["ok"] for r in cache_rows), "error_classes": {}, "private_cache_relpath": "private/probes_worker/compile_cache.jsonl", "source_manifest_sha256": sha_file(HERE / "source_manifest.json"), "probe_manifest_sha256": sha_file(HERE / "probe_manifest.json")}
    for receipt in cache_rows:
        cls = compile_reason(receipt)
        summary["error_classes"][cls] = summary["error_classes"].get(cls, 0) + 1
    json_write(HERE / "compile_summary.json", summary)
    print(json.dumps({"source": source_manifest["declared"], "probes": probe_manifest["counts"], "compile": {k: summary[k] for k in ("unique_compilations", "ok", "failed", "error_classes")}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
