/* Calculates Pearson's correlation coefficient.
   Sourced from Python's standard statistics library. */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <math.h>

/* -- Pre-condition -- */
int pre(double *x, int nx, double *y, int ny) {
    return x != NULL && y != NULL && nx == ny && nx >= 2;
}

/* -- Implementation -- */

double correlation(double *x, double *y, int n) {
    if (n < 2) {
        fprintf(stderr, "StatisticsError: correlation requires at least two data points\n");
        exit(1);
    }
    double xbar = 0.0, ybar = 0.0;
    for (int i = 0; i < n; i++) { xbar += x[i]; ybar += y[i]; }
    xbar /= n;
    ybar /= n;

    double sxy = 0.0, sxx = 0.0, syy = 0.0;
    for (int i = 0; i < n; i++) {
        double dx = x[i] - xbar;
        double dy = y[i] - ybar;
        sxy += dx * dy;
        sxx += dx * dx;
        syy += dy * dy;
    }
    double denom = sqrt(sxx * syy);
    if (denom == 0.0) {
        fprintf(stderr, "StatisticsError: at least one of the inputs is constant\n");
        exit(1);
    }
    return sxy / denom;
}

double benchmark_correlation(double *x, int nx, double *y, int ny) {
    if (!pre(x, nx, y, ny)) {
        fprintf(stderr, "StatisticsError: Invalid inputs for correlation\n");
        exit(1);
    }
    return correlation(x, y, nx);
}

/* -- Tests -- */

int check(void) {
    /* 1. Basic (~0.5) */
    double x1[] = {1, 2, 3}, y1[] = {1, 3, 2};
    assert(fabs(benchmark_correlation(x1, 3, y1, 3) - 0.5) < 1e-9);

    /* 2. Repeating pattern (~0.316) */
    double x2[] = {1,2,3,4,5,6,7,8,9};
    double y2[] = {1,2,3,1,2,3,1,2,3};
    assert(fabs(benchmark_correlation(x2, 9, y2, 9) - 0.316227766) < 1e-7);

    /* 3. Perfect Positive */
    double x3[] = {1, 2, 3}, y3[] = {1, 2, 3};
    assert(fabs(benchmark_correlation(x3, 3, y3, 3) - 1.0) < 1e-9);

    /* 4. Perfect Negative */
    double x4[] = {1, 2, 3}, y4[] = {-1, -2, -3};
    assert(fabs(benchmark_correlation(x4, 3, y4, 3) - (-1.0)) < 1e-9);

    /* 5. Reverse (-1.0) */
    double x5[] = {1, 2, 3}, y5[] = {3, 2, 1};
    assert(fabs(benchmark_correlation(x5, 3, y5, 3) - (-1.0)) < 1e-9);

    /* 6. Symmetry */
    double x6[] = {1,2,3,4,5,6,7,8,9};
    double y6[] = {9,8,7,6,5,4,3,2,1};
    double c1 = benchmark_correlation(x6, 9, y6, 9);
    double c2 = benchmark_correlation(y6, 9, x6, 9);
    assert(fabs(c1 - c2) < 1e-9);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
