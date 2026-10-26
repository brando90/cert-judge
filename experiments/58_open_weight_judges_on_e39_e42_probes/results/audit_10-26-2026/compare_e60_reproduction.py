#!/usr/bin/env python3
"""Compare complete saved E60 outputs exactly, excluding only input-directory metadata."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def compare(expected, actual):
    differences, matching = [], 0
    excluded = {"old_runs", "new_runs", "rep_runs"}

    def visit(a, b, path=""):
        nonlocal matching
        if isinstance(a, dict) and isinstance(b, dict):
            for key in sorted(a.keys() | b.keys()):
                if not path and key in excluded:
                    continue
                child = f"{path}/{key}"
                if key not in a or key not in b:
                    differences.append({"path": child, "reason": "missing key"})
                else:
                    visit(a[key], b[key], child)
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                differences.append({"path": path, "reason": "length", "expected": len(a), "actual": len(b)})
            else:
                for index, (x, y) in enumerate(zip(a, b)):
                    visit(x, y, f"{path}/{index}")
        elif a == b or (isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b)):
            matching += 1
        else:
            differences.append({"path": path, "expected": a, "actual": b})

    visit(expected, actual)
    return {"matching_scalar_leaves": matching, "differing_fields": differences, "excluded_fields": sorted(excluded)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("reproduced", type=Path)
    args = parser.parse_args()
    result = compare(json.loads(args.expected.read_text()), json.loads(args.reproduced.read_text()))
    result.update({name + "_sha256": hashlib.sha256(path.read_bytes()).hexdigest()
                   for name, path in (("expected", args.expected), ("reproduced", args.reproduced))})
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["differing_fields"]))
