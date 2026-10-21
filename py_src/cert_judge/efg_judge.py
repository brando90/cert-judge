"""
EFG (Epistemically and Formally Grounded) ensemble of LLM judges.

Baseline implementation of:
  Zhang, Valentino & Freitas, "Beyond Gold Standards: Epistemic Ensemble of
  LLM Judges for Formal Mathematical Reasoning", arXiv:2506.10903, 2025.

Adapted for Lean 4 theorem scoring (cert-judge): instead of evaluating NL-to-
formal autoformalization, we evaluate how well a *generated theorem* captures
the correctness properties of a *reference implementation* using the same
four-aspect taxonomy:

  LP  — Logical Preservation
  MC  — Mathematical Consistency
  FV  — Formal Validity
  FQ  — Formal Quality

Each aspect is estimated via Operable Atomic Properties (OAPs), binary
questions answered by an LLM judge. The final score is a weighted linear
combination (Eq. 1 of the paper):

  S_OA = w_LP * S_LP + w_MC * S_MC + w_FV * S_FV + w_FQ * S_FQ

with paper-optimal weights: w_LP=0.25, w_MC=0.19, w_FV=0.32, w_FQ=0.24.

Two scoring modes:
  - "direct":  ask one binary question per aspect, score ∈ {0, 1}
  - "oap_wa":  ask one binary question per OAP, aspect score = mean(OAPs),
               then combine via linear weights  (best in paper)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Weights from paper Section 3.1 (Table 4, optimal QP solution)
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS: Dict[str, float] = {
    "LP": 0.25,
    "MC": 0.19,
    "FV": 0.32,
    "FQ": 0.24,
}

# ---------------------------------------------------------------------------
# OAP → aspect mapping  (paper Appendix B + Figure 1)
# ---------------------------------------------------------------------------
OAP_TO_ASPECT: Dict[str, str] = {
    "pre_arg_structure": "LP",
    "quantification": "LP",
    "formula": "LP",
    "relation": "LP",
    "concept": "MC",
    "constant": "MC",
    "operator": "MC",
    "syntax_validity": "FV",
    "referential_completeness": "FV",
    "type_match": "FV",
    "conciseness": "FQ",
    "logical_consistency": "FQ",
}

ASPECT_OAPS: Dict[str, List[str]] = {}
for _oap, _asp in OAP_TO_ASPECT.items():
    ASPECT_OAPS.setdefault(_asp, []).append(_oap)

# ---------------------------------------------------------------------------
# Prompt templates  (adapted from Table 8 of the paper for Lean 4 theorem
# scoring rather than NL→formal autoformalization)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are an expert in Lean 4 formal verification.\n"
    "You will be given a REFERENCE IMPLEMENTATION (the gold-standard Lean 4 code) "
    "and a GENERATED THEOREM (a candidate Lean 4 theorem that attempts to capture "
    "the correctness properties of the reference).\n"
    "Your task is to evaluate a specific aspect of the generated theorem.\n"
    "The description of the aspect is: {aspect_description}\n"
    "You need to give two things about your evaluation:\n"
    "1. the judgement of whether the generated theorem satisfies this aspect. "
    "This should be a binary value in \"True\" or \"False\".\n"
    "2. the detailed explanation of your judgement.\n"
    "You should wrap your final results in a way illustrated as the following:\n"
    "%%%%%%%%%%\n"
    "Explanation: Your Detailed Explanation\n"
    "Judgement: Your Binary Judgement\n"
    "%%%%%%%%%%\n"
    "Strictly follow the instructions that have been claimed."
)

USER_TEMPLATE = (
    "REFERENCE IMPLEMENTATION:\n```lean\n{reference_impl}\n```\n\n"
    "GENERATED THEOREM:\n```lean\n{generated_theorem}\n```"
)

# --- Aspect-level descriptions (direct mode) --------------------------------
ASPECT_DESCRIPTIONS: Dict[str, str] = {
    "LP": (
        "Logical Preservation: Does the generated theorem capture the logical "
        "structure and correctness properties of the reference implementation?"
    ),
    "MC": (
        "Mathematical Consistency: Does the generated theorem accurately "
        "represent mathematical objects, operations, and invariants present "
        "in the reference implementation?"
    ),
    "FV": (
        "Formal Validity: Is the generated theorem syntactically correct "
        "and well-formed Lean 4 code?"
    ),
    "FQ": (
        "Formal Quality: Does the generated theorem demonstrate high quality "
        "in terms of structural clarity, conciseness, and usefulness?"
    ),
}

# --- OAP-level descriptions (oap_wa mode) -----------------------------------
OAP_DESCRIPTIONS: Dict[str, str] = {
    "pre_arg_structure": (
        "Does the generated theorem reflect the inherent predicate-argument "
        "structure of the reference implementation?"
    ),
    "quantification": (
        "Does the generated theorem accurately formalize all quantifiers "
        "(universal, existential) present in the reference implementation?"
    ),
    "formula": (
        "Are all mathematical formulas and expressions in the reference "
        "implementation (equations, inequalities, etc.) correctly and "
        "completely represented in the generated theorem?"
    ),
    "relation": (
        "Are the logical and mathematical relationships between propositions "
        "in the reference implementation preserved in the generated theorem?"
    ),
    "concept": (
        "Are all mathematical concepts mentioned in the reference "
        "implementation (types, structures, etc.) correctly formalized "
        "in the generated theorem?"
    ),
    "constant": (
        "Are all mathematical constants present in the reference "
        "implementation properly included in the generated theorem?"
    ),
    "operator": (
        "Are all mathematical operators used in the reference implementation "
        "(addition, subtraction, multiplication, etc.) correctly represented "
        "in the generated theorem?"
    ),
    "syntax_validity": (
        "Does the generated theorem contain no syntax or structural errors "
        "within Lean 4?"
    ),
    "referential_completeness": (
        "Are all symbols and terms used in the generated theorem properly "
        "defined or imported, ensuring nothing is left undefined?"
    ),
    "type_match": (
        "Are the types of variables and expressions in the generated theorem "
        "correctly and consistently assigned, in accordance with Lean 4 "
        "type rules?"
    ),
    "conciseness": (
        "Is the generated theorem expressed in a minimal, non-redundant form, "
        "avoiding unnecessary repetition or complexity?"
    ),
    "logical_consistency": (
        "Is the generated theorem internally coherent and contains no "
        "contradictions under the logical rules of Lean 4?"
    ),
}


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------
_JUDGEMENT_RE = re.compile(
    r"Judgement\s*:\s*(True|False)", re.IGNORECASE
)


def parse_efg_response(text: str) -> Tuple[bool, str]:
    """Parse an EFG judge response into (judgement_bool, explanation)."""
    m = _JUDGEMENT_RE.search(text)
    judgement = m.group(1).strip().lower() == "true" if m else False

    explanation = ""
    exp_m = re.search(
        r"Explanation\s*:\s*(.+?)(?=\n(?:Judgement\s*:|%%)|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if exp_m:
        explanation = exp_m.group(1).strip()

    return judgement, explanation


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


MAX_RETRIES = 3


def _get_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    for p in [
        os.path.expanduser("~/keys/openai_bm_key_koyejolab.txt"),
        os.path.expanduser("~/keys/openai_api_brandos_personal_key.txt"),
    ]:
        try:
            return Path(p).read_text().strip()
        except Exception:
            continue
    raise RuntimeError("Could not find any OpenAI API key")


def _get_anthropic_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    try:
        return Path(os.path.expanduser("~/keys/anthropic_bm_key_koyejolab.txt")).read_text().strip()
    except Exception:
        raise RuntimeError("Could not find Anthropic API key")


def _make_client(model: str):
    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        import openai
        return openai.OpenAI(api_key=_get_openai_key()), "openai"
    elif model.startswith("claude"):
        import anthropic
        return anthropic.Anthropic(api_key=_get_anthropic_key()), "anthropic"
    else:
        import openai
        return openai.OpenAI(api_key=_get_openai_key()), "openai"


def _call_llm(
    client,
    backend: str,
    system_msg: str,
    user_msg: str,
    model: str,
    temperature: float = 0.2,
) -> str:
    """Call LLM and return raw text response."""
    for attempt in range(MAX_RETRIES):
        try:
            if backend == "openai":
                response = client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    max_tokens=512,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                )
                return response.choices[0].message.content or ""
            else:  # anthropic
                response = client.messages.create(
                    model=model,
                    max_tokens=512,
                    system=system_msg,
                    messages=[{"role": "user", "content": user_msg}],
                )
                return response.content[0].text.strip()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                print(f"  [efg_judge] attempt {attempt+1} failed: {e}, retrying in {wait}s")
                time.sleep(wait)
                continue
            return f"ERROR: {e}"
    return "ERROR: max retries exceeded"


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache" / "efg_judge"


def _load_cache(namespace: str) -> dict:
    path = _CACHE_DIR / f"{namespace}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}


def _save_cache(namespace: str, cache: dict) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _CACHE_DIR / f"{namespace}.json"
    path.write_text(json.dumps(cache, indent=2))


# ---------------------------------------------------------------------------
# EFG Judge results
# ---------------------------------------------------------------------------
@dataclass
class OAPResult:
    name: str
    aspect: str
    judgement: bool
    explanation: str
    score: float = 0.0  # 1.0 if True, 0.0 if False

    def __post_init__(self):
        self.score = 1.0 if self.judgement else 0.0


@dataclass
class EFGResult:
    """Full result of an EFG evaluation for one (reference, generated) pair."""
    mode: str  # "direct" or "oap_wa"
    model: str
    aspect_scores: Dict[str, float] = field(default_factory=dict)
    oap_results: List[OAPResult] = field(default_factory=list)
    overall_score: float = 0.0
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))

    def compute_overall(self) -> float:
        w_total = sum(self.weights.values())
        if w_total <= 0:
            return 0.0
        s = sum(
            (self.weights.get(asp, 0.0) / w_total) * self.aspect_scores.get(asp, 0.0)
            for asp in ["LP", "MC", "FV", "FQ"]
        )
        self.overall_score = max(0.0, min(1.0, s))
        return self.overall_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "model": self.model,
            "overall_score": self.overall_score,
            "aspect_scores": self.aspect_scores,
            "weights": self.weights,
            "oap_results": [
                {"name": o.name, "aspect": o.aspect, "judgement": o.judgement, "score": o.score}
                for o in self.oap_results
            ],
        }


# ---------------------------------------------------------------------------
# Main judge functions
# ---------------------------------------------------------------------------
def efg_judge_direct(
    reference_impl: str,
    generated_theorem: str,
    model: str = "gpt-4o-mini",
    weights: Optional[Dict[str, float]] = None,
    cache_namespace: str = "efg_direct",
    temperature: float = 0.2,
) -> EFGResult:
    """
    Direct EFG judging: one LLM call per aspect (LP, MC, FV, FQ).
    Each aspect gets a binary True/False.
    """
    if weights is None:
        weights = dict(DEFAULT_WEIGHTS)

    ref_hash = _sha256(reference_impl)
    gen_hash = _sha256(generated_theorem)
    cache_key = f"{model}|{ref_hash}|{gen_hash}"
    cache = _load_cache(cache_namespace)

    if cache_key in cache:
        entry = cache[cache_key]
        result = EFGResult(
            mode="direct",
            model=model,
            aspect_scores=entry["aspect_scores"],
            weights=weights,
        )
        # The cache stores primitive aspect scores. Recompute the requested weighted
        # aggregate instead of silently reusing an aggregate made with old weights.
        result.compute_overall()
        return result

    client, backend = _make_client(model)
    user_msg = USER_TEMPLATE.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )

    aspect_scores: Dict[str, float] = {}
    for aspect, desc in ASPECT_DESCRIPTIONS.items():
        sys_msg = SYSTEM_PROMPT.format(aspect_description=desc)
        raw = _call_llm(client, backend, sys_msg, user_msg, model, temperature)
        judgement, explanation = parse_efg_response(raw)
        aspect_scores[aspect] = 1.0 if judgement else 0.0
        time.sleep(0.2)

    result = EFGResult(mode="direct", model=model, aspect_scores=aspect_scores, weights=weights)
    result.compute_overall()
    cache[cache_key] = {"aspect_scores": aspect_scores, "overall_score": result.overall_score}
    _save_cache(cache_namespace, cache)
    return result


def efg_judge_oap_wa(
    reference_impl: str,
    generated_theorem: str,
    model: str = "gpt-4o-mini",
    weights: Optional[Dict[str, float]] = None,
    cache_namespace: str = "efg_oap_wa",
    temperature: float = 0.2,
) -> EFGResult:
    """
    OAP-WA EFG judging (best method from paper Table 4):
    one LLM call per OAP (12 total), aspect score = mean of its OAPs,
    overall = weighted linear combination.
    """
    if weights is None:
        weights = dict(DEFAULT_WEIGHTS)

    ref_hash = _sha256(reference_impl)
    gen_hash = _sha256(generated_theorem)
    cache_key = f"{model}|{ref_hash}|{gen_hash}"
    cache = _load_cache(cache_namespace)

    if cache_key in cache:
        entry = cache[cache_key]
        result = EFGResult(
            mode="oap_wa",
            model=model,
            aspect_scores=entry["aspect_scores"],
            oap_results=[
                OAPResult(name=o["name"], aspect=o["aspect"], judgement=o["judgement"], explanation="")
                for o in entry.get("oap_results", [])
            ],
            weights=weights,
        )
        result.compute_overall()
        return result

    client, backend = _make_client(model)
    user_msg = USER_TEMPLATE.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )

    oap_results: List[OAPResult] = []
    for oap_name, oap_desc in OAP_DESCRIPTIONS.items():
        aspect = OAP_TO_ASPECT[oap_name]
        sys_msg = SYSTEM_PROMPT.format(aspect_description=oap_desc)
        raw = _call_llm(client, backend, sys_msg, user_msg, model, temperature)
        judgement, explanation = parse_efg_response(raw)
        oap_results.append(OAPResult(name=oap_name, aspect=aspect, judgement=judgement, explanation=explanation))
        time.sleep(0.15)

    aspect_scores: Dict[str, float] = {}
    for aspect, oap_names in ASPECT_OAPS.items():
        oap_vals = [r.score for r in oap_results if r.name in oap_names]
        aspect_scores[aspect] = sum(oap_vals) / len(oap_vals) if oap_vals else 0.0

    result = EFGResult(mode="oap_wa", model=model, aspect_scores=aspect_scores, oap_results=oap_results, weights=weights)
    result.compute_overall()
    cache[cache_key] = {
        "aspect_scores": aspect_scores,
        "overall_score": result.overall_score,
        "oap_results": [
            {"name": o.name, "aspect": o.aspect, "judgement": o.judgement, "score": o.score}
            for o in oap_results
        ],
    }
    _save_cache(cache_namespace, cache)
    return result


def efg_judge(
    reference_impl: str,
    generated_theorem: str,
    model: str = "gpt-4o-mini",
    mode: str = "oap_wa",
    weights: Optional[Dict[str, float]] = None,
    cache_namespace: Optional[str] = None,
    temperature: float = 0.2,
) -> EFGResult:
    """
    Unified entry point for EFG judging.

    Args:
        reference_impl: Gold-standard Lean 4 code.
        generated_theorem: Candidate Lean 4 theorem to evaluate.
        model: LLM model identifier (e.g. "gpt-4o-mini", "claude-sonnet-4-6").
        mode: "direct" (4 calls) or "oap_wa" (12 calls, best from paper).
        weights: {LP, MC, FV, FQ} weights summing to ~1. Default: paper-optimal.
        cache_namespace: Cache file prefix. Auto-set if None.
        temperature: LLM sampling temperature (paper uses 0.2).

    Returns:
        EFGResult with overall_score in [0, 1] and per-aspect breakdown.
    """
    if cache_namespace is None:
        cache_namespace = f"efg_{mode}"

    if mode == "direct":
        return efg_judge_direct(
            reference_impl, generated_theorem, model, weights,
            cache_namespace, temperature,
        )
    elif mode == "oap_wa":
        return efg_judge_oap_wa(
            reference_impl, generated_theorem, model, weights,
            cache_namespace, temperature,
        )
    else:
        raise ValueError(f"Unknown EFG mode: {mode!r}. Use 'direct' or 'oap_wa'.")


# ---------------------------------------------------------------------------
# Convenience: match judge_caller.judge() interface for drop-in use
# ---------------------------------------------------------------------------
def judge(
    generated_theorem: str,
    reference_impl: str,
    model: str = "gpt-4o-mini",
    n_repeats: int = 1,
    mode: str = "oap_wa",
    cache_namespace: str = "efg_compat",
    **kwargs,
) -> Dict[str, Any]:
    """
    Drop-in replacement for judge_caller.judge() that uses EFG scoring.

    Returns dict with keys: score, mean, std, scores, reasoning, model, cached,
    plus efg_aspect_scores and efg_oap_results for transparency.
    """
    import statistics

    scores: List[float] = []
    all_results: List[EFGResult] = []

    for i in range(n_repeats):
        ns = f"{cache_namespace}_r{i}" if n_repeats > 1 else cache_namespace
        result = efg_judge(
            reference_impl=reference_impl,
            generated_theorem=generated_theorem,
            model=model,
            mode=mode,
            cache_namespace=ns,
            **kwargs,
        )
        scores.append(result.overall_score)
        all_results.append(result)

    mean_score = statistics.mean(scores)
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0

    return {
        "score": mean_score,
        "mean": mean_score,
        "std": std_score,
        "scores": scores,
        "reasoning": f"EFG {mode}: LP={all_results[0].aspect_scores.get('LP', 0):.2f} "
                     f"MC={all_results[0].aspect_scores.get('MC', 0):.2f} "
                     f"FV={all_results[0].aspect_scores.get('FV', 0):.2f} "
                     f"FQ={all_results[0].aspect_scores.get('FQ', 0):.2f}",
        "model": model,
        "cached": False,
        "efg_aspect_scores": all_results[0].aspect_scores,
        "efg_oap_results": [o.to_dict() for o in all_results] if all_results else [],
    }


if __name__ == "__main__":
    # Quick self-test with dummy inputs
    ref = "theorem add_comm (n m : Nat) : n + m = m + n := by omega"
    gen = "theorem add_comm_nat (k j : Nat) : k + j = j + k := by omega"
    result = efg_judge(ref, gen, mode="oap_wa")
    print(f"Overall: {result.overall_score:.3f}")
    print(f"Aspects: {result.aspect_scores}")
    for o in result.oap_results:
        print(f"  {o.name:30s} ({o.aspect}): {o.judgement} -> {o.score}")
