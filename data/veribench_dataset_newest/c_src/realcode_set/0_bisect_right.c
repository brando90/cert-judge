/* Provides bisect_right for maintaining sorted lists.
   Sourced from Python's standard bisect library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>

/* -- Pre-condition -- */
int pre_bisect(int64_t *a, int n, int64_t lo, int64_t hi_val, int hi_is_none) {
    (void)a; (void)n; (void)hi_val; (void)hi_is_none;
    if (lo < 0) return 0;
    return 1;
}

/* -- Implementation -- */

int64_t bisect_right(int64_t *a, int n, int64_t x, int64_t lo, int64_t hi_val, int hi_is_none) {
    int64_t hi = hi_is_none ? (int64_t)n : hi_val;
    while (lo < hi) {
        int64_t mid = (lo + hi) / 2;
        if (x < a[mid]) {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    return lo;
}

/* NOTE: key= parameter simplified from Python version -- not supported in C translation */

int64_t benchmark_bisect_right(int64_t *a, int n, int64_t x, int64_t lo, int64_t hi_val, int hi_is_none) {
    if (!pre_bisect(a, n, lo, hi_val, hi_is_none)) {
        fprintf(stderr, "ValueError: lo must be non-negative\n");
        exit(1);
    }
    return bisect_right(a, n, x, lo, hi_val, hi_is_none);
}

/* -- Tests -- */
int check(void) {
    /* 1. Basic */
    int64_t a1[] = {1, 2, 4, 4, 10};
    assert(benchmark_bisect_right(a1, 5, 4, 0, 0, 1) == 4);
    assert(benchmark_bisect_right(a1, 5, 0, 0, 0, 1) == 0);
    assert(benchmark_bisect_right(a1, 5, 99, 0, 0, 1) == 5);

    /* 2. With explicit hi */
    assert(benchmark_bisect_right(a1, 5, 4, 0, 3, 0) == 3);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
