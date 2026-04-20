/* Check if in given list of numbers, are any two numbers closer to each other
   than given threshold. */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>
#include <math.h>

bool has_close_elements(double *numbers, int n, double threshold) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i != j) {
                double distance = fabs(numbers[i] - numbers[j]);
                if (distance < threshold) {
                    return true;
                }
            }
        }
    }
    return false;
}

int check(void) {
    {
        double a[] = {1.0, 2.0, 3.9, 4.0, 5.0, 2.2};
        assert(has_close_elements(a, 6, 0.3) == true);
    }
    {
        double a[] = {1.0, 2.0, 3.9, 4.0, 5.0, 2.2};
        assert(has_close_elements(a, 6, 0.05) == false);
    }
    {
        double a[] = {1.0, 2.0, 5.9, 4.0, 5.0};
        assert(has_close_elements(a, 5, 0.95) == true);
    }
    {
        double a[] = {1.0, 2.0, 5.9, 4.0, 5.0};
        assert(has_close_elements(a, 5, 0.8) == false);
    }
    {
        double a[] = {1.0, 2.0, 3.0, 4.0, 5.0, 2.0};
        assert(has_close_elements(a, 6, 0.1) == true);
    }
    {
        double a[] = {1.1, 2.2, 3.1, 4.1, 5.1};
        assert(has_close_elements(a, 5, 1.0) == true);
    }
    {
        double a[] = {1.1, 2.2, 3.1, 4.1, 5.1};
        assert(has_close_elements(a, 5, 0.5) == false);
    }
    /* Empty list */
    assert(has_close_elements(NULL, 0, 0.1) == false);
    /* Single element */
    {
        double a[] = {1.5};
        assert(has_close_elements(a, 1, 0.1) == false);
    }
    /* Two identical elements */
    {
        double a[] = {3.14, 3.14};
        assert(has_close_elements(a, 2, 0.1) == true);
    }
    {
        double a[] = {3.14, 3.14};
        assert(has_close_elements(a, 2, 0.0) == false);
    }
    /* Large threshold */
    {
        double a[] = {100, 200};
        assert(has_close_elements(a, 2, 999.9) == true);
    }
    /* Very close elements */
    {
        double a[] = {1.0, 1.00000001};
        assert(has_close_elements(a, 2, 1e-5) == true);
    }
    {
        double a[] = {1.0, 1.0002};
        assert(has_close_elements(a, 2, 1e-5) == false);
    }
    return 1;
}

int main(void) {
    check();
    printf("All tests passed.\n");
    return 0;
}
