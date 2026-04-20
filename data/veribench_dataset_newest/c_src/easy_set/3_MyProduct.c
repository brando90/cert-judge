/* Return the product of three natural numbers (non-negative integers).
 *
 * Edge cases:
 * - Any factor being 0 makes the product 0.
 * - product(1, 1, 1) = 1
 * - The function returns -1 if any input is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t a, int64_t b, int64_t c) {
    return (a >= 0) && (b >= 0) && (c >= 0);
}

int64_t prog(int64_t a, int64_t b, int64_t c) {
    if (!pre_prog(a, b, c)) return -1;
    return a * b * c;
}

int check(void) {
    assert(prog(2, 3, 4) == 24);
    assert(prog(0, 5, 6) == 0);
    assert(pre_prog(-1, 0, 0) == 0);
    assert(pre_prog(0, -2, 0) == 0);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
