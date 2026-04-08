#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <assert.h>

/**
 * For a given list of input numbers, calculate Mean Absolute Deviation around
 * the mean of this dataset:
 *
 *    MAD = average of | x - mean(x) |
 *
 * numbers is assumed to have length > 0 in typical usage.
 */
double mean_absolute_deviation(const double *numbers, int length) {
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        sum += numbers[i];
    }
    double mean_val = sum / length;

    double total_dev = 0.0;
    for (int i = 0; i < length; i++) {
        total_dev += fabs(numbers[i] - mean_val);
    }
    return total_dev / length;
}

/* Helper function to compare floating-point values with a tolerance. */
static int almost_equal(double a, double b, double tol) {
    return (fabs(a - b) < tol);
}

/* Test function analogous to the Python check(...) */
int check() {
    // Original tests
    {
        double arr1[] = {1.0, 2.0, 3.0};
        assert(almost_equal(mean_absolute_deviation(arr1, 3), 2.0/3.0, 1e-6));

        double arr2[] = {1.0, 2.0, 3.0, 4.0};
        assert(almost_equal(mean_absolute_deviation(arr2, 4), 1.0, 1e-6));

        double arr3[] = {1.0, 2.0, 3.0, 4.0, 5.0};
        assert(almost_equal(mean_absolute_deviation(arr3, 5), 6.0/5.0, 1e-6));
    }

    // Additional tests
    {
        // 1. Single element
        double arr_single[] = {42.0};
        assert(almost_equal(mean_absolute_deviation(arr_single, 1), 0.0, 1e-9));

        // 2. All elements the same
        double arr_same[] = {5.0, 5.0, 5.0, 5.0};
        assert(almost_equal(mean_absolute_deviation(arr_same, 4), 0.0, 1e-9));

        // 3. Larger dataset [10, 20, 30, 40, 50] => mean=30 => dev=[20,10,0,10,20], average=12
        double arr_large[] = {10.0, 20.0, 30.0, 40.0, 50.0};
        assert(almost_equal(mean_absolute_deviation(arr_large, 5), 12.0, 1e-6));

        // 4. Very small differences
        //    [1.000001, 1.000002, 1.000003]
        //    mean ~ 1.000002 => dev=[1e-6,0,1e-6], sum=2e-6 => avg=6.6667e-7
        double arr_small[] = {1.000001, 1.000002, 1.000003};
        double result_small = mean_absolute_deviation(arr_small, 3);
        double expected_small = 0.0000006666667; // ~6.666667e-7
        assert(almost_equal(result_small, expected_small, 1e-9));
    }

    return 1; // All tests passed
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
