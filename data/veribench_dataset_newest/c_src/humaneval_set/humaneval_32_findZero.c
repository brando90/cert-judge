/* Find a root of a polynomial via bisection on a given bracket [a, b]. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <stdbool.h>

double poly(double *xs, int n, double x) {
    double acc = 0.0;
    double p = 1.0;
    for (int i = 0; i < n; i++) {
        acc += xs[i] * p;
        p *= x;
    }
    return acc;
}

bool pre_find_zero(double *xs, int n, double a, double b, int fuel) {
    return (n > 0 && fuel >= 0 && a < b && poly(xs, n, a) * poly(xs, n, b) <= 0);
}

/* Returns root. Sets *error to 1 if pre-condition fails, 0 otherwise. */
double find_zero(double *xs, int n, double a, double b, int fuel, int *error) {
    if (!pre_find_zero(xs, n, a, b, fuel)) {
        *error = 1;
        return 0.0;
    }
    *error = 0;
    double left = a, right = b;
    for (int i = 0; i < fuel; i++) {
        double mid = (left + right) / 2.0;
        double f_mid = poly(xs, n, mid);
        if (fabs(f_mid) < 1e-10) {
            return mid;
        }
        if (poly(xs, n, left) * f_mid <= 0) {
            right = mid;
        } else {
            left = mid;
        }
    }
    return (left + right) / 2.0;
}

void check(void) {
    int err;
    double r;

    {
        double xs[] = {1.0, 2.0};
        r = find_zero(xs, 2, -1.0, 0.0, 100, &err);
        assert(err == 0);
        assert(fabs(r + 0.5) < 1e-2);
    }
    {
        double xs[] = {-6.0, 11.0, -6.0, 1.0};
        r = find_zero(xs, 4, 0.0, 2.0, 100, &err);
        assert(err == 0);
        assert(fabs(r - 1.0) < 1e-2);
    }
    {
        double xs[] = {0.0, 1.0};
        r = find_zero(xs, 2, -1.0, 1.0, 100, &err);
        assert(err == 0);
        assert(fabs(r - 0.0) < 1e-2);
    }
    {
        /* (x-2)^2 = x^2 - 4x + 4, root at x=2 where f(2)=0 */
        double xs[] = {4.0, -4.0, 1.0};
        /* f(1) = 1, f(2) = 0, so bracket [1, 2] has f(a)*f(b) = 0 */
        r = find_zero(xs, 3, 1.0, 2.0, 100, &err);
        assert(err == 0);
        assert(fabs(r - 2.0) < 1e-1);
    }
    /* Negative tests: pre-condition violations */
    {
        /* empty coeffs */
        find_zero(NULL, 0, -1.0, 1.0, 10, &err);
        assert(err == 1);
    }
    {
        /* negative fuel */
        double xs[] = {1.0};
        find_zero(xs, 1, 0.0, 1.0, -1, &err);
        assert(err == 1);
    }
    {
        /* a >= b */
        double xs[] = {1.0};
        find_zero(xs, 1, 1.0, 0.0, 10, &err);
        assert(err == 1);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
