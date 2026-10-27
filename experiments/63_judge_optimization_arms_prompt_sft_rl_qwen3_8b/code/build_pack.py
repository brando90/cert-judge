#!/usr/bin/env python3
"""E62 data pack: one record per unique judge prompt (experiment 39's H2 prompt, 249 unique of 521 cells), with the
frontier-teacher score histogram, the task split, and (crit items only) the expert mean. Writes pack_trainval.jsonl
(train+val tasks) and pack_test.jsonl (test tasks, held back until every arm is frozen), plus a manifest with hashes.
The H2 answer instruction is replaced by a one-digit instruction (all arms read the 0-5 score from the first token)."""
import gzip, json, hashlib, collections, sys
from pathlib import Path
REPO = Path("/var/lib/agent/scratch/cert-judge-at1209/experiments")
OUT = Path("/var/lib/agent/scratch/e62/pack"); OUT.mkdir(exist_ok=True, parents=True)
H = REPO / "39_label_free_proxy_index_train_val_test_over_judge_families/results/harvest"
FRONT = ("sol6h", "sonnet5m", "luna6h", "gem31h", "opus55x")
ANSWER_NEW = ("Answer with ONLY one digit, 0 to 5: your final_score_0_5 (the final score after the spam adjustment). "
              "No other text.")
items = json.load(open(REPO / "58_open_weight_judges_on_e39_e42_probes/results/criterion_items.json"))["items"]
split_of_task = {i["task"]: i["split"] for i in items}
expert = {i["item"]: i["target_expert"] for i in items}          # 0..1 (expert mean / 5)
rows = [json.loads(l) for l in gzip.open("/var/lib/agent/scratch/e62/H2.jsonl.gz", "rt")]
teach = {}; rat = {}
for m in FRONT:
    h = json.load(open(H / f"{m}__H2.json"))
    rat[m] = {c["cell"]: c.get("rationale") for c in h["cells"] if c["status"] == "measured"}
    teach[m] = {c["cell"]: c["score_raw"] for c in h["cells"] if c["status"] == "measured" and c.get("score_raw") is not None}
recs = {}
for r in rows:
    sysm = r["system"]; k = sysm.rfind("Answer with ONLY one JSON object")
    assert k > 0
    sysm = sysm[:k] + ANSWER_NEW
    pid = hashlib.sha256((sysm + "\x00" + r["user"]).encode()).hexdigest()[:16]
    rec = recs.setdefault(pid, dict(pid=pid, cells=[], task=r["task"], kind=r["kind"], item=r["item"], level=r["level"],
                                    split=split_of_task[r["task"]], system=sysm, user=r["user"], raws=[]))
    rec["cells"].append(r["cell"])
    if "rationale" not in rec:
        for m in FRONT:
            if rat[m].get(r["cell"]):
                rec["rationale"] = f"{rat[m][r['cell']]}"; break
    for m in FRONT:
        if r["cell"] in teach[m]:
            rec["raws"].append(teach[m][r["cell"]])
for rec in recs.values():
    n = len(rec["raws"]); rec["_n"] = n
    rec["hist"] = [rec["raws"].count(d) / n for d in range(6)]
    rec["T"] = sum(rec["raws"]) / n / 5.0
    rec["n_teacher"] = n
    rec["human"] = expert.get(rec["item"]) if rec["kind"] == "crit" else None
    del rec["raws"]
bad = [r for r in recs.values() if r["_n"] < 3]
print("prompts with <3 teacher scores (dropped):", len(bad))
for r in list(recs.values()): r.pop("_n", None)
for r in bad: recs.pop(r["pid"])
tv = [r for r in recs.values() if r["split"] in ("train", "val")]
te = [r for r in recs.values() if r["split"] == "test"]
for name, lst in (("pack_trainval.jsonl", tv), ("pack_test.jsonl", te)):
    with open(OUT / name, "w") as f:
        for r in sorted(lst, key=lambda r: r["pid"]): f.write(json.dumps(r) + "\n")
man = {"unique_prompts": len(recs), "trainval": len(tv), "test": len(te),
       "by_split": dict(collections.Counter(r["split"] for r in recs.values())),
       "by_split_kind": {f"{s}/{k}": n for (s, k), n in sorted(collections.Counter((r["split"], r["kind"]) for r in recs.values()).items())},
       "sha256": {n: hashlib.sha256((OUT / n).read_bytes()).hexdigest() for n in ("pack_trainval.jsonl", "pack_test.jsonl")},
       "answer_instruction": ANSWER_NEW, "teacher": FRONT}
json.dump(man, open(OUT / "manifest.json", "w"), indent=1); print(json.dumps(man, indent=1))
