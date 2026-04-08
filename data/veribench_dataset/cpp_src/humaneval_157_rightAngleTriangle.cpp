#include <iostream>
#include <cassert>

bool right_angle_triangle(int a, int b, int c) {
    // Ensure the sides are valid (non-zero and positive).
    if (a <= 0 || b <= 0 || c <= 0) {
        return false;
    }
    // Check if the triangle satisfies the Pythagorean theorem in any permutation.
    return (a * a == b * b + c * c) ||
           (b * b == a * a + c * c) ||
           (c * c == a * a + b * b);
}

bool check(bool (*candidate)(int, int, int)) {
    // Original tests
    assert(candidate(3, 4, 5) == true);
    assert(candidate(1, 2, 3) == false);
    assert(candidate(10, 6, 8) == true);
    assert(candidate(2, 2, 2) == false);
    assert(candidate(7, 24, 25) == true);
    assert(candidate(10, 5, 7) == false);
    assert(candidate(5, 12, 13) == true);
    assert(candidate(15, 8, 17) == true);
    assert(candidate(48, 55, 73) == true);

    // Edge cases
    assert(candidate(1, 1, 1) == false);
    assert(candidate(2, 2, 10) == false);

    // Additional tests
    // 1. Large numbers forming a right triangle
    assert(candidate(30000, 40000, 50000) == true);

    // 2. Permutation of inputs forming a right triangle
    assert(candidate(5, 13, 12) == true);

    // 3. All zeros (invalid triangle)
    assert(candidate(0, 0, 0) == false);

    // 4. Negative values (invalid input)
    assert(candidate(-3, -4, -5) == false);

    return true;
}

int main() {
    if (check(right_angle_triangle)) {
        std::cout << "Pass!" << std::endl;
    } else {
        std::cout << "Some tests failed." << std::endl;
    }
    return 0;
}
