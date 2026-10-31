#!/usr/bin/env python3
"""E64: render the set-N packet (v7, 125 files) into all nine E39 prompt families (D0 R4 H0 H1 H2 P1 P4 P8 LEX) the way E58 rendered them, no model calls.
Same route as E58's `rebuild_prompts.render_cells`: VeriBench families through experiment 100's `prompts.render` (E39 `x100_modules`), legacy families through E39's `legacy.render`
(reference = the gold's last theorem block); a D0 extraction refusal or an empty obligation list becomes the same non-call status E58 gives it. Prompt hash = E39's `sha256(system + "\\n\\n" + user)`.
Modes (all read no rating; the packet has none):
  check  : renders all 75 E39 criterion items in all nine families and compares status and prompt sha256 with E39's committed cells (results/cells/*__<prompt>.json, the hashes E58's rebuild
           matched 4689/4689) and with E58's own `render_cells` on the same items; also re-renders the old E63 test items' H2 prompt prefix against render_setN.py's (answer instruction aside).
  render : packet -> <out>/families/<P>.jsonl.gz (private, not committed) and <out>/FAMILIES_MANIFEST.json (sha256 of every prompt, status counts: the committed part).
  hours  : GPU-hour estimate from the plan's call and token counts with E58's assumed throughputs (GPU_HOURS.md; assumptions, not measurements).
  plan   : tokenizes the rendered prompts through each of E58's 13 models' own chat template (tokenizer files only) and applies E58's frozen over-context rule
           (budget = min(prompt max_tokens, max_model_len - prompt tokens) < 1024 -> unmeasured_over_context); writes counts and token totals (no prompt text).
Needs python3 with numpy and (plan only) transformers (e.g. ~/.venvs/l32/bin/python), this repo (E39, E58 scripts), the VeriBench clone E58 rebuilt from (--veribench: E58's VB_REPO,
the clone whose experiment 100 inputs match E39's committed hashes) and the packet.
  python3 render_setN_families.py check  --veribench ~/veribench_e58
  python3 render_setN_families.py render --veribench ~/veribench_e58 --packet <...>/human_round/sample_setN/packet --out setN_prompts
  python3 render_setN_families.py plan   --out setN_prompts --tokenizers <dir with one folder per E58 model key> --report results/RUN_PLAN_setN_E58_<date>.json"""
import argparse, hashlib, json, os, statistics, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
E58_SCRIPTS = next((REPO / "experiments").glob("58_*")) / "scripts"
sha = lambda b: hashlib.sha256(b).hexdigest()
ANSWER_NEW = ("Answer with ONLY one digit, 0 to 5: your final_score_0_5 (the final score after the spam adjustment). "
              "No other text.")                       # render_setN.py / E63: only used for the H2 prefix cross-check


def load_e58(veribench):
    os.environ["E58_VERIBENCH_REPO"] = str(Path(veribench).resolve())
    sys.path[:0] = [str(E58_SCRIPTS)]
    import e58, rebuild_prompts                                       # noqa: E401
    e39, _, legacy = e58.e39_modules()
    _, prompts_mod, _ = e39.x100_modules()
    return e58, rebuild_prompts, e39, legacy, prompts_mod


def render_family(e39, legacy, prompts_mod, key, item, cand_text, cand_name, gold_text):
    """One cell's (status, value, reason, system, user): E58 `render_cells`' branch for a single probe, unchanged."""
    unit = e39.PROMPTS[key]
    status, value, reason, system, user = "render", None, "", None, None
    if unit["family"] == "legacy":
        system, user = legacy.render(unit["rubric"], gold_text, cand_text)
    else:
        try:
            system, user = prompts_mod.render(unit["rubric"], item, cand_text, cand_name)
        except prompts_mod.Unmeasured as exc:
            msg = str(exc)
            if msg.startswith("no_candidate_obligations"):
                status, value, reason = "deterministic", 0.0, "deployed scorer assigns 0.0 without a call: no candidate obligations"
            elif msg.startswith("no_reference_obligations"):
                status, value, reason = "deterministic", 1.0, "deployed scorer assigns 1.0 without a call: no reference obligations"
            else:
                status, reason = "unmeasured_extraction", msg[:200]
    return status, value, reason, system, user


