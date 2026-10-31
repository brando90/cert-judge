"""Synthetic dry run of confirm64.py: no real ratings. Usage: ~/.venvs/e59/bin/python test_confirm64.py"""
import csv, json, subprocess, tempfile, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; rng = np.random.default_rng(0); T = Path(tempfile.mkdtemp())
items = [f"F{f:02d}_a{a}" for f in range(25) for a in range(5)]; truth = {i: rng.uniform(0, 5) for i in items}
with open(T / "r.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["item_id", "folder", "agent", "rater", "score", "qualified"])
    for i in items:
        for r in ("T01", "T02"): w.writerow([i, i[:3], i[-2:], r, float(np.clip(truth[i] + rng.normal(0, .6), 0, 5)), 1])
        w.writerow([i, i[:3], i[-2:], "A1", float(np.clip(truth[i] + rng.normal(0, .6), 0, 5)), 0])
(T / "j").mkdir()
names = [f"sft_q3_8b_hm_s{i}" for i in range(5)] + [f"sft_q3_8b_s{i}" for i in range(6)] + ["qwen36_27b__checklist__think__stated"]
for k, n in enumerate(names): json.dump({"ev": {i: truth[i] + rng.normal(0, 0.5 + 0.1 * (k > 4)) for i in items}}, open(T / "j" / f"{n}.json", "w"))
fr = {"old_test_items": {"item_ids": ["1_MyAdd"]}}; json.dump(fr, open(T / "f.json", "w"))
r = subprocess.run([sys.executable, str(H / "confirm64.py"), "--ratings", str(T / "r.csv"), "--judges", str(T / "j"), "--freeze", str(T / "f.json"), "--out", str(T / "o")], capture_output=True, text=True)
print(r.stdout, r.stderr[-800:]); d = json.load(open(T / "o/CONFIRMATORY_RESULT.json")); print(d["primary"]["A_human_mix_sft"]["mean_rho"], d["primary"]["A_minus_B"])
