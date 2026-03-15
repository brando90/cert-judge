#!/usr/bin/env python3
"""
Lean 4 theorem runner with caching.
Writes theorem to temp file, runs lean, returns (compiled: bool|None, error: str).
Cache: results/lean_cache.json keyed by sha256(theorem_string).
"""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

LEAN_BINARY = "/Users/brandomiranda/.elan/bin/lean"
LEAN_TIMEOUT = 30  # seconds

# Cache location relative to this file's location
_HERE = Path(__file__).parent.parent  # experiments/02_.../
CACHE_PATH = _HERE / "results" / "lean_cache.json"


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def run_lean(theorem_string: str) -> tuple:
    """
    Attempt to compile a Lean 4 theorem string.

    Returns:
        (compiled: bool|None, error_msg: str)
        - True: compiled successfully
        - False: compilation failed
        - None: lean not available
    """
    # Check lean binary
    if not os.path.exists(LEAN_BINARY):
        return (None, "lean_not_available")

    key = _sha256(theorem_string)
    cache = _load_cache()

    if key in cache:
        entry = cache[key]
        return (entry["compiled"], entry["error"])

    # Write to temp file with a minimal header
    # Note: without a lake project, 'import Mathlib' will fail.
    # We try a minimal approach and return gracefully on failure.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".lean", delete=False, prefix="cert_judge_"
    ) as f:
        tmp_path = f.name
        # Try with import Mathlib header first, then without
        f.write(theorem_string)

    compiled = False
    error_msg = ""

    try:
        result = subprocess.run(
            [LEAN_BINARY, tmp_path],
            capture_output=True,
            text=True,
            timeout=LEAN_TIMEOUT,
        )
        if result.returncode == 0:
            compiled = True
            error_msg = ""
        else:
            compiled = False
            error_msg = (result.stderr + result.stdout).strip()[:500]
    except subprocess.TimeoutExpired:
        compiled = False
        error_msg = "timeout after 30s"
    except FileNotFoundError:
        compiled = None
        error_msg = "lean_not_available"
    except Exception as e:
        compiled = False
        error_msg = str(e)[:200]
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    # Cache and return
    cache[key] = {"compiled": compiled, "error": error_msg, "theorem_snippet": theorem_string[:100]}
    _save_cache(cache)
    return (compiled, error_msg)


def lean_available() -> bool:
    return os.path.exists(LEAN_BINARY)


if __name__ == "__main__":
    # Quick test
    test = "theorem test_identity (n : Nat) : n = n := rfl"
    compiled, err = run_lean(test)
    print(f"compiled={compiled}, err={err!r}")
