/* Provides a function for reducing an array to a single value.
   Sourced from Python's standard functools library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <stdbool.h>

/* -- Pre-condition -- */
int pre_reduce(int64_t *sequence, int n, bool has_initial) {
    if (sequence == NULL && n > 0) return 0;
    if (!has_initial && n == 0) return 0;
    return 1;
}

/* -- Implementation -- */

typedef int64_t (*BinaryFunc)(int64_t, int64_t);

/* Returns result via *out. Returns 0 on success, -1 on error. */
int reduce(BinaryFunc function, int64_t *sequence, int n, int64_t initial, bool has_initial, int64_t *out) {
    int start = 0;
    int64_t value;

    if (!has_initial) {
        if (n == 0) return -1;  /* TypeError */
        value = sequence[0];
        start = 1;
    } else {
        value = initial;
    }

    for (int i = start; i < n; i++) {
        value = function(value, sequence[i]);
    }
    *out = value;
    return 0;
}

int64_t benchmark_reduce(BinaryFunc function, int64_t *sequence, int n, int64_t initial, bool has_initial) {
    if (!pre_reduce(sequence, n, has_initial)) {
        fprintf(stderr, "TypeError: Invalid arguments for reduce\n");
        exit(1);
    }
    int64_t result;
    int rc = reduce(function, sequence, n, initial, has_initial, &result);
    if (rc != 0) {
        fprintf(stderr, "TypeError: reduce() of empty iterable with no initial value\n");
        exit(1);
    }
    return result;
}

/* -- Tests -- */

static int64_t add(int64_t x, int64_t y) { return x + y; }

int check(void) {
    /* 1. Basic reduction */
    int64_t s1[] = {1, 2, 3, 4, 5};
    assert(benchmark_reduce(add, s1, 5, 0, false) == 15);

    /* 2. Initializer */
    int64_t s2[] = {1, 2, 3};
    assert(benchmark_reduce(add, s2, 3, 10, true) == 16);

    /* 3. Empty iterable with initializer */
    assert(benchmark_reduce(add, NULL, 0, 10, true) == 10);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