def check(a):
    e58, rp, e39, legacy, prompts_mod = load_e58(a.veribench)
    items = e39.load_items()
    rd = lambda p: Path(p).read_text(encoding="utf-8", errors="replace")
    rebuilt = {}                                               # E58's own route needs a `rebuilt` dict (crit kind: the candidate file as is)
    for it in items:
        pid = f"crit__{it['item']}__L0"
        rebuilt[pid] = dict(kind="crit", key=it["item"], task=it["task"], item=it["item"], level=0, sha256=e58.sha(rd(it["candidate_path_abs"]).encode()),
                            code=rd(it["candidate_path_abs"]), base_item=it, candidate_name=it["candidate_file"], sha_match=True)
    tot, bad, per = 0, [], {}
    for key in e58.PROMPT_ORDER:
        _, committed = rp.committed_cells("e39", key)
        e58_cells = {c["cell"]: c for c in rp.render_cells("e39", key, rebuilt, lambda kind: 1)}
        n_ok, n_stat = 0, Counter()
        for it in items:
            cell = f"crit__{it['item']}__L0__r1"
            status, value, reason, system, user = render_family(e39, legacy, prompts_mod, key, it, rd(it["candidate_path_abs"]), it["candidate_file"],
                                                                 rd(it["ref_ann_path_abs"]))
            got = dict(status=status, prompt_sha256=e58.prompt_sha(system, user) if status == "render" else None, score=value)
            c, r = e58_cells[cell], committed[cell]
            ok = (got["status"] == r["status"] == c["status"] and (got["prompt_sha256"] == r.get("prompt_sha256") == c.get("prompt_sha256"))
                  and got["score"] == r.get("score") == c.get("score"))
            n_stat[status] += 1; tot += 1; n_ok += ok
            if not ok:
                bad.append((key, it["item"], got["status"], r["status"], c["status"]))
        per[key] = dict(identical=n_ok, of=len(items), statuses=dict(n_stat))
    print(json.dumps(dict(veribench=str(a.veribench), items_sha256=e58.sha_file(e39.X100 / "inputs/items.jsonl"), per_family=per,
                          total_identical=tot - len(bad), total=tot, failures=bad[:10]), indent=1))
    sys.exit(1 if bad else 0)


def packet_items(packet):
    folders = sorted(p for p in Path(packet).iterdir() if p.is_dir() and p.name.startswith("N"))
    for f in folders:
        gold = sorted((f / "gold_lean").glob("*.lean")); py = sorted((f / "python_source").glob("*.py"))
        assert len(gold) == 1 and len(py) == 1, f
        for cand in sorted((f / "agent_lean").glob("*.lean")):
            yield f, gold[0], py[0], cand


