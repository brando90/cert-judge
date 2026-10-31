"""E64: test for run_setN_judge.py with a fake vLLM (no GPU, no model calls): the non-dry path writes raw/setn/<model>/<P>.jsonl and a ledger line, resumes without regenerating, and stops on a damaged family file.
Needs python with transformers; env E58_VERIBENCH_REPO as for the driver. Run: python3 test_run_setN_judge.py <prompts-dir> <tokenizer-root>"""
import gzip, json, shutil, sys, tempfile, types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_setN_judge as D


class FakeOut:
    def __init__(self):
        self.outputs = [types.SimpleNamespace(text="FAKE", token_ids=[1, 2], finish_reason="stop")]


class FakeParams(types.SimpleNamespace):
    def clone(self):
        return FakeParams(**vars(self))


class FakeLLM:
    calls = 0
    def __init__(self, **kw): pass
    def get_default_sampling_params(self):
        return FakeParams(temperature=0.6, top_p=0.95, top_k=20, min_p=0.0, repetition_penalty=1.0)
    def get_tokenizer(self):
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(str(TOK / "qwen3_4b"))
    def generate(self, prompts, params, use_tqdm=False):
        FakeLLM.calls += len(prompts)
        return [FakeOut() for _ in prompts]


prompts_dir, TOK = Path(sys.argv[1]), Path(sys.argv[2])
vllm, inputs = types.ModuleType("vllm"), types.ModuleType("vllm.inputs")
vllm.LLM, vllm.SamplingParams, inputs.TokensPrompt = FakeLLM, FakeParams, dict
sys.modules.update({"vllm": vllm, "vllm.inputs": inputs})
tmp = Path(tempfile.mkdtemp())
argv = ["x", "--run", str(tmp / "run"), "--prompts-dir", str(prompts_dir), "--weights-root", str(TOK), "--model", "qwen3_4b", "--prompts", "H2,D0", "--limit-cells", "4"]
sys.argv = argv
assert D.main() == 0
raw = tmp / "run/raw/setn/qwen3_4b/H2.jsonl"
rows = [json.loads(l) for l in open(raw)]
assert len(rows) == 4 and {r["status"] for r in rows} <= {"generated", "unmeasured_over_context"}, rows   # the smoke subset always holds the longest prompt
assert all(r["text"].endswith("FAKE") for r in rows if r["status"] == "generated") and any(r["status"] == "generated" for r in rows)
assert len(open(tmp / "run/ledger.jsonl").readlines()) == 2
n = FakeLLM.calls
assert D.main() == 0 and FakeLLM.calls == n, "a rerun must not regenerate finished cells"
# damaged family file stops before any unit
bad = tmp / "bad"; (bad / "families").mkdir(parents=True)
for p in (prompts_dir / "families").glob("*.gz"):
    shutil.copy(p, bad / "families" / p.name)
with open(bad / "families/H2.jsonl.gz", "ab") as fh:
    fh.write(b"x")
sys.argv = ["x", "--run", str(tmp / "r2"), "--prompts-dir", str(bad), "--weights-root", str(TOK), "--model", "qwen3_4b", "--prompts", "H2"]
try:
    D.main(); raise AssertionError("damaged file must stop")
except SystemExit as e:
    assert "STOP" in str(e.code)
print("ok")
