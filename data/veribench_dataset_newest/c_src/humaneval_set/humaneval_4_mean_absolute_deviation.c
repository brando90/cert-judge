/* Calculate Mean Absolute Deviation around the mean of a dataset. */
#include <stdio.h>
#include <assert.h>
#include <math.h>

double mean_absolute_deviation(double *numbers, int n) {
    double mean = 0.0;
    for (int i = 0; i < n; i++) {
        mean += numbers[i];
    }
    mean /= n;
    double mad = 0.0;
    for (int i = 0; i < n; i++) {
        mad += fabs(numbers[i] - mean);
    }
    return mad / n;
}

void check(void) {
    {
        double a[] = {1.0, 2.0, 3.0};
        assert(fabs(mean_absolute_deviation(a, 3) - 2.0/3.0) < 1e-6);
    }
    {
        double a[] = {1.0, 2.0, 3.0, 4.0};
        assert(fabs(mean_absolute_deviation(a, 4) - 1.0) < 1e-6);
    }
    {
        double a[] = {1.0, 2.0, 3.0, 4.0, 5.0};
        assert(fabs(mean_absolute_deviation(a, 5) - 6.0/5.0) < 1e-6);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