def render(a):
    e58, rp, e39, legacy, prompts_mod = load_e58(a.veribench)
    packet, out = Path(a.packet).resolve(), Path(a.out)
    (out / "families").mkdir(parents=True, exist_ok=True)
    rows = {k: [] for k in e58.PROMPT_ORDER}
    for f, gold, py, cand in packet_items(packet):
        ct, gt = (p.read_text(encoding="utf-8", errors="replace") for p in (cand, gold))
        item = dict(task=f.name, ref_ann_path=str(gold), ref_snap_path=str(gold), py_ann_path=str(py), gold_file_name=gold.name)
        for key in e58.PROMPT_ORDER:
            status, value, reason, system, user = render_family(e39, legacy, prompts_mod, key, item, ct, cand.name, gt)
            row = dict(cell=cand.stem, item=cand.stem, folder=f.name, status=status, candidate_sha256=sha(cand.read_bytes()))
            if status == "render":
                row.update(prompt_sha256=e58.prompt_sha(system, user), system=system, user=user)
            elif status == "deterministic":
                row.update(score=value, reason=reason)
            else:
                row.update(reason=reason)
            rows[key].append(row)
    man = dict(n_files=len(rows["H2"]), packet_files_sha256=sha((packet / "FILES.sha256").read_bytes()), items_sha256=e58.sha_file(e39.X100 / "inputs/items.jsonl"),
               veribench_repo_head=a.veribench_head, families={})
    for key, rs in rows.items():
        assert len(rs) == 125, (key, len(rs))
        path = out / "families" / f"{key}.jsonl.gz"
        e58.write_jsonl_gz(path, rs)
        man["families"][key] = dict(rubric=e39.PROMPTS[key]["rubric"], file_sha256=e58.sha_file(path), statuses=dict(Counter(r["status"] for r in rs)),
                                    prompt_sha256={r["item"]: r.get("prompt_sha256") for r in rs})
    # H2 cross-check against render_setN.py's frozen H2 (same text up to the answer instruction): reported, not asserted, because the two routes use different checkouts
    if a.h2_existing:
        old = {}
        for l in open(a.h2_existing):
            r = json.loads(l); old[r["item"]] = r
        same = 0
        for r in rows["H2"]:
            o = old[r["item"]]; k = r["system"].rfind("Answer with ONLY one JSON object")
            same += (r["user"] == o["user"] and r["system"][:k] == o["system"][:o["system"].rfind(ANSWER_NEW)])
        man["h2_prefix_vs_render_setN"] = dict(identical=same, of=125)
    (out / "FAMILIES_MANIFEST.json").write_text(json.dumps(man, indent=1))
    print(json.dumps({k: (v if k != "families" else {f: dict(file_sha256=d["file_sha256"], statuses=d["statuses"]) for f, d in v.items()}) for k, v in man.items()}, indent=1))


