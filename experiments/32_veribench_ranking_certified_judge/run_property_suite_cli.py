#!/usr/bin/env python3
"""Experiment 32 fallback: exp16-style property suite (P1 identity, P2 bug ladder, P3/P4 via repeats) for the
substitute judge configuration, through `codex exec` only.

Probe construction is the frozen Exp16 code, loaded by AST from the archived modules so that no module with a
provider client is imported:
  - experiments/archive/02_neurips_reviews/utils/variant_generator.py  (generate_variants: RENAME/REORDER/STYLE/ALPHA)
  - experiments/archive/02_neurips_reviews/utils/veribench_variance_utils.py (extract_theorem_blocks, build_bug_ladder)
Human-union pairs and the 24 unique problems are rebuilt exactly as exp16_multi_judge_human_sets.py does.
Every cell is one CLI call cached at results/property_raw/<row_type>__<item>__r<k>.json.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXP_DIR.parents[1]
sys.path.insert(0, str(EXP_DIR))
import run_ranking_cli as rr  # noqa: E402  (stdlib-only runner; provides run_codex_once, child_env, last_theorem_block)

RAW_DIR = EXP_DIR / "results" / "property_raw"
LOG_PATH = EXP_DIR / "results" / "property_run.log"
MANIFEST_PATH = EXP_DIR / "property_requests.json"
CONFIG_PATH = EXP_DIR / "judge_config.json"
V04 = REPO_ROOT / "experiments/archive/04_veribench_validation"
UTILS = REPO_ROOT / "experiments/archive/02_neurips_reviews/utils"
DATA = V04 / "data"
TSVS = {"pass1": DATA / "ethan_human_scores_20260425.tsv", "pass2": DATA / "ethan_human_scores_ORIGINAL.tsv",
        "avg": DATA / "ethan_human_scores_avg_two_passes_20260425.tsv"}
GOLD_ROOT = REPO_ROOT / "data/veribench_dataset/lean_src/veribench"
AGENTS_DIR = REPO_ROOT / "data/generated_agents"


def load_functions(path: Path, names: list[str]) -> dict:
    """Exec only the named top-level function defs of an archived module (no module import)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    wanted = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assigns = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("RENAME_MAP",) for t in n.targets)]
    module = ast.Module(body=assigns + wanted, type_ignores=[])
    ns = {"re": re, "List": list, "Dict": dict, "Tuple": tuple, "Sequence": list}
    exec(compile(module, str(path), "exec"), ns)  # noqa: S102 — archived, reviewed string-transform code only
    missing = [n for n in names if n not in ns]
    if missing:
        raise RuntimeError(f"{path}: missing {missing}")
    return ns


def build_requests() -> dict:
    vg = load_functions(UTILS / "variant_generator.py", ["_rename_variant", "_reorder_variant", "_style_variant", "_alpha_variant", "generate_variants"])
    vu = load_functions(UTILS / "veribench_variance_utils.py", ["extract_theorem_blocks", "_remove_last_theorem_block", "build_bug_ladder"])
    # exp16: union of the three label TSVs -> (gold_file, candidate_file) pairs
    union = set()
    labels = {}
    for name, p in TSVS.items():
        rows = {}
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                g, c, s = str(r.get("gold_file", "")).strip(), str(r.get("candidate_file", "")).strip(), str(r.get("human_score_0_5", "")).strip()
                if g and c and s:
                    rows.setdefault((g, c), []).append(float(s))
        labels[name] = {k: sum(v) / len(v) for k, v in rows.items()}
        union |= set(rows)
    idx = {}
    for p in GOLD_ROOT.rglob("*.lean"):
        idx.setdefault(p.name, []).append(p)
    human_rows, skipped, problems = [], [], {}
    for g, c in sorted(union):
        matches = idx.get(g, [])
        if not matches:
            skipped.append({"gold_file": g, "candidate_file": c, "reason": "missing_gold"}); continue
        gold_path = sorted(matches, key=lambda p: (len(p.parts), str(p)))[0]
        cand_path = AGENTS_DIR / c
        if not cand_path.exists():
            skipped.append({"gold_file": g, "candidate_file": c, "reason": "missing_candidate"}); continue
        gold_text = gold_path.read_text(encoding="utf-8", errors="ignore")
        gold_block = rr.last_theorem_block(gold_text)
        pkey = Path(g).stem
        human_rows.append({"row_type": "human_eval_union", "item_key": f"{g}::{c}", "problem_id": pkey,
                           "reference": gold_block, "candidate": cand_path.read_text(encoding="utf-8", errors="ignore"),
                           "gold_path": str(gold_path), "candidate_path": str(cand_path),
                           "human": {k: labels[k].get((g, c)) for k in TSVS}})
        problems.setdefault(pkey, gold_block)
    prop_rows = []
    for pkey, gold in problems.items():
        for v in vg["generate_variants"](gold):
            prop_rows.append({"row_type": "property_identity", "item_key": f"{pkey}::{v['variant_type']}", "problem_id": pkey,
                              "reference": gold, "candidate": v["code"]})
        for level, cand in enumerate(vu["build_bug_ladder"](gold)):
            prop_rows.append({"row_type": "property_bug", "item_key": f"{pkey}::L{level}", "problem_id": pkey,
                              "reference": gold, "candidate": cand})
    rows = human_rows + prop_rows
    for r in rows:
        r["cell_id"] = hashlib.sha256(f"{r['row_type']}|{r['item_key']}".encode()).hexdigest()[:16]
    return {"schema_version": "exp32_property_requests_v1", "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "source": "exp16_multi_judge_human_sets.py construction (union of pass1/pass2/avg TSVs; last theorem block of gold; generate_variants; build_bug_ladder)",
            "n_human_union": len(human_rows), "n_problems": len(problems), "n_identity": sum(r["row_type"] == "property_identity" for r in rows),
            "n_bug": sum(r["row_type"] == "property_bug" for r in rows), "n_rows": len(rows), "skipped_pairs": skipped, "rows": rows}


