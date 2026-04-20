"""Return the larger of two natural numbers (non-negative integers).

Edge cases:
- max(0, 0) = 0
- The function raises ValueError if either input is not a natural number.
"""

def pre(a: int, b: int) -> bool:
    """True iff both inputs are integers with a >= 0 and b >= 0."""
    return isinstance(a, int) and isinstance(b, int) and a >= 0 and b >= 0

def prog(a: int, b: int) -> int:
    """
    Return max(a, b) for non‑negative integers a and b.
    Raises ValueError if the precondition is violated.
    """
    if not pre(a, b):
        raise ValueError(f"Inputs must be non-negative integers (got a={a}, b={b})")
    return b if a <= b else a

# -- Tests --

from typing import Callable

def check(candidate: Callable[[int, int], int]) -> bool:
    # Basic unit test
    assert candidate(7, 3) == 7

    # Edge unit test
    assert candidate(0, 0) == 0

    # Negative (pre-violations must raise ValueError)
    bad_inputs = [(-1, 0), (0, -2)]
    for a, b in bad_inputs:
        try:
            candidate(a, b)
            raise AssertionError("expected pre-violation did not raise")
        except ValueError:
            pass

    return True

if __name__ == "__main__":
    assert check(prog), f"Failed: {__file__}"
    print("All tests passed.")
