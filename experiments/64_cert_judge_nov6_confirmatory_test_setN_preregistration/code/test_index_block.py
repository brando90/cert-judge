"""Synthetic dry run of confirm64.index_block (test D) with 200 draws; no real ratings. Usage: ~/.venvs/e59/bin/python test_index_block.py"""
import json, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H)); import confirm64
rng = np.random.default_rng(1); R = H.parents[1]
ana = json.load(open(R / "58_open_weight_judges_on_e39_e42_probes/results/full_13_judges_2026-10-30/ANALYSIS.json"))
items = [f"F{f:02d}_a{a}" for f in range(25) for a in range(5)]; truth = {i: rng.uniform(0, 5) for i in items}
human = {i: dict(folder=i[:3], h=truth[i]) for i in items}
sc = {}
for u in ana["units"]:
    q = u["indices"].get("C_ms_gold")
    if q is not None: sc[u["config"]] = {i: truth[i] + rng.normal(0, 3 - 2.5 * q) for i in items}
json.dump(sc, open("/tmp/units_syn.json", "w"))
confirm64.DRAWS = 200
fz = {"index": {"analysis_json_path": str(R / "58_open_weight_judges_on_e39_e42_probes/results/full_13_judges_2026-10-30/ANALYSIS.json")}}
o = confirm64.index_block("/tmp/units_syn.json", human, fz); print(o["status"], o["n_units"], o["n_models"], o.get("verdict"), o["gate"]["plain"]["spearman"], o["gate"]["model_clustered"]["spearman"])
