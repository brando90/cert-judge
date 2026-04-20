/* Calculates the median (middle value) of data.
   Sourced from Python's standard statistics library.
   NOTE: simplified from Python version -- only supports double arrays. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <math.h>
#include <string.h>

/* -- Pre-condition -- */
int pre(double *data, int n) {
    return data != NULL && n > 0;
}

/* -- Implementation -- */

static int double_cmp(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    if (da < db) return -1;
    if (da > db) return 1;
    return 0;
}

double median(double *data, int n) {
    if (n == 0) {
        fprintf(stderr, "StatisticsError: no median for empty data\n");
        exit(1);
    }
    /* Sort a copy */
    double *sorted = (double *)malloc((size_t)n * sizeof(double));
    memcpy(sorted, data, (size_t)n * sizeof(double));
    qsort(sorted, (size_t)n, sizeof(double), double_cmp);

    double result;
    if (n % 2 == 1) {
        result = sorted[n / 2];
    } else {
        int i = n / 2;
        result = (sorted[i - 1] + sorted[i]) / 2.0;
    }
    free(sorted);
    return result;
}

double benchmark_median(double *data, int n) {
    if (!pre(data, n)) {
        fprintf(stderr, "StatisticsError: requires a non-empty array of numbers\n");
        exit(1);
    }
    return median(data, n);
}

/* -- Tests -- */

int check(void) {
    /* 1. Odd number of elements */
    double d1[] = {1, 2, 3, 4, 5, 6, 9};
    assert(fabs(benchmark_median(d1, 7) - 4.0) < 1e-9);

    /* 2. Even number of elements */
    double d2[] = {1, 2, 3, 4, 5, 6};
    assert(fabs(benchmark_median(d2, 6) - 3.5) < 1e-9);

    double d3[] = {1, 3, 5, 7};
    assert(fabs(benchmark_median(d3, 4) - 4.0) < 1e-9);

    /* 3. Single value */
    double d4[] = {42};
    assert(fabs(benchmark_median(d4, 1) - 42.0) < 1e-9);

    /* 4. Unsorted input */
    double d5[] = {9, 1, 6, 2, 5, 4, 3};
    assert(fabs(benchmark_median(d5, 7) - 4.0) < 1e-9);

    /* 5. Duplication (idempotence property for median) */
    double d6[] = {1.5, 2.5, 9.75};
    double expected = benchmark_median(d6, 3);
    double d7[] = {1.5, 1.5, 2.5, 2.5, 9.75, 9.75};
    assert(fabs(benchmark_median(d7, 6) - expected) < 1e-9);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
