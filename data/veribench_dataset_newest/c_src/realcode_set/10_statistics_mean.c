/* Calculates the arithmetic mean (average) of a sample.
   Sourced from Python's standard statistics library.
   NOTE: simplified from Python version -- only supports double arrays. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <math.h>

/* -- Pre-condition -- */
int pre(double *data, int n) {
    return data != NULL && n > 0;
}

/* -- Implementation -- */

double mean(double *data, int n) {
    if (n < 1) {
        fprintf(stderr, "StatisticsError: mean requires at least one data point\n");
        exit(1);
    }
    double total = 0.0;
    for (int i = 0; i < n; i++) {
        total += data[i];
    }
    return total / n;
}

double benchmark_mean(double *data, int n) {
    if (!pre(data, n)) {
        fprintf(stderr, "StatisticsError: requires a non-empty array of numbers\n");
        exit(1);
    }
    return mean(data, n);
}

/* -- Tests -- */

int check(void) {
    /* 1. Basic Integers */
    double d1[] = {1, 2, 3, 4, 4};
    assert(fabs(benchmark_mean(d1, 5) - 2.8) < 1e-9);

    /* 2. Single Value */
    double d2[] = {42.5};
    assert(fabs(benchmark_mean(d2, 1) - 42.5) < 1e-9);

    /* 3. Shift Invariance */
    double c = 1e9;
    double data[] = {3.4, 4.5, 4.9, 6.7, 6.8, 7.2, 8.0, 8.1, 9.4};
    double expected = benchmark_mean(data, 9) + c;
    double shifted[9];
    for (int i = 0; i < 9; i++) shifted[i] = data[i] + c;
    double got = benchmark_mean(shifted, 9);
    assert(fabs(got - expected) <= 1e-3);  /* relaxed due to floating point */

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
