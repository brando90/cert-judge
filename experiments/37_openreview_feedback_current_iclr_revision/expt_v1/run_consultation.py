"""Run the requested local subscription client and preserve private receipts."""
from pathlib import Path
import datetime, json, os, subprocess
repo = Path(__file__).resolve().parents[3]
root = Path(__file__).resolve().parent
logs = root / "logs"
logs.mkdir(exist_ok=True)
env = dict(os.environ)
for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDECODE"):
    env.pop(name, None)
command = [str(Path.home()/".local/bin/claude"), "-p", "--dangerously-skip-permissions", "--model", "claude-fable-5-1", "--effort", "max", "--output-format", "stream-json", "--verbose", "--max-turns", "48"]
started = datetime.datetime.now().astimezone().isoformat()
with (root/"PROMPT_claude_assessment.md").open() as prompt, (logs/"claude_fable.jsonl").open("w") as out, (logs/"claude_fable.stderr").open("w") as err:
    proc = subprocess.Popen(command, cwd=repo, env=env, stdin=prompt, stdout=out, stderr=err)
    (logs/"claude_fable_process.json").write_text(json.dumps({"pid":proc.pid,"started":started,"command":command,"cwd":str(repo)},indent=2)+"\n")
    code = proc.wait()
(logs/"claude_fable_exit.json").write_text(json.dumps({"exit_code":code,"started":started,"ended":datetime.datetime.now().astimezone().isoformat()},indent=2)+"\n")
