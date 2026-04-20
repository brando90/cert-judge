/* If n is even return n^2 else return 2n, for integer n.
 *
 * Edge cases:
 * - Works for zero.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_square_or_double(int64_t n) {
    /* All int64_t are integers, so always valid */
    (void)n;
    return 1;
}

int64_t square_or_double(int64_t n) {
    if (!pre_square_or_double(n)) return -1;
    return (n % 2 == 0) ? n * n : 2 * n;
}

int check(void) {
    assert(square_or_double(4) == 16);
    assert(square_or_double(0) == 0);
    assert(square_or_double(5) == 10);
    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
