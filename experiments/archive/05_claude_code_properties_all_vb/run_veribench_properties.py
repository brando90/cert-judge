#!/usr/bin/env python3
"""
Scale cert-judge P1-P4 sanity checks across all VeriBench Lean files.

Computes:
  P1 (Identity):      Score each file against itself → expect max score.
  P2 (Bug Monoton.):   Score file variants with increasing bugs → expect decreasing scores.
  P3 (Spec Ablation):  Score file variants with progressively removed specs → expect decreasing scores.
  P4 (Stability):      Variance across repeated evaluations → expect low.

Generates aggregate figures: identity_property.png, monotonicity_bugs.png,
monotonicity_missing_specs.png.

Usage:
    python run_veribench_properties.py --max-files 3 --n-repeats 3 --seed 42
    python run_veribench_properties.py --max-files 0   # 0 = all files
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── cert-judge library ──────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "py_src"))
from cert_judge.hsj_scoring import (
    _pearson_corr,
    _safe_mean,
    compute_p1_identity,
    compute_p2_or_p3_ordering_auc,
    compute_p4_stability,
    compute_jti,
    compute_spearman_scaled,
)

# ── Constants ────────────────────────────────────────────────────────
VERIBENCH_ROOT = REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench"
VERIBENCH_ROOT_FALLBACK = Path.home() / "veribench" / "veribench_dataset" / "lean_src" / "veribench"

VERIBENCH_SUBSETS = ["cs_set", "easy_set", "humaneval_set", "realcode_set", "security_set"]

DEFAULT_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_KEY_PATH = Path.home() / "keys" / "anthropic_bm_key_koyejolab.txt"

JUDGE_PROMPT = """You are an expert in Lean 4 formal verification.
Score how well the GENERATED FILE captures the correctness properties
of the REFERENCE FILE. Score from 0.0 to 1.0.

- 1.0: Semantically equivalent — same specs, same properties, same guarantees
- 0.7-0.9: Captures most properties, misses minor ones
- 0.4-0.6: Captures some properties, has meaningful gaps
- 0.1-0.3: Technically valid Lean but misses core properties
- 0.0: Trivially true (e.g., `True`) or incorrect

REFERENCE FILE:
{reference}

GENERATED FILE:
{generated}

Respond ONLY with valid JSON, no markdown:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence max>"}}"""

MAX_RETRIES = 3
N_DEGRADATION_LEVELS = 10  # 0..9 levels of degradation


# ═══════════════════════════════════════════════════════════════════
#  VeriBench file discovery
# ═══════════════════════════════════════════════════════════════════

def discover_veribench_files(max_files: int = 0, seed: int = 42) -> List[Path]:
    """Find all .lean files under VeriBench subsets."""
    root = VERIBENCH_ROOT if VERIBENCH_ROOT.exists() else VERIBENCH_ROOT_FALLBACK
    if not root.exists():
        raise FileNotFoundError(
            f"VeriBench data not found at {VERIBENCH_ROOT} or {VERIBENCH_ROOT_FALLBACK}. "
            "Please clone the veribench dataset."
        )
    files: List[Path] = []
    for subset in VERIBENCH_SUBSETS:
        subset_dir = root / subset
        if subset_dir.is_dir():
            files.extend(sorted(subset_dir.glob("*.lean")))
    if not files:
        raise FileNotFoundError(f"No .lean files found under {root}")

    if max_files > 0 and max_files < len(files):
        rng = random.Random(seed)
        files = rng.sample(files, max_files)
    files.sort()
    return files


# ═══════════════════════════════════════════════════════════════════
#  Lean file parsing & degradation
# ═══════════════════════════════════════════════════════════════════

