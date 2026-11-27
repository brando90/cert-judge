"""Shared item join, budget gate, and digit-logprob parsing for experiments 69B and 69C."""
from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP69 = Path(__file__).resolve().parents[2]
RATINGS = EXP69 / "data/cert-judge-data/ttj-exp09-live-sync-2026-11-26/ratings"
SPEND_CAP_USD = 27.0
FORBIDDEN = ("gemini", "agy", "antigravity")
PATH_RE = re.compile(r"^task_[0-9]{2}_[\w]+/agent_lean/agent_[0-9]+\.lean$")
TRUNC = 12000

TRAIN = [
    "task_16_certificate_hostname", "task_05_factorial", "task_25_maximum_list_element",
    "task_14_statistical_quantiles", "task_10_lower_median", "task_22_shell_quoting",
    "task_15_prime_fibonacci_search", "task_06_counting_sort", "task_21_tor_hidden_service",
    "task_02_edit_distance",
]
VAL = [
    "task_07_transport_layer_security_downgrade", "task_01_heap_sort", "task_17_heapsort_algorithm",
    "task_19_string_prefixes", "task_23_duplicate_characters",
]
TEST = [
    "task_09_sum_of_digits", "task_03_application_entitlements", "task_11_html_escaping",
    "task_12_mean_absolute_deviation", "task_13_primality_testing", "task_08_base32_encoding",
    "task_20_integer_exponentiation", "task_24_trusted_platform_module_hash_safe",
    "task_04_integer_string_sequence", "task_18_topological_sorting",
]
SPLIT = {t: "train" for t in TRAIN} | {t: "val" for t in VAL} | {t: "test" for t in TEST}


def reject_model(name: str) -> None:
    low = name.lower()
    if any(tok in low for tok in FORBIDDEN):
        raise SystemExit(f"refusing model {name!r}: experiment 69B is no-agy and not Gemini")


def load_rating_rows() -> list[dict]:
    rows = []
    for path in sorted(RATINGS.glob("*native_main*.csv")):
        with path.open() as handle:
            for row in csv.DictReader(handle):
                if row.get("source_label") != "main":
                    continue
                raw = (row.get("final_score_0_5") or "").strip()
                if raw == "":
                    continue
                rows.append(row)
    return rows


def items_from_ratings(rows: list[dict] | None = None) -> list[dict]:
    """One record per item_id. Repair a non-path candidate_file from the other raters."""
    rows = rows if rows is not None else load_rating_rows()
    by_item: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_item[row["item_id"]].append(row)
    items = []
    for item_id, group in sorted(by_item.items()):
        paths = [r["candidate_file"].strip() for r in group if PATH_RE.match(r["candidate_file"].strip())]
        if not paths:
            raise ValueError(f"no path for {item_id}")
        path = max(set(paths), key=paths.count)
        task = path.split("/")[0]
        ratings = [int(round(float(r["final_score_0_5"]))) for r in group]
        items.append({
            "item_id": item_id,
            "task": task,
            "split": SPLIT[task],
            "candidate_file": path,
            "gold_file": f"{task}/gold_lean/reference.lean",
            "ratings": ratings,
        })
    return items


def read_capped(root: Path, rel: str) -> tuple[str, bool]:
    text = (root / rel).read_text(encoding="utf-8", errors="replace")
    if len(text) <= TRUNC:
        return text, False
    return text[:TRUNC], True


RUBRIC = """Rate how well the agent Lean theorem statements cover the gold Lean theorem statements.
Score statement coverage only, not proof style. 5 = all gold guarantees covered; 4 = one or two minor gaps; 3 = one important gap; 2 = fewer than half the gold theorems; 1 = no gold theorem but one relevant theorem; 0 = vacuous or broken.
If unsure between two adjacent scores, choose the lower one.
Answer with ONLY one digit, 0 to 5.
"""


def build_user(gold: str, cand: str) -> str:
    return f"GOLD LEAN:\n{gold}\n\nAGENT LEAN:\n{cand}\n"


def digit_probs_from_top(pairs: list[tuple[str, float]]) -> tuple[np.ndarray | None, float]:
    """pairs are (token, logprob). Returns (6-vector or None, mass on digit tokens)."""
    mass = np.zeros(6, dtype=float)
    for token, logp in pairs:
        dig = token.strip()
        if len(dig) == 1 and dig in "012345":
            mass[int(dig)] += np.exp(logp)
    total = float(mass.sum())
    if total <= 0:
        return None, 0.0
    return mass / total, total


def point_mass(digit: int) -> list[float]:
    p = [0.0] * 6
    p[digit] = 1.0
    return p


def within_cap(spent: float, next_cost: float, cap: float = SPEND_CAP_USD) -> bool:
    return spent + next_cost <= cap + 1e-9


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()
