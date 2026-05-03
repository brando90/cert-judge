#!/usr/bin/env python3
"""
Shared helpers for prompt/scale sensitivity experiments.
"""
import csv
import json
import random
import re
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

from utils.metrics import spearman_r
from utils.variant_generator import generate_variants


VERIBENCH_DIR = Path.home() / "veribench/veribench_dataset/lean_src/veribench"
LOCAL_FILE_EQ_DIR = Path(__file__).resolve().parents[3] / "data" / "file_equiv_08_19_2025"


PROMPT_VARIANTS: Dict[str, str] = {
    "P1_BASELINE": """You are an expert in Lean 4 formal verification.
Score how well the GENERATED THEOREM captures the correctness properties
of the REFERENCE IMPLEMENTATION. Score from 0.0 to 1.0.

- 1.0: Semantically equivalent to what the reference guarantees
- 0.7-0.9: Captures most properties, misses minor ones
- 0.4-0.6: Captures some properties, has meaningful gaps
- 0.1-0.3: Technically valid Lean but misses core properties
- 0.0: Trivially true (e.g., `True`) or incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Respond ONLY with valid JSON, no markdown:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence max>"}}""",
    "P2_FORMAL": """You are evaluating semantic equivalence between Lean 4 artifacts.
Assign a real-valued score in [0.0, 1.0] for how well GENERATED THEOREM preserves the guarantees of REFERENCE IMPLEMENTATION.

Rubric:
1.0 exact semantic match
0.7-0.9 mostly correct, minor omissions
0.4-0.6 partial coverage, important gaps
0.1-0.3 weak alignment
0.0 trivial/incorrect theorem

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Output strict JSON only:
{{"score": <0.0-1.0>, "reasoning": "<max one sentence>"}}""",
    "P3_CONCISE": """Judge semantic alignment of Lean code.
Return one score from 0.0 to 1.0 using:
1.0 equivalent, 0.7-0.9 minor misses, 0.4-0.6 partial, 0.1-0.3 poor, 0.0 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

JSON only:
{{"score": <float>, "reasoning": "<one sentence>"}}""",
    "P4_CHECKLIST": """Evaluate this in order:
1) What properties does REFERENCE IMPLEMENTATION guarantee?
2) Which are preserved by GENERATED THEOREM?
3) Are there missing core guarantees or trivialization?
4) Map to score in [0.0, 1.0]:
   1.0 equivalent; 0.7-0.9 minor gaps; 0.4-0.6 meaningful gaps; 0.1-0.3 weak; 0.0 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return JSON only:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}""",
    "P5_REORDERED_INPUT_FIRST": """REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Task: score semantic alignment from 0.0 to 1.0.
Rubric: 1.0 equivalent; 0.7-0.9 mostly right minor misses; 0.4-0.6 partial; 0.1-0.3 weak; 0.0 trivial or incorrect.
Be strict about semantic correctness, not syntax similarity.

Output JSON only:
{{"score": <float>, "reasoning": "<one sentence>"}}""",
    "P6_REORDERED_OUTPUT_FIRST": """Return ONLY:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}

Scoring intent: semantic equivalence of GENERATED THEOREM to REFERENCE IMPLEMENTATION.
Scale:
1.0 equivalent
0.7-0.9 mostly equivalent with minor omissions
0.4-0.6 some overlap with meaningful omissions
0.1-0.3 weak match
0.0 trivial/incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}""",
    "P7_STRICT_A": """You are a strict Lean 4 evaluator. Penalize any missing core property.
Score in [0,1]:
1.0 exact semantic match only
0.8 near-exact, very small omission
0.5 partial match with important missing guarantees
0.2 mostly misaligned
0.0 trivial/incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

JSON only:
{{"score": <float>, "reasoning": "<one sentence>"}}""",
    "P8_STRICT_B": """Evaluate conservatively. If uncertain, choose the lower score.
Use [0.0,1.0]:
1.0 equivalent semantics
0.7-0.9 mostly right, minor misses
0.4-0.6 substantial omissions
0.1-0.3 weak relation
0.0 trivial/incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return valid JSON only:
{{"score": <float>, "reasoning": "<one sentence>"}}""",
    "P9_LENIENT_A": """Evaluate overall semantic fidelity, allowing harmless stylistic differences.
Score in [0,1]:
1.0 equivalent guarantees
0.7-0.9 mostly equivalent
0.4-0.6 partial
0.1-0.3 weak
0.0 trivial/incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Output JSON only:
{{"score": <float>, "reasoning": "<one sentence>"}}""",
    "P10_LENIENT_B": """Score how much of the reference's intended correctness is captured.
Use:
1.0 full capture
0.7-0.9 high capture
0.4-0.6 moderate capture
0.1-0.3 low capture
0.0 none/trivial/incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

JSON only:
{{"score": <float>, "reasoning": "<one sentence>"}}""",
    "P11_JSON_FIRST": """Produce JSON only:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}

Task: compare GENERATED THEOREM against REFERENCE IMPLEMENTATION for semantic correctness guarantees.
Rubric:
1.0 equivalent
0.7-0.9 mostly correct
0.4-0.6 partial
0.1-0.3 poor
0.0 trivial/incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}""",
    "P12_REASONING_MINIMAL": """You are a Lean 4 semantic judge.
Score alignment of GENERATED THEOREM vs REFERENCE IMPLEMENTATION in [0,1].
Use:
1.0 equivalent; 0.7-0.9 mostly equivalent; 0.4-0.6 partial; 0.1-0.3 weak; 0.0 trivial/incorrect.
Keep reasoning under 12 words.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return JSON only:
{{"score": <float>, "reasoning": "<very short phrase>"}}""",
    "P13_HUMAN_ALIGN_STRICT": """You are grading semantic theorem/spec quality in Lean 4.

Goal: match expert human ratings of semantic correctness/completeness, not text similarity.

Scoring rules:
- Ignore superficial differences: variable names, formatting, theorem order, comments.
- Penalize missing guarantees heavily.
- Penalize vacuous truth / weakened preconditions heavily.
- Penalize wrong target theorem even if proof compiles.
- Reward exact semantic coverage of reference guarantees.

Rubric (0.0 to 1.0):
1.0 = semantically equivalent guarantees
0.8-0.9 = almost complete, minor omission
0.6-0.7 = mostly right, one meaningful missing guarantee
0.3-0.5 = partial, substantial gaps
0.1-0.2 = weak semantic match
0.0 = trivial/incorrect/misaligned

If uncertain between two bands, choose the lower band.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return JSON only:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}""",
    "P14_HUMAN_ALIGN_V2": """You are grading the semantic quality of a generated Lean 4 theorem/specification.

Goal: match expert human ratings of semantic correctness and completeness.
Do not grade surface similarity, proof style, theorem ordering, variable names, formatting, or comments.

Your task is to compare the GENERATED THEOREM against the semantic guarantees implied by the REFERENCE IMPLEMENTATION.
A theorem that compiles or is provable is not necessarily good: it may be vacuous, too weak, target the wrong property, or omit key guarantees.

Scoring principles:
- Reward exact coverage of the reference guarantees.
- Ignore superficial differences: names, formatting, theorem order, comments, auxiliary lemmas.
- Penalize missing postconditions or behavioral guarantees heavily.
- Penalize weakened assumptions/preconditions heavily if they make the theorem easier or less useful.
- Penalize vacuous truth heavily, including impossible assumptions or hypotheses that avoid the real case.
- Penalize wrong target theorem heavily, even if the Lean proof compiles.
- Penalize theorems that prove only type-correctness, existence, or trivial facts when the reference requires functional correctness.
- If uncertain between two score bands, choose the lower band.

Rubric:
1.0 = semantically equivalent guarantees
0.8-0.9 = almost complete; only minor omissions or harmless weakening
0.6-0.7 = mostly right; one meaningful missing guarantee or moderate weakening
0.3-0.5 = partial; substantial semantic gaps
0.1-0.2 = weak match; only loosely related to the intended guarantee
0.0 = trivial, vacuous, incorrect, or semantically misaligned

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return JSON only:
{{"score": <float from 0.0 to 1.0>, "reasoning": "<one concise sentence explaining the main semantic issue or why it matches>"}}""",
}


