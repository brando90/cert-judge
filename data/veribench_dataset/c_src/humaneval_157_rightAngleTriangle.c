#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

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

bool check() {
    // Original tests
    assert(right_angle_triangle(3, 4, 5) == true);
    assert(right_angle_triangle(1, 2, 3) == false);
    assert(right_angle_triangle(10, 6, 8) == true);
    assert(right_angle_triangle(2, 2, 2) == false);
    assert(right_angle_triangle(7, 24, 25) == true);
    assert(right_angle_triangle(10, 5, 7) == false);
    assert(right_angle_triangle(5, 12, 13) == true);
    assert(right_angle_triangle(15, 8, 17) == true);
    assert(right_angle_triangle(48, 55, 73) == true);

    // Edge cases
    assert(right_angle_triangle(1, 1, 1) == false);
    assert(right_angle_triangle(2, 2, 10) == false);

    // Additional tests
    // 1. Large numbers forming a right triangle
    assert(right_angle_triangle(30000, 40000, 50000) == true);

    // 2. Permutation of inputs forming a right triangle
    assert(right_angle_triangle(5, 13, 12) == true);

    // 3. All zeros (invalid triangle)
    assert(right_angle_triangle(0, 0, 0) == false);

    // 4. Negative values (invalid input)
    assert(right_angle_triangle(-3, -4, -5) == false);

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