def _find_spec_blocks(content: str) -> List[Tuple[int, int, str]]:
    """
    Find specification blocks in a Lean file.
    Returns list of (start_line, end_line, block_type) for each theorem/def Prop/example.
    """
    lines = content.split("\n")
    blocks: List[Tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        block_type = None
        if re.match(r"^(theorem|@\[simp\]\s*theorem)", line):
            block_type = "theorem"
        elif re.match(r"^def\s+\w+.*:\s*Prop", line) or re.match(r"^def\s+\w+_prop\b", line):
            block_type = "def_prop"
        elif re.match(r"^example\b", line):
            block_type = "example"

        if block_type:
            start = i
            # Find end of block: next blank line, next declaration, or next section marker
            j = i + 1
            while j < len(lines):
                lj = lines[j].strip()
                if lj == "":
                    break
                if re.match(r"^(theorem|def|example|/-!|end\s)", lj):
                    break
                if re.match(r"^@\[simp\]", lj):
                    break
                j += 1
            blocks.append((start, j, block_type))
            i = j
        else:
            i += 1
    return blocks


def create_bug_variant(content: str, n_bugs: int, seed: int = 42) -> str:
    """
    Create a variant of the file with n_bugs corrupted spec blocks.
    Corruption strategy: replace theorem/prop bodies with trivially true versions.
    """
    if n_bugs == 0:
        return content

    lines = content.split("\n")
    blocks = _find_spec_blocks(content)

    # Only corrupt theorem and def_prop blocks (not examples, which are tests)
    corruptible = [b for b in blocks if b[2] in ("theorem", "def_prop")]
    if not corruptible:
        return content

    rng = random.Random(seed + n_bugs)
    n_to_corrupt = min(n_bugs, len(corruptible))
    targets = rng.sample(corruptible, n_to_corrupt)

    corrupted_lines = list(lines)
    for start, end, btype in sorted(targets, reverse=True):
        if btype == "theorem":
            # Replace theorem body with trivially true version
            thm_line = corrupted_lines[start]
            # Find the theorem name
            m = re.match(r"^(@\[simp\]\s*)?theorem\s+(\w+)", thm_line)
            if m:
                prefix = m.group(1) or ""
                name = m.group(2)
                # Replace with trivially true theorem
                corrupted_lines[start:end] = [
                    f"{prefix}theorem {name}_CORRUPTED : True := trivial"
                ]
        elif btype == "def_prop":
            # Replace prop definition with True
            prop_line = corrupted_lines[start]
            m = re.match(r"^(.*def\s+\w+)(.*)$", prop_line)
            if m:
                corrupted_lines[start:end] = [
                    f"{m.group(1)} : Prop := True  -- CORRUPTED"
                ]

    return "\n".join(corrupted_lines)


def create_missing_spec_variant(content: str, n_removed: int, seed: int = 42) -> str:
    """
    Create a variant with n_removed spec blocks removed entirely.
    Removes theorem + corresponding def Prop blocks.
    """
    if n_removed == 0:
        return content

    lines = content.split("\n")
    blocks = _find_spec_blocks(content)

    # Remove theorems and their associated prop definitions
    removable = [b for b in blocks if b[2] in ("theorem", "def_prop")]
    if not removable:
        return content

    rng = random.Random(seed + n_removed + 1000)
    n_to_remove = min(n_removed, len(removable))
    targets = rng.sample(removable, n_to_remove)

    # Remove blocks in reverse order to preserve line indices
    result_lines = list(lines)
    for start, end, _ in sorted(targets, reverse=True):
        result_lines[start:end] = ["-- [REMOVED SPECIFICATION]"]

    return "\n".join(result_lines)


# ═══════════════════════════════════════════════════════════════════
#  LLM Judge calling (adapted from judge_caller.py)
# ═══════════════════════════════════════════════════════════════════

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


class JudgeCache:
    """Persistent JSON cache for judge calls."""

    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self._cache: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.cache_path.exists():
            try:
                self._cache = json.loads(self.cache_path.read_text())
            except Exception:
                self._cache = {}

    def _save(self):
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self._cache, indent=2))

    def get(self, key: str) -> Optional[dict]:
        return self._cache.get(key)

    def put(self, key: str, value: dict):
        self._cache[key] = value
        self._save()


def _get_anthropic_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    try:
        return ANTHROPIC_KEY_PATH.read_text().strip()
    except Exception:
        raise RuntimeError(f"Could not read Anthropic API key from {ANTHROPIC_KEY_PATH}")


