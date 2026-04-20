"""Return the sum of two natural numbers (non-negative integers).

Edge cases:
- 0 + n = n
- The function raises AssertionError if a or b is not a natural number.
"""

# -- Implementation --

def pre(a: int, b: int) -> bool:
    """True iff both inputs are integers with a >= 0 and b >= 0."""
    return isinstance(a, int) and isinstance(b, int) and a >= 0 and b >= 0

def my_add_non_negative(a: int, b: int) -> int:
    """
    Return the sum of two non‑negative integers.

    >>> my_add_non_negative(1, 2)
    3
    >>> my_add_non_negative(0, 0)
    0
    """
    if not pre(a, b):
        raise ValueError("Inputs must be non-negative")
    return a + b

# -- Tests --

from typing import Callable

def check(candidate: Callable[[int, int], int]) -> bool:
    # Basic unit tests
    assert candidate(1, 2) == 3, f"expected 3 from (1,2) but got {candidate(1, 2)}"
    # Edge unit tests
    assert candidate(0, 0) == 0, f"expected 0 from (0,0) but got {candidate(0, 0)}"

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
    assert check(my_add_non_negative), f"Failed: {__file__}"
    print("All tests passed.")
