/* Provides insort_left for maintaining sorted lists.
   Dependency: bisect_left is included as it is required by insort_left.
   Sourced from Python's standard bisect library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>

/* -- Pre-condition -- */
int pre_insort(int64_t lo) {
    return lo >= 0;
}

/* -- Implementation -- */

int64_t bisect_left(int64_t *a, int n, int64_t x, int64_t lo, int64_t hi_val, int hi_is_none) {
    int64_t hi = hi_is_none ? (int64_t)n : hi_val;
    while (lo < hi) {
        int64_t mid = (lo + hi) / 2;
        if (a[mid] < x) {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    return lo;
}

void insort_left(int64_t *a, int *n, int64_t x, int64_t lo, int64_t hi_val, int hi_is_none) {
    int64_t idx = bisect_left(a, *n, x, lo, hi_val, hi_is_none);
    memmove(&a[idx + 1], &a[idx], (size_t)(*n - idx) * sizeof(int64_t));
    a[idx] = x;
    (*n)++;
}

/* NOTE: key= parameter simplified from Python version -- not supported in C translation */

void benchmark_insort_left(int64_t *a, int *n, int64_t x, int64_t lo, int64_t hi_val, int hi_is_none) {
    if (!pre_insort(lo)) {
        fprintf(stderr, "ValueError: lo must be non-negative\n");
        exit(1);
    }
    insort_left(a, n, x, lo, hi_val, hi_is_none);
}

/* -- Tests -- */

static int arrays_equal(int64_t *a, int64_t *b, int n) {
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) return 0;
    }
    return 1;
}

int check(void) {
    /* 1. Basic Integer Sort - insort_left places 4 before existing 4s */
    int64_t lst1[16] = {1, 2, 4, 4, 10};
    int n1 = 5;
    benchmark_insort_left(lst1, &n1, 4, 0, 0, 1);
    int64_t exp1[] = {1, 2, 4, 4, 4, 10};
    assert(n1 == 6 && arrays_equal(lst1, exp1, 6));

    /* 2. Insert at beginning */
    int64_t lst2[16] = {1, 2, 4};
    int n2 = 3;
    benchmark_insort_left(lst2, &n2, 0, 0, 0, 1);
    int64_t exp2[] = {0, 1, 2, 4};
    assert(n2 == 4 && arrays_equal(lst2, exp2, 4));

    /* 3. Insert at end */
    int64_t lst3[16] = {1, 2, 4};
    int n3 = 3;
    benchmark_insort_left(lst3, &n3, 5, 0, 0, 1);
    int64_t exp3[] = {1, 2, 4, 5};
    assert(n3 == 4 && arrays_equal(lst3, exp3, 4));

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