def _parse_response(text: str) -> dict:
    """Parse JSON from LLM response, handling code fences."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        inner = [l for l in lines if not l.startswith("```")]
        stripped = "\n".join(inner).strip()
    try:
        parsed = json.loads(stripped)
        score = max(0.0, min(1.0, float(parsed.get("score", 0.5))))
        return {"score": score, "reasoning": str(parsed.get("reasoning", ""))}
    except Exception:
        m = re.search(r'"score"\s*:\s*([0-9.]+)', text)
        if m:
            return {"score": max(0.0, min(1.0, float(m.group(1)))), "reasoning": "regex_extracted"}
        return {"score": 0.5, "reasoning": f"parse_error: {text[:80]}"}


def call_judge_once(
    client,
    reference: str,
    generated: str,
    model: str,
) -> dict:
    """Single LLM judge API call."""
    prompt = JUDGE_PROMPT.format(reference=reference, generated=generated)
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            return _parse_response(text)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                print(f"  [judge] attempt {attempt+1} failed: {e}, retrying in {wait}s")
                time.sleep(wait)
            else:
                return {"score": 0.5, "reasoning": f"api_error: {str(e)[:80]}"}


def judge_score(
    reference: str,
    generated: str,
    model: str,
    n_repeats: int,
    cache: JudgeCache,
    client,
) -> Dict:
    """
    Call the LLM judge n_repeats times, return mean/std/all scores.
    Uses caching to avoid redundant API calls.
    """
    ref_hash = _sha256(reference)
    gen_hash = _sha256(generated)
    cache_key = f"{model}|{ref_hash}|{gen_hash}|n{n_repeats}"

    cached = cache.get(cache_key)
    if cached is not None:
        return {**cached, "cached": True}

    scores = []
    for i in range(n_repeats):
        result = call_judge_once(client, reference, generated, model)
        scores.append(result["score"])
        if i < n_repeats - 1:
            time.sleep(0.3)

    mean_score = statistics.mean(scores)
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
    entry = {
        "score": mean_score,
        "mean": mean_score,
        "std": std_score,
        "scores": scores,
        "model": model,
    }
    cache.put(cache_key, entry)
    return {**entry, "cached": False}


# ═══════════════════════════════════════════════════════════════════
#  Property computation
# ═══════════════════════════════════════════════════════════════════

def compute_all_properties(
    files: List[Path],
    model: str,
    n_repeats: int,
    n_degradation: int,
    cache: JudgeCache,
    client,
) -> Dict:
    """Run P1-P4 across all files. Returns raw results dict."""
    results = {
        "p1_scores": [],           # list of identity scores per file
        "p2_per_file": [],         # list of {file, counts, scores}
        "p3_per_file": [],         # list of {file, counts, scores}
        "p4_repeat_scores": {},    # {file_name: [scores from repeats]}
        "files_used": [],
    }

    total = len(files)
    for idx, fpath in enumerate(files):
        fname = fpath.stem
        content = fpath.read_text()
        print(f"\n[{idx+1}/{total}] Processing: {fname} ({fpath.parent.name})")
        results["files_used"].append(str(fpath))

        # ── P1: Identity ──────────────────────────────────────────
        print(f"  P1 (identity): scoring {fname} vs itself...")
        p1_result = judge_score(content, content, model, n_repeats, cache, client)
        results["p1_scores"].append(p1_result["mean"])
        print(f"    → identity score = {p1_result['mean']:.3f} ± {p1_result['std']:.3f}")

        # ── P4: Stability (collect individual repeat scores) ──────
        results["p4_repeat_scores"][fname] = p1_result["scores"]

        # ── P2: Bug ladder ────────────────────────────────────────
        print(f"  P2 (bugs): creating {n_degradation} degradation levels...")
        bug_counts = []
        bug_scores = []
        for level in range(n_degradation):
            variant = create_bug_variant(content, level, seed=42)
            res = judge_score(content, variant, model, n_repeats, cache, client)
            bug_counts.append(level)
            bug_scores.append(res["mean"])
            # Also collect repeats for P4 at each level
            key = f"{fname}_bug{level}"
            results["p4_repeat_scores"][key] = res["scores"]
            print(f"    level {level}: score = {res['mean']:.3f} ± {res['std']:.3f}"
                  f"{' (cached)' if res.get('cached') else ''}")

        results["p2_per_file"].append({
            "file": fname,
            "subset": fpath.parent.name,
            "counts": bug_counts,
            "scores": bug_scores,
        })

        # ── P3: Missing specs ladder ──────────────────────────────
        print(f"  P3 (missing specs): creating {n_degradation} ablation levels...")
        spec_counts = []
        spec_scores = []
        for level in range(n_degradation):
            variant = create_missing_spec_variant(content, level, seed=42)
            res = judge_score(content, variant, model, n_repeats, cache, client)
            spec_counts.append(level)
            spec_scores.append(res["mean"])
            key = f"{fname}_spec{level}"
            results["p4_repeat_scores"][key] = res["scores"]
            print(f"    level {level}: score = {res['mean']:.3f} ± {res['std']:.3f}"
                  f"{' (cached)' if res.get('cached') else ''}")

        results["p3_per_file"].append({
            "file": fname,
            "subset": fpath.parent.name,
            "counts": spec_counts,
            "scores": spec_scores,
        })

    return results


# ═══════════════════════════════════════════════════════════════════
#  Metrics computation
# ═══════════════════════════════════════════════════════════════════

def _spearman_rho(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rho in [-1, 1]."""
    return compute_spearman_scaled(x, y) * 2.0 - 1.0