def plan(a):
    e58, rp, e39, legacy, prompts_mod = load_e58(a.veribench)
    from transformers import AutoTokenizer
    fam = {k: e58.read_jsonl(Path(a.out) / "families" / f"{k}.jsonl.gz") for k in e58.PROMPT_ORDER}
    rec = dict(rule=f"budget = min(prompt max_tokens, max_model_len - prompt tokens); budget < {e58.MIN_GENERATION_BUDGET} -> unmeasured_over_context", models={})
    chat_ids = lambda tok, s, u, kw: tok.encode(tok.apply_chat_template([{"role": "system", "content": s}, {"role": "user", "content": u}], tokenize=False,
                                                                        add_generation_prompt=True, **kw), add_special_tokens=False)
    cache = {}                                                 # models whose tokenizer and chat-template files are byte-identical share one tokenization
    for mk in e58.MODEL_ORDER:
        m = e58.MODELS[mk]; tdir = Path(a.tokenizers) / mk
        fkey = sha(b"".join((tdir / f).read_bytes() for f in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja") if (tdir / f).exists())
                   + json.dumps(m.get("chat_kwargs", {}), sort_keys=True).encode())
        if fkey not in cache:
            tok = AutoTokenizer.from_pretrained(str(tdir))
            cache[fkey] = {key: {r["item"]: len(chat_ids(tok, r["system"], r["user"], m.get("chat_kwargs", {}))) for r in fam[key] if r["status"] == "render"}
                           for key in e58.PROMPT_ORDER}
        per = {}
        for key in e58.PROMPT_ORDER:
            n = cache[fkey][key]
            mt = e39.PROMPTS[key]["max_tokens"]
            over = sorted(i for i, x in n.items() if min(mt, m["max_model_len"] - x) < e58.MIN_GENERATION_BUDGET)
            det = sum(1 for r in fam[key] if r["status"] == "deterministic")      # carry a score without a call, count as scored (E39 coverage rule)
            ext = sum(1 for r in fam[key] if r["status"] == "unmeasured_extraction")
            per[key] = dict(calls=len(n) - len(over), over_context=len(over), over_context_items=over, deterministic_cells=det, unmeasured_extraction_cells=ext,
                            prompt_tokens_total=sum(n.values()), prompt_tokens_max=max(n.values()) if n else 0,
                            prompt_tokens_median=round(statistics.median(n.values())) if n else 0,
                            scored_share=round((len(n) - len(over) + det) / 125, 4), over_context_tokens=sum(n[i] for i in over))
        rec["models"][mk] = dict(max_model_len=m["max_model_len"], gpus=m["gpus"], configs=per, calls=sum(v["calls"] for v in per.values()),
                                 prompt_tokens_total_scored=sum(v["prompt_tokens_total"] - v["over_context_tokens"] for v in per.values()),
                                 units_below_90pct=[k for k, v in per.items() if v["scored_share"] + 1e-9 < 0.9])
        print(json.dumps({mk: {k: (m_["calls"], m_["over_context"]) for k, m_ in per.items()}}), flush=True)
    rec["calls_total"] = sum(v["calls"] for v in rec["models"].values())
    Path(a.report).write_text(json.dumps(rec, indent=1))


# E58 GPU_HOURS.md assumptions per model: (decode tok/s, prefill tok/s, mean output tokens per call), GPUs from e58.MODELS
THROUGHPUT = {"qwen3_4b": (5000, 30000, 3500), "qwen3_8b": (3200, 18000, 3500), "qwen3_14b": (1900, 10000, 3500), "qwen3_32b": (1500, 9000, 3500),
              "qwen36_27b": (1700, 9500, 4500), "llama31_8b": (3500, 18000, 350), "llama33_70b_awq": (900, 5500, 350), "gemma3_4b": (4500, 28000, 350),
              "gemma3_12b": (2300, 13000, 350), "gemma3_27b": (1500, 8000, 350), "olmo3_7b": (3300, 19000, 5000), "olmo3_32b": (1400, 8500, 5000),
              "gpt_oss_20b": (4200, 16000, 2500)}


def hours(a):
    rec = json.loads(Path(a.report).read_text())
    out, tot = {}, 0.0
    for mk, m in rec["models"].items():
        dec, pre, mo = THROUGHPUT[mk]
        h = m["calls"] * mo / dec / 3600 + m["prompt_tokens_total_scored"] / pre / 3600       # wall hours, one replica
        out[mk] = dict(calls=m["calls"], prompt_tokens_M=round(m["prompt_tokens_total_scored"] / 1e6, 2), gpus=m["gpus"], wall_h=round(h, 1), gpu_h=round(h * m["gpus"], 1))
        tot += h * m["gpus"]
    rec["hours"] = dict(assumption="E58 GPU_HOURS.md throughputs and mean output tokens, calls and prompt tokens from this plan; not measured", per_model=out, gpu_h_total=round(tot, 1))
    Path(a.report).write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec["hours"], indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=["check", "render", "plan", "hours"])
    ap.add_argument("--veribench", required=False, help="VeriBench clone E58 rebuilt from (E58_VERIBENCH_REPO)")
    ap.add_argument("--veribench-head", default="", help="its git HEAD, recorded in the manifest")
    ap.add_argument("--packet"); ap.add_argument("--out", default="setN_prompts")
    ap.add_argument("--h2-existing", help="setN_prompts/h2.jsonl from render_setN.py, for the H2 prefix cross-check")
    ap.add_argument("--tokenizers"); ap.add_argument("--report", default="RUN_PLAN.json")
    a = ap.parse_args()
    if a.mode != "hours" and not a.veribench:
        ap.error("--veribench is required for check, render and plan")
    dict(check=check, render=render, plan=plan, hours=hours)[a.mode](a)
