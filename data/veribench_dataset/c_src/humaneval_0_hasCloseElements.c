// Filename: humaneval_0_hasCloseElements.c

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

bool has_close_elements(const double *numbers, int length, double threshold) {
    for (int i = 0; i < length; i++) {
        for (int j = 0; j < length; j++) {
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

void assert_true(bool condition, const char *message) {
    if (!condition) {
        printf("Assertion failed: %s\n", message);
        exit(EXIT_FAILURE);
    }
}

bool check() {
    double test1[] = {1.0, 2.0, 3.9, 4.0, 5.0, 2.2};
    double test2[] = {1.0, 2.0, 5.9, 4.0, 5.0};
    double test3[] = {1.0, 2.0, 3.0, 4.0, 5.0, 2.0};
    double test4[] = {1.1, 2.2, 3.1, 4.1, 5.1};
    double test5[] = {};
    double test6[] = {1.5};
    double test7[] = {3.14, 3.14};
    double test8[] = {100, 200};
    double test9[] = {1.0, 1.00000001};
    double test10[] = {1.0, 1.0002};

    assert_true(has_close_elements(test1, 6, 0.3) == true, "Test 1 failed");
    assert_true(has_close_elements(test1, 6, 0.05) == false, "Test 2 failed");
    assert_true(has_close_elements(test2, 5, 0.95) == true, "Test 3 failed");
    assert_true(has_close_elements(test2, 5, 0.8) == false, "Test 4 failed");
    assert_true(has_close_elements(test3, 6, 0.1) == true, "Test 5 failed");
    assert_true(has_close_elements(test4, 5, 1.0) == true, "Test 6 failed");
    assert_true(has_close_elements(test4, 5, 0.5) == false, "Test 7 failed");

    // Edge cases
    assert_true(has_close_elements(test5, 0, 0.1) == false, "Test 8 failed");
    assert_true(has_close_elements(test6, 1, 0.1) == false, "Test 9 failed");
    assert_true(has_close_elements(test7, 2, 0.1) == true, "Test 10 failed");
    assert_true(has_close_elements(test7, 2, 0.0) == false, "Test 11 failed");
    assert_true(has_close_elements(test8, 2, 999.9) == true, "Test 12 failed");
    assert_true(has_close_elements(test9, 2, 1e-5) == true, "Test 13 failed");
    assert_true(has_close_elements(test10, 2, 1e-5) == false, "Test 14 failed");

    return true;
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
