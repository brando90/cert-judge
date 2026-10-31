#!/usr/bin/env python3
"""Writes FREEZE.json for E64 (hashes of every frozen candidate, code and input). Run from the repo root, once, before any set-N rating is read.
Adapter hashes come from scratch_sha.txt lines '<run> <epoch> <sha256>' (computed on SNAP and re-verified there with sha256sum -c)."""
import json, hashlib, glob, subprocess, sys
R = "experiments/"; E63 = glob.glob(R + "63_*")[0] + "/"; E58 = glob.glob(R + "58_*")[0] + "/"; D = glob.glob(R + "64_*")[0] + "/"
sh = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
ci = json.load(open(E58 + "results/criterion_items.json"))
ads = []
for l in open(sys.argv[1]):
    n, e, h = l.split(); fj = E63 + f"results/runs/{n}/FROZEN.json"
    ads.append(dict(name=n, arm="human_mix_sft" if "_hm_" in n else "teacher_only_sft", epoch=e, host="skampere1.stanford.edu (/dfs/scratch0, user brando9)",
                    path=f"/dfs/scratch0/brando9/e62/runs/{n}/{e}/adapter_model.safetensors", sha256=h, frozen_json=fj, frozen_json_sha256=sh(fj)))
code = {p: sh(p) for p in sorted(glob.glob(E63 + "code/*.py")) + [D + "code/confirm64.py", E58 + "scripts/analyze58.py", E58 + "scripts/e58.py"]}
fz = dict(
    frozen_for="E64 confirmatory test on the Nov 6 set-N human ratings",
    repo_head_before=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    A_human_mix_sft=dict(base_model="Qwen/Qwen3-8B (local copy /dfs/scratch0/brando9/e62/models/Qwen3-8B)", base_config_sha256="f7c4eadfbbf522470667b797a3c89be2524832d2d599797248dc304fff447c30",
                         base_index_sha256="f9fdbcb91c23971c13ec5d5f2573d2349e8f61f2f049371ec699281748fdb1bc", lora="r=16 alpha=32 all linear", prompt="E39 H2 with one-digit instruction, EV readout, thinking off",
                         adapters=[a for a in ads if a["arm"] == "human_mix_sft"]),
    B_teacher_only_sft=dict(adapters=[a for a in ads if a["arm"] == "teacher_only_sft"]),
    C_qwen36_27b_checklist_think=dict(model="Qwen/Qwen3.6-27B-FP8", variant="checklist__think", field="stated", selected_by="max mean-over-agents Spearman on the 45-item search split only (FarmShare run 2026-10-28)",
        repo="brando90/veribench", commit="6d838cfb000bb0df5d664143b812a6882ee94360", code_tree="docs/judge-validation/code (tree c08aa8687048ab789283eab9821cecaec5e28603)",
        final_json="docs/judge-validation/results_farmshare_oct28/final.json (blob 8635d32c09d6ef546021d4fef289debc917d1fd9)", note="the max-min pick (mirror__nothink/score) is NOT a frozen candidate"),
    D_index=dict(index="C_ms_gold", analysis_json_path=E58 + "results/full_13_judges_2026-10-30/ANALYSIS.json", analysis_json_sha256=sh(E58 + "results/full_13_judges_2026-10-30/ANALYSIS.json"),
                 e58_collection_manifest_sha256="a1863fee1c18b7649dd81c71221e61e09bdca886fd607ac9eab71a54652f8e10", gate="spearman >= 0.45 and permutation p < 0.05, plain and model-clustered, unchanged from E39/E58",
                 tvd_mi="exploratory only, not frozen"),
    old_test_items=dict(source=E58 + "results/criterion_items.json", source_sha256=sh(E58 + "results/criterion_items.json"),
                        item_ids=[i["item"] for i in ci["items"] if i["split"] == "test"], rule="no test read, selection or refit on these 30 items in E64"),
    code_sha256=code)
json.dump(fz, open(D + "FREEZE.json", "w"), indent=1); print(len(ads), "adapters;", len(fz["old_test_items"]["item_ids"]), "old test items;", len(code), "code files")
