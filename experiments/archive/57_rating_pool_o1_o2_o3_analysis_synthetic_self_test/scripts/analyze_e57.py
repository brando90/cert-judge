#!/usr/bin/env python3
"""TLDR: Run the four synthetic cases locked in PROTOCOL.md. No model calls and no human ratings."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pool_analysis as P  # noqa: E402

E57 = HERE.parent


def monotone(n):
    return list(range(n)), list(range(n))


def run():
    tau = P.frozen_tau()
    x, y = monotone(20)
    case1 = P.o1_gate(x, y, n_declared=20)
    case2 = P.o1_gate([-v for v in x], y, n_declared=20)
    present_x, present_y = monotone(31)
    case3 = P.o1_gate(present_x + [None] * 20, present_y + [None] * 20, n_declared=51)
    human = [i / 29 for i in range(30)]
    judge = [v + 0.2 for v in human]
    case4 = P.absolute_agreement(judge, human)
    # O3: five accepted, two of them fail; ten units, base rate 4/10.
    screen = [0.95, 0.95, 0.95, 0.95, 0.95, 0.2, 0.2, 0.2, 0.2, 0.2]
    meets = [True, True, True, False, False, True, True, False, False, False]
    case_o3 = P.false_acceptance(screen, meets, tau)
    expected = {"case1": "PASS", "case2": "FAIL", "case3": "INCONCLUSIVE"}
    got = {"case1": case1["reading"], "case2": case2["reading"], "case3": case3["reading"]}
    offset_ok = (abs(case4["bias"] - 0.2) < 1e-9 and abs(case4["mae"] - 0.2) < 1e-9
                 and case4["spearman"] == 1.0 and case4["icc_a1"] < case4["icc_c1"])
    # Five units are accepted and two of those fail (0.4). Five of the ten units fail overall (0.5).
    o3_ok = (abs(case_o3["false_acceptance"] - 0.4) < 1e-9 and abs(case_o3["base_rate"] - 0.5) < 1e-9)
    payload = {"written_utc": datetime.now(timezone.utc).isoformat(), "tau": tau,
               "case1_pass": case1, "case2_fail": case2, "case3_inconclusive": case3,
               "case4_offset": case4, "o3_known_rates": case_o3,
               "readings_match": got == expected and offset_ok and o3_ok,
               "expected_readings": expected, "got_readings": got, "offset_ok": offset_ok, "o3_ok": o3_ok}
    (E57 / "results").mkdir(exist_ok=True)
    (E57 / "results/self_test.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"readings_match": payload["readings_match"], "got": got, "bias": case4["bias"],
                      "icc_c": case4["icc_c1"], "icc_a": case4["icc_a1"], "tau": tau}, indent=1))
    return 0 if payload["readings_match"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
