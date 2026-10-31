#!/usr/bin/env python3
"""E64: render the set-N packet (v7, 25 folders x 5 agent files = 125 files) into the frozen judge prompts, no model calls.
Two prompts per file: the E39 H2 prompt with the one-digit answer instruction (judges A and B, candidates trained in E63) and the
judge-validation `checklist` prompt (judge C). Use `check` before `render`: it must reproduce, byte for byte, the 30 old E63 test
items' stored H2 prompts (pack_test.jsonl; the pack's own pid = sha256(system + NUL + user)[:16] is recomputed) and the jv
checklist renderer on the same 30 items. Reads no rating (the packet has none); takes no thresholds.

Needs python3 with numpy (jv imports it), two VeriBench checkouts (--veribench: docs/judge-validation; --x100-repo: the commit E39
rendered from, d7d36c319dc7, because later commits edited experiment 100's reference files and the rater instructions) and, for
`check`, the E63 pack_test.jsonl (SNAP: /dfs/scratch0/brando9/e62/pack_test.jsonl, sha256 in results/pack_manifest.json of E63).
  python3 render_setN.py check  --veribench ~/veribench --x100-repo ~/veribench_e39 --pack pack_test.jsonl
  python3 render_setN.py render --veribench ~/veribench --x100-repo ~/veribench_e39 --packet <...>/human_round/sample_setN/packet --out setN_prompts
render writes setN_prompts/{h2,checklist,pack_setN}.jsonl (system, user per item; pack_setN is the E63 sft_lora --eval_pack format; private, not committed), setN_items.jsonl (jv items format,
no ratings) and PROMPTS_MANIFEST.json (sha256 of every prompt, counts, source hashes: the committed part)."""
import argparse, glob, hashlib, json, sys
from pathlib import Path

ANSWER_NEW = ("Answer with ONLY one digit, 0 to 5: your final_score_0_5 (the final score after the spam adjustment). "
              "No other text.")                       # identical to E63 build_pack.py
RUBRIC = "H2_human_mirror_conventions_demos"
sha = lambda b: hashlib.sha256(b).hexdigest()


def load_modules(vb, x100_repo):
    vb, x100_repo = Path(vb).resolve(), Path(x100_repo).resolve()
    x100 = glob.glob(str(x100_repo / "experiments/100_*/scripts"))[0]
    sys.path[:0] = [x100, str(vb / "docs/judge-validation/code")]
    import prompts as x100_prompts           # experiment 100's frozen renderer (what E39 imported)
    from jv import prompts as jv_prompts, data as jv_data
    return x100_prompts, jv_prompts, jv_data


def render_h2(x100_prompts, item, cand_text, cand_name):
    """E39 H2 render, then E63's swap of the final answer instruction for the one-digit one."""
    system, user = x100_prompts.render(RUBRIC, item, cand_text, cand_name)
    k = system.rfind("Answer with ONLY one JSON object")
    assert k > 0
    return system[:k] + ANSWER_NEW, user


def render_checklist(jv_prompts, jv_data, py, ref, cand, py_name, ref_name, cand_name):
    it = jv_data.Item(item="x", task="x", agent="x", split="test", py=py, ref=ref, cand=cand,
                      py_name=py_name, ref_name=ref_name, cand_name=cand_name)
    return jv_prompts.render("checklist", it)


def old_items(x100_repo):
    x100 = Path(glob.glob(str(Path(x100_repo).resolve() / "experiments/100_*"))[0])
    rows = [json.loads(l) for l in (x100 / "inputs/items.jsonl").read_text().splitlines() if l.strip()]
    return x100, rows


def check(a):
    x100_prompts, jv_prompts, jv_data = load_modules(a.veribench, a.x100_repo)
    x100, rows = old_items(a.x100_repo)
    by_item = {r["item"]: r for r in rows}
    pack = [json.loads(l) for l in open(a.pack)]
    crit = [r for r in pack if r["kind"] == "crit"]
    assert len(crit) == 30, len(crit)
    bad, jv_items = [], {i.item: i for i in jv_data.load_items(x100 / "inputs/items.jsonl", x100, "all")}
    for rec in crit:
        r = by_item[rec["item"]]
        item = {k: str(x100 / r[k]) for k in ("ref_ann_path", "ref_snap_path", "py_ann_path")}
        item.update(task=r["task"], gold_file_name=r["gold_file_name"])
        cand = (x100 / r["candidate_path"]).read_text(encoding="utf-8", errors="replace")
        system, user = render_h2(x100_prompts, item, cand, r["candidate_file"])
        pid = sha((system + "\x00" + user).encode())[:16]
        ok = system == rec["system"] and user == rec["user"] and pid == rec["pid"]
        # checklist: our function against jv's own loader on the same item
        j = jv_items[rec["item"]]
        cs, cu = render_checklist(jv_prompts, jv_data, j.py, j.ref, j.cand, j.py_name, j.ref_name, j.cand_name)
        cs0, cu0 = jv_prompts.render("checklist", j)
        ok_cl = (cs, cu) == (cs0, cu0)
        if not (ok and ok_cl):
            bad.append((rec["item"], ok, ok_cl))
    print(f"H2 vs stored E63 prompts + checklist vs jv: {30 - len(bad)}/30 identical; failures: {bad}")
    sys.exit(1 if bad else 0)


