#include <stdio.h>
#include <math.h>
#include <assert.h>

/**
 * Given a positive floating point number, return its decimal part
 * (i.e., number - floor(number)).
 */
double truncate_number(double number) {
    /* 
       In Python, we had: return number % 1.0
       In C, we achieve the same using fmod(...) or number - floor(...).
     */
    return number - floor(number);
}

int check() {
    // Original tests
    assert(truncate_number(3.5) == 0.5);
    assert(fabs(truncate_number(1.33) - 0.33) < 1e-6);
    assert(fabs(truncate_number(123.456) - 0.456) < 1e-6);

    // Additional tests:

    // 1. Input is a whole number. The decimal part should be zero.
    assert(truncate_number(5.0) == 0.0);

    // 2. Very small fractional part
    assert(fabs(truncate_number(3.0000001) - 0.0000001) < 1e-9);

    // 3. Large number with fractional part
    assert(fabs(truncate_number(1234567.999999) - 0.999999) < 1e-9);

    // 4. Input is 0.0 => decimal part is 0.0
    assert(truncate_number(0.0) == 0.0);

    return 1;
}

int main() {
    if (check()) {
        printf("Pass!\n");
    } else {
        printf("Some tests failed.\n");
    }
    return 0;
}
