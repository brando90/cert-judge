#!/usr/bin/env python3
"""Experiment 32: score the four VeriBench agents with a certified-family judge via `codex exec` only.

No provider SDK, no HTTP client, no credential path. Every child process gets an
environment with all LLM API-key variables removed. Each (item, agent, repeat)
cell is one CLI call whose raw result is cached at
results/raw/<split>__<stem>__<agent>__r<k>.json, so the run is resumable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXP_DIR.parents[1]
RAW_DIR = EXP_DIR / "results" / "raw"
LOG_PATH = EXP_DIR / "results" / "run.log"
MANIFEST_PATH = EXP_DIR / "inputs_manifest.json"
CONFIG_PATH = EXP_DIR / "judge_config.json"
SCHEMA_PATH = EXP_DIR / "score_schema.json"
PROMPT_SOURCE = REPO_ROOT / "experiments/archive/02_neurips_reviews/utils/sensitivity_sweep.py"
THEOREM_BLOCK_RE = re.compile(
    r"(?ms)^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b.*?"
    r"(?=^[ \t]*(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\b|\Z)"
)
EXPLICIT_KEYS = {"ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "CODEX_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"}
_LOG_LOCK = threading.Lock()


def child_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in EXPLICIT_KEYS and not k.upper().endswith("_API_KEY")}
    assert not any(k.upper().endswith("_API_KEY") for k in env)
    return env


def load_prompt_template(name: str) -> str:
    """Read PROMPT_VARIANTS[name] from the frozen prompt source without importing it (it has API imports)."""
    import ast
    tree = ast.parse(PROMPT_SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if targets and any(isinstance(t, ast.Name) and t.id == "PROMPT_VARIANTS" for t in targets):
            variants = ast.literal_eval(node.value)
            return variants[name]
    raise KeyError(name)


def last_theorem_block(text: str) -> str:
    spans = [(m.start(), m.end()) for m in THEOREM_BLOCK_RE.finditer(text)]
    if not spans:
        return text
    s, e = spans[-1]
    block = text[s:e].strip()
    return block or text


def log(msg: str) -> None:
    line = f"{datetime.now(UTC).isoformat(timespec='seconds')} {msg}"
    with _LOG_LOCK:
        print(line, flush=True)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def cell_path(item: str, agent: str, rep: int) -> Path:
    return RAW_DIR / f"{item.replace('/', '__')}__{agent}__r{rep}.json"


def cell_is_done(p: Path) -> bool:
    if not p.exists():
        return False
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return False
    return d.get("status") == "ok" and isinstance(d.get("score"), (int, float))


def parse_last_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return json.loads(t)


def run_codex_once(prompt: str, cfg: dict, timeout: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="exp32-codex-") as tmp:
        root = Path(tmp)
        out_path = root / "last.json"
        argv = [
            "codex", "exec",
            "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
            "-C", str(root), "-s", "read-only", "--ephemeral", "--json", "--color", "never",
            "-m", cfg["model_requested_by_cli_flag"],
            "-c", f'model_reasoning_effort="{cfg["reasoning_effort"]}"',
            "--output-schema", str(SCHEMA_PATH),
            "-o", str(out_path),
            "-",
        ]
        t0 = time.time()
        completed = subprocess.run(argv, input=prompt, text=True, capture_output=True, timeout=timeout, check=False, env=child_env())
        elapsed = time.time() - t0
        result = {
            "argv": argv[:-1] + ["<stdin prompt>"],
            "returncode": completed.returncode,
            "elapsed_seconds": round(elapsed, 2),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        if completed.returncode != 0:
            raise RuntimeError(f"codex rc={completed.returncode}: {(completed.stderr or completed.stdout)[-400:]}", result)
        if not out_path.exists():
            raise RuntimeError("codex did not write --output-last-message", result)
        last = out_path.read_text(encoding="utf-8")
        result["last_message"] = last
        # Inspect JSONL events: forbid tool use, harvest any model/usage info.
        item_types: dict[str, int] = {}
        event_types: dict[str, int] = {}
        observed_models: set[str] = set()
        usage = None
        for line in completed.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            event_types[str(ev.get("type"))] = event_types.get(str(ev.get("type")), 0) + 1
            for key in ("model", "model_slug"):
                if isinstance(ev.get(key), str):
                    observed_models.add(ev[key])
            it = ev.get("item")
            if isinstance(it, dict):
                it_type = str(it.get("type"))
                item_types[it_type] = item_types.get(it_type, 0) + 1
                for key in ("model", "model_slug"):
                    if isinstance(it.get(key), str):
                        observed_models.add(it[key])
            if ev.get("type") == "turn.completed" and isinstance(ev.get("usage"), dict):
                usage = ev["usage"]
        forbidden = {k: v for k, v in item_types.items() if k not in {"agent_message", "reasoning", "error"}}
        error_items = []
        for line in completed.stdout.splitlines():
            try:
                ev = json.loads(line.strip())
            except Exception:
                continue
            it = ev.get("item")
            if isinstance(it, dict) and it.get("type") == "error":
                error_items.append(it)
            if ev.get("type") == "error":
                error_items.append(ev)
        result["error_items"] = error_items
        result.update({
            "event_types": event_types,
            "item_types": item_types,
            "forbidden_item_types": forbidden,
            "usage": usage,
            "observed_models_in_jsonl": sorted(observed_models),
        })
        m = re.search(r"(?m)^model:\s*(\S+)\s*$", completed.stdout + "\n" + completed.stderr)
        result["observed_model_header"] = m.group(1) if m else None
        benign = [e for e in error_items if str(e.get("message", "")).startswith("Skill descriptions were shortened")]
        real_errors = [e for e in error_items if e not in benign]
        result["benign_warnings"] = benign
        if real_errors:
            raise RuntimeError(f"codex error item: {json.dumps(real_errors)[:500]}", result)
        if forbidden:
            raise RuntimeError(f"codex attempted forbidden tool use: {forbidden}", result)
        parsed = parse_last_json(last)
        score = parsed.get("score")
        if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
            raise RuntimeError(f"invalid score in output: {last[:200]}", result)
        result["parsed"] = parsed
        return result


def score_cell(job: dict, cfg: dict, template: str, retries: int, timeout: int) -> dict:
    out = cell_path(job["item"], job["agent"], job["rep"])
    cand_text = Path(job["candidate_path"]).read_text(encoding="utf-8", errors="ignore")
    gold_text = Path(job["gold_path"]).read_text(encoding="utf-8", errors="ignore")
    reference = last_theorem_block(gold_text)
    prompt = template.format(reference_impl=reference, generated_theorem=cand_text)
    attempts = []
    for attempt in range(1, retries + 1):
        try:
            r = run_codex_once(prompt, cfg, timeout)
            rec = {
                "status": "ok",
                "item": job["item"], "agent": job["agent"], "split": job["split"], "repeat": job["rep"],
                "candidate_path": job["candidate_path"], "candidate_sha256": job["candidate_sha256"],
                "gold_path": job["gold_path"], "gold_sha256": job["gold_sha256"],
                "prompt_name": cfg["prompt_name"], "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "model_requested": cfg["model_requested_by_cli_flag"],
                "model_observed_header": r["observed_model_header"],
                "models_observed_in_jsonl": r["observed_models_in_jsonl"],
                "reasoning_effort": cfg["reasoning_effort"],
                "score": float(r["parsed"]["score"]), "reasoning": str(r["parsed"].get("reasoning", "")),
                "attempt": attempt, "failed_attempts": attempts,
                "elapsed_seconds": r["elapsed_seconds"], "usage": r["usage"], "benign_warnings": r.get("benign_warnings", []),
                "event_types": r["event_types"], "item_types": r["item_types"],
                "cli_stderr_tail": r["stderr"][-2000:], "cli_stdout_jsonl": r["stdout"],
                "finished_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            tmp = out.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            tmp.replace(out)
            return rec
        except subprocess.TimeoutExpired as exc:
            attempts.append({"attempt": attempt, "error": f"timeout after {timeout}s"})
        except RuntimeError as exc:
            detail = exc.args[1] if len(exc.args) > 1 and isinstance(exc.args[1], dict) else {}
            attempts.append({"attempt": attempt, "error": str(exc.args[0])[:600], "stderr_tail": str(detail.get("stderr", ""))[-600:],
                             "stdout_tail": str(detail.get("stdout", ""))[-1500:], "elapsed_seconds": detail.get("elapsed_seconds")})
        except Exception as exc:  # noqa: BLE001
            attempts.append({"attempt": attempt, "error": f"{type(exc).__name__}: {exc}"[:600]})
        log(f"RETRY {out.name} attempt {attempt} failed: {attempts[-1]['error'][:160]}")
        time.sleep(min(60, 5 * 2 ** (attempt - 1)))
    rec = {"status": "failed", "item": job["item"], "agent": job["agent"], "split": job["split"], "repeat": job["rep"],
           "failed_attempts": attempts, "finished_at": datetime.now(UTC).isoformat(timespec="seconds")}
    fail_path = out.with_suffix(".failed.json")
    fail_path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="only run the first N pending cells")
    ap.add_argument("--agents", default="", help="comma list to restrict agents")
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()
    if args.workers > 8:
        raise SystemExit("parallelism cap is 8")
    cfg = json.loads(CONFIG_PATH.read_text())
    manifest = json.loads(MANIFEST_PATH.read_text())
    template = load_prompt_template(cfg["prompt_name"])
    golds = {g["item"]: g for g in manifest["items"]}
    jobs = []
    for c in manifest["candidates"]:
        if args.agents and c["agent"] not in args.agents.split(","):
            continue
        for rep in range(cfg["n_repeats"]):
            if cell_is_done(cell_path(c["item"], c["agent"], rep)):
                continue
            g = golds[c["item"]]
            jobs.append({**c, "rep": rep, "gold_path": g["gold_path"], "gold_sha256": g["gold_sha256"]})
    # Order: repeat-major so an interrupted run leaves complete (all items x all agents) repeat layers;
    # items are shuffled with a fixed seed so every split/agent is covered evenly as the run proceeds.
    import random
    item_order = sorted({j["item"] for j in jobs})
    random.Random(0).shuffle(item_order)
    item_rank = {it: i for i, it in enumerate(item_order)}
    agent_rank = {a: i for i, a in enumerate(["baseline", "dspy_react", "trace_plus", "trace_plusplus"])}
    jobs.sort(key=lambda j: (j["rep"], item_rank[j["item"]], agent_rank.get(j["agent"], 99)))
    if args.limit:
        jobs = jobs[: args.limit]
    total = manifest["n_candidate_rows"] * cfg["n_repeats"]
    log(f"START model={cfg['model_requested_by_cli_flag']} effort={cfg['reasoning_effort']} prompt={cfg['prompt_name']} pending={len(jobs)} total_cells={total} workers={args.workers}")
    n_ok = n_fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(score_cell, j, cfg, template, args.retries, args.timeout): j for j in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            rec = fut.result()
            if rec["status"] == "ok":
                n_ok += 1
                if i % 20 == 0 or i <= 3:
                    rate = i / (time.time() - t0)
                    log(f"PROGRESS {i}/{len(jobs)} ok={n_ok} fail={n_fail} {rate*60:.1f} cells/min eta={((len(jobs)-i)/rate)/60:.1f} min")
            else:
                n_fail += 1
                log(f"FAILED {rec['item']} {rec['agent']} r{rec['repeat']}")
    log(f"DONE ok={n_ok} fail={n_fail} elapsed={(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
