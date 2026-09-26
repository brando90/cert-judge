"""Run the requested manuscript editor through the local subscription client."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--workspace", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
if "archive" in root.parts:
    raise SystemExit("This dispatch is archived. Register a new active experiment before new model work.")
logs = root / "logs"
logs.mkdir(exist_ok=True)
prompt_path = root / "PROMPT_astra_execution.md"
if not prompt_path.is_file():
    raise SystemExit("The consultation-dependent execution brief is missing.")
env = dict(os.environ)
for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
    env.pop(name, None)
command = [
    "/usr/local/bin/codex", "exec", "--dangerously-bypass-approvals-and-sandbox",
    "-m", "gpt-6-astra", "-c", 'model_reasoning_effort="ultra"',
    "--json", "--cd", str(args.workspace.resolve()),
    "--output-last-message", str(logs / "astra_final.md"), "-",
]
started = datetime.datetime.now().astimezone().isoformat()
with prompt_path.open() as prompt, (logs / "astra.jsonl").open("w") as out, (logs / "astra.stderr").open("w") as err:
    proc = subprocess.Popen(command, env=env, stdin=prompt, stdout=out, stderr=err)
    (logs / "astra_process.json").write_text(json.dumps({"pid": proc.pid, "started": started, "command": command}, indent=2) + "\n")
    code = proc.wait()
(logs / "astra_exit.json").write_text(json.dumps({"exit_code": code, "started": started, "ended": datetime.datetime.now().astimezone().isoformat()}, indent=2) + "\n")
