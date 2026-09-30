#!/usr/bin/env python3
"""TLDR: Emit experiment 39's Valkyrie judge task packs, one pack per judge model, in experiment 103's task-file
format (stamp line, `vb103-judge-cell` JSON header, system and user prompts between markers, a path-only
test.sh) so its validated `vb103_judge` agent can deliver the frozen prompt bytes; the header records the
TRUE rubric of each cell. Every task file is round-tripped through the agent's own parser. Zero model calls."""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402

PACK_ROOT = e39.PRIVATE / "packs"
STAMP_LINE = "<!-- VeriBench agent-spec v6: experiment 103 judge transport task, not a solver task -->"
SYS_BEGIN, SYS_END = "=== VB103_JUDGE_SYSTEM_BEGIN ===", "=== VB103_JUDGE_SYSTEM_END ==="
USER_BEGIN, USER_END = "=== VB103_JUDGE_USER_BEGIN ===", "=== VB103_JUDGE_USER_END ==="
OUTPUT_PATH = "/home/user/lean_project/Veribench/JudgeVerdict.lean"
MARKERS = (SYS_BEGIN, SYS_END, USER_BEGIN, USER_END, "vb103-judge-cell")
TEST_SH = ('#!/usr/bin/env bash\n'
           '# TLDR: Path declaration for an experiment 39 judge transport task; the service reads only the\n'
           '# SOLUTION_FILE line and never executes this file (the verdict is parsed on the host).\n'
           f'SOLUTION_FILE="{OUTPUT_PATH}"\n'
           'echo "experiment 39 judge transport: the verdict is parsed on the host" >&2\n'
           'exit 0\n')
SMOKE_ITEM_INDEX = 0          # the first crit cell (sorted) of every config is duplicated as the spare smoke cell
AGENT_STAMP_LINE = "<!-- VeriBench agent-spec v6: experiment 39 agent-judge task; the agent writes one verdict file -->"
AGENT_PREAMBLE = (
    "# Judging task\n\n"
    "You are acting as the judge described in the JUDGE INSTRUCTIONS below. Read the instructions and the MATERIAL TO JUDGE, "
    "then produce the verdict exactly in the format the instructions require (one JSON object, no markdown fences).\n\n"
    f"Write that JSON object, and nothing else, to the file `{OUTPUT_PATH}` (create the parent directories if they do not "
    "exist). Do not create, modify or delete any other file. Do not try to install software, reach the network, or compile "
    "anything; everything you need is in this task. When the file is written, you are done.\n\n"
)


def agent_task_file(cell: str, item: str | None, repeat: int, kind: str, rubric: str, system: str, user: str) -> str:
    """The agent-judge flavor: the same header and the same frozen prompt bytes between the same markers, wrapped in a
    plain task statement telling the agent to write the verdict file (its harness delivers this whole file as the task)."""
    for text, what in ((system, "system"), (user, "user")):
        for marker in MARKERS:
            assert marker not in text, f"{cell}: the {what} prompt contains the marker {marker!r}"
    header = {"cell": cell, "item": item, "repeat": repeat, "kind": kind, "rubric": rubric, "output_path": OUTPUT_PATH,
              "flavor": "agent", "system_sha256": e39.sha(system.encode()), "user_sha256": e39.sha(user.encode()),
              "prompt_sha256": e39.sha((system + "\n\n" + user).encode())}
    return (AGENT_STAMP_LINE + "\n" + "<!-- vb103-judge-cell: " + json.dumps(header, sort_keys=True) + " -->\n"
            + AGENT_PREAMBLE + "## JUDGE INSTRUCTIONS\n\n" + SYS_BEGIN + "\n" + system + "\n" + SYS_END + "\n\n"
            + "## MATERIAL TO JUDGE\n\n" + USER_BEGIN + "\n" + user + "\n" + USER_END + "\n")


def task_id_of(prefix: str, prompt_key: str, cell: str) -> str:
    return f"{prefix}__{prompt_key}__{cell}".replace("-", "_")


def task_file(cell: str, item: str | None, repeat: int, kind: str, rubric: str, system: str, user: str) -> str:
    for text, what in ((system, "system"), (user, "user")):
        for marker in MARKERS:
            assert marker not in text, f"{cell}: the {what} prompt contains the marker {marker!r}"
    header = {"cell": cell, "item": item, "repeat": repeat, "kind": kind, "rubric": rubric, "output_path": OUTPUT_PATH,
              "system_sha256": e39.sha(system.encode()), "user_sha256": e39.sha(user.encode()),
              "prompt_sha256": e39.sha((system + "\n\n" + user).encode())}
    return (STAMP_LINE + "\n" + "<!-- vb103-judge-cell: " + json.dumps(header, sort_keys=True) + " -->\n"
            + SYS_BEGIN + "\n" + system + "\n" + SYS_END + "\n" + USER_BEGIN + "\n" + user + "\n" + USER_END + "\n")


def emit(pack: Path, task_id: str, cell: dict, rubric: str, blob: dict, flavor: str = "transport") -> dict:
    maker = agent_task_file if flavor == "agent" else task_file
    body = maker(cell["cell"], cell.get("item") or cell.get("key"), cell["repeat"], cell["kind"], rubric, blob["system"], blob["user"])
    directory = pack / task_id
    (directory / "tests").mkdir(parents=True, exist_ok=True)
    (directory / "instruction.md").write_text(body)
    (directory / "tests/test.sh").write_text(TEST_SH)
    return {"task_id": task_id, "cell": cell["cell"], "kind": cell["kind"], "key": cell["key"], "task": cell["task"],
            "item": cell["item"], "level": cell["level"], "repeat": cell["repeat"], "prompt_sha256": cell["prompt_sha256"],
            "instruction_sha256": e39.sha(body.encode()), "instruction_bytes": len(body.encode())}


