/* Return the sum of two natural numbers (non-negative integers).
 *
 * Edge cases:
 * - 0 + n = n
 * - The function returns -1 if a or b is not a natural number.
 */

#include <stdio.h>
#include <assert.h>
#include <stdint.h>

int pre_prog(int64_t a, int64_t b) {
    return (a >= 0) && (b >= 0);
}

int64_t prog(int64_t a, int64_t b) {
    if (!pre_prog(a, b)) return -1;
    return a + b;
}

int check(void) {
    /* Basic unit test */
    assert(prog(1, 2) == 3);

    /* Edge unit test */
    assert(prog(0, 0) == 0);

    /* Negative (pre-violations) */
    assert(pre_prog(-1, 0) == 0);
    assert(pre_prog(0, -2) == 0);

    return 1;
}

int main(void) {
    assert(check());
    printf("All tests passed.\n");
    return 0;
}