def _weak_monotonicity_pct(counts: List[int], scores: List[float]) -> float:
    """% of adjacent pairs where more degradation → lower or equal score."""
    if len(counts) < 2:
        return 1.0
    correct = 0
    total = 0
    for i in range(len(counts) - 1):
        if counts[i] < counts[i + 1]:
            total += 1
            if scores[i] >= scores[i + 1]:
                correct += 1
    return correct / total if total > 0 else 1.0


def compute_aggregate_metrics(results: Dict) -> Dict:
    """Compute aggregate P1-P4 metrics from raw results."""
    metrics = {}

    # P1
    p1_scores = results["p1_scores"]
    metrics["p1_mean"] = _safe_mean(p1_scores)
    metrics["p1_std"] = statistics.stdev(p1_scores) if len(p1_scores) > 1 else 0.0
    metrics["p1_value"] = compute_p1_identity(p1_scores)

    # P2: aggregate across files
    all_bug_counts = []
    all_bug_scores = []
    p2_per_file_auc = []
    p2_pearson_per_file = []
    p2_spearman_per_file = []
    p2_weak_mono_per_file = []
    for entry in results["p2_per_file"]:
        counts = entry["counts"]
        scores = entry["scores"]
        all_bug_counts.extend(counts)
        all_bug_scores.extend(scores)
        p2_per_file_auc.append(compute_p2_or_p3_ordering_auc(counts, scores))
        p2_pearson_per_file.append(_pearson_corr(
            [float(c) for c in counts], [float(s) for s in scores]))
        p2_spearman_per_file.append(_spearman_rho(
            [float(c) for c in counts], [float(s) for s in scores]))
        p2_weak_mono_per_file.append(_weak_monotonicity_pct(counts, scores))

    metrics["p2_auc_mean"] = _safe_mean(p2_per_file_auc)
    metrics["p2_auc_std"] = statistics.stdev(p2_per_file_auc) if len(p2_per_file_auc) > 1 else 0.0
    metrics["p2_value"] = compute_p2_or_p3_ordering_auc(all_bug_counts, all_bug_scores)
    metrics["p2_pearson_mean"] = _safe_mean(p2_pearson_per_file)
    metrics["p2_spearman_mean"] = _safe_mean(p2_spearman_per_file)
    metrics["p2_weak_mono_pct"] = _safe_mean(p2_weak_mono_per_file)

    # P3: aggregate across files
    all_spec_counts = []
    all_spec_scores = []
    p3_per_file_auc = []
    p3_pearson_per_file = []
    p3_spearman_per_file = []
    p3_weak_mono_per_file = []
    for entry in results["p3_per_file"]:
        counts = entry["counts"]
        scores = entry["scores"]
        all_spec_counts.extend(counts)
        all_spec_scores.extend(scores)
        p3_per_file_auc.append(compute_p2_or_p3_ordering_auc(counts, scores))
        p3_pearson_per_file.append(_pearson_corr(
            [float(c) for c in counts], [float(s) for s in scores]))
        p3_spearman_per_file.append(_spearman_rho(
            [float(c) for c in counts], [float(s) for s in scores]))
        p3_weak_mono_per_file.append(_weak_monotonicity_pct(counts, scores))

    metrics["p3_auc_mean"] = _safe_mean(p3_per_file_auc)
    metrics["p3_auc_std"] = statistics.stdev(p3_per_file_auc) if len(p3_per_file_auc) > 1 else 0.0
    metrics["p3_value"] = compute_p2_or_p3_ordering_auc(all_spec_counts, all_spec_scores)
    metrics["p3_pearson_mean"] = _safe_mean(p3_pearson_per_file)
    metrics["p3_spearman_mean"] = _safe_mean(p3_spearman_per_file)
    metrics["p3_weak_mono_pct"] = _safe_mean(p3_weak_mono_per_file)

    # P4: Stability
    metrics["p4_value"] = compute_p4_stability(results["p4_repeat_scores"])
    # Compute pooled variance manually for reporting
    variances = []
    for scores in results["p4_repeat_scores"].values():
        s = list(scores)
        if len(s) > 1:
            mu = _safe_mean(s)
            var = _safe_mean([(v - mu) ** 2 for v in s])
            variances.append(var)
    metrics["p4_pooled_var"] = _safe_mean(variances) if variances else 0.0
    metrics["p4_pooled_std"] = metrics["p4_pooled_var"] ** 0.5

    # JTI
    metrics["jti"] = compute_jti(
        metrics["p1_value"], metrics["p2_value"],
        metrics["p3_value"], metrics["p4_value"],
    )

    return metrics