SCALE_VARIANTS: Dict[str, str] = {
    "S1_UNIT_0_1": """You are an expert in Lean 4 formal verification.
Score semantic alignment of GENERATED THEOREM to REFERENCE IMPLEMENTATION on a 0.0 to 1.0 scale.
Anchors: 1.0 equivalent, 0.7-0.9 mostly correct, 0.4-0.6 partial, 0.1-0.3 weak, 0.0 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}""",
    "S2_INT_1_10": """You are an expert in Lean 4 formal verification.
First choose an integer raw score from 1 to 10 for semantic alignment.
Then map it to normalized score = (raw - 1) / 9.
Anchors: 10 equivalent, 7-9 mostly correct, 4-6 partial, 2-3 weak, 1 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON with normalized score:
{{"score": <float 0.0-1.0>, "reasoning": "<mention raw score briefly>"}}""",
    "S3_INT_1_5": """You are an expert in Lean 4 formal verification.
First choose an integer raw score from 1 to 5 for semantic alignment.
Then map it to normalized score = (raw - 1) / 4.
Anchors: 5 equivalent, 4 mostly correct, 3 partial, 2 weak, 1 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON with normalized score:
{{"score": <float 0.0-1.0>, "reasoning": "<mention raw score briefly>"}}""",
    "S4_INT_0_100": """You are an expert in Lean 4 formal verification.
First choose an integer raw percentage from 0 to 100 for semantic alignment.
Then map it to normalized score = raw / 100.
Anchors: 100 equivalent, 70-90 mostly correct, 40-60 partial, 10-30 weak, 0 trivial/incorrect.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON with normalized score:
{{"score": <float 0.0-1.0>, "reasoning": "<mention raw percentage briefly>"}}""",
    "S5_CAT_4": """You are an expert in Lean 4 formal verification.
First choose one category:
FAIL, WEAK, MOSTLY, EQUIVALENT.
Then map to normalized score:
FAIL=0.00, WEAK=0.33, MOSTLY=0.67, EQUIVALENT=1.00.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON with normalized score:
{{"score": <float 0.0-1.0>, "reasoning": "<mention chosen category>"}}""",
    "S6_CAT_3": """You are an expert in Lean 4 formal verification.
First choose one category:
NO, PARTIAL, YES.
Then map to normalized score:
NO=0.00, PARTIAL=0.50, YES=1.00.

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Return ONLY JSON with normalized score:
{{"score": <float 0.0-1.0>, "reasoning": "<mention chosen category>"}}""",
}