def cell_path(r: dict, rep: int) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", r["item_key"])
    return RAW_DIR / f"{r['row_type']}__{safe}__r{rep}.json"


def log(msg: str) -> None:
    line = f"{datetime.now(UTC).isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def score_cell(r: dict, rep: int, cfg: dict, template: str, retries: int, timeout: int) -> dict:
    out = cell_path(r, rep)
    prompt = template.format(reference_impl=r["reference"], generated_theorem=r["candidate"])
    attempts = []
    for attempt in range(1, retries + 1):
        try:
            res = rr.run_codex_once(prompt, cfg, timeout)
            rec = {"status": "ok", "row_type": r["row_type"], "item_key": r["item_key"], "problem_id": r["problem_id"], "repeat": rep,
                   "prompt_name": cfg["prompt_name"], "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                   "model_requested": cfg["model_requested_by_cli_flag"], "model_observed_header": res["observed_model_header"],
                   "models_observed_in_jsonl": res["observed_models_in_jsonl"], "reasoning_effort": cfg["reasoning_effort"],
                   "score": float(res["parsed"]["score"]), "reasoning": str(res["parsed"].get("reasoning", "")),
                   "attempt": attempt, "failed_attempts": attempts, "elapsed_seconds": res["elapsed_seconds"], "usage": res["usage"],
                   "benign_warnings": res.get("benign_warnings", []), "event_types": res["event_types"], "item_types": res["item_types"],
                   "cli_stderr_tail": res["stderr"][-2000:], "cli_stdout_jsonl": res["stdout"],
                   "finished_at": datetime.now(UTC).isoformat(timespec="seconds")}
            tmp = out.with_suffix(".json.tmp"); tmp.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"); tmp.replace(out)
            return rec
        except Exception as exc:  # noqa: BLE001
            detail = exc.args[1] if len(exc.args) > 1 and isinstance(exc.args[1], dict) else {}
            attempts.append({"attempt": attempt, "error": f"{type(exc).__name__}: {str(exc.args[0]) if exc.args else exc}"[:600],
                             "stderr_tail": str(detail.get("stderr", ""))[-600:], "stdout_tail": str(detail.get("stdout", ""))[-1500:]})
            log(f"RETRY {out.name} attempt {attempt} failed: {attempts[-1]['error'][:160]}")
            time.sleep(min(60, 5 * 2 ** (attempt - 1)))
    rec = {"status": "failed", "row_type": r["row_type"], "item_key": r["item_key"], "repeat": rep, "failed_attempts": attempts,
           "finished_at": datetime.now(UTC).isoformat(timespec="seconds")}
    out.with_suffix(".failed.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-only", action="store_true", help="write property_requests.json and exit (no inference)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()
    if args.workers > 8:
        raise SystemExit("parallelism cap is 8")
    manifest = build_requests()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"requests: human={manifest['n_human_union']} problems={manifest['n_problems']} identity={manifest['n_identity']} bug={manifest['n_bug']} rows={manifest['n_rows']} skipped={manifest['skipped_pairs']}")
    if args.build_only:
        return
    cfg = json.loads(CONFIG_PATH.read_text())
    template = rr.load_prompt_template(cfg["prompt_name"])
    jobs = [(r, rep) for rep in range(cfg["n_repeats"]) for r in manifest["rows"] if not rr.cell_is_done(cell_path(r, rep))]
    if args.limit:
        jobs = jobs[: args.limit]
    log(f"START property suite model={cfg['model_requested_by_cli_flag']} effort={cfg['reasoning_effort']} prompt={cfg['prompt_name']} pending={len(jobs)} total={manifest['n_rows'] * cfg['n_repeats']} workers={args.workers}")
    n_ok = n_fail = 0; t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(score_cell, r, rep, cfg, template, args.retries, args.timeout) for r, rep in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            rec = fut.result()
            if rec["status"] == "ok":
                n_ok += 1
                if i % 20 == 0 or i <= 3:
                    rate = i / (time.time() - t0)
                    log(f"PROGRESS {i}/{len(jobs)} ok={n_ok} fail={n_fail} {rate*60:.1f} cells/min eta={((len(jobs)-i)/rate)/60:.1f} min")
            else:
                n_fail += 1; log(f"FAILED {rec['row_type']} {rec['item_key']} r{rec['repeat']}")
    log(f"DONE property suite ok={n_ok} fail={n_fail} elapsed={(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
