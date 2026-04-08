#include <iostream>
#include <cmath>
#include <cassert>

/**
 * Given a positive floating point number, return its decimal part
 * (i.e., number - floor(number)).
 */
double truncate_number(double number) {
    // Equivalent to `number % 1.0` in Python
    return number - floor(number);
}

bool check(double (*candidate)(double)) {
    // Original tests
    assert(candidate(3.5) == 0.5);
    assert(std::fabs(candidate(1.33) - 0.33) < 1e-6);
    assert(std::fabs(candidate(123.456) - 0.456) < 1e-6);

    // Additional tests:

    // 1. Whole number => decimal part = 0
    assert(candidate(5.0) == 0.0);

    // 2. Very small fractional part
    assert(std::fabs(candidate(3.0000001) - 0.0000001) < 1e-9);

    // 3. Large number with fractional part
    assert(std::fabs(candidate(1234567.999999) - 0.999999) < 1e-9);

    // 4. Zero input => decimal part = 0
    assert(candidate(0.0) == 0.0);

    return true;
}

int main() {
    if (check(truncate_number)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