# ═══════════════════════════════════════════════════════════════════
#  Figure generation (matching existing paper style)
# ═══════════════════════════════════════════════════════════════════

def _setup_plot_style():
    """Set up matplotlib style matching the existing paper figures."""
    plt.rcParams.update({
        "figure.figsize": (8, 6),
        "font.size": 12,
        "axes.grid": True,
        "grid.alpha": 0.3,
    })


def plot_identity(
    results: Dict,
    metrics: Dict,
    model: str,
    output_path: Path,
):
    """Plot P1 identity property: all files scored against themselves."""
    _setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    scores = results["p1_scores"]
    file_names = [Path(f).stem for f in results["files_used"]]
    x = list(range(len(scores)))

    ax.scatter(x, scores, s=80, alpha=0.7, zorder=5, color="steelblue", edgecolors="navy")

    # Horizontal line at 1.0
    ax.axhline(y=1.0, color="red", linestyle="--", alpha=0.7, label="Perfect Identity (1.0)")

    mean_val = metrics["p1_mean"]
    std_val = metrics["p1_std"]
    ax.axhline(y=mean_val, color="green", linestyle="-", alpha=0.5,
               label=f"Mean = {mean_val:.3f}")

    ax.set_xlabel("VeriBench File Index", fontsize=13)
    ax.set_ylabel("LLM Judge Score (Normalized)", fontsize=13)
    ax.set_title(f"Identity Property (P1) — All VeriBench Files ({model})", fontsize=14)
    ax.set_ylim(min(0.9, min(scores) - 0.05), 1.05)

    # Stats box
    textstr = (f"Mean = {mean_val:.3f}\n"
               f"Std = {std_val:.3f}\n"
               f"N files = {len(scores)}\n"
               f"P1 = {metrics['p1_value']:.3f}")
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment="top", bbox=props)

    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