def score_to_label(score: float) -> str:
    if score >= 0.9:
        return "equivalent"
    if score >= 0.7:
        return "mostly"
    if score >= 0.4:
        return "partial"
    if score >= 0.1:
        return "weak"
    return "fail"


def cohen_kappa(xs: List[str], ys: List[str], labels: List[str]) -> float:
    if not xs or len(xs) != len(ys):
        return 0.0
    n = len(xs)
    idx = {lab: i for i, lab in enumerate(labels)}
    mat = [[0 for _ in labels] for _ in labels]
    for x, y in zip(xs, ys):
        if x in idx and y in idx:
            mat[idx[x]][idx[y]] += 1
    po = sum(mat[i][i] for i in range(len(labels))) / n
    row = [sum(r) / n for r in mat]
    col = [sum(mat[r][c] for r in range(len(labels))) / n for c in range(len(labels))]
    pe = sum(r * c for r, c in zip(row, col))
    if pe >= 0.999999:
        return 1.0
    return (po - pe) / (1 - pe)


def pairwise_stats(
    score_by_item: Dict[str, Dict[str, float]],
    label_by_item: Dict[str, Dict[str, str]],
    names: List[str],
) -> List[dict]:
    labels = ["fail", "weak", "partial", "mostly", "equivalent"]
    item_ids = sorted(score_by_item.keys())
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]
            sa = [score_by_item[item_id][a] for item_id in item_ids]
            sb = [score_by_item[item_id][b] for item_id in item_ids]
            la = [label_by_item[item_id][a] for item_id in item_ids]
            lb = [label_by_item[item_id][b] for item_id in item_ids]
            rho, pval = spearman_r(sa, sb)
            kappa = cohen_kappa(la, lb, labels)
            mad = sum(abs(x - y) for x, y in zip(sa, sb)) / max(1, len(sa))
            out.append(
                {
                    "a": a,
                    "b": b,
                    "spearman_r": round(float(rho), 6),
                    "spearman_p": round(float(pval), 6),
                    "cohen_kappa": round(float(kappa), 6),
                    "mean_abs_diff": round(float(mad), 6),
                }
            )
    return out


