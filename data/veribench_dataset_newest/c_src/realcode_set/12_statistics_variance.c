/* Calculates the sample variance of data.
   Sourced from Python's standard statistics library.
   NOTE: simplified from Python version -- only supports double arrays. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <math.h>

/* -- Pre-condition -- */
int pre(double *data, int n) {
    return data != NULL && n >= 2;
}

/* -- Implementation -- */

double variance(double *data, int n) {
    if (n < 2) {
        fprintf(stderr, "StatisticsError: variance requires at least two data points\n");
        exit(1);
    }
    double mean = 0.0;
    for (int i = 0; i < n; i++) mean += data[i];
    mean /= n;

    double ss = 0.0;
    for (int i = 0; i < n; i++) {
        double d = data[i] - mean;
        ss += d * d;
    }
    return ss / (n - 1);
}

double benchmark_variance(double *data, int n) {
    if (!pre(data, n)) {
        fprintf(stderr, "StatisticsError: requires >= 2 data points\n");
        exit(1);
    }
    return variance(data, n);
}

/* -- Tests -- */

int check(void) {
    /* 1. Basic Integers */
    double d1[] = {4, 7, 13, 16};
    assert(fabs(benchmark_variance(d1, 4) - 30.0) < 1e-9);

    /* 2. Edge Cases */
    double d2[] = {1, 2};
    assert(fabs(benchmark_variance(d2, 2) - 0.5) < 1e-9);

    double d3[] = {7, 7, 7, 7};
    assert(fabs(benchmark_variance(d3, 4) - 0.0) < 1e-9);

    /* 3. Shift Invariance */
    double raw[] = {1, 3, 3, 4, 5, 7, 9, 10, 11, 16};
    double expected = benchmark_variance(raw, 10);
    double shifted[10];
    for (int i = 0; i < 10; i++) shifted[i] = raw[i] + 1000;
    assert(fabs(benchmark_variance(shifted, 10) - expected) < 1e-6);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