def plot_monotonicity(
    results: Dict,
    metrics: Dict,
    property_key: str,  # "p2" or "p3"
    model: str,
    output_path: Path,
):
    """Plot P2 or P3 monotonicity: aggregate scatter with trend line."""
    _setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    data_key = "p2_per_file" if property_key == "p2" else "p3_per_file"
    label = "Number of Bugs" if property_key == "p2" else "Number of Removed Specs"
    title_suffix = "Bugs" if property_key == "p2" else "Missing Specs"

    # Plot each file as a semi-transparent line + scatter
    all_counts = []
    all_scores = []
    for entry in results[data_key]:
        counts = entry["counts"]
        scores = entry["scores"]
        all_counts.extend(counts)
        all_scores.extend(scores)
        ax.plot(counts, scores, alpha=0.2, color="steelblue", linewidth=0.8)
        ax.scatter(counts, scores, s=30, alpha=0.3, color="steelblue", edgecolors="none")

    # Compute mean score at each degradation level
    level_scores: Dict[int, List[float]] = {}
    for entry in results[data_key]:
        for c, s in zip(entry["counts"], entry["scores"]):
            level_scores.setdefault(c, []).append(s)

    mean_counts = sorted(level_scores.keys())
    mean_scores = [_safe_mean(level_scores[c]) for c in mean_counts]
    std_scores = [
        (statistics.stdev(level_scores[c]) if len(level_scores[c]) > 1 else 0.0)
        for c in mean_counts
    ]

    # Plot mean trend with error bars
    ax.errorbar(mean_counts, mean_scores, yerr=std_scores, fmt="o-",
                color="red", linewidth=2, markersize=8, capsize=4,
                label="Mean ± Std across files", zorder=10)

    # Linear regression on means
    if len(mean_counts) >= 2:
        z = np.polyfit(mean_counts, mean_scores, 1)
        p = np.poly1d(z)
        x_fit = np.linspace(min(mean_counts), max(mean_counts), 100)
        ax.plot(x_fit, p(x_fit), "--", color="darkred", alpha=0.7, linewidth=1.5)

    # Correlation stats
    pearson_m = metrics[f"{property_key}_pearson_mean"]
    spearman_m = metrics[f"{property_key}_spearman_mean"]
    weak_mono = metrics[f"{property_key}_weak_mono_pct"]
    p_value = metrics[f"{property_key}_value"]

    textstr = (f"Pearson r = {pearson_m:.3f}\n"
               f"Spearman ρ = {spearman_m:.3f}\n"
               f"Weak monoton. = {weak_mono:.1%}\n"
               f"P{property_key[-1]} (AUC) = {p_value:.3f}")
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment="top", bbox=props)

    ax.set_xlabel(label, fontsize=13)
    ax.set_ylabel("LLM Judge Score (Normalized)", fontsize=13)
    ax.set_title(
        f"Monotonicity vs. {title_suffix} — All VeriBench Files ({model})",
        fontsize=14,
    )
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


def plot_stability(
    results: Dict,
    metrics: Dict,
    model: str,
    output_path: Path,
):
    """Plot P4 stability: distribution of per-item std across all evaluations."""
    _setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    stds = []
    for scores in results["p4_repeat_scores"].values():
        s = list(scores)
        if len(s) > 1:
            stds.append(statistics.stdev(s))

    if stds:
        ax.hist(stds, bins=min(30, max(5, len(stds) // 3)), color="steelblue",
                edgecolor="navy", alpha=0.7)

    ax.axvline(x=_safe_mean(stds) if stds else 0, color="red", linestyle="--",
               linewidth=2, label=f"Mean Std = {_safe_mean(stds):.4f}")

    textstr = (f"P4 (Stability) = {metrics['p4_value']:.3f}\n"
               f"Pooled Var = {metrics['p4_pooled_var']:.6f}\n"
               f"Pooled Std = {metrics['p4_pooled_std']:.4f}\n"
               f"N items = {len(stds)}")
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.8)
    ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment="top", horizontalalignment="right", bbox=props)

    ax.set_xlabel("Per-Item Standard Deviation", fontsize=13)
    ax.set_ylabel("Count", fontsize=13)
    ax.set_title(f"Judge Stability (P4) — Score Variance Distribution ({model})", fontsize=14)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