def _extract_bug_level(path: Path) -> int:
    m = re.search(r"_(\d+)_bugs\.lean$", path.name)
    if m:
        return int(m.group(1))
    return -1


def load_items_file_equiv(max_items: int = 0, seed: int = 42) -> List[dict]:
    ref_path = LOCAL_FILE_EQ_DIR / "correct_file_dir" / "my_add_0_bugs.lean"
    if not ref_path.exists():
        return []
    reference_impl = ref_path.read_text()
    candidates: List[Tuple[str, Path]] = []
    for subdir in ["correct_same_files_dir", "my_add_file_eq_with_bugs", "my_add_file_eq_with_missing_specs"]:
        for path in sorted((LOCAL_FILE_EQ_DIR / subdir).glob("*.lean")):
            candidates.append((subdir, path))

    if max_items and max_items > 0 and len(candidates) > max_items:
        rng = random.Random(seed)
        rng.shuffle(candidates)
        candidates = sorted(candidates[:max_items], key=lambda x: (x[0], x[1].name))

    items = []
    for subdir, cand_path in candidates:
        generated = cand_path.read_text()
        bug_level = _extract_bug_level(cand_path)
        item_id = f"{subdir}/{cand_path.name}"
        items.append(
            {
                "item_id": item_id,
                "source": "file_equiv_08_19_2025",
                "group": subdir,
                "bug_level": bug_level,
                "reference_impl": reference_impl,
                "generated_theorem": generated,
            }
        )
    return items


def load_items_veribench_variants(n_files: int = 20, seed: int = 42) -> List[dict]:
    if not VERIBENCH_DIR.exists():
        return []
    subdirs = ["easy_set", "cs_set", "humaneval_set", "realcode_set", "security_set"]
    files: List[Path] = []
    for subdir in subdirs:
        d = VERIBENCH_DIR / subdir
        if d.exists():
            files.extend(sorted(d.glob("*.lean")))
    if not files:
        return []
    rng = random.Random(seed)
    rng.shuffle(files)
    files = files[: max(1, n_files)]

    items: List[dict] = []
    for fpath in files:
        ref = fpath.read_text()
        variants = generate_variants(ref)
        for v in variants:
            item_id = f"{fpath.stem}:{v['variant_type']}"
            items.append(
                {
                    "item_id": item_id,
                    "source": "veribench_variants",
                    "group": v["variant_type"],
                    "bug_level": -1,
                    "reference_impl": ref,
                    "generated_theorem": v["code"],
                }
            )
    return items


def load_items(items_source: str, max_items: int, seed: int) -> List[dict]:
    if items_source == "file_equiv":
        return load_items_file_equiv(max_items=max_items, seed=seed)
    if items_source == "veribench_variants":
        n_files = max_items if max_items > 0 else 20
        return load_items_veribench_variants(n_files=n_files, seed=seed)
    if items_source == "auto":
        items = load_items_veribench_variants(n_files=max_items if max_items > 0 else 20, seed=seed)
        if items:
            return items
        return load_items_file_equiv(max_items=max_items, seed=seed)
    raise ValueError(f"Unknown items_source: {items_source}")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2))


def write_rows_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_score_distributions(score_by_item: Dict[str, Dict[str, float]], names: List[str]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    item_ids = sorted(score_by_item.keys())
    for name in names:
        vals = [score_by_item[item_id][name] for item_id in item_ids]
        if vals:
            mean = statistics.mean(vals)
            std = statistics.stdev(vals) if len(vals) > 1 else 0.0
            mn = min(vals)
            mx = max(vals)
            low = sum(v <= 0.01 for v in vals) / len(vals)
            high = sum(v >= 0.99 for v in vals) / len(vals)
            uniq = len(set(round(v, 4) for v in vals))
        else:
            mean = std = mn = mx = low = high = 0.0
            uniq = 0
        out[name] = {
            "mean": round(float(mean), 6),
            "std": round(float(std), 6),
            "min": round(float(mn), 6),
            "max": round(float(mx), 6),
            "pct_at_low_boundary": round(float(low), 6),
            "pct_at_high_boundary": round(float(high), 6),
            "n_unique_scores_4dp": int(uniq),
        }
    return out
