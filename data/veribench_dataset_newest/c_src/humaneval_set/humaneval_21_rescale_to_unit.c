/* Rescale a list of numbers so the smallest becomes 0 and the largest becomes 1. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>

/* Writes result into out array (must be pre-allocated with n elements). */
void rescale_to_unit(double *numbers, int n, double *out) {
    double min_val = numbers[0], max_val = numbers[0];
    for (int i = 1; i < n; i++) {
        if (numbers[i] < min_val) min_val = numbers[i];
        if (numbers[i] > max_val) max_val = numbers[i];
    }
    double range = max_val - min_val;
    for (int i = 0; i < n; i++) {
        out[i] = (numbers[i] - min_val) / range;
    }
}

void check(void) {
    double out[10];

    {
        double a[] = {2.0, 49.9};
        rescale_to_unit(a, 2, out);
        assert(out[0] == 0.0 && out[1] == 1.0);
    }
    {
        double a[] = {100.0, 49.9};
        rescale_to_unit(a, 2, out);
        assert(out[0] == 1.0 && out[1] == 0.0);
    }
    {
        double a[] = {1.0, 2.0, 3.0, 4.0, 5.0};
        double expected[] = {0.0, 0.25, 0.5, 0.75, 1.0};
        rescale_to_unit(a, 5, out);
        for (int i = 0; i < 5; i++) assert(fabs(out[i] - expected[i]) < 1e-9);
    }
    {
        double a[] = {2.0, 1.0, 5.0, 3.0, 4.0};
        double expected[] = {0.25, 0.0, 1.0, 0.5, 0.75};
        rescale_to_unit(a, 5, out);
        for (int i = 0; i < 5; i++) assert(fabs(out[i] - expected[i]) < 1e-9);
    }
    {
        double a[] = {12.0, 11.0, 15.0, 13.0, 14.0};
        double expected[] = {0.25, 0.0, 1.0, 0.5, 0.75};
        rescale_to_unit(a, 5, out);
        for (int i = 0; i < 5; i++) assert(fabs(out[i] - expected[i]) < 1e-9);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