def build_model_pack(model_key: str, units: list[dict], seed: int) -> dict:
    pack = PACK_ROOT / model_key
    if pack.exists():
        shutil.rmtree(pack)
    per_config = {}
    for unit in units:
        cells_blob = e39.read_json(e39.RESULTS / "cells" / (unit["config"].replace("|", "__") + ".json"))
        cell_dir = e39.PRIVATE / "cells" / unit["config"].replace("|", "__")
        rendered = [c for c in cells_blob["cells"] if c["status"] == "render"]
        order = list(range(len(rendered)))
        random.Random(f"{seed}|{unit['config']}").shuffle(order)            # admission permutation per config
        main_rows = []
        for queue_index, i in enumerate(order):
            cell = rendered[i]
            blob = e39.read_json(cell_dir / f"{cell['cell']}.json")
            if e39.sha((blob["system"] + "\n\n" + blob["user"]).encode()) != cell["prompt_sha256"]:
                raise AssertionError(f"{unit['config']}/{cell['cell']}: rendered bytes do not match the manifest hash")
            row = emit(pack, task_id_of("cj39", unit["prompt_key"], f"q{queue_index:05d}__{cell['cell']}"), cell, unit["rubric"], blob,
                       unit["pack_flavor"])
            main_rows.append({**row, "queue_index": queue_index})
        smoke_rows = []
        crit_cells = sorted((c for c in rendered if c["kind"] == "crit" and c["repeat"] == 1), key=lambda c: c["cell"])
        if crit_cells:
            cell = crit_cells[SMOKE_ITEM_INDEX]
            blob = e39.read_json(cell_dir / f"{cell['cell']}.json")
            smoke_rows.append(emit(pack, task_id_of("smoke", unit["prompt_key"], cell["cell"]), dict(cell, repeat=1), unit["rubric"], blob,
                                   unit["pack_flavor"]))
        per_config[unit["config"]] = {"rubric": unit["rubric"], "prompt_key": unit["prompt_key"], "flavor": unit["pack_flavor"],
                                      "harness": unit["harness"], "n_tasks": len(main_rows),
                                      "n_smoke_tasks": len(smoke_rows), "cells": main_rows, "smoke_cells": smoke_rows,
                                      "max_instruction_bytes": max((r["instruction_bytes"] for r in main_rows), default=0)}
    return {"model_key": model_key, "pack": str(pack), "benchmark": f"certjudge39-{model_key}", "per_config": per_config,
            "n_tasks_total": sum(v["n_tasks"] + v["n_smoke_tasks"] for v in per_config.values())}


def parse_agent_task_file(text: str) -> tuple[dict, str, str]:
    """Recover header and prompt bytes from an agent-flavor task file (same markers as the transport flavor)."""
    match = re.search(r"^<!-- vb103-judge-cell: (?P<json>\{.*\}) -->$", text, re.M)
    assert match, "no vb103-judge-cell header"
    header = json.loads(match.group("json"))

    def between(begin: str, end: str) -> str:
        open_marker, close_marker = begin + "\n", "\n" + end
        assert text.count(open_marker) == 1 and text.count(close_marker) == 1
        start = text.index(open_marker) + len(open_marker)
        stop = text.index(close_marker)
        assert stop > start
        return text[start:stop]
    return header, between(SYS_BEGIN, SYS_END), between(USER_BEGIN, USER_END)


def round_trip(pack_dir: Path, rows: list[dict], flavor: str = "transport") -> list[str]:
    if flavor == "agent":
        parse = parse_agent_task_file
    else:
        _, judge_call = e39.x103_judge_pack()
        parse = judge_call.parse_task_file
    failures = []
    for row in rows:
        body = (pack_dir / row["task_id"] / "instruction.md").read_text()
        header, system, user = parse(body)
        if (e39.sha(system.encode()) != header["system_sha256"] or e39.sha(user.encode()) != header["user_sha256"]
                or e39.sha((system + "\n\n" + user).encode()) != row["prompt_sha256"] or header["output_path"] != OUTPUT_PATH):
            failures.append(row["task_id"])
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, default=e39.RESULTS / "panel.json")
    ap.add_argument("--models", default="", help="comma list of model keys (default: all)")
    ap.add_argument("--skip-round-trip", action="store_true", help="local dry runs without the experiment 103 checkout")
    args = ap.parse_args()
    panel = e39.read_json(args.panel)
    units = [u for u in panel["units"] if u["kind"] == "llm"]
    wanted = set(args.models.split(",")) if args.models else {u["model_key"] for u in units}
    receipt = {"written_utc": e39.stamp(), "seed": e39.SEED, "output_path": OUTPUT_PATH,
               "format": "experiment 103 scripts/judge_pack.py task-file layout, re-emitted with the true rubric in the header",
               "packs": {}}
    for model_key in sorted(wanted):
        blob = build_model_pack(model_key, [u for u in units if u["model_key"] == model_key], e39.SEED)
        if not args.skip_round_trip:
            for cfg, info in blob["per_config"].items():
                info["round_trip_failures"] = round_trip(Path(blob["pack"]), info["cells"] + info["smoke_cells"], info["flavor"])
        receipt["packs"][model_key] = blob
    receipt["verdict"] = "PASS" if all(not info.get("round_trip_failures") for p in receipt["packs"].values() for info in p["per_config"].values()) else "FAIL"
    e39.write_json(e39.RESULTS / "packs.json", receipt)
    print(json.dumps({m: {"n_tasks_total": p["n_tasks_total"], "configs": {c: v["n_tasks"] for c, v in p["per_config"].items()}}
                      for m, p in receipt["packs"].items()} | {"verdict": receipt["verdict"]}, indent=1))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
