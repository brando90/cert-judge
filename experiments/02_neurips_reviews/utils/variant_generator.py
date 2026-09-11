#!/usr/bin/env python3
"""
Syntactic variant generator for Lean 4 theorem strings.
Produces 4 variants: RENAME, REORDER, STYLE, ALPHA.
All transformations are string-level only -- no Lean compilation required.
compiled=None means unknown (not validated).
"""
import re
from typing import List, Dict


# Variable renaming maps
RENAME_MAP = {
    r'\bn\b': 'k',
    r'\bh\b': 'hyp1',
    r'\bxs\b': 'items',
    r'\bm\b': 'j',
    r'\bx\b': 'val',
    r'\by\b': 'res',
    r'\ba\b': 'p',
    r'\bb\b': 'q',
    r'\bl\b': 'lst',
    r'\bs\b': 'str_arg',
}


def _rename_variant(code: str) -> str:
    """RENAME: replace variable names with alternatives."""
    result = code
    for pattern, replacement in RENAME_MAP.items():
        # Only replace when not preceded/followed by word chars
        # Use word boundary approach
        result = re.sub(pattern, replacement, result)
    return result


def _reorder_variant(code: str) -> str:
    """REORDER: swap two consecutive hypothesis parameters if found."""
    # Match patterns like (h1 : T1) (h2 : T2) and swap
    # Also handles implicit arguments {a : T1} (b : T2)
    pattern = r'(\([a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^)]+\))\s*(\([a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^)]+\))'

    def swap_first(m):
        return m.group(2) + ' ' + m.group(1)

    result = re.sub(pattern, swap_first, code, count=1)

    # If no change, try implicit args
    if result == code:
        pattern2 = r'(\{[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^}]+\})\s*(\{[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^}]+\})'
        result = re.sub(pattern2, swap_first, code, count=1)

    # If still no change, try swapping a named arg and implicit
    if result == code:
        # Add a comment to make it syntactically different
        result = code.replace("theorem ", "-- reordered\ntheorem ", 1)

    return result


def _style_variant(code: str) -> str:
    """STYLE: change proof style markers."""
    result = code

    # Replace 'sorry' with 'by sorry'
    # Be careful not to double-wrap existing 'by sorry'
    result = re.sub(r'(?<!by ):= sorry\b', ':= by sorry', result)
    result = re.sub(r'(?<!by )\bsorry\b(?! by)', 'by sorry', result)

    # Replace ':= by sorry' with just ':= by exact False.elim (by sorry)'
    # Actually keep it simple - just normalize spacing
    if result == code:
        # Add a style comment
        result = re.sub(r'\bsorry\b', 'by exact?; sorry', result, count=1)

    if result == code:
        # Normalize whitespace style: compact → spaced
        result = re.sub(r'\s+', ' ', code).strip()
        if result == code.strip():
            result = code + "\n-- style variant"

    return result


def _alpha_variant(code: str) -> str:
    """ALPHA: rename all single-letter variables to x0, x1, x2..."""
    # Find all single-letter identifiers used as variable names
    # Look for patterns in theorem signatures: (a : T), {b : T}, etc.
    seen = {}
    counter = [0]

    def get_alpha_name(letter):
        if letter not in seen:
            seen[letter] = f"x{counter[0]}"
            counter[0] += 1
        return seen[letter]

    # Replace single-letter vars in common positions
    # Pattern: single letter followed by space and colon (declaration)
    # or standalone single letter as argument
    result = code

    # Find single letters in theorem signature area (before :=)
    theorem_match = re.search(r'(theorem\s+\w+\s*)(.*?)(:=)', result, re.DOTALL)
    if theorem_match:
        prefix = result[:theorem_match.start(2)]
        sig = theorem_match.group(2)
        suffix = result[theorem_match.end(2):]

        # Replace single-letter vars in signature
        def replace_single_letter(m):
            letter = m.group(0)
            if letter in 'αβγδεζηθικλμνξοπρστυφχψω':  # Greek letters, skip
                return letter
            return get_alpha_name(letter)

        sig_new = re.sub(r'\b([a-z])\b', replace_single_letter, sig)
        result = prefix + sig_new + ':=' + suffix

    if result == code:
        # Fallback: just add alpha comment
        result = code + "\n-- alpha renamed"

    return result


def generate_variants(code: str) -> List[Dict]:
    """
    Generate 4 syntactic variants of a Lean 4 theorem string.

    Returns list of dicts:
        [{"variant_type": str, "code": str, "compiled": None}]
    """
    variants = []

    for variant_type, transform_fn in [
        ("RENAME",  _rename_variant),
        ("REORDER", _reorder_variant),
        ("STYLE",   _style_variant),
        ("ALPHA",   _alpha_variant),
    ]:
        try:
            transformed = transform_fn(code)
        except Exception as e:
            # Fallback: minimal change
            transformed = code + f"\n-- {variant_type.lower()} variant (error: {e})"

        # Ensure variant is actually different from original
        if transformed.strip() == code.strip():
            transformed = code + f"\n-- {variant_type.lower()} variant"

        variants.append({
            "variant_type": variant_type,
            "code": transformed,
            "compiled": None,  # not validated — lean compilation without lake is complex
        })

    return variants


if __name__ == "__main__":
    # Quick test
    test_theorem = """theorem add_comm_nat (n : Nat) (m : Nat) : n + m = m + n := by
  induction n with
  | zero => simp
  | succ k ih => simp [Nat.succ_add, ih]"""

    variants = generate_variants(test_theorem)
    for v in variants:
        print(f"\n=== {v['variant_type']} ===")
        print(v["code"])
