/* Fast Fibonacci via 2x2 matrix exponentiation for non-negative n.
 *
 * Edge cases:
 * - F(0) = 0, F(1) = 1
 * - Negative n is invalid (pre returns 0).
 * - Returns -1 on pre-violation.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

typedef struct { int64_t a11, a12, a21, a22; } Mat2;

int pre_fast_fibonacci(int64_t n) {
    return (n >= 0);
}

static Mat2 mat_mul(Mat2 a, Mat2 b) {
    Mat2 c;
    c.a11 = a.a11 * b.a11 + a.a12 * b.a21;
    c.a12 = a.a11 * b.a12 + a.a12 * b.a22;
    c.a21 = a.a21 * b.a11 + a.a22 * b.a21;
    c.a22 = a.a21 * b.a12 + a.a22 * b.a22;
    return c;
}

static Mat2 mat_pow(Mat2 m, int64_t n) {
    if (n == 0) return (Mat2){1, 0, 0, 1}; /* identity */
    if (n == 1) return m;
    Mat2 half = mat_pow(m, n / 2);
    Mat2 result = mat_mul(half, half);
    if (n % 2 == 1) result = mat_mul(result, m);
    return result;
}

int64_t fast_fibonacci(int64_t n) {
    if (!pre_fast_fibonacci(n)) return -1;
    if (n <= 1) return n;
    Mat2 fib = {1, 1, 1, 0};
    Mat2 result = mat_pow(fib, n - 1);
    return result.a11;
}

int check(void) {
    assert(fast_fibonacci(7) == 13);
    assert(fast_fibonacci(0) == 0);
    assert(pre_fast_fibonacci(-1) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