# ═══════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Scale cert-judge P1-P4 across all VeriBench files."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="LLM model for judge calls")
    parser.add_argument("--n-repeats", type=int, default=3,
                        help="Number of repeated judge calls per pair (for P4)")
    parser.add_argument("--max-files", type=int, default=0,
                        help="Max VeriBench files to process (0 = all)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for file sampling and degradation")
    parser.add_argument("--n-degradation", type=int, default=N_DEGRADATION_LEVELS,
                        help="Number of degradation levels for P2/P3")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for results (default: experiment dir)")
    parser.add_argument("--figures-dir", type=str, default=None,
                        help="Directory for figure PNGs (default: paper_latex/NeurIPS_2025/figures/)")
    args = parser.parse_args()

    # Output paths
    exp_dir = Path(__file__).resolve().parent
    output_dir = Path(args.output_dir) if args.output_dir else exp_dir / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    figures_dir = (Path(args.figures_dir) if args.figures_dir
                   else REPO_ROOT / "paper_latex" / "NeurIPS_2025" / "figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    cache_path = output_dir / "judge_cache.json"
    cache = JudgeCache(cache_path)

    # Discover files
    print("=" * 70)
    print("VeriBench P1-P4 Scaling Experiment")
    print("=" * 70)
    files = discover_veribench_files(max_files=args.max_files, seed=args.seed)
    print(f"Files to process: {len(files)}")
    print(f"Model: {args.model}")
    print(f"Repeats per call: {args.n_repeats}")
    print(f"Degradation levels: {args.n_degradation}")
    print(f"Output dir: {output_dir}")
    print(f"Figures dir: {figures_dir}")

    # Create Anthropic client
    import anthropic
    api_key = _get_anthropic_key()
    client = anthropic.Anthropic(api_key=api_key)
    print("Anthropic client initialized.\n")

    # Run all properties
    results = compute_all_properties(
        files=files,
        model=args.model,
        n_repeats=args.n_repeats,
        n_degradation=args.n_degradation,
        cache=cache,
        client=client,
    )

    # Compute metrics
    print("\n" + "=" * 70)
    print("Computing aggregate metrics...")
    metrics = compute_aggregate_metrics(results)

    # Print metrics
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"  P1 (Identity):     {metrics['p1_value']:.3f}  (mean={metrics['p1_mean']:.3f}, std={metrics['p1_std']:.3f})")
    print(f"  P2 (Bug Monoton.): {metrics['p2_value']:.3f}  (Pearson={metrics['p2_pearson_mean']:.3f}, "
          f"Spearman={metrics['p2_spearman_mean']:.3f}, Weak Mono={metrics['p2_weak_mono_pct']:.1%})")
    print(f"  P3 (Spec Ablation):{metrics['p3_value']:.3f}  (Pearson={metrics['p3_pearson_mean']:.3f}, "
          f"Spearman={metrics['p3_spearman_mean']:.3f}, Weak Mono={metrics['p3_weak_mono_pct']:.1%})")
    print(f"  P4 (Stability):    {metrics['p4_value']:.3f}  (pooled_var={metrics['p4_pooled_var']:.6f}, "
          f"pooled_std={metrics['p4_pooled_std']:.4f})")
    print(f"  JTI:               {metrics['jti']:.3f}")

    # Save results
    results_path = output_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump({"metrics": metrics, "config": {
            "model": args.model, "n_repeats": args.n_repeats,
            "max_files": args.max_files, "seed": args.seed,
            "n_degradation": args.n_degradation,
            "n_files": len(files),
        }}, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Save raw data as CSV
    csv_path = output_dir / "raw_scores.csv"
    with open(csv_path, "w") as f:
        f.write("file,property,level,score\n")
        for i, s in enumerate(results["p1_scores"]):
            fname = Path(results["files_used"][i]).stem
            f.write(f"{fname},P1,0,{s:.4f}\n")
        for entry in results["p2_per_file"]:
            for c, s in zip(entry["counts"], entry["scores"]):
                f.write(f"{entry['file']},P2,{c},{s:.4f}\n")
        for entry in results["p3_per_file"]:
            for c, s in zip(entry["counts"], entry["scores"]):
                f.write(f"{entry['file']},P3,{c},{s:.4f}\n")
    print(f"Raw CSV saved: {csv_path}")

    # Generate figures
    print("\nGenerating figures...")
    plot_identity(results, metrics, args.model,
                  figures_dir / "identity_property.png")
    plot_monotonicity(results, metrics, "p2", args.model,
                      figures_dir / "monotonicity_bugs.png")
    plot_monotonicity(results, metrics, "p3", args.model,
                      figures_dir / "monotonicity_missing_specs.png")
    plot_stability(results, metrics, args.model,
                   figures_dir / "stability_p4.png")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
