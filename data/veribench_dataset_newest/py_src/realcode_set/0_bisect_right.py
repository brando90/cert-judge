"""
Provides `bisect_right` for maintaining sorted lists.

Sourced from Python's standard `bisect` library.
"""

from typing import Callable, Iterable, List, Optional, TypeVar

# -- Pre-condition --

def pre_bisect(a: List, lo: int, hi: Optional[int]) -> bool:
    """True iff lo >= 0."""
    if not isinstance(lo, int) or lo < 0:
        return False
    return True

# -- Implementation --

T = TypeVar("T")
K = TypeVar("K")


def bisect_right(a: List[T], x: K, lo: int = 0, hi: Optional[int] = None, *, key: Optional[Callable[[T], K]] = None) -> int:
    """
    Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(i, x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.

    A custom key function can be supplied to customize the sort order.

    >>> bisect_right([1,2,4,4,10], 4)
    4
    >>> bisect_right(["A","bb","CC","ddd"], 2, key=len)
    3
    """
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match list.sort() / heapq semantics.
    if key is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if x < a[mid]:           # compare in element space
                hi = mid
            else:
                lo = mid + 1
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            if x < key(a[mid]):      # compare in key space
                hi = mid
            else:
                lo = mid + 1
    return lo


# Main functions to be verified by the agent
def benchmark_bisect_right(a: List[T], x: K, lo: int = 0, hi: Optional[int] = None, *, key: Optional[Callable[[T], K]] = None) -> int:
    if not pre_bisect(a, lo, hi):
        raise ValueError("lo must be non-negative")
    return bisect_right(a, x, lo, hi, key=key)


# -- Tests --
from typing import Callable

def check(
    bisect_candidate: Callable
) -> bool:
    """Test function for the benchmark candidates."""

    # 1. Test bisect_right
    # Basic
    assert bisect_candidate([1, 2, 4, 4, 10], 4, 0, None) == 4
    assert bisect_candidate([1, 2, 4, 4, 10], 0, 0, None) == 0
    assert bisect_candidate([1, 2, 4, 4, 10], 99, 0, None) == 5

    # With key=len on strings, compare in key space
    key = len
    def cand_with_key(a: List[str], k: int) -> int:
        return bisect_candidate(a, k, 0, None, key=key)

    assert cand_with_key(["A","bb","CC","ddd"], 1) == 1
    assert cand_with_key(["A","bb","CC","ddd"], 2) == 3
    assert cand_with_key(["A","bb","CC","ddd"], 3) == 4

    # Negative (pre-violation)
    try:
        bisect_candidate([1, 2, 3], 1, -1, None)
        assert False, "expected pre-violation for lo < 0 did not raise"
    except ValueError:
        pass

    return True


if __name__ == "__main__":
    assert check(benchmark_bisect_right), f"Failed: {__file__}"
    print("All tests passed.")