/* From a list of numbers select and return two that are closest to each other. */
#include <stdio.h>
#include <assert.h>
#include <math.h>

void find_closest_elements(double *numbers, int n, double *out_a, double *out_b) {
    double best_dist = -1;
    double a = 0, b = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i != j) {
                double d = fabs(numbers[i] - numbers[j]);
                if (best_dist < 0 || d < best_dist) {
                    best_dist = d;
                    if (numbers[i] <= numbers[j]) {
                        a = numbers[i]; b = numbers[j];
                    } else {
                        a = numbers[j]; b = numbers[i];
                    }
                }
            }
        }
    }
    *out_a = a;
    *out_b = b;
}

void check(void) {
    double a, b;

    {
        double arr[] = {1.0, 2.0, 3.9, 4.0, 5.0, 2.2};
        find_closest_elements(arr, 6, &a, &b);
        assert(a == 3.9 && b == 4.0);
    }
    {
        double arr[] = {1.0, 2.0, 5.9, 4.0, 5.0};
        find_closest_elements(arr, 5, &a, &b);
        assert(a == 5.0 && b == 5.9);
    }
    {
        double arr[] = {1.0, 2.0, 3.0, 4.0, 5.0, 2.2};
        find_closest_elements(arr, 6, &a, &b);
        assert(a == 2.0 && b == 2.2);
    }
    {
        double arr[] = {1.0, 2.0, 3.0, 4.0, 5.0, 2.0};
        find_closest_elements(arr, 6, &a, &b);
        assert(a == 2.0 && b == 2.0);
    }
    {
        double arr[] = {1.1, 2.2, 3.1, 4.1, 5.1};
        find_closest_elements(arr, 5, &a, &b);
        assert(fabs(a - 2.2) < 1e-9 && fabs(b - 3.1) < 1e-9);
    }
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