def render(a):
    x100_prompts, jv_prompts, jv_data = load_modules(a.veribench, a.x100_repo)
    packet, out = Path(a.packet).resolve(), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    folders = sorted(p for p in packet.iterdir() if p.is_dir() and p.name.startswith("N"))
    h2, cl, items, man = [], [], [], {}
    for f in folders:
        gold = sorted((f / "gold_lean").glob("*.lean")); py = sorted((f / "python_source").glob("*.py"))
        assert len(gold) == 1 and len(py) == 1, f
        for cand in sorted((f / "agent_lean").glob("*.lean")):
            iid = cand.stem
            ct = cand.read_text(encoding="utf-8", errors="replace")
            item = dict(task=f.name, ref_ann_path=str(gold[0]), ref_snap_path=str(gold[0]), py_ann_path=str(py[0]),
                        gold_file_name=gold[0].name)
            s1, u1 = render_h2(x100_prompts, item, ct, cand.name)
            s2, u2 = render_checklist(jv_prompts, jv_data, py[0].read_text(encoding="utf-8", errors="replace"),
                                      gold[0].read_text(encoding="utf-8", errors="replace"), ct, py[0].name, gold[0].name, cand.name)
            h2.append(dict(item=iid, folder=f.name, system=s1, user=u1))
            cl.append(dict(item=iid, folder=f.name, system=s2, user=u2))
            rel = lambda p: str(Path(p).relative_to(packet))
            items.append(dict(item=iid, task=f.name, split="test", agent_sample=iid, candidate_file=cand.name,
                              candidate_path=rel(cand), ref_ann_path=rel(gold[0]), py_ann_path=rel(py[0]),
                              gold_file_name=gold[0].name, ratings={}))
            man[iid] = dict(folder=f.name, candidate_sha256=sha(cand.read_bytes()),
                            h2_prompt_sha256=sha((s1 + "\x00" + u1).encode()), checklist_prompt_sha256=sha((s2 + "\x00" + u2).encode()))
    assert len(h2) == 125, len(h2)
    for name, rows in (("h2.jsonl", h2), ("checklist.jsonl", cl)):
        (out / name).write_text("".join(json.dumps(r) + "\n" for r in rows))
    # E63's sft_lora.py --eval_pack format (pid as in build_pack.py); split "setN" is skipped by its summaries; no rating is carried
    (out / "pack_setN.jsonl").write_text("".join(json.dumps(dict(
        pid=sha((r["system"] + "\x00" + r["user"]).encode())[:16], cells=[], task=r["folder"], kind="setN", item=r["item"], level=0,
        split="setN", system=r["system"], user=r["user"], T=0.0, human=None)) + "\n" for r in h2))
    (out / "setN_items.jsonl").write_text("".join(json.dumps(r) + "\n" for r in items))
    manifest = dict(n_items=len(h2), n_folders=len(folders), packet_files_sha256=sha((packet / "FILES.sha256").read_bytes()),
                    h2_jsonl_sha256=sha((out / "h2.jsonl").read_bytes()), checklist_jsonl_sha256=sha((out / "checklist.jsonl").read_bytes()),
                    setN_items_jsonl_sha256=sha((out / "setN_items.jsonl").read_bytes()),
                    pack_setN_jsonl_sha256=sha((out / "pack_setN.jsonl").read_bytes()), answer_instruction=ANSWER_NEW,
                    h2_rubric=RUBRIC, items=man)
    (out / "PROMPTS_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps({k: v for k, v in manifest.items() if k != "items"}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=["check", "render"])
    ap.add_argument("--veribench", required=True, help="VeriBench checkout with docs/judge-validation (jv, checklist prompt)")
    ap.add_argument("--x100-repo", required=True, help="VeriBench checkout E39 rendered from (skampere1 veribench_e39, d7d36c31): "
                    "experiment 100's prompts.py, inputs and the rater instructions; later commits changed those files")
    ap.add_argument("--pack"); ap.add_argument("--packet"); ap.add_argument("--out", default="setN_prompts")
    a = ap.parse_args()
    check(a) if a.mode == "check" else render(a)
