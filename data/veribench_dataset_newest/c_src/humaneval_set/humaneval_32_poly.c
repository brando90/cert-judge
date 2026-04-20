/* Evaluate polynomial and find a zero using bisection. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>

double poly(double *xs, int n, double x) {
    double result = 0.0;
    for (int i = 0; i < n; i++) {
        result += xs[i] * pow(x, i);
    }
    return result;
}

double find_zero(double *xs, int n) {
    double begin = -1.0, end = 1.0;
    while (poly(xs, n, begin) * poly(xs, n, end) > 0) {
        begin *= 2.0;
        end *= 2.0;
    }
    while (end - begin > 1e-10) {
        double center = (begin + end) / 2.0;
        if (poly(xs, n, center) * poly(xs, n, begin) > 0) {
            begin = center;
        } else {
            end = center;
        }
    }
    return begin;
}

void check(void) {
    /* Use a seeded PRNG to generate test coefficients like the Python version */
    srand(42);
    for (int trial = 0; trial < 100; trial++) {
        int ncoeff = 2 * (1 + rand() % 4);
        double coeffs[16];
        for (int i = 0; i < ncoeff; i++) {
            int c = (rand() % 21) - 10; /* -10 to 10 */
            if (c == 0) c = 1;
            coeffs[i] = (double)c;
        }
        double solution = find_zero(coeffs, ncoeff);
        assert(fabs(poly(coeffs, ncoeff, solution)) < 1e-4);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
